# coding=utf-8
import sys
import time

from teamcity.output import TeamCityMessagesPrinter

if sys.version_info < (3, ):
    # Python 2
    # flake8: noqa
    text_type = unicode
else:
    # Python 3
    text_type = str

# Capture some time functions to allow monkeypatching them in tests
_time = time.time
_localtime = time.localtime
_strftime = time.strftime

_quote = {"'": "|'", "|": "||", "\n": "|n", "\r": "|r", '[': '|[', ']': '|]'}


def escape_value(value):
    return "".join(_quote.get(x, x) for x in value)


class TeamcityServiceMessages(object):
    def __init__(self, output=None, now=_time, encoding='auto', output_handler=None):
        if output_handler is None:
            output_handler = TeamCityMessagesPrinter(output)
        self.output_handler = output_handler
        self.now = now

        if encoding and encoding != 'auto':
            self.encoding = encoding
        elif getattr(output, 'encoding', None) or encoding == 'auto':
            # Default encoding to 'utf-8' because it sucks if we fail with a
            # `UnicodeEncodeError` simply because LANG didn't get propagated to
            # a subprocess or something and sys.stdout.encoding is None
            self.encoding = getattr(output, 'encoding', None) or 'utf-8'
        else:
            self.encoding = None

    def encode(self, value):
        if self.encoding and isinstance(value, text_type):
            value = value.encode(self.encoding, errors='backslashreplace')
        return value

    def decode(self, value):
        if self.encoding and not isinstance(value, text_type):
            value = value.decode(self.encoding)
        return value

    if sys.version_info < (3, ):
        def escapeValue(self, value):
            return escape_value(self.encode(value))
    else:
        def escapeValue(self, value):
            return escape_value(self.decode(value))

    def message(self, messageName, **properties):
        current_time = self.now()
        (current_time_int, current_time_fraction) = divmod(current_time, 1)
        current_time_struct = _localtime(current_time_int)

        timestamp = _strftime("%Y-%m-%dT%H:%M:%S.", current_time_struct) + "%03d" % (int(current_time_fraction * 1000))
        message = ("##teamcity[%s timestamp='%s'" % (messageName, timestamp))

        for k in sorted(properties.keys()):
            value = properties[k]
            if value is None:
                continue

            message += (" %s='%s'" % (k, self.escapeValue(value)))

        message += ("]\n")

        self.output_handler.send_message(self.encode(message))

    def _single_value_message(self, messageName, value):
        message = ("##teamcity[%s '%s']\n" % (messageName, self.escapeValue(value)))

        self.output_handler.send_message(self.encode(message))

    def blockOpened(self, name, flowId=None):
        self.message('blockOpened', name=name, flowId=flowId)

    def blockClosed(self, name, flowId=None):
        self.message('blockClosed', name=name, flowId=flowId)

    # Special PyCharm-specific extension to track subtests, additional property is ignored by TeamCity
    def subTestBlockOpened(self, name, subTestResult, flowId=None):
        self.message('blockOpened', name=name, subTestResult=subTestResult, flowId=flowId)

    def block(self, name, flowId=None):
        import teamcity.context_managers as cm
        return cm.block(self, name=name, flowId=flowId)

    def compilationStarted(self, compiler):
        self.message('compilationStarted', compiler=compiler)

    def compilationFinished(self, compiler):
        self.message('compilationFinished', compiler=compiler)

    def compilation(self, compiler):
        import teamcity.context_managers as cm
        return cm.compilation(self, compiler=compiler)

    def testSuiteStarted(self, suiteName, flowId=None):
        self.message('testSuiteStarted', name=suiteName, flowId=flowId)

    def testSuiteFinished(self, suiteName, flowId=None):
        self.message('testSuiteFinished', name=suiteName, flowId=flowId)

    def testSuite(self, name):
        import teamcity.context_managers as cm
        return cm.testSuite(self, name=name)

    def testStarted(self, testName, captureStandardOutput=None, flowId=None, metainfo=None):
        """

        :param metainfo: Used to pass any payload from test runner to Intellij. See IDEA-176950
        """
        self.message('testStarted', name=testName, captureStandardOutput=captureStandardOutput, flowId=flowId, metainfo=metainfo)

    def testFinished(self, testName, testDuration=None, flowId=None):
        if testDuration is not None:
            duration_ms = testDuration.days * 86400000 + \
                testDuration.seconds * 1000 + \
                int(testDuration.microseconds / 1000)
            self.message('testFinished', name=testName, duration=str(duration_ms), flowId=flowId)
        else:
            self.message('testFinished', name=testName, flowId=flowId)

    def test(self, testName, captureStandardOutput=None, testDuration=None, flowId=None):
        import teamcity.context_managers as cm
        return cm.test(self, testName=testName, captureStandardOutput=captureStandardOutput, testDuration=testDuration, flowId=flowId)

    # Unsupported in TeamCity, used in IntellIJ-based IDEs to predict number of tests to be run in the test session
    def testCount(self, count, flowId=None):
        self.message('testCount', count=str(count), flowId=flowId)

    def testIgnored(self, testName, message='', flowId=None):
        self.message('testIgnored', name=testName, message=message, flowId=flowId)

    def testStopped(self, testName, message='', flowId=None):
        self.message('testIgnored', name=testName, message=message, flowId=flowId, stopped="true")

    def testFailed(self, testName, message='', details='', flowId=None, comparison_failure=None):
        if not comparison_failure:
            self.message('testFailed', name=testName, message=message, details=details, flowId=flowId)
        else:
            diff_message = u"\n{0} != {1}\n".format(comparison_failure.actual, comparison_failure.expected)
            self.message('testFailed',
                         name=testName,
                         message=text_type(message) + text_type(diff_message),
                         details=details,
                         flowId=flowId,
                         type="comparisonFailure",
                         actual=comparison_failure.actual,
                         expected=comparison_failure.expected)

    def testStdOut(self, testName, out, flowId=None):
        self.message('testStdOut', name=testName, out=out, flowId=flowId)

    def testStdErr(self, testName, out, flowId=None):
        self.message('testStdErr', name=testName, out=out, flowId=flowId)

    def publishArtifacts(self, path, flowId=None):
        self._single_value_message('publishArtifacts', path)

    def progressMessage(self, message):
        self._single_value_message('progressMessage', message)

    def progressStart(self, message):
        self._single_value_message('progressStart', message)

    def progressFinish(self, message):
        self._single_value_message('progressFinish', message)

    def progress(self, message):
        import teamcity.context_managers as cm
        return cm.progress(self, message=message)

    def buildProblem(self, description, identity):
        self.message('buildProblem', description=description, identity=identity)

    def buildStatus(self, status, text):
        self.message('buildStatus', status=status, text=text)

    def setParameter(self, name, value):
        self.message('setParameter', name=name, value=value)

    def buildStatisticLinesCovered(self, linesCovered):
        self.message('buildStatisticValue', key='CodeCoverageAbsLCovered', value=str(linesCovered))

    def buildStatisticTotalLines(self, totalLines):
        self.message('buildStatisticValue', key='CodeCoverageAbsLTotal', value=str(totalLines))

    def buildStatisticLinesUncovered(self, linesUncovered):
        self.message('buildStatisticValue', key='CodeCoverageAbsLUncovered', value=str(linesUncovered))

    def enableServiceMessages(self, flowId=None):
        self.message('enableServiceMessages', flowId=flowId)

    def disableServiceMessages(self, flowId=None):
        self.message('disableServiceMessages', flowId=flowId)

    def serviceMessagesDisabled(self, flowId=None):
        import teamcity.context_managers as cm
        return cm.serviceMessagesDisabled(self, flowId=flowId)

    def serviceMessagesEnabled(self, flowId=None):
        import teamcity.context_managers as cm
        return cm.serviceMessagesEnabled(self, flowId=flowId)

    def importData(self, typeID, pathToXMLFile):
        self.message('importData', type=typeID, path=pathToXMLFile)

    def customMessage(self, text, status, errorDetails='', flowId=None):
        self.message('message', text=text, status=status, errorDetails=errorDetails, flowId=flowId)
