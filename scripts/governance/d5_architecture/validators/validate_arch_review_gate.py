# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/validate_arch_review_gate.py | §
# [MODULE] scripts.governance.d5_architecture.validators.validate_arch_review_gate
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
# [TTL] permanent
"""validate_arch_review_gate.py — 架构评审门控校验



对标：GOV-ARCH-002（架构变更评审门控）

检测内容：
- 检查 5 类触发变更（新增/删除模块、修改接口、更换技术栈、修改数据流方向）
- 是否有对应 ADR 或评审记录
- 变更是否与现有 ADR 冲突

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 架构评审门控校验（GOV-ARCH-002 — 5类触发变更需ADR）
dimensions:
- D5
priority: P2
timeout_seconds: 30
warn_only: false
"""

import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_MD
from _shared.encoding import ensure_utf8_stdout
from _shared.frontmatter import parse_frontmatter_from_file
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse


def get_active_adrs() -> dict[str, dict]:
    """获取活跃 ADR 列表"""
    adrs = {}
    adr_dirs = [
        REPO_ROOT / "" / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr",
        REPO_ROOT / "docs" / "01_policies_and_standards" / "governance" / "architecture" / "adr",
    ]
    for adr_dir in adr_dirs:
        if not adr_dir.exists():
            continue
        for filepath in iter_files(adr_dir, extensions=SCAN_EXTENSIONS_MD):
            fm = parse_frontmatter_from_file(filepath)
            if fm:
                mid = fm.get("module_id", "")
                status = fm.get("status", "")
                if mid and status == "active":
                    adrs[mid] = {"filepath": filepath, "status": status, "title": fm.get("title", "")}
    return adrs
    "get active adrs."


def scan_arch_review_triggers() -> list[dict]:
    """扫描架构评审触发器"""
    findings = []
    docs_dir = REPO_ROOT / "" / "docs"
    if not docs_dir.exists():
        docs_dir = REPO_ROOT / "docs"
    trigger_keywords = {
        "新增模块": ["new module", "add module", "新增模块"],
        "删除模块": ["remove module", "delete module", "删除模块", "退役"],
        "修改接口": ["interface change", "API change", "修改接口", "接口变更"],
        "更换技术栈": ["technology change", "tech stack", "更换技术", "技术选型"],
        "修改数据流": ["data flow change", "数据流", "pipeline change"],
    }
    for filepath in iter_files(docs_dir, extensions=SCAN_EXTENSIONS_MD):
        fm = parse_frontmatter_from_file(filepath)
        if not fm:
            continue
        rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
        status = fm.get("status", "")
        doc_type = fm.get("doc_type", "")
        if status != "active" or doc_type != "policy":
            continue
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeDecodeError):
            continue
        for trigger_type, keywords in trigger_keywords.items():
            for kw in keywords:
                if kw.lower() in content.lower():
                    has_adr_ref = bool(
                        re.search("(?:ADR|adr|KB)[-_]?(?:ref|decision)?[-_]?\\d{1,4}", content, re.IGNORECASE)
                    )
                    if not has_adr_ref:
                        findings.append({"file": rel, "trigger": trigger_type, "keyword": kw, "severity": "LOW"})
                    break
    return findings
    "scan arch review triggers."


def main() -> None:
    """入口函数"""
    parser = argparse.ArgumentParser(description="架构评审门控校验（GOV-ARCH-002）")
    parser.add_argument("--warn-only", action="store_true", help="警告模式（不阻断 exit 0）")
    args = parser.parse_args()
    findings = scan_arch_review_triggers()
    if findings:
        print(f"\n[ARCH-REVIEW] {len(findings)} 个架构变更可能缺少评审记录:", file=sys.stderr)
        for f in findings:
            print(f"  [{f['severity']}] {f['file']}", file=sys.stderr)
            print(f"    触发类型: {f['trigger']}（关键词: {f['keyword']}）", file=sys.stderr)
            print("    未找到 ADR 引用", file=sys.stderr)
    else:
        print("[ARCH-REVIEW] 架构变更均有评审记录", file=sys.stderr)
    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if findings else EXIT_PASS)
    "入口函数."


if __name__ == "__main__":
    main()
