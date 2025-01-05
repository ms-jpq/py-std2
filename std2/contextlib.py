import sys
from abc import abstractmethod
from contextlib import asynccontextmanager
from sys import exit
from typing import AsyncIterator, Iterator, Protocol, TypeVar

_T = TypeVar("_T")


class Closable(Protocol):
    @abstractmethod
    def close(self) -> None: ...


class AClosable(Protocol):
    @abstractmethod
    async def aclose(self) -> None: ...


_T2 = TypeVar("_T2", bound=AClosable)


def keyboard_interrupt() -> Iterator[None]:
    try:
        yield None
    except KeyboardInterrupt:
        exit(130)


if sys.version_info < (3, 10):

    @asynccontextmanager
    async def aclosing(thing: _T2) -> AsyncIterator[_T2]:
        try:
            yield thing
        finally:
            await thing.aclose()

else:
    from contextlib import aclosing as _aclosing

    aclosing = _aclosing

if sys.version_info < (3, 10):

    # TODO -- 3.10 has this on nullcontext
    @asynccontextmanager
    async def nullacontext(enter_result: _T) -> AsyncIterator[_T]:
        yield enter_result

else:
    from contextlib import nullcontext

    nullacontext = nullcontext
