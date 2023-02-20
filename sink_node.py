import json
import ssl
import sys
import time
import csv
import threading
import queue
import pandas as pd
import paho.mqtt.client as mqtt
import requests

from matplotlib import pyplot as plt
from geopy import Nominatim
from datetime import datetime, timedelta
from actuators import water_system


class SinkNode:

    # noinspection SpellCheckingInspection
    API_KEY = ""  # DEFINE OPENWEATHERMAP API KEY
    MQTT_USERNAME = ""  # DEFINE USERNAME TO CONNECT TO THE MQTT BROKER
    MQTT_PASSWORD = ""  # DEFINE PASSWORD TO CONNECT TO THE MQTT BROKER
    MQTT_HOST = ""  # DEFINE MQTT CONNECTION HOST
    MQTT_PORT = ""  # DEFINE MQTT CONNECTION PORT

    def __init__(self, id_, location, sections):
        """ Class constructor """

        self._id = id_
        self._location = location
        self._geo_location = self.get_geolocation()
        self._sections = sections
        self._connected_water_system = water_system.WaterSystem(1)
        self._q = queue.Queue()

        self._inbound_mqtt_topic = "smart_garden"
        self._TAG = "SinkNode"

    def queue_worker(self):
        """ Function running on its own Thread - it will take the received observations from the object's queue,
        transform the data into the desired format and write it to the CSV file """

        while True:
            if not self._q.empty():
                json_obj = self._q.get()
                self._fw.writerow(self.transform_data(json_obj))
                self._f.flush()
                self._q.task_done()
                if self._stop_threads:
                    break

    def get_geolocation(self):
        """ Method to get the geolocation(latitude and longitude) of the garden """

        locator = Nominatim(user_agent="smart_garden_geocoder")
        location = locator.geocode(",".join(self._location))
        location_dict = {"lat": location.latitude, "long": location.longitude}

        return location_dict

    def update_sections(self, sections):
        """ Method which is called each time a new section is added to the garden to keep the list of sections
        monitored updated """

        self._sections = sections

    def get_weather_update(self):
        """ Method to pull weather related information from the OpenWeatherMap API """

        # Passing location information in the query and get the hourly forecast for the next 24 hours
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={self._geo_location['lat']}&lon=" \
              f"{self._geo_location['long']}&appid={self.API_KEY}&exclude=current,minutely,daily,alerts&units=metric"
        response = requests.get(url).json()

        current_dt = time.time()
        forecast_data = None

        # Iterate through the response object and find the forecast for the next hour
        for hourly in response['hourly']:
            if int(hourly['dt']) - current_dt >= 3600:
                forecast_data = hourly
                break

        weather_data = dict()  # Create an empty dictionary to store weather data

        # Populate the 'weather_data' dictionary using the forecast data for the hour
        weather_data["Time"] = datetime.utcfromtimestamp(int(forecast_data['dt'])).strftime("%Y/%m/%d - %H:%M")
        weather_data["Description"] = forecast_data['weather'][0]['description']
        weather_data["Temperature"] = forecast_data['temp']
        weather_data["Humidity"] = forecast_data['humidity']
        weather_data["Precipitation"] = forecast_data['pop']

        return weather_data

    def power_on(self):
        """ Method for 'switching on' the sink node - subscribe to the MQTT topic and start listening for messages
        published from edge nodes """

        # noinspection SpellCheckingInspection
        # Call setup and pass in credentials for the broker
        self.setup_mqtt(self.MQTT_USERNAME, self.MQTT_PASSWORD, True, self.MQTT_HOST, self.MQTT_HOST)

        while True:  # Wait in a loop for new publish from edge nodes
            if self._client.connected_flag:
                time.sleep(1)

    def setup_mqtt(self, user_name, password, clean_session, host, port):
        """ Method to set up connection to the online broker and connect to it """

        # Configure MQTT Client:
        self._client = mqtt.Client(client_id="SN1", clean_session=clean_session)
        self._client.username_pw_set(user_name, password)

        # Configure TLS connection
        self._client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        self._client.tls_insecure_set(False)

        # Define callback methods
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

        # Connect to MQTT Broker
        self._client.connect(host, port)
        self._client.connected_flag = False
        self._client.loop_start()
        while not self._client.connected_flag:
            time.sleep(1)

    def disconnect_mqtt(self):
        """ Method to define action taken when disconnected from the broker - disconnect client and close the CSV
        file """

        if self._client.connected_flag:
            self._client.disconnect()
            self._client.loop_stop()
            self._f.close()

    def on_connect(self, client, userdata, flags, rc):
        """ 'on_connect' callback function """

        if rc == 0:  # If connection successful
            print(f"Connected - {self._TAG}")  # Log the connection

            # Set connected to 'True' and subscribe to the topic
            self._client.connected_flag = True
            self._client.subscribe(self._inbound_mqtt_topic)

            # Open the CSV file for append and create the file writer object
            self._f = open('reading-result.csv', 'a')
            self._fw = csv.DictWriter(self._f, fieldnames=["feature_of_interest", "made_by", "date", "time",
                                                           "temperature", "humidity", "moisture_level"])
            if self._f.tell() == 0:  # Check if the file has already been written to, if not create headers
                self._fw.writeheader()

            # Set up processor thread
            self._t = threading.Thread(target=self.queue_worker, daemon=True)
            self._stop_threads = False
            self._t.start()

            return

        sys.exit(-1)  # In the case of connection to the broker refused

    def on_message(self, client, userdata, msg):
        """ 'on_message' callback function """

        # Decode the packet payload and load it in to a dictionary
        payload = str(msg.payload.decode("UTF-8"))
        observation_dict = json.loads(payload)

        # Get weather forecast for the garden's location
        weather_info = self.get_weather_update()

        # If the packet received contains valid readings
        if "hasResult" in observation_dict and observation_dict["feature_of_interest"] in self._sections.keys():
            # Add the dictionary to the queue for processing
            self._q.put(observation_dict)
            self._q.join()

            print(f"RECEIVED PACKET: {observation_dict}")

            observed_section = self._sections[observation_dict["feature_of_interest"]]  # Get the section object
            desired_moisture_level = observed_section.moisture_level  # Get the corresponding desired moisture level
            observed_moisture_level = observation_dict["hasResult"]["moisture_level"]  # Get the actual moisture level

            # If the moisture level received from the sensor is less than the desired value specified for the section
            if observed_moisture_level > desired_moisture_level:
                if weather_info["Precipitation"] < 0.75:  # If the chances of rain is less than 75%
                    # Turn water valve on for the observed section
                    self._connected_water_system.open_valve(observed_section.id)

    def transform_data(self, observation_dict):
        """ Method to transform the reading results, prepare for storing in CSV """

        transformed_dict = {}
        # Desired keys for the transformed dictionary
        field_names = ["feature_of_interest", "made_by", "date", "time", "temperature", "humidity", "moisture_level"]
        # Loop through the observation dictionary, extract values we wish to save and add them to the new dictionary,
        # unpack the 'hasResult' object into three individual columns for easier data analysis
        for key, value in observation_dict.items():
            if key in field_names:
                transformed_dict[key] = value
            elif key == "hasResult":
                for result_key, result_value in observation_dict['hasResult'].items():
                    transformed_dict[result_key] = result_value

        return transformed_dict

    def create_graph(self, section_id, feature):
        """ Method for graphing the result using the Pandas and Matplotlib libraries """
        try:
            data = pd.read_csv("reading-result.csv")
        except FileNotFoundError as err:
            print(f"{err} - File might not been created yet")
        else:
            data['date'] = pd.to_datetime(data['date'], dayfirst=True)
            data['date'] = data['date'].dt.date

            data = data[(data['date'] == pd.Timestamp.now().date() - timedelta(days=1)) &
                        (data['feature_of_interest'] == section_id)]

            plt.plot(data['time'], data[feature])
            plt.xlabel("Time of the day")
            plt.ylabel(f"{feature} value")

            plt.show()
