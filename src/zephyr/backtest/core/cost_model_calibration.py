# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.cost_model_calibration
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] 无（纯常量+纯函数；不导入 matching_logic——费率字面量真源仍在其内，本件零费率字面量）
# [CONSUMERS] zephyr.backtest.core.matching_logic（滑点腿 resolve_slippage_bps + LEGACY 对照常量）; zephyr.backtest.core.matching_engine（冲击腿 calibration_enabled + liquidity_tier + impact_level_for_tier）; zephyr.backtest.implementations.vectorized_engine（默认口径=逐笔解析，不再钉住 LEGACY 常量）; zephyr.backtest.core.cost_attribution（档位/证据/地板拖累闭式）; zephyr.backtest.io.result_repository（成本归因快照的补计口径）。注：地板佣金「最小单量」纪律当前以产物侧披露+告警兑现（cost_attribution），策略侧下单规模硬约束尚无消费者——勿凭本行臆断已有
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 分层阈值与档位值只能来自标定证据（PROVENANCE 记录窗口/样本量/口径），禁止无出处调参; liquidity_tier 单调非增（越不流动→成本越高）; slippage/impact 两腿互斥计费（滑点=尺寸无关、冲击=尺寸相关，eff<c1 实证支持不含尺寸溢价）; 纯函数无副作用无 I/O; 同输入必同输出; tier 越界 Fail-Closed 抛错（不静默夹取）
# [MODIFY-GUARD] 档位数值改动 MUST 同步更新 PROVENANCE（窗口/样本量/口径）并附真数据前后对比——数值即证据结论，无证据改数等同造第二真源
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CostCalibrationError(ZA-BT-0044)——非法输入（NaN/负/非单调表）时抛；不在查询路径静默兜底
# [TESTS] tests/backtest/test_cost_model_calibration.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""成本模型标定单一真源（车道 M / 台账 #23 H2-A·H2-C 治本）。

治本对象（挖矿真源：docs/_working/full-auto-chain/S11_assembled_backtest/
nodes/slippage_impact_cost_mining.md §1.2/§1.3/§1.5）：
  1. ``matching_logic.SLIPPAGE_BPS = 1`` 无出处——"日频低换手"前提被实盘
     52× 年化单边换手直接否证，且现值比实测一侧执行成本低 3.8 倍；
  2. ``almgren_chriss_impact_model.DEFAULT_PARAMS`` 恒被消费（estimate_params
     零生产者），实盘成交相对决策价恒 ±1.000bp 零方差 = 冲击≈0；
  3. 地板佣金吞噬收益（顶五成交占比 99.1%，全 run 佣金 ¥95,529 = 总亏损
     51.7%）——本件给出「地板佣金→最小下单规模」的第一性推导口径。

本件只做一件事：把上面三处的**标定结论**落成带出处的常量与纯查表函数，
使滑点/冲击参数有一个可读、可核、可回滚的单一真源位点。数值来源与口径
全部记在 ``PROVENANCE``（窗口 2026-07-24~2026-09-16，5,519 只标的，
13,119,233 条五档快照，本地无泄漏复算脚本见 TESTS 指向的用例）。

三段语义（务必按此消费，不得混用）：
  * 滑点腿 = **尺寸无关**的执行成本（跨价差 + 逆向选择），按流动性分层取值；
    回测合成盘口 ask1==bid1==last（零价差，matching_engine._synthetic_order_book），
    故滑点常量是价差成本的唯一承载位点，不是"额外保险"。
  * 冲击腿 = **尺寸相关**的成本（走深盘口的价格位移），由 Almgren-Chriss
    η·p^β·σ 承载，γ（永久项）实证不可从静态快照辨识，取 0（理由见
    IMPACT_GAMMA_RATIO 注释）——把测得的瞬时位移拆一半给 γ 会双重计费。
  * 佣金腿 = 券商费率结构（真源仍在 matching_logic，本件零费率字面量）。

# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/cost_model_calibration.yaml
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Final


class CostCalibrationError(Exception):
    """成本标定输入非法（Fail-Closed）。

    错误码 ZA-BT-0044（已登记转正；非法输入一律抛错，不降级为静默兜底）。

    改号留痕：初取 ZA-BT-0021 与 ``services.param_analyzer.ParamAnalysisError`` 重码
    （git 首引入者保留 canonical，#ARCH-ERRCODE-001），本类按「扫描真源+注册表并集
    max+1」顺延取 0044。
    """

    error_code = "ZA-BT-0044"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# ---------------------------------------------------------------------------
# 证据元数据（改动档位数值必须先改动这里，否则视为无出处调参）
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CalibrationProvenance:
    """标定证据（frozen；随 artifact 披露，让"参数从哪来"在产物里可审计）。"""

    calibration_id: str
    window_start: str
    window_end: str
    n_symbols: int
    n_tick_snapshots: int
    n_kline_days_per_symbol_min: int
    tables: tuple[str, ...]
    slippage_measure: str
    impact_measure: str
    identifiability: str
    cross_checks: dict[str, str]
    known_limits: tuple[str, ...]
    unit_gotchas: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "calibration_id": self.calibration_id,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "n_symbols": self.n_symbols,
            "n_tick_snapshots": self.n_tick_snapshots,
            "n_kline_days_per_symbol_min": self.n_kline_days_per_symbol_min,
            "tables": list(self.tables),
            "slippage_measure": self.slippage_measure,
            "impact_measure": self.impact_measure,
            "identifiability": self.identifiability,
            "cross_checks": dict(self.cross_checks),
            "known_limits": list(self.known_limits),
            "unit_gotchas": list(self.unit_gotchas),
        }


#: 标定证据真源（车道 M，2026-09-16 实数据挖掘）
PROVENANCE: Final[CalibrationProvenance] = CalibrationProvenance(
    calibration_id="COST-CAL-M-2026Q3-1",
    window_start="2026-07-24",
    window_end="2026-09-16",
    n_symbols=5519,
    n_tick_snapshots=13119233,
    n_kline_days_per_symbol_min=20,
    tables=("c1_market.tick_depth_5", "c1_market.kline_daily"),
    slippage_measure=(
        "有效价差（Lee-Ready 型）= median(|trade_price/mid - 1|)×1e4，逐标的取中位、"
        "逐流动性层取横截面中位；mid=(ask1+bid1)/2。同层 last→ask1 / last→bid1 一侧"
        "成本中位数（2.81bp 名义加权）低于本口径，故本表在所有层都不低估成本。"
    ),
    impact_measure=(
        "盘口走单价差曲线：Level k 的 VWAP 增量成本 c_k = Σ_{i≤k}(ask_i·v_i)/Σ_{i≤k}v_i ÷ mid - 1，"
        "对 (Δp = (v_k - v_1)/ADV股, Δc = c_k - c_1) 做 log-log 拟合；"
        "β 取五层各自拟合系数的中位数 β*，η 固定 β* 后取逐层 log(Δc/(p^β*·σ)) 中位数。"
    ),
    identifiability=(
        "A股最小变动价位 0.01 元（本样本中位 7.22bp/侧）：Δc 低于 1.5 个 tick 的点被量化噪声"
        "主导，全部剔除后再拟合。剔除后各层可辨识点占比 0%(L2)/1.5-7%(L3)/17-29%(L4)/82-92%(L5)，"
        "每层 1,067~1,397 个可辨识点。不做该剔除会得到 η≈20~41、¥2280 单 13-18bp 冲击的荒谬结论。"
    ),
    cross_checks={
        "eff_vs_quoted": (
            "各层有效价差 c1 比报价半价差 7.83/5.93/4.79/4.12/2.46 低 6%~5%（eff<c1）："
            "成交普遍在报价内改善 → 滑点腿不含尺寸溢价，与冲击腿正交，双腿相加不重复计费。"
        ),
        "sqrt_law_Y": (
            "平方根律等价系数 Y=cost/(σ·√p)=η·p^(β*-0.5)：Q1 @p=1e-3 时 Y≈2.2、Q5≈0.7，"
            "落于业界 A股中小票 1~3 区间（美股大盘约 0.5），量级自洽。"
        ),
        "turnover_premise": (
            "SLIPPAGE_BPS=1 的「日频低换手」前提被实盘 run 年化单边换手 50.2× 否证，"
            "且该 1bp 与实测最便宜一层（2.34bp）都相差 2.3 倍以上。"
        ),
    },
    known_limits=(
        "样本窗仅 39 个自然日（40 交易日）单一样本窗，未做跨 regime 稳健性检验；",
        "快照只含 5 档，订单规模超过 5 档累计深度时成本曲线外推（现网最大 p 未超域，见 run 侧披露）；",
        "有效价差用全时段快照中位数代理「收盘价基准」的次日执行成本，未单独测开盘竞价段；",
        "分层边界按成交额五分位（横截面等分），非市值分层——小市值低流动票主要落在 Q1，但不等价。",
    ),
    unit_gotchas=(
        "c1_market.kline_daily.volume 单位=**手**（实证：000001 amount/volume=1182.9=100×成交价 11.82），"
        "ADV 股数 = avg(volume)×100；",
        "c1_market.tick_depth_5.ask_volumeN 单位同样=**手**（实证：600519@2026-09-15 max(volume)=13762"
        " 与 kline_daily.volume(手) 逐笔对齐；601398 五档累计 58780 手=5.88e6 股=¥47.7M，"
        "若按股解释则仅 ¥0.48M，不成立）→ 参与率分母/分子一律 ×100 换算为股；",
        "把档位量纲读成「股」会让参与率小 100 倍、η 被 100^β 倍放大（实测 η 从 0.31~0.98 虚高到 ≈20）。",
    ),
)

#: 标定表版本（进 artifact，便于回溯是哪一版参数跑出的结果）
CALIBRATION_TABLE_VERSION: Final[str] = PROVENANCE.calibration_id


# ---------------------------------------------------------------------------
# 流动性分层（ADV 五分位）
# ---------------------------------------------------------------------------

#: 五分位上界（元/日成交额，升序 4 个边界 → 5 层）。窗口内横截面等分位点。
ADV_QUINTILE_BOUNDS_YUAN: Final[tuple[float, ...]] = (
    46410406.9,
    90212531.7,
    173965046.8,
    417979415.5,
)

#: 层名（披露用）
TIER_NAMES: Final[tuple[str, ...]] = ("Q1_illiquid", "Q2", "Q3", "Q4", "Q5_liquid")

#: 各层代表日成交额（横截面中位，元）——证据用，不参与计算
TIER_ADV_MEDIAN_YUAN: Final[tuple[float, ...]] = (
    30304653.0,
    65427447.5,
    124043709.15,
    248700286.75,
    811019252.1,
)

#: 各层横截面中位最小变动价位成本（bps/侧）——辨识门槛换算用
TIER_TICK_BPS: Final[tuple[float, ...]] = (8.783, 9.170, 7.915, 6.940, 4.140)


def n_tiers() -> int:
    """档位数（由分层边界唯一决定，禁手写魔数）。"""
    return len(ADV_QUINTILE_BOUNDS_YUAN) + 1


def liquidity_tier(daily_notional_yuan: float) -> int:
    """按日成交额（元）落流动性层：0=最不流动 … n_tiers()-1=最流动。

    分层母体是 40 日 ADV；调用方若只有"当日成交额"，用它代入是单调近似的
    同一把尺子（层对成本单调，误差只是层间抖动），可接受且已在报告披露。
    """
    if isinstance(daily_notional_yuan, bool) or not isinstance(daily_notional_yuan, (int, float)):
        raise CostCalibrationError(f"日成交额必须是数值: {daily_notional_yuan!r}")
    v = float(daily_notional_yuan)
    if not math.isfinite(v) or v < 0:
        raise CostCalibrationError(f"日成交额必须是非负有限数: {v!r}")
    if len(ADV_QUINTILE_BOUNDS_YUAN) + 1 != len(SLIPPAGE_TIER_BPS):
        raise CostCalibrationError("分层边界数与档位表长度不一致（标定表自毁）")
    for i, bound in enumerate(ADV_QUINTILE_BOUNDS_YUAN):
        if v < bound:
            return i
    return len(ADV_QUINTILE_BOUNDS_YUAN)


# ---------------------------------------------------------------------------
# 滑点腿：尺寸无关执行成本（分层）
# ---------------------------------------------------------------------------

#: 各层滑点（bps/单边，有效价差中位）。替换 matching_logic.SLIPPAGE_BPS=1 的一口价。
#: Q1=7.24 / Q2=5.69 / Q3=4.67 / Q4=4.00 / Q5=2.34
SLIPPAGE_TIER_BPS: Final[tuple[Decimal, ...]] = (
    Decimal("7.24"),
    Decimal("5.69"),
    Decimal("4.67"),
    Decimal("4.00"),
    Decimal("2.34"),
)

#: 旧一口价（仅作披露与回归对照，禁止作为默认值继续消费）
LEGACY_FLAT_SLIPPAGE_BPS: Final[Decimal] = Decimal("1")

#: 兼容/兜底档：全市场名义加权值（无法定标流动性的标的用它，仍是实证数）
SLIPPAGE_BPS_UNIVERSAL: Final[Decimal] = Decimal("3.79")

#: 默认档位表生效开关语义：True=按层取值（车道 A diff 用）
SLIPPAGE_TIERING_ENABLED: Final[bool] = True


def slippage_bps_for_notional(daily_notional_yuan: float) -> Decimal:
    """按流动性层取滑点 bps（单边，含价差+逆向选择，不含尺寸冲击）。"""
    return SLIPPAGE_TIER_BPS[liquidity_tier(daily_notional_yuan)]


def slippage_bps_universal() -> Decimal:
    """无流动性信息时的滑点 bps（名义加权实证值，非旧一口价）。"""
    return SLIPPAGE_BPS_UNIVERSAL


def calibration_enabled() -> bool:
    """标定口径总开关的**调用期**读法（= ``SLIPPAGE_TIERING_ENABLED``）。

    为什么要有这个访问器：消费方写 ``from ... import SLIPPAGE_TIERING_ENABLED``
    会把布尔值在导入期绑死成局部名，A/B 取证时就只能改源码才能回到旧口径；
    经本函数读全局，``monkeypatch.setattr(cost_model_calibration, "SLIPPAGE_TIERING_ENABLED",
    False)`` 即整仓回到 legacy 口径——开关位点仍是既有常量，不新设第二套命名空间。
    """
    return SLIPPAGE_TIERING_ENABLED


def resolve_slippage_bps(
    daily_notional_yuan: float | Decimal | None,
    *,
    pinned_flat_bps: Decimal | float | None = None,
) -> Decimal:
    """撮合/回测消费滑点腿的**唯一**解析入口（引擎侧零档位字面量）。

    优先级（唯一序，勿改、勿在任何消费方复制这段判断——复制即第二真源）：

      1. ``pinned_flat_bps is not None`` → 原样返回该固定口径。
         调用方（``MatchingConfig.slippage_bps``）显式覆写时用它做成本敏感性
         扫描/单笔对照；这是"人为钉住一个数"，不是标定值，故不参与分层。
      2. 开关关（``calibration_enabled() is False``）→ ``LEGACY_FLAT_SLIPPAGE_BPS``
         （1bp 旧一口价）。台账 #23 H2 的 A/B 取证复现位点：整条链逐位回到接线前。
      3. 逐笔「当日成交额」可得 → ``slippage_bps_for_notional()``（ADV 五分位分层）。
      4. 开关开但该笔无流动性信息 → ``slippage_bps_universal()``（3.79bp，全市场
         名义加权实证值）——宁取实证加权，不回退到无出处的 1bp。
    """
    if pinned_flat_bps is not None:
        try:
            pinned = Decimal(str(pinned_flat_bps))
        except (ArithmeticError, TypeError, ValueError) as exc:
            raise CostCalibrationError(
                f"pinned_flat_bps 必须可解析为 Decimal，实得 {pinned_flat_bps!r}（{exc}）"
            ) from exc
        if not pinned.is_finite() or pinned < 0:
            raise CostCalibrationError(f"pinned_flat_bps 必须是非负有限数（0=毛口径对照），实得 {pinned_flat_bps!r}")
        return pinned
    if not calibration_enabled():
        return LEGACY_FLAT_SLIPPAGE_BPS
    if daily_notional_yuan is not None:
        return slippage_bps_for_notional(float(daily_notional_yuan))
    return SLIPPAGE_BPS_UNIVERSAL


# ---------------------------------------------------------------------------
# 冲击腿：尺寸相关价格位移（Almgren-Chriss 参数档）
# ---------------------------------------------------------------------------

#: 参与率指数 β*（五层 log-log 斜率中位数；平方根律惯例 0.5，A-C 默认档 1.0）
IMPACT_BETA: Final[float] = 0.4205

#: 各层 η（临时冲击系数，与 IMPACT_TIER_SIGMA 同纲无量纲）
IMPACT_TIER_ETA: Final[tuple[float, ...]] = (
    0.9776,
    0.7295,
    0.5682,
    0.4793,
    0.3114,
)

#: 各层 σ（日收益率标准差，实证中位；A-C 公式的价格量纲由此带入）
IMPACT_TIER_SIGMA: Final[tuple[float, ...]] = (
    0.020428,
    0.023412,
    0.0275655,
    0.031818,
    0.03904,
)

#: 永久项占比 γ = ratio × η。**取 0 的裁定理由**：本层 η 由「静态五档走单的瞬时
#: 价格位移」直接标定，测得量已是 order 的全部成交位移；A-C 的 temp/perm 拆分
#: 需要时间轴（衰减/延续）才可辨识，静态快照分不出。若按惯例取 γ=0.5η 再让
#: 引擎 quote() 把 temp+perm 一起计入 cost_bps，等于把同一段位移计费两次。
#: 需要永久项的执行调度场景（decay_curve）另用显式注入，不走本默认档。
IMPACT_GAMMA_RATIO: Final[float] = 0.0

#: 永久冲击指数（A-C 默认档；γ=0 时不生效，保留以便执行调度侧显式启用）
IMPACT_PERMANENT_EXPONENT: Final[float] = 0.5

#: 引擎默认档参数（DEFAULT_PARAMS）的实证偏离倍数——披露用：η 相差 3~10 倍、
#: β 相差 2.4 倍，说明"永远消费默认档"不是保守而是错误。
DEFAULT_PARAMS_REF: Final[dict[str, float]] = {"eta": 0.1, "beta": 1.0, "gamma": 0.05, "sigma": 0.02}


@dataclass(frozen=True)
class CalibratedImpactLevel:
    """单层冲击档位（纯值；由 D_EXEC_SIM 转成 ImpactParams 消费）。"""

    tier: int
    eta: float
    beta: float
    gamma: float
    sigma: float
    permanent_exponent: float
    source: str

    def cost_ratio_at(self, participation: float) -> float:
        """参与率 p 的总冲击（价格相对位移比例，临时+永久）。"""
        if not 0.0 <= float(participation) <= 1.0:
            raise CostCalibrationError(f"参与率越界（须 ∈ [0,1]）: {participation!r}")
        p = float(participation)
        temp = self.eta * (p**self.beta) * self.sigma
        perm = self.gamma * (p**self.permanent_exponent) * self.sigma
        return temp + perm

    def cost_bps_at(self, participation: float) -> float:
        """参与率 p 的总冲击（bps）。"""
        return self.cost_ratio_at(participation) * 1e4

    def sqrt_law_coefficient(self, participation: float = 1e-3) -> float:
        """平方根律等价系数 Y=cost/(σ·√p)（业界基准交叉校验用）。"""
        p = float(participation)
        if p <= 0:
            raise CostCalibrationError(f"参考参与率须为正: {p!r}")
        return self.eta * (p ** (self.beta - 0.5))

    def to_dict(self) -> dict[str, object]:
        return {
            "tier": self.tier,
            "eta": self.eta,
            "beta": self.beta,
            "gamma": self.gamma,
            "sigma": self.sigma,
            "permanent_exponent": self.permanent_exponent,
            "source": self.source,
            "sqrt_law_Y@p=1e-3": self.sqrt_law_coefficient(1e-3),
        }


def impact_level_for_notional(daily_notional_yuan: float) -> CalibratedImpactLevel:
    """按流动性层取标定冲击档位（离线表档，source=offline_table）。"""
    tier = liquidity_tier(daily_notional_yuan)
    return impact_level_for_tier(tier)


def impact_level_for_tier(tier: int) -> CalibratedImpactLevel:
    """按层号取标定冲击档位。"""
    if isinstance(tier, bool) or not isinstance(tier, int):
        raise CostCalibrationError(f"tier 必须是整数: {tier!r}")
    if not 0 <= tier < n_tiers():
        raise CostCalibrationError(f"tier 越界: {tier}（合法 0..{n_tiers() - 1}）")
    return CalibratedImpactLevel(
        tier=tier,
        eta=IMPACT_TIER_ETA[tier],
        beta=IMPACT_BETA,
        gamma=IMPACT_GAMMA_RATIO * IMPACT_TIER_ETA[tier],
        sigma=IMPACT_TIER_SIGMA[tier],
        permanent_exponent=IMPACT_PERMANENT_EXPONENT,
        source=f"offline_table:{CALIBRATION_TABLE_VERSION}",
    )


# ---------------------------------------------------------------------------
# 地板佣金 → 最小下单规模（第一性推导，费率字面量由调用方注入）
# ---------------------------------------------------------------------------


def _as_positive_decimal(value: object, name: str) -> Decimal:
    """费率/下限注入的唯一闸门：不可解析 / 非有限（NaN、Inf）/ 非正一律抛错。

    为什么不能只写 ``<= 0``：``Decimal("NaN") <= 0`` 恒为 False，
    非法注入会穿过校验、把结果污染成 NaN 并静默进入成本口径（违沉默禁令）。
    """
    try:
        num = Decimal(str(value))
    except (ArithmeticError, TypeError, ValueError) as exc:
        raise CostCalibrationError(f"{name} 必须可解析为 Decimal，实得 {value!r}（{exc}）") from exc
    if not num.is_finite() or num <= 0:
        raise CostCalibrationError(f"{name} 必须是正有限数，实得 {value!r}")
    return num


def floor_drag_bps(notional_yuan: float, *, commission_rate: Decimal, min_commission: Decimal) -> float:
    """地板佣金造成的额外费率（bps）= max(五元, 比例佣金)/名义 ×1e4 − 名义费率×1e4。

    非顶地板时返回 0（无惩罚）。这是"碎片化下单"的直接代价口径。
    """
    if isinstance(notional_yuan, bool) or not isinstance(notional_yuan, (int, float, Decimal)):
        raise CostCalibrationError(f"下单名义必须是数值: {notional_yuan!r}")
    g = float(notional_yuan)
    if not math.isfinite(g) or g <= 0:
        raise CostCalibrationError(f"下单名义必须是正有限数: {notional_yuan!r}")
    rate = _as_positive_decimal(commission_rate, "commission_rate")
    floor = _as_positive_decimal(min_commission, "min_commission")
    proportional = Decimal(str(g)) * rate
    effective = proportional if proportional >= floor else floor
    return float(effective / Decimal(str(g)) * Decimal("10000") - rate * Decimal("10000"))


def notional_for_floor_drag_bps(drag_bps: float, *, commission_rate: Decimal, min_commission: Decimal) -> Decimal:
    """把"地板拖累不超过 drag_bps"翻译成最小下单名义（元）。

    闭式：min_notional = min_commission × 1e4 / (drag_bps + rate×1e4)。
    """
    try:
        d = float(drag_bps)
    except (TypeError, ValueError) as exc:
        raise CostCalibrationError(f"drag_bps 必须是数值，实得 {drag_bps!r}（{exc}）") from exc
    if not math.isfinite(d) or d <= 0:
        raise CostCalibrationError(f"drag_bps 须为正有限数: {drag_bps!r}")
    rate = _as_positive_decimal(commission_rate, "commission_rate")
    floor = _as_positive_decimal(min_commission, "min_commission")
    return (floor * Decimal("10000") / (Decimal(str(d)) + rate * Decimal("10000"))).quantize(Decimal("0.01"))


def commission_floor_nonbinding_notional(*, commission_rate: Decimal, min_commission: Decimal) -> Decimal:
    """佣金下限不再咬合的最小名义 = floor/rate（现结构 ≈ ¥58,548）。"""
    rate = _as_positive_decimal(commission_rate, "commission_rate")
    floor = _as_positive_decimal(min_commission, "min_commission")
    return (floor / rate).quantize(Decimal("0.01"))


__all__ = [
    "ADV_QUINTILE_BOUNDS_YUAN",
    "CALIBRATION_TABLE_VERSION",
    "CalibratedImpactLevel",
    "CalibrationProvenance",
    "CostCalibrationError",
    "DEFAULT_PARAMS_REF",
    "IMPACT_BETA",
    "IMPACT_GAMMA_RATIO",
    "IMPACT_PERMANENT_EXPONENT",
    "IMPACT_TIER_ETA",
    "IMPACT_TIER_SIGMA",
    "LEGACY_FLAT_SLIPPAGE_BPS",
    "PROVENANCE",
    "SLIPPAGE_BPS_UNIVERSAL",
    "SLIPPAGE_TIER_BPS",
    "SLIPPAGE_TIERING_ENABLED",
    "TIER_ADV_MEDIAN_YUAN",
    "TIER_NAMES",
    "TIER_TICK_BPS",
    "calibration_enabled",
    "commission_floor_nonbinding_notional",
    "floor_drag_bps",
    "impact_level_for_notional",
    "impact_level_for_tier",
    "liquidity_tier",
    "n_tiers",
    "notional_for_floor_drag_bps",
    "resolve_slippage_bps",
    "slippage_bps_for_notional",
    "slippage_bps_universal",
]
