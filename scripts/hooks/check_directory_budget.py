#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
写入门禁：目录文件预算 + 文件名版本号检查

触发时机：pre-commit (always_run: true)

检查内容：
1. 目录预算 — 当 docs/ 特定子目录被 staged 新增文件（A）后，
   检查该目录在工作区的总文件数是否超过配置上限。
2. 文件名版本号 — staged 新增文件的文件名不得含 -v2/-v3/-round2 等
   "文件名做版本控制"模式，应使用 git 历史作为版本记录。

退出码：0 = 通过；1 = 违规
"""
import io
import re
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

REPO = Path(__file__).resolve().parents[2]

# ──────────────────────────────────────────────────────────────────────────────
# 目录预算配置（文件上限）
# 调整原则：超过上限必须先清理旧文件，再提交新文件。
# ──────────────────────────────────────────────────────────────────────────────
BUDGETS: dict[str, int] = {
    "docs/09_AUDIT/STATE/DAILY":          10,   # 只保留 LATEST，最多 10 个
    "docs/09_AUDIT/STATE/SESSION_LOGS":   60,   # session 日志，会话完毕后清理
    "docs/09_AUDIT/STATE":                60,   # STATE 根目录（不含子目录递归）- 已清理至 60 以下
    "docs/09_AUDIT/REPORTS/ARCHIVE":     30,   # Wave 1-2 清理后的稳态上限
    "docs/09_AUDIT/REPORTS/INCIDENT":    20,   # 事故报告，保留最近 20 份
    "docs/09_AUDIT/REPORTS/QUALITY":     20,
    "docs/09_AUDIT/REPORTS/COMPLIANCE":  20,
    "docs/09_AUDIT/REPORTS/PERIODIC":    10,
}

# ──────────────────────────────────────────────────────────────────────────────
# 文件名版本号禁止模式
# ──────────────────────────────────────────────────────────────────────────────
BANNED_FILENAME_PATTERNS: list[re.Pattern] = [
    re.compile(r"-v\d+\.", re.IGNORECASE),          # -v2.md  -v3.json
    re.compile(r"_v\d+\.", re.IGNORECASE),           # _v2.md
    re.compile(r"-round\d+[-_.]", re.IGNORECASE),   # -round2_fix
    re.compile(r"-(final-)+.*-final\.", re.IGNORECASE),  # -final-...-final.md
    re.compile(r"-v\d+$", re.IGNORECASE),            # file-v2 (no extension)
]

# 豁免目录：这些目录下的文件不做版本号检查（归档区允许历史命名）
BANNED_EXEMPT_DIRS: list[str] = [
    "docs/06_ARCHIVE",
    "docs/09_AUDIT/REPORTS/ARCHIVE",
    "docs/09_AUDIT/STATE/MILESTONE",
]


def get_staged_additions() -> list[str]:
    """返回本次 commit 中新增（A）文件的路径列表（相对于仓库根）。"""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status"],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    additions = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].strip().startswith("A"):
            additions.append(parts[1].strip().replace("\\", "/"))
    return additions


def count_files_in_dir(dirpath: str) -> int:
    """统计目录下直接子文件数（不递归子目录）。"""
    p = REPO / dirpath
    if not p.exists():
        return 0
    return sum(1 for f in p.iterdir() if f.is_file())


def check_budget(staged: list[str]) -> list[str]:
    """返回超出预算的违规信息列表。"""
    violations: list[str] = []
    # 只检查本次 staged 新增文件所在目录
    touched_dirs: set[str] = set()
    for path in staged:
        parent = "/".join(path.split("/")[:-1])
        touched_dirs.add(parent)

    for budget_dir, limit in BUDGETS.items():
        # 如果本次新增文件涉及该目录（或其子目录），才检查
        if not any(d == budget_dir or d.startswith(budget_dir + "/") for d in touched_dirs):
            continue
        current = count_files_in_dir(budget_dir)
        if current > limit:
            violations.append(
                f"  目录预算超限: {budget_dir}/\n"
                f"    当前文件数: {current}，上限: {limit}\n"
                f"    请先删除旧文件再提交新文件。"
            )
    return violations


def check_filename_versions(staged: list[str]) -> list[str]:
    """返回含版本号的文件名违规信息列表。"""
    violations: list[str] = []
    for path in staged:
        # 检查是否在豁免目录下
        if any(path.startswith(exempt) for exempt in BANNED_EXEMPT_DIRS):
            continue
        filename = path.split("/")[-1]
        stem = Path(filename).stem  # 去掉最后一个扩展名
        for pattern in BANNED_FILENAME_PATTERNS:
            if pattern.search(stem + "."):  # 在 stem 后加点模拟完整文件名匹配
                violations.append(
                    f"  文件名含版本号: {path}\n"
                    f"    匹配模式: {pattern.pattern}\n"
                    f"    请使用 git 历史做版本控制，文件名保持不变。"
                )
                break
    return violations


def main() -> int:
    staged = get_staged_additions()
    if not staged:
        return 0

    all_violations: list[str] = []

    budget_violations = check_budget(staged)
    filename_violations = check_filename_versions(staged)

    all_violations.extend(budget_violations)
    all_violations.extend(filename_violations)

    if not all_violations:
        print("[write-gate] 写入预算检查通过")
        return 0

    print("[write-gate] 写入门禁：发现以下违规，提交被拒绝")
    print()
    for v in all_violations:
        print(v)
    print()
    print("[write-gate] 提示：")
    print("  - 目录超限 → 先运行流水线清理旧文件，再提交新内容")
    print("  - 文件名版本号 → 删除 -v2/-v3 等后缀，用 git log 查历史版本")
    print("  - 扫描产物 → 写入 .audit_cache/ 而非 docs/（已 gitignored）")
    return 1


if __name__ == "__main__":
    sys.exit(main())
