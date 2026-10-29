"""``python -m analyzer_service api`` or ``python -m analyzer_service worker``."""

import argparse
import logging
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="analyzer_service")
    parser.add_argument("command", choices=["api", "worker"])
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    if args.command == "api":
        import uvicorn

        from analyzer_service.api import create_app

        uvicorn.run(create_app(), host="127.0.0.1", port=8000)
        return 0

    from analyzer_service.worker import run_forever

    try:
        run_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
