
if __name__ == "__main__":
    from behave.formatter import _registry
    from behave.configuration import Configuration
    from behave.runner import Runner
    from teamcity.jb_behave_formatter import TeamcityFormatter

    _registry.register_as("TeamcityFormatter", TeamcityFormatter)
    configuration = Configuration()
    configuration.format = ["TeamcityFormatter"]
    configuration.stdout_capture = False
    configuration.stderr_capture = False
    Runner(configuration).run()
