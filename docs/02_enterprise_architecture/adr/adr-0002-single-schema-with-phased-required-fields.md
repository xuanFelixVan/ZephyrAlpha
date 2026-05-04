---
module_id: ADR-0002
title: 采用单一 frontmatter schema + 分阶段必填闸门
doc_type: adr
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R8, R12
related_open_questions: []
tags:
- metadata-contract
- frontmatter
- governance
- document-standard
summary: 所有文档共用同一套完整 frontmatter schema；不同成熟度（status）下必填字段不同，schema 本身不分叉。取代早期"沙盒档/正式档双
  schema"设计。
date: '2026-04-22'
ttl: permanent
---

# ADR-0002: 采用单一 frontmatter schema + 分阶段必填闸门

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-17
- **拍板日期**：2026-04-17
- **被谁取代**：—
- **取代了谁**：`discussion-document-standard.md` v1.0.0 的"沙盒档/正式档双轨"条款（已作为 v1 方案废弃）

## 2. 背景与问题（Context）

在 v1.0.0 的 `discussion-document-standard.md` 中，曾采用**两套 frontmatter schema 并存**的方案：

- **沙盒档**：3~5 个最小字段（`title`, `doc_type`, `status`）
- **正式档**：12+ 个完整字段（含 `module_id`, `version`, `owner`, `classification`, `language`, `summary` 等）

设计初衷：让讨论期文档负担小，只在升格到 canonical 时强制补齐。

**但质疑出现**：这种"双 schema"不是机构标准做法。经对标调研后发现：

- Google、IETF、IEEE、ISO 等机构都采用"单一 schema + status 驱动"
- 金融机构（JPMorgan、高盛）与咨询机构（McKinsey、BCG）都采用"单一 schema + 分阶段必填闸门"
- **双 schema** 违反机构"单一数据契约"原则，会导致工具链分叉、升格迁移、AI 写作混乱

**相关讨论**：`architecture-rationale-log.md` Stage 14（本轮埋雷审查）；结论 R8（现在应先做格式规范化）、R12（元数据契约已是机构标准）

## 3. 考虑过的方案（Options Considered）

### 方案 A：保持 v1.0.0 的沙盒档/正式档双 schema

- **优点**：
  - 起草阶段字段负担小
  - 对新手/非专业写作者友好
- **缺点**：
  - ❌ 升格时需要**字段迁移**（补齐缺失字段）
  - ❌ 工具链需要**多一个分支判断**（pre-commit、索引、向量化入库都要判断 schema 版本）
  - ❌ AI 写作**心智负担**（每次需要先判断用哪套 schema）
  - ❌ **违反机构"单一数据契约"原则**
  - ❌ 切换回单 schema 时成本随文档量指数级上升
- **机构案例**：**没有主流机构采用**此方案

### 方案 B：所有文档都必须全字段填写（不分阶段）

- **优点**：
  - 极致统一
  - 工具链最简单
- **缺点**：
  - 起草阶段心理负担过重
  - 草稿期字段填得都是占位值，意义不大
- **机构案例**：少数严格合规机构（如制药、航空）采用

### 方案 C：单一 schema + 分阶段必填闸门（**本 ADR 选定**）

- **优点**：
  - ✅ **单一 schema，工具链无分叉**
  - ✅ 起草阶段门槛低（`draft` 只要 4 字段）
  - ✅ 升格**只改 `status` 值**，不改 schema，不做字段迁移
  - ✅ 符合机构主流做法
  - ✅ pre-commit hook 只需按当前 status 校验必填字段
  - ✅ 未来 machine-readable schema 好做（单一 JSON Schema 即可）
- **缺点**：
  - 需要明确每个 status 对应的必填字段闸门
  - 初期需要少量迁移现有文档（但实际工作量极小，因为现有文档都已经填了完整字段）
- **机构案例**：Google、IETF RFC、IEEE、ISO、JPMorgan、高盛、McKinsey、BCG

## 4. 决策（Decision）

**最终选择：方案 C —— 单一 schema + 分阶段必填闸门**

### 4.1 完整 schema

所有文档共用同一套 frontmatter：

```yaml
module_id: <DOMAIN>-<TYPE>-<NNN>
title: 文档标题
doc_type: <受控词表值>
status: draft | in_discussion | review_ready | active | accepted | superseded | deprecated
version: 1.0.0
layer: cross_layer | enterprise_architecture | ...
owner: ZephyrAlpha-Owner
classification: internal | confidential | public
language: zh | en
created_by: human | agent
valid_from: YYYY-MM-DD

# 可选：superseded_by / supersedes / related_rationale / related_open_questions / sources / tags
summary: 一段话摘要
```

### 4.2 分阶段必填闸门

| status | 必填字段（最小集） |
|--------|------------------|
| `draft` | `title`, `doc_type`, `status`, `language`（4 个） |
| `in_discussion` / `review_ready` | 上述 + `module_id`, `owner`, `created_by`, `valid_from`, `summary`（9 个） |
| `active` / `accepted` | **全部完整字段**（12+ 个） |
| `superseded` / `deprecated` | 原有字段 + 必填 `superseded_by` |

### 4.3 单一真源标准文档

本 ADR 落地为 `19_development_workspace/structure-and-mapping/discussion-document-standard.md` v2.0.0。

## 5. 后果（Consequences）

### 正面后果

- 工具链（pre-commit、索引、入库）只认一套 schema
- AI 写作只需记一套字段表
- 升格只是改 `status`，没有迁移成本
- 符合机构主流，未来对标/招聘/协作无障碍
- 便于未来生成 machine-readable JSON Schema

### 负面后果 / 权衡

- 草稿期字段少于正式档，但可读性没有明显下降
- 需要 pre-commit hook 按 status 动态校验必填字段（工程工作量小）
- 需要一次性废弃 v1.0.0 "沙盒档"措辞（已在 standard v2.0.0 完成）

### 未来需要重新审视的触发条件

- 出现某个 domain 需要独立 schema（如极高敏感度文档需额外字段）
- 机器学习类资产（如模型卡片）需要专用扩展字段
- 外部合规要求强制字段变更

## 6. 落地动作（Implementation）

- [x] 重写 `discussion-document-standard.md` v2.0.0，废弃"沙盒档/正式档"措辞
- [x] 明确 `doc_type` 受控词表
- [x] 明确 `module_id` 命名规范
- [ ] 更新 pre-commit hook（`doc_guard_pre_commit.py`）按 status 动态校验必填字段
- [ ] 未来生成 machine-readable `frontmatter-schema.json`

## 7. 参考

- 相关 ADR：ADR-0001（唯一真源）、ADR-0003（双 AI 工作流）
- 相关文档：
  - `19_development_workspace/structure-and-mapping/discussion-document-standard.md` v2.0.0
  - `02_enterprise_architecture/architecture-rationale-log.md` Stage 14
- 外部参考：
  - IETF RFC 2119 "Key words for use in RFCs"
  - Google Docs internal metadata standard（未公开但业内共识）
  - ISO/IEC 11179 "Metadata Registries"

## 8. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-04-17 | 初版：基于埋雷审查发现"双 schema"非机构标准，改为"单一 schema + 分阶段必填闸门"。 |
