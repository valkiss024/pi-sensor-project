from .actuator import Actuator


class WaterSystem(Actuator):
    def __init__(self, id_):
        super().__init__(id_)

    def open_valve(self, section_id):
        print(f"Opening valve for section: {section_id}")

    def close_valve(self, section_id):
        print(f"Closing valve for section: {section_id}")
