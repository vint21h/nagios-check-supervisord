# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.pyi

from typing import List, Tuple, Dict, Union  # pylint: disable=W0611

from argparse import Namespace

try:
    from xmlrpc.client import ServerProxy
except ImportError:
    from xmlrpclib import ServerProxy # type: ignore


__all__: List[str] = ...


VERSION: Tuple[int, int, int] = ...
__version__: str = ...


class CheckSupervisord(object):

    OUTPUT_TEMPLATES: Dict[str, Dict[str, Union[str, int]]] = ...
    STATUS_CRITICAL: str = ...
    STATUS_WARNING: str = ...
    STATUS_UNKNOWN: str = ...
    STATUS_OK: str = ...
    EXIT_CODES: Dict[str, int]
    STATE_STOPPED: str = ...
    STATE_RUNNING: str = ...
    STATE_STARTING: str = ...
    STATE_BACKOFF: str = ...
    STATE_STOPPING: str = ...
    STATE_EXITED: str = ...
    STATE_FATAL: str = ...
    STATE_UNKNOWN: str = ...
    STATE_TO_TEMPLATE: Dict[str, str] = ...
    URI_TPL_HTTP: str = ...
    URI_TPL_HTTP_AUTH: str = ...
    URI_TPL_SOCKET: str = ...
    URI_TEMPLATES: Dict[str, str] = ...
    PRIORITY_CRITICAL: int = ...
    PRIORITY_WARNING: int = ...
    PRIORITY_UNKNOWN: int = ...
    PRIORITY_OK: int = ...
    PRIORITY_TO_STATUS: Dict[int, str] = ...

    def __init__(self) -> None: ...
    def _get_options(self) -> Namespace: ...
    def _get_connection_string(self, tpl: str) -> str: ...
    def _get_connection(self) -> ServerProxy: ...
    def _get_data(self) -> List[Dict[str, Union[str, int]]]: ...
    def _get_status(self, data: List[Dict[str, Union[str, int]]]) -> str: ...
    def _get_code(self, status: str) -> int: ...
    def _get_output(self, data: List[Dict[str, Union[str, int]]], status: str) -> str: ...
    def check(self) -> Tuple[str, int]: ...


def main() -> None: ...
