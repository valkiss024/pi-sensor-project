from .Sensor import Sensor

from sense_hat import SenseHat


class tempSensor(Sensor):
    
    def __init__(self, id):
        super().__init__(id)
        self._sense = SenseHat()

    def get_reading(self):

        temperature = self._sense.get_temperature()
        print("temp = ", end="")
        print(temperature)
        
        return temperature
    
    
   