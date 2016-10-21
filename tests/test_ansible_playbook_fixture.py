# -*- coding: utf-8 -*-


import os
import textwrap


def test_simple(testdir):
    """
    Make sure that``ansible_playbook`` fixture is recognized and pytest itself
    is not broken by running very simple playbook which has no side effects.
    """
    # create a minimal ansbile inventory file (just a single line inside)
    inventory = testdir.makefile(".ini", "localhost")
    # create a minimal ansbile playbook file (which does nothing)
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - action: ping",
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook('{0}')
        def test_foo(ansible_playbook):
            assert 1 == 1
        """.format(playbook.basename)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_foo PASSED'])
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_checkfile(testdir):
    """
    Make sure that``ansible_playbook`` fixture is actually executes
    given playbook.
    """
    # create a minimal ansbile inventory file
    inventory = testdir.makefile(".ini", "localhost")
    # define file path for a test file which will be created
    # by ansible-playbook run
    test_file_path = os.path.join(inventory.dirname, "test_file")
    # create ansbile playbook file (which would create file on test_file_path)
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - name: Create file in pytest testdir",
        "     lineinfile:",
        "       dest={0}".format(test_file_path),
        "       create=yes",
        "       line=testcontent",
        "       state=present",
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook('{0}')
        def test_foo(ansible_playbook):
            assert 1 == 1

        @pytest.mark.ansible_playbook('{0}')
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
        '*::test_foo PASSED',
        '*::test_bar FAILED',
        ])
    # check that test_file has been created
    with open(test_file_path, 'r') as test_file_object:
        content = test_file_object.read()
        assert content == "testcontent\n"
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


def test_two_checkfile(testdir):
    """
    Make sure that ``ansible_playbook`` fixture actually executes
    both playbooks specified in the marker decorator.
    """
    # create a minimal ansbile inventory file
    inventory = testdir.makefile(".ini", "localhost")
    # define file path for a test file which will be created
    # by ansible-playbook run
    test_file_paths = [
        os.path.join(inventory.dirname, "test_file_one"),
        os.path.join(inventory.dirname, "test_file_two"),
        ]
    # create ansbile playbook file (which would create file on test_file_path)
    playbook_one = testdir.makefile(
        ".one.yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - name: Create file in pytest testdir",
        "     lineinfile:",
        "       dest={0}".format(test_file_paths[0]),
        "       create=yes",
        "       line=testcontent",
        "       state=present",
        )
    playbook_two = testdir.makefile(
        ".two.yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - name: Create file in pytest testdir",
        "     lineinfile:",
        "       dest={0}".format(test_file_paths[1]),
        "       create=yes",
        "       line=testcontent",
        "       state=present",
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook('{0}', '{1}')
        def test_one(ansible_playbook):
            assert 1 == 1
        """.format(playbook_one.basename, playbook_two.basename)))
    # check assumption of this test case, if this fails, we need to rewrite
    # this test case so that both playbook files ends in the same directory
    assert playbook_one.dirname == playbook_two.dirname
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook_one.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines(['*::test_one PASSED'])
    # check that test_file has been created
    for file_path in test_file_paths:
        with open(file_path, 'r') as test_file_object:
            content = test_file_object.read()
            assert content == "testcontent\n"
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


def test_missing_mark(testdir):
    """
    Make sure that test cases ends in ERROR state when a test case is not
    marked with ``@pytest.mark.ansible_playbook('playbook.yml')``.
    """
    # create a minimal ansbile inventory file
    inventory = testdir.makefile(".ini", "localhost")
    # create a minimal ansbile playbook file (which does nothing)
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - action: ping",
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        def test_foo(ansible_playbook):
            assert 1 == 1
        """))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


def test_empty_mark(testdir):
    """
    Make sure that test cases ends in ERROR state when a test case is
    marked with empty marker decorator (``@pytest.mark.ansible_playbook()``).
    """
    # create a minimal ansbile inventory file
    inventory = testdir.makefile(".ini", "localhost")
    # create a minimal ansbile playbook file (which does nothing)
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - action: ping",
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook()
        def test_foo(ansible_playbook):
            assert 1 == 1
        """))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


def test_ansible_error(testdir):
    """
    Make sure that test cases ends in ERROR state when ``ansible_playbook``
    fixture fails (because of ansible reported error).
    """
    # create a minimal ansbile inventory file
    inventory = testdir.makefile(".ini", "localhost")
    # create a broken ansbile playbook file
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - nothing",  # here is the problem inserted on purpose
        )
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook('{0}')
        def test_foo(ansible_playbook):
            assert 1 == 1

        @pytest.mark.ansible_playbook('{0}')
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
        '*::test_foo ERROR',
        '*::test_bar ERROR',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1