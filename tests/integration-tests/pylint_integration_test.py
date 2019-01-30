import os
import sys
import pytest
import virtual_environments
from service_messages import ServiceMessage, assert_service_messages
from test_util import run_command


pylint_min = '1.8'
pylint_max = '1.9' if sys.version_info <= (3, ) else '2.1'


@pytest.fixture(scope='module', params=[('pylint==' + pylint_min, ), ('pylint==' + pylint_max, )])
def venv(request):
    """Virtual environment fixture with PyLint of the minimal and maximal supported version
    for a given python version.

    * Python 2.7 is supported up to PyLint 1.9.
    * Python 3.4+ is supported through to the latest (2.1)
    """
    if sys.version_info < (2, 7) or (3, ) <= sys.version_info < (3, 4):
        pytest.skip("PyLint integration requires Python 2.7 or 3.4+")

    return virtual_environments.prepare_virtualenv(request.param)


def test_sample(venv):
    filename = 'tests/guinea-pigs/pylint/sample.py'
    output = run(venv, filename)
    assert_service_messages(
        output,
        [
            ServiceMessage('inspectionType', dict(category='warning', description='Used when a warning note as FIXME or XXX is detected.',
                                                  id='W0511', name='fixme')),
            ServiceMessage('inspection', dict(SEVERITY='WARNING', file='tests/guinea-pigs/pylint/sample.py', line='10',
                                              message='TODO gets also picked up by PyLint (W0511)', typeId='W0511')),

            ServiceMessage('inspectionType', dict(category='refactor', description='Used when a function or method takes too many arguments.',
                                                  name='too-many-arguments', id='R0913')),
            ServiceMessage('inspection', dict(SEVERITY='WEAK WARNING', file='tests/guinea-pigs/pylint/sample.py', line='4',
                                              message='Too many arguments (6/5)')),

            ServiceMessage('inspectionType', dict(category='convention', description='Used when more than on statement are found on the same line.',
                                                  id='C0321', name='multiple-statements')),
            ServiceMessage('inspection', dict(SEVERITY='INFO', file='tests/guinea-pigs/pylint/sample.py', line='6',
                                              message='More than one statement on a single line', typeId='C0321')),

            ServiceMessage('inspectionType', dict(category='error', description='Used when an undefined variable is accessed.',
                                                  id='E0602', name='undefined-variable')),
            ServiceMessage('inspection', dict(SEVERITY='ERROR', file='tests/guinea-pigs/pylint/sample.py', line='7',
                                              message='Undefined variable |\'eight|\'', typeId='E0602')),
            ServiceMessage('inspection', dict(SEVERITY='ERROR', file='tests/guinea-pigs/pylint/sample.py', line='8',
                                              message='Undefined variable |\'nine|\'', typeId='E0602')),


            ServiceMessage('inspectionType', dict(category='warning', description='Used when a variable is defined but not used.',
                                                  name='unused-variable', id='W0612')),
            ServiceMessage('inspection', dict(SEVERITY='WARNING', file='tests/guinea-pigs/pylint/sample.py', line='7',
                                              message='Unused variable |\'seven|\'', typeId='W0612')),

            ServiceMessage('buildStatisticValue', dict(key='PyLintScore', value='-18.0')),
        ]
    )


def run(venv, filename):
    """Execute PyLint with the TeamCityReporter.

    :param VirtualEnvDescription venv: virtual environment to run the test in
    :param filename: filename to inspect
    :rtype: str
    :return: captured STDOUT
    """
    command = ' '.join([os.path.join(venv.bin, 'pylint'), '--output-format', 'teamcity.pylint_reporter.TeamCityReporter', filename])

    return run_command(command)
