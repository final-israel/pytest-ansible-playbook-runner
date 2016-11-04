#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-ansible-playbook',
    version='0.3.0',
    author='Martin Bukatovič',
    author_email='mbukatov@redhat.com',
    maintainer='Martin Bukatovič',
    maintainer_email='mbukatov@redhat.com',
    license='Apache 2.0',
    url='https://gitlab.com/mbukatov/pytest-ansible-playbook',
    description='Pytest fixture which runs given ansible playbook file.',
    long_description=read('README.rst'),
    py_modules=['pytest_ansible_playbook'],
    install_requires=['pytest>=2.9.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Operating System :: POSIX',
    ],
    entry_points={
        'pytest11': [
            'ansible-playbook = pytest_ansible_playbook',
        ],
    },
)
