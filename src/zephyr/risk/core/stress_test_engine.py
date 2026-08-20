# [BLUEPRINT] MOD-RK-12 | docs/03_modules/_domain_risk/stress_test_engine/blueprint.md
# [MODULE] zephyr.risk.core.stress_test_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; numpy; MOD-RK-05(VaR基准)
# [CONSUMERS] MOD-RK-03(Portfolio Risk Monitor,压力告警) ; MOD-RK-14(Black Swan Library,情景匹配)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 历史情景shock幅度固定不可改;反向压力测试二分搜索收敛;传染效应单调递增;压力损失=Σ(w_i·shock_i)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidStressTestInputError
# [TESTS] tests/risk/test_stress_test_engine.py
# [A_module] module_id=MOD-RK-12 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Stress Test Engine — 压力测试引擎 (MOD-RK-12)

D-RISK §1.2 分析引擎核心模块。压力测试四类场景:
    1. 历史情景 (HISTORICAL): 2008 金融危机 / 2015 股灾 / 2020 疫情, 预置 shock 不可改
    2. 假设情景 (HYPOTHETICAL): 用户自定义 shock 向量
    3. 反向压力测试 (REVERSE): 给定目标损失, 二分搜索找出致损情景
    4. 敏感性分析 (SENSITIVITY): 单因子在 shock 范围内的 PnL 变化曲线
    5. 传染效应 (CONTAGION): 冲击经相关性矩阵放大后的组合损失

数学:
    - 压力损失 = Σ w_i · shock_i  (shock_i 为负=下跌)
    - 传染放大: shocked_return = shock + Σ_j (ρ_ij · shock_j · contagion_factor)
    - 反向压力: 二分搜索 shock_scale 使 loss >= target_loss

属 A 类基础设施 (情景叠加 + 二分搜索, 逻辑明确), 历史情景幅度为 C 类不可改真源。
依据: D:\临时工作区\依赖图	-D-RISK-风控域.md §1.2 RK-12, §2 依赖(RK-05→RK-12)
SSoT: depgraph MOD-RK-12
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 组合权重与市值
#   fields: weights{symbol/sector: weight}非负自动归一化 + portfolio_value>0
#   code: run_historical() L265-267
# - id: I2
#   name: 历史情景库 HISTORICAL_SCENARIOS
#   fields: 2008金融危机/2015股灾/2020疫情三套8板块单日shock真源(负=下跌, 不可改)
#   code: HISTORICAL_SCENARIOS L93-134
# - id: I3
#   name: 自定义shock向量 字典
#   fields: shocks{symbol: shock_pct}负=下跌; 须覆盖全部持仓symbol
#   code: run_hypothetical() shocks L297
# - id: I4
#   name: 相关性矩阵与传染系数
#   fields: correlation_matrix(N,N)方阵 + assets行列对齐 + contagion_factor∈[0,1]
#   code: run_with_contagion() L447-449
# - id: I5
#   name: VaR基准 浮点数可选
#   fields: default_var_baseline(RK-05 VaR基准); 损失金额>基准则var_exceeded
#   code: __init__() L259-260
# 层: 算法
# - id: A1
#   name_zh: ① 情景应用与损失计算
#   name_en: _apply_scenario
#   intro: 权重归一后逐资产叠加shock, 算组合损失占比和金额
#   desc: loss_pct=Σw_i·shock_i; loss_value=loss_pct×portfolio_value; asset_losses逐资产; |loss_pct|×value>VaR基准→var_exceeded; loss≤-5%记severe(WARNING日志)
#   inputs: I1 I5
#   outputs: StressTestResult
#   invariant: 压力损失=Σ(w_i·shock_i)
# - id: A2
#   name_zh: ② 反向压力二分搜索
#   name_en: run_reverse
#   intro: 给定目标亏损, 二分搜索shock放大倍数找出致损情景
#   desc: base_shocks默认等权-1%; scale∈[0,max_scale=10]二分迭代50次使loss_pct≤target_loss_pct; 放大后构造REVERSE情景走_apply_scenario
#   inputs: I1 I3
#   outputs: 放大后的REVERSE情景结果
#   invariant: 反向压力测试二分搜索收敛
# - id: A3
#   name_zh: ③ 单因子敏感性分析
#   name_en: sensitivity_analysis
#   intro: 单因子在shock范围内等距采样, 看组合PnL影响曲线
#   desc: shock_levels=linspace(range,steps=21); impact=w_factor×shock×portfolio_value逐点计算
#   inputs: I1
#   outputs: SensitivityResult(shock水平-PnL影响序列)
# - id: A4
#   name_zh: ④ 传染效应放大
#   name_en: run_with_contagion
#   intro: 冲击经相关性矩阵放大后再叠加到组合
#   desc: contagion=corr@shock_vec×contagion_factor; shocked=shock+contagion; 转HYPOTHETICAL情景走_apply_scenario
#   inputs: I1 I3 I4
#   outputs: 传染放大后的情景结果
#   invariant: 传染效应单调递增
# 层: 输出
# - id: O1
#   name_zh: 压力测试结果
#   name_en: StressTestResult
#   intro: 单情景组合损失占比/金额/逐资产损失/是否超VaR基准/是否严重
#   invariant: 历史情景shock幅度固定不可改
#   downstream: Portfolio Risk Monitor MOD-RK-03(压力告警); Black Swan Library MOD-RK-14(情景匹配)
# - id: O2
#   name_zh: 敏感性分析结果
#   name_en: SensitivityResult
#   intro: 单因子shock_levels与pnl_impacts对应序列
#   downstream: Portfolio Risk Monitor MOD-RK-03
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I5 --> A1
# I2 --> A1
# I1 --> A2
# I3 --> A2
# I1 --> A3
# I1 --> A4
# I3 --> A4
# I4 --> A4
# A2 --> A1
# A4 --> A1
# A1 --> O1
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Final

import numpy as np

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "StressScenarioType",
    "StressScenario",
    "StressTestResult",
    "SensitivityResult",
    "StressTestEngine",
    "InvalidStressTestInputError",
    "HISTORICAL_SCENARIOS",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidStressTestInputError(ZephyrBaseError):
    """压力测试输入数据非法 (如权重不归一、shock 维度不匹配)。"""

    error_code = "ZA-RK-0012"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class StressScenarioType(Enum):
    """压力测试情景类型。"""

    HISTORICAL = "historical"  # 历史情景 (2008/2015/2020)
    HYPOTHETICAL = "hypothetical"  # 假设情景 (用户自定义)
    REVERSE = "reverse"  # 反向压力测试
    SENSITIVITY = "sensitivity"  # 敏感性分析


# ──────────────────────────────────────────────────────────────────────────────
# 历史情景真源 (不可改, C 类)
# ──────────────────────────────────────────────────────────────────────────────

HISTORICAL_SCENARIOS: dict[str, dict[str, float]] = {
    "2008_financial_crisis": {
        "description": "2008 全球金融危机 (雷曼破产, 系统性崩盘)",
        # 单日极端跌幅 shock (负=下跌), 按板块平均
        "shocks": {
            "financial": -0.095,  # 金融板块 -9.5%
            "real_estate": -0.082,  # 地产 -8.2%
            "industrial": -0.078,  # 工业 -7.8%
            "consumer": -0.065,  # 消费 -6.5%
            "tech": -0.072,  # 科技 -7.2%
            "energy": -0.085,  # 能源 -8.5%
            "healthcare": -0.052,  # 医疗 -5.2%
            "utilities": -0.045,  # 公用事业 -4.5%
        },
    },
    "2015_china_stock_crash": {
        "description": "2015 A股股灾 (去杠杆, 千股跌停)",
        "shocks": {
            "financial": -0.085,
            "real_estate": -0.090,
            "industrial": -0.092,
            "consumer": -0.088,
            "tech": -0.095,
            "energy": -0.078,
            "healthcare": -0.082,
            "utilities": -0.070,
        },
    },
    "2020_covid_crash": {
        "description": "2020 新冠疫情冲击 (全球熔断)",
        "shocks": {
            "financial": -0.068,
            "real_estate": -0.072,
            "industrial": -0.085,
            "consumer": -0.058,
            "tech": -0.045,  # 科技相对抗跌
            "energy": -0.112,  # 能源跌幅最深 (原油崩盘)
            "healthcare": -0.028,  # 医疗最抗跌
            "utilities": -0.038,
        },
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# 数据结构
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StressScenario:
    """压力测试情景定义。

    Attributes:
        name: 情景名称
        scenario_type: 情景类型
        shocks: {symbol/sector: shock_pct} (负=下跌)
        description: 情景描述
    """

    name: str
    scenario_type: StressScenarioType
    shocks: dict[str, float]
    description: str = ""

    @property
    def worst_shock(self) -> float:
        """最严重的 shock (最小值)。"""
        return min(self.shocks.values()) if self.shocks else 0.0


@dataclass(frozen=True)
class StressTestResult:
    """单情景压力测试结果。

    Attributes:
        scenario: 测试情景
        portfolio_loss_pct: 组合损失占比 (负=亏损)
        portfolio_loss_value: 组合损失金额
        asset_losses: {symbol: loss_value}
        var_exceeded: 是否超过 VaR 基准
        var_baseline: VaR 基准值 (None=未提供)
        timestamp: 测试时间
    """

    scenario: StressScenario
    portfolio_loss_pct: float
    portfolio_loss_value: float
    asset_losses: dict[str, float]
    timestamp: datetime
    var_exceeded: bool = False
    var_baseline: float | None = None

    @property
    def is_severe(self) -> bool:
        """是否为严重损失 (损失 >= 5%)。"""
        return self.portfolio_loss_pct <= -0.05

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_name": self.scenario.name,
            "scenario_type": self.scenario.scenario_type.value,
            "portfolio_loss_pct": self.portfolio_loss_pct,
            "portfolio_loss_value": self.portfolio_loss_value,
            "asset_losses": self.asset_losses,
            "var_exceeded": self.var_exceeded,
            "var_baseline": self.var_baseline,
            "is_severe": self.is_severe,
        }


@dataclass(frozen=True)
class SensitivityResult:
    """敏感性分析结果。

    Attributes:
        factor: 分析的因子/资产
        shock_levels: shock 水平序列
        pnl_impacts: 对应的组合 PnL 影响序列
        timestamp: 分析时间
    """

    factor: str
    shock_levels: list[float]
    pnl_impacts: list[float]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor": self.factor,
            "shock_levels": self.shock_levels,
            "pnl_impacts": self.pnl_impacts,
        }


# ──────────────────────────────────────────────────────────────────────────────
# 压力测试引擎
# ──────────────────────────────────────────────────────────────────────────────


class StressTestEngine:
    """压力测试引擎——历史/假设/反向/敏感性/传染。

    用法 (历史情景):
        engine = StressTestEngine()
        result = engine.run_historical(
            weights={"financial": 0.3, "tech": 0.7},
            portfolio_value=1_000_000,
            scenario_name="2008_financial_crisis",
        )

    用法 (假设情景):
        result = engine.run_hypothetical(
            weights={"600519": 0.5, "000001": 0.5},
            portfolio_value=1_000_000,
            shocks={"600519": -0.08, "000001": -0.05},
        )

    用法 (反向压力测试):
        scenarios = engine.run_reverse(
            weights={"financial": 0.3, "tech": 0.7},
            portfolio_value=1_000_000,
            target_loss_pct=-0.10,  # 找出致 10% 亏损的情景
        )
    """

    def __init__(self, default_var_baseline: float | None = None) -> None:
        self._default_var = default_var_baseline

    # ── 公开 API: 历史情景 ──

    def run_historical(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        scenario_name: str,
        now: datetime | None = None,
    ) -> StressTestResult:
        """运行历史情景压力测试 (2008/2015/2020)。

        Args:
            weights: {symbol/sector: weight}, 权重需归一化
            portfolio_value: 组合总价值
            scenario_name: HISTORICAL_SCENARIOS 中的键名
        """
        if scenario_name not in HISTORICAL_SCENARIOS:
            raise InvalidStressTestInputError(
                f"unknown historical scenario: {scenario_name}, available: {list(HISTORICAL_SCENARIOS.keys())}"
            )
        hist = HISTORICAL_SCENARIOS[scenario_name]
        scenario = StressScenario(
            name=scenario_name,
            scenario_type=StressScenarioType.HISTORICAL,
            shocks=hist["shocks"],
            description=hist["description"],
        )
        return self._apply_scenario(weights, portfolio_value, scenario, now)

    # ── 公开 API: 假设情景 ──

    def run_hypothetical(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        shocks: dict[str, float],
        name: str = "custom",
        now: datetime | None = None,
    ) -> StressTestResult:
        """运行用户自定义假设情景。

        Args:
            weights: {symbol: weight}
            portfolio_value: 组合总价值
            shocks: {symbol: shock_pct} (负=下跌)
            name: 情景名称
        """
        self._validate_weights_shocks(weights, shocks)
        scenario = StressScenario(
            name=name,
            scenario_type=StressScenarioType.HYPOTHETICAL,
            shocks=dict(shocks),
            description="用户自定义假设情景",
        )
        return self._apply_scenario(weights, portfolio_value, scenario, now)

    # ── 公开 API: 反向压力测试 ──

    def run_reverse(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        target_loss_pct: float,
        base_shocks: dict[str, float] | None = None,
        max_scale: float = 10.0,
        iterations: int = 50,
        now: datetime | None = None,
    ) -> StressTestResult:
        """反向压力测试——二分搜索找出致 target_loss 的 shock_scale。

        给定一组 base_shocks, 找出放大倍数 scale 使组合损失达到 target_loss_pct。

        Args:
            weights: {symbol: weight}
            portfolio_value: 组合总价值
            target_loss_pct: 目标损失占比 (负数, 如 -0.10)
            base_shocks: 基准 shock 向量 (None=用等权 -1%)
            max_scale: 最大放大倍数
            iterations: 二分搜索迭代次数

        Returns:
            StressTestResult (scenario_type=REVERSE, shocks 已放大)
        """
        if target_loss_pct >= 0:
            raise InvalidStressTestInputError(f"target_loss_pct must be negative, got {target_loss_pct}")
        if max_scale <= 1.0:
            raise InvalidStressTestInputError(f"max_scale must be >1.0, got {max_scale}")

        weights_norm = self._normalize_weights(weights)
        if base_shocks is None:
            base_shocks = {s: -0.01 for s in weights_norm}
        self._validate_weights_shocks(weights_norm, base_shocks)

        # 二分搜索: 找 scale 使 loss <= target_loss (loss 为负)
        lo, hi = 0.0, max_scale
        best_scale = hi
        for _ in range(iterations):
            mid = (lo + hi) / 2
            scaled = {s: v * mid for s, v in base_shocks.items()}
            loss_pct = sum(weights_norm[s] * scaled.get(s, 0.0) for s in weights_norm)
            if loss_pct <= target_loss_pct:
                best_scale = mid
                hi = mid
            else:
                lo = mid

        scaled_shocks = {s: v * best_scale for s, v in base_shocks.items()}
        scenario = StressScenario(
            name=f"reverse_scale_{best_scale:.2f}x",
            scenario_type=StressScenarioType.REVERSE,
            shocks=scaled_shocks,
            description=f"反向压力测试: 放大 {best_scale:.2f}x 达到目标损失 {target_loss_pct:.2%}",
        )
        result = self._apply_scenario(weights_norm, portfolio_value, scenario, now)
        logger.info(
            "Reverse stress test: target=%.2f%% achieved=%.2f%% scale=%.2fx",
            target_loss_pct * 100,
            result.portfolio_loss_pct * 100,
            best_scale,
        )
        return result

    # ── 公开 API: 敏感性分析 ──

    def sensitivity_analysis(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        factor: str,
        shock_range: tuple[float, float] = (-0.10, 0.10),
        steps: int = 21,
        now: datetime | None = None,
    ) -> SensitivityResult:
        """单因子敏感性分析——在 shock 范围内计算组合 PnL 影响。

        Args:
            weights: {symbol: weight}
            portfolio_value: 组合总价值
            factor: 分析的因子/资产名 (须在 weights 中)
            shock_range: (min_shock, max_shock)
            steps: 采样点数
        """
        weights_norm = self._normalize_weights(weights)
        if factor not in weights_norm:
            raise InvalidStressTestInputError(f"factor '{factor}' not in weights: {list(weights_norm.keys())}")
        if shock_range[0] >= shock_range[1]:
            raise InvalidStressTestInputError(f"shock_range must be increasing, got {shock_range}")
        if steps < 2:
            raise InvalidStressTestInputError(f"steps must be >=2, got {steps}")

        now = now or datetime.now(timezone.utc)
        shock_levels = np.linspace(shock_range[0], shock_range[1], steps).tolist()
        pnl_impacts = []
        for shock in shock_levels:
            # 单因子 shock 对组合 PnL 的影响 = weight_factor * shock * portfolio_value
            impact = weights_norm[factor] * shock * portfolio_value
            pnl_impacts.append(impact)

        return SensitivityResult(
            factor=factor,
            shock_levels=shock_levels,
            pnl_impacts=pnl_impacts,
            timestamp=now,
        )

    # ── 公开 API: 传染效应 ──

    def run_with_contagion(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        shocks: dict[str, float],
        correlation_matrix: np.ndarray,
        assets: list[str],
        contagion_factor: float = 0.5,
        now: datetime | None = None,
    ) -> StressTestResult:
        """带传染效应的压力测试——冲击经相关性矩阵放大。

        shocked_return_i = shock_i + Σ_j (ρ_ij · shock_j · contagion_factor)

        Args:
            weights: {symbol: weight}
            portfolio_value: 组合总价值
            shocks: {symbol: shock_pct}
            correlation_matrix: 相关性矩阵 (N, N)
            assets: 资产列表 (与矩阵行列对齐)
            contagion_factor: 传染放大系数 (0=无传染, 1=全传染)
        """
        weights_norm = self._normalize_weights(weights)
        self._validate_weights_shocks(weights_norm, shocks)
        corr = np.asarray(correlation_matrix, dtype=float)
        if corr.ndim != 2 or corr.shape[0] != corr.shape[1]:
            raise InvalidStressTestInputError(f"correlation_matrix must be square 2D, got {corr.shape}")
        if len(assets) != corr.shape[0]:
            raise InvalidStressTestInputError(f"assets count {len(assets)} != matrix dim {corr.shape[0]}")
        if not 0 <= contagion_factor <= 1:
            raise InvalidStressTestInputError(f"contagion_factor must be in [0,1], got {contagion_factor}")

        # 原始 shock 向量
        shock_vec = np.array([shocks.get(a, 0.0) for a in assets])
        # 传染放大: shocked = shock + corr @ shock * factor
        contagion = corr @ shock_vec * contagion_factor
        shocked_vec = shock_vec + contagion
        shocked_dict = {a: float(shocked_vec[i]) for i, a in enumerate(assets)}

        scenario = StressScenario(
            name="contagion",
            scenario_type=StressScenarioType.HYPOTHETICAL,
            shocks=shocked_dict,
            description=f"带传染效应 (factor={contagion_factor}) 的假设情景",
        )
        return self._apply_scenario(weights_norm, portfolio_value, scenario, now)

    # ── 公开 API: 批量历史情景 ──

    def run_all_historical(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        now: datetime | None = None,
    ) -> list[StressTestResult]:
        """运行全部历史情景 (2008/2015/2020)。"""
        return [self.run_historical(weights, portfolio_value, name, now) for name in HISTORICAL_SCENARIOS]

    # ── 内部: 应用情景 ──

    def _apply_scenario(
        self,
        weights: dict[str, float],
        portfolio_value: float,
        scenario: StressScenario,
        now: datetime | None,
    ) -> StressTestResult:
        """计算情景对组合的影响。"""
        now = now or datetime.now(timezone.utc)
        weights_norm = self._normalize_weights(weights)

        if portfolio_value <= 0:
            raise InvalidStressTestInputError(f"portfolio_value must be positive, got {portfolio_value}")

        asset_losses: dict[str, float] = {}
        total_loss_pct = 0.0
        for symbol, w in weights_norm.items():
            shock = scenario.shocks.get(symbol, 0.0)
            loss_value = w * shock * portfolio_value
            asset_losses[symbol] = loss_value
            total_loss_pct += w * shock

        var_baseline = self._default_var
        var_exceeded = var_baseline is not None and abs(total_loss_pct) * portfolio_value > var_baseline

        result = StressTestResult(
            scenario=scenario,
            portfolio_loss_pct=total_loss_pct,
            portfolio_loss_value=total_loss_pct * portfolio_value,
            asset_losses=asset_losses,
            timestamp=now,
            var_exceeded=var_exceeded,
            var_baseline=var_baseline,
        )

        if result.is_severe:
            logger.warning(
                "Severe stress loss: scenario=%s loss=%.2f%%",
                scenario.name,
                total_loss_pct * 100,
            )

        return result

    # ── 内部: 校验 ──

    @staticmethod
    def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
        if not weights:
            raise InvalidStressTestInputError("weights must be non-empty")
        total = sum(weights.values())
        if total <= 0:
            raise InvalidStressTestInputError(f"weights sum must be positive, got {total}")
        if any(w < 0 for w in weights.values()):
            raise InvalidStressTestInputError(f"negative weights not allowed: {weights}")
        return {s: w / total for s, w in weights.items()}

    @staticmethod
    def _validate_weights_shocks(weights: dict[str, float], shocks: dict[str, float]) -> None:
        if not shocks:
            raise InvalidStressTestInputError("shocks must be non-empty")
        missing = set(weights) - set(shocks)
        if missing:
            raise InvalidStressTestInputError(f"shocks missing for symbols: {missing}")
