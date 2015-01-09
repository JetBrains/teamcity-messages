# coding=utf-8
import os

from teamcity import is_running_under_teamcity
from teamcity.unittestpy import TeamcityTestResult
from teamcity.common import is_string, split_output, limit_output


# from nose.util.ln
def _ln(label):
    label_len = len(label) + 2
    chunk = (70 - label_len) // 2
    out = '%s %s %s' % ('-' * chunk, label, '-' * chunk)
    pad = 70 - len(out)
    if pad > 0:
        out = out + ('-' * pad)
    return out


_captured_output_start_marker = _ln(u'>> begin captured stdout <<') + "\n"
_captured_output_end_marker = "\n" + _ln(u'>> end captured stdout <<')


class TeamcityReport(TeamcityTestResult):
    name = 'teamcity-report'
    score = 10000

    def __init__(self):
        super(TeamcityReport, self).__init__()

        self.enabled = False

    def configure(self, options, conf):
        self.enabled = is_running_under_teamcity()

    def options(self, parser, env=os.environ):
        pass

    def convert_error_to_string(self, err):
        # workaround nose bug on python 3
        if is_string(err[1]):
            err = (err[0], Exception(err[1]), err[2])

        return super(TeamcityReport, self).convert_error_to_string(err)

    def report_fail(self, test, fail_type, err):
        test_id = self.get_test_id(test)

        details = self.convert_error_to_string(err)

        start_index = details.find(_captured_output_start_marker)
        end_index = details.find(_captured_output_end_marker)

        if start_index >= 0 and end_index >= 0:
            captured_output = details[start_index + len(_captured_output_start_marker):end_index]
            details = details[:start_index] + details[end_index + len(_captured_output_end_marker):]

            for chunk in split_output(limit_output(captured_output)):
                self.messages.testStdOut(test_id, chunk, flowId=test_id)

        self.messages.testFailed(test_id, message=fail_type, details=details, flowId=test_id)

    def is_doctest_class_name(self, fqn):
        return super(TeamcityReport, self).is_doctest_class_name(fqn) or fqn == "nose.plugins.doctests.DocTestCase"

    def addDeprecated(self, test):
        test_id = self.get_test_id(test)
        self.messages.testIgnored(test_id, message="Deprecated", flowId=test_id)

    def _lastPart(self, name):
        nameParts = name.split('.')
        return nameParts[-1]

    def setOutputStream(self, stream):
        self.output = stream
        self.create_messages()

        class dummy:
            def write(self, *arg):
                pass

            def writeln(self, *arg):
                pass

            def flush(self):
                pass

        d = dummy()
        return d
