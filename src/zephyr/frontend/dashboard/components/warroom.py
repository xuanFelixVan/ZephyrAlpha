# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.warroom
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.reporting.prediction_log_writer(query_predictions); zephyr.signal_ashare.next_day_8state_forecast(惰性); zephyr.regime.index_regime_panel(惰性); zephyr.plan_engine.scenario_playbook(惰性)
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] draft
# [INVARIANTS] 只读消费已落盘/可查询产物，前端零业务重算; 全部取数通道 fail-open（异常→该区"待数据/待接入"负反馈，不炸页面）; 未接入功能一律标注"待接入/待 P2/P3"（G4 反误导）; 90号§7铁律——只展示概率分布，不出点位/方向预测
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 取数/渲染异常不外抛（fail-open 降级留痕）
# [TESTS] tests/frontend/test_warroom.py
# [A_module] module_id=MOD-L28-WARROOM | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""warroom · 作战指挥室页组件（45号作战手册 P1，Owner 2026-08-28 页面结构裁定）

页面结构（Owner 裁定版，覆盖 45 号 memo 的 3×3×3 矩阵方案，勿照搬）：
  ① 前日预案区      —— 上一交易日生成的今日预案全文+关键价位/条件单；
                       数据源：prediction_log scenario_plan 族
                       （MOD-PLAN-005 产出 / MOD-PLAN-008 落库 / MOD-PLAN-018 日循环编排）
  ② 实时走势分析区  —— 今日走势分时段判定（竞价段 9:25=auction_verification 已落库；
                       开盘后 30 分钟桶=outcome 族盘后回写）；当前走势剧本+剧本对策
                       （scenario_playbook 模板库 production 只读检索）；
                       开盘 15 分钟/上午/下午分段形态识别（含 Open Rejection Reverse
                       四型）无后端产物（C24 时序分段状态机未施工）→ 待接入占位
  ③ 今日→明日惯性区 —— MOD-SIG-037 次日 8 态概率分布（production，只出分布不出点位），
                       8 态→三桶（上行/下行/震荡）为展示口径聚合
                       （与 dashboard_feeds 相关性净额展示聚合同先例）
  ④ 四指数状态卡    —— IDX-02 前端接入：MOD-REGIME-008 四指数 regime 面板
                       （testing，compute_index_regime_panel → to_dict）
  ⑤ 3×3 情景矩阵    —— 缺口⑥ P2 展示层：9 格封闭穷举（3 开盘 × 3 走势），
                       格概率=plan.grid_probabilities 落库字段（BM-SEL-04 暂缓
                       不抢建，未落库一律"概率待接入"）；格内动作=playbook 模板
  ⑥ 批量边界        —— 缺口⑦ P2 前端消费：MOD-PLAN-012 落库 tomorrow_boundary
                       族回查（prediction_log 只读；未跑批=待数据）
  ⑦ 风险包络 W5     —— 缺口⑨ 相关性净额（GAP-F-04 query_correlation_netting，
                       持仓/相关性对上游装配注入）+ 缺口⑩ 禁做清单
                       （MOD-PLAN-014 三源合成，源未装配=待接入）
  ⑧ W4 多空辩论台  —— 缺口⑧ P3 展示层：消费 llm_daily_analysis v2 辩论落库行
                       （MOD-PLAN-007 debate_mode=True 跑批产出：多头/空头陈词+
                       综合席三情景裁决）；交易员综合/风控 veto 位
                       （MOD-PLAN-013 四角色链 testing）未接日循环 → 恒"待接入"；
                       W0/W6 历史预案库折叠占位随样本积累后接入

渲染依赖: Panel（可选导入，测试环境零依赖仅返回 dict payload）。
"""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.reporting.prediction_log_writer import query_predictions
from zephyr.shared.io.paths import DB_PATH

log = logging.getLogger(__name__)

# prediction_log 查询口径（镜像 MOD-PLAN-008/MOD-RPT-029 常量，前端不反向 import
# plan_engine 全链以控制 app_panel 导入成本——值变更以 scenario_plan_recorder 为准）
_MODULE_SCENARIO_PLAN: Final = "plan_engine.scenario_planner"
_PT_SCENARIO_PLAN: Final = "scenario_plan"
_PT_OUTCOME: Final = "outcome"

# 批量边界落库族口径（镜像 MOD-PLAN-012 batch_boundary_runner 常量；语义产出方=MOD-PLAN-001）
_MODULE_BOUNDARY: Final = "plan_engine.tomorrow_boundary_planner"
_PT_TOMORROW_BOUNDARY: Final = "tomorrow_boundary"
_BOUNDARY_QUERY_LIMIT: Final = 64  # 作战池+持仓规模上限内（RULE-SEVEN 批量并发 ≤8，回查行数放宽）

# W4 辩论台查询口径（镜像 MOD-PLAN-007 llm_premarket_analysis 常量——llm_daily_analysis
# schema 唯一真源在产出方，前端不反向 import plan_engine 全链；值变更以产出方为准）
_LLM_STATUS_SUCCESS: Final = "success"
_LLM_DEBATE_SUFFIX: Final = "+debate"  # v2 辩论模式 prompt_version 后缀（44号 §9.14 铁律③）
_LLM_MODE_V2: Final = "v2_debate"
_SQL_LLM_DEBATE_LATEST: Final = (  # NO-BARE-SQL：常量+参数化
    "SELECT output_json, model_version, prompt_version, created_at "
    "FROM llm_daily_analysis "
    "WHERE trade_date = ? AND prompt_version LIKE ? AND status = ? "
    "ORDER BY id DESC LIMIT 1"
)

#: 9 情景 → （中文剧本名， 一句话逻辑）
_SCENARIO_ZH: Final[dict[str, tuple[str, str]]] = {
    "HIGH_OPEN_REAL_UP": ("高开高走·真涨", "强势确认，主线延续按预案执行"),
    "HIGH_OPEN_FAKE_UP": ("高开低走·假涨", "开盘拒绝反转（Open Rejection Reverse）——利好兑现嫌疑，不追高"),
    "HIGH_OPEN_WASH": ("高开洗盘", "方向不明，观望等确认"),
    "LOW_OPEN_REAL_DOWN": ("低开低走·真跌", "退潮确认，从严执行减仓纪律"),
    "LOW_OPEN_FAKE_DOWN": ("低开高走·假跌", "恐慌盘被接=黄金坑，观察反核不追卖"),
    "LOW_OPEN_WASH": ("低开洗盘", "方向不明，观望等确认"),
    "FLAT_OPEN_REAL_UP": ("平开高走·真涨", "内生强势，买主线龙头回踩"),
    "FLAT_OPEN_REAL_DOWN": ("平开低走·真跌", "弱势确认，减仓观察"),
    "FLAT_OPEN_WASH": ("平开震荡", "震荡延续，做T为主不开新仓"),
}

#: 三情景预案名 → 中文（触发区间由 payload 数值字段表达）
_PLAN_NAME_ZH: Final[dict[str, str]] = {
    "HIGH_OPEN": "高开预案",
    "FLAT_OPEN": "平开预案",
    "LOW_OPEN": "低开预案",
}

#: 档位 → 中文（44号 §9.5/§9.6 档位映射）
_STANCE_ZH: Final[dict[str, str]] = {
    "CONSERVATIVE": "保守档（×0.5）",
    "DEFENSIVE": "偏守档（×0.8）",
    "NORMAL": "正常档（×1.0）",
    "OFFENSIVE": "偏多半档（×1.2）",
    "AGGRESSIVE": "进攻档（×1.2）",
}

#: playbook 持仓动作 → 中文
_ACTION_ZH: Final[dict[str, str]] = {
    "HOLD": "持有不动",
    "ADD": "加仓",
    "REDUCE": "减仓",
    "EXIT": "离场",
    "WATCH": "观察",
}

#: 次日 8 态 → 中文（MOD-SIG-037）
_STATE8_ZH: Final[dict[str, str]] = {
    "GAP_UP_UP": "高开高走",
    "GAP_UP_DOWN": "高开低走",
    "GAP_DOWN_UP": "低开高走",
    "GAP_DOWN_DOWN": "低开低走",
    "FLAT_UP": "平开高走",
    "FLAT_DOWN": "平开低走",
    "FLAT_CLOSE": "震荡收平",
    "VIOLENT": "剧烈震荡",
}

#: 惯性三桶（展示口径聚合：8 态概率按方向归并，非业务算法）
_BUCKET_UP: Final = ("GAP_UP_UP", "FLAT_UP", "GAP_DOWN_UP")  # 低开高走=反转向上
_BUCKET_DOWN: Final = ("GAP_DOWN_DOWN", "FLAT_DOWN", "GAP_UP_DOWN")  # 高开低走=反转向下
_BUCKET_FLAT: Final = ("FLAT_CLOSE", "VIOLENT")

#: regime 7 态 → 中文（MOD-REGIME-002 语义注释）
_REGIME_ZH: Final[dict[str, str]] = {
    "r1": "低波震荡",
    "r2": "中波震荡",
    "r3": "牛市趋势",
    "r4": "熊市阴跌",
    "r10": "危机 CRISIS",
    "r11": "复苏 RECOVERY",
    "r12": "突破 BREAKOUT",
}

#: 惯性方向展示（direction → (alert_type, 操作联动提示模板)）
_DIRECTION_HINT: Final[dict[str, tuple[str, str]]] = {
    "up": ("success", "明日上行概率偏大——按预案正常执行（回踩主线龙头买入）"),
    "down": ("danger", "明日下行概率偏大——今日新建仓宜延迟/只打底仓（T+1：今天买入明天才能卖，宁等明日恐慌盘）"),
    "flat": ("warning", "方向不明——不开新仓等待确认，做T/回封除外"),
}

#: 3×3 情景矩阵（45号 §4 W2）：行=开盘（项目真实阈值 ±2%），列=开盘后 30 分钟走势（VWAP 判定）
_GRID_ROW_ZH: Final[dict[str, str]] = {
    "HIGH_OPEN": "高开（>+2%）",
    "FLAT_OPEN": "平开（±2%）",
    "LOW_OPEN": "低开（<-2%）",
}
_GRID_COL_ZH: Final[dict[str, str]] = {"up": "高走", "flat": "平走", "down": "低走"}
#: (开盘行, 走势列) → 9 情景 key（低走列在三行分别=假涨/真跌/假跌，勿想当然拼接）
_GRID_SCENARIO: Final[dict[tuple[str, str], str]] = {
    ("HIGH_OPEN", "up"): "HIGH_OPEN_REAL_UP",
    ("HIGH_OPEN", "flat"): "HIGH_OPEN_WASH",
    ("HIGH_OPEN", "down"): "HIGH_OPEN_FAKE_UP",
    ("FLAT_OPEN", "up"): "FLAT_OPEN_REAL_UP",
    ("FLAT_OPEN", "flat"): "FLAT_OPEN_WASH",
    ("FLAT_OPEN", "down"): "FLAT_OPEN_REAL_DOWN",
    ("LOW_OPEN", "up"): "LOW_OPEN_FAKE_DOWN",
    ("LOW_OPEN", "flat"): "LOW_OPEN_WASH",
    ("LOW_OPEN", "down"): "LOW_OPEN_REAL_DOWN",
}
_GRID_ROWS: Final = ("HIGH_OPEN", "FLAT_OPEN", "LOW_OPEN")
_GRID_COLS: Final = ("up", "flat", "down")

#: 禁做清单动作 → 中文（MOD-PLAN-014）
_SITOUT_ACTION_ZH: Final[dict[str, str]] = {
    "NO_TRADE": "禁交易",
    "NO_BUY": "禁买入",
    "NO_REVERSE": "禁反手",
}


@dataclass
class WarroomData:
    """作战室页数据（fetch 输出，全部 fail-open 降级）。

    Attributes:
        trade_date: 页面交易日（本地时区今日）。
        plan: 今日预案 payload（scenario_plan 族 dict；None=未生成）。
        plan_asof: 预案落库生效时点（展示用）。
        outcome: 今日实际 outcome payload（盘后回写族 dict；None=未回写）。
        playbook: 当前剧本对策（scenario_playbook 模板摘要；None=无剧本/未命中模板）。
        inertia: 今日→明日惯性（MOD-SIG-037 8 态分布+三桶聚合；None=不可用）。
        index_panel: 四指数 regime 面板 dict（IDX-02；None=不可用）。
        boundaries: 候选股批量边界 list（MOD-PLAN-012 落库 tomorrow_boundary 族；
            []=当日未跑批/无落库行；None=查询通道异常）。
        sit_out: 禁做清单 dict（MOD-PLAN-014 to_dict；None=三源未装配待接入/异常）。
        netting: 相关性净额 dict（GAP-F-04 query_correlation_netting；
            None=持仓/相关性对未装配待接入/异常）。
        debate: W4 多空辩论 dict（llm_daily_analysis v2 辩论行解析：
            bull/bear 陈词 + analysis 综合席裁决 + model/prompt 版本留痕；
            None=当日无 v2 辩论落库行——debate_mode 未启用/未跑批，正常态非异常）。
        errors: 各取数通道异常留痕（fail-open 负反馈）。
    """

    trade_date: str
    plan: dict | None = None
    plan_asof: str | None = None
    outcome: dict | None = None
    playbook: dict | None = None
    inertia: dict | None = None
    index_panel: dict | None = None
    boundaries: list[dict] | None = None
    sit_out: dict | None = None
    netting: dict | None = None
    debate: dict | None = None
    errors: list[str] = field(default_factory=list)


# ──────────────────────────────────────────────────────────────────────────────
# 取数层（fail-open；只读已落盘/可查询产物，零业务重算）
# ──────────────────────────────────────────────────────────────────────────────


def _today_str() -> str:
    """本地时区今日（YYYY-MM-DD）。"""
    return datetime.now().astimezone().strftime("%Y-%m-%d")


def _query_latest_payload(
    trade_date: str,
    prediction_type: str,
    db_path: object = None,
) -> tuple[dict | None, str | None]:
    """查 prediction_log 最新一行并解析 payload。返回 (payload, asof_ts)。

    查询/解析异常由调用方捕获（fetch 层统一 fail-open）。
    """
    rows = query_predictions(
        trade_date=trade_date,
        module=_MODULE_SCENARIO_PLAN,
        prediction_type=prediction_type,
        limit=1,
        db_path=db_path,
    )
    if not rows:
        return None, None
    payload = json.loads(rows[0]["payload_json"])
    return (payload if isinstance(payload, dict) else None), rows[0].get("asof_ts")


def fetch_warroom_plan(
    trade_date: str,
    db_path: object = None,
) -> tuple[dict | None, str | None, str | None]:
    """取今日预案（scenario_plan 族）。返回 (payload, asof_ts, error)。"""
    try:
        payload, asof = _query_latest_payload(trade_date, _PT_SCENARIO_PLAN, db_path)
        return payload, asof, None
    except Exception as exc:  # noqa: BLE001 — fail-open：查询异常降级"待数据"
        log.warning("作战室预案查询异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, None, f"预案查询：{type(exc).__name__}"


def fetch_warroom_outcome(
    trade_date: str,
    db_path: object = None,
) -> tuple[dict | None, str | None]:
    """取今日实际 outcome（盘后回写族）。返回 (payload, error)。"""
    try:
        payload, _asof = _query_latest_payload(trade_date, _PT_OUTCOME, db_path)
        return payload, None
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("作战室 outcome 查询异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"outcome 查询：{type(exc).__name__}"


def fetch_playbook_action(scenario: str | None) -> dict | None:
    """当前剧本对策：scenario_playbook 默认模板库（production）只读检索。

    返回 {template_id, action, action_zh, max_add_position, no_add_above_price,
    reduce_trigger_pct, risk_escalation}；scenario 未知/无模板 → None。
    """
    if not scenario:
        return None
    from zephyr.plan_engine.scenario_playbook import default_library

    lib = default_library()
    for tpl in lib.templates:
        if tpl.scenario == scenario:
            return {
                "template_id": tpl.template_id,
                "action": tpl.holding_action.value,
                "action_zh": _ACTION_ZH.get(tpl.holding_action.value, tpl.holding_action.value),
                "max_add_position": tpl.operation_boundary.max_add_position,
                "no_add_above_price": tpl.operation_boundary.no_add_above_price,
                "reduce_trigger_pct": tpl.operation_boundary.reduce_trigger_pct,
                "risk_escalation": tpl.risk_escalation,
            }
    return None


def fetch_next_day_inertia(
    symbol: str = "000300",
    forecaster: object = None,
) -> tuple[dict | None, str | None]:
    """今日→明日惯性：MOD-SIG-037 次日 8 态概率分布（production 可查询产物）。

    Args:
        symbol: 市场代理指数（默认沪深300，与 MOD-SIG-037 默认一致）。
        forecaster: 依赖注入位（测试 mock；None=NextDay8StateForecaster() 走 CH）。

    Returns:
        (inertia dict, error)。inertia 含 8 态分布 + 三桶聚合（上行/下行/震荡，
        展示口径）+ 方向判定与操作联动提示；不可用 → (None, error)。
    """
    try:
        if forecaster is None:
            from zephyr.signal_ashare.next_day_8state_forecast import NextDay8StateForecaster

            forecaster = NextDay8StateForecaster()
        fc = forecaster.forecast(symbol)
    except Exception as exc:  # noqa: BLE001 — fail-open：数据缺失/历史不足→待数据
        log.warning("次日 8 态预测不可用 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"惯性推演：{type(exc).__name__}"

    probs = {s.value: float(p) for s, p in fc.probabilities.items()}
    bucket_up = round(sum(probs.get(s, 0.0) for s in _BUCKET_UP), 4)
    bucket_down = round(sum(probs.get(s, 0.0) for s in _BUCKET_DOWN), 4)
    bucket_flat = round(sum(probs.get(s, 0.0) for s in _BUCKET_FLAT), 4)
    top_bucket = max((("up", bucket_up), ("down", bucket_down), ("flat", bucket_flat)), key=lambda kv: kv[1])[0]
    return {
        "symbol": symbol,
        "current_state": fc.current_state.value,
        "current_state_zh": _STATE8_ZH.get(fc.current_state.value, fc.current_state.value),
        "probs": probs,
        "top_state": fc.top_state.value,
        "top_state_zh": _STATE8_ZH.get(fc.top_state.value, fc.top_state.value),
        "top_probability": fc.top_probability,
        "confidence": fc.confidence,
        "n_transitions": fc.n_transitions,
        "bucket_up": bucket_up,
        "bucket_down": bucket_down,
        "bucket_flat": bucket_flat,
        "direction": top_bucket,
    }, None


def fetch_index_regime_panel(
    trade_date: str | None = None,
    panel_fn: Callable[..., Any] | None = None,
) -> tuple[dict | None, str | None]:
    """四指数 regime 面板（IDX-02 前端接入，消费 MOD-REGIME-008）。

    Args:
        trade_date: 面板 as-of 日（None=各指数在库最新交易日）。
        panel_fn: 依赖注入位（测试 mock；None=compute_index_regime_panel，HMM
            拟合耗秒级，异常/缺数据 → 该后端自身卡片降级，本层再兜底 fail-open）。

    Returns:
        (panel dict, error)。
    """
    try:
        if panel_fn is None:
            from zephyr.regime.index_regime_panel import compute_index_regime_panel

            panel_fn = compute_index_regime_panel
        panel = panel_fn(trade_date)
        return panel.to_dict() if hasattr(panel, "to_dict") else dict(panel), None
    except Exception as exc:  # noqa: BLE001 — fail-open：HMM/数据通道异常→待接入
        log.warning("四指数 regime 面板不可用 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"四指数面板：{type(exc).__name__}"


def fetch_batch_boundaries(
    trade_date: str,
    db_path: object = None,
) -> tuple[list[dict] | None, str | None]:
    """缺口⑦：候选股批量边界回查（MOD-PLAN-012 落库 tomorrow_boundary 族，只读）。

    Returns:
        (boundaries, error)。boundaries=payload dict 列表（symbol/box_upper/
        box_lower/max_add_position/no_add_price/must_exit_price/breakout_confirm/
        target_date）；[]=当日批量未跑（待数据）；None=查询通道异常。
        单行 payload 解析失败跳过留痕（不炸整批）。
    """
    try:
        rows = query_predictions(
            trade_date=trade_date,
            module=_MODULE_BOUNDARY,
            prediction_type=_PT_TOMORROW_BOUNDARY,
            limit=_BOUNDARY_QUERY_LIMIT,
            db_path=db_path,
        )
    except Exception as exc:  # noqa: BLE001 — fail-open：查询异常降级"待数据"
        log.warning("批量边界查询异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"批量边界：{type(exc).__name__}"
    items: list[dict] = []
    for row in rows:
        try:
            payload = json.loads(row["payload_json"])
        except Exception as exc:  # noqa: BLE001 — 单行解析失败跳过留痕
            log.warning("批量边界 payload 解析失败跳过: %s: %s", type(exc).__name__, exc)
            continue
        if isinstance(payload, dict) and payload.get("symbol"):
            items.append(payload)
    return items, None


def fetch_sit_out_list(
    trade_date: str,
    sources: dict | None = None,
) -> tuple[dict | None, str | None]:
    """缺口⑩：禁做清单（MOD-PLAN-014 三源合成，纯函数零 DB/CH）。

    Args:
        trade_date: 页面交易日。
        sources: 三源装配注入位 {events, stopped_symbols, limit_down_symbols,
            war_pool_symbols}（event 实例为 MOD-PLAN-014 CalendarEvent 契约形状，
            dict 亦可，本层负责还原）；None=三源未装配 → (None, None) 待接入
            （G4 反误导：源未接不输出"今日无禁做"假阴性）。

    Returns:
        (sit_out dict, error)。
    """
    if sources is None:
        return None, None
    try:
        from zephyr.plan_engine.sit_out_list import (
            CalendarEvent,
            StoppedSymbol,
            build_sit_out_list,
        )

        events = [
            ev if isinstance(ev, CalendarEvent) else CalendarEvent(**ev)
            for ev in (sources.get("events") or ())
        ]
        stopped = [
            s if isinstance(s, StoppedSymbol) else StoppedSymbol(**s)
            for s in (sources.get("stopped_symbols") or ())
        ]
        sit = build_sit_out_list(
            trade_date,
            events=events,
            stopped_symbols=stopped,
            limit_down_symbols=sources.get("limit_down_symbols") or (),
            war_pool_symbols=sources.get("war_pool_symbols"),
        )
        return sit.to_dict(), None
    except Exception as exc:  # noqa: BLE001 — fail-open：源数据非法/合成异常不炸页面
        log.warning("禁做清单合成异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"禁做清单：{type(exc).__name__}"


def fetch_correlation_netting(
    positions: dict | None = None,
    correlation_pairs: object = (),
    threshold: float | None = None,
    as_of: str | None = None,
) -> tuple[dict | None, str | None]:
    """缺口⑨：相关性净额（GAP-F-04 query_correlation_netting 展示层消费）。

    Args:
        positions: {symbol: 权重}（上游装配注入；None=持仓/相关性源未装配 →
            (None, None) 待接入，G4 反误导不输出假"无净额"）。
        correlation_pairs: [(a, b, rho)]（上游注入）。
        threshold: 聚合阈值（None=口径默认 0.7，对齐 MOD-PF-006 C5）。
        as_of: 数据日期（展示用）。

    Returns:
        (netting dict, error)。
    """
    if positions is None:
        return None, None
    try:
        from zephyr.frontend.services.dashboard_feeds import query_correlation_netting

        kwargs: dict[str, Any] = {"as_of": as_of}
        if threshold is not None:
            kwargs["threshold"] = threshold
        return query_correlation_netting(positions, correlation_pairs or (), **kwargs), None
    except Exception as exc:  # noqa: BLE001 — fail-open：输入非法/计算异常不炸页面
        log.warning("相关性净额计算异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"相关性净额：{type(exc).__name__}"


def _parse_debate_output(output: object, row: tuple) -> dict | None:
    """解析 llm_daily_analysis output_json 为 W4 展示 dict（不合格 → None）。"""
    if not isinstance(output, dict) or output.get("mode") != _LLM_MODE_V2:
        return None
    debate = output.get("debate") or {}
    bull = str(debate.get("bull") or "").strip() or None
    bear = str(debate.get("bear") or "").strip() or None
    if bull is None and bear is None:
        return None
    analysis = output.get("analysis")
    return {
        "bull": bull,
        "bear": bear,
        "analysis": analysis if isinstance(analysis, dict) else None,
        "model_version": row[1],
        "prompt_version": row[2],
        "created_at": row[3],
    }


def _query_debate_row(resolved: Path, trade_date: str) -> tuple | None:
    """查当日最新 v2 辩论 success 行（无行 → None）。"""
    from zephyr.shared.io.sqlite_factory import get_db_connection

    conn = get_db_connection(resolved)
    try:
        return conn.execute(
            _SQL_LLM_DEBATE_LATEST,
            (trade_date, f"%{_LLM_DEBATE_SUFFIX}", _LLM_STATUS_SUCCESS),
        ).fetchone()
    finally:
        conn.close()


def fetch_warroom_debate(
    trade_date: str,
    db_path: object = None,
) -> tuple[dict | None, str | None]:
    """W4 多空辩论台：LLM 盘前 v2 辩论落库产物（缺口⑧ P3 展示层）。

    数据源=governance.db llm_daily_analysis（MOD-PLAN-007 debate_mode=True 跑批
    落库，prompt_version 带 "+debate" 后缀的最新 success 行）：多头/空头陈词 +
    综合席三情景裁决。交易员综合/风控 veto（MOD-PLAN-013 四角色链 testing）
    未接日循环跑批，不在本通道产出（渲染层恒标"待接入"）。

    Returns:
        (debate dict, error)。当日无 v2 辩论落库行/库不存在/表未建（未启用/未跑批）
        → (None, None)——正常态非异常；解析异常 → (None, error) fail-open。
    """
    try:
        resolved = Path(db_path) if db_path is not None else DB_PATH
        if not resolved.exists():  # 只读通道不建库（connect 副作用创建空文件）
            return None, None
        row = _query_debate_row(resolved, trade_date)
        if row is None:
            return None, None
        return _parse_debate_output(json.loads(row[0]), row), None
    except sqlite3.OperationalError as exc:  # 表未建=从未跑批=待接入（正常态非异常）
        if "no such table" in str(exc).lower():
            return None, None
        log.warning("W4 辩论产物查询异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"辩论台：{type(exc).__name__}"
    except Exception as exc:  # noqa: BLE001 — fail-open：解析异常不炸页面
        log.warning("W4 辩论产物查询异常 fail-open: %s: %s", type(exc).__name__, exc)
        return None, f"辩论台：{type(exc).__name__}"


def fetch_warroom(
    trade_date: str | None = None,
    db_path: object = None,
    forecaster: object = None,
    panel_fn: Callable[..., Any] | None = None,
    index_symbol: str = "000300",
    positions: dict | None = None,
    correlation_pairs: object = (),
    netting_threshold: float | None = None,
    sit_out_sources: dict | None = None,
) -> WarroomData:
    """作战室页聚合取数（全通道 fail-open，单通道异常不炸页面）。

    Args:
        trade_date: 页面交易日（None=本地时区今日）。
        db_path: prediction_log 库路径注入位（None=DB_PATH SSoT）。
        forecaster: MOD-SIG-037 注入位（测试 mock）。
        panel_fn: MOD-REGIME-008 注入位（测试 mock）。
        index_symbol: 惯性推演市场代理指数。
        positions: 相关性净额持仓注入位（None=未装配待接入）。
        correlation_pairs: 相关性净额相关性对注入位。
        netting_threshold: 净额聚合阈值（None=口径默认 0.7）。
        sit_out_sources: 禁做清单三源注入位（None=未装配待接入）。
    """
    v_date = trade_date or _today_str()
    errors: list[str] = []

    plan, plan_asof, err = fetch_warroom_plan(v_date, db_path)
    if err:
        errors.append(err)
    outcome, err = fetch_warroom_outcome(v_date, db_path)
    if err:
        errors.append(err)

    # 当前剧本：盘后已回写以实际命中格为准，否则用预案最终情景（竞价段判定）
    scenario = None
    if outcome is not None:
        scenario = outcome.get("actual_scenario")
    if scenario is None and plan is not None:
        scenario = plan.get("final_scenario")
    try:
        playbook = fetch_playbook_action(scenario)
    except Exception as exc:  # noqa: BLE001 — fail-open
        log.warning("playbook 检索异常 fail-open: %s", exc)
        playbook = None
        errors.append(f"剧本对策：{type(exc).__name__}")

    inertia, err = fetch_next_day_inertia(index_symbol, forecaster)
    if err:
        errors.append(err)
    index_panel, err = fetch_index_regime_panel(v_date, panel_fn)
    if err:
        errors.append(err)

    boundaries, err = fetch_batch_boundaries(v_date, db_path)
    if err:
        errors.append(err)
    sit_out, err = fetch_sit_out_list(v_date, sit_out_sources)
    if err:
        errors.append(err)
    netting, err = fetch_correlation_netting(
        positions, correlation_pairs, threshold=netting_threshold, as_of=v_date
    )
    if err:
        errors.append(err)
    debate, err = fetch_warroom_debate(v_date, db_path)
    if err:
        errors.append(err)

    return WarroomData(
        trade_date=v_date,
        plan=plan,
        plan_asof=plan_asof,
        outcome=outcome,
        playbook=playbook,
        inertia=inertia,
        index_panel=index_panel,
        boundaries=boundaries,
        sit_out=sit_out,
        netting=netting,
        debate=debate,
        errors=errors,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 渲染层（payload + '_layout' 挂 Panel 布局；pn=None 仅返回 dict）
# ──────────────────────────────────────────────────────────────────────────────


def _pct(v: object, digits: int = 1) -> str:
    """比率 → 百分比字符串（None 安全）。"""
    try:
        return f"{float(v):+.{digits}%}" if digits else f"{float(v):.0%}"
    except (TypeError, ValueError):
        return "—"


def _pct_plain(v: object, digits: int = 1) -> str:
    try:
        return f"{float(v):.{digits}%}"
    except (TypeError, ValueError):
        return "—"


def _scenario_zh(scenario: object) -> str:
    if not isinstance(scenario, str) or not scenario:
        return "未知"
    zh = _SCENARIO_ZH.get(scenario)
    return f"{zh[0]}（{scenario}）" if zh else scenario


def _fmt_price(v: object) -> str:
    return f"{float(v):g}" if isinstance(v, (int, float)) else "待 boundary 注入"


def _md(text: str) -> Any:
    return pn.pane.Markdown(text, sizing_mode="stretch_width")


def _render_plan_section(data: WarroomData) -> Any:
    """区① 前日预案区（上一交易日生成的今日预案全文+关键价位/条件单）。"""
    items: list[Any] = []
    plan = data.plan
    if plan is None:
        items.append(pn.pane.Alert(
            f"今日（{data.trade_date}）预案未生成——prediction_log 无 scenario_plan 行"
            "（盘前管线 MOD-PLAN-018 未跑或落库失败），本区待数据",
            alert_type="warning",
        ))
        return pn.Card(*items, title="① 前日预案（上一交易日生成 · 今日执行）", sizing_mode="stretch_width")

    final_scenario = plan.get("final_scenario")
    confidence = plan.get("confidence_scale")
    degraded = plan.get("degraded")
    summary = (
        f"**最终剧本**：{_scenario_zh(final_scenario)}　"
        f"**信度缩放**：{confidence if confidence is not None else '—'}　"
        f"**预案生成时点**：{data.plan_asof or '—'}"
    )
    if degraded:
        summary += "　⚠️ **降级留痕**（竞价验证段降级或 boundary 缺省，价位字段可能为 None）"
    items.append(_md(summary))

    # 三情景预案卡（条件单=关键价位字段）
    cards: list[Any] = []
    for sp in plan.get("three_scenarios") or []:
        name_zh = _PLAN_NAME_ZH.get(sp.get("name"), sp.get("name", "?"))
        stance_zh = _STANCE_ZH.get(sp.get("stance"), sp.get("stance", "?"))
        lo, hi = sp.get("open_pct_min"), sp.get("open_pct_max")
        trigger = (
            f"开盘 ≥ {_pct(lo)}"
            if hi is None
            else (f"开盘 ≤ {_pct(hi)}" if lo is None else f"开盘 {_pct(lo)} ~ {_pct(hi)}")
        )
        lines = [
            f"**触发**：{trigger}　**档位**：{stance_zh}（final_shift={sp.get('final_shift', 0):+.1f}）",
            f"**加仓上限**：{_pct_plain(sp.get('max_add_position'), 0)}　"
            f"**禁加仓价**：{_fmt_price(sp.get('no_add_price'))}",
            f"**减仓触发价**：{_fmt_price(sp.get('reduce_trigger_price'))}　"
            f"**必出止盈价**：{_fmt_price(sp.get('must_exit_price'))}",
            "",
            *["- " + a for a in (sp.get("actions") or [])],
        ]
        cards.append(pn.Card(_md("\n\n".join(lines)), title=name_zh, sizing_mode="stretch_width"))
    if cards:
        items.append(pn.GridBox(*cards, ncols=3, sizing_mode="stretch_width"))

    # 竞价三细节（9:25 验证段，44号 §9.11）
    av = plan.get("auction_verification")
    if av:
        d1 = _pct(av.get("deviation"), 2)
        d2 = f"{float(av['volume_ratio']):.2f}×" if av.get("volume_ratio") is not None else "—"
        d3 = f"{float(av['fake_ratio']):.2f}" if av.get("fake_ratio") is not None else "—"
        premium = _pct(av.get("yesterday_limit_premium"), 2)
        verdicts = []
        if av.get("direction_void"):
            verdicts.append("⛔ D3 虚假申报（fake_ratio>0.6）→ 竞价方向信号作废")
        if av.get("confirmed"):
            verdicts.append("✅ D2 放量确认（≥1.2× 且方向一致）")
        if av.get("volume_shrink"):
            verdicts.append("⚠️ D2 量缩（<1.0×）→ 降信半档")
        if av.get("direction_consistent") is False:
            verdicts.append("⚠️ D1 与 gap_adj 方向背离 → 降信半档")
        items.append(_md(
            "**竞价三细节（9:25）**："
            f"D1 虚拟开盘价偏离 {d1} · D2 匹配量放大 {d2} · D3 撤单比 {d3} · "
            f"昨日涨停竞价溢价 {premium}（status={av.get('status', '?')}）"
            + ("　" + "　".join(verdicts) if verdicts else "")
        ))
    else:
        items.append(_md("**竞价三细节**：未执行（盘前跑批无竞价段）"))

    reasons = plan.get("reasons") or []
    if reasons:
        items.append(pn.Card(
            _md("\n".join("- " + r for r in reasons)),
            title="决策理由链（留痕）",
            collapsed=True,
            sizing_mode="stretch_width",
        ))
    return pn.Card(*items, title="① 前日预案（上一交易日生成 · 今日执行）", sizing_mode="stretch_width")


def _render_intraday_section(data: WarroomData) -> Any:
    """区② 实时走势分析区（分时段判定 + 当前走势剧本及对策）。"""
    items: list[Any] = []
    av = (data.plan or {}).get("auction_verification") or {}
    outcome = data.outcome

    # 分时段判定表（只读产物；无后端产物的时段一律"待接入"标注）
    auction_cell = "待数据（预案未生成）"
    if av:
        direction_zh = {"UP": "高开", "DOWN": "低开", "FLAT": "平开"}.get(av.get("direction"), "—")
        flags = []
        if av.get("direction_void"):
            flags.append("D3 作废（虚假申报）")
        elif av.get("confirmed"):
            flags.append("D2 放量确认")
        elif av.get("volume_shrink"):
            flags.append("D2 量缩降信")
        auction_cell = f"{direction_zh}倾向（D1={_pct(av.get('deviation'), 2)}）" + (
            "，" + "、".join(flags) if flags else ""
        )
    trend_cell = "待接入（盘后 outcome 回写后可见；C24 时序分段状态机未施工）"
    if outcome is not None and outcome.get("trend_pct") is not None:
        trend_cell = (
            f"开盘 {_pct(outcome.get('open_pct'), 2)}，30 分钟走势 {_pct(outcome.get('trend_pct'), 2)}"
            f"（{outcome.get('trend_source', '?')}）→ {_scenario_zh(outcome.get('actual_scenario'))}"
        )
    pending_cell = "待接入（开盘 15 分钟 4 型：直驱/试探驱动/拒绝反转 Open Rejection Reverse/震荡——C24 时序分段状态机未施工）"
    rows = [
        "| 时段 | 判定 | 数据源 |",
        "|---|---|---|",
        f"| 竞价段 9:15-9:25 | {auction_cell} | scenario_plan.auction_verification（已落库） |",
        f"| 开盘后 30 分钟 9:30-10:00 | {trend_cell} | outcome 族（MOD-PLAN-008 盘后回写） |",
        f"| 上午段 10:00-11:30 | {pending_cell} | — |",
        f"| 下午段 13:00-15:00 | {pending_cell} | — |",
    ]
    items.append(_md("\n".join(rows)))

    # 当前走势剧本
    plan = data.plan or {}
    final_scenario = outcome.get("actual_scenario") if outcome else plan.get("final_scenario")
    scenario_src = "盘后实际命中（outcome 回写）" if outcome else "9:25 竞价二次匹配（预案判定）"
    if final_scenario:
        zh = _SCENARIO_ZH.get(final_scenario, (final_scenario, ""))
        lines = [f"**当前走势剧本**：{zh[0]}（{final_scenario}）——{zh[1]}", f"判定来源：{scenario_src}"]
        if outcome is not None and outcome.get("hit") is not None:
            lines.append(
                f"**预案验证**：{'✅ 命中' if outcome.get('hit') else '❌ 未命中'}"
                f"（预测 {_scenario_zh(outcome.get('scenario'))} vs 实际 {_scenario_zh(outcome.get('actual_scenario'))}）"
            )
        elif not outcome:
            lines.append(
                f"信度缩放={plan.get('confidence_scale', '—')}；"
                "盘中滚动修正待 C24 时序分段状态机接入（待接入）"
            )
        pb = data.playbook
        if pb:
            boundary_bits = [f"加仓上限 {_pct_plain(pb.get('max_add_position'), 0)}"]
            if pb.get("no_add_above_price") is not None:
                boundary_bits.append(f"禁加价 {pb['no_add_above_price']:g}")
            if pb.get("reduce_trigger_pct") is not None:
                boundary_bits.append(f"减仓触发 -{float(pb['reduce_trigger_pct']):.0%}")
            esc = {0: "常规", 1: "提级", 2: "紧急"}.get(pb.get("risk_escalation"), "?")
            lines.append(
                f"**剧本对策**（playbook 模板 {pb.get('template_id')}，production）："
                f"{pb.get('action_zh')}　{' · '.join(boundary_bits)}　风控升级={esc}"
            )
        items.append(_md("\n\n".join(lines)))
    else:
        items.append(_md("**当前走势剧本**：待数据（预案未生成且 outcome 未回写）"))
    return pn.Card(*items, title="② 实时走势分析（今日走势分时段判定）", sizing_mode="stretch_width")


def _render_inertia_section(data: WarroomData) -> Any:
    """区③ 今日→明日惯性区（MOD-SIG-037 8 态分布 → 三桶展示聚合）。"""
    items: list[Any] = []
    inertia = data.inertia
    if inertia is None:
        items.append(pn.pane.Alert(
            "次日 8 态预测不可用（指数 K 线缺失/历史不足/数据通道异常）——本区待数据",
            alert_type="warning",
        ))
        return pn.Card(*items, title="③ 今日 → 明日惯性推演", sizing_mode="stretch_width")

    direction = inertia["direction"]
    direction_zh = {"up": "偏多惯性", "down": "偏空惯性", "flat": "震荡无方向"}[direction]
    items.append(_md(
        f"**明日惯性判定：{direction_zh}**　"
        f"上行 {_pct_plain(inertia['bucket_up'])} · 下行 {_pct_plain(inertia['bucket_down'])} · "
        f"震荡 {_pct_plain(inertia['bucket_flat'])}"
    ))
    items.append(_md(
        f"**依据**：今日盘面态={inertia['current_state_zh']}；"
        f"次日众数态={inertia['top_state_zh']}（{_pct_plain(inertia['top_probability'])}）；"
        f"置信度={inertia['confidence']:.2f}（转移样本 {inertia['n_transitions']}）　"
        f"**8 态分布**：" + " · ".join(
            f"{_STATE8_ZH.get(s, s)} {_pct_plain(p)}" for s, p in inertia["probs"].items()
        )
    ))
    alert_type, hint = _DIRECTION_HINT[direction]
    items.append(pn.pane.Alert(f"今日操作联动：{hint}", alert_type=alert_type))
    items.append(_md(
        "> 只出概率分布不出点位（90号 §7 BM-SEL-04 铁律）；T+1 隔夜风险——"
        "今天买入明天才能卖，\"明天会怎样\"决定\"今天能不能买\""
    ))
    return pn.Card(*items, title="③ 今日 → 明日惯性推演（服务\"明日下跌概率大则今日延迟建仓\"类决策）", sizing_mode="stretch_width")


def _render_index_panel_section(data: WarroomData) -> Any:
    """区④ 四指数状态卡（IDX-02 前端接入，消费 MOD-REGIME-008）。"""
    items: list[Any] = []
    panel = data.index_panel
    if panel is None:
        items.append(pn.pane.Alert(
            "四指数 regime 面板不可用（K 线数据/拟合通道异常）——待接入（IDX-02）",
            alert_type="warning",
        ))
        return pn.Card(*items, title="④ 四指数状态卡（IDX-02 · 1 引擎×4 代理 regime 面板）", sizing_mode="stretch_width")

    if panel.get("degraded"):
        items.append(pn.pane.Alert("面板级降级：全部指数卡缺数据/降级", alert_type="warning"))
    cards: list[Any] = []
    for card in panel.get("cards") or []:
        title = f"{card.get('name', '?')}（{card.get('code', '?')}）"
        if card.get("degraded"):
            body = f"⚠️ 降级：{card.get('degrade_reason') or '数据缺失'}"
        else:
            dominant = card.get("dominant_regime")
            probs = card.get("probabilities") or {}
            top2 = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[:2]
            rank = card.get("rank")
            lines = [
                f"**Regime**：{_REGIME_ZH.get(dominant, dominant)}（置信 {_pct_plain(card.get('confidence'))}）",
                f"**强弱位次**：{f'第 {rank}' if rank else '—'}　"
                f"**近20日收益**：{_pct(card.get('recent_return'), 2)}",
                "**概率 Top2**：" + " · ".join(f"{_REGIME_ZH.get(s, s)} {_pct_plain(p)}" for s, p in top2),
            ]
            if card.get("hmm_degraded"):
                lines.append("⚠️ HMM 拟合降级（均匀先验）")
            body = "\n\n".join(lines)
        cards.append(pn.Card(_md(body), title=title, sizing_mode="stretch_width"))
    if cards:
        items.append(pn.GridBox(*cards, ncols=4, sizing_mode="stretch_width"))

    for alert in panel.get("divergence_alerts") or []:
        items.append(pn.pane.Alert(f"⚠️ 背离警示：{alert.get('detail', '')}", alert_type="warning"))
    items.append(_md(
        f"> 数据截至 {panel.get('trade_date', '—')}；只输出 regime 概率分布与强弱排序，"
        "不出点位/方向预测（90号 §7 铁律）；强弱排序=近 20 日已实现收益/波动调整"
    ))
    return pn.Card(*items, title="④ 四指数状态卡（IDX-02 · 1 引擎×4 代理 regime 面板）", sizing_mode="stretch_width")


def _build_scenario_grid(data: WarroomData) -> list[dict[str, Any]]:
    """缺口⑥展示层：3×3 情景矩阵 9 格（纯函数，无 panel 依赖，可 JSON 序列化）。

    格概率=plan.grid_probabilities 落库字段（缺口⑥后端 BM-SEL-04 暂缓不抢建，
    未落库一律 prob=None 标"概率待接入"）；格内动作=playbook production 模板；
    最可能格=盘后 outcome.actual_scenario 优先，否则 plan.final_scenario。
    """
    plan = data.plan or {}
    grid_probs = plan.get("grid_probabilities")
    grid_probs = grid_probs if isinstance(grid_probs, dict) else {}
    focus = (data.outcome or {}).get("actual_scenario") or plan.get("final_scenario")

    cells: list[dict[str, Any]] = []
    for row in _GRID_ROWS:
        for col in _GRID_COLS:
            key = _GRID_SCENARIO[(row, col)]
            name_zh, logic = _SCENARIO_ZH[key]
            prob = grid_probs.get(key)
            action_zh = None
            try:
                pb = fetch_playbook_action(key)
                action_zh = pb["action_zh"] if pb else None
            except Exception as exc:  # noqa: BLE001 — fail-open：模板检索异常不影响格结构
                log.warning("矩阵格 playbook 检索异常 fail-open（%s）: %s", key, exc)
            cells.append({
                "scenario": key,
                "row": row,
                "row_zh": _GRID_ROW_ZH[row],
                "col": col,
                "col_zh": _GRID_COL_ZH[col],
                "name_zh": name_zh,
                "logic": logic,
                "prob": float(prob) if isinstance(prob, (int, float)) else None,
                "action_zh": action_zh,
                "is_focus": key == focus,
            })
    return cells


def _render_scenario_matrix_section(cells: list[dict[str, Any]]) -> Any:
    """区⑤ W2 3×3 情景矩阵（缺口⑥ P2 展示层）。"""
    has_prob = any(c["prob"] is not None for c in cells)
    cards: list[Any] = []
    for c in cells:
        prob_text = f"**概率**：{_pct_plain(c['prob'])}" if c["prob"] is not None else "**概率**：待接入（缺口⑥ BM-SEL-04 暂缓）"
        body = "\n\n".join([
            prob_text,
            f"**动作**：{c['action_zh'] or '—'}",
            c["logic"],
        ])
        title = ("⭐ " if c["is_focus"] else "") + f"{c['row_zh']}×{c['col_zh']} {c['name_zh']}"
        cards.append(pn.Card(_md(body), title=title, sizing_mode="stretch_width"))
    intro = (
        "行=开盘形态（项目真实阈值 ±2%），列=开盘后 30 分钟走势（分时均价线 VWAP 判定）；"
        "9 格封闭穷举，任何行情落下都有格子接住；⭐=当前判定格"
    )
    if not has_prob:
        intro += "；**格概率模型待接入**（缺口⑥，90号 §7 BM-SEL-04 暂缓裁定不抢建，当前以最可能格+信度缩放表达）"
    items: list[Any] = [
        _md(intro),
        pn.GridBox(*cards, ncols=3, sizing_mode="stretch_width"),
        _md("> 只展示概率分布/动作对策，不出点位方向预测（90号 §7 铁律）；格内个股方案点位由 ⑥ 批量边界区供给"),
    ]
    return pn.Card(*items, title="⑤ W2 3×3 情景矩阵（完备预案·9 格封闭穷举）", sizing_mode="stretch_width")


def _render_boundaries_section(data: WarroomData) -> Any:
    """区⑥ W2b 批量边界（缺口⑦：MOD-PLAN-012 落库 tomorrow_boundary 族回查）。"""
    items: list[Any] = []
    boundaries = data.boundaries
    if boundaries is None:
        items.append(pn.pane.Alert(
            "批量边界查询通道异常（fail-open 降级）——本区待数据",
            alert_type="warning",
        ))
    elif not boundaries:
        items.append(pn.pane.Alert(
            f"今日（{data.trade_date}）无 tomorrow_boundary 落库行——盘后批量管线"
            "（MOD-PLAN-012）未跑或候选清单为空，本区待数据；未算股一律视为「待计算」禁凭感觉操作",
            alert_type="warning",
        ))
    else:
        rows = [
            "| 标的 | 箱体（下沿~上沿） | 加仓上限 | 禁加仓价 | 必出价 | 突破验证 |",
            "|---|---|---|---|---|---|",
        ]
        for b in boundaries:
            box = f"{_fmt_price(b.get('box_lower'))} ~ {_fmt_price(b.get('box_upper'))}"
            rows.append(
                f"| {b.get('symbol')} | {box} | {_pct_plain(b.get('max_add_position'), 0)} | "
                f"{_fmt_price(b.get('no_add_price'))} | {_fmt_price(b.get('must_exit_price'))} | "
                f"{'放量站稳10分钟' if b.get('breakout_confirm') else '—'} |"
            )
        items.append(_md("\n".join(rows)))
        items.append(_md(
            f"> 共 {len(boundaries)} 票（MOD-PLAN-012 盘后批量，生效日="
            f"{boundaries[0].get('target_date', '—')}）；失效条件（逻辑破坏点）优先于价格触发"
        ))
    return pn.Card(*items, title="⑥ W2b 候选股/持仓股明日边界（批量栏杆）", sizing_mode="stretch_width")


def _render_risk_envelope_section(data: WarroomData) -> Any:
    """区⑦ W5 风险包络（缺口⑨ 相关性净额 + 缺口⑩ 禁做清单）。"""
    items: list[Any] = []

    netting = data.netting
    if netting is None:
        items.append(pn.pane.Alert(
            "相关性净额：持仓/相关性对上游未装配——待接入（GAP-F-04 查询函数已就绪，"
            "防「五个仓位实则一个赌注」）",
            alert_type="warning",
        ))
    else:
        items.append(_md(
            f"**相关性净额**：持仓 {netting.get('gross_position_count')} 笔 → "
            f"净风险单位 **{netting.get('net_risk_units')}** 个"
            f"（合并 {netting.get('netting_reduction')} 笔，|ρ|≥{netting.get('threshold')}）"
        ))
        for cl in netting.get("clusters") or []:
            items.append(pn.pane.Alert(
                f"高相关簇合并计 1 笔风险：{' + '.join(cl.get('members') or [])}"
                f"（max ρ={cl.get('max_pair_rho')}，合计权重 {_pct_plain(cl.get('combined_weight'))}）",
                alert_type="warning",
            ))

    sit_out = data.sit_out
    if sit_out is None:
        items.append(pn.pane.Alert(
            "禁做清单：三源（事件日历/止损状态/作战池）未装配——待接入"
            "（MOD-PLAN-014 生成器已就绪；违反清单=预案外操作，W0 归因记执行不一致）",
            alert_type="warning",
        ))
    else:
        entries = sit_out.get("entries") or []
        if not entries:
            note = (sit_out.get("annotations") or ["今日禁做清单空"])[0]
            items.append(pn.pane.Alert(f"禁做清单：{note}", alert_type="success"))
        else:
            lines = [
                f"- **{_SITOUT_ACTION_ZH.get(e.get('action'), e.get('action'))}**"
                f"（{e.get('scope')}{('/' + e['target']) if e.get('target') else ''}）：{e.get('reason')}"
                for e in entries
            ]
            items.append(pn.pane.Alert(
                f"⛔ 今日禁做清单 {len(entries)} 条（违反=预案外操作，W0 归因记执行不一致）",
                alert_type="danger",
            ))
            items.append(_md("\n".join(lines)))
        for note in sit_out.get("notes") or []:
            items.append(_md(f"> {note}"))
    return pn.Card(*items, title="⑦ W5 风险包络（相关性净额 + 禁做清单）", sizing_mode="stretch_width")


def _render_debate_section(data: WarroomData) -> Any:
    """区⑧ W4 多空辩论台（缺口⑧ P3 展示层）。

    只读 llm_daily_analysis v2 辩论落库行（MOD-PLAN-007）；交易员综合/风控 veto
    （MOD-PLAN-013 四角色链）未接日循环 → 恒"待接入"（G4 反误导）。
    """
    if data.debate is None:
        return pn.Card(
            _md(
                "**待接入**：今日无 v2 多空辩论落库产物——44号 §9.14 `debate_mode` 默认 "
                "False（v1 单调用验证期）；启用后由盘前跑批落库自动呈现。"
                "交易员综合/风控 veto 位（MOD-PLAN-013 四角色链 testing）待日循环接线。"
            ),
            title="⑧ W4 多空辩论台（预案质量门）",
            collapsed=True,
            sizing_mode="stretch_width",
        )
    d = data.debate
    items: list[Any] = []
    bull_body = d.get("bull") or "_多头陈词缺失（落库行未含 bull 段）_"
    bear_body = d.get("bear") or "_空头陈词缺失（落库行未含 bear 段）_"
    items.append(pn.Row(
        pn.Card(_md(bull_body), title="多头研究员", sizing_mode="stretch_width"),
        pn.Card(_md(bear_body), title="空头研究员", sizing_mode="stretch_width"),
        sizing_mode="stretch_width",
    ))
    analysis = d.get("analysis")
    if analysis:
        scenarios = analysis.get("scenarios") or {}

        def _sc_line(key: str, zh: str) -> str:
            s = scenarios.get(key) or {}
            prob = s.get("prob")
            prob_text = _pct_plain(float(prob) * 100.0) if isinstance(prob, (int, float)) else "—"
            return f"- **{zh}**：概率 {prob_text}；{s.get('action_boundary') or '—'}"

        lines = [_sc_line("gap_up", "高开"), _sc_line("flat", "平开"), _sc_line("gap_down", "低开")]
        risk_points = [str(p) for p in (analysis.get("risk_points") or [])]
        if risk_points:
            lines.append("- **风险点**：" + "；".join(risk_points))
        watch = [str(w) for w in (analysis.get("watch_sectors") or [])]
        if watch:
            lines.append("- **关注板块**：" + "、".join(watch))
        note = analysis.get("confidence_note")
        if note:
            lines.append(f"> 置信声明：{note}")
        items.append(pn.Card(_md("\n".join(lines)), title="综合席裁决（三情景）", sizing_mode="stretch_width"))
    items.append(_md(
        "> 交易员综合 / 风控 veto 位：**待接入**——MOD-PLAN-013 四角色链已落码（testing），"
        "接日循环跑批后呈现（D3>0.6 进攻方案自动否决红色标注）。　"
        f"`model={d.get('model_version')}` `prompt={d.get('prompt_version')}`"
    ))
    return pn.Card(*items, title="⑧ W4 多空辩论台（预案质量门）", sizing_mode="stretch_width")


def _render_backlog_section() -> Any:
    """区⑨ 折叠占位（W0/W6 历史预案库，随样本积累后接入）。"""
    body = "\n".join([
        "- **W0/W6 历史预案库 + Brier 校准度**——随 prediction_log 样本积累（MOD-PLAN-018 日循环跑批）后接入",
        "- 缺口⑧ 辩论台 P3 已落展示层（本页区⑧）：消费 llm_daily_analysis v2 辩论行；MOD-PLAN-013 四角色链接线待日循环",
        "- P2 已落：缺口⑥ 9 格矩阵展示层（格概率待 BM-SEL-04 解除暂缓）/缺口⑦ 批量边界回查/缺口⑨ 相关性净额/缺口⑩ 禁做清单",
    ])
    return pn.Card(
        _md(body),
        title="⑨ 折叠占位区（W0/W6 历史预案库，随样本积累后接入）",
        collapsed=True,
        sizing_mode="stretch_width",
    )


def render_warroom(data: WarroomData) -> dict[str, Any]:
    """渲染作战室页（payload + '_layout' 挂 Panel 布局）。

    测试环境（无 panel）仅返回 dict payload。
    """
    grid = _build_scenario_grid(data)
    payload: dict[str, Any] = {
        "trade_date": data.trade_date,
        "has_plan": data.plan is not None,
        "has_outcome": data.outcome is not None,
        "has_inertia": data.inertia is not None,
        "has_index_panel": data.index_panel is not None,
        "playbook": data.playbook,
        "scenario_grid": grid,
        "grid_prob_available": any(c["prob"] is not None for c in grid),
        "boundaries": data.boundaries,
        "has_boundaries": bool(data.boundaries),
        "sit_out": data.sit_out,
        "has_sit_out": data.sit_out is not None,
        "netting": data.netting,
        "has_netting": data.netting is not None,
        "debate": data.debate,
        "has_debate": data.debate is not None,
        "errors": list(data.errors),
        "renderer": "panel" if pn is not None else "dict",
    }
    if pn is None:
        return payload

    items: list[Any] = [
        _md("## 作战指挥室（War Room）"),
        _md(
            "实盘组 · **核心三件事：昨天定的预案是什么 → 现在走势匹配哪一格 → 明天大概怎么走、今天该怎么动**　"
            "盘中不思考，只匹配执行（45号作战手册 P1+P2；页面结构=Owner 2026-08-28 裁定）"
        ),
    ]
    if data.errors:
        items.append(pn.pane.Alert(
            "部分数据通道异常（fail-open 降级，不阻断页面）：" + "；".join(data.errors),
            alert_type="warning",
        ))
    items.append(_render_plan_section(data))
    items.append(_render_intraday_section(data))
    items.append(_render_inertia_section(data))
    items.append(_render_index_panel_section(data))
    items.append(_render_scenario_matrix_section(grid))
    items.append(_render_boundaries_section(data))
    items.append(_render_risk_envelope_section(data))
    items.append(_render_debate_section(data))
    items.append(_render_backlog_section())
    payload["_layout"] = pn.Column(*items, sizing_mode="stretch_width")
    return payload


__all__: Final = [
    "WarroomData",
    "fetch_batch_boundaries",
    "fetch_correlation_netting",
    "fetch_index_regime_panel",
    "fetch_next_day_inertia",
    "fetch_playbook_action",
    "fetch_sit_out_list",
    "fetch_warroom",
    "fetch_warroom_debate",
    "fetch_warroom_outcome",
    "fetch_warroom_plan",
    "render_warroom",
]
