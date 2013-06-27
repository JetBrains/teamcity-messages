# coding=utf-8
from setuptools import setup

setup(
    name="teamcity-messages",
    version="1.7",
    author='Leonid Shalupov',
    author_email='Leonid.Shalupov@jetbrains.com',
    description='Send test results ' +
                'to TeamCity continuous integration server from unittest, ' +
                'nose and py.test',
    long_description="""This packages provides unittest, nose and py.test
addons for sending test result messages
to TeamCity continuous integration server
http://www.jetbrains.com/teamcity/

**unittest**: see examples/simple.py for example how to
write your own test file which reports messages
under TeamCity and prints usual diagnostics without it.

**nose**: test status reporting enabled automatically under TeamCity build.

**py.test**: run with --teamcity command line option.
""",
    license='Apache 2.0',
    keywords='unittest teamcity test nose py.test pytest jetbrains',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing'
    ],
    url="https://github.com/JetBrains/teamcity-python",
    platforms=["any"],

    packages=["teamcity"],

    entry_points={
        'nose.plugins': [
            'nose-teamcity = teamcity.nose_report:TeamcityReport'
        ],

        'pytest11': [
            'name_of_plugin = teamcity.pytest_plugin',
        ],
    },
)
