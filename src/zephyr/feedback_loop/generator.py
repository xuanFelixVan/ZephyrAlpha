# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

# [MODULE] zephyr.feedback_loop.generator

# [INVARIANTS] MOD-INF-010 检测-诊断-动作链不可绕过; GateQueue 全局串行; 原子写入 temp-file+os.replace()

# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__

# [CONSUMERS] blueprint.md §0; zephyr.feedback_loop 内部模块; zephyr.runtime

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] FeedbackLoopError

# [TESTS] tests/feedback_loop/

"""[BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md | §3-§9

Generator

依据: 蓝图 MOD-INF-010 §3-§9

"""


# SRC-0068a: 从 _gen_inherited.py 拆分 - 代码生成执行器






import os





from zephyr.feedback_loop.template import SKELETONS





__all__ = ["generate", "BASE", "main"]





BASE = os.path.join(os.path.dirname(__file__), "")








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





    for rel_path, code in skeletons.items():


        target = os.path.normpath(os.path.join(target_root, rel_path))


        target_dir = os.path.dirname(target)





        os.makedirs(target_dir, exist_ok=True)





        if os.path.exists(target):


            skipped += 1


            continue





        tmp_path = target + ".tmp"


        try:


            with open(tmp_path, "w", encoding="utf-8") as f:


                f.write(code.strip() + "\n")


            os.replace(tmp_path, target)


            created += 1


        except PermissionError:


            errors += 1


            if os.path.exists(tmp_path):


                try:


                    os.remove(tmp_path)


                except OSError:


                    pass


        except Exception:


            errors += 1


            if os.path.exists(tmp_path):


                try:


                    os.remove(tmp_path)


                except OSError:


                    pass





    return created, skipped, errors








def main() -> None:


    """CLI 入口 - 与 _gen_inherited.py 的 __main__ 块行为一致."""


    created, skipped, errors = generate()


    print(f"TASK-0003: Created {created}, skipped {skipped}, errors {errors} (total {len(SKELETONS)})")








if __name__ == "__main__":


    main()


