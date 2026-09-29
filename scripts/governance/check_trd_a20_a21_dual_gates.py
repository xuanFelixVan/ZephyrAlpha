# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_trd_a20_a21_dual_gates.py | §
# [MODULE] scripts.governance.check_trd_a20_a21_dual_gates
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants; zephyr.shared.security.secrets; zephyr.strategy_pipeline.daily_decision_orchestrator
# [CONSUMERS] TRD-A15 check_live_readiness 实装时逐门聚合（admission_gate_design.md §3 输出契约）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只读快照（禁写生产路径）；G1 叫核对只报键名/状态绝不打印值（tc10 步骤5 口径）；
#  G7 未经 Owner confirmed 一律 FAIL 且 effective_hard_cap=0.0（fail-closed 不建仓）；禁 AI 代签
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 逐门 try/except → verdict=FAIL+evidence（门探针异常不伪装 PASS）；CLI 退出码 EXIT_PASS/EXIT_FINDINGS/EXIT_ERROR
# [TESTS] tests/governance/test_trd_a20_a21_dual_gates.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: 本件是 TRD-A20/21 准入双闸（G1 密钥轮换+G7 仓位参数 confirmed）的机械判定器，判据真源=live_readiness/admission_gate_design.md §3 判定矩阵；与 session_required_gate（提交会话注册闸）/liquidity_crisis_manager（流动性危机处置）既不同域也不同对象——CREATE-GUARD 命中词（'now iso'/'read status'）为通用词伪命中
"""TRD-A20/21 双闸机械判定器（准入门 G1 密钥轮换 + G7 仓位参数 confirmed）。

设计真源：docs/_working/live_readiness/admission_gate_design.md §1/§3（判定矩阵逐字落地）；
施工项出处：docs/_working/decision_map_campaign_20260924/13_trading_chain_audit.md §9
（TRD-A20=K1 密钥轮换+叫核对、TRD-A21=P1 仓位参数 confirmed+落 config）。

G1（key-validation）：
  读 docs/_working/recovered_task_cards/tc10_owner_report.md 步骤5 行==完成态
  AND 核对回执文件存在（data/runtime/key_rotation_receipt/*.json，verified=true）。
  叫核对执行体=verify_key_presence()：经 zephyr.shared.security.secrets.fail-closed
  通道逐键校验（缺失/空/占位符一律 FAIL），输出只含键名与状态，绝不打印值。

G7（position-cap）：
  读 config/position_parameters.yaml：status==confirmed AND owner_sign.signed_by 非空
  AND 表值与 daily_decision_orchestrator 代码常量零漂移 → PASS，否则 FAIL；
  effective_hard_cap()：confirmed 前=0.0（未确认=零仓位容许，宁可不动不可越顶）。

输出契约（admission_gate_design.md §3）：逐门 {"gate_id","verdict","evidence","checked_at"}
+ 顶部 all_green；all_green 也只产出"建议 Owner 签发"提示，不触发任何实盘动作。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

_SCRIPT_DIR = Path(__file__).resolve()
_REPO_ROOT = next(p for p in _SCRIPT_DIR.parents if (p / "src" / "zephyr").exists() and (p / "scripts").exists())
for _p in (str(_REPO_ROOT / "src"), str(_REPO_ROOT / "scripts" / "governance")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS  # noqa: E402

from zephyr.shared.security.secrets import SecretsError, get_secret_fail_closed  # noqa: E402

TC10_REPORT_RELATIVE: Final = "docs/_working/recovered_task_cards/tc10_owner_report.md"
RECEIPT_DIR_RELATIVE: Final = "data/runtime/key_rotation_receipt"
POSITION_PARAMS_RELATIVE: Final = "config/position_parameters.yaml"
_STEP5_DONE_MARKERS: Final[tuple[str, ...]] = ("已做", "已完成", "完成", "✅", "[x]")
_CONFIRMED: Final = "confirmed"
# G1 叫核对必换/建议换键名清单（tc10_owner_report.md 步骤5 行 + 裁定#392 同口径）；
# 仅键名常量，无值——值一律运行时经 secrets 通道读取。
KEY_ROTATION_CHECK_KEYS: Final[tuple[str, ...]] = (
    "OKX_ACCESS_KEY",
    "OKX_SECRET_KEY",
    "OKX_PASSPHRASE",
    "IFIND_TOKEN",
    "BAIDU_PAN_TOKEN",
    "TUSHARE_TOKEN",
)


def _now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


def _gate(gate_id: str, verdict: str, evidence: str) -> dict[str, Any]:
    return {"gate_id": gate_id, "verdict": verdict, "evidence": evidence, "checked_at": _now_iso()}


def _read_step5_status(report_path: Path) -> str:
    """抽取 tc10 报告步骤5 行原文（首个含"步骤5"的表格行）。"""
    if not report_path.is_file():
        return ""
    for line in report_path.read_text(encoding="utf-8").splitlines():
        if "步骤5" in line or "步骤 5" in line:
            return line
    return ""


def verify_key_presence(keys: tuple[str, ...] = KEY_ROTATION_CHECK_KEYS) -> list[dict[str, str]]:
    """叫核对执行体：逐键 fail-closed 校验，输出只含键名与状态，绝不回传值。

    校验通道=get_secret_fail_closed（F105 访问器：缺失/空/占位符一律 SecretsError，
    且异常详情里值已经 sanitize_secret 脱敏）。
    """
    results: list[dict[str, str]] = []
    for key in keys:
        try:
            get_secret_fail_closed(key)
            results.append({"key": key, "status": "ok"})
        except SecretsError as exc:
            results.append({"key": key, "status": f"fail: {exc.error_code}"})
    return results


def check_g1_key_rotation(
    report_path: Path | None = None,
    receipt_dir: Path | None = None,
) -> dict[str, Any]:
    """G1 密钥轮换闭环：步骤5 行完成态 AND 核对回执存在。当前态=FAIL（等 Owner，fail-closed）。"""
    report = report_path or _REPO_ROOT / TC10_REPORT_RELATIVE
    receipts = receipt_dir or _REPO_ROOT / RECEIPT_DIR_RELATIVE
    try:
        line = _read_step5_status(report)
        done = any(marker in line for marker in _STEP5_DONE_MARKERS)
        if not done:
            return _gate("G1", "FAIL", f"tc10 步骤5 行非完成态（Owner 未办或未登记）: {line[:80] or '行缺失'}")
        receipt_files = sorted(receipts.glob("*.json")) if receipts.is_dir() else []
        verified = False
        verified_name = ""
        for rf in receipt_files:
            try:
                data = json.loads(rf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if isinstance(data, dict) and data.get("verified") is True:
                verified = True
                verified_name = rf.name
                break
        if not verified:
            return _gate("G1", "FAIL", f"步骤5 行已做但核对回执缺失/未 verified（{receipts}）")
        return _gate("G1", "PASS", f"步骤5 完成态 + 核对回执 verified（{verified_name}）")
    except Exception as exc:  # noqa: BLE001 — 探针异常不伪装 PASS
        return _gate("G1", "FAIL", f"探针异常: {type(exc).__name__}: {exc}")


def _load_position_params(path: Path) -> dict[str, Any]:
    import yaml  # 仓内既有依赖

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _code_param_snapshot() -> dict[str, Any]:
    """代码常量同源快照（漂移守卫基准=daily_decision_orchestrator Final 常量）。"""
    from zephyr.strategy_pipeline.daily_decision_orchestrator import (
        BUDGET_BANDS,
        HARD_CAP,
        TRANSITION_FACTOR,
        TRANSITION_THRESHOLD,
    )

    return {
        "hard_cap": float(HARD_CAP),
        "transition": {"threshold": float(TRANSITION_THRESHOLD), "factor_low": 0.5, "factor_high": 0.7},
        "budget_bands": {k: [float(v[0]), float(v[1])] for k, v in BUDGET_BANDS.items()},
    }


def effective_hard_cap(params: dict[str, Any]) -> float:
    """仓位上限消费口径：未经 Owner confirmed 一律 0.0（fail-closed 不建仓）。"""
    if params.get("status") != _CONFIRMED:
        return 0.0
    sign = params.get("owner_sign") or {}
    if not str(sign.get("signed_by") or "").strip():
        return 0.0
    return float(params.get("hard_cap", 0.0))


def check_g7_position_params(params_path: Path | None = None) -> dict[str, Any]:
    """G7 仓位参数 confirmed：status==confirmed AND Owner 签发 AND 与代码常量零漂移。"""
    path = params_path or _REPO_ROOT / POSITION_PARAMS_RELATIVE
    try:
        if not path.is_file():
            return _gate("G7", "FAIL", f"仓位参数表缺失: {path}")
        params = _load_position_params(path)
        if params.get("status") != _CONFIRMED:
            return _gate("G7", "FAIL", f"status={params.get('status')!r}（等 Owner 签发，禁 AI 代签）")
        sign = params.get("owner_sign") or {}
        if not str(sign.get("signed_by") or "").strip():
            return _gate("G7", "FAIL", "status=confirmed 但 owner_sign.signed_by 空（签发不完整）")
        drift = _param_drift(params, _code_param_snapshot())
        if drift:
            return _gate("G7", "FAIL", f"参数表与代码常量漂移: {drift}")
        return _gate("G7", "PASS", f"confirmed by {sign.get('signed_by')} at {sign.get('signed_at')}，与代码常量零漂移")
    except Exception as exc:  # noqa: BLE001 — 探针异常不伪装 PASS
        return _gate("G7", "FAIL", f"探针异常: {type(exc).__name__}: {exc}")


def _param_drift(params: dict[str, Any], code: dict[str, Any]) -> list[str]:
    """表值 vs 代码常量漂移项（keys 列出即 FAIL——双真源禁分叉）。"""
    drift: list[str] = []
    if float(params.get("hard_cap", -1)) != code["hard_cap"]:
        drift.append(f"hard_cap {params.get('hard_cap')} != code {code['hard_cap']}")
    for k, v in code["transition"].items():
        got = (params.get("transition") or {}).get(k)
        if got is None or float(got) != float(v):
            drift.append(f"transition.{k} {got} != code {v}")
    code_bands = code["budget_bands"]
    cfg_bands = params.get("budget_bands") or {}
    for seg, span in code_bands.items():
        got = cfg_bands.get(seg)
        if got is None or [float(got[0]), float(got[1])] != list(span):
            drift.append(f"budget_bands.{seg} {got} != code {span}")
    return drift


def run_all(
    report_path: Path | None = None, receipt_dir: Path | None = None, params_path: Path | None = None
) -> dict[str, Any]:
    """双闸联跑（输出契约=admission_gate_design.md §3：逐门一行+顶部 all_green）。"""
    gates = [
        check_g1_key_rotation(report_path, receipt_dir),
        check_g7_position_params(params_path),
    ]
    all_green = all(g["verdict"] == "PASS" for g in gates)
    return {
        "all_green": all_green,
        "note": "all_green=true 也只产出建议 Owner 签发提示，不触发任何实盘动作（design §3 输出契约）",
        "gates": gates,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TRD-A20/21 双闸机械判定（G1 密钥轮换 + G7 仓位参数 confirmed）")
    parser.add_argument("--json", action="store_true", dest="as_json", help="输出 JSON（默认人类可读）")
    parser.add_argument("--report", type=Path, default=None, help="tc10 报告路径覆盖")
    parser.add_argument("--receipt-dir", type=Path, default=None, help="核对回执目录覆盖")
    parser.add_argument("--params", type=Path, default=None, help="仓位参数表路径覆盖")
    parser.add_argument("--keys", default="", help="叫核对键名逗号清单（只验存在性，绝不打印值）")
    args = parser.parse_args(argv)
    try:
        result = run_all(args.report, args.receipt_dir, args.params)
        if args.keys:
            result["key_check"] = verify_key_presence(tuple(k.strip() for k in args.keys.split(",") if k.strip()))
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=1))
        else:
            print(f"all_green={result['all_green']}")
            for g in result["gates"]:
                print(f"  [{g['gate_id']}] {g['verdict']}: {g['evidence']}")
        return EXIT_PASS if result["all_green"] else EXIT_FINDINGS
    except Exception as exc:  # noqa: BLE001 — CLI 面 fail-loud
        print(f"check_trd_a20_a21_dual_gates error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
