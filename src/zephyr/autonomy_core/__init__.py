# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [TTL] permanent
"""

[A_module] module_id=MOD-AUTONOMY_CORE | layer=infrastructure | stability=evolving | safety=L | ai_autonomy=ai_modifiable

autonomy_core 包结构指引（ARCH-033 治本）：
- skill_*.py -> skills/ 子包（技能子系统，MODULE_LIST 封闭集合）
- context_*.py + ce_*.py -> context/ 子包（上下文引擎子系统；ce_*.py 是工具/playground 层，原 ce/ 子包已合并）
- 其余独立功能模块平铺根目录（命名即分类，无前缀簇不强行归位）

查找方式：Glob src/zephyr/autonomy_core/**/*.py 实时列出所有模块
新建模块：按文件名前缀归位对应子包；无前缀的独立模块放根目录平铺

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求（无数据输入）
#   fields: docstring 内 ARCH-033 包结构指引（skill_*→skills/、context_*/ce_*→context/、其余平铺）
#   code: src/zephyr/autonomy_core/__init__.py L1-10
# 层: 算法
# - id: A1
#   name_zh: ① 子模块白名单导出与归位指引
#   name_en: __init__（模块级 __all__）
#   intro: 声明根包 13 个子模块名，并用 docstring 告诉新人模块该往哪个子包放
#   desc: docstring 给出命名前缀归位规则与 Glob 查找方式（L3-9）；__all__ 列出 13 个根模块名（L12-26），无导入无初始化逻辑
#   inputs: I1
#   outputs: 13 个子模块名导出表
# 层: 输出
# - id: O1
#   name_zh: 根包子模块导出表
#   name_en: __all__
#   intro: agent_observability/spec_engine/trigger_router 等 13 个根模块名对外可见
#   downstream: skills/context 子包及平铺子模块（如 MOD-AUTONOMY_CORE_context）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# NOTE(P1W12 2026-08-25): scaffold 注册器两次写入行首 eager import + 类名 append
# （#ARCH-228 同款 bug 复发），按本包"纯模块名导出"约定（上文 docstring
# ARCH-033：无导入无初始化逻辑）归一为模块名条目。
__all__ = [
    "agent_observability",
    "agentic_drift_guard",
    "ai_ops_autonomy_card",
    "all_skill_modules",
    "autonomy_level_registry",
    "drift_semantic_reviewer",
    "file_autoregister",
    "ide_watcher",
    "killswitch_response_levels",
    "non_ai_boundary_guard",
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
