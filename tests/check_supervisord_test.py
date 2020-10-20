# -*- coding: utf-8 -*-

# nagios-check-supervisord
# tests/check_supervisord_test.py


from __future__ import unicode_literals

import tempfile
from io import StringIO
from argparse import Namespace


try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib  # type: ignore

import pytest
import contextlib2


try:
    from pytest_mock.plugin import MockerFixture  # pylint: disable=W0611  # noqa: F401
except ImportError:
    from pytest_mock.plugin import (  # type: ignore  # pylint: disable=W0611  # noqa: F401,E501
        MockFixture as MockerFixture,
    )

from check_supervisord import CheckSupervisord


__all__ = [
    "test__get_options",
    "test__get_options__missing_server_option",
    "test__get_options__missing_password_option",
    "test__get_connection_uri__socket",
    "test__get_connection_uri__http",
    "test__get_connection_uri__http_auth",
    "test__get_connection__unix_support_not_available",
    "test__get_connection__socket",
    "test__get_connection__socket_auth",
    "test__get_connection__http",
    "test__get_connection__http_auth",
    "test__get_code",
    "test__get_code__warning",
    "test__get_code__critical",
    "test__get_code__unknown",
    "test__get_data",
    "test__get_data__network_error",
]


def test__get_options(mocker):
    """
    Test "_get_options" method must return argparse namespace.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])
    checker = CheckSupervisord()

    assert isinstance(checker.options, Namespace)  # nosec: B101


def test__get_options__missing_server_option(mocker):
    """
    Test "_get_options" method must exit with server option missing error.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_supervisord.py"])

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stderr(out):
            CheckSupervisord()

    assert (  # nosec: B101
        "Required server address option missing" in out.getvalue().strip()
    )


def test__get_options__missing_password_option(mocker):
    """
    Test "_get_options" method must exit with server option missing error.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    out = StringIO()
    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001", "-u", "supervisord"],
    )

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stderr(out):
            CheckSupervisord()

    assert (  # nosec: B101
        "Required supervisord user password missing" in out.getvalue().strip()
    )


def test__get_connection_uri__socket(mocker):
    """
    Test "_get_connection_uri" method must return connection string for socket.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "/tmp/supervisord.sock"],  # nosec: B108
    )

    checker = CheckSupervisord()

    assert (  # nosec: B101
        checker._get_connection_uri(tpl=checker.URI_TPL_SOCKET)
        == "unix:///tmp/supervisord.sock"
    )


def test__get_connection_uri__http(mocker):
    """
    Test "_get_connection_uri" method must return connection string for http.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"],
    )

    checker = CheckSupervisord()

    assert (  # nosec: B101
        checker._get_connection_uri(tpl=checker.URI_TPL_HTTP) == "http://127.0.0.1:9001"
    )


def test__get_connection_uri__http_auth(mocker):
    """
    Test "_get_connection_uri" method must return connection string for
    http with authorization.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        [
            "check_supervisord.py",
            "-s",
            "127.0.0.1",
            "-p",
            "9001",
            "-u",
            "supervisord",
            "-S",
            "password",
        ],
    )

    checker = CheckSupervisord()

    assert (  # nosec: B101
        checker._get_connection_uri(tpl=checker.URI_TPL_HTTP_AUTH)
        == "http://supervisord:password@127.0.0.1:9001"
    )


def test__get_connection__unix_support_not_available(mocker, capsys):
    """
    Test "_get_connection" method must exit with
    couldn't load supervisord library error.

    :param mocker: mock
    :type mocker: MockerFixture
    :param capsys: std capture
    :type capsys: CaptureFixture
    """

    with tempfile.NamedTemporaryFile() as sock:
        mocker.patch(
            "sys.argv",
            ["check_supervisord.py", "-s", sock.name],
        )
        mocker.patch.dict("sys.modules", {"supervisor": None})
        mocker.patch("stat.S_ISSOCK", return_value=True)

        with pytest.raises(SystemExit):
            CheckSupervisord()._get_connection()

    assert (  # nosec: B101
        "ERROR: Couldn't load module." in capsys.readouterr().out.strip()
    )


def test__get_connection__socket(mocker):
    """
    Test "_get_connection" method must return socket connection.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    with tempfile.NamedTemporaryFile() as sock:
        mocker.patch(
            "sys.argv",
            ["check_supervisord.py", "-s", sock.name],
        )
        mocker.patch("stat.S_ISSOCK", return_value=True)

        result = CheckSupervisord()._get_connection()

    assert isinstance(result, xmlrpclib.ServerProxy)  # nosec: B101


def test__get_connection__socket_auth(mocker):
    """
    Test "_get_connection" method must return socket connection with authorization.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    with tempfile.NamedTemporaryFile() as sock:
        mocker.patch(
            "sys.argv",
            [
                "check_supervisord.py",
                "-s",
                sock.name,
                "-u",
                "supervisord",
                "-S",
                "password",
            ],
        )
        mocker.patch("stat.S_ISSOCK", return_value=True)

        result = CheckSupervisord()._get_connection()

    assert isinstance(result, xmlrpclib.ServerProxy)  # nosec: B101


def test__get_connection__http(mocker):
    """
    Test "_get_connection" method must return http connection.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "127.0.0.1"],
    )

    result = CheckSupervisord()._get_connection()

    assert isinstance(result, xmlrpclib.ServerProxy)  # nosec: B101


def test__get_connection__http_auth(mocker):
    """
    Test "_get_connection" method must return http connection with authorization.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        [
            "check_supervisord.py",
            "-s",
            "127.0.0.1",
            "-p",
            "9001",
            "-u",
            "supervisord",
            "-S",
            "password",
        ],
    )

    result = CheckSupervisord()._get_connection()

    assert isinstance(result, xmlrpclib.ServerProxy)  # nosec: B101


def test__get_code(mocker):
    """
    Test "_get_code" method must return plugin exit code.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])

    result = CheckSupervisord()._get_code(status="ok")

    assert result == 0  # nosec: B101


def test__get_code__warning(mocker):
    """
    Test "_get_code" method must return plugin exit code
    (warning case).

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])

    result = CheckSupervisord()._get_code(status="warning")

    assert result == 1  # nosec: B101


def test__get_code__critical(mocker):
    """
    Test "_get_code" method must return plugin exit code
    (critical case).

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])

    result = CheckSupervisord()._get_code(status="critical")

    assert result == 2  # nosec: B101


def test__get_code__unknown(mocker):
    """
    Test "_get_code" method must return plugin exit code
    (unknown case).

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])

    result = CheckSupervisord()._get_code(status="unknown")

    assert result == 3  # nosec: B101


def test__get_data(mocker):
    """
    Test "_get_data" method must return data from server.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    info = [
        {
            "description": "pid 666, uptime 0 days, 0:00:00",
            "pid": 666,
            "stderr_logfile": "",
            "stop": 0,
            "logfile": "/var/log/example.log",
            "exitstatus": 0,
            "spawnerr": "",
            "now": 0,
            "group": "example",
            "name": "example",
            "statename": "RUNNING",
            "start": 0,
            "state": 20,
            "stdout_logfile": "/var/log/example.log",
        }
    ]
    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])
    mocker.patch(
        "{name}._Method.__call__".format(**{"name": xmlrpclib.__name__}),
        return_value=info,
    )

    result = CheckSupervisord()._get_data()

    assert result == info  # nosec: B101


def test__get_data__network_error(mocker):
    """
    Test "_get_data" method must exit with server error.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    out = StringIO()
    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])
    mocker.patch(
        "{name}._Method.__call__".format(**{"name": xmlrpclib.__name__}),
        side_effect=ConnectionRefusedError,
    )
    checker = CheckSupervisord()

    with pytest.raises(SystemExit):
        with contextlib2.redirect_stdout(out):
            checker._get_data()

    assert (  # nosec: B101
        "ERROR: Server communication problem" in out.getvalue().strip()
    )
