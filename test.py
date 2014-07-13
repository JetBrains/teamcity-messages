"""Additional test module that wraps each of the integration tests in their own virtualenv, installs the required
package and then destroys the virtualenv.

It is recommended to run setup.py test instead, but this requires the plugin to be wrapped in a virtualenv itself.
"""

import importlib
import os
import shutil
import sys
import tempfile
import subprocess
import unittest
from tests.core import MessagesTest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from tests.util import find_script, teamcity_message, escape_for_tc_message_value


def wrap_test_in_venv(test_name, package=None):
    """Create a new virtualenv to run the test case in."""

    import virtualenv
    venv_dir = tempfile.mkdtemp()
    virtualenv.create_environment(venv_dir)

    cmd = [find_script(venv_dir, "python"), sys.argv[0], test_name]
    if package:
        cmd.append(package)

    try:
        teamcity_message("##teamcity[testStarted name='%s']" % test_name)
        subprocess.call(cmd)
    finally:
        shutil.rmtree(venv_dir)
        teamcity_message("##teamcity[testFinished name='%s']" % test_name)


def prepare_test(test_name, package=None):
    """Prepare the test by installing the specified package (if any). This is called from a new process!"""

    if package:
        import pip
        sys.stdout = StringIO()
        pip.main(['install', package])
        sys.stdout = sys.__stdout__

    run_test(test_name)


def run_test(test_name):
    """Actually run the test."""

    testsuite = unittest.TestSuite()

    # Import the specific test
    module_name, testcase_name, method_name = test_name.rsplit('.', 2)
    module = importlib.import_module(module_name)
    testcase = getattr(module, testcase_name)

    # Run the specific test
    testsuite.addTest(testcase(method_name))

    # Report the results, if it is a
    if os.environ.get('TEAMCITY_VERSION') is not None:
        result = unittest.TestResult()
        testsuite.run(result)

        for failure in result.failures:
            teamcity_message("##teamcity[testFailed name='%s' message='%s' details='%s']" %
                             (test_name, 'Error', escape_for_tc_message_value(failure[1])))
        for error in result.errors:
            teamcity_message("##teamcity[testFailed name='%s' message='%s' details='%s']" %
                             (test_name, 'Error', escape_for_tc_message_value(error[1])))
    else:
        unittest.TextTestRunner(verbosity=2).run(testsuite)


def run_remaining_tests():
    """Run the remaining tests"""

    testsuite = unittest.TestLoader().loadTestsFromTestCase(MessagesTest)

    # Report the results, if it is a
    if os.environ.get('TEAMCITY_VERSION') is not None:
        result = unittest.TestResult()

        teamcity_message("##teamcity[testStarted name='remaining']")
        testsuite.run(result)

        for failure in result.failures:
            teamcity_message("##teamcity[testFailed name='%s' message='%s' details='%s']" %
                             ("remaining", 'Error', escape_for_tc_message_value(failure[1])))
        for error in result.errors:
            teamcity_message("##teamcity[testFailed name='%s' message='%s' details='%s']" %
                             ("remaining", 'Error', escape_for_tc_message_value(error[1])))

        teamcity_message("##teamcity[testFinished name='remaining']")
    else:
        unittest.TextTestRunner(verbosity=2).run(testsuite)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        wrap_test_in_venv('tests.core.IntegrationTest.test_unittest')
        wrap_test_in_venv('tests.core.IntegrationTest.test_pytest', 'pytest==2.3.4')
        wrap_test_in_venv('tests.core.IntegrationTest.test_nosetest', 'nose==1.2.1')
        run_remaining_tests()
    elif len(sys.argv) == 2:
        prepare_test(sys.argv[1])
    elif len(sys.argv) == 3:
        prepare_test(sys.argv[1], sys.argv[2])