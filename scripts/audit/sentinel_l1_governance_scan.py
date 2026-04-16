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
L1_REPORT_MD_REL = "docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_LATEST.md"


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


def path_depth_stats(all_files: list[Path]) -> dict:
    depths = []
    for p in all_files:
        rel = p.relative_to(REPO).as_posix()
        depths.append((rel.count("/"), rel))
    depths.sort(reverse=True)
    return {"deepest_30": [{"depth": d, "path": r} for d, r in depths[:30]]}


def main() -> None:
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
    }
    json_path = out_dir / "SENTINEL_L1_SCAN_LATEST.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    s = payload["links"]["stats"]
    md_lines = [
        "---",
        "module_id: AUDIT_SENTINEL_L1_SCAN_LATEST",
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

    (out_dir / "SENTINEL_L1_SCAN_LATEST.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Wrote {json_path} and SENTINEL_L1_SCAN_LATEST.md")


if __name__ == "__main__":
    main()
