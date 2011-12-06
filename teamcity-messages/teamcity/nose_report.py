import traceback, types, sys, os
from nose.plugins import Plugin

from teamcity import underTeamcity
from teamcity.unittestpy import TeamcityTestResult

class TeamcityReport(TeamcityTestResult):
    name = 'teamcity-report'
    score = 2

    def __init__(self):
        super(TeamcityTestResult, self).__init__()
        
    def configure(self, options, conf):
        self.enabled = underTeamcity()

    def options(self, parser, env=os.environ):
        pass

    def getCtxName(self, ctx):
        if type(ctx) is types.ModuleType:
            return ctx.__name__
        elif type(ctx) in (types.TypeType, types.ClassType):
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
