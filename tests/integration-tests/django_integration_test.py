__author__ = 'Leonid.Shalupov'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage


@pytest.fixture(scope='module', params=["latest"]) # '1.7'
def venv(request):
    return virtual_environments.prepare_virtualenv("django", request.param)


def test_smoke(venv):
    output = run(venv)

    ms = parse_service_messages(output)

    assert ms[0] >= ServiceMessage('testStarted', {'name': 'XXX identity'})
    assert ms[1] >= ServiceMessage('testFinished', {'name': 'XXX identity'})

def run(venv):
    # environment variables
    cur_env = os.environ.copy()
    env = dict([(k, cur_env[k]) for k in cur_env.keys() if not k.lower().startswith("python")])
    env['TEAMCITY_VERSION'] = "0.0.0"

    # Start the process and wait for its output
    command = os.path.join(os.getcwd(), venv.bin, 'python') + " manage.py test"
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            cwd=os.path.join(os.getcwd(), "tests", "guinea-pigs", "djangotest"), shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output
