---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-00 | TDM-X-FLOW 输出离场信号（终端聚合）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06 | 只读挖矿产物（本文件为新建规格卡，非实现）
- 接法分级: **S**（manifest 增列/导出，纯向量化口径不破坏）
- 依赖: X-S1-02/03/05、X-R1-01 等离场维任一落地后本卡才有内容可导出
- 真源: `config/trading_decision_map.yaml#TDM-X-FLOW`；`docs/_working/fullcirc_closeout_chief/t3_fullflow_exam_mining.md` §1.7

## 1. 机制定义

TDM 定义本节点为"全流终端聚合点：只承载结构与指向，不写机制不存实时数据"。考卷语义下，
"今日离场清单"= 离场变换（X-S1 族）修改权重路径后的**每日离场动作审计表**：哪些格点在哪些日
对哪些标的触发了哪类离场、权重从多少改到多少。本节点本身零算法，只做导出。

## 2. 计算式

设离场变换输出 `w_exit`（详见 X-S1-02/03 卡），与变换前目标权重 `w_tgt` 逐元素比较：

```
exit_mask[t,i]   = |w_exit[t,i] - w_tgt[t,i]| > 1e-12 且 w_exit[t,i] < w_tgt[t,i]   # 减仓/清仓动作
exit_bucket[t,i] ∈ {stop_loss, take_profit, trailing, time, breakout, breaker}      # 首因桶（触发顺序优先级）
```

## 3. 向量化实现要点

纯 DataFrame 比较+argmax 取桶，无行循环，不破坏 0.53s/格 GPU 薄核口径（变换本体在 CPU 侧
pandas，见 X-S1-02 卡）。导出放在 executor manifest 写入处，与 `cost_attribution` 条件列
（T6 ⑤）同形。

## 4. 引擎接法（S 级）

- `scripts/backtest/factory_grid_executor.py` evaluate_recipe 返回处：新增可选列
  `exit_actions_json`（每日 `{symbol: [bucket, w_from, w_to]}` 列表，空=无离场）；
  `exit_enabled=False`（缺省）时列不写、路径逐位零漂移（T6 各件同款缺省纪律）。
- schema：不新增维（本节点非考维），只随离场维（X-S1-02/03 卡的 X_stop/X_tp 维）出现。

## 5. 考法（T0 口径声明）

本卡自身是纯导出（S 级），不改变耗时口径；但其内容的有无取决于 X-S1 族 M 级变换是否落地——
**一旦 X_stop/X_tp 维激活，整格走路径依赖回路，T3b-T0 必须先重标定
per_point_seconds（0.53s/格 gpu 薄核与 35.33s/格 CPU 旧口径均不适用），fail-closed 沿用
`config/search_space_prereg.yaml` 既有钳制机制后再定 T1/T2 点数**。此条为 prereg 硬门槛，
不是估算项。

## 6. 数据列名

无新数据依赖。输出列：`exit_actions_json`（manifest）、`exit_bucket` 审计位。
