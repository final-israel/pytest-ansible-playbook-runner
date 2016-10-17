pytest-ansible-playbook
===================================

.. image:: https://travis-ci.org/mbukatov/pytest-ansible-playbook.svg?branch=master
    :target: https://travis-ci.org/mbukatov/pytest-ansible-playbook
    :alt: See Build Status on Travis CI

This repository contains `pytest`_ `plugin`_ which provides an easy way
to generate fixtures for running particular `ansible playbooks`_, so that you
can run full playbook during setup phase of a test case. This is useful when
you already have playbook files you would like to reuse during test setup or
plan to maintain test setup in ansible playbooks for you to be able to
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

* Generate `pytest fixtures`_ for given ansible playbook yaml files so that
  you can quickly run a ansible playbook during setup of a test case.

* Compatible with both python2 and python3 (playbooks are executed via
  running ``ansible-playbook`` in subprocess instead of using api
  of ansible python module).

* Doesn't allow you to configure ansible in any way, all changes of ansible
  setup needs to be done in ansible playbooks, variable or config files.
  This encourages you to maintain a clear separation of ansible playbooks
  and the tests.

Note that if you need to run particular ansible tasks with more control and
full details about the result, use `pytest-ansible`_ plugin instead.


Requirements
------------

Ansible should be installed (so that ``ansible-playbook`` binary is
available in PATH). Use version provided by packaging system of your operation
system.


Installation
------------

There is no stable release yet, so the only option is to use latest
sources from master branch.

Latest development version
~~~~~~~~~~~~~~~~~~~~~~~~~~

The suggested way to install from sources of current master branch is
via `python virtual enviroment`_::

    $ cd pytest-ansible-playbook
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -e .

Note that you can use `virtualenvwrapper`_ to simplify this workflow.

.. TODO: uncomment the following when the 1st release is done
.. Stable
.. ~~~~~~

.. You can install "pytest-ansible-playbook" via `pip`_ from `PyPI`_::

..     $ pip install pytest-ansible-playbook


Usage
-----

When the plugin is installed, you can use the following command-line
parameters::

    py.test \
        [--ansible-playbook-directory <path_to_directory_with_playbooks>] \
        [--ansible-playbook-inventory <path_to_inventory_file>]

Where ``<path_to_directory_with_playbooks>`` is a directory which contains
ansible playbooks yaml files and optionally other ansible files such as
configuration or roles, while ``<path_to_inventory_file>`` is file with
`ansible inventory`_.

Note that the option names were chosen this way so that it doesn't conflict
with `pytest-ansible`_ plugin.


Contributing
------------

Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.


License
-------

Distributed under the terms of the `GNU GPL v3.0`_ license,
"pytest-ansible-playbook" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed
description.

.. _`file an issue`: TODO
.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest`: http://docs.pytest.org/en/latest/
.. _`pytest fixtures`: http://doc.pytest.org/en/latest/fixture.html
.. _`plugin`: http://doc.pytest.org/en/latest/plugins.html
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.python.org/pypi/pip/
.. _`PyPI`: https://pypi.python.org/pypi
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/
.. _`virtualenvwrapper`: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`pytest-ansible`: https://pypi.python.org/pypi/pytest-ansible
.. _`ansible playbooks`: https://docs.ansible.com/ansible/playbooks.html
.. _`ansible facts`: https://docs.ansible.com/ansible/playbooks_variables.html#information-discovered-from-systems-facts
.. _`ansible inventory`: https://docs.ansible.com/ansible/intro_inventory.html
