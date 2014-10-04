from __future__ import print_function

__author__ = 'Leonid.Shalupov'

import os
import sys
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage, assert_service_messages


@pytest.fixture(scope='module')
def venv(request):
    """
    Prepares a virtual environment for unittest, no extra packages required
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv()


def test_nested_suits(venv):
    output = run_directly(venv, 'nested_suits.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.runTest'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.runTest'}),
        ])


def test_docstring(venv):
    output = run_directly(venv, 'docstring.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.A test'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.A test'}),
        ])


def test_assert(venv):
    output = run_directly(venv, 'assert.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.runTest'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.runTest', 'message': 'Failure'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.runTest'}),
        ])

    assert ms[1].params['details'].index("assert 1 == 0") > 0


def test_fail(venv):
    output = run_directly(venv, 'fail_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.runTest'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.runTest', 'message': 'Failure'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.runTest'}),
        ])

    assert ms[1].params['details'].index('fail("Grr")') > 0


def test_setup_error(venv):
    output = run_directly(venv, 'setup_error.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.runTest'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.runTest', 'message': 'Error'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.runTest'}),
        ])

    assert ms[1].params['details'].index("RRR") > 0
    assert ms[1].params['details'].index("setUp") > 0


def test_teardown_error(venv):
    output = run_directly(venv, 'teardown_error.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.runTest'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.runTest', 'message': 'Error'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.runTest'}),
        ])

    assert ms[1].params['details'].index("RRR") > 0
    assert ms[1].params['details'].index("tearDown") > 0


def test_doctests(venv):
    output = run_directly(venv, 'doctests.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.factorial'}),
            ServiceMessage('testFinished', {'name': '__main__.factorial'}),
        ])


@pytest.mark.skipif(sys.version_info < (2, 7), reason="skip requires Python 2.7+")
def test_skip(venv):
    output = run_directly(venv, 'skip_test.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestSkip.test_skip_me'}),
            ServiceMessage('testIgnored', {'name': '__main__.TestSkip.test_skip_me', 'message': 'Skipped: testing skipping'}),
            ServiceMessage('testFinished', {'name': '__main__.TestSkip.test_skip_me'}),
        ])


@pytest.mark.skipif(sys.version_info < (2, 7), reason="expectedFailure requires Python 2.7+")
def test_expected_failure(venv):
    output = run_directly(venv, 'expected_failure.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestSkip.test_expected_failure'}),
            ServiceMessage('testIgnored', {'name': '__main__.TestSkip.test_expected_failure'}),
            ServiceMessage('testFinished', {'name': '__main__.TestSkip.test_expected_failure'}),
        ])
    assert ms[1].params['message'].find("Expected failure") == 0
    assert ms[1].params['message'].find("this should happen unfortunately") > 0


@pytest.mark.skipif(sys.version_info < (2, 7), reason="unexpected_success requires Python 2.7+")
def test_unexpected_success(venv):
    output = run_directly(venv, 'unexpected_success.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestSkip.test_unexpected_success'}),
            ServiceMessage('testFailed', {'name': '__main__.TestSkip.test_unexpected_success',
                                          'details': "Test should not succeed since it|'s marked with @unittest.expectedFailure"}),
            ServiceMessage('testFinished', {'name': '__main__.TestSkip.test_unexpected_success'}),
        ])


@pytest.mark.skipif(sys.version_info < (2, 7), reason="unittest discovery requires Python 2.7+")
def test_discovery(venv):
    output = run_directly(venv, 'discovery.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
            ServiceMessage('testFinished', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
        ])


@pytest.mark.skipif(sys.version_info < (2, 7), reason="unittest discovery requires Python 2.7+")
def test_discovery_errors(venv):
    output = run_directly(venv, 'discovery_errors.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'unittest.loader.ModuleImportFailure.testsimple'}),
            ServiceMessage('testFailed', {'name': 'unittest.loader.ModuleImportFailure.testsimple', 'message': 'Error'}),
            ServiceMessage('testFinished', {'name': 'unittest.loader.ModuleImportFailure.testsimple'}),
        ])

    assert ms[1].params['details'].index("ImportError") > 0


def test_setup_module_error(venv):
    output = run_directly(venv, 'setup_module_error.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.setUpModule'}),
            ServiceMessage('testFailed', {'name': '__main__.setUpModule', 'message': 'Failure'}),
            ServiceMessage('testFinished', {'name': '__main__.setUpModule'}),
        ])

    assert ms[1].params['details'].index("assert 1 == 0") > 0


def run_directly(venv, file):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    # Start the process and wait for its output
    command = os.path.join(venv.bin, 'python') + " " + os.path.join('tests', 'guinea-pigs', 'unittest', file)
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "*"))

    return output
