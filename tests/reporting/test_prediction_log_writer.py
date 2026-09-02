# [BLUEPRINT] MOD-L07-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""prediction_log 统一落库写入器单元测试（92号清单 §7.13 M4-②，44号备忘 §12.1）。

覆盖：
- 写入-查询闭环（tmp 库复刻生产 schema——ensure_prediction_log_table 即 DDL 真源，
  禁止测试侧复刻副本；trend_analyzer db_path 注入同款隔离先例）；
- 幂等键 UNIQUE(trade_date, module, prediction_type, input_hash)：同键重复写=跳过
  保首条返回同 id；input_hash 缺省=canonical payload SHA-256 内容寻址；
- 非法输入 fail-closed（空 module/非法与非真实 date/非 JSON 可序列化 payload/
  非法 asof_ts/非法 limit/非 str 可空字段）；
- JSON 序列化（Decimal/datetime/Enum 放行，中文 ensure_ascii=False，sort_keys 稳定序）；
- 多模块多日期查询过滤 + 倒序 + limit 截断；默认 db_path 走 DB_PATH SSoT
  （monkeypatch 模块常量指向 tmp，不触真 governance.db）。
全 tmp 隔离，不连生产库。
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path

import pytest

from zephyr.reporting import prediction_log_writer as plw
from zephyr.reporting.prediction_log_writer import (
    ensure_prediction_log_table,
    log_prediction,
    query_predictions,
)

DATE_A = "2026-08-21"
DATE_B = "2026-08-22"


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    """tmp 库 + 幂等建表（DDL 真源=被测模块常量）。"""
    db = tmp_path / "governance.db"
    ensure_prediction_log_table(db)
    return db


# ── 写入-查询闭环 ──


class TestWriteQueryRoundtrip:
    def test_write_then_query(self, tmp_db: Path) -> None:
        """写入一条后按 trade_date 查询回读全字段。"""
        rid = log_prediction(
            trade_date=DATE_A,
            module="signal_ashare.market_sentiment",
            prediction_type="sentiment_score",
            payload={"score": 58, "degraded": False},
            asof_ts="2026-08-21T14:00:00+08:00",
            model_version="v1.0",
            db_path=tmp_db,
        )
        assert rid >= 1
        rows = query_predictions(trade_date=DATE_A, db_path=tmp_db)
        assert len(rows) == 1
        row = rows[0]
        assert row["id"] == rid
        assert row["module"] == "signal_ashare.market_sentiment"
        assert row["prediction_type"] == "sentiment_score"
        assert json.loads(row["payload_json"]) == {"score": 58, "degraded": False}
        assert row["asof_ts"] == "2026-08-21T14:00:00+08:00"
        assert row["model_version"] == "v1.0"
        assert row["prompt_version"] is None
        assert row["input_hash"]  # 缺省自动内容寻址，非空
        assert row["created_at"]

    def test_query_empty_db(self, tmp_db: Path) -> None:
        """空库查询返回空列表。"""
        assert query_predictions(db_path=tmp_db) == []


# ── 幂等键 ──


class TestIdempotency:
    def test_duplicate_same_key_skipped(self, tmp_db: Path) -> None:
        """显式同 hash 同键重复写=跳过保首条，返回同 id，仅一行。"""
        kwargs = {
            "trade_date": DATE_A,
            "module": "m1",
            "prediction_type": "t1",
            "payload": {"v": 1},
            "input_hash": "h-001",
            "db_path": tmp_db,
        }
        rid1 = log_prediction(**kwargs)
        rid2 = log_prediction(**kwargs)
        assert rid1 == rid2
        assert len(query_predictions(db_path=tmp_db)) == 1

    def test_first_write_preserved_on_conflict(self, tmp_db: Path) -> None:
        """同显式 hash 不同 payload 重复写：首条 payload_json 不覆写（审计语义）。"""
        rid1 = log_prediction(
            trade_date=DATE_A,
            module="m1",
            prediction_type="t1",
            payload={"v": 1},
            input_hash="h-x",
            db_path=tmp_db,
        )
        rid2 = log_prediction(
            trade_date=DATE_A,
            module="m1",
            prediction_type="t1",
            payload={"v": 999},
            input_hash="h-x",
            db_path=tmp_db,
        )
        assert rid1 == rid2
        rows = query_predictions(db_path=tmp_db)
        assert len(rows) == 1
        assert json.loads(rows[0]["payload_json"]) == {"v": 1}

    def test_auto_hash_content_addressed(self, tmp_db: Path) -> None:
        """input_hash 缺省=canonical payload SHA-256；同 payload 幂等，异 payload 新行。"""
        payload = {"b": 2, "a": 1}
        rid1 = log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload=payload, db_path=tmp_db)
        rid2 = log_prediction(
            trade_date=DATE_A, module="m1", prediction_type="t1", payload=dict(payload), db_path=tmp_db
        )
        assert rid1 == rid2  # 同内容（key 序无关，canonical sort_keys）→ 幂等
        expected = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
        rows = query_predictions(db_path=tmp_db)
        assert rows[0]["input_hash"] == expected

        rid3 = log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload={"a": 2}, db_path=tmp_db)
        assert rid3 != rid1
        assert len(query_predictions(db_path=tmp_db)) == 2

    def test_same_hash_different_date_both_kept(self, tmp_db: Path) -> None:
        """唯一键含 trade_date——同 hash 跨日两行都保留（每日预测各自留痕）。"""
        rid1 = log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload={"v": 1}, db_path=tmp_db)
        rid2 = log_prediction(trade_date=DATE_B, module="m1", prediction_type="t1", payload={"v": 1}, db_path=tmp_db)
        assert rid1 != rid2
        assert len(query_predictions(db_path=tmp_db)) == 2


# ── 非法输入 fail-closed ──


class TestInputValidation:
    def test_reject_empty_module(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="module"):
            log_prediction(trade_date=DATE_A, module="  ", prediction_type="t1", payload={}, db_path=tmp_db)

    def test_reject_empty_prediction_type(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="prediction_type"):
            log_prediction(trade_date=DATE_A, module="m1", prediction_type="", payload={}, db_path=tmp_db)

    def test_reject_bad_date_format(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            log_prediction(trade_date="2026/08/21", module="m1", prediction_type="t1", payload={}, db_path=tmp_db)

    def test_reject_unreal_date(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            log_prediction(trade_date="2026-02-30", module="m1", prediction_type="t1", payload={}, db_path=tmp_db)

    def test_reject_non_serializable_payload(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="payload"):
            log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload={"s": {1, 2}}, db_path=tmp_db)
        with pytest.raises(ValueError, match="payload"):
            log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload=object(), db_path=tmp_db)

    def test_reject_bad_asof_ts(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="asof_ts"):
            log_prediction(
                trade_date=DATE_A, module="m1", prediction_type="t1", payload={}, asof_ts="not-a-ts", db_path=tmp_db
            )

    def test_reject_non_str_optional_field(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="model_version"):
            log_prediction(
                trade_date=DATE_A, module="m1", prediction_type="t1", payload={}, model_version=123, db_path=tmp_db
            )

    def test_reject_bad_limit(self, tmp_db: Path) -> None:
        for bad in (0, -1, True, "10"):
            with pytest.raises(ValueError, match="limit"):
                query_predictions(limit=bad, db_path=tmp_db)

    def test_reject_bad_query_filter(self, tmp_db: Path) -> None:
        with pytest.raises(ValueError, match="trade_date"):
            query_predictions(trade_date="昨天", db_path=tmp_db)

    def test_validation_before_db_touch(self, tmp_path: Path) -> None:
        """输入非法时 fail-closed 在校验层——不存在的库路径也不应先建库文件。"""
        ghost = tmp_path / "ghost" / "never.db"
        with pytest.raises(ValueError):
            log_prediction(trade_date="bad", module="m1", prediction_type="t1", payload={}, db_path=ghost)
        assert not ghost.exists()


# ── JSON 序列化 ──


class _Color(Enum):
    RED = "red"


class TestJsonSerialization:
    def test_canonical_types_accepted(self, tmp_db: Path) -> None:
        """Decimal/datetime/Enum 按 canonical 规则放行（Decimal→str，dt→ISO，Enum→value）。"""
        rid = log_prediction(
            trade_date=DATE_A,
            module="m1",
            prediction_type="t1",
            payload={"price": Decimal("12.34"), "ts": datetime(2026, 8, 21, 15, 0, tzinfo=UTC), "c": _Color.RED},
            db_path=tmp_db,
        )
        row = query_predictions(db_path=tmp_db)[0]
        assert row["id"] == rid
        data = json.loads(row["payload_json"])
        assert data["price"] == "12.34"
        assert data["ts"] == "2026-08-21T15:00:00.000000Z"  # canonical serialization 口径（Z 后缀）
        assert data["c"] == "red"

    def test_chinese_and_sort_keys(self, tmp_db: Path) -> None:
        """中文 ensure_ascii=False 原样落库；canonical sort_keys 稳定序。"""
        log_prediction(
            trade_date=DATE_A,
            module="m1",
            prediction_type="t1",
            payload={"板块": "半导体", "alpha": 1},
            db_path=tmp_db,
        )
        raw = query_predictions(db_path=tmp_db)[0]["payload_json"]
        assert "半导体" in raw
        assert raw.index('"alpha"') < raw.index('"板块"')  # sort_keys 稳定序


# ── 多模块多日期过滤 ──


class TestQueryFilters:
    @pytest.fixture
    def seeded_db(self, tmp_db: Path) -> Path:
        log_prediction(
            trade_date=DATE_A, module="m1", prediction_type="sentiment_score", payload={"s": 50}, db_path=tmp_db
        )
        log_prediction(
            trade_date=DATE_A, module="m2", prediction_type="scenario_plan", payload={"p": 1}, db_path=tmp_db
        )
        log_prediction(
            trade_date=DATE_B, module="m1", prediction_type="sentiment_score", payload={"s": 60}, db_path=tmp_db
        )
        log_prediction(
            trade_date=DATE_B, module="m1", prediction_type="boundary_revision", payload={"b": 1}, db_path=tmp_db
        )
        return tmp_db

    def test_filter_by_trade_date(self, seeded_db: Path) -> None:
        rows = query_predictions(trade_date=DATE_A, db_path=seeded_db)
        assert len(rows) == 2
        assert {r["module"] for r in rows} == {"m1", "m2"}

    def test_filter_by_module(self, seeded_db: Path) -> None:
        rows = query_predictions(module="m2", db_path=seeded_db)
        assert len(rows) == 1
        assert rows[0]["prediction_type"] == "scenario_plan"

    def test_filter_by_type(self, seeded_db: Path) -> None:
        rows = query_predictions(prediction_type="sentiment_score", db_path=seeded_db)
        assert len(rows) == 2

    def test_filter_combined(self, seeded_db: Path) -> None:
        rows = query_predictions(trade_date=DATE_B, module="m1", prediction_type="boundary_revision", db_path=seeded_db)
        assert len(rows) == 1
        assert json.loads(rows[0]["payload_json"]) == {"b": 1}

    def test_order_desc_and_limit(self, seeded_db: Path) -> None:
        rows = query_predictions(db_path=seeded_db)
        assert [r["trade_date"] for r in rows] == [DATE_B, DATE_B, DATE_A, DATE_A]  # 倒序
        assert len(query_predictions(limit=2, db_path=seeded_db)) == 2


# ── 建表幂等 / 默认路径 SSoT ──


class TestDdl:
    def test_ensure_table_idempotent(self, tmp_path: Path) -> None:
        """两次建表不炸；表+两索引+UNIQUE 在册。"""
        db = tmp_path / "g.db"
        ensure_prediction_log_table(db)
        ensure_prediction_log_table(db)  # 幂等
        conn = sqlite3.connect(str(db))
        try:
            names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE tbl_name='prediction_log'")}
        finally:
            conn.close()
        assert {"prediction_log", "idx_prediction_log_trade_date", "idx_prediction_log_module"} <= names
        assert any("autoindex" in n for n in names)  # UNIQUE 键自动索引

    def test_default_db_path_is_ssot(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """db_path=None 走模块 DB_PATH 常量（monkeypatch 指向 tmp，不触真 governance.db）。"""
        fake = tmp_path / "ssot.db"
        monkeypatch.setattr(plw, "DB_PATH", fake)
        ensure_prediction_log_table()  # None → fake
        rid = log_prediction(trade_date=DATE_A, module="m1", prediction_type="t1", payload={"v": 1})
        assert fake.exists()
        assert query_predictions()[0]["id"] == rid
