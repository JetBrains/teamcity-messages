TeamCity plugin for unittest
============================

This packages provides unittest, nose and py.test addons for sending test result messages
to TeamCity continuous integration server http://www.jetbrains.com/teamcity/

Installation
------------

    pip install teamcity-messages

or

    python setup.py install

if you have extracted version or Github checkout

Usage
-----
**unittest** Use the TeamcityTestRunner as your test runner to report messages to TeamCity.
 f you wish to print usual diagnostics without it, you could use something like:

    import unittest
    from teamcity import is_running_under_teamcity
    from teamcity.unittestpy import TeamcityTestRunner

    class Test(unittest.TestCase):
        ...

    if __name__ == '__main__':
        if is_running_under_teamcity():
            runner = TeamcityTestRunner()
        else:
            runner = unittest.TextTestRunner()
        unittest.main(testRunner=runner)

See examples/simple.py for a full example

**nose** Test status reporting is enabled automatically under TeamCity build.

**py.test** Run with `--teamcity` command line option.

See
http://www.jetbrains.net/confluence/display/TCD3/Build+Script+Interaction+with+TeamCity
for more details

Tests
-----
This package integrates with different test framework and therefore requires some special testing. In the tests folder,
there are two additional folders: `test_output` and `test_scripts`. Each supported test framework has their own test
script (or module) that is executed from here. This test spawns an additional python process for each supported
framework. The output of this command is compared with the 'gold' files in the `test_output` folder.

There are two ways to run tests. The first is to simply run the unittests at tests/core.py. This requires py.test and
nose to be installed. (This is identical to running `python setup.py test`.) It is recommended to create a virtualenv
before running these tests. Note that you can run these tests using your favorite test framework, but for reporting to
TeamCity you probably require this module itself, which is a somewhat circular dependency.

The second method involves running `test.py`. This module requires `virtualenv` to be installed in your current env and
create a new virtualenv for each supported test framework. A new Python process is opened within this env, and this
process will then in turn run a single unit test. Since we use `pip` to install the required packages in the env, you
do not need to install py.test and nose in your main env. Additionally, this module offers some basic reporting
features for TeamCity.

Contact information
-------------------
https://github.com/JetBrains/teamcity-python

TeamCity support: http://www.jetbrains.com/support/teamcity

License
-------
Apache, version 2.0
http://www.apache.org/licenses/LICENSE-2.0
