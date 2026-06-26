---
module_id: KE-1175
title: MRS-004：禁止行为清单
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# MRS-004：禁止行为清单

MRS-004：禁止行为清单

以下行为被**明确禁止**，违反即视为同步违规：

| # | 禁止行为 | 示例 | 后果 |
|---|---------|------|------|
| 1 | **创建工件不登记**——创建了新文档/脚本/规则/ADR，但没有写入对应的登记表 | 创建了 GOV-MOD-007 但未写入 document-metadata-index-registry.yaml | 新 AI session 遍历登记表时该工件不可见——违反 Zero-Memory Restart 标准 |
| 2 | **只改物理文件不该登记表**——改了 frontmatter 的共享字段，但未同步任何登记表 | 改了 blueprint.md 的 version，module-registry.yaml 和 BPR 仍是旧值 | CR-001 FAIL |
| 3 | **只改登记表不改物理文件**——改了登记表的共享字段，物理 frontmatter 不同步 | 改了 module-registry 的 status，blueprint.md frontmatter 未改 | 物理文件与登记表背离——物理文件是 SSoT，登记偏差会永久化 |
| 4 | **改了 A 登记表不改 B 登记表**——两个登记表有同一个共享字段，只动了一个 | 改了 module-registry 的 version，BPR 还是旧值 | CR-001 FAIL——AI 读到矛盾版本 |
| 5 | **SearchReplace 模板不唯一导致误匹配**——多条记录共享相同字段值，替换命中错了目标 | v1.0.0+AI-GLM-5.1 同时出现在 MOD-INF-001 和 MOD-INF-003——本标准的 root cause | SearchReplace 只替换第一个匹配——需要差异化或使用更唯一的上下文 |
| 6 | **创建登记表本身但不登记到 registry-master-index.yaml**——新增了一张 YAML 登记表，但主索引不知道 | 创建了 deploy-registry.yaml，未写在 registry-master-index | MRS-001 矩阵缺失该表——违反 §1.4"新增即受管辖" |

---
