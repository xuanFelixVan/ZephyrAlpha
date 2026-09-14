# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §depgraph（被测真源挂靠，风格同 test_ops_guard_red_team）
# [MODULE] tests.governance.test_pg_dsn_utf8_guard
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] DATABASE_URL 含不可 UTF-8 编码码点(surrogateescape)时 fail-fast ValueError; 合法 URL 解析零回归
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_pg_dsn_utf8_guard.py — PG dsn 环境变量入口 UTF-8 严格校验

09-14 GATE-PANORAMA 检测器失效定案（2026-09-15）：瞬态进程环境的 DATABASE_URL
含非 UTF-8 字节 → psycopg2 C 层解 dsn 报 UnicodeDecodeError(0xd6@61)，栈深处
难定位。治本=入口 fail-fast，报错直接指向环境变量注入源。
"""

from __future__ import annotations

import pytest

from zephyr.governance.depgraph_schema import _load_pg_config_from_url


class TestPgDsnUtf8Guard:
    def test_surrogate_bytes_fail_fast(self) -> None:
        """坏字节经环境变量 surrogateescape 进入 str（PEP 528/529 实际形态）→ ValueError。"""
        poisoned = "postgres://depgraph_reader:pa\udcd6ss@localhost:5432/db"
        with pytest.raises(ValueError, match="DATABASE_URL"):
            _load_pg_config_from_url(poisoned)

    def test_error_message_points_to_env_var(self) -> None:
        """报错必须指向环境变量与文件回退（可诊断性钉死）。"""
        poisoned = "postgresql://u:\udcb0\udcd6@host/db"
        with pytest.raises(ValueError, match="config/\\.env\\.postgres"):
            _load_pg_config_from_url(poisoned)

    def test_good_url_zero_regression(self) -> None:
        """合法 URL（含 URL 编码密码）解析零回归。"""
        cfg = _load_pg_config_from_url("postgresql://u:p%40ss@10.0.0.1:5432/zdb")
        assert cfg["POSTGRES_HOST"] == "10.0.0.1"
        assert cfg["POSTGRES_PORT"] == "5432"
        assert cfg["POSTGRES_DB"] == "zdb"
        assert cfg["POSTGRES_USER"] == "u"
        assert cfg["POSTGRES_PASSWORD"] == "p@ss"
