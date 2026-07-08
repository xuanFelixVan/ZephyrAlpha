"""[A_module] module_id=MOD-AUTONOMY_CORE | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

autonomy_core 包结构指引（ARCH-033 治本）：
- skill_*.py -> skills/ 子包（技能子系统，MODULE_LIST 封闭集合）
- context_*.py + ce_*.py -> context/ 子包（上下文引擎子系统；ce_*.py 是工具/playground 层，原 ce/ 子包已合并）
- 其余独立功能模块平铺根目录（命名即分类，无前缀簇不强行归位）

查找方式：Glob src/zephyr/autonomy_core/**/*.py 实时列出所有模块
新建模块：按文件名前缀归位对应子包；无前缀的独立模块放根目录平铺
"""

__all__ = [
    "agent_observability",
    "all_skill_modules",
    "file_autoregister",
    "ide_watcher",
    "phase_planner",
    "progressive_disclosure_injector",
    "prompt_registry",
    "self_evolution_fidelity_gate",
    "skill_rbac_registry",
    "spec_engine",
    "trigger_router",
    "vibe_coding_quality_gate",
    "__main__",
]
