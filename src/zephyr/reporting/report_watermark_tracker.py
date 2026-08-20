# [BLUEPRINT] MOD-RPT-017 | docs/03_modules/_domain_reporting/report_watermark_tracker/blueprint.md
# [MODULE] zephyr.reporting.report_watermark_tracker
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ReportWatermark frozen不可变; 哈希链prev_watermark_hash(w_n)=record_hash(w_{n-1}); content须dict; watermark_signature=SHA-256(source+content_hash+timestamp); append-only禁止修改删除
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidWatermarkInputError(ZA-RPT-0004)
# [TESTS] tests/reporting/test_report_watermark_tracker.py
# [A_module] module_id=MOD-RPT-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_REPORTING — Report Watermark Tracker (报告水印追踪器)

为每份报告加盖不可篡改水印, 提供来源追溯+完整性校验+哈希链审计。
复用 POS-009/EX-15/RPT-013 的哈希链模式。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.3 D-REPORTING-17
蓝图: docs/03_modules/_domain_reporting/report_watermark_tracker/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 水印加盖请求
#   fields: report_id 报告标识 + content JSON可序列化dict + source 生成源模块名
#   code: stamp() 参数（report_id/content/source）
# 层: 算法
# - id: A1
#   name_zh: ① 水印加盖与哈希链（append-only）
#   name_en: WatermarkTracker.stamp/_compute_content_hash/_compute_signature/_compute_record_hash
#   intro: 为报告内容算内容指纹和水印签名，并链接上一条水印哈希形成防篡改链
#   desc: content_hash=SHA-256(canonical_json(content))；watermark_signature=SHA-256(source|content_hash|timestamp)；record_hash=SHA-256(watermark_id|report_id|source|timestamp|content_hash|signature|prev_watermark_hash)；prev_watermark_hash(w_n)=record_hash(w_{n-1})；Lock 线程安全
#   inputs: I1
#   outputs: ReportWatermark 不可变水印记录
#   invariant: watermark_signature=SHA-256(source+content_hash+timestamp)；append-only禁止修改删除
# - id: A2
#   name_zh: ② 水印完整性校验
#   name_en: WatermarkTracker.verify_watermark
#   intro: 重算内容哈希和水印签名，检测报告内容被篡改或水印被伪造
#   desc: 重算 content_hash 与记录比对（内容篡改检测）；重算 signature 与记录比对（水印伪造检测）；任一不符返回 False
#   inputs: A1
#   outputs: 水印校验 bool
# - id: A3
#   name_zh: ③ 水印哈希链审计
#   name_en: WatermarkTracker.verify_chain
#   intro: 遍历报告全部水印，验证链链接、签名与记录指纹均未被破坏
#   desc: 逐条校验 prev_watermark_hash 链接、signature 重算、record_hash 重算；任一不符返回 False；无水印返回 True
#   inputs: A1
#   outputs: 链完整性 bool
#   invariant: 哈希链prev_watermark_hash(w_n)=record_hash(w_{n-1})
# 层: 输出
# - id: O1
#   name_zh: 报告水印记录（含哈希链）
#   name_en: ReportWatermark
#   intro: 加盖在报告上的不可篡改水印，支持来源追溯（list_sources）与完整性校验
#   invariant: ReportWatermark frozen不可变
#   downstream: zephyr.reporting（报告域内部消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import Lock

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidWatermarkInputError(ZephyrBaseError):
    """水印输入非法——content 非 dict / source 为空。"""

    error_code = "ZA-RPT-0004"


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class ReportWatermark:
    """报告水印——含水印+哈希链的不可变记录。

    哈希链算法:
      content_hash        = SHA-256(canonical_json(content))
      watermark_signature = SHA-256(source + content_hash + timestamp)
      record_hash         = SHA-256(watermark_id + report_id + source +
                                    timestamp + content_hash +
                                    watermark_signature + prev_watermark_hash)
      prev_watermark_hash(w_n) = record_hash(w_{n-1}), 首个为 ""
    """

    watermark_id: str
    report_id: str
    source: str
    timestamp: datetime
    content_hash: str
    watermark_signature: str
    prev_watermark_hash: str
    record_hash: str
    schema_version: str = "1.0"


# ── 哈希工具 ──


def _canonical_json(content: dict) -> str:
    """规范 JSON 序列化（sort_keys 确保确定性）。"""
    return json.dumps(content, sort_keys=True, ensure_ascii=False, default=str)


def _sha256(data: str) -> str:
    """SHA-256 哈希。"""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_content_hash(content: dict) -> str:
    """计算内容指纹。"""
    return _sha256(_canonical_json(content))


def _compute_signature(source: str, content_hash: str, timestamp: datetime) -> str:
    """计算水印签名——绑定来源+内容+时间。"""
    return _sha256(f"{source}|{content_hash}|{timestamp.isoformat()}")


def _compute_record_hash(
    watermark_id: str,
    report_id: str,
    source: str,
    timestamp: datetime,
    content_hash: str,
    signature: str,
    prev_hash: str,
) -> str:
    """计算链指纹——链接前水印形成哈希链。"""
    raw = f"{watermark_id}|{report_id}|{source}|{timestamp.isoformat()}|{content_hash}|{signature}|{prev_hash}"
    return _sha256(raw)


# ── 水印追踪器主类 ──


class WatermarkTracker:
    """报告水印追踪器——水印加盖+完整性校验+哈希链审计。

    纯基础设施, 线程安全。Append-only: 已加盖水印禁止修改/删除。

    Usage:
        tracker = WatermarkTracker()
        wm = tracker.stamp("daily_pnl", {"total": 100}, "PnlCalculator")
        assert tracker.verify_watermark(wm, {"total": 100}) is True
        assert tracker.verify_chain("daily_pnl") is True
    """

    def __init__(self) -> None:
        # report_id → list[ReportWatermark]（按时间升序）
        self._store: dict[str, list[ReportWatermark]] = {}
        self._lock = Lock()

    # ── 水印加盖 ──

    def stamp(self, report_id: str, content: dict, source: str) -> ReportWatermark:
        """为报告加盖水印——append-only, 自动哈希链链接。

        Args:
            report_id: 报告标识。
            content: 报告内容, 必须为 JSON 可序列化 dict。
            source: 生成源模块名（如 "RiskReportEngine"）。

        Returns:
            ReportWatermark: 含水印+哈希链的不可变记录。

        Raises:
            InvalidWatermarkInputError: content 非 dict 或 source 为空。
        """
        if not isinstance(content, dict):
            raise InvalidWatermarkInputError(
                f"content 必须为 dict, 实际类型={type(content).__name__}",
                details={"report_id": report_id, "content_type": type(content).__name__},
            )
        if not source or not source.strip():
            raise InvalidWatermarkInputError(
                "source 不能为空",
                details={"report_id": report_id},
            )

        with self._lock:
            watermarks = self._store.setdefault(report_id, [])
            prev_hash = watermarks[-1].record_hash if watermarks else ""
            timestamp = datetime.now(UTC)
            watermark_id = str(uuid.uuid4())
            content_hash = _compute_content_hash(content)
            signature = _compute_signature(source, content_hash, timestamp)
            record_hash = _compute_record_hash(
                watermark_id,
                report_id,
                source,
                timestamp,
                content_hash,
                signature,
                prev_hash,
            )

            wm = ReportWatermark(
                watermark_id=watermark_id,
                report_id=report_id,
                source=source.strip(),
                timestamp=timestamp,
                content_hash=content_hash,
                watermark_signature=signature,
                prev_watermark_hash=prev_hash,
                record_hash=record_hash,
            )
            watermarks.append(wm)

            _logger.debug(
                "stamp: report_id=%s source=%s content_hash=%s record_hash=%s",
                report_id,
                wm.source,
                content_hash[:8],
                record_hash[:8],
            )
            return wm

    # ── 水印查询 ──

    def get_watermark(self, report_id: str) -> ReportWatermark | None:
        """获取报告最新水印（无水印返回 None）。"""
        with self._lock:
            watermarks = self._store.get(report_id, [])
            return watermarks[-1] if watermarks else None

    def list_watermarks(self, report_id: str) -> list[ReportWatermark]:
        """列出报告所有水印（按时间升序, 返回副本）。"""
        with self._lock:
            return list(self._store.get(report_id, []))

    def list_sources(self) -> list[str]:
        """列出所有去重的生成源模块。"""
        with self._lock:
            sources: set[str] = set()
            for wms in self._store.values():
                for wm in wms:
                    sources.add(wm.source)
            return sorted(sources)

    # ── 完整性校验 ──

    def verify_watermark(self, watermark: ReportWatermark, content: dict) -> bool:
        """校验水印与内容是否匹配——检测内容篡改。

        Args:
            watermark: 待校验水印。
            content: 当前报告内容。

        Returns:
            bool: True=内容未篡改, False=内容被篡改。
        """
        actual_hash = _compute_content_hash(content)
        if actual_hash != watermark.content_hash:
            _logger.warning(
                "verify_watermark FAIL: report_id=%s content_hash 不匹配（内容被篡改）",
                watermark.report_id,
            )
            return False
        # 校验签名一致性
        expected_sig = _compute_signature(watermark.source, watermark.content_hash, watermark.timestamp)
        if expected_sig != watermark.watermark_signature:
            _logger.warning(
                "verify_watermark FAIL: report_id=%s signature 不匹配（水印被伪造）",
                watermark.report_id,
            )
            return False
        return True

    # ── 哈希链验证 ──

    def verify_chain(self, report_id: str) -> bool:
        """验证报告水印哈希链完整性。

        遍历所有水印, 重算 content_hash/signature/record_hash, 比对链链接。
        任何篡改（删除/伪造/顺序乱）→ 返回 False。

        Returns:
            bool: True=完整, False=被篡改。无水印时返回 True。
        """
        with self._lock:
            watermarks = self._store.get(report_id, [])
            if not watermarks:
                return True

            expected_prev = ""
            for i, wm in enumerate(watermarks):
                # prev_watermark_hash 链接
                if wm.prev_watermark_hash != expected_prev:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s wm#%d prev_hash 不匹配",
                        report_id,
                        i,
                    )
                    return False
                # signature 重算
                expected_sig = _compute_signature(wm.source, wm.content_hash, wm.timestamp)
                if wm.watermark_signature != expected_sig:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s wm#%d signature 不匹配",
                        report_id,
                        i,
                    )
                    return False
                # record_hash 重算
                expected_record = _compute_record_hash(
                    wm.watermark_id,
                    wm.report_id,
                    wm.source,
                    wm.timestamp,
                    wm.content_hash,
                    wm.watermark_signature,
                    wm.prev_watermark_hash,
                )
                if wm.record_hash != expected_record:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s wm#%d record_hash 不匹配",
                        report_id,
                        i,
                    )
                    return False
                expected_prev = wm.record_hash

            return True


__all__ = [
    "InvalidWatermarkInputError",
    "ReportWatermark",
    "WatermarkTracker",
]
