# coding=utf-8
import sys
from unittest import TestResult, TextTestRunner
import datetime
import re

from teamcity.messages import TeamcityServiceMessages
from teamcity.common import is_string, get_class_fullname, convert_error_to_string

_real_stdout = sys.stdout


class TeamcityTestResult(TestResult):
    def __init__(self, stream=_real_stdout, descriptions=None, verbosity=None):
        super(TeamcityTestResult, self).__init__()

        self.test_started_datetime_map = {}
        self.messages = TeamcityServiceMessages(stream)

    def get_test_id(self, test):
        if is_string(test):
            return test

        # Force test_id for doctests
        if get_class_fullname(test) != "doctest.DocTestCase":
            desc = test.shortDescription()
            if desc and desc != test.id():
                return "%s (%s)" % (test.id(), desc)

        return test.id()

    def addSuccess(self, test):
        super(TeamcityTestResult, self).addSuccess(test)

    def addExpectedFailure(self, test, err):
        super(TeamcityTestResult, self).addExpectedFailure(test, err)

        err = convert_error_to_string(err)
        test_id = self.get_test_id(test)

        self.messages.testIgnored(test_id, message="Expected failure: " + err, flowId=test_id)

    def addSkip(self, test, reason=""):
        if sys.version_info >= (2, 7):
            super(TeamcityTestResult, self).addSkip(test, reason)

        test_id = self.get_test_id(test)
        self.messages.testIgnored(test_id, message="Skipped" + ((": " + reason) if reason else ""), flowId=test_id)

    def addUnexpectedSuccess(self, test):
        super(TeamcityTestResult, self).addUnexpectedSuccess(test)

        test_id = self.get_test_id(test)
        self.messages.testFailed(test_id, message='Failure',
                                 details="Test should not succeed since it's marked with @unittest.expectedFailure",
                                 flowId=test_id)

    def addError(self, test, err, *k):
        super(TeamcityTestResult, self).addError(test, err)

        if get_class_fullname(test) == "unittest.suite._ErrorHolder":
            # This is a standalone error

            test_name = test.id()
            # patch setUpModule (__main__) -> __main__.setUpModule
            test_name = re.sub(r'^(.*) \((.*)\)$', r'\2.\1', test_name)

            self.messages.testStarted(test_name, flowId=test_name)
            self.report_fail(test_name, 'Failure', err)
            self.messages.testFinished(test_name, flowId=test_name)
        elif get_class_fullname(err[0]) == "unittest2.case.SkipTest":
            message = getattr(err[1], "message", '')
            self.addSkip(test, message)
        else:
            self.report_fail(test, 'Error', err)

    def addFailure(self, test, err, *k):
        super(TeamcityTestResult, self).addFailure(test, err)

        self.report_fail(test, 'Failure', err)

    def report_fail(self, test, fail_type, err):
        test_id = self.get_test_id(test)
        self.messages.testFailed(test_id, message=fail_type, details=convert_error_to_string(err), flowId=test_id)

    def startTest(self, test):
        super(TeamcityTestResult, self).startTest(test)

        test_id = self.get_test_id(test)

        self.test_started_datetime_map[test_id] = datetime.datetime.now()
        self.messages.testStarted(test_id, captureStandardOutput='true', flowId=test_id)

    def stopTest(self, test):
        super(TeamcityTestResult, self).stopTest(test)

        test_id = self.get_test_id(test)

        time_diff = datetime.datetime.now() - self.test_started_datetime_map[test_id]
        self.messages.testFinished(test_id, testDuration=time_diff, flowId=test_id)


class TeamcityTestRunner(TextTestRunner):
    resultclass = TeamcityTestResult


if __name__ == '__main__':
    from unittest import main

    main(module=None, testRunner=TeamcityTestRunner())
