import os
import sys
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages


@pytest.fixture(scope='module')
def venv(request):
    """
    Prepares a virtual environment for unittest, no extra packages required
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv()


def test_nested_suits(venv):
    output = run_directly(venv, 'nested_suits.py')
    test_name = '__main__.TestXXX.runTest'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'captureStandardOutput': 'true', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_docstring(venv):
    output = run_directly(venv, 'docstring.py')
    test_name = '__main__.TestXXX.runTest (A test_)'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_assert(venv):
    output = run_directly(venv, 'assert.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("assert 1 == 0") > 0


def test_fail(venv):
    output = run_directly(venv, 'fail_test.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index('fail("Grr")') > 0


def test_setup_error(venv):
    output = run_directly(venv, 'setup_error.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Error', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("RRR") > 0
    assert ms[1].params['details'].index("setUp") > 0


def test_teardown_error(venv):
    output = run_directly(venv, 'teardown_error.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Error', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("RRR") > 0
    assert ms[1].params['details'].index("tearDown") > 0


def test_doctests(venv):
    output = run_directly(venv, 'doctests.py')
    test_name = '__main__.factorial'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_skip(venv):
    if sys.version_info < (2, 7):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2==0.5.1"])

    output = run_directly(venv, 'skip_test.py')
    test_name = '__main__.TestSkip.test_skip_me'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'message': 'Skipped: testing skipping', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="expectedFailure requires Python 2.7+")
def test_expected_failure(venv):
    output = run_directly(venv, 'expected_failure.py')
    test_name = '__main__.TestSkip.test_expected_failure'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert ms[1].params['message'].find("Expected failure") == 0
    assert ms[1].params['message'].find("this should happen unfortunately") > 0


@pytest.mark.skipif("sys.version_info < (3, 4)", reason="subtests require Python 3.4+")
def test_subtest_ok(venv):
    output = run_directly(venv, 'subtest_ok.py')
    test_name = '__main__.TestXXX.testSubtestSuccess'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': test_name + ' (i=0): ok|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': test_name + ' (i=1): ok|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (3, 4)", reason="subtests require Python 3.4+")
def test_subtest_error(venv):
    output = run_directly(venv, 'subtest_error.py')
    test_name = '__main__.TestXXX.testSubtestError'
    subtest_name = test_name + ' (i=|\'abc.xxx|\')'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': test_name + ' (i=0): ok|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdErr', {'out': subtest_name + ': error|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'message': 'Subtest failed', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert ms[3].params['details'].find(subtest_name) == 0
    assert ms[3].params['details'].find("RuntimeError") > 0
    assert ms[3].params['details'].find("RRR") > 0


@pytest.mark.skipif("sys.version_info < (3, 4)", reason="subtests require Python 3.4+")
def test_subtest_failure(venv):
    output = run_directly(venv, 'subtest_failure.py')
    test_name = '__main__.TestXXX.testSubtestFailure'
    subtest_name = test_name + ' (i=|\'abc.xxx|\')'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': test_name + ' (i=0): ok|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdErr', {'out': subtest_name + ': failure|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'message': 'Subtest failed', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert ms[3].params['details'].find(subtest_name) == 0
    assert ms[3].params['details'].find("AssertionError") > 0
    assert ms[3].params['details'].find("1 == 0") > 0


@pytest.mark.skipif("sys.version_info < (3, 4)", reason="subtests require Python 3.4+")
def test_subtest_mixed_failure(venv):
    output = run_directly(venv, 'subtest_mixed_failure.py')
    test_name = '__main__.TestXXX.testSubtestFailure'
    subtest_name = test_name + ' (i=|\'abc.xxx|\')'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': test_name + ' (i=0): ok|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdErr', {'out': subtest_name + ': failure|n', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'message': 'Failure', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert ms[3].params['details'].find(subtest_name) == 0
    assert ms[3].params['details'].find("AssertionError") > 0
    assert ms[3].params['details'].find("1 == 0") > 0
    assert ms[3].params['details'].find("6 == 1") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="unexpected_success requires Python 2.7+")
def test_unexpected_success(venv):
    output = run_directly(venv, 'unexpected_success.py')
    test_name = '__main__.TestSkip.test_unexpected_success'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name,
                                          'details': "Test should not succeed since it|'s marked with @unittest.expectedFailure",
                                          'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="unittest discovery requires Python 2.7+")
def test_discovery(venv):
    output = run_directly(venv, 'discovery.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
            ServiceMessage('testFinished', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="unittest discovery requires Python 2.7+")
def test_discovery_errors(venv):
    output = run_directly(venv, 'discovery_errors.py')
    test_name = 'unittest.loader.ModuleImportFailure.testsimple'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Error', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("ImportError") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_setup_module_error(venv):
    output = run_directly(venv, 'setup_module_error.py')
    test_name = '__main__.setUpModule'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("assert 1 == 0") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_setup_class_error(venv):
    output = run_directly(venv, 'setup_class_error.py')
    test_name = '__main__.TestXXX.setUpClass'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    assert ms[1].params['details'].index("RRR") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_teardown_class_error(venv):
    output = run_directly(venv, 'teardown_class_error.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.tearDownClass'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.tearDownClass', 'message': 'Failure'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.tearDownClass'}),
        ])

    assert ms[3].params['details'].index("RRR") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_teardown_module_error(venv):
    output = run_directly(venv, 'teardown_module_error.py')
    teardown_test_name = '__main__.tearDownModule'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testStarted', {'name': teardown_test_name, 'flowId': teardown_test_name}),
            ServiceMessage('testFailed', {'name': teardown_test_name, 'message': 'Failure', 'flowId': teardown_test_name}),
            ServiceMessage('testFinished', {'name': teardown_test_name, 'flowId': teardown_test_name}),
        ])

    assert ms[3].params['details'].index("assert 1 == 0") > 0


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
