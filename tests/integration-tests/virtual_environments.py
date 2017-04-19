import os
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


def get_exe_suffix():
    return ("", ".exe")[_windows]


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

    vpip_install = [vpip, "install"]
    if (2, 5) <= sys.version_info < (2, 6):
        vpip_install.append("--insecure")

    venv_description = VirtualEnvDescription(home_dir=vdir, bin_dir=vbin, python=vpython, pip=vpip, packages=packages)

    env = get_clean_system_environment()
    env['PIP_DOWNLOAD_CACHE'] = os.path.abspath(os.path.join(vroot, "pip-download-cache"))

    # Cache environment
    done_flag_file = os.path.join(vdir, "done")
    if not os.path.exists(done_flag_file):
        if os.path.exists(vdir):
            shutil.rmtree(vdir)

        virtualenv.create_environment(vdir)

        for package_spec in packages:
            subprocess.check_call(vpip_install + [package_spec], env=env)

        open(done_flag_file, 'a').close()

    subprocess.check_call([vpython, "setup.py", "install"], env=env, cwd=get_teamcity_messages_root())

    return venv_description


def get_env_key(packages):
    key = "%d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
    key += "-" + os.name
    for package in packages:
        key += "-" + package.replace('=', '-')
    return key


def get_clean_system_environment():
    cur_env = os.environ.copy()
    env = dict([(k, cur_env[k]) for k in cur_env.keys() if not k.lower().startswith("python")])

    return env


def get_vroot():
    return os.path.join(tempfile.gettempdir(), "teamcity-python-venv")
