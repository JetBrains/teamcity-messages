import os

import subprocess

import virtual_environments


def get_teamcity_messages_root():
    path = os.getcwd()
    while path != os.path.dirname(path):
        setup_py = os.path.join(path, "setup.py")
        if os.path.exists(setup_py):
            return path
        path = os.path.dirname(path)
    raise Exception("Could not find teamcity-messages project root from working directory " + os.getcwd())


def run_command(command, env=None, print_output=True, set_tc_version=True, cwd=None):
    encoding = "UTF-8"  # Force UTF for remote process and parse its output in same encoding

    if env is not None:
        env_copy = dict(env)
    else:
        env_copy = virtual_environments.get_clean_system_environment()
    env_copy.update({'PYTHONIOENCODING': encoding})
    if set_tc_version:
        env_copy['TEAMCITY_VERSION'] = "0.0.0"
    elif 'TEAMCITY_VERSION' in env_copy:  # There could be this value in env when tests launched via PyCharm
        del env_copy['TEAMCITY_VERSION']

    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                            env=env_copy, cwd=cwd or get_teamcity_messages_root())
    output = "".join([x.decode(encoding) for x in proc.stdout.readlines()])
    proc.wait()
    if print_output:
        print("OUTPUT:" + output.replace("#", "*"))
    return output
