# [BLUEPRINT] MOD-BT-196 | docs/03_modules/_domain_backtest/blueprint.md（成本口径对账尺，C345 前置工程件）
# [MODULE] scripts.backtest.cost_accounting_ruler
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] config/exam_scale_cost_gate.yaml（考尺冻结档真源，只读）；ast（字面量普查）
# [CONSUMERS] C345 数值整改波（⚑-2 B案生效后的另波施工）；夜总攻 C 组车道验收
# [STARTUP] on-demand（CLI 一次性对账；无常驻）
# [MATURITY] experimental
# [INVARIANTS] 只读对账零数值改动（C345 数值改动等 ⚑-2 生效后另波，本尺只量不改）；
#   普查表=显式在册清单（本文件 COST_SITES），禁止全仓正则盲扫误报；
#   判定语义=「基线外漂移」：与 2026-09-30 普查基线逐项比对，已知差异（C345 四件）在册=绿
#   （红证固化语义），基线外漂移=红 exit 1；市场/费率政策变更须先改本尺普查表+裁定登记（禁散改）。
# [MODIFY-GUARD] tests/backtest/test_cost_accounting_ruler.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(0)=对账通过（含已知差异在册）；SystemExit(1)=基线外漂移（新差异/已知差异消失=有人动了数值）；
#   RuntimeError=普查目标文件缺失/解析失败（fail-closed）
# [TESTS] tests/backtest/test_cost_accounting_ruler.py
# [A_module] module_id=MOD-BT-COST-RULER | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""成本口径对账尺（C345 四件前置工程件，2026-09-30 夜总攻二 C 组车道）。

四件红证的机读固化（对账尺只量不改，数值改动=⚑-2 B案生效后另波）：
  ①手续费 5 处重复：同一费率字面量 Decimal("0.0000854")（万0.854，#233 裁定）散落 5 个定义点
    （matching_logic / transaction_cost_optimizer / t0_cost_model / simulation_broker / pnl_calculator）；
  ②印花税两侧过期：考尺引擎 _c4_engine STAMP_BP=10.0（2010-2023-08 旧卖侧千1口径）
    vs 实盘/撮合侧 0.0005（万5，2023-08-28 起法定）——两侧数值不等且考尺侧为过期口径；
  ③c* 无规模参数：_c4_engine._net_line 成本线 = f(turnover) 单变量，无 participation/ADV 规模维
    ⇒ "验收门恒过"结构性风险（exam gate 判定面已由 scale_gate 补 participation_ref，引擎线未接）；
  ④阶梯双真源：考尺滑点阶梯 config/exam_scale_cost_gate.yaml tiers_bp=[0,5,10,20,40]
    vs 逐笔标定阶梯 cost_model_calibration ADV 五分位（2.34~7.24bp）——两套阶梯并存各自为政。

对账口径：
  R1 五处佣金字面量同值（漂移=红）
  R2 实盘侧印花税三处同值=万5（漂移=红）
  R3 考尺引擎冻结档 SLIPPAGE_BP ∈ 冻结册 tiers_bp（脱档=红）
  R4 C345 已知差异仍在册且数值未动（差异消失=有人改了数值未走裁定=红；差异扩大=红）
  R5 vectorized_engine 禁字面量复述佣金（第二字面量=红）
  R6 考尺成本线无规模参数（如实红证：签名含规模维=本尺需更新+另波接线核）

用法：
  python scripts/backtest/cost_accounting_ruler.py            # 全量对账（exit 0/1）
  python scripts/backtest/cost_accounting_ruler.py --json out # 机读报告落盘（.runtime/tmp 之下）
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[2]

# ---- 普查基线（2026-09-30 C 组车道实测入册；改表=裁定登记，禁散改）----

#: ①佣金字面量五处（同值 0.0000854=万0.854，#233 裁定 2026-08-21）；unit=decimal|bps
COMMISSION_SITES: tuple[dict[str, str], ...] = (
    {
        "file": "src/zephyr/backtest/core/matching_logic.py",
        "symbol": "COMMISSION_RATE",
        "unit": "decimal",
        "role": "truth_source",
    },
    {
        "file": "src/zephyr/ex_sor/services/transaction_cost_optimizer.py",
        "symbol": "FeeSchedule.commission_rate_bps",
        "unit": "bps",
        "role": "sor_fee_schedule",
    },
    {
        "file": "src/zephyr/ex_sor/services/t0_cost_model.py",
        "symbol": "T0CostConfig.commission_rate",
        "unit": "decimal",
        "role": "t0_cost",
    },
    {
        "file": "src/zephyr/governance/adapters/simulation_broker.py",
        "symbol": "commission_rate",
        "unit": "decimal",
        "role": "sim_broker",
    },
    {
        "file": "src/zephyr/trading/pnl_calculator.py",
        "symbol": "FeeConfig.commission_rate",
        "unit": "decimal",
        "role": "pnl",
    },
)
COMMISSION_BASELINE = "0.0000854"

#: ②印花税：实盘侧三处=万5；考尺侧=冻结土规 10bp（过期，C345②红证）
STAMP_SPOT_SITES: tuple[dict[str, str], ...] = (
    {"file": "src/zephyr/backtest/core/matching_logic.py", "symbol": "STAMP_TAX_RATE", "unit": "decimal"},
    {
        "file": "src/zephyr/ex_sor/services/transaction_cost_optimizer.py",
        "symbol": "FeeSchedule.stamp_duty_rate_bps",
        "unit": "bps",
    },
    {
        "file": "src/zephyr/ex_sor/services/t0_cost_model.py",
        "symbol": "T0CostConfig.stamp_duty_rate",
        "unit": "decimal",
    },
)
STAMP_SPOT_BASELINE = "0.0005"  # 万5（bps 单位面=5，统一折小数比对）
EXAM_ENGINE_FILE = "scripts/backtest/translated/_c4_engine.py"
EXAM_STAMP_BP_BASELINE = 10.0  # C345② 已知过期值（红证固化：动它=须裁定）
EXAM_COMMISSION_BP_BASELINE = 2.5  # C345① 关联已知差异（冻结土规与实盘费率并存）
EXAM_SLIPPAGE_BP_BASELINE = 5.0

#: ③考尺成本线函数（规模维缺席红证面）
NET_LINE_FUNC = "_net_line"
SCALE_PARAM_CANDIDATES = ("participation", "adv", "scale", "notional")

#: ④阶梯双真源第二真源（逐笔标定件；存在性+口径注记面）
CALIBRATION_HINTS = ("cost_model_calibration",)


# ---- 解析（AST 字面量级，禁正则散扫）----


def _extract_decimal_assigns(tree: ast.AST) -> dict[str, str]:
    """module 级 Assign/AnnAssign → {name: Decimal 字面量文本}（只取 Decimal(...) 直赋）。"""
    out: dict[str, str] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if value is None:
            continue
        # Decimal("0.854") / Decimal('0.0000854')
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "Decimal":
            if value.args and isinstance(value.args[0], ast.Constant) and isinstance(value.args[0].value, str):
                lit = value.args[0].value
                for t in targets:
                    if isinstance(t, ast.Name):
                        out[t.id] = lit
    return out


def _extract_class_default(tree: ast.AST, cls: str, field: str) -> str | None:
    """类字段默认值里的 Decimal 字面量（dataclass frozen 配置面）。"""
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == cls:
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                    v = stmt.value
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "Decimal":
                        if v.args and isinstance(v.args[0], ast.Constant) and isinstance(v.args[0].value, str):
                            if stmt.target.id == field:
                                return v.args[0].value
                if isinstance(stmt, ast.Assign) and stmt.value is not None:
                    v = stmt.value
                    if (
                        isinstance(v, ast.Call)
                        and isinstance(v.func, ast.Name)
                        and v.func.id == "Decimal"
                        and v.args
                        and isinstance(v.args[0], ast.Constant)
                        and isinstance(v.args[0].value, str)
                        and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Name)
                        and stmt.targets[0].id == field
                    ):
                        return v.args[0].value
    return None


def _extract_init_kwdefault(tree: ast.AST, param: str, *, cls_hint: str | None = None) -> str | None:
    """__init__ 签名 kw 默认值里的 Decimal 字面量（__init__(self, p: Decimal = Decimal("x")) 面）。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            if cls_hint is not None:
                parents = getattr(node, "_parents", None)
            defaults = list(node.args.defaults) + list(node.args.kw_defaults)
            posargs = [a for a in node.args.args + node.args.posonlyargs if a.arg != "self"]
            names = [a.arg for a in posargs] + [a.arg for a in node.args.kwonlyargs]
            # defaults 对齐：posargs 尾部 n_default 个 + kwonly 逐位（None=无默认）
            n_pos_default = len(node.args.defaults)
            aligned = [None] * (len(posargs) - n_pos_default) + list(node.args.defaults) + list(node.args.kw_defaults)
            for name, d in zip(names, aligned, strict=False):
                if name != param or d is None:
                    continue
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Name) and d.func.id == "Decimal":
                    if d.args and isinstance(d.args[0], ast.Constant) and isinstance(d.args[0].value, str):
                        return d.args[0].value
    return None


def _read_site_value(site: dict[str, str], tree: ast.AST) -> str | None:
    """按 site 符号形态取值：Module 常量 / Class.字段 / __init__ 参数默认。"""
    sym = site["symbol"]
    if "." in sym:
        cls, field = sym.split(".", 1)
        return _extract_class_default(tree, cls, field)
    mod = _extract_decimal_assigns(tree).get(sym)
    if mod is not None:
        return mod
    return _extract_init_kwdefault(tree, sym)


def _normalize_site(site: dict[str, str], raw: str | None) -> str | None:
    """单位归一到小数（bps 面除以 1e4），输出可比文本。"""
    if raw is None:
        return None
    val = float(raw)
    if site.get("unit") == "bps":
        val = val / 10000.0
    return format(val, ".10f").rstrip("0")


def _read_module(rel: str) -> ast.AST:
    p = _REPO / rel
    if not p.exists():
        raise RuntimeError(f"对账目标缺失（fail-closed）: {rel}")
    return ast.parse(p.read_text(encoding="utf-8"), filename=rel)


def _bps_to_decimal_text(bps: str | float) -> str:
    """bps 文本→小数文本（统一比对单位：0.854bps→0.0000854；5bps→0.0005）。"""
    return format(float(bps) / 10000.0, ".10f").rstrip("0")


def _norm_decimal(txt: str) -> str:
    return format(float(txt), ".10f").rstrip("0")


# ---- 普查项实现 ----


def r1_commission_five_sites() -> dict[str, Any]:
    """①佣金五处字面量同值对账。"""
    found: dict[str, str | None] = {}
    for site in COMMISSION_SITES:
        tree = _read_module(site["file"])
        raw = _read_site_value(site, tree)
        found[site["file"]] = _normalize_site(site, raw)
    drift = {f: v for f, v in found.items() if v is None or v != _norm_decimal(COMMISSION_BASELINE)}
    return {
        "id": "R1-commission-five-sites",
        "finding": "C345① 手续费 5 处重复（同值字面量散落 5 定义点）",
        "baseline": COMMISSION_BASELINE,
        "measured": found,
        "pass": not drift,
        "note": "重复本身在册为已知（收敛=另波单一真源改造）；本尺断言五处同值不漂移",
    }


def r2_stamp_spot_side() -> dict[str, Any]:
    """②实盘侧印花税三处同值=万5。"""
    found: dict[str, str | None] = {}
    for site in STAMP_SPOT_SITES:
        tree = _read_module(site["file"])
        raw = _read_site_value(site, tree)
        found[site["file"]] = _normalize_site(site, raw)
    drift = {f: v for f, v in found.items() if v is None or v != _norm_decimal(STAMP_SPOT_BASELINE)}
    return {
        "id": "R2-stamp-spot-side",
        "finding": "C345② 实盘/撮合侧印花税口径（万5 法定）三处同值",
        "baseline": STAMP_SPOT_BASELINE,
        "measured": found,
        "pass": not drift,
        "note": "考尺侧 10bp 过期差异在 R4 单列（红证固化）",
    }


def _extract_numeric_assigns(tree: ast.AST) -> dict[str, float]:
    """module 级 Assign/AnnAssign → {name: float}（裸数值字面量，考尺冻结土规常量面）。"""
    out: dict[str, float] = {}
    for node in tree.body:
        targets: list[ast.expr] = []
        value: ast.expr | None = None
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        if (
            isinstance(value, ast.Constant)
            and isinstance(value.value, (int, float))
            and not isinstance(value.value, bool)
        ):
            for t in targets:
                if isinstance(t, ast.Name):
                    out[t.id] = float(value.value)
    return out


def _read_exam_constants() -> dict[str, float]:
    tree = _read_module(EXAM_ENGINE_FILE)
    assigns = _extract_numeric_assigns(tree)
    out: dict[str, float] = {}
    for name, key in (
        ("COMMISSION_BP", "commission_bp"),
        ("STAMP_BP", "stamp_bp"),
        ("SLIPPAGE_BP", "slippage_bp"),
    ):
        raw = assigns.get(name)
        if raw is None:
            raise RuntimeError(f"{EXAM_ENGINE_FILE} 缺 {name}（fail-closed：冻结土规常量失踪）")
        out[key] = float(raw)
    return out


def r3_exam_tier_in_frozen_gate(gate: dict[str, Any]) -> dict[str, Any]:
    """③考尺默认滑点档 ∈ 冻结册 tiers_bp（脱档=引擎与考尺口径断裂）。"""
    tiers = [float(t) for t in gate["cost_gate"]["tiers_bp"]]
    slip = _read_exam_constants()["slippage_bp"]
    return {
        "id": "R3-exam-slippage-in-frozen-tiers",
        "finding": "考尺引擎默认滑点档须落在冻结册五档内",
        "measured": {"slippage_bp": slip, "tiers_bp": tiers},
        "pass": slip in tiers,
        "note": "阶梯双真源并存=C345④ 已知（收敛=另波）；本尺只断言默认档不脱册",
    }


def r4_known_diffs_stable() -> dict[str, Any]:
    """④C345 已知差异红证固化：考尺 2.5bp/10bp 数值未动（动=未经裁定的暗改=红）。"""
    c = _read_exam_constants()
    expected = {"commission_bp": EXAM_COMMISSION_BP_BASELINE, "stamp_bp": EXAM_STAMP_BP_BASELINE}
    drift = {k: {"expected": v, "actual": c[k]} for k, v in expected.items() if abs(c[k] - v) > 1e-12}
    return {
        "id": "R4-c345-known-diffs-stable",
        "finding": "C345①② 考尺侧已知差异数值冻结（改动须裁定#通道，本尺锁值）",
        "measured": c,
        "expected": expected,
        "drift": drift,
        "pass": not drift,
        "note": "差异本身=在册红证（owner gate C345）；本尺防的是数值被静默改",
    }


def r6_net_line_scale_param_absent() -> dict[str, Any]:
    """⑥考尺成本线无规模参数（C345③ 红证固化；增参=另波接线+本尺同步更新）。"""
    tree = _read_module(EXAM_ENGINE_FILE)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == NET_LINE_FUNC:
            params = [a.arg.lower() for a in node.args.args + node.args.kwonlyargs]
            hit = [p for p in params if any(h in p for h in SCALE_PARAM_CANDIDATES)]
            return {
                "id": "R6-net-line-no-scale-param",
                "finding": "C345③ c* 无规模参数致验收门恒过（结构性红证固化）",
                "measured": {"params": params},
                "pass": not hit,
                "note": "pass=现状如实（规模维缺席在册）；接线规模维=⚑-2 生效后另波，届时本尺改判据",
            }
    raise RuntimeError(f"{EXAM_ENGINE_FILE} 缺 {NET_LINE_FUNC}（fail-closed）")


def r5_vectorized_no_literal() -> dict[str, Any]:
    """⑤vectorized_engine 佣金同源引用（第二字面量=红）。"""
    rel = "src/zephyr/backtest/implementations/vectorized_engine.py"
    tree = _read_module(rel)
    literals = _extract_decimal_assigns(tree)
    bad = {k: v for k, v in literals.items() if "COMMISSION" in k.upper()}
    return {
        "id": "R5-vectorized-single-source",
        "finding": "佣金单一真源=matching_logic（vectorized_engine 禁字面量复述）",
        "measured": {"module_level_commission_literals": bad},
        "pass": not bad,
        "note": "真源治理声明见 BacktestConfig.commission_rate docstring",
    }


def run_ruler(repo_root: Path | None = None) -> dict[str, Any]:
    """全量对账：checks 列表 + overall（全部 pass 才绿）。"""
    global _REPO
    if repo_root is not None:
        _REPO = repo_root
    import yaml

    gate_path = _REPO / "config" / "exam_scale_cost_gate.yaml"
    gate = yaml.safe_load(gate_path.read_text(encoding="utf-8"))
    checks = [
        r1_commission_five_sites(),
        r2_stamp_spot_side(),
        r3_exam_tier_in_frozen_gate(gate),
        r4_known_diffs_stable(),
        r5_vectorized_no_literal(),
        r6_net_line_scale_param_absent(),
    ]
    return {
        "schema": "cost_accounting_ruler/report-1",
        "generated_for": "C345（夜总攻二 C 组车道 st-nightsweep2-nc-20260930）",
        "baseline_date": "2026-09-30",
        "checks": checks,
        "all_pass": all(c["pass"] for c in checks),
        "disclaimer": "对账尺只量不改；C345 数值改动=⚑-2 B案生效后另波（裁定#435 通道）",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="成本口径对账尺（C345 四件红证固化，只量不改）")
    ap.add_argument("--json", type=Path, default=None, help="机读报告落盘路径（建议 .runtime/tmp/ 之下）")
    args = ap.parse_args()
    report = run_ruler()
    lines = []
    for c in report["checks"]:
        lines.append(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['id']} — {c['finding']}")
    lines.append(f"ALL_PASS={report['all_pass']}")
    print("\n".join(lines))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report -> {args.json}")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
