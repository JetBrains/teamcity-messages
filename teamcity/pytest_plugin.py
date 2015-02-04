# coding=utf-8
"""
Aaron Buchanan
Nov. 2012

Plug-in for py.test for reporting to TeamCity server
Report results to TeamCity during test execution for immediate reporting
    when using TeamCity.

This should be installed as a py.test plugin and will be automatically enabled by running
tests under TeamCity build.
"""

import os
import sys
import re
import traceback
from datetime import timedelta

from teamcity.messages import TeamcityServiceMessages
from teamcity.common import limit_output, split_output, convert_error_to_string
from teamcity import is_running_under_teamcity


def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting", "reporting", after="general")

    group._addoption('--teamcity', action="count",
                     dest="teamcity", default=0, help="force output of JetBrains TeamCity service messages")
    group._addoption('--no-teamcity', action="count",
                     dest="no_teamcity", default=0, help="disable output of JetBrains TeamCity service messages")


def pytest_configure(config):
    if config.option.no_teamcity >= 1:
        enabled = False
    elif config.option.teamcity >= 1:
        enabled = True
    else:
        enabled = is_running_under_teamcity()

    if enabled:
        output_capture_enabled = getattr(config.option, 'capture', 'fd') != 'no'
        coverage_controller = _get_coverage_controller(config)

        config._teamcityReporting = EchoTeamCityMessages(output_capture_enabled, coverage_controller)
        config.pluginmanager.register(config._teamcityReporting)


def pytest_unconfigure(config):
    teamcity_reporting = getattr(config, '_teamcityReporting', None)
    if teamcity_reporting:
        del config._teamcityReporting
        config.pluginmanager.unregister(teamcity_reporting)


def _get_coverage_controller(config):
    cov_plugin = config.pluginmanager.getplugin('_cov')
    if not cov_plugin:
        return None

    return cov_plugin.cov_controller


# The following code relies on py.test nodeid uniqueness


class EchoTeamCityMessages(object):
    def __init__(self, output_capture_enabled, coverage_controller):
        self.coverage_controller = coverage_controller
        self.output_capture_enabled = output_capture_enabled

        self.teamcity = TeamcityServiceMessages()
        self.test_start_reported_mark = set()

        self.max_reported_output_size = 1 * 1024 * 1024
        self.reported_output_chunk_size = 50000

    def format_test_id(self, nodeid):
        test_id = nodeid

        if test_id.find("::") < 0:
            test_id += "::top_level"

        test_id = test_id.replace("::()::", "::")
        test_id = re.sub(r"\.pyc?::", r"::", test_id)
        test_id = test_id.replace(".", "_").replace(os.sep, ".").replace("/", ".").replace('::', '.')

        return test_id

    def pytest_runtest_logstart(self, nodeid, location):
        self.ensure_test_start_reported(self.format_test_id(nodeid))

    def ensure_test_start_reported(self, test_id):
        if test_id not in self.test_start_reported_mark:
            self.teamcity.testStarted(test_id, flowId=test_id, captureStandardOutput='false' if self.output_capture_enabled else 'true')
            self.test_start_reported_mark.add(test_id)

    def report_has_output(self, report):
        for (secname, data) in report.sections:
            if report.when in secname and ('stdout' in secname or 'stderr' in secname):
                return True
        return False

    def report_test_output(self, report, test_id, when):
        for (secname, data) in report.sections:
            if when not in secname:
                continue
            if not data:
                continue

            if 'stdout' in secname:
                for chunk in split_output(limit_output(data)):
                    self.teamcity.testStdOut(test_id, out=chunk, flowId=test_id)
            elif 'stderr' in secname:
                for chunk in split_output(limit_output(data)):
                    self.teamcity.testStdErr(test_id, out=chunk, flowId=test_id)

    def pytest_runtest_logreport(self, report):
        """
        :type report: _pytest.runner.TestReport
        """
        orig_test_id = self.format_test_id(report.nodeid)

        suffix = '' if report.when == 'call' else ('_' + report.when)
        test_id = orig_test_id + suffix

        duration = timedelta(seconds=report.duration)

        if report.passed:
            # Do not report passed setup/teardown if no output
            if report.when == 'call' or self.report_has_output(report):
                self.ensure_test_start_reported(test_id)
                self.report_test_output(report, test_id, report.when)
                self.teamcity.testFinished(test_id, testDuration=duration, flowId=test_id)
        elif report.failed:
            self.ensure_test_start_reported(test_id)
            self.report_test_output(report, test_id, report.when)
            self.teamcity.testFailed(test_id, str(report.location), str(report.longrepr), flowId=test_id)
            self.teamcity.testFinished(test_id, testDuration=duration, flowId=test_id)

            # If test setup failed, report test failure as well
            if report.when == 'setup':
                self.ensure_test_start_reported(orig_test_id)
                self.teamcity.testFailed(orig_test_id, "test setup failed, see %s test failure" % test_id, flowId=orig_test_id)
                self.teamcity.testFinished(orig_test_id, flowId=orig_test_id)
        elif report.skipped:
            if type(report.longrepr) is tuple and len(report.longrepr) == 3:
                reason = report.longrepr[2]
            else:
                reason = str(report.longrepr)
            self.ensure_test_start_reported(orig_test_id)
            self.report_test_output(report, orig_test_id, report.when)
            self.teamcity.testIgnored(orig_test_id, reason, flowId=orig_test_id)
            self.teamcity.testFinished(orig_test_id, flowId=orig_test_id)

    def pytest_collectreport(self, report):
        if report.failed:
            test_id = self.format_test_id(report.nodeid) + "_collect"

            self.teamcity.testStarted(test_id, flowId=test_id)
            self.teamcity.testFailed(test_id, str(report.location), str(report.longrepr), flowId=test_id)
            self.teamcity.testFinished(test_id, flowId=test_id)

    def pytest_terminal_summary(self):
        if self.coverage_controller is not None:
            try:
                self._report_coverage()
            except:
                tb = traceback.format_exc()
                self.teamcity.customMessage("Coverage statistics reporting failed", "ERROR", errorDetails=tb)

    def _report_coverage(self):
        from coverage.misc import NotPython
        from coverage.report import Reporter
        from coverage.results import Numbers

        class _CoverageReporter(Reporter):
            def __init__(self, coverage, config, messages):
                super(_CoverageReporter, self).__init__(coverage, config)

                self.branches = coverage.data.has_arcs()
                self.messages = messages

            def report(self, morfs, outfile=None):
                self.find_code_units(morfs)

                total = Numbers()

                for cu in self.code_units:
                    try:
                        analysis = self.coverage._analyze(cu)
                        nums = analysis.numbers
                        total += nums
                    except KeyboardInterrupt:
                        raise
                    except:
                        if self.config.ignore_errors:
                            continue

                        err = sys.exc_info()
                        typ, msg = err[:2]
                        if typ is NotPython and not cu.should_be_python():
                            continue

                        test_id = cu.name
                        details = convert_error_to_string(err)

                        self.messages.testStarted(test_id, flowId=test_id)
                        self.messages.testFailed(test_id, message="Coverage analysis failed", details=details, flowId=test_id)
                        self.messages.testFinished(test_id, flowId=test_id)

                if total.n_files > 0:
                    covered = total.n_executed + (total.n_executed_branches if self.branches else 0)
                    total_statements = total.n_statements + (total.n_branches if self.branches else 0)
                    self.messages.buildStatisticLinesCovered(covered)
                    self.messages.buildStatisticTotalLines(total_statements)
                    self.messages.buildStatisticLinesUncovered(total_statements - covered)
        reporter = _CoverageReporter(
            self.coverage_controller.cov,
            self.coverage_controller.cov.config,
            self.teamcity,
        )
        reporter.report(None)
