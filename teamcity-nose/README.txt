TeamCity plugin for nose
------------------------

Just install this python egg to
enable reporting test results to TeamCity server.

Plugin will activate itself only under TeamCity build
(which is detected by presence of environment variable
TEAMCITY_PROJECT_NAME)

Installation
------------

easy_install teamcity-nose

or

python setup.py install
if you have extracted version or subversion checkout

Technical details
-----------------

Actual plugin code placed in teamcity-messages
package which is referenced here.

This packages just installs "entry point" for nose

Contact information
-------------------

Ask your questions on our support forums:
http://www.intellij.net/forums
or mail to teamcity-feedback@jetbrains.com

http://www.jetbrains.com/support/teamcity

License
-------

Apache, version 2.0
http://www.apache.org/licenses/LICENSE-2.0
