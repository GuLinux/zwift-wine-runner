import requests
import logging
import os
from settings import settings
import subprocess_utils
import tempfile
from tqdm import tqdm
import shutil
from zipfile import ZipFile
from configure import set_zwift_username
from zwift_launcher import zwift_launcher

logger = logging.getLogger(__name__)

ZWIFT_WINDOWS_URL = 'https://cdn.zwift.com/app/ZwiftSetup.exe'
RUNFROMPROCESS_URL = 'https://www.nirsoft.net/utils/runfromprocess.zip'
EDGE_WEBVIEW_SETUP = 'https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/3717aef3-49b0-4c74-bf9c-8beee165346a/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
EDGE_SETUP = 'https://msedge.sf.dl.delivery.mp.microsoft.com/filestreamingservice/files/d1b0e946-e654-4d81-a42a-d581b8f3c40c/MicrosoftEdgeWebView2RuntimeInstallerX64.exe'
DOTNET_VERSIONS_TO_INSTALL = [
        # '35',
        # '40',
        # '472',
        '48',
        '20sp2',
    ]

class ZwiftInstaller:
    def __init__(self):
        self.filename = os.path.basename(ZWIFT_WINDOWS_URL)
        self.file_path = self.__tempfile(self.filename)

    def install_zwift(self):
        zwift_launcher.killall()
        # self.set_windows_version()
        self.__download(ZWIFT_WINDOWS_URL, self.file_path)
        logger.info('Installing Zwift')
        subprocess_utils.run(['wine', self.file_path, '/SP-', '/VERYSILENT', '/SUPPRESSMSGBOXES', '/NORESTART' '/NOCANCEL', '/NOICONS', '/NORESTARTAPPLICATIONS'], logname='install_zwift')
        set_zwift_username()

    def install_deps(self):
        self.set_windows_version()
        for version in DOTNET_VERSIONS_TO_INSTALL:
            logger.info(f'Installing dotnet{version}')
            subprocess_utils.run([
                'winetricks',
                '--unattended',
                '--force',
                f'dotnet{version}',
                'win10',
                ], logname=f'dotnet{version}')

        subprocess_utils.run(['winetricks', '--unattended', 'd3dcompiler_47'])
        # logger.info('Installing MsEdge webview runtime')
        # webview_file_path = self.__tempfile(os.path.basename(EDGE_WEBVIEW_SETUP))
        # self.__download(EDGE_WEBVIEW_SETUP, webview_file_path)
        # self.set_windows_version()
        # subprocess_utils.run(['wine', webview_file_path], logname='ms_edge_webview_setup')

        edge_file_path = self.__tempfile(os.path.basename(EDGE_SETUP))
        self.__download(EDGE_SETUP, edge_file_path)
        subprocess_utils.run(['wine', edge_file_path])

    def prune(self):
        zwift_launcher.killall()
        shutil.rmtree(settings.wine_prefix, ignore_errors=True)
        shutil.rmtree(settings.logs_path, ignore_errors=True)
        try:
            os.remove(settings.launcher_path)
        except FileNotFoundError:
            pass

    def setup_dpi(self, dpi):
        registry_text = '\n'.join(['REGEDIT4', '', '[HKEY_LOCAL_MACHINE\System\CurrentControlSet\Hardware Profiles\Current\Software\Fonts]', '"LogPixels"=dword:{:08x}']).format(dpi)
        dpi_reg_path = self.__tempfile('dpi.reg')
        with open(dpi_reg_path, 'w') as dpi_reg:
            dpi_reg.write(registry_text)

        logger.info('Applying DPI settings')
        subprocess_utils.run(['regedit', '/S', dpi_reg_path], logname='set_dpi')

    def set_windows_version(self, version='win10'):
        logger.info('Setting windows version to ' + version)
        subprocess_utils.run(['winetricks', version], logname='set_win10')

    def install_runfromprocess(self):
        runfromprocess_zip_file_path = self.__tempfile('runfromprocess.zip')
        self.__download(RUNFROMPROCESS_URL, runfromprocess_zip_file_path)
        logger.info('Installing RunFromProcess')
        runfromprocess_zip_file = ZipFile(runfromprocess_zip_file_path)
        runfromprocess_zip_file.extract(settings.runfromprocess_filename, settings.zwift_path)

    def install_desktop_icon(self):
        shutil.rmtree(os.path.join(os.environ.get('HOME'), '.local/share/applications/wine/Programs/Zwift'), ignore_errors=True)
        try:
            os.remove(os.path.join(os.environ.get('HOME'), 'Desktop/Zwift.desktop'))
        except FileNotFoundError:
            pass
        try:
            os.remove(os.path.join(os.environ.get('HOME'), 'Desktop/Zwift.lnk'))
        except FileNotFoundError:
            pass

        with open(settings.launcher_path, 'w') as desktop_file:
            desktop_file.write('''[Desktop Entry]
Comment=
Exec=/usr/bin/env python3 '{module_path}/zwift.py' run
Path={module_path}
Icon={module_path}/zwift-logo.png
Name=Zwift Wine launcher
NoDisplay=false
StartupNotify=true
Terminal=0
TerminalOptions=
Categories=Game
Type=Application
'''.format(module_path=settings.module_path))

    def install_all(self):
        self.setup_dpi(settings.dpi)
        self.install_deps()
        self.install_zwift()
        self.install_runfromprocess()
        self.install_desktop_icon()
        logger.info('Finished')


    def __tempfile(self, name):
        return os.path.join(tempfile.gettempdir(), name)

    def __download(self, url, file_path, filename=None):
        if not filename:
            filename = os.path.basename(file_path)
        response = requests.get(url, stream=True)
        with tqdm.wrapattr(open(file_path, "wb"), "write",
            miniters=1, desc=filename,
            total=int(response.headers.get('content-length', 0))) as fout:
            for chunk in response.iter_content(chunk_size=4096):
                fout.write(chunk)

zwift_installer = ZwiftInstaller()
