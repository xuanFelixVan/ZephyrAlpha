# [BLUEPRINT] GOV-076 | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] scripts.governance.observability.gate_cache
# [DOMAIN] D_OPS
# [DEPENDENCIES]
# [CONSUMERS] phase_manager.py;run_all.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 缓存key必须包含文件哈希;缓存失效必须及时
# [MODIFY-GUARD] 缓存格式变更需同步gate_engine.py
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CacheCorruptionError
# [TESTS] tests/test_gate_cache.py
# [TTL] permanent

from __future__ import annotations


__manifest__ = """
args: []
description: ⚠ 请补充 description
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""

import argparse
import hashlib
import json
import os
import sys
import threading
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

_BUF_SIZE = 65536


class CacheCorruptionError(RuntimeError):
    pass


class GateCache:
    def __init__(self, cache_dir: Path | None = None) -> None:
        if cache_dir is None:
            project_root = Path(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            )
            cache_dir = project_root / "data" / "gate_cache"
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._stats: dict[str, int] = {"hits": 0, "misses": 0}
        self._stats_lock = threading.Lock()  # 5.172.M12 修复: 保护 _stats += 自增线程安全

    def _incr_stat(self, key: str) -> None:
        # 5.172.M12 修复: += 是"读-改-写"三步操作, GIL 不保证原子性, 需加锁
        with self._stats_lock:
            self._stats[key] += 1

    @staticmethod
    def _file_hash(path: str) -> str:
        file_path = Path(path)
        if not file_path.exists():
            return ""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(_BUF_SIZE)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def _cache_entry_path(self, gate_id: str, file_hash: str) -> Path:
        safe_gate = gate_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        shard_dir = self._cache_dir / safe_gate
        shard_dir.mkdir(parents=True, exist_ok=True)
        return shard_dir / f"{file_hash}.json"

    def get(self, gate_id: str, file_path: str) -> dict | None:
        file_hash = self._file_hash(file_path)
        if not file_hash:
            self._incr_stat("misses")  # 5.172.M12 修复: 加锁自增
            return None
        entry_path = self._cache_entry_path(gate_id, file_hash)
        if not entry_path.exists():
            self._incr_stat("misses")  # 5.172.M12 修复: 加锁自增
            return None
        try:
            with open(entry_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            raise CacheCorruptionError(f"Cache entry corrupted: {entry_path} — {exc}") from exc
        stored_path = data.get("file_path", "")
        if stored_path != file_path:
            self._incr_stat("misses")  # 5.172.M12 修复: 加锁自增
            return None
        self._incr_stat("hits")  # 5.172.M12 修复: 加锁自增
        return data.get("result")

    def put(self, gate_id: str, file_path: str, result: dict) -> None:
        file_hash = self._file_hash(file_path)
        if not file_hash:
            return
        entry_path = self._cache_entry_path(gate_id, file_hash)
        payload: dict[str, Any] = {
            "gate_id": gate_id,
            "file_path": file_path,
            "file_hash": file_hash,
            "result": result,
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2)
        atomic_write_safe(entry_path, content)

    def invalidate(self, gate_id: str, file_path: str) -> None:
        file_hash = self._file_hash(file_path)
        if not file_hash:
            return
        entry_path = self._cache_entry_path(gate_id, file_hash)
        if entry_path.exists():
            try:
                os.remove(entry_path)
            except OSError:
                pass

    def invalidate_all(self, gate_id: str) -> None:
        safe_gate = gate_id.replace("/", "_").replace("\\", "_").replace(":", "_")
        shard_dir = self._cache_dir / safe_gate
        if not shard_dir.exists():
            return
        for entry in shard_dir.glob("*.json"):
            try:
                os.remove(entry)
            except OSError:
                pass

    def stats(self) -> dict[str, Any]:
        total_entries = 0
        total_size = 0
        for shard_dir in self._cache_dir.iterdir():
            if not shard_dir.is_dir():
                continue
            for entry in shard_dir.glob("*.json"):
                total_entries += 1
                try:
                    total_size += entry.stat().st_size
                except OSError:
                    pass
        return {
            "hits": self._stats["hits"],
            "misses": self._stats["misses"],
            "total_entries": total_entries,
            "total_size_bytes": total_size,
            "cache_dir": str(self._cache_dir),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase Gate file hash cache")
    parser.add_argument("--warn-only", action="store_true", help="Warn only mode")
    args = parser.parse_args()

    cache = GateCache()
    st = cache.stats()
    print("Gate Cache Stats:")
    print(f"  cache_dir:     {st['cache_dir']}")
    print(f"  hits:          {st['hits']}")
    print(f"  misses:        {st['misses']}")
    print(f"  total_entries: {st['total_entries']}")
    print(f"  total_size:    {st['total_size_bytes']} bytes")

    if args.warn_only:
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()
