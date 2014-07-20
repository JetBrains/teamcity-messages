__author__ = 'Leonid.Bushuev'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage


@pytest.fixture(scope='module', params=['1.2.1', '1.3.0', "latest"])
def venv(request):
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv("nose", request.param)


def test_pass(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parse_service_messages(output)

    assert ms[0] >= ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= ServiceMessage('testStarted', {'name': 'test_pass'})
    assert ms[3] >= ServiceMessage('testFinished', {'name': 'test_pass'})
    assert ms[4] >= ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[5] >= ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'})


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parse_service_messages(output)

    assert ms[0] >= ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= ServiceMessage('testStarted', {'name': 'test_fail'})
    assert ms[3] >= ServiceMessage('testFailed', {'name': 'test_fail', 'details': 'Traceback'})
    assert ms[4] >= ServiceMessage('testFinished', {'name': 'test_fail'})
    assert ms[5] >= ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[6] >= ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'})

    assert "2 * 2 == 5" in output


def test_fail_with_msg(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_with_msg')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parse_service_messages(output)

    assert ms[0] >= ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= ServiceMessage('testStarted', {'name': 'test_fail'})
    assert ms[3] >= ServiceMessage('testFailed',
                                    {'name': 'test_fail', 'details': 'Bitte keine Werbung'})
    assert ms[4] >= ServiceMessage('testFinished', {'name': 'test_fail'})
    assert ms[5] >= ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[6] >= ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'})


def test_fail_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_output')

    print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parse_service_messages(output)

    assert ms[3] >= ServiceMessage('testFailed', {'name': 'test_fail', 'details': 'Output line 1'})
    assert ms[3] >= ServiceMessage('testFailed', {'name': 'test_fail', 'details': 'Output line 2'})
    assert ms[3] >= ServiceMessage('testFailed', {'name': 'test_fail', 'details': 'Output line 3'})


def run(venv, file, clazz, test):
    """
    Executes the specified test using nose
    """

    # environment variables
    env = os.environ.copy()
    env['TEAMCITY_VERSION'] = "0.0.0"

    # Start the process and wait for its output
    command = os.path.join(venv.bin, 'nosetests') + " -v " \
              + os.path.join('tests', 'guinea-pigs', file) + ":" + clazz + '.' + test
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output
