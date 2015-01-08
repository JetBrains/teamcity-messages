__author__ = 'Leonid.Bushuev'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import parse_service_messages, ServiceMessage, assert_service_messages


@pytest.fixture(scope='module', params=["nose"])  # '1.2.1', '1.3.0',
def venv(request):
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_environments.VirtualEnvDescription
    """
    return virtual_environments.prepare_virtualenv([request.param])


def test_hierarchy(venv):
    output = run(venv, 'hierarchy')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'namespace1'}),
            ServiceMessage('testSuiteStarted', {'name': 'namespace2'}),
            ServiceMessage('testSuiteStarted', {'name': 'testmyzz'}),
            ServiceMessage('testStarted', {'name': 'test'}),
            ServiceMessage('testFinished', {'name': 'test'}),
            ServiceMessage('testSuiteFinished', {'name': 'testmyzz'}),
            ServiceMessage('testSuiteFinished', {'name': 'namespace2'}),
            ServiceMessage('testSuiteFinished', {'name': 'namespace1'}),
        ])


def test_doctests(venv):
    output = run(venv, 'doctests', options="--with-doctest")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'doctests'}),
            ServiceMessage('testSuiteStarted', {'name': 'namespace1'}),
            ServiceMessage('testSuiteStarted', {'name': 'd'}),
            ServiceMessage('testStarted', {'name': 'multiply'}),
            ServiceMessage('testFinished', {'name': 'multiply'}),
            ServiceMessage('testSuiteFinished', {'name': 'd'}),
            ServiceMessage('testSuiteFinished', {'name': 'namespace1'}),
            ServiceMessage('testSuiteFinished', {'name': 'doctests'}),
        ])


def test_docstrings(venv):
    output = run(venv, 'docstrings')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'testa'}),
            ServiceMessage('testStarted', {'name': 'test_func (My cool test name)'}),
            ServiceMessage('testFinished', {'name': 'test_func (My cool test name)'}),
            ServiceMessage('testSuiteFinished', {'name': 'testa'}),
        ])


def test_skip(venv):
    # Note: skip reason is unavailable, see https://groups.google.com/forum/#!topic/nose-users/MnPwgZG8UbQ

    output = run(venv, 'skiptest')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'testa'}),
            ServiceMessage('testStarted', {'name': 'test_func'}),
            ServiceMessage('testIgnored', {'name': 'test_func', 'message': 'Skipped'}),
            ServiceMessage('testFinished', {'name': 'test_func'}),
            ServiceMessage('testSuiteFinished', {'name': 'testa'}),
        ])


def test_coverage(venv):
    venv_with_coverage = virtual_environments.prepare_virtualenv(venv.packages + ["coverage==3.7.1"])

    coverage_file = os.path.join(virtual_environments.get_vroot(), "coverage-temp.xml")

    output = run(venv_with_coverage, 'coverage', options="--with-coverage --cover-tests --cover-xml --cover-xml-file=\"" + coverage_file + "\"")
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'testa'}),
            ServiceMessage('testStarted', {'name': 'test_mycode'}),
            ServiceMessage('testFinished', {'name': 'test_mycode'}),
            ServiceMessage('testSuiteFinished', {'name': 'testa'}),
        ])

    f = open(coverage_file, "rb")
    content = str(f.read())
    f.close()

    assert content.find('<line hits="1" number="2"/>') > 0


def test_deprecated(venv):
    output = run(venv, 'deprecatedtest')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'testa'}),
            ServiceMessage('testStarted', {'name': 'test_func'}),
            ServiceMessage('testIgnored', {'name': 'test_func', 'message': 'Deprecated'}),
            ServiceMessage('testFinished', {'name': 'test_func'}),
            ServiceMessage('testSuiteFinished', {'name': 'testa'}),
        ])


def test_generators(venv):
    output = run(venv, 'generators')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'testa'}),
            ServiceMessage('testSuiteStarted', {'name': 'test_evens'}),
            ServiceMessage('testStarted', {'name': 'test_evens(0, 0)'}),
            ServiceMessage('testFinished', {'name': 'test_evens(0, 0)'}),
            ServiceMessage('testStarted', {'name': 'test_evens(1, 3)'}),
            ServiceMessage('testFinished', {'name': 'test_evens(1, 3)'}),
            ServiceMessage('testStarted', {'name': 'test_evens(2, 6)'}),
            ServiceMessage('testFinished', {'name': 'test_evens(2, 6)'}),
            ServiceMessage('testSuiteFinished', {'name': 'test_evens'}),
            ServiceMessage('testSuiteFinished', {'name': 'testa'}),
        ])


def test_pass(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')
    assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'}),
            ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'}),
            ServiceMessage('testStarted', {'name': 'test_pass'}),
            ServiceMessage('testFinished', {'name': 'test_pass'}),
            ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'}),
            ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'}),
        ])


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'}),
            ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'}),
            ServiceMessage('testStarted', {'name': 'test_fail'}),
            ServiceMessage('testFailed', {'name': 'test_fail'}),
            ServiceMessage('testFinished', {'name': 'test_fail'}),
            ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'}),
            ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'}),
        ])

    assert ms[3].params['details'].find("Traceback") == 0
    assert ms[3].params['details'].find("2 * 2 == 5") > 0


def test_fail_with_msg(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_with_msg')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'}),
            ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'}),
            ServiceMessage('testStarted', {'name': 'test_fail_with_msg'}),
            ServiceMessage('testFailed', {'name': 'test_fail_with_msg'}),
            ServiceMessage('testFinished', {'name': 'test_fail_with_msg'}),
            ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'}),
            ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'}),
        ])
    assert ms[3].params['details'].find("Bitte keine Werbung") > 0


def test_fail_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_output')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testSuiteStarted', {'name': 'nose-guinea-pig'}),
            ServiceMessage('testSuiteStarted', {'name': 'GuineaPig'}),
            ServiceMessage('testStarted', {'name': 'test_fail_output'}),
            ServiceMessage('testFailed', {'name': 'test_fail_output'}),
            ServiceMessage('testFinished', {'name': 'test_fail_output'}),
            ServiceMessage('testSuiteFinished', {'name': 'GuineaPig'}),
            ServiceMessage('testSuiteFinished', {'name': 'nose-guinea-pig'}),
        ])

    assert ms[3].params['details'].find('Output line 1') > 0
    assert ms[3].params['details'].find('Output line 2') > 0
    assert ms[3].params['details'].find('Output line 3') > 0


def run(venv, file, clazz=None, test=None, options=""):
    env = virtual_environments.get_clean_system_environment()
    env['TEAMCITY_VERSION'] = "0.0.0"

    command = os.path.join(venv.bin, 'nosetests') + \
        " -v " + options + " " + \
        os.path.join('tests', 'guinea-pigs', 'nose', file) + \
        ((":" + clazz) if clazz else "") + \
        (('.' + test) if test else "")
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "*"))

    return output
