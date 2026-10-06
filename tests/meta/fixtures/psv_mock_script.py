"""Mock script for post_sync_validator flag-registration testing.

Registered flags: --foo, --bar, --baz
Used by tests/governance/shared/test_post_sync_validation.py to assert that
validate_post_sync_command correctly detects registered vs hallucinated flags
via the script's --help output.

Intentionally minimal — this is a test oracle, not production code.
"""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="psv mock script for flag testing")
    parser.add_argument("--foo", help="foo flag")
    parser.add_argument("--bar", help="bar flag")
    parser.add_argument("--baz", action="store_true", help="baz flag")
    parser.parse_args()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
