#!/usr/bin/env python
# -*- coding: utf-8 -*-

# nagios-check-supervisord
# setup.py

from setuptools import setup, find_packages

# metadata
VERSION = (0, 1, 4)
__version__ = '.'.join(map(str, VERSION))

DATA = ['README.rst', 'COPYING', ]

setup(
    name="nagios-check-supervisord",
    version=__version__,
    packages=find_packages(),
    scripts=['check_supervisord.py', ],
    install_requires=[],
    package_data={
        'nagios-check-supervisord': DATA,
    },
    data_files=[
        ('share/doc/nagios-check-supervisord/', DATA),
    ],
    author="Alexei Andrushievich",
    author_email="vint21h@vint21h.pp.ua",
    description="Check supervisord programs status Nagios plugin",
    long_description=open('README.rst').read(),
    license="GPLv3 or later",
    url="https://github.com/vint21h/nagios-check-supervisord",
    download_url="https://github.com/vint21h/nagios-check-supervisord/archive/%s.tar.gz" % __version__,
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ]
)
