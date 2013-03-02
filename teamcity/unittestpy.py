# coding=utf-8
import traceback
import sys
from unittest import TestResult
import datetime

from teamcity.messages import TeamcityServiceMessages


# Added *k to some methods to get compatibility with nosetests
class TeamcityTestResult(TestResult):
    def __init__(self, stream=sys.stdout):
        TestResult.__init__(self)

        self.output = stream
        self.test_started_datetime = None

        self.createMessages()

    def createMessages(self):
        self.messages = TeamcityServiceMessages(self.output)

    def formatErr(self, err):
        exctype, value, tb = err
        return ''.join(traceback.format_exception(exctype, value, tb))

    def getTestName(self, test):
        return test.shortDescription() or str(test)

    def addSuccess(self, test, *k):
        TestResult.addSuccess(self, test)

        self.output.write("ok\n")

    def addError(self, test, err, *k):
        TestResult.addError(self, test, err)

        err = self.formatErr(err)

        self.messages.testFailed(self.getTestName(test),
                                 message='Error', details=err)

    def addFailure(self, test, err, *k):
        TestResult.addFailure(self, test, err)

        err = self.formatErr(err)

        self.messages.testFailed(self.getTestName(test),
                                 message='Failure', details=err)

    def startTest(self, test):
        self.test_started_datetime = datetime.datetime.now()
        self.messages.testStarted(self.getTestName(test))

    def stopTest(self, test):
        time_diff = datetime.datetime.now() - self.test_started_datetime
        self.messages.testFinished(self.getTestName(test), time_diff)


class TeamcityTestRunner(object):
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def _makeResult(self):
        return TeamcityTestResult(self.stream)

    def run(self, test):
        result = self._makeResult()
        test(result)
        return result
