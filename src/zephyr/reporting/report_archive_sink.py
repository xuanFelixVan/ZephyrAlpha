# [BLUEPRINT] MOD-RPT-037 | docs/03_modules/_domain_reporting/report_archive_sink/blueprint.md | §
# [MODULE] zephyr.reporting.report_archive_sink
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.report_publisher
# [CONSUMERS] zephyr.reporting.report_publisher（注入位）; zephyr.reporting.review_trigger（接线位）; zephyr.frontend.dashboard.api_server（只读投影 /api/reports）
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] append-only JSONL 落盘（一行一 ArchivedReport，禁改写历史行）; 哈希链跨进程连续（重启后 last_record_hash 接续 prev_hash）; 落盘失败不阻断内存归档主链（publisher 侧降级隔离）; 默认落点=仓根 data/reports/report_archive.jsonl（路径可注入，测试走 tmp_path）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReportArchiveSinkError(ZA-RPT-0038)
# [TESTS] tests/reporting/test_report_archive_sink.py
# [A_module] module_id=MOD-RPT-037 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# create-guard-not-dup: D_REPORTING 报告域归档持久化 sink（MOD-RPT-037），消费 ReportPublisher 唯一出口面——与 telemetry 日志 sink/commit 网关校验器/新闻情绪分析等命中件不同域不同对象，命中系翻译册大白话 token 撞词非第二真源

"""
D_REPORTING — Report Archive Sink (报告归档持久化出口，MOD-RPT-037)

F115 R2 归档链薄刀：把 ReportPublisher 的进程内存归档（`self._archive: list`，
头注自认"基础版不含持久化"）补一个**文件持久化出口**——append-only JSONL 落盘
`data/reports/report_archive.jsonl`（54 号 §7 全量落库施工的前置薄刀，DDL 真源
reconciliation_schema.py 不动，跨 data 域协同后续批）。

定位（内收判据自检）：
  - 不是第二归档出口——ReportPublisher 唯一出口面（D-RPT-D05）不变，本模块是
    其**注入式持久化 sink**（构造参数 archive_sink 挂入 publish 路径）；
  - 不做数据库落库（54 号 §7 后续批）；不做读改写（append-only，禁历史行修改）；
  - 投影链（R3 /api/reports）经 load_report_records() 只读本落盘面，跨进程可见。

哈希链跨进程连续：ReportPublisher.publish 在内存链为空时以
last_record_hash() 取盘面尾记录哈希接续 prev_hash——进程重启不再"归档全丢"。

# [ALGO_FLOW] external: docs/03_modules/_domain_reporting/algo_flow/report_archive_sink.yaml
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Final

from zephyr.reporting.report_publisher import ArchivedReport
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

#: 默认归档文件名（落点=仓根 data/reports/，与晨报面同目录不同文件，零路径冲突）
DEFAULT_ARCHIVE_FILENAME: Final = "report_archive.jsonl"


class ReportArchiveSinkError(ZephyrBaseError):
    """报告归档持久化异常——落盘面路径非法等（IO 异常原样上抛不包装）。"""

    error_code = "ZA-RPT-0038"


def _default_archive_path() -> Path:
    """默认落点=仓根 data/reports/report_archive.jsonl（ROOT 随仓走，同 morning_digest 范式）。"""
    return Path(__file__).resolve().parents[3] / "data" / "reports" / DEFAULT_ARCHIVE_FILENAME


def record_to_dict(report: ArchivedReport) -> dict:
    """ArchivedReport → 可 JSON 序列化 dict（archived_at 转 ISO8601 带时区）。"""
    return {
        "archive_id": report.archive_id,
        "report_id": report.report_id,
        "source": report.source.value,
        "report_type": report.report_type,
        "archived_at": report.archived_at.isoformat(),
        "content": report.content,
        "content_hash": report.content_hash,
        "prev_hash": report.prev_hash,
        "record_hash": report.record_hash,
        "schema_version": report.schema_version,
    }


class JsonlArchiveSink:
    """JSONL 追加式归档 sink——ReportPublisher 的持久化注入位（MOD-RPT-037）。

    Usage:
        sink = JsonlArchiveSink()                      # 默认 data/reports/report_archive.jsonl
        pub = ReportPublisher(archive_sink=sink)       # publish 时自动追加落盘
        sink.load_records()                            # 只读投影用（坏行跳过）
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self._path = Path(path) if path is not None else _default_archive_path()
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        """归档文件落点（只读）。"""
        return self._path

    def persist(self, report: ArchivedReport) -> Path:
        """追加一条归档记录（append-only；父目录惰性构造；线程安全）。

        Returns:
            Path: 归档文件落点。

        Raises:
            OSError: 落盘 IO 异常原样上抛——publisher 侧捕获降级，不阻断内存归档。
        """
        line = json.dumps(record_to_dict(report), sort_keys=True, ensure_ascii=False, default=str)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        _logger.debug("archive sink persist: archive_id=%s path=%s", report.archive_id, self._path)
        return self._path

    def last_record_hash(self) -> str:
        """盘面尾记录哈希（跨进程接链用）；空盘/文件缺失返回空串。

        坏行（JSON 解析失败）跳过并留 WARN——尾哈希取最后一条**可解析**记录。
        """
        last = ""
        with self._lock:
            if not self._path.exists():
                return ""
            with self._path.open("r", encoding="utf-8") as fh:
                for raw_line in fh:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        _logger.warning("archive sink 坏行跳过: path=%s", self._path)
                        continue
                    record_hash = record.get("record_hash")
                    if isinstance(record_hash, str) and record_hash:
                        last = record_hash
        return last

    def load_records(self) -> list[dict]:
        """只读加载全部可解析记录（按盘面顺序=归档升序；坏行跳过不抛）。"""
        records: list[dict] = []
        with self._lock:
            if not self._path.exists():
                return records
            with self._path.open("r", encoding="utf-8") as fh:
                for raw_line in fh:
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        _logger.warning("archive sink 坏行跳过: path=%s", self._path)
                        continue
                    if isinstance(record, dict):
                        records.append(record)
        return records


def load_report_records(path: str | Path | None = None) -> list[dict]:
    """模块级只读读面（/api/reports 投影用）——缺文件/坏文件降级为空列表语义见 sink。"""
    return JsonlArchiveSink(path).load_records()


__all__: Final = [
    "DEFAULT_ARCHIVE_FILENAME",
    "JsonlArchiveSink",
    "ReportArchiveSinkError",
    "load_report_records",
    "record_to_dict",
]
