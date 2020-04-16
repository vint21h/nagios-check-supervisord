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

from argparse import ArgumentParser
import os
import stat
import sys


try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib


__all__ = [
    "main",
]


# metadata
VERSION = (0, 6, 1)
__version__ = ".".join(map(str, VERSION))

# global variables
OUTPUT_TEMPLATES = {
    "critical": {"text": "problem with '{name}': ({status})", "priority": 1},
    "warning": {
        "text": "something curiously with '{name}': ({status})",
        "priority": 2,
    },
    "unknown": {"text": "'{name}' not found in server response", "priority": 3},
    "ok": {"text": "'{name}': OK", "priority": 4},
}
# exit codes
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
# programs states
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
# server connection URI's
URI_TPL_HTTP, URI_TPL_HTTP_AUTH, URI_TPL_SOCKET = "http", "http-auth", "socket"
URI_TEMPLATES = {
    URI_TPL_HTTP: "http://{server}:{port}",
    URI_TPL_HTTP_AUTH: "http://{username}:{password}@{server}:{port}",
    URI_TPL_SOCKET: "unix://{server}",
}


def _get_options():
    """
    Parse commandline options arguments.

    :return: parsed command line arguments
    :rtype: Namespace
    """

    parser = ArgumentParser(description="Check supervisord programs status Nagios plugin")
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
        "-q",
        "--quiet",
        metavar="QUIET",
        action="store_true",
        default=False,
        dest="quiet",
        help="be quiet",
    )
    parser.add_argument(
        "--stopped-state",
        action="store",
        dest="stopped_state",
        type=str,
        choices=EXIT_CODES.keys(),
        default=EXIT_CODE_OK,
        metavar="STOPPED_STATE",
        help="stopped state",
    )
    parser.add_argument(
        "--network-errors-exit-code",
        action="store",
        dest="network_errors_exit_code",
        type=str,
        choices=EXIT_CODES.keys(),
        default=EXIT_CODE_UNKNOWN,
        metavar="NETWORK_ERRORS_EXIT_CODE",
        help="network errors exit code",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="{version}".format(**{"version": __version__}),
    )

    options = parser.parse_args()
    # update stopped state value from command line argument
    STATE_TO_TEMPLATE[
        STATE_STOPPED
    ] = options.stopped_state

    # check mandatory command line options supplied
    if not options.server:
        parser.error("Required server address option missing")
    if options.username and not options.password:
        parser.error("Required supervisord user password")

    return options


def _get_data(options):
    """
    Get and return data from supervisord.

    :return: data from supervisord
    :rtype: Dict[]
    """

    payload = {  # server connection URI formatted string payload
        "username": options.username,
        "password": options.password,
        "server": options.server,
        "port": options.port,
    }

    try:
        if options.server.startswith("/") and stat.S_ISSOCK(
            os.stat(options.server).st_mode
        ):  # communicate with server via unix socket
            # (simple check is server address is path and path is unix socket)
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

            if all([options.username, options.password]):  # with auth
                connection = xmlrpclib.ServerProxy(
                    "https://",
                    transport=supervisor.xmlrpc.SupervisorTransport(
                        options.username,
                        options.password,
                        serverurl=URI_TEMPLATES[URI_TPL_SOCKET].format(**payload),
                    ),
                )
            else:
                connection = xmlrpclib.ServerProxy(
                    "https://",
                    transport=supervisor.xmlrpc.SupervisorTransport(
                        None, None, serverurl=URI_TEMPLATES[URI_TPL_SOCKET].format(**payload)
                    ),
                )

        else:  # communicate with server via http
            if all([options.username, options.password]):  # with auth
                connection = xmlrpclib.Server(URI_TEMPLATES[URI_TPL_HTTP_AUTH].format(**payload))
            else:
                connection = xmlrpclib.Server(URI_TEMPLATES[URI_TPL_HTTP].format(**payload))

        return connection.supervisor.getAllProcessInfo()

    except Exception as error:
        if not options.quiet:
            sys.stdout.write(
                "ERROR: Server communication problem. {error}\n".format(error=error)
            )
        sys.exit(EXIT_CODES.get(options.network_errors_exit_code, EXIT_CODE_UNKNOWN))


def _get_output(data, options):
    """
    Create Nagios and human readable supervisord statuses.

    :param data: supervisord XML-RPC call result
    :type data: Dict[]
    :return: Nagios and human readable supervisord statuses and exit code
    :rtype: Tuple[str, int]
    """

    output = {}
    programs = (
        map(lambda program: program.strip(), options.programs.strip().split(","))
        if options.programs
        else map(lambda x: x["name"], data)
    )

    for program in programs:
        try:
            program_data = filter(lambda x: x["name"] == program, data)[0]
            output.update(
                {
                    program: {
                        "name": program,
                        "template": STATE_TO_TEMPLATE[program_data["statename"]],
                        "status": program_data["spawnerr"]
                        if program_data["spawnerr"]
                        else program_data["statename"],
                    }
                }
            )
        except IndexError:
            output.update(
                {program: {"name": program, "template": "unknown", "status": ""}}
            )

    # getting main status for check
    # (for multiple check need to get main status by priority)
    statuses = [
        status[0]
        for status in sorted(
            [
                (status, OUTPUT_TEMPLATES[status]["priority"])
                for status in list(set([output[d]["template"] for d in output.keys()]))
            ],
            key=lambda x: x[1],
        )
    ]
    # if no programs found or configured by supervisord set status ok and custom message
    status = statuses[0] if statuses else EXIT_CODE_OK
    text = (
        ", ".join(
            [
                OUTPUT_TEMPLATES[output[program]["template"]]["text"].format(
                    **output[program]
                )
                for program in sorted(
                    output.keys(),
                    key=lambda x: OUTPUT_TEMPLATES[output[x]["template"]]["priority"],
                )
            ]
        )
        if statuses
        else "No program configured/found"
    )

    # create exit code (unknown if something happened wrong)
    code = EXIT_CODES.get(status, EXIT_CODE_UNKNOWN)

    # return full status string with main status
    # for multiple programs and all programs states
    return (
        "{status}: {output}\n".format(**{"status": status.upper(), "output": text}),
        code,
    )


def main():
    """
    Program main.
    """

    options = _get_options()
    output, code = _get_output(data=_get_data(options=options), options=options)
    sys.stdout.write(output)
    sys.exit(code)


if __name__ == "__main__":

    main()
