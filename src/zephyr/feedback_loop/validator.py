# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

# [MODULE] zephyr.feedback_loop.validator

# [INVARIANTS] MOD-INF-010 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.feedback_loop 内部模块; zephyr.runtime

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] FeedbackLoopError

# [TESTS] tests/feedback_loop/

"""[BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

Validator

依据: 蓝图 MOD-INF-010 §3-§9

"""


# SRC-0068a: 从 _gen_inherited.py 拆分 - 骨骼文件验证器






import os





from zephyr.feedback_loop.template import SKELETONS





__all__ = ["validate_all", "validate_one", "missing_files", "BASE"]





BASE = os.path.join(os.path.dirname(__file__), "")








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


