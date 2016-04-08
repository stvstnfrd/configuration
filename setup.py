#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


_version = '1.0.0'
with open('README.md') as file_input:
    readme = file_input.read()


setup(
    # Metadata
    name='openedx-configuration',
    version=_version,
    license='AGPL-3.0',
    description='TODO: Short description',
    long_description=readme,
    author='stv',
    author_email='stv@stanford.edu',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
    ],
    # URLs
    url='https://github.com/Stanford-Online/configuration',
    # Packages
    # packages=find_packages('src'),
    # include_package_data=True,
    # package_dir={
        # '': 'src',
        # 'openedx_configuration': 'src/openedx_configuration',
    # },
    dependency_links=[
        'http://github.com/edx/ansible/tarball/stable-1.9.3-rc1-edx#egg=ansible-1.9.3-edx',
    ],
    install_requires=[
        'ansible==1.9.3-edx',
        'awscli==1.4.2',
        'boto==2.32.1',
        'docopt==0.6.1',
        'ecdsa==0.11',
        'Jinja2==2.7.3',
        'MarkupSafe==0.23',
        'paramiko==1.15.1',
        'prettytable==0.7.2',
        'pycrypto==2.6.1',
        'python-simple-hipchat==0.2',
        'PyYAML==3.11',
        'requests',
        'wsgiref==0.1.2',
    ],
    tests_require=[
    ],
    cmdclass={
        # 'test': Tox,
    },
    scripts=[
        'bin/provision-sandbox',
        'bin/provision-sandbox-infrastructure',
    ],
)
