"""local_replay 单测（MOD-L00-004，裁定 #ARCH-CH-013 Phase 2）。

测试内容：
- save_fallback（用 tmp_path 隔离，不污染真实 data/local_fallback/）
- has_backlog / get_backlog_summary
- _replay_one_file（mock ch_writer_mod.write_tsv）
  - 成功/失败/跳过/异常
  - 表名前缀补全（裸表名→<_DEFAULT_DB>.<table>，裁定 Phase 2）
  - cols_clause 始终传 None（裁定 Phase 1 根因修复）
- replay_batch（mock ch_writer.write_tsv）
  - 空 manifest / 成功 / 失败保留 / max_files 限制

不依赖真实 ClickHouse 和真实 data/local_fallback/ 目录。
"""
import json
from unittest.mock import patch, MagicMock

import pytest

from src.zephyr.data import local_replay
from src.zephyr.data.local_replay import (
    save_fallback,
    has_backlog,
    get_backlog_summary,
    _replay_one_file,
    replay_batch,
)


class TestSaveFallback:
    """save_fallback 测试（用 tmp_path 隔离）。"""

    def test_save_success(self, tmp_path, monkeypatch):
        """成功落盘：文件存在 + manifest 条目存在。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")

        ok = save_fallback("c1_market.kline_daily", "(col1, col2)", b"v1\tv2\nv3\tv4\n")

        assert ok is True
        # 验证文件存在
        table_dir = tmp_path / "c1_market__kline_daily"
        assert table_dir.exists()
        tsv_files = list(table_dir.glob("*.tsv"))
        assert len(tsv_files) == 1
        # 验证 manifest
        manifest = (tmp_path / "_manifest.jsonl").read_text(encoding="utf-8")
        entry = json.loads(manifest.strip())
        assert entry["table"] == "c1_market.kline_daily"
        assert entry["cols_clause"] == "(col1, col2)"
        assert entry["rows"] == 2

    def test_save_empty_data(self, tmp_path, monkeypatch):
        """空数据直接返回 True，不落盘。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")

        ok = save_fallback("c1_market.test", None, b"")

        assert ok is True
        assert not (tmp_path / "_manifest.jsonl").exists()

    def test_save_none_cols_clause(self, tmp_path, monkeypatch):
        """cols_clause=None 时 manifest 记录 null。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")

        ok = save_fallback("c1_market.test", None, b"v1\n")

        assert ok is True
        manifest = (tmp_path / "_manifest.jsonl").read_text(encoding="utf-8")
        entry = json.loads(manifest.strip())
        assert entry["cols_clause"] is None


class TestHasBacklog:
    """has_backlog 测试。"""

    def test_no_manifest(self, tmp_path, monkeypatch):
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")
        assert has_backlog() is False

    def test_empty_manifest(self, tmp_path, monkeypatch):
        manifest = tmp_path / "_manifest.jsonl"
        manifest.write_text("", encoding="utf-8")
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest)
        assert has_backlog() is False

    def test_has_manifest(self, tmp_path, monkeypatch):
        manifest = tmp_path / "_manifest.jsonl"
        manifest.write_text('{"table":"t","file":"f.tsv","rows":1}\n', encoding="utf-8")
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest)
        assert has_backlog() is True


class TestGetBacklogSummary:
    """get_backlog_summary 测试。"""

    def test_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")
        assert get_backlog_summary() == {}

    def test_multi_table(self, tmp_path, monkeypatch):
        manifest = tmp_path / "_manifest.jsonl"
        manifest.write_text(
            '{"table":"c1_market.a","file":"f1.tsv","rows":10}\n'
            '{"table":"c1_market.a","file":"f2.tsv","rows":5}\n'
            '{"table":"c1_market.b","file":"f3.tsv","rows":3}\n',
            encoding="utf-8",
        )
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest)
        summary = get_backlog_summary()
        assert summary == {"c1_market.a": 15, "c1_market.b": 3}


class TestReplayOneFile:
    """_replay_one_file 测试（mock ch_writer_mod 参数）。"""

    def test_file_not_exist(self, tmp_path, monkeypatch):
        """文件不存在→skipped。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        entry = {"table": "c1_market.test", "file": "nonexistent.tsv", "rows": 1}
        mock_cw = MagicMock()

        status = _replay_one_file(entry, mock_cw)

        assert status == "skipped"
        mock_cw.write_tsv.assert_not_called()

    def test_replay_success(self, tmp_path, monkeypatch):
        """回灌成功→replayed + 文件删除。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\tv2\n")
        entry = {"table": "c1_market.test", "file": "data.tsv", "rows": 1}
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = True

        status = _replay_one_file(entry, mock_cw)

        assert status == "replayed"
        assert not tsv_path.exists()  # 文件已删除
        mock_cw.write_tsv.assert_called_once()

    def test_replay_failure_keeps_file(self, tmp_path, monkeypatch):
        """回灌失败→failed + 文件保留。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {"table": "c1_market.test", "file": "data.tsv", "rows": 1}
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = False

        status = _replay_one_file(entry, mock_cw)

        assert status == "failed"
        assert tsv_path.exists()  # 文件保留

    def test_replay_exception_returns_failed(self, tmp_path, monkeypatch):
        """回灌异常→failed（不抛出，ERROR_CONTRACT 保证）。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {"table": "c1_market.test", "file": "data.tsv", "rows": 1}
        mock_cw = MagicMock()
        mock_cw.write_tsv.side_effect = Exception("CH down")

        status = _replay_one_file(entry, mock_cw)

        assert status == "failed"

    def test_cols_clause_always_none(self, tmp_path, monkeypatch):
        """回灌时 cols_clause 始终传 None（裁定 #ARCH-CH-013 Phase 1 根因修复）。

        即使 manifest 中 cols_clause 有值，回灌时也必须传 None，
        强制 ch_writer 重新查询表列，避免使用过期/无效列清单。
        """
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {
            "table": "c1_market.test",
            "file": "data.tsv",
            "rows": 1,
            "cols_clause": "(a, b)",  # manifest 中有值
        }
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = True

        _replay_one_file(entry, mock_cw)

        # 验证 write_tsv 第二个位置参数（columns）是 None
        call_args = mock_cw.write_tsv.call_args
        assert call_args[0][1] is None

    def test_full_table_name_no_prefix(self, tmp_path, monkeypatch):
        """完整表名（含 db. 前缀）不补全。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {"table": "c1_market.kline_daily", "file": "data.tsv", "rows": 1}
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = True

        _replay_one_file(entry, mock_cw)

        call_args = mock_cw.write_tsv.call_args
        assert call_args[0][0] == "c1_market.kline_daily"

    def test_bare_table_name_gets_default_prefix(self, tmp_path, monkeypatch):
        """裸表名补全为 <_DEFAULT_DB>.<table>（裁定 #ARCH-CH-013 Phase 2）。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_DEFAULT_DB", "c1_market")
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {"table": "kline_daily", "file": "data.tsv", "rows": 1}  # 裸表名
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = True

        _replay_one_file(entry, mock_cw)

        call_args = mock_cw.write_tsv.call_args
        assert call_args[0][0] == "c1_market.kline_daily"

    def test_bare_table_name_custom_db(self, tmp_path, monkeypatch):
        """_DEFAULT_DB 支持多库场景（如 c3_fundamental）。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_DEFAULT_DB", "c3_fundamental")
        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")
        entry = {"table": "news_data", "file": "data.tsv", "rows": 1}
        mock_cw = MagicMock()
        mock_cw.write_tsv.return_value = True

        _replay_one_file(entry, mock_cw)

        call_args = mock_cw.write_tsv.call_args
        assert call_args[0][0] == "c3_fundamental.news_data"


class TestReplayBatch:
    """replay_batch 测试（mock ch_writer.write_tsv）。"""

    def test_empty_manifest(self, tmp_path, monkeypatch):
        """空 manifest→全0。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", tmp_path / "_manifest.jsonl")

        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True):
            result = replay_batch()

        assert result == {"replayed": 0, "failed": 0, "remaining": 0}

    def test_replay_success(self, tmp_path, monkeypatch):
        """成功回灌→replayed+1, remaining=0, manifest 删除。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        manifest_path = tmp_path / "_manifest.jsonl"

        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")

        entry = {"table": "c1_market.test", "file": "data.tsv", "rows": 1}
        manifest_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest_path)

        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True) as mock_w:
            result = replay_batch()

        assert result["replayed"] == 1
        assert result["failed"] == 0
        assert result["remaining"] == 0
        assert not manifest_path.exists()  # 无剩余条目，manifest 删除
        assert not tsv_path.exists()  # 文件删除
        mock_w.assert_called_once()

    def test_replay_failure_keeps_entry(self, tmp_path, monkeypatch):
        """回灌失败→failed+1, remaining+1, manifest 保留。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        manifest_path = tmp_path / "_manifest.jsonl"

        tsv_path = tmp_path / "data.tsv"
        tsv_path.write_bytes(b"v1\n")

        entry = {"table": "c1_market.test", "file": "data.tsv", "rows": 1}
        manifest_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest_path)

        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=False):
            result = replay_batch()

        assert result["replayed"] == 0
        assert result["failed"] == 1
        assert result["remaining"] == 1
        assert manifest_path.exists()  # manifest 保留
        assert tsv_path.exists()  # 文件保留

    def test_max_files_limit(self, tmp_path, monkeypatch):
        """max_files 限制：超过上限的条目保留在 manifest。"""
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        manifest_path = tmp_path / "_manifest.jsonl"

        # 准备 3 个文件
        entries = []
        for i in range(3):
            (tmp_path / f"data{i}.tsv").write_bytes(b"v1\n")
            entries.append({"table": "c1_market.test", "file": f"data{i}.tsv", "rows": 1})
        manifest_path.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
        )
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest_path)

        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True):
            result = replay_batch(max_files=2)  # 只回灌2个

        assert result["replayed"] == 2
        assert result["remaining"] == 1
        assert manifest_path.exists()  # 剩余1条
