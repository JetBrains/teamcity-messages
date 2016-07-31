import re
from io import BytesIO

from flake8.formatting import base

from teamcity.messages import TeamcityServiceMessages
from teamcity import __version__


class TeamcityReport(base.BaseFormatter):
    name = 'teamcity-messages'
    version = __version__

    options_added = False

    @classmethod
    def add_options(cls, parser):
        if not cls.options_added:
            parser.add_option('--teamcity', default=False,
                              action='callback', callback=cls.set_option_callback,
                              help="Enable teamcity messages (does nothing "
                                   "in flake8 v3; here for backwards "
                                   "compatibility only with flake8 v2)")
            cls.options_added = True

    @classmethod
    def set_option_callback(cls, option, opt, value, parser):
        global enable_teamcity
        enable_teamcity = True

    def format(self, error):
        position = '%s:%d:%d' % (
            error.filename, error.line_number, error.column_number)
        error_message = '%s %s' % (error.code, error.text)
        test_name = 'pep8: %s: %s' % (position, error_message)

        line = error.physical_line
        offset = error.column_number
        details = [
            line.rstrip(),
            re.sub(r'\S', ' ', line[:offset]) + '^',
        ]
        details = '\n'.join(details)

        bytesio = BytesIO()
        messages = TeamcityServiceMessages(output=bytesio)

        messages.testStarted(test_name)
        messages.testFailed(test_name, error_message, details)
        messages.testFinished(test_name)

        return bytesio.getvalue().decode('UTF-8')
