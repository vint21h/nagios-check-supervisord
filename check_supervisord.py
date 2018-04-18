#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.py

# Copyright (c) 2015-2018 Alexei Andrushievich <vint21h@vint21h.pp.ua>
# Check supervisord programs status Nagios plugin [https://github.com/vint21h/nagios-check-supervisord]
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
import sys

try:
    from optparse import OptionParser
    import xmlrpclib
    from string import strip
except ImportError as error:
    sys.stderr.write("ERROR: Couldn't load module. {error}\n".format(error=error))
    sys.exit(-1)


__all__ = ["main", ]


# metadata
VERSION = (0, 5, 2)
__version__ = ".".join(map(str, VERSION))

# global variables
OUTPUT_TEMPLATES = {
    "critical": {
        "text": "problem with '{name}': ({status})",
        "priority": 1,
    },
    "warning": {
        "text": "something curiously with '{name}': ({status})",
        "priority": 2,
    },
    "unknown": {
        "text": "'{name}' not found in server response",
        "priority": 3,
    },
    "ok": {
        "text": "'{name}': OK",
        "priority": 4,
    },
}
EXIT_CODE_OK, EXIT_CODE_WARNING, EXIT_CODE_CRITICAL, EXIT_CODE_UNKNOWN = "ok", "warning", "critical", "unknown"
EXIT_CODES = {
    EXIT_CODE_OK: 0,
    EXIT_CODE_WARNING: 1,
    EXIT_CODE_CRITICAL: 2,
    EXIT_CODE_UNKNOWN: 3,
}
STATE_STOPPED, STATE_RUNNING, STATE_STARTING, STATE_BACKOFF, STATE_STOPPING, STATE_EXITED, STATE_FATAL, STATE_UNKNOWN = "STOPPED", "RUNNING", "STARTING", "BACKOFF", "STOPPING", "EXITED", "FATAL", "UNKNOWN"
STATE2TEMPLATE = {
    STATE_STOPPED: EXIT_CODE_OK,
    STATE_RUNNING: EXIT_CODE_OK,
    STATE_STARTING: EXIT_CODE_WARNING,
    STATE_BACKOFF: EXIT_CODE_WARNING,
    STATE_STOPPING: EXIT_CODE_WARNING,
    STATE_EXITED: EXIT_CODE_WARNING,
    STATE_FATAL: EXIT_CODE_CRITICAL,
    STATE_UNKNOWN: EXIT_CODE_UNKNOWN,
}


def parse_options():
    """
    Commandline options arguments parsing.

    :return: parsed commandline arguments.
    :rtype: optparse.Values.
    """

    version = "%%prog {version}".format(version=__version__)
    parser = OptionParser(version=version)
    parser.add_option(
        "-s", "--server", action="store", dest="server",
        type="string", default="", metavar="SERVER",
        help="server name or IP address"
    )
    parser.add_option(
        "-p", "--port", action="store", type="int", dest="port",
        default=9001, metavar="PORT", help="port number"
    )
    parser.add_option(
        "-P", "--programs", action="store", dest="programs", type="string", default="",
        metavar="PROGRAMS", help="comma separated programs list, or empty for all programs in supervisord response"
    )
    parser.add_option(
        "-u", "--username", action="store", dest="username", type="string", default="",
        metavar="USERNAME", help="supervisord user"
    )
    parser.add_option(
        "-S", "--password", action="store", dest="password", type="string", default="",
        metavar="PASSWORD", help="supervisord user password"
    )
    parser.add_option(
        "-q", "--quiet", metavar="QUIET", action="store_true", default=False, dest="quiet", help="be quiet"
    )
    parser.add_option(
        "--stopped-state", action="store", dest="stopped_state", type="choice", choices=EXIT_CODES.keys(), default=EXIT_CODE_OK,
        metavar="STOPPED_STATE", help="stopped state"
    )
    parser.add_option(
        "--network-errors-exit-code", action="store", dest="network_errors_exit_code", type="choice", choices=EXIT_CODES.keys(), default=EXIT_CODE_UNKNOWN,
        metavar="NETWORK_ERRORS_EXIT_CODE", help="network errors exit code"
    )

    options = parser.parse_args(sys.argv)[0]
    STATE2TEMPLATE[STATE_STOPPED] = options.stopped_state  # update stopped state value from command line argument

    # check mandatory command line options supplied
    if not options.server:
        parser.error("Required server address option missing")
    if options.username and not options.password:
        parser.error("Required supervisord user password")

    return options


def get_status(options):
    """
    Get programs statuses.

    :param options: parsed commandline arguments.
    :type options: optparse.Values.
    :return: supervisord XML-RPC call result.
    :rtype: dict.
    """

    try:
        if all([options.username, options.password, ]):
            connection = xmlrpclib.Server("http://{username}:{password}@{server}:{port}/RPC2".format(**{
                "username": options.username,
                "password": options.password,
                "server": options.server,
                "port": options.port,
            }))
        else:
            connection = xmlrpclib.Server("http://{server}:{port}/RPC2".format(**{
                "server": options.server,
                "port": options.port,
            }))

        return connection.supervisor.getAllProcessInfo()
    except Exception as error:
        if not options.quiet:
            sys.stdout.write("ERROR: Server communication problem. {error}\n".format(error=error))
        sys.exit(EXIT_CODES.get(options.network_errors_exit_code, EXIT_CODE_UNKNOWN))


def create_output(data, options):
    """
    Create Nagios and human readable supervisord statuses.

    :param data: supervisord XML-RPC call result.
    :type data: dict.
    :param options: parsed commandline arguments.
    :type options: optparse.Values.
    :return: Nagios and human readable supervisord statuses and exit code.
    :rtype: (str, int).
    """

    output = {}
    programs = map(strip, options.programs.strip().split(",")) if options.programs else map(lambda x: x["name"], data)

    for program in programs:
        try:
            program_data = filter(lambda x: x["name"] == program, data)[0]
            output.update({
                program: {
                    "name": program,
                    "template": STATE2TEMPLATE[program_data["statename"]],
                    "status": program_data["spawnerr"] if program_data["spawnerr"] else program_data["statename"],
                }
            })
        except IndexError:
            output.update({
                program: {
                    "name": program,
                    "template": "unknown",
                    "status": "",
                }
            })

    # getting main status for check (for multiple check need to get main status by priority)
    statuses = [status[0] for status in sorted([(status, OUTPUT_TEMPLATES[status]["priority"]) for status in list(set([output[d]["template"] for d in output.keys()]))], key=lambda x: x[1])]
    # if no programs found or configured by supervisord set status ok and custom message
    status = statuses[0] if statuses else EXIT_CODE_OK
    text = ", ".join([OUTPUT_TEMPLATES[output[program]["template"]]["text"].format(**output[program]) for program in sorted(output.keys(), key=lambda x: OUTPUT_TEMPLATES[output[x]["template"]]["priority"])]) if statuses else "No program configured/found"

    # create exit code (unknown if something happened wrong)
    code = EXIT_CODES.get(status, EXIT_CODE_UNKNOWN)

    # return full status string with main status for multiple programs and all programs states
    return "{status}: {output}\n".format(**{
        "status": status.upper(),
        "output": text,
    }), code


def main():
    """
    Program main.
    """

    options = parse_options()
    output, code = create_output(get_status(options), options)
    sys.stdout.write(output)
    sys.exit(code)


if __name__ == "__main__":
    """
    Run program main.
    """

    main()
