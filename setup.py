#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup
import version

def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-ansible-playbook-runner',
    version=version.version,
    author='Martin Bukatovič',
    author_email='mbukatov@redhat.com',
    maintainer='Pavel Rogovoy',
    maintainer_email='pavelr@final.co.il',
    license='Apache 2.0',
    url='https://github.com/final-israel/pytest-ansible-playbook-runner',
    description='Pytest fixture which runs given ansible playbook file.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['pytest_ansible_playbook'],
    install_requires=['pytest>=3.1.0', 'playbook_runner>=0.1.5'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
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
