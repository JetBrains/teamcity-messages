Python Unit Test Reporting to TeamCity
======================================

[![AppVeyor Build status](https://ci.appveyor.com/api/projects/status/vt08bybn8k60a77s/branch/master?svg=true)](https://ci.appveyor.com/project/shalupov/teamcity-python/branch/master)
[![Travis Build Status](https://travis-ci.org/JetBrains/teamcity-messages.svg?branch=master)](https://travis-ci.org/JetBrains/teamcity-messages)

This packages integrates Python with the [TeamCity](http://www.jetbrains.com/teamcity/) Continuous Integration (CI) server. It allow sending ["service messages"](https://confluence.jetbrains.com/display/TCD9/Build+Script+Interaction+with+TeamCity) from Python code. Additionally, it provides integration with the following testing frameworks and tools:

- [py.test](http://pytest.org/)
- [nose](https://nose.readthedocs.org/)
- [Django](https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#other-testing-frameworks)
- [unittest (Python standard library)](https://docs.python.org/2/library/unittest.html)
- [Trial (Twisted)](http://twistedmatrix.com/trac/wiki/TwistedTrial)
- [Flake8](https://flake8.readthedocs.org/)

Installation
------------
Install using pip:

    pip install teamcity-messages

or from source:

    python setup.py install


Usage
-----
This package uses service messages to report  build status to TeamCity. See https://confluence.jetbrains.com/display/TCD9/Build+Script+Interaction+with+TeamCity for more details

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
For Django 1.6+: Use the `TeamcityDjangoRunner` runner instead of the default `DiscoverRunner` by changing the following setting in your settings.py:

```python
TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"
```

If you are using another test runner, you should override the `run_suite` method or use the `DiscoverRunner.test_runner` property introduced in Django 1.7.

### flake8
Add the `--teamcity` command line option.

### Twisted trial
Add `--reporter=teamcity` option to trial command line


Contact information
-------------------

https://github.com/JetBrains/teamcity-messages

TeamCity support: http://www.jetbrains.com/support/teamcity

License
-------

Apache, version 2.0
http://www.apache.org/licenses/LICENSE-2.0
