#!/usr/bin/env python
# -*- coding: utf-8 -*-

# nagios-check-supervisord
# setup.py


from setuptools import setup, find_packages


# metadata
VERSION = (0, 6, 1)
__version__ = ".".join(map(str, VERSION))

DATA = [
    "README.rst",
    "COPYING",
    "AUTHORS",
]

setup(
    name="nagios-check-supervisord",
    version=__version__,
    packages=find_packages(exclude=["tests.*", "tests"]),
    scripts=["check_supervisord.py"],
    package_data={"nagios-check-supervisord": DATA},
    data_files=[("share/doc/nagios-check-supervisord/", DATA)],
    author="Alexei Andrushievich",
    author_email="vint21h@vint21h.pp.ua",
    description="Check supervisord programs status Nagios plugin",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    license="GPLv3+",
    license_file="COPYING",
    url="https://github.com/vint21h/nagios-check-supervisord/",
    download_url="https://github.com/vint21h/nagios-check-supervisord/archive/{version}.tar.gz".format(  # noqa: E501
        version=__version__
    ),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=2.7",
    test_suite="tests",
    keywords=[
        "nagios",
        "supervisord",
        "check-supervisord",
        "plugin",
        "check-supervisord-plugin",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
    ],
    extras_require={
        "unix-socket-support": ["supervisor"],
        "test": [
            "bandit==1.6.2",
            "black==19.10b0",
            "check-manifest==0.42",
            "contextlib2==0.6.0.post1",
            "coverage==5.1",
            "coveralls==2.0.0",
            "dodgy==0.2.1",
            "flake8-annotations-complexity==0.0.4",
            "flake8-bugbear==20.1.4",
            "flake8-docstrings==1.5.0",
            "flake8-mypy==17.8.0",
            "flake8==3.7.9",
            "interrogate==1.2.0",
            "isort[pipfile]==4.3.21",
            "mypy==0.770",
            "pep8-naming==0.10.0",
            "pre-commit-hooks==2.5.0",
            "pre-commit==2.3.0",
            "pygments==2.6.1",
            "pylint==2.5.2",
            "pyroma==2.6",
            "pytest-cov==2.8.1",
            "pytest-mock==3.1.0",
            "pytest-tldr==0.2.1",
            "pytest==5.4.2",
            "readme_renderer==26.0",
            "removestar==1.2.2",
            "seed-isort-config==2.1.1",
            "tox-pyenv==1.1.0",
            "tox-travis==0.12",
            "tox==3.15.0",
            "twine==3.1.1",
        ],
        "test-old-python": [
            "check-manifest==0.41",
            "contextlib2==0.6.0.post1",
            "coverage==5.1",
            "coveralls==1.11.1",
            "pygments==2.5.2",
            "pytest-cov==2.8.1",
            "pytest-mock==2.0.0",
            "pytest-tldr==0.2.1",
            "pytest==4.6.9",
            "readme_renderer==26.0",
            "tox-pyenv==1.1.0",
            "tox-travis==0.12",
            "tox==3.15.0",
            "twine==1.15.0",
        ],
    },
)
