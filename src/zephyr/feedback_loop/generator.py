# [BLUEPRINT] MOD-FBL-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: skeletons 参数
#   fields: 参数 skeletons，类型注解 dict[str, str] | None
#   code: generator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: target_root 参数
#   fields: 参数 target_root，类型注解 str | None
#   code: generator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate
#   name_en: generate
#   intro: 执行骨骼代码生成.
#   desc: 执行骨骼代码生成. 返回 (created, skipped, errors). 从 _gen_inherited.py 的 __main__ 块拆分而来. target_roo…；源码 L91-L148
#   inputs: skeletons target_root
#   outputs: tuple[int, int, int]
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: CLI 入口 - 与 _gen_inherited.
#   desc: CLI 入口 - 与 _gen_inherited.py 的 __main__ 块行为一致.；源码 L151-L156
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: tuple[int, int, int]
#   name_en: tuple[int, int, int]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §3-§9
# [MODULE] zephyr.feedback_loop.generator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] blueprint.md §0; zephyr.feedback_loop 内部模块; zephyr.trading
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] MOD-FEEDBACK_LOOP 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeedbackLoopError
# [TESTS] tests/feedback-loop/
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

Generator

依据: 蓝图 MOD-FEEDBACK_LOOP §3-§9

# [ALGO_FLOW]
# I1: skeletons(相对路径→代码骨架 dict, 默认 SKELETONS 模板全集) + target_root(写入根, 默认 BASE=包目录, 测试传 tmp_path 隔离)
# A1: _write_one(目标已存在→skipped; 否则 temp-file(pid 后缀)+os.replace 原子写入→created; PermissionError/异常→error)
# A2: ThreadPoolExecutor(max_workers=8) 并行写盘 + as_completed 聚合 created/skipped/errors 三态计数
# O1: (created, skipped, errors) 三元组
# [/ALGO_FLOW]
"""


# SRC-0068a: 从 _gen_inherited.py 拆分 - 代码生成执行器

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from zephyr.feedback_loop.template import SKELETONS

__all__ = ["BASE", "generate", "main"]


BASE: Final[str] = os.path.join(os.path.dirname(__file__), "")


def generate(skeletons: dict[str, str] | None = None, target_root: str | None = None) -> tuple[int, int, int]:
    """执行骨骼代码生成. 返回 (created, skipped, errors).

    从 _gen_inherited.py 的 __main__ 块拆分而来.
    target_root: 写入根目录（默认 BASE=包目录）；测试须传 tmp_path 隔离——
    2026-08-18 第八统筹治本：test_generates_new_files 未传 target 致
    src/zephyr/feedback_loop/subdir/test_file.py 泄漏进真源树（ORPHAN-MODULE 门禁实证拦截）。

    """
    if skeletons is None:
        skeletons = SKELETONS

    if target_root is None:
        target_root = BASE
    created = 0
    skipped = 0
    errors = 0
    pid = os.getpid()

    def _write_one(rel_path: str, code: str) -> tuple[str, str]:
        target = os.path.normpath(os.path.join(target_root, rel_path))
        target_dir = os.path.dirname(target)
        os.makedirs(target_dir, exist_ok=True)
        if os.path.exists(target):
            return ("skipped", rel_path)
        tmp_path = f"{target}.{pid}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(code.strip() + "\n")
            os.replace(tmp_path, target)
            return ("created", rel_path)
        except PermissionError:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return ("error", rel_path)
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            return ("error", rel_path)

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(_write_one, rel_path, code): rel_path for rel_path, code in skeletons.items()}
        for future in as_completed(futures):
            status, _ = future.result()
            if status == "created":
                created += 1
            elif status == "skipped":
                skipped += 1
            else:
                errors += 1

    return created, skipped, errors


def main() -> None:
    """CLI 入口 - 与 _gen_inherited.py 的 __main__ 块行为一致."""

    created, skipped, errors = generate()

    print(f"TASK-0003: Created {created}, skipped {skipped}, errors {errors} (total {len(SKELETONS)})")


if __name__ == "__main__":
    main()
