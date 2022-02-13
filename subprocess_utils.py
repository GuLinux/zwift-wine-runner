from settings import settings
import subprocess
import logging

logger = logging.getLogger(__name__)

def run(command, logname=None, check=True, *args, **kwargs):
    logfile_path = settings.logfile(logname) if logname else '/dev/null'
    with open(logfile_path, 'w') as logfile:
        try:
            process = subprocess.run(command, env=settings.env, stdout=logfile, stderr=subprocess.STDOUT, check=check, *args, **kwargs)
        except subprocess.CalledProcessError as e:
            logger.error('Process `{}` returned non-zero exit status: {}'.format(command, e.returncode))
            logger.error('Showing last 20 log lines from {}'.format(logfile_path))
            with open(logfile_path, 'r') as logfile:
                for line in logfile.readlines()[-20:-1]:
                    logger.error(line)
            raise RuntimeError('Process failed: `{}` returned {}'.format(command, e.returncode))
        return process

def popen(command, logname=None, *args, **kwargs):
    logfile_path = settings.logfile(logname)
    with open(logfile_path, 'w') as logfile:
        return subprocess.Popen(command, env=settings.env, stdout=logfile, stderr=subprocess.STDOUT, *args, **kwargs)

