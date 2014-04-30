# coding=utf-8
import os
import sys
import re
import shutil
from os.path import join
import traceback

sdfsdf
eggs = os.path.abspath("test_support")
test_name = 'Unnamed_Test'
in_teamcity = False


werrewclass Framework(object):
    def __init__(self, name, version, test_command):
ame = name
     self.version = version
       self.test_command = test_command


FRAMEWORKS = 
    Framework("unittest", "bundled", ["python", "test-unittest.py"]),
    Framework("nose", 1", ["nosetests", "-w", "nose_integration_tests"]),
    Framework("pytest",3.4", ["py.test", "--teamcity", "test-pytest.py"]),
]


def generate_test_name(fw_name, fw_version):
    return "Framework.%s(%s)" % (fw_name, fw_version)


def normalize_output(s):
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
    return s


def clean_directory(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.mkdir(d)


def build_egg():
    from distutils import core

    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    dist = core.run_setup("setup.py", script_args=["-q", "bdist_egg"])
    return os.path.abspath(dist.dist_files[0][2])


def tc_msg(msg):
    if os.environ.get('TEAMCITY_VERSION') is not None:
        sys.stdout.write(msg)
        sys.stdout.write('\n')
        sys.stdout.flush()


def find_script(venv, name):
    if os.path.isdir(join(venv, "bin")):
        return join(venv, "bin", name)
    if os.path.isdir(join(venv, "Scripts")):
        return join(venv, "Scripts", name)

    raise RuntimeError("No " + name + " found in " + venv)


def install_file(file_to_install):
    from setuptools.command import easy_install

    easy_install.main(["-q", file_to_install])


def install_package(package):
    from setuptools.command import easy_install

    easy_install.main(["-q", "-Hnone", "-f", eggs, package])


def escape_for_tc_message_value(expected_output):
    return expected_output \
        .replace('\r', '') \
        .replace('|', '||') \
        .replace('\n', '|n') \
        .replace("'", "|'") \
        .replace('[', '|[') \
        .replace(']', '|]')


def run_test_internal(venv, framework):
    teamcity_messages_egg = build_egg()
    install_file(teamcity_messages_egg)

    if framework.version != "bundled":
        install_package(framework.name + "==" + framework.version)

    global in_teamcity, test_name

    (cmd, args) = (framework.test_command[0], framework.test_command[1:])
    cmd = find_script(venv, cmd)

    cwd = os.getcwd()
    os.chdir("test")
    clean_directory("__pycache__")
    os.putenv("TEAMCITY_PROJECT_NAME", "project_name")

    import subprocess

    proc = subprocess.Popen([cmd] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = "".join([normalize_output(x.decode()) for x in proc.stdout.readlines()])
    proc.wait()

    os.chdir(cwd)

    file_prefix = join("test", "test-" + framework.name + ".output")

    expected_output_file = file_prefix + ".gold"
    expected_output = "".join(open(expected_output_file, "r").readlines()).replace("\r", "")

    actual_output_file = file_prefix + ".tmp"
    if expected_output != output:
        if in_teamcity:
            expected_string = escape_for_tc_message_value(expected_output)
            actual_string = escape_for_tc_message_value(output)
            message = "##teamcity[testFailed type='comparisonFailure' name='%s' message='Output doesn|'t match the relative gold file. See the diff for detail.' expected='%s' actual='%s']\n" \
                      % (test_name, expected_string, actual_string)
            sys.stdout.write(message)
            sys.stdout.flush()
        else:
            sys.stderr.write(
                "ERROR Wrong output, check the differences between " + expected_output_file + " and " + actual_output_file + "\n")
            open(actual_output_file, "w").write(output)

            DIFF = "/usr/bin/diff"
            if os.path.exists(DIFF):
                subprocess.call([DIFF, "-u", expected_output_file, actual_output_file])
        return 1
    else:
        sys.stdout.write("OK\n")
        if os.path.isfile(actual_output_file):
            os.unlink(actual_output_file)
        return 2


#noinspection PyBroadException
def run_one_test_in_venv(venv, framework):
    """
    Runs one test for the specified virtual env and framework.
    Returns:
        2 - the test passed successfully
        1 - the test finished with non-matched output (test failure)
        0 or an exception - the test not finished (probably a run-time error happened)
    """
    try:
        return run_test_internal(venv, framework)
    except:
        err_name = escape_for_tc_message_value(sys.exc_info()[0].__name__)
        trace = escape_for_tc_message_value(traceback.format_exc())
        if in_teamcity:
            tc_msg("##teamcity[testFailed name='%s' message='%s' details='%s']" % (test_name, err_name, trace))
        return 0


def run_one_test(args):
    (name, version, venv) = args
    global test_name, in_teamcity
    test_name = generate_test_name(name, version)
    in_teamcity = os.environ.get('TEAMCITY_VERSION') is not None
    success = 0
    for fw in FRAMEWORKS:
        if fw.name == name and fw.version == version:
            success = run_one_test_in_venv(venv, fw)
            break
    sys.exit(success)


def main(args):
    if len(args) == 0:
        from tests import main as main2
        main2()
    else:
        run_one_test(args)


if __name__ == "__main__":
    main(sys.argv[1:])
