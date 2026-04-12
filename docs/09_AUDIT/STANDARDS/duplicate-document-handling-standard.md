---

module_id: 09_AUDIT_STANDARDS_DUPLICATE_DOCUMENT_HANDLING_001

version: 1.0.0

status: Active

created_date: 2026-04-08

last_updated: 2026-04-08

owner: 文档治理系统

standard_type: 治理标准

applicable_scope: 全库 Markdown 文档（重复/重叠/多版本）

related_documents:

  - ./DOCUMENT_REPOSITORY_LAYOUT_STANDARD.md

  - ./DOCUMENT_VERSION_NAMING_STANDARD.md

  - ./DOC_REFERENCE_STANDARD.md

  - ../STATE/STRICT_ORPHAN_FILES_REPORT_20260408.md

layer: layer_09
responsibility: "处理DUPLICATE_DOCUMENT_HANDLING_STANDARD相关业务"
---





# 重复文档处理标准（canonical 裁决）



> **目的**：当仓库内出现“同题重复/多版本并存/迁移重叠（overlap）”时，提供一致的裁决规则，确保读者只看到一个权威入口，同时保留可追溯性。



## 1. 核心原则（机构常用）



1. **唯一权威（canonical）**：同一主题只允许一个可对外引用的权威入口。  

2. **可追溯**：非 canonical 不直接删除，必须保留“指向 canonical 的重定向声明”。  

3. **入口收敛**：所有 `INDEX.md`/SITEMAP/导航页最终只指向 canonical。  

4. **渐进收敛**：先“止血”（重定向 + 索引收敛），后“整形”（合并/重写/归档清理）。  



## 2. 重复类型



- **完全重复**：内容几乎一致，仅路径/版本/命名不同。  

- **部分重复**：主体相同，但各自夹带增量小节。  

- **同题不同写法**：主题一致但结构不同，容易误判为两套机制（高风险）。  

- **重复但语境不同**：例如“蓝图”与“施工/技术规格”重叠，但服务阶段不同（允许存在，但需声明）。  



## 3. canonical 裁决优先级（从高到低）



1. **权威栈位置优先**：`01_FRAMEWORK/` > 其他实施目录 > `06_ARCHIVE/`。  

2. **状态/版本优先**：`status: Active`、版本更高、更新时间更近。  

3. **可达性优先**：被入口索引引用、被引用更多者优先。  

4. **门禁完整度优先**：职责边界/契约/验收/限制更完整者优先。  

5. **命名与规范优先**：`module_id`、路径与命名更符合标准者优先。  



> **输出要求**：每次裁决必须留下“裁决记录”（最小：在非 canonical 的重定向声明中写明原因与日期）。



## 4. 非 canonical 的标准处置



### 4.1 重定向声明（必须）



在非 canonical 文件顶部加入（示例，建议作为固定模板）：



```markdown

> **状态**：Superseded（已被替代）  

> **canonical**：`<relative_path_to_canonical.md>`（替换为可点击的相对路径链接）  

> **原因**：重复/合并/迁移重叠  

> **最后维护**：YYYY-MM-DD  

> **备注**：本文件仅用于历史追溯，不再更新。

```



### 4.2 是否保留正文



- **完全重复**：保留 3–10 行摘要，其余可移除或整体迁入归档目录。  

- **部分重复**：先把差异并入 canonical，再让非 canonical 只保留“差异摘要 + 指向 canonical”。  

- **同题不同写法**：以 canonical 为唯一入口重写整合；其余标记为历史版本。  



## 5. 归档与清理窗口



- 建议归档位置：`docs/06_ARCHIVE/`（尤其 `overlap_*`、迁移中间产物、旧版报告）。  

- 建议追溯窗口：30/90/180 天（由 Owner 决策）。到期后可删除，但必须在索引记录处置日期与理由。  



