# coding=utf-8
import os
import subprocess
import sys

import pytest

import virtual_environments
from common import get_output_encoding
from diff_test_tools import expected_messages, SCRIPT
from service_messages import ServiceMessage, assert_service_messages, match
from test_util import get_teamcity_messages_root


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
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'captureStandardOutput': 'true', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_docstring(venv):
    output = run_directly(venv, 'docstring.py')
    test_name = '__main__.TestXXX.runTest (A test_)'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_assert(venv):
    output = run_directly(venv, 'assert.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index("assert 1 == 0") > 0


def test_fail(venv):
    output = run_directly(venv, 'fail_test.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index('fail("Grr")') > 0


def test_setup_error(venv):
    output = run_directly(venv, 'setup_error.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Error', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index("RRR") > 0
    assert failed_ms.params['details'].index("setUp") > 0


def test_teardown_error(venv):
    output = run_directly(venv, 'teardown_error.py')
    test_name = '__main__.TestXXX.runTest'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Error', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index("RRR") > 0
    assert failed_ms.params['details'].index("tearDown") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="buffer requires Python 2.7+")
def test_buffer_output(venv):
    output = run_directly(venv, 'buffer_output.py')
    test_name = '__main__.SpamTest.test_test'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': "stdout_test1|n", 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': "stdout_test2|n", 'flowId': test_name}),
            ServiceMessage('testStdErr', {'out': "stderr_test1", 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdErr', {'out': "stderr_test2", 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    # Check no stdout_test or stderr_test in the output (not in service messages)
    # it checks self._mirrorOutput = False
    output = output.replace("out='stdout_test", "").replace("out='stderr_test", "")
    assert output.find("stdout_test") < 0
    assert output.find("stderr_test") < 0


def test_doctests(venv):
    output = run_directly(venv, 'doctests.py')
    test_name = '__main__.factorial'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
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
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': '__main__.TestSkip.test_ok'}),
            ServiceMessage('testFinished', {'name': '__main__.TestSkip.test_ok'}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'message': u'Skipped: testing skipping причина', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_expected_failure(venv):
    if sys.version_info < (2, 7):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'expected_failure.py')
    test_name = '__main__.TestSkip.test_expected_failure'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testIgnored', {'name': test_name}))
    assert failed_ms.params['message'].find("Expected failure") == 0
    assert failed_ms.params['message'].find("this should happen unfortunately") > 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_ok(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_ok.py')
    test_name = '__main__.TestXXX.testSubtestSuccess'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=0)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=0)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=1)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=1)', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_error(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_error.py')
    test_name = '__main__.TestXXX.testSubtestError'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=0)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=0)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': "(i=|'abc_xxx|')", 'flowId': test_name, 'subTestResult': 'Error'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockClosed', {'name': "(i=|'abc_xxx|')", 'flowId': test_name}),
            ServiceMessage('testFailed', {'details': "Failed subtests list: (i=|'abc_xxx|')",
                                          'message': 'One or more subtests failed',
                                          'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testStdErr', {'name': test_name}))
    assert failed_ms.params['out'].find("SubTest error") >= 0
    assert failed_ms.params['out'].find("RuntimeError") >= 0
    assert failed_ms.params['out'].find("RRR") >= 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_failure(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_failure.py')
    test_name = '__main__.TestXXX.testSubtestFailure'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=0)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=0)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': "(i=|'abc_xxx|')", 'flowId': test_name, 'subTestResult': 'Failure'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockClosed', {'name': "(i=|'abc_xxx|')", 'flowId': test_name}),
            ServiceMessage('testFailed', {'details': "Failed subtests list: (i=|'abc_xxx|')",
                                          'message': 'One or more subtests failed',
                                          'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testStdErr', {'name': test_name}))
    assert failed_ms.params['out'].find("SubTest failure") >= 0
    assert failed_ms.params['out'].find("AssertionError") >= 0
    assert failed_ms.params['out'].find("assert 1 == 0") >= 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_nested(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_nested.py')
    test_name = '__main__.TestXXX.testNested'

    # Nested blocks support requires strict notifications about starting and stopping subtests
    # which is not yet supported, see https://mail.python.org/pipermail/python-dev/2016-June/145402.html
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=2)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=2)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=1)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=1)', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_skip(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_skip.py')
    test_name = '__main__.TestXXX.testSubtestSkip'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=2)', 'flowId': test_name, 'subTestResult': 'Skip'}),
            ServiceMessage('testStdOut', {'name': test_name, 'flowId': test_name, 'out': 'SubTest skipped: skip reason|n'}),
            ServiceMessage('blockClosed', {'name': '(i=2)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=0)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=0)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=1)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=1)', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_setup_class_skip(venv):
    if sys.version_info < (2, 7):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'setup_class_skip.py')
    test1_name = '__main__.TestSimple.setUpClass'
    test2_name = '__main__.TestSubSimple.setUpClass'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "7"}),
            ServiceMessage('testStarted', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testIgnored', {'name': test1_name, 'flowId': test1_name, 'message': "Skipped: Skip whole Case"}),
            ServiceMessage('testFinished', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name, 'flowId': test2_name}),
            ServiceMessage('testIgnored', {'name': test2_name, 'flowId': test2_name, 'message': "Skipped: Skip whole Case"}),
            ServiceMessage('testFinished', {'name': test2_name, 'flowId': test2_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_subtest_mixed_failure(venv):
    if sys.version_info < (3, 4):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'subtest_mixed_failure.py')
    test_name = '__main__.TestXXX.testSubtestFailure'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': '(i=0)', 'flowId': test_name, 'subTestResult': 'Success'}),
            ServiceMessage('blockClosed', {'name': '(i=0)', 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': "(i=|'abc_xxx|')", 'flowId': test_name, 'subTestResult': 'Failure'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockClosed', {'name': "(i=|'abc_xxx|')", 'flowId': test_name}),
            ServiceMessage('testFailed', {'message': 'Failure', 'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Failed subtests list: (i=|'abc_xxx|')|n|n") >= 0
    assert failed_ms.params['details'].find("AssertionError") > 0
    assert failed_ms.params['details'].find("6 == 1") > 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="unittest2 requires Python 2.6+")
def test_unexpected_success(venv):
    if sys.version_info < (2, 7):
        venv = virtual_environments.prepare_virtualenv(list(venv.packages) + ["unittest2"])

    output = run_directly(venv, 'unexpected_success.py')
    test_name = '__main__.TestSkip.test_unexpected_success'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
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
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
            ServiceMessage('testFinished', {'name': 'testsimple.TestTeamcityMessages.runTest'}),
        ])


@pytest.mark.skipif("sys.version_info < (3, 2)", reason="unittest failfast requires Python 3.2+")
def test_fail_fast(venv):
    output = run_directly(venv, 'fail_fast.py')
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "3"}),
            ServiceMessage('testStarted', {'name': '__main__.FooTest.test_1_test'}),
            ServiceMessage('testFinished', {'name': '__main__.FooTest.test_1_test'}),
            ServiceMessage('testStarted', {'name': '__main__.FooTest.test_2_test'}),
            ServiceMessage('testFailed', {'name': '__main__.FooTest.test_2_test'}),
            ServiceMessage('testFinished', {'name': '__main__.FooTest.test_2_test'}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="unittest discovery requires Python 2.7+")
def test_discovery_errors(venv):
    output = run_directly(venv, 'discovery_errors.py')

    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {}),
            ServiceMessage('testFailed', {'message': 'Error'}),
            ServiceMessage('testFinished', {}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {}))
    assert failed_ms.params['details'].index("ImportError") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_setup_module_error(venv):
    output = run_directly(venv, 'setup_module_error.py')
    test_name = '__main__.setUpModule'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index("assert 1 == 0") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_setup_class_error(venv):
    output = run_directly(venv, 'setup_class_error.py')
    test_name = '__main__.TestXXX.setUpClass'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'message': 'Failure', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].index("RRR") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_teardown_class_error(venv):
    output = run_directly(venv, 'teardown_class_error.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.tearDownClass'}),
            ServiceMessage('testFailed', {'name': '__main__.TestXXX.tearDownClass', 'message': 'Failure'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.tearDownClass'}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': '__main__.TestXXX.tearDownClass'}))
    assert failed_ms.params['details'].index("RRR") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_teardown_module_error(venv):
    output = run_directly(venv, 'teardown_module_error.py')
    teardown_test_name = '__main__.tearDownModule'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testFinished', {'name': '__main__.TestXXX.test_ok'}),
            ServiceMessage('testStarted', {'name': teardown_test_name, 'flowId': teardown_test_name}),
            ServiceMessage('testFailed', {'name': teardown_test_name, 'message': 'Failure', 'flowId': teardown_test_name}),
            ServiceMessage('testFinished', {'name': teardown_test_name, 'flowId': teardown_test_name}),
        ])

    failed_ms = match(ms, ServiceMessage('testFailed', {'name': teardown_test_name}))
    assert failed_ms.params['details'].index("assert 1 == 0") > 0


# As of twisted 15.2.1 trial is not available on Python 3
@pytest.mark.skipif("sys.version_info < (2, 6) or sys.version_info >= (3, 0)", reason="requires Python 2.6 or 2.7")
def test_twisted_trial(venv):
    packages = list(*venv.packages)
    packages.append("twisted==15.2.1")
    if os.name == 'nt':
        if sys.version_info < (2, 7):
            pytest.skip("pypiwin32 is available since Python 2.7")
        packages.append("pypiwin32==219")
    venv_with_twisted = virtual_environments.prepare_virtualenv(packages)

    env = virtual_environments.get_clean_system_environment()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), "tests", "guinea-pigs", "unittest")

    # Start the process and wait for its output
    trial_file = os.path.join(venv_with_twisted.bin, 'trial')
    trial_exe_file = os.path.join(venv_with_twisted.bin, 'trial.exe')
    trial_py_file = os.path.join(venv_with_twisted.bin, 'trial.py')

    if os.path.exists(trial_file):
        command = trial_file
    elif os.path.exists(trial_py_file):
        command = os.path.join(venv_with_twisted.bin, 'python') + " " + trial_py_file
    elif os.path.exists(trial_exe_file):
        command = trial_exe_file
    else:
        raise Exception("twisted trial is not found at " + trial_py_file + " or " + trial_file + " or " + trial_exe_file)

    command += " --reporter=teamcity twisted_trial"
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "*"))

    test1 = "twisted_trial.test_case.CalculationTestCase.test_fail (some desc)"
    test2 = "twisted_trial.test_case.CalculationTestCase.test_ok"

    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test1}),
            ServiceMessage('testFailed', {'name': test1}),
            ServiceMessage('testFinished', {'name': test1}),
            ServiceMessage('testStarted', {'name': test2}),
            ServiceMessage('testFinished', {'name': test2}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test1}))
    assert failed_ms.params['details'].index("5 != 4") > 0


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff(venv):
    output = run_directly(venv, SCRIPT)
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
        ] + expected_messages("__main__.FooTest.test_test"))


def run_directly(venv, file):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    # Start the process and wait for its output
    command = os.path.join(venv.bin, 'python') + " " + os.path.join('tests', 'guinea-pigs', 'unittest', file)
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=env, shell=True, cwd=get_teamcity_messages_root())
    output = "".join([x.decode(get_output_encoding()) for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "*"))

    return output
