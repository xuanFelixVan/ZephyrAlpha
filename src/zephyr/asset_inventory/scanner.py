"""AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器

蓝图 §3.1：遍历六大目录，为每个文件计算 SHA-256/大小/mtime，
使用 ThreadPoolExecutor 并行计算，产出 raw_asset_scan.json。
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from zephyr.asset_inventory.models import RawFileEntry, ScanResult

logger = logging.getLogger(__name__)

_MAX_WORKERS = 8
_TIMEOUT_SECONDS = 300
_MAX_FILE_SIZE_MB = 50
_MAX_DEPTH = 15
_GLIDE_WINDOW_SECONDS = 60

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCANS_DIR = PROJECT_ROOT / "data" / "scans"

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
    "session-logs",
    "_backup",
    "_archive",
}


class Scanner:
    """全量文件系统扫描器——Phase 1 实现（蓝图 §3.1）。"""

    def __init__(
        self,
        directories: Optional[list[str]] = None,
        excludes: Optional[set[str]] = None,
        max_workers: int = _MAX_WORKERS,
        timeout_seconds: int = _TIMEOUT_SECONDS,
        max_file_size_mb: int = _MAX_FILE_SIZE_MB,
        max_depth: int = _MAX_DEPTH,
        root: Optional[Path] = None,
    ) -> None:
        self.directories = directories or DEFAULT_DIRECTORIES
        self.excludes = excludes or DEFAULT_EXCLUDES
        self.max_workers = max_workers
        self.timeout_seconds = timeout_seconds
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.max_depth = max_depth
        self.root = root or PROJECT_ROOT

    def scan(self, *, incremental: bool = False, last_scan_time: Optional[datetime] = None) -> ScanResult:
        scan_id = _generate_scan_id()
        scanned_at = datetime.now(timezone.utc)
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
                logger.error(msg)
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
            completed_at=datetime.now(timezone.utc),
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
        last_scan_time: Optional[datetime],
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
                    mtime_dt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
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
            futures = {
                executor.submit(_process_one, fp, self.root): fp
                for fp in file_paths
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    entries.append(result)
                except Exception as exc:
                    fp = futures[future]
                    msg = f"处理失败 {fp}: {exc}"
                    logger.error(msg)
                    errors.append(msg)

        return entries, errors

    def save(self, result: ScanResult, output_path: Optional[Path] = None) -> Path:
        target = output_path or (SCANS_DIR / "raw_asset_scan.json")
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
    now = datetime.now(timezone.utc)
    seq = str(now.timestamp()).replace(".", "")[-3:]
    return f"SCAN-{now.strftime('%Y%m%d')}-{seq}"


def _process_one(file_path: Path, root: Path) -> RawFileEntry:
    stat = file_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
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
