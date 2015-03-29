import os
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages


@pytest.fixture(scope='module', params=["flake8==2.0.0", "flake8==2.4.0", "flake8"])
def venv(request):
    return virtual_environments.prepare_virtualenv([request.param])


def test_smoke(venv):
    output = run(venv)

    file_name = "tests/guinea-pigs/flake8/smoke.py"
    test1_name = "E302: " + file_name + ":3:1"
    test2_name = "W391: " + file_name + ":7:1"

    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': "pep8: " + file_name}),

            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFailed', {'name': test1_name, 'message': "E302: expected 2 blank lines, found 1"}),
            ServiceMessage('testFinished', {'name': test1_name}),

            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFailed', {'name': test2_name, 'message': "W391: blank line at end of file"}),
            ServiceMessage('testFinished', {'name': test2_name}),

            ServiceMessage('testSuiteFinished', {'name': "pep8: " + file_name}),
        ])


def run(venv):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    command = os.path.join(os.getcwd(), venv.bin, 'flake8.exe') + " --teamcity " + os.path.join("tests", "guinea-pigs", "flake8")
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            cwd=os.path.join(os.getcwd()), shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "$"))

    return output
