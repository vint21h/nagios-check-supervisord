# -*- coding: utf-8 -*-

# nagios-check-supervisord
# tests/check_supervisord_test.py


from __future__ import unicode_literals

from io import StringIO
from argparse import Namespace

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
    "test__get_connection_string__socket",
    "test__get_connection_string__http",
    "test__get_connection_string__http_auth",
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


def test__get_connection_string__socket(mocker):
    """
    Test "_get_connection_string" method must return connection string for socket.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "/tmp/supervisord.sock"],
    )

    checker = CheckSupervisord()

    assert (
        checker._get_connection_string(tpl=checker.URI_TPL_SOCKET)
        == "unix:///tmp/supervisord.sock"
    )


def test__get_connection_string__http(mocker):
    """
    Test "_get_connection_string" method must return connection string for http.

    :param mocker: mock
    :type mocker: MockerFixture
    """

    mocker.patch(
        "sys.argv",
        ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"],
    )

    checker = CheckSupervisord()

    assert (
        checker._get_connection_string(tpl=checker.URI_TPL_HTTP)
        == "http://127.0.0.1:9001"
    )


def test__get_connection_string__http_auth(mocker):
    """
    Test "_get_connection_string" method must return connection string for http with authorization.

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

    assert (
        checker._get_connection_string(tpl=checker.URI_TPL_HTTP_AUTH)
        == "http://supervisord:password@127.0.0.1:9001"
    )
