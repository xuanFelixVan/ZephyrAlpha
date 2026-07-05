# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.walk_forward
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] WF三模式;CPCV v2;White's Reality Check
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WalkForwardError
# [TESTS]
# [TTL] permanent
# [A_module] module_id=MOD-BT-001-walk_forward | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
"""Walk-Forward分析与多重比较偏差校正模块

职责:
  - Walk-Forward三模式切分(R-93/P1-29): 滚动(rolling)/锚定(anchored)/扩展(expanding)
  - White's Reality Check(P1-19): bootstrap多重比较偏差校正, 检验策略相对基准的显著超额收益
  - CPCV v2配置预留(P1-18): 组合净化交叉验证, 消除PIT泄漏(配置项待P1-18实现时添加)

约束:
  - PIT铁律: 训练集严禁包含测试集数据, 切分时train_end <= test_start
  - 步进step必须>0(防止死循环)
  - 年化基准: 252交易日

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# White's Reality Check显著性水平(alpha)
WRC_SIGNIFICANCE_LEVEL = 0.05


class WalkForwardError(Exception):
    """Walk-Forward分析错误"""


@dataclass(frozen=True)
class WalkForwardConfig:
    """Walk-Forward分析配置(不可变)

    Attributes:
        mode: 切分模式, rolling(滚动) | anchored(锚定) | expanding(扩展)
        train_window: 训练窗口长度(交易日)
        test_window: 测试窗口长度(交易日)
        step: 滚动步进(交易日), 用于rolling/anchored模式
        block_size: stationary block bootstrap平均块长(0=自动T^(1/3))
    """

    mode: str = "rolling"
    train_window: int = 252
    test_window: int = 63
    step: int = 63
    block_size: int = 0

    def __post_init__(self):
        if self.train_window <= 0:
            raise WalkForwardError(f"train_window必须>0, got {self.train_window}")
        if self.test_window <= 0:
            raise WalkForwardError(f"test_window必须>0, got {self.test_window}")
        if self.step <= 0:
            raise WalkForwardError(f"step必须>0(防止死循环), got {self.step}")
        if self.mode not in ("rolling", "anchored", "expanding"):
            raise WalkForwardError(
                f"不支持的mode: {self.mode} (支持: rolling/anchored/expanding)"
            )
        if self.block_size < 0:
            raise WalkForwardError(f"block_size必须>=0, got {self.block_size}")


class WalkForwardAnalyzer:
    """Walk-Forward分析器

    提供三模式时间序列切分与White's Reality Check多重比较偏差校正。
    按策略类型选择切分模式:
      - rolling: 短周期/非平稳策略, 固定训练窗口滑动
      - anchored: 中周期策略, 训练集从起点按step扩展
      - expanding: 长周期/稳健策略, 训练集逐步吸收测试数据增长
    """

    def __init__(self, config: WalkForwardConfig | None = None):
        self.config = config if config is not None else WalkForwardConfig()

    def split_rolling(self, dates: list) -> list[tuple[list, list]]:
        """滚动窗口切分(固定训练窗口滑动)

        每折训练窗口大小固定为train_window, 按step步进滑动。
        fold i: train=[i*step, i*step+train_window), test=[i*step+train_window, ...+test_window)

        Args:
            dates: 日期/索引序列(按时间升序)

        Returns:
            列表, 每元素为(train_dates, test_dates)元组; 数据不足时返回空列表

        Raises:
            WalkForwardError: dates为None
        """
        if dates is None:
            raise WalkForwardError("dates不能为None")
        n = len(dates)
        tw = self.config.train_window
        ow = self.config.test_window
        step = self.config.step
        folds: list[tuple[list, list]] = []
        i = 0
        while i + tw + ow <= n:
            train = list(dates[i : i + tw])
            test = list(dates[i + tw : i + tw + ow])
            folds.append((train, test))
            i += step
        return folds

    def split_anchored(self, dates: list) -> list[tuple[list, list]]:
        """锚定窗口切分(训练集从起点扩展, 按step增长)

        训练集起点固定在0, 训练终点按step递增(初始为train_window)。
        fold i: train=[0, train_window+i*step), test=[train_window+i*step, ...+test_window)

        Args:
            dates: 日期/索引序列(按时间升序)

        Returns:
            列表, 每元素为(train_dates, test_dates)元组; 数据不足时返回空列表

        Raises:
            WalkForwardError: dates为None
        """
        if dates is None:
            raise WalkForwardError("dates不能为None")
        n = len(dates)
        tw = self.config.train_window
        ow = self.config.test_window
        step = self.config.step
        folds: list[tuple[list, list]] = []
        train_end = tw
        while train_end + ow <= n:
            train = list(dates[0:train_end])
            test = list(dates[train_end : train_end + ow])
            folds.append((train, test))
            train_end += step
        return folds

    def split_expanding(self, dates: list) -> list[tuple[list, list]]:
        """扩展窗口切分(训练集逐步吸收测试数据增长)

        训练集起点固定在0, 每折吸收上一折的测试窗口, 训练终点按test_window递增。
        fold i: train=[0, train_window+i*test_window), test=[train_window+i*test_window, ...+test_window)
        注: expanding模式忽略step, 以test_window为增长步长(无重叠无间隙)。

        Args:
            dates: 日期/索引序列(按时间升序)

        Returns:
            列表, 每元素为(train_dates, test_dates)元组; 数据不足时返回空列表

        Raises:
            WalkForwardError: dates为None
        """
        if dates is None:
            raise WalkForwardError("dates不能为None")
        n = len(dates)
        tw = self.config.train_window
        ow = self.config.test_window
        folds: list[tuple[list, list]] = []
        train_end = tw
        while train_end + ow <= n:
            train = list(dates[0:train_end])
            test = list(dates[train_end : train_end + ow])
            folds.append((train, test))
            train_end += ow
        return folds

    def split(self, dates: list) -> list[tuple[list, list]]:
        """按config.mode自动选择切分模式

        Args:
            dates: 日期/索引序列(按时间升序)

        Returns:
            列表, 每元素为(train_dates, test_dates)元组

        Raises:
            WalkForwardError: dates为None或mode不支持
        """
        mode = self.config.mode
        if mode == "rolling":
            return self.split_rolling(dates)
        if mode == "anchored":
            return self.split_anchored(dates)
        if mode == "expanding":
            return self.split_expanding(dates)
        # __post_init__已校验mode, 此处防御性兜底
        raise WalkForwardError(f"不支持的mode: {mode} (支持: rolling/anchored/expanding)")

    def whites_reality_check(
        self,
        strategy_returns: pd.Series,
        benchmark_returns: pd.Series,
        n_bootstrap: int = 1000,
        block_size: int = 0,
    ) -> dict:
        """White's Reality Check(多重比较偏差校正, stationary block bootstrap)

        通过bootstrap重采样检验策略相对基准是否存在显著超额收益(superior predictive ability)。
        原假设H0: 策略无超额收益能力(期望差分<=0)。

        实现说明:
          - 对齐strategy与benchmark的索引后计算差分序列 d_t = strategy_t - benchmark_t
          - 观测统计量为差分均值的t统计量
          - 对差分序列重新中心化(d_t - mean(d))后在H0下bootstrap重采样
          - p_value = P(bootstrap_t >= observed_t) (单侧)
          - 采用stationary block bootstrap(Politis & Romano 1994),
            块长L~Geometric(mean=block_size), 块起始均匀随机, 保留时间序列自相关
          - block_size=0时自动取T^(1/3)(Politis & Romano最优块长)

        Args:
            strategy_returns: 策略收益率序列
            benchmark_returns: 基准收益率序列(与strategy_returns时间对齐)
            n_bootstrap: bootstrap重采样次数, 默认1000
            block_size: stationary block bootstrap平均块长(0=自动T^(1/3))

        Returns:
            dict: p_value(float), is_significant(bool, p<0.05), t_stat(float, 观测t统计量)

        Raises:
            WalkForwardError: 输入为None或n_bootstrap<=0
        """
        if strategy_returns is None or benchmark_returns is None:
            raise WalkForwardError("strategy_returns与benchmark_returns不能为None")
        if n_bootstrap <= 0:
            raise WalkForwardError(f"n_bootstrap必须>0, got {n_bootstrap}")

        # 对齐索引并丢弃缺失
        aligned = pd.concat([strategy_returns, benchmark_returns], axis=1).dropna()
        if len(aligned) < 2:
            return {"p_value": 1.0, "is_significant": False, "t_stat": 0.0}

        diff = (aligned.iloc[:, 0] - aligned.iloc[:, 1]).to_numpy(dtype=float)
        n = len(diff)
        obs_mean = float(np.mean(diff))
        obs_std = float(np.std(diff, ddof=1))
        if obs_std <= 0:
            # 收益率无波动, 无法做统计检验
            return {"p_value": 1.0, "is_significant": False, "t_stat": 0.0}
        sqrt_n = float(np.sqrt(n))
        obs_t = obs_mean / (obs_std / sqrt_n)

        # 自动计算block_size: T^(1/3)(Politis & Romano 1994最优块长)
        if block_size <= 0:
            block_size = max(1, int(round(n ** (1.0 / 3.0))))

        # 重新中心化(under H0: 均值为0), stationary block bootstrap估计null分布
        recentered = diff - obs_mean
        rng = np.random.default_rng()
        boot_stats = np.empty(n_bootstrap)
        for b in range(n_bootstrap):
            sample = self._stationary_block_bootstrap(recentered, block_size, rng)
            s_std = float(np.std(sample, ddof=1))
            if s_std <= 0:
                boot_stats[b] = 0.0
            else:
                boot_stats[b] = float(np.mean(sample)) / (s_std / sqrt_n)

        # 单侧p-value(超额收益能力: bootstrap >= observed)
        p_value = float(np.mean(boot_stats >= obs_t))
        is_significant = bool(p_value < WRC_SIGNIFICANCE_LEVEL)
        return {
            "p_value": p_value,
            "is_significant": is_significant,
            "t_stat": float(obs_t),
        }

    @staticmethod
    def _stationary_block_bootstrap(
        data: np.ndarray, block_size: int, rng: np.random.Generator
    ) -> np.ndarray:
        """Stationary block bootstrap(Politis & Romano 1994)

        块长L ~ Geometric(mean=block_size), 块起始位置均匀随机,
        保留时间序列自相关结构。最优block_size = T^(1/3)。

        Args:
            data: 一维数据数组
            block_size: 平均块长(Geometric分布的均值)
            rng: numpy随机数生成器

        Returns:
            重采样后的数组(长度等于data)
        """
        n = len(data)
        result = np.empty(n)
        # 块长服从Geometric分布, p = 1/block_size
        p_block = 1.0 / max(block_size, 1)
        idx = 0
        while idx < n:
            # 采样块长L ~ Geometric(p_block)
            block_len = int(rng.geometric(p_block))
            if block_len <= 0:
                block_len = 1
            # 块起始位置均匀随机(stationary: 允许环绕)
            start = int(rng.integers(0, n))
            for j in range(block_len):
                if idx >= n:
                    break
                # 环绕索引(块可跨越序列边界)
                result[idx] = data[(start + j) % n]
                idx += 1
        return result


__all__ = [
    "WalkForwardConfig",
    "WalkForwardAnalyzer",
    "WalkForwardError",
    "WRC_SIGNIFICANCE_LEVEL",
]
