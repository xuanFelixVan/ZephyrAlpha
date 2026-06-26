# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/constants.py | §
# [MODULE] scripts.governance._shared.constants
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""
constants.py — 审计脚本共享常量

对标 SCRIPT-QUALITY-001 D-D-03（魔法数字提取为命名常量）
             D-D-04（同一概念只在一处定义）
             D-G-01a（路径从项目根推导，非硬编码绝对路径）

所有脚本通过 from _shared.constants import REPO_ROOT 引用，
不再各自硬编码 parents[N] 或 .parent 链。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 一次性 bootstrap：算 sys.path（此 N 值对本文件固定且仅用一次，符合 project_memory 豁免）。
# 先例：scripts/git_commit.py、scripts/governance/check_ssot_gate.py 均已 bootstrap import src/。
# 注意：不能用 REPO_ROOT（它要从 zephyr 导入，而 zephyr 需要 sys.path 已设置——鸡生蛋）。
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # scripts/governance/_shared/ -> root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# find_repo_root / REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 本模块 re-export，消除算法重复实现。scripts/ 可 import src/（已有先例），无需独立定义。
from zephyr.shared.io.paths import REPO_ROOT, find_repo_root  # noqa: E402

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
        # vector_db 是 vector database 运行时数据目录（~52万文件，已被 .gitignore 忽略）。
        # 临时文件/废弃路径检测针对源代码区，扫描 vector_db 浪费时间且无意义。
        # 治本：加入 EXCLUDE_DIRS 后所有治理脚本（iter_files / os.walk+prune）统一跳过。
        "vector_db",
        # models 是 ML 模型文件目录（含 tokenizer.json 等大文件，已被 .gitignore 忽略）。
        # 模型 JSON 的转义字符（\\\\）会被误判为"路径双重嵌套"，扫描无意义且产生假阳性。
        "models",
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

# 与 src/zephyr/shared/paths.DB_PATH 对齐（治理脚本不得各自硬编码库文件名）
DB_PATH: Path = REPO_ROOT / "data" / "databases" / "governance.db"

# depgraph.db 路径——供 sync_yaml_to_depgraph.py 等治理脚本引用（裁定#206 / Bug H 修复）
# 历史：sync_yaml_to_depgraph.py 曾硬编码 r"D:\ZephyrAlpha\..." 绝对路径，违反可移植性；
#       统一到此处常量后，所有治理脚本通过 _shared.constants 单一引用点获取路径。
DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"

EXIT_PASS: int = 0
EXIT_FINDINGS: int = 1
EXIT_ERROR: int = 2
