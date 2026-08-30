# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.cpcv
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] 预留(策略验证流水线/过拟合检测升级, 52号§6重评触发后接线)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CPCV组合数=C(n_groups,k_test);train严禁含test组样本;t1重叠purge+test末端embargo剔除;PBO∈[0,1]
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CPCVError(ZA-BT-0033)
# [TESTS] tests/backtest/test_cpcv.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: n_samples/n_groups/k_test + t1(各样本标签末端索引,可选) + embargo(隔离样本数)
# I2: is_performance/oos_performance 性能矩阵(n_splits×n_trials, 调用方注入)
# A1: generate_cpcv_splits(N组取k组组合→test; 其余组train; 按t1重叠purge+各test组末端embargo剔除)
# A2: compute_pbo(每split取IS最优trial→其OOS相对秩ω=rank/(M+1)→logit(ω)→PBO=P(logit<0))
# O1: list[CPCVSplit] / PBO报告dict(pbo/logits/omega)
# [/ALGO_FLOW]
"""
CPCV(组合净化交叉验证) + PBO(回测过拟合概率)模块

职责(52号 memo §6 暂缓项函数级落地, 重评条件触发后启用):
  - generate_cpcv_splits: Combinatorial Purged CV 路径生成(López de Prado),
    N 组取 k 组作 test 的全组合切分, train 侧按标签窗口重叠 purge + embargo 隔离
  - compute_pbo: Probability of Backtest Overfitting(Bailey et al. 2014),
    IS 最优 trial 在 OOS 的相对秩 logit 小于 0 的比例

约束:
  - PIT铁律: train 严禁包含 test 组样本; purge 基于调用方注入的 t1(标签末端索引)
  - 纯 numpy 操作, 不依赖外部数据连接, 性能矩阵由调用方注入(输入注入式)

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/52_backtest_framework_docking.md §6

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: n_groups 参数
#   fields: 参数 n_groups，类型注解 int
#   code: cpcv.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: k_test 参数
#   fields: 参数 k_test，类型注解 int
#   code: cpcv.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: n_samples 参数
#   fields: 参数 n_samples，类型注解 int
#   code: cpcv.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: t1 参数
#   fields: 参数 t1（无注解）
#   code: cpcv.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① expected_n_splits
#   name_en: expected_n_splits
#   intro: CPCV 切分组合数 = C(n_groups, k_test)
#   desc: CPCV 切分组合数 = C(n_groups, k_test)；源码 L148-L154
#   inputs: n_groups k_test
#   outputs: int
# - id: A2
#   name_zh: ② generate_cpcv_splits
#   name_en: generate_cpcv_splits
#   intro: 生成 CPCV 全组合切分(净化+隔离)
#   desc: 生成 CPCV 全组合切分(净化+隔离) 算法: 1. 将样本均分为 n_groups 个连续组, 取 k_test 组的全组合 C(n_groups, k_test) 作 te…；源码 L172-L251
#   inputs: n_samples n_groups k_test t1 embargo
#   outputs: list[CPCVSplit]
# - id: A3
#   name_zh: ③ compute_pbo
#   name_en: compute_pbo
#   intro: 计算 PBO(Probability of Backtest Overfitting, Bailey et al.
#   desc: 计算 PBO(Probability of Backtest Overfitting, Bailey et al. 2014) 算法: 每折 split: n* = argmax…；源码 L270-L325
#   inputs: is_performance oos_performance
#   outputs: dict
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 预留(策略验证流水线/过拟合检测升级, 52号§6重评触发后接线)
# - id: O2
#   name_zh: list[CPCVSplit]
#   name_en: list[CPCVSplit]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 预留(策略验证流水线/过拟合检测升级, 52号§6重评触发后接线)
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

import math
from dataclasses import dataclass
from itertools import combinations

import numpy as np

__all__ = [
    "CPCVError",
    "CPCVSplit",
    "generate_cpcv_splits",
    "expected_n_splits",
    "compute_pbo",
]


class CPCVError(Exception):
    """CPCV/PBO 计算错误(输入非法)"""

    error_code = "ZA-BT-0033"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class CPCVSplit:
    """CPCV 单折切分结果(不可变)

    Attributes:
        split_id: 折序号(按组合生成顺序)
        test_groups: 本折作为测试集的组号元组
        train_indices: 训练集样本索引(purge+embargo 后)
        test_indices: 测试集样本索引(各 test 组样本并集, 升序)
    """

    split_id: int
    test_groups: tuple[int, ...]
    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]


def expected_n_splits(n_groups: int, k_test: int) -> int:
    """CPCV 切分组合数 = C(n_groups, k_test)"""
    if n_groups < 2:
        raise CPCVError(f"n_groups必须>=2, got {n_groups}")
    if not 1 <= k_test < n_groups:
        raise CPCVError(f"k_test必须在[1, n_groups), got k_test={k_test}, n_groups={n_groups}")
    return math.comb(n_groups, k_test)


def _group_bounds(n_samples: int, n_groups: int) -> list[tuple[int, int]]:
    """将 [0, n_samples) 均分为 n_groups 个连续块, 返回各组 [start, end) 边界。

    前 remainder 组多分得 1 个样本(与 np.array_split 语义一致)。
    """
    base, remainder = divmod(n_samples, n_groups)
    bounds: list[tuple[int, int]] = []
    start = 0
    for g in range(n_groups):
        size = base + (1 if g < remainder else 0)
        bounds.append((start, start + size))
        start += size
    return bounds


def generate_cpcv_splits(
    n_samples: int,
    n_groups: int = 6,
    k_test: int = 2,
    *,
    t1: list[int] | np.ndarray | None = None,
    embargo: int = 0,
) -> list[CPCVSplit]:
    """生成 CPCV 全组合切分(净化+隔离)

    算法:
      1. 将样本均分为 n_groups 个连续组, 取 k_test 组的全组合 C(n_groups, k_test) 作 test
      2. train = 其余组样本, 对每个 test 组区间 [s, e):
         - purge: 剔除标签窗口 [i, t1[i]] 与 [s, e-1] 重叠的 train 样本 i
           (t1 为 None 时 t1[i]=i, train 本不含 test 组样本, 退化为无 purge)
         - embargo: 剔除落在 [e, e+embargo) 内的 train 样本(test 末端后隔离带)

    Args:
        n_samples: 样本总数
        n_groups: 分组数(>=2)
        k_test: 每折测试组数(1 <= k_test < n_groups)
        t1: 各样本标签末端索引(长度 n_samples, 单调不减且 t1[i] >= i); None=点标签
        embargo: test 区间末端后的隔离样本数(>=0)

    Returns:
        CPCVSplit 列表, 长度 = C(n_groups, k_test)

    Raises:
        CPCVError: 参数非法或 t1 结构非法
    """
    if n_samples <= 0:
        raise CPCVError(f"n_samples必须>0, got {n_samples}")
    expected_n_splits(n_groups, k_test)  # 复用参数校验
    if n_samples < n_groups:
        raise CPCVError(f"n_samples({n_samples})必须>=n_groups({n_groups})")
    if embargo < 0:
        raise CPCVError(f"embargo必须>=0, got {embargo}")

    if t1 is None:
        t1_arr = np.arange(n_samples)
    else:
        t1_arr = np.asarray(t1, dtype=int)
        if t1_arr.shape != (n_samples,):
            raise CPCVError(f"t1长度必须等于n_samples={n_samples}, got shape {t1_arr.shape}")
        if np.any(t1_arr < np.arange(n_samples)):
            raise CPCVError("t1必须满足 t1[i] >= i(标签末端不得早于样本自身)")
        if np.any(np.diff(t1_arr) < 0):
            raise CPCVError("t1必须单调不减(时间序列标签末端不可倒流)")

    bounds = _group_bounds(n_samples, n_groups)
    splits: list[CPCVSplit] = []
    all_idx = np.arange(n_samples)

    for split_id, test_groups in enumerate(combinations(range(n_groups), k_test)):
        test_mask = np.zeros(n_samples, dtype=bool)
        for g in test_groups:
            s, e = bounds[g]
            test_mask[s:e] = True
        test_indices = tuple(int(i) for i in all_idx[test_mask])

        drop_mask = test_mask.copy()
        for g in test_groups:
            s, e = bounds[g]
            # purge: 标签窗口 [i, t1[i]] 与 test 区间 [s, e-1] 重叠
            overlap = (np.arange(n_samples) <= e - 1) & (t1_arr >= s)
            drop_mask |= overlap
            # embargo: test 末端后 [e, e+embargo) 隔离带
            if embargo > 0:
                drop_mask[e : min(n_samples, e + embargo)] = True

        train_indices = tuple(int(i) for i in all_idx[~drop_mask])
        splits.append(
            CPCVSplit(
                split_id=split_id,
                test_groups=tuple(int(g) for g in test_groups),
                train_indices=train_indices,
                test_indices=test_indices,
            )
        )
    return splits


def _average_ranks_ascending(values: np.ndarray) -> np.ndarray:
    """升序平均秩(最小值秩=1, 同值取平均秩), 纯 numpy 实现避免 scipy 依赖。"""
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    sorted_vals = values[order]
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and sorted_vals[j] == sorted_vals[i]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0  # 秩从1开始: 位置[i, j)的平均秩
        ranks[order[i:j]] = avg_rank
        i = j
    return ranks


def compute_pbo(
    is_performance: list[list[float]] | np.ndarray,
    oos_performance: list[list[float]] | np.ndarray,
) -> dict:
    """计算 PBO(Probability of Backtest Overfitting, Bailey et al. 2014)

    算法:
      每折 split: n* = argmax_trial IS 性能 → 取该 trial 的 OOS 性能在本折
      全部 trial OOS 性能中的相对秩 ω = rank/(M+1)(升序, M=trial 数, ω∈(0,1))
      → logit(ω) = ln(ω/(1-ω)) → PBO = P(logit < 0)(IS 最优 OOS 低于中位数的比例)。
      PBO 越高, 回测过拟合越严重(IS 选出的"最优"在样本外大概率跑输中位数)。

    Args:
        is_performance: IS 性能矩阵, 形状 (n_splits, n_trials), 输入注入
        oos_performance: OOS 性能矩阵, 形状同 is_performance(逐 split 对齐)

    Returns:
        dict: pbo(float∈[0,1]), mean_logit(float), logits(list[float]),
              omega(list[float]), n_splits(int), n_trials(int)

    Raises:
        CPCVError: 矩阵形状不一致/非2D/trial<2/含非有限值
    """
    is_arr = np.asarray(is_performance, dtype=float)
    oos_arr = np.asarray(oos_performance, dtype=float)
    if is_arr.shape != oos_arr.shape:
        raise CPCVError(f"IS/OOS性能矩阵形状必须一致, got {is_arr.shape} vs {oos_arr.shape}")
    if is_arr.ndim != 2:
        raise CPCVError(f"性能矩阵必须是2D(n_splits×n_trials), got ndim={is_arr.ndim}")
    n_splits, n_trials = is_arr.shape
    if n_splits < 1:
        raise CPCVError("n_splits必须>=1")
    if n_trials < 2:
        raise CPCVError(f"n_trials必须>=2(相对秩才有意义), got {n_trials}")
    if not (np.all(np.isfinite(is_arr)) and np.all(np.isfinite(oos_arr))):
        raise CPCVError("性能矩阵含NaN/Inf, 拒绝计算")

    logits: list[float] = []
    omegas: list[float] = []
    for s in range(n_splits):
        n_star = int(np.argmax(is_arr[s]))
        ranks = _average_ranks_ascending(oos_arr[s])
        omega = float(ranks[n_star]) / (n_trials + 1.0)
        omegas.append(omega)
        logits.append(math.log(omega / (1.0 - omega)))

    logits_arr = np.asarray(logits, dtype=float)
    pbo = float(np.mean(logits_arr < 0.0))
    return {
        "pbo": pbo,
        "mean_logit": float(np.mean(logits_arr)),
        "logits": logits,
        "omega": omegas,
        "n_splits": n_splits,
        "n_trials": n_trials,
    }
