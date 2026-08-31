# [BLUEPRINT] MOD-FBL-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rel_path 参数
#   fields: 参数 rel_path，类型注解 str
#   code: validator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① missing_files
#   name_en: missing_files
#   intro: 返回尚未生成的骨骼文件列表.
#   desc: 返回尚未生成的骨骼文件列表.；源码 L92-L103
#   inputs: 无参数
#   outputs: list[str]
# - id: A2
#   name_zh: ② validate_one
#   name_en: validate_one
#   intro: 验证单个骨骼文件是否存在.
#   desc: 验证单个骨骼文件是否存在.；源码 L106-L111
#   inputs: rel_path
#   outputs: bool
# - id: A3
#   name_zh: ③ validate_all
#   name_en: validate_all
#   intro: 验证所有骨骼文件的完整性.
#   desc: 验证所有骨骼文件的完整性. 返回 {rel_path: exists}；源码 L114-L122
#   inputs: 无参数
#   outputs: dict[str, bool]
# 层: 输出
# - id: O1
#   name_zh: list[str]
#   name_en: list[str]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §3-§9
# [MODULE] zephyr.feedback_loop.validator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] blueprint.md §0; zephyr.feedback_loop 内部模块; zephyr.trading
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MOD-FEEDBACK_LOOP 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeedbackLoopError
# [TESTS] tests/feedback-loop/
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

Validator

依据: 蓝图 MOD-FEEDBACK_LOOP §3-§9

"""


# SRC-0068a: 从 _gen_inherited.py 拆分 - 骨骼文件验证器

import os

from zephyr.feedback_loop.template import SKELETONS

__all__ = ["BASE", "missing_files", "validate_all", "validate_one"]


BASE: Final[str] = os.path.join(os.path.dirname(__file__), "")


def missing_files() -> list[str]:
    """返回尚未生成的骨骼文件列表."""

    missing: list[str] = []

    for rel_path in SKELETONS:
        target = os.path.normpath(os.path.join(BASE, rel_path))

        if not os.path.exists(target):
            missing.append(rel_path)

    return missing


def validate_one(rel_path: str) -> bool:
    """验证单个骨骼文件是否存在."""

    target = os.path.normpath(os.path.join(BASE, rel_path))

    return os.path.exists(target)


def validate_all() -> dict[str, bool]:
    """验证所有骨骼文件的完整性. 返回 {rel_path: exists}"""

    result: dict[str, bool] = {}

    for rel_path in SKELETONS:
        result[rel_path] = validate_one(rel_path)

    return result
