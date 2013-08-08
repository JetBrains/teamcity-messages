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
from datetime import datetime, timedelta

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
    teamcityReporiting = getattr(config, '_teamcityReporting', None)
    if teamcityReporiting:
        del config._teamcityReporting
        config.pluginmanager.unregister(teamcityReporiting)


class EchoTeamCityMessages(object):
    def __init__(self, ):
        self.tw = py.io.TerminalWriter(py.std.sys.stdout)
        self.teamcity = TeamcityServiceMessages(self.tw)
        self.currentSuite = None

    def format_names(self, name):
        split = '.py'
        file, testname = name.split(split, 1)
        if not testname:
            testname = file
            file = 'NO_TEST_FILE_FOUND'
        testname = testname.replace("::()::", ".")
        testname = testname.replace("::", ".")
        testname = testname.strip(".")
        return "".join([file, split]), testname

    def pytest_runtest_logstart(self, nodeid, location):
        file, testname = self.format_names(nodeid)
        if not file == self.currentSuite:
            if self.currentSuite:
                self.teamcity.testSuiteFinished(self.currentSuite)
            self.currentSuite = file
            self.teamcity.testSuiteStarted(self.currentSuite)
        self.teamcity.testStarted(testname)

    def pytest_runtest_logreport(self, report):
        file, testname = self.format_names(report.nodeid)
        if report.passed:
            if report.when == "call":  # ignore setup/teardown
                duration = timedelta(seconds=report.duration)
                self.teamcity.testFinished(testname, testDuration=duration)
        elif report.failed:
            if report.when == "call":
                self.teamcity.testFailed(testname, str(report.location), str(report.longrepr))
                duration = timedelta(seconds=report.duration)
                self.teamcity.testFinished(testname, testDuration=duration)  # report finished after the failure
        elif report.skipped:
            self.teamcity.testIgnored(testname, str(report.longrepr))
            self.teamcity.testFinished(testname)  # report finished after the skip

    def pytest_sessionfinish(self, session, exitstatus, __multicall__):
        if self.currentSuite:
            self.teamcity.testSuiteFinished(self.currentSuite)
