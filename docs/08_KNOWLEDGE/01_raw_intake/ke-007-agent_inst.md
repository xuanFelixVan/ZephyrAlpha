---
module_id: KE-007
status: active
title: 5.2.2 十维审计清单：每次施工后必须过一遍
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 5.2.2 十维审计清单：每次施工后必须过一遍

5.2.2 十维审计清单：每次施工后必须过一遍

> **触发条件**：任何涉及文件创建/修改/删除/移动的操作完成后。对标 §6.15 漂移免疫架构原则——漂移不是"可能发生"，而是"必然发生"，唯一问题是"什么时候被发现"。
>
> **维度来源**：覆盖项目 D1~D12 十二审计维度中的核心十维（D10 暂未定义）。

| # | 审计维度 | 审什么 | 重点检查项 | 关键自动化脚本 | 对应铁律 |
|:---:|---------|-------|-----------|----------|---------|
| **A** | **责任单一** | 文件/文件夹/概念是否只做一件事？ | 1️⃣ 文件名=职责？<br>2️⃣ 同一概念是否只在1处定义？<br>3️⃣ 是否有万能文件夹？ | `d5_architecture/validate_field_ownership.py`、`d5_architecture/detect_duplicate_module_names.py`、`d5_architecture/validate_directory_structure.py` | §5.1原则2、§6.4、§6.9 |
| **B** | **真源清晰** | 每个事实是否只有一个SSoT？YAML是否为canonical？ | 1️⃣ 找到同一事实的所有定义位置→只能有1个canonical→其余标注derived_from<br>2️⃣ vocabulary YAML↔所有派生文件枚举是否一致？<br>3️⃣ Markdown是否与YAML冲突（冲突→YAML为准）？ | `d5_architecture/validate_ssot.py`、`d3_metadata/validate_enum_consistency.py`、`d3_metadata/validate_derived_from.py`、`d5_architecture/validate_code_yaml_alignment.py` | §6.9、§6.13、§6.15 |
| **C** | **内容无冲突** | 不同文件对同一事实的描述是否一致？ | 1️⃣ frontmatter status=正文blockquote status=document-metadata-index-registry.yaml status（三方对齐）？<br>2️⃣ YAML版本>MD引用版本（MD落后于YAML）？<br>3️⃣ 跨登记表共享字段是否一致？<br>4️⃣ YAML Summary声称数字与实际是否一致？ | `d5_architecture/validate_three_way_consistency.py`、`d5_architecture/validate_cross_references.py`、`d11_compliance/validate_truth_source_cascade.py`、`d5_architecture/validate_yaml_summaries.py`、`check_registry_consistency.py` | §6.10、§6.15 |
| **D** | **文件夹职责清晰** | 每个目录是否只有一个职责？ | 1️⃣ 目录名=职责（能否一句话说清"放什么"）？<br>2️⃣ 目录内是否有不属于该职责的文件？<br>3️⃣ 是否有"源码↔YAML↔MD"三层漂移？<br>4️⃣ 一级目录是否符合白名单？ | `d5_architecture/validate_directory_structure.py`、`d1_structure/audit_directory_integrity.py`、`d5_architecture/validate_code_yaml_alignment.py` | GOV-DOC-002, §6.10 |
| **E** | **无废话** | 文档/文件是否每个字节都有存在必要？ | 1️⃣ 是否引用而非复制？<br>2️⃣ 是否有"等等""类似"等模糊词？<br>3️⃣ 是否有空壳文件/临时文件 (\_temp\*/\_check\*/\_phase\*)/残留物？<br>4️⃣ 是否有孤立文档（无入边引用）？<br>5️⃣ 是否有废墟引用（指向已删除的文件/目录）？<br>6️⃣ 是否有被替代但未删除的文件？<br>7️⃣ 新文件是否通过了准入门禁三问（内容不重复/跨phase有价值/不可替代）？ | `d1_structure/detect_residual_files.py`、`d1_structure/detect_temp_files.py`、`d1_structure/detect_orphan_py.py`、`d9_knowledge/detect_orphan_documents.py`、`d4_paths/detect_ruins_references.py`、`d6_security/detect_vague_terms.py`、zero-residue gate | IRN-011, §6.12, GOV-DOC-007 |
| **F** | **蓝图-代码同步** | 蓝图§16路径索引 ↔ 磁盘实际是否一致？ | 1️⃣ 蓝图声称"已实现"的文件是否存在（幽灵路径）？<br>2️⃣ 磁盘新增文件是否已在蓝图§16登记（遗漏登记）？<br>3️⃣ 蓝图路径 vs 实际路径是否一致（路径漂移）？<br>4️⃣ completed蓝图是否含实际代码实现情况节？ | `d5_architecture/validate_blueprint_code_sync.py`、`d5_architecture/sync_blueprint_code_index.py`、`d5_architecture/validate_blueprint_implementation_docs.py` | §6.14 |
| **G** | **链接完整** | 项目内所有跨文件引用是否可达？ | 1️⃣ 所有.md/.yaml中的路径引用→目标文件是否存在（断链检测）？<br>2️⃣ 是否有相对路径引用（应使用绝对路径）？<br>3️⃣ depends_on引用链是否≤3层？是否有环？ | `d2_links/audit_broken_links.py`、`d2_links/detect_relative_references.py`、`d5_architecture/audit_depends_on_chain_depth.py`、`d5_architecture/detect_depends_on_cycles.py` | §5.1原则3、§6.2 |
| **H** | **安全红线** | 代码中是否存在不可接受的安全漏洞？ | 1️⃣ 密钥/Token/凭证硬编码？<br>2️⃣ shell=True/os.system()？<br>3️⃣ 危险Git命令（push --force/reset --hard）？<br
