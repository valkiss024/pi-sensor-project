from .Sensor import Sensor
import random

from sense_hat import SenseHat


class moistSensor(Sensor):
    
    def __init__(self, id):
        super().__init__(id)
        self._sense = SenseHat()

    def get_reading(self):

        moisture_level = random.randint(0, 1024)

        """
        NOTE:
        In standard soil moisture sensors the output of the sensor is an ADC value ranging from 0 to 1023, where
        1023 indicates that the soil is completely dry and 0 is for completely wet. Therefore, in our implementation to
        mimic this behaviour, we are generating a random integer value between the range 0 - 1023.         
        """
        
        return moisture_level
    