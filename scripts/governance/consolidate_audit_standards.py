#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性将 docs/09_AUDIT/STANDARDS 自 34 份合并为 20 份（保留执行记录，不重复运行）。
"""
from __future__ import annotations

import io
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]
STD = REPO / "docs" / "09_AUDIT" / "STANDARDS"


def strip_frontmatter(md: str) -> str:
    t = md.lstrip("\ufeff")
    if not t.startswith("---"):
        return md
    end = t.find("\n---", 3)
    if end == -1:
        return md
    return t[end + 4 :].lstrip()


def merge_two(path_a: Path, path_b: Path, title_b: str) -> str:
    a = path_a.read_text(encoding="utf-8", errors="replace")
    b = path_b.read_text(encoding="utf-8", errors="replace")
    body_a = a.rstrip()
    sep = f"\n\n---\n\n## （合并）{title_b}\n\n"
    return body_a + sep + strip_frontmatter(b).strip() + "\n"


def merge_three(path_a: Path, path_b: Path, path_c: Path, titles: tuple[str, str]) -> str:
    base = path_a.read_text(encoding="utf-8", errors="replace").rstrip()
    b = strip_frontmatter(path_b.read_text(encoding="utf-8", errors="replace")).strip()
    c = strip_frontmatter(path_c.read_text(encoding="utf-8", errors="replace")).strip()
    return (
        base
        + f"\n\n---\n\n## （合并）{titles[0]}\n\n"
        + b
        + f"\n\n---\n\n## （合并）{titles[1]}\n\n"
        + c
        + "\n"
    )


def merge_four(
    path_a: Path,
    path_b: Path,
    path_c: Path,
    path_d: Path,
    titles: tuple[str, str, str],
) -> str:
    base = path_a.read_text(encoding="utf-8", errors="replace").rstrip()
    b = strip_frontmatter(path_b.read_text(encoding="utf-8", errors="replace")).strip()
    c = strip_frontmatter(path_c.read_text(encoding="utf-8", errors="replace")).strip()
    d = strip_frontmatter(path_d.read_text(encoding="utf-8", errors="replace")).strip()
    return (
        base
        + f"\n\n---\n\n## （合并）{titles[0]}\n\n"
        + b
        + f"\n\n---\n\n## （合并）{titles[1]}\n\n"
        + c
        + f"\n\n---\n\n## （合并）{titles[2]}\n\n"
        + d
        + "\n"
    )


def main() -> int:
    if not STD.is_dir():
        print("STANDARDS 目录不存在", file=sys.stderr)
        return 1

    # 1) continuous-improvement-process + continuous-quality-improvement-process
    p = STD / "continuous-improvement-process.md"
    merged = merge_two(p, STD / "continuous-quality-improvement-process.md", "持续质量改进流程（原 continuous-quality-improvement-process）")
    p.write_text(merged, encoding="utf-8")
    (STD / "continuous-quality-improvement-process.md").unlink(missing_ok=True)

    # 2) doc-governance-mechanism + optimization + system plan + process standard
    mech = STD / "doc-governance-mechanism.md"
    merged = merge_four(
        mech,
        STD / "doc-governance-optimization-proposal.md",
        STD / "doc-governance-system-plan.md",
        STD / "document-governance-process-standard.md",
        (
            "文档治理优化提案（原 doc-governance-optimization-proposal）",
            "文档治理系统计划（原 doc-governance-system-plan）",
            "文档治理流程标准（原 document-governance-process-standard）",
        ),
    )
    mech.write_text(merged, encoding="utf-8")
    for n in (
        "doc-governance-optimization-proposal.md",
        "doc-governance-system-plan.md",
        "document-governance-process-standard.md",
    ):
        (STD / n).unlink(missing_ok=True)

    # 3) periodic-audit + periodic-check
    pa = STD / "periodic-audit-mechanism.md"
    pa.write_text(
        merge_two(pa, STD / "periodic-check-plan.md", "周期性检查计划（原 periodic-check-plan）"),
        encoding="utf-8",
    )
    (STD / "periodic-check-plan.md").unlink(missing_ok=True)

    # 4) quality + doc-quality-culture-plan
    qs = STD / "quality-standard.md"
    qs.write_text(merge_two(qs, STD / "doc-quality-culture-plan.md", "文档质量文化计划（原 doc-quality-culture-plan）"), encoding="utf-8")
    (STD / "doc-quality-culture-plan.md").unlink(missing_ok=True)

    # 5) NEW testing-and-defect-prevention-standard
    td = STD / "test_driven_governance_standard.md"
    dd = STD / "document-defect-prevention-standard.md"
    out = STD / "testing-and-defect-prevention-standard.md"
    combined = (
        "---\n"
        "module_id: TESTING_AND_DEFECT_PREVENTION_STANDARD\n"
        "version: 1.0.0\n"
        "status: Active\n"
        "last_updated: '2026-04-16'\n"
        "owner: Project Owner\n"
        "layer: layer_09\n"
        "standard_type: 合并标准\n"
        "applicable_scope: 测试驱动治理 + 文档缺陷预防\n"
        "---\n\n"
        "# 测试与缺陷预防合并标准\n\n"
        "> 由原 `test_driven_governance_standard.md` 与 `document-defect-prevention-standard.md` 合并。\n\n"
        "## 第一部分：测试驱动治理\n\n"
        + strip_frontmatter(td.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n\n---\n\n## 第二部分：文档缺陷预防\n\n"
        + strip_frontmatter(dd.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n"
    )
    out.write_text(combined, encoding="utf-8")
    td.unlink(missing_ok=True)
    dd.unlink(missing_ok=True)

    # 6) NEW orphan-duplicate
    dup = STD / "duplicate-document-handling-standard.md"
    orb = STD / "doc-orphan-and-duplicate-governance-playbook.md"
    out2 = STD / "orphan-duplicate-and-overlap-governance-standard.md"
    out2.write_text(
        "---\n"
        "module_id: ORPHAN_DUPLICATE_OVERLAP_GOVERNANCE_STANDARD\n"
        "version: 1.0.0\n"
        "status: Active\n"
        "last_updated: '2026-04-16'\n"
        "owner: Project Owner\n"
        "layer: layer_09\n"
        "standard_type: 合并标准\n"
        "---\n\n"
        "# 孤儿、重复与重叠治理合并标准\n\n"
        "## 第一部分：重复文档处理（canonical）\n\n"
        + strip_frontmatter(dup.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n\n---\n\n## 第二部分：孤儿与重复治理 Playbook\n\n"
        + strip_frontmatter(orb.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n",
        encoding="utf-8",
    )
    dup.unlink(missing_ok=True)
    orb.unlink(missing_ok=True)

    # 7) NEW audit-and-compliance-master
    au = STD / "audit-standards.md"
    co = STD / "compliance-audit-system.md"
    out3 = STD / "audit-and-compliance-master-standard.md"
    out3.write_text(
        "---\n"
        "module_id: AUDIT_AND_COMPLIANCE_MASTER_STANDARD\n"
        "version: 1.0.0\n"
        "status: Active\n"
        "last_updated: '2026-04-16'\n"
        "owner: Project Owner\n"
        "layer: layer_09\n"
        "standard_type: 合并标准\n"
        "---\n\n"
        "# 审计与合规合并标准\n\n"
        "## 第一部分：审计标准总纲\n\n"
        + strip_frontmatter(au.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n\n---\n\n## 第二部分：合规审计系统\n\n"
        + strip_frontmatter(co.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n",
        encoding="utf-8",
    )
    au.unlink(missing_ok=True)
    co.unlink(missing_ok=True)

    # 8) doc-naming + file-naming
    dn = STD / "doc-naming-standard.md"
    dn.write_text(merge_two(dn, STD / "file-naming-standard.md", "文件命名标准（原 file-naming-standard）"), encoding="utf-8")
    (STD / "file-naming-standard.md").unlink(missing_ok=True)

    # 9) NEW document-metadata-and-versioning
    mt = STD / "document-metadata-template.md"
    vn = STD / "document-version-naming-standard.md"
    out4 = STD / "document-metadata-and-versioning-standard.md"
    out4.write_text(
        "---\n"
        "module_id: DOCUMENT_METADATA_AND_VERSIONING_STANDARD\n"
        "version: 1.0.0\n"
        "status: Active\n"
        "last_updated: '2026-04-16'\n"
        "owner: Project Owner\n"
        "layer: layer_09\n"
        "standard_type: 合并标准\n"
        "---\n\n"
        "# 文档元数据与版本命名合并标准\n\n"
        "## 第一部分：元数据模板\n\n"
        + strip_frontmatter(mt.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n\n---\n\n## 第二部分：版本命名\n\n"
        + strip_frontmatter(vn.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n",
        encoding="utf-8",
    )
    mt.unlink(missing_ok=True)
    vn.unlink(missing_ok=True)

    # 10) NEW path-and-reference
    pr = STD / "path-reference-standard.md"
    dr = STD / "doc-reference-standard.md"
    out5 = STD / "path-and-reference-standard.md"
    out5.write_text(
        "---\n"
        "module_id: PATH_AND_REFERENCE_STANDARD\n"
        "version: 1.0.0\n"
        "status: Active\n"
        "last_updated: '2026-04-16'\n"
        "owner: Project Owner\n"
        "layer: layer_09\n"
        "standard_type: 合并标准\n"
        "---\n\n"
        "# 路径与引用合并标准\n\n"
        "## 第一部分：路径引用\n\n"
        + strip_frontmatter(pr.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n\n---\n\n## 第二部分：文档引用\n\n"
        + strip_frontmatter(dr.read_text(encoding="utf-8", errors="replace")).strip()
        + "\n",
        encoding="utf-8",
    )
    pr.unlink(missing_ok=True)
    dr.unlink(missing_ok=True)

    # 11) document-classification + exception list
    dc = STD / "document-classification-standard.md"
    dc.write_text(
        merge_two(dc, STD / "document-classification-exception-list.md", "分类例外清单（原 document-classification-exception-list）"),
        encoding="utf-8",
    )
    (STD / "document-classification-exception-list.md").unlink(missing_ok=True)

    # 12) delete v1 responsibility (refs updated separately)
    (STD / "responsibility-description-standard.md").unlink(missing_ok=True)

    print("✅ consolidate_audit_standards 完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
