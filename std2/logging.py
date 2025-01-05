from contextlib import contextmanager
from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING, Logger, getLevelName
from typing import Iterator, Mapping, Tuple, Type

_LEVELS = (
    CRITICAL,
    DEBUG,
    ERROR,
    INFO,
    NOTSET,
    WARNING,
)


def _gen_lvls() -> Mapping[str, int]:
    def cont() -> Iterator[Tuple[str, int]]:
        for lv in _LEVELS:
            name: str = getLevelName(lv)
            yield name, lv
            yield name.casefold(), lv

    return {k: v for k, v in cont()}


LOG_LEVELS = _gen_lvls()


@contextmanager
def log_exc(
    log: Logger, *exns: Type[BaseException], suppress: bool = False
) -> Iterator[None]:
    try:
        yield None
    except BaseException as e:
        if isinstance(e, exns or Exception):
            log.exception("%s", e)
        if not suppress:
            raise
