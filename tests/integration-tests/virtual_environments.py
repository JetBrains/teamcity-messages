import os
import shutil
import subprocess
import virtualenv


_windows = os.name == 'nt'


class VirtualEnvDescription:
    def __init__(self, home, bin, python, pip):
        self.home = home
        self.bin = bin
        self.python = python
        self.pip = pip


def prepare_virtualenv(package_name=None, package_version=None):
    """
    Prepares a virtual environment.
    :rtype : VirtualEnvDescription
    """
    vdir = 'env'
    if os.path.exists(vdir):
        shutil.rmtree(vdir)
    virtualenv.create_environment(vdir)
    vbin = os.path.join(vdir, ('bin', 'Scripts')[_windows])
    exe_suffix = ("", ".exe")[_windows]
    vpython = os.path.join(vbin, 'python' + exe_suffix)
    vpip = os.path.join(vbin, 'pip' + exe_suffix)

    if package_name is not None:
        if package_version is None or package_version == "latest":
            package_spec = package_name
        else:
            package_spec = package_name + "==" + package_version
        subprocess.call([vpip, "install", package_spec])

    subprocess.call([vpython, "setup.py", "install"])
    return VirtualEnvDescription(home=vdir, bin=vbin, python=vpython, pip=vpip)
