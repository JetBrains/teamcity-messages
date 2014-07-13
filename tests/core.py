from datetime import datetime

import os
import unittest
import subprocess
import sys
from teamcity.messages import TeamcityServiceMessages
from tests.util import normalize_output, get_script_path


class IntegrationTest(unittest.TestCase):
    """Test suite using Python unittests for comparing hte output of the different integrating test suites with the
    expected output in the gold files.
    """

    maxDiff = None

    def _run_and_compare(self, command, gold_file):
        gold_file = os.path.join(os.path.dirname(__file__), 'test_output', gold_file)

        # Create an environment that acts as if it is called from TeamCity and add the source root to the
        # path of the process
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(os.path.dirname(__file__))
        env["TEAMCITY_PROJECT_NAME"] = "project_name"

        # Start the process and wait for its output
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        actual_output = "".join([normalize_output(x.decode()) for x in proc.stdout.readlines()])
        proc.wait()

        # Get the expected output
        with open(gold_file, 'r') as f:
            expected_output = f.read().replace("\r", "")

        self.assertEqual(expected_output, actual_output, "actual output does not match gold file, called with: %s"
                                                         % " ".join(command))

    def test_unittest(self):
        self._run_and_compare([sys.executable, get_script_path('test-unittest.py')],
                              'test-unittest.output.gold')

    def test_pytest(self):
        self._run_and_compare(["py.test", "--teamcity", get_script_path('test-pytest.py')],
                              'test-pytest.output.gold')

    def test_nosetest(self):
        self._run_and_compare(["nosetests", "-w", get_script_path('test-nose')],
                              'test-nose.output.gold')


class MessagesTest(unittest.TestCase):
    class StreamStub(object):
        def __init__(self):
            self.observed_output = ''

        def write(self, msg):
            self.observed_output += msg

    def test_no_properties(self):
        stream = MessagesTest.StreamStub()
        messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
        messages.message('dummyMessage')
        self.assertEqual(stream.observed_output, "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00']\n")

    def test_one_property(self):
        stream = MessagesTest.StreamStub()
        messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
        messages.message('dummyMessage', fruit='apple')
        self.assertEqual(stream.observed_output,
                         "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00' fruit='apple']\n")

    def test_three_properties(self):
        stream = MessagesTest.StreamStub()
        messages = TeamcityServiceMessages(output=stream, now=lambda: datetime.min)
        messages.message('dummyMessage', fruit='apple', meat='steak', pie='raspberry')
        self.assertEqual(stream.observed_output,
                         "\n##teamcity[dummyMessage timestamp='0001-01-01T00:00' "
                         "fruit='apple' meat='steak' pie='raspberry']\n")