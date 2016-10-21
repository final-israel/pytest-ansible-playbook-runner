# -*- coding: utf-8 -*-
"""
Implementation of pytest-ansible-playbook plugin.
"""


from __future__ import print_function
import subprocess

import pytest


def pytest_addoption(parser):
    """
    Define py.test command line options for this plugin.
    """
    group = parser.getgroup('ansible-playbook')
    group.addoption(
        '--ansible-playbook-directory',
        action='store',
        dest='ansible_playbook_directory',
        metavar="PLAYBOOK_DIR",
        help='Directory where ansible playbooks are stored.',
        )
    group.addoption(
        '--ansible-playbook-inventory',
        action='store',
        dest='ansible_playbook_inventory',
        metavar="INVENTORY_FILE",
        help='Ansible inventory file.',
        )


@pytest.fixture
def ansible_playbook(request):
    """
    Pytest fixture which runs given ansible playbook. When ansible returns
    nonzero return code, the test case which uses this fixture is not
    executed and ends in ``ERROR`` state.
    """
    marker = request.node.get_marker('ansible_playbook')
    if marker is None:
        msg = (
            "ansible playbook not specified for the test case, "
            "please add a decorator like this one "
            "``@pytest.mark.ansible_playbook('playbook.yml')`` "
            "for ansible_playbook fixture to know which playbook to use")
        raise Exception(msg)
    if len(marker.args) == 0:
        msg = (
            "no playbook is specified in ``@pytest.mark.ansible_playbook`` "
            "decorator of this test case, please add at least one playbook "
            "file name as a parameter into the marker, eg. "
            "``@pytest.mark.ansible_playbook('playbook.yml')``")
        raise Exception(msg)
    for playbook_file in marker.args:
        ansible_command = [
            "ansible-playbook",
            "-vv",
            "-i", request.config.option.ansible_playbook_inventory,
            playbook_file,
            ]
        subprocess.check_call(
            ansible_command,
            cwd=request.config.option.ansible_playbook_directory)
