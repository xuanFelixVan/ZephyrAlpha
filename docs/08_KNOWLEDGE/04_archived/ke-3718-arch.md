---
module_id: KE-3570
title: 4. ARCH 域（架构规则）
category: governance_rule
---

# 4. ARCH 域（架构规则）

4. ARCH 域（架构规则）

> 来源：`02_enterprise_architecture/` 下的 ADR 和架构文档。

| 登记号 | 规则内容 | 对应 COND | 强制方式 | 来源路径 |
|--------|---------|----------|---------|---------|
| ARCH-001 | L02-L07 禁止直接调用 LLM Providers，必须通过 L08 LSG 代理 | COND-30 | doc | `02_enterprise_architecture/target_architecture/04-technology_architecture.md` L164 |
| ARCH-002 | 业务数据不得写入治理 SQLite | COND-31 | doc | `02_enterprise_architecture/adr/adr-0030-sqlite-task-metadata-store.md` L175 |
| ARCH-003 | 门禁级别禁止运行时动态升降级 | COND-33 | doc | `02_enterprise_architecture/gate-strategy-standard.md` L121 |
| ARCH-004 | 门禁跳级禁止——task 的 gate_status 必须按顺序推进 | COND-34 | doc | `02_enterprise_architecture/gate-strategy-standard.md` L322-324 |
| ARCH-005 | 门禁 disable 开关生产禁止关闭 | COND-35 | doc | `02_enterprise_architecture/gate-strategy-standard.md` L361 |
| ARCH-006 | AI 禁止自行签发门禁豁免 | COND-36 | doc | `02_enterprise_architecture/gate-strategy-standard.md` L497 |
| ARCH-007 | Pydantic 校验失败不得静默吞掉 | COND-37 | doc | `02_enterprise_architecture/adr/adr-0040-pydantic-v2-structured-contracts.md` L58 |
| ARCH-008 | 禁止引用 Deprecated ADR 作为当前决策依据 | COND-38 | doc | `02_enterprise_architecture/ssot-authority-map.md` L150-151 |
| ARCH-009 | 同一 module_id 不得在两个 Active 文件中出现 | COND-39 | ci | `scripts/governance/validate_authority_registry.py` L14 |
| ARCH-010 | Schema 三处（ADR / DDL / Pydantic Model）必须同步更新 | COND-40 | doc | `02_enterprise_architecture/adr/adr-0040-pydantic-v2-structured-contracts.md` L187 |
| ARCH-011 | SSoT 注册表与实际文件必须同步 | COND-41 | hook | `src/zephyr/hooks/ssot_guard.py` L27-30 |
| ARCH-012 | CoVe Step 2 必须使用与 Step 1 异构的模型 | COND-42 | doc | `02_enterprise_architecture/adr/adr-0039-cove-hallucination-detection.md` L187-189 |
| ARCH-013 | FLE 禁止直接 import 实现类，必须定义本地 Protocol | COND-43 | doc | `03_modules/_b_track_interfaces/feedback-loop-engine-interface.md` L383 |
| ARCH-014 | FLE Action 必须记录 effective_from + ttl | COND-44 | doc | `03_modules/_b_track_interfaces/feedback-loop-engine-interface.md` L690 |
| ARCH-015 | 服务降级必须写入日志 | COND-45 | doc | `03_modules/_b_track_interfaces/context-engine-interface.md` L712 |
| ARCH-016 | 知识库写入必须传 provenance | COND-46 | code | `src/zephyr/kb/unified_memory_api.py` L17 |
| ARCH-017 | HandoffPackage 8 必填字段不得删减 | COND-47 | doc | `02_enterprise_architecture/adr/adr-0041-session-handoff-protocol.md` L83 |
| ARCH-018 | 未经 KB 决策记录 审批禁止创建新正交视图 | COND-48 | doc | `02_enterprise_architecture/target_architecture/README.md` L120 |
| ARCH-019 | beta 接入真实资金前必须升级容器隔离 | COND-49 | doc | `02_enterprise_architecture/adr/adr-0018-agent-sandbox-windows-acl.md` L49 |
| ARCH-020 | KMS G4 强制人工最终拍板，AI 不得自主激活知识 | — | doc | `02_enterprise_architecture/adr/adr-0005-kms-architecture.md` L172 |
| ARCH-021 | YAML 门禁文件严禁直接写 P0/P1/P2，必须使用 error/warning/info | — | doc | `02_enterprise_architecture/gate-strategy-standard.md` L111 |
| ARCH-022 | Pydantic 模型禁止 Any 类型字段（边界透传场景除外且需注释） | — | doc | `02_enterprise_architecture/adr/adr-0040-pydantic-v2-structured-contracts.md` L59 |
| ARCH-023 | H/CRITICAL 级 FLE 提案强制 Owner 审批 |
