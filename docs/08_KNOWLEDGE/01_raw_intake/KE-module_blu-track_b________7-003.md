---
module_id: KE-module_blu-track_b________7-003
title: Track B：金融领域知识（7 类）
category: module_blueprint
---

# Track B：金融领域知识（7 类）

Track B：金融领域知识（7 类）

> 来源：arXiv 论文 / GitHub 开源项目 / 券商研报 / 监管文件。提取优先级：Owner 触发或定期批量注入。

| # | `category` | 含义 | 优先级 | `halflife_h` | 典型来源 | 示例 |
|:--:|-----------|------|:---:|:---:|---------|------|
| B1 | `strategy_logic` | 策略逻辑 | HIGH | 2160h(90d) | 论文 / 开源 / 内部研发 | "Turtle Trading：20 日突破入场 + 10 日反向出场 + ATR(20) 止损" |
| B2 | `factor_design` | 因子设计 | HIGH | 4320h(180d) | 论文 / 研究 | "Momentum 因子：过去 12-1 月累计收益，截面标准化" |
| B3 | `risk_management` | 风险管理 | HIGH | 2160h(90d) | 论文 / 监管 / 内部实践 | "VaR 99% 置信度 20 日回望窗口——巴塞尔 III 推荐" |
| B4 | `data_quality` | 数据质量 | MID | 4320h(180d) | 治理经验 / 踩坑 | "东方财富 API 复权因子：需和通达信交叉校验后使用" |
| B5 | `market_microstructure` | 市场微观结构 | MID | 8640h(360d) | 论文 / 交易经验 | "A 股 T+1 制度：当日买入次日才能卖出；涨停板 ±10%" |
| B6 | `compliance` | 合规知识 | MID | 2160h(90d) | 监管文件 / 法律 | "私募基金信息披露：季度报告应在季后 15 个工作日内提交" |
| B7 | `backtest_methodology` | 回测方法论 | MID | 4320h(180d) | 论文 / 专业实践 | "样本外测试最小周期 ≥ 样本内的 1/3——De Prado 建议" |

**优先级驱动的提取与存储策略**（对标 n1n.ai priority-based classification）：

| 优先级 | 条件 | 存储策略 | 对应类别 |
|:---:|------|---------|---------|
| **HIGH** | 不可变核心知识 + 错误必可避免类 | 提取后直接写入 KE（跳级），不入 KO 等待队列 | A1-A4, B1-B3 |
| **MID** | 可变偏好/配置/方法论类 | 先入 KO（Knowledge Observation）→ MTM 晋升队列 → 达升格阀值后变为 KE | A5-A8, B4-B7 |
| **LOW** | 瞬时/会话级/不可复用 | 保留在 Session Log 原位置，不入知识库。G2 Triage 阶段过滤 | 天气、临时报错、单次手动修法 |
