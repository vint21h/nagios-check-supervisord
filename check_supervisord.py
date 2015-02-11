#!/usr/bin/env python

# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.py

# Copyright (c) 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua>
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

import sys

try:
    from optparse import OptionParser
    import xmlrpclib
    from string import strip
except ImportError, err:
    sys.stderr.write("ERROR: Couldn't load module. %s\n" % err)
    sys.exit(-1)

__all__ = ["main", ]

# metadata
VERSION = (0, 1, 1)
__version__ = '.'.join(map(str, VERSION))

# global variables
OUTPUT_TEMPLATES = {
    "critical": {
        "text": u"problem with program '%(name)s: (%(status)s)",
        "priority": 1,
    },
    "warning": {
        "text": u"something curiously with program '%(name)s: (%(status)s)",
        "priority": 2,
    },
    "unknown": {
        "text": u"program '%(name)s' not found in server response",
        "priority": 3,
    },
    "ok": {
        "text": u"program %(name)s status OK",
        "priority": 4,
    },
}
STATE2TEMPLATE = {
    "STOPPED": u"ok",
    "RUNNING": u"ok",
    "STARTING": u"warning",
    "BACKOFF": u"warning",
    "STOPPING": u"warning",
    "EXITED": u"warning",
    "FATAL": u"critical",
    "UNKNOWN": u"unknown",
}


def parse_options():
    """
    Commandline options arguments parsing.
    """

    version = "%%prog %s" % __version__
    parser = OptionParser(version=version)
    parser.add_option(
        "-s", "--server", action="store", dest="server",
        type="string", default="", metavar="SERVER",
        help=u"server name or IP address"
    )
    parser.add_option(
        "-p", "--port", action="store", type="int", dest="port",
        default=9001, metavar="PORT", help=u"port number"
    )
    parser.add_option(
        "-P", "--programs", action="store", dest="programs", type="string", default="",
        metavar="PROGRAMS", help=u"comma separated programs list, or empty for all programs in supervisord response"
    )
    parser.add_option(
        "-u", "--username", action="store", dest="username", type="string", default="",
        metavar="USERNAME", help=u"supervisord user"
    )
    parser.add_option(
        "-S", "--password", action="store", dest="password", type="string", default="",
        metavar="PASSWORD", help=u"supervisord user password"
    )
    parser.add_option(
        "-q", "--quiet", metavar="QUIET", action="store_true", default=False, dest="quiet", help=u"be quiet"
    )

    options = parser.parse_args(sys.argv)[0]

    # check mandatory command line options supplied
    if not options.server:
        parser.error(u"Required server address option missing")
    if options.username and not options.password:
        parser.error(u"Required supervisord user password")

    return options


def get_status(options):
    """
    Get programs statuses.
    """

    data = {}

    try:
        if all([options.username, options.password, ]):
            connection = xmlrpclib.Server(u"http://%(username)s:%(password)s@%(server)s:%(port)s/RPC2" % {
                "username": options.username,
                "password": options.password,
                "server": options.server,
                "port": options.port,
            })
        else:
            connection = xmlrpclib.Server(u"http://%(server)s:%(port)s/RPC2" % {
                "server": options.server,
                "port": options.port,
            })
        data = connection.supervisor.getAllProcessInfo()
    except Exception, error:
        if not options.quiet:
            sys.stderr.write(u"ERROR: Server communication problem. %s\n" % error)
        sys.exit(-1)

    return data


def create_output(data, options):
    """
    Create Nagios and human readable supervisord statuses.
    """

    output = {}
    programs = map(strip, options.programs.strip().split(u",")) if options.programs else map(lambda x: x["name"], data)

    for program in programs:
        try:
            program_data = filter(lambda x: x["name"] == program, data)[0]
            output.update({
                program: {
                    'name': program,
                    "template": STATE2TEMPLATE[program_data["statename"]],
                    "status": program_data["spawnerr"],
                }
            })
        except IndexError:
            output.update({
                program: {
                    'name': program,
                    "template": u"unknown",
                    "status": u"",
                }
            })

    # getting main status for check (for multiple check need to get main status by priority)
    status = [status[0] for status in sorted([(status, OUTPUT_TEMPLATES[status]['priority']) for status in list(set([output[d]['template'] for d in output.keys()]))], key=lambda x: x[1])][0]

    # return full status string with main status for multiple programs and all programs states
    return u"%(status)s: %(output)s\n" % {
        "status": status.upper(),
        "output": u", ".join([OUTPUT_TEMPLATES[output[program]['template']]['text'] % output[program] for program in output.keys()]),
    }


def main():
    """
    Program main.
    """

    options = parse_options()
    sys.stdout.write(create_output(get_status(options), options))
    sys.exit(0)

if __name__ == "__main__":

    main()
