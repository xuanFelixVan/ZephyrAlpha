# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.self_check
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/__main__.py; src/zephyr/gov_drift/_analysis.py (+2 more)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 自检逻辑不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_self_check | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Self-Drift Check — self_check.py


Drift detector 自身完整性验证（纯 stdlib，零 zephyr 依赖）。


对标 blueprint.md §2.7（自漂移检测——Watcher 的 Watcher）。"""

from __future__ import annotations

import hashlib
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    except (OSError, PermissionError):
        return "ERROR"


def check_core_files(base: Path) -> dict[str, str]:
    results: dict[str, str] = {}

    for fname in [
        "_detector-registry.yaml",
        "drift_engine.py",
        "reconciler.py",
        "state_machine.py",
        "baseline_manager.py",
        "detector_dispatcher.py",
        "drift_models.py",
    ]:
        fp = base / fname

        if not fp.exists():
            results[fname] = "MISSING"

            continue

        results[fname] = sha256_file(fp)

    return results


def check_registry_parsable(base: Path) -> bool:
    registry_path = base / "_detector-registry.yaml"

    if not registry_path.exists():
        return False

    try:
        import yaml

        with open(registry_path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        if data is None:
            return False

        detectors = data.get("detectors", {})

        if not isinstance(detectors, dict):
            return False

        return True

    except Exception:
        return False


def bootstrap_self_check(base: Path | None = None) -> bool:
    if base is None:
        base = Path(__file__).parent

    results = check_core_files(base)

    all_present = all(v != "MISSING" for v in results.values())

    registry_ok = check_registry_parsable(base)

    return all_present and registry_ok


def run_self_check() -> int:
    base = Path(__file__).parent

    ok = bootstrap_self_check(base)

    if not ok:
        print(f"[P0 CRITICAL] Drift detector self-check FAILED at {base}", file=sys.stderr)

        return 1

    print("[OK] Drift detector self-check passed")

    return 0


if __name__ == "__main__":
    sys.exit(run_self_check())
