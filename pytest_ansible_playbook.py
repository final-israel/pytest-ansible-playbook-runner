# -*- coding: utf-8 -*-
"""
Implementation of pytest-ansible-playbook plugin.
"""

# Copyright 2016 Martin Bukatovič <mbukatov@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function
import os
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


def pytest_configure(config):
    """
    Validate pylatest-ansible-playbook options: when such option is used,
    the given file or directory should exist.

    This check makes the pytest fail immediatelly when wrong path is
    specified, without waiting for the first test case with ansible_playbook
    fixture to fail.
    """
    dir_path = config.getvalue('ansible_playbook_directory')
    if dir_path is not None and not os.path.isdir(dir_path):
        msg = (
            "value of --ansible-playbook-directory option ({0}) "
            "is not a directory").format(dir_path)
        raise pytest.UsageError(msg)
    inventory_path = config.getvalue('ansible_playbook_inventory')
    if inventory_path is None:
        return
    if not os.path.isabs(inventory_path) and dir_path is not None:
        inventory_path = os.path.join(dir_path, inventory_path)
    if not os.path.isfile(inventory_path):
        msg = (
            "value of --ansible-playbook-inventory option ({}) "
            "is not accessible").format(inventory_path)
        raise pytest.UsageError(msg)


def get_ansible_cmd(inventory_file, playbook_file):
    """
    Return process args list for ansible-playbook run.
    """
    ansible_command = [
        "ansible-playbook",
        "-vv",
        "-i", inventory_file,
        playbook_file,
        ]
    return ansible_command


def get_empty_marker_error(marker_type):
    """
    Generate error message for empty marker.
    """
    msg = (
        "no playbook is specified in "
        "``@pytest.mark.ansible_playbook_{0}`` decorator "
        "of this test case, please add at least one playbook "
        "file name as a parameter into the marker, eg. "
        "``@pytest.mark.ansible_playbook_{0}('playbook.yml')``")
    return msg.format(marker_type)


@pytest.fixture
def ansible_playbook(request):
    """
    Pytest fixture which runs given ansible playbook. When ansible returns
    nonzero return code, the test case which uses this fixture is not
    executed and ends in ``ERROR`` state.
    """
    setup_marker = request.node.get_marker('ansible_playbook_setup')
    setup_playbooks = []
    teardown_marker = request.node.get_marker('ansible_playbook_teardown')
    teardown_playbooks = []

    if setup_marker is None and teardown_marker is None:
        msg = (
            "no ansible playbook is specified for the test case, "
            "please add a decorator like this one "
            "``@pytest.mark.ansible_playbook_setup('playbook.yml')`` "
            "or "
            "``@pytest.mark.ansible_playbook_teardown('playbook.yml')`` "
            "for ansible_playbook fixture to know which playbook to use")
        raise Exception(msg)
    if setup_marker is not None:
        setup_playbooks = setup_marker.args
        if len(setup_marker.args) == 0:
            raise Exception(get_empty_marker_error("setup"))
    if teardown_marker is not None:
        teardown_playbooks = teardown_marker.args
        if len(teardown_marker.args) == 0:
            raise Exception(get_empty_marker_error("teardown"))

    # setup
    for playbook_file in setup_playbooks:
        subprocess.check_call(
            get_ansible_cmd(
                request.config.option.ansible_playbook_inventory,
                playbook_file),
            cwd=request.config.option.ansible_playbook_directory)
    yield
    # teardown
    for playbook_file in teardown_playbooks:
        subprocess.check_call(
            get_ansible_cmd(
                request.config.option.ansible_playbook_inventory,
                playbook_file),
            cwd=request.config.option.ansible_playbook_directory)
