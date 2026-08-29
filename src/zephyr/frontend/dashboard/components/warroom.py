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
  ⑤ P2/P3 折叠占位  —— 缺口⑥~⑩（9格概率模型完整版/批量边界/辩论实例化/
                       相关性净额/禁做清单），本期不实现

渲染依赖: Panel（可选导入，测试环境零依赖仅返回 dict payload）。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Final

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.reporting.prediction_log_writer import query_predictions

log = logging.getLogger(__name__)

# prediction_log 查询口径（镜像 MOD-PLAN-008/MOD-RPT-029 常量，前端不反向 import
# plan_engine 全链以控制 app_panel 导入成本——值变更以 scenario_plan_recorder 为准）
_MODULE_SCENARIO_PLAN: Final = "plan_engine.scenario_planner"
_PT_SCENARIO_PLAN: Final = "scenario_plan"
_PT_OUTCOME: Final = "outcome"

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
        errors: 各取数通道异常留痕（fail-open 负反馈）。
    """

    trade_date: str
    plan: dict | None = None
    plan_asof: str | None = None
    outcome: dict | None = None
    playbook: dict | None = None
    inertia: dict | None = None
    index_panel: dict | None = None
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


def fetch_warroom(
    trade_date: str | None = None,
    db_path: object = None,
    forecaster: object = None,
    panel_fn: Callable[..., Any] | None = None,
    index_symbol: str = "000300",
) -> WarroomData:
    """作战室页聚合取数（全通道 fail-open，单通道异常不炸页面）。

    Args:
        trade_date: 页面交易日（None=本地时区今日）。
        db_path: prediction_log 库路径注入位（None=DB_PATH SSoT）。
        forecaster: MOD-SIG-037 注入位（测试 mock）。
        panel_fn: MOD-REGIME-008 注入位（测试 mock）。
        index_symbol: 惯性推演市场代理指数。
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

    return WarroomData(
        trade_date=v_date,
        plan=plan,
        plan_asof=plan_asof,
        outcome=outcome,
        playbook=playbook,
        inertia=inertia,
        index_panel=index_panel,
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


def _render_backlog_section() -> Any:
    """区⑤ P2/P3 折叠占位（缺口⑥~⑩，本期不实现）。"""
    body = "\n".join([
        "- **缺口⑥ 9 格概率模型完整版**（3×3 情景矩阵逐格概率）——待 P2（CAND 评审；90号 §7 BM-SEL-04 暂缓裁定不抢建，当前以最可能剧本+信度缩放表达）",
        "- **缺口⑦ 候选股批量边界**（TomorrowBoundary 对主线候选股批量出栏杆）——待 P2（Owner 2026-08-28 裁定本期仅占位；MOD-PLAN-001 单票 production 已就绪）",
        "- **缺口⑧ 交易域多空辩论实例化 W4**（多头/空头研究员→交易员→风控四角色链）——待 P3（CAND 评审；agent_debate 治理域已 production）",
        "- **缺口⑨ 相关性净额前端消费 W5**（高相关持仓合并计 1 笔风险）——待 P2（dashboard_feeds.query_correlation_netting 可接，组合域 prod 已就绪）",
        "- **缺口⑩ 禁做清单生成器 W5**（事件日历+止损状态+池外规则 → sit-out list）——待 P2（event_calendar 注册表已有）",
        "- **W0/W6 历史预案库 + Brier 校准度**——随 prediction_log 样本积累（MOD-PLAN-018 日循环跑批）后接入",
    ])
    return pn.Card(
        _md(body),
        title="⑤ P2/P3 待施工区（缺口⑥~⑩ + W0/W6，本期不实现）",
        collapsed=True,
        sizing_mode="stretch_width",
    )


def render_warroom(data: WarroomData) -> dict[str, Any]:
    """渲染作战室页（payload + '_layout' 挂 Panel 布局）。

    测试环境（无 panel）仅返回 dict payload。
    """
    payload: dict[str, Any] = {
        "trade_date": data.trade_date,
        "has_plan": data.plan is not None,
        "has_outcome": data.outcome is not None,
        "has_inertia": data.inertia is not None,
        "has_index_panel": data.index_panel is not None,
        "playbook": data.playbook,
        "errors": list(data.errors),
        "renderer": "panel" if pn is not None else "dict",
    }
    if pn is None:
        return payload

    items: list[Any] = [
        _md("## 作战指挥室（War Room）"),
        _md(
            "实盘组 · **核心三件事：昨天定的预案是什么 → 现在走势匹配哪一格 → 明天大概怎么走、今天该怎么动**　"
            "盘中不思考，只匹配执行（45号作战手册 P1；页面结构=Owner 2026-08-28 裁定）"
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
    items.append(_render_backlog_section())
    payload["_layout"] = pn.Column(*items, sizing_mode="stretch_width")
    return payload


__all__: Final = [
    "WarroomData",
    "fetch_index_regime_panel",
    "fetch_next_day_inertia",
    "fetch_playbook_action",
    "fetch_warroom",
    "fetch_warroom_outcome",
    "fetch_warroom_plan",
    "render_warroom",
]
