# coding=utf-8
import os
import inspect

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestResult


class TeamcityReport(TeamcityTestResult):
    name = 'teamcity-report'
    score = 10000

    def __init__(self):
        super(TeamcityReport, self).__init__()

        self.enabled = False

    def configure(self, options, conf):
        self.enabled = is_running_under_teamcity()

    def options(self, parser, env=os.environ):
        pass

    def is_doctest_class_name(self, fqn):
        return super(TeamcityReport, self).is_doctest_class_name(fqn) or fqn == "nose.plugins.doctests.DocTestCase"

    def addDeprecated(self, test):
        test_id = self.get_test_id(test)
        self.messages.testIgnored(test_id, message="Deprecated")

    def _lastPart(self, name):
        nameParts = name.split('.')
        return nameParts[-1]

    def setOutputStream(self, stream):
        self.output = stream
        self.create_messages()

        class dummy:
            def write(self, *arg):
                pass

            def writeln(self, *arg):
                pass

            def flush(self):
                pass

        d = dummy()
        return d
