from __future__ import print_function

__author__ = 'Leonid.Shalupov'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage


@pytest.fixture(scope='module', params=["latest"])
def venv(request):
    """
    Prepares a virtual environment for py.test
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv("pytest", request.param)


def test_hierarchy(venv):
    output = run(venv, os.path.join('namespace'))

    ms = parse_service_messages(output)
    assert ms[0] >= ServiceMessage('testSuiteStarted', {'name': 'tests.guinea-pigs.pytest.namespace.pig_test_py'})
    assert ms[1] >= ServiceMessage('testStarted', {'name': 'TestSmoke.test_smoke'})
    assert ms[2] >= ServiceMessage('testFinished', {'name': 'TestSmoke.test_smoke'})
    assert ms[3] >= ServiceMessage('testSuiteFinished', {'name': 'tests.guinea-pigs.pytest.namespace.pig_test_py'})


def test_custom_test_items(venv):
    output = run(venv, os.path.join('custom'))

    ms = parse_service_messages(output)
    assert ms[0] >= ServiceMessage('testSuiteStarted', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml'})
    assert ms[1] >= ServiceMessage('testStarted', {'name': 'line1'})
    assert ms[2] >= ServiceMessage('testFinished', {'name': 'line1'})
    assert ms[3] >= ServiceMessage('testSuiteFinished', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml'})


def run(venv, file, test=None):
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.abspath(os.path.join('tests', 'guinea-pigs', 'pytest'))
    env['TEAMCITY_VERSION'] = "0.0.0"
    env['TEAMCITY_PROJECT'] = "TEST"

    print(env['PYTHONPATH'])
    # Start the process and wait for its output
    test_suffix = ("::" + test) if test is not None else ""
    command = os.path.join(venv.bin, 'py.test') + " --teamcity " + \
              os.path.join('tests', 'guinea-pigs', 'pytest', file) + test_suffix
    print("RUN: " + command)
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output
