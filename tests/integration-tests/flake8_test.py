import os
import subprocess

import pytest

import virtual_environments
from service_messages import ServiceMessage, assert_service_messages, parse_service_messages


@pytest.fixture(scope='module', params=["flake8==3.7.9", "flake8"])
def venv_flake8_v3(request):
    return virtual_environments.prepare_virtualenv([request.param])


def test_smoke_flake8_v3(venv_flake8_v3):
    output = run(venv_flake8_v3, options="")

    file_name = "./smoke.py"
    test1_name = "pep8: " + file_name + ": E302 expected 2 blank lines, found 1"
    test2_name = "pep8: " + file_name + ": W391 blank line at end of file"

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


def test_flake8_v3_no_teamcity(venv_flake8_v3):
    output = run(venv_flake8_v3, options="--no-teamcity")

    assert_service_messages(output, [])


def test_flake8_v3_no_reporting_without_explicit_option_and_tc_env(venv_flake8_v3):
    output = run(venv_flake8_v3, options="", set_tc_version=False)

    ms = parse_service_messages(output)
    assert len(ms) == 0

    assert output.find("E302") > 0
    assert output.find("W391") > 0


def run(venv, options, set_tc_version=True):
    env = virtual_environments.get_clean_system_environment()

    if set_tc_version:
        env['TEAMCITY_VERSION'] = "0.0.0"
    elif 'TEAMCITY_VERSION' in env:  # There could be this value in env when tests launched via PyCharm
        del env['TEAMCITY_VERSION']

    flake8_dir = os.path.join(os.getcwd(), "tests", "guinea-pigs", "flake8")

    command = os.path.join(
        os.getcwd(), venv.bin,
        'flake8' + virtual_environments.get_exe_suffix()) + " " + options + " ."

    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            cwd=flake8_dir, shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    print("OUTPUT:" + output.replace("#", "$"))

    return output
