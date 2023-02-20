from sensors import tempSensor
from sensors import humSensor
from sensors import moistSensor

from time import sleep
from datetime import datetime, date

import paho.mqtt.client as mqtt

import ssl
import sys
import json


class EdgeNode:
    MQTT_USERNAME = ""  # DEFINE USERNAME TO CONNECT TO THE MQTT BROKER
    MQTT_PASSWORD = ""  # DEFINE PASSWORD TO CONNECT TO THE MQTT BROKER
    MQTT_HOST = ""  # DEFINE MQTT CONNECTION HOST
    MQTT_PORT = ""  # DEFINE MQTT CONNECTION PORT

    def __init__(self, id_, section_id):
        self._id = id_
        self._section_id = section_id
        self._tempSensor = tempSensor.tempSensor("temp")
        self._humSensor = humSensor.humSensor("hum")
        self._moistSensor = moistSensor.moistSensor("moist")
        self._outbound_mqtt_topic = "smart_garden"
        self._TAG = "EdgeNode1"
        
    def power_on(self):

        # noinspection SpellCheckingInspection
        self.setup_mqtt(self.MQTT_USERNAME, self.MQTT_PASSWORD, True, self.MQTT_HOST, self.MQTT_PORT)
        
        while True:
            if self._client.connected_flag:
                humidity = self._humSensor.get_reading()
                sleep(1)
                temperature = self._tempSensor.get_reading()
                sleep(1)
                moisture = self._moistSensor.get_reading()

                reading_date = date.today()
                reading_time = datetime.now().time().strftime("%H:%M:%S")

                obs_dict = {"type": "observation", "feature_of_interest": self._section_id, "observed_property":
                            ["temperature", "humidity", "moisture_level"], "made_by": self._id, "date": reading_date,
                            "time": reading_time, "hasResult": {"temperature": temperature,
                                                                "humidity": humidity, "moisture_level": moisture}}
                
                self._client.publish(self._outbound_mqtt_topic, payload=json.dumps(obs_dict, default=str), qos=2,
                                     retain=False)

                print(f"Just PUBLISHED: {obs_dict} to TOPIC: {self._outbound_mqtt_topic}")

                sleep(1800)
        
    def setup_mqtt(self, user_name, password, clean_session, host, port):
        self._client = mqtt.Client(client_id="EN1", clean_session=clean_session)
        self._client.username_pw_set(user_name, password)
        
        self._client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
        self._client.tls_insecure_set(False)
        
        self._client.on_connect = self.on_connect
        
        self._client.on_message = self.on_message
        
        self._client.connect(host, port)
        self._client.connected_flag = False
        self._client.loop_start()
        while not self._client.connected_flag:
            sleep(1)
            
    def disconnect_mqtt(self):
        if self._client.connected_flag:
            self._client.disconnect()
            self._client.loop_stop()
            
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self._client.connected_flag = True
            return
        sys.exit(-1)
        
    def on_message(self, client, userdata, msg):
        payload = str(msg.payload.decode("UTF-8"))
        observation_dict = json.loads(payload)


if __name__ == "__main__":
    sensor = int(input("Please enter the ID for this sensor:\n>>"))
    section = int(input("Please enter the ID of the section the sensor is monitoring:\n>>"))

    sensor_node = EdgeNode(sensor, section)
    sensor_node.power_on()
