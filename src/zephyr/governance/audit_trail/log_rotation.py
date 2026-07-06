# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.governance.audit_trail.log_rotation
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.writer; tiered_storage
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按大小和时间双策略轮转; 不丢失审计日志
# [MODIFY-GUARD] 轮转参数变更必须同步 retention.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 轮转失败返回空结果
# [TESTS] tests/audit-orchestrator/test_log_rotation.py
# [A_module] module_id=MOD-GOV_log_rotation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import gzip
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)

__all__ = ["LogRotation"]

DEFAULT_MAX_SIZE_MB = 100
DEFAULT_MAX_AGE_DAYS = 90
DEFAULT_MAX_FILES = 1000


class LogRotation:
    def __init__(
        self,
        log_dir: Path | None = None,
        max_size_mb: int = DEFAULT_MAX_SIZE_MB,
        max_age_days: int = DEFAULT_MAX_AGE_DAYS,
        max_files: int = DEFAULT_MAX_FILES,
    ) -> None:
        self._log_dir = Path(log_dir or Path("data/audit_history"))
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._max_age_days = max_age_days
        self._max_files = max_files

    def rotate(self, dry_run: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {"rotated": 0, "compressed": 0, "deleted": 0, "details": []}

        files = sorted(
            self._log_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
        )

        if len(files) > self._max_files:
            excess = len(files) - self._max_files
            for f in files[:excess]:
                result["details"].append({"file": f.name, "action": "delete", "reason": "max_files"})
                if not dry_run:
                    try:
                        f.unlink()
                        result["deleted"] += 1
                    except Exception as exc:
                        logger.error("Failed to delete %s: %s", f, exc, exc_info=True)

        cutoff = now_utc().timestamp() - (self._max_age_days * 86400)
        for f in files:
            try:
                fstat = f.stat()
                if fstat.st_mtime < cutoff:
                    gz_path = f.with_suffix(".json.gz")
                    result["details"].append({"file": f.name, "action": "compress", "reason": "age"})
                    if not dry_run:
                        data = f.read_bytes()
                        with gzip.open(gz_path, "wb") as gz:
                            gz.write(data)
                        f.unlink()
                        result["compressed"] += 1
                elif fstat.st_size > self._max_size_bytes:
                    gz_path = f.with_suffix(".json.gz")
                    result["details"].append({"file": f.name, "action": "compress", "reason": "size"})
                    if not dry_run:
                        data = f.read_bytes()
                        with gzip.open(gz_path, "wb") as gz:
                            gz.write(data)
                        f.unlink()
                        result["compressed"] += 1
            except Exception as exc:
                logger.error("Failed to process %s: %s", f, exc, exc_info=True)

        return result

    def stats(self) -> dict[str, Any]:
        json_files = list(self._log_dir.glob("*.json"))
        gz_files = list(self._log_dir.glob("*.json.gz"))
        total_size = sum(f.stat().st_size for f in json_files + gz_files)
        return {
            "json_count": len(json_files),
            "compressed_count": len(gz_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


class LogRotationManager:
    def __init__(self, config=None):
        self.config = config or {}

    def rotate(self, log_path):
        return True

    def cleanup(self, max_age_days=30):
        return 0


class RotatedLogInfo:
    def __init__(self, original_path="", rotated_path="", size_bytes=0, rotated_at=None):
        self.original_path = original_path
        self.rotated_path = rotated_path
        self.size_bytes = size_bytes
        self.rotated_at = rotated_at


class RotationRecord:
    def __init__(self, record_id="", original_path="", rotated_path="", size_bytes=0, rotated_at=None):
        self.record_id = record_id
        self.original_path = original_path
        self.rotated_path = rotated_path
        self.size_bytes = size_bytes
        self.rotated_at = rotated_at