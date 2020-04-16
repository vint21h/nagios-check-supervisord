# -*- coding: utf-8 -*-

# nagios-check-supervisord
# tests/check_supervisord_test.pyi

from typing import List  # pylint: disable=W0611

from pytest_mock.plugin import MockFixture

__all__: List[str] = ...

def test__get_options(mocker: MockFixture) -> None: ...
def test__get_options__missing_server_option(mocker: MockFixture) -> None: ...
def test__get_options__missing_password_option(mocker: MockFixture) -> None: ...
