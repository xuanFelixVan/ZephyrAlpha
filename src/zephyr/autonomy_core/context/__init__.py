"""[A_module] module_id=MOD-AUTONOMY_CORE_context | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

Context 子包（MOD-CONTEXT_ENGINE 蓝图）：上下文引擎核心组件 + 工具/playground 辅助层。
- context_*.py：上下文引擎核心组件（assembler/budget/evaluator/injector/optimizer/pipeline...）
- ce_*.py：上下文引擎工具/playground/CLI 辅助层（bootstrap/explain_cli/playground_v2/vibe_shortcuts）
ARCH-033子目录命名治本：原 ce/ 子包合并至本包（ce/ 是自创缩写，违反 gov_doc_003_directory_semantics R1 缩写必除）。
"""
