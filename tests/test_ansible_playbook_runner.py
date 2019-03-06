# -*- coding: utf8 -*-


import textwrap

import pytest


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_runner_intest_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type):
    """
    Make sure that ``pytest_ansible_playbook.runner`` context manager actually
    executes given playbook when used in a test case.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        from pytest_ansible_playbook import runner

        def test_bar(request):
            with runner(request, {0}_playbooks=['{1}']):
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
        with pytest.raises(IOError):
            open(test_file_path, 'r')
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("scope", ["function", "module", "class", "session"])
@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_customfixture_scope_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type, scope):
    """
    Build custom fixture using ``pytest_ansible_playbook.runner`` context
    manager and check that it executes given playbooks as expected.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest
        from pytest_ansible_playbook import runner

        @pytest.fixture(scope="{2}")
        def some_fixture(request):
            with runner(request, {0}_playbooks=['{1}']):
                yield

        def test_bar(some_fixture):
            assert 1 == 0
        """.format(marker_type, playbook.basename, scope)))
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
