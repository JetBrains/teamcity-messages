import os
import re
import sys


def normalize_output(s):
    """Replaces the output of the script with a dummy text where needed."""

    s = s.replace("\r", "")
    s = re.sub(r"'Traceback(\|'|[^'])+'", "'TRACEBACK'", s)
    s = re.sub(r"timestamp='\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d'", "timestamp='TIMESTAMP'", s)
    s = re.sub(r"duration='\d+'", "duration='MS'", s)
    s = re.sub(r"File \"[^\"]*\"", "File \"FILE\"", s)
    s = re.sub(r"passed in \d+\.\d+ seconds", "passed in X.XX seconds", s)
    s = re.sub(r"^platform .+$", "platform SPEC", s)
    s = re.sub(r"instance at 0x.*>", "instance at 0x????????>", s)
    s = re.sub(r"object at 0x.*>", "instance at 0x????????>", s)
    s = re.sub(r"line \d+", "line LINE", s)
    s = re.sub(r"\|'EvilClassThatDoesNotExist\|'", "EvilClassThatDoesNotExist", s)  # workaround
    s = re.sub(r"/?(tests/)?test_scripts/", "", s)
    return s


def get_script_path(path):
    return os.path.join(os.path.dirname(__file__), 'test_scripts', path)


def escape_for_tc_message_value(expected_output):
    return expected_output \
        .replace('\r', '') \
        .replace('|', '||') \
        .replace('\n', '|n') \
        .replace("'", "|'") \
        .replace('[', '|[') \
        .replace(']', '|]')


def find_script(venv, name):
    if os.path.isdir(os.path.join(venv, "bin")):
        return os.path.join(venv, "bin", name)
    if os.path.isdir(os.path.join(venv, "Scripts")):
        return os.path.join(venv, "Scripts", name)

    raise RuntimeError("No " + name + " found in " + venv)


def teamcity_message(msg):
    if os.environ.get('TEAMCITY_VERSION') is not None:
        sys.stdout.write(msg)
        sys.stdout.write('\n')
        sys.stdout.flush()