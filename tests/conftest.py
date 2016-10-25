# -*- coding: utf-8 -*-

import os
import random
import string

import pytest


pytest_plugins = 'pytester'


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
