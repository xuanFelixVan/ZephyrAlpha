---
module_id: KE-669
status: active
title: Ke Governance                     003
ttl: permanent
doc_type: knowledge_entry
---

--___________-----003
title: ---- 必填字段（禁止省略）----
category: governance
---

# ---- 必填字段（禁止省略）----

---- 必填字段（禁止省略）----
schema_version: "1.0"                  # YAML schema 版本，升级时递增
doc_type: gate                         # 固定值，frontmatter_validator 据此选校验规则
gate_id: G1                            # 机读主键，格式 /^G[1-5]$/，必须在 {G1,G2,G3,G4,G5} 内
gate_name: ingest                      # 机读 slug，kebab-case，必须在 {ingest,triage,evaluate,activate,extract} 内
title: "G1 Ingest Gate"                # 人类可读标签，格式 "G{N} {Name} Gate"
description: "一句话总述本门禁职责"     # ≤ 200 字
status: active                         # active | deprecated | draft
ttl: permanent                         # 门禁策略文件 TTL 固定为 permanent
