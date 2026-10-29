"""Run a module-level function in a spawned child process."""

import multiprocessing
from multiprocessing.process import BaseProcess

from analyzer_core.errors import AnalyzerError, ErrorCode


def _child_entry(func, args, conn) -> None:
    try:
        result = func(*args)
        conn.send({"ok": True, "result": result})
    except Exception as exc:
        conn.send(
            {
                "ok": False,
                "exc_type": type(exc).__name__,
                "exc_message": str(exc),
            }
        )
    finally:
        conn.close()


def _stop(proc: BaseProcess) -> None:
    if not proc.is_alive():
        return
    proc.terminate()
    proc.join(0.5)
    if proc.is_alive():
        proc.kill()
        proc.join(0.5)


def run_isolated(func, args, timeout_s):
    """Run ``func(*args)`` in a ``spawn`` child and return its dict result.

    ``func`` must be a module-level function so the child can import it.
    The child sends one picklable dict back on a pipe.
    """

    ctx = multiprocessing.get_context("spawn")
    parent_conn, child_conn = ctx.Pipe(duplex=False)
    proc = ctx.Process(target=_child_entry, args=(func, tuple(args), child_conn))
    proc.start()
    child_conn.close()

    timed_out = False
    payload = None
    read_error: EOFError | None = None
    try:
        if not parent_conn.poll(timeout_s):
            timed_out = True
        else:
            try:
                payload = parent_conn.recv()
            except EOFError as exc:
                read_error = exc
    finally:
        parent_conn.close()
        if proc.is_alive():
            _stop(proc)
        else:
            proc.join(0.5)

    if timed_out:
        raise AnalyzerError(
            ErrorCode.E_TIMEOUT,
            f"Isolated call exceeded {timeout_s} seconds.",
        )
    if read_error is not None:
        raise AnalyzerError(
            ErrorCode.E_PARSE_FAILED,
            "EOFError: child exited without a result",
        ) from read_error
    if not isinstance(payload, dict) or "ok" not in payload:
        raise AnalyzerError(
            ErrorCode.E_PARSE_FAILED,
            "TypeError: child returned an unexpected payload",
        )
    if not payload["ok"]:
        exc_type = payload.get("exc_type", "Exception")
        exc_message = payload.get("exc_message", "")
        raise AnalyzerError(
            ErrorCode.E_PARSE_FAILED,
            f"{exc_type}: {exc_message}",
        )
    return payload["result"]
