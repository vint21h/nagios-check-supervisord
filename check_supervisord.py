#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.py

# Copyright (c) 2015-2020 Alexei Andrushievich <vint21h@vint21h.pp.ua>
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
VERSION = (0, 6, 1)
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
    EXIT_CODE_OK, EXIT_CODE_WARNING, EXIT_CODE_CRITICAL, EXIT_CODE_UNKNOWN = (
        "ok",
        "warning",
        "critical",
        "unknown",
    )
    EXIT_CODES = {
        EXIT_CODE_OK: 0,
        EXIT_CODE_WARNING: 1,
        EXIT_CODE_CRITICAL: 2,
        EXIT_CODE_UNKNOWN: 3,
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
        STATE_STOPPED: EXIT_CODE_OK,
        STATE_RUNNING: EXIT_CODE_OK,
        STATE_STARTING: EXIT_CODE_WARNING,
        STATE_BACKOFF: EXIT_CODE_WARNING,
        STATE_STOPPING: EXIT_CODE_WARNING,
        STATE_EXITED: EXIT_CODE_WARNING,
        STATE_FATAL: EXIT_CODE_CRITICAL,
        STATE_UNKNOWN: EXIT_CODE_UNKNOWN,
    }
    URI_TPL_HTTP, URI_TPL_HTTP_AUTH, URI_TPL_SOCKET = "http", "http-auth", "socket"
    URI_TEMPLATES = {
        URI_TPL_HTTP: "http://{server}:{port}",
        URI_TPL_HTTP_AUTH: "http://{username}:{password}@{server}:{port}",
        URI_TPL_SOCKET: "unix://{server}",
    }

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
            "--stopped-state",
            action="store",
            dest="stopped_state",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.EXIT_CODE_OK,
            metavar="STOPPED_STATE",
            help="stopped state",
        )
        parser.add_argument(
            "--network-errors-exit-code",
            action="store",
            dest="network_errors_exit_code",
            type=str,
            choices=self.EXIT_CODES.keys(),
            default=self.EXIT_CODE_UNKNOWN,
            metavar="NETWORK_ERRORS_EXIT_CODE",
            help="network errors exit code",
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
        self.STATE_TO_TEMPLATE[self.STATE_STOPPED] = options.stopped_state

        # check mandatory command line options supplied
        if not options.server:
            parser.error(message="Required server address option missing")
        if options.username and not options.password:
            parser.error(message="Required supervisord user password missing")

        return options

    def _get_connection_string(self, tpl):
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

    def _get_data(self):
        """
        Get and return data from supervisord.

        :return: data from supervisord
        :rtype: List[Dict[str, Union[str, int]]]
        """

        try:
            if self.options.server.startswith("/") and stat.S_ISSOCK(
                os.stat(self.options.server).st_mode
            ):  # communicate with server via unix socket
                # (check is server address is path and path is unix socket)
                try:
                    import supervisor.xmlrpc
                except ImportError as error:
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
                            serverurl=self._get_connection_string(
                                tpl=self.URI_TPL_SOCKET
                            ),
                        ),
                    )
                else:
                    connection = xmlrpclib.ServerProxy(
                        uri="https://",
                        transport=supervisor.xmlrpc.SupervisorTransport(
                            username=None,
                            password=None,
                            serverurl=self._get_connection_string(
                                tpl=self.URI_TPL_SOCKET
                            ),
                        ),
                    )

            else:  # communicate with server via http
                if all([self.options.username, self.options.password]):  # with auth
                    connection = xmlrpclib.Server(
                        uri=self._get_connection_string(tpl=self.URI_TPL_HTTP_AUTH)
                    )
                else:
                    connection = xmlrpclib.Server(
                        uri=self._get_connection_string(tpl=self.URI_TPL_HTTP)
                    )

            return connection.supervisor.getAllProcessInfo()

        except Exception as error:
            if not self.options.quiet:
                sys.stdout.write(
                    "ERROR: Server communication problem. {error}\n".format(error=error)
                )
            sys.exit(
                self.EXIT_CODES.get(
                    self.options.network_errors_exit_code, self.EXIT_CODE_UNKNOWN
                )
            )

    def _get_output(self, data):
        """
        Create Nagios and human readable supervisord statuses.

        :param data: supervisord XML-RPC call result
        :type data: List[Dict[str, Union[str, int]]]
        :return: Nagios and human readable supervisord statuses and exit code
        :rtype: Tuple[str, int]
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

        # getting main status for check
        # (for multiple check need to get main status by priority)
        statuses = [
            status[0]
            for status in sorted(
                [
                    (status, self.OUTPUT_TEMPLATES[status]["priority"])
                    for status in list(
                        set([states[program]["template"] for program in states.keys()])
                    )
                ],
                key=lambda item: item[1],  # type: ignore
            )
        ]
        # if no programs found or configured by supervisord
        # set status ok and custom message
        status = statuses[0] if statuses else self.EXIT_CODE_OK
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
            if statuses
            else "No program configured/found"
        )

        # create exit code (unknown if something happened wrong)
        code = self.EXIT_CODES.get(status, self.EXIT_CODE_UNKNOWN)

        # return full status string with main status
        # for multiple programs and all programs states
        return (
            "{status}: {output}\n".format(
                **{"status": status.upper(), "output": output}
            ),
            code,
        )

    def check(self):
        """
        Get data from server and create plugin output.

        :return: plugin output and exit code
        :rtype: Tuple[str, int]
        """

        data = self._get_data()  # type: ignore

        return self._get_output(data=data)  # type: ignore


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
