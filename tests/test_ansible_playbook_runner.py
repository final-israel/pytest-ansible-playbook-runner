# -*- coding: utf8 -*-


import textwrap

import pytest


def test_intest_runplaybook(
        testdir, inventory, testfile_playbook_generator):
    """
    Make sure that run_playbook actually
    executes given playbook when used in a test case.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest
        from pytest_ansible_playbook import ansible_playbook

        def test_bar(ansible_playbook):
            ret = ansible_playbook.run_playbook('{0}')
            assert ret['localhost'][0]['msg'] == 'line added'
            assert 1 == 0
        """.format(playbook.basename)))
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


def test_skip_teardown(
        testdir, inventory, testfile_playbook_generator):
    """
    Make sure that ``pytest_ansible_playbook.runner`` context manager actually
    executes given playbook when used in a test case.
    """
    playbook, test_file_path, test_file_content = \
        testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest
        from pytest_ansible_playbook import ansible_playbook

        @pytest.mark.ansible_playbook_teardown('{0}')
        @pytest.mark.skip_teardown(True)
        def test_bar(ansible_playbook):
            assert 1 == 0
        """.format(playbook.basename)))
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
    # check that test_file hasn't been created
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
        from pytest_ansible_playbook import fixture_runner

        @pytest.fixture(scope="{2}")
        def some_fixture(request):
            with fixture_runner(request, {0}_playbooks=[{1}]):
                yield

        def test_bar(some_fixture):
            assert 1 == 0
        """.format(marker_type, {'file': playbook.basename}, scope)))
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


def test_customfixture_sessionscope_teardown_checkfile(
        testdir, inventory, testfile_playbook_generator):
    """
    Build custom fixture using ``pytest_ansible_playbook.runner`` context
    manager and make sure that it actually executes setup playbook during
    enter phase, and then teardown playbook during exit.
    """
    # setup playbook
    playbook_1, filepath_1, content_1 = testfile_playbook_generator.get()
    # teardown playbook
    playbook_2, filepath_2, content_2 = testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest
        from pytest_ansible_playbook import fixture_runner

        @pytest.fixture(scope="session")
        def some_fixture(request):
            with fixture_runner(
                    request, [{setup_playbook}], [{teardown_playbook}]):
                yield

        def test_proper_teardown_one(some_fixture):
            with open('{setup_file_path}', 'r') as test_file_object:
                content = test_file_object.read()
                assert content == '{setup_exp_content}' + "\\n"
            with pytest.raises(IOError):
                open('{teardown_file_path}', 'r')

        # this 2nd test case is there to check that session scope works fine
        def test_proper_teardown_two(some_fixture):
            with open('{setup_file_path}', 'r') as test_file_object:
                content = test_file_object.read()
                assert content == '{setup_exp_content}' + "\\n"
            # The following check will pass only because ``some_fixture`` has
            # "session" scope. If the fixture had "function" scope, the
            # teardown playbook would be already executed at this point and so
            # the check would not get expected IOError error.
            with pytest.raises(IOError):
                open('{teardown_file_path}', 'r')
        """.format(
            setup_playbook={'file': playbook_1.basename},
            teardown_playbook={'file': playbook_2.basename},
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
    result.stdout.fnmatch_lines([
        '*::test_proper_teardown_one PASSED*',
        '*::test_proper_teardown_two PASSED*',
        ])
    # check that test_file has been created
    for file_path, exp_content in zip(
            (filepath_1, filepath_2),
            (content_1, content_2)):
        with open(file_path, 'r') as test_file_object:
            content = test_file_object.read()
            assert content == exp_content + "\n"
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
