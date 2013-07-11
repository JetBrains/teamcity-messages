import atexit
import sys
import shutil
import tempfile
from os.path import join
from test import tc_msg, FRAMEWORKS, clean_directory, find_script, eggs, generate_test_name


__author__ = 'Leonid Bushuev'


def main():

    success = runner()
    sys.exit(0 if success else 1)





def runner():
    temp = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, temp)

    ok = True
    for fw in FRAMEWORKS:
        fw_name = fw.name
        fw_version = fw.version
        test = generate_test_name(fw_name, fw_version)
        tc_msg("##teamcity[testStarted name='%s']" % test)
        try:
            result = run(fw, temp)
            if result < 2:
                ok = False
        finally:
            tc_msg("##teamcity[testFinished name='%s']" % test)

    return ok


def run(fw, temp):
    venv = join(temp, "venv-" + fw.name)
    clean_directory(venv)

    from test_support import virtualenv

    # virtualenv.logger = virtualenv.Logger([(virtualenv.Logger.DEBUG, sys.stdout)])
    virtualenv.DISTRIBUTE_SETUP_PY = virtualenv.DISTRIBUTE_SETUP_PY.replace("0.6.28", "0.6.34")
    virtualenv.create_environment(venv, use_distribute=True,
                                  never_download=True, search_dirs=[eggs])

    import subprocess

    python = find_script(venv, "python")
    rc = subprocess.call([python, "test.py", fw.name, fw.version, venv])

    return rc



##########################
if __name__ == "__main__":
    main()
