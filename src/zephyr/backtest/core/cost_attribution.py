# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.cost_attribution
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.cost_model_calibration（标定表与证据披露）
# [CONSUMERS] zephyr.backtest.io.result_repository.build_artifact_from_data（唯一注入点，落盘 artifact 的 metrics["cost_attribution"]，调用方=scripts/run_backtest.py + pf_core/strategy_engine/framework_composer.py S11 整装回测）; tests/backtest/test_cost_attribution.py
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数无 I/O 无墙钟; 费率字面量一律由调用方注入（本件零费率字面量，真源在 matching_logic）; 佣金分量重构 MUST 与 trade.commission 逐笔对账（相对偏差>容差即告警，不得静默改口径）; 顶地板判定用同一 max(比例佣金, 下限) 口径; 成本合计=佣金+滑点+冲击（印花/过户已含在上报佣金内，禁重复相加）; 冲击应计腿= max(引擎实测, 标定档)——实测只可抬高不可清零（任何入参组合都不得使 impact_cost_total 归零），实测另记 impact_cost_measured_total 作 as-run 披露; 任一关键量不可算 → 产出 ALERT 而非省略字段（沉默禁令）; 空 trade_log 显式抛错（不返回零值假象）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CostAttributionError(ZA-BT-0043)——结构性非法输入（缺键/非序列/空序列）时抛；数据可算但触发阈值时不抛，转为 alerts
# [TESTS] tests/backtest/test_cost_attribution.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""成交成本归因（车道 M / 台账 #23 H2-A 治本：把"一半亏损是佣金"变成产物里的显式事实）。

问题（挖矿真源 slippage_impact_cost_mining.md §1.5）：现网 run 单笔成交名义中位数
仅 ¥2,280，佣金 ¥5 下限几乎笔笔咬合，实际佣金率中位 万21.5（名义万0.854 的 25 倍），
全 run 佣金 ¥95,529 = 总亏损 ¥184,653 的 **51.7%**，而 artifact metrics 里没有任何
字段说这件事——回测把它静默吞掉了。

本件在真 artifact 上复算的口径更正（写进报告，不改台账文件）：顶地板笔数不是台账
所记 1382 笔，而是 **14,184/14,311 = 99.1%**（比例佣金只在名义 ≥¥58,548 时才生效）。

输出三类硬事实 + 结构化告警（进 ``metrics["cost_attribution"]``）：
  1. 地板佣金占比（笔数/金额/地板溢价占总佣金比）；
  2. 碎片化惩罚（名义中位数与分位、单标的单日笔数、要把地板拖累压进容忍线
     所需的名义放大倍数）；
  3. 成本/结果比 + **冲击可辨识性签名**（成交价对决策价偏离的截面标准差 ≈0 ⇔
     冲击项恒零 ⇔ 参数未标定）。用统计量而不是注释来阻止"假装已计费"。

冲击腿反旁路（H2-B 治本，口径务必看清）：应计冲击 = **max(引擎实测, 标定档)**，
调用方传入的 ``impact_bps_by_trade`` 只能抬高、不能清零应计腿——上报恒零（或未上报
却也无从辨识）不再是一句注释，而是 ``IMPACT-LEG-BYPASSED`` P0 告警；引擎真实计费
口径另记 ``impact_cost_measured_total`` 供 as-run 对账，两轨互不遮蔽。

告警是数据不是异常：触发阈值不 raise；**沉默**才是被禁止的行为。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/cost_attribution.yaml
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Final, Mapping, Sequence

from zephyr.backtest.core.cost_model_calibration import (
    LEGACY_FLAT_SLIPPAGE_BPS,
    PROVENANCE,
    SLIPPAGE_TIER_BPS,
    TIER_ADV_MEDIAN_YUAN,
    CostCalibrationError,
    floor_drag_bps,
    impact_level_for_tier,
    liquidity_tier,
    notional_for_floor_drag_bps,
)


class CostAttributionError(Exception):
    """成本归因结构性非法输入（Fail-Closed）。错误码 ZA-BT-0043（已登记转正）。

    改号留痕：初取 ZA-BT-0022 与 ``services.data_quality_checker.InvalidDataFormatError``
    重码（git 首引入者保留 canonical，#ARCH-ERRCODE-001），本类按「扫描真源+注册表
    并集 max+1」顺延取 0043。
    """

    error_code = "ZA-BT-0043"


# --- 告警阈值（全部带出处；改阈值=改口径，MUST 同步注释）---------------------

#: 顶地板笔数占比告警线 25%。出处：按 A股 100 股整手 + 万0.854 + ¥5 下限结构，
#: 地板完全不咬合需单笔名义 ≥¥58,548（100 万账户需 ≤6 只等权持仓）；四分之一的
#: 单子在下限上被惩罚即属结构性碎片化，低于该线视为零星尾单可容忍。
FLOOR_BOUND_SHARE_ALERT: Final[float] = 0.25

#: 总成本/结果绝对值 告警线 25%。出处：成本吃掉 1/4 以上结果时 alpha 与成本的
#: 归因已不可分离，报告必须先讲成本再讲信号。
COST_SHARE_OF_LOSS_ALERT: Final[float] = 0.25

#: 年化单边换手告警线 12×。出处：旧 SLIPPAGE_BPS=1 的立论前提「日频低换手」按
#: 月频调仓（单边 12×/年）为上限；现网 50.2× 直接否证（挖矿 §1.2 结论）。
TURNOVER_ONE_SIDE_ANNUAL_ALERT: Final[float] = 12.0

#: 执行成本截面标准差下限（bps）。出处：真实价差/冲击必然带横截面异质性；
#: σ<0.05bp 说明成交价是决策价的仿射函数（只有固定比例滑点）⇒ 冲击项实际恒零。
IMPACT_SIGNATURE_STDEV_ALERT: Final[float] = 0.05

#: 冲击实测「恒零」判据（bps 加权，量级即浮点噪声）。出处：真金白银的走单位移
#: 不可能小于 1e-9bp；上报到这个量级 ⇔ 冲击腿根本没参与计费（旁路），而非"很小"。
#: 背离容忍线不新设常量——与滑点欠计同纲，复用 ``SLIPPAGE_UNDERCHARGE_RATIO_ALERT``。
IMPACT_MEASURED_ZERO_EPS_BPS: Final[float] = 1e-9

#: 标定滑点/实际消费滑点 比值告警线。出处：>1.5× 即成本被结构性低估，
#: 与 2026-09 外部审查对成本口径一致性的要求同纲。
SLIPPAGE_UNDERCHARGE_RATIO_ALERT: Final[float] = 1.5

#: 地板拖累容忍线（bps）——政策单一真源在此，order_size_discipline 引用本值。
#: 取 5bp 的依据：中位名义抬到 ¥8,541 时地板拖累=5bp，与买卖双边滑点(≈7.6bp)同量级，
#: 再往下压就要牺牲持仓分散度（碎片化的另一面）。
FLOOR_DRAG_CAP_BPS: Final[float] = 5.0

#: 佣金重构逐笔对账容差（相对偏差）。出处：Decimal 舍入 + float 存储 ~1e-7 量级，
#: 取 1e-4 留三个数量级余量；超出即口径漂移（印花/过户疑似被重复计或漏计）。
COMMISSION_RECON_TOLERANCE: Final[float] = 1e-4


@dataclass(frozen=True)
class CostAlert:
    """产物内告警（结构化：代码 + 严重度 + 人话 + 数值）。"""

    code: str
    severity: str  # P0 | P1 | P2
    message: str
    value: float | None = None
    threshold: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
        }


def _quantile(sorted_vals: Sequence[float], q: float) -> float:
    """线性插值分位数（确定性；空序列 Fail-Closed）。"""
    if not sorted_vals:
        raise CostAttributionError("空序列无分位数")
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    pos = (len(sorted_vals) - 1) * q
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = pos - lo
    return float(sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac)


@dataclass(frozen=True)
class CostAttribution:
    """一次 run 的成本归因快照（frozen；``to_metrics_dict()`` 进 artifact）。"""

    trades_count: int
    buy_count: int
    sell_count: int
    notional_total: float
    notional_buy: float
    notional_sell: float
    notional_median: float
    notional_p10: float
    notional_p90: float
    commission_reported_total: float
    commission_pure_total: float
    commission_floor_premium_total: float
    transfer_fee_total: float
    stamp_tax_total: float
    floor_bound_trades: int
    floor_bound_share: float
    effective_commission_rate_median_bps: float
    quoted_commission_rate_bps: float
    slippage_cost_total: float
    impact_cost_total: float
    cost_total: float
    realized_exec_cost_bps_median: float
    realized_exec_cost_bps_stdev: float
    turnover_one_side_annualized: float | None
    cost_share_of_abs_result: float | None
    orders_per_symbol_day_mean: float
    distinct_symbol_days: int
    fragmentation_scale_up_needed: float
    min_notional_for_floor_drag_cap: float
    realized_exec_cost_total: float = 0.0
    realized_exec_cost_coverage: float = 0.0
    cost_total_as_run: float = 0.0
    cost_share_of_abs_result_as_run: float | None = None
    tier_trade_counts: tuple[int, ...] = ()
    tier_notional: tuple[float, ...] = ()
    calibrated_slippage_w_bps: float = 0.0
    calibrated_impact_w_bps: float = 0.0
    consumed_slippage_w_bps: float = 0.0
    recon_max_relative_error: float = 0.0
    impact_cost_measured_total: float = 0.0
    impact_leg_bypassed: bool = False
    adv_source: str = "trade_notional_fallback"
    alerts: tuple[CostAlert, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=dict)

    @property
    def commission_share_of_cost(self) -> float:
        return self.commission_reported_total / self.cost_total if self.cost_total > 0 else 0.0

    def to_metrics_dict(self) -> dict[str, Any]:
        """artifact ``metrics`` 片段（自由 dict，不破 frozen codegen 契约 CTR-P1-017）。"""
        return {
            "schema": "cost_attribution/1.0",
            "trades": {
                "count": self.trades_count,
                "buy": self.buy_count,
                "sell": self.sell_count,
                "notional_total": round(self.notional_total, 2),
                "notional_buy": round(self.notional_buy, 2),
                "notional_sell": round(self.notional_sell, 2),
                "notional_median": round(self.notional_median, 2),
                "notional_p10": round(self.notional_p10, 2),
                "notional_p90": round(self.notional_p90, 2),
                "orders_per_symbol_day_mean": round(self.orders_per_symbol_day_mean, 3),
                "distinct_symbol_days": self.distinct_symbol_days,
            },
            "floor_commission": {
                "floor_bound_trades": self.floor_bound_trades,
                "floor_bound_share": round(self.floor_bound_share, 6),
                "commission_reported_total": round(self.commission_reported_total, 2),
                "commission_pure_total": round(self.commission_pure_total, 2),
                "commission_floor_premium_total": round(self.commission_floor_premium_total, 2),
                "floor_premium_share_of_commission": (
                    round(self.commission_floor_premium_total / self.commission_pure_total, 6)
                    if self.commission_pure_total
                    else None
                ),
                "effective_commission_rate_median_bps": round(self.effective_commission_rate_median_bps, 3),
                "quoted_commission_rate_bps": round(self.quoted_commission_rate_bps, 3),
                "rate_inflation_x": (
                    round(self.effective_commission_rate_median_bps / self.quoted_commission_rate_bps, 2)
                    if self.quoted_commission_rate_bps
                    else None
                ),
                "min_notional_for_floor_drag_cap": round(self.min_notional_for_floor_drag_cap, 2),
                "floor_drag_cap_bps": FLOOR_DRAG_CAP_BPS,
                "fragmentation_scale_up_needed": round(self.fragmentation_scale_up_needed, 2),
            },
            "friction": {
                "transfer_fee_total": round(self.transfer_fee_total, 2),
                "stamp_tax_total": round(self.stamp_tax_total, 2),
                "slippage_cost_total": round(self.slippage_cost_total, 2),
                "impact_cost_total": round(self.impact_cost_total, 2),
                "impact_cost_measured_total": round(self.impact_cost_measured_total, 2),
                "impact_leg_bypassed": self.impact_leg_bypassed,
                "cost_total": round(self.cost_total, 2),
                "cost_share_of_abs_result": self.cost_share_of_abs_result,
                "cost_total_as_run": round(self.cost_total_as_run, 2),
                "cost_share_of_abs_result_as_run": self.cost_share_of_abs_result_as_run,
                "realized_exec_cost_total": round(self.realized_exec_cost_total, 2),
                "realized_exec_cost_coverage": round(self.realized_exec_cost_coverage, 6),
                "turnover_one_side_annualized": self.turnover_one_side_annualized,
                "realized_exec_cost_bps_median": round(self.realized_exec_cost_bps_median, 4),
                "realized_exec_cost_bps_stdev": round(self.realized_exec_cost_bps_stdev, 6),
                "commission_share_of_cost": round(self.commission_share_of_cost, 4),
                "recon_max_relative_error": self.recon_max_relative_error,
            },
            "calibration_gap": {
                "adv_source": self.adv_source,
                "tier_trade_counts": list(self.tier_trade_counts),
                "tier_notional": [round(v, 2) for v in self.tier_notional],
                "consumed_slippage_w_bps": round(self.consumed_slippage_w_bps, 4),
                "calibrated_slippage_w_bps": round(self.calibrated_slippage_w_bps, 4),
                "calibrated_impact_w_bps": round(self.calibrated_impact_w_bps, 4),
                "legacy_flat_slippage_bps": float(LEGACY_FLAT_SLIPPAGE_BPS),
                "slippage_tier_bps": [float(v) for v in SLIPPAGE_TIER_BPS],
            },
            "alerts": [a.to_dict() for a in self.alerts],
            "provenance": PROVENANCE.to_dict(),
            "extra": dict(self.extra),
        }


def _side_of(row: Mapping[str, Any]) -> str:
    side = str(row.get("side") or "").strip().upper()
    if side in ("BUY", "B", "买", "买入"):
        return "BUY"
    if side in ("SELL", "S", "卖", "卖出"):
        return "SELL"
    raise CostAttributionError(f"未知买卖方向: {row.get('side')!r}（词表 BUY|SELL）")


def _build_alerts(ctx: dict[str, Any]) -> list[CostAlert]:
    """按阈值把事实翻成告警（唯一告警出口，便于用例穷举）。"""
    alerts: list[CostAlert] = []
    if ctx["floor_share"] > FLOOR_BOUND_SHARE_ALERT:
        alerts.append(
            CostAlert(
                code="COST-FLOOR-DOMINANT",
                severity="P0",
                message=(
                    f"{ctx['floor_bound']}/{ctx['n']} 笔成交顶佣金下限（{ctx['floor_share']:.1%}），"
                    f"中位名义 ¥{ctx['notional_median']:,.0f}，需合并至 ≥¥{ctx['min_notional_cap']:,.0f}"
                    f" 才能把地板拖累压进 {FLOOR_DRAG_CAP_BPS:g}bp——策略碎片化未受约束"
                ),
                value=ctx["floor_share"],
                threshold=FLOOR_BOUND_SHARE_ALERT,
            )
        )
    if ctx["cost_share"] is not None and ctx["cost_share"] > COST_SHARE_OF_LOSS_ALERT:
        _extra = (
            f"（该 run 实际计费口径 ¥{ctx['cost_total_as_run']:,.0f} = {ctx['cost_share_as_run']:.1%}）"
            if ctx.get("cost_share_as_run") is not None
            else ""
        )
        alerts.append(
            CostAlert(
                code="COST-DOMINATES-RESULT",
                severity="P0",
                message=(
                    f"交易成本 ¥{ctx['cost_total']:,.0f} 占结果绝对值 {ctx['cost_share']:.1%}"
                    f"{_extra}，其中佣金 ¥{ctx['commission_reported']:,.0f}"
                    f"（地板溢价 ¥{ctx['floor_premium']:,.0f}）——收益归因前必须先做成本归因"
                ),
                value=ctx["cost_share"],
                threshold=COST_SHARE_OF_LOSS_ALERT,
            )
        )
    if ctx["turnover"] is not None and ctx["turnover"] > TURNOVER_ONE_SIDE_ANNUAL_ALERT:
        alerts.append(
            CostAlert(
                code="TURNOVER-BREAKS-SLIPPAGE-PREMISE",
                severity="P1",
                message=(
                    f"年化单边换手 {ctx['turnover']:.1f}× > 旧固定滑点立论上限 "
                    f"{TURNOVER_ONE_SIDE_ANNUAL_ALERT:g}×——「日频低换手」前提已被证伪，"
                    "滑点必须按流动性分层计费"
                ),
                value=ctx["turnover"],
                threshold=TURNOVER_ONE_SIDE_ANNUAL_ALERT,
            )
        )
    if ctx["exec_n"] > 1 and ctx["stdev"] < IMPACT_SIGNATURE_STDEV_ALERT:
        alerts.append(
            CostAlert(
                code="IMPACT-TERMS-UNIDENTIFIED",
                severity="P1",
                message=(
                    f"成交价对决策价偏离 中位 {ctx['median_exec']:.4f}bp / 标准差 {ctx['stdev']:.6f}bp"
                    f"（n={ctx['exec_n']}）——执行成本是决策价的仿射函数，冲击项实际恒零，"
                    "Almgren-Chriss 参数未经标定（DEFAULT_PARAMS 静默旁路）"
                ),
                value=ctx["stdev"],
                threshold=IMPACT_SIGNATURE_STDEV_ALERT,
            )
        )
    if ctx["impact_bypassed"]:
        _zero = ctx["impact_measured_w_bps"] <= IMPACT_MEASURED_ZERO_EPS_BPS
        _how = "恒零＝冲击腿完全未参与计费" if _zero else f"仅为标定档的 1/{ctx['impact_undercharge_x']:.1f}"
        alerts.append(
            CostAlert(
                code="IMPACT-LEG-BYPASSED",
                severity="P0",
                message=(
                    f"引擎上报逐笔冲击加权 {ctx['impact_measured_w_bps']:.6g}bp/边（{_how}），"
                    f"标定档应为 {ctx['calibrated_impact_w_bps']:.2f}bp/边——冲击成本被旁路；"
                    f"应计冲击腿已按 max(实测, 标定档) 计足 {ctx['calibrated_impact_w_bps']:.2f}bp/边，"
                    "任何入参组合都无法把 cost_total 的冲击分量清零"
                ),
                value=ctx["impact_measured_w_bps"],
                threshold=IMPACT_MEASURED_ZERO_EPS_BPS if _zero else SLIPPAGE_UNDERCHARGE_RATIO_ALERT,
            )
        )
    if ctx["slippage_ratio"] > SLIPPAGE_UNDERCHARGE_RATIO_ALERT:
        alerts.append(
            CostAlert(
                code="SLIPPAGE-UNDERCHARGED",
                severity="P1",
                message=(
                    f"该 run 消费滑点 {ctx['consumed_bps']:g}bp/边，标定应为 "
                    f"{ctx['calibrated_slippage_w_bps']:.2f}bp/边（{ctx['slippage_ratio']:.1f}×）"
                    f"，冲击应为 {ctx['calibrated_impact_w_bps']:.2f}bp/边——成本被结构性低估"
                ),
                value=ctx["slippage_ratio"],
                threshold=SLIPPAGE_UNDERCHARGE_RATIO_ALERT,
            )
        )
    if ctx["recon_err"] > COMMISSION_RECON_TOLERANCE:
        alerts.append(
            CostAlert(
                code="COMMISSION-RECON-DRIFT",
                severity="P1",
                message=(
                    f"逐笔佣金重构与上报值最大相对偏差 {ctx['recon_err']:.2e} > 容差 "
                    f"{COMMISSION_RECON_TOLERANCE:.0e}——费率口径疑似重复计或漏计"
                ),
                value=ctx["recon_err"],
                threshold=COMMISSION_RECON_TOLERANCE,
            )
        )
    if not alerts:
        alerts.append(CostAlert(code="COST-MODEL-OK", severity="P2", message="成本归因无越线项（阈值全过）"))
    return alerts


def attribute_trade_costs(
    trades: Sequence[Mapping[str, Any]],
    *,
    commission_rate: Decimal,
    stamp_tax_rate: Decimal,
    transfer_fee_rate: Decimal,
    min_commission: Decimal,
    consumed_slippage_bps: Decimal | float | None = None,
    initial_capital: float | None = None,
    n_trading_days: int | None = None,
    net_result: float | None = None,
    adv_notional_by_symbol: Mapping[str, float] | None = None,
    impact_bps_by_trade: Sequence[float] | None = None,
) -> CostAttribution:
    """从成交明细重构成本归因（纯函数；费率注入，本件零费率字面量）。

    Args:
        trades: artifact ``trade_log`` 形态（timestamp/symbol/side/price/quantity[/commission
            /decision_price]）。缺 commission 时按注入费率重构。
        commission_rate / stamp_tax_rate / transfer_fee_rate / min_commission:
            注入自 ``matching_logic`` 常量真源（禁第二处字面量）。
        consumed_slippage_bps: 该 run 实际消费的滑点 bps（标定缺口披露用）。
        initial_capital / n_trading_days: 给了才算年化单边换手。
        net_result: 该 run 净结果（元，正负均可）；给了才算成本/结果比。
        adv_notional_by_symbol: 标的 → 日均成交额（元）。缺失时以该笔自身名义就近
            落层（小额单必落最不流动层 = 成本上界，保守方向）；参用率分母退化到
            该层代表 ADV，两者都写进 ``adv_source`` 供披露。
        impact_bps_by_trade: 逐笔冲击 bps（引擎真实计费口径，长度须等于笔数）。
            只用于 as-run 披露与旁路判定：**应计冲击 = max(实测, 标定档)**，实测
            只能抬高不能清零；非有限/负值 → CostAttributionError。缺省（None）时
            应计腿直接取标定档推算，实测轨记 0，但「未上报」本身不判为旁路。
    """
    if trades is None:
        raise CostAttributionError("trades 不能为 None")
    if isinstance(trades, (str, bytes)) or not isinstance(trades, Sequence):
        raise CostAttributionError("trades 必须是序列")
    if len(trades) == 0:
        raise CostAttributionError("trades 为空——无成交则成本归因无定义，请显式分支处理")
    rate = Decimal(str(commission_rate))
    stamp = Decimal(str(stamp_tax_rate))
    transfer = Decimal(str(transfer_fee_rate))
    floor = Decimal(str(min_commission))
    if rate <= 0 or floor <= 0 or stamp < 0 or transfer < 0:
        raise CostAttributionError(f"费率注入非法: {rate} {stamp} {transfer} {floor}")
    if impact_bps_by_trade is not None:
        if isinstance(impact_bps_by_trade, (str, bytes)) or not isinstance(impact_bps_by_trade, Sequence):
            raise CostAttributionError("impact_bps_by_trade 必须是序列（None 表示引擎未上报）")
        if len(impact_bps_by_trade) != len(trades):
            raise CostAttributionError(
                f"impact_bps_by_trade 长度 {len(impact_bps_by_trade)} ≠ 成交笔数 {len(trades)}"
                "（截断=实测冲击被静默少计，Fail-Closed）"
            )

    adv_map = {str(k)[:6]: float(v) for k, v in (adv_notional_by_symbol or {}).items()}
    consumed_bps = (
        float(consumed_slippage_bps) if consumed_slippage_bps is not None else float(LEGACY_FLAT_SLIPPAGE_BPS)
    )

    notionals: list[float] = []
    sides: list[str] = []
    eff_rate_bps: list[float] = []
    exec_cost_bps: list[float] = []
    tier_counts = [0] * len(SLIPPAGE_TIER_BPS)
    tier_notional = [0.0] * len(SLIPPAGE_TIER_BPS)
    symbol_day: dict[tuple[str, str], int] = defaultdict(int)
    reported_commission = 0.0
    pure_commission = 0.0
    proportional_only = 0.0
    transfer_total = 0.0
    stamp_total = 0.0
    floor_bound = 0
    slip_cost = 0.0
    imp_cost = 0.0
    imp_cost_calibrated = 0.0
    imp_cost_measured = 0.0
    recon_err = 0.0
    adv_hits = 0
    realized_exec_total = 0.0
    realized_exec_n = 0
    realized_notional = 0.0

    for idx, row in enumerate(trades):
        if not isinstance(row, Mapping):
            raise CostAttributionError(f"trade[{idx}] 必须是 mapping，实得 {type(row).__name__}")
        price = row.get("price")
        qty = row.get("quantity")
        if price is None or qty is None:
            raise CostAttributionError(f"trade[{idx}] 缺 price/quantity 键")
        try:
            g = Decimal(str(price)) * Decimal(str(qty))
        except Exception as exc:  # noqa: BLE001 — 结构非法必须点名到笔
            raise CostAttributionError(f"trade[{idx}] price/quantity 非数值: {exc}") from exc
        if g <= 0:
            raise CostAttributionError(f"trade[{idx}] 名义非正: {g}")
        g_float = float(g)
        side = _side_of(row)
        notionals.append(g_float)
        sides.append(side)

        proportional = g * rate
        proportional_only += float(proportional)
        if proportional < floor:
            floor_bound += 1
            commission_pure = floor
        else:
            commission_pure = proportional
        pure_commission += float(commission_pure)
        tr = float(g * transfer)
        st = float(g * stamp) if side == "SELL" else 0.0
        transfer_total += tr
        stamp_total += st
        eff_rate_bps.append(float(commission_pure / g * Decimal("10000")))

        reported = row.get("commission")
        if reported is not None:
            reported_commission += float(reported)
            expected = float(commission_pure) + tr + st
            if expected > 0:
                recon_err = max(recon_err, abs(float(reported) - expected) / expected)

        sym = str(row.get("symbol") or "")[:6]
        ts = str(row.get("timestamp") or "")
        if sym and ts:
            symbol_day[(sym, ts)] += 1

        # ---- 分层与两腿成本 ----
        adv_raw = adv_map.get(sym)
        adv_is_real = adv_raw is not None and adv_raw > 0
        if adv_is_real:
            adv_hits += 1
            adv = adv_raw
        else:
            adv = g_float  # 保守退化：小名义 → 高成本层（仅用于分层）
        try:
            tier = liquidity_tier(adv)
        except CostCalibrationError as exc:
            raise CostAttributionError(f"trade[{idx}] 分层失败: {exc}") from exc
        tier_counts[tier] += 1
        tier_notional[tier] += g_float
        slip_bps = float(SLIPPAGE_TIER_BPS[tier])
        slip_cost += g_float * slip_bps / 1e4
        # rpt_b11 P1：旧码分母=max(g, tier_median×1e-12)，ADV 缺失时 g/max(g,ε)≡1.0
        # → 落在标定拟合域外 2 个数量级，冲击腿 199.7bp/边（55× 虚高）。
        # 对齐 docstring 契约：ADV 缺失时分母退化到该层代表 ADV。
        part_denom = adv if adv_is_real else float(TIER_ADV_MEDIAN_YUAN[tier])
        participation = g_float / max(part_denom, TIER_ADV_MEDIAN_YUAN[tier] * 1e-12)
        calibrated_imp_bps = impact_level_for_tier(tier).cost_bps_at(min(max(participation, 0.0), 1.0))
        imp_cost_calibrated += g_float * calibrated_imp_bps / 1e4
        if impact_bps_by_trade is not None:
            try:
                measured_imp_bps = float(impact_bps_by_trade[idx])
            except (TypeError, ValueError) as exc:
                raise CostAttributionError(f"trade[{idx}] 冲击 bps 非数值: {exc}") from exc
            if not math.isfinite(measured_imp_bps) or measured_imp_bps < 0:
                raise CostAttributionError(f"trade[{idx}] 冲击 bps 必须是 [0,∞) 有限数，实得 {measured_imp_bps!r}")
            imp_cost_measured += g_float * measured_imp_bps / 1e4
            # 反旁路：实测只抬高应计腿，永不清零（清零=DEFAULT_PARAMS 未标定路径）
            imp_bps = max(measured_imp_bps, calibrated_imp_bps)
        else:
            imp_bps = calibrated_imp_bps
        imp_cost += g_float * imp_bps / 1e4

        dp = row.get("decision_price")
        if dp:
            bps = (float(price) - float(dp)) / float(dp) * 1e4 * (1.0 if side == "BUY" else -1.0)
            exec_cost_bps.append(bps)
            realized_exec_total += g_float * bps / 1e4
            realized_exec_n += 1
            realized_notional += g_float

    ordered = sorted(notionals)
    notional_total = sum(notionals)
    notional_buy = sum(n for n, s in zip(notionals, sides, strict=True) if s == "BUY")
    notional_median = _quantile(ordered, 0.5)
    notional_p10 = _quantile(ordered, 0.10)
    notional_p90 = _quantile(ordered, 0.90)
    buy_count = sides.count("BUY")
    sell_count = len(sides) - buy_count
    commission_reported = (
        reported_commission if reported_commission > 0 else pure_commission + transfer_total + stamp_total
    )
    cost_total = commission_reported + slip_cost + imp_cost
    # as-run：该 run **实际**扣掉的钱（佣金上报值 + 成交价对决策价的真实偏离）。
    # decision_price 缺失时退化为「消费滑点比例 × 名义」（冲击项按引擎实测≈0 计）。
    if realized_exec_n:
        realized_exec_cost_total = realized_exec_total + ((notional_total - realized_notional) * consumed_bps / 1e4)
        realized_exec_coverage = realized_exec_n / len(notionals)
    else:
        realized_exec_cost_total = notional_total * consumed_bps / 1e4
        realized_exec_coverage = 0.0
    cost_total_as_run = commission_reported + realized_exec_cost_total
    calibrated_slippage_w_bps = slip_cost / notional_total * 1e4
    calibrated_impact_w_bps = imp_cost_calibrated / notional_total * 1e4
    measured_impact_w_bps = imp_cost_measured / notional_total * 1e4
    # 反旁路判定只在引擎确实上报了冲击时进行：恒零或欠计越过容忍线（与滑点欠计同纲）
    impact_leg_bypassed = impact_bps_by_trade is not None and (
        measured_impact_w_bps <= IMPACT_MEASURED_ZERO_EPS_BPS
        or calibrated_impact_w_bps > measured_impact_w_bps * SLIPPAGE_UNDERCHARGE_RATIO_ALERT
    )
    impact_undercharge_x = calibrated_impact_w_bps / measured_impact_w_bps if measured_impact_w_bps > 0 else math.inf

    turnover: float | None = None
    if initial_capital and n_trading_days and float(initial_capital) > 0 and int(n_trading_days) > 0:
        turnover = notional_buy / float(initial_capital) * (252.0 / float(n_trading_days))
    cost_share = cost_total / abs(net_result) if net_result is not None and abs(net_result) > 0 else None
    cost_share_as_run = cost_total_as_run / abs(net_result) if net_result is not None and abs(net_result) > 0 else None

    if exec_cost_bps:
        mu = sum(exec_cost_bps) / len(exec_cost_bps)
        stdev = (
            math.sqrt(sum((v - mu) ** 2 for v in exec_cost_bps) / (len(exec_cost_bps) - 1))
            if len(exec_cost_bps) > 1
            else 0.0
        )
        median_exec = _quantile(sorted(exec_cost_bps), 0.5)
    else:
        mu = stdev = median_exec = 0.0

    min_notional_cap = float(
        notional_for_floor_drag_bps(FLOOR_DRAG_CAP_BPS, commission_rate=rate, min_commission=floor)
    )
    slippage_ratio = calibrated_slippage_w_bps / consumed_bps if consumed_bps > 0 else float("inf")

    alerts = _build_alerts(
        {
            "n": len(notionals),
            "floor_bound": floor_bound,
            "floor_share": floor_bound / len(notionals),
            "notional_median": notional_median,
            "min_notional_cap": min_notional_cap,
            "cost_total": cost_total,
            "cost_share": cost_share,
            "cost_share_as_run": cost_share_as_run,
            "cost_total_as_run": cost_total_as_run,
            "floor_premium": pure_commission - proportional_only,
            "commission_reported": commission_reported,
            "turnover": turnover,
            "exec_n": len(exec_cost_bps),
            "stdev": stdev,
            "median_exec": median_exec,
            "consumed_bps": consumed_bps,
            "calibrated_slippage_w_bps": calibrated_slippage_w_bps,
            "calibrated_impact_w_bps": calibrated_impact_w_bps,
            "impact_bypassed": impact_leg_bypassed,
            "impact_measured_w_bps": measured_impact_w_bps,
            "impact_undercharge_x": impact_undercharge_x,
            "slippage_ratio": slippage_ratio,
            "recon_err": recon_err,
        }
    )

    return CostAttribution(
        trades_count=len(notionals),
        buy_count=buy_count,
        sell_count=sell_count,
        notional_total=notional_total,
        notional_buy=notional_buy,
        notional_sell=sum(notionals) - notional_buy,
        notional_median=notional_median,
        notional_p10=notional_p10,
        notional_p90=notional_p90,
        commission_reported_total=commission_reported,
        commission_pure_total=pure_commission,
        commission_floor_premium_total=pure_commission - proportional_only,
        transfer_fee_total=transfer_total,
        stamp_tax_total=stamp_total,
        floor_bound_trades=floor_bound,
        floor_bound_share=floor_bound / len(notionals),
        effective_commission_rate_median_bps=_quantile(sorted(eff_rate_bps), 0.5),
        quoted_commission_rate_bps=float(rate * Decimal("10000")),
        slippage_cost_total=slip_cost,
        impact_cost_total=imp_cost,
        cost_total=cost_total,
        realized_exec_cost_bps_median=median_exec,
        realized_exec_cost_bps_stdev=stdev,
        turnover_one_side_annualized=turnover,
        cost_share_of_abs_result=cost_share,
        realized_exec_cost_total=realized_exec_cost_total,
        realized_exec_cost_coverage=realized_exec_coverage,
        cost_total_as_run=cost_total_as_run,
        cost_share_of_abs_result_as_run=cost_share_as_run,
        orders_per_symbol_day_mean=sum(symbol_day.values()) / len(symbol_day) if symbol_day else 0.0,
        distinct_symbol_days=len(symbol_day),
        fragmentation_scale_up_needed=min_notional_cap / notional_median if notional_median > 0 else math.inf,
        min_notional_for_floor_drag_cap=min_notional_cap,
        tier_trade_counts=tuple(tier_counts),
        tier_notional=tuple(tier_notional),
        calibrated_slippage_w_bps=calibrated_slippage_w_bps,
        calibrated_impact_w_bps=calibrated_impact_w_bps,
        consumed_slippage_w_bps=consumed_bps,
        recon_max_relative_error=recon_err,
        impact_cost_measured_total=imp_cost_measured,
        impact_leg_bypassed=impact_leg_bypassed,
        adv_source=(
            "adv_table"
            if adv_hits == len(notionals)
            else f"adv_table_partial({adv_hits}/{len(notionals)})"
            if adv_hits
            else "trade_notional_fallback"
        ),
        alerts=tuple(alerts),
        extra={
            "floor_drag_median_bps": round(
                floor_drag_bps(notional_median, commission_rate=rate, min_commission=floor), 3
            ),
            "floor_drag_p10_bps": round(floor_drag_bps(notional_p10, commission_rate=rate, min_commission=floor), 3),
            "floor_drag_p90_bps": round(floor_drag_bps(notional_p90, commission_rate=rate, min_commission=floor), 3),
            "proportional_commission_only_total": round(proportional_only, 2),
            "impact_accrued_w_bps": round(imp_cost / notional_total * 1e4, 4),
            "impact_measured_w_bps": round(measured_impact_w_bps, 4),
        },
    )


__all__ = [
    "COMMISSION_RECON_TOLERANCE",
    "COST_SHARE_OF_LOSS_ALERT",
    "FLOOR_BOUND_SHARE_ALERT",
    "FLOOR_DRAG_CAP_BPS",
    "IMPACT_MEASURED_ZERO_EPS_BPS",
    "IMPACT_SIGNATURE_STDEV_ALERT",
    "SLIPPAGE_UNDERCHARGE_RATIO_ALERT",
    "TURNOVER_ONE_SIDE_ANNUAL_ALERT",
    "CostAlert",
    "CostAttribution",
    "CostAttributionError",
    "attribute_trade_costs",
]
