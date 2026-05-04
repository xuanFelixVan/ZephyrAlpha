#!/usr/bin/env python3
"""
GATE-15: Frontmatter 元数据校验

SSoT 架构（v2.1.0）：
  校验器自身不再硬编码合法值——所有合法值从 YAML 词汇表文件动态加载。
  词汇表 = 唯一的真源，校验器 = 纯执行层。
  新增/删除合法值只需修改词汇表 YAML，校验器自动同步，零漂移风险。

  词汇表路径（绝对路径）：
    status   → docs/01_policies_and_standards/_registry/vocabularies/status-vocabulary.yaml
    doc_type → docs/01_policies_and_standards/_registry/vocabularies/doc_type-vocabulary.yaml
    ttl      → docs/01_policies_and_standards/_registry/vocabularies/ttl-vocabulary.yaml

  fallback 硬编码（防御纵深安全网）：
    当词汇表 YAML 文件缺失/损坏时，校验器使用最小合法值集合作为降级安全网。
    这不是 SSoT 违规——这是灾难恢复机制：宁可拒绝边缘值，也不静默放行一切。
    对标：K8s ValidatingWebhook failurePolicy=Fail → API Server 不可用时拒绝而非放行。

用法：
  python check_frontmatter_metadata.py [--warn-only] [--staged]
"""

import argparse
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from typing import Any

import yaml as _yaml_lib
from _shared.constants import REPO_ROOT

def _load_vocabulary_values(yaml_path: Path) -> set[str]:
    """从词汇表 YAML 加载当前活跃（非 deprecated）的合法值集合。

    对标：Kubernetes Admission Controller —— 准入规则从 API 资源定义推导，不硬编码。
    大白话：校验器不再自己"记住"哪些值合法，而是每次运行时去问词汇表文件。
           改词汇表 = 改校验行为，零代码修改。

    Returns:
        活跃的合法值集合（小写）。加载失败返回空集。
    """
    if not yaml_path.exists():
        return set()
    try:
        data = _yaml_lib.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return set()
    if not isinstance(data, dict):
        return set()
    values = data.get("values", [])
    if not isinstance(values, list):
        return set()
    deprecated = {str(d.get("value", "")).strip() for d in data.get("deprecated_values", []) if isinstance(d, dict)}
    active = set()
    for v in values:
        if not isinstance(v, dict):
            continue
        val = str(v.get("value", "")).strip().lower()
        if val and v.get("value", "").strip() not in deprecated:
            active.add(val)
    return active

_VOCAB_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"

STATUS_LEGAL_LOWER = _load_vocabulary_values(_VOCAB_DIR / "status-vocabulary.yaml")
if not STATUS_LEGAL_LOWER:
    STATUS_LEGAL_LOWER = {"draft", "active", "deprecated"}

STATUS_LEGAL_TITLE = {v.title() for v in STATUS_LEGAL_LOWER}

DOC_TYPE_LEGAL = _load_vocabulary_values(_VOCAB_DIR / "doc_type-vocabulary.yaml")
if not DOC_TYPE_LEGAL:
    DOC_TYPE_LEGAL = {"policy", "standard", "register", "index", "blueprint"}

TTL_LEGAL = _load_vocabulary_values(_VOCAB_DIR / "ttl-vocabulary.yaml")
if not TTL_LEGAL:
    TTL_LEGAL = {"permanent", "30d", "7d", "session", "periodic_review_90d"}

CREATED_BY_LEGAL = {"human", "agent", "human_plus_agent"}

AI_AUTONOMY_LEGAL = {"immutable_core", "human_gated", "ai_modifiable"}

SAFETY_LEVEL_LEGAL = {"H", "M", "L"}

EVOLUTION_POLICY_LEGAL = {"frozen", "extendable", "rewritable"}

GOVERNANCE_FAMILY_LEGAL = {"A", "B", "C", "D"}

AI_CAPABILITY_SLOT_LEGAL = {"planned", "reserved", "active", "none"}

CATEGORY_LEGAL = {
    "blueprint_decision",
    "strategy",
    "factor",
    "best_practice",
    "lesson_learned",
    "architecture",
    "risk_control",
    "data_governance",
    "operations",
    "compliance",
}

DOMAIN_LEGAL = {
    "data",
    "feature",
    "model",
    "signal",
    "execution",
    "risk",
    "portfolio",
    "reporting",
    "infrastructure",
    "other",
}

REVIEW_STATUS_LEGAL = {"unreviewed", "reviewed", "approved", "rejected"}

MODULE_ID_PATTERN = re.compile(
    r"^(ADR-\d{4}|DOM-L\d{2}-(\d{3}|IDX)|L\d{2}-[A-Z]{2,5}-\d{3}|[A-Z]{2,5}-[A-Z]{2,5}-\d{3}|[A-Z]{2,5}-[A-Z]{2,5}-[A-Z]{2,5}-\d{3}|TEMPLATE-[A-Z]+-\d{3}|DW-[A-Z]+-TEMPLATE)$"
)

DRAFT_REQUIRED = {"module_id", "title", "doc_type", "status", "version", "date", "owner"}
ACTIVE_REQUIRED = DRAFT_REQUIRED | {"layer", "classification", "language", "created_by", "ttl", "summary", "tags"}
ACCEPTED_REQUIRED = ACTIVE_REQUIRED | {"valid_from"}

INDEX_MINIMAL_REQUIRED = {"doc_type", "status"}

DOC_TYPE_PATH_RULES = {
    "policy": {"allowed": ["01_policies_and_standards/"], "forbidden": ["03_blueprints/", "08_knowledge/"]},
    "standard": {"allowed": ["01_policies_and_standards/", "08_knowledge/"], "forbidden": ["03_blueprints/"]},
    "adr": {"allowed": ["02_enterprise_architecture/adr/"], "forbidden": []},
    "blueprint": {"allowed": ["03_blueprints/"], "forbidden": ["01_policies_and_standards/", "04_construction_plans/"]},
    "construction_plan": {
        "allowed": ["04_construction_plans/"],
        "forbidden": ["01_policies_and_standards/", "03_blueprints/"],
    },
    "design": {
        "allowed": ["02_enterprise_architecture/"],
        "forbidden": ["01_policies_and_standards/", "03_blueprints/", "04_construction_plans/"],
    },
    "plan": {"allowed": ["19_development_workspace/"], "forbidden": ["01_policies_and_standards/"]},
    "roadmap": {"allowed": ["19_development_workspace/"], "forbidden": ["01_policies_and_standards/"]},
    "ai_governance": {"allowed": ["01_policies_and_standards/governance/ai/"], "forbidden": []},
    "knowledge_entry": {"allowed": ["08_knowledge/"], "forbidden": ["01_policies_and_standards/"]},
    "audit_report": {"allowed": ["09_audit/"], "forbidden": ["03_blueprints/"]},
    "candidate_pool": {
        "allowed": ["19_development_workspace/migrated-from-pool/"],
        "forbidden": ["01_policies_and_standards/"],
    },
    "discussion_draft": {
        "allowed": ["19_development_workspace/drafts-and-audits/"],
        "forbidden": ["01_policies_and_standards/", "02_enterprise_architecture/"],
    },
    "reference": {
        "allowed": ["02_enterprise_architecture/", "19_development_workspace/"],
        "forbidden": ["01_policies_and_standards/"],
    },
}

from _shared.frontmatter import parse_frontmatter_from_file as parse_frontmatter

def _check_template_integrity(fm: dict[str, Any], filepath: Path, rel_str: str) -> list[tuple[str, str, str]]:
    """防御纵深：模板文件的交叉验证。

    模板设计模式：模板故意用其展示的目标 doc_type（如 adr-template.md → doc_type: adr）。
    这本身是合法的。真正有风险的是"非模板文件错放进 templates/"——

    判定规则：
    1. 文件名以 -template.md 结尾 → 合法模板，放行
    2. 文件名 = index.md → 模板目录索引，放行
    3. 其他：doc_type ≠ "template" 且无模板命名信号 → 告警
    """
    errors: list[tuple[str, str, str]] = []
    doc_type = fm.get("doc_type", "")
    filename = filepath.name

    if filename.endswith("-template.md"):
        return errors

    if filename == "index.md":
        return errors

    if doc_type and doc_type != "template":
        errors.append(
            (
                "META-V24",
                "P2",
                f"文件在 templates/ 但 doc_type='{doc_type}' ≠ 'template'"
                f"，且文件名 '{filename}' 非 '-template.md' 结尾——可能错放目录",
            )
        )

    return errors

def _check_yaml_integrity(filepath: Path) -> list[tuple[str, str, str]]:
    errors: list[tuple[str, str, str]] = []
    try:
        import yaml as _yaml

        data = _yaml.safe_load(filepath.read_text(encoding="utf-8", errors="replace"))
        if data is None:
            errors.append(("META-V26", "P3", "YAML 文件内容为空"))
        elif not isinstance(data, (dict, list)):
            errors.append(("META-V26", "P3", f"YAML 顶层类型非 dict/list: {type(data).__name__}"))
    except Exception as e:
        errors.append(("META-V26", "P2", f"YAML 解析失败: {e}"))
    return errors

def check_file(filepath: Path, warn_only: bool) -> list[Any]:
    """check file."""
    errors = []
    """检查并返回违规列表."""
    fm = parse_frontmatter(filepath)
    if not fm:
        if filepath.suffix in (".yaml", ".yml"):
            yaml_errs = _check_yaml_integrity(filepath)
            errors.extend(yaml_errs)
            return errors
        errors.append(("META-V01", "P0", "缺少 frontmatter"))
        return errors

    rel = filepath.relative_to(REPO_ROOT)
    rel_str = str(rel).replace("\\", "/")

    if "templates/" in rel_str:
        tmpl_errs = _check_template_integrity(fm, filepath, rel_str)
        errors.extend(tmpl_errs)
        return errors

    doc_type = fm.get("doc_type", "")
    status_raw = fm.get("status", "")
    status = status_raw.lower()
    created_by = fm.get("created_by", "")
    ttl = fm.get("ttl", "")
    module_id = fm.get("module_id", "")
    ai_autonomy = fm.get("ai_autonomy", "")

    if doc_type and doc_type not in DOC_TYPE_LEGAL:
        errors.append(("META-V03", "P0", f"doc_type='{doc_type}' 不在21种合法值中"))

    if status_raw and status not in STATUS_LEGAL_LOWER and status_raw not in STATUS_LEGAL_TITLE:
        errors.append(("META-V04", "P1", f"status='{status_raw}' 不在7种合法值中"))

    if ttl and ttl not in TTL_LEGAL:
        errors.append(("META-V05", "P1", f"ttl='{ttl}' 不在4种合法值中"))

    if module_id and not MODULE_ID_PATTERN.match(module_id):
        errors.append(("META-V06", "P1", f"module_id='{module_id}' 格式不符合 DOMAIN-TYPE-NNN 规范"))

    if created_by and created_by not in CREATED_BY_LEGAL:
        errors.append(("META-V09", "P1", f"created_by='{created_by}' 不在合法值中"))

    if ai_autonomy and ai_autonomy not in AI_AUTONOMY_LEGAL:
        errors.append(("META-V07", "P1", f"ai_autonomy='{ai_autonomy}' 不在合法值中"))

    safety_level = fm.get("safety_level", "")
    if safety_level and safety_level not in SAFETY_LEVEL_LEGAL:
        errors.append(("META-V13", "P1", f"safety_level='{safety_level}' 不在合法值(H/M/L)中"))

    evolution_policy = fm.get("evolution_policy", "")
    if evolution_policy and evolution_policy not in EVOLUTION_POLICY_LEGAL:
        errors.append(
            ("META-V14", "P1", f"evolution_policy='{evolution_policy}' 不在合法值(frozen/extendable/rewritable)中")
        )

    governance_family = fm.get("governance_family", "")
    if governance_family and governance_family not in GOVERNANCE_FAMILY_LEGAL:
        errors.append(("META-V18", "P2", f"governance_family='{governance_family}' 不在合法值(A/B/C/D)中"))

    ai_capability_slot = fm.get("ai_capability_slot", "")
    if ai_capability_slot and ai_capability_slot not in AI_CAPABILITY_SLOT_LEGAL:
        errors.append(
            ("META-V19", "P2", f"ai_capability_slot='{ai_capability_slot}' 不在合法值(planned/reserved/active/none)中")
        )

    category = fm.get("category", "")
    if category and category not in CATEGORY_LEGAL:
        errors.append(("META-V20", "P2", f"category='{category}' 不在10种合法值中"))

    domain_val = fm.get("domain", "")
    if domain_val and domain_val not in DOMAIN_LEGAL:
        errors.append(("META-V21", "P2", f"domain='{domain_val}' 不在10种合法值中"))

    review_status = fm.get("review_status", "")
    if review_status and review_status not in REVIEW_STATUS_LEGAL:
        errors.append(
            ("META-V22", "P1", f"review_status='{review_status}' 不在合法值(unreviewed/reviewed/approved/rejected)中")
        )

    safety_level_val = fm.get("safety_level", "")
    if safety_level_val == "H" and review_status == "unreviewed":
        errors.append(("META-V23", "P1", "safety_level=H 但 review_status=unreviewed，高风险文件应尽快 review"))

    if doc_type == "construction_plan" and not fm.get("blueprint_refs"):
        errors.append(("META-V15", "P1", "doc_type='construction_plan' 缺少 blueprint_refs 字段"))

    if created_by == "agent" and not ttl:
        errors.append(("META-V10", "P1", "AI 生成文件(created_by=agent)缺少 ttl 字段"))

    if status in ("deprecated", "superseded") and not fm.get("superseded_by"):
        errors.append(("META-V11", "P1", f"status='{status}' 但缺少 superseded_by 字段"))

    is_index_file = filepath.name == "index.md"
    if is_index_file:
        missing = INDEX_MINIMAL_REQUIRED - set(fm.keys())
        if missing:
            errors.append(("META-V02", "P2", f"index.md 缺最少字段: {', '.join(sorted(missing))}"))
        return errors

    if status == "draft":
        missing = DRAFT_REQUIRED - set(fm.keys())
        if missing:
            errors.append(("META-V02", "P0", f"Draft 阶段缺必填字段: {', '.join(sorted(missing))}"))
    elif status == "active":
        missing = ACTIVE_REQUIRED - set(fm.keys())
        if missing:
            errors.append(("META-V02", "P0", f"Active 阶段缺必填字段: {', '.join(sorted(missing))}"))
    elif status == "accepted":
        missing = ACCEPTED_REQUIRED - set(fm.keys())
        if missing:
            errors.append(("META-V02", "P0", f"Accepted 阶段缺必填字段: {', '.join(sorted(missing))}"))

    if doc_type in DOC_TYPE_PATH_RULES:
        rules = DOC_TYPE_PATH_RULES[doc_type]
        for forbidden in rules.get("forbidden", []):
            if forbidden in rel_str:
                errors.append(("META-V08", "P2", f"doc_type='{doc_type}' 禁止存放在 {forbidden}"))
        if rules.get("allowed"):
            in_allowed = any(a in rel_str for a in rules["allowed"])
            if not in_allowed:
                errors.append(("META-V08", "P2", f"doc_type='{doc_type}' 应存放在 {rules['allowed']}"))

    return errors
    """check file."""

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="GATE-15: Frontmatter 元数据校验")
    parser.add_argument("--warn-only", action="store_true", help="只警告不阻塞")
    parser.add_argument("--staged", action="store_true", help="只检查暂存文件")
    args = parser.parse_args()

    docs_dir = REPO_ROOT / "docs"
    if not docs_dir.exists():
        print("GATE-15 SKIP: docs/ 不存在", file=sys.stderr)
        sys.exit(0)

    md_files = list(docs_dir.rglob("*.md")) + list(docs_dir.rglob("*.yaml")) + list(docs_dir.rglob("*.yml"))

    total_errors = 0
    total_warnings = 0
    files_with_issues = 0

    for fp in sorted(md_files):
        errors = check_file(fp, args.warn_only)
        if not errors:
            continue
        files_with_issues += 1
        for code, severity, msg in errors:
            rel = fp.relative_to(REPO_ROOT)
            if severity == "P0" and not args.warn_only:
                total_errors += 1
                print(f"BLOCK  {code} {rel}: {msg}", file=sys.stderr)
            else:
                total_warnings += 1
                print(f"WARN   {code} {rel}: {msg}", file=sys.stderr)

    print(
        f"\nGATE-15 结果: {len(md_files)} 文件扫描, {files_with_issues} 文件有问题, {total_errors} 阻断, {total_warnings} 警告",
        file=sys.stderr,
    )

    if total_errors > 0 and not args.warn_only:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
