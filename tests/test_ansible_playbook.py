# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest('--help')
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'ansible-playbook:',
        '*--ansible-playbook-directory=PLAYBOOK_DIR*',
        '*--ansible-playbook-inventory=INVENTORY_FILE*',
        ])
