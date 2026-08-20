# [BLUEPRINT] MOD-RPT-013 | docs/03_modules/_domain_reporting/report_version_manager/blueprint.md
# [MODULE] zephyr.reporting.report_version_manager
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] ReportVersion/VersionDiff frozen不可变; 版本号per report_id单调递增; 哈希链prev_hash(v_n)=record_hash(v_{n-1}); append-only禁止修改删除; content须JSON可序列化dict
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidVersionInputError(ZA-RPT-0002)
# [TESTS] tests/reporting/test_report_version_manager.py
# [A_module] module_id=MOD-RPT-013 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

D_REPORTING — Report Version Manager (报告版本管理器)

报告域版本化基座。为所有报告提供: 版本存储(append-only) + 差异引擎(版本间 diff)
+ 快照管理(create/get/list) + 哈希链审计(Tamper-Evident, 篡改可检测)。

复用 POS-009/EX-15 的哈希链模式, 满足 §4 审计约束(交易日志≥7年/不可篡改)。

设计真源: D:/临时工作区/依赖图/10-D-REPORTING-报告域.md §1.3 D-REPORTING-13, §4.3
蓝图: docs/03_modules/_domain_reporting/report_version_manager/blueprint.md

核心职责（阶段1）:
  - 版本存储: append-only, per report_id 版本号单调递增
  - 哈希链: content_hash + record_hash + prev_hash, 篡改可检测
  - 差异引擎: 版本间键级 diff (add/del/mod)
  - 快照管理: store/get_version/get_latest/list_versions/list_reports
  - 审计链验证: verify_chain 重算哈希链比对

阶段2扩展（本次不实现, 见蓝图 §4）:
  - SQLite 持久化 / Merkle 树批量完整性证明 / OpenLineage 血缘

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 报告内容存储请求
#   fields: report_id 逻辑报告标识 + content JSON可序列化dict
#   code: store() 参数（report_id/content）
# - id: I2
#   name: 版本差异请求
#   fields: report_id + from_version + to_version 版本号
#   code: diff() 参数
# 层: 算法
# - id: A1
#   name_zh: ① 版本存储与哈希链（append-only）
#   name_en: ReportVersionManager.store/_compute_content_hash/_compute_record_hash
#   intro: 内容算 SHA-256 指纹、版本号自动递增并链接前版哈希，append-only 落存
#   desc: version_number=len(versions)+1；content_hash=SHA-256(canonical_json(content))；record_hash=SHA-256(version_id|timestamp|report_id|version_number|content_hash|prev_hash)；prev_hash(v_n)=record_hash(v_{n-1})；Lock 线程安全
#   inputs: I1
#   outputs: ReportVersion 不可变版本记录
#   invariant: 版本号per report_id单调递增；哈希链prev_hash(v_n)=record_hash(v_{n-1})；append-only禁止修改删除
# - id: A2
#   name_zh: ② 快照管理
#   name_en: get_version/get_latest/list_versions/list_reports
#   intro: 按版本号取版本、取最新版、列全部版本和全部 report_id
#   desc: 内存 _store: report_id→list[ReportVersion]（按版本号升序），查询返回副本
#   inputs: A1
#   outputs: 版本查询结果
# - id: A3
#   name_zh: ③ 差异引擎（键级 diff）
#   name_en: ReportVersionManager.diff
#   intro: 对比两版本内容字典，按键给出新增/删除/修改三类差异
#   desc: 遍历 old∪new 键：仅新有→additions，仅旧有→deletions，值不等→modifications(key→(old,new))；版本不存在抛 ZA-RPT-0002
#   inputs: I2 A2
#   outputs: VersionDiff（additions/deletions/modifications）
# - id: A4
#   name_zh: ④ 审计链验证
#   name_en: ReportVersionManager.verify_chain
#   intro: 遍历全部版本重算哈希，验证版本号连续、prev_hash 链接、内容与记录指纹未篡改
#   desc: 逐项校验 version_number==i+1、prev_hash 链接、content_hash 重算、record_hash 重算；任一不符返回 False；空链视为完整
#   inputs: A1
#   outputs: 链完整性 bool
# 层: 输出
# - id: O1
#   name_zh: 报告版本记录（含哈希链）
#   name_en: ReportVersion
#   intro: 报告域版本化基座产出的不可变版本记录，满足交易日志≥7年不可篡改审计约束
#   invariant: ReportVersion frozen不可变
#   downstream: zephyr.reporting（各报告模块版本化基座）
# - id: O2
#   name_zh: 版本差异
#   name_en: VersionDiff
#   intro: 两版本间键级差异（新增/删除/修改），供报告变更审计与对比
#   downstream: zephyr.reporting（报告域内部消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A3
# A1 --> A2
# A2 --> A3
# A2 --> A4
# A1 --> A4
# A1 --> O1
# A3 --> O2
# A4 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidVersionInputError(ZephyrBaseError):
    """版本管理输入非法——content 非 dict / 版本号不存在 / diff 版本非法。"""

    error_code = "ZA-RPT-0002"


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class ReportVersion:
    """报告版本——含哈希链的不可变版本记录。

    哈希链算法（复用 POS-009/EX-15）:
      content_hash = SHA-256(canonical_json(content))
      record_hash  = SHA-256(version_id + timestamp + report_id
                              + version_number + content_hash + prev_hash)
      prev_hash(v_n) = record_hash(v_{n-1}), 首版本 prev_hash=""
    """

    version_id: str
    report_id: str
    version_number: int
    timestamp: datetime
    content: dict
    content_hash: str
    prev_hash: str
    record_hash: str
    schema_version: str = "1.0"


@dataclass(frozen=True)
class VersionDiff:
    """版本差异——两个版本间的键级 diff。不可变。"""

    from_version: int
    to_version: int
    additions: dict = field(default_factory=dict)  # key → new_value
    deletions: dict = field(default_factory=dict)  # key → old_value
    modifications: dict = field(default_factory=dict)  # key → (old_value, new_value)

    @property
    def has_changes(self) -> bool:
        """是否存在差异。"""
        return bool(self.additions or self.deletions or self.modifications)


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


def _compute_record_hash(
    version_id: str,
    timestamp: datetime,
    report_id: str,
    version_number: int,
    content_hash: str,
    prev_hash: str,
) -> str:
    """计算链指纹——链接前版本形成哈希链。"""
    raw = f"{version_id}|{timestamp.isoformat()}|{report_id}|{version_number}|{content_hash}|{prev_hash}"
    return _sha256(raw)


# ── 版本管理器主类 ──


class ReportVersionManager:
    """报告版本管理器——版本存储+差异引擎+快照管理+哈希链审计。

    纯基础设施, 无外部依赖（仅标准库 + errors）。线程安全。
    Append-only: 已存储版本禁止修改/删除。

    Usage:
        mgr = ReportVersionManager()

        v1 = mgr.store("daily_pnl", {"total": 100, "fee": 5})
        v2 = mgr.store("daily_pnl", {"total": 120, "fee": 5, "tax": 1})

        # 差异
        d = mgr.diff("daily_pnl", 1, 2)
        print(d.additions, d.modifications)  # {"tax":1} / {"total":(100,120)}

        # 完整性校验
        assert mgr.verify_chain("daily_pnl") is True
    """

    def __init__(self) -> None:
        # report_id → list[ReportVersion]（按版本号升序）
        self._store: dict[str, list[ReportVersion]] = {}
        self._lock = Lock()

    # ── 版本存储 ──

    def store(self, report_id: str, content: dict) -> ReportVersion:
        """存储报告新版本——append-only, 自动版本号递增, 哈希链链接。

        Args:
            report_id: 逻辑报告标识（如 "daily_pnl_20260802"）。
            content: 报告内容, 必须为 JSON 可序列化 dict。

        Returns:
            ReportVersion: 含哈希链的不可变版本记录。

        Raises:
            InvalidVersionInputError: content 非 dict。
        """
        if not isinstance(content, dict):
            raise InvalidVersionInputError(
                f"content 必须为 dict, 实际类型={type(content).__name__}",
                details={"report_id": report_id, "content_type": type(content).__name__},
            )

        with self._lock:
            versions = self._store.setdefault(report_id, [])
            version_number = len(versions) + 1
            prev_hash = versions[-1].record_hash if versions else ""
            timestamp = datetime.now(UTC)
            version_id = str(uuid.uuid4())
            content_hash = _compute_content_hash(content)
            record_hash = _compute_record_hash(
                version_id, timestamp, report_id, version_number, content_hash, prev_hash
            )

            version = ReportVersion(
                version_id=version_id,
                report_id=report_id,
                version_number=version_number,
                timestamp=timestamp,
                content=dict(content),  # 防御性拷贝
                content_hash=content_hash,
                prev_hash=prev_hash,
                record_hash=record_hash,
            )
            versions.append(version)

            _logger.debug(
                "store: report_id=%s version=%d content_hash=%s record_hash=%s",
                report_id,
                version_number,
                content_hash[:8],
                record_hash[:8],
            )
            return version

    # ── 快照管理 ──

    def get_version(self, report_id: str, version_number: int) -> ReportVersion | None:
        """获取指定版本（不存在返回 None）。"""
        with self._lock:
            versions = self._store.get(report_id, [])
            for v in versions:
                if v.version_number == version_number:
                    return v
            return None

    def get_latest(self, report_id: str) -> ReportVersion | None:
        """获取最新版本（无版本返回 None）。"""
        with self._lock:
            versions = self._store.get(report_id, [])
            return versions[-1] if versions else None

    def list_versions(self, report_id: str) -> list[ReportVersion]:
        """列出报告所有版本（按版本号升序, 返回副本）。"""
        with self._lock:
            return list(self._store.get(report_id, []))

    def list_reports(self) -> list[str]:
        """列出所有 report_id。"""
        with self._lock:
            return list(self._store.keys())

    # ── 差异引擎 ──

    def diff(self, report_id: str, from_version: int, to_version: int) -> VersionDiff:
        """计算两个版本的差异（键级 diff）。

        Args:
            report_id: 报告标识。
            from_version: 起始版本号。
            to_version: 目标版本号。

        Returns:
            VersionDiff: 含 additions/deletions/modifications。

        Raises:
            InvalidVersionInputError: 版本不存在。
        """
        v_from = self.get_version(report_id, from_version)
        v_to = self.get_version(report_id, to_version)
        if v_from is None:
            raise InvalidVersionInputError(
                f"版本不存在: report_id={report_id} version={from_version}",
                details={"report_id": report_id, "version": from_version},
            )
        if v_to is None:
            raise InvalidVersionInputError(
                f"版本不存在: report_id={report_id} version={to_version}",
                details={"report_id": report_id, "version": to_version},
            )

        old = v_from.content
        new = v_to.content
        additions: dict[str, Any] = {}
        deletions: dict[str, Any] = {}
        modifications: dict[str, Any] = {}

        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            in_old = key in old
            in_new = key in new
            if in_old and not in_new:
                deletions[key] = old[key]
            elif in_new and not in_old:
                additions[key] = new[key]
            elif old[key] != new[key]:
                modifications[key] = (old[key], new[key])

        return VersionDiff(
            from_version=from_version,
            to_version=to_version,
            additions=additions,
            deletions=deletions,
            modifications=modifications,
        )

    # ── 审计链验证 ──

    def verify_chain(self, report_id: str) -> bool:
        """验证报告版本哈希链完整性。

        遍历所有版本, 重算 content_hash/record_hash, 比对 prev_hash 链接。
        任何篡改（content 变/版本顺序乱/record_hash 伪造）→ 返回 False。

        Returns:
            bool: True=完整, False=被篡改或损坏。无版本时返回 True（空链视为完整）。
        """
        with self._lock:
            versions = self._store.get(report_id, [])
            if not versions:
                return True

            expected_prev = ""
            for i, v in enumerate(versions):
                # 版本号连续性
                if v.version_number != i + 1:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s 版本号不连续 expected=%d actual=%d",
                        report_id,
                        i + 1,
                        v.version_number,
                    )
                    return False
                # prev_hash 链接
                if v.prev_hash != expected_prev:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s v%d prev_hash 不匹配",
                        report_id,
                        v.version_number,
                    )
                    return False
                # content_hash 重算
                if _compute_content_hash(v.content) != v.content_hash:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s v%d content_hash 不匹配（内容被篡改）",
                        report_id,
                        v.version_number,
                    )
                    return False
                # record_hash 重算
                expected_record = _compute_record_hash(
                    v.version_id,
                    v.timestamp,
                    v.report_id,
                    v.version_number,
                    v.content_hash,
                    v.prev_hash,
                )
                if v.record_hash != expected_record:
                    _logger.warning(
                        "verify_chain FAIL: report_id=%s v%d record_hash 不匹配",
                        report_id,
                        v.version_number,
                    )
                    return False
                expected_prev = v.record_hash

            return True


__all__ = [
    "InvalidVersionInputError",
    "ReportVersion",
    "ReportVersionManager",
    "VersionDiff",
]
