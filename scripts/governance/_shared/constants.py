"""
constants.py — 审计脚本共享常量

对标 SCRIPT-QUALITY-001 D-D-03（魔法数字提取为命名常量）
             D-D-04（同一概念只在一处定义）
             D-G-01a（路径从项目根推导，非硬编码绝对路径）

所有脚本通过 from _shared.constants import REPO_ROOT 引用，
不再各自硬编码 parents[N] 或 .parent 链。
"""

from __future__ import annotations

from pathlib import Path


def find_repo_root() -> Path:
    """从当前文件向上查找项目根目录（包含 src/zephyr/ 的目录）。

    比 parents[N] 或 .parent 链更健壮——不依赖文件深度，
    任何位置的脚本都能正确定位项目根。

    Returns:
        Path: 项目根目录的绝对路径。

    Raises:
        FileNotFoundError: 向上遍历到文件系统根仍未找到标记。
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "src" / "zephyr" / "__init__.py").exists():
            return parent
    raise FileNotFoundError(f"Cannot find project root (no src/zephyr/__init__.py found) from {current}")


REPO_ROOT: Path = find_repo_root()

EXCLUDE_DIRS: frozenset[str] = frozenset(
    {
        "__pycache__",
        ".git",
        ".runtime",
        "node_modules",
        ".venv",
        "_DO_NOT_USE_old_tree",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
    }
)

SCAN_EXTENSIONS_MD_YAML: frozenset[str] = frozenset(
    {
        ".md",
        ".yaml",
        ".yml",
    }
)

SCAN_EXTENSIONS_CODE: frozenset[str] = frozenset(
    {
        ".py",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".md",
        ".sh",
        ".ps1",
    }
)

SCAN_EXTENSIONS_DOCS: frozenset[str] = frozenset(
    {
        ".md",
        ".yaml",
        ".yml",
        ".txt",
        ".rst",
    }
)

SCAN_EXTENSIONS_PY: frozenset[str] = frozenset({".py"})

SCAN_EXTENSIONS_MD: frozenset[str] = frozenset({".md"})

SCAN_EXTENSIONS_DATA: frozenset[str] = frozenset(
    {
        ".json",
        ".yaml",
        ".yml",
        ".md",
    }
)

GOV_DOCS_DIR: Path = REPO_ROOT / "docs" / "01_policies_and_standards"
SRC_DIR: Path = REPO_ROOT / "src" / "zephyr"
CONFIG_DIR: Path = REPO_ROOT / "config"
SCRIPTS_DIR: Path = REPO_ROOT / "scripts" / "governance"
MANIFEST_PATH: Path = SCRIPTS_DIR / "script_manifest.yaml"
