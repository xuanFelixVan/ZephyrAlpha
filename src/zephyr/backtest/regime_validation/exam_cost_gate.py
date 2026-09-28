# [BLUEPRINT] MOD-BT-IBT-COSTGATE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.exam_cost_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] numpy; pandas
# [CONSUMERS] scripts/backtest/f06_e4_wfa_exam.py（E4 正考档位扫描+换手门）；scripts/backtest/exam_cost_reexam.py（存活池重过成本门/批D 新鲜窗）；批F 三路搜索轨（F06Grid/E1C/LLM）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 纯函数零 IO 零重跑：净值档位序列由调用方注入（_c4_engine.daily_net_returns slippage_bp 档覆盖），本件只做判定；五档单调性=逐档 sharpe 非增（容差 tol）；全成本档存活=最高档 sharpe>=survival_floor；E7 换手上限门=年化单边换手<=cap（预注册默认 8x/年，Owner 通宵令批C 预注册档冻结后禁改）；规模调整存活门（裁-4 item5 2026-09-28）=participation_rate 显式传入时有效档 tiers[-1]×开方律乘数判 survival_floor（缺省 None=规模维禁用行为零变化，40bp 锚=ref 处 m=1 判定逐字一致）；fail-closed：证据缺失（档位<3/天数<min_days）判不通过非跳过，participation 非正=ValueError；裁定#325 口径：出证禁"全绿"，逐条如实判档；扫描/判定两面分离（2026-09-24 方案①）：run_cost_tier_scan tiers_bp 子集覆盖仅供 T1 轻档粗筛扫描（validate_scan_tiers 两档合法），三门判定仍恒全档证据（<3 档 fail-closed 不通过）；nets_by_tier 预算档注入（st-ddup-20260925）：缺省 None=逐档 net_fn 行为零变化，注入缺档=ValueError fail-closed
# [MODIFY-GUARD] tests/backtest/test_exam_cost_gate.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(配置非法：档位不含0/未升序/cap<=0/规模锚非正/规模律指数出界/乘数上限<1；participation 非正)；判定函数不抛异常（证据缺失=fail-closed 不通过）
# [TESTS] tests/backtest/test_exam_cost_gate.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-IBT-COSTGATE | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""E4 考尺成本门（批C 成本焊进考尺，Max 整改方案 §2-C；MOD-BT-IBT-COSTGATE）。

三门+可选规模维（预注册默认档冻结后禁改，参数面见 config/exam_scale_cost_gate.yaml）:
  1. 档位单调性: 五档滑点(0/5/10/20/40bp，冻结土规口径)下 sharpe 逐档非增
     （成本越高收益越低的市场常识=无前视套利的必要条件，首跑敏感性框架同款）;
  2. 全成本档存活: 最高档(40bp) sharpe >= survival_floor(预注册 0.0)——
     纸面亮实盘死的勤快策略在此现形;
  3. E7 换手上限门: 年化单边换手 <= turnover_cap_annual_x（预注册 8x/年，
     推导: 38.6pct/4.75 年 ÷39x ≈ 0.21pct/换手·年，8x→成本拖累 ≈1.7pct/年，
     OOS 零成本超额 +18pct 保留一半即过 C 门线）;
  4. 规模调整存活（裁-4 item5 2026-09-28，可选）: 调用方注入格点自身参与率
     （成交额/ADV）时，有效档=tiers[-1]×开方律乘数（(participation/5%ADV)^0.5，
     单边只罚不奖，上限 2×），档位曲线在该有效档取值判 survival_floor——
     旧门对成交规模恒盲（40bp 锚任何规模一刀切）=验收门恒过橡皮图章，本轮可 fail。
     participation<=锚 时 m=1，判定与缺省逐字一致=40bp 锚语义不动。

照妖镜语义: 4440（超短频繁交易）必须被本门拦截；E4 存活池重过产"成本合格名单"。
裁定#325 口径: 判定结果逐条如实（PASS/FAIL+数字证据），禁"全绿"表述。
# [ALGO_FLOW] external: docs/03_modules/_domain_backtest/algo_flow/exam_cost_gate.yaml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

import numpy as np
import pandas as pd

#: 预注册默认档（Owner 通宵令批C；冻结后禁改，调整=裁定通道）
DEFAULT_COST_TIERS_BP: tuple[float, ...] = (0.0, 5.0, 10.0, 20.0, 40.0)
DEFAULT_SURVIVAL_FLOOR: float = 0.0
DEFAULT_TURNOVER_CAP_ANNUAL_X: float = 8.0
DEFAULT_TURNOVER_DAYS_BASIS: int = 244
DEFAULT_MONOTONIC_TOL: float = 1e-9
#: 换手/单调性证据的最低样本天数（低于此 fail-closed 判不通过）
DEFAULT_MIN_DAYS: int = 60
#: 规模维（裁-4 item5 2026-09-28：成本档不带规模参数=验收门恒过/橡皮图章）——
#: 档位 bp 视为在参与率锚 scale_participation_ref 处校准（5% ADV 机构级分界）；
#: 开方律冲击模型（square_root，cost_model_registry impact_model 枚举既有，见 CST-ASTOCK-002）：
#: m=(participation/ref)^exponent，单边只罚不奖（participation<=ref 时 m=1，保 40bp 锚语义）；
#: 上限 cap 防测量档外无限外推（40bp 锚最深 2×=80bp 有效档）。
DEFAULT_SCALE_PARTICIPATION_REF: float = 0.05
DEFAULT_SCALE_EXPONENT: float = 0.5
DEFAULT_SCALE_MULTIPLIER_CAP: float = 2.0

__all__: Final = [
    "CostGateConfig",
    "CostGateVerdict",
    "validate_scan_tiers",
    "run_cost_tier_scan",
    "evaluate_exam_cost_gate",
    "cost_scale_multiplier",
]


@dataclass(frozen=True)
class CostGateConfig:
    """考尺成本门预注册参数（不可变；YAML 载入后构造）。"""

    tiers_bp: tuple[float, ...] = DEFAULT_COST_TIERS_BP
    survival_floor: float = DEFAULT_SURVIVAL_FLOOR
    turnover_cap_annual_x: float = DEFAULT_TURNOVER_CAP_ANNUAL_X
    turnover_days_basis: int = DEFAULT_TURNOVER_DAYS_BASIS
    monotonic_tol: float = DEFAULT_MONOTONIC_TOL
    min_days: int = DEFAULT_MIN_DAYS
    #: 规模维三参（预注册，config/exam_scale_cost_gate.yaml scale_gate 同源；冻结后禁改）
    scale_participation_ref: float = DEFAULT_SCALE_PARTICIPATION_REF
    scale_exponent: float = DEFAULT_SCALE_EXPONENT
    scale_multiplier_cap: float = DEFAULT_SCALE_MULTIPLIER_CAP

    def __post_init__(self) -> None:
        tiers = tuple(float(t) for t in self.tiers_bp)
        if len(tiers) < 3:
            raise ValueError(f"档位数 {len(tiers)} < 3，单调性证据不足（fail-closed 设计）")
        if any(tiers[i + 1] <= tiers[i] for i in range(len(tiers) - 1)):
            raise ValueError(f"档位必须严格升序: {tiers}")
        if tiers[0] != 0.0:
            raise ValueError(f"首档必须为 0bp（零成本对照）: {tiers}")
        if float(self.turnover_cap_annual_x) <= 0:
            raise ValueError(f"换手上限必须为正: {self.turnover_cap_annual_x}")
        if not float(self.scale_participation_ref) > 0:
            raise ValueError(f"规模锚参与率必须为正: {self.scale_participation_ref}")
        if not 0 < float(self.scale_exponent) <= 1:
            raise ValueError(f"规模律指数须在 (0,1]: {self.scale_exponent}")
        if float(self.scale_multiplier_cap) < 1.0:
            raise ValueError(f"规模乘数上限须 >=1: {self.scale_multiplier_cap}")


@dataclass(frozen=True)
class CostGateVerdict:
    """成本门判定——不可变，逐条带数字证据（裁定#325 口径禁"全绿"表述）。"""

    passed: bool
    monotonic: bool
    full_cost_survived: bool
    turnover_within_cap: bool
    annual_turnover_x: float
    tier_sharpes: dict[float, float] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    #: 规模维证据（裁-4 item5）：None=未启用（participation_rate 缺省，行为零变化）
    scale_adjusted_survived: bool | None = None
    scale_multiplier: float | None = None
    effective_top_bp: float | None = None


def _sharpe(net: pd.Series) -> float:
    std = float(net.std())
    return float(net.mean() / std * np.sqrt(244)) if std > 0 else 0.0


def cost_scale_multiplier(participation_rate: float, config: CostGateConfig | None = None) -> float:
    """规模乘数（裁-4 item5，开方律单边只罚不奖）: m=(participation/ref)^exponent, [1, cap]。

    participation<=ref（≤校准锚规模）→ m=1.0：40bp 锚语义原样（档位 bp 按冻结口径适用）；
    participation>ref → m>1：测量档曲线按末段斜率外推至 tiers[-1]×m 有效档判存活。
    participation 非正（含 NaN）=ValueError fail-closed。
    """
    cfg = config or CostGateConfig()
    p = float(participation_rate)
    if not p > 0:  # 覆盖 0/负数/NaN（NaN 比较恒 False）
        raise ValueError(f"参与率必须为正数: {participation_rate!r}")
    if p <= cfg.scale_participation_ref:
        return 1.0
    m = (p / cfg.scale_participation_ref) ** cfg.scale_exponent
    return float(min(m, cfg.scale_multiplier_cap))


def _sharpe_at_effective_bp(tiers: list[float], sharpes: list[float], bp: float) -> float:
    """档位曲线在 bp 处取值：测量档内线性插值；越过最高测量档按末段斜率线性外推。

    外推即规模门的"能fail"机制：策略在 40bp 锚勉强存活（末段斜率向下）时，
    规模上调的有效档（>40bp）把 sharpe 推穿 survival_floor——旧门对此恒盲。
    """
    if bp <= tiers[0]:
        return sharpes[0]
    if bp <= tiers[-1]:
        return float(np.interp(bp, tiers, sharpes))
    slope = (sharpes[-1] - sharpes[-2]) / (tiers[-1] - tiers[-2])
    return float(sharpes[-1] + slope * (bp - tiers[-1]))


def validate_scan_tiers(tiers_bp) -> tuple[float, ...]:
    """扫描档位集校验（扫描面，非判定面）: 非空、严格升序、首档=0bp 零成本对照。

    与 CostGateConfig 的判定不变量（≥3 档）分离：方案①两轮制 T1 轻档两档 [0,5]
    只做粗筛扫描，不做三门判定（终审仍在 T2 全档 evaluate_exam_cost_gate）。
    非法=ValueError（调用方 decide 去向；执行器预算闸侧转 SystemExit fail-closed）。
    """
    try:
        tiers = tuple(float(t) for t in tiers_bp)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"档位集非法（须为数值序列）: {tiers_bp!r}") from exc
    if not tiers:
        raise ValueError("档位集为空——零成本对照档缺失（fail-closed）")
    if any(tiers[i + 1] <= tiers[i] for i in range(len(tiers) - 1)):
        raise ValueError(f"档位必须严格升序: {tiers}")
    if tiers[0] != 0.0:
        raise ValueError(f"首档必须为 0bp（零成本对照）: {tiers}")
    return tiers


def run_cost_tier_scan(
    weights: pd.DataFrame,
    px_close: pd.DataFrame,
    net_fn,
    config: CostGateConfig | None = None,
    *,
    tiers_bp=None,
    nets_by_tier=None,
) -> dict[str, float]:
    """档位滑点净值扫描（引擎口径唯一性由 net_fn 保证，本件零重实现）。

    Args:
        weights/px_close: 与引擎同构的权重/收盘价宽表。
        net_fn: callable(weights, px_close, *, slippage_bp) -> pd.Series——**必须以关键字传**
            滑点档。引擎真身签名是 (weights, px_close, gate_limits=True, slippage_bp=None)
            （scripts/backtest/translated/_c4_engine.py），位置传参会把 bp 绑进 gate_limits：
            五档 Sharpe 逐位相同=门形同虚设，且 0bp 档顺带关掉涨跌停可成交闸
            （gate_limits 收到假值 0.0）。2026-09-23 st-e2e-20260924 实测复现：
            位置传参 {0,5,10,20,40}bp→Sharpe 恒 10.6211；显式 kwargs→11.63/10.62/9.56/7.45/3.83。
            传 _c4_engine.daily_net_returns 即冻结土规口径档位覆盖。
        config: 档位等参数。
        tiers_bp: 档位子集覆盖（方案①两轮制 2026-09-24，裁定#413 下一窗口升级案）——
            None=用 config 档位（缺省，全档，行为零变化）；否则须过 validate_scan_tiers
            （T1 轻档两档合法）。档位子集只影响扫描面；三门判定仍以 config 全档证据计。
        nets_by_tier: 预算档净值注入（st-ddup-20260925 去重改造①，与本件"净值档位序列
            由调用方注入"不变量同构）——None（缺省）=现行路径逐档调 net_fn（行为零变化）；
            传入 {float(bp): net} 时跳过 net_fn，逐档 sharpe 只对注入序列计（引擎侧
            net_returns_by_tiers 一趟派生，与逐档 daily_net_returns 逐位一致）。
            缺档=ValueError（fail-closed，禁静默跳档）。

    Returns:
        {slippage_bp: sharpe}（含 0bp 零成本对照档）。
    """
    cfg = config or CostGateConfig()
    tiers = validate_scan_tiers(cfg.tiers_bp if tiers_bp is None else tiers_bp)
    if nets_by_tier is None:
        return {float(bp): round(_sharpe(net_fn(weights, px_close, slippage_bp=bp)), 4) for bp in tiers}
    missing = [bp for bp in tiers if float(bp) not in nets_by_tier]
    if missing:
        raise ValueError(f"nets_by_tier 缺档: {missing}（fail-closed，禁静默跳档）")
    return {float(bp): round(_sharpe(nets_by_tier[float(bp)]), 4) for bp in tiers}


def evaluate_exam_cost_gate(
    tier_sharpes: dict[float, float],
    mean_daily_turnover_1side: float,
    days: int,
    config: CostGateConfig | None = None,
    *,
    participation_rate: float | None = None,
) -> CostGateVerdict:
    """三门判定+可选规模维（裁-4 item5），fail-closed。

    Args:
        tier_sharpes: run_cost_tier_scan 产出 {slippage_bp: sharpe}。
        mean_daily_turnover_1side: 冻结土规口径日均单边换手
            （_c4_engine run_backtest 输出 avg_turnover_1side 同源）。
        days: 样本交易日数（< min_days 判不通过——证据不足非跳过）。
        config: 预注册参数。
        participation_rate: 格点自身规模（成交额/ADV 参与率）——None（缺省）=规模维
            禁用=行为零变化（三门判定原样）；传入时新增门4"规模调整存活"：以
            tiers[-1]×cost_scale_multiplier 为有效档取档位曲线值判 survival_floor，
            规模把成本推穿地板即拦截（旧门对成交规模恒盲=橡皮图章，本轮可fail）。
            40bp 锚语义不动：锚=校准参与率 ref 处 m=1，判定与缺省逐字一致。
    """
    cfg = config or CostGateConfig()
    tiers = sorted(float(k) for k in tier_sharpes)
    sharpes = [float(tier_sharpes[k]) for k in tiers]
    reasons: list[str] = []

    # 证据充分性（fail-closed：缺证据=不通过，非跳过）
    if len(tiers) != len(cfg.tiers_bp) or days < cfg.min_days:
        reasons.append(f"证据不足(fail-closed): 档位数={len(tiers)}/{len(cfg.tiers_bp)}, 天数={days}<{cfg.min_days}")
        return CostGateVerdict(
            passed=False,
            monotonic=False,
            full_cost_survived=False,
            turnover_within_cap=False,
            annual_turnover_x=float("nan"),
            tier_sharpes=dict(tier_sharpes),
            reasons=tuple(reasons),
        )

    # 门1: 五档单调性（成本升 sharpe 非增，容差 tol）
    monotonic = all(sharpes[i] >= sharpes[i + 1] - cfg.monotonic_tol for i in range(len(sharpes) - 1))
    if not monotonic:
        reasons.append(f"档位单调性破缺: {[round(s, 3) for s in sharpes]} @ {tiers}bp——成本升收益反升=口径或前视嫌疑")

    # 门2: 全成本档存活
    full_sharpe = sharpes[-1]
    full_cost_survived = full_sharpe >= cfg.survival_floor
    if not full_cost_survived:
        reasons.append(
            f"全成本档({tiers[-1]:g}bp) sharpe={full_sharpe:.3f} < 存活地板 {cfg.survival_floor:.2f}——纸面亮实盘死"
        )

    # 门3: E7 换手上限门（年化单边换手 = 日均单边换手 × 年交易日基准）
    annual_turnover_x = float(mean_daily_turnover_1side) * cfg.turnover_days_basis
    turnover_within_cap = annual_turnover_x <= cfg.turnover_cap_annual_x
    if not turnover_within_cap:
        reasons.append(
            f"E7 换手门: 年化单边换手 {annual_turnover_x:.1f}x > 上限 {cfg.turnover_cap_annual_x:g}x"
            f"（日均 {mean_daily_turnover_1side:.4f} × {cfg.turnover_days_basis}）——成本拖累超预注册预算"
        )

    # 门4: 规模调整存活（裁-4 item5 2026-09-28）——仅 participation_rate 显式传入时启用
    scale_adjusted_survived: bool | None = None
    scale_multiplier: float | None = None
    effective_top_bp: float | None = None
    if participation_rate is not None:
        scale_multiplier = cost_scale_multiplier(participation_rate, cfg)
        effective_top_bp = tiers[-1] * scale_multiplier
        scaled_sharpe = _sharpe_at_effective_bp(tiers, sharpes, effective_top_bp)
        scale_adjusted_survived = scaled_sharpe >= cfg.survival_floor
        if not scale_adjusted_survived:
            reasons.append(
                f"规模存活门: 参与率 {float(participation_rate):.2%} → 乘数 {scale_multiplier:.2f}，"
                f"有效档 {effective_top_bp:g}bp 处 sharpe={scaled_sharpe:.3f} < 存活地板 "
                f"{cfg.survival_floor:.2f}——旧门按 40bp 锚判存活但该格点规模下成本已穿地板（开方律）"
            )

    passed = monotonic and full_cost_survived and turnover_within_cap and (scale_adjusted_survived is not False)
    if passed:
        scale_note = (
            f"，规模维 参与率 {float(participation_rate):.2%}×乘数 {scale_multiplier:.2f}→有效档 "
            f"{effective_top_bp:g}bp 存活(sharpe={_sharpe_at_effective_bp(tiers, sharpes, effective_top_bp):.3f})"
            if participation_rate is not None
            else ""
        )
        reasons.append(
            f"成本门通过: 档位 sharpe {[round(s, 3) for s in sharpes]} 单调且全成本档存活"
            f"（{tiers[-1]:g}bp={full_sharpe:.3f}），年化换手 {annual_turnover_x:.1f}x<={cfg.turnover_cap_annual_x:g}x"
            f"{scale_note}"
        )
    return CostGateVerdict(
        passed=passed,
        monotonic=monotonic,
        full_cost_survived=full_cost_survived,
        turnover_within_cap=turnover_within_cap,
        annual_turnover_x=annual_turnover_x,
        tier_sharpes=dict(tier_sharpes),
        reasons=tuple(reasons),
        scale_adjusted_survived=scale_adjusted_survived,
        scale_multiplier=scale_multiplier,
        effective_top_bp=effective_top_bp,
    )
