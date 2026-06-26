---
module_id: KE-336
title: 4.2 Stage-level metrics / 阶段级指标表
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.2 Stage-level metrics / 阶段级指标表

4.2 Stage-level metrics / 阶段级指标表

| 阶段 | 核心工件 | Owner | Lead Time | Process Time | %C&A | 主要延迟来源 |
|------|---------|-------|----------|-------------|------|-----------|
| ② Factor Research | 因子假设 + 特征工程 | S2 | 5-20 天 | 2-8 小时 | 70% | 想法→验证的探索回合、PIT 数据整备 |
| ② Factor Library | 因子入库 + 质量断言 | S2 + S6 | 15-60 min | 10-30 min | 98% | PIT 三字段校验、五类质量断言 |
| ③ Model Train/Deploy | 模型 + 部署 manifest | S7（未来）| 2-24 小时 | 30 min-4 h | 95% | GPU 排队、超参搜索 |
| ③ Signal Generation | 信号 payload | S2 | 15-60 min | 5-15 min | 98% | 因子刷新依赖、下游订阅对齐 |
| ④ Portfolio Construction | 目标仓位 | S2 → S9（未来）| 5-15 min | 1-5 min | 99% | 约束求解器收敛 |
| ④ Pre-trade Risk | 风控审批结果 | S4 | &lt;1 min | 5-30 s | 99.9% | 限额查询、手工复核（ad-hoc）|
| ⑤ Order Submission | broker ACK | S3 | 1-5 min | 10-60 s | 99.5% | 券商 API 网络、Idempotency 校验（H10 红线）|
| ⑤ Fill &amp; Reconcile | 成交单 + 对账记录 | S3 + S6 | intraday | 1-5 min | 99% | 成交回报到齐、T+0/T+1 对账窗口 |
| ⑥ Attribution | PnL + 归因报告 | S2 | T+1 | 10-30 min | 99% | 日终结算数据到齐 |
| ⑦ Feedback loop | 研究结论 / ADR 候选 | S1 + S2 | T+1 ~ T+5 | 1-4 h | 85% | 人工复盘、AI 辅助分析往返 |

> **注**：LT/PT 数字基于当前"非 HFT、daily/hourly batch"定位（见 §5 NFR）。若未来激活 intraday 高频（触发条件：portfolio ≥ $10M + 接入 L1 行情），本表需整体向秒级压缩重写。
