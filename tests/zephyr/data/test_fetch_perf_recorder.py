# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""fetch_perf 被动记录通道测试（64号 Q16）。

测试内容（tmp_path 隔离，不写真实 .runtime）：
- JSONL 按日滚动追加 / 字段保留 / ts 自动补
- 中文 ensure_ascii=False 保留 / 非序列化对象 default=str 容错
- 写入失败吞异常返回 None（被动记录不得阻断调度）

设计文档：64_data_source_download_spec.md §16.2 Q16
"""

from __future__ import annotations

import datetime
import json

from zephyr.data.fetch_perf_recorder import record_fetch_perf


class TestRecordFetchPerf:
    def test_writes_jsonl_with_fields(self, tmp_path):
        rec = {
            "task_id": "kline_daily_incremental",
            "source": "miniqmt",
            "capability": "kline_daily",
            "table": "c1_market.kline_daily",
            "status": "SUCCESS",
            "elapsed_sec": 12.345,
            "rows": 5207,
            "error": "",
        }
        path = record_fetch_perf(rec, base_dir=tmp_path)
        assert path is not None and path.is_file()
        day = datetime.date.today().isoformat().replace("-", "")
        assert path.name == f"fetch_perf_{day}.jsonl"
        payload = json.loads(path.read_text(encoding="utf-8").strip())
        assert payload["task_id"] == "kline_daily_incremental"
        assert payload["status"] == "SUCCESS"
        assert payload["rows"] == 5207
        assert "ts" in payload  # ts 自动补

    def test_appends_multiple_lines(self, tmp_path):
        record_fetch_perf({"task_id": "t1", "status": "SUCCESS"}, base_dir=tmp_path)
        path = record_fetch_perf({"task_id": "t2", "status": "FAILED"}, base_dir=tmp_path)
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["task_id"] == "t1"
        assert json.loads(lines[1])["task_id"] == "t2"

    def test_explicit_ts_preserved(self, tmp_path):
        path = record_fetch_perf({"task_id": "t", "ts": "2026-08-20T01:00:00"}, base_dir=tmp_path)
        payload = json.loads(path.read_text(encoding="utf-8").strip())
        assert payload["ts"] == "2026-08-20T01:00:00"

    def test_chinese_preserved(self, tmp_path):
        path = record_fetch_perf({"task_id": "t", "error": "连接超时（东财反爬）"}, base_dir=tmp_path)
        text = path.read_text(encoding="utf-8")
        assert "连接超时（东财反爬）" in text  # ensure_ascii=False

    def test_non_serializable_fallback_str(self, tmp_path):
        class _Weird:
            def __str__(self):
                return "weird-object"

        path = record_fetch_perf({"task_id": "t", "extra": _Weird()}, base_dir=tmp_path)
        payload = json.loads(path.read_text(encoding="utf-8").strip())
        assert payload["extra"] == "weird-object"

    def test_failure_swallowed_returns_none(self, tmp_path):
        """base_dir 指向已存在的文件→mkdir 失败→返回 None 不抛。"""
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        assert record_fetch_perf({"task_id": "t"}, base_dir=blocker) is None

    def test_creates_nested_dir(self, tmp_path):
        nested = tmp_path / "a" / "b"
        path = record_fetch_perf({"task_id": "t"}, base_dir=nested)
        assert path is not None and path.is_file()
