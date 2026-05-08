---
module_id: KE-module_blu-o__ai___________b5-o01_o08-008
title: O. AI 施工模式库与反模式（B5-O01~O08）
category: module_blueprint
---

# O. AI 施工模式库与反模式（B5-O01~O08）

O. AI 施工模式库与反模式（B5-O01~O08）

> **最前沿的盲点**：AI需要被教"在这个系统中应该怎么做模块"+"绝对不要做什么"。这是氛围编程的"风格指南"——不是代码lint，而是设计决策lint。

| 盲点 ID | 缺失内容 | 氛围编程社区对标 |
|---------|---------|---------------|
| B5-O01 | **Module Template System（模块模板系统）**——AI创建新模块时自动从模板生成：`abc→lifecycle→event_handler→config→tests` | `cookiecutter` / Copilot Workspace |
| B5-O02 | **Anti-Patterns Catalog（反模式目录）**——"在这个系统中绝对不要做什么"——如：不要绕过EventBus直接import其他模块的内部函数 | Google Code Smells / Refactoring.Guru |
| B5-O03 | **Design Decision Tree（设计决策树）**——"我应该用EventBus还是直接调用？"→决策流程图→AI可执行规则 | The Architecture Decision Record (ADR) |
| B5-O04 | **Error Handling Patterns by Module Type（按模块类型的错误处理模式）**——数据模块:重试+降级→静态值；交易模块:重试1次→报警→拒绝 | Netflix Error Handling Taxonomy |
| B5-O05 | **Module Naming Convention Enforcer（模块命名规范执行器）**——`lXX_function_module_name` 强制一致——防止AI创造不一致的名字 | PEP 8 + ZephyrAlpha Naming Spec |
| B5-O06 | **Code Ownership Manifest（代码所属声明）**——每个py文件声明：AI施工 % vs Owner手动 % vs AI自修复 %——量化的"谁写的" | GitHub CODEOWNERS |
| B5-O07 | **AI Confidence Annotation（AI信心标注）**——AI在自己写的代码中标注信心分数(0-1)——低信心代码标注为REVIEW_NEEDED | Copilot Confidence / Claude Artifacts |
| B5-O08 | **Progressive Code Review Depth（渐进代码审查深度）**——AI信心>0.9→轻审(仅lint+safety)；0.5-0.9→中审(+contract test)；<0.5→重审(+full test suite+Owner review) | Google CR+Review Levels |

---
