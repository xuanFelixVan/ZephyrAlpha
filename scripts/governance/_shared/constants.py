# [BLUEPRINT] MOD-INF-005 | scripts/governance/_shared/constants.py | §
# [MODULE] scripts.governance._shared.constants
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
constants.py — 审计脚本共享常量

对标 SCRIPT-QUALITY-001 D-D-03（魔法数字提取为命名常量）
             D-D-04（同一概念只在一处定义）
             D-G-01a（路径从项目根推导，非硬编码绝对路径）

所有脚本通过 from _shared.constants import REPO_ROOT 引用，
不再各自硬编码 parents[N] 或 .parent 链。

另含 DOC_HTTP_BASE（文档 HTTP server 地址 SSoT）——6 个 D5 生成器统一引用，
不再各自硬编码 localhost:8765（治本 NO-HARDCODED-URL 存量）。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

# 一次性 bootstrap：算 sys.path（此 N 值对本文件固定且仅用一次，符合 project_memory 豁免）。
# 先例：scripts/git_commit.py、scripts/governance/check_ssot_gate.py 均已 bootstrap import src/。
# 注意：不能用 REPO_ROOT（它要从 zephyr 导入，而 zephyr 需要 sys.path 已设置——鸡生蛋）。
# 治本(2026-07-19): 必须添加 src/ 而非项目根——zephyr 包位于 src/zephyr，
# 添加项目根会导致 from zephyr import ... 失败（ModuleNotFoundError）。
# 原 bug：添加 _PROJECT_ROOT（根目录）而非 _PROJECT_ROOT/src，导致所有 governance
# 脚本在 subprocess 调用时（无 PYTHONPATH 继承）都报 ModuleNotFoundError: No module named 'zephyr'。
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # scripts/governance/_shared/ -> root
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

# find_repo_root / REPO_ROOT 真源为 zephyr.shared.io.paths（project_memory 钦定唯一真源）。
# 本模块 re-export，消除算法重复实现。scripts/ 可 import src/（已有先例），无需独立定义。
# DM-90974 Phase 2 治本（2026-07-19 真源收敛）：DEPGRAPH_DIRTY_FLAG 同从此处导入，
# 消除原 reconciliation_registry.py:2864 独立重算路径字符串的真源重复。
from zephyr.shared.io.paths import (  # noqa: E402
    DB_PATH,
    DEPGRAPH_DIRTY_FLAG,
    REPO_ROOT,
    find_repo_root,
)

# DM-90974 Phase 2: depgraph dirty flag — PG 写入脚本落此空文件标记 DB 已变，
# GATE-REGENERATE reconciler（含原 GATE-DOMAIN-DOC 功能）trigger 检测此 flag 存在即 fire，
# reconcile 成功后删除。真源仍是 PostgreSQL DB；此 flag 仅作"运行时 DB 写入→下次 commit
# 触发 reconciler"的桥接信号（派生缓存，单向 DB 写入→flag→reconcile→删 flag）。
# 解决"apply_depgraph.py --delete-nodes 等运行时操作不产生 git commit → reconciler 永不 fire"的盲区。
# 路径真源：zephyr.shared.io.paths.DEPGRAPH_DIRTY_FLAG（本模块仅 re-export，禁止重算）。


def mark_depgraph_dirty() -> None:
    """DM-90974: 标记 depgraph (PostgreSQL) 已被写入。

    在 PG-write 脚本成功 commit 后调用，写一个空 flag 文件到 data/databases/depgraph_dirty.flag
    （路径真源：zephyr.shared.io.paths.DEPGRAPH_DIRTY_FLAG）。
    GATE-REGENERATE reconciler 的 _trigger_domain_doc 检测此 flag 存在即返回 True 触发重生。
    _reconcile_domain_doc 成功后删除此 flag。

    失败不阻断主流程（写入脚本已成功 commit DB）——最坏情况是 flag 未写，
    下次 commit 不触发 reconciler，域文档延迟刷新（与治本前等价，不退化）。
    """
    try:
        DEPGRAPH_DIRTY_FLAG.parent.mkdir(parents=True, exist_ok=True)
        DEPGRAPH_DIRTY_FLAG.touch()
    except OSError:
        # flag 写入失败不阻断主流程（DB 已成功写入，flag 仅是优化信号）
        pass


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


def get_depgraph_pg_connection(
    autocommit: bool = True,
    allow_edge_delete: bool = False,
    read_only: bool = True,
    superuser: bool = False,
) -> PgConnExecuteWrapper:
    """获取 depgraph (PostgreSQL) 连接（包装为兼容 sqlite3 接口）。

    sanctioned wrapper：sqlite3 兼容语义（AGENTS.md §11.4 F4），
    真源在 zephyr.governance.depgraph_schema.get_depgraph_pg_connection。
    禁止删除本 wrapper 或改为直连（29+ 调用点依赖 execute/fetchall 兼容语义）。

    P2迁移后：所有治理脚本通过此入口获取 PG 连接，避免散点连接绕过统一配置。
    返回的 PgConnExecuteWrapper 支持 conn.execute(sql, params).fetchone()/fetchall() 模式，
    与原 sqlite3.Connection.execute() 接口兼容。

    裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: 角色分级访问控制
    - 默认 read_only=True 使用 depgraph_reader 只读角色
    - allow_edge_delete=True 自动隐含 read_only=False（删边需写权限）
    - superuser=True 使用 postgres 超级用户（优先级最高，覆盖 read_only）
    - 仅白名单脚本（apply_depgraph/generate_project_depgraph/sync_yaml_to_depgraph）可写

    :param autocommit: True 启用自动提交（默认，适合只读/简单写）；False 需显式 conn.commit()
    :param allow_edge_delete: S1.3 — True 时设置 session variable 允许删除 apply_depgraph design edges
                              (valid_since IS NULL)。仅 apply_depgraph.py 应传 True。
                              （自动隐含 read_only=False，因删边需写权限）
    :param read_only: True（默认）只读角色；False 读写角色（仅白名单脚本）
    :param superuser: True 使用 postgres 超级用户（用于 DDL/迁移，覆盖 read_only）
    :return: PgConnExecuteWrapper 包装的 psycopg2 连接
    """
    # allow_edge_delete 需要写权限，自动覆盖 read_only
    if allow_edge_delete:
        read_only = False

    # 调用 F1 真源（depgraph_schema.get_depgraph_pg_connection），非本模块 wrapper。
    # 用 import 别名消除同名遮蔽，否则会无限递归（wrapper 调用自己）。
    conn = PgConnExecuteWrapper(
        _get_depgraph_pg_connection_from_depgraph_schema(
            autocommit=autocommit, read_only=read_only, superuser=superuser
        )
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
        # data 是运行时数据目录（security_baselines/asset_index/audit_trail/drift_* 等），
        # 含 177MB secret_baseline JSON + 101MB archive YAML 等大文件（均 .gitignore 忽略）。
        # 治本（2026-07-18）：detect_secrets.py 扫描 data/ 导致 30s 超时——
        # 运行时数据非源码，扫描无意义且产生假阳性，统一加入 EXCLUDE_DIRS 跳过。
        "data",
        # tmp 是临时数据目录（pg_backups/pytest_benchleak/drift 等），
        # 含多个 13MB+ depgraph_*.json 备份文件（均 .gitignore 忽略）。
        # 治本（2026-07-18）：同 data/，临时数据非源码，统一排除。
        "tmp",
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
# 治本（2026-08-17）：原指向 src/zephyr/governance/rule_enforcement（governance→gov_enforcement
# 改名后的陈旧路径，目录不存在）——audit_registration 的 gate 孤儿/僵尸检测、
# validate_gate_yaml / validate_gate_prompt_conflict 的 YAML 迭代全部静默失明（iter 空目录）。
# 引擎自身锚定（gate_engine.py L112: Path(__file__).parent.parent）证实真路径。
GATES_DIR: Path = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "rule_enforcement"

# DB_PATH 真源为 zephyr.shared.io.paths（上方 import），本模块 re-export。
# 治理脚本不得各自硬编码库文件名。

# 文档 HTTP server 地址（SSoT）：生成器生成 MD 里"可缩放 HTML 版"链接的前缀。
# 对齐 generate_module_algorithm_overview.py 的 getenv 模式：环境变量优先，默认 localhost:8765。
# 为什么集中这里：6 个生成器共用同一地址，硬编码分散会漂移（治本 NO-HARDCODED-URL 存量）。
DOC_HTTP_HOST = "localhost"
DOC_HTTP_PORT = 8765
DOC_HTTP_BASE = os.environ.get("ZEPHYR_DOC_HTTP_BASE") or f"http://{DOC_HTTP_HOST}:{DOC_HTTP_PORT}"

# depgraph.db 路径——供 sync_yaml_to_depgraph.py 等治理脚本引用（裁定#206 / Bug H 修复）
# 治本（2026-06-27）：删除 DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"。
# 历史：sync_yaml_to_depgraph.py 曾硬编码仓根盘符绝对路径字面量，违反可移植性；
#       统一到此处常量后，所有治理脚本通过 _shared.constants 单一引用点获取路径。
# P2 迁移后（2026-06）：depgraph 已迁至 PostgreSQL，实际 DB 连接通过
#       get_depgraph_pg_connection() 获取，此常量沦为路径污染源（指向往已归档的 .db 文件）。
# 治本删除理由：常量指向往已归档的 .db 文件，AI 可能误用导致路径污染；
#       经 grep 确认无任何脚本 import 此常量（generate_project_path_tree.py 自定义本地常量，P1 范围待治本）；
#       测试 test_vocab_sync_chain.py::TestBugHDepgraphDbPath 已反转语义保护此治本成果。

# AI-03 S3 治本（真源收敛，2026-08-01）：pg_backups/ 下受保护人工安全备份命名前缀。
# 此类备份由人工/repair 脚本一次性产生（如 depgraph_pre_RSK_rollback_*），排除出自动
# keep-N 退役计数——独立保留最新若干份，避免被自动保留策略挤出丢失回滚安全快照。
# 消费方：backup_runtime_state._is_protected_backup + retire_tmp_artifacts._is_protected_pg_backup
# 真源唯一收敛点（原两文件各定义一份副本，漂移风险——治本收敛至此，禁止他处重定义）。
PROTECTED_PG_BACKUP_PREFIXES: tuple[str, ...] = (
    "architecture_pre_",
    "architecture_pinned_",
    "depgraph_pre_",
    "depgraph_pinned_",
)

EXIT_PASS: int = 0
EXIT_FINDINGS: int = 1
EXIT_ERROR: int = 2
