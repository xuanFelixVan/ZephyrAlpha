# [BLUEPRINT] MOD-RPT-003 | docs/03_modules/_domain_reporting/report_publisher/blueprint.md
# [MODULE] zephyr.reporting.report_publisher
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting (各报告模块汇聚至此)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 报告域唯一出口(D-RPT-D05); append-only归档+哈希链; 3分发渠道(ARCHIVE/WEBHOOK/EMAIL); frozen不可变; 线程安全; 纯消费层不发布事件(D-RPT-D01)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPublishInputError(ZA-RPT-0003)
# [TESTS] tests/reporting/test_report_publisher.py
# [A_module] module_id=MOD-RPT-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_REPORTING — Report Publisher (报告发布器)

报告域唯一出口(D-RPT-D05)。所有报告模块的输出汇聚至此, 归档+分发。

基础版功能:
  - 报告汇聚: publish() 接收各模块输出, 归档为 ArchivedReport
  - 报告归档: append-only + 哈希链(复用 POS-009/EX-15/RPT-013 模式)
  - 报告分发: ARCHIVE(仅归档→SENT) / WEBHOOK(微信→PENDING) / EMAIL(邮件→PENDING)
  - 报告查询: 按 archive_id/source/type 查询, get_latest
  - 完整性校验: verify_chain() 校验哈希链

受限功能(基础版不含): LLM摘要/Crypto-Shredding/SQLite+Parquet持久化/Merkle树/
微信Webhook/邮件SMTP实际发送。

属 A 类基础设施(确定性归档 + 接口定义), 纯消费层不发布事件。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.1 D-REPORTING-03, §2.1, §3
蓝图: docs/03_modules/_domain_reporting/report_publisher/blueprint.md
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_SCHEMA_VERSION = "1.0"


class InvalidPublishInputError(ZephyrBaseError):
    """报告发布输入非法——report_id/source/report_type/content 为空或非法。"""

    error_code = "ZA-RPT-0003"


# ── 枚举 ──


class ReportSource(str, Enum):
    """报告来源——各报告模块。"""

    TCA = "tca"
    ATTRIBUTION = "attribution"
    REALTIME_PNL = "realtime_pnl"
    REGULATORY = "regulatory"
    RISK = "risk"
    EXPLAINABILITY = "explainability"
    TRADING_REVIEW = "trading_review"
    PERFORMANCE_AUDIT = "performance_audit"
    VERSION = "version"
    WATERMARK = "watermark"
    TRADE_RECORD = "trade_record"
    EXECUTION_AUDIT = "execution_audit"


class DistributionChannel(str, Enum):
    """分发渠道。"""

    ARCHIVE = "archive"
    WEBHOOK = "webhook"
    EMAIL = "email"


class DistributionStatus(str, Enum):
    """分发状态。"""

    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class ArchivedReport:
    """归档报告——含内容+元数据+哈希链的不可变记录。"""

    archive_id: str
    report_id: str
    source: ReportSource
    report_type: str
    archived_at: datetime
    content: dict
    content_hash: str
    prev_hash: str
    record_hash: str
    schema_version: str = _SCHEMA_VERSION


@dataclass(frozen=True)
class DistributionRecord:
    """分发记录——单次分发操作的不可变记录。"""

    distribution_id: str
    archive_id: str
    channel: DistributionChannel
    status: DistributionStatus
    distributed_at: datetime
    error_message: str = ""
    schema_version: str = _SCHEMA_VERSION


# ── 哈希工具 ──


def _canonical_json(content: dict) -> str:
    """规范 JSON 序列化（sort_keys 确保确定性）。"""
    return json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)


def _compute_content_hash(content: dict) -> str:
    """计算内容指纹——SHA-256(canonical_json(content))。"""
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


def _compute_record_hash(
    archive_id: str,
    archived_at: datetime,
    report_id: str,
    source: str,
    report_type: str,
    content_hash: str,
    prev_hash: str,
) -> str:
    """计算哈希链指纹——SHA-256(链指纹)。"""
    raw = (
        f"{archive_id}|{archived_at.isoformat()}|{report_id}|{source}"
        f"|{report_type}|{content_hash}|{prev_hash}"
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _require(value: object, field_name: str) -> object:
    """提取必填字段, 缺失或空抛异常。"""
    if value is None:
        raise InvalidPublishInputError(
            f"缺少必填字段: {field_name}",
            details={"missing_field": field_name},
        )
    if isinstance(value, str) and not value.strip():
        raise InvalidPublishInputError(
            f"字段 {field_name} 不能为空",
            details={"field": field_name},
        )
    if isinstance(value, (list, dict)) and len(value) == 0:
        raise InvalidPublishInputError(
            f"字段 {field_name} 不能为空列表/字典",
            details={"field": field_name},
        )
    return value


# ── 分发逻辑（基础版）──

# 基础版: ARCHIVE→SENT, WEBHOOK/EMAIL→PENDING
_BASE_DISTRIBUTION_STATUS: dict[DistributionChannel, DistributionStatus] = {
    DistributionChannel.ARCHIVE: DistributionStatus.SENT,
    DistributionChannel.WEBHOOK: DistributionStatus.PENDING,
    DistributionChannel.EMAIL: DistributionStatus.PENDING,
}


def _distribute(
    archive_id: str,
    channel: DistributionChannel,
) -> DistributionRecord:
    """执行分发（基础版）——根据渠道确定状态。"""
    status = _BASE_DISTRIBUTION_STATUS.get(channel, DistributionStatus.PENDING)
    return DistributionRecord(
        distribution_id=f"DIST-{uuid.uuid4().hex[:10]}",
        archive_id=archive_id,
        channel=channel,
        status=status,
        distributed_at=datetime.now(UTC),
        error_message="",
    )


# ── 报告发布器主类 ──


class ReportPublisher:
    """报告发布器——报告域唯一出口。

    汇聚所有报告模块输出, 归档(append-only+哈希链)+分发。
    线程安全（内部加 Lock）。

    Usage:
        pub = ReportPublisher()
        archived = pub.publish(
            report_id="RPT-001",
            source=ReportSource.RISK,
            report_type="daily_risk",
            content={"risk_level": "HIGH"},
            channels=[DistributionChannel.ARCHIVE, DistributionChannel.WEBHOOK],
        )
        assert pub.verify_chain() is True
    """

    def __init__(self) -> None:
        self._archive: list[ArchivedReport] = []
        self._archive_by_id: dict[str, ArchivedReport] = {}
        self._distributions: dict[str, list[DistributionRecord]] = {}
        self._lock = threading.Lock()

    # ── 发布（归档 + 分发）──

    def publish(
        self,
        report_id: str,
        source: ReportSource,
        report_type: str,
        content: dict,
        channels: list[DistributionChannel] | None = None,
    ) -> ArchivedReport:
        """发布报告——归档 + 分发。

        Args:
            report_id: 报告逻辑标识（来自源模块）。
            source: 报告来源（ReportSource 枚举）。
            report_type: 报告类型（如 "daily_risk"/"programmatic_trading"）。
            content: 报告内容（JSON 可序列化 dict）。
            channels: 分发渠道列表, 默认 [ARCHIVE]。

        Returns:
            ArchivedReport: 归档后的报告（含哈希链）。
        """
        _require(report_id, "report_id")
        _require(source, "source")
        _require(report_type, "report_type")
        _require(content, "content")
        if not isinstance(content, dict):
            raise InvalidPublishInputError(
                f"content 必须为 dict, 实际类型: {type(content).__name__}",
                details={"field": "content", "type": type(content).__name__},
            )

        if channels is None:
            channels = [DistributionChannel.ARCHIVE]

        with self._lock:
            archive_id = f"ARCH-{uuid.uuid4().hex[:10]}"
            archived_at = datetime.now(UTC)
            content_hash = _compute_content_hash(content)
            prev_hash = self._archive[-1].record_hash if self._archive else ""

            record_hash = _compute_record_hash(
                archive_id, archived_at, report_id, source.value,
                report_type, content_hash, prev_hash,
            )

            archived = ArchivedReport(
                archive_id=archive_id,
                report_id=report_id,
                source=source,
                report_type=report_type,
                archived_at=archived_at,
                content=dict(content),
                content_hash=content_hash,
                prev_hash=prev_hash,
                record_hash=record_hash,
                schema_version=_SCHEMA_VERSION,
            )

            self._archive.append(archived)
            self._archive_by_id[archive_id] = archived

            # 执行分发
            dist_records = [_distribute(archive_id, ch) for ch in channels]
            self._distributions[archive_id] = dist_records

        _logger.debug(
            "publish: report_id=%s source=%s type=%s archive_id=%s channels=%d",
            report_id, source.value, report_type, archive_id, len(channels),
        )
        return archived

    # ── 查询 ──

    def get_report(self, archive_id: str) -> ArchivedReport | None:
        """按 archive_id 查询归档报告。"""
        with self._lock:
            return self._archive_by_id.get(archive_id)

    def list_by_source(self, source: ReportSource) -> list[ArchivedReport]:
        """按来源模块查询归档报告（按归档时间升序）。"""
        with self._lock:
            return [r for r in self._archive if r.source == source]

    def list_by_type(self, report_type: str) -> list[ArchivedReport]:
        """按报告类型查询归档报告（按归档时间升序）。"""
        with self._lock:
            return [r for r in self._archive if r.report_type == report_type]

    def get_latest(self, source: ReportSource) -> ArchivedReport | None:
        """获取指定来源的最新归档报告。"""
        with self._lock:
            for r in reversed(self._archive):
                if r.source == source:
                    return r
            return None

    def list_distributions(self, archive_id: str) -> list[DistributionRecord]:
        """查询某归档报告的分发记录。"""
        with self._lock:
            return list(self._distributions.get(archive_id, []))

    # ── 完整性校验 ──

    def verify_chain(self) -> bool:
        """校验哈希链完整性——遍历归档, 重算哈希, 比对 prev_hash 链接。

        Returns:
            bool: True=链完整(无篡改), False=链断裂或内容被篡改。
        """
        with self._lock:
            prev_hash = ""
            for r in self._archive:
                # 1. 校验 content_hash
                actual_content_hash = _compute_content_hash(r.content)
                if actual_content_hash != r.content_hash:
                    _logger.warning(
                        "verify_chain FAIL: archive_id=%s content_hash 不匹配",
                        r.archive_id,
                    )
                    return False
                # 2. 校验 prev_hash 链接
                if r.prev_hash != prev_hash:
                    _logger.warning(
                        "verify_chain FAIL: archive_id=%s prev_hash 链接断裂",
                        r.archive_id,
                    )
                    return False
                # 3. 校验 record_hash
                actual_record_hash = _compute_record_hash(
                    r.archive_id, r.archived_at, r.report_id, r.source.value,
                    r.report_type, r.content_hash, r.prev_hash,
                )
                if actual_record_hash != r.record_hash:
                    _logger.warning(
                        "verify_chain FAIL: archive_id=%s record_hash 不匹配",
                        r.archive_id,
                    )
                    return False
                prev_hash = r.record_hash
        return True

    # ── 统计 ──

    @property
    def archive_count(self) -> int:
        """已归档报告总数。"""
        with self._lock:
            return len(self._archive)


__all__ = [
    "ArchivedReport",
    "DistributionChannel",
    "DistributionRecord",
    "DistributionStatus",
    "InvalidPublishInputError",
    "ReportPublisher",
    "ReportSource",
]
