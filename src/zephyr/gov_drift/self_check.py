# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.self_check
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_analysis.py (+2 more)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 自检逻辑不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Self-Drift Check — self_check.py


Drift detector 自身完整性验证（纯 stdlib，零 zephyr 依赖）。


对标 blueprint.md §2.7（自漂移检测——Watcher 的 Watcher）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: path 参数
#   fields: 参数 path，类型注解 Path
#   code: self_check.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: base 参数
#   fields: 参数 base，类型注解 Path
#   code: self_check.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① sha256_file
#   name_en: sha256_file
#   intro: sha256_file(path) 源码 L106-L111
#   desc: 源码 L106-L111
#   inputs: path
#   outputs: str
# - id: A2
#   name_zh: ② check_core_files
#   name_en: check_core_files
#   intro: check_core_files(base) 源码 L114-L135
#   desc: 源码 L114-L135
#   inputs: base
#   outputs: dict[str, str]
# - id: A3
#   name_zh: ③ check_registry_parsable
#   name_en: check_registry_parsable
#   intro: check_registry_parsable(base) 源码 L138-L161
#   desc: 源码 L138-L161
#   inputs: base
#   outputs: bool
# - id: A4
#   name_zh: ④ bootstrap_self_check
#   name_en: bootstrap_self_check
#   intro: bootstrap_self_check(base) 源码 L164-L174
#   desc: 源码 L164-L174
#   inputs: base
#   outputs: bool
# - id: A5
#   name_zh: ⑤ run_self_check
#   name_en: run_self_check
#   intro: run_self_check() 源码 L177-L189
#   desc: 源码 L177-L189
#   inputs: 无参数
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_analysis.py (+2 more)
# - id: O2
#   name_zh: dict[str, str]
#   name_en: dict[str, str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/__main__.py ; src/zephyr/gov_drift/_analysis.py (+2 more)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

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
        "_detector_registry.yaml",
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
    registry_path = base / "_detector_registry.yaml"

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

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
