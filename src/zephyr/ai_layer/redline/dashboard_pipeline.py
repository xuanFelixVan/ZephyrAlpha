# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §obj_s_dual_metric_dashboard
# [MODULE] zephyr.ai_layer.redline.dashboard_pipeline
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.shared.utils.time_utils (now_utc)（阈值真源=config/obj_s_degradation.yaml，
#                mtime 热加载照抄 resource_optimization 先例；DDL 落点=schemas/categories/ai_cost_daily.py）
# [CONSUMERS] OBJ_S 双指标看板（日刷新双列：日运行成本×模拟盘组合回撤）;
#             OBJ_M 路由表（degrade_model_tier 事件消费方）; L6 排产挂起（heavy_pause 动作消费方）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] "不亏钱"代理量尺（DESIGN §4）：看板=日刷新双列，任一越限→自动降档（不问 AI 意见）；
#   阈值真源=config/obj_s_degradation.yaml（初值追认：Owner 夜批授权原值生效；OBJ_M 首月数据后
#   OBJ_R 定标），热加载=mtime 变化下一监控周期生效；降档动作按序生效（重活停→便宜模型顶上→
#   挖矿暂停），本模块只产动作指令与事件载荷，不直接执行（L6 挂起/OBJ_M 路由/配额冻结各有
#   原生消费方，OBJ_S 不绕过直改状态——接线图双向只走事件与路由表）；组合回撤=Σ各钱包 equity
#   对组合高水位的回撤（c1_backtest.sim_pocket_daily 行形状，行数据经注入供给，模块自身零连库）；
#   hysteresis 三件套照抄 resource_optimization 先例原值（confirmation_count=2/cooldown 60s/
#   振荡每小时≤3），恢复=N 日回线+滞回，防振荡
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_S_perimeter/DESIGN.md §4；
#                阈值数值变更=config/obj_s_degradation.yaml（OBJ_R 定标流程）
# [STABILITY] new
# [SAFETY] M（降档联动触发面——只产指令不执行；数值=预注册初值）
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 阈值文件缺/形状非法 → DegradationConfigError（fail-closed 首载）；
#                  热加载失败（重载解析错）→ 保留上一份好配置+warning（fail-open 连续性优先，
#                  不炸监控周期）；回撤行畸形（日期不可解析/equity 非数）→ 跳过行计数留痕；
#                  空数据 → 回撤 0.0+skipped 口径诚实返回（不虚构）
# [TESTS] tests/ai_layer/redline/test_dashboard_pipeline.py（阈值解析/缺键抛错/热加载 mtime/
#         坏重载保旧/组合高水位回撤已知值/畸形行跳过/软硬线三档判定/恢复滞回三件套/
#         degrade 事件载荷形状/成本兜底估算）
"""dashboard_pipeline — "不亏钱"双指标看板数据链（OBJ_S 施工项 S5）。

DESIGN §4：看板=日刷新双列（日运行成本 × 模拟盘组合回撤），任一越限→自动降档。

- 指标 1 日运行成本：数据源分级①渠道账单 API（首选）→②LLM 网关遥测 token×单价兜底估算
  （estimate_daily_cost）；日账落 c1_backtest.ai_cost_daily（DDL 真源正门）。
- 指标 2 模拟盘组合回撤：数据源 c1_backtest.sim_pocket_daily（策略钱包日账），组合日回撤=
  Σ各钱包 equity 对组合高水位的回撤；事件流 sim_trade_log 兼作对账真源（rebuild 可重建）。
- 越限降档联动：阈值=config/obj_s_degradation.yaml（mtime 热加载）；动作指令只产不执行，
  原生消费方=L6（重活停）/OBJ_M 路由表（便宜模型顶上）/配额池（挖矿暂停）。

连库读取经注入的行供给（行形状=sim_pocket_daily 的 trade_date/strategy_id/equity），
模块自身零 DB 依赖——生产接线批用 ClickHouse reader 供给行，测试用合成行。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

import yaml

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH: Final = REPO_ROOT / "config" / "obj_s_degradation.yaml"

TIER_NORMAL: Final = "normal"
TIER_ATTENTION: Final = "attention"
TIER_DEGRADE: Final = "degrade"

ACTION_ALERT_YELLOW: Final = "alert_yellow"
ACTION_HEAVY_PAUSE: Final = "heavy_pause"
ACTION_CHEAP_MODEL: Final = "cheap_model_fallback"
ACTION_MINING_PAUSE: Final = "mining_pause"

DEGRADE_ACTIONS: Final[tuple[str, ...]] = (ACTION_HEAVY_PAUSE, ACTION_CHEAP_MODEL, ACTION_MINING_PAUSE)
ATTENTION_ACTIONS: Final[tuple[str, ...]] = (ACTION_ALERT_YELLOW,)

REQUIRED_THRESHOLD_KEYS: Final[tuple[str, ...]] = (
    "soft_yuan",
    "hard_yuan",
    "attention_pct",
    "degrade_pct",
)


class DegradationConfigError(RuntimeError):
    """阈值真源缺文件/形状非法（fail-closed 首载）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


@dataclass(frozen=True)
class Thresholds:
    """双指标降档阈值（obj_s_degradation.yaml 解析产物）。"""

    cost_soft_yuan: float
    cost_hard_yuan: float
    drawdown_attention_pct: float
    drawdown_degrade_pct: float
    recovery_consecutive_days: int = 3
    confirmation_count: int = 2
    cooldown_seconds: float = 60.0
    oscillation_threshold_per_hour: int = 3


def parse_thresholds(data: Mapping[str, Any]) -> Thresholds:
    """YAML dict → Thresholds（缺必填键抛 DegradationConfigError，fail-closed）。"""
    cost = data.get("cost_daily") if isinstance(data.get("cost_daily"), dict) else {}
    drawdown = data.get("drawdown_pct") if isinstance(data.get("drawdown_pct"), dict) else {}
    merged: dict[str, Any] = {
        "soft_yuan": cost.get("soft_yuan"),
        "hard_yuan": cost.get("hard_yuan"),
        "attention_pct": drawdown.get("attention_pct"),
        "degrade_pct": drawdown.get("degrade_pct"),
    }
    missing = [key for key in REQUIRED_THRESHOLD_KEYS if not isinstance(merged.get(key), (int, float))]
    if missing:
        raise DegradationConfigError(f"阈值真源缺必填数值键（fail-closed）: {missing}")
    recovery = data.get("recovery") if isinstance(data.get("recovery"), dict) else {}
    hysteresis = data.get("hysteresis") if isinstance(data.get("hysteresis"), dict) else {}
    return Thresholds(
        cost_soft_yuan=float(merged["soft_yuan"]),
        cost_hard_yuan=float(merged["hard_yuan"]),
        drawdown_attention_pct=float(merged["attention_pct"]),
        drawdown_degrade_pct=float(merged["degrade_pct"]),
        recovery_consecutive_days=int(recovery.get("consecutive_days", 3)),
        confirmation_count=int(hysteresis.get("confirmation_count", 2)),
        cooldown_seconds=float(hysteresis.get("cooldown_seconds", 60.0)),
        oscillation_threshold_per_hour=int(hysteresis.get("oscillation_threshold_per_hour", 3)),
    )


class DegradationConfig:
    """阈值真源载入器（mtime 热加载：文件变化下一监控周期生效，resource_optimization 先例）。"""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path) if path else DEFAULT_CONFIG_PATH
        self._mtime: float | None = None
        self._thresholds: Thresholds | None = None

    @property
    def thresholds(self) -> Thresholds:
        if self._thresholds is None:
            self._load()
        assert self._thresholds is not None
        return self._thresholds

    def _read_mtime(self) -> float | None:
        try:
            return self._path.stat().st_mtime
        except OSError:
            return None

    def _load(self) -> None:
        try:
            data = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise DegradationConfigError("阈值真源读取/解析失败（fail-closed）", details={"path": str(self._path)}) from exc
        if not isinstance(data, dict):
            raise DegradationConfigError("阈值真源形状非法（fail-closed）", details={"path": str(self._path)})
        self._thresholds = parse_thresholds(data)
        self._mtime = self._read_mtime()

    def reload_if_changed(self) -> bool:
        """mtime 变化则重载；重载失败保留上一份好配置+warning（连续性优先）。返回是否重载。"""
        if self._thresholds is None:
            self._load()
            return True
        mtime = self._read_mtime()
        if mtime is None or mtime == self._mtime:
            return False
        try:
            self._load()
        except DegradationConfigError:
            logger.warning("obj_s_degradation 热加载失败，保留上一份好配置: %s", self._path, exc_info=True)
            return False
        return True


# ────────────────── 指标 2：模拟盘组合回撤（行供给注入）──────────────────


@dataclass(frozen=True)
class DrawdownReport:
    """组合回撤报告（对组合高水位；空数据诚实返回 0.0+skipped 计数）。"""

    current_drawdown_pct: float
    max_drawdown_pct: float
    high_water_mark: float
    portfolio_equity_latest: float
    days_evaluated: int
    skipped_rows: int


def _row_date(raw: object) -> date | None:
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return None


def portfolio_drawdown(rows: Sequence[Mapping[str, Any]]) -> DrawdownReport:
    """纯函数核：sim_pocket_daily 行形状 → 组合高水位回撤报告。

    组合日权益=按日 Σ各钱包 equity；高水位=截至当日的组合权益最大值；
    日回撤%=(高水位-当日组合权益)/高水位×100；current=最后一日，max=窗口最大。
    """
    by_day: dict[date, float] = {}
    skipped = 0
    for row in rows:
        day = _row_date(row.get("trade_date"))
        equity = row.get("equity")
        if day is None or not isinstance(equity, (int, float)) or isinstance(equity, bool):
            skipped += 1
            continue
        by_day[day] = by_day.get(day, 0.0) + float(equity)
    if not by_day:
        return DrawdownReport(0.0, 0.0, 0.0, 0.0, 0, skipped)
    days = sorted(by_day)
    hwm = 0.0
    max_dd = 0.0
    equities: list[float] = []
    for day in days:
        equity = by_day[day]
        equities.append(equity)
        hwm = max(hwm, equity)
        if hwm > 0:
            max_dd = max(max_dd, (hwm - equity) / hwm * 100.0)
    latest = equities[-1]
    current_dd = (hwm - latest) / hwm * 100.0 if hwm > 0 else 0.0
    return DrawdownReport(
        current_drawdown_pct=round(current_dd, 6),
        max_drawdown_pct=round(max_dd, 6),
        high_water_mark=hwm,
        portfolio_equity_latest=latest,
        days_evaluated=len(days),
        skipped_rows=skipped,
    )


# ────────────────── 指标 1：成本兜底估算（遥测口径）──────────────────


def estimate_daily_cost(
    token_usage: Mapping[str, tuple[int, int]],
    unit_prices: Mapping[str, tuple[float, float]],
) -> tuple[float, list[str]]:
    """兜底估算：{渠道: (输入token, 输出token)} × {渠道: (元/千输入, 元/千输出)} → (日成本元, 无价渠道)。

    DESIGN §4 指标 1 数据源②（账单 API 缺席时的兜底口径；cost_source=telemetry_est）。
    无单价渠道跳过并列出（诚实口径：不虚构单价）。
    """
    total = 0.0
    unknown: list[str] = []
    for channel, (token_in, token_out) in token_usage.items():
        price = unit_prices.get(channel)
        if price is None:
            unknown.append(channel)
            continue
        total += token_in / 1000.0 * price[0] + token_out / 1000.0 * price[1]
    return round(total, 6), sorted(unknown)


# ────────────────── 越限降档联动（只产指令不执行）──────────────────


@dataclass(frozen=True)
class DegradationVerdict:
    """降档裁定：tier+触发原因+按序动作指令（原生消费方=L6/OBJ_M/配额池）。"""

    tier: str
    triggered_by: tuple[str, ...] = field(default_factory=tuple)
    actions: tuple[str, ...] = field(default_factory=tuple)


def evaluate_degradation(
    cost_yuan: float,
    drawdown_pct: float,
    thresholds: Thresholds,
) -> DegradationVerdict:
    """纯函数核：双指标 vs 软/硬线 → 三档裁定（任一越限即触发，DESIGN §4 联动表）。"""
    triggered: list[str] = []
    degrade = cost_yuan > thresholds.cost_hard_yuan or drawdown_pct > thresholds.drawdown_degrade_pct
    if cost_yuan > thresholds.cost_hard_yuan:
        triggered.append(f"cost {cost_yuan} > hard {thresholds.cost_hard_yuan}")
    if drawdown_pct > thresholds.drawdown_degrade_pct:
        triggered.append(f"drawdown {drawdown_pct}% > degrade {thresholds.drawdown_degrade_pct}%")
    if degrade:
        return DegradationVerdict(TIER_DEGRADE, tuple(triggered), DEGRADE_ACTIONS)
    attention = cost_yuan > thresholds.cost_soft_yuan or drawdown_pct > thresholds.drawdown_attention_pct
    if cost_yuan > thresholds.cost_soft_yuan:
        triggered.append(f"cost {cost_yuan} > soft {thresholds.cost_soft_yuan}")
    if drawdown_pct > thresholds.drawdown_attention_pct:
        triggered.append(f"drawdown {drawdown_pct}% > attention {thresholds.drawdown_attention_pct}%")
    if attention:
        return DegradationVerdict(TIER_ATTENTION, tuple(triggered), ATTENTION_ACTIONS)
    return DegradationVerdict(TIER_NORMAL, (), ())


def recovery_allowed(
    consecutive_ok_days: int,
    seconds_since_last_switch: float,
    oscillations_last_hour: int,
    thresholds: Thresholds,
) -> bool:
    """纯函数核：恢复门=N 日回线+滞回三件套（confirmation_count/cooldown/振荡上限照抄先例）。"""
    need_days = max(thresholds.recovery_consecutive_days, thresholds.confirmation_count)
    if consecutive_ok_days < need_days:
        return False
    if seconds_since_last_switch < thresholds.cooldown_seconds:
        return False
    return oscillations_last_hour < thresholds.oscillation_threshold_per_hour


def degrade_event_payload(verdict: DegradationVerdict) -> dict[str, Any]:
    """OBJ_M 契约事件载荷（degrade_model_tier：champion→flash/fallback；双向只走事件）。"""
    return {
        "event": "degrade_model_tier",
        "tier": verdict.tier,
        "target_route": "flash_fallback" if verdict.tier == TIER_DEGRADE else None,
        "triggered_by": list(verdict.triggered_by),
        "actions": list(verdict.actions),
        "issued_at": now_utc().isoformat(),
    }


def dashboard_snapshot(
    cost_yuan: float,
    drawdown: DrawdownReport,
    thresholds: Thresholds,
) -> dict[str, Any]:
    """看板日刷新快照（双列+档位；S7 周报 degradation_events 的计数来源）。"""
    verdict = evaluate_degradation(cost_yuan, drawdown.current_drawdown_pct, thresholds)
    return {
        "snapshot_at": now_utc().isoformat(),
        "metric_cost_yuan": cost_yuan,
        "metric_drawdown_pct": drawdown.current_drawdown_pct,
        "drawdown_max_pct": drawdown.max_drawdown_pct,
        "high_water_mark": drawdown.high_water_mark,
        "days_evaluated": drawdown.days_evaluated,
        "skipped_rows": drawdown.skipped_rows,
        "thresholds": {
            "cost_soft_yuan": thresholds.cost_soft_yuan,
            "cost_hard_yuan": thresholds.cost_hard_yuan,
            "drawdown_attention_pct": thresholds.drawdown_attention_pct,
            "drawdown_degrade_pct": thresholds.drawdown_degrade_pct,
        },
        "tier": verdict.tier,
        "triggered_by": list(verdict.triggered_by),
    }
