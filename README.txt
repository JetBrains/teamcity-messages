TeamCity plugin for unittest
----------------------------

This packages provides unittest, nose and py.test
addons for sending test result messages
to TeamCity continuous integration server
http://www.jetbrains.com/teamcity/

Installation
------------

easy_install teamcity-messages

or

python setup.py install
if you have extracted version or githib checkout

Usage
-----

unittest: see examples/simple.py for example how to
write your own test file which reports messages
under TeamCity and prints usual diagnostics without it.

nose: test status reporting enabled automatically under TeamCity build.

py.test: run with --teamcity command line option.

See
http://www.jetbrains.net/confluence/display/TCD3/Build+Script+Interaction+with+TeamCity
for more details

Contact information
-------------------

https://github.com/JetBrains/teamcity-python

TeamCity support: http://www.jetbrains.com/support/teamcity

License
-------

Apache, version 2.0
http://www.apache.org/licenses/LICENSE-2.0
