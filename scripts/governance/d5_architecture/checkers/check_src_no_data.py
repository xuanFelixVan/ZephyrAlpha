#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# [A_full] module_id=CFG-check-src-no-data | layer=config | stability=stable | safety=L | ai_autonomy=human_gated
# [TTL] permanent
#
# GATE-SRC-NO-DATA: src/ 下禁止 data/ 子目录校验
#
# 真源：trae_047_engineering_file_header.yaml §gov_eng_002_directory_mapping 禁止规则
#       "src/下禁止data/子目录(数据真源唯一位置为data/目录,src/仅放代码不放运行态数据)"
#
# 原理：data/ 是运行态数据（brain passport / audit_logs / telemetry / capability_cards 等）
#       唯一合法存放位置。src/ 下创建 data/ 子目录会导致双真源漂移。
# 历史教训：src/data/brain/passports/ 与 data/brain/passports/ 并存导致版本漂移
#           （2026-06-27 清理，commit 36871193）
#
# 模式：--ci 硬阻断（违规 exit 1 拒绝提交）/ --warn-only 只警告
# 触发：pre-commit（事件驱动，staged 文件检测，自动运行自动关闭）
# 消费者：.pre-commit-config.yaml gate-src-no-data
"""
import argparse
import subprocess
import sys

# 禁止路径前缀（小写，大小写不敏感比较——Windows 文件系统大小写不敏感）
# 规则真源见 trae_047 §gov_eng_002_directory_mapping，此处为校验执行逻辑非第二真源
FORBIDDEN_PREFIX = "src/data/"


def get_staged_files():
    """获取 staged 文件列表（相对路径，仅新增/修改/重命名）"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_src_no_data(files):
    """检测是否有 src/data/ 路径的 staged 文件（大小写不敏感）"""
    violations = []
    for f in files:
        if f.lower().startswith(FORBIDDEN_PREFIX):
            violations.append(f)
    return violations


def main():
    parser = argparse.ArgumentParser(
        description="GATE-SRC-NO-DATA: src/ 下禁止 data/ 子目录（数据真源唯一位置为 data/）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ci", action="store_true", help="硬阻断模式（违规 exit 1）")
    mode.add_argument("--warn-only", action="store_true", help="只警告不阻断")
    args = parser.parse_args()

    files = get_staged_files()
    if not files:
        return 0

    violations = check_src_no_data(files)
    if not violations:
        return 0

    msg = (
        f"[GATE-SRC-NO-DATA] 违规：src/ 下禁止 data/ 子目录（数据真源唯一位置为 data/）\n"
        f"  违规文件：{violations}\n"
        f"  真源：trae_047 §gov_eng_002_directory_mapping 禁止规则\n"
        f"  原因：src/ 仅放代码，运行态数据必须放 data/ 下\n"
        f"  历史教训：src/data/brain/ 与 data/brain/ 并存导致版本漂移（2026-06-27 清理）"
    )
    print(msg, file=sys.stderr)

    if args.ci:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
