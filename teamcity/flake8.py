import pep8
import re

from teamcity import is_running_under_teamcity
from teamcity.messages import TeamcityServiceMessages


class Pep8MonkeyPatcher(object):
    name = 'teamcity'
    version = '1.9'

    def __init__(self, tree, filename):
        pass

    @classmethod
    def add_options(cls, parser):
        parser.add_option('--teamcity', default=False,
                          action='callback', callback=Pep8MonkeyPatcher.set_option_callback,
                          help="Enable teamcity messages")

    @staticmethod
    def set_option_callback(option, opt, value, parser):
        Pep8MonkeyPatcher._set_teamcity_options()

    @staticmethod
    def _set_teamcity_options():
        pep8.StandardReport.get_file_results = \
            Pep8MonkeyPatcher.patched_get_file_results

    @staticmethod
    def patched_get_file_results(report):
        report._deferred_print.sort()

        messages = TeamcityServiceMessages()

        suite_name = 'pep8: %s' % report.filename
        messages.testSuiteStarted(suite_name)
        for line_number, offset, code, text, doc in report._deferred_print:
            position = '%(path)s:%(row)d:%(col)d' % {
                'path': report.filename,
                'row': report.line_offset + line_number,
                'col': offset + 1,
            }

            error_message = '%s: %s' % (code, text)
            test_name = '%s: %s' % (code, position)

            messages.testStarted(test_name)

            if line_number > len(report.lines):
                line = ''
            else:
                line = report.lines[line_number - 1]

            details = [
                line.rstrip(),
                re.sub(r'\S', ' ', line[:offset]) + '^',
            ]

            if doc:
                details.append(doc.strip())

            details = '\n'.join(details)

            messages.testFailed(test_name, error_message, details)
            messages.testFinished(test_name)
        messages.testSuiteFinished(suite_name)
        return report.file_errors

    def run(self):
        return []
