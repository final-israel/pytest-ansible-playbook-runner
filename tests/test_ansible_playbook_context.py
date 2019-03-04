# -*- coding: utf8 -*-


import textwrap

import pytest


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_simple(testdir, inventory, minimal_playbook, marker_type):
    """
    Make sure that``ansible_playbook_context`` fixture is recognized and pytest
    itself is not broken by running very simple playbook which has no side
    effects.
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        def test_foo(ansible_playbook_context):
            with ansible_playbook_context({0}_playbooks=['{1}']):
                pass
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
def test_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type):
    """
    Make sure that ``ansible_playbook_context`` context manager actually
    executes given playbook.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        def test_bar(ansible_playbook_context):
            with ansible_playbook_context({0}_playbooks=['{1}']):
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
        '*::test_bar FAILED*',
        ])
    # check that test_file has been created only for setup playbook
    if marker_type == "setup":
        with open(test_file_path, 'r') as test_file_object:
            content = test_file_object.read()
            assert content == test_file_content + "\n"
    else:
        with pytest.raises(FileNotFoundError):
            open(test_file_path, 'r')
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_custom_fixture_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type):
    """
    Build custom fixture using ``ansible_playbook_context`` context manager and
    check that it executes given playbooks as expected.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.fixture
        def some_fixture(ansible_playbook_context):
            {0}_playbooks = ['{1}']
            with ansible_playbook_context({0}_playbooks):
                yield

        def test_bar(some_fixture):
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
        '*::test_bar FAILED*',
        ])
    # check that test_file has been created
    with open(test_file_path, 'r') as test_file_object:
        content = test_file_object.read()
        assert content == test_file_content + "\n"
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1
