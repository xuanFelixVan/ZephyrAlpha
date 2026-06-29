---
doc_type: index
title: 临时工作区入口
ttl: task_bound
completes_when: "docs/_working/ 下所有子区完成清理或晋升,本目录仅剩 index.md"
---

# docs/_working/ 临时工作区入口

> **定位**: 项目唯一过程性文档临时区。所有 task_bound 文档默认落此。
> **真源**: [trae_047 §gov_eng_002_directory_mapping](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#L140-L159) | [ttl_vocabulary.yaml decision_tree](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml)

## 一、子区职责表

| 子区 | 职责 | 允许格式 | 状态 |
|---|---|---|---|
| `audit/` | 审计报告与状态快照 | .md | active |
| `archive/` | 统一归档区(所有永久区 deprecated 文件归此) | .md | active(2026-06-29 新增) |
| `decomposition/` | 任务分解卡(DM-100252~255) | .md | active |
| `research_notes/` | 研究笔记归集 | .md/.txt/.yaml | active |
| `ttl_content_audit/` | TTL 重分类审计 | .csv | active |
| `module_migration/` | P2 模块迁移追踪(完成后删除) | .md | active(待清理) |

## 二、命名禁令

`_working/` 下子目录名 **禁止** 与永久区子目录同名,避免歧义:
- 禁止 `03_governance_reports/`(与 [docs/02_enterprise_architecture/03_governance_reports/](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports) 生成器豁免区同名)
- 禁止与 `docs/01/02/03/08` 下任何子目录同名

## 三、completes_when 规则

新增 .md 文件 MUST 在 frontmatter 声明 `completes_when` 字段,内容为可验证的完成条件。
GitCommitGateway commit 时自动拦截缺失该字段的新文档。

示例:
```yaml
completes_when: "PANORAMA-REBUILD 分解任务全部完成且 tasks/ 目录归档"
```

## 四、晋升门禁

task_bound → permanent 须经 GitCommitGateway `--allow-promote`:
- AI 不得自行批准晋升
- 永久区路径: `docs/01_policies_and_standards/` | `docs/02_enterprise_architecture/` | `docs/03_modules/` | `docs/08_knowledge/`
- 生成器豁免区(02 下 `00_overview_entry/`、`01_global_architecture_diagram/`、`02_domain_architecture_docs/`、`03_governance_reports/`)跳过此门禁

## 五、幽灵引用验证

读取 `_working/` 下任何 .md 前 MUST 验证文档引用的脚本/YAML/blueprint_id 是否仍存在:
1. 提取文档内所有 `file://` 链接与路径引用
2. 逐个验证目标文件存在
3. 发现断链 → 修复引用或删除文档

## 六、已知违规(待清理)

| 文件/目录 | 违规 | 处置计划 |
|---|---|---|
| `_commit_batch.py` | .py 不允许在 `_working/`(违反 [trae_047 L154](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#L154)) | P2 迁移完成后迁移至 `scripts/` 或删除 |
| `_gen_lists.py` | 同上 | 同上 |
| `03_governance_reports/` | 与永久区生成器豁免区同名 | 改名为 `reports/`(阶段3) |
| `module_migration/` | 过程性目录长期化,镜像 `03_modules/` | P2 迁移完成后整体删除(阶段6) |
