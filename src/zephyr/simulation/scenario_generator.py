# [BLUEPRINT] MOD-SIM-005 | docs/03_modules/_domain_simulation/scenario_generator/blueprint.md
# [MODULE] zephyr.simulation.scenario_generator
# [DOMAIN] D_SIMULATION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-SIM-002(strategy_simulator) ; SIM-01/SIM-04/SIM-06
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 全frozen不可变; 同seed可复现; 历史场景不修改源数据; 纯numpy/pandas
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ScenarioGenerationError(ZA-SIM-0005)
# [TESTS] tests/simulation/test_scenario_generator.py
# [A_module] module_id=MOD-SIM-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_SIMULATION — Scenario Generator (场景生成器)

生成 what-if 市场场景(SimulationScenario), 供 SIM-01/02/04/06 消费。
三种模式: 蒙特卡洛(GBM) / 历史场景(切片) / 自定义场景(冲击叠加)。
是仿真流水线起点(场景→市场→策略)。

属 A 类基础设施(确定性生成), 阈值为 C 类可调参数。纯 numpy/pandas, 不依赖外部数据库。
核心 Aggregate: SimulationScenario。核心事件: E-SIM-02 ScenarioGenerated。

设计真源: D-SIMULATION-05 "场景生成器+蒙特卡洛+历史场景+自定义场景 | Monte Carlo"
蓝图: docs/03_modules/_domain_simulation/scenario_generator/blueprint.md
SSoT: depgraph MOD-SIM-005

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 蒙特卡洛参数 MonteCarloParams
#   fields: 起始价/n_bars + 年化漂移率drift + 年化波动率volatility + 时间步dt=1/252 + seed=42 + symbol
#   code: MonteCarloParams L89
# - id: I2
#   name: 历史场景参数 HistoricalParams
#   fields: 真实OHLCV源数据source_data(DataFrame需含open/high/low/close/volume) + start_idx + n_bars(0=到末尾)
#   code: HistoricalParams L123
# - id: I3
#   name: 自定义场景参数 CustomParams
#   fields: 起始价/n_bars + 冲击序列shocks[(bar_idx,pct)] + 每期线性趋势trend + seed=42
#   code: CustomParams L158
# - id: I4
#   name: 生成器配置 ScenarioGeneratorConfig
#   fields: 默认seed=42 + 默认成交量10000
#   code: ScenarioGeneratorConfig L190
# 层: 算法
# - id: A1
#   name_zh: ① 蒙特卡洛GBM路径生成
#   name_en: generate_monte_carlo
#   intro: 用几何布朗运动生成随机价格路径（同seed可复现）
#   desc: Z~N(0,1) → log_ret=(drift-0.5vol²)dt+vol√dt·Z → S_t=S_{t-1}·exp(log_ret)逐bar复利 → close序列
#   inputs: I1 A4
#   outputs: 蒙特卡洛场景（含参数快照）
#   invariant: 同seed可复现
# - id: A2
#   name_zh: ② 历史场景切片
#   name_en: generate_historical
#   intro: 从真实历史数据切一段封装成可重放场景
#   desc: iloc[start_idx:end].copy()切片 → 重建RangeIndex(0..n) → 封装（不修改源数据）
#   inputs: I2
#   outputs: 历史场景
#   invariant: 历史场景不修改源数据
# - id: A3
#   name_zh: ③ 自定义冲击场景生成
#   name_en: generate_custom
#   intro: 基础随机游走+线性趋势+指定bar叠加百分比冲击的确定性what-if场景
#   desc: noise=0.1%随机游走 → ret=trend+noise+shock_map[i]（命中冲击bar叠加pct） → price×=(1+ret)逐bar → close序列
#   inputs: I3 A4
#   outputs: 自定义场景（含参数快照）
# - id: A4
#   name_zh: ④ OHLCV数据框构建
#   name_en: _build_ohlcv
#   intro: 把close序列包装成OHLCV五列DataFrame
#   desc: open=前收(close滚动1位) → high=max(open,close)×1.001 → low=min(open,close)×0.999 → volume=常数10000
#   inputs: I4
#   outputs: OHLCV market_data
# - id: A5
#   name_zh: ⑤ 场景类型分发
#   name_en: generate
#   intro: 按ScenarioType把参数对象分发到对应生成方法
#   desc: MONTE_CARLO→A1 / HISTORICAL→A2 / CUSTOM→A3；参数类型不匹配抛ScenarioGenerationError(ZA-SIM-0005)
#   inputs: I1 I2 I3
#   outputs: 分发到A1/A2/A3
# 层: 输出
# - id: O1
#   name_zh: 仿真场景 SimulationScenario
#   name_en: SimulationScenario
#   intro: 封装生成的OHLCV市场数据+元数据+参数快照的不可变Aggregate（仿真流水线起点）
#   invariant: 全frozen不可变；params快照可精确复现
#   downstream: MOD-SIM-002(strategy_simulator) ; SIM-01/SIM-04/SIM-06（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A5
# I2 --> A5
# I3 --> A5
# A5 --> A1
# A5 --> A2
# A5 --> A3
# I1 --> A1
# I3 --> A3
# I4 --> A4
# A1 --> A4
# A3 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "ScenarioType",
    "MonteCarloParams",
    "HistoricalParams",
    "CustomParams",
    "ScenarioGeneratorConfig",
    "SimulationScenario",
    "ScenarioGenerator",
    "ScenarioGenerationError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class ScenarioGenerationError(ZephyrBaseError):
    """场景生成参数非法(n_bars<=0/start_price<=0/越界/源数据缺列)。"""

    error_code = "ZA-SIM-0005"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class ScenarioType(str, Enum):
    """场景类型。"""

    MONTE_CARLO = "monte_carlo"
    HISTORICAL = "historical"
    CUSTOM = "custom"


# ──────────────────────────────────────────────────────────────────────────────
# 生成参数 (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class MonteCarloParams:
    """蒙特卡洛场景参数——GBM 价格路径。

    drift/volatility 为年化值, dt 为年化时间步(默认 1/252 交易日)。
    """

    start_price: float
    n_bars: int
    drift: float = 0.0  # 年化漂移率
    volatility: float = 0.20  # 年化波动率
    dt: float = 1.0 / 252.0  # 年化时间步
    seed: int = 42
    symbol: str = "SIM"

    def __post_init__(self) -> None:
        if self.start_price <= 0:
            raise ScenarioGenerationError(f"start_price must be > 0, got {self.start_price}")
        if self.n_bars <= 0:
            raise ScenarioGenerationError(f"n_bars must be > 0, got {self.n_bars}")
        if self.volatility < 0:
            raise ScenarioGenerationError(f"volatility must be >= 0, got {self.volatility}")
        if self.dt <= 0:
            raise ScenarioGenerationError(f"dt must be > 0, got {self.dt}")


@dataclass(frozen=True)
class HistoricalParams:
    """历史场景参数——从真实数据切片。"""

    source_data: pd.DataFrame
    start_idx: int = 0
    n_bars: int = 0  # 0 = 到末尾
    symbol: str = "HIST"

    def __post_init__(self) -> None:
        if not isinstance(self.source_data, pd.DataFrame):
            raise ScenarioGenerationError(f"source_data must be a DataFrame, got {type(self.source_data).__name__}")
        required = {"open", "high", "low", "close", "volume"}
        missing = required - set(self.source_data.columns)
        if missing:
            raise ScenarioGenerationError(f"source_data missing columns: {sorted(missing)}")
        if self.start_idx < 0:
            raise ScenarioGenerationError(f"start_idx must be >= 0, got {self.start_idx}")
        end = len(self.source_data) if self.n_bars == 0 else self.start_idx + self.n_bars
        if self.start_idx >= len(self.source_data):
            raise ScenarioGenerationError(f"start_idx {self.start_idx} out of range (len={len(self.source_data)})")
        if end > len(self.source_data):
            raise ScenarioGenerationError(
                f"slice [{self.start_idx}:{end}] exceeds source length {len(self.source_data)}"
            )


@dataclass(frozen=True)
class CustomParams:
    """自定义场景参数——基础路径+冲击序列+趋势。"""

    start_price: float
    n_bars: int
    shocks: tuple[tuple[int, float], ...] = ()  # [(bar_idx, pct_shock), ...]
    trend: float = 0.0  # 每期线性漂移
    seed: int = 42
    symbol: str = "CUST"

    def __post_init__(self) -> None:
        if self.start_price <= 0:
            raise ScenarioGenerationError(f"start_price must be > 0, got {self.start_price}")
        if self.n_bars <= 0:
            raise ScenarioGenerationError(f"n_bars must be > 0, got {self.n_bars}")
        for bar_idx, pct in self.shocks:
            if bar_idx < 0 or bar_idx >= self.n_bars:
                raise ScenarioGenerationError(f"shock bar_idx {bar_idx} out of range [0,{self.n_bars})")


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ScenarioGeneratorConfig:
    """场景生成器配置——不可变。"""

    default_seed: int = 42
    default_volume: float = 10000.0  # 默认成交量


# ──────────────────────────────────────────────────────────────────────────────
# SimulationScenario Aggregate (frozen 不可变)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SimulationScenario:
    """仿真场景——核心 Aggregate, 不可变。

    封装生成的市场数据 + 元数据, 供下游仿真模块消费。
    params 为生成参数快照, 可用于精确复现。
    """

    scenario_id: str
    scenario_type: ScenarioType
    symbol: str
    market_data: pd.DataFrame
    params: dict[str, Any]
    generated_at: str  # ISO8601
    description: str = ""

    @property
    def n_bars(self) -> int:
        return len(self.market_data)


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _make_scenario_id(scenario_type: ScenarioType) -> str:
    """生成全局唯一 scenario_id: 类型-时间戳-短uuid。"""
    return f"{scenario_type.value}-{uuid.uuid4().hex[:8]}"


# ──────────────────────────────────────────────────────────────────────────────
# 场景生成器
# ──────────────────────────────────────────────────────────────────────────────


class ScenarioGenerator:
    """场景生成器——蒙特卡洛/历史/自定义三种模式。

    用法:
        gen = ScenarioGenerator()
        # 蒙特卡洛
        scenario = gen.generate_monte_carlo(MonteCarloParams(
            start_price=100.0, n_bars=252, drift=0.08, volatility=0.25, seed=42
        ))
        df = scenario.market_data  # OHLCV DataFrame
        # 历史
        scenario = gen.generate_historical(HistoricalParams(source_data=real_df, n_bars=60))

    纯 numpy/pandas 生成, 同 seed 可复现。

    Args:
        config: 生成器配置(默认 seed/volume)
    """

    def __init__(self, config: ScenarioGeneratorConfig | None = None) -> None:
        self._config = config or ScenarioGeneratorConfig()

    @property
    def config(self) -> ScenarioGeneratorConfig:
        return self._config

    # ── 蒙特卡洛 (GBM) ──

    def generate_monte_carlo(self, params: MonteCarloParams) -> SimulationScenario:
        """基于几何布朗运动生成随机价格路径。

        S_t = S_{t-1} * exp((drift - 0.5*vol²)*dt + vol*sqrt(dt)*Z)
        """
        rng = np.random.default_rng(params.seed)
        n = params.n_bars
        # 布朗增量
        z = rng.standard_normal(n)
        drift_term = (params.drift - 0.5 * params.volatility**2) * params.dt
        diffusion = params.volatility * np.sqrt(params.dt) * z
        log_returns = drift_term + diffusion

        # 价格路径 (close)
        closes = np.empty(n)
        prices = params.start_price
        for i in range(n):
            prices = prices * np.exp(log_returns[i])
            closes[i] = prices

        df = self._build_ohlcv(closes, params.symbol)
        return SimulationScenario(
            scenario_id=_make_scenario_id(ScenarioType.MONTE_CARLO),
            scenario_type=ScenarioType.MONTE_CARLO,
            symbol=params.symbol,
            market_data=df,
            params={
                "start_price": params.start_price,
                "n_bars": params.n_bars,
                "drift": params.drift,
                "volatility": params.volatility,
                "dt": params.dt,
                "seed": params.seed,
            },
            generated_at=_utcnow_iso(),
            description=f"Monte Carlo GBM scenario: drift={params.drift}, vol={params.volatility}",
        )

    # ── 历史场景 ──

    def generate_historical(self, params: HistoricalParams) -> SimulationScenario:
        """从真实历史数据切片封装为可重放场景。"""
        end = len(params.source_data) if params.n_bars == 0 else params.start_idx + params.n_bars
        # 切片拷贝, 不修改源数据
        df = params.source_data.iloc[params.start_idx : end].copy()
        df.index = pd.RangeIndex(start=0, stop=len(df), step=1)

        return SimulationScenario(
            scenario_id=_make_scenario_id(ScenarioType.HISTORICAL),
            scenario_type=ScenarioType.HISTORICAL,
            symbol=params.symbol,
            market_data=df,
            params={
                "source_rows": len(params.source_data),
                "start_idx": params.start_idx,
                "n_bars": len(df),
            },
            generated_at=_utcnow_iso(),
            description=f"Historical scenario: slice [{params.start_idx}:{end}]",
        )

    # ── 自定义场景 ──

    def generate_custom(self, params: CustomParams) -> SimulationScenario:
        """基础路径 + 冲击序列 + 趋势, 生成确定性 what-if 场景。"""
        rng = np.random.default_rng(params.seed)
        n = params.n_bars
        # 基础: 微小随机游走 + 线性趋势
        noise = rng.standard_normal(n) * 0.001  # 0.1% 噪声
        closes = np.empty(n)
        price = params.start_price
        shock_map = {idx: pct for idx, pct in params.shocks}
        for i in range(n):
            ret = params.trend + noise[i]
            if i in shock_map:
                ret += shock_map[i]  # 叠加冲击
            price = price * (1 + ret)
            closes[i] = price

        df = self._build_ohlcv(closes, params.symbol)
        return SimulationScenario(
            scenario_id=_make_scenario_id(ScenarioType.CUSTOM),
            scenario_type=ScenarioType.CUSTOM,
            symbol=params.symbol,
            market_data=df,
            params={
                "start_price": params.start_price,
                "n_bars": params.n_bars,
                "shocks": list(params.shocks),
                "trend": params.trend,
                "seed": params.seed,
            },
            generated_at=_utcnow_iso(),
            description=f"Custom scenario: {len(params.shocks)} shocks, trend={params.trend}",
        )

    # ── 通用分发 ──

    def generate(
        self,
        scenario_type: ScenarioType,
        params: MonteCarloParams | HistoricalParams | CustomParams,
    ) -> SimulationScenario:
        """按类型分发到对应生成方法。"""
        if scenario_type is ScenarioType.MONTE_CARLO:
            if not isinstance(params, MonteCarloParams):
                raise ScenarioGenerationError(f"MONTE_CARLO requires MonteCarloParams, got {type(params).__name__}")
            return self.generate_monte_carlo(params)
        if scenario_type is ScenarioType.HISTORICAL:
            if not isinstance(params, HistoricalParams):
                raise ScenarioGenerationError(f"HISTORICAL requires HistoricalParams, got {type(params).__name__}")
            return self.generate_historical(params)
        if scenario_type is ScenarioType.CUSTOM:
            if not isinstance(params, CustomParams):
                raise ScenarioGenerationError(f"CUSTOM requires CustomParams, got {type(params).__name__}")
            return self.generate_custom(params)
        raise ScenarioGenerationError(f"unknown scenario_type: {scenario_type}")

    # ── 内部: OHLCV 构建 ──

    def _build_ohlcv(self, closes: np.ndarray, symbol: str) -> pd.DataFrame:
        """从 close 序列构建 OHLCV DataFrame。

        open=前收(close[-1] 滚动), high/low 围绕 close, volume=常数。
        """
        n = len(closes)
        opens = np.empty(n)
        opens[0] = closes[0]
        opens[1:] = closes[:-1]
        highs = np.maximum(opens, closes) * 1.001
        lows = np.minimum(opens, closes) * 0.999
        volumes = np.full(n, self._config.default_volume)

        df = pd.DataFrame(
            {
                "open": opens,
                "high": highs,
                "low": lows,
                "close": closes,
                "volume": volumes,
            }
        )
        return df
