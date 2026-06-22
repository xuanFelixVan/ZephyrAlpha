---
module_id: KE-040------------file-deletion-q-006
status: active
title: 6.8 文件删除质量对比预检（File Deletion Quality Comparison Gate）
category: agent_instruction
---

# 6.8 文件删除质量对比预检（File Deletion Quality Comparison Gate）

6.8 文件删除质量对比预检（File Deletion Quality Comparison Gate）

> **v1.0.0（2026-05-02）**：触发条件——任何"删除文件"的操作（无论是 AI 主动建议还是 Owner 指令）。对标 ITIL Change Enablement → Change Impact Assessment（变更影响评估——删除是不可逆操作，删除前必须充分评估影响）。
>
> **⚠️ 与 GOV-DOC-007 的分工**：[GOV-DOC-007 trae_029_doc_operation_security.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_029_doc_operation_security.yaml) 定义删除前的**操作安全门禁**（三问三步——防断链、保护锚点）。本节定义**质量保全门禁**（两步预检——防删掉更好的版本）。两者互补不重叠，删除操作必须**同时通过两道门禁**。规则文件删除还需遵守 [PS-STD-009 rule_lifecycle_and_change_standard.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/meta/rule_lifecycle_and_change_standard.yaml) 的废弃状态机。

AI 在提议或执行文件删除操作前，MUST 完成以下两步预检流程。缺失任何一步视为操作不合规。

- **执行流程（两步，顺序不可颠倒）**：

  **第一步：内容重复性验证（Content Duplication Check）**
  - 目标文件的内容是否已在项目其他文件中被完全覆盖？
  - 检查维度：
    - 知识点覆盖：目标文件的每一个知识点块，是否在其他文件中有等价或更优的描述？
    - 功能性覆盖：目标文件承担的功能（如决策框架、原则定义、映射表），是否有其他文件承担相同功能？
    - 引用链覆盖：现有引用目标文件的其他文件，在删除后引用的内容是否仍可获取？
  - 输出：逐块标注"已覆盖 / 部分覆盖 / 未覆盖"+"覆盖来源文件路径"

  **第二步：质量对比（Quality Comparison）——"谁更好？"**
  - 对第一步中标记为"已覆盖"的知识点块，逐块进行质量对比：
    - **专业深度**：谁的论述更完整？谁引用了更多专业机构实践？
    - **结构化程度**：谁的定义更精确（可量化枚举 > 自然语言描述）？谁的阈值/标准更明确？
    - **维护友好性**：谁的格式更适合 AI 后续施工（YAML > 结构化 Markdown > 散落 prose）？
    - **时效性**：谁的内容更新、更符合当前架构决策？
    - **可操作性**：谁的内容能直接指导施工（含具体步骤/检查清单/量化指标）？
  - 输出：每个知识块的质量对比结论——"保留方更优 / 被删方更优 / 等价"

- **决策规则**：
  - 所有知识块均"已覆盖" + 覆盖方质量"更优或等价" → ✅ 可以安全删除
  - 存在"部分覆盖"或"未覆盖"的知识块 → ⚠️ 先提取该知识块到正确目标位置，再删除
  - 存在"已覆盖但被删方更优"的知识块 → 🔴 **禁止删除**——被删方内容更好，应改为：用被删方内容升级覆盖方，或保留被删方并改状态为 `active`
  - 第二步未执行 → 🔴 操作不合规，视为违反本规则

- **Session Log 记录要求**：
  - 每次文件删除决策必须在 Session Log 中记录：
    1. 两步预检的完整结论（每个知识块的覆盖状态 + 质量对比结果）
    2. 最终决策及理由（删除 / 提取后删除 / 保留并升级 / 保留）
    3. 确认"引用链"——删除后是否有其他文件的链接会断裂

- **专业参考**：ITIL Change Enablement → Change Impact Assessment（变更影响评估——删除前必须评估对系统其他部分的影响）/ Git → `git rm` vs `rm`（可追溯删除 vs 物理删除——删除决定本身应留下审计记录）/ ISO 42001 §8 → AI system impact assessment（AI 系统影响评估——AI agent 主动删除文件前必须做影响评估）
