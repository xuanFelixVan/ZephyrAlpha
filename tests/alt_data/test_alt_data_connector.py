# [BLUEPRINT] MOD-ALT-007 | docs/03_modules/_domain_alt_data/alt_data_connector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ALT-007 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.alt_data.test_alt_data_connector
# [TESTS] src/zephyr/alt_data/alt_data_connector.py
"""MOD-ALT-007 单元测试：alt_data_connector 另类数据统一接入器。

蓝图验收（B5-07081/CAND-TESTA-022，B5 D-ALT-DATA-01）：
三类连接器注册表（免费源优先确定性排序）+ 格式适配协议 + 增量游标断点
续传（checkpoint 导出/恢复）+ API 密钥加密保管（注入 cipher 仅落密文）+
source_health 每次同步必登记（回调异常不阻断）+ Fail-Closed 分支。
fetcher/cipher/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.alt_data.alt_data_connector",
    reason="alt_data_connector not importable",
)

from zephyr.alt_data.alt_data_connector import (  # noqa: E402
    AltDataConnector,
    AltDataConnectorError,
    ConnectorKind,
    ConnectorSpec,
    SyncCheckpoint,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)


def _spec(
    connector_id: str = "akshare_news",
    kind: ConnectorKind = ConnectorKind.NEWS,
    free: bool = True,
) -> ConnectorSpec:
    return ConnectorSpec(connector_id=connector_id, kind=kind, free=free, description="测试源")


def _adapter(raw):
    return raw["id"], {"title": raw.get("title", "")}


def _hub(**kw) -> AltDataConnector:
    kw.setdefault("clock", lambda: _T0)
    return AltDataConnector(**kw)


def _registered_hub(**kw) -> AltDataConnector:
    hub = _hub(**kw)
    hub.register(_spec())
    hub.set_adapter("akshare_news", _adapter)
    return hub


# ──────────────────────────────────────────────────────────────────────────────
# 连接器注册表
# ──────────────────────────────────────────────────────────────────────────────


class TestRegister:
    def test_free_first_ordering_and_kind_filter(self) -> None:
        hub = _hub()
        hub.register(_spec("paid_x", ConnectorKind.NEWS, free=False))
        hub.register(_spec("free_z", ConnectorKind.NEWS, free=True))
        hub.register(_spec("free_a", ConnectorKind.SOCIAL, free=True))
        ids = [s.connector_id for s in hub.list_connectors()]
        assert ids == ["free_a", "free_z", "paid_x"]  # 免费优先 + id 升序
        news = hub.list_connectors(kind=ConnectorKind.NEWS)
        assert [s.connector_id for s in news] == ["free_z", "paid_x"]

    def test_duplicate_raises(self) -> None:
        hub = _hub()
        hub.register(_spec())
        with pytest.raises(AltDataConnectorError):
            hub.register(_spec())

    def test_invalid_spec_raises(self) -> None:
        hub = _hub()
        with pytest.raises(AltDataConnectorError):
            hub.register(_spec(connector_id=""))  # 空 id
        with pytest.raises(AltDataConnectorError):
            hub.register(ConnectorSpec(connector_id="x", kind="news"))  # kind 非枚举
        with pytest.raises(AltDataConnectorError):
            hub.register(ConnectorSpec(connector_id="y", kind=ConnectorKind.NEWS, free=1))  # free 非 bool
        with pytest.raises(AltDataConnectorError):
            hub.register("not-a-spec")  # 类型非法
        with pytest.raises(AltDataConnectorError):
            hub.list_connectors(kind="news")  # 过滤类别非法


class TestAdapter:
    def test_set_adapter_unknown_raises(self) -> None:
        hub = _hub()
        with pytest.raises(AltDataConnectorError):
            hub.set_adapter("ghost", _adapter)

    def test_set_adapter_not_callable_raises(self) -> None:
        hub = _hub()
        hub.register(_spec())
        with pytest.raises(AltDataConnectorError):
            hub.set_adapter("akshare_news", "not-callable")


# ──────────────────────────────────────────────────────────────────────────────
# API 密钥加密保管
# ──────────────────────────────────────────────────────────────────────────────


class TestApiKey:
    def test_store_get_roundtrip_ciphertext_only(self) -> None:
        hub = _registered_hub(
            cipher_encrypt=lambda s: "enc:" + s[::-1],
            cipher_decrypt=lambda s: s[4:][::-1],
        )
        hub.store_api_key("akshare_news", "sk-secret-001")
        assert hub.has_api_key("akshare_news") is True
        assert hub.get_api_key("akshare_news") == "sk-secret-001"

    def test_store_without_cipher_fail_closed(self) -> None:
        hub = _registered_hub()
        with pytest.raises(AltDataConnectorError):
            hub.store_api_key("akshare_news", "sk-x")
        assert hub.has_api_key("akshare_news") is False

    def test_access_errors_raise(self) -> None:
        hub = _registered_hub(cipher_encrypt=lambda s: "enc:" + s)  # 无 decrypt
        with pytest.raises(AltDataConnectorError):
            hub.store_api_key("akshare_news", "")  # 空密钥
        with pytest.raises(AltDataConnectorError):
            hub.get_api_key("akshare_news")  # 无已存密钥
        hub.store_api_key("akshare_news", "sk-y")
        with pytest.raises(AltDataConnectorError):
            hub.get_api_key("akshare_news")  # cipher_decrypt 未注入
        with pytest.raises(AltDataConnectorError):
            hub.store_api_key("ghost", "sk-z")  # 未知连接器


# ──────────────────────────────────────────────────────────────────────────────
# 增量同步（断点续传 + source_health）
# ──────────────────────────────────────────────────────────────────────────────


def _scripted_fetcher(batches: list, seen_cursors: list | None = None):
    def _fetch(spec: ConnectorSpec, cursor: str | None):
        if seen_cursors is not None:
            seen_cursors.append(cursor)
        batch, next_cursor = batches.pop(0)
        return batch, next_cursor

    return _fetch


class TestSync:
    def test_sync_ok(self) -> None:
        health_log: list = []
        hub = _registered_hub(
            fetcher=_scripted_fetcher([([{"id": "n1", "title": "快讯"}, {"id": "n2"}], "cur-2")]),
            health_sink=health_log.append,
        )
        count = hub.sync("akshare_news")
        assert count == 2
        records = hub.records("akshare_news")
        assert [r.external_id for r in records] == ["n1", "n2"]
        assert records[0].payload == {"title": "快讯"}  # 适配器规范化
        assert records[0].fetched_at == _T0
        assert hub.cursor_of("akshare_news") == "cur-2"
        latest = hub.latest_health("akshare_news")
        assert latest is not None and latest.success is True and latest.new_records == 2
        assert health_log == [latest]  # source_health 回调登记

    def test_sync_resume_uses_cursor(self) -> None:
        seen: list = []
        hub = _registered_hub(
            fetcher=_scripted_fetcher(
                [([{"id": "n1"}], "cur-2"), ([{"id": "n2"}], "cur-3")],
                seen_cursors=seen,
            )
        )
        hub.sync("akshare_news")
        hub.sync("akshare_news")
        assert seen == [None, "cur-2"]  # 首抓游标 None，续抓用上一游标
        assert [r.external_id for r in hub.records("akshare_news")] == ["n1", "n2"]

    def test_sync_dedup_idempotent(self) -> None:
        hub = _registered_hub(
            fetcher=_scripted_fetcher(
                [([{"id": "n1"}], "cur-2"), ([{"id": "n1"}, {"id": "n2"}], "cur-3")],
            )
        )
        assert hub.sync("akshare_news") == 1
        assert hub.sync("akshare_news") == 1  # n1 重传去重，仅 n2 新落
        assert [r.external_id for r in hub.records("akshare_news")] == ["n1", "n2"]
        assert hub.latest_health("akshare_news").new_records == 1

    def test_sync_precondition_raises(self) -> None:
        hub = _hub(fetcher=_scripted_fetcher([([], "cur-1")]))
        with pytest.raises(AltDataConnectorError):
            hub.sync("ghost")  # 未知连接器
        hub.register(_spec())
        with pytest.raises(AltDataConnectorError):
            hub.sync("akshare_news")  # 未绑定适配器
        hub.set_adapter("akshare_news", _adapter)
        no_fetch = _hub()
        no_fetch.register(_spec())
        no_fetch.set_adapter("akshare_news", _adapter)
        with pytest.raises(AltDataConnectorError):
            no_fetch.sync("akshare_news")  # fetcher 未注入 Fail-Closed

    def test_fetcher_exception_health_failure(self) -> None:
        health_log: list = []

        def _boom(spec, cursor):
            raise RuntimeError("api down")

        hub = _registered_hub(fetcher=_boom, health_sink=health_log.append)
        with pytest.raises(AltDataConnectorError):
            hub.sync("akshare_news")
        latest = hub.latest_health("akshare_news")
        assert latest.success is False and latest.new_records == 0
        assert health_log == [latest]
        assert hub.cursor_of("akshare_news") is None  # 游标不前移，重试安全

    def test_adapter_exception_raises(self) -> None:
        def _bad(raw):
            raise ValueError("bad payload")

        hub = _registered_hub(fetcher=_scripted_fetcher([([{"id": "n1"}], "cur-2")]))
        hub.set_adapter("akshare_news", _bad)
        with pytest.raises(AltDataConnectorError):
            hub.sync("akshare_news")
        assert hub.latest_health("akshare_news").success is False
        assert hub.cursor_of("akshare_news") is None

    def test_bad_fetch_contract_raises(self) -> None:
        hub = _registered_hub(fetcher=_scripted_fetcher([([{"id": "n1"}], "")]))
        with pytest.raises(AltDataConnectorError):
            hub.sync("akshare_news")  # next_cursor 空非法
        hub2 = _registered_hub(fetcher=_scripted_fetcher([("not-a-list", "cur-2")]))
        with pytest.raises(AltDataConnectorError):
            hub2.sync("akshare_news")  # raw_batch 类型非法
        hub3 = _registered_hub(fetcher=_scripted_fetcher([([{"id": "n1"}], "cur-2")]))
        hub3.set_adapter("akshare_news", lambda raw: ("", {}))
        with pytest.raises(AltDataConnectorError):
            hub3.sync("akshare_news")  # external_id 空非法

    def test_health_sink_exception_not_blocking(self) -> None:
        def _sink(_health):
            raise RuntimeError("sink down")

        hub = _registered_hub(
            fetcher=_scripted_fetcher([([{"id": "n1"}], "cur-2")]),
            health_sink=_sink,
        )
        assert hub.sync("akshare_news") == 1  # 回调异常不阻断
        assert hub.latest_health("akshare_news").success is True


# ──────────────────────────────────────────────────────────────────────────────
# checkpoint 导出/恢复
# ──────────────────────────────────────────────────────────────────────────────


class TestCheckpoint:
    def test_export_cursor_lifecycle(self) -> None:
        hub = _registered_hub(fetcher=_scripted_fetcher([([{"id": "n1"}], "cur-2")]))
        cp0 = hub.export_checkpoint("akshare_news")
        assert cp0.cursor is None and cp0.exported_at == _T0  # 未同步过
        hub.sync("akshare_news")
        cp1 = hub.export_checkpoint("akshare_news")
        assert cp1.cursor == "cur-2" and cp1.connector_id == "akshare_news"

    def test_restore_resume(self) -> None:
        seen: list = []
        hub = _registered_hub(
            fetcher=_scripted_fetcher(
                [([{"id": "n9"}], "cur-10")],
                seen_cursors=seen,
            )
        )
        hub.restore_checkpoint(
            SyncCheckpoint(
                connector_id="akshare_news",
                cursor="cur-7",
                exported_at=_T0,
            )
        )
        hub.sync("akshare_news")
        assert seen == ["cur-7"]  # 断点续传自恢复游标起抓

    def test_restore_invalid_raises(self) -> None:
        hub = _registered_hub()
        with pytest.raises(AltDataConnectorError):
            hub.restore_checkpoint(SyncCheckpoint("akshare_news", None, _T0))  # 空游标
        with pytest.raises(AltDataConnectorError):
            hub.restore_checkpoint(SyncCheckpoint("akshare_news", "", _T0))
        with pytest.raises(AltDataConnectorError):
            hub.restore_checkpoint(SyncCheckpoint("ghost", "cur-1", _T0))  # 未知连接器
        with pytest.raises(AltDataConnectorError):
            hub.restore_checkpoint("not-a-checkpoint")  # 类型非法
        with pytest.raises(AltDataConnectorError):
            hub.export_checkpoint("ghost")
