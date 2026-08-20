#!/usr/bin/env python
# [MODULE] scripts.governance._archive.one_off.oneoff_update_four_question_text_fields
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_UPDATE_FOUR_QUESTION | layer=script | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""ONEOFF: 更新 candidate_module_registry.yaml 非注释数据字段中的"四问"引用。

策略：q1 保留并改名为"一问标准 q1"；q2/q3/q4 直接删除（含证据文本），不留(已废)历史。
只改非注释行（不以 # 开头的行），注释行保留历史标注（已由头部批量废弃说明覆盖）。
"""

import sys
from pathlib import Path

YAML_PATH = Path(r"D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\candidate_module_registry.yaml")

# 替换映射（顺序敏感：先长后短，避免部分匹配）
REPLACEMENTS = [
    # --- q1+q2 组合：保留 q1，删除 q2 及其证据 ---
    ("四问①②挂:功能已实现+无消费者。", "一问标准 q1挂:功能已实现。"),
    # --- q1 单独：保留并改名 ---
    ("四问①挂", "一问标准 q1挂"),
    ("四问①功能已实现", "q1功能已实现"),
    # --- q2：删除标签+证据，保留 note 中其余内容 ---
    ("四问②挂:无需求驱动。", ""),  # → "depgraph 入边0..."
    ("四问②挂:无重构驱动。", ""),  # → "位置仅作..."
    (" ②无需求驱动(无消费者)", ""),  # tech_notes 中 → "...).depgraph..."
    # --- q3：删除 ---
    ("四问③挂", ""),
    # --- q4：删除标签+证据 ---
    ("四问④挂:AI替代。", ""),  # → "不建代码模块..."
    ("四问④评估", ""),  # check 字段 → ""
    # --- 通用改名（四问过滤 → 一问标准） ---
    ("四问过滤审查", "一问标准审查"),
    ("过四问过滤", "过一问标准"),
    ("四问过滤", "一问标准"),
    # --- 通用改名（待四问 → 待一问标准） ---
    ("待四问评估", "待一问标准评估"),
    ("待四问确认", "待一问标准确认"),
]


def is_comment_line(line: str) -> bool:
    """判断是否为注释行（以 # 开头，可能有前导空格）。"""
    stripped = line.lstrip()
    return stripped.startswith("#")


def apply_replacements(text: str) -> tuple[str, int]:
    """对非注释行应用替换，返回 (新文本, 替换次数)。"""
    lines = text.split("\n")
    count = 0
    new_lines = []
    for line in lines:
        if is_comment_line(line):
            new_lines.append(line)
            continue
        new_line = line
        for old, new in REPLACEMENTS:
            if old in new_line:
                new_line = new_line.replace(old, new)
                count += 1
        new_lines.append(new_line)
    return "\n".join(new_lines), count


def main():
    """Entry point: parse args, run logic, return exit code."""
    if not YAML_PATH.exists():
        print(f"ERROR: {YAML_PATH} not found")
        sys.exit(1)

    original = YAML_PATH.read_text(encoding="utf-8")

    # 统计替换前非注释行的"四问"出现次数
    before_count = sum(1 for line in original.split("\n") if not is_comment_line(line) and "四问" in line)
    print(f"替换前：非注释行中有 {before_count} 行含'四问'")

    new_text, replace_count = apply_replacements(original)

    # 统计替换后
    after_count = sum(1 for line in new_text.split("\n") if not is_comment_line(line) and "四问" in line)
    print(f"替换次数：{replace_count}")
    print(f"替换后：非注释行中有 {after_count} 行含'四问'")

    if before_count == 0:
        print("无需替换，退出")
        return

    # 写入
    YAML_PATH.write_text(new_text, encoding="utf-8")
    print(f"已写入 {YAML_PATH}")

    # 验证 YAML 合法性
    import yaml

    yaml.safe_load(new_text)
    print("YAML 语法验证通过")


if __name__ == "__main__":
    main()
