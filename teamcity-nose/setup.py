from setuptools import setup
setup(
    name = "teamcity-nose",
    version = "1.2",
    author = 'Leonid Shalupov',
    author_email = 'Leonid.Shalupov@jetbrains.com',
    description = 'A nose plugin to send test result messages '+
        'to TeamCity continuous integration server',
    long_description = """Just install this python egg to
enable reporting test results to TeamCity server.

Plugin will activate itself only under TeamCity build
(which is detected by presence of environment variable
TEAMCITY_PROJECT_NAME)
""",
    license = 'Apache 2.0',
    keywords = 'unittest nose teamcity test',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
        ],
    url = "http://pypi.python.org/pypi/teamcity-nose",
    platforms = ["any"],

    install_requires = [
        "nose >=0.10",
        "teamcity-messages >=1.4"
    ],

    entry_points = {
        'nose.plugins': [
            'nose-teamcity = teamcity.nose_report:TeamcityReport'
        ]
    },
)
