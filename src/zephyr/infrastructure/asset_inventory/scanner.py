# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain-infra_ops/asset-inventory/blueprint.md
# [MODULE] zephyr.infrastructure.asset_inventory.scanner
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器

蓝图 §3.1：遍历六大目录，为每个文件计算 SHA-256/大小/mtime，
使用 ThreadPoolExecutor 并行计算，产出 raw-asset-scan.json。
"""

import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from zephyr.infrastructure.asset_inventory.models import RawFileEntry, ScanResult
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

logger = logging.getLogger(__name__)

_MAX_WORKERS = 8
_TIMEOUT_SECONDS = 300
_MAX_FILE_SIZE_MB = 50
_MAX_DEPTH = 15
_GLIDE_WINDOW_SECONDS = 60

SCANS_DIR = REPO_ROOT / "data" / "scans"

DEFAULT_DIRECTORIES = [
    "src/zephyr/",
    "scripts/",
    "docs/",
    "config/",
    "tests/",
    "data/",
]

DEFAULT_EXCLUDES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    "egg-info",
    ".ailocks",
    "session_logs",
    "_backup",
    "_archive",
}


class Scanner:
    """全量文件系统扫描器——Phase 1 实现（蓝图 §3.1）。"""

    def __init__(
        self,
        directories: list[str] | None = None,
        excludes: set[str] | None = None,
        max_workers: int = _MAX_WORKERS,
        timeout_seconds: int = _TIMEOUT_SECONDS,
        max_file_size_mb: int = _MAX_FILE_SIZE_MB,
        max_depth: int = _MAX_DEPTH,
        root: Path | None = None,
    ) -> None:
        self.directories = directories or DEFAULT_DIRECTORIES
        self.excludes = excludes or DEFAULT_EXCLUDES
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_depth = max_depth
        self.root = root or REPO_ROOT

    def scan(self, *, incremental: bool = False, last_scan_time: datetime | None = None) -> ScanResult:
        scan_id = _generate_scan_id()
        scanned_at = datetime.now(UTC)
        logger.info("开始 %s 扫描: %s", "增量" if incremental else "全量", scan_id)

        t0 = time.monotonic()
        file_paths: list[Path] = []
        errors: list[str] = []

        for rel_dir in self.directories:
            abs_dir = self.root / rel_dir
            if not abs_dir.is_dir():
                logger.warning("目录不存在，跳过: %s", abs_dir)
                continue
            try:
                self._walk(abs_dir, rel_dir, file_paths, incremental, last_scan_time)
            except Exception as exc:
                msg = f"目录遍历异常 {rel_dir}: {exc}"
                logger.error(msg, exc_info=True)
                errors.append(msg)

        total_files = len(file_paths)
        logger.info("收集到 %d 个文件，开始并行处理...", total_files)

        entries, scan_errors = self._process_parallel(file_paths)
        errors.extend(scan_errors)

        duration = time.monotonic() - t0
        total_size = sum(e.size_bytes for e in entries)

        logger.info("扫描完成: %d 文件, %.1fs", total_files, duration)

        return ScanResult(
            scan_id=scan_id,
            scanned_at=scanned_at,
            completed_at=datetime.now(UTC),
            total_files=total_files,
            total_size_bytes=total_size,
            scan_mode="incremental" if incremental else "full",
            entries=entries,
            errors=errors,
            duration_seconds=round(duration, 2),
        )

    def _walk(
        self,
        abs_dir: Path,
        rel_dir: str,
        out: list[Path],
        incremental: bool,
        last_scan_time: datetime | None,
    ) -> None:
        for entry in abs_dir.iterdir():
            if entry.is_symlink():
                continue
            if entry.name in self.excludes:
                continue

            if entry.is_dir():
                depth = len(entry.relative_to(self.root).parts)
                if depth > self.max_depth:
                    continue
                try:
                    self._walk(entry, f"{rel_dir}{entry.name}/", out, incremental, last_scan_time)
                except PermissionError:
                    pass
                continue

            if not entry.is_file():
                continue

            try:
                stat = entry.stat()
                if stat.st_size > self.max_file_size:
                    continue
                if incremental and last_scan_time:
                    mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
                    if mtime_dt < last_scan_time:
                        continue
                out.append(entry)
            except (OSError, PermissionError):
                pass

    def _process_parallel(self, file_paths: list[Path]) -> tuple[list[RawFileEntry], list[str]]:
        entries: list[RawFileEntry] = []
        errors: list[str] = []

        if not file_paths:
            return entries, errors

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_process_one, fp, self.root): fp for fp in file_paths}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    entries.append(result)
                except Exception as exc:
                    fp = futures[future]
                    msg = f"处理失败 {fp}: {exc}"
                    logger.error(msg, exc_info=True)
                    errors.append(msg)

        return entries, errors

    def save(self, result: ScanResult, output_path: Path | None = None) -> Path:
        target = output_path or (SCANS_DIR / "raw-asset-scan.json")
        SCANS_DIR.mkdir(parents=True, exist_ok=True)

        payload = result.model_dump(mode="json")
        content = json.dumps(payload, ensure_ascii=False, indent=2)

        tmp = f"{target}.{os.getpid()}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                f.write(content)
            os.replace(tmp, target)
        except PermissionError:
            try:
                os.remove(tmp)
            except OSError:
                pass
            raise

        logger.info("扫描结果已写入: %s (%d 条目)", target, result.total_files)
        return Path(target)

    def main(self) -> None:
        result = self.scan()
        output = self.save(result)

        print(f"  SCAN   {result.scan_id}")
        print(f"  FILES  {result.total_files}")
        print(f"  SIZE   {result.total_size_bytes:,} bytes")
        print(f"  TIME   {result.duration_seconds:.1f}s")
        print(f"  OUTPUT {output}")


def _generate_scan_id() -> str:
    now = datetime.now(UTC)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"SCAN-{now.strftime('%Y%m%d')}-{seq}"


def _process_one(file_path: Path, root: Path) -> RawFileEntry:
    stat = file_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
    sha = _sha256(file_path)

    rel = file_path.relative_to(root).as_posix()

    return RawFileEntry(
        relative_path=rel,
        absolute_path=str(file_path),
        file_name=file_path.name,
        extension=file_path.suffix,
        size_bytes=stat.st_size,
        mtime_utc=mtime,
        sha256=sha,
        is_binary=False,
    )


def _sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    Scanner().main()


if __name__ == "__main__":
    main()

# ============================================================================
# SRC-0040: 从 concurrent.py 合并 — ConcurrentScanner + merge_scans
# ============================================================================


class ConcurrentScanner:
    """跨会话并发扫描器——Glide Window + SHA256 重试 + 锁感知跳过。"""

    GLIDE_WINDOW_SEC = 60
    SHA_RETRY_COUNT = 3
    SHA_RETRY_DELAY_MS = 200
    DEFAULT_MAX_WORKERS = 4

    def __init__(self, project_root: Path) -> None:
        self._root = project_root
        self._lock_dir = project_root / ".ailocks"

    def _is_locked(self, path: Path) -> bool:
        try:
            rel = path.relative_to(self._root)
            sanitized = str(rel).replace("\\", "_").replace("/", "_")
            lock_dir = self._lock_dir / f"{sanitized}.lock"
            return lock_dir.exists()
        except ValueError:
            return False

    def scan_file(self, path: Path) -> RawFileEntry | None:
        if self._is_locked(path):
            return None

        age_sec = time.time() - path.stat().st_mtime
        if age_sec < self.GLIDE_WINDOW_SEC:
            return self._scan_with_retry(path)

        return self._scan_normal(path)

    def _scan_normal(self, path: Path) -> RawFileEntry | None:
        import hashlib

        try:
            st = path.stat()
            sha = hashlib.sha256(path.read_bytes()).hexdigest()
            rel_path = str(path.relative_to(self._root))
            return RawFileEntry(
                relative_path=rel_path,
                absolute_path=str(path),
                file_name=path.name,
                extension=path.suffix,
                size_bytes=st.st_size,
                mtime_utc=datetime.fromtimestamp(st.st_mtime, tz=UTC),
                ctime_utc=datetime.fromtimestamp(st.st_ctime, tz=UTC),
                sha256=sha,
            )
        except (OSError, PermissionError):
            return None

    def _scan_with_retry(self, path: Path) -> RawFileEntry | None:
        for _ in range(self.SHA_RETRY_COUNT):
            entry = self._scan_normal(path)
            if entry and self._verify_sha(path, entry.sha256):
                return entry
            time.sleep(self.SHA_RETRY_DELAY_MS / 1000)
        return None

    def _verify_sha(self, path: Path, expected: str) -> bool:
        import hashlib

        try:
            return hashlib.sha256(path.read_bytes()).hexdigest() == expected
        except (OSError, PermissionError):
            return False

    def scan_batch(
        self,
        paths: list[Path],
        max_workers: int | None = None,
    ) -> list[RawFileEntry]:
        workers = max_workers or self.DEFAULT_MAX_WORKERS
        results: list[RawFileEntry] = []
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_to_path = {pool.submit(self.scan_file, p): p for p in paths}
            for future in as_completed(future_to_path):
                try:
                    entry = future.result()
                    if entry is not None:
                        results.append(entry)
                except Exception as e:
                    logger.warning("suppressed error in scanner", exc_info=True)
        return results


def merge_scans(scan_a: ScanResult, scan_b: ScanResult) -> ScanResult:
    """多 Scanner 产出合并策略——保留最新 mtime 的版本。"""
    merged: dict[str, RawFileEntry] = {}

    for e in scan_a.entries:
        merged[e.relative_path] = e

    for e in scan_b.entries:
        if e.relative_path not in merged:
            merged[e.relative_path] = e
            continue

        existing = merged[e.relative_path]
        if existing.sha256 != e.sha256:
            if e.mtime_utc > existing.mtime_utc:
                merged[e.relative_path] = e

    entries = sorted(merged.values(), key=lambda x: x.relative_path)

    return ScanResult(
        scan_id=f"MERGE-{scan_a.scan_id}+{scan_b.scan_id}",
        scanned_at=min(scan_a.scanned_at, scan_b.scanned_at),
        completed_at=max(scan_a.completed_at, scan_b.completed_at),
        total_files=len(entries),
        total_size_bytes=sum(e.size_bytes for e in entries),
        entries=entries,
    )


# ============================================================================
# SRC-0040: 从 security_enforcer.py 合并 — SecurityFilter + SecurityAccessLogger
# ============================================================================

SECRET_FILENAME_PATTERNS: list[str] = [
    "*.env*",
    "*.secrets*",
    "*_key*",
    "*_token*",
    "*credentials*",
    "*.pem",
    "*.pkcs12",
]

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024

EXCLUDED_DIR_PARTS: set[str] = {".ailocks", "session_logs", ".git", "__pycache__", "node_modules"}


def _match_pattern(name: str, pattern: str) -> bool:
    import fnmatch

    return fnmatch.fnmatch(name, pattern)


class SecurityAccessRecord(BaseModel):
    """安全访问审计记录。"""

    ts: str
    action: str
    path: str
    reason: str | None = None
    sha256: str | None = None
    size: int | None = None


class SecurityFilter:
    """安全隐私边界过滤器——六不得铁律的机械化执行。"""

    def __init__(
        self,
        max_size_bytes: int = MAX_FILE_SIZE_BYTES,
        secret_patterns: list[str] | None = None,
        excluded_dirs: set[str] | None = None,
    ) -> None:
        self._max_size = max_size_bytes
        self._secret_patterns = secret_patterns or SECRET_FILENAME_PATTERNS
        self._excluded_dirs = excluded_dirs or EXCLUDED_DIR_PARTS

    def should_scan(self, path: Path) -> tuple[bool, str | None]:
        name = path.name.lower()

        for pattern in self._secret_patterns:
            if _match_pattern(name, pattern):
                return False, "matches_secret_pattern"

        parts = set(path.parts)
        if parts & self._excluded_dirs:
            return False, f"excluded_dir: {parts & self._excluded_dirs}"

        try:
            if path.is_symlink():
                return False, "is_symlink"
        except OSError:
            return False, "os_error"

        try:
            if path.stat().st_size > self._max_size:
                return False, f"over_size_limit: {path.stat().st_size} > {self._max_size}"
        except OSError:
            return False, "stat_error"

        return True, None


class SecurityAccessLogger:
    """审计追踪——盘点器每次扫描的文件级访问记录。"""

    def __init__(self, log_dir: Path) -> None:
        self._log_dir = log_dir
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._log_dir / "security_access_log.jsonl"

    def log_skip(self, file_path: str, reason: str) -> None:
        self._append(
            SecurityAccessRecord(
                ts=datetime.now(UTC).isoformat(),
                action="SCAN_SKIP",
                path=file_path,
                reason=reason,
            )
        )

    def log_ok(self, file_path: str, sha256: str, size: int) -> None:
        self._append(
            SecurityAccessRecord(
                ts=datetime.now(UTC).isoformat(),
                action="SCAN_OK",
                path=file_path,
                sha256=sha256,
                size=size,
            )
        )

    def _append(self, record: SecurityAccessRecord) -> None:
        try:
            tmp = f"{self._log_path}.{os.getpid()}.tmp"
            line = record.model_dump_json(exclude_none=True) + "\n"
            with open(tmp, "a", encoding="utf-8") as f:
                f.write(line)
            os.replace(tmp, self._log_path)
        except OSError:
            pass

    def recent_skips(self, limit: int = 50) -> list[SecurityAccessRecord]:
        if not self._log_path.exists():
            return []
        records: list[SecurityAccessRecord] = []
        try:
            for line in self._log_path.read_text(encoding="utf-8").strip().split("\n"):
                try:
                    obj = json.loads(line)
                    if obj.get("action") == "SCAN_SKIP":
                        records.append(SecurityAccessRecord(**obj))
                except (json.JSONDecodeError, ValueError):
                    continue
        except OSError:
            pass
        return records[-limit:]