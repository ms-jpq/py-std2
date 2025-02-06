import sys
from contextlib import suppress
from os import F_OK, environ
from shutil import which
from signal import Signals
from subprocess import DEVNULL, PIPE, CalledProcessError, CompletedProcess, Popen
from typing import IO, AbstractSet, Callable, Mapping, Optional, Union

from .pathlib import AnyPath
from .platform import OS, os

if sys.version_info < (3, 9):
    _R = CompletedProcess
else:
    _R = CompletedProcess[bytes]


try:
    from signal import SIGKILL

    SIGDED: Signals = SIGKILL
except:
    from signal import Signals

    SIGDED = Signals.SIGTERM


try:
    from os import getpgid, killpg

    def kill_children(pid: int, sig: Signals) -> None:
        killpg(getpgid(pid), sig)

except ImportError:
    from os import kill

    def kill_children(pid: int, sig: Signals) -> None:
        kill(pid, sig)


def call(
    arg0: AnyPath,
    *argv: AnyPath,
    kill_signal: Signals = SIGDED,
    capture_stdout: bool = True,
    capture_stderr: bool = True,
    stdin: Union[IO[bytes], bytes, None] = None,
    cwd: Optional[AnyPath] = None,
    env: Optional[Mapping[str, str]] = None,
    creationflags: int = 0,
    preexec_fn: Optional[Callable[[], None]] = None,
    check: AbstractSet[int] = frozenset((0,)),
) -> _R:
    if a0 := which(arg0):
        kwargs = {} if os is OS.windows else {"preexec_fn": preexec_fn}
        with Popen(
            (a0, *argv),
            start_new_session=True,
            creationflags=creationflags,
            stdin=PIPE if isinstance(stdin, bytes) else (stdin if stdin else DEVNULL),
            stdout=PIPE if capture_stdout else None,
            stderr=PIPE if capture_stderr else None,
            cwd=cwd,
            env=None if env is None else {**environ, **env},
            **kwargs,  # type: ignore
        ) as proc:
            try:
                cmd = (arg0, *argv)
                stdout, stderr = proc.communicate(
                    stdin if isinstance(stdin, bytes) else None
                )
                code = proc.wait()

                if check and code not in check:
                    raise CalledProcessError(
                        returncode=code,
                        cmd=cmd,
                        output=stdout if capture_stdout else None,
                        stderr=stderr.decode() if capture_stderr else None,
                    )
                else:
                    return CompletedProcess(
                        args=cmd,
                        returncode=code,
                        stdout=stdout if capture_stdout else b"",
                        stderr=stderr if capture_stderr else b"",
                    )
            finally:
                with suppress(ProcessLookupError):
                    try:
                        kill_children(proc.pid, sig=kill_signal)
                    except PermissionError:
                        proc.kill()
                proc.wait()
    elif a0 := which(arg0, mode=F_OK):
        raise PermissionError(a0)
    else:
        raise FileNotFoundError(arg0)
