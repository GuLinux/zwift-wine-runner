import readline
from settings import settings
from getpass import getpass
import xml.etree.ElementTree as ET
import os
import appdirs



def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()



def set_zwift_username():
    # TODO: path hardcoded, try to find out dynamically
    prefs_base_path = os.path.join(os.environ.get('HOME'), 'Documents', 'Zwift')
    prefs_path = os.path.join(prefs_base_path, 'prefs.xml')
    try:
        prefs = ET.parse(prefs_path)
    except FileNotFoundError:
        prefs = ET.ElementTree(ET.Element('ZWIFT'))
    zwift_element = prefs.getroot()
    user_element = zwift_element.find('USER') or ET.SubElement(zwift_element, 'USER')
    name_element = user_element.find('NAME') or ET.SubElement(user_element, 'NAME')
    name_element.text = settings.username
    os.makedirs(prefs_base_path, exist_ok=True)
    prefs.write(prefs_path, xml_declaration=False)

def configure():
    settings.username = rlinput('Please enter your Zwift username: ', prefill=settings.username)
    settings.password = getpass('Please enter your Zwift password for {}: '.format(settings.username))
    settings.dpi = rlinput('Please enter the DPI setting for Wine (usually 96, or 192 for HiDPI monitors): ', prefill=str(settings.dpi))
    settings.nvidia_offload = rlinput('Use NVIDIA Prime render offload? [y/n]: ', prefill='y' if settings.nvidia_offload else 'n').lower().startswith('y')
    settings.check_power_supply = rlinput('Check power supply is plugged before launching? [y/n]: ', prefill='y' if settings.check_power_supply else 'n').lower().startswith('y')
    settings.before_launch = rlinput('If you want to launch a custom command/script before launching zwift, please type it below: \n', prefill=settings.before_launch)
    set_zwift_username()

