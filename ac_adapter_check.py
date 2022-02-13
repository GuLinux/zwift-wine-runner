from settings import settings
import time
import logging
from notifications import notifications
import threading

logger = logging.getLogger(__name__)

class ACAdapterCheck:
    def __init__(self):
        self.notification = None

    def is_ac_connected(self):
        with open(settings.check_power_supply_path, 'r') as f:
            val = f.read().strip() == '1'
            logger.debug('power status for %s: %d', settings.check_power_supply_path, val)
            return val
            

    def check_power(self, extra_message=''):
        if not self.is_ac_connected():
            notification = notifications.notify('Zwift Warning', '\n'.join(['AC adapter unplugged', extra_message]), timeout=0)
            while not self.is_ac_connected():
                time.sleep(0.5)
            notification.close()

    def start_power_check_thread(self):
        threading.Thread(target=self.__power_check_loop).start()


    def __power_check_loop(self):
        while True:
            self.check_power()

