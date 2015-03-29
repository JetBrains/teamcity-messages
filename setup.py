# coding=utf-8
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        import sys
        errno = pytest.main(["-l", "--junitxml=test-result.xml", "tests/unit-tests", "tests/integration-tests"])
        sys.exit(errno)

setup(
    name="teamcity-messages",
    version="1.13",
    author='JetBrains',
    author_email='teamcity-feedback@jetbrains.com',
    description='Send test results ' +
                'to TeamCity continuous integration server from unittest, nose and py.test (Python 2.6+)',
    long_description="""This packages provides unittest, nose and py.test
plugins for sending test result messages
to TeamCity continuous integration server
http://www.jetbrains.com/teamcity/

**unittest**: see examples/simple.py for example how to
write your own test file which reports messages
under TeamCity and prints usual diagnostics without it.

**nose**, **py.test** : test status reporting enabled automatically under TeamCity build (when teamcity-messages package is installed)

**django**: For Django 1.6+: Use the Teamcity runner instead of the default DiscoverRunner by changing the following setting in your settings.py:
TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"
If you are using another test runner, you should override the `run_suite` method or use the `DiscoverRunner.test_runner` property introduced in Django 1.7.

**flake8**: add `--teamcity` option to flake8 command line to report errors and warning as TeamCity failed tests

ChangeLog: https://github.com/JetBrains/teamcity-python/blob/master/CHANGELOG.txt

Issue Tracker: https://github.com/JetBrains/teamcity-python/issues
""",
    license='Apache 2.0',
    keywords='unittest teamcity test nose py.test pytest jetbrains',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    ],
    url="https://github.com/JetBrains/teamcity-python",
    platforms=["any"],

    packages=["teamcity"],

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
            'P999 = teamcity.flake8_plugin',
        ]
    },
)
