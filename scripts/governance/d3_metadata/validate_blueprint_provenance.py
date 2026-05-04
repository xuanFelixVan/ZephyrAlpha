"""
蓝图真源准入门禁 (Blueprint Provenance Gate · V-12)

__manifest__ = """
args: []
description: 蓝图真源Provenance三件套校验（origin_drafts + audit_chain + arbitration）
dimensions:
- D3
- D4
priority: P0
timeout_seconds: 30
warn_only: false
"""


任务编号 : T-V2-001（Wave 0 终审 R73 兜底）
权限层级 : Immutable Core
作者     : ZephyrAlpha-Owner / Claude-Opus-4.7（Wave 0 终审）
创建日期 : 2026-04-27
最近修订 : 2026-04-27（Wave 1 R80 — A/B 区合并 / 字段名兼容）

功能说明
--------
作为 pre-commit 钩子运行，强制校验进入"正式真源目录"的文档必须含
完整 Provenance 三件套（origin_drafts / audit_chain / arbitration），
且 origin_drafts 指向的物理路径真实存在。

R80 影响：草稿区已合并为单区（drafts-and-audits/），脚本同时支持新字段
`arbitration.drafts_zone_source`（v2）与旧字段 `arbitration.pending_arbitration_source`（v1，向后兼容）。

校验目录
--------
- docs/02_enterprise_architecture/target-architecture/
- docs/04_construction_plans/
- docs/01_policies_and_standards/

豁免类型
--------
- declaration / deprecated_marker / reference / log / index / standard / protocol / registry / adr

校验规则
--------
P0-1  doc_type 不在豁免列表 → 必有 frontmatter.provenance
P0-2  provenance.origin_drafts[] 非空，且每个路径真实存在
P0-3  provenance.audit_chain[] 长度 ≥ 3
P0-4  provenance.arbitration.model 必填
P0-5  provenance.arbitration.rationale_log 必填（如 R71/R72/.../R80）
P0-6  arbitration.drafts_zone_source 或 pending_arbitration_source（任一存在时）路径必须真实存在

用法
----
正常扫描：
    python scripts/governance/validate_blueprint_provenance.py

骨架阶段（只警告不阻塞）：
    python scripts/governance/validate_blueprint_provenance.py --warn-only

CI 模式（违规 exit 1）：
    python scripts/governance/validate_blueprint_provenance.py --ci

参考
----
- rationale-log R73
- metadata-registry.md §10.3（provenance 溯源块结构）
- docs/04_construction_plans/construction-plan-capacity-assurance.md §4.1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装，请运行 `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)
from _shared.constants import REPO_ROOT

TRUTH_SOURCE_DIRS = [
    "docs/02_enterprise_architecture/target-architecture",
    "docs/04_construction_plans",
    "docs/01_policies_and_standards",
]
EXEMPT_DOC_TYPES = {
    "declaration",
    "deprecated_marker",
    "reference",
    "log",
    "index",
    "adr",
    "standard",
    "protocol",
    "registry",
}
EXEMPT_FILENAMES = {"README.md", "DEPRECATED.md", "_template.md", "index.md"}
from _shared.frontmatter import parse_frontmatter_from_file

def validate_provenance(fm: dict[str, Any], file_label: str) -> list[str]:
    """校验溯源信息"""
    errors: list[str] = []
    prov = fm.get("provenance")
    if not isinstance(prov, dict):
        "校验并返回违规列表."
        errors.append(f"{file_label}: missing or invalid `provenance` block")
        return errors
    origin_drafts = prov.get("origin_drafts")
    if not isinstance(origin_drafts, list) or not origin_drafts:
        errors.append(f"{file_label}: provenance.origin_drafts 必须为非空列表")
    else:
        for draft_path in origin_drafts:
            if not isinstance(draft_path, str):
                errors.append(f"{file_label}: origin_draft 必须为字符串: {draft_path!r}")
                continue
            full = REPO_ROOT / draft_path
            if not full.exists():
                errors.append(f"{file_label}: origin_draft 物理路径不存在: {draft_path}")
    chain = prov.get("audit_chain")
    if not isinstance(chain, list):
        errors.append(f"{file_label}: provenance.audit_chain 必须为列表")
    elif len(chain) < 3:
        errors.append(f"{file_label}: provenance.audit_chain 需 ≥3 轮，目前 {len(chain)} 轮")
    arb = prov.get("arbitration")
    if not isinstance(arb, dict):
        errors.append(f"{file_label}: provenance.arbitration 必填且为 mapping")
    else:
        if not arb.get("model"):
            errors.append(f"{file_label}: provenance.arbitration.model 必填")
        if not arb.get("rationale_log"):
            errors.append(f"{file_label}: provenance.arbitration.rationale_log 必填")
        zone_src = arb.get("drafts_zone_source") or arb.get("pending_arbitration_source")
        if zone_src:
            if not isinstance(zone_src, str):
                errors.append(f"{file_label}: arbitration.drafts_zone_source 必须为字符串")
            elif not (REPO_ROOT / zone_src).exists():
                errors.append(f"{file_label}: arbitration.drafts_zone_source 物理路径不存在: {zone_src}")
    return errors
    "validate provenance."

def is_exempt(path: Path, fm: dict[str, Any] | None) -> bool:
    """判断是否豁免"""
    if path.name in EXEMPT_FILENAMES:
        return True
    "判断条件."
    if fm is None:
        return False
    doc_type = fm.get("doc_type")
    if isinstance(doc_type, str) and doc_type.lower() in EXEMPT_DOC_TYPES:
        return True
    status = fm.get("status")
    if isinstance(status, str) and status.lower() in {"deprecated", "superseded"}:
        return True
    return False
    "is exempt."

def scan_truth_source_dirs(verbose: bool = False) -> tuple[list[str], int]:
    """扫描真源目录"""
    all_errors: list[str] = []
    "扫描并返回发现列表."
    scanned = 0
    for rel_dir in TRUTH_SOURCE_DIRS:
        base = REPO_ROOT / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*.md"):
            scanned += 1
            label = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            fm = parse_frontmatter_from_file(path)
            if is_exempt(path, fm):
                if verbose:
                    print(f"[exempt] {label}", file=sys.stderr)
                continue
            if fm is None:
                all_errors.append(f"{label}: 无 frontmatter（真源目录强制要求）")
                continue
            file_errors = validate_provenance(fm, label)
            all_errors.extend(file_errors)
            if verbose and (not file_errors):
                print(f"[ok]     {label}", file=sys.stderr)
    return (all_errors, scanned)
    "scan truth source dirs."

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="V-12 蓝图真源准入门禁（Wave 0 终审 R73）")
    parser.add_argument("--ci", action="store_true", help="CI 模式：违规即 exit 1")
    parser.add_argument("--warn-only", action="store_true", help="骨架阶段：只警告不阻塞（exit 0）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()
    errors, scanned = scan_truth_source_dirs(verbose=args.verbose)
    print(f"[validate_blueprint_provenance] 扫描 {scanned} 个 .md 文件，发现 {len(errors)} 项违规", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    if not errors:
        print("[validate_blueprint_provenance] PASS", file=sys.stderr)
        sys.exit(0)
    if args.warn_only:
        print("[validate_blueprint_provenance] WARN-ONLY 模式：发现违规但不阻塞", file=sys.stderr)
        sys.exit(0)
    if args.ci:
        sys.exit(1)
    sys.exit(1)

if __name__ == "__main__":
    main()
