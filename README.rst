.. nagios-check-supervisord
.. README.rst

A nagios-check-supervisord documentation
========================================

|GitHub|_ |Coveralls|_ |pypi-license|_ |pypi-version|_ |pypi-python-version|_ |pypi-format|_ |pypi-wheel|_ |pypi-status|_

    *nagios-check-supervisord is a Nagios-plugin that check supervisord (http://supervisord.org/) programs status*

.. contents::

Installation
------------
* Obtain your copy of source code from the git repository: ``$ git clone https://github.com/vint21h/nagios-check-supervisord.git``. Or download the latest release from https://github.com/vint21h/nagios-check-supervisord/tags/.
* Run ``$ python ./setup.py install`` from the repository source tree or unpacked archive. Or use pip: ``$ pip install nagios-check-supervisord``.

Configuration
-------------
* Read and understand Nagios documentation.
* Create Nagios command and service definitions like this:

.. code-block::

    # "check_supervisord" command
    define command
    {
        command_name check_supervisord
        command_line $USER1$/check_supervisord -s $ARG1$ -p $ARG2$ -P $ARG3$ -u $ARG4$ -S $ARG5$
    }

    # "check_supervisord" service for "myprog" program
    define service
    {
        use                 local-service
        host_name           localhost
        service_description My program state
        check_command       check_supervisord!127.0.0.1!9001!myprog!username!password
    }

Without ``--programs`` option script check all programs from supervisord response and return priority-based global status:

* critical
* warning
* unknown
* ok

Also, ``--programs`` option can take a comma-separated list of programs to check.

``--stopped-state-exit-code`` option allows set Nagios status for stopped programs.

``--starting-state-exit-code`` option allows set Nagios status for starting programs.

``--network-errors-exit-code`` option allows set Nagios status for checks network errors.

``--no-programs-defined-exit-code`` option allows set Nagios status for not configured/found programs in supervisord response.

nagios-check-supervisord support connection to supervisord XML-RPC interface through HTTP and Unix Domain Socket.
To install nagios-check-supervisord with Unix Domain Socket: ``$ pip install nagios-check-supervisord[unix-socket-support]``

Licensing
---------
nagios-check-supervisord is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
For complete license text see COPYING file.

Contacts
--------
**Project Website**: https://github.com/vint21h/nagios-check-supervisord/

**Author**: Alexei Andrushievich <vint21h@vint21h.pp.ua>

For other authors list see AUTHORS file.


.. |GitHub| image:: https://github.com/vint21h/nagios-check-supervisord/workflows/build/badge.svg
    :alt: GitHub
.. |Coveralls| image:: https://coveralls.io/repos/github/vint21h/nagios-check-supervisord/badge.svg?branch=master
    :alt: Coveralls
.. |pypi-license| image:: https://img.shields.io/pypi/l/nagios-check-supervisord
    :alt: License
.. |pypi-version| image:: https://img.shields.io/pypi/v/nagios-check-supervisord
    :alt: Version
.. |pypi-python-version| image:: https://img.shields.io/pypi/pyversions/nagios-check-supervisord
    :alt: Supported Python version
.. |pypi-format| image:: https://img.shields.io/pypi/format/nagios-check-supervisord
    :alt: Package format
.. |pypi-wheel| image:: https://img.shields.io/pypi/wheel/nagios-check-supervisord
    :alt: Python wheel support
.. |pypi-status| image:: https://img.shields.io/pypi/status/nagios-check-supervisord
    :alt: Package status
.. _GitHub: https://github.com/vint21h/nagios-check-supervisord/actions/
.. _Coveralls: https://coveralls.io/github/vint21h/nagios-check-supervisord?branch=master
.. _pypi-license: https://pypi.org/project/nagios-check-supervisord/
.. _pypi-version: https://pypi.org/project/nagios-check-supervisord/
.. _pypi-python-version: https://pypi.org/project/nagios-check-supervisord/
.. _pypi-format: https://pypi.org/project/nagios-check-supervisord/
.. _pypi-wheel: https://pypi.org/project/nagios-check-supervisord/
.. _pypi-status: https://pypi.org/project/nagios-check-supervisord/
