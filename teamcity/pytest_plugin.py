# coding=utf-8
"""
Aaron Buchanan
Nov. 2012

Plug-in for py.test for reporting to TeamCity server
Report results to TeamCity during test execution for immediate reporting
    when using TeamCity.

This should be installed as a py.test plugin and is enabled by running
py.test with a --teamcity command line option.
"""

import os
from datetime import timedelta

from teamcity.messages import TeamcityServiceMessages


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting", "reporting", after="general")
    group._addoption('--teamcity', action="count",
                     dest="teamcity", default=0, help="output teamcity messages")


def pytest_configure(config):
    if config.option.teamcity >= 1:
        config._teamcityReporting = EchoTeamCityMessages()
        config.pluginmanager.register(config._teamcityReporting)


def pytest_unconfigure(config):
    teamcity_reporting = getattr(config, '_teamcityReporting', None)
    if teamcity_reporting:
        del config._teamcityReporting
        config.pluginmanager.unregister(teamcity_reporting)

# The following code relies on py.test nodeid uniqueness


class EchoTeamCityMessages(object):
    def __init__(self, ):
        self.teamcity = TeamcityServiceMessages()
        self.currentSuite = None
        self.test_start_reported_mark = set()

    def format_test_id(self, nodeid):
        test_id = nodeid

        if test_id.find("::") < 0:
            test_id += "::top_level"

        test_id = test_id.replace("::()::", "::")

        test_id = test_id.replace(".", "_").replace(os.sep, ".").replace("/", ".").replace('::', '.')

        return test_id

    def pytest_runtest_logstart(self, nodeid, location):
        self.ensure_test_start_reported(self.format_test_id(nodeid))

    def ensure_test_start_reported(self, test_id):
        if test_id not in self.test_start_reported_mark:
            self.teamcity.testStarted(test_id, flowId=test_id)
            self.test_start_reported_mark.add(test_id)

    def pytest_runtest_logreport(self, report):
        """
        :type report: _pytest.runner.TestReport
        """
        test_id = self.format_test_id(report.nodeid)
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                duration = timedelta(seconds=report.duration)
                self.ensure_test_start_reported(test_id)
                self.teamcity.testFinished(test_id, testDuration=duration, flowId=test_id)
        elif report.failed:
            if report.when in ("call", "setup"):
                self.ensure_test_start_reported(test_id)
                self.teamcity.testFailed(test_id, str(report.location), str(report.longrepr), flowId=test_id)
                duration = timedelta(seconds=report.duration)
                self.teamcity.testFinished(test_id, testDuration=duration, flowId=test_id)  # report finished after the failure
            elif report.when == "teardown":
                name = test_id + "_teardown"
                self.teamcity.testStarted(name, flowId=test_id)
                self.teamcity.testFailed(name, str(report.location), str(report.longrepr), flowId=test_id)
                self.teamcity.testFinished(name, flowId=test_id)
        elif report.skipped:
            if type(report.longrepr) is tuple and len(report.longrepr) == 3:
                reason = report.longrepr[2]
            else:
                reason = str(report.longrepr)
            self.ensure_test_start_reported(test_id)
            self.teamcity.testIgnored(test_id, reason, flowId=test_id)
            self.teamcity.testFinished(test_id, flowId=test_id)  # report finished after the skip

    def pytest_collectreport(self, report):
        if report.failed:
            test_id = self.format_test_id(report.nodeid) + "_collect"

            self.teamcity.testStarted(test_id, flowId=test_id)
            self.teamcity.testFailed(test_id, str(report.location), str(report.longrepr), flowId=test_id)
            self.teamcity.testFinished(test_id, flowId=test_id)

    def pytest_sessionfinish(self, session, exitstatus, __multicall__):
        if self.currentSuite:
            self.teamcity.testSuiteFinished(self.currentSuite)
