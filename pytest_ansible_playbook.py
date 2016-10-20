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
        dest='ansible_playbook_dir',
        metavar="PLAYBOOK_DIR",
        help='Directory where ansible playbooks are stored.',
        )
    group.addoption(
        '--ansible-playbook',
        action='store',
        dest='ansible_playbook_file',
        metavar="PLAYBOOK_FILE",
        help='Ansible playbook file.',
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
    ansible_command = [
        "ansible-playbook",
        "-vv",
        "-i", request.config.option.ansible_playbook_inventory,
        request.config.option.ansible_playbook_file,
        ]
    subprocess.check_call(ansible_command)
