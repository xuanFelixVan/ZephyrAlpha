# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.1
# [MODULE] zephyr.library.collectors.fs_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读扫描白名单目录（src/scripts/tests/docs/config/data/schemas/architecture_model）；跳过运行时/平行副本目录；>1MB 只记 size+mtime 不算哈希
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单文件读失败跳过（fail-soft）
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""fs_collector — 文件系统采集器：白名单目录全量盘点（只读）。

产出 FILE:/MOD: 资产（含 sha256 指纹），编外检测与七馆生成的底座。
# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/fs_collector.yaml
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Final

from zephyr.library.ledger_schema import derive_asset_id

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_SKIP_DIRS: Final[frozenset[str]] = frozenset(
    {
        ".git",
        "_working",
        ".runtime",
        ".aidrafts",
        ".aidrafts_pool",
        ".worktrees",
        "__pycache__",
        "node_modules",
        ".venv",
        "tmp",
        "vendor",
        "models",
        "_archive",
        ".trae",
        ".openclaw",
    }
)

_SCAN_ROOTS: Final[tuple[str, ...]] = (
    "src",
    "scripts",
    "tests",
    "docs",
    "config",
    "data",
    "schemas",
    "architecture_model",
)

_TEXT_SUFFIXES: Final[frozenset[str]] = frozenset(
    {
        ".py",
        ".md",
        ".yaml",
        ".yml",
        ".json",
        ".csv",
        ".ps1",
        ".sh",
        ".sql",
        ".txt",
        ".toml",
        ".cfg",
        ".ini",
        ".html",
    }
)

_MAX_HASH_BYTES = 1_000_000


def _sha256_file(path: Path) -> str:
    """流式计算文件 sha256。

    Args:
        path: 文件路径。

    Returns:
        十六进制哈希。
    """
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect(root: str = ".", limit: int = 60000) -> list[dict[str, Any]]:
    """扫描白名单目录，产出 FILE:/MOD: 资产列表。

        Args:
            root: 仓库根。
            limit: 产出上限（防失控）。

        Returns:
            资产字典列表（asset_id/kind/home/fingerprint_sha256/fingerprint_aux/title/tags）。

    # [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/fs_collector.yaml
    """
    base = Path(root)
    out: list[dict[str, Any]] = []
    for scan_root in _SCAN_ROOTS:
        base_dir = base / scan_root
        if not base_dir.exists():
            continue
        for path in sorted(base_dir.rglob("*")):
            if len(out) >= limit:
                return out
            if not path.is_file():
                continue
            rel = path.relative_to(base).as_posix()
            if any(part in _SKIP_DIRS for part in path.parts):
                continue
            suffix = path.suffix.lower()
            if suffix not in _TEXT_SUFFIXES:
                continue
            try:
                size = path.stat().st_size
            except OSError:
                continue
            kind: str
            if suffix == ".py" and rel.startswith("src/"):
                kind = "module"
            elif rel.startswith("docs/01_policies_and_standards/_registry/catalogs/"):
                kind = "registry"
            elif rel.startswith("docs/"):
                kind = "doc"
            else:
                kind = "file"
            fingerprint = None
            aux: dict[str, Any] = {"size": size}
            if size <= _MAX_HASH_BYTES:
                try:
                    fingerprint = _sha256_file(path)
                except OSError:
                    fingerprint = None
            else:
                aux["hash_skipped"] = "oversize"
            out.append(
                {
                    "asset_id": derive_asset_id(kind, rel),
                    "kind": kind,
                    "home": rel,
                    "fingerprint_sha256": fingerprint,
                    "fingerprint_aux": aux,
                    "title": path.name,
                    "ai_contract": None,
                    "owner_domain": None,
                    "tags": ["fs"],
                }
            )
    return out
