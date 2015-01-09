from __future__ import print_function

__author__ = 'Leonid.Shalupov'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage, assert_service_messages


@pytest.fixture(scope='module', params=["pytest"])
def venv(request):
    """
    Prepares a virtual environment for py.test
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv([request.param])


def test_hierarchy(venv):
    output = run(venv, 'namespace')
    test_name = 'tests.guinea-pigs.pytest.namespace.pig_test_py.TestSmoke.test_smoke'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


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


def test_runtime_error(venv):
    output = run(venv, 'runtime_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test_py.test_exception'}),
            ServiceMessage('testFailed', {'flowId': 'tests.guinea-pigs.pytest.runtime_error_test_py.test_exception'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test_py.test_exception'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test_py.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test_py.test_error'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("oops") > 0
    assert ms[4].params["details"].find("assert 0 != 0") > 0


def test_unittest_error(venv):
    output = run(venv, 'unittest_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test_py.TestErrorFail.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test_py.TestErrorFail.test_error'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test_py.TestErrorFail.test_fail'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test_py.TestErrorFail.test_fail'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("oops") > 0
    assert ms[4].params["details"].find("AssertionError") > 0


def test_fixture_error(venv):
    output = run(venv, 'fixture_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.fixture_error_test_py.test_error1'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.fixture_error_test_py.test_error1'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.fixture_error_test_py.test_error2'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.fixture_error_test_py.test_error2'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("oops") > 0
    assert ms[4].params["details"].find("raise Exception") > 0
    assert ms[4].params["details"].find("oops") > 0


def test_teardown_error(venv):
    output = run(venv, 'teardown_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.teardown_error_test_py.test_error'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.teardown_error_test_py.test_error'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.teardown_error_test_py.test_error_teardown'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.teardown_error_test_py.test_error_teardown'}),
        ])
    assert ms[3].params["details"].find("raise Exception") > 0
    assert ms[3].params["details"].find("teardown oops") > 0


def test_module_error(venv):
    output = run(venv, 'module_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.module_error_test_py.top_level_collect'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.module_error_test_py.top_level_collect'}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("module oops") > 0


def test_skip(venv):
    output = run(venv, 'skip_test.py')
    test_name = 'tests.guinea-pigs.pytest.skip_test_py.test_function'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testIgnored', {'message': 'Skipped: skip reason', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_params(venv):
    output = run(venv, 'params_test.py')

    test1_name = 'tests.guinea-pigs.pytest.params_test_py.test_eval[3+5-8|]'
    test2_name = "tests.guinea-pigs.pytest.params_test_py.test_eval[|'1_5|' + |'2|'-1_52|]"
    test3_name = 'tests.guinea-pigs.pytest.params_test_py.test_eval[6*9-42|]'

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
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test_py.test_unexpectedly_passing'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test_py.test_unexpectedly_passing'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test_py.test_expected_to_fail'}),
            ServiceMessage('testIgnored', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test_py.test_expected_to_fail'}),
        ])
    assert ms[4].params["message"].find("xfail reason") > 0


def run(venv, file, test=None):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    test_suffix = ("::" + test) if test is not None else ""
    command = os.path.join(venv.bin, 'py.test') + " --teamcity " + \
        os.path.join('tests', 'guinea-pigs', 'pytest', file) + test_suffix
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output
