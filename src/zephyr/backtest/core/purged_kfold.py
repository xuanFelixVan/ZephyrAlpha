# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.purged_kfold
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] 预留(标签重叠窗口策略上线时接入, 52号§6 BM-BT-04-C)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] train严禁含test折样本;t1重叠purge+test末端embargo剔除;K折连续块无重叠
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PurgedKFoldError(ZA-BT-0034)
# [TESTS] tests/backtest/test_purged_kfold.py
# [TTL] permanent
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [ALGO_FLOW]
# I1: n_samples/n_splits + t1(各样本标签末端索引,可选) + embargo(隔离样本数)
# A1: purged_kfold_split(K折连续块→test; 其余train; 按t1重叠purge+test末端embargo剔除)
# O1: list[(train_indices, test_indices)] 长度=n_splits
# [/ALGO_FLOW]
"""Purged K-Fold 交叉验证切分模块(BM-BT-04-C)

职责(52号 memo §6 暂缓项函数级落地, 标签重叠窗口策略上线时启用):
  - purged_kfold_split: López de Prado Purged K-Fold——连续 K 折切分,
    train 侧剔除标签窗口与 test 区间重叠的样本(purge),
    并剔除 test 末端后 embargo 隔离带内的样本(防序列相关泄漏)

与 WFA Embargo 的关系: walk_forward 的 Embargo 在滚动窗口链路内已部分等效;
本模块面向"标签重叠窗口策略"(多周期持仓)的独立 K-Fold 场景, 标签末端 t1
由调用方注入(输入注入式, 不连接外部数据)。

约束:
  - PIT铁律: train 严禁包含 test 折样本; purge 基于调用方注入的 t1
  - 纯 numpy 操作

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/52_backtest_framework_docking.md §6
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "PurgedKFoldError",
    "purged_kfold_split",
]


class PurgedKFoldError(Exception):
    """Purged K-Fold 切分错误(输入非法)"""

    error_code = "ZA-BT-0034"

    def __init__(self, *args, error_code: str | None = None) -> None:
        super().__init__(*args)
        if error_code is not None:
            self.error_code = error_code


def purged_kfold_split(
    n_samples: int,
    n_splits: int = 5,
    *,
    t1: list[int] | np.ndarray | None = None,
    embargo: int = 0,
) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Purged K-Fold 切分(净化+隔离)

    算法:
      1. 将 [0, n_samples) 均分为 n_splits 个连续折(前 remainder 折多 1 样本)
      2. 第 k 折作 test=[s, e), train=其余样本:
         - purge: 剔除标签窗口 [i, t1[i]] 与 [s, e-1] 重叠的 train 样本 i
           (t1 为 None 时 t1[i]=i, 退化为仅 embargo)
         - embargo: 剔除落在 [e, e+embargo) 内的 train 样本

    Args:
        n_samples: 样本总数(>=n_splits)
        n_splits: 折数(>=2)
        t1: 各样本标签末端索引(长度 n_samples, 单调不减且 t1[i] >= i); None=点标签
        embargo: test 区间末端后的隔离样本数(>=0)

    Returns:
        长度 n_splits 的列表, 每项为 (train_indices, test_indices) 元组(升序)

    Raises:
        PurgedKFoldError: 参数非法或 t1 结构非法
    """
    if n_samples <= 0:
        raise PurgedKFoldError(f"n_samples必须>0, got {n_samples}")
    if n_splits < 2:
        raise PurgedKFoldError(f"n_splits必须>=2, got {n_splits}")
    if n_samples < n_splits:
        raise PurgedKFoldError(f"n_samples({n_samples})必须>=n_splits({n_splits})")
    if embargo < 0:
        raise PurgedKFoldError(f"embargo必须>=0, got {embargo}")

    if t1 is None:
        t1_arr = np.arange(n_samples)
    else:
        t1_arr = np.asarray(t1, dtype=int)
        if t1_arr.shape != (n_samples,):
            raise PurgedKFoldError(
                f"t1长度必须等于n_samples={n_samples}, got shape {t1_arr.shape}"
            )
        if np.any(t1_arr < np.arange(n_samples)):
            raise PurgedKFoldError("t1必须满足 t1[i] >= i(标签末端不得早于样本自身)")
        if np.any(np.diff(t1_arr) < 0):
            raise PurgedKFoldError("t1必须单调不减(时间序列标签末端不可倒流)")

    base, remainder = divmod(n_samples, n_splits)
    all_idx = np.arange(n_samples)
    splits: list[tuple[tuple[int, ...], tuple[int, ...]]] = []

    start = 0
    for k in range(n_splits):
        size = base + (1 if k < remainder else 0)
        s, e = start, start + size
        start = e

        test_indices = tuple(int(i) for i in range(s, e))
        drop_mask = np.zeros(n_samples, dtype=bool)
        drop_mask[s:e] = True
        # purge: 标签窗口 [i, t1[i]] 与 test 区间 [s, e-1] 重叠
        overlap = (all_idx <= e - 1) & (t1_arr >= s)
        drop_mask |= overlap
        # embargo: test 末端后 [e, e+embargo) 隔离带
        if embargo > 0:
            drop_mask[e : min(n_samples, e + embargo)] = True

        train_indices = tuple(int(i) for i in all_idx[~drop_mask])
        splits.append((train_indices, test_indices))

    return splits
