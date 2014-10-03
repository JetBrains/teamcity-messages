# coding=utf-8
import os
import inspect

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestResult


class TeamcityReport(TeamcityTestResult):
    name = 'teamcity-report'
    score = 2

    def __init__(self):
        super(TeamcityReport, self).__init__()

    def configure(self, options, conf):
        self.enabled = is_running_under_teamcity()

    def options(self, parser, env=os.environ):
        pass

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
