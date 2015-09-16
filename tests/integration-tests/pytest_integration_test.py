import os
import sys
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages, has_service_messages


def construct_fixture():
    params = []

    if sys.version_info >= (2, 6):
        # latest version
        params.append(("pytest",))

    if (2, 5) <= sys.version_info < (2, 6):
        params.append(("pytest==2.5.0", "py==1.4.19"))

    if (2, 4) <= sys.version_info < (2, 5):
        params.append(("pytest==2.3.3", "py==1.4.12"))

    @pytest.fixture(scope='module', params=params)
    def venv(request):
        return virtual_environments.prepare_virtualenv(request.param)

    return venv

globals()['venv'] = construct_fixture()


def test_hierarchy(venv):
    output = run(venv, 'namespace')
    test_name = 'tests.guinea-pigs.pytest.namespace.pig_test.TestSmoke.test_smoke'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_force_tc_reporting(venv):
    output = run(venv, 'namespace', options="--teamcity", set_tc_version=False)
    assert has_service_messages(output)


def test_tc_reporting(venv):
    output = run(venv, 'namespace')
    assert has_service_messages(output)


def test_no_reporting_when_no_teamcity(venv):
    output = run(venv, 'namespace', set_tc_version=False)
    assert not has_service_messages(output)


def test_reporting_disabled(venv):
    output = run(venv, 'namespace', set_tc_version=True, options="--no-teamcity")
    assert not has_service_messages(output)


def test_custom_test_items(venv):
    output = run(venv, 'custom')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line1'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line1'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line2'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line2'}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_coverage(venv):
    venv_with_coverage = virtual_environments.prepare_virtualenv(venv.packages + ("pytest-cov==1.8.1",))

    output = run(venv_with_coverage, 'coverage_test', options="--cov coverage_test")
    test_name = "tests.guinea-pigs.pytest.coverage_test.coverage_test.test_covered_func"
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
            ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLCovered', 'value': '9'}),
            ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLTotal', 'value': '13'}),
            ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLUncovered', 'value': '4'}),
        ])


def test_runtime_error(venv):
    output = run(venv, 'runtime_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testFailed', {'flowId': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_error'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("oops") > 0
    assert ms[4].params["details"].find("assert 0 != 0") > 0


def test_unittest_error(venv):
    output = run(venv, 'unittest_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("oops") > 0
    assert ms[4].params["details"].find("AssertionError") > 0


def test_fixture_error(venv):
    output = run(venv, 'fixture_error_test.py')

    test1_name = 'tests.guinea-pigs.pytest.fixture_error_test.test_error1'
    test1_setup = test1_name + '_setup'
    test2_name = 'tests.guinea-pigs.pytest.fixture_error_test.test_error2'
    test2_setup = test2_name + '_setup'

    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testStarted', {'name': test1_setup}),
            ServiceMessage('testFailed', {'name': test1_setup, 'flowId': test1_setup}),
            ServiceMessage('testFinished', {'name': test1_setup}),
            ServiceMessage('testFailed', {'name': test1_name,
                                          'message': 'test setup failed, see ' + test1_setup + ' test failure',
                                          'flowId': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name, 'flowId': test2_name}),
            ServiceMessage('testStarted', {'name': test2_setup, 'flowId': test2_setup}),
            ServiceMessage('testFailed', {'name': test2_setup, 'flowId': test2_setup}),
            ServiceMessage('testFinished', {'name': test2_setup, 'flowId': test2_setup}),
            ServiceMessage('testFailed', {'name': test2_name, 'flowId': test2_name,
                                          'message': 'test setup failed, see ' + test2_setup + ' test failure'}),
            ServiceMessage('testFinished', {'name': test2_name, 'flowId': test2_name}),
        ])
    assert ms[2].params["details"].find("raise Exception") > 0
    assert ms[2].params["details"].find("oops") > 0
    assert ms[8].params["details"].find("raise Exception") > 0
    assert ms[8].params["details"].find("oops") > 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_output(venv):
    output = run(venv, 'output_test.py')

    test_name = 'tests.guinea-pigs.pytest.output_test.test_out'
    test_setup = test_name + '_setup'
    test_teardown = test_name + '_teardown'

    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name, 'captureStandardOutput': 'false'}),
            ServiceMessage('testStarted', {'name': test_setup, 'flowId': test_setup}),
            ServiceMessage('testStdOut', {'name': test_setup, 'flowId': test_setup, 'out': 'setup stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_setup, 'flowId': test_setup, 'out': 'setup stderr|n'}),
            ServiceMessage('testFinished', {'name': test_setup}),
            ServiceMessage('testStdOut', {'name': test_name, 'flowId': test_name, 'out': 'test stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name, 'out': 'test stderr|n'}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStarted', {'name': test_teardown, 'flowId': test_teardown}),
            ServiceMessage('testStdOut', {'name': test_teardown, 'flowId': test_teardown, 'out': 'teardown stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_teardown, 'flowId': test_teardown, 'out': 'teardown stderr|n'}),
            ServiceMessage('testFinished', {'name': test_teardown, 'flowId': test_teardown}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_chunked_output(venv):
    output = run(venv, 'chunked_output_test.py')

    full_line = 'x' * 50000
    leftovers = 'x' * (1024 * 1024 - 50000 * 20)

    assert_service_messages(
        output,
        [ServiceMessage('testStarted', {})] +
        [ServiceMessage('testStdOut', {'out': full_line})] * 20 +
        [ServiceMessage('testStdOut', {'out': leftovers})] +
        [ServiceMessage('testStdErr', {'out': full_line})] * 20 +
        [ServiceMessage('testStdErr', {'out': leftovers})] +
        [ServiceMessage('testFinished', {})]
    )


def test_output_no_capture(venv):
    output = run(venv, 'output_test.py', options="-s")

    test_name = 'tests.guinea-pigs.pytest.output_test.test_out'

    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name, 'captureStandardOutput': 'true'}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert "setup stderr" in output
    assert "setup stdout" in output
    assert "test stderr" in output
    assert "test stdout" in output
    assert "teardown stderr" in output
    assert "teardown stdout" in output


def test_teardown_error(venv):
    output = run(venv, 'teardown_error_test.py')
    teardown_test_id = 'tests.guinea-pigs.pytest.teardown_error_test.test_error_teardown'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.teardown_error_test.test_error'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.teardown_error_test.test_error'}),
            ServiceMessage('testStarted', {'name': teardown_test_id, 'flowId': teardown_test_id}),
            ServiceMessage('testFailed', {'flowId': teardown_test_id}),
            ServiceMessage('testFinished', {'name': teardown_test_id, 'flowId': teardown_test_id}),
        ])
    assert ms[3].params["details"].find("raise Exception") > 0
    assert ms[3].params["details"].find("teardown oops") > 0


def test_module_error(venv):
    output = run(venv, 'module_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.module_error_test.top_level_collect'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.module_error_test.top_level_collect'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("module oops") > 0


def test_skip(venv):
    output = run(venv, 'skip_test.py')
    test_name = 'tests.guinea-pigs.pytest.skip_test.test_function'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testIgnored', {'message': 'Skipped: skip reason', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_params(venv):
    output = run(venv, 'params_test.py')

    test1_name = 'tests.guinea-pigs.pytest.params_test.test_eval|[3+5-8|]'
    test2_name = "tests.guinea-pigs.pytest.params_test.test_eval|[|'1_5|' + |'2|'-1_52|]"
    test3_name = 'tests.guinea-pigs.pytest.params_test.test_eval|[6*9-42|]'

    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
            ServiceMessage('testStarted', {'name': test3_name}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': test3_name}),
        ])


def test_xfail(venv):
    output = run(venv, 'xfail_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_unexpectedly_passing'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_unexpectedly_passing'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_expected_to_fail'}),
            ServiceMessage('testIgnored', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_expected_to_fail'}),
        ])
    assert ms[4].params["message"].find("xfail reason") > 0


def run(venv, file_name, test=None, options='', set_tc_version=True):
    env = virtual_environments.get_clean_system_environment()

    if set_tc_version:
        env['TEAMCITY_VERSION'] = "0.0.0"

    if test is not None:
        test_suffix = "::" + test
    else:
        test_suffix = ""

    command = os.path.join(venv.bin, 'py.test') + " " + options + " " + \
        os.path.join('tests', 'guinea-pigs', 'pytest', file_name) + test_suffix
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    # print("OUTPUT: " + output.replace("#", "*"))
    proc.wait()

    return output
