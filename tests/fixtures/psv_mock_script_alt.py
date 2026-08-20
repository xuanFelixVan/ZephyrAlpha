"""Alt mock script for post_sync_validator per-subcommand isolation testing.

Registers ONLY --foo (not --bar / --baz).

Used by R27 to verify chain isolation: when a chain runs script A then
script B, B's hallucinated flag must be checked against B's own --help,
not A's. Without a distinct second script, mutation M08 (no chain split)
survives because all chain subs share the same script and flag set.

Intentionally minimal — a test oracle, not production code.
"""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="psv alt mock — --foo only")
    parser.add_argument("--foo", help="foo flag")
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
