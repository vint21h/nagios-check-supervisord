# -*- coding: utf-8 -*-

# nagios-check-supervisord
# tests/check_supervisord_test.py


from __future__ import unicode_literals

from argparse import Namespace
from io import StringIO

import contextlib2
import pytest

from check_supervisord import CheckSupervisord


__all__ = [
    "test__get_options",
    "test__get_options__missing_server_option",
    "test__get_options__missing_password_option",
]


def test__get_options(mocker):
    """
    Test "_get_options" method must return argparse namespace.
    """

    mocker.patch("sys.argv", ["check_supervisord.py", "-s", "127.0.0.1", "-p", "9001"])
    checker = CheckSupervisord()

    assert isinstance(checker.options, Namespace)  # nosec: B101


def test__get_options__missing_server_option(mocker):
    """
    Test "_get_options" method must exit with server option missing error.
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
