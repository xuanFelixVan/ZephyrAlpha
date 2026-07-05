# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3
# [MODULE] zephyr.governance.audit_trail.finding_ingest
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.audit_trail.finding_model; zephyr.governance.audit_trail.writer; zephyr.shared.event_bus
# [CONSUMERS] pipeline_runner.py; run_all.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] FindingIngest is the sole bridge between 144 governance scripts and audit-trail; every finding MUST pass through this class
# [MODIFY-GUARD] Ingest format changes require Finding Schema JSONL compatibility verification
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ingest_file() never raises; individual finding parse failures are logged and skipped
# [TESTS] tests/test_audit_finding_ingest.py
# [A_module] module_id=MOD-UNK_finding_ingest | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.governance.audit_trail.writer import AuditWriter

from pydantic import BaseModel, Field

from zephyr.governance.audit_trail.finding_model import AuditFinding

_logger = logging.getLogger(__name__)


class IngestResult(BaseModel):
    total: int = 0
    ingested: int = 0
    skipped: int = 0
    errors: int = 0
    finding_ids: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0


class FindingIngest:
    _subscribers_registered: bool = False

    def __init__(self, audit_dir: str = "data/audit_events") -> None:
        self._audit_dir = audit_dir
        self._writer: AuditWriter | None = None
        self._writer_initialized = False
        self._lock = threading.Lock()  # Phase 2 P2 修复（并发安全 MEDIUM）：_get_writer lazy init 线程安全

    def _get_writer(self) -> Any:
        if self._writer_initialized:
            return self._writer
        with self._lock:
            if self._writer_initialized:
                return self._writer
            self._writer_initialized = True
            try:
                from zephyr.governance.audit_trail.writer import get_audit_writer

                self._writer = get_audit_writer()
            except Exception:
                _logger.debug("FindingIngest: audit-trail.writer unavailable, will use local JSONL fallback")
                self._writer = None
        return self._writer

    def ingest_file(self, jsonl_path: str) -> IngestResult:
        self._ensure_subscribers()
        start = time.monotonic()
        total = 0
        ingested = 0
        skipped = 0
        errors = 0
        finding_ids: list[str] = []
        try:
            with open(jsonl_path, encoding="utf-8") as f:
                for line in f:
                    total += 1
                    stripped = line.strip()
                    if not stripped:
                        skipped += 1
                        continue
                    try:
                        finding = AuditFinding.from_jsonl(stripped)
                    except (ValueError, Exception) as exc:
                        errors += 1
                        _logger.warning("FindingIngest: parse error on line %d in %s: %s", total, jsonl_path, exc)
                        continue
                    if self._write_to_audit_trail(finding):
                        ingested += 1
                        finding_ids.append(finding.finding_id)
                        self._emit_event(finding)
                    else:
                        errors += 1
        except Exception as exc:
            _logger.error("FindingIngest: failed to read %s: %s", jsonl_path, exc)
        return IngestResult(
            total=total,
            ingested=ingested,
            skipped=skipped,
            errors=errors,
            finding_ids=finding_ids,
            duration_seconds=time.monotonic() - start,
        )

    def ingest_string(self, jsonl_content: str) -> IngestResult:
        self._ensure_subscribers()
        start = time.monotonic()
        total = 0
        ingested = 0
        skipped = 0
        errors = 0
        finding_ids: list[str] = []
        for line in jsonl_content.splitlines():
            total += 1
            stripped = line.strip()
            if not stripped:
                skipped += 1
                continue
            try:
                finding = AuditFinding.from_jsonl(stripped)
            except (ValueError, Exception) as exc:
                errors += 1
                _logger.warning("FindingIngest: parse error on line %d: %s", total, exc)
                continue
            if self._write_to_audit_trail(finding):
                ingested += 1
                finding_ids.append(finding.finding_id)
                self._emit_event(finding)
            else:
                errors += 1
        return IngestResult(
            total=total,
            ingested=ingested,
            skipped=skipped,
            errors=errors,
            finding_ids=finding_ids,
            duration_seconds=time.monotonic() - start,
        )

    def ingest_findings(self, findings: list[AuditFinding]) -> IngestResult:
        self._ensure_subscribers()
        start = time.monotonic()
        total = len(findings)
        ingested = 0
        errors = 0
        finding_ids: list[str] = []
        for finding in findings:
            if self._write_to_audit_trail(finding):
                ingested += 1
                finding_ids.append(finding.finding_id)
                self._emit_event(finding)
            else:
                errors += 1
        return IngestResult(
            total=total,
            ingested=ingested,
            skipped=0,
            errors=errors,
            finding_ids=finding_ids,
            duration_seconds=time.monotonic() - start,
        )

    @classmethod
    def _ensure_subscribers(cls) -> None:
        if cls._subscribers_registered:
            return
        try:
            from zephyr.shared.events.event_bus import bus

            bus.subscribe("audit.finding_created", cls._on_finding_created)
            bus.subscribe("audit.finding_resolved", cls._on_finding_resolved)
            cls._subscribers_registered = True
        except Exception:
            pass

    @staticmethod
    def _on_finding_created(payload: dict) -> None:
        import logging

        logger = logging.getLogger(__name__)
        severity = payload.get("severity", "")
        if severity in ("CRITICAL", "HIGH"):
            logger.info(
                "Event: audit.finding_created severity=%s finding_id=%s", severity, payload.get("finding_id", "")
            )

    @staticmethod
    def _on_finding_resolved(payload: dict) -> None:
        import logging

        logger = logging.getLogger(__name__)
        logger.info("Event: audit.finding_resolved finding_id=%s", payload.get("finding_id", ""))

    def _write_to_audit_trail(self, finding: AuditFinding) -> bool:
        writer = self._get_writer()
        if writer is not None:
            try:
                event_dict = finding.to_finding_dict()
                event_dict["event_type"] = "finding_ingested"
                writer.write(event_dict)
                return True
            except Exception as exc:
                _logger.error("FindingIngest: writer.write failed for %s: %s", finding.finding_id, exc)
        try:
            audit_path = Path(self._audit_dir)
            audit_path.mkdir(parents=True, exist_ok=True)
            fallback_file = audit_path / "findings.jsonl"
            tmp_path = str(fallback_file) + f".{os.getpid()}.tmp"
            line = finding.to_jsonl()
            existing = ""
            if fallback_file.exists():
                existing = fallback_file.read_text(encoding="utf-8")
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(existing)
                if existing and not existing.endswith("\n"):
                    f.write("\n")
                f.write(line)
            os.replace(tmp_path, str(fallback_file))
            _logger.info("FindingIngest: wrote %s to fallback %s", finding.finding_id, fallback_file)
            return True
        except Exception as exc:
            _logger.error("FindingIngest: fallback write failed for %s: %s", finding.finding_id, exc)
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            return False

    def _emit_event(self, finding: AuditFinding) -> None:
        try:
            from zephyr.shared.events.event_bus import bus

            payload = finding.to_finding_dict()
            bus.emit(topic="audit.finding_created", payload=payload)
        except Exception:
            pass
