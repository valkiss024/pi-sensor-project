import threading

from sink_node import SinkNode
from section import Section


class Garden:
    def __init__(self, name, street, city, country, sections=None):
        self._name = name
        self._street = street
        self._city = city
        self._country = country
        if not sections:
            self._sections = {}
        else:
            self._sections = sections

        self.sink_node = SinkNode(1, [self._street, self._city, self._country], self._sections)
        threading.Thread(target=self.sink_node.power_on).start()

    def __str__(self):
        return f"Name: {self._name}\nLocation information:\n\tStreet: {self._street}\n\tCity: {self._city}\n\t" \
               f"Country: {self._country}"

    @property
    def sections(self):
        return self._sections

    def add_section(self, section):
        section_id = section.id
        self._sections[section_id] = section
        self.sink_node.update_sections(self._sections)


if __name__ == "__main__":
    """ GENERATE GARDEN """
    garden_name = input("Please enter a name for your garden:\n>> ")
    print("For full functionality please specify the location:")
    garden_street = input("\t>> street: ")
    garden_city = input("\t>> city: ")
    garden_country = input("\t>> country: ")

    """ GENERATE SECTIONS """

    counter = 1  # Counter used for section IDs
    sections_added = {}
    add_new_section = True

    print("Now lets populate the garden!")

    while add_new_section:
        crop_type = input(f"What kind of crop will be planted in section({counter})?\n>> ")
        moisture_level = int(input(f"What is your desired moisture level for {crop_type}?\n>> "))
        new_section = Section(counter, crop_type, moisture_level)
        print(f"CREATED - {new_section}")
        sections_added[new_section.id] = new_section
        while True:
            add_another = input("Would you like to add another section? [Y / n]\n>> ").upper()
            if add_another == "Y":
                counter += 1
                break
            else:
                add_new_section = False
                break

    my_garden = Garden(garden_name, garden_street, garden_city, garden_country, sections_added)

