# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_adr_frontmatter_consistency.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_adr_frontmatter_consistency
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.validators.__init__
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
#!/usr/bin/env python3
"""validate_adr_frontmatter_consistency.py — ADR frontmatter 一致性闸门（GATE-ADR-FM）
v1.0.0 — 2026-05-03



根因（R6 审计 P1-11/P1-12/P2-11/P2-12）：ADR 分三批次产出（早期 0001~0013、
中期 0014~0022、晚期 0030~0041），三批使用不同 frontmatter 字段集，Stage F
归一化仅处理了文件名/编号/module_id 前缀，未统一 frontmatter schema。

本闸门：扫描所有 ADR 文件的 frontmatter，检测：
  DIM-1: index.md 登记表状态 vs ADR frontmatter status 不一致
  DIM-2: summary 字段为空或缺失
  DIM-3: 取代关系双向完整性（superseded_by ↔ supersedes）
  DIM-4: ADR §1 状态节 vs frontmatter status 不一致
  DIM-5: 必填字段缺失检测

对标：adr-tools `adr link` 双向链接校验 / log4brains ADR lifecycle validation

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ADR frontmatter 一致性校验（ADR 文档 frontmatter 字段与规范对齐）
dimensions:
- D3
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter

ensure_utf8_stdout()

ADR_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "adr"
REQUIRED_FIELDS = ["module_id", "title", "doc_type", "status", "version", "layer", "owner", "summary"]


def extract_index_statuses(index_content: str) -> dict[str, str]:
    """提取索引状态."""
    result = {}
    """提取数据."""
    for line in index_content.split("\n"):
        cols = [c.strip() for c in line.split("|")]
        if len(cols) < 5:
            continue
        m = re.search(r"ADR-(\d+)", cols[1])
        if m:
            num = m.group(1)
            status = cols[3].strip().strip("*")
            result[f"ADR-{num}"] = status
    return result
    """extract index statuses."""


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true", help="warn mode: exit 0 even if findings")
    args = parser.parse_args()

    print("=" * 72)
    print("GATE-ADR-FM: ADR frontmatter 一致性闸门 v1.0.0")
    print("=" * 72)

    index_path = ADR_DIR / "index.md"
    if not index_path.exists():
        print("🔴 index.md 不存在")
        return EXIT_ERROR
    index_statuses = extract_index_statuses(index_path.read_text(encoding="utf-8"))

    adr_files = sorted(ADR_DIR.glob("adr-*.md"))
    adr_data = {}

    findings = []

    for fpath in adr_files:
        content = fpath.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        adr_id = fm.get("module_id", fpath.stem.upper())
        adr_data[adr_id] = {"fm": fm, "file": fpath.name, "content": content}

    # DIM-1: index.md vs frontmatter status
    print("\n  DIM-1: index.md 状态 vs frontmatter status ...")
    for adr_id, status in index_statuses.items():
        if adr_id not in adr_data:
            continue
        fm_status = adr_data[adr_id]["fm"].get("status", "?")
        if status.lower() not in (fm_status.lower(), f"**{fm_status.lower()}**"):
            if not (status == "accepted" and fm_status == "active") and not (
                status == "partially_superseded" and fm_status == "partially_superseded"
            ):
                findings.append(
                    {
                        "dim": 1,
                        "adr": adr_id,
                        "msg": f"index.md='{status}' vs frontmatter='{fm_status}'",
                    }
                )

    # DIM-2: summary empty
    print("  DIM-2: summary 字段空检测 ...")
    for adr_id, info in adr_data.items():
        summary = info["fm"].get("summary", None)
        if summary is None or summary == "" or summary == "''":
            findings.append(
                {
                    "dim": 2,
                    "adr": adr_id,
                    "msg": "summary 为空",
                }
            )

    # DIM-3: superseded_by ↔ supersedes bidirectional
    print("  DIM-3: 取代关系双向完整性 ...")
    for adr_id, info in adr_data.items():
        superseded_by = info["fm"].get("superseded_by")
        if superseded_by and isinstance(superseded_by, str) and superseded_by.startswith("ADR-"):
            target_id = superseded_by.split("（")[0].strip()
            if target_id in adr_data:
                target_supersedes = adr_data[target_id]["fm"].get("supersedes")
                if not target_supersedes or adr_id not in str(target_supersedes):
                    findings.append(
                        {
                            "dim": 3,
                            "adr": adr_id,
                            "msg": f"superseded_by={target_id} 但 {target_id}.supersedes 未反向引用 {adr_id}",
                        }
                    )

    # DIM-4: §1 status vs frontmatter
    print("  DIM-4: §1 状态节 vs frontmatter ...")
    for adr_id, info in adr_data.items():
        fm_status = info["fm"].get("status", "?")
        m = re.search(r"当前状态[：:]\s*`(\w+)`", info["content"])
        if m:
            body_status = m.group(1)
            if body_status != fm_status and not (body_status == "accepted" and fm_status == "active"):
                findings.append(
                    {
                        "dim": 4,
                        "adr": adr_id,
                        "msg": f"§1 status='{body_status}' vs frontmatter='{fm_status}'",
                    }
                )

    # DIM-5: required fields
    print("  DIM-5: 必填字段缺失 ...")
    for adr_id, info in adr_data.items():
        missing = [f for f in REQUIRED_FIELDS if f not in info["fm"] or info["fm"][f] is None]
        if missing:
            findings.append(
                {
                    "dim": 5,
                    "adr": adr_id,
                    "msg": f"缺失字段: {', '.join(missing)}",
                }
            )

    if not findings:
        print("\n✅ 所有 ADR frontmatter 一致——零问题")
        return EXIT_PASS
    print(f"\n🟡 发现 {len(findings)} 个 ADR frontmatter 问题：\n")
    for f in findings:
        print(f"  DIM-{f['dim']} {f['adr']}: {f['msg']}")

    return EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
