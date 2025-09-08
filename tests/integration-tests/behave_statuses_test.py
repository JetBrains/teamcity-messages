# coding: utf8
import os

import pytest

import virtual_environments
from service_messages import parse_service_messages, match, ServiceMessage
from test_util import run_command, get_teamcity_messages_root

@pytest.fixture(scope='module', params=["behave==1.2.6", "behave"])
def venv(request):
    """
    Prepares a virtual environment for behave.
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv([request.param])


def test_step_with_exception(venv):
    output = run(venv, arguments="Simple.feature")
    fail_service_message = match(parse_service_messages(output), ServiceMessage('testFailed', {'name': 'Given I like BDD'}))
    error = fail_service_message.params['message']
    assert error is not None, 'Empty error message'
    assert 'raise RuntimeError("Failed step")' in error, 'Raised error is not mentioned in the error message'


def run(venv, options="", arguments=""):
    behave_wd = os.path.join(get_teamcity_messages_root(), "tests", "guinea-pigs", "behave")
    cwd = os.path.join(behave_wd, "statuses")
    behave = " ".join([os.path.join(venv.bin, "python"), os.path.join(behave_wd, "_behave_runner.py"), options, arguments])
    return run_command(behave, cwd=cwd)
