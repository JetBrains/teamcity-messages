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
        if is_running_under_teamcity():
            cls._set_teamcity_options()
        else:
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
        messages.testSuiteStarted('pep8')
        for line_number, offset, code, text, doc in report._deferred_print:
            test_name = '%(path)s:%(row)d:%(col)d' % {
                'path': report.filename,
                'row': report.line_offset + line_number,
                'col': offset + 1,
            }

            messages.testStarted(test_name)

            messages.testFailed(test_name, '%s: %s' % (code, text))

            if line_number > len(report.lines):
                line = ''
            else:
                line = report.lines[line_number - 1]
            print(line.rstrip())
            print(re.sub(r'\S', ' ', line[:offset]) + '^')

            if doc:
                print('    ' + doc.strip())

            messages.testFinished(test_name)
        return report.file_errors

    def run(self):
        return []
