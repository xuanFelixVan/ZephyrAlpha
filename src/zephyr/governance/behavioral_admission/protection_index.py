# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §17
# [MODULE] zephyr.governance.behavioral_admission.protection_index
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.behavioral_admission.verdict_engine
# [CONSUMERS] zephyr.governance.behavioral_admission.verdict_engine;MOD-INF-027(audit-orchestrator)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] anchor路径永远返回anchor级别；Bloom Filter假阳性必须通过Trie精确二次验证
# [MODIFY-GUARD] docs/docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md;src/zephyr/behavioral-admission/__init__.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] query: BloomFilterError->fallback to Trie-only; rebuild: IOError->return partial stats
# [TESTS] tests/test_behavioral_audit/test_protection_index.py
# [A_module] module_id=MOD-GOV_protection_index | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
import logging
import struct
import threading
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from zephyr.governance.behavioral_admission.verdict_engine import ProtectionLevel

logger = logging.getLogger(__name__)

ANCHOR_PATTERNS: Final[list[str]] = [
    ".trae/rules/",
    "project_rules.md",
    "_index.yaml",
    "AGENTS.md",
    "CLAUDE.md",
    "kill_switch.py",
    "rollback.py",
    "scripts/governance/",
    "scripts/lock_files.py",
    "src/zephyr/governance/",
    "src/zephyr/agent-rbac/",
    "src/zephyr/llm-security/",
    "src/zephyr/escalation-engine/",
    "src/zephyr/budget-enforcer/",
]

PROTECTED_PATTERNS: Final[list[str]] = [
    "src/zephyr/audit-trail/",
    "src/zephyr/rollback/",
    "src/zephyr/shared/",
    "src/zephyr/behavioral-admission/",
    "src/zephyr/behavioral-auditor/",
    "blueprint.md",
    "_registry.yaml",
    "script-manifest.yaml",
    "src/zephyr/kb/",
    "src/zephyr/vector-memory/",
]

NORMAL_PATTERNS: Final[list[str]] = [
    "src/zephyr/pipeline/",
    "src/zephyr/orchestrator/",
    "src/zephyr/runtime/",
    "src/zephyr/telemetry/",
    "src/zephyr/system-telemetry/",
    "src/zephyr/asset-inventory/",
    "tests/",
    "scripts/",
]

PUBLIC_PATTERNS: Final[list[str]] = [
    "docs/",
    "README.md",
    "LICENSE",
    ".gitignore",
    "pyproject.toml",
    "requirements",
]


class ProtectionEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = ""
    level: ProtectionLevel = ProtectionLevel.normal
    owner_module: str = ""
    anchor_reason: str = ""
    registered_at: float = 0.0


class IndexStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_entries: int = 0
    anchor_count: int = 0
    protected_count: int = 0
    normal_count: int = 0
    public_count: int = 0
    bloom_filter_size: int = 0
    trie_node_count: int = 0
    last_rebuild_time: float = 0.0


_FNV_OFFSET_BASIS_64: int = 0xCBF29CE484222325
_FNV_PRIME_64: int = 0x100000001B3
_BLOOM_DEFAULT_SIZE: int = 32768


def _fnv1a_64(data: bytes) -> int:
    h = _FNV_OFFSET_BASIS_64
    for byte in data:
        h ^= byte
        h = (h * _FNV_PRIME_64) & 0xFFFFFFFFFFFFFFFF
    return h


class _SimpleBloomFilter:
    __slots__ = ("_bits", "_count", "_num_hashes", "_size")

    def __init__(self, expected_items: int = 2000, fp_rate: float = 0.001) -> None:
        if expected_items <= 0:
            expected_items = 2000
        if fp_rate <= 0 or fp_rate >= 1:
            fp_rate = 0.001
        self._size = max(_BLOOM_DEFAULT_SIZE, int(-expected_items * (fp_rate**0.5) * 2))
        self._num_hashes = max(3, int(-expected_items * (fp_rate**0.5) / self._size * 8) + 3)
        self._bits: bytearray = bytearray((self._size + 7) // 8)
        self._count: int = 0

    def add(self, item: str) -> None:
        data = item.encode("utf-8")
        for i in range(self._num_hashes):
            h = _fnv1a_64(data + struct.pack("<I", i))
            idx = h % self._size
            byte_idx = idx >> 3
            bit_idx = idx & 7
            self._bits[byte_idx] |= 1 << bit_idx
        self._count += 1

    def might_contain(self, item: str) -> bool:
        data = item.encode("utf-8")
        for i in range(self._num_hashes):
            h = _fnv1a_64(data + struct.pack("<I", i))
            idx = h % self._size
            byte_idx = idx >> 3
            bit_idx = idx & 7
            if not (self._bits[byte_idx] & (1 << bit_idx)):
                return False
        return True

    @property
    def size(self) -> int:
        return self._size

    @property
    def count(self) -> int:
        return self._count

    def clear(self) -> None:
        self._bits = bytearray((self._size + 7) // 8)
        self._count = 0


class _PrefixTrie:
    __slots__ = ("_children", "_value")

    def __init__(self) -> None:
        self._children: dict[str, _PrefixTrie] = {}
        self._value: ProtectionLevel | None = None

    def insert(self, prefix: str, level: ProtectionLevel) -> None:
        node = self
        for ch in prefix:
            if ch not in node._children:
                node._children[ch] = _PrefixTrie()
            node = node._children[ch]
        node._value = level

    def lookup(self, path: str) -> ProtectionLevel | None:
        node = self
        result: ProtectionLevel | None = None
        for ch in path:
            if ch in node._children:
                node = node._children[ch]
                if node._value is not None:
                    result = node._value
            else:
                break
        return result

    def remove(self, prefix: str) -> bool:
        path_nodes: list[tuple[str, _PrefixTrie]] = []
        node = self
        for ch in prefix:
            if ch not in node._children:
                return False
            path_nodes.append((ch, node))
            node = node._children[ch]
        if node._value is None:
            return False
        node._value = None
        for ch, parent in reversed(path_nodes):
            child = parent._children[ch]
            if child._value is None and not child._children:
                del parent._children[ch]
            else:
                break
        return True

    @property
    def node_count(self) -> int:
        count = 1
        for child in self._children.values():
            count += child.node_count
        return count


class ProtectionIndex:
    def __init__(
        self,
        project_root: str | None = None,
        bloom_expected_items: int = 2000,
        bloom_fp_rate: float = 0.001,
    ) -> None:
        self._project_root = project_root or str(Path.cwd())
        self._bloom = _SimpleBloomFilter(expected_items=bloom_expected_items, fp_rate=bloom_fp_rate)
        self._trie = _PrefixTrie()
        self._entries: dict[str, ProtectionEntry] = {}
        self._lock = threading.Lock()
        self._last_rebuild_time: float = 0.0
        self._rebuild()

    def query(self, file_path: str) -> ProtectionLevel:
        # 修复路径分隔符：统一为正斜杠以兼容 Windows 反斜杠路径
        file_path = file_path.replace("\\", "/")
        with self._lock:
            if file_path in self._entries:
                return self._entries[file_path].level

            trie_result = self._trie.lookup(file_path)
            if trie_result is not None:
                return trie_result

            if self._bloom.might_contain(file_path):
                return self._trie.lookup(file_path) or ProtectionLevel.normal

            return ProtectionLevel.normal

    def query_batch(self, file_paths: list[str]) -> dict[str, ProtectionLevel]:
        return {fp: self.query(fp) for fp in file_paths}

    def is_anchor(self, file_path: str) -> bool:
        return self.query(file_path) == ProtectionLevel.anchor

    def get_entry(self, file_path: str) -> ProtectionEntry | None:
        with self._lock:
            return self._entries.get(file_path)

    def register(
        self,
        path: str,
        level: ProtectionLevel,
        owner_module: str = "",
        anchor_reason: str = "",
    ) -> None:
        import time as _time

        with self._lock:
            entry = ProtectionEntry(
                path=path,
                level=level,
                owner_module=owner_module,
                anchor_reason=anchor_reason,
                registered_at=_time.time(),
            )
            self._entries[path] = entry
            self._bloom.add(path)
            self._trie.insert(path, level)

    def unregister(self, path: str) -> bool:
        with self._lock:
            if path not in self._entries:
                return False
            del self._entries[path]
            self._trie.remove(path)
            return True

    def rebuild(self) -> IndexStats:
        with self._lock:
            self._bloom.clear()
            self._trie = _PrefixTrie()
            for path, entry in self._entries.items():
                self._bloom.add(path)
                self._trie.insert(path, entry.level)
            self._last_rebuild_time = __import__("time").time()
            return self._compute_stats()

    def get_stats(self) -> IndexStats:
        with self._lock:
            return self._compute_stats()

    def verify_integrity(self) -> list[str]:
        issues: list[str] = []
        with self._lock:
            for path, entry in self._entries.items():
                trie_result = self._trie.lookup(path)
                if trie_result != entry.level:
                    issues.append(
                        f"trie_mismatch:path={path}:entry_level={entry.level.value}:trie_level={trie_result.value if trie_result else 'None'}"
                    )
                if not self._bloom.might_contain(path):
                    issues.append(f"bloom_missing:path={path}")
        return issues

    def health_check(self) -> dict[str, Any]:
        stats = self.get_stats()
        issues = self.verify_integrity()
        return {
            "status": "healthy" if not issues else "degraded",
            "stats": stats.model_dump(),
            "integrity_issues": issues,
            "integrity_issue_count": len(issues),
        }

    def _rebuild(self) -> None:
        import time as _time

        self._last_rebuild_time = _time.time()
        for pattern in ANCHOR_PATTERNS:
            self._trie.insert(pattern, ProtectionLevel.anchor)
            self._bloom.add(pattern)
        for pattern in PROTECTED_PATTERNS:
            self._trie.insert(pattern, ProtectionLevel.protected)
            self._bloom.add(pattern)
        for pattern in NORMAL_PATTERNS:
            self._trie.insert(pattern, ProtectionLevel.normal)
            self._bloom.add(pattern)
        for pattern in PUBLIC_PATTERNS:
            self._trie.insert(pattern, ProtectionLevel.public)
            self._bloom.add(pattern)

    def _compute_stats(self) -> IndexStats:
        anchor_count = 0
        protected_count = 0
        normal_count = 0
        public_count = 0
        for entry in self._entries.values():
            if entry.level is ProtectionLevel.anchor:
                anchor_count += 1
            elif entry.level is ProtectionLevel.protected:
                protected_count += 1
            elif entry.level is ProtectionLevel.normal:
                normal_count += 1
            else:
                public_count += 1
        return IndexStats(
            total_entries=len(self._entries),
            anchor_count=anchor_count,
            protected_count=protected_count,
            normal_count=normal_count,
            public_count=public_count,
            bloom_filter_size=self._bloom.size,
            trie_node_count=self._trie.node_count,
            last_rebuild_time=self._last_rebuild_time,
        )
