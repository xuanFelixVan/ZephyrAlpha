# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
"""
总清单严格路径核对：解析指定 Markdown 中的 (1) 相对 Markdown 内链 (2) 正文/表格中的 docs/... 路径，
要求在仓库根下存在（文件或目录）。默认目标为蓝图阶段总清单。

用法（仓库根目录）：
  python scripts/governance/verify_manifest_paths_strict.py
  python scripts/governance/verify_manifest_paths_strict.py --manifest docs/other.md

退出码：存在缺失路径时为 1（供 CI / pre-commit）；全通过为 0。

报告：docs/09_AUDIT/STATE/MANIFEST_PATH_AUDIT_<stem>.json 与同基名 .md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
# 表格或正文中的 docs/ 路径（含子目录与可选 .md、末尾 /）
DOCS_LITERAL_RE = re.compile(
    r"docs/(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+(?:\.md)?/?"
)
STATE_DIR = REPO / "docs" / "09_AUDIT" / "STATE"


def resolve_link(source: Path, url: str) -> Path | None:
    u = url.strip()
    if not u or u.startswith(("#", "mailto:", "tel:", "http://", "https://", "file:")):
        return None
    u = u.split("#", 1)[0].strip()
    if not u:
        return None
    try:
        return (source.parent / u).resolve()
    except OSError:
        return None


def exists_under_repo(target: Path) -> bool:
    try:
        target.relative_to(REPO)
    except ValueError:
        return False
    return target.is_file() or target.is_dir()


def normalize_docs_literal(raw: str) -> str:
    s = raw.strip().rstrip(".,);」』\"'")
    return s


def collect_refs(manifest: Path) -> tuple[list[dict], list[dict]]:
    text = manifest.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    md_hits: list[dict] = []
    literal_hits: list[dict] = []

    for lineno, line in enumerate(lines, start=1):
        if "](" in line:
            for m in LINK_RE.finditer(line):
                url = m.group(2).strip()
                resolved = resolve_link(manifest, url)
                if resolved is None:
                    continue
                md_hits.append(
                    {
                        "kind": "markdown_link",
                        "line": lineno,
                        "url": url,
                        "resolved_posix": resolved.relative_to(REPO).as_posix(),
                    }
                )

    for m in DOCS_LITERAL_RE.finditer(text):
        raw = m.group(0)
        norm = normalize_docs_literal(raw)
        # 说明性省略号（如「docs/ 下的 …」被误扫）不作为路径
        if norm == "docs/..." or norm.endswith("/...") or "/.../" in norm:
            continue
        # 行号近似：按首次出现分行定位
        pos = text.find(raw)
        line_no = text.count("\n", 0, pos) + 1 if pos >= 0 else 0
        literal_hits.append(
            {
                "kind": "docs_literal",
                "line": line_no,
                "raw": raw,
                "normalized_posix": norm,
            }
        )

    return md_hits, literal_hits


def check_manifest(manifest: Path) -> dict:
    md_hits, literal_hits = collect_refs(manifest)
    missing: list[dict] = []
    checked: list[dict] = []

    seen: set[str] = set()

    for h in md_hits:
        key = ("md", h["resolved_posix"])
        if key in seen:
            continue
        seen.add(key)
        p = REPO / h["resolved_posix"]
        ok = exists_under_repo(p)
        row = {**h, "exists": ok}
        checked.append(row)
        if not ok:
            missing.append(row)

    for h in literal_hits:
        rel = h["normalized_posix"]
        key = ("lit", rel)
        if key in seen:
            continue
        seen.add(key)
        p = REPO / rel
        ok = exists_under_repo(p)
        row = {**h, "resolved_posix": rel, "exists": ok}
        checked.append(row)
        if not ok:
            missing.append(row)

    return {
        "manifest": manifest.relative_to(REPO).as_posix(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_checked_unique": len(checked),
        "missing_count": len(missing),
        "checked": checked,
        "missing": missing,
    }


def write_reports(result: dict, stem: str) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = STATE_DIR / f"MANIFEST_PATH_AUDIT_{stem}.json"
    md_path = STATE_DIR / f"MANIFEST_PATH_AUDIT_{stem}.md"
    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "---",
        f"title: 总清单路径严格核对 — {stem}",
        f"generated_at_utc: {result['generated_at_utc']}",
        "---",
        "",
        f"- **manifest**: `{result['manifest']}`",
        f"- **唯一核对项数**: {result['total_checked_unique']}",
        f"- **缺失数**: {result['missing_count']}",
        "",
    ]
    if result["missing_count"]:
        lines.append("## 缺失项")
        for m in result["missing"]:
            lines.append(f"- L{m.get('line', '?')}: `{m.get('resolved_posix', m.get('url', ''))}` ({m.get('kind')})")
    else:
        lines.append("## 结果")
        lines.append("全部路径可解析且存在于仓库根下。")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="总清单 Markdown 路径严格核对")
    ap.add_argument(
        "--manifest",
        type=Path,
        default=REPO / "docs" / "01_FRAMEWORK" / "BLUEPRINT_STAGE_COMPLETE_SUMMARY.md",
        help="待核对的 Markdown 路径（相对仓库根或绝对）",
    )
    args = ap.parse_args()
    manifest = args.manifest
    if not manifest.is_absolute():
        manifest = (REPO / manifest).resolve()
    if not manifest.is_file():
        print(f"ERROR: manifest not found: {manifest}", file=sys.stderr)
        return 2

    result = check_manifest(manifest)
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", manifest.stem).upper() or "MANIFEST"
    write_reports(result, stem)

    print(f"Wrote: docs/09_AUDIT/STATE/MANIFEST_PATH_AUDIT_{stem}.json")
    print(f"Checked unique: {result['total_checked_unique']}, missing: {result['missing_count']}")

    if result["missing_count"]:
        for m in result["missing"]:
            print(f"  MISSING {m.get('kind')} L{m.get('line')}: {m.get('resolved_posix', m.get('url'))}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
