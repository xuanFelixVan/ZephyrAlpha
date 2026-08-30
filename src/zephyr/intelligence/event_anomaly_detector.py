# [BLUEPRINT] MOD-INT-EVENT-ANOMALY | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5
# [MODULE] zephyr.intelligence.event_anomaly_detector
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] numpy
# [CONSUMERS] 事件驱动 sleeve（异动事件源→事件分类/评分，26 号 §2.2 异动行）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 相关系数<0（个股与基准脱钩）+超额收益方向显著 双条件才判异动；序列长度不足/零方差/NaN → 降级 is_anomaly=False 不抛异常；两序列长度不一致 → EventAnomalyError
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EventAnomalyError(ZA-IT-0006)——输入契约违反（长度不一致/非数值）时抛；数据退化降级不抛
# [TESTS] tests/intelligence/test_event_anomaly_detector.py
# [A_module] module_id=MOD-INT-EVENT-ANOMALY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5 异动识别器（国盛异动雷达施工化）
# [ALGO_FLOW]
# I1: intraday_returns + benchmark_returns（分钟级收益率序列，等长）
# F1: 末窗口滚动相关系数（corr<0 判"脱钩"；零方差→NaN 降级）
# F2: 超额收益 cumprod(1+r)/cumprod(1+b)-1（全序列累计）
# A1: 双条件判定 is_anomaly = corr<阈值 AND |excess|>阈值；方向=sign(excess)
# O1: AnomalyResult(is_anomaly/anomaly_type/excess_return/rolling_corr/degraded)
# [/ALGO_FLOW]
"""
MOD-INT-EVENT-ANOMALY — 异动识别器（国盛证券异动雷达 2026-03 施工化，26 号 §2.5）。

方法：个股与基准分钟序列价格/成交量**相关系数 < 0** 触发"异动"（脱离同向
才是真异动——固定涨幅阈值会把大盘联动误判为异动），叠加**超额收益方向显著**
判定异动方向。国盛实证（2016-2026 中证800）：通道策略年化超额 7.51%/IR 2.48，
叠加负向筛选 9.77%/IR 2.92；此方法捕获 78% 重大事件前异动。

**G23 校准参数常量化**（26 号 §5 暂缓项 3：A 股参数——窗口/阈值/基准——
需 G23 回测校准，当前为 memo 首版裁定值的命名常量，校准后改常量单点生效）：
- ``ANOMALY_ROLLING_WINDOW = 20``（分钟，memo "window 默认 20"）
- ``ANOMALY_CORR_THRESHOLD = 0.0``
- ``ANOMALY_EXCESS_THRESHOLD = 0.03``

降级契约：序列过短（< window+1）/ 末窗口零方差 / 输入含 NaN →
``is_anomaly=False, degraded=True``，不抛异常（sleeve 链路任一环节失效可降级不阻塞，
26 号 §1.3）。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: event_anomaly_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: intraday_returns 参数
#   fields: 参数 intraday_returns，类型注解 Sequence[float]
#   code: event_anomaly_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: benchmark_returns 参数
#   fields: 参数 benchmark_returns，类型注解 Sequence[float]
#   code: event_anomaly_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: window 参数
#   fields: 参数 window，类型注解 int
#   code: event_anomaly_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① AnomalyResult
#   name_en: AnomalyResult
#   intro: 异动识别结果。
#   desc: 异动识别结果。 degraded : True 表示输入退化（序列过短/零方差/NaN），is_anomaly 恒 False。；公共方法（定义序）: to_dict；源码 L134-L155
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② detect_anomaly
#   name_en: detect_anomaly
#   intro: 异动识别（国盛异动雷达施工化）：相关系数<阈值 + 超额收益方向显著。
#   desc: 异动识别（国盛异动雷达施工化）：相关系数<阈值 + 超额收益方向显著。 Parameters ---------- symbol : 标的代码（追踪用，不参与计算）。 intra…；源码 L175-L235
#   inputs: symbol intraday_returns benchmark_returns window corr_threshold exces…
#   outputs: AnomalyResult
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: AnomalyResult
#   name_en: AnomalyResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 事件驱动 sleeve（异动事件源→事件分类/评分，26 号 §2.2 异动行）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Any, Final, Sequence

import numpy as np

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # noqa: BLE001  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_log = logging.getLogger(__name__)


class EventAnomalyError(ZephyrBaseError):
    """ZA-IT-0006: 异动识别输入契约违反（两序列长度不一致/非数值）。"""

    # 2026-08-21 定稿（Owner 批准两步收口）：原 ZA-INT-0002 与 sentinel_server.MCPError
    # 重码→改号 ZA-INT-0006（git 首引入裁定 canonical=先引入者）；同日 INT→IT 前缀
    # 语义迁移定稿 ZA-IT-0006（注册表 IT=D_INTELLIGENCE 为本模块域；零消费方实证）
    error_code = "ZA-IT-0006"


# ── G23 校准参数（26 号 §5 暂缓项 3——回测校准前为首版裁定常量）──
ANOMALY_ROLLING_WINDOW: Final[int] = 20  # 滚动相关窗口（分钟）
ANOMALY_CORR_THRESHOLD: Final[float] = 0.0  # 相关系数阈值（<0 判脱钩）
ANOMALY_EXCESS_THRESHOLD: Final[float] = 0.03  # 超额收益显著性阈值

ANOMALY_TYPE_POSITIVE: Final[str] = "positive"  # 异动上涨
ANOMALY_TYPE_NEGATIVE: Final[str] = "negative"  # 异动下跌
ANOMALY_TYPE_NONE: Final[str] = ""  # 无异动/降级


@dataclass(frozen=True, slots=True)
class AnomalyResult:
    """异动识别结果。

    degraded : True 表示输入退化（序列过短/零方差/NaN），is_anomaly 恒 False。
    """

    symbol: str
    is_anomaly: bool
    anomaly_type: str
    excess_return: float
    rolling_corr: float
    degraded: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "is_anomaly": self.is_anomaly,
            "anomaly_type": self.anomaly_type,
            "excess_return": self.excess_return,
            "rolling_corr": self.rolling_corr,
            "degraded": self.degraded,
        }


def _degraded(symbol: str, reason: str) -> AnomalyResult:
    _log.warning("detect_anomaly: %s 降级（%s）", symbol, reason)
    return AnomalyResult(symbol, False, ANOMALY_TYPE_NONE, 0.0, float("nan"), degraded=True)


_ZERO_VAR_EPS: Final[float] = 1e-12  # 零方差判定 eps（浮点常数序列 std≈1e-19 非精确 0）


def _last_window_corr(stock: np.ndarray, bench: np.ndarray, window: int) -> float:
    """末窗口 Pearson 相关系数；任一序列零方差 → NaN（不调 np.corrcoef 避免告警）。"""
    s_tail = stock[-window:]
    b_tail = bench[-window:]
    if np.std(s_tail) <= _ZERO_VAR_EPS or np.std(b_tail) <= _ZERO_VAR_EPS:
        return float("nan")
    return float(np.corrcoef(s_tail, b_tail)[0, 1])


def detect_anomaly(
    symbol: str,
    intraday_returns: Sequence[float],
    benchmark_returns: Sequence[float],
    window: int = ANOMALY_ROLLING_WINDOW,
    corr_threshold: float = ANOMALY_CORR_THRESHOLD,
    excess_threshold: float = ANOMALY_EXCESS_THRESHOLD,
) -> AnomalyResult:
    """异动识别（国盛异动雷达施工化）：相关系数<阈值 + 超额收益方向显著。

    Parameters
    ----------
    symbol : 标的代码（追踪用，不参与计算）。
    intraday_returns / benchmark_returns : 分钟级收益率序列（等长，时间升序）。
    window : 滚动相关窗口（默认 20 分钟，G23 待校准）。
    corr_threshold : 相关系数阈值（默认 0.0——脱离同向才算异动）。
    excess_threshold : 超额收益显著性阈值（默认 3%）。

    Returns
    -------
    AnomalyResult —— is_anomaly=True 时 anomaly_type 为 positive/negative；
    输入退化时 degraded=True 且 is_anomaly=False（不抛异常）。

    Raises
    ------
    EventAnomalyError
        两序列长度不一致 / 非数值输入（契约违反）。
    """
    if len(intraday_returns) != len(benchmark_returns):
        raise EventAnomalyError(
            f"detect_anomaly: 两序列长度不一致 stock={len(intraday_returns)} bench={len(benchmark_returns)}"
        )
    if window < 2:
        raise EventAnomalyError(f"detect_anomaly: window 须 ≥2，实际 {window}")

    try:
        stock = np.asarray(intraday_returns, dtype=float)
        bench = np.asarray(benchmark_returns, dtype=float)
    except (TypeError, ValueError) as exc:
        raise EventAnomalyError(f"detect_anomaly: 非数值输入 {exc}") from exc

    if stock.size < window + 1:
        return _degraded(symbol, f"序列过短 {stock.size} < window+1={window + 1}")
    if np.isnan(stock).any() or np.isnan(bench).any():
        return _degraded(symbol, "输入含 NaN")

    # 1. 末窗口滚动相关系数（memo 全序列 rolling 仅需末值，等价单点计算）
    rolling_corr = _last_window_corr(stock, bench, window)
    if math.isnan(rolling_corr):
        return _degraded(symbol, "末窗口零方差，相关系数未定义")

    # 2. 超额收益（全序列累计）
    excess = np.cumprod(1 + stock) / np.cumprod(1 + bench) - 1
    excess_final = float(excess[-1])

    # 3. 异动判定：相关系数<阈值（脱钩）+ 超额收益方向显著
    is_anomaly = bool(rolling_corr < corr_threshold and abs(excess_final) > excess_threshold)
    if not is_anomaly:
        return AnomalyResult(symbol, False, ANOMALY_TYPE_NONE, excess_final, rolling_corr)
    anomaly_type = ANOMALY_TYPE_POSITIVE if excess_final > 0 else ANOMALY_TYPE_NEGATIVE
    return AnomalyResult(symbol, True, anomaly_type, excess_final, rolling_corr)


__all__: Final = [
    "ANOMALY_ROLLING_WINDOW",
    "ANOMALY_CORR_THRESHOLD",
    "ANOMALY_EXCESS_THRESHOLD",
    "ANOMALY_TYPE_POSITIVE",
    "ANOMALY_TYPE_NEGATIVE",
    "ANOMALY_TYPE_NONE",
    "EventAnomalyError",
    "AnomalyResult",
    "detect_anomaly",
]
