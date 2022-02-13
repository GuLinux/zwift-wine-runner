import gi
import threading

gi.require_version('Notify', '0.7')
gi.require_version('Gtk', '3.0')
from gi.repository import Notify
from gi.repository import Gtk


class Notifications:
    def __init__(self):
        Notify.init('Zwift')

    def notify(self, summary, message, timeout=10, show=True):
        from settings import settings
        notification = Notify.Notification.new(summary, message, settings.get_resource('zwift-logo'))
        notification.set_timeout(timeout * 1000)
        if show:
            notification.show()
        return notification

    def notify_callback(self, summary, message, timeout=10, actions={}):
        notification = self.notify(summary, message, timeout, show=False)
        def on_closed(n):
            Gtk.main_quit()

        def on_action(n, a):
            actions[a]['callback']()
            Gtk.main_quit()

        for key, value in actions.items():
            notification.add_action(key, value['label'], on_action)
        notification.connect('closed', on_closed)
        notification.show()
        t = threading.Thread(target=Gtk.main)
        t.start()
        notification.main_thread = t
        return notification




notifications = Notifications()
