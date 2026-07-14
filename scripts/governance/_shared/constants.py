# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/constants.py | §
# [MODULE] scripts.governance._shared.constants
# [DOMAIN] D_GOV_SCRIPTS
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
from typing import Any

# 一次性 bootstrap：算 sys.path（此 N 值对本文件固定且仅用一次，符合 project_memory 豁免）。
# 先例：scripts/git_commit.py、scripts/governance/check_ssot_gate.py 均已 bootstrap import src/。
# 注意：不能用 REPO_ROOT（它要从 zephyr 导入，而 zephyr 需要 sys.path 已设置——鸡生蛋）。
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # scripts/governance/_shared/ -> root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# find_repo_root / REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 本模块 re-export，消除算法重复实现。scripts/ 可 import src/（已有先例），无需独立定义。
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT, find_repo_root  # noqa: E402

# P2迁移后：depgraph.db 已迁移到 PostgreSQL，所有治理脚本通过此入口获取 PG 连接。
# 真源：docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md
import psycopg2  # noqa: E402
from psycopg2.extras import RealDictCursor  # noqa: E402
# 注意：import 用别名，避免与本模块下方定义的 wrapper 函数同名遮蔽导致无限递归。
# F1 真源（depgraph_schema）返回 psycopg2 connection；F4 wrapper（本模块）包装为 PgConnExecuteWrapper。
# 同名设计是为调用方透明替代，但 wrapper 内部必须调用真源，不能调用自己。
# 治本（2026-06-28）：原直接 import 同名，L107 调用解析到局部 wrapper → RecursionError →
# path_tree sync failed warning。改用别名消除遮蔽。见 AGENTS.md §11.4。
from zephyr.governance.depgraph_schema import (
    get_depgraph_pg_connection as _get_depgraph_pg_connection_from_depgraph_schema,  # noqa: E402
)


class PgConnExecuteWrapper:
    """兼容 sqlite3.Connection.execute() 接口的 psycopg2 connection 包装器。

    P2迁移后：psycopg2 connection 没有 execute() 方法，此包装器使原 SQLite 代码无需修改。
    每次调用 execute() 创建一个新的 RealDictCursor（与原 sqlite3.Row 的 dict(row)/row['col'] 用法等价）。

    注意：RealDictRow 不支持 row[0] 数字索引，需用列名访问（如 row['node_id']）。
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection) -> None:
        self._pg_conn = pg_conn

    def execute(self, sql: str, params: tuple = ()) -> Any:
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        return cur

    def cursor(self):
        """兼容 sqlite3 conn.cursor() 接口，返回 RealDictCursor（支持 execute/fetchone/fetchall）。"""
        return self._pg_conn.cursor(cursor_factory=RealDictCursor)

    def executemany(self, sql: str, params_list: list[tuple]) -> None:
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.executemany(sql, params_list)
        cur.close()

    def commit(self) -> None:
        self._pg_conn.commit()

    def rollback(self) -> None:
        self._pg_conn.rollback()

    def close(self) -> None:
        self._pg_conn.close()

    @property
    def row_factory(self) -> None:
        """兼容 sqlite3 row_factory 设置（PG 模式下忽略，由 cursor_factory 替代）。"""
        return None

    @row_factory.setter
    def row_factory(self, value: Any) -> None:
        # PG 模式下忽略设置（已通过 cursor_factory=RealDictCursor 实现 dict-like 行）
        pass


def get_depgraph_pg_connection(autocommit: bool = True, allow_edge_delete: bool = False) -> PgConnExecuteWrapper:
    """获取 depgraph (PostgreSQL) 连接（包装为兼容 sqlite3 接口）。

    P2迁移后：所有治理脚本通过此入口获取 PG 连接，避免散点连接绕过统一配置。
    返回的 PgConnExecuteWrapper 支持 conn.execute(sql, params).fetchone()/fetchall() 模式，
    与原 sqlite3.Connection.execute() 接口兼容。

    :param autocommit: True 启用自动提交（默认，适合只读/简单写）；False 需显式 conn.commit()
    :param allow_edge_delete: S1.3 — True 时设置 session variable 允许删除 apply_depgraph design edges
                              (valid_since IS NULL)。仅 apply_depgraph.py 应传 True。
    :return: PgConnExecuteWrapper 包装的 psycopg2 连接
    """
    # 调用 F1 真源（depgraph_schema.get_depgraph_pg_connection），非本模块 wrapper。
    # 用 import 别名消除同名遮蔽，否则会无限递归（wrapper 调用自己）。
    conn = PgConnExecuteWrapper(
        _get_depgraph_pg_connection_from_depgraph_schema(autocommit=autocommit)
    )
    if allow_edge_delete:
        # S1.3: edges 表三写分区保护 — apply_depgraph.py 需删除 design edges (valid_since IS NULL)
        # 其他脚本（sync_yaml_to_depgraph / generate_project_depgraph）不设此变量，
        # 触发器 trg_edges_protect_apply_depgraph 会阻断对 apply_depgraph edges 的 DELETE。
        conn.execute("SET app.allow_delete_apply_depgraph_edges = on")
    return conn

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

# 治本(ARCH-036 P1-3): 收敛散点路径常量定义。
# 原 5 个文件各自定义 BLUEPRINTS_DIR，原 5 个文件各自定义 _GATES_DIR。
# 统一到此处单一真源，调用方 from _shared.constants import BLUEPRINTS_DIR, GATES_DIR。
BLUEPRINTS_DIR: Path = REPO_ROOT / "docs" / "03_modules"
GATES_DIR: Path = REPO_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"

# DB_PATH 真源为 zephyr.shared.io.paths（上方 import），本模块 re-export。
# 治理脚本不得各自硬编码库文件名。

# depgraph.db 路径——供 sync_yaml_to_depgraph.py 等治理脚本引用（裁定#206 / Bug H 修复）
# 治本（2026-06-27）：删除 DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"。
# 历史：sync_yaml_to_depgraph.py 曾硬编码 r"D:\ZephyrAlpha\..." 绝对路径，违反可移植性；
#       统一到此处常量后，所有治理脚本通过 _shared.constants 单一引用点获取路径。
# P2 迁移后（2026-06）：depgraph 已迁至 PostgreSQL，实际 DB 连接通过
#       get_depgraph_pg_connection() 获取，此常量沦为路径污染源（指向往已归档的 .db 文件）。
# 治本删除理由：常量指向往已归档的 .db 文件，AI 可能误用导致路径污染；
#       经 grep 确认无任何脚本 import 此常量（generate_project_path_tree.py 自定义本地常量，P1 范围待治本）；
#       测试 test_vocab_sync_chain.py::TestBugHDepgraphDbPath 已反转语义保护此治本成果。

EXIT_PASS: int = 0
EXIT_FINDINGS: int = 1
EXIT_ERROR: int = 2
