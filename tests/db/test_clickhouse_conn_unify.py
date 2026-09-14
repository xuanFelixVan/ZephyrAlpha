# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] tests.db.test_clickhouse_conn_unify
# [DOMAIN] D_INFRA_RUNTIME
# [TTL] permanent
"""CH 连接统一治本验收单测（2026-09-14，docs/_working/2026-09-14-ch-connection-handoff.md）。

覆盖：
- get_db_service() 进程级单例；
- get_clickhouse_conn(role, slot) 同 (role, slot) 缓存同实例、异角色/异槽位隔离；
- invalidate_clickhouse_conn 弃槽后重建；
- 非法角色 fail-fast；
- ch_writer.get_client_strict 在 TCP 冷却期 fail-visible 抛 RuntimeError。

全部 mock clickhouse_driver.Client，不依赖真实 CH。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.infrastructure.database_service import DatabaseService, get_db_service  # noqa: E402


def _fake_client_factory():
    return MagicMock(name="FakeCHClient")


def test_get_db_service_singleton():
    ds1 = get_db_service()
    ds2 = get_db_service()
    assert ds1 is ds2
    assert isinstance(ds1, DatabaseService)


def test_role_slot_cache_identity():
    ds = DatabaseService()
    with patch("clickhouse_driver.Client", side_effect=lambda **kw: _fake_client_factory()):
        a = ds.get_clickhouse_conn(role="writer")
        b = ds.get_clickhouse_conn(role="writer")
        assert a is b, "同 (role, slot) 必须返回同一连接（治本核心：进程级单连接）"

        admin = ds.get_clickhouse_conn(role="admin")
        assert admin is not a, "不同角色必须隔离"

        audit = ds.get_clickhouse_conn(role="admin", slot="asset_audit")
        assert audit is not admin, "同角色不同 slot 必须独立连接（api_server 审计通道依赖）"


def test_invalidate_rebuilds():
    ds = DatabaseService()
    with patch("clickhouse_driver.Client", side_effect=lambda **kw: _fake_client_factory()):
        a = ds.get_clickhouse_conn(role="writer")
        ds.invalidate_clickhouse_conn(role="writer")
        b = ds.get_clickhouse_conn(role="writer")
        assert b is not a, "弃槽后必须重建（断连自愈通道）"
        # 其他槽位不受牵连
        admin = ds.get_clickhouse_conn(role="admin")
        ds.invalidate_clickhouse_conn(role="writer")
        assert ds.get_clickhouse_conn(role="admin") is admin


def test_invalid_role_raises():
    ds = DatabaseService()
    try:
        ds.get_clickhouse_conn(role="root")
    except ValueError as e:
        assert "reader/writer/admin" in str(e)
    else:
        raise AssertionError("非法角色必须 ValueError fail-fast")


def test_reader_role_keeps_readonly_setting():
    """reader 角色必须保留 readonly=1（原默认行为不回退）。"""
    ds = DatabaseService()
    captured: dict = {}

    def _fake(**kw):
        captured.update(kw)
        return _fake_client_factory()

    with patch("clickhouse_driver.Client", side_effect=_fake):
        ds.get_clickhouse_conn(role="reader")
    assert captured.get("settings") == {"readonly": 1}


def test_writer_role_params_preserved():
    """writer 角色必须承接 ch_writer 历史连接参数（keepalive/探针语义）。"""
    ds = DatabaseService()
    captured: dict = {}

    def _fake(**kw):
        captured.update(kw)
        return _fake_client_factory()

    with patch("clickhouse_driver.Client", side_effect=_fake):
        ds.get_clickhouse_conn(role="writer")
    assert captured.get("tcp_keepalive") is True
    assert captured.get("connect_timeout") == 3


def test_extra_kwargs_only_on_first_build():
    ds = DatabaseService()
    captured: dict = {}

    def _fake(**kw):
        captured.update(kw)
        return _fake_client_factory()

    with patch("clickhouse_driver.Client", side_effect=_fake):
        a = ds.get_clickhouse_conn(role="admin", slot="t", extra_kwargs={"connect_timeout": 3})
        _ = ds.get_clickhouse_conn(role="admin", slot="t")
    assert captured.get("connect_timeout") == 3
    assert a is not None


def test_get_client_strict_raises_on_cooldown():
    """TCP 冷却期（get_client 返回 None）必须 fail-visible 抛 RuntimeError。"""
    import zephyr.data.ch_writer as cw

    with patch.object(cw, "get_client", return_value=None):
        try:
            cw.get_client_strict()
        except RuntimeError as e:
            assert "不可用" in str(e)
        else:
            raise AssertionError("冷却期必须抛 RuntimeError 而非返回 None")
