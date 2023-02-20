from .Sensor import Sensor

from sense_hat import SenseHat


class humSensor(Sensor):
    
    def __init__(self, id):
        super().__init__(id)
        self._sense = SenseHat()

    def get_reading(self):

        humidity = self._sense.get_humidity()
        print("hum = ", end="")
        print(humidity)
        
        return humidity