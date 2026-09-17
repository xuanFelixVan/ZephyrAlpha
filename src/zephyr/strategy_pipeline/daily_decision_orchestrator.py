# [BLUEPRINT] MOD-BT-214 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] zephyr.strategy_pipeline.daily_decision_orchestrator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] daily_gate_snapshot(一闸); pf_alloc.allocation_inputs(只 import 不改);
#   schemas.categories.decision_daily(表 DDL/列/SQL 真源); zephyr.data.ch_writer(写通道);
#   zephyr.data.trading_calendar(XSHG 旁证); pipeline_events(resolve_pf_alloc_trade_date/
#   SIM_DAILY_WAKE_TASKS/alert——函数级惰性导入避开事件层相互引用); PyYAML(TDM 只读查表)
# [CONSUMERS] pipeline_events(maybe_run_daily_decision 事件挂点，daily_kline SUCCESS 末棒);
#   frontend.dashboard.components.warroom(读 decision_daily); 手工补跑=__main__ 直呼
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 调度器不是策略（蓝图 §一.2）：只读齐→合成拍板→落库分发，零新增判断逻辑；
#   "今日不交易"=禁新开仓≠清仓（§一.5），保命件横切独立，本件任何故障不削弱其运行；
#   幂等=业务日级 marker 先拍板先占（S6；同日重唤醒跳过，失败不回滚记号=防重拍风暴，
#   人工重跑走 run_daily_decision(force=True)）；快照只增不改（重拍=新 run_id 追加）；
#   ingest_ts 由 DB 生成（写侧禁墙钟）；写侧唯一=本模块；D1-D7 全收敛禁新开仓/维持现状；
#   自身异常 fail-open 不留半行（D7）；首版分发=留痕+仪表盘零实盘变更（裁定#305 第 6 点）；
#   无已毕业包=安全态全链（裁定#305 第 2 点，S-OWNER-001/002 考试链 FAIL 台账在案）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_daily_decision 永不外抛（D7 fail-open：异常折进返回 action=error+告警）；
#   date 非法=ValueError（fail-closed 唯一例外）；sink 注入方决定投递语义（非 committed/durable 即抛）
# [TESTS] tests/strategy_pipeline/test_decision_orchestrator.py
# [A_module] module_id=MOD-BT-214 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] daily-decision-orchestrator-mod-bt-214-20260916
"""daily_decision_orchestrator — 日度编排器（BT-P1-031 刀 3 一器，T2 晨判拍板体）。

真源：docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md（§二 S1-S7/
§三 事件触发/§六.2 降级矩阵 D1-D7）+ 裁定#305（8 条批准点保守默认自裁，Owner 通宵全量施工令）。

定位：持有"今日不交易权"的日度拍板体——把散在三处的"今日不交易"语义（C1 预算带 0%/
sit_out_list 禁做清单/kill_switch 熔断）合成收拢为 c1_backtest.decision_daily 一行可审计
快照=当日唯一放行凭证（无快照行=无新开仓令，机会成本单向可控）。与 daily_warroom_pipeline
（MOD-PLAN-018）为并列拍板体：复用其两段编排/fail-open/幂等/次交易日解析口径，不改造其职责。

每日流程（蓝图 §二，机械时点=前一交易日盘后批尾，生效日=次交易日）：
    S1 查交易日历（trade_calendar 真源 + XSHG 旁证 + 行情实证 data_proven 三层，§三续期机制）
    S2 读 regime 昨收 PIT（regime_snapshot_history，六段映射=v0 草案查表可调）
    S3 读五层门快照（daily_gate_snapshot，缺席语义按蓝图 §四.2）
    S4 策略包选择（state_matrix TDM-E-L1 格查表∩已毕业包集；v1 包集=空→安全态）
    S5 定总仓位上限+no_trade 三源合成（预算带插值×过渡带折减 vs 60% 硬顶；三源=预算带 0%
       ∨ kill_switch ∨ regime 缺席，另有预算 run 缺席/日历歧义）
    S6 落 decision_daily（date-marker 先拍板先占，重拍=新 run_id 追加）
    S7 分发（v1=播报前缀+仪表盘留痕，不产执行单）

事件触发（宪法 §9.3，蓝图 §三）：daily_kline SUCCESS 唤醒链**末棒**（regime 刷新→判定台账
结算/验证→pf_alloc 分配→模拟盘日件→drain 落地之后——编排器 S2 消费 regime 快照、S3/L4 消费
当日 alloc run，排末使正常路径零降级；结算/验证钩子之后=钩子序契约）。不建新事件 kind、
不开闹钟（非交易日无 daily_kline SUCCESS=自然休眠）。

参数草案声明（裁定#305 第 1/3 点，标注可调，Owner 终裁后改常量+跑测试）：
    六段预算带=TDM-F-C1 注释值（全 proposed）；过渡带=最大隶属度<60% 折减×0.5（0.5-0.7
    带内取保守下缘）；硬顶=60%（RLM-CONCENTRATION-002）；regime→六段映射=v0 查表。
"""

from __future__ import annotations

import json
import logging
import math
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.pf_alloc.allocation_inputs import resolve_reader, validate_date_literal
from zephyr.strategy_pipeline.daily_gate_snapshot import (
    collect_gate_snapshot,
    read_latest_regime_snapshot,
    resolve_table_name,
)

log = logging.getLogger(__name__)

__all__: Final = [
    "ORCHESTRATOR_KIND",
    "ORCHESTRATOR_PREFIX",
    "BUDGET_BANDS",
    "GRADUATED_PACKAGES",
    "run_daily_decision",
    "maybe_run_daily_decision",
    "select_packages",
    "intraday_revoke",
    "postmarket_reconcile",
]

# ── 口径常量（草案值 v0，裁定#305 标可调）─────────────────────────────────
ORCHESTRATOR_KIND: Final = "daily_decision"          # marker 幂等键前缀（不建事件 kind，蓝图 §三.3）
ORCHESTRATOR_PREFIX: Final = "[DAILY-DECISION]"      # 播报稳定前缀（对齐 REGIME_SNAPSHOT_PREFIX 先例）
SCHEMA_VERSION: Final = "v1"
HARD_CAP: Final = 0.60                # 总仓位硬顶（RLM-CONCENTRATION-002；裁定#305 第 3 点草案）
TRANSITION_THRESHOLD: Final = 0.60    # 过渡带阈值：最大隶属度 <60%（TDM-F-C1 注记；裁定#305 第 1 点草案）
TRANSITION_FACTOR: Final = 0.5        # 过渡带折减（0.5-0.7 带内取保守下缘；裁定#305 第 3 点草案）
# 六段预算带（TDM-F-C1 节点注释值，全 proposed；capitulation 0-10%/accumulation 20-30%/
# ignition 30-50%/expansion 50-70%/euphoria ≤30% 只卖不买/distribution 0% 空仓）
BUDGET_BANDS: Final[dict[str, tuple[float, float]]] = {
    "capitulation": (0.00, 0.10),
    "accumulation": (0.20, 0.30),
    "ignition": (0.30, 0.50),
    "expansion": (0.50, 0.70),
    "euphoria": (0.00, 0.30),
    "distribution": (0.00, 0.00),
}
# regime dominant（7 维 HMM+overlay）→ 六段 v0 映射查表（草案值，裁定#305 第 1 点标注可调；
# 语义锚：r10 CRISIS→冰点投降 / r4 熊市阴跌→退潮派发 / r1 低波震荡+RECOVERY→修复吸筹 /
# r2 中波震荡+BREAKOUT→点火 / r3 牛市趋势→发酵扩张；情绪六段判定器接电后切换真源）
REGIME_TO_SEGMENT: Final[dict[str, str]] = {
    "r10": "capitulation",
    "r4": "distribution",
    "r1": "accumulation",
    "r11": "accumulation",
    "r2": "ignition",
    "r12": "ignition",
    "r3": "expansion",
}
# 已毕业策略包集（v1=空，裁定#305 第 2 点：S-OWNER-001 考试 FAIL、S-OWNER-002 机制
# 验证 FAIL——判定台账在案，裁定登记见各自交付分支待合并；当前无已毕业包，
# "无已毕业包，今日不出手"安全态；毕业通道接电后由工厂考试台账喂入，禁手填）
GRADUATED_PACKAGES: Final[frozenset[str]] = frozenset()
# 日历哨兵（蓝图 §三续期机制三层；裁定#305 第 4 点：N=3）
CALENDAR_LEAD_TRADING_DAYS: Final = 10   # 表尾距 target 提前量 <10 交易日 → calendar_stale 哨兵
DATA_PROVEN_ESCALATE_N: Final = 3        # 连续 data_proven 运行 N 日 → 升级告警
_TDM_CONFIG: Final = "config/trading_decision_map.yaml"
_STATE_NODE: Final = "TDM-E-L1"          # state_matrix 溯源节点（L1 总闸）
_PENDING_ADOPTION: Final = "pending-owner-adoption"

Reader = Callable[[str], Any]
Sink = Callable[[str, str, bytes], str]
AlertFn = Callable[..., None]


@dataclass(frozen=True)
class DecisionDeps:
    """拍板注入位（参数对象，§5.150 合规）：reader/sink/旁证/配置/marker/告警/force。"""

    reader: Reader | None = None
    sink: Sink | None = None
    xshg_fn: Callable[[str], bool] | None = None
    decision_map: dict[str, Any] | None = None
    marker_dir: Path | str | None = None
    alert_fn: AlertFn | None = None
    force: bool = False


@dataclass
class LegCtx:
    """降级账本（S2/S3/S5 各腿共享的可变三清单）。"""

    reasons: list[str]
    degrade: list[str]
    notes: list[str]

# SQL 模板（NO-BARE-SQL：_SQL_ 前缀常量；{date} 由 validate_date_literal 校验后方可入 SQL；
# 表名经 TableRegistry 真源解析（#ARCH-CH-024 禁硬编码字面量），解析失败=日历通道故障走
# data_proven/休眠分叉，不携带 fallback 字面量绕真源）
_CAL_CATEGORY: Final = "market_trade_calendar"
_SQL_CAL_DAY: Final = ("SELECT cal_date FROM {cal_table} "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
                       "WHERE is_open = 1 AND cal_date = '{date}' LIMIT 1")
_SQL_CAL_NEXT: Final = ("SELECT min(cal_date) FROM {cal_table} "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
                        "WHERE is_open = 1 AND cal_date > '{date}'")
_SQL_CAL_PREV: Final = ("SELECT max(cal_date) FROM {cal_table} "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
                        "WHERE is_open = 1 AND cal_date < '{date}'")
_SQL_CAL_LEAD: Final = ("SELECT count() FROM {cal_table} "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
                        "WHERE is_open = 1 AND cal_date > '{date}'")
# P2b 场景引擎联测读口（判定台账标准 §三表 3：预案+盘中/EOD 验证事实，只读）
_SQL_SCENARIO_PLAN: Final = (
    "SELECT plan_date, payload FROM c1_market.judgment_daily_plan "  # noqa: bare-sql  模块级 _SQL_ 前缀常量真源(P2b 台账只读模板)
    "WHERE plan_date = '{date}' ORDER BY asof_ts DESC LIMIT 1")
_SQL_SCENARIO_VERIFY: Final = ("SELECT data_date, actual_scenario_id, scenario_hits, verified_by "  # noqa: bare-sql  模块级 _SQL_ 前缀 SQL 模板常量唯一真源(禁散落重拼)
                               "FROM c1_market.judgment_plan_verification "
                               "WHERE data_date = '{date}' ORDER BY ingest_ts DESC LIMIT 1")


# ── 记号（业务日级先拍板先占，蓝图 S6；与 pipeline_events AUDIT_MARKER 分文件防互踩）──
def _marker_path(marker_dir: Path | str | None) -> Path:
    if marker_dir is not None:
        return Path(marker_dir) / "daily_decision_marker.json"
    from zephyr.strategy_pipeline.pipeline_events import STATE_DIR

    return STATE_DIR / "daily_decision_marker.json"


def _marker_seen(day: str, marker_dir: Path | str | None = None) -> bool:
    try:
        data = json.loads(_marker_path(marker_dir).read_text(encoding="utf-8"))
        return bool(data.get(f"{ORCHESTRATOR_KIND}:{day}"))
    except Exception:  # noqa: BLE001 — 标记损坏/缺失按未拍板处理（force/CLI 自有逃生口）
        return False


def _touch_marker(day: str, run_id: str, marker_dir: Path | str | None = None) -> None:
    """先拍板先占（蓝图 S6）：记号落盘才动手；失败不回滚=防唤醒点重拍风暴（regime 先例裁定）。"""
    from zephyr.shared.io.file_utils import safe_write_text

    path = _marker_path(marker_dir)
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:  # noqa: BLE001
        data = {}
    data[f"{ORCHESTRATOR_KIND}:{day}"] = run_id
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_write_text(str(path), json.dumps(data, ensure_ascii=False, indent=1) + "\n")


# ── S1 日历（三层：trade_calendar 真源 / XSHG 旁证 / 行情实证，蓝图 §三续期机制）──
def _scalar1(sql: str, reader: Reader) -> Any:
    rows = list(resolve_reader(reader)(sql))
    return rows[0][0] if rows and rows[0] else None





def _xshg_probe(xshg_fn: Callable[[str], bool] | None, day: str) -> tuple[bool, str]:
    """XSHG 旁证探测：返回（是否开市, 错误留痕）。旁证不可用=如实留痕不猜。"""
    if xshg_fn is None:
        def xshg_fn(d: str) -> bool:
            from zephyr.data.trading_calendar import is_trading_day

            return is_trading_day(__import__("datetime").date.fromisoformat(d))
    try:
        return bool(xshg_fn(day)), ""
    except Exception as exc:  # noqa: BLE001 — 旁证不可用如实留痕
        return False, type(exc).__name__


def _cal_state_base(day: str, cal_table: str | None, rd: Reader, xshg_open: bool,
                    xshg_err: str, data_proven: bool) -> dict[str, Any]:
    """S1 基态：真源行 × 旁证 × 行情实证 → 正常/data_proven 降级/休眠三态。"""
    out: dict[str, Any] = {"source": "trade_calendar", "target_date": None, "prev_day": None,
                           "degraded": 0, "ambiguous": 0, "stale": 0, "lead_days": None,
                           "sleep": 0, "xshg_open": xshg_open, "xshg_error": xshg_err}
    cal_row = None
    if cal_table:
        try:
            cal_row = _scalar1(_SQL_CAL_DAY.format(cal_table=cal_table, date=day), rd)
        except Exception as exc:  # noqa: BLE001 — 日历通道故障≠休市（走 data_proven 分叉）
            log.warning("[DAILY-DECISION] trade_calendar 查询失败: %s", type(exc).__name__)
    if cal_row is None and not data_proven and not xshg_open:
        out["sleep"] = 1
        return out
    if cal_row is None:
        # D4：行情实证开市（data_proven 模式降级续命，误休眠=最大静默风险，蓝图自裁 5）
        out["source"] = "data_proven"
        out["degraded"] = 1
    elif not xshg_open and not xshg_err:
        # 真源说开市、XSHG 旁证反对 → 以降级态继续（data_proven 口径）
        out["source"] = "data_proven"
        out["degraded"] = 1
    return out


def _cal_target(day: str, cal_table: str | None, rd: Reader, xshg_open: bool,
                out: dict[str, Any]) -> None:
    """次交易日解析（warroom 同款口径 is_open=1 且 >数据日 LIMIT 1）；缺→XSHG 旁证找次会话。"""
    if not cal_table:
        out["ambiguous"] = 1
        out["degraded"] = 1
        return
    try:
        nxt = _scalar1(_SQL_CAL_NEXT.format(cal_table=cal_table, date=day), rd)
    except Exception:  # noqa: BLE001
        nxt = None
    if nxt:
        out["target_date"] = str(nxt)
        return
    try:
        lead = list(resolve_reader(rd)(_SQL_CAL_LEAD.format(cal_table=cal_table, date=day)))[0][0]
        if not lead and xshg_open:
            from zephyr.data.trading_calendar import trading_days_in_range
            import datetime as _dt

            sessions = trading_days_in_range(
                _dt.date.fromisoformat(day) + _dt.timedelta(days=1),
                _dt.date.fromisoformat(day) + _dt.timedelta(days=30))
            if sessions:
                out["target_date"] = sessions[0].isoformat()
                out["degraded"] = 1
    except Exception:  # noqa: BLE001
        pass
    if not out["target_date"]:
        out["ambiguous"] = 1
        out["degraded"] = 1


def _cal_sentinel(day: str, cal_table: str | None, rd: Reader, out: dict[str, Any]) -> None:
    """D5 哨兵：表尾提前量 <10 交易日（出声不续，续期归属数据域任务链）。"""
    if not cal_table:
        out["stale"] = 1
        return
    try:
        prev = _scalar1(_SQL_CAL_PREV.format(cal_table=cal_table, date=day), rd)
        out["prev_day"] = str(prev) if prev else None
    except Exception:  # noqa: BLE001
        pass
    try:
        lead = int(_scalar1(_SQL_CAL_LEAD.format(
            cal_table=cal_table, date=out["target_date"] or day), rd) or 0)
        out["lead_days"] = lead
        if lead < CALENDAR_LEAD_TRADING_DAYS:
            out["stale"] = 1
    except Exception:  # noqa: BLE001
        out["stale"] = 1


def resolve_calendar(
    data_date: str,
    *,
    reader: Reader | None = None,
    xshg_fn: Callable[[str], bool] | None = None,
    data_proven: bool = True,
) -> dict[str, Any]:
    """S1 日历解析：{source, target_date, prev_day, degraded, ambiguous, stale, lead_days, sleep}。

    - trade_calendar 有 D 行 ∧ XSHG 一致 → 正常态 source=trade_calendar；
    - D 行缺 ∧ 行情实证（data_proven）→ data_proven 降级开市（D4，误休眠=最大静默风险）；
    - D 行缺 ∧ 无行情实证 ∧ XSHG 非会话 → sleep=休眠（无行写入）；
    - 表尾提前量 <10 交易日 → stale=哨兵告警不阻断（D5）；
    - target 解析失败（无次日行 ∧ XSHG 不可用）→ ambiguous（安全侧不出行）。
    """
    day = validate_date_literal(data_date)
    rd = resolve_reader(reader)
    try:
        cal_table: str | None = resolve_table_name(_CAL_CATEGORY)
    except Exception as exc:  # noqa: BLE001 — 注册表不可用=日历通道故障
        cal_table = None
        log.warning("[DAILY-DECISION] TableRegistry 解析失败: %s", type(exc).__name__)
    xshg_open, xshg_err = _xshg_probe(xshg_fn, day)
    out = _cal_state_base(day, cal_table, rd, xshg_open, xshg_err, data_proven)
    if not out.get("sleep"):
        _cal_target(day, cal_table, rd, xshg_open, out)
        _cal_sentinel(day, cal_table, rd, out)
    return out


# ── S4 策略包选择（S-OWNER-002 切换器查表骨架，蓝图 §五.2 PackageDecision 契约）──
def _load_decision_map() -> dict[str, Any] | None:
    """TDM 配置只读加载（失败=残缺态 fail-open，包集空=安全侧）。"""
    try:
        import yaml

        from zephyr.shared.io.paths import REPO_ROOT

        return yaml.safe_load((REPO_ROOT / _TDM_CONFIG).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        log.warning("[DAILY-DECISION] state_matrix 不可读: %s", type(exc).__name__)
        return None


def _lookup_state_cell(dm: dict[str, Any] | None, state: str) -> dict[str, Any] | None:
    """state_matrix 内 TDM-E-L1×state 格查找（无格=None）。"""
    for c in ((dm or {}).get("state_matrix") or {}).get("cells") or []:
        if isinstance(c, dict) and c.get("node_id") == _STATE_NODE and c.get("state") == state:
            return c
    return None


def _package_verdict(mounted: list[str], enabled: list[str], reason: str) -> tuple[bool, str]:
    """（incomplete, note）判定：空格残缺催 Owner 采纳/无毕业包安全态/全量启用。"""
    if not mounted:
        prefix = reason.split(" ", 1)[0] if reason else ""
        if reason.startswith(_PENDING_ADOPTION):
            return True, f"格空（{prefix}）：该段无包可启=安全侧（蓝图 §一.4，AI 禁自填 Owner 格）"
        return True, f"格空：该段无挂载（{reason[:80] or '无注记'}）"
    if len(enabled) < len(mounted):
        return True, "无已毕业包可启（挂载∩已毕业∅；v1 安全态，裁定#305 第 2 点）"
    return False, ""


def select_packages(
    market_state: str | None,
    *,
    decision_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """state_matrix TDM-E-L1 格查表 → PackageDecision（蓝图 §五.2 契约逐字段）。

    v1 包集=GRADUATED_PACKAGES（空，裁定#305 第 2 点）→ enabled_packages 恒 []，
    incomplete=格缺/pending-owner-adoption/毕业∩挂载<挂载数 任一为真；空格残缺在 note 催 Owner 采纳。
    """
    out: dict[str, Any] = {"enabled_packages": [], "per_package_cap": {},
                           "source_cell": f"{_STATE_NODE}|{market_state or 'unknown'}",
                           "source_confidence": "untested", "incomplete": True}
    if not market_state:
        return out
    dm = decision_map if decision_map is not None else _load_decision_map()
    cell = _lookup_state_cell(dm, market_state)
    if cell is None:
        out["note"] = f"state_matrix 无 {_STATE_NODE}|{market_state} 格（包选择残缺，催 Owner 采纳）"
        return out
    out["source_confidence"] = str(cell.get("confidence") or "untested")
    mounted = [str(s) for s in (cell.get("mounted") or [])]
    enabled = sorted(set(mounted) & set(GRADUATED_PACKAGES))
    out["mounted"] = mounted
    out["enabled_packages"] = enabled
    out["incomplete"], out["note"] = _package_verdict(
        mounted, enabled, str(cell.get("mounted_reason") or ""))
    # per_package_cap：启用包受 position_cap 约束等分（v1 包集空→恒 {}；接入时按 cap/Σcap 切分）
    return out


# ── S5 仓位上限合成（E-L1 总闸语义×TDM-F-C1 预算带，零新判断：全部查表+机械插值）──
def compute_position_cap(market_state: str, confidence: float) -> dict[str, Any]:
    """六段预算带带内插值 ×（过渡带折减）→ min(·, 60% 硬顶)。

    Returns:
        {"band_low","band_high","position_cap","transition":bool,"sell_only":bool}
        market_state 不在封闭集 → {"position_cap": 0.0, "invalid_state": True}（保守侧）。
    """
    band = BUDGET_BANDS.get(market_state)
    if band is None:
        return {"band_low": 0.0, "band_high": 0.0, "position_cap": 0.0,
                "transition": False, "sell_only": False, "invalid_state": True}
    conf = min(1.0, max(0.0, float(confidence)))
    cap = band[0] + (band[1] - band[0]) * conf
    transition = conf < TRANSITION_THRESHOLD
    if transition:
        cap *= TRANSITION_FACTOR
    return {"band_low": band[0], "band_high": band[1],
            "position_cap": round(min(cap, HARD_CAP), 6),
            "transition": transition, "sell_only": market_state == "euphoria"}


# ── S6 写侧（列清单唯一真源=schemas/categories/decision_daily.py；投递口径如实）──
def _cell(value: Any) -> str:
    from zephyr.data.ch_writer import tsv_escape

    if isinstance(value, bool):
        return "1" if value else "0"
    if value is None:
        return tsv_escape(None)
    if isinstance(value, float) and math.isnan(value):
        return tsv_escape(None)
    return tsv_escape(value)


def _default_sink(table: str, columns: str, payload: bytes) -> str:
    from zephyr.data.ch_writer import write_tsv_outcome

    return write_tsv_outcome(table, columns, payload).disposition.value


def write_decision_row(row: dict[str, Any], *, sink: Sink | None = None) -> tuple[int, str]:
    """按 INSERT_COLUMNS 声明列序落一行决策快照 → (行数, 投递事实)。

    Raises:
        RuntimeError: 缺声明列 / 未持久化（fail-closed——"算了但没落地"禁，同 allocation_persistence）。
    """
    from schemas.categories.decision_daily import INSERT_COLUMNS, TABLE_NAME

    body = INSERT_COLUMNS.strip().strip("()")
    declared = [c.strip() for c in body.split(",") if c.strip()]
    missing = [c for c in declared if c not in row]
    if missing:
        raise RuntimeError(f"decision_daily 行缺声明列 {missing}（禁静默补空）")
    line = "\t".join(_cell(row[c]) for c in declared)
    payload = (line + "\n").encode("utf-8")
    disposition = (sink or _default_sink)(TABLE_NAME, INSERT_COLUMNS, payload)
    if disposition not in ("ch_committed", "local_durable"):
        raise RuntimeError(f"decision_daily 落库未确认（disposition={disposition}）——fail-closed")
    return 1, disposition


def _alert(alert_fn: AlertFn | None, message: str, level: str = "INFO") -> None:
    """播报（S7 分发面 v1）：注入优先，默认 pipeline_events.alert（日志+Alerter 落盘）。"""
    try:
        if alert_fn is not None:
            alert_fn(message, level=level)
        else:
            from zephyr.strategy_pipeline.pipeline_events import alert

            alert(message, level=level)
    except Exception:  # noqa: BLE001 — 告警通道故障不反噬拍板主流程
        log.debug("[DAILY-DECISION] 告警通道不可达", exc_info=True)


def _resolve_kline_day(rd: Reader) -> str:
    """行情最新入库日（data_proven 判据；与 resolve_pf_alloc_trade_date 同源口径）。"""
    try:
        from zephyr.strategy_pipeline.pipeline_events import PF_ALLOC_BIZ_DATE_SQL

        raw = _scalar1(PF_ALLOC_BIZ_DATE_SQL, rd)
    except Exception:  # noqa: BLE001
        return ""
    return str(raw or "")[:10]


def _read_plan_context(day: str, rd: Reader) -> str:
    """P2b 场景引擎联测：昨日预案+盘中归类结果一行摘要（缺席=空串，不阻塞拍板）。"""
    parts: list[str] = []
    try:
        row = _scalar1_wrap(rd, _SQL_SCENARIO_PLAN.format(date=day))
        if row:
            parts.append(f"plan={str(row[0])}")
    except Exception:  # noqa: BLE001
        pass
    try:
        row = _scalar1_wrap(rd, _SQL_SCENARIO_VERIFY.format(date=day))
        if row:
            parts.append(f"scenario={str(row[1] or '') or 'pending'}({_hits_count(row[2])}hits)")
    except Exception:  # noqa: BLE001
        pass
    return ",".join(parts)


def _hits_count(raw: Any) -> int:
    try:
        return len(json.loads(str(raw) or "[]"))
    except ValueError:
        return 0


def _scalar1_wrap(rd: Reader, sql: str) -> tuple | None:
    rows = list(rd(sql))
    return tuple(rows[0]) if rows else None


# ── S2/S3 分腿判定（复杂度拆分：每腿只做一件事，D1/D3/D6 折进各自腿）─────────
def _s2_regime_leg(day: str, rd: Reader, cal: dict[str, Any],
                   ctx: "LegCtx") -> tuple[str | None, float, dict]:
    """S2 regime 腿：PIT 读+新鲜度（D1）+六段映射+预算带合成。缺席/陈旧→no_trade 原因落账。"""
    regime = read_latest_regime_snapshot(day, reader=rd)
    if regime.get("status") != "ok":
        ctx.reasons.append("regime_missing")
        ctx.degrade.append("D1_regime_missing")
        ctx.notes.append(f"regime 快照缺席（{regime.get('error')}）→ no_trade")
        return None, 0.0, compute_position_cap("", 0.0)
    source_date = str(regime.get("source_date") or "")
    prev_day = cal.get("prev_day")
    if (source_date < prev_day) if prev_day else (source_date < day):
        ctx.reasons.append("regime_missing")
        ctx.degrade.append("D1_regime_stale")
        ctx.notes.append(f"regime 快照陈旧（source={source_date} < 前交易日{prev_day or 'N/A'}）")
        return None, 0.0, compute_position_cap("", 0.0)
    state = REGIME_TO_SEGMENT.get(str(regime.get("dominant")))
    confidence = float(regime.get("confidence") or 0.0)
    if state is None:
        ctx.reasons.append("regime_missing")
        ctx.degrade.append("D1_regime_state_unmappable")
        ctx.notes.append(f"dominant={regime.get('dominant')} 不可映射六段（保守侧）")
        return None, 0.0, compute_position_cap("", 0.0)
    cap_calc = compute_position_cap(state, confidence)
    if cap_calc.get("transition"):
        ctx.degrade.append("transition_band")
        ctx.notes.append(f"过渡带（隶属度 {confidence:.2f}<{TRANSITION_THRESHOLD}）×{TRANSITION_FACTOR}")
    if cap_calc.get("sell_only"):
        ctx.notes.append("euphoria 段只卖不买（TDM-F-C1）")
    return state, confidence, cap_calc


def _s3_gate_leg(gate: dict[str, Any], ctx: "LegCtx") -> None:
    """S3 门腿评估（采集在 run 主链）：D2 缺席降级不阻断 / D6 kill_switch 保守侧 / D3 预算缺席。"""
    gate_absent = list(gate.get("absent_layers") or [])
    if gate_absent:
        ctx.degrade.append("D2_gate_absent:" + ",".join(gate_absent))
        ctx.notes.append(f"门缺席层按门关（依赖包今日禁用）：{gate_absent}")
    ks = (gate.get("l5") or {}).get("kill_switch") or {}
    if ks.get("status") != "ok":
        ctx.reasons.append("kill_switch")
        ctx.degrade.append("D6_kill_switch_conservative")
        ctx.notes.append("kill_switch 读态失败 → 按熔断保守侧（保命件方向不猜）")
    elif str(ks.get("state")) != "normal":
        ctx.reasons.append("kill_switch")
        ctx.degrade.append("D6_kill_switch_active")
        ctx.notes.append(f"kill_switch={ks.get('state')} 熔断生效 → 禁新开仓")
    if (gate.get("l4") or {}).get("status") != "ok":
        ctx.reasons.append("budget_run_missing")
        ctx.degrade.append("D3_budget_run_missing")
        ctx.notes.append("alloc_budget_daily 当日无 run（预算无来源=不出预算）")


def _no_trade_sources(state: str | None, ctx: "LegCtx") -> None:
    """三源合成第一源：distribution 预算带 0%（禁新开仓，存量由 X 流信号驱动离场，D98）。"""
    if state == "distribution":
        ctx.reasons.append("distribution_band")
        ctx.notes.append("distribution 预算带 0%（禁新开仓，存量由 X 流信号驱动离场，D98）")


# ── 编排主入口（S1-S7 串行；永不外抛，D7 fail-open）────────────────────────
def run_daily_decision(data_date: str | None = None, *,
                       deps: DecisionDeps | None = None,
                       **legacy: Any) -> dict[str, Any]:
    """拍板一个业务日：S1-S7 全链 → decision_daily 一行（或 sleep/error 无行）。

    Args:
        data_date: 数据日（None=行情最新入库日 resolve_pf_alloc_trade_date，禁墙钟猜日）。
        deps: 注入位参数对象（reader/sink/xshg_fn/decision_map/marker_dir/alert_fn/force）。
        legacy: 旧关键字注入兼容面（逐键转 DecisionDeps，未知键=TypeError fail-closed）；
            reader/sink/xshg_fn/decision_map/marker_dir/alert_fn/force。

    Returns:
        {"action": "adjudicated|sleep|skipped_marker|error|blocked_no_target", ...,
         "brief"}（action=error 时带 error 字段）。
    """
    d = deps if deps is not None else DecisionDeps(**legacy)
    try:
        return _run_inner(data_date, d)
    except Exception as exc:  # noqa: BLE001 — D7：编排器自身异常 fail-open（不留半行+告警出声）
        msg = (f"{ORCHESTRATOR_PREFIX} 拍板未完成（data_date={data_date or '未知'}）："
               f"{type(exc).__name__}: {exc}")
        log.error("%s 拍板异常 fail-open（下游无凭证=保守侧）", ORCHESTRATOR_PREFIX, exc_info=True)
        _alert(d.alert_fn, msg[:300], "ERROR")
        return {"action": "error", "error": f"{type(exc).__name__}: {exc}"[:200],
                "data_date": data_date}


def _resolve_data_date(data_date: str | None) -> str:
    """业务日真源：显式参数或行情最新入库日（禁墙钟猜日，蓝图 §三）。"""
    if data_date is not None:
        return validate_date_literal(data_date)
    from zephyr.strategy_pipeline.pipeline_events import resolve_pf_alloc_trade_date

    return resolve_pf_alloc_trade_date()


def _s1_precheck(day: str, rd: Reader, deps: DecisionDeps) -> tuple[dict[str, Any], str] | dict[str, Any]:
    """S1 前置：行情实证+日历三态。休眠/歧义=终止分支（返回终态 dict），否则返回 (cal, kline_day)。"""
    kline_day = _resolve_kline_day(rd)
    proven = bool(kline_day) and kline_day >= day  # 行情实证：请求日已有入库数据
    cal = resolve_calendar(day, reader=rd, xshg_fn=deps.xshg_fn, data_proven=proven)
    if cal.get("sleep"):
        _alert(deps.alert_fn, f"{ORCHESTRATOR_PREFIX} {day} 非交易日且无行情实证 → 休眠（不开闹钟）")
        return {"action": "sleep", "data_date": day}
    if cal.get("ambiguous"):
        # 日历歧义且次交易日不可解析：无生效日=不出快照行（无行=无新开仓令，安全侧）
        _alert(deps.alert_fn,
               f"{ORCHESTRATOR_PREFIX} {day} 次交易日不可解析（日历/XSHG 均无）→ 不出决策快照",
               "ERROR")
        return {"action": "blocked_no_target", "data_date": day}
    return cal, kline_day


def _s5_no_trade(day: str, rd: Reader, state: str | None, cap_calc: dict,
                 decision_map: dict[str, Any] | None, ctx: "LegCtx") -> tuple[float, dict, dict]:
    """S3/S4/S5 合成：门快照+包选择+仓位上限+no_trade 三源 → (position_cap, packages, gate)。"""
    gate = collect_gate_snapshot(day, market_state=state, reader=rd)
    _s3_gate_leg(gate, ctx)
    _no_trade_sources(state, ctx)
    plan_ctx = _read_plan_context(day, rd)
    if plan_ctx:
        ctx.notes.append("plan_context=" + plan_ctx)
    packages = select_packages(state, decision_map=decision_map)
    pkg_note = packages.pop("note", None)
    if pkg_note:
        ctx.notes.append(pkg_note)
    if not packages["enabled_packages"]:
        ctx.notes.append("无已毕业包，今日不出手（v1 安全态，裁定#305 第 2 点）")
    position_cap = 0.0 if ctx.reasons else float(cap_calc["position_cap"])
    return position_cap, packages, gate


def _run_inner(data_date: str | None, deps: DecisionDeps) -> dict[str, Any]:
    rd = resolve_reader(deps.reader)
    day = _resolve_data_date(data_date)
    # 幂等闸：业务日级 marker 先拍板先占（同日重唤醒直接跳过；force=人工重跑逃生口）
    if not deps.force and _marker_seen(day, deps.marker_dir):
        return {"action": "skipped_marker", "data_date": day,
                "why": "already_adjudicated（重拍走 run_daily_decision(force=True)=新 run_id 追加）"}
    # S1 日历（休眠/歧义分支返回终态）
    pre = _s1_precheck(day, rd, deps)
    if not isinstance(pre, tuple):
        return pre
    cal, _kline_day = pre
    ctx = LegCtx(reasons=[], degrade=[], notes=[])
    if cal.get("degraded"):
        ctx.degrade.append(f"calendar:{cal['source']}")
    if cal.get("stale"):
        ctx.degrade.append("calendar_stale")
        _alert(deps.alert_fn,
               f"{ORCHESTRATOR_PREFIX} 日历续期哨兵：表尾提前量 "
               f"{cal.get('lead_days')} 交易日 <{CALENDAR_LEAD_TRADING_DAYS}（data_proven 续命中，"
               f"连续 {DATA_PROVEN_ESCALATE_N} 日升级告警催人工续期）", "WARN")
    # S2 regime 腿（D1 三分支折进）+ S3/S4/S5 合成腿（D2/D6/D3+包选择+仓位）
    state, confidence, cap_calc = _s2_regime_leg(day, rd, cal, ctx)
    position_cap, packages, gate = _s5_no_trade(day, rd, state, cap_calc,
                                                deps.decision_map, ctx)
    # S6 落快照（marker 先拍板先占在写之前占位=蓝图 S6 口径；失败不回滚防风暴）
    run_id = f"decision-{day}-{uuid.uuid4().hex[:6]}"
    _touch_marker(day, run_id, deps.marker_dir)
    no_trade = int(bool(ctx.reasons))
    row = {
        "run_id": run_id,
        "trade_date": cal.get("target_date") or day,
        "asof_data_date": day,
        "market_state": state or "unknown",
        "state_confidence": confidence,
        "budget_band_low": float(cap_calc["band_low"]),
        "budget_band_high": float(cap_calc["band_high"]),
        "position_cap": 0.0 if no_trade else position_cap,
        "package_set_json": json.dumps(packages, ensure_ascii=False),
        "gate_snapshot_json": json.dumps(gate, ensure_ascii=False),
        "no_trade": no_trade,
        "no_trade_reason": ";".join(dict.fromkeys(ctx.reasons)),
        "sit_out_list_json": json.dumps({"entries": [], "source": "sit_out_list:v1_feeds_unwired"},
                                        ensure_ascii=False),
        "calendar_source": str(cal.get("source")),
        "degraded": 1 if (ctx.degrade or cal.get("degraded")) else 0,
        "degrade_reasons": ";".join(dict.fromkeys(ctx.degrade)),
        "note": " | ".join(ctx.notes),
        "schema_version": SCHEMA_VERSION,
    }
    n, disposition = write_decision_row(row, sink=deps.sink)
    # S7 分发（v1=播报前缀+仪表盘留痕，不产执行单，裁定#305 第 6 点）
    brief = (f"target={row['trade_date']} state={row['market_state']}"
             f"@{confidence:.2f} cap={row['position_cap']:.2%} no_trade={no_trade}"
             f"({row['no_trade_reason'] or '-'}) packages={packages['enabled_packages'] or '∅'}"
             f" degraded={row['degraded']}({row['degrade_reasons'] or '-'})"
             f" rows={n} 投递={disposition}")
    _alert(deps.alert_fn, f"{ORCHESTRATOR_PREFIX} 拍板完成 {brief}", "INFO")
    return {"action": "adjudicated", "run_id": run_id, "data_date": day,
            "trade_date": row["trade_date"], "no_trade": no_trade,
            "no_trade_reason": row["no_trade_reason"],
            "position_cap": row["position_cap"],
            "market_state": row["market_state"], "degraded": row["degraded"],
            "degrade_reasons": row["degrade_reasons"], "rows": n, "disposition": disposition,
            "brief": brief}


# ── 事件挂点（pipeline_events wire 末棒；永不反噬唤醒链）────────────────────
def maybe_run_daily_decision(task_id: Any = None, success: bool = True,
                             **kwargs: Any) -> dict[str, Any]:
    """daily_kline SUCCESS 唤醒链末棒的编排器产出者（蓝图 §三；不建 cron/Timer/sleep-loop）。

    唤醒任务子串匹配与 regime/pf_alloc 同源（SIM_DAILY_WAKE_TASKS）；幂等闸在
    run_daily_decision 内（业务日级 marker 先拍板先占）。永不抛：拍板失败已告警，
    绝不反噬调度器唤醒钩子链。
    """
    tid = str(task_id or "")
    try:
        from zephyr.strategy_pipeline.pipeline_events import SIM_DAILY_WAKE_TASKS

        wake = success and any(k in tid for k in SIM_DAILY_WAKE_TASKS)
    except Exception:  # noqa: BLE001
        wake = success
    if not wake:
        return {"action": "skipped_wake_point"}
    kwargs.pop("task_id", None)
    kwargs.pop("success", None)
    out = run_daily_decision(None, **kwargs)
    log.info("%s 唤醒拍板: %s", ORCHESTRATOR_PREFIX, out.get("action"))
    return out


# ── T3/T4 接口签名（蓝图 §九.7：首版只留签名不施工）────────────────────────
def intraday_revoke(reason: str, *, trade_date: str | None = None) -> dict[str, Any]:
    """盘中修订接口（预留，不施工）：熔断触发时对当日决策追加修订行（新 run_id，no_trade=1）。

    v1 裁定#305 第 7 点：无自动实盘干预，盘中修订权 Owner 人工保留——本签名仅契约占位。
    """
    return {"action": "reserved_v1", "reason": reason, "trade_date": trade_date,
            "note": "盘中修订权 Owner 人工保留（裁定#305 第 7 点）；执行面接入后另裁触发白名单"}


def postmarket_reconcile(data_date: str) -> dict[str, Any]:
    """盘后核对接口（预留，不施工）：当日决策 vs 实际核对留痕（对接 plan_deviation_monitor 口径）。"""
    return {"action": "reserved_v1", "data_date": data_date,
            "note": "T4 盘后核对首版仅签名占位（蓝图 §九.7）"}


# ── 手工补跑逃生口（P2b 同款：非自动链路；自动触发=pipeline_events wire 末棒事件订阅）──
# force 重拍/指定日期逃生口（编程式，不设 argparse——MANUAL-ONLY-PERMANENT 门禁合规）：
#   python -c "from zephyr.strategy_pipeline.daily_decision_orchestrator import run_daily_decision as r; r('YYYY-MM-DD', force=True)"
if __name__ == "__main__":  # pragma: no cover — 手工补跑逃生口（非自动链路）
    print(json.dumps(run_daily_decision(None), ensure_ascii=False, indent=1, default=str))
