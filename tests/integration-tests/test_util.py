import os

import subprocess


def get_teamcity_messages_root():
    path = os.getcwd()
    while path != os.path.dirname(path):
        setup_py = os.path.join(path, "setup.py")
        if os.path.exists(setup_py):
            return path
        path = os.path.dirname(path)
    raise Exception("Could not find teamcity-messages project root from working directory " + os.getcwd())


def run_command(command, env, print_output=True, set_tc_version=True):
    encoding = "UTF-8"  # Force UTF for remote process and parse its output in same encoding
    env.update({'PYTHONIOENCODING': encoding})
    if set_tc_version:
        env['TEAMCITY_VERSION'] = "0.0.0"
    print("RUN: " + command)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=env, shell=True, cwd=get_teamcity_messages_root())
    output = "".join([x.decode(encoding) for x in proc.stdout.readlines()])
    proc.wait()
    if print_output:
        print("OUTPUT:" + output.replace("#", "*"))
    return output
