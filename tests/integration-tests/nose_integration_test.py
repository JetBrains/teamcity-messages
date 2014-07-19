__author__ = 'Leonid.Bushuev'

import re
import os
import shutil
import subprocess
import pytest
import virtualenv


windows = os.name == 'nt'


class virtual_env_desc:
    def __init__(self, home, bin, python, pip):
        self.home = home
        self.bin = bin
        self.python = python
        self.pip = pip


class service_message:
    def __init__(self, name, params):
        self.name = name
        self.params = params

    def __ge__(self, other):
        """
        :type self: service_message
        :type other: service_message
        :rtype: bool
        """
        if self.name != other.name:
            return False

        for p in other.params:
            if p in self.params:
                v1 = self.params[p]
                v2 = other.params[p]
                if not (v2 in v1):
                    return False
            else:
                return False
        return True

    def __str__(self):
        str = "[" + self.name
        for k, v in self.params.iteritems():
            str = str + ' ' + k + "='" + v + "'"
        str = str + "]"
        return str

    def __repr__(self):
        return self.__str__()


@pytest.fixture(scope='module', params=['1.2.1', '1.3.0', "latest"])
def venv(request):
    """
    Prepares a virtual environment for nose.
    :rtype : virtual_env_desc
    """
    vdir = 'env'
    if os.path.exists(vdir):
        shutil.rmtree(vdir)
    virtualenv.create_environment(vdir)
    vbin = os.path.join(vdir, ('bin', 'Scripts')[windows])
    exe_suffix = ("", ".exe")[windows]
    vpython = os.path.join(vbin, 'python' + exe_suffix)
    vpip = os.path.join(vbin, 'pip' + exe_suffix)

    if request.param == "latest":
        nose_spec = "nose"
    else:
        nose_spec = "nose==" + request.param
    subprocess.call([vpip, "install", nose_spec])

    subprocess.call([vpython, "setup.py", "install"])
    return virtual_env_desc(home=vdir, bin=vbin, python=vpython, pip=vpip)


def test_pass(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_pass')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parseServiceMessages(output)

    assert ms[0] >= service_message('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= service_message('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= service_message('testStarted', {'name': 'test_pass'})
    assert ms[3] >= service_message('testFinished', {'name': 'test_pass'})
    assert ms[4] >= service_message('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[5] >= service_message('testSuiteFinished', {'name': 'nose-guinea-pig'})


def test_fail(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parseServiceMessages(output)

    assert ms[0] >= service_message('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= service_message('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= service_message('testStarted', {'name': 'test_fail'})
    assert ms[3] >= service_message('testFailed', {'name': 'test_fail', 'details': 'Traceback'})
    assert ms[4] >= service_message('testFinished', {'name': 'test_fail'})
    assert ms[5] >= service_message('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[6] >= service_message('testSuiteFinished', {'name': 'nose-guinea-pig'})

    assert "2 * 2 == 5" in output


def test_fail_with_msg(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_with_msg')

    # print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parseServiceMessages(output)

    assert ms[0] >= service_message('testSuiteStarted', {'name': 'nose-guinea-pig'})
    assert ms[1] >= service_message('testSuiteStarted', {'name': 'GuineaPig'})
    assert ms[2] >= service_message('testStarted', {'name': 'test_fail'})
    assert ms[3] >= service_message('testFailed',
                                    {'name': 'test_fail', 'details': 'Bitte keine Werbung'})
    assert ms[4] >= service_message('testFinished', {'name': 'test_fail'})
    assert ms[5] >= service_message('testSuiteFinished', {'name': 'GuineaPig'})
    assert ms[6] >= service_message('testSuiteFinished', {'name': 'nose-guinea-pig'})


def test_fail_output(venv):
    output = run(venv, 'nose-guinea-pig.py', 'GuineaPig', 'test_fail_output')

    print(output)

    assert "##teamcity" in output, "Output should contain TC service messages"

    ms = parseServiceMessages(output)

    assert ms[3] >= service_message('testFailed', {'name': 'test_fail', 'details': 'Output line 1'})
    assert ms[3] >= service_message('testFailed', {'name': 'test_fail', 'details': 'Output line 2'})
    assert ms[3] >= service_message('testFailed', {'name': 'test_fail', 'details': 'Output line 3'})


def run(venv, file, clazz, test):
    """
    Executes the specified test using nose
    """

    # environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = venv.home
    env['TEAMCITY_VERSION'] = "0.0.0"
    env['TEAMCITY_PROJECT'] = "TEST"

    # Start the process and wait for its output
    command = os.path.join(venv.bin, 'nosetests') + " -v " \
              + os.path.join('tests', 'guinea-pigs', file) + ":" + clazz + '.' + test
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
                            shell=True)
    output = "".join([x.decode() for x in proc.stdout.readlines()])
    proc.wait()

    return output


def normalizeOutput(output):
    output = re.sub(r"timestamp='\d+.*?\d+'", "timestamp='TTT'", output)
    output = re.sub(r"duration='\d+'", "duration='0'", output)
    return output


def parseServiceMessages(text):
    """
    Parses service messages from the given build log.
    :type text: str
    :rtype: list
    """
    messages = list()
    for line in text.splitlines():
        r = line.strip()
        if r.startswith("##teamcity[") and r.endswith("]"):
            m = parseSM(r)
            messages.append(m)
    return messages


def parseSM(str):
    """
    Parses one service message.
    :type str: str
    :rtype: service_message
    """
    b1 = str.index('[')
    b2 = str.rindex(']', b1)
    inner = str[b1 + 1:b2].strip()
    space1 = inner.find(' ')
    namelen = space1 if space1 >= 0 else inner.__len__()
    name = inner[0:namelen]
    params = dict()
    beg = namelen + 1
    while beg < inner.__len__():
        if inner[beg] == '_':
            beg = beg + 1
            continue
        eq = inner.find('=', beg)
        if eq == -1: break
        q1 = inner.find("'", eq)
        if q1 == -1: break
        q2 = inner.find("'", q1 + 1)
        while (q2 > 0 and inner[q2 - 1] == '|'): q2 = inner.find("'", q2 + 1)
        if q2 == -1: break
        param_name = inner[beg:eq].strip()
        param_value = inner[q1 + 1:q2]
        params[param_name] = param_value
        beg = q2 + 1
    return service_message(name, params)





