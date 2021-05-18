#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.py

# Copyright (c) 2015-2021 Alexei Andrushievich <vint21h@vint21h.pp.ua>
# Check supervisord programs status Nagios plugin [https://github.com/vint21h/nagios-check-supervisord/]  # noqa: E501
#
# This file is part of nagios-check-supervisord.
#
# nagios-check-supervisord is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals

import os
import sys
import stat
from collections import OrderedDict
from argparse import Namespace, ArgumentParser  # pylint: disable=W0611  # noqa: F401


try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib  # type: ignore


__all__ = [
    "main",
    "CheckSupervisord",
]


# metadata
VERSION = (2, 2, 0)
__version__ = ".".join(map(str, VERSION))


class CheckSupervisord(object):
    """
    Check supervisord programs status Nagios plugin.
    """

    OUTPUT_TEMPLATES = {
        "critical": {"text": "problem with '{name}': ({status})", "priority": 1},
        "warning": {
            "text": "something curiously with '{name}': ({status})",
            "priority": 2,
        },
        "unknown": {"text": "'{name}' not found in server response", "priority": 3},
        "ok": {"text": "'{name}': OK", "priority": 4},
    }
    STATUS_CRITICAL, STATUS_WARNING, STATUS_UNKNOWN, STATUS_OK = [
        "critical",
        "warning",
        "unknown",
        "ok",
    ]
    EXIT_CODES = {
        STATUS_OK: 0,
        STATUS_WARNING: 1,
        STATUS_CRITICAL: 2,
        STATUS_UNKNOWN: 3,
    }
    (
        STATE_STOPPED,
        STATE_RUNNING,
        STATE_STARTING,
        STATE_BACKOFF,
        STATE_STOPPING,
        STATE_EXITED,
        STATE_FATAL,
        STATE_UNKNOWN,
    ) = (
        "STOPPED",
        "RUNNING",
        "STARTING",
        "BACKOFF",
        "STOPPING",
        "EXITED",
        "FATAL",
        "UNKNOWN",
    )
    STATE_TO_TEMPLATE = {
        STATE_STOPPED: STATUS_OK,
        STATE_RUNNING: STATUS_OK,
        STATE_STARTING: STATUS_WARNING,
        STATE_BACKOFF: STATUS_WARNING,
        STATE_STOPPING: STATUS_WARNING,
        STATE_EXITED: STATUS_WARNING,
        STATE_FATAL: STATUS_CRITICAL,
        STATE_UNKNOWN: STATUS_UNKNOWN,
    }
    URI_TPL_HTTP, URI_TPL_HTTP_AUTH, URI_TPL_SOCKET = "http", "http-auth", "socket"
    URI_TEMPLATES = {
        URI_TPL_HTTP: "http://{server}:{port}",
        URI_TPL_HTTP_AUTH: "http://{username}:{password}@{server}:{port}",
        URI_TPL_SOCKET: "unix://{server}",
    }
    (
        PRIORITY_CRITICAL,
        PRIORITY_WARNING,
        PRIORITY_UNKNOWN,
        PRIORITY_OK,
    ) = range(1, 5)
    PRIORITY_TO_STATUS = {
        PRIORITY_CRITICAL: STATUS_CRITICAL,
        PRIORITY_WARNING: STATUS_WARNING,
        PRIORITY_UNKNOWN: STATUS_UNKNOWN,
        PRIORITY_OK: STATUS_OK,
    }
    STATUS_TO_PRIORITY = {
        STATUS_CRITICAL: PRIORITY_CRITICAL,
        STATUS_WARNING: PRIORITY_WARNING,
        STATUS_UNKNOWN: PRIORITY_UNKNOWN,
        STATUS_OK: PRIORITY_OK,
    }
    HELP_STATUSES = "Possible variants: {statuses}".format(
        statuses=", ".join(EXIT_CODES.keys())
    )

    def __init__(self):
        """
        Get command line args.
        """

        self.options = self._get_options()  # type: ignore

    def _get_options(self):
        """
        Parse commandline options arguments.

        :return: parsed command line arguments
        :rtype: Namespace
        """

        parser = ArgumentParser(
            description="Check supervisord programs status Nagios plugin"
        )
        parser.add_argument(
            "-s",
            "--server",
            action="store",
            dest="server",
            type=str,
            default="",
            metavar="SERVER",
            help="server name, IP address or unix socket path",
        )
        parser.add_argument(
            "-p",
            "--port",
            action="store",
            type=int,
            dest="port",
            default=9001,
            metavar="PORT",
            help="port number",
        )
        parser.add_argument(
            "-P",
            "--programs",
            action="store",
            dest="programs",
            type=str,
            default="",
            metavar="PROGRAMS",
            help="comma separated programs list, or empty for all programs in supervisord response",  # noqa: E501
        )
        parser.add_argument(
            "-u",
            "--username",
            action="store",
            dest="username",
            type=str,
            default="",
            metavar="USERNAME",
            help="supervisord user",
        )
        parser.add_argument(
            "-S",
            "--password",
            action="store",
            dest="password",
            type=str,
            default="",
            metavar="PASSWORD",
            help="supervisord user password",
        )
        parser.add_argument(
            "--stopped-state-exit-code",
            action="store",
            dest="stopped_state_exit_code",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.STATUS_OK,
            metavar="STOPPED_STATE_EXIT_CODE",
            help="stopped state exit code. {statuses}".format(
                statuses=self.HELP_STATUSES
            ),
        )
        parser.add_argument(
            "--starting-state-exit-code",
            action="store",
            dest="starting_state_exit_code",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.STATUS_WARNING,
            metavar="STARTING_STATE_EXIT_CODE",
            help="starting state exit code. {statuses}".format(
                statuses=self.HELP_STATUSES
            ),
        )
        parser.add_argument(
            "--network-errors-exit-code",
            action="store",
            dest="network_errors_exit_code",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.STATUS_UNKNOWN,
            metavar="NETWORK_ERRORS_EXIT_CODE",
            help="network errors exit code. {statuses}".format(
                statuses=self.HELP_STATUSES
            ),
        )
        parser.add_argument(
            "--no-programs-defined-exit-code",
            action="store",
            dest="no_programs_defined_exit_code",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.STATUS_UNKNOWN,
            metavar="NO_PROGRAMS_DEFINED_EXIT_CODE",
            help="no programs defined exit code. {statuses}".format(
                statuses=self.HELP_STATUSES
            ),
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            default=False,
            dest="quiet",
            help="be quiet",
        )
        parser.add_argument(
            "-v",
            "--version",
            action="version",
            version="{version}".format(version=__version__),
        )

        options = parser.parse_args()
        # update stopped state value from command line argument
        self.STATE_TO_TEMPLATE[self.STATE_STOPPED] = options.stopped_state_exit_code
        # update starting state value from command line argument
        self.STATE_TO_TEMPLATE[self.STATE_STARTING] = options.starting_state_exit_code

        # check mandatory command line options supplied
        if not options.server:
            parser.error(message="Required server address option missing")
        if options.username and not options.password:
            parser.error(message="Required supervisord user password missing")

        return options

    def _get_connection_uri(self, tpl):
        """
        Creates server connection URI formatted connection string.

        :param tpl: connection string template name
        :type tpl: str
        :return: server connection URI formatted connection string
        :rtype: str
        """

        payload = {
            "username": self.options.username,
            "password": self.options.password,
            "server": self.options.server,
            "port": self.options.port,
        }

        return self.URI_TEMPLATES[tpl].format(**payload)

    def _get_connection(self):
        """
        Creates and return connection to supervisord.

        :return: connection to supervisord
        :rtype: ServerProxy
        """

        if self.options.server.startswith("/") and stat.S_ISSOCK(
            os.stat(self.options.server).st_mode
        ):  # communicate with server via unix socket
            # (check is server address is path and path is unix socket)
            try:
                import supervisor.xmlrpc
            except ImportError as error:  # noqa: B014
                sys.stdout.write(
                    "ERROR: Couldn't load module. {error}\n".format(error=error)
                )
                sys.stdout.write(
                    "ERROR: Unix socket support not available! Please install nagios-check-supervisord with unix socket support: 'nagios-check-supervisord[unix-socket-support]' or install 'supervisor' separately.\n"  # noqa: E501
                )
                sys.exit(3)

            if all([self.options.username, self.options.password]):  # with auth
                connection = xmlrpclib.ServerProxy(
                    uri="https://",
                    transport=supervisor.xmlrpc.SupervisorTransport(
                        self.options.username,
                        self.options.password,
                        serverurl=self._get_connection_uri(tpl=self.URI_TPL_SOCKET),  # type: ignore  # noqa: E501
                    ),
                )
            else:
                connection = xmlrpclib.ServerProxy(
                    uri="https://",
                    transport=supervisor.xmlrpc.SupervisorTransport(
                        username=None,
                        password=None,
                        serverurl=self._get_connection_uri(tpl=self.URI_TPL_SOCKET),  # type: ignore  # noqa: E501
                    ),
                )

        else:  # communicate with server via http
            if all([self.options.username, self.options.password]):  # with auth
                connection = xmlrpclib.Server(
                    uri=self._get_connection_uri(tpl=self.URI_TPL_HTTP_AUTH)  # type: ignore  # noqa: E501
                )
            else:
                connection = xmlrpclib.Server(
                    uri=self._get_connection_uri(tpl=self.URI_TPL_HTTP)  # type: ignore  # noqa: E501
                )

        return connection

    def _get_data(self):
        """
        Get and return data from supervisord.

        :return: data from supervisord
        :rtype: List[Dict[str, Union[str, int]]]
        """

        try:
            connection = self._get_connection()  # type: ignore  # noqa: E501

            return connection.supervisor.getAllProcessInfo()

        except Exception as error:
            if not self.options.quiet:
                sys.stdout.write(
                    "ERROR: Server communication problem. {error}\n".format(error=error)
                )
            sys.exit(
                self.EXIT_CODES.get(
                    self.options.network_errors_exit_code, self.STATUS_UNKNOWN
                )
            )

    def _get_status(self, data):
        """
        Create main status.

        :param data: devices states info
        :type data: List[Dict[str, Union[str, int]]]
        :return: main check status
        :rtype: str
        """

        # for multiple check need to get main status by priority
        priority = (
            min(  # type: ignore  # noqa: C407
                [
                    self.OUTPUT_TEMPLATES[self.STATE_TO_TEMPLATE[info["statename"]]][
                        "priority"
                    ]
                    for info in data
                ]
            )
            if data
            else self.STATUS_TO_PRIORITY[self.options.no_programs_defined_exit_code]
        )
        status = self.PRIORITY_TO_STATUS.get(priority, self.PRIORITY_CRITICAL)  # type: ignore  # noqa: E501

        return status

    def _get_code(self, status):
        """
        Create exit code.

        :param status: main check status
        :type status: str
        :return: exit code
        :rtype: int
        """

        # create exit code (unknown if something happened wrong)
        return self.EXIT_CODES.get(status, self.STATUS_UNKNOWN)

    def _get_output(self, data, status):
        """
        Create Nagios and human readable supervisord statuses.

        :param data: supervisord XML-RPC call result
        :type data: List[Dict[str, Union[str, int]]]
        :param status: main check status
        :type status: str
        :return: human readable supervisord statuses
        :rtype: str
        """

        states = OrderedDict()
        programs = (
            map(
                lambda program: program.strip(),
                self.options.programs.strip().split(","),
            )
            if self.options.programs
            else map(lambda x: x["name"], data)
        )

        for program in programs:
            try:
                info = min(filter(lambda x: x["name"] == program, data))
                states.update(
                    {
                        program: {
                            "name": program,
                            "template": self.STATE_TO_TEMPLATE[info["statename"]],
                            "status": info["spawnerr"]
                            if info["spawnerr"]
                            else info["statename"],
                        }
                    }
                )
            except ValueError:
                states.update(
                    {program: {"name": program, "template": "unknown", "status": ""}}
                )

        output = (
            ", ".join(
                [
                    str(
                        self.OUTPUT_TEMPLATES[states[program]["template"]]["text"]
                    ).format(**states[program])
                    for program in sorted(
                        states.keys(),
                        key=lambda item: self.OUTPUT_TEMPLATES[  # type: ignore
                            states[item]["template"]
                        ]["priority"],
                    )
                ]
            )
            if len(states)
            else "No program configured/found"
        )

        # return full status string with main status
        # for multiple programs and all programs states
        return "{status}: {output}\n".format(
            **{"status": status.upper(), "output": output}
        )

    def check(self):
        """
        Get data from server and create plugin output.

        :return: plugin output and exit code
        :rtype: Tuple[str, int]
        """

        data = self._get_data()  # type: ignore
        status = self._get_status(data=data)  # type: ignore
        code = self._get_code(status=status)  # type: ignore

        return self._get_output(data=data, status=status), code  # type: ignore


def main():
    """
    Program main.
    """

    checker = CheckSupervisord()  # type: ignore
    output, code = checker.check()  # type: ignore
    sys.stdout.write(output)
    sys.exit(code)


if __name__ == "__main__":

    main()  # type: ignore
