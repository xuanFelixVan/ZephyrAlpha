---
module_id: KE-governance-mth-008_ssot________single_sou-003
title: MTH-008：SSoT 冲突裁决协议（Single Source of Truth Conflict Arbitration）
category: governance
---

# MTH-008：SSoT 冲突裁决协议（Single Source of Truth Conflict Arbitration）

MTH-008：SSoT 冲突裁决协议（Single Source of Truth Conflict Arbitration）

当两个或以上规则文件对同一概念作出不同声明（编号冲突、字段定义冲突、职责重叠）时，必须使用本协议判定真源（SSoT）。

- **裁决四步法**：
  1. **时序优先**（Temporal Priority）：谁先注册/定义该概念？——先注册的文件拥有初始权。查 frontmatter `date` 或 `created_at` 字段
  2. **职责归属**（Semantic Ownership）：该概念的语义属于哪个文件的自然领域？——`ABS-`（行为边界）的语义自然属于 PS-STD-003（行为边界标准），不是 PS-STD-009（规则治理标准——尽管它包含生命周期内容，但编号空间 ABS- 不属于治理领域）。语义匹配度 = 该概念名是否直接描述了该文件的 core purpose
  3. **专业先例**（Professional Precedent）：专业机构在同类场景中怎么判定？——IETF RFC 编辑在发现编号冲突时，已有的 RFC 号不收回，新文档用更高的未使用号。OWASP 发现项目缩写冲突时，后来者必须重命名
  4. **裁决输出**（Arbitration Output）：输出明确的三句话：
     - 真源文件是 X（module_id + 绝对路径）
     - 冲突文件是 Y（module_id + 绝对路径）
     - 修复方式：Y 迁移到独立编号空间 / 删除 Y 中的重复定义 / Y 改为引用 X

- **裁决不可协商部分**：
  - 编号空间（如 `ABS-`、`LFC-`、`MTH-`）只属于一个文件。不存在"两个文件共享一个编号前缀"
  - 字段定义（如 `status`、`stability`）的真源是 PS-STD-001。其他文件只引用，不重定义
- **违反后果**：两个 AI session 读到不同的 `ABS-001` 定义 → 执行不同的规则 → 工程质量不可预测
- **验证方式**：裁决后执行 `grep "ABS-" --files-with-matches` 是否只返回 PS-STD-003？如果在其他文件中仍有 `ABS-` 引用，裁决未执行完毕
- **专业参考**：IETF RFC Editor → Publication Process（发现编号冲突时已发布 RFC 不变，新文档分配更高号）/ OWASP Project Governance → Project Naming Conflicts（后来者必须重命名）/ ISO/TC 37 → Terminology Unification（术语统一——同一概念只有一个标准定义）
