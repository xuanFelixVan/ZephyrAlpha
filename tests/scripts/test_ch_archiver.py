# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §19
# [TTL] permanent
"""Unit tests for scripts/ch/archiver.py — 元组分区键（--period）支持 + news 分区表达式修复。

契约依据：data_retention_contract.yaml §2A 派生数据治理（v1.2.0，2026-08-16）：
  - 原则3 唯一通道：派生表窗口外数据只能经 archiver.py 归档
  - technical_indicator PARTITION BY (period, toYYYYMM(trade_date))，归档必须按周期维度

锁定的事实：
  - c3_fundamental.news_data 真实时间列是 publish_time（publish_date 列不存在——原配置从未被执行过）
  - 旧清单记录无 period 键，与非元组表 period=None 匹配（向后兼容）
  - Parquet 路径约定：元组键表按周期子目录分层 technical_indicator/60min/201901.parquet
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("ch_archiver", _ROOT / "scripts" / "ch" / "archiver.py")
archiver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(archiver)


# ============== _require_period ==============


class TestRequirePeriod:
    def test_tuple_table_missing_period_raises(self):
        with pytest.raises(ValueError, match="必须指定 --period"):
            archiver._require_period("c1_market.technical_indicator", None)

    def test_tuple_table_with_period_ok(self):
        archiver._require_period("c1_market.technical_indicator", "60min")

    def test_plain_table_with_period_raises(self):
        with pytest.raises(ValueError, match="禁止指定 --period"):
            archiver._require_period("c1_market.kline_1min", "60min")

    def test_plain_table_without_period_ok(self):
        archiver._require_period("c1_market.kline_1min", None)


# ============== _build_where ==============


class TestBuildWhere:
    def test_plain_table(self):
        w = archiver._build_where("c1_market.kline_1min", "201901", None)
        assert w == "toYYYYMM(trade_date) = 201901"

    def test_tuple_table_adds_period_filter(self):
        w = archiver._build_where("c1_market.technical_indicator", "201901", "60min")
        assert w == "period = '60min' AND toYYYYMM(trade_date) = 201901"

    def test_news_uses_publish_time(self):
        """回归：news_data 真实列是 publish_time（publish_date 不存在）。"""
        w = archiver._build_where("c3_fundamental.news_data", "200001", None)
        assert w == "toYYYYMM(publish_time) = 200001"
        assert "publish_date" not in archiver._PARTITION_EXPR["c3_fundamental.news_data"]


# ============== _drop_partition_sql ==============


class TestDropPartitionSql:
    def test_plain(self):
        assert (
            archiver._drop_partition_sql("c1_market.kline_1min", "201901", None)
            == "ALTER TABLE c1_market.kline_1min DROP PARTITION 201901"
        )

    def test_tuple_literal_form(self):
        assert (
            archiver._drop_partition_sql("c1_market.technical_indicator", "201901", "60min")
            == "ALTER TABLE c1_market.technical_indicator DROP PARTITION ('60min',201901)"
        )


# ============== _parquet_path ==============


class TestParquetPath:
    def test_plain(self):
        p = archiver._parquet_path("c1_market.kline_1min", "201901")
        assert p == archiver.ARCHIVE_ROOT / "c1_market" / "kline_1min" / "201901.parquet"

    def test_tuple_period_subdir(self):
        p = archiver._parquet_path("c1_market.technical_indicator", "201901", "60min")
        assert p == archiver.ARCHIVE_ROOT / "c1_market" / "technical_indicator" / "60min" / "201901.parquet"


# ============== _get_partitions（mock ch_reader）==============


class TestGetPartitions:
    def test_tuple_filter_and_range(self, monkeypatch):
        fake = "('60min',201812)\n('60min',201901)\n('60min',202108)\n('60min',202109)\n('120min',201901)\n"
        monkeypatch.setattr(archiver.ch_reader, "query", lambda sql: fake)
        got = archiver._get_partitions("c1_market.technical_indicator", "201901", "202108", period="60min")
        assert got == ["201901", "202108"]

    def test_plain_range(self, monkeypatch):
        fake = "201812\n201901\n201902\n201903\n"
        monkeypatch.setattr(archiver.ch_reader, "query", lambda sql: fake)
        got = archiver._get_partitions("c1_market.kline_1min", "201901", "201902")
        assert got == ["201901", "201902"]


# ============== _is_archived（mock manifest）==============


class TestIsArchived:
    def _records(self):
        return [
            {"table": "c1_market.kline_1min", "partition": "201901", "dropped": True},
            {"table": "c1_market.technical_indicator", "partition": "201901", "period": "60min", "dropped": True},
        ]

    def test_legacy_record_matches_none_period(self, monkeypatch):
        monkeypatch.setattr(archiver, "_read_manifest", lambda: self._records())
        assert archiver._is_archived("c1_market.kline_1min", "201901", None) is not None

    def test_period_record_matches_same_period(self, monkeypatch):
        monkeypatch.setattr(archiver, "_read_manifest", lambda: self._records())
        assert archiver._is_archived("c1_market.technical_indicator", "201901", "60min") is not None

    def test_period_record_not_matches_other_period(self, monkeypatch):
        monkeypatch.setattr(archiver, "_read_manifest", lambda: self._records())
        assert archiver._is_archived("c1_market.technical_indicator", "201901", "120min") is None


# ============== _manifest_record ==============


class TestManifestRecord:
    def test_period_attached_only_when_present(self, tmp_path):
        pq = tmp_path / "x.parquet"
        pq.write_bytes(b"1234")
        r_plain = archiver._manifest_record("c1_market.kline_1min", "201901", pq, True, None)
        assert "period" not in r_plain
        r_tuple = archiver._manifest_record("c1_market.technical_indicator", "201901", pq, True, "60min")
        assert r_tuple["period"] == "60min"
        assert r_tuple["parquet_size_bytes"] == 4


# ============== export 注入 FINAL（重复摄入治本，2026-08-16）==============


class TestExportInjectsFinal:
    def test_export_sql_passes_through_inject_final(self, monkeypatch, tmp_path):
        """export_partition 构造的 SQL 必须经 ch_reader.inject_final 处理。"""
        monkeypatch.setattr(archiver, "ARCHIVE_ROOT", tmp_path)
        calls: list[str] = []
        monkeypatch.setattr(archiver.ch_reader, "inject_final", lambda sql: calls.append(sql) or sql)
        archiver.export_partition("c1_market.kline_5min", "202101", dry_run=True)
        assert len(calls) == 1
        assert "toYYYYMM(trade_time) = 202101" in calls[0]

    def test_final_injected_for_replacing_table(self, monkeypatch):
        """ReplacingMergeTree 表导出带 FINAL（逻辑视图=消费者所读）。"""
        monkeypatch.setattr(archiver.ch_reader.ch_writer, "is_replacing_engine", lambda t: True)
        sql = archiver.ch_reader.inject_final("SELECT * FROM c1_market.kline_5min WHERE x = 1 FORMAT Parquet")
        assert "FROM c1_market.kline_5min FINAL WHERE" in sql

    def test_final_not_injected_for_plain_table(self, monkeypatch):
        """非 ReplacingMergeTree 表（如 tick_data）不注入 FINAL。"""
        monkeypatch.setattr(archiver.ch_reader.ch_writer, "is_replacing_engine", lambda t: False)
        sql = archiver.ch_reader.inject_final("SELECT * FROM c1_market.tick_data WHERE x = 1 FORMAT Parquet")
        assert "FINAL" not in sql


# ============== verify 强化 + 独立 export（18 号 §10 开放问题 6，AI-NIGHT-001）==============

import datetime as _dt
import hashlib as _hashlib
import json as _json

import pandas as _pd
import pyarrow as _pa
import pyarrow.parquet as _pq


def _write_test_parquet(path, rows: int = 50, corrupt_symbol: str | None = None) -> list[dict]:
    """构造测试 Parquet（symbol/trade_date/OHLC/volume），返回行 dict 列表。"""
    data = []
    for i in range(rows):
        data.append(
            {
                "symbol": corrupt_symbol if (corrupt_symbol and i == 0) else f"000{i:03d}.SZ",
                "trade_date": _dt.date(2021, 1, 4) + _dt.timedelta(days=i % 20),
                "open": 10.0 + i * 0.1,
                "high": 10.5 + i * 0.1,
                "low": 9.5 + i * 0.1,
                "close": 10.2 + i * 0.1,
                "volume": 100000 + i,
            }
        )
    df = _pd.DataFrame(data)
    _pq.write_table(_pa.Table.from_pandas(df), str(path))
    return data


def _ch_json(rows: list[dict]) -> str:
    """模拟 ClickHouse FORMAT JSON 输出（date→str）。"""

    def conv(v):
        if isinstance(v, (_dt.date, _dt.datetime)):
            return v.isoformat()
        return v

    return _json.dumps({"data": [{k: conv(v) for k, v in r.items()} for r in rows]})


class TestFileMd5:
    def test_known_content(self, tmp_path):
        p = tmp_path / "x.bin"
        p.write_bytes(b"abc")
        assert archiver._file_md5(p) == _hashlib.md5(b"abc").hexdigest()

    def test_empty_file(self, tmp_path):
        p = tmp_path / "e.bin"
        p.write_bytes(b"")
        assert archiver._file_md5(p) == _hashlib.md5(b"").hexdigest()


class TestNormalizeVal:
    def test_nulls(self):
        assert archiver._normalize_val(None) == ""
        assert archiver._normalize_val(float("nan")) == ""

    def test_date_iso(self):
        assert archiver._normalize_val(_dt.date(2021, 1, 4)) == "2021-01-04"

    def test_tz_timestamp_matches_ch_json(self):
        ts = _pd.Timestamp("2021-01-04 09:30:00.500", tz="Asia/Shanghai")
        assert archiver._normalize_val(ts) == "2021-01-04 09:30:00.500"

    def test_float32_rounding(self):
        import numpy as np

        assert archiver._normalize_val(np.float32(12.34)) == archiver._normalize_val(12.34)

    def test_int_and_str(self):
        assert archiver._normalize_val(123) == "123"
        assert archiver._normalize_val("abc") == "abc"


class TestVerifySampleFieldComparison:
    """抽样 100 行字段值比对（符号/OHLC/volume 精确比对，替换原"可查性确认"）。"""

    def _setup(self, monkeypatch, tmp_path, rows: list[dict], sample: list[dict]):
        pq_path = tmp_path / "p.parquet"
        _pq.write_table(_pa.Table.from_pandas(_pd.DataFrame(rows)), str(pq_path))

        def fake_query(sql):
            if sql.startswith("SELECT count()"):
                return str(len(rows))
            if "ORDER BY rand() LIMIT 100" in sql:
                return _ch_json(sample)
            raise AssertionError(f"unexpected SQL: {sql}")

        monkeypatch.setattr(archiver.ch_reader, "query", fake_query)
        monkeypatch.setattr(archiver.ch_reader, "inject_final", lambda s: s)
        return pq_path

    def test_sample_match_passes(self, monkeypatch, tmp_path):
        rows = _write_test_parquet(tmp_path / "seed.parquet", 50)
        sample = [rows[3], rows[10], rows[49]]
        pq_path = self._setup(monkeypatch, tmp_path, rows, sample)
        assert archiver.verify_partition("c1_market.kline_1min", "202101", pq_path) is True

    def test_sample_value_mismatch_fails(self, monkeypatch, tmp_path):
        rows = _write_test_parquet(tmp_path / "seed.parquet", 50)
        bad = dict(rows[3])
        bad["close"] = 999.99  # 字段值篡改
        pq_path = self._setup(monkeypatch, tmp_path, rows, [rows[10], bad])
        assert archiver.verify_partition("c1_market.kline_1min", "202101", pq_path) is False

    def test_sample_phantom_row_fails(self, monkeypatch, tmp_path):
        rows = _write_test_parquet(tmp_path / "seed.parquet", 50)
        phantom = dict(rows[0])
        phantom["symbol"] = "999999.SZ"  # CH 有而 Parquet 无（幻影行）
        pq_path = self._setup(monkeypatch, tmp_path, rows, [phantom])
        assert archiver.verify_partition("c1_market.kline_1min", "202101", pq_path) is False

    def test_count_mismatch_fails(self, monkeypatch, tmp_path):
        rows = _write_test_parquet(tmp_path / "seed.parquet", 50)
        pq_path = self._setup(monkeypatch, tmp_path, rows, rows[:1])
        monkeypatch.setattr(
            archiver.ch_reader, "query", lambda sql: "51" if sql.startswith("SELECT count()") else _ch_json(rows[:1])
        )
        assert archiver.verify_partition("c1_market.kline_1min", "202101", pq_path) is False

    def test_missing_parquet_fails(self, tmp_path):
        assert archiver.verify_partition("c1_market.kline_1min", "202101", tmp_path / "nope.parquet") is False


class TestManifestExtendedFields:
    def test_rows_ch_size_compress_ratio_checksum(self, tmp_path):
        pq = tmp_path / "x.parquet"
        _write_test_parquet(pq, 20)
        rec = archiver._manifest_record(
            "c1_market.kline_1min",
            "202101",
            pq,
            True,
            None,
            rows=20,
            ch_size_bytes=pq.stat().st_size * 4,
        )
        assert rec["rows"] == 20
        assert rec["ch_size_bytes"] == pq.stat().st_size * 4
        assert rec["compress_ratio"] == pytest.approx(0.25)
        assert rec["checksum_md5"] == _hashlib.md5(pq.read_bytes()).hexdigest()

    def test_optional_fields_absent_when_not_given(self, tmp_path):
        """向后兼容：不传新字段时记录不含新键（与 1865 条存量记录同形）。"""
        pq = tmp_path / "x.parquet"
        pq.write_bytes(b"1234")
        rec = archiver._manifest_record("c1_market.kline_1min", "202101", pq, True, None)
        assert "rows" not in rec and "checksum_md5" not in rec


class TestExportOnlySubcommand:
    def test_export_only_writes_manifest_not_dropped(self, monkeypatch, tmp_path):
        """纯备份模式：export+verify 后 manifest 记 verified=True/dropped=False，不删分区。"""
        pq = tmp_path / "exp.parquet"
        _write_test_parquet(pq, 20)
        monkeypatch.setattr(archiver, "ARCHIVE_ROOT", tmp_path)
        monkeypatch.setattr(archiver, "MANIFEST_PATH", tmp_path / "manifest.jsonl")
        monkeypatch.setattr(archiver, "export_partition", lambda t, p, dry_run=False, period=None: pq)
        monkeypatch.setattr(archiver, "verify_partition", lambda t, p, path, period=None: True)
        monkeypatch.setattr(archiver, "_ch_partition_size_bytes", lambda t, p, period=None: 4000)
        ok = archiver.export_only_partition("c1_market.kline_1min", "202101")
        assert ok is True
        recs = [_json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
        assert len(recs) == 1
        r = recs[0]
        assert r["verified"] is True and r["dropped"] is False
        assert r["rows"] == 20 and r["ch_size_bytes"] == 4000
        assert r["checksum_md5"] == _hashlib.md5(pq.read_bytes()).hexdigest()
        # 未执行 drop：_is_archived 判定为未归档（dropped=False），后续可正常 archive
        assert archiver._is_archived("c1_market.kline_1min", "202101", None) is None

    def test_export_only_verify_failure_no_manifest(self, monkeypatch, tmp_path):
        pq = tmp_path / "exp.parquet"
        _write_test_parquet(pq, 20)
        monkeypatch.setattr(archiver, "MANIFEST_PATH", tmp_path / "manifest.jsonl")
        monkeypatch.setattr(archiver, "export_partition", lambda t, p, dry_run=False, period=None: pq)
        monkeypatch.setattr(archiver, "verify_partition", lambda t, p, path, period=None: False)
        ok = archiver.export_only_partition("c1_market.kline_1min", "202101")
        assert ok is False
        assert not (tmp_path / "manifest.jsonl").exists()

    def test_cli_export_wiring(self, monkeypatch):
        """CLI export 子命令接线：参数正确路由到 export_only_partition。"""
        calls = []
        monkeypatch.setattr(
            archiver,
            "export_only_partition",
            lambda table, partition, dry_run=False, period=None: (
                calls.append((table, partition, dry_run, period)) or True
            ),
        )
        monkeypatch.setattr(
            "sys.argv", ["archiver.py", "export", "--table", "c1_market.kline_1min", "--partition", "202101"]
        )
        archiver.main()
        assert calls == [("c1_market.kline_1min", "202101", False, None)]


class TestRestoreChecksumGuard:
    def test_checksum_mismatch_blocks_restore(self, monkeypatch, tmp_path):
        """manifest 含 checksum 且文件腐坏 → restore 拒绝（防 E 盘静默腐坏）。"""
        pq = tmp_path / "c1_market" / "kline_1min" / "202101.parquet"
        pq.parent.mkdir(parents=True)
        _write_test_parquet(pq, 10)
        monkeypatch.setattr(archiver, "ARCHIVE_ROOT", tmp_path)
        monkeypatch.setattr(archiver, "_manifest_checksum", lambda t, p, period=None: "deadbeef")
        assert archiver.restore_partition("c1_market.kline_1min", "202101") is False

    def test_checksum_match_proceeds(self, monkeypatch, tmp_path):
        pq = tmp_path / "c1_market" / "kline_1min" / "202101.parquet"
        pq.parent.mkdir(parents=True)
        _write_test_parquet(pq, 10)
        monkeypatch.setattr(archiver, "ARCHIVE_ROOT", tmp_path)
        monkeypatch.setattr(
            archiver,
            "_manifest_checksum",
            lambda t, p, period=None: _hashlib.md5(pq.read_bytes()).hexdigest(),
        )

        class _FakeClient:
            def execute(self, sql, rows):
                return None

        monkeypatch.setattr(archiver, "_get_writer_client", lambda: _FakeClient())
        assert archiver.restore_partition("c1_market.kline_1min", "202101") is True

    def test_no_checksum_record_proceeds_legacy(self, monkeypatch, tmp_path):
        """存量记录无 checksum_md5（1865 条）→ 不校验直接恢复（向后兼容）。"""
        pq = tmp_path / "c1_market" / "kline_1min" / "202101.parquet"
        pq.parent.mkdir(parents=True)
        _write_test_parquet(pq, 10)
        monkeypatch.setattr(archiver, "ARCHIVE_ROOT", tmp_path)
        monkeypatch.setattr(archiver, "_manifest_checksum", lambda t, p, period=None: None)

        class _FakeClient:
            def execute(self, sql, rows):
                return None

        monkeypatch.setattr(archiver, "_get_writer_client", lambda: _FakeClient())
        assert archiver.restore_partition("c1_market.kline_1min", "202101") is True
