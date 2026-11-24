"""``python -m analyzer_service api``, ``worker``, or ``serve``."""

import argparse
import logging
import multiprocessing
import os
import sys
import threading

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)


def _serve() -> int:
    import uvicorn

    from analyzer_service.api import create_app
    from analyzer_service.settings import load_settings
    from analyzer_service.worker import run_worker_process

    settings = load_settings()
    context = multiprocessing.get_context("spawn")
    worker = context.Process(target=run_worker_process, name="analyzer-worker")
    worker.start()
    api_stopped = threading.Event()

    def watch_worker() -> None:
        # Railway restarts the container when this process exits non-zero.
        while not api_stopped.wait(0.25):
            if not worker.is_alive():
                os._exit(1)

    threading.Thread(target=watch_worker, name="worker-watch", daemon=True).start()

    # workers must be 1: the active-upload set is in-process, and SQLite has a single writer.
    uvicorn.run(
        create_app(settings),
        host=settings.host,
        port=settings.port,
        workers=1,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
    api_stopped.set()
    if not worker.is_alive():
        return 1
    worker.terminate()
    worker.join(timeout=5)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="analyzer_service")
    parser.add_argument("command", choices=["api", "worker", "serve"])
    args = parser.parse_args(argv)
    _configure_logging()

    if args.command == "serve":
        return _serve()

    from analyzer_service.settings import load_settings

    settings = load_settings()

    if args.command == "api":
        import uvicorn

        from analyzer_service.api import create_app

        uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
        return 0

    from analyzer_service.worker import run_forever

    try:
        run_forever(settings)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
