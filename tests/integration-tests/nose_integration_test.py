__author__ = 'Leonid.Bushuev'

import os
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages


@pytest.fixture(scope='module', params=["nose", "nose==1.2.1", "nose==1.3.0"])
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
            ServiceMessage('testStarted', {'name': 'namespace1.namespace2.testmyzz.test', 'captureStandardOutput': 'true'}),
            ServiceMessage('testFinished', {'name': 'namespace1.namespace2.testmyzz.test'}),
        ])


def test_doctests(venv):
    output = run(venv, 'doctests', options="--with-doctest")
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'doctests.namespace1.d.multiply'}),
            ServiceMessage('testFinished', {'name': 'doctests.namespace1.d.multiply'}),
        ])


def test_docstrings(venv):
    output = run(venv, 'docstrings')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testa.test_func (My cool test name)'}),
            ServiceMessage('testFinished', {'name': 'testa.test_func (My cool test name)'}),
        ])


def test_skip(venv):
    # Note: skip reason is unavailable, see https://groups.google.com/forum/#!topic/nose-users/MnPwgZG8UbQ

    output = run(venv, 'skiptest')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testa.test_func'}),
            ServiceMessage('testIgnored', {'name': 'testa.test_func', 'message': 'Skipped'}),
            ServiceMessage('testFinished', {'name': 'testa.test_func'}),
        ])


def test_coverage(venv):
    venv_with_coverage = virtual_environments.prepare_virtualenv(venv.packages + ["coverage==3.7.1"])

    coverage_file = os.path.join(virtual_environments.get_vroot(), "coverage-temp.xml")

    output = run(venv_with_coverage, 'coverage', options="--with-coverage --cover-erase --cover-tests --cover-xml --cover-xml-file=\"" + coverage_file + "\"")
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testa.test_mycode'}),
            ServiceMessage('testFinished', {'name': 'testa.test_mycode'}),
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
            ServiceMessage('testStarted', {'name': 'testa.test_func'}),
            ServiceMessage('testIgnored', {'name': 'testa.test_func', 'message': 'Deprecated'}),
            ServiceMessage('testFinished', {'name': 'testa.test_func'}),
        ])


def test_generators(venv):
    output = run(venv, 'generators')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'testa.test_evens(0, 0)'}),
            ServiceMessage('testFinished', {'name': 'testa.test_evens(0, 0)'}),
            ServiceMessage('testStarted', {'name': 'testa.test_evens(1, 3)'}),
            ServiceMessage('testFinished', {'name': 'testa.test_evens(1, 3)'}),
            ServiceMessage('testStarted', {'name': 'testa.test_evens(2, 6)'}),
            ServiceMessage('testFinished', {'name': 'testa.test_evens(2, 6)'}),
        ])


def test_pass(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'nose-guinea-pig.GuineaPig.test_pass'}),
            ServiceMessage('testFinished', {'name': 'nose-guinea-pig.GuineaPig.test_pass'}),
        ])


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])

    assert ms[1].params['details'].find("Traceback") == 0
    assert ms[1].params['details'].find("2 * 2 == 5") > 0


def test_fail_with_msg(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_with_msg')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_with_msg'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    assert ms[1].params['details'].find("Bitte keine Werbung") > 0


def test_fail_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_output')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_output'
    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'out': 'Output line 1|nOutput line 2|nOutput line 3|n'}),
            ServiceMessage('testFailed', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_fail_big_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_big_output')
    test_name = 'nose-guinea-pig.GuineaPig.test_fail_big_output'

    full_line = 'x' * 50000
    leftovers = 'x' * (1024 * 1024 - 50000 * 20)

    assert_service_messages(
        output,
        [ServiceMessage('testStarted', {})] +
        [ServiceMessage('testStdOut', {'out': full_line})] * 20 +
        [ServiceMessage('testStdOut', {'out': leftovers})] +
        [ServiceMessage('testFailed', {'name': test_name})] +
        [ServiceMessage('testFinished', {})]
    )


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
