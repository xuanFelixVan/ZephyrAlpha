---
module_id: KE-039----------code-transformat-005
status: active
title: 6.7a 代码变换保真铁律（Code Transformation Fidelity Rule）
category: agent_instruction
ttl: permanent
doc_type: knowledge_entry
---

# 6.7a 代码变换保真铁律（Code Transformation Fidelity Rule）

6.7a 代码变换保真铁律（Code Transformation Fidelity Rule）

> **v1.0.0（2026-05-04）**：触发条件——AI 对任何 `.py` 文件执行"解析→修改→写回"操作时。对标 Instagram/Meta LibCST（Concrete Syntax Tree——无损代码变换）+ ruff safe/unsafe 修复分类（涉及注释时标记 unsafe，拒绝自动应用）。

AI 对 `.py` 文件执行代码变换（添加 docstring、修改 import、重构函数签名等）时，**MUST 使用无损工具**，禁止使用 `ast.unparse()` 重写文件。

- **禁止**：`ast.parse()` → 修改 AST → `ast.unparse()` → `write_text()` — 丢失行内注释、自定义格式
- **必须**：`libcst.parse_module()` → `CSTTransformer` → `tree.code` → `write_text()` — 100% 保留注释和格式
- **现成工具**：`python scripts/governance/_shared/libcst_docstring_adder.py` — 无损添加 docstring
- **自动修复**：`python scripts/governance/d11_compliance/validate_script_quality.py --fix` — 一键修复 D-C-02 违规（使用 LibCST）
- **质量门禁**：`validate_script_quality.py` D-G-06 检查器自动检测 `ast.unparse()` + 文件写入
- **专业参考**：Instagram/Meta LibCST → Concrete Syntax Tree / ruff PR #24270 → safe/unsafe fix classification
- **通俗解释**：`ast.unparse()` 就像 JPEG——每次保存都丢信息。LibCST 就像 PNG——无损保存，注释一个字不丢
