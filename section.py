class Section:
    def __init__(self, id_, crop, moisture_level):
        self._id = id_
        self._crop = crop
        self._moisture_level = moisture_level

    def __str__(self):
        return f"Section: {self._id}\nCrop type: {self._crop}\nMoisture level: {self._moisture_level}"

    @property
    def id(self):
        return self._id

    @property
    def crop(self):
        return self._crop

    @property
    def moisture_level(self):
        return self._moisture_level

    @crop.setter
    def crop(self, crop):
        self._crop = crop

    @moisture_level.setter
    def moisture_level(self, moisture_level):
        self._moisture_level = moisture_level

