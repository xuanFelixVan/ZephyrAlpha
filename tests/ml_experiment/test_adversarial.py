"""ML-Experiment Domain 红白对抗测试 (canonical entry point)
=====================================================
Delegates to test_adversarial_ml.py for actual test logic.
This file exists to match the session manifest path convention.
"""
from test_adversarial_ml import *  # noqa: F401,F403
from test_adversarial_ml import run_all_attacks, __all__ as _ml_all

__all__ = _ml_all + ["run_all_attacks"]

if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))

    from test_adversarial_ml import run_all_attacks as _run
    report = _run()

    import json as _json
    print("=" * 60)
    print("  Red/Blue Team Adversarial Test: ML-EXPERIMENT-DOMAIN-001")
    print("=" * 60)
    print()
    for r in report["results"]:
        detected = r.get("detected", False)
        icon = "[GREEN]" if detected else "[RED]"
        print(f"[{r['attack_id']}] {r['description']}")
        print(f"  {icon} detected={detected}  status={r.get('status', 'N/A')}")
        print()

    print("=" * 60)
    print(f"  TOTAL: {report['total_attacks']} attacks, {report['detected']} DETECTED, {report['missed']} MISSED")
    print(f"  SCORE: {report['score']}")
    print("=" * 60)

    sys.exit(0 if report["missed"] == 0 else 1)
