from Xlib import display
from Xlib.error import BadWindow
import time

class WindowManager:
    def __init__(self):
        pass

    def find_windows_by_name(self, name):
        try:
            return self.find_by(lambda w: w.get_wm_name() == name)
        except BadWindow:
            return None

    def find_windows_including_name(self, name):
        try:
            return self.find_by(lambda w: w.get_wm_name() and name in w.get_wm_name())
        except BadWindow:
            return None


    def find_by(self, f):
        try:
            return [window for window in self.__get_all_windows() if f(window)]
        except BadWindow:
            return None


    def wait_for_window(self, window_name, timeout=None):
        started = time.time()
        while not self.find_windows_by_name(window_name) or (timeout and time.time() - started >= timeout):
            time.sleep(0.2)

    def __get_all_windows(self):
        return self.__get_children(self.__get_root(), [])

    def __get_root(self):
        return display.Display().screen().root

    def __get_children(self, window, windows_list=[]):
        try:
            windows_list.extend(window.query_tree().children)
            for w in window.query_tree().children:
                self.__get_children(w, windows_list)

        except BadWindow:
            pass
        return windows_list



window_manager = WindowManager()

