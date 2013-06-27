# coding=utf-8
import sys
import datetime


class TeamcityServiceMessages(object):
    quote = {"'": "|'", "|": "||", "\n": "|n", "\r": "|r", ']': '|]'}

    def __init__(self, output=sys.stdout, now=datetime.datetime.now):
        self.output = output
        self.now = now

    def escapeValue(self, value):
        return "".join([self.quote.get(x, x) for x in value])

    def message(self, messageName, **properties):
        self.output.write("\n##teamcity[%s timestamp='%s'"
                          % (messageName, self.now().isoformat()[:-3]))
        for k in sorted(properties.keys()):
            value = properties[k]
            if value is None:
                continue

            self.output.write(" %s='%s'" % (k, self.escapeValue(value)))
        self.output.write("]\n")

    def testSuiteStarted(self, suiteName):
        self.message('testSuiteStarted', name=suiteName)

    def testSuiteFinished(self, suiteName):
        self.message('testSuiteFinished', name=suiteName)

    def testStarted(self, testName, captureStandardOutput=None):
        self.message('testStarted', name=testName,
                     captureStandardOutput=captureStandardOutput)

    def testFinished(self, testName, testDuration=None):
        if testDuration is not None:
            duration = str(int(testDuration.total_seconds() * 1000))
            self.message('testFinished', name=testName, duration=duration)
        else:
            self.message('testFinished', name=testName)

    def testIgnored(self, testName, message=''):
        self.message('testIgnored', name=testName, message=message)

    def testFailed(self, testName, message='', details=''):
        self.message('testFailed', name=testName,
                     message=message, details=details)

    def testStdOut(self, testName, out):
        self.message('testStdOut', name=testName, out=out)

    def testStdErr(self, testName, out):
        self.message('testStdErr', name=testName, out=out)
