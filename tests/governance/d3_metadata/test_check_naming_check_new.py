# [BLUEPRINT] MOD-INF-005 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""--check-new 增量 N-16 模式：只拦 staged 新增重名，不拦历史遗留/未跟踪 WIP。

背景（#ARCH-PRECOMMIT-INCREMENTAL，2026-08-05）：
    eia_provider.py 提交被全仓 --scan 模式扫出 369 个"阻断性"违规卡死，
    实际真阻断只有 2 个 N-16（docs/_working/ WIP 副本）。治本：pre-commit 走
    --check-new 增量模式（git ls-files 基线，只拦 staged 新增重名），全仓审计移 CI。

    --check-new CLI 由 GitCommitGateway 集成时落地（commit 8a777f3fec 等，
    N-16 检查逻辑真源统一到 check_naming_convention.py）。本测试验证其行为符合
    增量守门铁律（pre-commit 路径只拦本次 staged 文件引入的新违规）。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GATE = ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    """调用 check_naming_convention.py（cwd=REPO_ROOT，与 pre-commit 运行环境一致）。"""
    return subprocess.run(
        [sys.executable, str(GATE), *args],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )


def test_check_new_cli_exists():
    """--check-new 必须是合法 CLI arg（pre-commit hook + GitCommitGateway 均依赖）。"""
    r = subprocess.run(
        [sys.executable, str(GATE), "--help"],
        capture_output=True,
        text=True,
    )
    assert "--check-new" in r.stdout, "check_naming_convention.py 缺 --check-new CLI arg"


def test_check_new_blocks_duplicate_in_scope():
    """staged 新文件（docs/ 前缀）与已跟踪文件重名 → --check-new exit 非零 + N-16 输出。

    用 docs/battle_map_merge_mapping.md 作为虚构新文件（basename 与已跟踪的
    docs/_working/battle_map_merge_task/battle_map_merge_mapping.md 相同）。
    增量模式用 git ls-files 基线，应检出跨目录同名冲突（草稿区文件作基线仍参与检测）。
    """
    r = _run(["--check-new", "docs/battle_map_merge_mapping.md"])
    assert r.returncode != 0, (
        f"--check-new 应拦截新增重名 docs/battle_map_merge_mapping.md，实际 exit 0。stdout={r.stdout} stderr={r.stderr}"
    )
    assert "N-16" in (r.stdout + r.stderr), f"输出应含 N-16 标记。stdout={r.stdout}"


def test_check_new_passes_unique_in_scope():
    """staged 新文件名唯一（docs/ 前缀）→ --check-new exit 0。"""
    unique = "docs/zzz_unique_for_check_new_test_20260806.md"
    r = _run(["--check-new", unique])
    assert r.returncode == 0, (
        f"--check-new 对唯一新名应 exit 0，实际 {r.returncode}。stdout={r.stdout} stderr={r.stderr}"
    )


def test_check_new_empty_args_passes():
    """--check-new 无参数（pre-commit 无 staged 文件匹配时）→ exit 0，不误阻断。

    场景：pre-commit pass_filenames:true 但本次 commit 无 .py/.md/.yaml 文件，
    pre-commit 传空列表给 --check-new。应 exit 0（无新文件 = 无新违规）。
    """
    r = _run(["--check-new"])
    assert r.returncode == 0, (
        f"--check-new 无参数应 exit 0（无新文件），实际 {r.returncode}。stdout={r.stdout} stderr={r.stderr}"
    )


def test_check_new_skips_bare_filename_out_of_scope():
    """裸文件名（无 tests//docs//src/ 前缀）不在 N-16 scope → 不检测，exit 0。

    增量 N-16 只覆盖 tests/docs/src 三个 scope（与全量 check_filename_uniqueness_all
    一致）。裸文件名被视为项目根级文件，不在 scope 内，不检测。
    防止 pre-commit 传入根级配置文件（如 pyproject.toml）误触发 N-16。
    """
    r = _run(["--check-new", "pyproject.toml"])
    assert r.returncode == 0, (
        f"裸文件名 pyproject.toml 不在 N-16 scope，应 exit 0，实际 {r.returncode}。stdout={r.stdout} stderr={r.stderr}"
    )
