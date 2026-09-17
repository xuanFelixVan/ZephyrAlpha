# [BLUEPRINT] MOD-BT-198 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.strategy_pipeline.fw_backtest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.pipeline_events（journal/告警原语，import 复用非修改）;
#   zephyr.backtest.core.decision_gate（三段门控+风险准入判定源，只调不改）; zephyr.backtest.core.walk_forward
#   （折切分件）; zephyr.backtest.core.metrics（分段指标/DSR 复算，同一真源）;
#   zephyr.pf_core.strategy_engine.framework_composer; zephyr.pf_core.strategy_engine.translated_strategy_adapter;
#   scripts/backtest/generate_framework_plan_from_tdm（子进程）; scripts/backtest/print_regime_history（子进程，regime 供给）
# [CONSUMERS] scripts/backtest/auto_mount.py（挂图落地后 emit_fw_backtest_due）;
#   管线 CLI（python -m zephyr.strategy_pipeline.fw_backtest run）
# [STARTUP] imported（本模块不建线程/不建调度器；重活=子进程隔离+超时）
# [MATURITY] experimental
# [INVARIANTS] 契约钉死 run_fw_backtest_due(event: dict) -> dict；事件不丢（journal 先落，
#   成功才出队，失败留档计 attempts 毒丸告警）；重活子进程隔离（生成器/回测/regime 印制均
#   subprocess+超时，禁长活阻塞挂图进程主流程）；证据包必含 plan 身份/面板对账/核心指标/
#   bt-fw 产物路径/时间戳（验收五要素）+ 执行链六要素（换手实测/标的池幸存者偏差披露/
#   现金账本闭合/目标权重 Σ→1 归一统计/拒单分类/未建模清单 #24）；标的池必 PIT 窗口口径
#   （禁 valid_to IS NULL 期末快照=幸存者偏差）；幂等=plan 指纹（权重+TDM sha）不变且旧证据
#   acceptance 每道闸键（ok/risk_admitted/cash_closure_admitted/gate_passed）逐条显式 True
#   →跳过重跑（force=True 可越过，缺任一键=该闸当时未接线，必须重跑复评）；语义失败（对账超
#   容差/空净值/组合完整性不过：未兑现 α 占方案
#   >framework_composer.DEAD_MEMBER_ALPHA_SHARE_LIMIT 或无
#   dead_weight_disclosed 披露；现金账本不闭合或无 cash_ledger_reconciliation 披露）不重试
#   ——落证据包+ERROR
#   告警+消费出队（同输入重跑结果必然相同，重试无意义）；瞬时故障（生成器 rc≠0/CH 不可达/
#   异常）上抛留 journal 等重放；
#   H5-B：acceptance 另要求三段决策门控 overall_passed（判定器=zephyr.backtest.core
#   .decision_gate.DecisionGate，阈值零自造）——IS/WFA/OOS 证据取本 run 同一条实测净值的
#   时间切片（口径=窗口内零再拟合的锁定账簿稳定性/退化考核，非参数拟合内外；真 fit-window
#   IS 属 TDM 侧欠账），净值切不出 IS+≥2 完整折即"缺证据"按 fail-closed 判拒；
#   H5-D：引擎/撮合侧 fail-open 降级在 run 期经 logging 出声归类计数，落
#   run.guard_degradation_ledger + acceptance.degraded_guards 并逐条 WARN——只做可见性不新增
#   否决权（是否升格为否决属 Owner 门位），计数 0 仅表示"本次未听见"，不等同健康
# [MODIFY-GUARD] tests/strategy_pipeline/test_fw_backtest.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(生成器失败/方案缺失/CAS 冲突/子进程超时)——由 drain 语义保留重试
# [TESTS] tests/strategy_pipeline/test_fw_backtest.py
# [A_module] module_id=MOD-BT-198 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fw_backtest_due 自动触发件——挂图成功→整装组合回测自动跑→证据包落档（断桥③桥件）。

流程（S11 README §5 施工项 3，四步）:
  ① 重跑方案表生成器（generate_framework_plan_from_tdm，子进程）——TDM sleeves→fw-tdm-current；
  ② 幂等闸: plan 指纹（成员权重+TDM sha12）与最近一次 ok 证据包相同→跳过（返回 skipped 摘要）；
  ③ 组装参数: symbols=沪深300 窗口内成份并集（PIT，含期末已调出/退市者；#24 H3-D 反
     幸存者偏差）∪ STR 成员面板列并集（预取缓存零二次 build）；
     窗口=滚动 12 个月（payload 可覆盖）；regime 日序=regime_snapshot_history.dominant
     窗口内日序（可用则附——fw-tdm-current 无 regime_overrides 时纯披露口径，权重不变）；
  ④ run_framework_backtest → 验收（panel_reconciliation.within_tolerance ∧ equity_points>0
     ∧ 风险闸 evaluate_strategy_risk_admission ∧ 三段门控闸 DecisionGate.evaluate(IS→WFA→OOS
     +DSR，H5-B) ∧ 组合完整性闸 _evaluate_composition_integrity
     ∧ 现金账本闭合闸 _evaluate_cash_closure）
     → 证据包 JSON 落 data/backtest_artifacts/fw-auto/（fw-auto-<ts>-<fp8>.json + latest.json；
     run.* 含 #24 执行链六要素：turnover_disclosure / universe_disclosure /
     cash_ledger_reconciliation / target_weight_renormalization / skipped_fills /
     execution_model_disclosure / signal_age_disclosed，另含 H5-B staged_gate_decision
     与 H5-D guard_degradation_ledger=当次哪些风险护栏降级/未生效）；幂等短路要求旧证据
     每道闸（ok/risk_admitted/cash_closure_admitted/gate_passed）均显式放行，缺键=重跑复评。

事件语义（本班裁定留痕——pipeline_events.py 并行编辑禁令未动其文件）:
  fw_backtest_due 为重 kind（分钟级），但 pipeline_events 的 LIGHT/HEAVY 词表与
  _default_handler 分派表不含本 kind（本班不能改该文件）；故 emit_fw_backtest_due 自带
  消费路径：journal record → 子进程执行本模块 CLI → rc==0 出队 / 失败留档（attempts 语义
  与 drain 同款，≥3 毒丸告警）。若未来把 fw_backtest_due 注册进 pipeline_events 分派表，
  emit 帮手自动兼容（消费体仍是本模块 run_fw_backtest_due）。

regime 日序供给（S11 README §5 施工项 4）——精确挂法登记（主会话执行，DataScheduler 重启
属受控步骤，本班不改 tasks.yaml）:
  现状: c1_backtest.regime_snapshot_history 唯一写方=print_regime_history.py（manual CLI，
  无排班；全窗 walk-forward 逐日重印，append-only 台账）。
  建议挂点 A（首选，零新机制）: pipeline_events.wire_data_scheduler 的 _on_task_completed
  钩子里加一行 `fw_backtest.ensure_regime_snapshot()`（有数据任务完成=自然唤醒点，事件触发
  合规；staleness≤3 天零成本返回，超限只告警不阻塞——refresh=True 才印制）。
  建议挂点 B（备选）: DataScheduler tasks.yaml 增 kind=regime_snapshot_daily 事件
  （daily_kline 完成唤醒，重 kind 显式 drain 消费）。
  本班已交付: ensure_regime_snapshot()/regime_snapshot_freshness() 可直接调用；
  fw_backtest_due 证据包自动引用表新鲜度。

用法:
    python -m zephyr.strategy_pipeline.fw_backtest run --payload '{"trigger":"manual"}'
真源: docs/_working/full-auto-chain/S11_assembled_backtest/README.md §5 施工项 3/4。
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import logging
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Final

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_DIR = ROOT / "data" / "backtest_artifacts" / "fw-auto"
ARTIFACT_DIR = ROOT / "data" / "backtest_artifacts"
GENERATOR_SCRIPT = ROOT / "scripts" / "backtest" / "generate_framework_plan_from_tdm.py"
REGIME_WRITER_SCRIPT = ROOT / "scripts" / "backtest" / "print_regime_history.py"
PLAN_ID = "fw-tdm-current"
DEFAULT_TIMEOUT_S = 3600  # S11 §5 施工项 5 首值
_REGIME_STALE_DAYS = 3

_EVENT_KIND = "fw_backtest_due"

# 自动标的池基池（H3-D PIT 成份窗口查询用）
_H300_INDEX_CODE = "000300.SH"
# ClickHouse SCD-2 未失效哨兵（口径真源=zephyr.data.pit_query 的 valid_to 谓词）
_NO_EXPIRY_SENTINEL = "1900-01-01"
_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _assert_iso_date(value: str, name: str) -> str:
    """窗口日期硬校验（SQL 拼接前置闸）。

    start/end 来自事件 payload（外部可填），拼进 CH SQL 前必须是裸 ISO 日期——
    不符即抛，禁"查不出来当空池"（空池在本模块是硬失败，但畸形日期更该早爆）。
    """
    if not _ISO_DATE_RE.match(str(value or "")):
        raise RuntimeError(f"{name} 须为 YYYY-MM-DD，got {value!r}——拒绝拼接 PIT 成份查询")
    return str(value)


# ---------- 幂等指纹 ----------

def plan_fingerprint(plans_path: str | Path | None = None) -> dict[str, Any]:
    """fw-tdm-current 身份指纹：成员权重表 + TDM 源 sha12（变更即新指纹）。"""
    from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan

    plan = get_framework_plan(PLAN_ID, plans_path)
    weights = {w.strategy_id: round(w.weight, 9) for w in plan.weights}
    raw = (Path(plans_path) if plans_path else ROOT / "config" / "framework_plans.yaml").read_text(
        encoding="utf-8"
    )
    import re

    m = re.search(r"source_sha256_12: ([0-9a-f]{12})", raw)
    payload = json.dumps({"weights": weights, "tdm": m.group(1) if m else ""}, sort_keys=True)
    return {
        "plan_id": PLAN_ID,
        "weights": weights,
        "tdm_sha256_12": m.group(1) if m else None,
        "fingerprint": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12],
    }


def _latest_evidence() -> dict[str, Any] | None:
    latest = EVIDENCE_DIR / "latest.json"
    if not latest.exists():
        return None
    try:
        return json.loads(latest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# ---------- 输入组装 ----------

def default_window(today: date | None = None) -> tuple[str, str]:
    """滚动 12 个月窗口（S11 §5：start/end=近 12 个月滚动窗）。"""
    end = today or date.today()
    start = end - timedelta(days=365)
    return start.isoformat(), end.isoformat()


def _hs300_symbols(start: str, end: str) -> tuple[list[str], dict[str, Any]]:
    """沪深300 **窗口内成份并集**（PIT，纯 6 位代码）+ 幸存者偏差披露（H3-D，#24）。

    旧口径 `WHERE valid_to IS NULL` 取的是"今天还在指数里"的名字——回测窗口内被调出/
    退市的成分从未进入标的池（实测近 12 个月窗口 300 → 331，9.4% 的票整批缺席），
    等于用后视镜选股，收益/回撤系统性偏乐观。改为 SCD-2 区间与回测窗口求交，谓词与
    zephyr.data.pit_query 的 in-window 口径同源（含 1900-01-01 未失效哨兵）。

    同源关系：`_c4_engine.load_hs300/index_constituents` 已于 2026-09-18（E4 retrofit，
    c0f87635）同步为 SCD-2 窗口并集口径，与本函数同范式；"当前快照"口径已废——择时
    快照用途须显式按日查询，勿以无窗调用复辟幸存者偏差。

    Returns:
        (symbols, disclosure)——disclosure 显式给出旧口径会给多少个、差额多少，
        使"少了票"这件事在证据包里可见（禁静默）。
    """
    from zephyr.data.ch_writer import get_client_strict

    _assert_iso_date(start, "start")
    _assert_iso_date(end, "end")
    rows = get_client_strict().execute(
        "SELECT symbol_canonical, valid_to FROM c1_market.index_constituent "
        f"WHERE index_code = '{_H300_INDEX_CODE}' "
        f"AND valid_from <= toDate('{end}') "
        f"AND (valid_to IS NULL OR valid_to = toDate('{_NO_EXPIRY_SENTINEL}') "
        f"OR valid_to > toDate('{start}'))"
    )
    universe: set[str] = set()
    still_in_at_end: set[str] = set()
    for raw, valid_to in rows:
        code = (str(raw) if raw else "")[:6]
        if not code:
            continue
        universe.add(code)
        vt = "" if valid_to is None else str(valid_to)[:10]
        if vt in ("", _NO_EXPIRY_SENTINEL) or vt > end:
            still_in_at_end.add(code)
    if not universe:
        raise RuntimeError("index_constituent 沪深300 成份缺失——自动标的池不可组装")
    exited = sorted(universe - still_in_at_end)
    disclosure: dict[str, Any] = {
        "schema": "universe_disclosure/v1",
        "mode": "pit_index_window",
        "index_code": _H300_INDEX_CODE,
        "window": {"start": start, "end": end},
        "universe_n": len(universe),
        "snapshot_n": len(still_in_at_end),
        "since_exit_n": len(exited),
        "since_exit_share": round(len(exited) / len(universe), 4) if universe else None,
        "since_exit_sample": exited[:20],
        "note": (
            "窗口内曾为成份即入池（含期末已调出/退市者）；snapshot_n=旧 'valid_to IS NULL' "
            "口径会给的只数，差额即被幸存者偏差静默剔除的标的数"
        ),
    }
    return sorted(universe), disclosure


def resolve_symbols(
    start: str, end: str, base: list[str] | None = None
) -> tuple[list[str], dict[str, Any]]:
    """自动标的池=基池（默认沪深300 快照）∪ STR 成员面板列并集（预取触发缓存）。

    返回 (symbols, info)；info.str_columns_by_sid 供证据包披露各 STR 成员标的宇宙。
    """
    from zephyr.pf_core.strategy_engine.framework_composer import get_framework_plan
    from zephyr.pf_core.strategy_engine.translated_strategy_adapter import (
        is_translated_member,
        prefetch_translated_panels,
    )

    plan = get_framework_plan(PLAN_ID)
    str_ids = [w.strategy_id for w in plan.weights if is_translated_member(w.strategy_id)]
    panels = prefetch_translated_panels(str_ids, start, end)
    str_cols: set[str] = set()
    by_sid: dict[str, int] = {}
    for sid, panel in panels.items():
        cols = {str(c) for c in panel.columns}
        str_cols |= cols
        by_sid[sid] = len(cols)
    symbols_base, universe = (
        (sorted({str(s) for s in base}), {
            "schema": "universe_disclosure/v1",
            "mode": "payload_override",
            "universe_n": len(set(base or [])),
            "snapshot_n": None,
            "since_exit_n": None,
            "note": "基池由 payload.symbols 给定——PIT 成份窗口未参与，幸存者偏差由调用方承担"
            "（自动挂图路径不应给 base）",
        })
        if base
        else _hs300_symbols(start, end)
    )
    symbols = sorted(set(symbols_base) | str_cols)
    return symbols, {
        "str_members": str_ids,
        "str_columns_n": by_sid,
        "total": len(symbols),
        "universe_disclosure": universe,
    }


def load_regime_series(start: str, end: str) -> dict[str, Any]:
    """regime_snapshot_history.dominant 窗口日序（可用=附作披露口径；空/异常=静态降级）。"""
    out: dict[str, Any] = {"mode": "static", "series": None, "freshness": None, "note": ""}
    try:
        from zephyr.data.ch_writer import get_client_strict

        rows = get_client_strict().execute(
            f"SELECT trade_date, dominant FROM c1_backtest.regime_snapshot_history "
            f"WHERE trade_date >= '{start}' AND trade_date <= '{end}' ORDER BY trade_date"
        )
        out["freshness"] = regime_snapshot_freshness()
        if rows:
            series = {str(r[0])[:10]: str(r[1]) for r in rows}
            out.update({"mode": "dynamic_disclosure", "series": series,
                        "note": "fw-tdm-current 无 regime_overrides——日序仅供分段披露，权重=基准（查表语义）"})
        else:
            out["note"] = "窗口内无 regime 快照行——静态模式降级"
    except Exception as exc:  # noqa: BLE001  ——regime 供给失败降静态，不阻断整装跑
        out["note"] = f"regime 日序加载失败（静态降级）: {type(exc).__name__}: {exc}"[:160]
    return out


# ---------- 风险信号消费（车道 L：acceptance 真读 overfitting_flag/DSR/n_trials）----------

def _load_artifact_nav(run_id: str | None) -> Any:
    """读回测产物 equity_curve 重建净值序列（只读；缺文件/短序列/异常→None，禁崩主流程）。

    run_framework_backtest 落 `data/backtest_artifacts/<run_id>.json`，其 metrics 快照仅含
    overfitting_flag（引擎 sink 字段），不含 dsr/n_trials——故 S11 验收在此用同一 DSR 真源
    （metrics.calculate_full_metrics + 账本 n_trials）复算，与引擎逐位同输入同函数→零分叉。
    """
    if not run_id:
        return None
    path = ARTIFACT_DIR / f"{run_id}.json"
    if not path.exists():
        return None
    try:
        import pandas as pd

        d = json.loads(path.read_text(encoding="utf-8"))
        ec = d.get("equity_curve") or []
        if len(ec) < 2:
            return None
        nav = pd.Series({str(p["timestamp"]): float(p["equity"]) for p in ec})
        return nav.sort_index()
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _evaluate_risk_decision(result: dict, nav: Any = None) -> dict[str, Any]:
    """对整装回测结果施加回测→实盘共用风险判据（单一真源，fail-closed）。

    取值优先级：产物 metrics 若已带 dsr/n_trials 直接用（前向兼容引擎侧上收），否则用
    净值序列复算（同一 DSR 官方件 + 账本 n_trials）。overfitting_flag 取引擎产物旗标。
    最终裁决一律经 decision_gate.evaluate_strategy_risk_admission——缺失即拒，绝不静默放行。

    Args:
        result: run_framework_backtest 产物 dict。
        nav: 已载入的净值序列（None 时本函数自行按 run_id 读产物，保持可独立调用）。
    """
    from zephyr.backtest.core.decision_gate import evaluate_strategy_risk_admission
    from zephyr.backtest.core.metrics import calculate_full_metrics

    metrics = result.get("metrics") or {}
    overfitting_flag = metrics.get("overfitting_flag")
    dsr = metrics.get("dsr")
    n_trials = metrics.get("n_trials")
    n_trials_source = metrics.get("n_trials_source")

    if dsr is None:
        if nav is None:
            nav = _load_artifact_nav(result.get("run_id"))
        if nav is not None:
            try:
                full = calculate_full_metrics(nav, trades_count=int(metrics.get("trades_count") or 0))
                dsr = full.get("dsr")
                n_trials = full.get("n_trials", n_trials)
                n_trials_source = full.get("n_trials_source", n_trials_source)
                if overfitting_flag is None:
                    overfitting_flag = full.get("is_overfitting")
            except Exception as exc:  # noqa: BLE001  ——DSR 复算失败=缺证据，交由 fail-closed 拒
                _alert(f"整装回测风险裁决 DSR 复算失败（fail-closed 将拒）: {type(exc).__name__}: {exc}"[:200],
                       level="WARN")

    admission = evaluate_strategy_risk_admission(overfitting_flag, dsr)
    return {
        "accepted": bool(admission.accepted),
        "overfitting_flag": overfitting_flag,
        "dsr": dsr,
        "n_trials": n_trials,
        "n_trials_source": n_trials_source,
        "reasons": list(admission.reasons),
    }


# ---------- 三段决策门控接线（H5-B：IS→WFA→OOS + DSR，判定全委托 DecisionGate） ----------
#
# 为什么在此接线而不是引擎里：引擎（vectorized/event_driven）自带 `evaluate_decision_gate`
# 全仓零调用（本车道禁改该二文件），而 S11 收尾是**唯一自动跑的整装回测出口**——门控结论
# 不进 acceptance 就等于整套 IS/WFA/OOS  machinery 在产线上不存在（挖矿 §1.2 判"蓝图兑现为 0"）。
# 阈值零自造：全部取 `DecisionGate()` 默认配置（DSR 线 0.95 与 OOS/IS 比率等单一真源），
# 本模块只负责"把证据搬到判定器面前"。
#
# 证据口径（关键裁定，勿当参数拟合内外读）：S11 在窗口内**不再拟合参数**（方案权重由 plan
# 指纹锁定），故三段证据取自同一条**实测净值**的时间切片——IS=首段、WFA=其后各完整折、
# OOS=各折起点之后的全部后段。这是"锁定账簿的时间稳定性/退化"考核（walk-forward 的退化
# 分支），不是"参数拟合样本内/外"考核；真正的 fit-window IS 属 TDM 侧欠账（S11 README
# §登记远期第 6 条），本处不假造该数字。

#: 单段最少样本数 = metrics.MIN_SAMPLES_FOR_SHARPE + 1（低于该线 calculate_metrics 恒返
#: Sharpe=0，折证据无效——用既有常量作下限，禁另拍魔数）
_GATE_MIN_SEG_SAMPLES: Final[int] = 61
#: 净值等分份数（1 份 IS + ≥2 份 WFA 折；"多数通过"判定在 ≥2 折上才有意义）
_GATE_TARGET_SEGMENTS: Final[int] = 3
#: WFA 折数下限——切不出即缺证据，按 fail-closed 判拒
_GATE_MIN_FOLDS: Final[int] = 2


def _gate_fold_evidence(nav: Any) -> dict[str, Any] | None:
    """净值 → IS/WFA/OOS 三段证据（切分委托既有 WalkForwardAnalyzer，零手写切片算法）。

    Returns:
        {is_sharpe, oos_sharpe, folds:[{fold,sharpe,max_drawdown,days}], scheme:{...}}；
        样本不足以切出 IS + ≥_GATE_MIN_FOLDS 折时返回 None（调用方按缺证据 fail-closed）。
    """
    from zephyr.backtest.core.metrics import calculate_metrics
    from zephyr.backtest.core.walk_forward import WalkForwardAnalyzer, WalkForwardConfig

    if nav is None or len(nav) < _GATE_MIN_SEG_SAMPLES * _GATE_TARGET_SEGMENTS:
        return None
    seg = max(_GATE_MIN_SEG_SAMPLES, len(nav) // _GATE_TARGET_SEGMENTS)
    analyzer = WalkForwardAnalyzer(
        WalkForwardConfig(mode="expanding", train_window=seg, test_window=seg)
    )
    folds = analyzer.split(list(nav.index))
    if len(folds) < _GATE_MIN_FOLDS:
        return None

    fold_rows: list[dict[str, Any]] = []
    for k, (_train, test) in enumerate(folds):
        m = calculate_metrics(nav.loc[test], trades_count=0)
        fold_rows.append(
            {"fold": k, "sharpe": float(m["sharpe_ratio"]), "max_drawdown": float(m["max_drawdown"]),
             "days": len(test)}
        )
    is_m = calculate_metrics(nav.iloc[:seg], trades_count=0)
    oos_m = calculate_metrics(nav.iloc[seg:], trades_count=0)  # 各折起点后的全部后段（含末段残样）
    return {
        "is_sharpe": float(is_m["sharpe_ratio"]),
        "oos_sharpe": float(oos_m["sharpe_ratio"]),
        "folds": fold_rows,
        "scheme": {
            "caliber": "locked_book_time_split（窗口内无再拟合，净值时间切片）",
            "segment_days": int(seg),
            "is_days": int(seg),
            "oos_days": int(len(nav) - seg),
            "n_folds": len(fold_rows),
            "min_seg_samples": _GATE_MIN_SEG_SAMPLES,
            "nav_days": int(len(nav)),
        },
    }


def _evaluate_staged_gate(result: dict, *, nav: Any, locked_params: dict[str, Any], dsr: Any) -> dict[str, Any]:
    """把三段决策门控接进 S11 验收（判定器=DecisionGate，本函数只搬证据+摊开结论）。

    Args:
        result: run_framework_backtest 产物 dict（仅用于 run_id 留痕）。
        nav: 与风险裁决同一条净值序列（None=无产物净值，缺证据判拒）。
        locked_params: 方案锁定权重（IS 阶段参数稳定性判定的参数字典；敏感性扫描缺件见
            degraded_guards 的 is_param_plateau_gate 条目）。
        dsr: 已解析的 DSR（与 evaluate_strategy_risk_admission 同一数值，禁二次计算）。

    Returns:
        {passed, can_deploy, is_passed, wfa_passed, wfa_windows, has_disaster, oos_passed,
         oos_is_ratio, reasons, evidence}——reasons 逐条留痕，evidence 落证据包可复核。
    """
    from zephyr.backtest.core.decision_gate import DecisionGate

    ev = _gate_fold_evidence(nav)
    if ev is None:
        return {
            "passed": False,
            "can_deploy": False,
            "is_passed": False,
            "wfa_passed": False,
            "wfa_windows": "0/0",
            "has_disaster": False,
            "oos_passed": False,
            "oos_is_ratio": None,
            "reasons": [
                "三段门控证据不足：净值切不出 IS + ≥"
                f"{_GATE_MIN_FOLDS} 个完整折（每折 ≥{_GATE_MIN_SEG_SAMPLES} 样本）——缺证据按不通过处理(fail-closed)"
            ],
            "evidence": None,
        }

    verdict = DecisionGate().evaluate(
        is_sharpe=ev["is_sharpe"],
        params=dict(locked_params),
        param_sensitivity=None,  # S11 无敏感性扫描产物——门控自身记"跳过稳定性门控"，消费侧另落降级账
        walk_forward_results=[
            {"sharpe": f["sharpe"], "max_drawdown": f["max_drawdown"]} for f in ev["folds"]
        ],
        oos_sharpe=ev["oos_sharpe"],
        params_locked=True,  # 方案权重按 plan 指纹锁定，窗口内零再拟合（见 _evaluate_composition_integrity 同族披露）
        dsr=dsr,
    )
    return {
        "passed": bool(verdict.overall_passed),
        "can_deploy": bool(verdict.can_deploy),
        "is_passed": bool(verdict.is_stage.passed),
        "wfa_passed": bool(verdict.wfa_stage.passed),
        "wfa_windows": f"{verdict.wfa_stage.windows_passed}/{verdict.wfa_stage.windows_total}",
        "has_disaster": bool(verdict.wfa_stage.has_disaster),
        "oos_passed": bool(verdict.oos_stage.passed),
        "oos_is_ratio": round(float(verdict.oos_stage.oos_is_ratio), 4),
        "downgraded": bool(verdict.downgraded),
        "reasons": list(verdict.reasons),
        "evidence": ev,
        "run_id": result.get("run_id"),
    }


def _evaluate_composition_integrity(result: dict) -> dict[str, Any]:
    """组合完整性闸（T1A-2 消费端）——死成员摊派超阈即否决验收，禁"知情放行"。

    为什么必须在这一层消费：compose 侧把"方案承诺的 α 有多少没能兑现"如实落进
    ``metrics.dead_weight_disclosed`` 并写进 warn，但 warn 只进日志——若验收仍判 ok，
    披露就退化成产而不消。回测结论的前提是"跑的组合=方案说的组合"，前提破了，
    指标再漂亮也不可采信（量化实务同口径：construction integrity check 先于
    performance check）。

    口径:
      - 判据用 ``skipped_alpha_share_of_plan``（**全部**未兑现 α：面板缺失/整表为零/
        显式零权重/构建路空跑），因为"组合已非方案原意"的幅度与死法无关；死法分域
        （kind）只用于处置路由，留在 ``run.dead_weight_disclosed`` 里看。
      - 行级归一 material（成员部分日无信号）只披露不否决——整装面板逐日常态，
        拿它当否决条件会制造告警噪声，掩盖真正的结构性缺口。
      - 无披露=无证据，fail-closed 判不过（与风险闸"缺失即拒"同族）。
    """
    from zephyr.pf_core.strategy_engine.framework_composer import (
        DEAD_MEMBER_ALPHA_SHARE_LIMIT,
    )

    disclosure = result.get("dead_weight_disclosed") or {}
    row_norm = disclosure.get("row_normalization") or {}
    if not disclosure:
        return {
            "accepted": False,
            "skipped_alpha_share": None,
            "limit": DEAD_MEMBER_ALPHA_SHARE_LIMIT,
            "row_norm_material": None,
            "reasons": ["无 dead_weight_disclosed 披露（组合未按方案合成或产物过旧）"],
        }
    share = float(disclosure.get("skipped_alpha_share_of_plan") or 0.0)
    reasons: list[str] = []
    if share > DEAD_MEMBER_ALPHA_SHARE_LIMIT:
        reasons.append(
            f"未兑现 α 占方案 {share * 100:.1f}%（>限 {DEAD_MEMBER_ALPHA_SHARE_LIMIT * 100:.0f}%）"
            "——跑的组合已非方案原意，回测结论不可用"
        )
    return {
        "accepted": not reasons,
        "skipped_alpha_share": share,
        "limit": DEAD_MEMBER_ALPHA_SHARE_LIMIT,
        "row_norm_material": bool(row_norm.get("material")),
        "dead_member_alpha_share_of_plan": float(
            (disclosure.get("dead_member_alpha_base") or 0.0)
            / float(disclosure.get("plan_weight_total") or 1.0)
        ),
        "reasons": reasons,
    }


# ---------- 执行链证据（#24 H3/H4）----------

def _evaluate_cash_closure(result: dict) -> dict[str, Any]:
    """现金账本闭合闸（H4-B，#24）——账本不闭合，指标再漂亮也不可采信。

    与组合完整性闸同族 fail-closed：无披露键（产物过旧 / 引擎换成不落地现金腿的
    实现）判不过，禁"没数据=通过"。判据取 ``reconcile_cash_ledger.within_tolerance``
    （逐日残差 ≤ portfolio.CASH_LEDGER_TOLERANCE，容差单一真源在账本属主侧）。

    本闸只核对**内账**（成交流水 ↔ 现金余额），与 tracker #275 裁定的"外账不可对"
    （成员净值 vs 整装净值因整手取整/最低佣金/涨跌停拒单不可闭合）是两件事——
    那条裁定不约束本闸，本闸也不得被拿去当外账判据。
    """
    metrics = result.get("metrics") or {}
    recon = (
        result.get("cash_ledger_reconciliation")
        or metrics.get("cash_ledger_reconciliation")
        or {}
    )
    if not recon:
        return {
            "accepted": False,
            "samples": None,
            "max_abs_residual": None,
            "tolerance_abs": None,
            "reasons": ["无 cash_ledger_reconciliation 披露（产物过旧或现金腿未接）"],
        }
    samples = int(recon.get("samples") or 0)
    reasons: list[str] = []
    if samples <= 0:
        reasons.append("现金账本无逐日样本可核对（cash_history 空）")
    elif not bool(recon.get("within_tolerance")):
        reasons.append(
            f"现金账本不闭合：最大逐日残差 {recon.get('max_abs_residual')} 元 "
            f"> 容差 {recon.get('tolerance_abs')}（{recon.get('over_tolerance')} 日破口，"
            f"最差日 {recon.get('worst_date')}，未核对流水 {recon.get('bad_trade_rows')} 笔）"
            "——成交/手续费与现金余额对不上，回测账本有洞"
        )
    return {
        "accepted": not reasons,
        "samples": samples,
        "max_abs_residual": recon.get("max_abs_residual"),
        "tolerance_abs": recon.get("tolerance_abs"),
        "worst_date": recon.get("worst_date"),
        "cash_last": recon.get("cash_last"),
        "reconstructed_cash_last": recon.get("reconstructed_cash_last"),
        "reasons": reasons,
    }


def _turnover_disclosure(result: dict) -> dict[str, Any]:
    """换手证据上提（H3-A，#24）——成本归因算出的换手率必须在验收面可见。

    归因层**已**算出年化单边换手并带告警（真源 cost_attribution），但 ``core_metrics``
    白名单不含换手，证据包只看得到收益——"换手预算"这条约束此前在整装回测面等于
    不存在。本函数把它连同阈值与告警原文提进 ``run.turnover_disclosure``。

    阈值引用不复制（RULE-SSOT）：只读 ``TURNOVER_ONE_SIDE_ANNUAL_ALERT``。
    **没有**在此实现 no-trade band/换手硬节流——那是改成交行为（执行口径），
    属 Owner 裁定项（AI 自主权外，登记在 lane #24 报告）。
    """
    from zephyr.backtest.core.cost_attribution import TURNOVER_ONE_SIDE_ANNUAL_ALERT

    metrics = result.get("metrics") or {}
    cost = metrics.get("cost_attribution") or {}
    friction = cost.get("friction") or {}
    turnover = friction.get("turnover_one_side_annualized")
    measured = isinstance(turnover, (int, float)) and turnover == turnover  # NaN=未测
    alerts = [
        a for a in (cost.get("alerts") or []) if str(a.get("code", "")).startswith("TURNOVER")
    ]
    return {
        "schema": "turnover_disclosure/v1",
        "measured": bool(measured),
        "one_side_annualized": turnover,
        "alert_threshold_one_side_annual": TURNOVER_ONE_SIDE_ANNUAL_ALERT,
        "over_alert": (bool(turnover > TURNOVER_ONE_SIDE_ANNUAL_ALERT) if measured else None),
        "cost_alerts": alerts,
        "cost_total": friction.get("cost_total"),
        "cost_share_of_abs_result": friction.get("cost_share_of_abs_result"),
        "note": (
            "换手率=成本归因层实测（单边年化）；阈值只作告警不作节流——"
            "no-trade band/换手预算硬约束未实现（改执行口径需 Owner 裁定）"
        ),
    }


# ---------- 风险护栏 fail-open 可观测性（H5-D：降级计数进 acceptance + WARNING 出声） ----------
#
# 降级点位在引擎/撮合内部（vectorized_engine / matching_engine 的 4+ 处 fail-open，本车道
# **禁改**该二文件），其共同点是"每次降级都记一条日志、但不进产物 metrics"。消费侧的等价
# 观测手段=在 run_framework_backtest 执行期挂一个 logging.Handler，把 zephyr.backtest.* 的
# 降级出声**结构化成计数**（同进程、同一次 run，计数=当次真值）。语义零改：本账本只让
# "哪些闸当次失效"可见（acceptance + 证据包 + WARN），不新增否决权（既有 cash/composition/
# risk/三段门四闸已有否决，护栏降级是否升格为否决属 Owner 门位，登记在节点报告）。

#: 监视表：(guard_id, 匹配正则, 一句话"失效含义")——正则锚在引擎既有出声文案关键词上；
#: 引擎若改文案，该项计数恒为 0（=未听见，不等于健康），故 note 里标明来源是出声归类。
_GUARD_LOG_WATCH: Final[tuple[tuple[str, str, str], ...]] = (
    ("pit_universe_filter", r"标的池过滤降级|上市注册表为空",
     "PIT 上市/退市窗口腿不可用→当日不做幸存者/次新过滤（护栏当次失效）"),
    ("pit_st_filter", r"PIT ST 判定失败|ST 兜底降级",
     "ST 腿故障→该轮不剔 ST（护栏当次失效）"),
    ("impact_cost_model", r"冲击成本旁路|冲击报价失败",
     "Almgren-Chriss 冲击不可用→按无冲击成交（成本低估）"),
    ("liquidity_participation_cap", r"成交量上限/冲击成本自动旁路",
     "数据无 volume 列→P0-2 参与率上限整体旁路（容量约束当次不存在）"),
    ("participation_rate_sanity", r"参与率越界",
     "参与率∉[0,1]（疑 INV-UNIT-001 量纲违例）→该标的按无冲击成交"),
    ("stk_limit_bounds", r"StkLimitProvider 预取失败|涨跌停表行不可用|切片真源调用失败",
     "涨跌停价腿故障→退规则兜底/按不封板处理（可成交性约束当次失效）"),
    ("fill_integrity", r"Fill skipped|fill 被拒绝",
     "撮合拒单→实际成交偏离信号意图（回测非所求组合）"),
)


class _GuardDegradationCollector(logging.Handler):
    """把 zephyr.backtest.* 的护栏降级出声归类计数（emit 零抛——观测面不得反噬回测）。"""

    def __init__(self) -> None:
        super().__init__(level=logging.INFO)
        self._watch = [(gid, re.compile(pat), note) for gid, pat, note in _GUARD_LOG_WATCH]
        self.counts: dict[str, int] = {gid: 0 for gid, _p, _n in _GUARD_LOG_WATCH}
        self.samples: dict[str, str] = {}

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001  ——格式化失败不该拖垮回测
            return
        for gid, rx, _note in self._watch:
            if rx.search(msg):
                self.counts[gid] = self.counts.get(gid, 0) + 1
                self.samples.setdefault(gid, f"{record.name}:{record.levelname}: {msg[:180]}")
                return


@contextlib.contextmanager
def _capture_guard_degradations():
    """run_framework_backtest 执行期的护栏降级采集器（退出即摘钩、还原级别）。"""
    logger = logging.getLogger("zephyr.backtest")
    handler = _GuardDegradationCollector()
    prev_level = logger.level
    logger.addHandler(handler)
    if logger.level > logging.INFO or logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    try:
        yield handler
    finally:
        logger.removeHandler(handler)
        logger.setLevel(prev_level)


#: 证据缺件型"闸未生效"的一句话解释（不新增判定，只把 DecisionGate 自己的跳过语义说出声）
_GAP_MEANINGS: Final[dict[str, str]] = {
    "is_param_plateau_gate": "无参数敏感性扫描产物→DecisionGate IS 段稳定性/悬崖门当次跳过",
    "phase5_regime_gate": "未注入 regime 适配/参数收缩 checker→Phase5 后置双闸当次不参与",
}


def _degraded_guard_report(
    handler: _GuardDegradationCollector | None,
    *,
    regime_mode: str,
    symbols_override: bool,
    stk_limit_enabled: bool,
    gate_skipped: list[str],
) -> dict[str, Any]:
    """汇总本次运行的护栏失效账（日志观测 + 消费侧配置缺件），并对每条降级 WARN 出声。

    计数语义：`count=0` 且该闸在 watch 表内=本次未听见过其降级出声（引擎只在真失效时记
    日志）；`count>0`=当次失效次数。配置性旁路（payload 关闸/自报标的池/regime 静态回退/
    敏感性扫描缺件）由消费侧直接登记，不依赖日志。
    """
    observed = handler.counts if handler is not None else {}
    samples = handler.samples if handler is not None else {}
    guards: list[dict[str, Any]] = [
        {
            "guard": gid,
            "count": int(observed.get(gid, 0)),
            "source": "engine_log_observed",
            "meaning": note,
            "sample": samples.get(gid),
        }
        for gid, _pat, note in _GUARD_LOG_WATCH
    ]
    guards += [
        {
            "guard": "regime_dynamic_overlay",
            "count": 0 if regime_mode != "static" else 1,
            "source": "consumer_config",
            "meaning": f"regime 日序模式={regime_mode}（static=动态权重腿当次未生效，仅静态基准权重）",
        },
        {
            "guard": "pit_universe_window",
            "count": 1 if symbols_override else 0,
            "source": "consumer_config",
            "meaning": "标的池由 payload 自报→PIT 成份窗口未参与，幸存者偏差由调用方承担",
        },
        {
            "guard": "stk_limit_provider",
            "count": 0 if stk_limit_enabled else 1,
            "source": "consumer_config",
            "meaning": "payload 显式关闭涨跌停 PIT 提供器（退回规则兜底口径）",
        },
    ]
    guards += [
        {"guard": g, "count": 1, "source": "gate_evidence_gap", "meaning": _GAP_MEANINGS[g]}
        for g in gate_skipped
        if g in _GAP_MEANINGS
    ]

    degraded = [g for g in guards if g["count"]]
    for g in degraded:
        _alert(
            f"整装回测护栏降级: {g['guard']} ×{g['count']}（{g['source']}）—— {g['meaning']}"
            + (f" 样例: {g['sample']}" if g.get("sample") else ""),
            level="WARN",
        )
    return {
        "schema": "degraded_guards/v1",
        "degraded": degraded,
        "degraded_n": len(degraded),
        "watched": [g["guard"] for g in guards],
        "log_watch_patterns": len(_GUARD_LOG_WATCH),
        "note": (
            "count=本次运行内该护栏降级次数；source=engine_log_observed 者由 zephyr.backtest.* "
            "出声归类而得（引擎侧改文案会使该项退为 0=未听见，非=健康）；count=0 的 "
            "consumer_config 项=本次配置下该闸确实在岗"
        ),
    }


# ---------- 核心契约 ----------

#: 幂等闸要求旧证据具备的验收键——缺任一键=该闸当时未接线，据其短路会让被冻结的策略永不再判
_IDEMPOTENT_REQUIRED_ACCEPTANCE: Final[tuple[str, ...]] = (
    "ok", "risk_admitted", "cash_closure_admitted", "gate_passed",
)


def _idempotent_skip(fp: dict[str, Any], latest: dict[str, Any] | None, force: bool) -> str | None:
    """幂等闸判据：同指纹 + 旧证据"每一道闸都显式放行"才返回跳过理由，否则 None（须重跑）。

    车道 L：要求旧证据 risk_admitted is True——接线前的老证据只有 ok=True 从无该键，
    据其短路将令被冻结的过拟合策略永不再判。#24 H4-B（cash_closure_admitted）与本轮
    H5-B（gate_passed，三段门控后接）同族：任何后加的闸都要旧证据显式认账才可短路。
    """
    if force or not latest:
        return None
    if (latest.get("plan", {}).get("fingerprint") or "") != fp["fingerprint"]:
        return None
    acc = latest.get("acceptance") or {}
    for key in _IDEMPOTENT_REQUIRED_ACCEPTANCE:
        if acc.get(key) is not True:
            return None
    return "plan_fingerprint_unchanged（同指纹最近已 ok 且各闸均放行，force=true 可强制重跑）"


def _assemble_acceptance(
    result: dict[str, Any],
    risk: dict[str, Any],
    gate: dict[str, Any],
    composition: dict[str, Any],
    cash: dict[str, Any],
    guard_report: dict[str, Any],
) -> dict[str, Any]:
    """验收七硬项汇总（跑通 ∧ 面板对账 ∧ 净值非空 ∧ 风险准入 ∧ 三段门控 ∧ 组合完整性 ∧ 现金闭合）。

    降级护栏不进 ok 判据（H5-D 裁定）：本项是"当次哪些闸失效"的可见性账，升格为否决权
    属 Owner 门位——故只落 acceptance 字段 + WARN 出声，不参与 ok 计算。
    """
    recon = result.get("panel_reconciliation") or {}
    base_ok = (
        bool(result.get("ok"))
        and bool(recon.get("within_tolerance"))
        and int(result.get("equity_points") or 0) > 0
    )
    return {
        "ok": bool(
            base_ok and risk["accepted"] and gate["passed"]
            and composition["accepted"] and cash["accepted"]
        ),
        "run_ok": bool(result.get("ok")),
        "within_tolerance": bool(recon.get("within_tolerance")),
        "equity_points": int(result.get("equity_points") or 0),
        "risk_admitted": bool(risk["accepted"]),
        "gate_passed": bool(gate["passed"]),
        "gate_can_deploy": bool(gate["can_deploy"]),
        "gate_is_passed": bool(gate["is_passed"]),
        "gate_wfa_passed": bool(gate["wfa_passed"]),
        "gate_wfa_windows": gate["wfa_windows"],
        "gate_oos_passed": bool(gate["oos_passed"]),
        "gate_oos_is_ratio": gate["oos_is_ratio"],
        "gate_has_disaster": bool(gate["has_disaster"]),
        "composition_admitted": bool(composition["accepted"]),
        "cash_closure_admitted": bool(cash["accepted"]),
        "cash_max_abs_residual": cash["max_abs_residual"],
        "skipped_alpha_share": composition["skipped_alpha_share"],
        "composition_over_limit": bool(
            composition["skipped_alpha_share"] is not None
            and composition["skipped_alpha_share"] > composition["limit"]
        ),
        "overfitting_flag": risk["overfitting_flag"],
        "dsr": risk["dsr"],
        "n_trials": risk["n_trials"],
        "n_trials_source": risk["n_trials_source"],
        "degraded_guard_n": guard_report["degraded_n"],
        "degraded_guards": [g["guard"] for g in guard_report["degraded"]],
        "risk_reasons": risk["reasons"],
        "gate_reasons": gate["reasons"],
        "composition_reasons": composition["reasons"],
        "cash_closure_reasons": cash["reasons"],
    }


def _build_run_block(
    result: dict[str, Any],
    recon: dict[str, Any],
    risk: dict[str, Any],
    gate: dict[str, Any],
    composition: dict[str, Any],
    cash: dict[str, Any],
    guard_report: dict[str, Any],
    sym_info: dict[str, Any],
) -> dict[str, Any]:
    """证据包 run 章：核心指标 + 四道裁决 + #24 执行链证据 + H5-D 护栏失效账。

    `chain_evidence` 只透传产物 metrics 既有键（缺键=None，消费方按缺键 fail-closed），
    本函数不补默认值——补了就是把"没测"洗成"测过"。
    """
    metrics = result.get("metrics") or {}
    core_metrics = {
        k: metrics.get(k)
        for k in ("total_return", "annual_return", "sharpe_ratio", "max_drawdown",
                  "win_rate", "trades_count")
        if k in metrics
    }
    chain_evidence = {
        k: metrics.get(k)
        for k in (
            "cash_ledger_reconciliation",
            "target_weight_renormalization",
            "skipped_fills",
            "execution_model_disclosure",
            "signal_age_disclosed",
        )
    }
    run_id = result.get("run_id")
    return {
        "ok": result.get("ok"),
        "run_id": run_id,
        "artifact_path": f"data/backtest_artifacts/{run_id}.json" if run_id else None,
        "participants": result.get("participants"),
        "skipped": result.get("skipped"),
        "rescale_factor": result.get("rescale_factor"),
        "warn": result.get("warn"),
        "panel_reconciliation": recon,
        "equity_points": result.get("equity_points"),
        "trades": result.get("trades"),
        "core_metrics": core_metrics,
        "risk_decision": risk,
        "staged_gate_decision": gate,
        "dead_weight_disclosed": result.get("dead_weight_disclosed") or {},
        "composition_decision": composition,
        "turnover_disclosure": _turnover_disclosure(result),
        "universe_disclosure": sym_info.get("universe_disclosure") or {},
        "cash_decision": cash,
        "guard_degradation_ledger": guard_report,
        **chain_evidence,
    }


def _acceptance_failure_note(
    acceptance: dict[str, Any],
    risk: dict[str, Any],
    gate: dict[str, Any],
    composition: dict[str, Any],
    cash: dict[str, Any],
) -> str:
    """验收失败时按"第一道否决闸"补一段人可读否决留痕（禁只报 ok=false 不报为什么）。"""
    if not acceptance["run_ok"] or not acceptance["within_tolerance"] or not acceptance["equity_points"]:
        return " 基础跑通闸（run/对账/净值）未过——后续闸结论不作数"
    notes: list[str] = []
    if not risk["accepted"]:
        notes.append(
            f" 风险闸否决: overfitting_flag={risk['overfitting_flag']} dsr={risk['dsr']} "
            f"n_trials={risk['n_trials']} ({risk['n_trials_source']}) reasons={risk['reasons']}"
        )
    if not gate["passed"]:
        notes.append(
            f" 三段门控否决: IS={gate['is_passed']} WFA={gate['wfa_passed']}"
            f"({gate['wfa_windows']}) OOS={gate['oos_passed']}(ratio={gate['oos_is_ratio']}) "
            f"reasons={gate['reasons']}"
        )
    if not composition["accepted"]:
        notes.append(f" 组合完整性闸否决: reasons={composition['reasons']}")
    if not cash["accepted"]:
        notes.append(f" 现金账本闭合闸否决: reasons={cash['reasons']}")
    return "".join(notes)


def run_fw_backtest_due(event: dict) -> dict[str, Any]:
    """fw_backtest_due 事件处理体（契约钉死）。

    Args:
        event: 完整事件 {"kind", "payload", ...} 或裸 payload dict；payload 建议
            {"trigger": "auto_mount", "sids": [...]}，可选 start/end/symbols/force/timeout_s。

    Returns:
        摘要 dict（ok/skipped/evidence_path/run_id/plan/window/acceptance/...）。

    Raises:
        RuntimeError: 瞬时故障（生成器 rc≠0、方案缺失、参数组装失败）——journal 留档重试。
    """
    from zephyr.pf_core.strategy_engine.framework_composer import (
        FrameworkBacktestConfig,
        run_framework_backtest,
    )

    t0 = time.time()
    payload = dict(event.get("payload") or event) if isinstance(event, dict) else {}
    trigger = str(payload.get("trigger", "manual"))
    force = bool(payload.get("force", False))

    # ① 方案表生成器（子进程隔离；rc≠0=瞬时故障留 journal 重试）
    gen = _run_generator(payload.get("timeout_s"))

    # ①.5 regime 日序新鲜度闸（fresh=零成本直通；stale=告警披露进证据包，不阻断跑批）
    regime_guard = ensure_regime_snapshot()

    # ② 幂等闸：指纹未变且最近一次"每道闸都已放行"→ 跳过（同指纹重跑结果必然逐位同——
    #    面板由同窗口同数据决定，引擎确定性；省分钟级重跑与产物膨胀）。判据见 _idempotent_skip。
    fp = plan_fingerprint()
    latest = _latest_evidence()
    skip_reason = _idempotent_skip(fp, latest, force)
    if skip_reason:
        return {
            "ok": True,
            "skipped": skip_reason,
            "plan_fingerprint": fp["fingerprint"],
            "latest_evidence": str((latest or {}).get("evidence_path", "")),
            "generator": gen,
        }

    # ③ 参数组装（窗口/标的池/regime 日序）
    start = str(payload.get("start") or default_window()[0])
    end = str(payload.get("end") or default_window()[1])
    base = payload.get("symbols") or None
    symbols, sym_info = resolve_symbols(start, end, base)
    regime = load_regime_series(start, end)

    config = FrameworkBacktestConfig(
        regime_by_date=regime.get("series"),
        enable_stk_limit_provider=bool(payload.get("enable_stk_limit_provider", True)),
    )
    # ④ 回测（执行期挂 H5-D 护栏降级采集器——引擎 fail-open 只出声不落地，消费侧就地计数）
    with _capture_guard_degradations() as guard_handler:
        result = run_framework_backtest(PLAN_ID, symbols, start, end, config=config)

    # ⑤ 验收（同一条净值喂风险裁决与三段门控，禁两次读产物）
    recon = result.get("panel_reconciliation") or {}
    nav = _load_artifact_nav(result.get("run_id"))
    risk = _evaluate_risk_decision(result, nav)
    gate = _evaluate_staged_gate(result, nav=nav, locked_params=fp["weights"], dsr=risk["dsr"])
    guard_report = _degraded_guard_report(
        guard_handler,
        regime_mode=str(regime.get("mode") or "static"),
        symbols_override=bool(base),
        stk_limit_enabled=bool(config.enable_stk_limit_provider),
        gate_skipped=["is_param_plateau_gate", "phase5_regime_gate"],
    )
    composition = _evaluate_composition_integrity(result)
    cash = _evaluate_cash_closure(result)
    acceptance = _assemble_acceptance(result, risk, gate, composition, cash, guard_report)
    summary: dict[str, Any] = {
        "ok": acceptance["ok"],
        "trigger": trigger,
        "sids": payload.get("sids") or [],
        "plan": {**fp, "name": result.get("plan_id"), "static_mode": regime["mode"] != "dynamic_disclosure"},
        "window": {"start": start, "end": end},
        "symbols_total": sym_info["total"],
        "symbols_info": sym_info,
        "regime": {k: regime[k] for k in ("mode", "freshness", "note") if k in regime}
        | {"freshness_guard": regime_guard.get("action")},
        "regime_day_counts": result.get("regime_day_counts") or {},
        "run": _build_run_block(result, recon, risk, gate, composition, cash, guard_report, sym_info),
        "generator": gen,
        "duration_s": round(time.time() - t0, 1),
        "acceptance": acceptance,
    }
    evidence_path = _write_evidence(summary)
    summary["evidence_path"] = str(evidence_path)
    if not acceptance["ok"]:
        _alert(
            f"fw-tdm-current 整装回测验收未过: ok={acceptance['run_ok']} "
            f"within_tolerance={acceptance['within_tolerance']} "
            f"equity_points={acceptance['equity_points']} warn={result.get('warn')!r}"
            + _acceptance_failure_note(acceptance, risk, gate, composition, cash)
            + f" degraded_guards={acceptance['degraded_guards']}"
            f" evidence={evidence_path}",
            level="ERROR",
        )
    return summary


def _run_generator(timeout_payload: Any) -> dict[str, Any]:
    """重跑方案表生成器（子进程；--check 语义内置在生成器幂等里）。"""
    timeout_s = int(timeout_payload or DEFAULT_TIMEOUT_S)
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, str(GENERATOR_SCRIPT)],
        capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
        encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"方案表生成器失败 rc={proc.returncode}: {(proc.stderr or '')[-300:]}")
    try:
        out = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    except ValueError:
        out = {"raw_stdout_tail": (proc.stdout or "")[-200:]}
    return {"rc": 0, "duration_s": round(time.time() - t0, 1), "summary": out}


def _write_evidence(summary: dict[str, Any]) -> Path:
    """证据包落档：fw-auto-<ts>-<fp8>.json + latest.json（safe_write_text；时间戳命名不覆盖历史）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    fp8 = (summary.get("plan", {}).get("fingerprint") or "00000000")[:8]
    path = EVIDENCE_DIR / f"fw-auto-{stamp}-{fp8}.json"
    body = json.dumps(summary, ensure_ascii=False, indent=1, default=str)
    r = safe_write_text(path, body, newline="\n")
    if not getattr(r, "written", True):
        raise RuntimeError(f"证据包写入未确认: {path}")
    latest = dict(summary)
    latest["evidence_path"] = str(path)  # latest 与分档件同构（跳过闸读 plan/acceptance 两键）
    safe_write_text(EVIDENCE_DIR / "latest.json",
                    json.dumps(latest, ensure_ascii=False, indent=1, default=str), newline="\n")
    return path


# ---------- regime 日序供给（挂点登记见模块 docstring） ----------

def regime_snapshot_freshness() -> dict[str, Any]:
    """regime_snapshot_history 新鲜度（max(trade_date)/行数/滞后天数）。"""
    from zephyr.data.ch_writer import get_client_strict

    row = get_client_strict().execute(
        "SELECT max(trade_date), count() FROM c1_backtest.regime_snapshot_history"
    )[0]
    max_date = row[0]
    stale_days = (date.today() - max_date).days if max_date else -1
    return {
        "max_trade_date": str(max_date) if max_date else None,
        "rows": int(row[1]),
        "stale_days": int(stale_days),
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def ensure_regime_snapshot(
    max_staleness_days: int = _REGIME_STALE_DAYS,
    refresh: bool = False,
    timeout_s: int = DEFAULT_TIMEOUT_S,
) -> dict[str, Any]:
    """regime 日序供给件（最小实现）：staleness 检查→（默认）告警 /（refresh=True）子进程印制。

    调度挂点=管线唤醒钩子（挂法登记见模块 docstring；本函数零副作用可安全挂）。
    """
    fresh = regime_snapshot_freshness()
    if fresh["stale_days"] <= max_staleness_days:
        return {"action": "fresh", **fresh}
    msg = (f"regime_snapshot_history 滞后 {fresh['stale_days']} 天"
           f"（max={fresh['max_trade_date']}）——整装动态模式日序供给告急")
    if not refresh:
        _alert(msg, level="WARN")
        return {"action": "stale_alert_only", **fresh}
    proc = subprocess.run(
        [sys.executable, str(REGIME_WRITER_SCRIPT)],
        capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
        encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        _alert(f"regime 印制失败 rc={proc.returncode}: {(proc.stderr or '')[-200:]}", level="ERROR")
        return {"action": "refresh_failed", "rc": proc.returncode, **fresh}
    return {"action": "refreshed", "rc": 0, **regime_snapshot_freshness()}


# ---------- emit 帮手（写侧钩子，auto_mount 调用） ----------

def emit_fw_backtest_due(trigger: str, sids: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    """journal record + 子进程立即消费（成功出队/失败留档）。任何异常不反噬调用方主流程由调用方兜。

    与 c4_batch_screen._emit_pipeline_hook 同款防御姿态：本函数自身不抛（故障转告警+返回值）。
    """
    from zephyr.strategy_pipeline import pipeline_events as pe

    payload: dict[str, Any] = {"trigger": trigger, "sids": list(sids or []), **extra}
    evt = pe.record(_EVENT_KIND, payload)
    timeout_s = int(payload.get("timeout_s") or DEFAULT_TIMEOUT_S)
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "zephyr.strategy_pipeline.fw_backtest",
             "run", "--payload", json.dumps(payload, ensure_ascii=False)],
            capture_output=True, text=True, timeout=timeout_s, cwd=str(ROOT),
            encoding="utf-8", errors="replace",
        )
    except Exception as exc:  # noqa: BLE001  ——超时/启动失败=留档等重放
        _retain_event(pe, evt, f"{type(exc).__name__}: {exc}"[:200])
        return {"event": evt["id"], "drained": False, "error": str(exc)[:200]}
    if proc.returncode != 0:
        _retain_event(pe, evt, f"rc={proc.returncode} {(proc.stderr or '')[-200:]}")
        return {"event": evt["id"], "drained": False, "rc": proc.returncode}
    _dequeue_event(pe, evt)
    result_tail = (proc.stdout or "").strip().splitlines()[-1] if (proc.stdout or "").strip() else "{}"
    return {"event": evt["id"], "drained": True, "result_tail": result_tail[:500]}


def _retain_event(pe: Any, evt: dict[str, Any], err: str) -> None:
    """失败留档：attempts+1，≥MAX_ATTEMPTS 毒丸告警（与 drain 同款语义，不动 pipeline_events 文件）。"""
    try:
        evts = pe.pending()
        for e in evts:
            if e["id"] == evt["id"]:
                e["attempts"] = int(e.get("attempts", 0)) + 1
                e["last_error"] = err
                if e["attempts"] >= pe.MAX_ATTEMPTS:
                    e["poison"] = True
                    _alert(f"管线事件毒丸留档: {evt['id']} kind={evt['kind']} err={err}", level="ERROR")
        pe._rewrite(evts)
    except Exception:  # noqa: BLE001  ——簿记失败不反噬
        pass
    _alert(f"fw_backtest_due 消费失败（事件留 journal 待重放）: {evt['id']} {err}", level="WARN")


def _dequeue_event(pe: Any, evt: dict[str, Any]) -> None:
    """成功出队+回执（只动本事件，不碰 journal 其余事件）。"""
    try:
        pe._rewrite([e for e in pe.pending() if e["id"] != evt["id"]])
        pe._save_receipt({
            "processed": [{"id": evt["id"], "kind": evt["kind"], "result": "fw_backtest_done"}],
            "failed": [], "skipped": [], "stop_reason": None,
            "pending_left": len(pe.pending()),
        })
    except Exception:  # noqa: BLE001
        pass


def _alert(message: str, level: str = "WARN") -> None:
    try:
        from zephyr.strategy_pipeline.pipeline_events import alert as pe_alert

        pe_alert(message, level=level)
    except Exception:  # noqa: BLE001  ——告警通道故障不反噬主流程
        pass


# ---------- CLI（子进程消费入口） ----------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="fw_backtest_due 触发件 CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="执行一次整装回测（emit 帮手子进程入口）")
    r.add_argument("--payload", default="{}", help="事件 payload JSON")
    f = sub.add_parser("freshness", help="regime_snapshot_history 新鲜度")
    args = ap.parse_args(argv)
    if args.cmd == "freshness":
        print(json.dumps(regime_snapshot_freshness(), ensure_ascii=False))
        return 0
    out = run_fw_backtest_due({"kind": _EVENT_KIND, "payload": json.loads(args.payload)})
    print(json.dumps(out, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
