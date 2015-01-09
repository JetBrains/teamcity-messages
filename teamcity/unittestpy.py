# coding=utf-8
import traceback
import sys
from unittest import TestResult
import datetime
import re

from teamcity.messages import TeamcityServiceMessages
from teamcity.common import is_string


# Added *k to some methods to get compatibility with nosetests
class TeamcityTestResult(TestResult):
    def __init__(self, stream=sys.stdout):
        super(TeamcityTestResult, self).__init__()

        self.output = stream
        self.test_started_datetime_map = {}

        self.create_messages()

    def create_messages(self):
        self.messages = TeamcityServiceMessages(self.output)

    def convert_error_to_string(self, err):
        try:
            exctype, value, tb = err
            return ''.join(traceback.format_exception(exctype, value, tb))
        except:
            tb = traceback.format_exc()
            return "*FAILED TO GET TRACEBACK*: " + tb

    def _class_fullname(self, o):
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__

    def is_doctest_class_name(self, fqn):
        return fqn == "doctest.DocTestCase"

    def get_test_id(self, test):
        if is_string(test):
            return test

        # Force test_id for doctests
        if not self.is_doctest_class_name(self._class_fullname(test)):
            desc = test.shortDescription()
            if desc and desc != test.id():
                return "%s (%s)" % (test.id(), desc)

        return test.id()

    def addSuccess(self, test, *k):
        super(TeamcityTestResult, self).addSuccess(test)

    def addExpectedFailure(self, test, err):
        # workaround nose bug on python 3

        super(TeamcityTestResult, self).addExpectedFailure(test, err)

        err = self.convert_error_to_string(err)

        self.messages.testIgnored(self.get_test_id(test), message="Expected failure: " + err)

    def addSkip(self, test, reason="", *k):
        if sys.version_info >= (2, 7):
            super(TeamcityTestResult, self).addSkip(test, reason)

        self.messages.testIgnored(self.get_test_id(test), message="Skipped" + ((": " + reason) if reason else ""))

    def addUnexpectedSuccess(self, test):
        super(TeamcityTestResult, self).addUnexpectedSuccess(test)

        self.messages.testFailed(self.get_test_id(test), message='Failure',
                                 details="Test should not succeed since it's marked with @unittest.expectedFailure")

    def addError(self, test, err, *k):
        super(TeamcityTestResult, self).addError(test, err)

        if self._class_fullname(test) == "unittest.suite._ErrorHolder":
            # This is a standalone error

            test_name = test.id()
            # patch setUpModule (__main__) -> __main__.setUpModule
            test_name = re.sub(r'^(.*) \((.*)\)$', r'\2.\1', test_name)

            self.messages.testStarted(test_name)
            self.report_fail(test_name, 'Failure', err)
            self.messages.testFinished(test_name)

            return

        self.report_fail(test, 'Error', err)

    def addFailure(self, test, err, *k):
        super(TeamcityTestResult, self).addFailure(test, err)

        self.report_fail(test, 'Failure', err)

    def report_fail(self, test, fail_type, err):
        self.messages.testFailed(self.get_test_id(test), message=fail_type, details=self.convert_error_to_string(err))

    def startTest(self, test):
        test_id = self.get_test_id(test)

        self.test_started_datetime_map[test_id] = datetime.datetime.now()
        self.messages.testStarted(test_id)

    def stopTest(self, test):
        test_id = self.get_test_id(test)

        time_diff = datetime.datetime.now() - self.test_started_datetime_map[test_id]
        self.messages.testFinished(test_id, time_diff)


class TeamcityTestRunner(object):
    def __init__(self, stream=sys.stderr, *args, **kwargs):
        self.stream = stream

    def _makeResult(self):
        return TeamcityTestResult(self.stream)

    def run(self, test):
        result = self._makeResult()
        test(result)
        return result


if __name__ == '__main__':
    from unittest import main

    main(module=None, testRunner=TeamcityTestRunner())
