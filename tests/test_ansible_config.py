# -*- coding: utf-8 -*-


import pytest


def test_help_message(testdir):
    """
    Check that ``py.test --help`` output lists options of
    ansible-playbook pytest plugin.
    """
    result = testdir.runpytest('--help')
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'ansible-playbook:',
        '*--ansible-playbook-directory=PLAYBOOK_DIR*',
        '*--ansible-playbook-inventory=INVENTORY_FILE*',
        ])


@pytest.mark.parametrize("dir_value, dir_error", [
    ("/none", "is not a directory"),
    ("/dev", None),
    (None, None),
    ])
@pytest.mark.parametrize("inv_value, inv_error", [
    ("/none", "is not accessible"),
    ("/dev/zero", None),
    ("zero", None),
    (None, None),
    ])
def test_invalid_options(testdir, dir_value, dir_error, inv_value, inv_error):
    """
    Make sure that test pytests reports an ERROR immediatelly when invalid
    options are specified.

    For a file or directory which doesn't exist, "/none" path is used (see
    parametrize decorator).

    For a file or directory which is expected to exist, "/dev/zero" and "/dev"
    values are used (to simplify the setup of the test, but it make the test
    run only on POSIX systems).
    """
    # build ``py.test`` command line arugment list
    args = []
    if dir_value is not None:
        args.append('--ansible-playbook-directory={0}'.format(dir_value))
    if inv_value is not None:
        args.append('--ansible-playbook-inventory={0}'.format(inv_value))
    args.append('-v')

    # run pytest with the following cmd args
    result = testdir.runpytest(*args)

    # build list of expected errors to check in stderr of pytest command
    match_lines = []
    if dir_error is not None:
        match_lines.append('ERROR:*value of *{0}'.format(dir_error))
    # note: when dir_error is detected, pytest ends reporting the problem
    # immediatelly without going on to check inventory, so we don't check
    # for inventory related error message when issue with directory is
    # detected as well
    if inv_error is not None and dir_error is None:
        match_lines.append('ERROR:*value of *{0}'.format(inv_error))
    # when inventory path is relative, but the path to the directory is not
    # specified
    if inv_value == "zero" and dir_value is None:
        match_lines.append('ERROR:*value of *{0}'.format("is not accessible"))

    # fnmatch_lines does an assertion internally
    result.stderr.fnmatch_lines(match_lines)

    # make sure that that we get expected error code
    if dir_value is None and inv_value is None:
        # this is a case without any ansible-playbook options, equiv. of
        # running ``py.test -v`` in a directory without any tests,
        # so there should be no error
        assert result.ret == 5
    elif dir_value is not None and dir_error is None and inv_value is None:
        # case when only the --ansible-playbook-directory is specified
        # correctly, without using --ansible-playbook-inventory option,
        # so again, no error
        assert result.ret == 5
    else:
        assert result.ret == 4
