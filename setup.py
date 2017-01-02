# coding=utf-8
import os
import re
from setuptools import setup
from setuptools.command.test import test as TestCommand


here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGELOG.txt')).read()
except IOError:
    README = CHANGES = ''

version_re = r"^__version__ = ['\"]([^'\"]+)['\"]$"
version_file = os.path.join(here, 'teamcity', '__init__.py')
version_match = re.search(version_re, open(version_file).read(), re.MULTILINE)
if not version_match:
    raise RuntimeError("Could not find package version in " + version_file)

VERSION = version_match.group(1)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        try:
            self.test_args = []
        except AttributeError:
            # It may fail on some setuptools versions where test_args is a property
            # On that versions "test_args = []" is not required anyway
            pass
        self.test_suite = "fake_suite"

    def run_tests(self):
        import pytest
        import sys

        if not self.pytest_args:
            self.pytest_args = ["-l", "--junitxml=test-result.xml", "tests/unit-tests", "tests/integration-tests"]
            if sys.version_info >= (2, 6):
                self.pytest_args.append("tests/unit-tests-since-2.6")

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="teamcity-messages",
    version=VERSION,
    author='JetBrains',
    author_email='teamcity-feedback@jetbrains.com',
    description='Send test results ' +
                'to TeamCity continuous integration server from unittest, nose, py.test, twisted trial (Python 2.4+)',
    long_description=README + '\n\n' + CHANGES,
    license='Apache 2.0',
    keywords='unittest teamcity test nose py.test pytest jetbrains',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing'
    ],
    url="https://github.com/JetBrains/teamcity-messages",
    platforms=["any"],

    packages=["teamcity", "twisted.plugins"],
    zip_safe=False,
    package_data={
        'twisted': ['plugins/teamcity_plugin.py'],
    },

    tests_require=['pytest', 'virtualenv'],
    cmdclass={'test': PyTest},

    entry_points={
        'nose.plugins.0.10': [
            'teamcity-report = teamcity.nose_report:TeamcityReport'
        ],

        'pytest11': [
            'pytest-teamcity = teamcity.pytest_plugin',
        ],

        'flake8.extension': [
            'teamcity-messages = teamcity.flake8_plugin:TeamcityReport',
        ],
        'flake8.report': [
            'teamcity-messages = teamcity.flake8_plugin:TeamcityReport',
        ]
    },
)

# Make Twisted regenerate the dropin.cache, if possible.  This is necessary
# because in a site-wide install, dropin.cache cannot be rewritten by
# normal users.
#
# See https://stackoverflow.com/questions/7275295/how-do-i-write-a-setup-py-for-a-twistd-twisted-plugin-that-works-with-setuptools
# to discover deepness of this pit.
try:
    from twisted.plugin import IPlugin, getPlugins
    from twisted.python import log

    def my_log_observer(d):
        if d.get("isError", 0):
            import sys

            text = log.textFromEventDict(d)
            sys.stderr.write("\nUnhandled error while refreshing twisted plugins cache: \n")
            sys.stderr.write("    " + text.replace("\n", "\n    "))
    log.startLoggingWithObserver(my_log_observer, setStdout=False)

    list(getPlugins(IPlugin))
except:
    # Do not break module install because of twisted internals
    pass
