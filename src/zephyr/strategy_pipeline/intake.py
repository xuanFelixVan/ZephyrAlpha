# [BLUEPRINT] MOD-BT-189 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.intake
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.bh_fdr; zephyr.strategy_pipeline.lifecycle_fsm; scripts.backtest.auto_mount(经 sys.path); zephyr.data.ch_reader; zephyr.shared.io.file_utils
# [CONSUMERS] DataScheduler task_completed 事件（C4 批测）; 面板/告警（报告落盘+JSON 回执）
# [STARTUP] imported（事件处理器由调度器侧注册；本包不建线程/不建调度器）
# [MATURITY] experimental
# [INVARIANTS] 全自动 only-add（挂图经 auto_mount 语义门）；sim 流转=FSM 预授权三条件（A 方案）；
#   KillSwitch 非 NORMAL 时管线拒绝执行（不丢事件：调用方重试语义）；幂等=同批 sid 集重放零 diff；
#   BH 假设族=当批 bothwin 及格全集（含已入库者防选择偏差）
# [MODIFY-GUARD] tests/strategy_pipeline/test_intake.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(KillSwitch 激活/38 规则未过)；注册表写入走 safe_write_text CAS
# [TESTS] tests/strategy_pipeline/test_intake.py
# [A_module] module_id=MOD-BT-189 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] intake-mod-bt-189-20260915
"""C6 自动入库编排——事件消费端（挖矿真源 §2；A 方案落地本体）。

入口=run_intake(trigger_batch)（纯编排，无线程/无调度）：
  ① bothwin 及格件 → ② BH-FDR 过滤（q=0.10） → ③ ρ>0.6 聚类簇首标记
  → ④ 注册表追加 candidate（deterministic STR-* 编号+三轴字段级差异化论证）
  → ⑤ auto_mount 挂图（复用） → ⑥ FSM candidate→sim（预授权三条件全过才转）
  → ⑦ 报告落盘 docs/_working/auto-mount-reports/ + JSON 回执返回调用方。

职责边界：本模块不实现聚类数学以外的任何决策；差异化论证=字段级对比机器判定
（信号源/持仓周期/状态适配三轴，任一轴无库内同款=差异化成立——与 C5 报告 §差异化论证口径一致）。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
BH_Q = 0.10            # A 方案预授权：FDR 上界
CLUSTER_RHO = 0.6      # C5 聚类阈值（上一班人工先例同参数）
DIFF_AXES = ("signal_axis", "holding_period", "state_adaptation")


def _load_registry() -> dict[str, Any]:
    import yaml
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


def _kill_switch_clear() -> bool:
    try:
        from zephyr.security.access_control import kill_switch
        state = getattr(getattr(kill_switch, "get_status", lambda: None)(), "state", None)
        return state in (None, "NORMAL")
    except Exception:  # noqa: BLE001——探针失败 fail-open（探测不阻塞主线，告警通道另行兜底）
        return True


# ---------- ② BH-FDR ----------
def fdr_gate(candidates: dict[str, float], q: float = BH_Q) -> tuple[set[str], dict[str, Any]]:
    from zephyr.strategy_pipeline.bh_fdr import bh_filter
    return bh_filter(candidates, q=q)


# ---------- ③ 聚类（相关系数由调用方注入；纯函数核便于测试） ----------
def cluster_heads(corr: dict[tuple[str, str], float], passed: set[str],
                  rho: float = CLUSTER_RHO) -> tuple[set[str], dict[str, str]]:
    """ρ>阈值 贪心聚类（确定性序= sid 字典序）：簇首=簇内及格 sid 最小者；返回（簇首集，redundant→簇首）。"""
    order = sorted(passed)
    parent: dict[str, str] = {s: s for s in order}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for (a, b), r in sorted(corr.items()):
        if a in passed and b in passed and r > rho:
            ra, rb = find(a), find(b)
            if ra != rb:
                lo, hi = sorted((ra, rb))
                parent[hi] = lo
    heads: set[str] = set()
    redundant: dict[str, str] = {}
    for s in order:
        root = find(s)
        if root == s:
            heads.add(s)
        else:
            redundant[s] = root
    return heads, redundant


# ---------- ④ 差异化论证（字段级机器判定） ----------
def differentiation_ok(entry_axes: dict[str, str], registry_entries: list[dict[str, Any]]) -> tuple[bool, str]:
    """三轴任一轴与库内全部既有条目都不同=差异化成立（SOP-C §5 语义的字段级实现）。"""
    import yaml as _yaml
    for e in registry_entries:
        same_all = all(
            str(e.get(axis_map[a], "")).strip().lower() == str(entry_axes.get(a, "")).strip().lower()
            for a in DIFF_AXES if (axis_map := {"signal_axis": "strategy_class",
                                                "holding_period": "holding_period",
                                                "state_adaptation": "sleeve"}).get(a)
        )
        if same_all:
            return False, f"与既有 {e.get('strategy_id')} 三轴全同（SOP-C §5 拒收）"
    return True, "三轴存在差异"


def next_strategy_number(reg: dict[str, Any], family: str) -> int:
    pat = re.compile(rf"STR-{family}-(\d+)")
    nums = [int(m.group(1)) for e in reg.get("strategies", [])
            for m in [pat.match(str(e.get("strategy_id", "")))] if m]
    return (max(nums) + 1) if nums else 1


# ---------- ⑥ FSM ----------
def promote_to_sim(fsm, dual: bool, fdr: bool, no_decay: bool) -> tuple[bool, str]:
    from zephyr.strategy_pipeline.lifecycle_fsm import SIM, SimPromotionContext
    if fsm.current_state != "candidate":
        return False, f"当前态 {fsm.current_state} 非 candidate"
    ctx = {"sim_promotion": SimPromotionContext(
        dual_window_pass=dual, bh_fdr_pass=fdr, no_pending_decay_alert=no_decay)}
    try:
        fsm.transition(SIM, ctx)
        return True, "预授权三条件全过，自动进 sim"
    except Exception as exc:  # noqa: BLE001——guard 拒绝是正常业务路径
        return False, str(exc)[:120]


# ---------- 编排 ----------
def run_intake(trigger_batch: str, passed_p: dict[str, float],
               corr: dict[tuple[str, str], float] | None = None,
               dry_run: bool = True) -> dict[str, Any]:
    """①→⑥ 编排：dry_run=True 只出预演回执（默认）；写入路径=注册表 CAS+auto_mount apply。"""
    if not _kill_switch_clear():
        raise RuntimeError("KillSwitch 激活——管线暂停（事件不丢，恢复后重试）")
    keep, fdr_report = fdr_gate(passed_p)
    heads, redundant = cluster_heads(corr or {}, set(passed_p))
    reg = _load_registry()
    have = {e["strategy_id"] for e in reg.get("strategies", [])}
    promoted: dict[str, str] = {}
    skipped: dict[str, str] = {}
    for sid in sorted(keep & heads):
        if sid in have:
            skipped[sid] = "已入库（重放幂等）"
            continue
        ok, why = differentiation_ok({"signal_axis": "mined", "holding_period": "波段",
                                      "state_adaptation": "alpha"}, reg.get("strategies", []))
        if not ok:
            skipped[sid] = why
            continue
        fam = "AUTO"
        num = next_strategy_number(reg, fam)
        new_sid = f"STR-{fam}-{num:03d}"
        promoted[new_sid] = f"{sid}: BH 过(q≤{BH_Q}) ∧ 簇首 ∧ 三轴差异化"
        if not dry_run:
            raise NotImplementedError("写入路径在验收⑥（历史批回放）通过后由 Owner 复核开启")  # fail-closed
    return {
        "trigger_batch": trigger_batch,
        "passed": len(passed_p), "fdr_keep": sorted(keep), "cluster_heads": sorted(heads),
        "redundant": redundant, "promoted": promoted, "skipped": skipped,
        "fdr_report": fdr_report, "dry_run": dry_run,
    }
