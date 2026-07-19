# [A_test] module_id: SRC-TST-0090 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-248 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
ZephyrAlpha 2.0 — 全局测试配置与共享 fixture
=============================================

本文件是 pytest 的全局 conftest.py，提供：
  1. 公共 fixture（tmp_db、tmp_project_dir）
  2. 自定义 pytest marker 注册
  3. 全局钩子（如 UTF-8 输出保障）

各测试文件仍可保留自己的局部 fixture（如 manager、engine 等），
但数据库初始化和临时项目目录等通用模式应提取到此处。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src_path = _PROJECT_ROOT / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Ensure subprocess scripts (check_pure_shim.py, check_frontmatter_metadata.py, etc.)
# can import zephyr regardless of their cwd. PYTHONPATH=src (relative) fails when
# subprocess cwd != project root; conftest sets absolute path so subprocesses inherit it.
import os as _os
_src_abs = str(_src_path)
_existing_pp = _os.environ.get("PYTHONPATH", "")
if _src_abs not in _existing_pp.split(_os.pathsep):
    _os.environ["PYTHONPATH"] = _src_abs + (_os.pathsep + _existing_pp if _existing_pp else "")

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


@pytest.fixture
def tmp_db(tmp_path):
    """返回已初始化的 SQLite 数据库路径（临时目录）。

    使用 zephyr.data_governance_governance.persistence.sqlite_schema.init_db 初始化，
    适用于所有需要数据库的测试（task_repo、circuit_breaker、olap_engine 等）。

    5.34.3 双轨说明：本 fixture 是默认的 SQLite 快速轨（零依赖、秒级）；
    需要与生产 depgraph (PostgreSQL) 对齐的测试请改用 pg_db fixture
    （ZEPHYR_TEST_PG=1 激活，见下方注释）。
    """
    from zephyr.governance.persistence.sqlite_schema import init_db

    db_path = tmp_path / "test_zalpha.db"
    init_db(db_path)
    return db_path


def _load_test_pg_config() -> dict[str, str] | None:
    """解析 PG 测试库连接参数（5.34.3 治本——双轨测试的可选 PG 轨）。

    优先级：``config/.env.postgres.test``（KEY=VALUE，若存在）>
    ``ZEPHYR_TEST_PG_*`` 环境变量。两者均未提供 host/db 时返回 None，
    调用方应 ``pytest.skip``——默认 SQLite 快速轨不受影响。

    禁止回退到 ``config/.env.postgres``（生产库真源）——测试连接目标必须
    显式声明，防测试误写生产表（5.34.4 交叉确认）。
    """
    cfg: dict[str, str] = {}
    env_file = _PROJECT_ROOT / "config" / ".env.postgres.test"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                cfg[key.strip()] = value.strip()
    host = _os.environ.get("ZEPHYR_TEST_PG_HOST") or cfg.get("POSTGRES_HOST")
    port = _os.environ.get("ZEPHYR_TEST_PG_PORT") or cfg.get("POSTGRES_PORT", "5432")
    dbname = _os.environ.get("ZEPHYR_TEST_PG_DB") or cfg.get("POSTGRES_DB")
    user = _os.environ.get("ZEPHYR_TEST_PG_USER") or cfg.get("POSTGRES_USER", "zephyr")
    password = _os.environ.get("ZEPHYR_TEST_PG_PASSWORD") or cfg.get("POSTGRES_PASSWORD", "")
    if not (host and dbname):
        return None
    return {"host": host, "port": port, "dbname": dbname, "user": user, "password": password}


@pytest.fixture
def pg_db():
    """可选 PG 测试库连接 fixture（5.34.3 治本——双轨测试的 PG 轨）。

    仅在 ``ZEPHYR_TEST_PG=1`` 时激活；连接参数来自 ``_load_test_pg_config()``
    （``config/.env.postgres.test`` 或 ``ZEPHYR_TEST_PG_*`` 环境变量，独立 PG
    test 库模式；未引入 testcontainers 依赖）。未激活 / 未配置 / PG 不可用时
    ``pytest.skip``——默认 SQLite 快速轨（tmp_db）不受影响。
    teardown 回滚未提交事务，保证测试间隔离。
    """
    if _os.environ.get("ZEPHYR_TEST_PG") != "1":
        pytest.skip("ZEPHYR_TEST_PG!=1，跳过 PG 测试轨（默认 SQLite 快速路径）")
    cfg = _load_test_pg_config()
    if cfg is None:
        pytest.skip("PG 测试库未配置（ZEPHYR_TEST_PG_* 或 config/.env.postgres.test）")
    try:
        import psycopg2

        conn = psycopg2.connect(**cfg)
    except Exception as exc:  # noqa: BLE001 — PG 不可用一律降级为 skip，不阻断测试套件
        pytest.skip(f"PG 测试库不可用: {exc}")
    yield conn
    conn.rollback()  # 测试间隔离：丢弃未提交事务
    conn.close()


@pytest.fixture
def tmp_project_dir(tmp_path):
    """返回一个模拟项目根目录，包含 docs/ 和 src/zephyr/ 子目录。

    适用于 InputSanitizer、SSoTGuard 等需要项目目录结构的测试。
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "zephyr").mkdir(parents=True)
    (tmp_path / "scripts" / "governance").mkdir(parents=True)
    (tmp_path / ".audit_cache").mkdir()
    return tmp_path


@pytest.fixture
def sanitizer(tmp_project_dir):
    """返回绑定 tmp_project_dir 的 InputSanitizer 实例。"""
    from zephyr.security.llm_defense.llm_security.input_sanitizer import InputSanitizer

    return InputSanitizer(root=str(tmp_project_dir))


@pytest.fixture()
def kb_root(tmp_path: Path) -> Path:
    """知识库测试根路径——所有 kb/ 相关测试复用此 fixture。"""
    return tmp_path / "kb"
