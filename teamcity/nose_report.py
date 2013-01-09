# coding=utf-8
import types
import os

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestResult


class TeamcityReport(TeamcityTestResult):
    name = 'teamcity-report'
    score = 2

    def __init__(self):
        super(TeamcityTestResult, self).__init__()

    def configure(self, options, conf):
        self.enabled = is_running_under_teamcity()

    def options(self, parser, env=os.environ):
        pass

    def getCtxName(self, ctx):
        if isinstance(ctx, types.ModuleType):
            return ctx.__name__
        elif isinstance(ctx, type) or isinstance(ctx, types.ClassType) or isinstance(ctx, types.InstanceType):
            return ctx.__module__ + '.' + ctx.__name__
        else:
            return str(ctx)

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
