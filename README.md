# SMART GARDEN PROJECT

#### Smart Garden Overview:
The aim of the project is to help enhance crop growth rate and regulate water consumption!
The system implementation is based on the modularization of the garden, where each section of the garden is dedicated
to a type of crop with its own desired soil moisture level defined by the user. Each section is equipped with a 
sensor device (Raspberry Pi) which then is sending data regarding current temperature, humidity and soil moisture level.
The readings for each section are received by a gateway device, which is responsible for processing and saving this data.
This device as well monitors weather forecast. If the soil moisture level for a specific section drops below the desired
amount, and no rain is expected to the next hour, then the gateway device instructs the watering system to turn on the valve
for that specific section


#### Hardware Requirements:
* A number of sensor Raspberry Pis equal the number of sections monitored in the garden - these devices must be equipped with the following sensors:
  * Temperature sensor
  * Humidity sensor
  * Soil moisture sensor
* A gateway device (Raspberry Pi) for receiving, processing and saving sensor information

#### Setup:
For setting up both sensor devices and gateway device clone the repo onto the target machine, then install all the required modules:
  <br>
  - pip3 install -r requirements.txt

For gateway device:
 - python3 garden.py<br>The configuration of the device then begins, the user will be prompted to enter the details of the garden as well as the sections in the garden

For sensor devices in the garden simply run:
 - python3 edgeNode.py<br>The configuration of the sensor device then begins, the user must enter a unique id for the device as well as the identifier of the section in the garden (must match the ID given in the gateway node) the device is 

#### 3rd party web/cloud services used for the project:
* OpenWeatherMap.org API to gather weather forecast data. An API key must be generated to use the service
* MyQttHub MQTT Broker - the project has been linked up with an account on myqtthub.com - this allowed communication through the myqtthub Broker, and access to the myqtthub dashboard to create and monitor all devices connected<br>
 Credentials for using the Broker have been hardcoded into each device, however this can be updated in the future with the scaling of the project

#### Security concerns
The MyQttHub server has been chosen as the MQTT broker to have full control of all devices connected to the broker. Using the dashboard that comes with MyQttHub each device can be set up with their unique ID and password to connect to the broker, giving an extra layer of security.
<br>
Apart from authentication on the application level, TLS for each client has been enabled for transport encryption

#### Current limitations
The developers of the project could not get a hold on to the soil moisture sensor. 
The data for soil moisture levels have been auto generated. 
However, the logic for it has been implemented and therefore making it easy to add soil moisture sensors to sensor devices in the future