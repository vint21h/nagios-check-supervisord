# -*- coding: utf-8 -*-

# nagios-check-supervisord
# tests/check_supervisord_test.pyi

from typing import List  # pylint: disable=W0611

from _pytest.capture import CaptureFixture

try:
    from pytest_mock.plugin import MockerFixture  # pylint: disable=W0611  # noqa: F401
except ImportError:
    from pytest_mock.plugin import (  # type: ignore  # pylint: disable=W0611  # noqa: F401,E501
        MockFixture as MockerFixture,
    )

__all__: List[str] = ...

def test__get_options(mocker: MockerFixture) -> None: ...
def test__get_options__missing_server_option(mocker: MockerFixture) -> None: ...
def test__get_options__missing_password_option(mocker: MockerFixture) -> None: ...
def test__get_connection_uri__socket(mocker: MockerFixture) -> None: ...
def test__get_connection_uri__http(mocker: MockerFixture) -> None: ...
def test__get_connection_uri__http_auth(mocker: MockerFixture) -> None: ...
def test__get_connection__unix_support_not_available(
    mocker: MockerFixture, capsys: CaptureFixture  # type: ignore
) -> None: ...
def test__get_connection_socket(mocker: MockerFixture) -> None: ...
def test__get_connection_socket_auth(mocker: MockerFixture) -> None: ...
def test__get_connection_http(mocker: MockerFixture) -> None: ...
def test__get_connection_http_auth(mocker: MockerFixture) -> None: ...
def test__get_code(mocker: MockerFixture) -> None: ...
def test__get_code__warning(mocker: MockerFixture) -> None: ...
def test__get_code__critical(mocker: MockerFixture) -> None: ...
def test__get_code__unknown(mocker: MockerFixture) -> None: ...
def test__get_data(mocker: MockerFixture) -> None: ...
def test__get_data__network_error(mocker: MockerFixture) -> None: ...
def test__get_status(mocker: MockerFixture) -> None: ...
def test__get_status__stopped(mocker: MockerFixture) -> None: ...
def test__get_status__critical(mocker: MockerFixture) -> None: ...
def test__get_status__warning__starting(mocker: MockerFixture) -> None: ...
def test__get_status__warning__backoff(mocker: MockerFixture) -> None: ...
def test__get_status__warning__stopping(mocker: MockerFixture) -> None: ...
def test__get_status__warning__exited(mocker: MockerFixture) -> None: ...
def test__get_status__unknown(mocker: MockerFixture) -> None: ...
def test__get_output(mocker: MockerFixture) -> None: ...
def test__get_output__critical(mocker: MockerFixture) -> None: ...
def test__get_output__warning__starting(mocker: MockerFixture) -> None: ...
def test__get_output__warning__backoff(mocker: MockerFixture) -> None: ...
def test__get_output__warning__stopping(mocker: MockerFixture) -> None: ...
def test__get_output__warning__exited(mocker: MockerFixture) -> None: ...
def test__get_output__unknown(mocker: MockerFixture) -> None: ...
def test__get_output__unknown__unknown_program(mocker: MockerFixture) -> None: ...
def test__get_output__unknown__no_data(mocker: MockerFixture) -> None: ...
def test_check(mocker: MockerFixture) -> None: ...
def test_check__critical(mocker: MockerFixture) -> None: ...
def test_check__warning__starting(mocker: MockerFixture) -> None: ...
def test_check__warning__backoff(mocker: MockerFixture) -> None: ...
def test_check__warning__stopping(mocker: MockerFixture) -> None: ...
def test_check__warning__exited(mocker: MockerFixture) -> None: ...
def test_check__unknown(mocker: MockerFixture) -> None: ...
def test_check__unknown__unknown_program(mocker: MockerFixture) -> None: ...
def test_check__unknown__no_data(mocker: MockerFixture) -> None: ...
