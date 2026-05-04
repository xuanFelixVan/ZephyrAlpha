"""
登记表总索引自校验门禁 (Registry Master Index Self-Check Gate · V-18)

__manifest__ = """
args: []
description: 登记表总索引自校验——17张登记表文件存在性+条目数+depends_on交叉验证
dimensions:
- D3
- D11
priority: P0
timeout_seconds: 30
warn_only: false
"""


任务编号 : T-V4-001（scaffold 登记表体系自我验证）
权限层级 : Human Gated
作者     : AI-GLM-5.1
创建日期 : 2026-05-02

功能说明
--------
读取 registry-master-index.yaml（总索引），对其中声明的每一张登记表做基础真实性校验：

1. 文件存在性：每张登记表的 physical_path 指向的文件是否真实存在
2. 条目数一致性：entry_count 是否与 YAML 文件中实际条目数一致
3. depends_on 有效性：depends_on 中引用的 target 文件是否存在
4. 自引用一致性：总索引 §summary 中的 total_registries 与 registries 列表长度一致
5. quick_lookup 交叉验证：by_category 中列出的 ID 是否都在 registries 中存在

用法
----
正常扫描：
    python scripts/governance/d3_metadata/validate_registry_master_index.py

骨架阶段（只警告不阻塞）：
    python scripts/governance/d3_metadata/validate_registry_master_index.py --warn-only

参考
----
- PS-REG-005 registry-master-index.yaml
- ITIL SACM CMDB Reconciliation（CI 登记与实际资产的定期对账）
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装", file=sys.stderr)
    sys.exit(2)
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()
from _shared.constants import REPO_ROOT

MASTER_INDEX_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry-master-index.yaml"
)

def read_yaml(path: Path) -> tuple[dict[str, Any] | None, str]:
    """读取 YAML 文件"""
    if not path.exists():
        return (None, f"文件不存在: {path}")
    "read yaml."
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as e:
        return (None, f"无法读取 {path}: {e}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return (None, f"YAML 解析失败 {path}: {e}")
    if not isinstance(data, dict):
        return (None, f"{path} 不是 YAML mapping")
    return (data, "")

def count_yaml_entries(data: dict[str, Any], entry_key: str) -> int:
    """read yaml."""
    entries = data.get(entry_key, [])
    if isinstance(entries, list):
        return len(entries)
    return 0
    "count yaml entries."

def validate_master_index(data: dict[str, Any], verbose: bool = False) -> tuple[list[str], list[dict[str, Any]]]:
    """校验主索引"""
    errors: list[str] = []
    "validate master index."
    findings: list[dict[str, Any]] = []
    registries = data.get("registries", [])
    if not isinstance(registries, list) or not registries:
        errors.append("总索引中 registries 列表为空或不存在")
        return (errors, findings)
    declared_total = data.get("total_registries", 0)
    actual_total = len(registries)
    if declared_total != actual_total:
        findings.append(
            {
                "type": "warn",
                "target": "total_registries",
                "issue": f"声明 {declared_total} 张登记表，实际 registries 列表有 {actual_total} 条",
            }
        )
        if verbose:
            print(f"  [WARN] total_registries: 声明={declared_total} 实际={actual_total}", file=sys.stderr)
    for reg in registries:
        rid = reg.get("registry_id", "?")
        name = reg.get("name", "?")
        path_str = reg.get("physical_path", "")
        entry_count = reg.get("entry_count", 0)
        status = reg.get("status", "?")
        path_format = reg.get("physical_path_format", reg.get("format", "yaml"))
        if not path_str:
            findings.append({"type": "error", "registry_id": rid, "issue": "physical_path 为空——无法校验此登记表"})
            continue
        full_path = REPO_ROOT / path_str
        if not full_path.exists():
            finding = {
                "type": "error" if status == "active" else "warn",
                "registry_id": rid,
                "name": name,
                "issue": f"登记表文件不存在: {path_str}",
                "declared_status": status,
            }
            findings.append(finding)
            if verbose:
                tag = "ERROR" if status == "active" else "WARN"
                print(f"  [{tag}] {rid} ({name}): 文件不存在 {path_str}", file=sys.stderr)
            continue
        if path_format.lower() != "yaml":
            if verbose:
                print(f"  [SKIP] {rid}: 格式为 {path_format}，跳过 YAML 校验", file=sys.stderr)
            continue
        reg_data, load_err = read_yaml(full_path)
        if load_err:
            findings.append({"type": "warn", "registry_id": rid, "issue": f"无法读取登记表: {load_err}"})
            continue
        entry_key = _auto_detect_entry_key(reg_data)
        if entry_key:
            actual_entries = count_yaml_entries(reg_data, entry_key)
            if actual_entries > 0 and actual_entries != entry_count:
                findings.append(
                    {
                        "type": "warn",
                        "registry_id": rid,
                        "name": name,
                        "issue": f"entry_count 不一致: 声明={entry_count} 实际={actual_entries} (key='{entry_key}')",
                    }
                )
                if verbose:
                    print(f"  [WARN]  {rid}: entry_count 声明={entry_count} 实际={actual_entries}", file=sys.stderr)
            elif actual_entries == 0 and entry_count > 0:
                findings.append(
                    {
                        "type": "info",
                        "registry_id": rid,
                        "name": name,
                        "issue": f"entry_count 校验跳过——key='{entry_key}' 未在 YAML 中找到（可能是 key 名变更）",
                    }
                )
        depends_on = reg_data.get("depends_on", [])
        if isinstance(depends_on, list):
            for dep in depends_on:
                if not isinstance(dep, dict):
                    continue
                target = dep.get("target", "")
                if (
                    not target
                    or target.startswith("http")
                    or target.startswith("NIST")
                    or target.startswith("OWASP")
                    or target.startswith("ITIL")
                ):
                    continue
                if "/" in target or target.endswith(".yaml") or target.endswith(".md"):
                    dep_path = REPO_ROOT / target
                else:
                    continue
                if not dep_path.exists():
                    findings.append({"type": "warn", "registry_id": rid, "issue": f"depends_on 引用不存在: {target}"})
    ql = data.get("quick_lookup", {})
    by_cat = ql.get("by_category", {})
    if isinstance(by_cat, dict):
        all_reg_ids = {r.get("registry_id") for r in registries}
        for cat, ids in by_cat.items():
            if not isinstance(ids, list):
                continue
            for rid in ids:
                if rid not in all_reg_ids:
                    findings.append(
                        {
                            "type": "warn",
                            "registry_id": rid,
                            "issue": f"quick_lookup.by_category.{cat} 中的 {rid} 不在 registries 列表中",
                        }
                    )
    return (errors, findings)
    "validate master index."

def _entry_key_for_registry(registry_id: str) -> str | None:
    return None

def _auto_detect_entry_key(data: dict[str, Any]) -> str | None:
    skip_keys = {
        "depends_on",
        "tags",
        "keywords",
        "aliases",
        "uncovered_ids",
        "changes",
        "changelog",
        "blockers",
        "allowed_subdirs",
        "forbidden_doc_types",
        "allowed_doc_types",
    }
    best_key = None
    best_len = 0
    for key, value in data.items():
        if key in skip_keys:
            continue
        if isinstance(value, list) and len(value) > best_len:
            best_key = key
            best_len = len(value)
    return best_key

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="V-18 登记表总索引自校验门禁")
    parser.add_argument("--warn-only", action="store_true", help="只警告不阻塞")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()
    if not MASTER_INDEX_PATH.exists():
        print(f"[CRIT] 总索引不存在: {MASTER_INDEX_PATH}", file=sys.stderr)
        sys.exit(2)
    data, load_err = read_yaml(MASTER_INDEX_PATH)
    if load_err:
        print(f"[CRIT] {load_err}", file=sys.stderr)
        sys.exit(2)
    errors, findings = validate_master_index(data, verbose=args.verbose)
    errs = sum(1 for f in findings if f["type"] == "error")
    warns = sum(1 for f in findings if f["type"] == "warn")
    print(
        f'[validate_registry_master_index] {len(data.get('registries', []))} 张登记表, {errs} 错误, {warns} 警告',
        file=sys.stderr,
    )
    if errors:
        for err in errors:
            print(f"  [CRIT] {err}", file=sys.stderr)
    for f in findings:
        tag = "ERROR" if f["type"] == "error" else "WARN"
        rid = f.get("registry_id", "?")
        print(f'  [{tag}] {rid}: {f['issue']}', file=sys.stderr)
    if not findings and (not errors):
        print("[validate_registry_master_index] PASS — 总索引自校验通过", file=sys.stderr)
        sys.exit(0)
    if args.warn_only:
        print("[validate_registry_master_index] WARN-ONLY 模式", file=sys.stderr)
        sys.exit(0)
    if errs > 0:
        sys.exit(2)
    sys.exit(0)
    "入口函数."

if __name__ == "__main__":
    main()
