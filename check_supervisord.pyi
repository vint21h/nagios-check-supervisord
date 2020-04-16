# -*- coding: utf-8 -*-

# nagios-check-supervisord
# check_supervisord.pyi

from typing import List, Tuple, Dict, Union  # pylint: disable=W0611

from argparse import Namespace


__all__: List[str] = ...


VERSION: Tuple[int, int, int] = ...
__version__: str = ...


class CheckSupervisord(object):

    OUTPUT_TEMPLATES: Dict[str, Dict[str, Union[str, int]]] = ...
    EXIT_CODE_OK: str = ...
    EXIT_CODE_WARNING: str = ...
    EXIT_CODE_CRITICAL: str = ...
    EXIT_CODE_UNKNOWN: str = ...
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

    def __init__(self) -> None: ...
    def _get_options(self) -> Namespace: ...
    def _get_data(self) -> List[Dict[str, Union[str, int]]]: ...
    def _get_output(self, data: List[Dict[str, Union[str, int]]]) -> Tuple[str, int]: ...
    def check(self) -> Tuple[str, int]: ...
