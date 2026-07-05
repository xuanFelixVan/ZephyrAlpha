# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.io.paths
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_paths | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
paths.py — 项目路径常量 SSoT（Single Source of Truth）

对标 AGENTS.md §6.4（最有利于 AI 施工的选择）
         YAML canonical SSoT 铁律

根因修复：此前 7 个文件各自通过 Path(__file__).parents[N] 独立计算
REPO_ROOT，导致：
  1. 目录层级调整需改 7 处
  2. DB_PATH 大小写冲突（state vs STATE）因无 SSoT 未被发现
  3. 路径常量分散定义，漂移风险极高

本文件是 src/zephyr/ 下所有路径常量的唯一真源。
任何需要 REPO_ROOT / DB_PATH / 路径常量的模块，必须从此处导入。

对标：
  - scripts/governance/_shared/constants.py（治理脚本侧的路径 SSoT）
  - Google Style Guide: "Define constants in one place"（常量只在一处定义）
  - Terraform: provider 配置集中定义，模块引用而非重定义
"""

from pathlib import Path


def find_repo_root() -> Path:
    """从当前文件向上查找项目根目录（包含 src/zephyr/ 的目录）。

    比 parents[N] 或 .parent 链更健壮——不依赖文件深度，
    任何位置的模块都能正确定位项目根。

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

DB_DIR: Path = REPO_ROOT / "data"

# DB_PATH — computed locally to avoid circular import from zephyr.governance.persistence
# Previously: from zephyr.governance.persistence.sqlite_schema import DB_PATH
DB_PATH: Path = REPO_ROOT / "data" / "databases" / "governance.db"

GATES_DIR: Path = REPO_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"
SNAPSHOTS_DIR: Path = REPO_ROOT / ".runtime" / "snapshots"
RATIONALE_LOG_PATH: Path = REPO_ROOT / "docs" / "02_enterprise_architecture" / "architecture-rationale-log.md"

VECTOR_INDEX_DIR: Path = REPO_ROOT / ".audit_cache" / "vector_index"
MODELS_CACHE_DIR: Path = REPO_ROOT / ".audit_cache" / "models"


def get_tmp_dir() -> Path:
    """返回运行时临时目录 REPO_ROOT / '.runtime' / 'tmp'，并确保目录存在。

    Returns:
        Path: 临时目录的绝对路径（已确保存在）。
    """
    tmp_dir = REPO_ROOT / ".runtime" / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    return tmp_dir


def get_data_dir() -> Path:
    """返回数据目录 REPO_ROOT / 'data'，并确保目录存在。

    Returns:
        Path: 数据目录的绝对路径（已确保存在）。
    """
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_dir() -> Path:
    """返回配置目录 REPO_ROOT / 'config'，并确保目录存在。

    Returns:
        Path: 配置目录的绝对路径（已确保存在）。
    """
    config_dir = REPO_ROOT / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


__all__ = [
    "DB_DIR",
    "DB_PATH",
    "GATES_DIR",
    "MODELS_CACHE_DIR",
    "RATIONALE_LOG_PATH",
    "REPO_ROOT",
    "SNAPSHOTS_DIR",
    "VECTOR_INDEX_DIR",
    "find_repo_root",
    "get_config_dir",
    "get_data_dir",
    "get_tmp_dir",
]
