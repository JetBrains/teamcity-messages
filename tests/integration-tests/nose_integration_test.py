# coding=utf-8
import os
import sys

import pytest

import virtual_environments
from diff_test_tools import SCRIPT, expected_messages
from service_messages import ServiceMessage, assert_service_messages, match
from test_util import run_command, get_teamcity_messages_root


@pytest.fixture(scope='module', params=["nose==1.3.7"])  # Nose is dead, support only latest version
def venv(request):
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_environments.VirtualEnvDescription
    """
    if sys.version_info >= (3, 8):
        pytest.skip("nose is outdated and doesn't support 3.8")
    return virtual_environments.prepare_virtualenv([request.param])


def _test_count(venv, count):
    nose_version = None
    for package in venv.packages:
        if package.startswith("nose=="):
            nose_version = tuple([int(x) for x in package[6:].split(".")])
    if nose_version is None or nose_version >= (1, 3, 4):
        return ServiceMessage('testCount', {'count': str(count)})
    return None


def test_hierarchy(venv):
    output = run(venv, 'hierarchy')
    test_name = 'namespace1.namespace2.testmyzz.test'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'captureStandardOutput': 'false', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_doctests(venv):
    output = run(venv, 'doctests', options="--with-doctest")
    test_name = 'doctests.namespace1.d.multiply'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_docstrings(venv):
    output = run(venv, 'docstrings')
    test_name = 'testa.test_func (My cool test_name)'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_skip(venv):
    output = run(venv, 'skiptest')
    test_name = 'testa.test_func'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'message': u'SKIPPED: my skip причина', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_coverage(venv):
    venv_with_coverage = virtual_environments.prepare_virtualenv(venv.packages + ["coverage==4.5.4"])

    coverage_file = os.path.join(virtual_environments.get_vroot(), "coverage-temp.xml")

    output = run(venv_with_coverage, 'coverage', options="--with-coverage --cover-erase --cover-tests --cover-xml --cover-xml-file=\"" + coverage_file + "\"")
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': 'testa.test_mycode'}),
            ServiceMessage('testFinished', {'name': 'testa.test_mycode'}),
        ])

    f = open(coverage_file, "rb")
    content = str(f.read())
    f.close()

    assert content.find('<line hits="1" number="2"/>') > 0


def test_flask_test_incomplete(venv):
    venv_with_flask = virtual_environments.prepare_virtualenv(venv.packages + ["Flask-Testing==0.8.1"])

    output = run(venv_with_flask, 'flask_testing_incomplete')
    test_name = 'test_foo.TestIncompleteFoo.test_add'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("nNotImplementedError") > 0


def test_flask_test_ok(venv):
    venv_with_flask = virtual_environments.prepare_virtualenv(venv.packages + ["Flask-Testing==0.8.1"])

    output = run(venv_with_flask, 'flask_testing_ok')
    test_name = 'test_foo.TestFoo.test_add'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_deprecated(venv):
    output = run(venv, 'deprecatedtest')
    test_name = 'testa.test_func'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'message': 'Deprecated', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff(venv):
    output = run(venv, SCRIPT)
    assert_service_messages(
        output,
        [
            _test_count(venv, 3),
        ] + expected_messages('diff_assert.FooTest'))


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_long_diff(venv):
    output = run(venv, "../diff_assert_long.py")
    test_name = 'diff_assert_long.FooTest.test_test'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_generators(venv):
    output = run(venv, 'generators')
    assert_service_messages(
        output,
        [
            _test_count(venv, 3),
            ServiceMessage('testStarted', {'name': 'testa.test_evens(0, 0, |\'_|\')'}),
            ServiceMessage('testFinished', {'name': 'testa.test_evens(0, 0, |\'_|\')'}),
            ServiceMessage('testStarted', {'name': "testa.test_evens(1, 3, |'_|')"}),
            ServiceMessage('testFinished', {'name': "testa.test_evens(1, 3, |'_|')"}),
            ServiceMessage('testStarted', {'name': "testa.test_evens(2, 6, |'_|')"}),
            ServiceMessage('testFinished', {'name': "testa.test_evens(2, 6, |'_|')"}),
        ])


def test_generators_class(venv):
    output = run(venv, 'generators_class')
    assert_service_messages(
        output,
        [
            _test_count(venv, 3),
            ServiceMessage('testStarted', {'name': 'testa.TestA.test_evens(0, 0, |\'_|\')'}),
            ServiceMessage('testFinished', {'name': 'testa.TestA.test_evens(0, 0, |\'_|\')'}),
            ServiceMessage('testStarted', {'name': "testa.TestA.test_evens(1, 3, |'_|')"}),
            ServiceMessage('testFinished', {'name': "testa.TestA.test_evens(1, 3, |'_|')"}),
            ServiceMessage('testStarted', {'name': "testa.TestA.test_evens(2, 6, |'_|')"}),
            ServiceMessage('testFinished', {'name': "testa.TestA.test_evens(2, 6, |'_|')"}),
        ])


def test_pass_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')
    test_name = 'nose-guinea-pig.GuineaPig.test_pass'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'captureStandardOutput': 'false'}),
            ServiceMessage('testStdOut', {'out': 'Output from test_pass|n', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_pass_no_capture(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass', options="--nocapture")
    assert output.find("Output from test_pass") > 0
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': 'nose-guinea-pig.GuineaPig.test_pass', 'captureStandardOutput': 'true'}),
            ServiceMessage('testFinished', {'name': 'nose-guinea-pig.GuineaPig.test_pass'}),
        ])


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("2 * 2 == 5") > 0


def test_setup_module_error(venv):
    output = run(venv, 'setup_module_error')
    test_name = 'namespace2.testa.setup'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_setup_class_error(venv):
    output = run(venv, 'setup_class_error')
    test_name = 'testa.TestXXX.setup'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name, 'message': 'error in setup context'}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("RRR") > 0


def test_setup_package_error(venv):
    output = run(venv, 'setup_package_error')
    test_name = 'namespace2.setup'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name, 'message': 'error in setup context'}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_setup_function_error(venv):
    output = run(venv, 'setup_function_error')
    test_name = 'testa.test'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_teardown_module_error(venv):
    output = run(venv, 'teardown_module_error')
    test_name = 'namespace2.testa.teardown'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': 'namespace2.testa.test_mycode'}),
            ServiceMessage('testFinished', {'name': 'namespace2.testa.test_mycode'}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name, 'message': 'error in teardown context'}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_teardown_class_error(venv):
    output = run(venv, 'teardown_class_error')
    test_name = 'testa.TestXXX.teardown'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': 'testa.TestXXX.runTest'}),
            ServiceMessage('testFinished', {'name': 'testa.TestXXX.runTest'}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name, 'message': 'error in teardown context'}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("RRR") > 0


def test_teardown_package_error(venv):
    output = run(venv, 'teardown_package_error')
    test_name = 'namespace2.teardown'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': 'namespace2.testa.test_mycode'}),
            ServiceMessage('testFinished', {'name': 'namespace2.testa.test_mycode'}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name, 'message': 'error in teardown context'}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_teardown_function_error(venv):
    output = run(venv, 'teardown_function_error')
    test_name = 'testa.test'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Traceback") == 0
    assert failed_ms.params['details'].find("AssertionError") > 0


def test_buffer_output(venv):
    output = run(venv, 'buffer_output')
    test_name = 'test_buffer_output.SpamTest.test_test'
    assert_service_messages(
        output,
        [_test_count(venv, 1)] +
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': "stdout_line1|n", 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': "stdout_line2|n", 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': "stdout_line3_nonewline", 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])

    # Check no stdout_test or stderr_test in the output (not in service messages)
    # it checks self._mirrorOutput = False
    output = output.replace("out='stdout_test", "").replace("out='stderr_test", "")
    assert output.find("stdout_test") < 0
    assert output.find("stderr_test") < 0

    # assert logcapture plugin works
    assert output.find("begin captured logging") > 0
    assert output.find("log info message") >= 0


def test_fail_with_msg(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_with_msg')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_with_msg'
    ms = assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    failed_ms = match(ms, ServiceMessage('testFailed', {'name': test_name}))
    assert failed_ms.params['details'].find("Bitte keine Werbung") > 0


def test_fail_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_output')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_output'
    assert_service_messages(
        output,
        [
            _test_count(venv, 1),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'out': 'Output line 1|n', 'flowId': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'out': 'Output line 2|n', 'flowId': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'out': 'Output line 3|n', 'flowId': test_name}),
            ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_fail_big_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_big_output', print_output=False)
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_big_output'

    full_line = 'x' * 50000
    leftovers = 'x' * (1024 * 1024 - 50000 * 20)

    assert_service_messages(
        output,
        [_test_count(venv, 1)] +
        [ServiceMessage('testStarted', {})] +
        [ServiceMessage('testStdOut', {'out': full_line, 'flowId': test_name})] * 20 +
        [ServiceMessage('testStdOut', {'out': leftovers, 'flowId': test_name})] +
        [ServiceMessage('testFailed', {'name': test_name, 'flowId': test_name})] +
        [ServiceMessage('testFinished', {})]
    )


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_issue_98(venv):
    # Start the process and wait for its output
    custom_test_loader = os.path.join(get_teamcity_messages_root(), 'tests', 'guinea-pigs', 'nose', 'issue_98', 'custom_test_loader.py')
    command = os.path.join(venv.bin, 'python') + " " + custom_test_loader
    output = run_command(command)

    test_name = 'simple_tests.SimpleTests.test_two'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testIgnored', {'name': test_name, 'message': 'Skipped: Skipping', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ],
        actual_messages_predicate=lambda ms: ms.name != "testCount"
    )


def test_nose_parameterized(venv):
    venv_with_params = virtual_environments.prepare_virtualenv(venv.packages + ["nose-parameterized"])

    output = run(venv_with_params, 'nose_parameterized')
    test1_name = "test.test(|'1_1|', |'https://facebook_com/share_php?http://foo_com/|')"
    test2_name = 'test.test(None, 3)'
    assert_service_messages(
        output,
        [
            _test_count(venv, 2),
            ServiceMessage('testStarted', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name, 'flowId': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name, 'flowId': test2_name}),
        ])


def run(venv, file, clazz=None, test=None, print_output=True, options=""):
    if clazz:
        clazz_arg = ":" + clazz
    else:
        clazz_arg = ""

    if test:
        test_arg = "." + test
    else:
        test_arg = ""

    command = os.path.join(venv.bin, 'nosetests') + \
        " -v " + options + " " + \
        os.path.join('tests', 'guinea-pigs', 'nose', file) + clazz_arg + test_arg
    return run_command(command, print_output=print_output)
