"""Compatibility wrapper for :mod:`src.configuration.importer`."""

if __package__:
    from .configuration.importer import *  # noqa: F401,F403
    from .configuration.importer import main
else:
    from configuration.importer import *  # noqa: F401,F403
    from configuration.importer import main


if __name__ == "__main__":
    raise SystemExit(main())
