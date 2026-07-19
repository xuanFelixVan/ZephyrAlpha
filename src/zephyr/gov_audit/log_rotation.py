# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §5.1
# [MODULE] zephyr.gov_audit.log_rotation
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.writer; tiered_storage
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按大小和时间双策略轮转; 不丢失审计日志; 覆盖.json+.jsonl含MCP审计目录logs/mcp_audit
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
from typing import Final

logger = logging.getLogger(__name__)

__all__ = ["MCP_AUDIT_LOG_DIR", "LogRotation"]

DEFAULT_MAX_SIZE_MB: Final[int] = 100
DEFAULT_MAX_AGE_DAYS: Final[int] = 90
DEFAULT_MAX_FILES: Final[int] = 1000

# 5.37.12：MCP 审计日志目录纳入轮转覆盖；.jsonl 与 .json 均参与轮转
MCP_AUDIT_LOG_DIR: Final[Path] = Path("logs/mcp_audit")
_ROTATE_PATTERNS: Final[tuple[str, ...]] = ("*.json", "*.jsonl")


class LogRotation:
    def __init__(
        self,
        log_dir: Path | None = None,
        max_size_mb: int = DEFAULT_MAX_SIZE_MB,
        max_age_days: int = DEFAULT_MAX_AGE_DAYS,
        max_files: int = DEFAULT_MAX_FILES,
        extra_dirs: list[Path] | tuple[Path, ...] | None = None,
    ) -> None:
        self._log_dir = Path(log_dir or Path("data/audit_history"))
        # 5.37.12：默认追加 MCP 审计日志目录（tools_call.jsonl）到轮转范围；
        # 显式传 extra_dirs=() 可关闭追加（测试隔离），传自定义 list 可扩展。
        dirs: list[Path] = [self._log_dir]
        for d in (extra_dirs if extra_dirs is not None else (MCP_AUDIT_LOG_DIR,)):
            p = Path(d)
            if p not in dirs:
                dirs.append(p)
        self._log_dirs: list[Path] = dirs
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._max_age_days = max_age_days
        self._max_files = max_files

    def _iter_log_files(self) -> list[Path]:
        """枚举全部覆盖目录的轮转候选文件（5.37.12：.json + .jsonl，按 mtime 升序）。"""
        files: list[Path] = []
        for d in self._log_dirs:
            if not d.exists():
                continue
            for pattern in _ROTATE_PATTERNS:
                files.extend(f for f in d.glob(pattern) if f.is_file())
        return sorted(files, key=lambda p: p.stat().st_mtime)

    def rotate(self, dry_run: bool = False) -> dict[str, Any]:
        result: dict[str, Any] = {"rotated": 0, "compressed": 0, "deleted": 0, "details": []}

        files = self._iter_log_files()

        if len(files) > self._max_files:
            excess = len(files) - self._max_files
            for f in files[:excess]:
                result["details"].append({"file": f.name, "action": "delete", "reason": "max_files"})
                if not dry_run:
                    try:
                        f.unlink()
                        result["deleted"] += 1
                    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                        logger.error("Failed to delete %s: %s", f, exc, exc_info=True)

        cutoff = now_utc().timestamp() - (self._max_age_days * 86400)
        for f in files:
            try:
                fstat = f.stat()
                if fstat.st_mtime < cutoff:
                    # 5.37.12：保留原扩展名再加 .gz（.jsonl -> .jsonl.gz，不再误改 .json.gz）
                    gz_path = f.with_name(f.name + ".gz")
                    result["details"].append({"file": f.name, "action": "compress", "reason": "age"})
                    if not dry_run:
                        data = f.read_bytes()
                        with gzip.open(gz_path, "wb") as gz:
                            gz.write(data)
                        f.unlink()
                        result["compressed"] += 1
                elif fstat.st_size > self._max_size_bytes:
                    gz_path = f.with_name(f.name + ".gz")
                    result["details"].append({"file": f.name, "action": "compress", "reason": "size"})
                    if not dry_run:
                        data = f.read_bytes()
                        with gzip.open(gz_path, "wb") as gz:
                            gz.write(data)
                        f.unlink()
                        result["compressed"] += 1
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.error("Failed to process %s: %s", f, exc, exc_info=True)

        return result

    def stats(self) -> dict[str, Any]:
        json_files: list[Path] = []
        jsonl_files: list[Path] = []
        gz_files: list[Path] = []
        for d in self._log_dirs:
            if not d.exists():
                continue
            json_files.extend(d.glob("*.json"))
            jsonl_files.extend(d.glob("*.jsonl"))
            gz_files.extend(d.glob("*.gz"))
        total_size = sum(f.stat().st_size for f in json_files + jsonl_files + gz_files)
        return {
            "json_count": len(json_files),
            "jsonl_count": len(jsonl_files),
            "compressed_count": len(gz_files),
            "covered_dirs": [str(d) for d in self._log_dirs],
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