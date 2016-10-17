# -*- coding: utf-8 -*-


import pytest


def pytest_addoption(parser):
    group = parser.getgroup('ansible-playbook')
    group.addoption(
        '--ansible-playbook-directory',
        action='store',
        dest='ansible_playbook_dir',
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
def bar(request):
    return request.config.option.dest_foo
