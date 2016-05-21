import os
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages, parse_service_messages


@pytest.fixture(scope='module', params=["flake8==2.0.0", "flake8==2.4.0", "flake8"])
def venv(request):
    return virtual_environments.prepare_virtualenv([request.param])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_smoke(venv):
    output = run(venv, options="--teamcity")

    file_name = "tests/guinea-pigs/flake8/smoke.py"
    test1_name = "pep8: " + file_name + ":3:1: E302 expected 2 blank lines, found 1"
    test2_name = "pep8: " + file_name + ":7:1: W391 blank line at end of file"

    assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFailed', {'name': test1_name, 'message': "E302 expected 2 blank lines, found 1"}),
            ServiceMessage('testFinished', {'name': test1_name}),

            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFailed', {'name': test2_name, 'message': "W391 blank line at end of file"}),
            ServiceMessage('testFinished', {'name': test2_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_no_reporting_without_explicit_option(venv):
    output = run(venv, options="")

    ms = parse_service_messages(output)
    assert len(ms) == 0

    assert output.find("E302") > 0
    assert output.find("W391") > 0


def run(venv, options):
    env = virtual_environments.get_clean_system_environment()

    command = os.path.join(
        os.getcwd(), venv.bin,
        'flake8' + virtual_environments.get_exe_suffix()) + " " + options + " " + os.path.join("tests", "guinea-pigs", "flake8")

    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            cwd=os.path.join(os.getcwd()), shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "$"))

    return output
