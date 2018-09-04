pytest-ansible-playbook
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

* The plugin provides ``ansible_playbook`` `pytest fixture`_, which allows
  one to run one or more ansible playbooks during test setup or tear down.

* It's compatible with both python2 and python3 (playbooks are executed via
  running ``ansible-playbook`` in subprocess instead of using api
  of ansible python module).

* Doesn't allow you to configure ansible in any way, all changes of ansible
  setup needs to be done in ansible playbooks, variable or config files.
  This encourages you to maintain a clear separation of ansible playbooks
  and the tests.


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

You can install "pytest-ansible-playbook" via `pip`_ from `PyPI`_::

    $ pip install pytest-ansible-playbook


Installing latest development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The suggested way to install from sources of current master branch is
via `python virtual enviroment`_::

    $ cd pytest-ansible-playbook
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


Contributing
------------

Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `Apache License 2.0`_ license,
"pytest-ansible-playbook" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed
description.

.. _`file an issue`: https://gitlab.com/mbukatov/pytest-ansible-playbook/issues
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
.. _`stable release from PyPI`: https://pypi.org/project/pytest-ansible-playbook/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/
.. _`virtualenvwrapper`: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`pytest-ansible`: https://pypi.python.org/pypi/pytest-ansible
.. _`ansible playbooks`: https://docs.ansible.com/ansible/playbooks.html
.. _`ansible facts`: https://docs.ansible.com/ansible/playbooks_variables.html#information-discovered-from-systems-facts
.. _`ansible inventory`: https://docs.ansible.com/ansible/intro_inventory.html
.. _`Apache License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
