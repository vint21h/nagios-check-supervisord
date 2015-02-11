.. nagios-check-supervisord
.. README.rst

A nagios-check-supervisord documentation
========================================

    *nagios-check-supervisord is a Nagios-plugin that check supervisord (http://supervisord.org/) programs status*

.. contents::

Installation
------------
* Obtain your copy of source code from git repository: ``git clone https://github.com/vint21h/nagios-check-supervisord.git``. Or download latest release from https://github.com/vint21h/nagios-check-supervisord/tags.
* Run ``python ./setup.py install`` from repository source tree or unpacked archive under root user. Or use pip: ``pip install nagios-check-supervisord``.

Configuration
-------------
* Read and understand Nagios documentation.
* Create Nagios command and service definitions like this:

::

    # 'check_supervisord' command
        define command
        {
            command_name check_supervisord
            command_line /usr/bin/check_supervisord.py -s $ARG1$ -p $ARG2$ -P $ARG3$ -u $ARG4$ -s $ARG4$
        }

    # 'check_supervisord' service for 'myapp' program
    define service
    {
        use                 local-service
        host_name           localhost
        service_description My app state
        check_command       check_supervisord!127.0.0.1!9001!myapp!username!password
    }

Without ``--programs`` option script check all programs from supervisord response and return priority based global status:

* critical
* warning
* unknown
* ok

Also, ``--programs`` option can take comma separated list of programs to check.


Licensing
---------
nagios-check-supervisord is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
For complete license text see COPYING file.


Contacts
--------
**Project Website**: https://github.com/vint21h/nagios-check-supervisord

**Author**: Alexei Andrushievich <vint21h@vint21h.pp.ua>