import os


def get_teamcity_messages_root():
    path = os.getcwd()
    while path != os.path.dirname(path):
        setup_py = os.path.join(path, "setup.py")
        if os.path.exists(setup_py):
            return path
        path = os.path.dirname(path)
    raise Exception("Could not find teamcity-messages project root from working directory " + os.getcwd())
