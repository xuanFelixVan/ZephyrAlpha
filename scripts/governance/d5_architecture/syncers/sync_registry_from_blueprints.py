# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/syncers/sync_registry_from_blueprints.py | §
# [MODULE] scripts.governance.d5_architecture.syncers.sync_registry_from_blueprints
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.syncers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""sync_registry_from_blueprints.py -- 从 blueprint.md frontmatter 同步 blueprint_registry.yaml

对标: Problem IX -- blueprint_registry.yaml 大面积不同步
职责: 扫描 03_modules/**/blueprint.md 的 frontmatter,与 registry 对账,生成 diff 或写入更新

changelog: 默认在 --write 且相对当前文件 blueprints[] 有差异时，在 changelog 顶部自动插入一条
  version=（取首条 x.y.z 记录的 patch+1），changes 含 [auto-sync] 摘要 + 差异 bullet。
  使用 --no-changelog 可跳过（例如 CI 或重复执行写入时避免噪音）。

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

import os

__manifest__ = {
    "args": ["--write", "--no-changelog"],
    "description": "同步 blueprint_registry.yaml [从 blueprint.md frontmatter 驱动]",
    "dimensions": ["D5"],
    "priority": "P0",
    "timeout_seconds": 60,
    "warn_only": False,
}

import argparse
import hashlib
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import BLUEPRINTS_DIR, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.walk import iter_files
from _shared.encoding import ensure_utf8_stdout
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

ensure_utf8_stdout()
BLUEPRINT_REGISTRY_PATH = REPO_ROOT / "docs" / "03_modules" / "blueprint_registry.yaml"

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装, 请运行 pip install pyyaml", file=sys.stderr)
    sys.exit(EXIT_ERROR)


def find_all_blueprints() -> list[Path]:
    """find_all_blueprints implementation."""
    if not BLUEPRINTS_DIR.exists():
        return []
    return iter_files(BLUEPRINTS_DIR, name_pattern="blueprint.md")


LAYER_DIR_MAP = {
    "data": "L2_domain",
    "infrastructure_runtime_integration": "L0_infrastructure",
    "factor": "L2_domain",
    "signal": "L2_domain",
    "risk": "L2_domain",
    "pf_core": "L2_domain",
    "ex_core": "L2_domain",
    "frontend": "L3_application",
    "research": "L2_domain",
    "compliance": "L2_domain",
    "ml_train": "L2_domain",
    "observability": "L0_infrastructure",
    "integration": "L2_domain",
    "_cross_layer": "L1_foundation",
    "_master-blueprint": "L1_foundation",
    "_domain-governance": "L1_foundation",
    "_system_master": "L1_foundation",
}


def expected_layer_from_path(filepath: Path) -> str | None:
    """expected_layer_from_path implementation."""
    rel = filepath.relative_to(REPO_ROOT).as_posix()
    for dir_key, expected_layer in LAYER_DIR_MAP.items():
        if f"/{dir_key}/" in rel or rel.startswith(f"docs/03_modules/{dir_key}/"):
            return expected_layer
    return None


def validate_layer_consistency(filepath: Path, fm: dict[str, Any]) -> list[str]:
    """Validate target against rules and report findings."""
    declared = fm.get("layer", "")
    expected = expected_layer_from_path(filepath)
    if expected is None:
        return []
    if declared != expected:
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        return [f"LAYER MISMATCH: {rel} — frontmatter layer={declared}，物理路径要求={expected}"]
    return []


def extract_frontmatter(filepath: Path) -> dict[str, Any]:
    """extract_frontmatter implementation."""
    text = filepath.read_text(encoding="utf-8")
    # 治本: 部分蓝图文件因编辑器/编码转换积累多个 BOM 字符，
    # 原只去 1 个 BOM，导致 22 个蓝图被误判排除。改用 lstrip 去所有 BOM。
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1)
    try:
        return yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        return {}


def field_signature(fm: dict[str, Any]) -> str:
    """field_signature implementation."""
    fields = [
        str(fm.get("module_id", "")),
        str(fm.get("title", "")),
        str(fm.get("version", "")),
        str(fm.get("status", "")),
        str(fm.get("date", "")),
        str(fm.get("layer", "")),
    ]
    return hashlib.md5("|".join(fields).encode()).hexdigest()[:8]


def load_registry() -> dict[str, Any] | None:
    """load_registry implementation."""
    if not BLUEPRINT_REGISTRY_PATH.exists():
        return None
    with open(BLUEPRINT_REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def make_registry_path(filepath: Path) -> str:
    """make_registry_path implementation."""
    try:
        rel = filepath.relative_to(REPO_ROOT / "docs")
        return rel.as_posix()
    except ValueError:
        return str(filepath)


def build_registry_entry(filepath: Path, fm: dict[str, Any]) -> dict[str, Any]:
    """build_registry_entry implementation."""
    rel_path = make_registry_path(filepath)
    return {
        "module_id": fm.get("module_id", ""),
        "name": filepath.parent.name,
        "title": fm.get("title", ""),
        "summary": fm.get("summary", ""),
        "layer": fm.get("layer", ""),
        "functional_domain": fm.get("functional_domain", fm.get("domain", "")),
        "blueprint_status": fm.get("status", "Draft"),
        "blueprint_level": fm.get("blueprint_level", "module"),
        "priority": fm.get("priority", "P2"),
        "version": fm.get("version", ""),
        "generation": fm.get("generation", ""),
        "last_updated": fm.get("last_updated", fm.get("date", "")),
        "file_path": rel_path,
        "construction_progress": fm.get("construction_progress", "not_started"),
    }


def _bump_changelog_semver(existing: list[Any]) -> str:
    """在既有 changelog 中找首条 x.y.z，patch+1；否则退回 1.0.0。"""
    for item in existing:
        if not isinstance(item, dict):
            continue
        v = str(item.get("version", "")).strip()
        m = re.match(r"^(\d+)\.(\d+)\.(\d+)$", v)
        if m:
            return f"{m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}"
    return "1.0.0"


def collect_registry_diff_bullets(
    old_entries: list[dict[str, Any]],
    new_entries: list[dict[str, Any]],
    *,
    max_lines: int = 28,
) -> list[str]:
    """与 dry-run 相同判据，产出可写入 changelog 的短句列表（超标截断）。"""
    if not old_entries and new_entries:
        return [
            f"全量登记 {len(new_entries)} 条 blueprint（登记表中原无 blueprints[] 或为空）",
        ]
    old_map = {e.get("module_id", ""): e for e in old_entries if e.get("module_id")}
    new_map = {e.get("module_id", ""): e for e in new_entries if e.get("module_id")}
    key_fields = (
        "title",
        "version",
        "last_updated",
        "layer",
        "file_path",
        "construction_progress",
        "priority",
        "blueprint_level",
        "blueprint_status",
    )
    mids = sorted(set(old_map.keys()) | set(new_map.keys()))
    out: list[str] = []
    for mid in mids:
        if not mid:
            continue
        old = old_map.get(mid)
        new = new_map.get(mid)
        if old is None and new is not None:
            out.append(f"新增 {mid} → {new.get('file_path', '?')}")
        elif old is not None and new is None:
            out.append(f"移除 {mid}（曾位于 {old.get('file_path', '?')}）")
        elif old and new:
            for k in key_fields:
                ov = str(old.get(k, ""))
                nv = str(new.get(k, ""))
                if ov != nv:
                    out.append(f"{mid}.{k}: [{ov}] → [{nv}]")

    excess = len(out) - max_lines
    if excess > 0:
        out = out[:max_lines]
        out.append(f"… 另 {excess} 条差异未展开（运行 dry-run 查看全量）")
    return out


def prepend_auto_changelog(
    registry: dict[str, Any],
    diff_bullets: list[str],
    *,
    total_blueprints: int,
) -> None:
    """prepend_auto_changelog implementation."""
    if not diff_bullets:
        return
    cl = registry.get("changelog")
    if not isinstance(cl, list):
        cl = []
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    version = _bump_changelog_semver(cl)
    head = (
        f"[auto-sync] blueprint-registry + module-registry；"
        f"扫描 {total_blueprints} 份 blueprint.md；登记项相对上一版有 {len(diff_bullets)} 条差异摘要"
    )
    entry: dict[str, Any] = {
        "version": version,
        "date": today,
        "changes": [head, *diff_bullets],
    }
    registry["changelog"] = [entry, *cl]
    print(f"[changelog] prepend version={version} bullets={len(diff_bullets)}", file=sys.stderr)


def rebuild_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """rebuild_summary implementation."""
    by_status: dict[str, int] = {}
    by_layer: dict[str, int] = {}
    by_cp: dict[str, int] = {}
    for e in entries:
        s = str(e.get("blueprint_status", "Draft"))
        by_status[s] = by_status.get(s, 0) + 1
        ly = str(e.get("layer", ""))
        by_layer[ly] = by_layer.get(ly, 0) + 1
        cp = str(e.get("construction_progress", "not_started"))
        by_cp[cp] = by_cp.get(cp, 0) + 1
    return {
        "total": len(entries),
        "by_blueprint_status": by_status,
        "by_layer": by_layer,
        "by_construction_progress": by_cp,
        "note": "由 sync_registry_from_blueprints.py 从 blueprints[] 派生——细则以物理 frontmatter 为准",
        "last_recomputed": datetime.now(UTC).strftime("%Y-%m-%d"),
    }


def run_dry_run(registry: dict[str, Any], new_entries: list[dict[str, Any]], file_paths: list[Path]) -> int:
    """run_dry_run implementation."""
    old_map: dict[str, dict] = {e.get("module_id", ""): e for e in registry.get("blueprints", [])}
    new_map: dict[str, dict] = {e.get("module_id", ""): e for e in new_entries}
    diffs: list[str] = []
    key_fields = (
        "title",
        "version",
        "last_updated",
        "layer",
        "file_path",
        "construction_progress",
        "priority",
        "blueprint_level",
    )
    for mid in sorted(set(list(old_map.keys()) + list(new_map.keys()))):
        old = old_map.get(mid)
        new = new_map.get(mid)
        if old is None and new is not None:
            diffs.append(f"  + NEW: {mid} [{new.get('file_path', '?')}]")
        elif old is not None and new is None:
            diffs.append(f"  - GONE: {mid} [{old.get('file_path', '?')}]")
        elif old and new:
            for k in key_fields:
                ov = str(old.get(k, ""))
                nv = str(new.get(k, ""))
                if ov != nv:
                    diffs.append(f"  ~ {mid}.{k}: [{ov}] -> [{nv}]")
    total = len(new_entries)
    reg_total = int(registry.get("registry", {}).get("total_blueprints", 0))
    if total != reg_total:
        diffs.append(f"  COUNT: {reg_total} -> {total}")

    print(f"Scan: {total} blueprints found (registry had {reg_total})")
    if diffs:
        print(f"Diffs ({len(diffs)}):")
        for d in diffs:
            print(d)
        return EXIT_FINDINGS
    else:
        print("No differences. Registry is in sync.")
        return EXIT_PASS


def run_write(
    registry: dict[str, Any],
    new_entries: list[dict[str, Any]],
    file_paths: list[Path],
    *,
    write_changelog: bool = True,
) -> int:
    """run_write implementation."""
    new_entries = sorted(new_entries, key=lambda e: e.get("module_id", ""))

    old_entries_raw = registry.get("blueprints", [])
    old_entries: list[dict[str, Any]] = [dict(e) for e in old_entries_raw] if isinstance(old_entries_raw, list) else []

    reg_meta = registry.get("registry", {})
    reg_meta["total_blueprints"] = len(new_entries)
    reg_meta["last_updated"] = datetime.now(UTC).strftime("%Y-%m-%d")
    reg_meta["note"] = f"Auto-synced from {len(new_entries)} blueprint.md files by sync_registry_from_blueprints.py"
    registry["registry"] = reg_meta
    if "metadata" not in registry or not isinstance(registry["metadata"], dict):
        registry["metadata"] = {}
    registry["metadata"]["generated_at"] = datetime.now(UTC).strftime("%Y-%m-%d")
    registry["metadata"]["generated_by"] = "sync_registry_from_blueprints.py"
    registry["metadata"]["canonical_source"] = (
        "物理 docs/03_modules/**/blueprint.md frontmatter（SSoT）；"
        "本文件由 sync_registry_from_blueprints.py 自动生成"
    )
    if write_changelog:
        bullets = collect_registry_diff_bullets(old_entries, new_entries)
        prepend_auto_changelog(registry, bullets, total_blueprints=len(new_entries))

    registry["blueprints"] = new_entries
    registry["summary"] = rebuild_summary(new_entries)

    content = yaml.dump(registry, allow_unicode=True, default_flow_style=False, sort_keys=False)
    atomic_write_safe(BLUEPRINT_REGISTRY_PATH, content)
    print(f"Wrote: {len(new_entries)} blueprints to {BLUEPRINT_REGISTRY_PATH}")
    return EXIT_PASS


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="同步 blueprint_registry.yaml 与磁盘 blueprint.md 文件")
    parser.add_argument("--write", action="store_true", help="写入 registry (默认 dry-run)")
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        help="写入时不自动在 blueprint_registry.yaml 顶部 prepend changelog（CI/重复跑脚本时用）",
    )
    parser.add_argument("--warn-only", action="store_true", help="警告模式: 失败不阻塞 (exit 0)")
    args = parser.parse_args()

    file_paths = find_all_blueprints()
    if not file_paths:
        print("No blueprint.md files found under docs/03_modules/")
        sys.exit(EXIT_ERROR if not args.warn_only else EXIT_PASS)

    entries: list[dict[str, Any]] = []
    layer_warnings: list[str] = []
    for fp in file_paths:
        fm = extract_frontmatter(fp)
        if not fm or not fm.get("module_id"):
            print(f"WARN: {fp} -- no valid frontmatter or missing module_id")
            continue
        entries.append(build_registry_entry(fp, fm))
        layer_warnings.extend(validate_layer_consistency(fp, fm))

    if layer_warnings:
        print(
            f"\n[LAYER-CHECK] {len(layer_warnings)} 个 layer 不一致警告 (registry 记录与物理路径不符):", file=sys.stderr
        )
        for w in layer_warnings:
            print(f"  ⚠ {w}", file=sys.stderr)
        print("", file=sys.stderr)

    registry = load_registry()
    if registry is None:
        print("ERROR: blueprint_registry.yaml not found")
        sys.exit(EXIT_ERROR if not args.warn_only else EXIT_PASS)

    if args.write:
        rc = run_write(
            registry,
            entries,
            file_paths,
            write_changelog=not args.no_changelog,
        )
    else:
        rc = run_dry_run(registry, entries, file_paths)

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if rc else EXIT_PASS)


if __name__ == "__main__":
    main()
