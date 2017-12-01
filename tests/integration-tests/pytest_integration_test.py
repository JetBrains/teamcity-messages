# coding=utf-8
import os
import platform
import sys

import pytest

import virtual_environments
from diff_test_tools import expected_messages, SCRIPT
from service_messages import ServiceMessage, assert_service_messages, has_service_messages
from test_util import run_command


def construct_fixture():
    # pytest 3.2.5 is the last version to support 2.6 or 3.3
    # https://docs.pytest.org/en/latest/changelog.html
    if ((2, 6) <= sys.version_info < (2, 7)) or ((3, 3) <= sys.version_info < (3, 4)):
        params = [("py==1.4.34", "pytest==3.2.5")]
    else:
        # latest version
        params = [("pytest",)]

    @pytest.fixture(scope='module', params=params)
    def venv(request):
        return virtual_environments.prepare_virtualenv(request.param)

    return venv


globals()['venv'] = construct_fixture()


def fix_slashes(s):
    if platform.system() == 'Windows':
        return s.replace('/', '\\')
    else:
        return s.replace('\\', '/')


# disable pytest-pep8 on 3.4 due to "No such file or directory: 'doc'" issue
# see https://bugs.funtoo.org/browse/FL-3596
if (sys.version_info[0] == 2 and sys.version_info >= (2, 7)) or (sys.version_info[0] == 3 and sys.version_info >= (3, 5)):
    def test_pytest_pep8(venv):
        venv_with_pep8 = virtual_environments.prepare_virtualenv(venv.packages + ("pytest-pep8",))

        output = run(venv_with_pep8, 'pep8_test.py', options="--pep8")
        pep8_test_name = "tests.guinea-pigs.pytest.pep8_test.PEP8"
        test_name = "tests.guinea-pigs.pytest.pep8_test.test_ok"
        ms = assert_service_messages(
            output,
            [
                ServiceMessage('testCount', {'count': "2"}),
                ServiceMessage('testStarted', {'name': pep8_test_name}),
                ServiceMessage('testFailed', {'name': pep8_test_name}),
                ServiceMessage('testFinished', {'name': pep8_test_name}),
                ServiceMessage('testStarted', {'name': test_name}),
                ServiceMessage('testFinished', {'name': test_name}),
            ])

        assert ms[2].params["details"].find("E302 expected 2 blank lines, found 1") > 0

    def test_pytest_pylint(venv):
        venv_with_pylint = virtual_environments.prepare_virtualenv(venv.packages + ("pytest-pylint",))

        output = run(venv_with_pylint, 'pylint_test.py', options="--pylint")
        pylint_test_name = "tests.guinea-pigs.pytest.pylint_test.Pylint"
        test_name = "tests.guinea-pigs.pytest.pylint_test.test_ok"
        ms = assert_service_messages(
            output,
            [
                ServiceMessage('testCount', {'count': "2"}),
                ServiceMessage('testStarted', {'name': pylint_test_name}),
                ServiceMessage('testFailed', {'name': pylint_test_name}),
                ServiceMessage('testFinished', {'name': pylint_test_name}),
                ServiceMessage('testStarted', {'name': test_name}),
                ServiceMessage('testFinished', {'name': test_name}),
            ])

        assert ms[2].params["details"].find("Unused import sys") > 0


def test_hierarchy(venv):
    output = run(venv, 'namespace')
    test_name = 'tests.guinea-pigs.pytest.namespace.pig_test.TestSmoke.test_smoke'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


def test_force_tc_reporting(venv):
    output = run(venv, 'namespace', options="--teamcity", set_tc_version=False)
    assert has_service_messages(output)


def test_tc_reporting(venv):
    output = run(venv, 'namespace')
    assert has_service_messages(output)


def test_no_reporting_when_no_teamcity(venv):
    output = run(venv, 'namespace', set_tc_version=False)
    assert not has_service_messages(output)


def test_reporting_disabled(venv):
    output = run(venv, 'namespace', set_tc_version=True, options="--no-teamcity")
    assert not has_service_messages(output)


def test_custom_test_items(venv):
    output = run(venv, 'custom')
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line1'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line1'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line2'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.custom.test_simple_yml.line2'}),
        ])


if sys.version_info >= (2, 6):
    @pytest.mark.parametrize("coverage_version, pytest_cov_version", [
        ("==3.7.1", "==1.8.1"),
        ("==4.0.1", "==2.2.0"),
        # latest
        ("", ""),
    ])
    def test_coverage(venv, coverage_version, pytest_cov_version):
        if coverage_version != "==3.7.1" and (3, 1) < sys.version_info < (3, 3):
            pytest.skip("coverage >= 4.0 dropped support for Python 3.2")

        venv_with_coverage = virtual_environments.prepare_virtualenv(
            venv.packages + (
                "coverage" + coverage_version,
                "pytest-cov" + pytest_cov_version))

        output = run(venv_with_coverage, 'coverage_test', options="--cov coverage_test")
        test_name = "tests.guinea-pigs.pytest.coverage_test.coverage_test.test_covered_func"
        assert_service_messages(
            output,
            [
                ServiceMessage('testCount', {'count': "1"}),
                ServiceMessage('testStarted', {'name': test_name}),
                ServiceMessage('testFinished', {'name': test_name}),
                ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLCovered', 'value': '9'}),
                ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLTotal', 'value': '13'}),
                ServiceMessage('buildStatisticValue', {'key': 'CodeCoverageAbsLUncovered', 'value': '4'}),
            ])


def test_runtime_error(venv):
    output = run(venv, 'runtime_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testFailed', {'flowId': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_exception'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.runtime_error_test.test_error'}),
        ])
    assert ms[2].params["details"].find("raise Exception") > 0
    assert ms[2].params["details"].find("oops") > 0
    assert ms[5].params["details"].find("assert 0 != 0") > 0


def test_unittest_error(venv):
    output = run(venv, 'unittest_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
        ])
    assert ms[2].params["details"].find("raise Exception") > 0
    assert ms[2].params["details"].find("oops") > 0
    assert ms[5].params["details"].find("AssertionError") > 0


def test_fixture_error(venv):
    output = run(venv, 'fixture_error_test.py')

    test1_name = 'tests.guinea-pigs.pytest.fixture_error_test.test_error1'
    test2_name = 'tests.guinea-pigs.pytest.fixture_error_test.test_error2'

    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),

            ServiceMessage('testStarted', {'name': test1_name, 'flowId': test1_name}),
            ServiceMessage('testFailed', {'name': test1_name,
                                          'message': 'test setup failed',
                                          'flowId': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name}),

            ServiceMessage('testStarted', {'name': test2_name, 'flowId': test2_name}),
            ServiceMessage('testFailed', {'name': test2_name,
                                          'message': 'test setup failed',
                                          'flowId': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
        ])
    assert ms[2].params["details"].find("raise Exception") > 0
    assert ms[2].params["details"].find("oops") > 0
    assert ms[5].params["details"].find("raise Exception") > 0
    assert ms[5].params["details"].find("oops") > 0


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_output(venv):
    output = run(venv, 'output_test.py')

    test_name = 'tests.guinea-pigs.pytest.output_test.test_out'

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),

            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name, 'captureStandardOutput': 'false'}),
            ServiceMessage('blockOpened', {'name': 'test setup', 'flowId': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'flowId': test_name, 'out': 'setup stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name, 'out': 'setup stderr|n'}),
            ServiceMessage('blockClosed', {'name': 'test setup'}),
            ServiceMessage('testStdOut', {'name': test_name, 'flowId': test_name, 'out': 'test stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name, 'out': 'test stderr|n'}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('blockOpened', {'name': 'test teardown', 'flowId': test_name}),
            ServiceMessage('testStdOut', {'name': test_name, 'flowId': test_name, 'out': 'teardown stdout|n'}),
            ServiceMessage('testStdErr', {'name': test_name, 'flowId': test_name, 'out': 'teardown stderr|n'}),
            ServiceMessage('blockClosed', {'name': 'test teardown'}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_chunked_output(venv):
    output = run(venv, 'chunked_output_test.py')

    full_line = 'x' * 50000
    leftovers = 'x' * (1024 * 1024 - 50000 * 20)

    assert_service_messages(
        output,
        [ServiceMessage('testCount', {'count': "1"})] +
        [ServiceMessage('testStarted', {})] +
        [ServiceMessage('testStdOut', {'out': full_line})] * 20 +
        [ServiceMessage('testStdOut', {'out': leftovers})] +
        [ServiceMessage('testStdErr', {'out': full_line})] * 20 +
        [ServiceMessage('testStdErr', {'out': leftovers})] +
        [ServiceMessage('testFinished', {})]
    )


def test_output_no_capture(venv):
    output = run(venv, 'output_test.py', options="-s")

    test_name = 'tests.guinea-pigs.pytest.output_test.test_out'

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name, 'captureStandardOutput': 'true'}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])
    assert "setup stderr" in output
    assert "setup stdout" in output
    assert "test stderr" in output
    assert "test stdout" in output
    assert "teardown stderr" in output
    assert "teardown stdout" in output


def test_teardown_error(venv):
    output = run(venv, 'teardown_error_test.py')
    teardown_test_id = 'tests.guinea-pigs.pytest.teardown_error_test.test_error_teardown'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.teardown_error_test.test_error'}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.teardown_error_test.test_error'}),
            ServiceMessage('testStarted', {'name': teardown_test_id, 'flowId': teardown_test_id}),
            ServiceMessage('testFailed', {'flowId': teardown_test_id,
                                          'message': fix_slashes('tests/guinea-pigs/pytest/teardown_error_test.py') + ':13 (test_error)'}),
            ServiceMessage('testFinished', {'name': teardown_test_id, 'flowId': teardown_test_id}),
        ])
    assert ms[4].params["details"].find("raise Exception") > 0
    assert ms[4].params["details"].find("teardown oops") > 0


def test_module_error(venv):
    output = run(venv, 'module_error_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.module_error_test.top_level_collect'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.module_error_test.top_level_collect'}),
            ServiceMessage('testCount', {'count': "0"}),
        ])
    assert ms[1].params["details"].find("raise Exception") > 0
    assert ms[1].params["details"].find("module oops") > 0


def test_skip(venv):
    output = run(venv, 'skip_test.py')
    test_name = 'tests.guinea-pigs.pytest.skip_test.test_function'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testIgnored', {'message': u'Skipped: skip reason причина', 'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


def test_monkey_patch_strftime(venv):
    output = run(venv, 'monkey_patch_strftime_test.py')
    test_name = 'tests.guinea-pigs.pytest.monkey_patch_strftime_test.test_monkeypatch'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])
    assert output.find("spam") == -1


def test_collect_exception(venv):
    output = run(venv, 'collect_exception_test.py')
    test_name = 'tests.guinea-pigs.pytest.collect_exception_test.top_level_collect'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': 'Some output|n', 'flowId': test_name}),
            ServiceMessage('testFailed', {'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testCount', {'count': "0"}),
        ])
    assert ms[2].params["details"].find("runtime error") > 0


@pytest.mark.skipif("sys.version_info < (2, 7)", reason="requires Python 2.7+")
def test_collect_skip(venv):
    output = run(venv, 'collect_skip_test.py')
    test_name = 'tests.guinea-pigs.pytest.collect_skip_test.top_level_collect'
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testStdOut', {'out': 'Some output|n', 'flowId': test_name}),
            ServiceMessage('testIgnored', {'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testCount', {'count': "0"}),
        ])
    assert ms[2].params["message"].find("skip reason") > 0


def test_params(venv):
    output = run(venv, 'params_test.py')

    test1_name = 'tests.guinea-pigs.pytest.params_test.test_eval(3+5-8)'
    test2_name = "tests.guinea-pigs.pytest.params_test.test_eval(|'1_5|' + |'2|'-1_52)"
    test3_name = 'tests.guinea-pigs.pytest.params_test.test_eval(6*9-42)'

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "3"}),
            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
            ServiceMessage('testStarted', {'name': test3_name}),
            ServiceMessage('testFailed', {'name': test3_name,
                                          'message': fix_slashes('tests/guinea-pigs/pytest/params_test.py') + ':3 (test_eval|[6*9-42|])'}),
            ServiceMessage('testFinished', {'name': test3_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 5)", reason="broken on 2.4 somehow")
def test_params_2(venv):
    output = run(venv, 'params_test_2.py')

    test1_name = 'tests.guinea-pigs.pytest.params_test_2.test(None-https://facebook_com/)'
    test2_name = "tests.guinea-pigs.pytest.params_test_2.test(None-https://facebook_com/share_php?http://foo_com/)"

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 6)", reason="requires Python 2.6+")
def test_nose_parameterized(venv):
    venv_with_params = virtual_environments.prepare_virtualenv(venv.packages + ("nose-parameterized",))

    output = run(venv_with_params, 'nose_parameterized_test.py')

    test1_name = 'tests.guinea-pigs.pytest.nose_parameterized_test.test(0)'
    test2_name = "tests.guinea-pigs.pytest.nose_parameterized_test.test(1)"

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': test1_name}),
            ServiceMessage('testFinished', {'name': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_long_diff(venv):
    output = run(venv, "../diff_assert_error_long.py")
    test_name = 'tests.guinea-pigs.diff_assert_error_long.test_test'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            # "..." inserted by pytest that cuts long lines
            ServiceMessage('testFailed', {'name': test_name, "expected": "foofoofoofoo...ofoofoofoofoo", "actual": "spamspamspams...mspamspamspam"}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_num_diff(venv):
    output = run(venv, "../diff_assert_error_nums.py")
    test_name = 'tests.guinea-pigs.diff_assert_error_nums.FooTest.test_test'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, "expected": "123", "actual": "456"}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff(venv):
    output = run(venv, SCRIPT)
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
        ] + expected_messages("tests.guinea-pigs.diff_assert.FooTest.test_test"))


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff_assert_error(venv):
    output = run(venv, "../diff_assert_error.py")
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test"}),
            ServiceMessage('testFailed', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test", "expected": "spam", "actual": "eggs"}),
            ServiceMessage('testFinished', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test"}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff_top_level_assert_error(venv):
    output = run(venv, "../diff_toplevel_assert_error.py")
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': "tests.guinea-pigs.diff_toplevel_assert_error.test_test"}),
            ServiceMessage('testFailed', {'name': "tests.guinea-pigs.diff_toplevel_assert_error.test_test", "expected": "spam", "actual": "eggs"}),
            ServiceMessage('testFinished', {'name': "tests.guinea-pigs.diff_toplevel_assert_error.test_test"}),
        ])


def test_xfail(venv):
    output = run(venv, 'xfail_test.py')
    ms = assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_unexpectedly_passing'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_unexpectedly_passing'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_expected_to_fail'}),
            ServiceMessage('testIgnored', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.xfail_test.test_expected_to_fail'}),
        ])
    assert ms[5].params["message"].find("xfail reason") > 0


def run(venv, file_name, test=None, options='', set_tc_version=True):
    env = virtual_environments.get_clean_system_environment()
    if test is not None:
        test_suffix = "::" + test
    else:
        test_suffix = ""

    command = os.path.join(venv.bin, 'py.test') + " " + options + " " + \
        os.path.join('tests', 'guinea-pigs', 'pytest', file_name) + test_suffix
    return run_command(command, env, True, set_tc_version)
