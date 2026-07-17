# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/verify_reconciliation_registry.py | §
# [MODULE] scripts.governance.meta.verify_reconciliation_registry
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] _shared.constants
# [CONSUMERS] validate_mutation_testing.py（false_negative_cases/reconciliation_registry_cases.yaml 的 verifier）
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] --warn-only 始终 exit 0（非阻断）；importlib 加载 SSoT 绕过 zephyr.* import 链
# [MODIFY-GUARD] CHECKS 列表与 reconciliation_registry_cases.yaml 的 expected_finding_id 一一对应
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PASS=0；--warn-only 始终 0；非 warn-only 且有 FAIL=1；SSoT 加载失败=1（warn-only 时 0）
# [TESTS] P3-T1 dry-run + 实际 run（8 case 全 detected）
# [A_module] module_id=MOD-GOV-verify_reconciliation_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""verify_reconciliation_registry.py — ReconciliationRegistry 轻量结构 audit（P3-T1）

被 ``validate_mutation_testing.py`` 的
``false_negative_cases/reconciliation_registry_cases.yaml`` 作为 verifier 调用
（``--warn-only``）。importlib 直接加载 SSoT
``src/zephyr/gov_audit/reconciliation_registry.py``（绕过 ``zephyr.*`` import 链断裂，
仿 ``post_sync_validator.py`` SSoT 解耦模式），检查 8 项结构/行为不变量，打印
``FN-RR-XXX: PASS/FAIL: <detail>`` 供 check_detection 子串匹配。

设计裁定（P3-T1 scaffold vs P3-T2 rigorous，呼应 continuation plan §5.1/§5.2）
------------------------------------------------------------------------
本 verifier 是"轻量 audit"——打印每个检查的 finding ID（PASS/FAIL），使
``validate_mutation_testing`` 子串匹配判定 detected（ID 在 stdout 即 detected）。
严格的"变异注入→oracle 判 killed/survived"由 P3-T2 的
``mutation_test_reconciliation_registry.py`` 承担（仿 ``mutation_test_post_sync_validator``），
二者互补：

- **P3-T1**（本文件 + cases yaml）：建 case + 可运行 verifier——打破自指的 oracle 种子
  （AI 写 Gate + AI 写测试共享同源盲区，机械可加载的 SSoT audit 是逃脱起点）
- **P3-T2**：机械注入 ~15 个变异到 SSoT 副本，跑本 verifier 看 PASS/FAIL，
  统计 killed/survived，≥80% 达标，反馈环补变异

8 项不变量（与 ``reconciliation_registry_cases.yaml`` 一一对应）
--------------------------------------------------------------
- FN-RR-001: ReconcilerSpec 必需字段齐全（gate_id/trigger/reconcile/priority）
- FN-RR-002: register 同 gate_id 覆盖（幂等，不产生重复 spec）
- FN-RR-003: reconcile_for 返回 list（D3 修复，非单值）
- FN-RR-004: reconcile_for 按 priority 升序执行命中 trigger 的 reconciler
- FN-RR-005: 单 reconciler 异常降级为 warn，不中断后续
- FN-RR-006: 空 registry / 无 trigger 命中 → reconcile_for 返回 []（非 None）
- FN-RR-007: reconcile_for 收集所有命中 trigger 的结果（append 不可移除）——杀 M07
- FN-RR-008: ReconcilerSpec 未传 priority 时默认 100——杀 M09

seam：``RR_UNDER_TEST`` 环境变量重定向 SSoT 到变异副本（供 P3-T2 使用），
      缺省指向真源（正常 audit 不受影响）。

Usage::

    python scripts/governance/meta/verify_reconciliation_registry.py --warn-only
"""

from __future__ import annotations

__manifest__ = """
args: []
description: verify_reconciliation_registry.py — ReconciliationRegistry 轻量结构 audit（P3-T1）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parents[1]
_GOV_DIR = str(_SCRIPT_DIR)
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT  # noqa: E402

SSOT_PATH = REPO_ROOT / "src" / "zephyr" / "governance" / "audit" / "reconciliation_registry.py"


@dataclass
class CheckResult:
    """单项不变量检查结果。"""

    finding_id: str
    passed: bool
    detail: str


def _load_ssot():
    """importlib 加载 SSoT（绕过 zephyr.* import 链断裂）。

    ``RR_UNDER_TEST`` 环境变量重定向到变异副本（P3-T2 seam）；缺省指向真源。

    Returns:
        tuple: (module, error) — module 为 None 时 error 描述失败原因。
    """
    path = Path(os.environ.get("RR_UNDER_TEST", "") or SSOT_PATH)
    if not path.exists():
        return None, f"SSoT not found: {path}"
    spec = importlib.util.spec_from_file_location("_rr_ssot_under_test", path)
    if spec is None or spec.loader is None:
        return None, f"cannot create import spec for {path}"
    mod = importlib.util.module_from_spec(spec)
    # 关键：exec_module 前须注册到 sys.modules，否则模块内引用自身 __name__
    # （如 logging.getLogger(__name__)）的导入机制会报
    # "'NoneType' object has no attribute '__dict__'"——标准 importlib 模式。
    sys.modules[spec.name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # noqa: BLE001 — 报告给调用者，不吞
        sys.modules.pop(spec.name, None)
        return None, f"SSoT import failed: {e}"
    return mod, None


# ── 8 项不变量检查 ─────────────────────────────────────────────────────


def _check_001_spec_fields(mod) -> CheckResult:
    """FN-RR-001: ReconcilerSpec 必需字段齐全（gate_id/trigger/reconcile/priority）。"""
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if spec_cls is None:
        return CheckResult("FN-RR-001", False, "ReconcilerSpec class missing")
    try:
        fields = {f for f in spec_cls.__dataclass_fields__}
    except AttributeError:
        return CheckResult("FN-RR-001", False, "ReconcilerSpec not a dataclass")
    required = {"gate_id", "trigger", "reconcile", "priority"}
    missing = required - fields
    if missing:
        return CheckResult("FN-RR-001", False, f"missing fields: {sorted(missing)}")
    return CheckResult("FN-RR-001", True, f"all 4 fields present: {sorted(required & fields)}")


def _check_002_register_idempotent(mod) -> CheckResult:
    """FN-RR-002: register 同 gate_id 覆盖（幂等，不产生重复 spec）。"""
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if reg_cls is None or spec_cls is None:
        return CheckResult("FN-RR-002", False, "registry/spec class missing")
    reg = reg_cls()

    def _mk(gid: str) -> object:
        return spec_cls(
            gate_id=gid,
            trigger=lambda files: False,
            reconcile=lambda files, sid: mod.ReconcileResult(action="skip"),
        )

    reg.register(_mk("G1"))
    reg.register(_mk("G1"))
    reg.register(_mk("G1"))
    if reg.spec_count != 1:
        return CheckResult(
            "FN-RR-002", False, f"register not idempotent: count={reg.spec_count} (expected 1)"
        )
    return CheckResult("FN-RR-002", True, "register idempotent (same gate_id replaces)")


def _check_003_reconcile_returns_list(mod) -> CheckResult:
    """FN-RR-003: reconcile_for 返回 list（D3 修复，非单值）。"""
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    if reg_cls is None:
        return CheckResult("FN-RR-003", False, "registry class missing")
    reg = reg_cls()
    result = reg.reconcile_for([], "sess")
    if not isinstance(result, list):
        return CheckResult(
            "FN-RR-003", False, f"reconcile_for returns {type(result).__name__}, not list"
        )
    return CheckResult("FN-RR-003", True, f"reconcile_for returns list (len={len(result)})")


def _check_004_priority_order(mod) -> CheckResult:
    """FN-RR-004: reconcile_for 按 priority 升序执行命中 trigger 的 reconciler。"""
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if reg_cls is None or spec_cls is None:
        return CheckResult("FN-RR-004", False, "registry/spec class missing")
    reg = reg_cls()
    order: list[str] = []
    # 故意让 gate_id 字典序(A<B<C)与 priority 升序(B<A<C)不同——
    # 杀灭 M13 盲区:若 sort key 被改为 gate_id，order=[A,B,C]≠[B,A,C] 即 FAIL。
    # 同时仍杀灭 M02(reverse 降序→[C,A,B])与 M03(移除 sort→register 序[C,B,A])。
    for prio, gid in [(300, "C"), (100, "B"), (200, "A")]:

        def _reconcile(files, sid, _gid=gid):
            order.append(_gid)
            return mod.ReconcileResult(action="clean", detail=_gid)

        reg.register(
            spec_cls(gate_id=gid, trigger=lambda files: True, reconcile=_reconcile, priority=prio)
        )
    reg.reconcile_for(["x.py"], "sess")
    if order != ["B", "A", "C"]:  # noqa: gate-vocab  测试断言：校验优先级排序输出 [B,A,C]（gate_id 测试夹具，非 governance_family 词表校验）
        return CheckResult("FN-RR-004", False, f"priority order wrong: {order} (expected B,A,C)")
    return CheckResult("FN-RR-004", True, f"priority ascending: {order}")


def _check_005_exception_isolation(mod) -> CheckResult:
    """FN-RR-005: 单 reconciler 异常降级为 warn，不中断后续。"""
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if reg_cls is None or spec_cls is None:
        return CheckResult("FN-RR-005", False, "registry/spec class missing")
    reg = reg_cls()
    ran_after = {"v": False}

    def _boom(files, sid):
        raise RuntimeError("injected failure")

    def _ok(files, sid):
        ran_after["v"] = True
        return mod.ReconcileResult(action="clean")

    reg.register(spec_cls(gate_id="BOOM", trigger=lambda f: True, reconcile=_boom, priority=100))
    reg.register(spec_cls(gate_id="OK", trigger=lambda f: True, reconcile=_ok, priority=200))
    results = reg.reconcile_for(["x.py"], "sess")
    if not ran_after["v"]:
        return CheckResult("FN-RR-005", False, "subsequent reconciler not run after exception")
    warn_actions = [r for r in results if r.action == "warn"]
    if not warn_actions:
        return CheckResult("FN-RR-005", False, "exception not degraded to warn result")
    return CheckResult(
        "FN-RR-005", True, f"exception isolated, {len(results)} results, ran_after=True"
    )


def _check_006_empty_registry(mod) -> CheckResult:
    """FN-RR-006: 空 registry / 无 trigger 命中 → reconcile_for 返回 []（非 None）。"""
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    if reg_cls is None:
        return CheckResult("FN-RR-006", False, "registry class missing")
    reg = reg_cls()
    result = reg.reconcile_for(["x.py"], "sess")
    if result != []:
        return CheckResult("FN-RR-006", False, f"empty registry returned {result!r}, not []")
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if spec_cls is not None:
        reg.register(
            spec_cls(
                gate_id="NO",
                trigger=lambda f: False,
                reconcile=lambda f, s: mod.ReconcileResult(action="skip"),
            )
        )
        result2 = reg.reconcile_for(["x.py"], "sess")
        if result2 != []:
            return CheckResult(
                "FN-RR-006", False, f"no-trigger-match returned {result2!r}, not []"
            )
    return CheckResult("FN-RR-006", True, "empty/no-match → [] (no silent None)")


def _check_007_result_collection(mod) -> CheckResult:
    """FN-RR-007: reconcile_for 收集所有命中 trigger 的结果（append 不可移除）。

    M07 盲区: append 移除后返回空 list（仍是 list，过 FN-RR-003/006）。
    本检查注册 2 个 trigger 命中的 spec，断言返回 len==2，确保 append 完整。
    """
    reg_cls = getattr(mod, "ReconciliationRegistry", None)
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if reg_cls is None or spec_cls is None:
        return CheckResult("FN-RR-007", False, "registry/spec class missing")
    reg = reg_cls()
    for gid in ("G1", "G2"):
        reg.register(
            spec_cls(
                gate_id=gid,
                trigger=lambda files: True,
                reconcile=lambda files, sid: mod.ReconcileResult(action="clean"),
            )
        )
    results = reg.reconcile_for(["x.py"], "sess")
    if len(results) != 2:
        return CheckResult(
            "FN-RR-007", False,
            f"collected {len(results)} results, expected 2 (append removed?)",
        )
    return CheckResult("FN-RR-007", True, f"collected all {len(results)} results")


def _check_008_default_priority(mod) -> CheckResult:
    """FN-RR-008: ReconcilerSpec 未传 priority 时默认 100。

    M09 盲区: priority 默认 100→999，字段仍在过 FN-RR-001。
    本检查构造不传 priority 的 spec，断言 priority==100。
    """
    spec_cls = getattr(mod, "ReconcilerSpec", None)
    if spec_cls is None:
        return CheckResult("FN-RR-008", False, "ReconcilerSpec class missing")
    try:
        spec = spec_cls(
            gate_id="DEF",
            trigger=lambda files: False,
            reconcile=lambda files, sid: mod.ReconcileResult(action="skip"),
        )
    except TypeError as e:
        return CheckResult("FN-RR-008", False, f"cannot construct spec without priority: {e}")
    if spec.priority != 100:
        return CheckResult(
            "FN-RR-008", False, f"default priority={spec.priority}, expected 100"
        )
    return CheckResult("FN-RR-008", True, "default priority=100")


CHECKS = [
    _check_001_spec_fields,
    _check_002_register_idempotent,
    _check_003_reconcile_returns_list,
    _check_004_priority_order,
    _check_005_exception_isolation,
    _check_006_empty_registry,
    _check_007_result_collection,
    _check_008_default_priority,
]


def main() -> int:
    """Entry point: parse args, run 8 invariant checks, print findings, return exit code."""
    parser = argparse.ArgumentParser(
        description="ReconciliationRegistry 轻量结构 audit (P3-T1)"
    )
    parser.add_argument(
        "--warn-only", action="store_true", help="非阻断模式（始终 exit 0，仅报告）"
    )
    args = parser.parse_args()

    mod, err = _load_ssot()
    if mod is None:
        print(f"FN-RR-LOAD: FAIL: {err}")
        return EXIT_PASS if args.warn_only else 1

    fail_count = 0
    for check in CHECKS:
        try:
            r = check(mod)
        except Exception as e:  # noqa: BLE001 — 单 check 异常不中断其余
            r = CheckResult(check.__name__, False, f"check raised: {e}")
        status = "PASS" if r.passed else "FAIL"
        print(f"{r.finding_id}: {status}: {r.detail}")
        if not r.passed:
            fail_count += 1

    if fail_count:
        print(f"\nFAIL: {fail_count} invariant check(s) failed", file=sys.stderr)
    else:
        print(f"\nOK: all {len(CHECKS)} ReconciliationRegistry invariant checks passed")

    return EXIT_PASS if args.warn_only else (1 if fail_count else EXIT_PASS)


if __name__ == "__main__":
    sys.exit(main())
