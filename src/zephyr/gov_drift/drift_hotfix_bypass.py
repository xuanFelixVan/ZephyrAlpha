# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.drift_hotfix_bypass
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] src/zephyr/gov_drift/_drift.py ; src/zephyr/gov_enforcement/rule_enforcement/drift_detector.py (+3 more)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 旁路必须72h自动过期
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Hotfix Bypass — drift_hotfix_bypass.py


P0 Hotfix 快速旁路处理：[HOTFIX]/[EMERGENCY] commit 自动标记为 ACKNOWLEDGED + SUPPRESSED(72h)。


对标 blueprint.md §2.12（热修复/紧急变更旁路）。


同时写入核心 zephyr.gov_audit.writer.AuditWriter 不可变审计链。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: drift_hotfix_bypass.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HotfixBypass
#   name_en: HotfixBypass
#   intro: class HotfixBypass 源码 L99-L260
#   desc: 公共方法（定义序）: audit_dir, audit_log_path, core_writer, project_root, is_hotfix_commit, process_hotfix, check_expi…
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: HotfixBypass
#   downstream: src/zephyr/gov_drift/_drift.py ; src/zephyr/gov_enforcement/rule_enforcement/dr…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

logger = logging.getLogger(__name__)

import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

# 5.138.2 治本：zephyr.shared.contracts.protocols 仅依赖 typing+pydantic，
# shared 层不可能反向 import gov_drift，与本模块无真实循环链——
# 移除 try/except ImportError 静默降级，import 失败显式化。
from zephyr.shared.contracts.protocols import AuditWriterProtocol

HOTFIX_PREFIXES: Final[tuple[str, ...]] = ("[HOTFIX]", "[EMERGENCY]", "[HOTFIX]", "[EMERGENCY]")


SUPPRESSION_TTL_HOURS: Final[int] = 72


@dataclass
class HotfixAuditEntry:
    entry_id: uuid.UUID

    commit_hash: str

    module_ids: list[str]

    dimensions: list[str]

    owner_ack: str = ""

    timestamp: datetime | None = None

    suppressed_until: datetime | None = None


class HotfixBypass:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._audit_dir = os.path.join(project_root, "data", "drift_audit")

        os.makedirs(self._audit_dir, exist_ok=True)

        self._audit_log_path = os.path.join(self._audit_dir, "hotfix_audit.jsonl")

        self._active_hotfixes: dict[str, HotfixAuditEntry] = {}

        self._core_writer: AuditWriterProtocol | None = None

        try:
            import importlib as _importlib

            _CoreAuditWriter = _importlib.import_module("zephyr.gov_audit.writer").AuditWriter
            self._core_writer = _CoreAuditWriter()

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("suppressed error in drift_hotfix_bypass", exc_info=True)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def audit_dir(self):
        """只读：audit_dir（Stage 4 公共化）。"""
        return self._audit_dir

    @audit_dir.setter
    def audit_dir(self, value):
        """写入：audit_dir（Stage 4 公共化）。"""
        self._audit_dir = value

    @property
    def audit_log_path(self):
        """只读：audit_log_path（Stage 4 公共化）。"""
        return self._audit_log_path

    @audit_log_path.setter
    def audit_log_path(self, value):
        """写入：audit_log_path（Stage 4 公共化）。"""
        self._audit_log_path = value

    @property
    def core_writer(self) -> AuditWriterProtocol | None:
        """只读：core_writer（Stage 4 公共化）。"""
        return self._core_writer

    @core_writer.setter
    def core_writer(self, value):
        """写入：core_writer（Stage 4 公共化）。"""
        self._core_writer = value

    @property
    def project_root(self):
        """只读：project_root（Stage 4 公共化）。"""
        return self._project_root

    @project_root.setter
    def project_root(self, value):
        """写入：project_root（Stage 4 公共化）。"""
        self._project_root = value

    def is_hotfix_commit(self, commit_message: str) -> bool:
        upper = commit_message.strip().upper()

        for prefix in HOTFIX_PREFIXES:
            if upper.startswith(prefix):
                return True

        return False

    def process_hotfix(
        self,
        commit_hash: str,
        commit_message: str,
        module_ids: list[str],
        affected_dimensions: list[str],
        owner_ack: str = "",
    ) -> HotfixAuditEntry:
        now = datetime.now(UTC)

        entry = HotfixAuditEntry(
            entry_id=uuid.uuid4(),
            commit_hash=commit_hash,
            module_ids=module_ids,
            dimensions=affected_dimensions,
            owner_ack=owner_ack,
            timestamp=now,
            suppressed_until=now + timedelta(hours=SUPPRESSION_TTL_HOURS),
        )

        self._active_hotfixes[commit_hash] = entry

        self._write_audit_log(entry)

        return entry

    def check_expired_hotfixes(self) -> list[str]:
        now = datetime.now(UTC)

        expired: list[str] = []

        for ch, entry in list(self._active_hotfixes.items()):
            if entry.suppressed_until and now >= entry.suppressed_until:
                expired.append(ch)

                del self._active_hotfixes[ch]

        return expired

    def is_suppressed(self, commit_hash: str) -> bool:
        entry = self._active_hotfixes.get(commit_hash)

        if entry is None:
            return False

        if entry.suppressed_until and datetime.now(UTC) < entry.suppressed_until:
            return True

        return False

    def _write_audit_log(self, entry: HotfixAuditEntry) -> None:
        record = {
            "entry_id": str(entry.entry_id),
            "commit_hash": entry.commit_hash,
            "module_ids": entry.module_ids,
            "dimensions": entry.dimensions,
            "owner_ack": entry.owner_ack,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else "",
            "suppressed_until": entry.suppressed_until.isoformat() if entry.suppressed_until else "",
        }

        if self._core_writer is not None:
            try:
                core_event = dict(record)

                core_event["event_type"] = "drift_hotfix_bypass"

                core_event["agent_id"] = entry.owner_ack or "hotfix_bypass"

                core_event["session_id"] = str(entry.entry_id)

                core_event["target_path"] = entry.commit_hash

                core_event["status"] = "suppressed"

                self._core_writer.write(core_event)

                return

            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in drift_hotfix_bypass", exc_info=True)

        with open(self._audit_log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

            fh.flush()
