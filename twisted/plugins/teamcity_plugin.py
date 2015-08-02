import sys
from teamcity.unittestpy import TeamcityTestResult
from twisted.trial.reporter import Reporter
from twisted.plugins.twisted_trial import _Reporter


class TeamcityReporter(TeamcityTestResult, Reporter):

    def __init__(self,
                 stream=sys.stdout,
                 tbformat='default',
                 realtime=False,
                 publisher=None):
        TeamcityTestResult.__init__(self)
        Reporter.__init__(self,
                          stream=stream,
                          tbformat=tbformat,
                          realtime=realtime,
                          publisher=publisher)

Teamcity = _Reporter("Teamcity Reporter",
                     "twisted.plugins.teamcity_plugin",
                     description="teamcity messages",
                     longOpt="teamcity",
                     shortOpt="teamcity",
                     klass="TeamcityReporter")
