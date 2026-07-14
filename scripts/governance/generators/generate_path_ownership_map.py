# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §
# [MODULE] scripts.governance.generators.generate_path_ownership_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
"""从蓝图§0.1聚合生成 path_ownership_map.yaml 路径归属声明。

对标: CODEOWNERS + Bazel visibility。
生成物: docs/03_modules/path_ownership_map.yaml

用法:
    python scripts/governance/generators/generate_path_ownership_map.py            # stdout
    python scripts/governance/generators/generate_path_ownership_map.py --write    # 覆写
    python scripts/governance/generators/generate_path_ownership_map.py --check    # CI 漂移检测
    python scripts/governance/generators/generate_path_ownership_map.py --conflicts  # 仅输出冲突
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 从蓝图§0.1聚合生成 path_ownership_map.yaml 路径归属声明。
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

# 治本(ARCH-036 迁移遗漏): 迁移到 generators/ 子目录后需添加父目录到 sys.path
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT
from _shared.file_utils import atomic_write  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from zephyr.governance.rule_patterns import MODULE_ID_RE  # noqa: E402  # SSoT 治本 2026-07-02 (ARCH-033 Phase 7)

# v2.0.0: 数据源改为 depgraph.nodes（真源），不再解析蓝图 §0.1
sys.path.insert(0, str(REPO_ROOT / "src"))
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402

PROJECT_ROOT = REPO_ROOT
MODULES_DIR = PROJECT_ROOT / "docs" / "03_modules"
OUTPUT_FILE = MODULES_DIR / "path_ownership_map.yaml"
BLUEPRINT_PATTERN = "**/blueprint.md"

# MODULE_ID_RE 已迁移到 zephyr.governance.rule_patterns（SSoT 治本 2026-07-02, ARCH-033 Phase 7）
ACTUAL_DISK_PATH_RE = re.compile(r"^actual_disk_path:\s*[\"']?(.+?)[\"']?\s*$", re.MULTILINE)
FILE_TABLE_ROW_RE = re.compile(
    r"\|\s*\d+\s*\|\s*`?([^`|\n]+)`?\s*\|\s*§[\d.]+\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|"
)
SECTION_01_MARKER = "### §0.1"
SECTION_02_MARKER = "### §0.2"
SSOT_CLAIMS_RE = re.compile(r"^ssot_claims:\s*$", re.MULTILINE)
SSOT_CLAIM_ENTRY_RE = re.compile(
    r"-\s*claim:\s*['\"]?([^'\"]+)['\"]?\s*\n\s*scope:\s*['\"]?([^'\"]+)['\"]?",
    re.MULTILINE,
)

logger = logging.getLogger(__name__)


def extract_module_id(text: str) -> str | None:
    m = MODULE_ID_RE.search(text)
    return m.group(1).strip() if m else None


def extract_actual_disk_path(text: str) -> str:
    m = ACTUAL_DISK_PATH_RE.search(text)
    if not m:
        return ""
    raw = m.group(1).strip().strip("\"'")
    parts = [
        p.strip() for p in raw.replace("+", ",").split(",") if p.strip() and not p.strip().startswith(("D:", "C:", "/"))
    ]
    return parts[0] if parts else ""


def extract_section_01_files(text: str) -> list[dict]:
    pos = text.find(SECTION_01_MARKER)
    if pos < 0:
        return []
    chunk = text[pos:]
    next_section = len(chunk)
    for marker in ["### §0.2", "### §0.3", "## §1", "### §1"]:
        idx = chunk.find(marker, 10)
        if idx > 0 and idx < next_section:
            next_section = idx
    chunk = chunk[:next_section]

    files: list[dict] = []
    for line in chunk.splitlines():
        m = FILE_TABLE_ROW_RE.search(line)
        if not m:
            continue
        file_path = m.group(1).strip().strip("`")
        responsibility = m.group(2).strip()
        existence = m.group(3).strip()
        ownership = m.group(4).strip()
        if not file_path or file_path.startswith("{"):
            continue
        files.append(
            {
                "path": file_path,
                "responsibility": responsibility,
                "existence": existence,
                "ownership": ownership,
            }
        )
    return files


def extract_ssot_claims(text: str) -> list[dict]:
    claims: list[dict] = []
    for m in SSOT_CLAIM_ENTRY_RE.finditer(text):
        claims.append({"claim": m.group(1).strip(), "scope": m.group(2).strip()})
    return claims


SQL_SELECT_FILE_NODES = (
    "SELECT blueprint_id, path, build_status FROM nodes "
    "WHERE granularity = 'file' "
    "AND path IS NOT NULL AND path <> '' "
    "AND blueprint_id IS NOT NULL AND blueprint_id <> ''"
)


def _query_depgraph_files() -> list[dict]:
    """v2.0.0: 从 depgraph.nodes 查询所有文件级节点（真源）。

    返回: [{blueprint_id, path, build_status}, ...]
    """
    conn = get_depgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(SQL_SELECT_FILE_NODES)
            rows = cur.fetchall()
    finally:
        conn.close()

    files = []
    for row in rows:
        bp = row[0] if not isinstance(row, dict) else row.get("blueprint_id", "")
        path = row[1] if not isinstance(row, dict) else row.get("path", "")
        bs = row[2] if not isinstance(row, dict) else row.get("build_status", "")
        if bp and path:
            files.append({"blueprint_id": bp, "path": path, "build_status": bs})
    return files


def scan_blueprints() -> tuple[list[dict], list[dict]]:
    """v2.0.0: 数据源改为 depgraph.nodes（真源），不再解析蓝图 §0.1。

    文件路径来自 depgraph.nodes（生成器自动维护），
    ssot_claims 仍然从蓝图 frontmatter 提取（蓝图独有信息）。
    """
    # 1. 从蓝图提取 module_id → declared_in 映射 + ssot_claims
    blueprint_map: dict[str, str] = {}  # module_id → 蓝图相对路径
    all_claims: list[dict] = []

    for bp in sorted(MODULES_DIR.glob(BLUEPRINT_PATTERN)):
        text = bp.read_text(encoding="utf-8", errors="replace")
        mod_id = extract_module_id(text)
        if not mod_id:
            continue

        relative_bp = str(bp.relative_to(PROJECT_ROOT)).replace("\\", "/")
        blueprint_map[mod_id] = relative_bp

        claims = extract_ssot_claims(text)
        for c in claims:
            all_claims.append(
                {
                    "claim": c["claim"],
                    "scope": c["scope"],
                    "owner_blueprint": mod_id,
                    "declared_in": relative_bp,
                }
            )

    # 2. 从 depgraph.nodes 查询文件路径（真源）
    dg_files = _query_depgraph_files()

    # 3. 生成 ownership_entries
    ownership_entries: list[dict] = []
    for f in dg_files:
        mod_id = f["blueprint_id"]
        path = f["path"]
        bs = f.get("build_status", "")
        # build_status → existence 映射
        if bs == "production":
            existence = "已实现"
        elif bs in ("design", "planned"):
            existence = "未实现"
        else:
            existence = bs or "unknown"

        declared_in = blueprint_map.get(mod_id, "")

        ownership_entries.append(
            {
                "path": path,
                "owner_blueprint": mod_id,
                "claim_type": "depgraph_node",  # v2.0.0: 数据源标记改为 depgraph
                "declared_in": declared_in,
                "existence": existence,
                "ownership_judgment": "本模块",
            }
        )

    return ownership_entries, all_claims


def detect_conflicts(entries: list[dict]) -> list[dict]:
    path_map: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        path_map[e["path"]].append(e)

    conflicts: list[dict] = []
    for path, claimants in path_map.items():
        if len(claimants) > 1:
            owners = set(c["owner_blueprint"] for c in claimants)
            if len(owners) > 1:
                conflicts.append(
                    {
                        "path": path,
                        "claimants": [
                            {
                                "blueprint": c["owner_blueprint"],
                                "claim_type": c["claim_type"],
                                "declared_in": c["declared_in"],
                            }
                            for c in claimants
                        ],
                        "resolution": "ssot_claims_priority",
                    }
                )
    return conflicts


def generate_yaml() -> str:
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries, ssot_claims = scan_blueprints()
    conflicts = detect_conflicts(entries)

    header = (
        "# ============================================================================\n"
        "# ZephyrAlpha 路径归属声明 — 自动生成，禁止手写\n"
        "# 生成工具: scripts/governance/generators/generate_path_ownership_map.py\n"
        "# 用途: 每个路径归哪个蓝图管——路径冲突检测的 SSoT\n"
        "# 冲突裁决: ssot_claims 声明优先于 §0.1 清单声明\n"
        "# ============================================================================\n\n"
    )

    meta_lines = [
        "meta:",
        f"  generated_at: '{now}'",
        "  auto_generated_by: 'scripts/governance/generators/generate_path_ownership_map.py'",
        f"  total_path_claims: {len(entries)}",
        f"  total_ssot_claims: {len(ssot_claims)}",
        f"  total_conflicts: {len(conflicts)}",
        "  conflict_resolution: 'ssot_claims_priority'",
        "",
    ]

    ownership_lines = ["ownership:"]
    for e in entries:
        ownership_lines.append(f"  - path: '{e['path']}'")
        ownership_lines.append(f"    owner_blueprint: '{e['owner_blueprint']}'")
        ownership_lines.append(f"    claim_type: '{e['claim_type']}'")
        ownership_lines.append(f"    declared_in: '{e['declared_in']}'")
        ownership_lines.append(f"    existence: '{e['existence']}'")
        ownership_lines.append(f"    ownership_judgment: '{e['ownership_judgment']}'")
        ownership_lines.append("")

    ssot_lines = ["ssot_claims:"]
    for c in ssot_claims:
        ssot_lines.append(f"  - claim: '{c['claim']}'")
        ssot_lines.append(f"    scope: '{c['scope']}'")
        ssot_lines.append(f"    owner_blueprint: '{c['owner_blueprint']}'")
        ssot_lines.append(f"    declared_in: '{c['declared_in']}'")
        ssot_lines.append("")

    conflict_lines = ["conflicts:"]
    if conflicts:
        for c in conflicts:
            conflict_lines.append(f"  - path: '{c['path']}'")
            for claimant in c["claimants"]:
                conflict_lines.append("    claimant:")
                conflict_lines.append(f"      blueprint: '{claimant['blueprint']}'")
                conflict_lines.append(f"      claim_type: '{claimant['claim_type']}'")
                conflict_lines.append(f"      declared_in: '{claimant['declared_in']}'")
            conflict_lines.append(f"    resolution: '{c['resolution']}'")
            conflict_lines.append("")
    else:
        conflict_lines.append("  []")
        conflict_lines.append("")

    return (
        header + "\n".join(meta_lines) + "\n".join(ownership_lines) + "\n".join(ssot_lines) + "\n".join(conflict_lines)
    )


def cmd_write() -> None:
    content = generate_yaml()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(OUTPUT_FILE, content)
    print(f"[OK] Written to {OUTPUT_FILE}")


def cmd_check() -> None:
    if not OUTPUT_FILE.exists():
        print("[FAIL] path_ownership_map.yaml does not exist. Run with --write first.")
        sys.exit(1)
    generated = generate_yaml()
    current = OUTPUT_FILE.read_text(encoding="utf-8")
    gen_stripped = re.sub(r"generated_at: '[^']*'", "generated_at: ''", generated)
    cur_stripped = re.sub(r"generated_at: '[^']*'", "generated_at: ''", current)
    if cur_stripped.strip() != gen_stripped.strip():
        print("[FAIL] path_ownership_map.yaml is OUT OF SYNC with blueprints.")
        print("       Run: python scripts/governance/generators/generate_path_ownership_map.py --write")
        sys.exit(1)
    else:
        print("[OK] path_ownership_map.yaml is in sync with blueprints.")


def cmd_conflicts() -> None:
    entries, _ = scan_blueprints()
    conflicts = detect_conflicts(entries)
    if not conflicts:
        print("[OK] No path ownership conflicts detected.")
        return
    print(f"[CONFLICT] {len(conflicts)} path ownership conflict(s) detected:")
    for c in conflicts:
        print(f"  Path: {c['path']}")
        for claimant in c["claimants"]:
            print(f"    Claimed by: {claimant['blueprint']} ({claimant['claim_type']}) in {claimant['declared_in']}")
        print(f"    Resolution: {c['resolution']}")
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate path-ownership-map.yaml")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="Overwrite registry file")
    group.add_argument("--check", action="store_true", help="CI mode: exit 1 if mismatch")
    group.add_argument("--conflicts", action="store_true", help="Only output conflicts")
    args = parser.parse_args()

    if args.check:
        cmd_check()
    elif args.write:
        cmd_write()
    elif args.conflicts:
        cmd_conflicts()
    else:
        print(generate_yaml())


if __name__ == "__main__":
    main()
