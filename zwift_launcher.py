import subprocess_utils
import os
import logging
import psutil
import time

from settings import settings
from ac_adapter_check import ACAdapterCheck
from screen_manager import ScreenManager
from notifications import notifications
from window_manager import window_manager
import subprocess

logger = logging.getLogger(__name__)

class ZwiftLauncher:
    def __init__(self):
        self.launcher_process = None
        self.ac_adapter_check = ACAdapterCheck()
        self.screen_manager = ScreenManager()

    def run_launcher(self):
        if self.launcher_running():
            raise RuntimeError('Launcher already started')
        logger.info('Starting ZwiftLauncher')
        self.launcher_process = subprocess_utils.popen(['wine', 'ZwiftLauncher.exe'], logname='zwift_launcher', cwd=settings.zwift_path)
        window_manager.wait_for_window('Zwift Launcher', timeout=300)

    def run_zwift(self):
        if settings.check_power_supply:
            logger.info('Checking for power supply')
            self.ac_adapter_check.check_power(extra_message='Please plug the power supply to continue')

        logger.info('Launching Zwift')
        zwift_process = subprocess_utils.popen(['wine', settings.runfromprocess_filename, 'ZwiftLauncher.exe', 'ZwiftApp.exe'], logname='zwift', cwd=settings.zwift_path)
        window_manager.wait_for_window('Zwift', timeout=300)

        logger.debug('Checking for password box')
        if self.screen_manager.find('password_box', on_found=lambda found: self.screen_manager.write(settings.password, enter=True), timeout=settings.password_field_checking_timeout):
            logger.info('Password typed successfully')
        else:
            logger.warning('Password box not found, you\'ll have to type your password manually :(')

        while window_manager.find_windows_by_name('Zwift'):
            time.sleep(5)

    def run_launcher_and_zwift(self):
        if settings.before_launch:
            subprocess.run(settings.before_launch, check=True, shell=True)
        if not self.launcher_running():
            self.run_launcher()
        else:
            logger.info('ZwiftLauncher already running')
        matches = []
        logger.info('Checking for update process')
        t1 = self.screen_manager.find_async('preparing_update', on_found=lambda found: matches.append(found), timeout=settings.update_checking_timeout)
        t2 = self.screen_manager.find_async('updating', on_found=lambda found: matches.append(found), timeout=settings.update_checking_timeout)
        
        def skip_callback():
            t1.stop()
            t2.stop()

        notify_actions = {
            'skip': { 'label': 'Skip', 'callback': skip_callback },
        }

        updates_notification = notifications.notify_callback('Zwift', 'Checking for Zwift updates on launcher window', timeout=settings.update_checking_timeout, actions=notify_actions)

        t1.join()
        t2.join()
        updates_notification.main_thread.join()

        if [m for m in matches if m]:
            logger.info('Zwift is updating, skipping main launch')
            notifications.notify('Zwift', 'Zwift is updating, please launch again when update finishes')
            return
        self.run_zwift()
        self.killall()
        # if self.launcher_process:
        #     self.terminate_launcher()

    def killall(self):
        subprocess_utils.run(['wineserver', '-k'], logname='kill_wineserver', check=False)

    def terminate_launcher(self):
        process = self.find_launcher_process()
        if not process:
            raise RuntimeError('Launcher not yet started')
        logger.info('Terminating Zwift Launcher')
        process.terminate()
        process.wait()

    def launcher_running(self):
        return bool(self.find_launcher_process())

    def find_launcher_process(self):
        processes = [p for p in psutil.process_iter() if 'ZwiftLauncher.exe' in ' '.join(p.cmdline())]
        return processes[0] if processes else None

zwift_launcher = ZwiftLauncher()
