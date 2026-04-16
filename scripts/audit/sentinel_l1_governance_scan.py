# -*- coding: utf-8 -*-
"""
Sentinel L1：全库 md 链接可达性 + module_id 重复扫描（只读），输出到 docs/09_AUDIT/STATE/

module_id 重复：**仅**各文件首道 `---` YAML 内第一个 `module_id`，与 ADR-OC-003 及
`dedupe_module_id_frontmatter.py` 一致；不扫描正文或第二段 YAML 中的示例行，避免假阳性。

用法：在仓库根目录执行  python scripts/audit/sentinel_l1_governance_scan.py
"""
from __future__ import annotations

import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKIP_PARTS = {
    ".git", ".venv", ".pytest_cache", "__pycache__",
    ".audit_fix_backup",   # 备份目录，非活跃治理范围
    ".trae",               # 工具私有目录
    "review_materials_package",  # 评审材料包，不计入日常治理
    ".venv-1",             # 第二虚拟环境，含三方包 LICENSE.md 等，不纳入治理
}
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
MODULE_ID_RE = re.compile(r"^module_id:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
MAX_DETAIL = 20000  # 扩容至全量（Phase 2 需完整断链列表供 fix_dead_links.py 消费）
# 本脚本覆写的 Markdown 报告：本轮扫描读到的仍是旧稿，勿计入「无 module_id」以免自指为 1
L1_REPORT_MD_REL = "docs/09_AUDIT/STATE/sentinel-l1-scan-latest.md"


def split_first_front_matter(raw: str) -> tuple[str, str, str] | None:
    """返回 (bom_prefix, fm_inner, body_after_fm)。与 dedupe_module_id_frontmatter 语义一致。"""
    bom = ""
    s = raw
    if s.startswith("\ufeff"):
        bom = "\ufeff"
        s = s[1:]
    lines = s.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    inner: list[str] = []
    i = 1
    while i < len(lines):
        if lines[i].strip() == "---":
            break
        inner.append(lines[i])
        i += 1
    if i >= len(lines):
        return None
    body = "\n".join(lines[i + 1 :])
    fm_inner = "\n".join(inner)
    return (bom, fm_inner, body)


def first_front_matter_module_id(raw: str) -> str | None:
    """仅首道 YAML front matter 内第一个 module_id（ADR-OC-003 / 台账口径）。"""
    sp = split_first_front_matter(raw)
    if not sp:
        return None
    m = MODULE_ID_RE.search(sp[1])
    if not m:
        return None
    k = m.group(1).strip().strip('"').strip("'")
    return k or None


def iter_md_files() -> list[Path]:
    out: list[Path] = []
    for p in REPO.rglob("*.md"):
        if not p.is_file():
            continue
        if any(x in p.parts for x in SKIP_PARTS):
            continue
        out.append(p)
    return sorted(out)


def build_index(all_files: list[Path]) -> dict[str, str]:
    """lower(relposix) -> canonical relposix"""
    idx: dict[str, str] = {}
    for p in all_files:
        rel = p.relative_to(REPO).as_posix()
        idx[rel.lower()] = rel
        idx[Path(rel).name.lower()] = rel
    return idx


def resolve_target(source: Path, url: str) -> Path | None:
    u = url.strip()
    if not u or u.startswith(("#", "mailto:", "tel:", "http://", "https://", "file:")):
        return None
    u = u.split("#", 1)[0].strip()
    if not u:
        return None
    base = source.parent
    try:
        return (base / u).resolve()
    except OSError:
        return None


def scan_links(all_files: list[Path]) -> dict:
    idx = build_index(all_files)
    invalid: list[dict] = []
    stats = {
        "total_files_scanned": 0,
        "total_md_links": 0,
        "skipped_external": 0,
        "valid": 0,
        "invalid": 0,
    }
    for md in all_files:
        stats["total_files_scanned"] += 1
        try:
            lines = md.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        rel = md.relative_to(REPO).as_posix()
        # 按行匹配，避免无闭合 ) 时正则吞掉整文件
        for line in lines:
            if "](" not in line:
                continue
            for m in LINK_RE.finditer(line):
                stats["total_md_links"] += 1
                url = m.group(2).strip()
                if url.startswith(("#", "mailto:", "tel:", "http://", "https://", "file:")):
                    stats["skipped_external"] += 1
                    continue
                if url.startswith("/") and not url.startswith("//"):
                    target = (REPO / url.lstrip("/")).resolve()
                else:
                    target = resolve_target(md, url)
                if target is None:
                    stats["skipped_external"] += 1
                    continue
                try:
                    if target.is_file():
                        stats["valid"] += 1
                        continue
                    if target.is_dir():
                        stats["valid"] += 1
                        continue
                    if (target / "INDEX.md").is_file() or (target / "index.md").is_file():
                        stats["valid"] += 1
                        continue
                except OSError:
                    pass
                try:
                    trel = target.relative_to(REPO).as_posix()
                except ValueError:
                    trel = None
                if trel:
                    cand = idx.get(trel.lower())
                    if cand and (REPO / cand).is_file():
                        stats["valid"] += 1
                        continue
                    tdir = REPO / trel
                    if tdir.is_dir() or (tdir / "INDEX.md").is_file():
                        stats["valid"] += 1
                        continue
                stats["invalid"] += 1
                if len(invalid) < MAX_DETAIL:
                    try:
                        rpv = target.relative_to(REPO).as_posix()
                    except ValueError:
                        rpv = str(target)
                    invalid.append({"source": rel, "url": url, "resolved": rpv})
    return {
        "stats": stats,
        "invalid_details_sample": invalid,
        "invalid_truncated": stats["invalid"] > len(invalid),
    }


def scan_module_ids(all_files: list[Path]) -> dict:
    mid_to_files: dict[str, list[str]] = defaultdict(list)
    no_id: list[str] = []
    for md in all_files:
        rel = md.relative_to(REPO).as_posix()
        if rel.startswith("review_materials_package"):
            continue
        try:
            raw = md.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        k = first_front_matter_module_id(raw)
        if not k:
            if rel != L1_REPORT_MD_REL:
                no_id.append(rel)
            continue
        mid_to_files[k].append(rel)
    dup = {k: v for k, v in mid_to_files.items() if len(v) > 1}
    return {
        "unique_module_ids": len(mid_to_files),
        "duplicate_ids_count": len(dup),
        "duplicates": {k: v for k, v in sorted(dup.items(), key=lambda x: -len(x[1]))[:200]},
        "files_without_module_id_sample": no_id[:MAX_DETAIL],
        "no_id_total": len(no_id),
    }


def scan_registry_diff() -> dict:
    """
    注册表差集比对（Registry Diff Logic）——Sentinel L1 漏网之鱼发现机制。

    对比 governance-asset-inventory.yaml 中登记的文件 vs 磁盘实际存在的文件，检测：
    1. 漏网之鱼（unregistered）：磁盘有但注册表无 → 潜在违规资产
    2. 幽灵条目（ghost）：注册表有但磁盘无 → 注册表未同步更新

    规则（来源：AGENTS.md 第八-B节 + audit-system.mdc 准入门禁）：
    - scripts/audit/, scripts/governance/, scripts/hooks/, scripts/ci_audit/ 下所有 .py 文件
      必须在 governance-asset-inventory.yaml 中有对应 name 条目
    - .github/workflows/ 下所有 .yml 文件必须在 ci_workflows.files 中登记
    - .cursor/rules/ 下所有 .mdc 文件必须在 cursor_rules_layers 中登记
    - .trae/ 下活跃文件必须在 trae_assets 中登记
    """
    INVENTORY_PATH = REPO / "docs" / "01_GOVERNANCE" / "governance-asset-inventory.yaml"

    result: dict = {
        "inventory_found": INVENTORY_PATH.exists(),
        "unregistered": [],   # 漏网之鱼：在磁盘上但未在注册表登记
        "ghost_entries": [],  # 幽灵条目：在注册表中但磁盘上已不存在
        "summary": {},
    }

    if not INVENTORY_PATH.exists():
        result["error"] = "governance-asset-inventory.yaml 未找到，跳过注册表差集比对"
        return result

    try:
        import yaml  # type: ignore[import]
        raw = INVENTORY_PATH.read_text(encoding="utf-8", errors="replace")
        # 去除 ## 开头的注释行（YAML 不允许以 # 开头的文件头部注释，只允许行内）
        clean_lines = [ln for ln in raw.splitlines() if not ln.startswith("##")]
        inventory = yaml.safe_load("\n".join(clean_lines)) or {}
    except Exception as e:
        result["error"] = f"解析 governance-asset-inventory.yaml 失败: {e}"
        return result

    # ─────────────────────────────────────────────
    # 1. 受治理的脚本目录（.py 文件）
    # ─────────────────────────────────────────────
    # governance-asset-inventory.yaml 结构：顶层 tools → audit_scripts/governance_scripts/...
    script_sections = {
        "scripts/audit":      ("tools", "audit_scripts"),
        "scripts/governance": ("tools", "governance_scripts"),
        "scripts/hooks":      ("tools", "pre_commit_hooks"),
        "scripts/ci_audit":   ("tools", "ci_audit_scripts"),
    }

    # 豁免清单：这些文件名不纳入漏网之鱼检查（工具生成 / 遗留 / 备份目录内）
    EXEMPT_NAMES = {
        "__pycache__", "__init__.py",
        # _BACKUP_SCRIPTS 子目录内文件不强制注册
    }

    for rel_dir, (top_key, sub_key) in script_sections.items():
        disk_dir = REPO / rel_dir
        if not disk_dir.exists():
            continue

        # 获取注册表中已登记的文件名集合
        registered_names: set[str] = set()
        section = inventory.get(top_key, {}).get(sub_key, {})
        for entry in section.get("files", []):
            n = entry.get("name", "").strip()
            if n:
                registered_names.add(n)

        # 扫描磁盘上的 .py 文件（只检查直接子文件，不递归）
        for py_file in disk_dir.iterdir():
            if not py_file.is_file():
                continue
            if py_file.suffix != ".py":
                continue
            if py_file.name in EXEMPT_NAMES:
                continue
            # 跳过 _BACKUP_SCRIPTS 子目录的文件（不在此路径内，备份在 scripts/_BACKUP_SCRIPTS/）
            if py_file.name not in registered_names:
                result["unregistered"].append({
                    "type": "script",
                    "path": f"{rel_dir}/{py_file.name}",
                    "directory": rel_dir,
                    "severity": "HIGH",
                    "action": "立即走准入门禁6步手续，或删除",
                })

        # 检查注册表中的文件是否在磁盘上存在（幽灵条目）
        for name in registered_names:
            if not (disk_dir / name).exists():
                result["ghost_entries"].append({
                    "type": "script",
                    "registered_path": f"{rel_dir}/{name}",
                    "action": "从 governance-asset-inventory.yaml 中移除该条目",
                })

    # ─────────────────────────────────────────────
    # 2. CI 工作流（.yml 文件）
    # ─────────────────────────────────────────────
    workflows_dir = REPO / ".github" / "workflows"
    if workflows_dir.exists():
        registered_workflows: set[str] = set()
        for entry in inventory.get("tools", {}).get("ci_workflows", {}).get("files", []):
            n = entry.get("name", "").strip()
            if n:
                registered_workflows.add(n)

        for wf_file in workflows_dir.iterdir():
            if wf_file.is_file() and wf_file.suffix in (".yml", ".yaml"):
                if wf_file.name not in registered_workflows:
                    result["unregistered"].append({
                        "type": "ci_workflow",
                        "path": f".github/workflows/{wf_file.name}",
                        "severity": "MEDIUM",
                        "action": "在 governance-asset-inventory.yaml ci_workflows.files 中登记",
                    })
        for name in registered_workflows:
            if not (workflows_dir / name).exists():
                result["ghost_entries"].append({
                    "type": "ci_workflow",
                    "registered_path": f".github/workflows/{name}",
                    "action": "从 governance-asset-inventory.yaml ci_workflows.files 中移除",
                })

    # ─────────────────────────────────────────────
    # 3. Cursor 规则文件（.mdc）
    # ─────────────────────────────────────────────
    rules_dir = REPO / ".cursor" / "rules"
    if rules_dir.exists():
        registered_rules: set[str] = set()
        onboarding = inventory.get("ai_onboarding", {})
        for layer_key in ("layer_0_always", "layer_1_glob_triggered", "layer_2_description_triggered"):
            for entry in onboarding.get("cursor_rules_layers", {}).get(layer_key, {}).get("files", []):
                p = entry.get("path", "").strip()
                if p:
                    registered_rules.add(Path(p).name)

        for mdc_file in rules_dir.iterdir():
            if mdc_file.is_file() and mdc_file.suffix == ".mdc":
                if mdc_file.name not in registered_rules:
                    result["unregistered"].append({
                        "type": "cursor_rule",
                        "path": f".cursor/rules/{mdc_file.name}",
                        "severity": "LOW",
                        "action": "在 governance-asset-inventory.yaml ai_onboarding 中登记",
                    })

    # ─────────────────────────────────────────────
    # 4. 汇总
    # ─────────────────────────────────────────────
    unregistered_by_severity: dict[str, int] = {}
    for item in result["unregistered"]:
        sev = item.get("severity", "UNKNOWN")
        unregistered_by_severity[sev] = unregistered_by_severity.get(sev, 0) + 1

    result["summary"] = {
        "total_unregistered": len(result["unregistered"]),
        "total_ghost_entries": len(result["ghost_entries"]),
        "unregistered_by_severity": unregistered_by_severity,
        "registry_health": (
            "CLEAN" if not result["unregistered"] and not result["ghost_entries"]
            else "WARNING" if len(result["unregistered"]) <= 3
            else "CRITICAL"
        ),
    }

    return result


def path_depth_stats(all_files: list[Path]) -> dict:
    depths = []
    for p in all_files:
        rel = p.relative_to(REPO).as_posix()
        depths.append((rel.count("/"), rel))
    depths.sort(reverse=True)
    return {"deepest_30": [{"depth": d, "path": r} for d, r in depths[:30]]}


def main() -> None:
    import sys as _sys
    import os as _os
    # 如果在 pre-commit 环境（PRECOMMIT=1）或传入 --cache 参数，写入 .audit_cache/ 避免修改 docs/
    use_cache = "--cache" in _sys.argv or _os.environ.get("PRECOMMIT") == "1"
    if use_cache:
        out_dir = REPO / ".audit_cache"
    else:
        out_dir = REPO / "docs" / "09_AUDIT" / "STATE"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    all_files = iter_md_files()
    payload = {
        "scan_time_utc": ts,
        "repo": str(REPO),
        "md_file_count": len(all_files),
        "links": scan_links(all_files),
        "module_ids": scan_module_ids(all_files),
        "path_depth": path_depth_stats(all_files),
        "registry_diff": scan_registry_diff(),
    }
    json_path = out_dir / "sentinel-l1-scan-latest.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    s = payload["links"]["stats"]
    md_lines = [
        "---",
        "module_id: AUDIT_sentinel-l1-scan-latest",
        "standard_type: audit_state",
        "generated_by: scripts/governance/sentinel_l1_governance_scan.py",
        "---",
        "",
        "# Sentinel L1 扫描结果（机器生成）",
        "",
        f"> **UTC 时间**: {ts}",
        f"> **Markdown 文件数**: {len(all_files)}",
        "",
        "## 链接统计",
        "",
        "| 指标 | 数值 |",
        "|------|------|",
        f"| 扫描文件 | {s['total_files_scanned']} |",
        f"| Markdown 内链（非 http/锚点等已排除） | {s['total_md_links']} |",
        f"| 跳过（外链/锚点等） | {s['skipped_external']} |",
        f"| 判定有效 | {s['valid']} |",
        f"| 判定无效 | {s['invalid']} |",
        "",
        "### 无效链接样本（最多 {} 条）".format(MAX_DETAIL),
        "",
    ]
    for row in payload["links"]["invalid_details_sample"][:50]:
        md_lines.append(f"- `{row['source']}` → `{row['url']}`")
    if payload["links"]["invalid_truncated"]:
        md_lines.append("")
        md_lines.append("（更多无效链接见 JSON `invalid_details_sample` 与统计字段）")
    mi = payload["module_ids"]
    md_lines.extend(
        [
            "",
            "## module_id",
            "",
            f"- 唯一 module_id 数: **{mi['unique_module_ids']}**",
            f"- 重复 id 数: **{mi['duplicate_ids_count']}**",
            f"- 首道 front matter 无 `module_id` 的文件数: **{mi['no_id_total']}**",
            "",
            "### 重复模块（前 20 个）",
            "",
        ]
    )
    for i, (k, v) in enumerate(list(mi["duplicates"].items())[:20]):
        md_lines.append(f"- `{k}`: {len(v)} 个文件")
    md_lines.extend(["", "## 路径深度 Top 10", ""])
    for item in payload["path_depth"]["deepest_30"][:10]:
        md_lines.append(f"- depth={item['depth']} `{item['path']}`")

    # ── 注册表差集比对区 ──────────────────────────────────────
    rd = payload["registry_diff"]
    rd_summary = rd.get("summary", {})
    health = rd_summary.get("registry_health", "UNKNOWN")
    health_emoji = {"CLEAN": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(health, "❓")
    md_lines.extend(
        [
            "",
            "## 注册表差集比对（漏网之鱼检测）",
            "",
            f"> **注册表健康度**: {health_emoji} {health}",
            f"> **漏网资产数（未登记）**: {rd_summary.get('total_unregistered', 0)}",
            f"> **幽灵条目数（已删除但注册表未清）**: {rd_summary.get('total_ghost_entries', 0)}",
        ]
    )
    if rd.get("error"):
        md_lines.append(f"\n> ⚠️ 警告: {rd['error']}")

    if rd.get("unregistered"):
        md_lines.extend(["", "### 漏网资产（须立即走准入门禁或删除）", ""])
        for item in rd["unregistered"]:
            sev = item.get("severity", "")
            md_lines.append(f"- [{sev}] `{item['path']}` → {item.get('action', '')}")

    if rd.get("ghost_entries"):
        md_lines.extend(["", "### 幽灵条目（注册表中存在但文件已删除）", ""])
        for item in rd["ghost_entries"]:
            md_lines.append(
                f"- `{item['registered_path']}` → {item.get('action', '从注册表中移除')}"
            )

    if not rd.get("unregistered") and not rd.get("ghost_entries") and rd.get("inventory_found"):
        md_lines.append("\n> 所有受治理目录的文件均已在注册表中登记，注册表与文件系统完全同步。")

    (out_dir / "sentinel-l1-scan-latest.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {json_path} and sentinel-l1-scan-latest.md")


if __name__ == "__main__":
    main()
