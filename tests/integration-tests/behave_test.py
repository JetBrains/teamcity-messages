import os

import pytest

import virtual_environments
from service_messages import assert_service_messages, ServiceMessage
from test_util import run_command, get_teamcity_messages_root


@pytest.fixture(scope='module', params=["behave"])
def venv(request):
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv([request.param])


def test_all_features(venv):
    output = run(venv)
    assert_service_messages(
        output,
        [
            # Complex
            ServiceMessage('testSuiteStarted', {'name': 'Complex'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.1'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is USA'}),
            ServiceMessage('testFinished', {'name': 'When country is USA'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Washington'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Washington'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.1'}),


            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is Japan'}),
            ServiceMessage('testFinished', {'name': 'When country is Japan'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Tokio'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Tokio'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.3'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is I will fail'}),
            ServiceMessage('testFinished', {'name': 'When country is I will fail'}),

            ServiceMessage('testStarted', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFailed', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFinished', {'name': 'Then capital is I will fail'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.3'}),



            ServiceMessage('testSuiteStarted', {'name': 'Broken'}),
            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'Given I will fail'}),
            ServiceMessage('testFailed', {'name': 'Given I will fail'}),
            ServiceMessage('testFinished', {'name': 'Given I will fail'}),


            ServiceMessage('testStarted', {'name': 'Given Skip me'}),
            ServiceMessage('testIgnored', {'name': 'Given Skip me'}),
            ServiceMessage('testFinished', {'name': 'Given Skip me'}),

            ServiceMessage('testSuiteFinished', {'name': 'Broken'}),
            ServiceMessage('testSuiteFinished', {'name': 'Complex'}),



            # Simple
            ServiceMessage('testSuiteStarted', {'name': 'Simple'}),

            ServiceMessage('testSuiteStarted', {'name': 'Must be OK'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testSuiteFinished', {'name': 'Must be OK'}),

            ServiceMessage('testSuiteStarted', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testStarted', {'name': 'Then No step def'}),
            ServiceMessage('testFailed', {'name': 'Then No step def', 'message': 'Undefined'}),
            ServiceMessage('testFinished', {'name': 'Then No step def'}),

            ServiceMessage('testSuiteFinished', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testSuiteFinished', {'name': 'Simple'}),
        ])


def test_complex_suite(venv):
    output = run(venv, arguments="Complex.feature")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'Complex'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.1'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is USA'}),
            ServiceMessage('testFinished', {'name': 'When country is USA'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Washington'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Washington'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.1'}),


            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is Japan'}),
            ServiceMessage('testFinished', {'name': 'When country is Japan'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Tokio'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Tokio'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.3'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is I will fail'}),
            ServiceMessage('testFinished', {'name': 'When country is I will fail'}),

            ServiceMessage('testStarted', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFailed', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFinished', {'name': 'Then capital is I will fail'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.3'}),



            ServiceMessage('testSuiteStarted', {'name': 'Broken'}),
            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'Given I will fail'}),
            ServiceMessage('testFailed', {'name': 'Given I will fail'}),
            ServiceMessage('testFinished', {'name': 'Given I will fail'}),


            ServiceMessage('testStarted', {'name': 'Given Skip me'}),
            ServiceMessage('testIgnored', {'name': 'Given Skip me'}),
            ServiceMessage('testFinished', {'name': 'Given Skip me'}),

            ServiceMessage('testSuiteFinished', {'name': 'Broken'}),
            ServiceMessage('testSuiteFinished', {'name': 'Complex'}),
        ])


def test_complex_suite_outlines(venv):
    output = run(venv, arguments="Complex.feature", options="-n \"With examples\"")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'Complex'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.1'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is USA'}),
            ServiceMessage('testFinished', {'name': 'When country is USA'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Washington'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Washington'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.1'}),


            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is Japan'}),
            ServiceMessage('testFinished', {'name': 'When country is Japan'}),

            ServiceMessage('testStarted', {'name': 'Then capital is Tokio'}),
            ServiceMessage('testFinished', {'name': 'Then capital is Tokio'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.2'}),

            ServiceMessage('testSuiteStarted', {'name': 'With examples -- @1.3'}),

            ServiceMessage('testStarted', {'name': 'Given I will create background'}),
            ServiceMessage('testFinished', {'name': 'Given I will create background'}),

            ServiceMessage('testStarted', {'name': 'When country is I will fail'}),
            ServiceMessage('testFinished', {'name': 'When country is I will fail'}),

            ServiceMessage('testStarted', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFailed', {'name': 'Then capital is I will fail'}),
            ServiceMessage('testFinished', {'name': 'Then capital is I will fail'}),

            ServiceMessage('testSuiteFinished', {'name': 'With examples -- @1.3'}),


            ServiceMessage('testSuiteFinished', {'name': 'Complex'}),
        ])


def test_simple_suite_only_ok(venv):
    output = run(venv, arguments="Simple.feature", options="-n \"Must be OK\"")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'Simple'}),

            ServiceMessage('testSuiteStarted', {'name': 'Must be OK'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testSuiteFinished', {'name': 'Must be OK'}),
            ServiceMessage('testSuiteFinished', {'name': 'Simple'}),
        ])


def test_simple_suite_only_fail(venv):
    output = run(venv, arguments="Simple.feature", options="-n \"First step ok, second ignored\"")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'Simple'}),


            ServiceMessage('testSuiteStarted', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testStarted', {'name': 'Then No step def'}),
            ServiceMessage('testFailed', {'name': 'Then No step def', 'message': 'Undefined'}),
            ServiceMessage('testFinished', {'name': 'Then No step def'}),

            ServiceMessage('testSuiteFinished', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testSuiteFinished', {'name': 'Simple'}),
        ])


def test_simple_suite(venv):
    output = run(venv, arguments="Simple.feature")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'Simple'}),

            ServiceMessage('testSuiteStarted', {'name': 'Must be OK'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testSuiteFinished', {'name': 'Must be OK'}),

            ServiceMessage('testSuiteStarted', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testStarted', {'name': 'Given I like BDD'}),
            ServiceMessage('testFinished', {'name': 'Given I like BDD'}),
            ServiceMessage('testStarted', {'name': 'Then No step def'}),
            ServiceMessage('testFailed', {'name': 'Then No step def', 'message': 'Undefined'}),
            ServiceMessage('testFinished', {'name': 'Then No step def'}),

            ServiceMessage('testSuiteFinished', {'name': 'First step ok, second ignored'}),
            ServiceMessage('testSuiteFinished', {'name': 'Simple'}),
        ])


def run(venv, options="", arguments=""):
    cwd = os.path.join(get_teamcity_messages_root(), "tests", "guinea-pigs", "behave")
    behave = " ".join([os.path.join(venv.bin, "python"), "_behave_runner.py", options, arguments])
    return run_command(behave, cwd=cwd)
