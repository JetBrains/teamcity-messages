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

    def getTestName(self, test):
        short_description = test.shortDescription()
        test_id = test.id()
        test_id_last_part = self._lastPart(test_id)

        # Force test_id for nose doctests
        if self._class_fullname(test) != "nose.plugins.doctests.DocTestCase":
            if short_description and short_description != test_id:
                return "%s (%s)" % (test_id_last_part, short_description)

        return test_id_last_part

    def addDeprecated(self, test):
        self.messages.testIgnored(self.test_name, message="Deprecated")

    def getCtxName(self, ctx):
        if inspect.ismodule(ctx):
            name = self._lastPart(ctx.__name__)
        else:
            name = ctx.__name__ if hasattr(ctx, "__name__") else str(ctx)
        return name

    def _lastPart(self, name):
        nameParts = name.split('.')
        return nameParts[-1]

    def setOutputStream(self, stream):
        self.output = stream
        self.createMessages()

        class dummy:
            def write(self, *arg):
                pass

            def writeln(self, *arg):
                pass

            def flush(self):
                pass

        d = dummy()
        return d

    def startContext(self, ctx):
        self.messages.testSuiteStarted(self.getCtxName(ctx))

    def stopContext(self, ctx):
        self.messages.testSuiteFinished(self.getCtxName(ctx))
