# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/validate_registry_master_index.py | §
# [MODULE] scripts.governance.d3_metadata.validate_registry_master_index
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.__init__
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
"""登记表总索引自校验门禁 (Registry Master Index Self-Check Gate · V-18).

任务 T-V4-001：扫描 registry-master-index.yaml，校验登记表文件存在性、
entry_count、depends_on 与 quick_lookup 交叉引用。
"""

from __future__ import annotations

__manifest__ = {
    "args": [],
    "description": "登记表总索引自校验：登记表文件存在性、条目数、depends_on 交叉验证",
    "dimensions": ["D3", "D11"],
    "priority": "P0",
    "timeout_seconds": 30,
    "warn_only": False,
}

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML 未安装", file=sys.stderr)
    sys.exit(EXIT_ERROR)
_GOV_DIR = str(next(p for p in Path(__file__).resolve().parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout
from _shared.registry_entry_count import count_primary_registry_entries, primary_count_entry_key

ensure_utf8_stdout()
from _shared.constants import EXIT_ERROR, EXIT_PASS, REPO_ROOT

MASTER_INDEX_PATH = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "registry-master-index.yaml"
)


def read_yaml(path: Path) -> tuple[dict[str, Any] | None, str]:
    """读取 YAML 文件"""
    if not path.exists():
        return (None, f"文件不存在: {path}")
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


def validate_master_index(data: dict[str, Any], verbose: bool = False) -> tuple[list[str], list[dict[str, Any]]]:
    """校验主索引。"""
    errors: list[str] = []
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
        stem = full_path.stem
        actual_entries = count_primary_registry_entries(reg_data, stem)
        entry_key_label = primary_count_entry_key(reg_data, stem)
        if actual_entries > 0 and actual_entries != entry_count:
            findings.append(
                {
                    "type": "warn",
                    "registry_id": rid,
                    "name": name,
                    "issue": f"entry_count 不一致: 声明={entry_count} 实际={actual_entries} (source='{entry_key_label}')",
                }
            )
            if verbose:
                print(
                    f"  [WARN]  {rid}: entry_count 声明={entry_count} 实际={actual_entries}",
                    file=sys.stderr,
                )
        elif actual_entries == 0 and entry_count > 0:
            findings.append(
                {
                    "type": "info",
                    "registry_id": rid,
                    "name": name,
                    "issue": f"entry_count 校验信息——声明>0 但主列表为空 (source='{entry_key_label}')",
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


def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description="V-18 登记表总索引自校验门禁")
    parser.add_argument("--warn-only", action="store_true", help="只警告不阻塞")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    args = parser.parse_args()
    if not MASTER_INDEX_PATH.exists():
        print(f"[CRIT] 总索引不存在: {MASTER_INDEX_PATH}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    data, load_err = read_yaml(MASTER_INDEX_PATH)
    if load_err:
        print(f"[CRIT] {load_err}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    errors, findings = validate_master_index(data, verbose=args.verbose)
    errs = sum(1 for f in findings if f["type"] == "error")
    warns = sum(1 for f in findings if f["type"] == "warn")
    nreg = len(data.get("registries", []))
    print(
        f"[validate_registry_master_index] {nreg} 张登记表, {errs} 错误, {warns} 警告",
        file=sys.stderr,
    )
    if errors:
        for err in errors:
            print(f"  [CRIT] {err}", file=sys.stderr)
    for f in findings:
        if f["type"] == "error":
            tag = "ERROR"
        elif f["type"] == "info":
            tag = "INFO"
        else:
            tag = "WARN"
        rid = f.get("registry_id", "?")
        issue = f.get("issue", "")
        print(f"  [{tag}] {rid}: {issue}", file=sys.stderr)
    if not findings and (not errors):
        print("[validate_registry_master_index] PASS — 总索引自校验通过", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if args.warn_only:
        print("[validate_registry_master_index] WARN-ONLY 模式", file=sys.stderr)
        sys.exit(EXIT_PASS)
    if errs > 0:
        sys.exit(EXIT_ERROR)
    sys.exit(EXIT_PASS)


if __name__ == "__main__":
    main()
