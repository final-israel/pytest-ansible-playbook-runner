# -*- coding: utf-8 -*-


import textwrap

import pytest


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_simple(testdir, inventory, minimal_playbook, marker_type):
    """
    Make sure that``ansible_playbook`` fixture is recognized and pytest itself
    is not broken by running very simple playbook which has no side effects.
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}')
        def test_foo(ansible_playbook):
            assert 1 == 1
        """.format(marker_type, minimal_playbook.basename)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(minimal_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_foo PASSED*'])
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_simple_usedbyfixture(
        testdir,
        inventory,
        minimal_playbook,
        marker_type):
    """
    Check what happens when ``ansible_playbook`` fixture is used with a fixtrue
    by running very simple playbook which has no side effects.

    This is expected to end with ERROR as mark has no effect in fixture
    functions, see also:

     * https://gitlab.com/mbukatov/pytest-ansible-playbook/issues/4
     * https://github.com/pytest-dev/pytest/issues/3664

    I keep it here as a reference and to be able to notice any changes related
    to this use case in pytest.
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}')
        @pytest.fixture
        def fixture_foo(ansible_playbook):
            return 1

        def test_foo(fixture_foo):
            assert 1 == fixture_foo
        """.format(marker_type, minimal_playbook.basename)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(minimal_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_foo ERROR*'])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type):
    """
    Make sure that ``ansible_playbook`` fixture is actually executes
    given playbook.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}')
        def test_foo(ansible_playbook):
            assert 1 == 1

        @pytest.mark.ansible_playbook_{0}('{1}')
        def test_bar(ansible_playbook):
            assert 1 == 0
        """.format(marker_type, playbook.basename)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo PASSED*',
        '*::test_bar FAILED*',
        ])
    # check that test_file has been created
    with open(test_file_path, 'r') as test_file_object:
        content = test_file_object.read()
        assert content == test_file_content + "\n"
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
@pytest.mark.parametrize("pytest_case", [
    pytest.param(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}')
        @pytest.mark.ansible_playbook_{0}('{2}')
        def test_1(ansible_playbook):
            assert 1 == 1
        """), id="twomarkers"),
    pytest.param(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}', '{2}')
        def test_1(ansible_playbook):
            assert 1 == 1
        """), id="onemarker"),
    ])
def test_two_checkfile(
        testdir,
        inventory,
        testfile_playbook_generator,
        marker_type,
        pytest_case):
    """
    Make sure that ``ansible_playbook`` fixture actually executes
    both playbooks specified in the marker decorator.
    """
    playbook_1, filepath_1, content_1 = testfile_playbook_generator.get()
    playbook_2, filepath_2, content_2 = testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(pytest_case.format(
        marker_type, playbook_1.basename, playbook_2.basename))
    # check assumption of this test case, if this fails, we need to rewrite
    # this test case so that both playbook files ends in the same directory
    assert playbook_1.dirname == playbook_2.dirname
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook_1.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_1 PASSED*'])
    # check that test_file has been created
    for file_path, exp_content in zip(
            (filepath_1, filepath_2),
            (content_1, content_2)):
        with open(file_path, 'r') as test_file_object:
            content = test_file_object.read()
            assert content == exp_content + "\n"
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_teardown_checkfile(testdir, inventory, testfile_playbook_generator):
    """
    Make sure that ``ansible_playbook`` fixture actually executes
    setup playbook during setup, and then teardown playbook during teardown.

    This is done by making the check in the temporary pytest module
    (see testdir.makepyfile call), which makes sure that:

    * setup temporary file exists
    * teardown temporary file doesn't exist
    """
    # setup playbook
    playbook_1, filepath_1, content_1 = testfile_playbook_generator.get()
    # teardown playbook
    playbook_2, filepath_2, content_2 = testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_setup('{setup_playbook}')
        @pytest.mark.ansible_playbook_teardown('{teardown_playbook}')
        def test_proper_teardown(ansible_playbook):
            with open('{setup_file_path}', 'r') as test_file_object:
                content = test_file_object.read()
                assert content == '{setup_exp_content}' + "\\n"
            with pytest.raises(IOError):
                open('{teardown_file_path}', 'r')
        """.format(
            setup_playbook=playbook_1.basename,
            teardown_playbook=playbook_2.basename,
            setup_file_path=filepath_1,
            setup_exp_content=content_1,
            teardown_file_path=filepath_2,
            )))
    # check assumption of this test case, if this fails, we need to rewrite
    # this test case so that both playbook files ends in the same directory
    assert playbook_1.dirname == playbook_2.dirname
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook_1.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_proper_teardown PASSED*'])
    # check that test_file has been created
    for file_path, exp_content in zip(
            (filepath_1, filepath_2),
            (content_1, content_2)):
        with open(file_path, 'r') as test_file_object:
            content = test_file_object.read()
            assert content == exp_content + "\n"
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_missing_mark(testdir, inventory, minimal_playbook):
    """
    Make sure that test cases ends in ERROR state when a test case is not
    marked with ``@pytest.mark.ansible_playbook_setup('playbook.yml')``.
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        def test_foo(ansible_playbook):
            assert 1 == 1
        """))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(minimal_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR*',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
@pytest.mark.parametrize("emptiness", ["", "()"])
def test_empty_mark(
        testdir, inventory, minimal_playbook, marker_type, emptiness):
    """
    Make sure that test cases ends in ERROR state when a test case is
    marked with empty marker decorator
    (``@pytest.mark.ansible_playbook_setup()``).
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}{1}
        def test_foo(ansible_playbook):
            assert 1 == 1
        """.format(marker_type, emptiness)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(minimal_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR*',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_ansible_error(testdir, inventory, broken_playbook, marker_type):
    """
    Make sure that test cases ends in ERROR state when ``ansible_playbook``
    fixture fails (because of ansible reported error).
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}')
        def test_foo(ansible_playbook):
            assert 1 == 1

        @pytest.mark.ansible_playbook_{0}('{1}')
        def test_bar(ansible_playbook):
            assert 1 == 0
        """.format(marker_type, broken_playbook.basename)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(broken_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR*',
        '*::test_bar ERROR*',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1
