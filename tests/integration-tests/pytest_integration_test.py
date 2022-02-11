# coding=utf-8
import contextlib
import os
import platform
import sys

import pytest

import virtual_environments
from diff_test_tools import expected_messages, SCRIPT
from service_messages import ServiceMessage, assert_service_messages, has_service_messages
from test_util import run_command, get_teamcity_messages_root


def construct_fixture():
    params = []
    if sys.version_info > (3, 0):
        params.append(('pytest>=6',))
    else:
        params.append(('pytest>=4,<5',))

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


@contextlib.contextmanager
def make_ini(content):
    path = os.path.join(get_teamcity_messages_root(), 'pytest.ini')
    with open(path, 'w+') as f:
        f.write(content)
    yield
    os.remove(path)


# disable pytest-pep8 on 3.4 due to "No such file or directory: 'doc'" issue
# see https://bugs.funtoo.org/browse/FL-3596
if (sys.version_info[0] == 2 and sys.version_info >= (2, 7)) or (sys.version_info[0] == 3 and sys.version_info >= (3, 5)):
    def test_pytest_pep8(venv):
        if 'pytest>=4,<5' not in venv.packages and 'pytest>=5,<6' not in venv.packages:
            pytest.skip("pytest-pep8 not working for pytest>=6")
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

    def test_pytest_flake8(venv):
        # Use flake8 < 4 as there is an issue in pytest-flake8 package:
        # https://github.com/tholo/pytest-flake8/issues/81
        venv_with_pylint = virtual_environments.prepare_virtualenv(venv.packages + ("pytest-flake8",) + ("flake8==3.9.2",))

        file_names = ['./flake8_test1.py', './flake8_test2.py']
        output = run(venv_with_pylint, file_names, options="--flake8")
        file_paths = [os.path.realpath(os.path.join('tests', 'guinea-pigs', 'pytest', file_name))
                      for file_name in file_names]
        expected = [ServiceMessage('testCount', {'count': "4"})]
        for file_path in file_paths:
            test_base, _ = os.path.splitext(os.path.basename(file_path))
            flake8_test_name = "tests.guinea-pigs.pytest.{}.FLAKE8".format(test_base)
            pytest_name = "tests.guinea-pigs.pytest.{}.test_ok".format(test_base)
            expected.extend([
                ServiceMessage('testStarted', {'name': flake8_test_name}),
                ServiceMessage('testFailed', {'name': flake8_test_name}),
                ServiceMessage('testFinished', {'name': flake8_test_name}),
                ServiceMessage('testStarted', {'name': pytest_name}),
                ServiceMessage('testFinished', {'name': pytest_name}),
            ])
        for file_path in file_paths:
            test_message = "F401 |'sys|' imported but unused"
            test_name = "pep8: {}: {}".format(file_path.replace("\\", "/"), test_message)
            expected.extend([
                ServiceMessage('testStarted', {'name': test_name}),
                ServiceMessage('testFailed', {'name': test_name, 'message': test_message}),
                ServiceMessage('testFinished', {'name': test_name}),
            ])
        ms = assert_service_messages(output, expected)
        assert ms[2].params["details"].find(test_message.replace('|', '|||')) > 0


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
    custom = 'custom'
    if 'pytest>=4,<5' in venv.packages:
        custom = 'old_custom'
    output = run(venv, custom)
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "2"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.{}.test_simple_yml.line1'.format(custom)}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.{}.test_simple_yml.line1'.format(custom)}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.{}.test_simple_yml.line2'.format(custom)}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.{}.test_simple_yml.line2'.format(custom)}),
        ])


if sys.version_info >= (2, 6):
    @pytest.mark.parametrize("coverage_version, pytest_cov_version", [
        ("==4.4.2", "==2.11.1"),
        ("==4.5.4", "==2.11.1"),
        ("==5.0.1", "==2.11.1"),
        # latest
        ("", ""),
    ])
    def test_coverage(venv, coverage_version, pytest_cov_version):
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
            ServiceMessage('testCount', {'count': "3"}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_error'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail'}),
            ServiceMessage('testStarted', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail_diff'}),
            ServiceMessage('testFailed', {}),
            ServiceMessage('testFinished', {'name': 'tests.guinea-pigs.pytest.unittest_error_test.TestErrorFail.test_fail_diff'}),
        ])
    assert ms[2].params["details"].find("raise Exception") > 0
    assert ms[2].params["details"].find("oops") > 0
    assert ms[8].params["details"].find("unittest_error_test.py:13: AssertionError") > 0


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


def test_class_with_method(venv):
    output = run(venv, 'class_with_method.py')
    assert_service_messages(
        output,
        [ServiceMessage('testCount', {'count': "1"})] +
        [ServiceMessage('testStarted', {"metainfo": "test_method"})] +
        [ServiceMessage('testFailed', {})] +
        [ServiceMessage('testFinished', {})]
    )


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
    if "pytest==2.7" in venv.packages:
        pytest.skip("Diff is broken for ancient pytest")

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


@pytest.mark.skipif("sys.version_info < (3, 6)", reason="requires Python 3.6+")
def test_rerun(venv):
    run(venv, 'test_rerun.py')
    output = run(venv, 'test_rerun.py', options='--last-failed')
    test_name = "tests.guinea-pigs.pytest.test_rerun.TestPyTest.testTwo"
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name}),
            ServiceMessage('testFailed', {'flowId': test_name}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name}),
        ])


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
            ServiceMessage('testStarted', {'name': test1_name, 'metainfo': 'test_eval|[3+5-8|]'}),
            ServiceMessage('testFinished', {'name': test1_name}),
            ServiceMessage('testStarted', {'name': test2_name}),
            ServiceMessage('testFinished', {'name': test2_name}),
            ServiceMessage('testStarted', {'name': test3_name}),
            ServiceMessage('testFailed', {'name': test3_name,
                                          'message': fix_slashes(
                                              'tests/guinea-pigs/pytest/params_test.py') + ':3 (test_eval|[6*9-42|])|n54 != 42|n'}),
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


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_long_diff(venv):
    output = run(venv, "../diff_assert_error_long.py")
    test_name = 'tests.guinea-pigs.diff_assert_error_long.test_test'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, "actual": "foo" * 10000, "expected": "spam" * 10}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_multiline_diff(venv):
    output = run(venv, "../diff_assert_error_multiline.py")
    test_name = 'tests.guinea-pigs.diff_assert_error_multiline.test_test'
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name}),
            ServiceMessage('testFailed', {'name': test_name, "actual": "a|n" * 30, "expected": "b|n" * 30}),
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
            ServiceMessage('testFailed', {'name': test_name, "actual": "123", "expected": "456"}),
            ServiceMessage('testFinished', {'name': test_name}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff(venv):
    if "pytest==2.7" in venv.packages:
        pytest.skip("Diff is broken for ancient pytest")

    output = run(venv, SCRIPT)
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "3"}),
        ] + expected_messages("tests.guinea-pigs.diff_assert.FooTest"))


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_diff_assert_error(venv):
    output = run(venv, "../diff_assert_error.py")
    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test"}),
            ServiceMessage('testFailed', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test", "actual": "spam", "expected": "eggs"}),
            ServiceMessage('testFinished', {'name': "tests.guinea-pigs.diff_assert_error.FooTest.test_test"}),
        ])


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_swap_diff_assert_error(venv):
    with make_ini('[pytest]\nswapdiff=true'):
        output = run(venv, "../diff_assert_error.py")
    check_swap_diff_result(output)


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_swap_diff_argument_assert_error(venv):
    output = run(venv, "../diff_assert_error.py", additional_arguments="--jb-swapdiff")
    check_swap_diff_result(output)


def check_swap_diff_result(output):
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
            ServiceMessage('testFailed', {'name': "tests.guinea-pigs.diff_toplevel_assert_error.test_test", "actual": "spam", "expected": "eggs"}),
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


@pytest.mark.skipif("sys.version_info < (2, 7) ", reason="requires Python 2.7")
def test_skip_passed_output(venv):
    with make_ini('[pytest]\nskippassedoutput=true'):
        output = run(venv, 'output_test.py')

    test_name = 'tests.guinea-pigs.pytest.output_test.test_out'

    assert_service_messages(
        output,
        [
            ServiceMessage('testCount', {'count': "1"}),
            ServiceMessage('testStarted', {'name': test_name, 'flowId': test_name, 'captureStandardOutput': 'false'}),
            ServiceMessage('testFinished', {'name': test_name, 'flowId': test_name})
        ])


def run(venv, file_names, test=None, options='', set_tc_version=True, additional_arguments=None, env=None):
    if test is not None:
        test_suffix = "::" + test
    else:
        test_suffix = ""

    if not isinstance(file_names, list):
        file_names = [file_names]

    command = os.path.join(venv.bin, 'py.test') + " " + options + " "
    command += ' '.join(os.path.join('tests', 'guinea-pigs', 'pytest', file_name) + test_suffix
                        for file_name in file_names)
    if additional_arguments:
        command += " " + additional_arguments
    return run_command(command, set_tc_version=set_tc_version, env=env)
