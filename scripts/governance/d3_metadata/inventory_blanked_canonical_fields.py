# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/inventory_blanked_canonical_fields.py | §
# [MODULE] scripts.governance.d3_metadata.inventory_blanked_canonical_fields
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] stdlib（argparse/subprocess/pathlib）；yaml；zephyr.shared.io.paths（REPO_ROOT SSoT）
# [CONSUMERS] closeout campaign st-zcloseout-20260928 D3；Owner 债务盘点；--check 可挂预检
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] READ-ONLY 盘点尺：绝不写两个被盘注册表；空白判定按"注册条目身份集"计数
#   （非行数）；dup 按 root section 身份键计数；HEAD-vs-disk 键集差双向列出；
#   报告 YAML 落 docs/_working/three_piece_infra/blanked_debt/（本尺唯一写面）；
#   --check 退出码 1=有债 / 2=结构错误 / 0=净；registry 文件缺失=结构错误（fail-closed）；
#   YAML 解析失败该 registry 记 structural_error 并计入退出码 2（不静默跳过）
# [MODIFY-GUARD] 仅创建报告文件（固定路径，TTL 区），不触碰注册表热文件
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 结构错误（文件缺失/YAML 不可解析/root section 非列表）→ 退出码 2 + stderr；
#   报告写出失败 → 退出码 2；其余正常退出 0/1
# [TESTS] tests/governance/d3_metadata/test_inventory_blanked_canonical_fields.py
# [A_module] module_id=MOD-INF-005（depgraph design node 15320909, granularity=file）| layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: E501  M11豁免(m11-perm-manual-legitimate): AI 会话按需调用的 permanent 盘点 CLI（登记债务只读尺，非常驻服务），会话显式触发
"""inventory_blanked_canonical_fields — 两册空白字段/身份键撞车只读盘点尺（D3）。

对 ``module_translation_registry.yaml`` 与
``capability_canonical_file_registry.yaml`` 逐 root section 报告：

(a) 空白必填字段债 —— 按"注册条目身份集"计数（同一身份键只记 1 条，非行数）；
(b) 身份键撞车 —— 每 root section 内重复身份键及出现次数（"567 撞车"同型面）；
(c) HEAD-vs-disk 键集差 —— 双向缺失清单（HEAD 有 disk 无 / disk 有 HEAD 无）。

报告（YAML）固定落 ``docs/_working/three_piece_infra/blanked_debt/``，
``--check`` 在 blanked>0 或 dup>0 或 diff>0 时退出 1（可作预检挂点）。

用法::

    python scripts/governance/d3_metadata/inventory_blanked_canonical_fields.py
    python scripts/governance/d3_metadata/inventory_blanked_canonical_fields.py --check
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from zephyr.shared.io.paths import REPO_ROOT  # SSoT 真源，禁本地重定义（SSOT-REDEFINITION）

REPORT_DIR = REPO_ROOT / "docs" / "_working" / "three_piece_infra" / "blanked_debt"

# 每册配置：文件 → 多个 root section，各 section 独立身份键与必填字段。
# required 依据：module_translation=entry_schema 全集（册头自声明）；
# capability 主体 capability_id+description 为手工真源（canonical_override/aliases
# 由 CapabilityLookup 派生，属可选）；creation_tokens 以 CREATE-GUARD 处方四字段为准。
REGISTRY_SPECS: list[dict[str, Any]] = [
    {
        "name": "module_translation_registry",
        "path": "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",
        "sections": [
            {
                "root": "entries",
                "identity": "module_path",
                "required": [
                    "module_path",
                    "domain_id",
                    "name_zh",
                    "name_en",
                    "desc_zh",
                    "desc_en",
                    "plain_zh",
                ],
            }
        ],
    },
    {
        "name": "capability_canonical_file_registry",
        "path": "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
        "sections": [
            {
                "root": "capabilities",
                "identity": "capability_id",
                "required": ["capability_id", "description"],
            },
            {
                "root": "creation_tokens",
                "identity": "file",
                "required": ["file", "token", "created_by", "capability"],
            },
        ],
    },
]


def _is_blank(value: Any) -> bool:
    """True = 缺失/None/空白串/空容器（字段级空白判定）。"""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def _load_side(text: str) -> dict[str, Any]:
    data = yaml.safe_load(text)
    return data if isinstance(data, dict) else {}


def _section_keys(data: dict[str, Any], section: dict[str, Any]) -> list[str]:
    entries = data.get(section["root"])
    if entries is None:
        return []
    if not isinstance(entries, list):
        raise ValueError(f"root section {section['root']!r} is not a list")
    out: list[str] = []
    for entry in entries:
        out.append(str(entry.get(section["identity"], "")) if isinstance(entry, dict) else "")
    return out


def _scan_section(data: dict[str, Any], section: dict[str, Any]) -> dict[str, Any]:
    identity = section["identity"]
    required = section["required"]
    entries = data.get(section["root"]) or []
    blanked: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        key = str(entry.get(identity, ""))
        blank_fields = [f for f in required if _is_blank(entry.get(f))]
        if blank_fields:
            blanked.append({"key": key or f"<blank-identity@{idx}>", "blank_fields": blank_fields})
        if key:
            seen[key] = seen.get(key, 0) + 1
    dups = {k: n for k, n in seen.items() if n > 1}
    return {
        "root": section["root"],
        "identity_field": identity,
        "entry_count": len(seen) + sum(1 for e in entries if not isinstance(e, dict)),
        "blanked_identity_count": len({b["key"] for b in blanked}),
        "blanked_entries": blanked,
        "duplicate_identity_count": len(dups),
        "duplicate_extra_occurrences": sum(n - 1 for n in dups.values()),
        "duplicates": dups,
    }


def inventory(spec: dict[str, Any], head_text: str | None, disk_text: str) -> dict[str, Any]:
    try:
        disk_data = _load_side(disk_text)
        head_data = _load_side(head_text) if head_text is not None else {}
        sections = [_scan_section(disk_data, s) for s in spec["sections"]]
        key_diffs = []
        for s in spec["sections"]:
            disk_keys = _section_keys(disk_data, s)
            head_keys = _section_keys(head_data, s) if head_text is not None else []
            head_set, disk_set = set(head_keys), set(disk_keys)
            key_diffs.append(
                {
                    "root": s["root"],
                    "missing_on_disk": sorted(k for k in head_set - disk_set if k),
                    "missing_on_head": sorted(k for k in disk_set - head_set if k),
                }
            )
        result = {
            "registry": spec["name"],
            "path": spec["path"],
            "sections": sections,
            "key_diff": key_diffs,
            "structural_error": None,
        }
    except (yaml.YAMLError, ValueError) as exc:
        result = {
            "registry": spec["name"],
            "path": spec["path"],
            "sections": [],
            "key_diff": [],
            "structural_error": str(exc),
        }
    result["blanked_count"] = sum(s["blanked_identity_count"] for s in result["sections"])
    result["duplicate_key_count"] = sum(s["duplicate_identity_count"] for s in result["sections"])
    result["key_diff_count"] = sum(len(d["missing_on_disk"]) + len(d["missing_on_head"]) for d in result["key_diff"])
    return result


def _head_text(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8")
    return r.stdout if r.returncode == 0 else None  # 新文件无 HEAD 基线 → 空基线


def build_report(results: list[dict[str, Any]]) -> dict[str, Any]:
    structural = [r for r in results if r["structural_error"]]
    totals = {
        "blanked_total": sum(r["blanked_count"] for r in results),
        "duplicate_keys_total": sum(r["duplicate_key_count"] for r in results),
        "key_diff_total": sum(r["key_diff_count"] for r in results),
        "structural_errors": len(structural),
    }
    dirty = (
        totals["blanked_total"] > 0
        or totals["duplicate_keys_total"] > 0
        or totals["key_diff_total"] > 0
        or totals["structural_errors"] > 0
    )
    return {
        "report": "inventory_blanked_canonical_fields",
        "description": "D3 只读盘点：空白必填字段(按身份键计)+每 root section 身份键撞车+HEAD/磁盘键集差",
        "registries": results,
        "totals": totals,
        "verdict": "debt_present" if dirty else "clean",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="有债（空白>0 或撞车>0 或键差>0 或结构错误）时退出 1",
    )
    parser.add_argument(
        "--report",
        default=str(REPORT_DIR / "inventory_blanked_canonical_fields_report.yaml"),
        help="报告输出路径（默认 docs/_working/three_piece_infra/blanked_debt/ 下）",
    )
    parser.add_argument("--no-report", action="store_true", help="不写 YAML 报告（纯 stdout）")
    args = parser.parse_args(argv)

    results: list[dict[str, Any]] = []
    for spec in REGISTRY_SPECS:
        path = REPO_ROOT / spec["path"]
        if not path.exists():
            print(f"[d3-inventory] structural error: missing {spec['path']}", file=sys.stderr)
            return 2
        try:
            disk_text = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[d3-inventory] structural error: {exc}", file=sys.stderr)
            return 2
        results.append(inventory(spec, _head_text(spec["path"]), disk_text))

    report = build_report(results)
    if report["totals"]["structural_errors"]:
        for r in results:
            if r["structural_error"]:
                print(
                    f"[d3-inventory] YAML 结构错误 {r['path']}: {r['structural_error']}",
                    file=sys.stderr,
                )

    if not args.no_report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            body = yaml.safe_dump(report, allow_unicode=True, sort_keys=False, width=100)
            frontmatter = (
                "---\nttl: task_bound\ncompletes_when: 本尺重跑即刷新本报告；两册清债（verdict=clean）后可退役\n---\n"
            )
            report_path.write_text(frontmatter + body, encoding="utf-8")
        except OSError as exc:
            print(f"[d3-inventory] report write failed: {exc}", file=sys.stderr)
            return 2
        print(f"[d3-inventory] report -> {report_path}")

    print(
        "[d3-inventory] blanked={blanked_total} dup_keys={duplicate_keys_total} "
        "key_diff={key_diff_total} structural_errors={structural_errors} verdict={verdict}".format(
            **report["totals"], verdict=report["verdict"]
        )
    )

    if args.check:
        dirty = report["verdict"] == "debt_present"
        return 1 if dirty else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
