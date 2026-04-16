---
module_id: KE-048
title: "> ****:"
category: factor
source_file: "docs/02_FACTOR_LIBRARY/05_BACKTEST/06_FACTOR_DECAY.md"
source_git_deleted: true
original_path: "docs/02_FACTOR_LIBRARY/05_BACKTEST/06_FACTOR_DECAY.md"
deleted_in_commit: "71a4b0f3e53d1e0691aa44d14f722d534772a756"
recovery_date: "2026-04-16"
extracted_date: "2026-04-16"
version: "1.0.0"
status: Active
layer: L03
owner: ZephyrAlpha-Owner
---

# > ****:

## 核心内容摘要
```python
import pandas as pd
import numpy as np
from scipy import stats

def calculate_decay_curve(
    factor: pd.Series,
    returns: pd.Series,
    max_holding_periods: int = 20
) -> pd.DataFrame:
    """IC

    ?
        factor: ?
        returns: ?
        max_holding_periods: 

    ?
        ICDataFrame
    """
    decay_data = []

    for period in range(1, max_holding_periods + 1):
        # 
        forward_returns = returns.shift(-period)

        # ?
        valid_idx = factor.not...

## 关键设计要点
1. 该文件包含重要的技术规格和设计决策
2. 适用于Phase 2施工阶段参考
3. 具体内容请查看原始文件恢复命令

## 适用场景
- Phase 2 施工中L03层的实现参考
- 相关模块的设计决策依据

## 原始文件
- 恢复命令：`git show 71a4b0f3e53d1e0691aa44d14f722d534772a756^:docs/02_FACTOR_LIBRARY/05_BACKTEST/06_FACTOR_DECAY.md`
