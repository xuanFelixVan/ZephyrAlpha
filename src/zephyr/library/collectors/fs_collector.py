# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.1
# [MODULE] zephyr.library.collectors.fs_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读扫描白名单目录（src/scripts/tests/docs/config/data/schemas/architecture_model）；跳过运行时/平行副本目录（跳判按仓内相对路径成分，禁吃绝对路径）；vendored 模型产物走 _SKIP_PATHS 显式前缀（data/models；裸词 models 已废——审计失明清单#6：裸词吞掉全部 src/*/models 真包）；族级目录 _FAMILY_DIRS 只出 1 条族资产不逐件入册；>1MB 只记 size+mtime 不算哈希
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
        "_archive",
        ".trae",
        ".openclaw",
    }
)

# vendored/运行态模型产物显式前缀（审计失明清单#6 处方 B4：裸词 "models" 换显式白名单——
# 裸词按路径成分匹配会把 src/zephyr/<dom>/models/ 真包 26 处静默吞掉）。
_SKIP_PATHS: Final[tuple[str, ...]] = ("data/models",)

# 族级目录（ulib3 方案 A 同法）：按保留期滚动删除的运行态大盘，逐件入册=每轮转一次积一笔
# ghost 债（2026-09-23 实测两目录占 226/259 ghost、馆内 1988 行）。只出 1 条族资产指大盘，
# 明细不入册——与日志抽屉"族级入册、明细自查大盘"同口径。
_FAMILY_DIRS: Final[dict[str, str]] = {
    "data/architecture_health": "架构健康大盘（轮转快照，族级登记不逐件入册）",
    "data/runtime_violation_snapshot": "运行态违规快照大盘（轮转快照，族级登记不逐件入册）",
}

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
            # 只按仓内相对路径成分判跳（旧写法吃 path.parts=绝对路径全成分，仓库父目录名
            # 一旦撞上 tmp/vendor/models 等跳词，整棵扫描树静默归零）
            if any(part in _SKIP_DIRS for part in rel.split("/")):
                continue
            if any(rel == sp or rel.startswith(f"{sp}/") for sp in _SKIP_PATHS):
                continue  # vendored 模型产物（显式前缀，不误伤 src/*/models 真包）
            if any(rel == fam or rel.startswith(f"{fam}/") for fam in _FAMILY_DIRS):
                continue  # 族级目录逐件不入册，由下方族资产行统一代表
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
    for fam_rel, fam_title in _FAMILY_DIRS.items():
        fam_dir = base / fam_rel
        if not fam_dir.is_dir():
            continue
        n_files = sum(1 for p in fam_dir.rglob("*") if p.is_file())
        out.append(
            {
                "asset_id": derive_asset_id("file", fam_rel),
                "kind": "file",
                "home": fam_rel,
                "fingerprint_sha256": None,
                "fingerprint_aux": {"family": True, "files_on_disk": n_files},
                "title": fam_title,
                "ai_contract": (
                    f"族级资产：{fam_title}；当前在盘 {n_files} 件，明细不编目，进大盘自查"
                    "（与日志抽屉方案 A 同口径）。轮转删除不再产生 ghost。"
                ),
                "owner_domain": None,
                "tags": ["fs"],
            }
        )
    return out
