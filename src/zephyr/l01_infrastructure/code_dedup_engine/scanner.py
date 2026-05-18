# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §3

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.scanner

# [INVARIANTS] MinHash signature size=128; min_token_count=20; LSH bands=16 rows=8

# [MODIFY-GUARD] signature_size/min_token_count/LSH_params change requires benchmark re-run

# [CONSUMERS] cli._cmd_scan; ct_deduplication.DeduplicationHandler; self_scanner

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] raises nothing; returns empty list on failure

# [TESTS] tests/unit/test_code_dedup_engine.py

"""Stage 1: Token 级 MinHash + LSH 扫描器.

职责：
  - Token 序列归一化（变量名→ _VAR_，函数名→ _FUNC_，剥离 docstring/注释）
  - MinHash 签名计算 + LSH 近似去重
  - 代码块级滑动窗口（min_block_size≥5 行）检测 import 块/异常模板
  - 路径感知阈值（shared:0.3 / core:0.6 / *:0.7 / tests:0.9 / scripts:0.7）
"""

from __future__ import annotations

import ast
import hashlib
import tokenize
from collections import defaultdict
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any


IDIOM_WHITELIST: frozenset[str] = frozenset({
    "__init__", "__repr__", "__str__", "__eq__", "__hash__",
    "__len__", "__getitem__", "__setitem__", "__contains__",
    "__iter__", "__next__", "__enter__", "__exit__",
    "__call__", "__bool__",
})

DESIGN_PATTERN_WHITELIST: frozenset[str] = frozenset({
    "Strategy", "Adapter", "Factory", "TemplateMethod",
    "Observer", "Decorator", "Singleton", "Builder",
})


@dataclass
class ScanResult:
    file: str
    matches: list[tuple[str, float]] = field(default_factory=list)
    minhash: list[int] = field(default_factory=list)
    token_count: int = 0
    skipped: bool = False
    skip_reason: str = ""


@dataclass
class DuplicateGroup:
    group_id: str
    members: list[tuple[str, str]] = field(default_factory=list)
    similarity: float = 0.0
    detection_method: str = ""
    confidence: float = 0.0


class Scanner:
    """Stage 1: Token 级扫描——MinHash + LSH + 路径感知阈值."""

    _SIGNATURE_SIZE: int = 128
    _MIN_TOKEN_COUNT: int = 20
    _LSH_BANDS: int = 16
    _LSH_ROWS: int = 8

    _PATH_THRESHOLDS: dict[str, float] = {
        "shared": 0.3,
        "core": 0.6,
        "tests": 0.9,
        "scripts": 0.7,
    }
    _DEFAULT_THRESHOLD: float = 0.7
    _MIN_BLOCK_SIZE: int = 5

    def __init__(self) -> None:
        self._minhashes: dict[str, list[int]] = {}
        self._tokens: dict[str, list[str]] = {}
        self._skipped: dict[str, str] = {}

    def scan_file(self, file_path: str | Path) -> ScanResult:
        """扫描单个文件——返回归一化 tokens + MinHash."""
        path = Path(file_path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ScanResult(file=str(file_path), skipped=True, skip_reason="read_error")

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return ScanResult(file=str(file_path), skipped=True, skip_reason="syntax_error")

        if self._is_whitelisted(tree):
            return ScanResult(
                file=str(file_path), skipped=True, skip_reason="idiom_whitelist"
            )

        try:
            tokens = self._tokenize_and_normalize(source)
        except Exception:
            tokens = []

        if len(tokens) < self._MIN_TOKEN_COUNT:
            return ScanResult(
                file=str(file_path),
                minhash=[],
                token_count=len(tokens),
                skipped=True,
                skip_reason=f"too_few_tokens({len(tokens)}<{self._MIN_TOKEN_COUNT})",
            )

        self._tokens[str(file_path)] = tokens
        minhash = self._compute_minhash(tokens)
        self._minhashes[str(file_path)] = minhash

        return ScanResult(
            file=str(file_path),
            minhash=minhash,
            token_count=len(tokens),
        )

    def scan_files(self, file_paths: list[str | Path]) -> list[ScanResult]:
        """批量扫描多文件."""
        return [self.scan_file(p) for p in file_paths]

    def find_duplicates(self) -> list[DuplicateGroup]:
        """LSH banding + Jaccard 精确估计——找出相似候选对."""
        candidates = self._lsh_candidates()
        groups: list[DuplicateGroup] = []
        seen: set[tuple[str, str]] = set()

        for fi, fj in candidates:
            pair = (min(fi, fj), max(fi, fj))
            if pair in seen:
                continue
            seen.add(pair)

            sim = self._jaccard_estimate(
                self._minhashes[fi], self._minhashes[fj]
            )
            threshold = max(self._get_threshold(fi), self._get_threshold(fj))
            if sim < threshold:
                continue

            groups.append(
                DuplicateGroup(
                    group_id=f"DUP-{hashlib.md5(f'{fi}_{fj}'.encode()).hexdigest()[:12]}",
                    members=[(fi, ""), (fj, "")],
                    similarity=round(sim, 3),
                    detection_method="minhash_lsh",
                    confidence=min(sim * 100, 95),
                )
            )

        return groups

    def scan_blocks(self, source: str) -> list[list[str]]:
        """对源码做 min_block_size 行滑动窗口——返回每个窗口的归一化 tokens."""
        lines = source.splitlines()
        if len(lines) < self._MIN_BLOCK_SIZE:
            return []

        blocks: list[list[str]] = []
        for start in range(len(lines) - self._MIN_BLOCK_SIZE + 1):
            block_text = "\n".join(lines[start : start + self._MIN_BLOCK_SIZE])
            try:
                tokens = self._tokenize_and_normalize(block_text)
            except Exception:
                tokens = []
            blocks.append(tokens)
        return blocks

    def _lsh_candidates(self) -> set[tuple[str, str]]:
        """LSH banding: 将签名分 band，同 band 同 hash 的文件对为候选."""
        bands = self._LSH_BANDS
        rows = self._LSH_ROWS
        sig_len = bands * rows
        candidates: set[tuple[str, str]] = set()

        if sig_len != self._SIGNATURE_SIZE:
            bands = self._SIGNATURE_SIZE // rows
            if bands < 1:
                bands = 1

        band_buckets: dict[int, dict[str, list[str]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for file_path, sig in self._minhashes.items():
            usable = sig[:bands * rows]
            for band_idx in range(bands):
                start = band_idx * rows
                end = start + rows
                if end > len(usable):
                    break
                band_slice = usable[start:end]
                band_hash = hashlib.md5(
                    ",".join(str(v) for v in band_slice).encode()
                ).hexdigest()
                band_buckets[band_idx][band_hash].append(file_path)

        for band_idx, buckets in band_buckets.items():
            for band_hash, files in buckets.items():
                if len(files) < 2:
                    continue
                for i in range(len(files)):
                    for j in range(i + 1, len(files)):
                        candidates.add((files[i], files[j]))

        return candidates

    def _is_whitelisted(self, tree: ast.AST) -> bool:
        """检查 AST 是否为惯用法白名单模式（仅含 __init__/__repr__/property 等）."""
        func_names: list[str] = []
        has_real_code: bool = False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_names.append(node.name)
            elif isinstance(node, (ast.Return, ast.Delete, ast.Global, ast.Nonlocal)):
                has_real_code = True
            elif isinstance(node, ast.Assign):
                for target in getattr(node, 'targets', []):
                    if isinstance(target, ast.Attribute):
                        has_real_code = True
            elif isinstance(node, ast.Call):
                if not isinstance(getattr(node, 'func', None), ast.Name):
                    has_real_code = True

        if not func_names and not has_real_code:
            return True

        if not func_names:
            return False

        non_whitelisted = [n for n in func_names if n not in IDIOM_WHITELIST]
        if len(non_whitelisted) == 0:
            return True

        return False

    def _tokenize_and_normalize(self, source: str) -> list[str]:
        """Python tokenize 后归一化——剥离 docstring/注释 + 保留关键字和定义名."""
        tokens: list[str] = []
        prev_keyword: str | None = None
        try:
            g = tokenize.generate_tokens(StringIO(source).readline)
            for tok_type, tok_str, _, _, _ in g:
                if tok_type == tokenize.COMMENT:
                    continue
                if tok_type == tokenize.STRING:
                    tokens.append("_STR_")
                    prev_keyword = None
                    continue
                if tok_type == tokenize.NAME:
                    keywords = {
                        "def", "class", "return", "if", "else", "elif",
                        "for", "while", "try", "except", "finally",
                        "with", "as", "import", "from", "pass", "raise",
                        "yield", "and", "or", "not", "in", "is", "None",
                        "True", "False",
                    }
                    if tok_str in keywords:
                        tokens.append(tok_str)
                        prev_keyword = tok_str
                    elif prev_keyword in ("def", "class"):
                        tokens.append(tok_str)
                        prev_keyword = None
                    elif prev_keyword in ("import", "from"):
                        tokens.append(tok_str)
                        prev_keyword = None
                    else:
                        tokens.append("_VAR_")
                        prev_keyword = None
                    continue
                if tok_type == tokenize.NEWLINE:
                    tokens.append("_NL_")
                    prev_keyword = None
                    continue
                prev_keyword = None
                tokens.append(tok_str)
        except tokenize.TokenError:
            pass
        return tokens

    def _compute_minhash(self, tokens: list[str]) -> list[int]:
        """计算 MinHash 签名——128 个哈希种子，不压缩."""
        if not tokens:
            return [0] * self._SIGNATURE_SIZE

        signature: list[int] = []
        for seed in range(self._SIGNATURE_SIZE):
            min_val = min(
                self._token_hash(t, seed) for t in tokens
            )
            signature.append(min_val)

        return signature

    @staticmethod
    def _token_hash(token: str, seed: int) -> int:
        data = f"{seed}:{token}".encode("utf-8")
        return int(hashlib.md5(data).hexdigest(), 16) % (2**31)

    def _jaccard_estimate(self, a: list[int], b: list[int]) -> float:
        """MinHash Jaccard 相似度估计——使用完整 128 签名."""
        if not a or not b:
            return 0.0
        min_len = min(len(a), len(b))
        if min_len == 0:
            return 0.0
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / min_len

    def _get_threshold(self, file_path: str) -> float:
        path_lower = file_path.lower().replace("\\", "/")
        for keyword, th in self._PATH_THRESHOLDS.items():
            if keyword in path_lower:
                return th
        return self._DEFAULT_THRESHOLD
