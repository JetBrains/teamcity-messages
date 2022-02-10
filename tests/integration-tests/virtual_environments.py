import os
import re
import shutil
import subprocess
import sys
import tempfile

import virtualenv

from test_util import get_teamcity_messages_root


_windows = os.name == 'nt'


class VirtualEnvDescription:
    def __init__(self, home_dir, bin_dir, python, pip, packages):
        self.home = home_dir
        self.bin = bin_dir
        self.python = python
        self.pip = pip
        self.packages = packages

    def __str__(self):
        return "home:" + self.home + " pip:" + self.pip + " python:" + self.python + " packages:" + str(self.packages)

    def __unicode__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


def get_exe_suffix():
    return ("", ".exe")[_windows]


def _call(commands, **kwargs):
    print("Will call: " + str(commands))
    rc = subprocess.call(commands, **kwargs)
    if rc != 0:
        raise Exception("Error " + str(rc) + " calling " + str(commands))


def prepare_virtualenv(packages=()):
    """
    Prepares a virtual environment.
    :rtype : VirtualEnvDescription
    """
    vroot = get_vroot()
    env_key = get_env_key(packages)
    vdir = os.path.join(vroot, env_key)

    vbin = os.path.join(vdir, ('bin', 'Scripts')[_windows])
    vpython = os.path.join(vbin, 'python' + get_exe_suffix())
    vpip = os.path.join(vbin, 'pip' + get_exe_suffix())

    vpip_install = [vpip, "install", "--force-reinstall"]
    if (2, 5) <= sys.version_info < (2, 6):
        vpip_install.append("--insecure")

    venv_description = VirtualEnvDescription(home_dir=vdir, bin_dir=vbin, python=vpython, pip=vpip, packages=packages)
    print("Will install now")
    print(str(venv_description))

    env = get_clean_system_environment()
    env['PIP_DOWNLOAD_CACHE'] = os.path.abspath(os.path.join(vroot, "pip-download-cache"))

    # Cache environment
    done_flag_file = os.path.join(vdir, "done")
    if not os.path.exists(done_flag_file):
        if os.path.exists(vdir):
            shutil.rmtree(vdir)

        virtualenv.cli_run([vdir])
        # Update for newly created environment
        if sys.version_info >= (2, 7):
            _call([vpython, "-m", "pip", "install", "--upgrade", "pip", "setuptools"], env=env, cwd=get_teamcity_messages_root())

        for package_spec in packages:
            _call(vpip_install + [package_spec], env=env)

        open(done_flag_file, 'a').close()

    # Update for env.  that already exists: does not take long, but may save old envs.
    if sys.version_info >= (2, 7):
        _call([vpython, "-m", "pip", "install", "--upgrade", "pip", "setuptools"], env=env, cwd=get_teamcity_messages_root())
    _call([vpython, "setup.py", "install"], env=env, cwd=get_teamcity_messages_root())
    return venv_description


def get_env_key(packages):
    # Method must return short but unique folder name for interpreter and packages
    key = "%d%d" % (sys.version_info[0], sys.version_info[1])
    for package in packages:
        name_version = re.split("(==|<=|>=)", package)
        name = name_version[0]
        key += name if len(name) <= 4 else name[:2] + name[-2:]
        if len(name_version) == 3:
            key += re.sub("[^a-zA-Z0-9]+", "", name_version[2])
        key = re.sub("[^a-zA-Z0-9]+", "", key)

    return key


def get_clean_system_environment():
    cur_env = os.environ.copy()
    env = dict([(k, cur_env[k]) for k in cur_env.keys() if not k.lower().startswith("python")])

    return env


def get_vroot():
    return os.path.join(tempfile.gettempdir(), "teamcity-python-venv")
