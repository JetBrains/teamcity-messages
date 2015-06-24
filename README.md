Python Unit Test Reporting to TeamCity
======================================

[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/vt08bybn8k60a77s/branch/master?svg=true)](https://ci.appveyor.com/project/shalupov/teamcity-python/branch/master)
[![Travis Build Status](https://travis-ci.org/JetBrains/teamcity-python.svg?branch=master)](https://travis-ci.org/JetBrains/teamcity-python)

This packages provides unittest, nose and py.test addons for sending test result messages to TeamCity continuous integration server http://www.jetbrains.com/teamcity/

Installation
------------
Install using pip:

    pip install teamcity-messages

or from source:

    python setup.py install


Usage
-----
This package uses service messages to report  build status to TeamCity. See http://www.jetbrains.net/confluence/display/TCD8/Build+Script+Interaction+with+TeamCity for more details

### unittest
If you wish to use Python default's unittest framework, you should modify the Test runner, e.g.:

```python
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
```

See `examples/simple.py` for a full example.

If you are used to running unittest from the command line, instead of using `python -m unittest`, you could use `python -m teamcity.unittestpy`. 

### nose
Test status reporting is enabled automatically under TeamCity build.

### py.test
Test status reporting is enabled automatically under TeamCity build.

### Django
For Django 1.6+: Use the Teamcity runner instead of the default DiscoverRunner by changing the following setting in your settings.py:

    TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"

If you are using another test runner, you should override the `run_suite` method or use the `DiscoverRunner.test_runner` property introduced in Django 1.7.

### flake8
Add the `--teamcity` command line option.


Contact information
-------------------

https://github.com/JetBrains/teamcity-messages

TeamCity support: http://www.jetbrains.com/support/teamcity

License
-------

Apache, version 2.0
http://www.apache.org/licenses/LICENSE-2.0
