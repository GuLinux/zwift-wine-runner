#!/usr/bin/env python3
import time
import pyautogui
import logging
import threading
from settings import settings

logger = logging.getLogger(__name__)


class ScreenManager:
    class Job:
        def __init__(self, screen_manager, *args, **kwargs):
            self.screen_manager = screen_manager
            self.is_stopping = False
            self.bg_thread = threading.Thread(target=self.__find, args=args, kwargs=kwargs)
            self.bg_thread.start()

        def join(self, *args):
            return self.bg_thread.join(*args)

        def stop(self):
            self.is_stopping = True

        def __find(self, *args, **kwargs):
            self.screen_manager.find(*args, **kwargs, job=self)
            
    def __init__(self):
        pass

    def find_async(self, *args, **kwargs):
        return ScreenManager.Job(self, *args, **kwargs)

    def find(self, image, timeout=5*60, region=None, on_found=None, grayscale=True, confidence=0.9, job=None):
        image_match_found = None
        started = time.time()
        image_match = settings.get_resource('{}.png'.format(image))

        logger.debug('Trying to find {} on screen, timeout={}, region={}, grayscale={}, confidence={}, on_found={}'.format(image_match, timeout, region, grayscale, confidence, on_found))
        while not image_match_found and time.time() - started < timeout and (not job or not job.is_stopping):
            image_match_found = pyautogui.locateOnScreen(image_match, grayscale=grayscale, confidence=confidence, region=region)
            if not image_match_found:
                logger.debug('Not found, retrying')
        if image_match_found and on_found:
            on_found(image_match_found)
        logger.debug(image_match_found)
        return image_match_found

    def write(self, text, enter=False):
        pyautogui.write(text)
        if enter:
            self.press('enter')

    def press(self, key):
        pyautogui.press(key)


