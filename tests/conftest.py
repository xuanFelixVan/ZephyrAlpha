# [A_test] module_id: SRC-TST-0090 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-248 | docs/03_modules/_domain_governance/blueprint.md | §
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
    """
    from zephyr.governance.persistence.sqlite_schema import init_db

    db_path = tmp_path / "test_zalpha.db"
    init_db(db_path)
    return db_path


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
