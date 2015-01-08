import sys

__author__ = 'Leonid.Shalupov'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage


@pytest.fixture(scope='module', params=["1.6", "1.7", "latest"])
def venv(request):
    if request.param != "1.6" and sys.version_info < (2, 7):
        pytest.skip("Django 1.7+ requires Python 2.7+")
    return virtual_environments.prepare_virtualenv("django", request.param)


def test_smoke(venv):
    output = run(venv)

    ms = parse_service_messages(output)

    assert ms[0] >= ServiceMessage('testStarted', {'name': 'test_smoke.SmokeTestCase.test_xxx (XXX identity)'})
    assert ms[1] >= ServiceMessage('testFinished', {'name': 'test_smoke.SmokeTestCase.test_xxx (XXX identity)'})


def run(venv):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    command = os.path.join(os.getcwd(), venv.bin, 'python') + " manage.py test"
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            cwd=os.path.join(os.getcwd(), "tests", "guinea-pigs", "djangotest"), shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output)

    return output
