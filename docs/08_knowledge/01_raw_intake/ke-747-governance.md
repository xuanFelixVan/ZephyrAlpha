---
module_id: KE-671
status: active
title: Ke Governance     005
ttl: permanent
doc_type: knowledge_entry
---

--005
title: ﻿---
category: governance
---

# ﻿---

﻿---
module_id: GOV-MOD-007
title: 多登记表同步标准
doc_type: standard
status: active
version: "2.1.1"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-02"
ttl: permanent
summary: "定义所有项目操作（创建规则/模块/脚本/ADR/文档/目录/门禁/知识条目等）后必须同步更新的登记表清单和同步顺序。`catalogs/` 内自动收录数以 `registry-master-index.yaml` 的 `total_registries` 为准（勿写死常量）；MRS-001 矩阵仍按 15 类登记目标描述「写到哪里」。v2.1.1：更正历史文案中误用的「24 张」常数。对标 ITIL SACM + AGENTS.md §6.2。"
tags: [module, governance, registry, synchronization, multi-registry, ssot, artifact-lifecycle]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2", why: "frontmatter 字段合法性——本文档所有 frontmatter 字段格式遵循其约束"}
  - {target: PS-REG-002, at: "cross_registry_rules", why: "`registry_consistency_contract.yaml` 中的 CR 规则（跨表共享字段与 SSoT 归属）——本标准是其在登记表同步操作上的落地规范"}
  - {target: PS-REG-005, at: "§2", why: "登记表总索引——`total_registries` 动态收录；本标准 MRS-001 覆盖全部可登记目标分类"}
  - {target: GOV-MOD-ALPHA_SIGNAL_DOMAIN, at: "§8", why: "准入记录写入——创建模块时 MRS-001 引用其准入记录模板"}
  - {target: GOV-MOD-003, at: "§3", why: "status 受控枚举——module-registry.yaml 的 blueprint.status 值来源于此"}
ai_autonomy: ai_modifiable
---
