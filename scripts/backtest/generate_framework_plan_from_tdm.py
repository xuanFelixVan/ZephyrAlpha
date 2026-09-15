# [BLUEPRINT] MOD-BT-197 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.generate_framework_plan_from_tdm
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] config/trading_decision_map.yaml; config/framework_plans.yaml;
#   zephyr.pf_core.strategy_engine.framework_composer; zephyr.shared.io.file_utils
# [CONSUMERS] zephyr.strategy_pipeline.fw_backtest（fw_backtest_due handler 第一步重跑本生成器）;
#   人工 CLI（月度核对）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 生成器产管禁手工维护（运维红线 5）——fw-tdm-current 块唯一写方=本脚本；
#   三套人工预设（fw-defensive/balanced/aggressive）字节级不动（文本级手术，块外零改动）；
#   写入必经 safe_write_text CAS（热文件规则）；幂等（同 TDM 状态重跑零 diff）；
#   静态模式（regime 激活态只落 provenance 元数据，composer 零权重成员不支持动态覆盖表——
#   权重合法域 (0,1] 不收 0）；TDM sleeves Σ≠1（容差 1e-4）=拒绝生成（fail-closed）
# [MODIFY-GUARD] tests/backtest/test_generate_framework_plan_from_tdm.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError: TDM sleeves 缺失/重复/Σ≠1/写后自校验失败/CAS 冲突
# [TESTS] tests/backtest/test_generate_framework_plan_from_tdm.py
# [A_module] module_id=MOD-BT-197 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fw-tdm-current 整装方案生成器——TDM PP-001 sleeves → config/framework_plans.yaml（断桥①桥件）。

断桥本体（S11 挖矿 §1.3）: auto_mount 挂图写的是 TDM portfolio_plan.sleeves，而整装回测
runner 只读 config/framework_plans.yaml——两套权重真源不通，挂图策略永不参与整装回测。
本脚本=唯一桥：读 TDM sleeves（真源，auto_mount only-add 已保 Σ=1）→ 生成/替换
framework_plans.yaml 中 plan_id=fw-tdm-current 块（其余内容字节级不动）。

幂等策略: 渲染纯确定性（权重 6 位定点微单位整数化，禁时间戳进内容；唯一随机源=TDM 内容
sha 前 12 位）。重跑=渲染结果与现状逐字节比对，相同则零写（"重放零 diff"）。
写后自校验: load_framework_plans 全文件重解析（含三套预设一并验证）+ fw-tdm-current 权重
逐位比对 + 二次渲染零 diff 断言。

用法:
    python scripts/backtest/generate_framework_plan_from_tdm.py            # 生成/更新
    python scripts/backtest/generate_framework_plan_from_tdm.py --check    # 只报告不写
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

TDM_PATH = ROOT / "config" / "trading_decision_map.yaml"
PLANS_PATH = ROOT / "config" / "framework_plans.yaml"
PLAN_ID = "fw-tdm-current"
_SUM_TOLERANCE = 1e-4  # TDM 侧求和容差（auto_mount round(6) 舍入余量）
_WEIGHT_UNIT = 1_000_000  # 6 位定点微单位（渲染与求和全整数化，杜绝浮点尾差）

_BLOCK_HEAD_RE = re.compile(rf"(?m)^  - plan_id: {PLAN_ID}$")
_ANY_PLAN_HEAD_RE = re.compile(r"(?m)^  - plan_id: ")


def load_sleeves(tdm_path: str | Path | None = None) -> tuple[list[dict[str, Any]], str]:
    """读 TDM portfolio_plan.sleeves（真源）。返回 (sleeves, tdm 文本 sha 前 12 位)。

    Raises:
        RuntimeError: TDM 缺失 / 无 portfolio_plan.sleeves / strategy_ref 重复 / Σ≠1。
    """
    import yaml

    path = Path(tdm_path) if tdm_path else TDM_PATH
    if not path.exists():
        raise RuntimeError(f"TDM 缺失: {path}")
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    sleeves = (data.get("portfolio_plan") or {}).get("sleeves") or []
    if not sleeves:
        raise RuntimeError(f"TDM 无 portfolio_plan.sleeves: {path}")
    refs = [str(s.get("strategy_ref", "")) for s in sleeves]
    dupes = sorted({r for r in refs if refs.count(r) > 1})
    if dupes:
        raise RuntimeError(f"TDM sleeves strategy_ref 重复: {dupes}")
    total = sum(float(s.get("weight", 0.0)) for s in sleeves)
    if abs(total - 1.0) > _SUM_TOLERANCE:
        raise RuntimeError(f"TDM sleeves 权重合计≠1: {total:.6f}（容差 {_SUM_TOLERANCE}）")
    return sleeves, hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def normalize_weights(sleeves: list[dict[str, Any]]) -> list[tuple[str, int, Any]]:
    """sleeves → [(strategy_ref, 微单位权重, activation_state)]，Σ 恰=1e6（整数化余量归大权重）。

    余量调整目标=最大权重 sleeve（平局取首个）——确定性选择，禁随机/时间因素。
    """
    items: list[tuple[str, int, Any]] = []
    for s in sleeves:
        ref = str(s.get("strategy_ref", ""))
        w_u = int(round(float(s.get("weight", 0.0)) * _WEIGHT_UNIT))
        items.append((ref, w_u, s.get("activation_state")))
    residual = _WEIGHT_UNIT - sum(w for _, w, _ in items)
    if residual:
        j = max(range(len(items)), key=lambda i: (items[i][1], -i))
        ref, w, act = items[j]
        items[j] = (ref, w + residual, act)
    return items


def _fmt_activation(act: Any) -> str:
    """激活态渲染（null→全段；list→+ 连接；禁自由文本）。"""
    if not act:
        return "全段"
    if isinstance(act, (list, tuple)):
        return "+".join(str(a) for a in act)
    return str(act)


def render_plan_block(
    sleeves: list[dict[str, Any]], tdm_sha12: str, tdm_rel_path: str = "config/trading_decision_map.yaml"
) -> str:
    """渲染 fw-tdm-current 计划块（纯确定性；YAML 文本与 plans 缩进体系对齐）。"""
    items = normalize_weights(sleeves)
    lines: list[str] = [
        f"  - plan_id: {PLAN_ID}",
        "    name_zh: TDM 整装方案（当前挂图 PP-001，生成器产物）",
        "    risk_profile: balanced",
        "    description: >-",
        "      生成器产物（scripts/backtest/generate_framework_plan_from_tdm.py，禁手工维护）——",
        f"      真源={tdm_rel_path} portfolio_plan.sleeves（PP-001，sha12={tdm_sha12}）；",
        "      regime 激活态为静态模式：activation 只落 role/x_tdm_provenance 记录，",
        "      不生成 regime_overrides（composer 权重合法域 (0,1] 不收 0，动态化待其支持零权重成员）。",
        "    weights:",
    ]
    for ref, w_u, act in items:
        lines.append(f"      - strategy_id: {ref}")
        lines.append(f"        weight: {w_u / _WEIGHT_UNIT:.6f}")
        lines.append(f'        role: "TDM sleeve（activation: {_fmt_activation(act)}）"')
    lines += [
        "    x_tdm_provenance:",
        f"      source: {tdm_rel_path}",
        f"      source_sha256_12: {tdm_sha12}",
        "      generated_by: scripts/backtest/generate_framework_plan_from_tdm.py",
        "      plan_ref: PP-001",
        "      static_mode: true",
        "      activation_state:",
    ]
    for ref, _, act in items:
        act_str = "null" if not act else "[" + ", ".join(str(a) for a in (act if isinstance(act, (list, tuple)) else [act])) + "]"
        lines.append(f"        - {{strategy_ref: {ref}, activation: {act_str}}}")
    return "\n".join(lines) + "\n"


def _merge_block(existing_text: str, block: str) -> str:
    """文本级手术：fw-tdm-current 块原位替换；不存在则文件尾追加（块外字节零改动）。"""
    m = _BLOCK_HEAD_RE.search(existing_text)
    if not m:
        base = existing_text if existing_text.endswith("\n") else existing_text + "\n"
        return base + "\n" + block
    start = m.start()
    nxt = _ANY_PLAN_HEAD_RE.search(existing_text, m.end())
    end = nxt.start() if nxt else len(existing_text)
    return existing_text[:start] + block + existing_text[end:]


def generate(
    plans_path: str | Path | None = None,
    tdm_path: str | Path | None = None,
    check: bool = False,
) -> dict[str, Any]:
    """生成/更新 fw-tdm-current（幂等：同 TDM 状态重跑零 diff 零写）。返回执行摘要。"""
    from zephyr.pf_core.strategy_engine.framework_composer import load_framework_plans
    from zephyr.shared.io.file_utils import safe_write_text

    plans_p = Path(plans_path) if plans_path else PLANS_PATH
    sleeves, tdm_sha12 = load_sleeves(tdm_path)
    tdm_rel = Path(tdm_path).name if tdm_path else "config/trading_decision_map.yaml"
    if tdm_path:
        tdm_rel = str(Path(tdm_path))
    block = render_plan_block(sleeves, tdm_sha12, tdm_rel)

    if not plans_p.exists():
        raise RuntimeError(f"整装方案配置缺失: {plans_p}")
    before = plans_p.read_text(encoding="utf-8")
    after = _merge_block(before, block)
    changed = after != before

    summary: dict[str, Any] = {
        "plan_id": PLAN_ID,
        "changed": changed,
        "members": len(sleeves),
        "sum_weight": round(sum(w for _, w, _ in normalize_weights(sleeves)) / _WEIGHT_UNIT, 6),
        "tdm_sha256_12": tdm_sha12,
        "plans_path": str(plans_p),
        "written": False,
    }
    if changed and check:
        summary["action"] = "check_only（--check：有变化未写）"
        return summary
    if changed:
        result = safe_write_text(
            plans_p, after,
            expected_base_sha256=hashlib.sha256(before.encode("utf-8")).hexdigest(),
            newline="\n",
        )
        if not getattr(result, "written", True):
            raise RuntimeError("safe_write_text 未确认写入（CAS 未落地）——fw-tdm-current 不落盘")
        summary["written"] = True

    # 写后自校验（无论本次是否写入都执行——含 --check 与幂等重放路径）：
    # ① 全文件（含三套人工预设）可被 composer loader 解析；② fw-tdm-current 权重逐位一致；
    # ③ 二次渲染与文件现状零 diff（幂等性自证）。
    verify = _verify(plans_p, sleeves, tdm_sha12, tdm_rel)
    summary["verify"] = verify
    if not verify["ok"]:
        raise RuntimeError(f"写后自校验失败: {verify['errors']}")
    summary["action"] = "written" if summary["written"] else "no_change（幂等重放零 diff）"
    return summary


def _verify(
    plans_p: Path, sleeves: list[dict[str, Any]], tdm_sha12: str, tdm_rel: str
) -> dict[str, Any]:
    """三重自校验（见 generate 注释）。返回 {ok, errors, plan_weights}。"""
    from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan, load_framework_plans

    errors: list[str] = []
    try:
        load_framework_plans(plans_p)
    except Exception as exc:  # noqa: BLE001——校验函数自身收集错误不抛
        errors.append(f"全文件解析失败: {type(exc).__name__}: {exc}")
        return {"ok": False, "errors": errors, "plan_weights": {}}
    try:
        plan = get_framework_plan(PLAN_ID, plans_p)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"fw-tdm-current 不存在/不可解析: {exc}")
        return {"ok": False, "errors": errors, "plan_weights": {}}
    expected = {ref: w / _WEIGHT_UNIT for ref, w, _ in normalize_weights(sleeves)}
    actual = {w.strategy_id: w.weight for w in plan.weights}
    plan_weights = {k: round(v, 6) for k, v in actual.items()}
    if set(expected) != set(actual):
        errors.append(f"成员集不一致: 生成器={sorted(expected)} vs 文件={sorted(actual)}")
    for ref, w in expected.items():
        if abs(actual.get(ref, -1.0) - w) > 1e-9:
            errors.append(f"权重漂移 {ref}: 文件={actual.get(ref)} 期望={w}")
    text = plans_p.read_text(encoding="utf-8")
    if _merge_block(text, render_plan_block(sleeves, tdm_sha12, tdm_rel)) != text:
        errors.append("二次渲染非零 diff（幂等破坏）")
    return {"ok": not errors, "errors": errors, "plan_weights": plan_weights}


def main() -> int:
    ap = argparse.ArgumentParser(description="fw-tdm-current 生成器（TDM sleeves→framework_plans）")
    ap.add_argument("--check", action="store_true", help="只报告是否有变化，不写")
    ap.add_argument("--tdm", default=None, help="TDM 路径覆盖（默认 config/trading_decision_map.yaml；测试注入用）")
    ap.add_argument("--plans", default=None, help="framework_plans 路径覆盖（测试注入用）")
    args = ap.parse_args()
    out = generate(plans_path=args.plans, tdm_path=args.tdm, check=args.check)
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
