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
import uuid
import contextlib
from playbook_runner import playbook_runner
import subprocess
import json
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
    Validate pytest-ansible-playbook options: when such option is used,
    the given file or directory should exist.

    This check makes the pytest fail immediately when wrong path is
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


def get_missing_file_error(marker_type, playbook):
    """
        Generate error message for empty marker.
        """
    msg = (
        "no file is specified in "
        "``@pytest.mark.ansible_playbook_{0}`` decorator "
        "for the playbook - ``{1}``")
    return msg.format(marker_type, playbook)


class PytestAnsiblePlaybook(playbook_runner.AnsiblePlaybook):
    def __init__(self, ansible_playbook_inventory, ansible_playbook_directory,
                 request, session_uuid=None):
        playbook_runner.AnsiblePlaybook.__init__(
            self,
            ansible_playbook_inventory,
            ansible_playbook_directory,
        )

        self._request = request
        self._setup_playbooks = []
        self._teardown_playbooks = []

        self.session_uuid = session_uuid
        self.outputs = {
            'setup': {},
            'teardown': {},
        }
        self._inventory = None

    def get_inventory(self):
        if self._inventory is not None:
            return self._inventory

        cmd = [
                'ansible-inventory',
                '-i',
                self._ansible_playbook_inventory,
                '--list'
                ]
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.wait(timeout=60)
        stdout, stderr = proc.communicate(timeout=10)
        self._inventory = json.loads(stdout.decode('utf-8'))
        return self._inventory

    def add_to_teardown(self, element):
        self._teardown_playbooks.append(element)

    def fill_from_custom(self, setup, teardown):
        self._setup_playbooks = setup
        self._teardown_playbooks = teardown

    def fill_from_markers(self):
        if hasattr(self._request.node, "iter_markers"):
            # since pytest 4.0.0, markers api changed, see:
            # https://github.com/pytest-dev/pytest/pull/4564
            # https://docs.pytest.org/en/latest/mark.html#updating-code
            setup_ms = self._request.node.iter_markers(
                'ansible_playbook_setup')
            teardown_ms = self._request.node.iter_markers(
                'ansible_playbook_teardown')
        else:
            marker = self._request.node.get_marker('ansible_playbook_setup')
            setup_ms = [marker] if marker is not None else []
            marker = self._request.node.get_marker('ansible_playbook_teardown')
            teardown_ms = [marker] if marker is not None else []

        for marker in setup_ms:
            if len(marker.args) == 0:
                raise Exception(get_empty_marker_error("setup"))
            # extend because multiple mark entries are supported
            self._setup_playbooks.extend(marker.args)
        for marker in teardown_ms:
            if len(marker.args) == 0:
                raise Exception(get_empty_marker_error("teardown"))
            # extend because multiple mark entries are supported
            self._teardown_playbooks.extend(list(marker.args))

    def run_playbook(self, play_filename, extra_vars_dict=None):
        if extra_vars_dict is None:
            extra_vars_dict = {}
        ret = playbook_runner.AnsiblePlaybook.run_playbook(self, play_filename, extra_vars_dict)
        if 'skip_errors' not in extra_vars_dict or \
                not extra_vars_dict['skip_errors']:
            assert ret == 0

        return self.get_output()

    def setup(self):
        for playbook in self._setup_playbooks:
            if 'file' not in playbook:
                raise Exception(get_missing_file_error("setup", playbook))

            extra_vars = {"session_uuid": self.session_uuid}
            if 'extra_vars' in playbook:
                for k, v in playbook['extra_vars'].items():
                    extra_vars[k] = v

            self.outputs['setup'][playbook['file']] = \
                self.run_playbook(playbook['file'], extra_vars)

    def teardown(self):
        for playbook in self._teardown_playbooks:
            if 'file' not in playbook:
                raise Exception(get_missing_file_error("teardown", playbook))

            extra_vars = {"session_uuid": self.session_uuid}
            if 'extra_vars' in playbook:
                for k, v in playbook['extra_vars'].items():
                    extra_vars[k] = v

            self.outputs['teardown'][playbook['file']] = \
                self.run_playbook(playbook['file'], extra_vars)


@contextlib.contextmanager
def fixture_runner(
        request,
        setup_playbooks=None,
        teardown_playbooks=None,
        skip_teardown=False):
    """
    Context manager which will run playbooks specified in it's arguments.

    :param request: pytest request object
    :param setup_playbooks: list of setup playbook names (optional)
    :param teardown_playbooks: list of setup playbook names (optional)
    :param skip_teardown:
        if True, teardown playbooks are not executed when test case fails

    It's expected to be used to build custom fixtures or to be used
    directly in a test case code.
    """
    setup_playbooks = setup_playbooks or []
    teardown_playbooks = teardown_playbooks or []

    # process request object
    directory = request.config.option.ansible_playbook_directory
    inventory = request.config.option.ansible_playbook_inventory

    pap = PytestAnsiblePlaybook(
        inventory,
        directory,
        request,
    )

    pap.fill_from_custom(setup_playbooks, teardown_playbooks)
    with runner(pap, skip_teardown):
        yield pap


@contextlib.contextmanager
def runner(pap, skip_teardown=False):
    """
    Context manager which will run playbooks specified in it's arguments.

    :param request: pytest request object
    :param setup_playbooks: list of setup playbook names (optional)
    :param teardown_playbooks: list of setup playbook names (optional)
    :param skip_teardown:
        if True, teardown playbooks are not executed when test case fails

    It's expected to be used to build custom fixtures or to be used
    directly in a test case code.
    """
    run_teardown = True

    # setup
    pap.setup()

    try:
        yield
    except Exception as ex:
        if skip_teardown:
            run_teardown = False
        raise ex
    finally:
        if run_teardown:
            # teardown
            pap.teardown()


@pytest.fixture(scope='session')
def session_uuid():
    return uuid.uuid4()


@pytest.fixture(scope='session')
def ansible_playbook_directory(request):
    path = os.path.abspath(
        request.config.getoption('--ansible-playbook-directory'))
    assert os.path.isdir(path)
    return path


@pytest.fixture(scope='session')
def ansible_playbook_inventory(request):
    path = os.path.abspath(
        request.config.getoption('--ansible-playbook-inventory'))
    assert os.path.isfile(path)
    return path


@pytest.fixture(scope='function')
def ansible_playbook(request, ansible_playbook_directory,
                     ansible_playbook_inventory, session_uuid):
    pap = PytestAnsiblePlaybook(
        ansible_playbook_inventory,
        ansible_playbook_directory,
        request,
        session_uuid,
    )

    if hasattr(request.node, "iter_markers"):
        skip_teardown = request.node.get_closest_marker(
            'skip_teardown',
            default=False
        )
    else:
        skip_teardown = request.node.get_marker('skip_teardown')
        if skip_teardown is None:
            skip_teardown = False

    pap.fill_from_markers()
    with runner(pap, skip_teardown):
        yield pap


@pytest.fixture(scope='session')
def ansible_playbook_session(request, ansible_playbook_directory,
                     ansible_playbook_inventory, session_uuid):
    pap = PytestAnsiblePlaybook(
        ansible_playbook_inventory,
        ansible_playbook_directory,
        request,
        session_uuid,
    )

    with runner(pap, False):
        yield pap
