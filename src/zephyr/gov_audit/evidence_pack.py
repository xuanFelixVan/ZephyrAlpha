# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.evidence_pack
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.models
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""




audit-trail.evidence_pack — MOD-INF-020 · 证据包导出器
=======================================================
蓝图 D-020-24 · 审计证据导出 (JSON / PDF / FCA 格式)

格式
----
  JSON — 结构化 JSON 证据包
  FCA  — FCA (Financial Conduct Authority) 合规格式
  PDF  — PDF 证据报告 (需 reportlab)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: data_dir 参数
#   fields: 参数 data_dir（无注解）
#   code: evidence_pack.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: output_dir 参数
#   fields: 参数 output_dir（无注解）
#   code: evidence_pack.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EvidencePackExporter
#   name_en: EvidencePackExporter
#   intro: class EvidencePackExporter 源码 L109-L244
#   desc: 公共方法（定义序）: data_dir, output_dir, export_json, export_fca；源码 L109-L244
#   inputs: data_dir output_dir
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: EvidencePackExporter
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.governance.evidence_pack import EvidencePack  # re-export: audit_trail 模块依赖 EvidencePack
from zephyr.shared.io.paths import AUDIT_DATA_DIR  # 路径真源（SSoT）
from zephyr.shared.io.serialization import dumps

_logger = logging.getLogger(__name__)

# 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 AUDIT_DATA_DIR 真源。
DEFAULT_AUDIT_DATA_DIR: Path = AUDIT_DATA_DIR


class EvidencePackMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pack_id: str = ""
    created_at: str = ""
    format: str = ""
    entry_count: int = 0
    date_range_start: str = ""
    date_range_end: str = ""
    filters: dict[str, Any] = Field(default_factory=dict)
    checksum: str = ""


class ExportResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    output_path: str = ""
    format: str = ""
    entry_count: int = 0
    file_size_bytes: int = 0
    checksum: str = ""
    exported_at: str = ""


class EvidencePackExporter:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        output_dir: Path | str | None = None,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._output_dir = Path(output_dir) if output_dir else self._data_dir / "evidence_packs"
        self._output_dir.mkdir(parents=True, exist_ok=True)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def data_dir(self):
        """只读：data_dir（Stage 4 公共化）。"""
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value):
        """写入：data_dir（Stage 4 公共化）。"""
        self._data_dir = value

    @property
    def output_dir(self):
        """只读：output_dir（Stage 4 公共化）。"""
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        """写入：output_dir（Stage 4 公共化）。"""
        self._output_dir = value

    def export_json(
        self,
        events: list[dict[str, Any]],
        pack_id: str = "",
        filters: dict[str, Any] | None = None,
    ) -> ExportResult:
        import hashlib

        if not pack_id:
            pack_id = f"EVID-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

        timestamps = [e.get("timestamp", "") for e in events if e.get("timestamp")]
        metadata = EvidencePackMetadata(
            pack_id=pack_id,
            created_at=datetime.now(UTC).isoformat(),
            format="json",
            entry_count=len(events),
            date_range_start=min(timestamps) if timestamps else "",
            date_range_end=max(timestamps) if timestamps else "",
            filters=filters or {},
        )

        pack = {
            "metadata": metadata.model_dump(),
            "events": events,
        }

        pack_json = dumps(pack, indent=2, ensure_ascii=False)
        checksum = hashlib.sha256(pack_json.encode("utf-8")).hexdigest()
        metadata.checksum = checksum
        pack["metadata"]["checksum"] = checksum

        output_path = self._output_dir / f"{pack_id}.json"
        output_path.write_text(pack_json, encoding="utf-8")

        result = ExportResult(
            success=True,
            output_path=str(output_path),
            format="json",
            entry_count=len(events),
            file_size_bytes=output_path.stat().st_size,
            checksum=checksum,
            exported_at=datetime.now(UTC).isoformat(),
        )
        _logger.info("EvidencePackExporter: exported JSON pack %s (%d entries)", pack_id, len(events))
        return result

    def export_fca(
        self,
        events: list[dict[str, Any]],
        pack_id: str = "",
        firm_reference: str = "",
        report_type: str = "audit-trail",
    ) -> ExportResult:
        import hashlib

        if not pack_id:
            pack_id = f"FCA-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"

        timestamps = [e.get("timestamp", "") for e in events if e.get("timestamp")]
        fca_record = {
            "header": {
                "schema_version": "1.0",
                "report_type": report_type,
                "firm_reference": firm_reference,
                "generated_at": datetime.now(UTC).isoformat(),
                "period_start": min(timestamps) if timestamps else "",
                "period_end": max(timestamps) if timestamps else "",
                "total_records": len(events),
            },
            "records": [],
        }

        for i, event in enumerate(events):
            fca_entry = {
                "record_id": f"REC-{i:06d}",
                "timestamp": event.get("timestamp", ""),
                "event_type": event.get("event_type", ""),
                "agent_id": event.get("agent_id", ""),
                "action": event.get("action_type", event.get("operation", "")),
                "target": event.get("target_path", event.get("file_path", "")),
                "status": event.get("status", ""),
                "entry_hash": event.get("entry_hash", ""),
                "provenance": event.get("provenance", ""),
                "metadata": event.get("metadata", {}),
            }
            fca_record["records"].append(fca_entry)

        fca_json = dumps(fca_record, indent=2, ensure_ascii=False)
        checksum = hashlib.sha256(fca_json.encode("utf-8")).hexdigest()

        output_path = self._output_dir / f"{pack_id}.fca.json"
        output_path.write_text(fca_json, encoding="utf-8")

        result = ExportResult(
            success=True,
            output_path=str(output_path),
            format="fca",
            entry_count=len(events),
            file_size_bytes=output_path.stat().st_size,
            checksum=checksum,
            exported_at=datetime.now(UTC).isoformat(),
        )
        _logger.info("EvidencePackExporter: exported FCA pack %s (%d entries)", pack_id, len(events))
        return result
