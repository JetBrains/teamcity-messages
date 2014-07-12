# coding=utf-8
import traceback
import sys
import unittest
import datetime

from teamcity.messages import TeamcityServiceMessages


def _is_string(obj):
    if sys.version_info >= (3, 0):
        return isinstance(obj, str)
    else:
        return isinstance(obj, basestring)


# Added *k to some methods to get compatibility with nosetests
# noinspection PyPep8Naming
class TeamcityTestResult(unittest.TestResult):
    def __init__(self, stream=sys.stdout):
        super(TeamcityTestResult, self).__init__()

        self.output = stream
        self.test_started_datetime = datetime.datetime.now()
        self.test_name = None
        self.messages = None
        self.createMessages()

        self.test_succeeded = False
        self.subtest_errors = []
        self.subtest_failures = []

    def createMessages(self):
        self.messages = TeamcityServiceMessages(self.output)

    def formatErr(self, err):
        try:
            exctype, value, tb = err
            return ''.join(traceback.format_exception(exctype, value, tb))
        except Exception:
            tb = traceback.format_exc()
            return "*FAILED TO GET TRACEBACK*: " + tb

    def getTestName(self, test):
        return test.shortDescription() or str(test)

    def addSuccess(self, test, *args):
        super(TeamcityTestResult, self).addSuccess(test)

        self.output.write("ok\n")

    def addError(self, test, err, *k):
        super(TeamcityTestResult, self).addError(test, err)

        err = self.formatErr(err)
        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addError(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Error: %s\n" % err)
            return

        self.test_succeeded = False
        self.messages.testFailed(self.getTestName(test), message='Error', details=err)

    def addFailure(self, test, err, *k):
        # workaround nose bug on python 3
        if _is_string(err[1]):
            err = (err[0], Exception(err[1]), err[2])

        super(TeamcityTestResult, self).addFailure(test, err)

        err = self.formatErr(err)
        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addFailure(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Error: %s\n" % err)
            return

        self.test_succeeded = False
        self.messages.testFailed(self.getTestName(test), message='Failure', details=err)

    def addSkip(self, test, reason):
        super(TeamcityTestResult, self).addSkip(test, reason)
        
        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addSkip(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Reason: %s\n" % reason)
            return

        self.messages.testIgnored(self.getTestName(test), reason)

    def addExpectedFailure(self, test, err):
        super(TeamcityTestResult, self).addExpectedFailure(test, err)

        if self.getTestName(test) != self.test_name:
            err = self.formatErr(err)
            sys.stderr.write("INTERNAL ERROR: addExpectedFailure(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Error: %s\n" % err)
            return

        self.output.write("ok (failure expected)\n")

    def addUnexpectedSuccess(self, test):
        super(TeamcityTestResult, self).addUnexpectedSuccess(test)

        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addUnexpectedSuccess(%s) outside of test\n" % self.getTestName(test))
            return

        self.test_succeeded = False
        self.messages.testFailed(self.getTestName(test), message='Unexpected success')

    def addSubTest(self, test, subtest, err):
        super(TeamcityTestResult, self).addSubTest(test, subtest, err)

        if err is not None:
            if issubclass(err[0], test.failureException):
                self.subtest_failures.append("%s:\n%s" % (self.getTestName(subtest), self.formatErr(err)))
                self.output.write("%s: failure\n" % self.getTestName(subtest))
            else:
                self.subtest_errors.append("%s:\n%s" % (self.getTestName(subtest), self.formatErr(err)))
                self.output.write("%s: error\n" % self.getTestName(subtest))
        else:
            self.output.write("%s: ok\n" % self.getTestName(subtest))

    def startTest(self, test):
        self.test_started_datetime = datetime.datetime.now()
        self.test_name = self.getTestName(test)
        self.test_succeeded = True  # we assume it succeeded, and set it to False when we send a failure message
        self.subtest_errors = []
        self.subtest_failures = []

        self.messages.testStarted(self.test_name)

    def stopTest(self, test):
        # Record the test as a failure after the entire test was run and any subtest has errors
        if self.test_succeeded and (self.subtest_errors or self.subtest_failures):
            self.messages.testFailed(self.getTestName(test), message='Subtest error',
                                     details="\n\n".join(self.subtest_failures) + "\n".join(self.subtest_errors))

        time_diff = datetime.datetime.now() - self.test_started_datetime
        if self.getTestName(test) != self.test_name:
            sys.stderr.write(
                "INTERNAL ERROR: stopTest(%s) after startTest(%s)" % (self.getTestName(test), self.test_name))
        self.messages.testFinished(self.test_name, time_diff)
        self.test_name = None


class TeamcityTestRunner(object):
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def _makeResult(self):
        return TeamcityTestResult(self.stream)

    def run(self, test):
        result = self._makeResult()
        test(result)
        return result
