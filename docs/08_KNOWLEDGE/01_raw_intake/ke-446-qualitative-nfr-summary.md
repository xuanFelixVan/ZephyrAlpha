---
module_id: KE-446
status: active
title: 5.1 Qualitative NFR summary / 定性 NFR 概览
category: documentation
---

# 5.1 Qualitative NFR summary / 定性 NFR 概览

5.1 Qualitative NFR summary / 定性 NFR 概览

本节的定位原则（**先立边界再定数字**）：

- **Non-HFT 定位**：不追求微秒/毫秒级；延迟单位为**秒 / 分钟 / 小时**。若未来接入 L1 行情或组合 ≥ $10M，NFR 整体需重写。
- **市场时段 vs 非市场时段分层**：可用性/延迟 SLO 只在**市场时段（含盘前盘后 30 min 缓冲）**严格执行；非市场时段为 best-effort。
- **可审计 ≫ 可用性**：当前阶段（单人无外部用户）若可用性与可审计冲突，必须选可审计。

| Category / 类别 | Requirement / 要求 | Current phase target / 当前阶段目标 | 量化 SLO 见 |
|----------------|-------------------|-----------------------------------|-----------|
| **Latency / 延迟** | Non-HFT；秒级—分钟级 batch；端到端 signal→order ≤ 90s（p99）| 不追求微秒级 | §5.2 SLO-2 / SLO-3 |
| **Availability / 可用性** | 市场时段 99.9% / 非市场时段 best-effort | 单人操作，非 24/7 | §5.2 SLO-6 |
| **Auditability / 可审计性** | Full decision trail, immutable ADR, seven-dimension decision logs | **高优先级**（不可降）| §5.2 SLO-Audit |
| **Compliance / 合规性** | Personal-scale；future multi-investor triggers stricter | 当前最简，留扩展口 | §5.2 SLO-Audit |
| **Maintainability / 可维护性** | Single operator + AI collab；docs-as-code | 高优先级 | — |
| **Extensibility / 可扩展性** | 平台模块（Gateway / Memory Pipeline）deferred 但预留接口 | 架构预留 | — |
| **Security / 安全性** | Personal scale；密钥管理、无公开暴露 | `security_architecture.md` skeleton，激活条件见其 §8 | — |
| **Data Quality / 数据质量** | PIT / survivorship / lineage 三断言；完整度 / 一致性 / 及时性三维度 | 高优先级（因子与回测可信度的前置）| §5.2 SLO-7 |
