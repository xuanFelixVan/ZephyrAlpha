---
module_id: KE-4047---9-000
title: 3. Risk Mitigation (§9)
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3. Risk Mitigation (§9)

3. Risk Mitigation (§9)

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | 恶意内容通过 CE 进入 LLM | 中 | 极高 | CT-CE-LSG-001 fail-closed: LSG 不可用→拒绝注入 |
| R2 | Token 预算耗尽→模型截断 | 中 | 高 | L1→L2→L3 渐进 + DocCompressor 压缩 |
| R3 | 过时 KE 主导最新经验 | 中 | 高 | Freshness Decay + TTL=90 天标记 legacy |
| R4 | VMS 不可用→上下文空洞 | 低 | 高 | embedded_defaults→硬编码基础上下文 |
| R5 | 3 核心文件未实现 (vector_bridge 等) | 已知 | — | construction_progress=phase_1_partial, beta 补 |
