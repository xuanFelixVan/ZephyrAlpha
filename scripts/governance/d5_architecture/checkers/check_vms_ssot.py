#!/usr/bin/env python
# -*- coding: utf-8 -*-
# [A_full] module_id=CFG-check-vms-ssot | layer=config | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
#
# GATE-VMS-SSOT: VMS 单一真源门禁（governance/vector_memory 漂移副本防复发）
#
# 真源：AGENTS.md §11.2 遗留项-3 VMS SSoT 声明
#       "integration/vector_memory/ 是 VMS 唯一真源，governance/vector_memory/ 已删除（2026-06-28）"
#
# 原理：governance/vector_memory/ 曾是 integration/vector_memory/ 的漂移副本，
#       两者并存导致维度方向双向漂移（integration 512d 领先 / governance 384d 落后）。
#       2026-06-28 阶段3 删除 governance 副本治本（commit 306dbb2f76 + 0137750451），
#       本门禁防止 AI 重建已删除的漂移副本。
#
# 历史教训：governance/vector_memory 26 文件漂移副本与 integration/vector_memory 并存，
#           导致 SSoT 双向漂移；AI"不搜索就新生成"是副本复发的根因
#
# 模式：--ci 硬阻断（违规 exit 1 拒绝提交）/ --warn-only 只警告
# 触发：pre-commit（事件驱动，staged 文件检测，自动运行自动关闭）
# 消费者：.pre-commit-config.yaml gate-vms-ssot
"""GATE-VMS-SSOT: VMS 单一真源门禁——检测 governance/vector_memory 漂移副本复发。

防止 AI 重建已删除的 governance/vector_memory/ 目录（VMS 漂移副本）。
真源为 integration/vector_memory/（MOD-INF-011 蓝图）。

与 GATE-SRC-NO-DATA 的区别：
    - GATE-SRC-NO-DATA 禁止 src/data/（数据真源唯一 data/），真源 trae_047
    - 本脚本禁止 src/zephyr/governance/vector_memory/（VMS 真源唯一 integration/），真源 AGENTS.md §11.2

Exit codes:
    0 = PASS（无违规或无 staged 文件）
    1 = VIOLATION（检测到 governance/vector_memory 路径 staged 文件，--ci 模式）
"""
import argparse
import subprocess
import sys

# 禁止路径前缀（小写，大小写不敏感比较——Windows 文件系统大小写不敏感）
# 规则真源见 AGENTS.md §11.2 遗留项-3 VMS SSoT 声明，此处为校验执行逻辑非第二真源
FORBIDDEN_PREFIX = "src/zephyr/governance/vector_memory/"


def get_staged_files():
    """获取 staged 文件列表（相对路径，仅新增/修改/重命名）"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_vms_ssot(files):
    """检测是否有 governance/vector_memory 路径的 staged 文件（大小写不敏感）"""
    violations = []
    for f in files:
        if f.lower().startswith(FORBIDDEN_PREFIX):
            violations.append(f)
    return violations


def main():
    parser = argparse.ArgumentParser(
        description="GATE-VMS-SSOT: VMS 单一真源门禁（governance/vector_memory 漂移副本防复发）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--ci", action="store_true", help="硬阻断模式（违规 exit 1）")
    mode.add_argument("--warn-only", action="store_true", help="只警告不阻断")
    args = parser.parse_args()

    files = get_staged_files()
    if not files:
        return 0

    violations = check_vms_ssot(files)
    if not violations:
        return 0

    msg = (
        f"[GATE-VMS-SSOT] 违规：governance/vector_memory/ 是已删除的漂移副本目录\n"
        f"  违规文件：{violations}\n"
        f"  真源：AGENTS.md §11.2 遗留项-3 VMS SSoT 声明\n"
        f"  原因：integration/vector_memory/ 是 VMS 唯一真源，"
        f"governance/vector_memory/ 已于 2026-06-28 删除\n"
        f"  历史教训：26 文件漂移副本与真源并存导致维度方向双向漂移"
        f"（commit 306dbb2f76 + 0137750451 治本）\n"
        f"  修复：删除 governance/vector_memory/ 下的文件，改用 integration/vector_memory/"
    )
    print(msg, file=sys.stderr)

    if args.ci:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
