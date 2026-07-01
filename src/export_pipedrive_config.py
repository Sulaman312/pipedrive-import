"""Compatibility wrapper for :mod:`src.configuration.exporter`."""

if __package__:
    from .configuration.exporter import *  # noqa: F401,F403
    from .configuration.exporter import main
else:
    from configuration.exporter import *  # noqa: F401,F403
    from configuration.exporter import main


if __name__ == "__main__":
    raise SystemExit(main())
