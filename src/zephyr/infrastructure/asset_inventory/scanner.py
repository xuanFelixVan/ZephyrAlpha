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
# [A_module] module_id=MOD-INF-026 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
AssetDiscoveryScanner — MOD-INF-026 L1 全量文件系统扫描器

蓝图 §3.1：遍历六大目录，为每个文件计算 SHA-256/大小/mtime，
使用 ThreadPoolExecutor 并行计算，产出 raw-asset-scan.json。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: scan_a 参数
#   fields: 参数 scan_a，类型注解 ScanResult
#   code: scanner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: scan_b 参数
#   fields: 参数 scan_b，类型注解 ScanResult
#   code: scanner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① Scanner
#   name_en: Scanner
#   intro: 全量文件系统扫描器——Phase 1 实现（蓝图 §3.1）。
#   desc: 全量文件系统扫描器——Phase 1 实现（蓝图 §3.1）。；公共方法（定义序）: tokenize_and_normalize, jaccard_estimate, get_threshold, compute_m…
#   inputs: directories excludes max_workers timeout_seconds max_file_size_mb max…
#   outputs: 返回值
# - id: A2
#   name_zh: ② main
#   name_en: main
#   intro: main() 源码 L540-L541
#   desc: 源码 L540-L541
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ConcurrentScanner
#   name_en: ConcurrentScanner
#   intro: 跨会话并发扫描器——Glide Window + SHA256 重试 + 锁感知跳过。
#   desc: 跨会话并发扫描器——Glide Window + SHA256 重试 + 锁感知跳过。；公共方法（定义序）: verify_sha, scan_normal, lock_dir, is_locked, root, sc…
#   inputs: project_root
#   outputs: 返回值
# - id: A4
#   name_zh: ④ merge_scans
#   name_en: merge_scans
#   intro: 多 Scanner 产出合并策略——保留最新 mtime 的版本。
#   desc: 多 Scanner 产出合并策略——保留最新 mtime 的版本。；源码 L671-L697
#   inputs: scan_a scan_b
#   outputs: ScanResult
# - id: A5
#   name_zh: ⑤ SecurityFilter
#   name_en: SecurityFilter
#   intro: 安全隐私边界过滤器——六不得铁律的机械化执行。
#   desc: 安全隐私边界过滤器——六不得铁律的机械化执行。；公共方法（定义序）: should_scan；源码 L736-L772
#   inputs: max_size_bytes secret_patterns excluded_dirs
#   outputs: 返回值
# - id: A6
#   name_zh: ⑥ SecurityAccessLogger
#   name_en: SecurityAccessLogger
#   intro: 审计追踪——盘点器每次扫描的文件级访问记录。
#   desc: 审计追踪——盘点器每次扫描的文件级访问记录。；公共方法（定义序）: log_skip, log_ok, recent_skips；源码 L775-L828
#   inputs: log_dir
#   outputs: 返回值
#   （注：A6 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ScanResult
#   name_en: ScanResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

import hashlib
import io
import json
import keyword
import logging
import os
import re
import time
import tokenize
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel

from zephyr.infrastructure.asset_inventory.models import DuplicateGroup, RawFileEntry, ScanResult
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

logger = logging.getLogger(__name__)

_MAX_WORKERS = 8
_TIMEOUT_SECONDS = 300
_MAX_FILE_SIZE_MB = 50
_MAX_DEPTH = 15
_GLIDE_WINDOW_SECONDS = 60

# MOD-INF-017: 重复代码检测常量
_MINHASH_SIZE = 8
_MINHASH_SEEDS = [
    (31, 1000000007),
    (37, 1000000009),
    (41, 1000000021),
    (43, 1000000033),
    (47, 1000000087),
    (53, 1000000093),
    (59, 1000000097),
    (61, 1000000103),
]
_BLOCK_MIN_LINES = 3
_DEFAULT_THRESHOLD = 0.7

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
        # MOD-INF-017: 单文件扫描结果缓存（find_duplicates 使用）
        self._file_results: list[ScanResult] = []

    def tokenize_and_normalize(self, code) -> list[str]:
        """公共接口：tokenize_and_normalize（Stage 4 公共化）。"""
        return self._tokenize_and_normalize(code)

    def jaccard_estimate(self, a, b) -> float:
        """公共接口：jaccard_estimate（Stage 4 公共化）。"""
        return self._jaccard_estimate(a, b)

    def get_threshold(self, path) -> float:
        """公共接口：get_threshold（Stage 4 公共化）。"""
        return self._get_threshold(path)

    def compute_minhash(self, tokens) -> list[int]:
        """公共接口：compute_minhash（Stage 4 公共化）。"""
        return self._compute_minhash(tokens)

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
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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

    # ── MOD-INF-017: 重复代码检测方法 ──────────────────────────────────
    def scan_file(self, file_path: str) -> ScanResult:
        """扫描单个文件，返回带 minhash 的 ScanResult。"""
        p = Path(file_path)
        if not p.exists() or not p.is_file():
            return ScanResult(file=str(file_path), token_count=0, minhash=[0] * _MINHASH_SIZE)
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ScanResult(file=str(file_path), token_count=0, minhash=[0] * _MINHASH_SIZE)
        tokens = self._tokenize_and_normalize(content)
        minhash = self._compute_minhash(tokens)
        result = ScanResult(
            file=str(file_path),
            token_count=len(tokens),
            minhash=minhash,
        )
        self._file_results.append(result)
        return result

    def scan_files(self, file_paths: list[str]) -> list[ScanResult]:
        """批量扫描多个文件。"""
        return [self.scan_file(fp) for fp in file_paths]

    def find_duplicates(self) -> list[DuplicateGroup]:
        """检测已扫描文件中的重复组。"""
        groups: list[DuplicateGroup] = []
        results = list(self._file_results)
        n = len(results)
        if n < 2:
            return groups
        group_id_counter = 1
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._jaccard_estimate(results[i].minhash, results[j].minhash)
                threshold = self._get_threshold(results[i].file)
                if sim >= threshold:
                    groups.append(
                        DuplicateGroup(
                            group_id=f"DUP-{group_id_counter:03d}",
                            members=[
                                (results[i].file, ""),
                                (results[j].file, ""),
                            ],
                            similarity=round(sim, 4),
                            detection_method="minhash_lsh",
                            confidence=round(sim * 100, 2),
                        )
                    )
                    group_id_counter += 1
        return groups

    def scan_blocks(self, code: str) -> list[str]:
        """将代码切分为块（每块至少 _BLOCK_MIN_LINES 行）。"""
        lines = code.splitlines()
        if len(lines) < _BLOCK_MIN_LINES:
            return []
        blocks: list[str] = []
        step = _BLOCK_MIN_LINES
        for start in range(0, len(lines) - step + 1, step):
            block = "\n".join(lines[start : start + step])
            blocks.append(block)
        return blocks

    def _tokenize_and_normalize(self, code: str) -> list[str]:
        """tokenize 并归一化：关键字保留，名称→_NAME_，字符串→_STR_，注释剔除。"""
        tokens: list[str] = []
        try:
            reader = io.StringIO(code).readline
            for tok in tokenize.generate_tokens(reader):
                normalized = self._normalize_token(tok.type, tok.string)
                if normalized is not None:
                    tokens.append(normalized)
        except tokenize.TokenError:
            tokens = self._fallback_tokenize(code)
        return tokens

    @staticmethod
    def _normalize_token(ttype: int, tval: str) -> str | None:
        """将单个 token 归一化为标准形式，返回 None 表示跳过。"""
        _SKIP_TYPES = {
            tokenize.ENCODING,
            tokenize.ENDMARKER,
            tokenize.NEWLINE,
            tokenize.NL,
            tokenize.INDENT,
            tokenize.DEDENT,
            tokenize.COMMENT,
        }
        if ttype in _SKIP_TYPES:
            return None
        if ttype == tokenize.STRING:
            return "_STR_"
        if ttype == tokenize.NAME:
            return tval if keyword.iskeyword(tval) else "_NAME_"
        if ttype == tokenize.NUMBER:
            return "_NUM_"
        return tval if tval.strip() else None

    @staticmethod
    def _fallback_tokenize(code: str) -> list[str]:
        """语法错误时的退化分词器。"""
        tokens: list[str] = []
        parts = re.findall(r"\w+|[^\s\w]+", code)
        for part in parts:
            if part.startswith("#"):
                continue
            if part.startswith('"') or part.startswith("'"):
                tokens.append("_STR_")
            elif keyword.iskeyword(part):
                tokens.append(part)
            elif re.match(r"^\d", part):
                tokens.append("_NUM_")
            elif re.match(r"^[A-Za-z_]\w*$", part):
                tokens.append("_NAME_")
            else:
                tokens.append(part)
        return tokens

    def _compute_minhash(self, tokens: list[str]) -> list[int]:
        """计算 MinHash 签名（8 维）。空输入返回 [0]*8。

        使用 2-gram shingle 保留 token 序列信息，避免纯 token 集合导致的误判。
        """
        if not tokens:
            return [0] * _MINHASH_SIZE
        # 构建 2-gram shingles（单 token 时退化为 1-gram）
        if len(tokens) == 1:
            shingles = [tokens[0]]
        else:
            shingles = [f"{tokens[i]}|{tokens[i + 1]}" for i in range(len(tokens) - 1)]
        minhash: list[int] = []
        for a, m in _MINHASH_SEEDS:
            min_h = m
            for s in shingles:
                h = (a * hash(s) + 17) % m
                if h < min_h:
                    min_h = h
            minhash.append(min_h)
        return minhash

    def _jaccard_estimate(self, a: list[int], b: list[int]) -> float:
        """基于 MinHash 签名估算 Jaccard 相似度。"""
        if not a or not b:
            return 0.0
        if len(a) != len(b):
            return 0.0
        matches = sum(1 for x, y in zip(a, b, strict=False) if x == y)
        return matches / len(a)

    def _get_threshold(self, path: str) -> float:
        """根据文件路径返回相似度阈值。"""
        p = str(path).replace("\\", "/")
        if "shared" in p:
            return 0.3
        if "core" in p:
            return 0.6
        if "tests" in p:
            return 0.9
        if "scripts" in p:
            return 0.7
        return _DEFAULT_THRESHOLD

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
                except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            with open(tmp, "w", encoding="utf-8", newline="") as f:
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

    def verify_sha(self, path, expected) -> bool:
        """公共接口：verify_sha（Stage 4 公共化）。"""
        return self._verify_sha(path, expected)

    def scan_normal(self, path) -> RawFileEntry | None:
        """公共接口：scan_normal（Stage 4 公共化）。"""
        return self._scan_normal(path)

    @property
    def lock_dir(self):
        """只读：lock_dir（Stage 4 公共化）。"""
        return self._lock_dir

    @lock_dir.setter
    def lock_dir(self, value):
        """写入：lock_dir（Stage 4 公共化）。"""
        self._lock_dir = value

    def is_locked(self, path) -> bool:
        """公共接口：is_locked（Stage 4 公共化）。"""
        return self._is_locked(path)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def root(self):
        """只读：root（Stage 4 公共化）。"""
        return self._root

    @root.setter
    def root(self, value):
        """写入：root（Stage 4 公共化）。"""
        self._root = value

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
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
            with open(tmp, "a", encoding="utf-8", newline="") as f:
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
