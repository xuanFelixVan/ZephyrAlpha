---
ttl: task_bound
---

# 技术指标库 批 7 开工方案——消费端接线批（指标→因子/策略首建）

> 触发：Owner"开工方案"指令。前序：批 4/5 挖矿（indicator-mining-batch4.md）→ 批 6 施工（15a4326bc1）。
> 批 6 方案 §5 已立项的"消费端接线批"在此展开为可施工方案。施工 SOP 15 步同批 6 模式。

## 0. 方案挖矿增补（6 轮）

| 轮 | 矿脉 | 判定 | 产出 |
|---|------|------|------|
| W-R1 | 下游消费内部反查（二次核实） | **signal（结论修正）** | 初次 grep 的 kdj_k/atr_14 命中实为指标库自身 meta 定义；**真实业务消费引用≈0 维持**——接线批定位从"打通"改为"从 0 首建" |
| W-R2 | 机构平台接线范式 | signal | [Qlib 官方数据层文档](https://qlib.readthedocs.io/en/v0.6.2/component/data.html)：DataLoader（预计算特征库）→DataHandler（读取+处理器）→Dataset→模型；Alpha158=技术指标当特征的范式（我们指标表=DataLoader 层，缺的是 Handler） |
| W-R3 | 回填前置条件核查 | signal | 二轮完成（d/w/m 931 万行）；三轮死于并发写冲突、四轮已手动补发在跑；**启动条件=四轮完成+探针验证**（见 §4） |
| W-R4 | 技术路径内部盘点 | signal | 读取用 zephyr.data.ch_reader（FINAL 语义注意 ReplacingMergeTree 去重）；PIT 语义=预热 NaN 不前向填充+显示位移列（senkou_a/b）已存显示位；无现成 feature store——首版直接薄封装 ch_reader |
| W-R5 | 不做边界 | signal | 盘中实时 compute() 接线（sleeve 域）另立项；前端呈现归 TDM/工厂前端会话；Volume Profile 类另立 |

## 1. 目标（验收标准即定义）

**让 135 列指标从"存了"变成"能用"**：
1. 一个 PIT 安全的指标读取 API（首版薄封装）
2. ≥2 个真实消费落地（因子或回测冒烟）
3. 双向锚点（消费代码 ↔ REG-IND-001 条目 used_by_factors 字段回填）

## 2. 施工内容（三工作块）

### 块 A：指标读取 API（新建 src/zephyr/factor/indicator_reader.py）

```python
read_indicator(symbol, period, columns, start, end, as_of=None) -> DataFrame
```
- 走 ch_reader（禁裸 SQL，走 FINAL 或 argMax 去重语义）
- PIT 铁律：as_of 之后的数据硬拒读；预热 NaN 保持 NaN（消费方自行决定填充策略）
- 列名白名单校验（对照 TechnicalIndicatorRegistry.list_output_columns()，防拼错列名静默空返回）
- 单测：读取真实数据冒烟 + as_of 拦截 + 非法列名报错

### 块 B：首批消费落地（选 2 个真实场景）

| 场景 | 消费方 | 接线内容 |
|---|---|---|
| B1 波动率止损冒烟 | 回测/风控侧 | atr_14/yang_zhang_20 读取→止损位演示计算（脚本级消费冒烟） |
| B2 超买超卖因子输入 | factor 域 | rsi_6/boll_pctb 读取→演示因子构造（_STDDEV 先例口径） |

（场景设计为"消费模式样板"——后续因子照抄接线模式即可）

### 块 C：双向锚点回填

- REG-IND-001 被 B1/B2 消费的条目 used_by_factors 字段回填（batch 脚本 safe_write_text）
- 架构议题登记：消费端接线批完成记录（16 号 memo §7 开放问题⑦销项）

## 3. 前置条件与顺序

1. **回填四轮完成 + 最终探针**（d/w/m 行数≥批 2b 时点、批 3/6 新列非空抽样）——当前四轮在跑
2. 块 A → 块 B → 块 C（严格串行，B 依赖 A 的 API）
3. 工时估计：1 班（A≈0.3/B≈0.4/C≈0.3）

## 4. 回填链收尾状态（本方案发布时点）

| 周期 | 状态 | 覆盖 |
|---|---|---|
| weekly | ✅ 满 | 2019-01-04 起，178.8 万行 |
| monthly | ✅ 满 | 2019-01-31 起，44.5 万行 |
| daily | 🟡 基础列满（2021-01 起 707 万行）；批 4-6 新列历史等四轮 | 四轮手动补发在跑 |

三轮事故记录：与二轮并发写冲突死信（BufferedWriter.add 失败）——接力链判据改为"上轮日志完成标志"后仍有窗口，后续批次回填应串行执行。

## 5. 不做边界

- 盘中实时 compute() 消费（sleeve 域职权）
- 特征存储/Feature Store 平台化（Qlib 式 handler 生态，等消费规模起来再议）
- 前端指标看板（TDM/工厂前端会话职权）
