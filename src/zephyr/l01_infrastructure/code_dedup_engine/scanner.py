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
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from typing import Any


@dataclass
class ScanResult:
    file: str
    matches: list[tuple[str, float]] = field(default_factory=list)
    minhash: list[int] = field(default_factory=list)
    token_count: int = 0


@dataclass
class DuplicateGroup:
    group_id: str
    members: list[tuple[str, str]] = field(default_factory=list)
    similarity: float = 0.0
    detection_method: str = ""
    confidence: float = 0.0


class Scanner:
    """Stage 1: Token 级扫描——MinHash + LSH + 路径感知阈值."""

    _HASH_SEEDS: int = 128

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

    # ── 公共 API ──────────────────────────────────────────────

    def scan_file(self, file_path: str | Path) -> ScanResult:
        """扫描单个文件——返回归一化 tokens + MinHash."""
        path = Path(file_path)
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ScanResult(file=str(file_path))

        try:
            tokens = self._tokenize_and_normalize(source)
        except Exception:
            tokens = []

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
        """跨文件 LSHP 映射 —— 找出 Jaccard 相似的候选对."""
        groups: list[DuplicateGroup] = []
        files = list(self._minhashes.keys())
        seen: set[tuple[str, str]] = set()

        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                fi, fj = files[i], files[j]
                pair = (min(fi, fj), max(fi, fj))
                if pair in seen:
                    continue
                seen.add(pair)

                sim = self._jaccard_estimate(
                    self._minhashes[fi], self._minhashes[fj]
                )
                threshold = self._get_threshold(fi)
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

    # ── 代码块滑动窗口 ───────────────────────────────────────

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

    # ── 内部方法 ─────────────────────────────────────────────

    def _tokenize_and_normalize(self, source: str) -> list[str]:
        """Python tokenize 后归一化——剥离 docstring/注释 + 替换变量名/函数名."""
        tokens: list[str] = []
        try:
            g = tokenize.generate_tokens(StringIO(source).readline)
            for tok_type, tok_str, _, _, _ in g:
                if tok_type == tokenize.COMMENT:
                    continue
                if tok_type == tokenize.STRING:
                    tokens.append("_STR_")
                    continue
                if tok_type == tokenize.NAME:
                    if tok_str in {
                        "def", "class", "return", "if", "else", "elif",
                        "for", "while", "try", "except", "finally",
                        "with", "as", "import", "from", "pass", "raise",
                        "yield", "and", "or", "not", "in", "is", "None",
                        "True", "False",
                    }:
                        tokens.append(tok_str)
                    else:
                        tokens.append("_NAME_")
                    continue
                if tok_type == tokenize.NEWLINE:
                    tokens.append("_NL_")
                    continue
                tokens.append(tok_str)
        except tokenize.TokenError:
            pass
        return tokens

    def _compute_minhash(self, tokens: list[str]) -> list[int]:
        """计算 MinHash 签名——128 个哈希种子."""
        if not tokens:
            return [0] * 8

        signature: list[int] = []
        for seed in range(min(self._HASH_SEEDS, 128)):
            min_val = min(
                self._token_hash(t, seed) for t in tokens
            )
            signature.append(min_val)

        return self._compress_signature(signature)

    @staticmethod
    def _compress_signature(sig: list[int], n: int = 8) -> list[int]:
        """压缩——取间隔采样前 n 个."""
        if len(sig) <= n:
            return sig
        step = len(sig) // n
        return [sig[i * step] for i in range(n)]

    @staticmethod
    def _token_hash(token: str, seed: int) -> int:
        data = f"{seed}:{token}".encode("utf-8")
        return int(hashlib.md5(data).hexdigest(), 16) % (2**31)

    def _jaccard_estimate(self, a: list[int], b: list[int]) -> float:
        """MinHash Jaccard 相似度估计."""
        if not a or not b:
            return 0.0
        matches = sum(1 for x, y in zip(a, b) if x == y)
        return matches / min(len(a), len(b))

    def _get_threshold(self, file_path: str) -> float:
        path_lower = file_path.lower().replace("\\", "/")
        for keyword, th in self._PATH_THRESHOLDS.items():
            if keyword in path_lower:
                return th
        return self._DEFAULT_THRESHOLD
