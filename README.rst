Python Unit Test Reporting to TeamCity
======================================

|  |jb_project| |license| |pypi_version|
|  |versions| |appveyor_ci| |travis_ci|

This package integrates Python with the
`TeamCity <http://www.jetbrains.com/teamcity/>`__ Continuous Integration
(CI) server. It allows sending `"service
messages" <https://confluence.jetbrains.com/display/TCDL/Build+Script+Interaction+with+TeamCity>`__
from Python code. Additionally, it provides integration with the
following testing frameworks and tools:

-  `py.test <http://pytest.org/>`__
-  `nose <https://nose.readthedocs.org/>`__
-  `Django <https://docs.djangoproject.com/en/1.8/topics/testing/advanced/#other-testing-frameworks>`__
-  `unittest (Python standard
   library) <https://docs.python.org/2/library/unittest.html>`__
-  `Trial (Twisted) <http://twistedmatrix.com/trac/wiki/TwistedTrial>`__
-  `Flake8 <https://flake8.readthedocs.org/>`__
-  `Behave <https://behave.readthedocs.io/>`__
-  `PyLint <https://www.pylint.org/>`__

Installation
------------

Install using pip:

::

    pip install teamcity-messages

or from source:

::

    python setup.py install

Usage
-----

This package uses service messages to report the build status to TeamCity.
See https://confluence.jetbrains.com/display/TCDL/Build+Script+Interaction+with+TeamCity
for more details

unittest
~~~~~~~~

If you wish to use the Python default unittest framework, you should
modify the Test runner, e.g.:

.. code:: python

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

See ``examples/simple.py`` for a full example.

If you are used to running unittest from the command line, instead of
using ``python -m unittest``, you could use
``python -m teamcity.unittestpy``.

nose
~~~~

Test status reporting is enabled automatically under TeamCity build.

py.test
~~~~~~~

Test status reporting is enabled automatically under TeamCity build.

Django
~~~~~~

For Django 1.6+: Use the ``TeamcityDjangoRunner`` runner instead of the
default ``DiscoverRunner`` by changing the following setting in your
settings.py:

.. code:: python

    TEST_RUNNER = "teamcity.django.TeamcityDjangoRunner"

If you are using another test runner, you should override the
``run_suite`` method or use the ``DiscoverRunner.test_runner`` property
introduced in Django 1.7.

flake8
~~~~~~

Test status reporting is enabled automatically under TeamCity build.

PyLint
~~~~~~

Add ``--output-format=teamcity.pylint_reporter.TeamCityReporter`` to
the ``pylint`` command line.

tox
~~~

Pass TEAMCITY_VERSION environment variable inside your test virtenv.
TEAMCITY_VERSION environment variable exists during build on TeamCity.
teamcity-messages uses it in order to enable reporting to TeamCity.

::

    [testenv]
    passenv = TEAMCITY_VERSION

Twisted trial
~~~~~~~~~~~~~

Add ``--reporter=teamcity`` option to trial command line

Behave
~~~~~~

For Behave 1.2.6:

.. code:: python

    from behave.formatter import _registry
    from behave.configuration import Configuration
    from behave.runner import Runner
    from teamcity.jb_behave_formatter import TeamcityFormatter

    _registry.register_as("TeamcityFormatter", TeamcityFormatter)
    configuration = Configuration()
    configuration.format = ["TeamcityFormatter"]
    configuration.stdout_capture = False
    configuration.stderr_capture = False
    Runner(configuration).run()


Python version compatibility
----------------------------

See https://pypi.org/project/teamcity-messages for Python version compatibility

Contact information
-------------------

https://github.com/JetBrains/teamcity-messages

TeamCity support: http://www.jetbrains.com/support/teamcity

License
-------

Apache, version 2.0 http://www.apache.org/licenses/LICENSE-2.0

.. |jb_project| image:: http://jb.gg/badges/official.svg
   :target: https://confluence.jetbrains.com/display/ALL/JetBrains+on+GitHub
   :alt: Official JetBrains project
.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: Apache 2.0 license
.. |versions| image:: https://img.shields.io/pypi/pyversions/teamcity-messages.svg
   :target: https://pypi.python.org/pypi/teamcity-messages
   :alt: Python versions supported
.. |appveyor_ci| image:: https://ci.appveyor.com/api/projects/status/vt08bybn8k60a77s/branch/master?svg=true
   :target: https://ci.appveyor.com/project/shalupov/teamcity-python/branch/master
   :alt: AppVeyor Build Status
.. |travis_ci| image:: https://travis-ci.org/JetBrains/teamcity-messages.svg?branch=master
   :target: https://travis-ci.org/JetBrains/teamcity-messages
   :alt: Travis Build Status
.. |pypi_version| image:: https://badge.fury.io/py/teamcity-messages.svg
   :target: https://pypi.python.org/pypi/teamcity-messages
   :alt: PyPI version
