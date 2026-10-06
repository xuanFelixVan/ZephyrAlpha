---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-03 | TDM-X-S1-01 信号收集与六桶分类

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写：离场信号矩阵的桶标签层，日频可表达）
- 依赖: X-S1-02/03/04（桶信号生成器）、X-R1-01（breaker 桶，模拟盘已有语义）
- 真源: `config/trading_decision_map.yaml#TDM-X-S1-01`（六桶=risk/signal/target/trailing/time/volatility）

## 1. 机制定义

8 类卖出信号源聚合去重（同持仓多信号合并为一条带来源列表），按六桶分类；分类决定判定链与
确认模式（止损类 immediate 不辩论，止盈类 close_confirm 收盘确认）。考卷语义=**桶标签矩阵**：
每持仓日在每个标的上的触发桶集合。

## 2. 计算式

```
# 各桶布尔宽表 (T×N)，由子卡生成：
B_risk       = X-S1-02 五路止损任一触发（含 Chandelier/固定/支撑/时间）
B_target     = X-S1-03 目标位达成
B_trailing   = X-S1-03 移动止盈/峰值回撤
B_signal     = X-S1-04 突破失败/情绪退潮
B_time       = X-S1-02 时间止损腿
B_volatility = 波动率离场（vol_stop：当日 |ret| > k·σ20 触发降半仓；k∈prereg）
exit_buckets[t,i] = {bucket: B_bucket[t,i]}
```

注意 TDM 六桶词表（risk/signal/target/trailing/time/volatility）与 42 号"止损/止盈/目标/移动/
时间/波动"同义映射——考卷列名按 TDM 词表，禁第二套词表。

## 3. 向量化实现要点

纯布尔矩阵按位或+列拼接，零行循环。桶之间不互斥（去重=同桶多源合并为集合，向量化下天然
无损）。紧贴 X-S1-05 融合卡消费。

## 4. 引擎接法（M 级）

- executor：新增 `exit_signal_surface(w_tgt, closes, atr, ...) -> dict[str, DataFrame]` 模块
  函数（建议落 `scripts/backtest/exit_surface.py` 新件——CREATE-GUARD 登记义务随施工批走）；
  evaluate_recipe 以 `exit_mode` 参数消费，缺省 `off` 时函数不调用、路径零漂移。
- schema：新增考维 `X_exit_buckets`（active_if exit_mode≠off），属 schema 修订→须走裁定
  （schema 一次定型纪律，revisions 增行），**施工前置=Owner 裁定，非本卡权限**。

## 5. 考法（T0 口径声明）

本卡自身零行循环；但其上游 X-S1-02/03 为路径依赖（须持仓记忆），**整格激活即破坏纯向量化：
T3b-T0 必须先重标定 per_point_seconds（0.53s/格口径禁用），fail-closed 沿用 prereg 钳制后再
定 T1/T2 点数**。

## 6. 数据列名

close/high/low（`c1_market.kline_daily`，经 `load_px(fields=("close","high","low"))`）；
ATR 由其派生（X-S1-02 卡）；vol_stop 用 close 派生 σ20。
