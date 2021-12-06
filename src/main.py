import logging
import time
import os

from pybleno import Bleno
from my_service import MyService
from smbus2 import SMBus
import schedule


class Peripheral:
    def __init__(self, i2c, logger):
        self.logger = logger

        self.bleno = Bleno()
        self.primary_service = MyService(i2c, logger)

        self.bleno.on('stateChange', self.on_state_change)
        self.bleno.on('advertisingStart', self.on_advertising_start)
        self.bleno.on('disconnect', self.on_disconnect)
        self.bleno.start()

    def loop(self):
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        except Exception as err:
            self.logger.error(err)
        finally:
            self.bleno.stopAdvertising()
            self.bleno.disconnect()

    def on_state_change(self, state):
        self.logger.info(f"state = {state}");

        if state == 'poweredOn':
            self.bleno.startAdvertising('MyService', [self.primary_service.uuid]);
            # data = array.array("B", [0x02, 0xff, 0xff, 0xff, 0x01, 0x02])
            # self.bleno.startAdvertisingWithEIRData(data, None)
        else:
            self.bleno.stopAdvertising();

    def on_advertising_start(self, error):
        self.logger.info(f"error = {error}")

        if not error:
            self.bleno.setServices([
                self.primary_service
            ], self.on_set_service_error)

    def on_set_service_error(self, error):
        self.logger.info(f"error = {error}")

    def on_disconnect(self, clientAddress):
        logger.debug(f"clientAddress = {clientAddress}")

        self.primary_service.characteristics[0].onUnsubscribe()


def get_logger(name, level, file_name=None):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(funcName)-10s %(threadName)-10s: %(message)s")
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if file_name is not None:
            handler = logging.FileHandler(file_name)
            handler.setLevel(level)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

    logger.setLevel(level)
    logger.propagate = False

    return logger


if __name__ == "__main__":
    logger = get_logger(__name__, logging.DEBUG)
    os.environ['BLENO_DEVICE_NAME'] = 'PiZero'

    i2c = SMBus(1)
    peripheral = Peripheral(i2c, logger)
    peripheral.loop()
