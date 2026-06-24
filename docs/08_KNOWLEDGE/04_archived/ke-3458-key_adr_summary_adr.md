---
module_id: KE-3326------adr-002
title: 5. Key ADR summary / 关键 ADR 汇总
category: documentation
---

# 5. Key ADR summary / 关键 ADR 汇总

5. Key ADR summary / 关键 ADR 汇总

| ADR | Decision / 决策 | Impact / 影响 |
|-----|----------------|--------------|
| KBG-0001 | `docs/` is the single canonical source of truth / 唯一真源 | 所有文档归属 |
| KBG-0002 | Single frontmatter schema + phased required fields / 单一 schema + 分阶段必填 | 所有文档 frontmatter |
| KBG-0003 | Dual/multi AI collaboration workflow (Kimi diverge + Opus converge) / 双 AI 协作工作流 | 文档生产方式 |
| KBG-0015 | Context Engine：NetworkX + JSON + 本地 LLM 压缩 (Qwen2.5-3B) | 6 大核心服务之一 |
| KBG-0016 | Vector Memory：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 | 6 大核心服务之一 |
| KBG-0017 | Agent Orchestrator：SQLite + asyncio.Queue 起步，NATS 升级 | 6 大核心服务之一 |
| KBG-0018 | Agent Sandbox：Windows ACL + 只读挂载；Docker Desktop（升级）| Orchestrator 配套 |
| KBG-0019 | Feedback Loop Engine：SQLite 时间序列 + EMA 异常检测 | 6 大核心服务之一 |
| KBG-0020 | LLM Security Gateway：OWASP LLM Top 10 + fail-closed + 四层防御 | 6 大核心服务之一 |
| KBG-0021 | SSoT Validator：scaffold 唯一任务，阻塞下游 | scaffold 门禁 |

Full ADR index: KB:decisions namespace（33 ADRs, SQLite knowledge 表）

---
