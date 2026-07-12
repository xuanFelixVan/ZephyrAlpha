from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §3-§9
# [MODULE] zephyr.feedback_loop.generator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS] blueprint.md §0; zephyr.trading.feedback_loop 内部模块; zephyr.trading
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] MOD-FEEDBACK_LOOP 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FeedbackLoopError
# [TESTS] tests/feedback-loop/
# [A_module] module_id=MOD-UNK_generator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

Generator

依据: 蓝图 MOD-FEEDBACK_LOOP §3-§9

"""


# SRC-0068a: 从 _gen_inherited.py 拆分 - 代码生成执行器

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from zephyr.feedback_loop.template import SKELETONS

__all__ = ["BASE", "generate", "main"]


BASE: Final[str] = os.path.join(os.path.dirname(__file__), "")


def generate(skeletons: dict[str, str] | None = None) -> tuple[int, int, int]:
    """执行骨骼代码生成. 返回 (created, skipped, errors).

    从 _gen_inherited.py 的 __main__ 块拆分而来.

    """
    if skeletons is None:
        skeletons = SKELETONS

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
        except Exception:
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
