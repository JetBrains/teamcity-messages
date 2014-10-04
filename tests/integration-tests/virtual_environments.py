import os
import shutil
import subprocess
import sys
import tempfile
import virtualenv


_windows = os.name == 'nt'


class VirtualEnvDescription:
    def __init__(self, home_dir, bin_dir, python, pip):
        self.home = home_dir
        self.bin = bin_dir
        self.python = python
        self.pip = pip


def prepare_virtualenv(package_name=None, package_version=None):
    """
    Prepares a virtual environment.
    :rtype : VirtualEnvDescription
    """
    vroot = get_vroot()
    env_key = get_env_key(package_name, package_version)
    vdir = os.path.join(vroot, env_key)

    vbin = os.path.join(vdir, ('bin', 'Scripts')[_windows])
    exe_suffix = ("", ".exe")[_windows]
    vpython = os.path.join(vbin, 'python' + exe_suffix)
    vpip = os.path.join(vbin, 'pip' + exe_suffix)
    venv_description = VirtualEnvDescription(home_dir=vdir, bin_dir=vbin, python=vpython, pip=vpip)

    env = get_clean_system_environment()
    env['PIP_DOWNLOAD_CACHE'] = os.path.abspath(os.path.join(vroot, "pip-download-cache"))

    # Cache environment
    done_flag_file = os.path.join(vdir, "done")
    if not os.path.exists(done_flag_file):
        if os.path.exists(vdir):
            shutil.rmtree(vdir)

        virtualenv.create_environment(vdir)

        if package_name is not None:
            if package_version is None or package_version == "latest":
                package_spec = package_name
            else:
                package_spec = package_name + "==" + package_version
            subprocess.call([vpip, "install", package_spec], env=env)

        open(done_flag_file, 'a').close()

    subprocess.call([vpython, "setup.py", "install"], env=env)

    return venv_description


def get_env_key(package_name, package_version):
    key = "%d.%d.%d" % (sys.version_info[0], sys.version_info[1], sys.version_info[2])
    key += "-" + os.name
    if package_name is not None:
        key += "-" + package_name
    if package_version is not None:
        key += "-" + package_version
    return key


def get_clean_system_environment():
    cur_env = os.environ.copy()
    env = dict([(k, cur_env[k]) for k in cur_env.keys() if not k.lower().startswith("python")])

    return env


def get_vroot():
    return os.path.join(tempfile.gettempdir(), "teamcity-python-venv")
