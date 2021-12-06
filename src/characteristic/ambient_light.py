import schedule
from pybleno import Characteristic
from characteristic.tsl2572 import TSL2572


class AmbientLight(Characteristic):
    NOTIFY_INTERVAL = 1

    def __init__(self, i2c, logger):
        super().__init__({
            'uuid': '035c942b-f80f-4ce8-a596-d193fd61883f',
            'properties': ['read', 'notify'],
            'value': None
        })
        self.lux = None
        self.notify = False
        self.logger = logger
        self.tsl2572 = TSL2572(0x39, i2c)

        self.updateValueCallback = None
        self._value = bytes([0])

    def onReadRequest(self, offset, callback):
        if self.tsl2572.meas_single():
            lux = self.tsl2572.lux
            value = self.lux2bytes(lux)
            callback(Characteristic.RESULT_SUCCESS, value)

    def onSubscribe(self, maxValueSize, updateValueCallback):
        if not self.notify:
            self.notification(updateValueCallback)
            job = schedule.every(self.NOTIFY_INTERVAL).seconds.do(self.notification, updateValueCallback).tag(self.uuid)
            self.logger.debug(job)
            self.notify = True

    def onUnsubscribe(self):
        self.logger.info("unsubscribe")
        schedule.clear(self.uuid)
        self.notify = False

    def notification(self, callback):
        if self.tsl2572.meas_single():
            lux = self.tsl2572.lux

            if self.lux is None or abs(self.lux - lux) >= (self.lux * 0.1):
                value = self.lux2bytes(lux)
                callback(value)

    def lux2bytes(self, lux):
        self.lux = lux
        value = int(lux * 10).to_bytes(3, byteorder="big")
        self.logger.debug(f"lux = {lux:,.1f}, bytes = {value}")

        return value
