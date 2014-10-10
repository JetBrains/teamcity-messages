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

import py
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


class EchoTeamCityMessages(object):
    def __init__(self, ):
        self.teamcity = TeamcityServiceMessages()
        self.currentSuite = None

    def format_names(self, name):
        if name.find("::") > 0:
            file, testname = name.split("::", 1)
        else:
            file, testname = name, "top_level"

        testname = testname.replace("::()::", ".")
        testname = testname.replace("::", ".")
        testname = testname.strip(".")
        file = file.replace(".", "_").replace(os.sep, ".").replace("/", ".")
        return file, testname

    def pytest_runtest_logstart(self, nodeid, location):
        file, testname = self.format_names(nodeid)
        if not file == self.currentSuite:
            if self.currentSuite:
                self.teamcity.testSuiteFinished(self.currentSuite)
            self.currentSuite = file
            self.teamcity.testSuiteStarted(self.currentSuite)
        self.teamcity.testStarted(testname)

    def pytest_runtest_logreport(self, report):
        """
        :type report: _pytest.runner.TestReport
        """
        file, testname = self.format_names(report.nodeid)
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                duration = timedelta(seconds=report.duration)
                self.teamcity.testFinished(testname, testDuration=duration)
        elif report.failed:
            if report.when in ("call", "setup"):
                self.teamcity.testFailed(testname, str(report.location), str(report.longrepr))
                duration = timedelta(seconds=report.duration)
                self.teamcity.testFinished(testname, testDuration=duration)  # report finished after the failure
            elif report.when == "teardown":
                name = testname + "_teardown"
                self.teamcity.testStarted(name)
                self.teamcity.testFailed(name, str(report.location), str(report.longrepr))
                self.teamcity.testFinished(name)
        elif report.skipped:
            if type(report.longrepr) is tuple and len(report.longrepr) == 3:
                reason = report.longrepr[2]
            else:
                reason = str(report.longrepr)
            self.teamcity.testIgnored(testname, reason)
            self.teamcity.testFinished(testname)  # report finished after the skip

    def pytest_collectreport(self, report):
        if report.failed:
            file, testname = self.format_names(report.nodeid)

            name = file + "_collect"
            self.teamcity.testStarted(name)
            self.teamcity.testFailed(name, str(report.location), str(report.longrepr))
            self.teamcity.testFinished(name)

    def pytest_sessionfinish(self, session, exitstatus, __multicall__):
        if self.currentSuite:
            self.teamcity.testSuiteFinished(self.currentSuite)
