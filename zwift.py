#!/usr/bin/env python3
import subprocess
import time
import argparse
import logging
from settings import settings
from zwift_installer import zwift_installer
from zwift_launcher import zwift_launcher
from configure import configure

actions = {
    'run': 'Start Zwift from the configured Wine prefix (default)',
    'install': 'Install Zwift, automatically downloading the setup file and configuring the Wine environment',
    'configure': 'Configure Zwift Wine runner (username, password, launcher options)',
    'reset': 'Reset Zwift Wine runner configuration',
    'prune': 'Remove all files from Zwift Wine prefix',
    'kill': 'Kill all processes in Zwift wine prefix',
    'check-server': 'Check if ZwiftLauncher is running',
    'settings': 'Print zwift launcher settings',
}

actions_help = ['{}: {}'.format(key, value) for key, value in actions.items()]

parser = argparse.ArgumentParser(description='Zwift Wine setup and launcher', epilog='Available actions:\n\t{}'.format('\n\t'.join(actions_help)), formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('action', type=str, choices=actions.keys(), default='run', nargs='?')
parser.add_argument('-l', '--log-level', type=str, choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], default='INFO')
parser.add_argument('-s', '--only-server', action='store_true', help='Only launch ZwiftLauncher server (useful if you want to allow for updates)')
parser.add_argument('--skip-deps', action='store_true', help='Only launch ZwiftLauncher server (useful if you want to allow for updates)')
args=parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log_level))
logging.debug(args)

if args.action == 'reset':
    settings.reset()
elif args.action == 'prune':
    zwift_launcher.killall()
    zwift_installer.prune()
elif args.action == 'kill':
    zwift_launcher.killall()
elif args.action == 'install':
    settings.check()
    if args.skip_deps:
        zwift_installer.install_zwift()
    else:
        zwift_installer.install_all()
elif args.action == 'configure':
    configure()
elif args.action == 'check-server':
    print('ZwiftLauncher process is running' if zwift_launcher.launcher_running() else 'ZwiftInstaller process is NOT running')
elif args.action == 'settings':
    print('# Settings in {}'.format(settings.config_file_path))
    print(settings)
elif args.action == 'run':
    settings.check()
    if args.only_server:
        zwift_launcher.run_launcher()
    else:
        zwift_launcher.run_launcher_and_zwift()
