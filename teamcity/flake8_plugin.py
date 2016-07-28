from flake8.formatting import base

import re

from teamcity.messages import TeamcityServiceMessages
from teamcity import __version__


class TeamcityReport(base.BaseFormatter):
    name = 'teamcity'
    version = __version__
    messages = TeamcityServiceMessages()

    def format(self, error):
        position = '%s:%d:%d' % (
            error.filename, error.line_number, error.column_number)
        error_message = '%s %s' % (error.code, error.text)
        test_name = 'flake8: %s: %s' % (position, error_message)

        line = error.physical_line
        offset = error.column_number
        details = [
            line.rstrip(),
            re.sub(r'\S', ' ', line[:offset]) + '^',
        ]
        details = '\n'.join(details)

        self.messages.testFailed(test_name, error_message, details)
