# -*- coding: utf-8 -*-


import os
import random
import string
import textwrap

import pytest


@pytest.fixture
def inventory(testdir):
    """
    Create minimal ansible inventory file (such file contains just
    single line ``localhost``).
    """
    inventory = testdir.makefile(".ini", "localhost")
    return inventory


@pytest.fixture
def minimal_playbook(testdir):
    """
    Create minimal ansible playbook file without any side effects.
    """
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - action: ping",
        )
    return playbook


@pytest.fixture
def broken_playbook(testdir):
    """
    Create minimal ansible playbook file with an error in it, so that the
    ``ansible-playbook`` would immediatelly fail when trying to execute it.
    """
    playbook = testdir.makefile(
        ".yml",
        "---",
        "- hosts: all",
        "  connection: local",
        "  tasks:",
        "   - nothing",  # here is the problem inserted on purpose
        )
    return playbook


@pytest.fixture
def testfile_playbook_generator(testdir):
    """
    Return an object with ``get()`` method to generate a playbook file which
    creates a test file along with expected path and content.

    This is usefull when one needs one or more playbooks with simple and easy
    to check side effect.
    """
    class PlaybookGenerator(object):
        _id = 1

        def get(self):
            # create dummy temp file,
            # so that we can check it's ``.dirname`` attribute later
            dummy_file = testdir.makefile(".dummy", "")
            # define file path for a test file which will be created
            # by ansible-playbook run
            test_file_path = os.path.join(
                dummy_file.dirname,
                "test_file.{0}".format(PlaybookGenerator._id))
            # generate random content of the test file
            test_file_content = "".join(
                random.choice(string.ascii_letters) for _ in range(15))
            # create ansbile playbook file(which would create file on
            # test_file_path with test_file_content in it)
            playbook = testdir.makefile(
                ".{0}.yml".format(PlaybookGenerator._id),
                "---",
                "- hosts: all",
                "  connection: local",
                "  tasks:",
                "   - name: Create test file",
                "     lineinfile:",
                "       dest={0}".format(test_file_path),
                "       create=yes",
                "       line={0}".format(test_file_content),
                "       state=present",
                )
            PlaybookGenerator._id += 1
            return playbook, test_file_path, test_file_content

    return PlaybookGenerator()


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
    result.stdout.fnmatch_lines(['*::test_foo PASSED'])
    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


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
        '*::test_foo PASSED',
        '*::test_bar FAILED',
        ])
    # check that test_file has been created
    with open(test_file_path, 'r') as test_file_object:
        content = test_file_object.read()
        assert content == test_file_content + "\n"
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_two_checkfile(
        testdir, inventory, testfile_playbook_generator, marker_type):
    """
    Make sure that ``ansible_playbook`` fixture actually executes
    both playbooks specified in the marker decorator.
    """
    playbook_1, filepath_1, content_1 = testfile_playbook_generator.get()
    playbook_2, filepath_2, content_2 = testfile_playbook_generator.get()
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}('{1}', '{2}')
        def test_1(ansible_playbook):
            assert 1 == 1
        """.format(marker_type, playbook_1.basename, playbook_2.basename)))
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
    result.stdout.fnmatch_lines(['*::test_1 PASSED'])
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
    result.stdout.fnmatch_lines(['*::test_proper_teardown PASSED'])
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
        '*::test_foo ERROR',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1


@pytest.mark.parametrize("marker_type", ["setup", "teardown"])
def test_empty_mark(testdir, inventory, minimal_playbook, marker_type):
    """
    Make sure that test cases ends in ERROR state when a test case is
    marked with empty marker decorator
    (``@pytest.mark.ansible_playbook_setup()``).
    """
    # create a temporary pytest test module
    testdir.makepyfile(textwrap.dedent("""\
        import pytest

        @pytest.mark.ansible_playbook_{0}()
        def test_foo(ansible_playbook):
            assert 1 == 1
        """.format(marker_type)))
    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--ansible-playbook-directory={0}'.format(minimal_playbook.dirname),
        '--ansible-playbook-inventory={0}'.format(inventory.basename),
        '-v',
        )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_foo ERROR',
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
        '*::test_foo ERROR',
        '*::test_bar ERROR',
        ])
    # make sure that that we get a '1' exit code for the testsuite
    assert result.ret == 1
