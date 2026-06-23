# [BLUEPRINT] MOD-INF-027 | docs/03_modules/_cross_layer/audit-orchestrator/blueprint.md | §4.4
# [MODULE] zephyr.governance.audit_trail.writer
# [DOMAIN] D-GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_trail.models
# [CONSUMERS] audit-orchestrator.pipeline_runner; cli
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 报告写入必须原子操作(temp-file+os.replace)
# [MODIFY-GUARD] 报告格式变更必须同步 cli.py + query.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 写入失败抛IOError
# [TESTS] tests/audit-orchestrator/test_writer.py
# [A_module] module_id=MOD-GOV_writer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from zephyr.governance.audit_trail.models import AuditIssue, GlobalAuditReport

logger = logging.getLogger(__name__)

__all__ = ["AuditReportWriter"]

DEFAULT_REPORT_DIR = Path("data/audit_history")


class AuditReportWriter:
    def __init__(self, report_dir: Path | None = None) -> None:
        self._report_dir = Path(report_dir or DEFAULT_REPORT_DIR)
        self._report_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, report: GlobalAuditReport, path: Path | None = None) -> Path:
        output_path = path or self._report_dir / f"{report.audit_id}.json"
        report.finished_at = report.finished_at or datetime.now()
        content = report.model_dump_json(indent=2, default=str)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(str(tmp_path), str(output_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        logger.info("Audit report written: %s", output_path)
        return output_path

    def write_issue(self, issue: AuditIssue, report_dir: Path) -> Path:
        dir_path = Path(report_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        output_path = dir_path / f"{issue.issue_id}.json"

        content = issue.model_dump_json(indent=2, default=str)
        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(str(tmp_path), str(output_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        return output_path

    def write_json(self, data: dict[str, Any], filename: str) -> Path:
        output_path = self._report_dir / filename
        content = json.dumps(data, indent=2, ensure_ascii=False, default=str)

        tmp_path = Path(str(output_path) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(content, encoding="utf-8")
            os.replace(str(tmp_path), str(output_path))
        except Exception:
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise

        return output_path

    def list_reports(self, limit: int = 50) -> list[Path]:
        files = sorted(self._report_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[:limit]


class AuditWriter:
    def __init__(self, backend=None):
        self.backend = backend

    def write(self, entry):
        pass

    def flush(self):
        pass


def get_audit_writer(backend=None):
    return AuditWriter(backend=backend)


def _generate_entry_id():
    import uuid

    return str(uuid.uuid4())


def _resolve_hmac_key(config=None):
    return b"default-key"
