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
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

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
        # 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
        from zephyr.shared.io.paths import REPO_ROOT

        self._log_dir = Path(log_dir or (REPO_ROOT / "data" / "audit_history"))
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
    """审计日志轮转管理器——按天轮转 events.jsonl，支持压缩和过期清理。"""

    _ACTIVE_LOG_NAME = "events.jsonl"
    _ROTATED_PREFIX = "audit-trail-"

    def __init__(
        self,
        data_dir: Path | str | None = None,
        compress_rotated: bool = True,
        max_rotated_days: int = 90,
        config: dict | None = None,
    ) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：相对默认锚定 REPO_ROOT 真源。
        from zephyr.shared.io.paths import REPO_ROOT

        self._data_dir = Path(data_dir) if data_dir else REPO_ROOT / "data" / "audit_history"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._compress_rotated = compress_rotated
        self._max_rotated_days = max_rotated_days
        self._last_rotation_date: str | None = None
        self.config = config or {}

    @property
    def max_rotated_days(self):
        """只读：max_rotated_days（Stage 4 公共化）。"""
        return self._max_rotated_days

    @max_rotated_days.setter
    def max_rotated_days(self, value):
        """写入：max_rotated_days（Stage 4 公共化）。"""
        self._max_rotated_days = value


    @property
    def compress_rotated(self):
        """只读：compress_rotated（Stage 4 公共化）。"""
        return self._compress_rotated

    @compress_rotated.setter
    def compress_rotated(self, value):
        """写入：compress_rotated（Stage 4 公共化）。"""
        self._compress_rotated = value


    @staticmethod
    def extract_date(filename: str) -> str | None:
        '从轮转文件名中提取日期（YYYY-MM-DD），无法提取返回 None。'
        import re
        m = re.search('(\\d{4}-\\d{2}-\\d{2})', filename)
        return m.group(1) if m else None


    @property
    def _active_log_path(self) -> Path:
        return self._data_dir / self._ACTIVE_LOG_NAME

    @staticmethod
    def _extract_date(filename: str) -> str | None:
        """向后兼容 thin wrapper（Stage 4 公共化，反向层级）。"""
        return LogRotationManager.extract_date(filename)

    def rotate(self, force: bool = False) -> RotationRecord | None:
        """轮转活跃日志。返回 RotationRecord 或 None。"""
        active = self._active_log_path
        if not active.exists():
            return None

        content = active.read_text(encoding="utf-8")
        if not content.strip():
            return None

        today = now_utc().strftime("%Y-%m-%d")
        if not force and self._last_rotation_date == today:
            return None

        entries = sum(1 for line in content.splitlines() if line.strip())
        rotated_name = f"{self._ROTATED_PREFIX}{today}.jsonl"
        rotated_path = self._data_dir / rotated_name
        compressed = False

        if self._compress_rotated:
            rotated_path = rotated_path.with_suffix(".jsonl.gz")
            data = content.encode("utf-8")
            with gzip.open(rotated_path, "wb") as gz:
                gz.write(data)
            compressed = True
        else:
            rotated_path.write_text(content, encoding="utf-8")

        active.write_text("", encoding="utf-8")
        self._last_rotation_date = today

        return RotationRecord(
            original_path=str(active),
            rotated_path=str(rotated_path),
            size_bytes=rotated_path.stat().st_size,
            rotated_at=now_utc(),
            entries_rotated=entries,
            compressed=compressed,
        )

    def get_rotated_logs(self) -> list[RotatedLogInfo]:
        """返回已轮转的日志文件列表。"""
        logs: list[RotatedLogInfo] = []
        for f in sorted(self._data_dir.glob(f"{self._ROTATED_PREFIX}*")):
            if not f.is_file():
                continue
            logs.append(RotatedLogInfo(
                original_path=str(self._active_log_path),
                rotated_path=str(f),
                size_bytes=f.stat().st_size,
                rotated_at=f.stat().st_mtime,
            ))
        return logs

    def cleanup_old_rotations(self) -> int:
        """删除超过 max_rotated_days 天的轮转文件（按文件名日期判断），返回删除数。"""
        from datetime import timedelta

        cutoff_date = (now_utc() - timedelta(days=self._max_rotated_days)).date()
        deleted = 0
        for f in self._data_dir.glob(f"{self._ROTATED_PREFIX}*"):
            if not f.is_file():
                continue
            date_str = self._extract_date(f.name)
            if not date_str:
                continue
            try:
                file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            if file_date < cutoff_date:
                try:
                    f.unlink()
                    deleted += 1
                except OSError:
                    continue
        return deleted

    def cleanup(self, max_age_days: int = 30) -> int:
        """兼容旧 API——委托至 cleanup_old_rotations。"""
        old_max = self._max_rotated_days
        self._max_rotated_days = max_age_days
        try:
            return self.cleanup_old_rotations()
        finally:
            self._max_rotated_days = old_max


class RotatedLogInfo:
    def __init__(self, original_path="", rotated_path="", size_bytes=0, rotated_at=None):
        self.original_path = original_path
        self.rotated_path = rotated_path
        self.size_bytes = size_bytes
        self.rotated_at = rotated_at


class RotationRecord:
    def __init__(
        self,
        record_id: str = "",
        original_path: str = "",
        rotated_path: str = "",
        size_bytes: int = 0,
        rotated_at=None,
        entries_rotated: int = 0,
        compressed: bool = False,
    ):
        self.record_id = record_id
        self.original_path = original_path
        self.rotated_path = rotated_path
        self.size_bytes = size_bytes
        self.rotated_at = rotated_at
        self.entries_rotated = entries_rotated
        self.compressed = compressed