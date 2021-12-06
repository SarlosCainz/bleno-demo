from pybleno import BlenoPrimaryService
from characteristic import AmbientLight


class MyService(BlenoPrimaryService):
    def __init__(self, i2c, logger):
        self.ambient_light = AmbientLight(i2c, logger)
        super().__init__({
            'uuid': 'e911aa1b-e27f-42f6-8ce7-9fc481d75bd4',
            'characteristics': [
                self.ambient_light,
            ]})
        self.logger = logger
