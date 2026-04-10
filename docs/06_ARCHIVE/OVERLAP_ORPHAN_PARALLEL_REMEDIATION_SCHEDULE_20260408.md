---
module_id: ARCHIVE_OVERLAP_ORPHAN_SCHEDULE_20260408
version: 1.0.0
status: Active
created_date: 2026-04-08
last_updated: 2026-04-08
owner: 文档治理系统
standard_type: 治理排期
applicable_scope: overlap_* canonical 声明补全 + 严格孤儿 A 类入口补齐（并行）
compliance_level: 专业标准
---

# overlap 与严格孤儿 A 类：按主题批次 + 并行排期（2026-04-08）

> **目的**：用专业机构常见节奏，**避免一次性改几百个文件**，同时保证每条线可验收、可复跑门禁（如 L1 链接扫描）。

## 1. 两条并行轨道（双轨）

| 轨道 | 对象 | 建议动作 | 验收 |
|------|------|----------|------|
| **轨道 A** | `docs/06_ARCHIVE/overlap_*.md`（约 228 篇，不含模板） | 按 **主题批次** 补 **canonical 声明**（模板见下文），必要时回填 `canonical_path` | 每批次改完后 **L1：Invalid links = 0**；索引可发现 |
| **轨道 B** | [`STRICT_ORPHAN_FILES_REPORT_20260408.md`](../09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md) 中 **A 类（应挂入口）** | 按 **业务目录/波次** 在对应 `INDEX.md` 等入口 **增加链接**（只索引、大段不改正文） | 每波次后复跑严格孤儿统计或抽样核对入度；**L1 = 0** |

**并行原则**：同一周期内可同时推进 A、B，但**单次 PR/提交**建议只包含「一个主题批次（轨道 A）」或「一个目录波次（轨道 B）」，便于评审与回滚。

## 2. 轨道 A：`overlap_*` 按主题分批（建议）

> 以下为 **推荐主题顺序**（可按实际 canonical 裁决微调）。每批 **15～30 个文件** 为宜；超大主题可拆子批。

| 批次 | 主题（文件名模式/说明） | 典型 canonical 归属 | 备注 |
|------|-------------------------|---------------------|------|
| A1 | **文档治理 / 元数据 / 命名**（如 `overlap_DOCUMENT_*`、`overlap_*METADATA*`、`overlap_*NAMING*`） | `docs/09_AUDIT/STANDARDS/`、`docs/10_GOVERNANCE_COMPLIANCE/` 等 | 与审计标准对齐 |
| A2 | **架构 / 蓝图 / Gap**（如 `overlap_ARCHITECTURE_*`、`overlap_*GAP*`、`overlap_*BLUEPRINT*` 中偏架构者） | `docs/01_FRAMEWORK/`、对应施工蓝图 | 先对 `ARCHITECTURE.md` 与蓝图映射 |
| A3 | **Layer 专项审计报告**（`overlap_LAYER*_DEEP_AUDIT*`、`overlap_LAYER*_FULL_AUDIT*`） | 对应 Layer 蓝图或 `09_AUDIT/REPORTS` 正式报告 | 审计类优先指向 **报告真源** 或 Layer 索引 |
| A4 | **数据 / 目录 / Catalog**（`overlap_DATA_*`、`overlap_*CATALOG*`、`overlap_*DIRECTORY*`） | `docs/01_FRAMEWORK/DATA_SOURCE_LAYER_BLUEPRINT.md`、`docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/` | 与数据源层一致 |
| A5 | **策略 / 执行**（`overlap_STRATEGY_*`、`overlap_*EXECUTION*`、`overlap_LIVE_*`） | `docs/03_TRADING_TACTICS/`、`docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/` | 与 STRATEGY / 执行回测蓝图对齐 |
| A6 | **AI / 舆情 / 工作流**（`overlap_AI_*`、`overlap_SENTIMENT_*`、`overlap_*WORKFLOW*`） | `docs/10_AI_WORKFLOW/`、`docs/01_FRAMEWORK/` 相关蓝图 | 与舆情/AI 蓝图对齐 |
| A7 | **因子 / 组合**（`overlap_*FACTOR*`、`overlap_*PORTFOLIO*`、`overlap_AI_FACTOR_*`） | `docs/02_FACTOR_LIBRARY/` 对应子模块蓝图 | 已有个别 overlap 已指向业务真源，可复用模式 |
| A8 | **杂项 / 兜底**（剩余 `overlap_*`） | 按文题个案裁决 `canonical_path=TBD` → 再分批填满 | 台账登记优先于硬删 |

**单批操作 checklist（执行人自用）**

1. 选定本批文件列表（可脚本按前缀筛出）。  
2. 对每个文件顶部粘贴 [`OVERLAP_CANONICAL_POINTER_TEMPLATE.md`](./OVERLAP_CANONICAL_POINTER_TEMPLATE.md) 片段，填 `canonical_path`（或暂 `TBD` 并在本目录台账备注）。  
3. 运行 L1 扫描；若有无效链接，只修本批引入的链接。  
4. 提交说明写清：**批次编号 + 文件数 + 主题**。  

## 3. 轨道 B：严格孤儿 **A 类** 按目录波次（建议）

> A 类定义见 [`STRICT_ORPHAN_FILES_REPORT_20260408.md`](../09_AUDIT/STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md)。**不要**单次把 568 篇全挂进一个 INDEX。

| 波次 | 目录/范围（示例） | 挂接入口（示例） | 每波建议规模 |
|------|-------------------|------------------|--------------|
| B1 | `docs/01_FRAMEWORK/`（含 `LAYER4_ML/`） | `docs/01_FRAMEWORK/INDEX.md` 或已有「严格孤儿挂载」小节 | 20～50 条链接/波 |
| B2 | `docs/03_TRADING_TACTICS/` | `docs/03_TRADING_TACTICS/INDEX.md` | 同上 |
| B3 | `docs/05_IMPLEMENTATION/` 各子域 | 对应子目录 `INDEX.md` | 同上 |
| B4 | `docs/07_RESEARCH/`、`docs/08_KNOWLEDGE/` | 各 `INDEX.md` / `index.md` | 同上 |
| B5 | `docs/09_AUDIT/`（报告类） | `docs/09_AUDIT/REPORTS/INDEX_GROUPED_REPORTS_20260408.md` 或分桶索引 | 大批量用分组索引，避免单页过长 |

**原则**：入口页只增加 **可点击链接**，不重写归档正文；与 overlap 轨道 **同一周可并行不同目录**，但单次提交仍宜「一个波次」。

## 4. 与现有入口的关系

- **归档总说明**：[`README.md`](./README.md)  
- **overlap 规则与模板**：[`overlap_INDEX_20260407_190203.md`](./overlap_INDEX_20260407_190203.md)、[`OVERLAP_CANONICAL_POINTER_TEMPLATE.md`](./OVERLAP_CANONICAL_POINTER_TEMPLATE.md)  
- **duplicates 台账**：[`../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md`](../09_ARCHIVE/duplicates/CANONICAL_POINTERS.md)  
- **重复文档标准**：[`../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md`](../09_AUDIT/STANDARDS/DUPLICATE_DOCUMENT_HANDLING_STANDARD.md)  

## 5. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0.0 | 2026-04-08 | 初版：双轨并行排期与主题批次表 |
