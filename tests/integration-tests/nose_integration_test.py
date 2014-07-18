__author__ = 'Leonid.Bushuev'

import re
import os
import shutil
import subprocess
import pytest
import virtualenv


windows = os.name == 'nt'


class virtual_env_desc:
    home = ""
    bin = ""
    python = ""
    pip = ""
    def __init__(self, home, bin, python, pip):
        self.home = home
        self.bin = bin
        self.python = python
        self.pip = pip


@pytest.fixture(scope='module')
def venv():
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_env_desc
    """
    vdir = 'env'
    if (os.path.exists(vdir)):
        shutil.rmtree(vdir)
    virtualenv.create_environment(vdir)
    vbin = os.path.join(vdir, ('bin','Scripts')[windows])
    exe_suffix = ("",".exe")[windows]
    vpython = os.path.join(vbin, 'python'+exe_suffix)
    vpip = os.path.join(vbin, 'pip'+exe_suffix)
    subprocess.call([vpip, "install", "nose"])
    subprocess.call([vpython, "setup.py", "install"])
    return virtual_env_desc(home=vdir, bin=vbin, python=vpython, pip=vpip)


def test_pass(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')

    #print(output)

    output = normalizeOutput(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    assert "##teamcity[testSuiteStarted timestamp='TTT' name='nose-guinea-pig']" in output
    assert "##teamcity[testSuiteStarted timestamp='TTT' name='GuineaPig']" in output
    assert "##teamcity[testStarted timestamp='TTT' name='test_pass (nose-guinea-pig.GuineaPig)']" in output
    assert "##teamcity[testFinished timestamp='TTT' duration='0' name='test_pass (nose-guinea-pig.GuineaPig)']" in output
    assert "##teamcity[testSuiteFinished timestamp='TTT' name='GuineaPig']" in output
    assert "##teamcity[testSuiteFinished timestamp='TTT' name='nose-guinea-pig']" in output


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')

    #print(output)

    output = normalizeOutput(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    assert "##teamcity[testSuiteStarted timestamp='TTT' name='nose-guinea-pig']" in output
    assert "##teamcity[testSuiteStarted timestamp='TTT' name='GuineaPig']" in output
    assert "##teamcity[testStarted timestamp='TTT' name='test_fail (nose-guinea-pig.GuineaPig)']" in output
    assert "##teamcity[testFailed" in output
    assert "2 * 2 == 5" in output
    assert "##teamcity[testFinished timestamp='TTT' duration='0' name='test_fail (nose-guinea-pig.GuineaPig)']" in output
    assert "##teamcity[testSuiteFinished timestamp='TTT' name='GuineaPig']" in output
    assert "##teamcity[testSuiteFinished timestamp='TTT' name='nose-guinea-pig']" in output


def run(venv, file, clazz, test):
    """
    Executes the specified test using nose
    """

    # environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = venv.home
    env['TEAMCITY_VERSION'] = "0.0.0"
    env['TEAMCITY_PROJECT'] = "TEST"

    # Start the process and wait for its output
    command = os.path.join(venv.bin, 'nosetests') + " -v " \
              + os.path.join('tests', 'guinea-pigs', file) + " " \
              + clazz + ':' + test
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output


def normalizeOutput(output):
    output = re.sub(r"timestamp='\d+.*?\d+'", "timestamp='TTT'", output)
    output = re.sub(r"duration='\d+'", "duration='0'", output)
    return output



