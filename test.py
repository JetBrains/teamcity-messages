# coding=utf-8
import atexit
import os
import sys
import re
import shutil
import tempfile
from os.path import join

eggs = os.path.abspath("test_support")


class Framework(object):
    def __init__(self, name, version, test_command):
        self.name = name
        self.version = version
        self.test_command = test_command

FRAMEWORKS = [
    Framework("unittest", "bundled", ["python", "test-unittest.py"]),
    Framework("nose", "1.2.1", ["nosetests", "test-nose.py"]),
    Framework("pytest", "2.3.4", ["py.test", "--teamcity", "test-pytest.py"]),
]


def normalize_output(s):
    s = s.replace("\r", "")
    s = re.sub(r"File \"[^\"]*\"", "File \"FILE\"", s)
    s = re.sub(r"passed in \d+\.\d+ seconds", "passed in X.XX seconds", s)
    s = re.sub(r"^platform .+$", "platform SPEC", s)
    s = re.sub(r"instance at 0x.*>", "instance at 0x????????>", s)
    s = re.sub(r"line \d+", "line LINE", s)
    return s


def clean_directory(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.mkdir(d)


def build_egg():
    from distutils import core

    from test_support.distribute_setup import use_setuptools

    use_setuptools(to_dir=eggs, download_base="offline-mode")

    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    dist = core.run_setup("setup.py", script_args=["-q", "bdist_egg"])
    return os.path.abspath(dist.dist_files[0][2])


def runner():
    temp = tempfile.mkdtemp()
    atexit.register(shutil.rmtree, temp)

    egg = build_egg()

    ok = True
    for fw in FRAMEWORKS:
        print "* testing %s, %s" % (fw.name, fw.version)

        success = run(fw, egg, temp)
        if not success:
            ok = False

    return ok


def find_script(venv, name):
    if os.path.isdir(join(venv, "bin")):
        return join(venv, "bin", name)
    if os.path.isdir(join(venv, "Scripts")):
        return join(venv, "Scripts", name)

    raise RuntimeError("No " + name + " found in " + venv)


def run(fw, egg, temp):
    venv = join(temp, "venv")
    clean_directory(venv)

    from test_support import virtualenv

    virtualenv.create_environment(venv, use_distribute=True,
                                  never_download=True, search_dirs=[eggs])

    import subprocess

    python = find_script(venv, "python")
    rc = subprocess.call([python, __file__, fw.name, fw.version, egg, venv])

    return rc == 0


def install_file(file):
    from setuptools.command import easy_install

    easy_install.main(["-q", file])


def install_package(package):
    from setuptools.command import easy_install

    easy_install.main(["-q", "-Hnone", "-f", eggs, package])


def in_venv(venv, framework, teamcity_messages_egg):
    install_file(teamcity_messages_egg)

    if framework.version != "bundled":
        install_package(framework.name + "==" + framework.version)

    (cmd, args) = (framework.test_command[0], framework.test_command[1:])
    cmd = find_script(venv, cmd)

    cwd = os.getcwd()
    os.chdir("test")
    clean_directory("__pycache__")
    os.putenv("TEAMCITY_PROJECT_NAME", "project_name")

    import subprocess

    proc = subprocess.Popen([cmd] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = "".join([normalize_output(x) for x in proc.stdout.readlines()])
    proc.wait()

    os.chdir(cwd)

    expected_output_file = join("test", "test-" + framework.name + ".output.gold")
    expected_output = "".join(open(expected_output_file, "r").readlines()).replace("\r", "")

    actual_output_file = join("test", "test-" + framework.name + ".output.tmp")
    if expected_output != output:
        print "Wrong output, check the differences between " + expected_output_file + " and " + actual_output_file
        open(actual_output_file, "w").write(output)
        return False
    else:
        print "OK"
        if os.path.isfile(actual_output_file):
            os.unlink(actual_output_file)
        return True


def main(args):
    success = False

    if len(args) == 0:
        success = runner()
    else:
        (name, version, teamcity_messages_egg, venv) = args

        for fw in FRAMEWORKS:
            if fw.name == name and fw.version == version:
                success = in_venv(venv, fw, teamcity_messages_egg)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main(sys.argv[1:])
