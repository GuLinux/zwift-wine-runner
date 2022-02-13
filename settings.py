import yaml
import os
import time
import appdirs
import keyring
import pathlib
from notifications import notifications


class Settings:
    APPNAME = 'Zwift-Wine-Runner'
    def __init__(self):
        self.config_file_path = os.path.join(appdirs.user_config_dir(Settings.APPNAME), 'zwift-wine-runner.yaml')
        self.config = dict()
        self.load()

    @property
    def username(self):
        return self.config.get('username')

    @username.setter
    def username(self, value):
        self.config['username'] = value
        self.save()

    @property
    def password(self):
        return keyring.get_password(Settings.APPNAME, self.username)

    @password.setter
    def password(self, value):
        keyring.set_password(Settings.APPNAME, self.username, value)

    @property
    def wine_prefix(self):
        return self.config.get('wine_prefix', appdirs.user_data_dir(Settings.APPNAME))

    @wine_prefix.setter
    def wine_prefix(self, value):
        self.config['wine_prefix'] = value
        self.save()


    @property
    def before_launch(self):
        return self.config.get('before_launch', '')

    @before_launch.setter
    def before_launch(self, value):
        self.config['before_launch'] = value
        self.save()

    @property
    def dpi(self):
        return int(self.config.get('dpi', 96))

    @dpi.setter
    def dpi(self, value):
        self.config['dpi'] = value
        self.save()

    @property
    def wine_arch(self):
        return 'win64'

    @property
    def zwift_path(self):
        return os.path.join(self.wine_prefix, 'drive_c/Program Files (x86)/Zwift')

    @property
    def runfromprocess_filename(self):
        return 'RunFromProcess-x64.exe'

    @property
    def nvidia_offload(self):
        return self.config.get('nvidia_offload', False)

    @nvidia_offload.setter
    def nvidia_offload(self, value):
        self.config['nvidia_offload'] = value
        self.save()

    @property
    def check_power_supply(self):
        return self.config.get('check_power_supply', False)

    @check_power_supply.setter
    def check_power_supply(self, value):
        self.config['check_power_supply'] = value
        self.save()

    @property
    def check_power_supply_path(self):
        return self.config.get('check_power_supply_path', '/sys/class/power_supply/AC/online')

    @check_power_supply_path.setter
    def check_power_supply_path(self, value):
        self.config['check_power_supply_path'] = value
        self.save()

    @property
    def update_checking_timeout(self):
        return self.config.get('update_checking_timeout', 20)

    @update_checking_timeout.setter
    def update_checking_timeout(self, value):
        self.config['update_checking_timeout'] = value
        self.save()

    @property
    def password_field_checking_timeout(self):
        return self.config.get('password_field_checking_timeout', 50)

    @password_field_checking_timeout.setter
    def password_field_checking_timeout(self, value):
        self.config['password_field_checking_timeout'] = value
        self.save()

    @property
    def env(self):
        env = os.environ.copy()
        env['MESA_GL_VERSION_OVERRIDE'] = '3.1'
        env['WINEPREFIX'] = self.wine_prefix
        env['WINEARCH']=self.wine_arch
        #env['WINEDLLOVERRIDES']='mscoree,mshtml='
        if self.nvidia_offload:
            env['__NV_PRIME_RENDER_OFFLOAD'] ='1'
            env['__GLX_VENDOR_LIBRARY_NAME'] ='nvidia' 
        return env

    @property
    def module_path(self):
        return pathlib.Path(__file__).parent.resolve()

    @property
    def logs_path(self):
        return os.path.join(appdirs.user_cache_dir(Settings.APPNAME), 'logs')

    @property
    def launcher_path(self):
        return os.path.join(appdirs.user_data_dir(), 'applications', f'{Settings.APPNAME}.desktop')

    def get_resource(self, filename):
        return os.path.join(self.module_path, filename)

    def to_map(self):
        return {
                'username': self.username,
                'nvidia_offload': self.nvidia_offload,
                'wine_prefix': self.wine_prefix,
                'check_power_supply': self.check_power_supply,
                'check_power_supply_path': self.check_power_supply_path,
                'update_checking_timeout': self.update_checking_timeout,
                'password_field_checking_timeout': self.password_field_checking_timeout,
                'before_launch': self.before_launch,
                'dpi': self.dpi,
            }

    def reset(self):
        self.config = dict()
        self.save()

    def load(self):
        try:
            with open(self.config_file_path, 'r') as config_file:
                self.config = yaml.load(config_file, Loader=yaml.Loader)
        except Exception as e:
            pass

    def save(self):
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
        with open(self.config_file_path, 'w') as config_file:
            yaml.dump(self.to_map(), config_file, Dumper=yaml.Dumper)

    def logfile(self, name):
        os.makedirs(self.logs_path, exist_ok=True)
        return os.path.join(self.logs_path, '{}-{}.log'.format(time.strftime('%Y%m%dT%H%M%S'), name))

    def check(self):
        if not self.username or not self.password:
            notifications.notify('Zwift', 'Invalid settings, please configure the app first')
            raise RuntimeError('Invalid settings, please run `configure` first')

    def __str__(self):
        return yaml.dump(self.to_map(), Dumper=yaml.Dumper)

    def __repr__(self):
        return self.__str__()


settings = Settings()

