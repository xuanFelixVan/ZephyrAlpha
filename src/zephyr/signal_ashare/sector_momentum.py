# [BLUEPRINT] MOD-SIG-026 supplement | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/22_sector_rotation_spec.md §3.1⑧
# [MODULE] zephyr.signal_ashare.sector_momentum
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES]
# [CONSUMERS] (待 G05 选股引擎 / 板块强度综合层第三维)
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] qN ∈ [0,1]; strength_momentum ∈ [0,1]; 纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 收盘价序列长度 < max(windows)+1 的板块跳过不出现在结果中
# [TESTS] tests/signal_ashare/test_sector_momentum.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: closes_by_sector(板块→日K收盘价序列 dict, market_kline_sector_880 盘后批量)
# A1: ret_N(i,t) = close(t)/close(t-N) − 1（N 日累计涨跌幅）
# A2: qN(i,t) = percentile_rank(ret_N(i,t), 全板块截面)（0~1 归一化消除量纲）
# A3: strength_momentum = 0.4×q20 + 0.3×q5 + 0.3×q3（多时间框架动量加权）
# O1: dict[板块代码, strength_momentum ∈ [0,1]]（板块强度综合层第三维输入）
# [/ALGO_FLOW]
"""
短周期动量 q3/q5/q20 多时间框架加权（22 号 spec §3.1⑧，BM-SEL-08 增强）。

应对板块一日游（Top3 次日重合率 14.8%，spec §2.3）：旧版 0.7×q20+0.3×q5
在"板块持续领涨"假设下成立，A 股一日游特征下 20 日权重过高会持续追
"已经走完的领涨"。新版 0.4×q20（中期趋势锚定）+ 0.3×q5 + 0.3×q3（超短期
最快感知方向变化）。不替换 production 双模块，作为板块强度综合层第三维
叠加（与 RRG 21d/63d/252d 多 TF 不同：q 是绝对涨幅排名打分，RRG 是相对
强度追轮动序列）。

数据源：market_kline_sector_880 日K 收盘价（盘后批量，T+1 开盘可执行）。
权重 0.4/0.3/0.3 为初拟（WyckoffTradingAgent v2.1.x 移植），待 G05 回测校准。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: closes 参数
#   fields: 参数 closes，类型注解 list[float]
#   code: sector_momentum.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: n 参数
#   fields: 参数 n，类型注解 int
#   code: sector_momentum.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: values 参数
#   fields: 参数 values，类型注解 dict[str, float]
#   code: sector_momentum.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: closes_by_sector 参数
#   fields: 参数 closes_by_sector，类型注解 dict[str, list[float]]
#   code: sector_momentum.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① n_day_return
#   name_en: n_day_return
#   intro: N 日累计涨跌幅 = close(t)/close(t-N) − 1。
#   desc: N 日累计涨跌幅 = close(t)/close(t-N) − 1。 Raises: ValueError: 序列长度 < n+1 或基准收盘价 ≤0。；源码 L109-L120
#   inputs: closes n
#   outputs: float
# - id: A2
#   name_zh: ② percentile_ranks
#   name_en: percentile_ranks
#   intro: 截面百分位排名（0=最弱，1=最强； ties 取平均秩）。
#   desc: 截面百分位排名（0=最弱，1=最强； ties 取平均秩）。 单板块时返回 0.5（无截面可比性，中性）。；源码 L123-L144
#   inputs: values
#   outputs: dict[str, float]
# - id: A3
#   name_zh: ③ multi_tf_momentum
#   name_en: multi_tf_momentum
#   intro: 多时间框架动量加权：strength_momentum = Σ w_k × q_{window_k}。
#   desc: 多时间框架动量加权：strength_momentum = Σ w_k × q_{window_k}。 Args: closes_by_sector: 板块代码 → 日K 收盘价…；源码 L147-L180
#   inputs: closes_by_sector windows weights
#   outputs: dict[str, float]
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 G05 选股引擎 / 板块强度综合层第三维)
# - id: O2
#   name_zh: dict[str, float]
#   name_en: dict[str, float]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 G05 选股引擎 / 板块强度综合层第三维)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

# ------------------------------------------------------------------
# 常量（初拟，22 号 spec §6 待 G05 回测校准）
# ------------------------------------------------------------------

DEFAULT_WINDOWS = (20, 5, 3)  # 多时间框架窗口（中期锚定/短中期/超短期）
DEFAULT_WEIGHTS = (0.4, 0.3, 0.3)  # 对应权重（之和=1.0）


def n_day_return(closes: list[float], n: int) -> float:
    """N 日累计涨跌幅 = close(t)/close(t-N) − 1。

    Raises:
        ValueError: 序列长度 < n+1 或基准收盘价 ≤0。
    """
    if len(closes) < n + 1:
        raise ValueError(f"计算 {n} 日涨跌幅需至少 {n + 1} 个收盘价，当前 {len(closes)} 个")
    base = closes[-(n + 1)]
    if base <= 0:
        raise ValueError("基准收盘价必须为正")
    return closes[-1] / base - 1.0


def percentile_ranks(values: dict[str, float]) -> dict[str, float]:
    """截面百分位排名（0=最弱，1=最强； ties 取平均秩）。

    单板块时返回 0.5（无截面可比性，中性）。
    """
    n = len(values)
    if n == 0:
        return {}
    if n == 1:
        return {k: 0.5 for k in values}
    ordered = sorted(values.items(), key=lambda kv: kv[1])
    ranks: dict[str, float] = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and ordered[j + 1][1] == ordered[i][1]:
            j += 1
        avg_rank = (i + j) / 2.0  # 等值并列取平均秩（0 基）
        for k in range(i, j + 1):
            ranks[ordered[k][0]] = avg_rank / (n - 1)
        i = j + 1
    return ranks


def multi_tf_momentum(
    closes_by_sector: dict[str, list[float]],
    *,
    windows: tuple[int, ...] = DEFAULT_WINDOWS,
    weights: tuple[float, ...] = DEFAULT_WEIGHTS,
) -> dict[str, float]:
    """多时间框架动量加权：strength_momentum = Σ w_k × q_{window_k}。

    Args:
        closes_by_sector: 板块代码 → 日K 收盘价序列（时间升序）。
        windows: 时间窗元组（默认 (20, 5, 3)）。
        weights: 权重元组（默认 (0.4, 0.3, 0.3)，与 windows 等长）。

    Returns:
        板块代码 → strength_momentum ∈ [0, 1]。
        收盘价序列长度 < max(windows)+1 的板块跳过（不出现在结果中）。

    Raises:
        ValueError: windows 与 weights 长度不一致。
    """
    if len(windows) != len(weights):
        raise ValueError("windows 与 weights 长度必须一致")
    min_len = max(windows) + 1
    valid = {code: closes for code, closes in closes_by_sector.items() if len(closes) >= min_len}
    if not valid:
        return {}

    # 各窗口截面百分位排名
    q_by_window: list[dict[str, float]] = []
    for w in windows:
        rets = {code: n_day_return(closes, w) for code, closes in valid.items()}
        q_by_window.append(percentile_ranks(rets))

    return {code: sum(weight * q[code] for weight, q in zip(weights, q_by_window, strict=True)) for code in valid}
