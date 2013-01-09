from setuptools import setup
setup(
    name = "teamcity-messages",
    version = "1.6",
    author = 'Leonid Shalupov',
    author_email = 'Leonid.Shalupov@jetbrains.com',
    description = 'A unittest extension to send test result messages '+
        'to TeamCity continuous integration server',
    long_description = """This packages provides unittest and nose
addon for sending test result messages
to TeamCity continuous integration server
http://www.jetbrains.com/teamcity/

unittest: see examples/simple.py for example how to
write your own test file which reports messages
under TeamCity and prints usual diagnostics without it.

nose: test status reporting enabled automatically under TeamCity build
""",
    license = 'Apache 2.0',
    keywords = 'unittest teamcity test',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing'
        ],
    url = "http://pypi.python.org/pypi/teamcity-messages",
    platforms = ["any"],

    packages = ["teamcity"],

    entry_points = {
        'nose.plugins': [
            'nose-teamcity = teamcity.nose_report:TeamcityReport'
        ],

        'pytest11': [
            'name_of_plugin = teamcity.pytest_plugin',
        ],
    },
)
