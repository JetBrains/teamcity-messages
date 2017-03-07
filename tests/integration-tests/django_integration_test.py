import sys
import os
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages


@pytest.fixture(scope='module', params=["django==1.6", "django==1.7", "django"])
def venv(request):
    if sys.version_info < (2, 6):
        pytest.skip("Django (all versions) requires Python 2.6+")

    if request.param != "django==1.6" and sys.version_info < (2, 7):
        pytest.skip("Django 1.7+ requires Python 2.7+")
    if (request.param == "django==1.6" or request.param == "django==1.7") and sys.version_info >= (3, 5):
        pytest.skip("Django supports Python 3.5+ since 1.8.6")
    if request.param == "django":
        if sys.version_info[0] == 2 and sys.version_info < (2, 7):
            pytest.skip("Django 1.9+ requires Python 2.7+")
        if sys.version_info[0] == 3 and sys.version_info < (3, 4):
            pytest.skip("Django 1.9+ requires Python 3.4+")
    return virtual_environments.prepare_virtualenv([request.param])


def test_smoke(venv):
    output = run(venv)

    test_name = "test_smoke.SmokeTestCase.test_xxx (XXX identity)"
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


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
