# coding=utf-8
import traceback
import sys
from unittest import TestResult
import datetime

from teamcity.messages import TeamcityServiceMessages


def _is_string(obj):
    if sys.version_info >= (3, 0):
        return isinstance(obj, str)
    else:
        return isinstance(obj, basestring)


# Added *k to some methods to get compatibility with nosetests
class TeamcityTestResult(TestResult):
    def __init__(self, stream=sys.stdout):
        TestResult.__init__(self)

        self.output = stream
        self.test_started_datetime = None
        self.test_name = None

        self.createMessages()

    def createMessages(self):
        self.messages = TeamcityServiceMessages(self.output)

    def formatErr(self, err):
        try:
            exctype, value, tb = err
            return ''.join(traceback.format_exception(exctype, value, tb))
        except:
            tb = traceback.format_exc()
            return "*FAILED TO GET TRACEBACK*: " + tb

    def getTestName(self, test):
        return test.shortDescription() or str(test)

    def addSuccess(self, test, *k):
        TestResult.addSuccess(self, test)

        self.output.write("ok\n")

    def addError(self, test, err, *k):
        TestResult.addError(self, test, err)

        err = self.formatErr(err)
        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addError(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Error: %s\n" % err)
            return

        self.messages.testFailed(self.getTestName(test),
                                 message='Error', details=err)

    def addFailure(self, test, err, *k):
        # workaround nose bug on python 3
        if _is_string(err[1]):
            err = (err[0], Exception(err[1]), err[2])

        TestResult.addFailure(self, test, err)

        err = self.formatErr(err)
        if self.getTestName(test) != self.test_name:
            sys.stderr.write("INTERNAL ERROR: addFailure(%s) outside of test\n" % self.getTestName(test))
            sys.stderr.write("Error: %s\n" % err)
            return

        self.messages.testFailed(self.getTestName(test),
                                 message='Failure', details=err)

    def startTest(self, test):
        self.test_started_datetime = datetime.datetime.now()
        self.test_name = self.getTestName(test)
        self.messages.testStarted(self.test_name)

    def stopTest(self, test):
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
