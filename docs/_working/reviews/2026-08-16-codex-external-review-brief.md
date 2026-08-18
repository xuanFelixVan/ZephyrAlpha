---
title: Codex 外部审查任务书——量化核心算法正确性专项
date: 2026-08-16
doc_type: review_request
ttl: task_bound
completes_when: "Codex 审查报告回收并裁定后归档"
---

# Codex 外部审查任务书（量化核心算法正确性专项）

> **发包方**：ZephyrAlpha 统筹（coord-0815-gov3）
> **审查方**：Codex 最强模型（一次性深度审查）
> **模式**：只审不改——输出发现清单（分级+证据+修复建议），不改任何代码

## 〇、系统画像（30 秒背景）

A 股量化交易系统，Python，ClickHouse+PIT 数据层。单笔交易全链路已闭环：信号→仓位→风控→合规→执行→对账→监控。本批 4.5 万项测试全绿——**但测试是自写的，可能镜像同样的错误假设**。你的价值=用独立视角审"测试覆盖不到的正确性"。

## 一、审查点清单（按"错=亏钱"程度排序）

### R1 · VaR/ES 数值正确性（最高优先）

- **文件**：`src/zephyr/risk/core/var_calculator.py`（VaRCalculator L291 起）
- **设计文档**：`docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md`
- **重点审**：
  1. FHS（Filtered Historical Simulation）分位数插值方法——线性/最近邻/中点口径是否自洽，与 ES（尾部均值）是否用同一排序样本
  2. ES 是否真取"≤VaR 的尾部均值"还是误用"≤ 分位点的切片"（off-by-one 高发区）
  3. 年化因子 √252 的应用方向（收益率→风险还是风险→收益率，乘反就是 15.9 倍误差）
  4. 极端输入：空窗口/全同值（σ=0 除零）/NaN 传播/样本量 < 置信度要求时的行为
  5. n-1 自由度的使用是否全篇一致
- **我最担心**：测试锚点是自算的——如果公式错了，测试锚点也是错的，双错互证绿

### R2 · RegimeMeta 分配数学

- **文件**：`src/zephyr/pf_alloc/core/regime_meta_allocator.py`
- **设计文档**：`.../design_memos/34_regime_meta_allocator.md`
- **重点审**：
  1. Sortino 下行偏差：分母用 n 还是 n-1，半方差是否只取负收益（含未持仓日 0 的口径=全时间线纪律，审口径是否被某路径破坏）
  2. water-filling 分配：N=2 无解兜底逻辑是否数学正确（回归锚点：两策略排序相同/相反时分配是否退化合理）
  3. allocation × global_shrinkage 解耦：两层缩放连乘是否可能双重折扣（设计意图是 shrinkage ≤1.0 只减不增）
  4. CRISIS floor 0.09→0.05 的切换路径有无状态残留
- **我最担心**：解耦的两层缩放在某边界路径上连乘生效，仓位被平方级压缩

### R3 · 仓位算法 Kelly 边界

- **文件**：`src/zephyr/position/core/position_sizing_engine.py`
- **设计文档**：`.../design_memos/31_position_sizing.md`
- **重点审**：
  1. 半 Kelly+截 0：f*≤0 时的输出（应为 0 仓位，审有无负数/异常值漏出）
  2. 分布感知调整因子 dist_adj：默认 ≤1、正偏例外 ≤1.1——例外路径的触发条件是否可被构造输入绕过
  3. 追高边界浮点尾差（施工期实证捕获过：价格恰好=阈值时买入/拒单行为是否确定）
  4. §2.8 漂移再平衡触发逻辑：漂移带判定用绝对/相对口径是否与设计文档一致
- **我最担心**：边界等值路径（价格==阈值、漂移==带宽）的行为未定义或未测试

### R4 · 资金对账一致性（对账错了=发现不了亏钱）

- **文件**：`src/zephyr/ex_core/position_reconciler.py` + `src/zephyr/trading/settlement_reconciliation.py` + `src/zephyr/risk/stop_loss.py`（detect_ghost_positions）
- **设计文档**：`.../design_memos/54_reconciliation_attribution.md` + `53_simulation_live_path.md`
- **重点审**：
  1. 幽灵持仓检测：券商有仓/系统无仓的枚举完整性（部分成交后断线恢复路径）
  2. Crash-only 恢复：崩溃后重放的状态一致性——会不会重复计成交/重复扣款
  3. 对账差异的归因分类有无"其他/unknown"静默吞差异的兜底桶
  4. 日申报笔数硬计数器（5000 预警/1 万阻断）：自然日滚动窗口的跨日重置边界、报单+撤单双计有无漏计路径
- **我最担心**：crash 恢复路径的幂等性——重复恢复=重复成交

### R5 · 极端行情降级链（平时测不到的路径）

- **文件**：`src/zephyr/risk/core/liquidity_crisis_manager.py` + `liquidity_monitor.py` + `src/zephyr/position/core/drawdown_controller.py` + `src/zephyr/risk/core/drawdown_tracker.py`
- **设计文档**：`.../design_memos/37_liquidity_crisis_protocol.md` + `35_drawdown_protocol_impl.md`
- **重点审**：
  1. 涨跌停无法成交时的卖出降级链（挂单价→市价→次日）有无死循环/死等路径
  2. Kill Switch 触发条件恰好等于阈值（==vs>）的行为
  3. 回撤 Protocol 各档位切换的状态机完备性（有无无法到达/无法退出的状态）
  4. 多 Protocol 同时触发时的优先级仲裁（流动性危机 vs 回撤 vs KillSwitch 同刻触发的行为定义）
- **我最担心**：多 Protocol 同刻触发未定义——极端行情恰恰是多 Protocol 同时触发的场景

## 二、输出格式要求

每个发现给四要素：

```
[P0/P1/P2] 标题
位置：文件:行号
证据：代码片段+推演路径（为什么这是错的/风险的）
修复建议：具体到改法
```

- P0=会亏钱/会失控，P1=口径漂移/边界未定义，P2=健壮性建议
- 没有发现问题的审查点也要明说"R3 审过，未发现 P0/P1"——阴性结论同样有价值
- 引用设计文档与代码不一致处单独列一节（文档-代码漂移清单）

## 三、约束

- 不改任何代码（只读审查）
- 不信测试绿——测试锚点可能镜像错误假设，用独立推算验证
- A 股语境：T+1、涨跌停 10%/20%、无裸卖空——用美股惯例指出的"问题"先核对是否已被 A 股规则覆盖
