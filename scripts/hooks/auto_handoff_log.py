# [BLUEPRINT] MOD-INF-005 | scripts/hooks/auto_handoff_log.py | §
# [MODULE] scripts.hooks.auto_handoff_log
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.hooks.git_secrets_setup.sh
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
from __future__ import annotations

#!/usr/bin/env python3
import os

"""自动交接日志生成器 — Sprint 0 批次F (F-02)

基于 ``git diff --name-only HEAD`` 和 ``git diff --stat HEAD`` 的输出，
自动生成 Markdown 格式的交接日志并写入
``docs/19_development_workspace/handoff-logs/`` 目录。

用法::

    python scripts/hooks/auto_handoff_log.py
    python scripts/hooks/auto_handoff_log.py --last-commit   # post-commit：记录刚提交的 HEAD

运行后会：
1. 在终端打印改动摘要
2. 将完整交接日志写入 handoff-logs/ 目录（UTF-8 编码）

要求：Python 3.12+，工作目录为项目根目录（包含 ``.git``）。
"""

import argparse
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# bootstrap: 定位 scripts/governance/ 以 import _shared.constants（REPO_ROOT SSoT 真源）
_GOV_DIR = str(Path(__file__).resolve().parents[1] / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import REPO_ROOT  # noqa: E402

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

handoff_DIR: Path = REPO_ROOT / "docs" / "19_development_workspace" / "handoff-logs"
TIMEZONE_CST = timezone(timedelta(hours=8))

# ---------------------------------------------------------------------------
# Git 辅助函数
# ---------------------------------------------------------------------------


def _run_git(args: list[str]) -> str:
    """执行 git 命令并返回 stdout（UTF-8 解码）。

    Parameters
    ----------
    args:
        传给 ``git`` 的参数列表，例如 ``["diff", "--name-only", "HEAD"]``。

    Returns
    -------
    str
        命令的标准输出内容。

    Raises
    ------
    SystemExit
        当 git 命令执行失败时退出。
    """
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as exc:
        print(f"[ERROR] git {' '.join(args)} 失败: {exc.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("[ERROR] 未找到 git 命令，请确认 git 已安装并在 PATH 中。", file=sys.stderr)
        sys.exit(1)


def get_changed_files() -> list[str]:
    """获取当前工作区相对于 HEAD 的改动文件列表。

    Returns
    -------
    list[str]
        改动文件的相对路径列表（可能为空）。
    """
    output: str = _run_git(["diff", "--name-only", "HEAD"])
    if not output:
        return []
    return output.splitlines()


def get_last_commit_files() -> list[str]:
    """``git show --name-only HEAD`` 本次提交涉及的文件列表。"""
    output: str = _run_git(["show", "--name-only", "--pretty=format:", "HEAD"])
    if not output:
        return []
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_last_commit_stat() -> str:
    """``git show --stat HEAD``。"""
    return _run_git(["show", "--stat", "HEAD"])


def get_diff_stat() -> str:
    """获取 ``git diff --stat HEAD`` 的统计摘要。

    Returns
    -------
    str
        统计摘要文本。
    """
    return _run_git(["diff", "--stat", "HEAD"])


# ---------------------------------------------------------------------------
# Markdown 生成
# ---------------------------------------------------------------------------


def build_handoff_markdown(
    changed_files: list[str],
    diff_stat: str,
    timestamp: datetime,
) -> str:
    """构建交接日志的 Markdown 内容。

    Parameters
    ----------
    changed_files:
        改动文件列表。
    diff_stat:
        ``git diff --stat`` 输出。
    timestamp:
        日志生成时间。

    Returns
    -------
    str
        完整的 Markdown 文本。
    """
    ts_str: str = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
    file_count: int = len(changed_files)

    lines: list[str] = [
        "# 交接日志 / Handoff Log",
        "",
        f"> 生成时间: {ts_str}",
        f"> 改动文件数: {file_count}",
        "",
        "---",
        "",
        "## 改动文件清单",
        "",
    ]

    if changed_files:
        for f in changed_files:
            lines.append(f"- `{f}`")
    else:
        lines.append("_（无改动文件）_")

    lines.extend(
        [
            "",
            "---",
            "",
            "## 统计摘要",
            "",
            "```",
            diff_stat if diff_stat else "(无统计信息)",
            "```",
            "",
            "---",
            "",
            "## 下一步建议",
            "",
            "<!-- TODO: 在此填写下一步工作建议 -->",
            "",
            "- [ ] 待补充：下一个 Sprint / 批次的优先任务",
            "- [ ] 待补充：需要关注的风险或阻塞项",
            "- [ ] 待补充：需要其他成员接手的事项",
            "",
            "---",
            "",
            "*本文件由 `auto_handoff_log.py` 自动生成（工作区 diff 或 `--last-commit`）*",
            "",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def main() -> None:
    """主函数：收集 git diff 信息，生成交接日志并写入文件。"""
    parser = argparse.ArgumentParser(description="生成交接日志 Markdown")
    parser.add_argument(
        "--last-commit",
        action="store_true",
        help="基于刚完成的 HEAD 提交（供 post-commit 钩子使用）",
    )
    args = parser.parse_args()

    now: datetime = datetime.now(tz=TIMEZONE_CST)

    # 1. 收集 git 信息
    if args.last_commit:
        changed_files = get_last_commit_files()
        diff_stat = get_last_commit_stat()
    else:
        changed_files = get_changed_files()
        diff_stat = get_diff_stat()

    # 2. 构建 Markdown
    markdown: str = build_handoff_markdown(changed_files, diff_stat, now)

    # 3. 确保输出目录存在
    handoff_DIR.mkdir(parents=True, exist_ok=True)

    # 4. 写入文件
    filename: str = f"handoff-{now.strftime('%Y%m%d-%H%M%S')}.md"
    output_path: Path = handoff_DIR / filename
    tmp_path = f"{output_path}.{os.getpid()}.tmp"

    try:
        Path(tmp_path).write_text(markdown, encoding="utf-8")

        os.replace(tmp_path, output_path)

    except PermissionError:
        try:
            os.remove(tmp_path)

        except OSError:
            pass

    # 5. 终端打印摘要
    print("=" * 60)
    print("  交接日志生成完成 / Handoff Log Generated")
    print("=" * 60)
    print(f"  时间: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  改动文件数: {len(changed_files)}")
    print(f"  输出路径: {output_path}")
    print("-" * 60)

    if changed_files:
        print("  改动文件:")
        for f in changed_files[:20]:
            print(f"    - {f}")
        if len(changed_files) > 20:
            print(f"    ... 及其他 {len(changed_files) - 20} 个文件")
    else:
        print("  （无改动文件）")

    print("-" * 60)
    if diff_stat:
        print("  统计:")
        for line in diff_stat.splitlines()[-3:]:
            print(f"    {line}")
    print("=" * 60)


if __name__ == "__main__":
    main()
