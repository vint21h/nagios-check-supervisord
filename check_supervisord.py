#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.py

# Copyright (c) 2015-2016 Alexei Andrushievich <vint21h@vint21h.pp.ua>
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
except ImportError, error:
    sys.stderr.write("ERROR: Couldn't load module. {error}\n".format(error=error))
    sys.exit(-1)

__all__ = ["main", ]

# metadata
VERSION = (0, 3, 1)
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
STATE2TEMPLATE = {
    "STOPPED": "ok",
    "RUNNING": "ok",
    "STARTING": "warning",
    "BACKOFF": "warning",
    "STOPPING": "warning",
    "EXITED": "warning",
    "FATAL": "critical",
    "UNKNOWN": "unknown",
}
EXIT_CODES = {
    "ok": 0,
    "warning": 1,
    "critical": 2,
}


def parse_options():
    """
    Commandline options arguments parsing.
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
        "--stopped-state", action="store", dest="stopped_state", type="choice", choices=EXIT_CODES.keys(), default="ok",
        metavar="STOPPED_STATE", help="stopped state"
    )

    options = parser.parse_args(sys.argv)[0]
    STATE2TEMPLATE["STOPPED"] = options.stopped_state  # update stopped state value from command line argument

    # check mandatory command line options supplied
    if not options.server:
        parser.error("Required server address option missing")
    if options.username and not options.password:
        parser.error("Required supervisord user password")

    return options


def get_status(options):
    """
    Get programs statuses.
    """

    data = {}

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
        data = connection.supervisor.getAllProcessInfo()
    except Exception, error:
        if not options.quiet:
            sys.stdout.write("ERROR: Server communication problem. {error}\n".format(error=error))
        sys.exit(3)

    return data


def create_output(data, options):
    """
    Create Nagios and human readable supervisord statuses.
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
    status = [status[0] for status in sorted([(status, OUTPUT_TEMPLATES[status]["priority"]) for status in list(set([output[d]["template"] for d in output.keys()]))], key=lambda x: x[1])][0]

    code = EXIT_CODES.get(status, 3)  # create exit code

    # return full status string with main status for multiple programs and all programs states
    return "{status}: {output}\n".format(**{
        "status": status.upper(),
        "output": ", ".join([OUTPUT_TEMPLATES[output[program]["template"]]["text"].format(**output[program]) for program in sorted(output.keys(), key=lambda x: OUTPUT_TEMPLATES[output[x]["template"]]["priority"])]),
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

    main()
