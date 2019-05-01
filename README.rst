pytest-ansible-playbook-runner
===================================

This repository contains `pytest`_ `plugin`_ which provides an easy way
to run particular `ansible playbooks`_ during setup phase of a test case.
This is useful when
you already have some playbook files you would like to reuse during test setup
or plan to maintain test setup in ansible playbooks for you to be able to
use it both during test run setup and directly via ansible for other purposes
(automatically during deployment or manually when needed).

Compared with `pytest-ansible`_ module, this module doesn't allow you to
inspect `ansible facts`_ or details about results of each ansible task, nor
doest it allow to specify and execute an ansible task directly. So if you need
any of that, go for `pytest-ansible`_ instead. This plugin provides the only
missing ansible feature which `pytest-ansible`_ is not supposed to provide - to
run ansible playbook file directly.

Initial structure of this repository was generated with `Cookiecutter`_
along with `@hackebrot`_'s `Cookiecutter-pytest-plugin`_ template.


Features
--------

**Notes:**

- The plugin provides `ansible_playbook` `pytest fixture`_, which allows
  one to run one or more ansible playbooks during test setup or tear down of a
  test case.
  
- It also provides `context manager`_ `pytest_ansible_playbook.runner()`
  which can be used to build custom fixtures with any `scope`_ or to execute
  setup and/or teardown playbooks in a code of a test case.
  
- It's compatible with python3 (playbooks are executed via
  running `ansible-playbook` in subprocess instead of using api
  of ansible python module).
  
- Doesn't allow you to configure ansible in any way, all changes of ansible
  setup needs to be done in ansible playbooks, variable or config files.
  This encourages you to maintain a clear separation of ansible playbooks
  and the tests.
  
  

**Key features:**

1. An option to run arbitrary playbooks in the middle of the test:
    
    ```python
    def test_something(ansible_playbook,....):
      ...
  ansible_playbook.run_playbook('my_playbook.yml')
      ...
      
    ```
    
2. An option to add teardown playbooks in the middle of the test::
    def test_something(ansible_playbook,....):
      ...
      ansible_playbook.add_to_teardown({'file': 'my_playbook.yml', 'extra_vars': {})
      ...

3. Return values have been added to every playbook run. The return value respects playbook execution order and for every host::

  def test_something(ansible_playbook,....):
      ...
      ret = ansible_playbook.run_playbook('my_playbook.yml')
      assert ret['localhost'][0]['msg'] == 'line added'

4. A test can pass arguments to the playbooks it runs. Thus the playbook has changed from string to dictionary::

  def test_something(ansible_playbook,....):
      ...
      ansible_playbook.run_playbook('my_playbook.yml', {'play_host_groupd': 'some_ansible_group', 'param1': 'value1'})
      ...

5. Mark setup / teardown syntax::

  @pytest.mark.ansible_playbook_setup(
      {'file': 'some_playbook.yml', 'extra_vars': {'play_host_groupd': 'some_ansible_group', 'param1': 'value1'}}
  )
  @pytest.mark.ansible_playbook_teardown(
      {'file': 'my_teardown1.yml', 'extra_vars': {'play_host_groupd': 'some_ansible_group', 'param1': 'value1'}},
      {'file': 'my_teardown2.yml', 'extra_vars': {'play_host_groupd': 'some_ansible_group', 'param1': 'value1'}}
  )
  def test_something(ansible_playbook,....):
      ...
      ansible_playbook.run_playbook('my_playbook.yml', {'play_host_groupd': 'some_ansible_group', 'param1': 'value1'})
      ...


Now the pytest plugin uses a separate module: playbook_runner.
https://github.com/final-israel/playbook_runner
This is because other tools may want to also run playbooks not necessarily as a part of the pytest framework.


Requirements
------------

Ansible should be installed (so that ``ansible-playbook`` binary is
available in PATH). Use version provided by packaging system of your operation
system.


Installation
------------

You can either install `stable release from PyPI`_ or use latest development
version from master branch.


Installing stable release
~~~~~~~~~~~~~~~~~~~~~~~~~

You can install "pytest-ansible-playbook-runner" via `pip`_ from `PyPI`_::

    $ pip install pytest-ansible-playbook-runner


Installing latest development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The suggested way to install from sources of current master branch is
via `python virtual enviroment`_::

    $ cd pytest-ansible-playbook-runner
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -e .

Note that you can use `virtualenvwrapper`_ to simplify this workflow.


Usage
-----

When the plugin is installed, you can use the following command-line
parameters::

    py.test \
        [--ansible-playbook-directory <path_to_directory_with_playbooks>] \
        [--ansible-playbook-inventory <path_to_inventory_file>]

Where ``<path_to_directory_with_playbooks>`` is a directory which contains
ansible playbooks and any other ansible files such as
configuration or roles if needed. A ``ansible-playbook`` process will be able
to access the files stored there, since this directory is set as cwd (current
working directory) of the ansible process.

The ``<path_to_inventory_file>`` is file with `ansible inventory`_. You can
use either an absolute path or a relative path within the ansible directory
specified via the 1st option.

Note that the option names were chosen this way so that it doesn't conflict
with `pytest-ansible`_ plugin.


Using ansible playbook fixture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The plugin provides a single pytest fixture called ``ansible_playbook``. To
specify playbooks to be executed by the fixture, use the following `pytest
markers`_:

* ``@pytest.mark.ansible_playbook_setup('playbook.yml')``
* ``@pytest.mark.ansible_playbook_teardown('playbook.yml')``

Note that you can list multiple playbooks in the marker if needed, eg.::

    @pytest.mark.ansible_playbook_setup('playbook.01.yml', 'playbook.02.yml')

both playbooks would be executed in the given order.

Here is an example how to specify 2 playbooks to be run during setup phase
of a test case and one for the teardown::

    @pytest.mark.ansible_playbook_setup('setup_foo.yml', 'bar.yml')
    @pytest.mark.ansible_playbook_teardown('teardown_foo.yml')
    def test_foo(ansible_playbook):
        """
        Some testing is done here.
        """

While using markers without ``ansible_playbook`` fixture like this is valid::

    @pytest.mark.ansible_playbook_setup('setup_foo.yml')
    @pytest.mark.ansible_playbook_teardown('teardown_foo.yml')
    def test_foo():
        """
        Some testing is done here.
        """

no playbook would be executed in such case.

Also note that using a marker without any playbook parameter or using the
fixture without any marker is not valid and would cause an error.


Using ansible playbook runner function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Function ``pytest_ansible_playbook.runner`` is a `context manager`_ which can
be used either to create a custom `pytest fixture`_  or to run playbooks within
a test case.

Creating custom fixture this way is useful when you want to:

* define set of setup/teardown playbooks and use it with multiple test cases,
* run setup or teardown playbooks in any fixture `scope`_
  (to overcome the fact that ``ansible_playbook`` has ``fuction`` scope),
* combine run of given setup/teardown playbooks with other non
  ansible setup or teardown steps
  (to overcome the fact that you can't use ``ansible_playbook`` fixture to run
  setup/teardown for another fixture, because `pytest doesn't expect fixtures
  to have markers`_).
* specify that teardown playbooks are skipped when a test case fails

Example of simple custom fixture::

    import pytest
    from pytest_ansible_playbook import runner
    
    @pytest.fixture(scope="session")
    def custom_fixture(request):
        setup_playbooks = ['setup_foo.yml', 'setup_bar.yml']
        teardown_playbooks = ['teardown_foo.yml', 'teardown_bar.yml']
        with runner(request, setup_playbooks, teardown_playbooks):
            # here comes code executed during setup, after running the setup
            # playbooks
            yield
            # here you can place code to be executed during teardown, but
            # before running the teardown playbooks
    
    def test_bar(custom_fixture):
        assert 1 == 1

And here is an example of using the fixture inside a test case directly::

    from pytest_ansible_playbook import runner
    
    def test_foo(request):
        with runner(request, ['setup_foo.yml'], ['teardown_foo.yml']):
            # code here is executed after the setup playbooks, but before the
            # teardown ones
            assert 1 == 1

If you want to avoid running teardown playbook(s) when a test case fails, use
``skip_teardown`` argument of the runner::

    with runner(
            request, teardown_playbooks=['teardown.yml'], skip_teardown=True):
        assert 1 == 0


Contributing
------------

Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `Apache License 2.0`_ license,
"pytest-ansible-playbook-runner" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed
description.

.. _`file an issue`: https://github.com/final-israel/pytest-ansible-playbook-runner/issues
.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest`: http://docs.pytest.org/en/latest/
.. _`pytest fixture`: http://doc.pytest.org/en/latest/fixture.html
.. _`pytest markers`: http://doc.pytest.org/en/latest/example/markers.html
.. _`plugin`: http://doc.pytest.org/en/latest/plugins.html
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
.. _`stable release from PyPI`: https://pypi.org/project/pytest-ansible-playbook-runner/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/
.. _`virtualenvwrapper`: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`pytest-ansible`: https://pypi.python.org/pypi/pytest-ansible
.. _`ansible playbooks`: https://docs.ansible.com/ansible/playbooks.html
.. _`ansible facts`: https://docs.ansible.com/ansible/playbooks_variables.html#information-discovered-from-systems-facts
.. _`ansible inventory`: https://docs.ansible.com/ansible/intro_inventory.html
.. _`Apache License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`context manager`: https://docs.python.org/3.6/library/stdtypes.html#context-manager-types
.. _`scope`: https://docs.pytest.org/en/latest/fixture.html#scope-sharing-a-fixture-instance-across-tests-in-a-class-module-or-session
.. _`pytest doesn't expect fixtures to have markers`: https://github.com/pytest-dev/pytest/issues/3664

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~