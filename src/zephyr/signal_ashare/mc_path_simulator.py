# [BLUEPRINT] MOD-SIG-074 | 待统筹登记（缺口总账 GAP-F-36 行）
# [MODULE] zephyr.signal_ashare.mc_path_simulator
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy（纯数值，零 DB/网络/LLM）
# [CONSUMERS] （候选：作战室 W2 方案卡 / 个股决策弹窗"压力测试"卡，GAP-F-36 消费位）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双法封闭 {gbm, bootstrap}；胜率=终点价严格大于起点价的路径占比 ∈ [0,1]；90% 置信上下限=终点价 5%/95% 分位（ci_level 对称分位一般化）；逐日分布带 low<=mid<=high；种子可复现（np.random.default_rng）；零波动降级=路径恒平胜率 0 不炸；输入校验 fail-closed（历史不足/非正非有限价格/参数越界）；frozen dataclass JSON 可序列化；分布输出非点位预测（90号 §7 只画栏杆不算命）
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-36 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（历史不足/价格非法/method/n_paths/horizon/ci_level 越界，fail-closed）
# [TESTS] tests/signal_ashare/test_mc_path_simulator.py
# [A_module] module_id=MOD-SIG-074 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""蒙特卡洛路径模拟引擎（MOD-SIG-074，GAP-F-36）。

缺口总账 GAP-F-36（作战室 W2 方案卡 / 个股决策弹窗）：个股级 20 日路径分布
+ 胜率 + 90% 置信上下限。双法封闭：

- ``gbm``：几何布朗运动。由历史对数收益估计日漂移 μ 与日波动 σ，按
  ``log S_t+1 - log S_t ~ N(μ - σ²/2, σ²)`` 向前模拟 horizon 天。
- ``bootstrap``：历史日简单收益有放回重采样（经验分布，不假设正态），
  ``S_t+1 = S_t × (1 + r_sampled)``。

产出：终点价分布的分位数（默认 5%/50%/95% → 90% 置信区间）、胜率
（终点严格大于起点的路径占比）、逐日 p5/p50/p95 分布带（前端画扇形图用）。

纪律：分布是状态描摹不是点位预测（90号 §7）；胜率非校准概率。
不做什么：不读库（closes 由上游装载注入）/不下单/不做方向性荐股。

依据: 缺口总账 GAP-F-36
SSoT: depgraph node 10505565（MOD-SIG-074，待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: closes（收盘价升序序列，≥min_history+1 根，正且有限）+ method + MCSimConfig
# 特征: 日对数/简单收益（μ/σ 估计或经验池）
# 算法: GBM 正态抽样 | bootstrap 经验重采样 → (n_paths, horizon) 路径矩阵
# 输出: MCSimResult（胜率/90%CI/逐日分布带/μσ 估计留痕）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

import numpy as np

logger = logging.getLogger(__name__)

__all__: Final = [
    "METHOD_BOOTSTRAP",
    "METHOD_GBM",
    "MCSimConfig",
    "MCSimResult",
    "simulate_paths",
]

METHOD_GBM: Final = "gbm"
METHOD_BOOTSTRAP: Final = "bootstrap"
_METHODS: Final = frozenset({METHOD_GBM, METHOD_BOOTSTRAP})

_TRADING_DAYS_PER_YEAR: Final = 252


@dataclass(frozen=True, slots=True)
class MCSimConfig:
    """蒙特卡洛模拟配置（参数 >4 收 dataclass）。

    Attributes:
        horizon: 模拟天数（默认 20，缺口契约 20 日路径分布）。
        n_paths: 路径条数（≥100 保分位数稳定）。
        seed: 随机种子（可复现）。
        min_history: 最小历史根数（收益样本 = 根数-1，不足拒算防空转）。
        ci_level: 置信水平（默认 0.90 → 上下限取 5%/95% 分位）。
    """

    horizon: int = 20
    n_paths: int = 2000
    seed: int = 42
    min_history: int = 30
    ci_level: float = 0.90

    def __post_init__(self) -> None:
        if int(self.horizon) < 1:
            raise ValueError(f"horizon 非法（须 ≥1）: {self.horizon!r}")
        if int(self.n_paths) < 100:
            raise ValueError(f"n_paths 非法（须 ≥100）: {self.n_paths!r}")
        if int(self.min_history) < 5:
            raise ValueError(f"min_history 非法（须 ≥5）: {self.min_history!r}")
        if not (0.5 < float(self.ci_level) < 1.0):
            raise ValueError(f"ci_level 非法（须 ∈ (0.5,1)）: {self.ci_level!r}")


@dataclass(frozen=True, slots=True)
class MCSimResult:
    """蒙特卡洛路径分布产出（JSON 可序列化）。"""

    method: str
    horizon: int
    n_paths: int
    start_price: float
    win_rate: float  # 终点价 > 起点价的路径占比
    terminal_median: float  # 终点价中位数
    ci_lower: float  # 终点价下分位（90%CI 下限）
    ci_upper: float  # 终点价上分位（90%CI 上限）
    band_lower: tuple[float, ...] = ()  # 逐日下分位带（horizon 长）
    band_median: tuple[float, ...] = ()
    band_upper: tuple[float, ...] = ()
    drift_daily: float = 0.0  # 日漂移估计（GBM=μ；bootstrap=经验均值）
    annualized_vol: float = 0.0  # 年化波动估计
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_closes(closes: Sequence[float], min_history: int) -> np.ndarray:
    arr = np.asarray(list(closes), dtype=float)
    if arr.ndim != 1 or len(arr) < min_history + 1:
        raise ValueError(f"历史不足（须 ≥{min_history + 1} 根收盘价）: n={len(arr)}")
    if not np.all(np.isfinite(arr)) or not np.all(arr > 0):
        raise ValueError("价格非法（须全部为正且有限）")
    return arr


def _simulate_gbm(log_rets: np.ndarray, cfg: MCSimConfig) -> tuple[np.ndarray, float, float]:
    mu = float(np.mean(log_rets))
    sigma = float(np.std(log_rets, ddof=1)) if len(log_rets) > 1 else 0.0
    rng = np.random.default_rng(cfg.seed)
    shocks = rng.standard_normal((cfg.n_paths, cfg.horizon))
    daily = (mu - 0.5 * sigma * sigma) + sigma * shocks
    return np.cumsum(daily, axis=1), mu, sigma


def _simulate_bootstrap(simple_rets: np.ndarray, cfg: MCSimConfig) -> tuple[np.ndarray, float, float]:
    rng = np.random.default_rng(cfg.seed)
    sampled = rng.choice(simple_rets, size=(cfg.n_paths, cfg.horizon), replace=True)
    paths_log = np.cumsum(np.log1p(sampled), axis=1)
    mu = float(np.mean(np.log1p(simple_rets)))
    sigma = float(np.std(np.log1p(simple_rets), ddof=1)) if len(simple_rets) > 1 else 0.0
    return paths_log, mu, sigma


def simulate_paths(
    closes: Sequence[float],
    *,
    method: str = METHOD_GBM,
    config: MCSimConfig | None = None,
) -> MCSimResult:
    """蒙特卡洛路径模拟主入口（个股级 20 日路径分布+胜率+90% 置信上下限）。

    Args:
        closes: 收盘价升序序列（正且有限，≥min_history+1 根）。
        method: "gbm"（几何布朗）| "bootstrap"（历史收益重采样）。
        config: 模拟配置（None=默认 20 日×2000 路径×90%CI）。

    Returns:
        MCSimResult（胜率/置信上下限/逐日分布带，JSON 可序列化）。

    Raises:
        ValueError: 输入/参数非法（fail-closed）。
    """
    cfg = config or MCSimConfig()
    if method not in _METHODS:
        raise ValueError(f"method 非法（合法={sorted(_METHODS)}）: {method!r}")
    arr = _validate_closes(closes, cfg.min_history)
    start = float(arr[-1])

    log_rets = np.diff(np.log(arr))
    if method == METHOD_GBM:
        paths_log, mu, sigma = _simulate_gbm(log_rets, cfg)
    else:
        paths_log, mu, sigma = _simulate_bootstrap(np.diff(arr) / arr[:-1], cfg)
    paths = start * np.exp(paths_log)  # (n_paths, horizon)

    terminal = paths[:, -1]
    alpha = 1.0 - float(cfg.ci_level)
    q_lo, q_mid, q_hi = alpha / 2.0, 0.5, 1.0 - alpha / 2.0
    band_lo = np.quantile(paths, q_lo, axis=0)
    band_mid = np.quantile(paths, q_mid, axis=0)
    band_hi = np.quantile(paths, q_hi, axis=0)

    notes: list[str] = []
    if sigma == 0.0:
        notes.append("历史收益零波动（恒定价格），路径恒平降级")

    return MCSimResult(
        method=method,
        horizon=cfg.horizon,
        n_paths=cfg.n_paths,
        start_price=start,
        win_rate=float(np.mean(terminal > start)),
        terminal_median=float(np.quantile(terminal, q_mid)),
        ci_lower=float(np.quantile(terminal, q_lo)),
        ci_upper=float(np.quantile(terminal, q_hi)),
        band_lower=tuple(float(x) for x in band_lo),
        band_median=tuple(float(x) for x in band_mid),
        band_upper=tuple(float(x) for x in band_hi),
        drift_daily=mu,
        annualized_vol=sigma * float(np.sqrt(_TRADING_DAYS_PER_YEAR)),
        notes=tuple(notes),
    )
