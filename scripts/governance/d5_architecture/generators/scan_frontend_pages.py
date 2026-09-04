# [BLUEPRINT] MOD-D_GOV_SCRIPTS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""前端页面扫描器（四件套 Phase 2；2026-09-04 双真源合并改造）——pages/*.html → web/frontend_map.yaml 全量建账（半自动）。

职责：把"前端有什么"从人肉盘点变成机器普查。每个页面抽取：
  - 页面标题（h2.page-title）
  - 功能点候选（card 内 h3/.lab/sec-title 标题）
  - backend_ref 自动提取：扫 core/<page>.js 的 /api/ 调用（fetchJson/ZK.api 路径字面量）
写入 src/zephyr/frontend/dashboard/web/frontend_map.yaml（★唯一真源，Owner 2026-09-04 裁定；
旧 architecture_model/frontend/frontend_map.yaml 已降级为废弃副本，勿再写入）：
  - 已有页面（page 字段已在册）跳过不覆盖——在册判定按扁平契约的 page 字段
  - 新页面写入 auto_scanned: true 标记（翻新会话到时转正为语义化 id）
  - 幂等：重复扫描不产生重复条目（按 feature id 去重）
用法：python scripts/governance/d5_architecture/generators/scan_frontend_pages.py [--apply]
  默认 dry-run 只打印统计；--apply 才写 frontend_map.yaml。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
WEB_PAGES = REPO / "src/zephyr/frontend/dashboard/web/pages"
WEB_CORE = REPO / "src/zephyr/frontend/dashboard/web/core"
MAP_FILE = REPO / "src/zephyr/frontend/dashboard/web/frontend_map.yaml"  # ★唯一真源（2026-09-04 裁定）

TAG_RE = re.compile(r"<[^>]+>")
PAGE_TITLE_RE = re.compile(r'<h2 class="page-title">(.*?)</h2>', re.S)
SEC_TITLE_RE = re.compile(r'<div class="sec-title"[^>]*>(.*?)</div>', re.S)
CARD_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
LAB_RE = re.compile(r'<div class="lab">(.*?)</div>', re.S)
BADGE_RE = re.compile(r'<span class="badge[^"]*">.*?</span>')
DIM_RE = re.compile(r'<span class="dim[^"]*">.*?</span>')
API_RE = re.compile(r"/api/[a-z0-9\-]+")


def clean(text: str) -> str:
    text = BADGE_RE.sub("", text)
    text = DIM_RE.sub("", text)
    text = TAG_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()[:60]


def scan_backend_ref(page_stem: str) -> str:
    """扫 core/<page>.js 的 /api/ 调用 → 类型化 backend_ref（扁平契约五前缀之一）。"""
    core = WEB_CORE / f"{page_stem}.js"
    if core.exists():
        apis = sorted(set(API_RE.findall(core.read_text(encoding="utf-8", errors="ignore"))))
        if apis:
            return "api:" + " × ".join(apis)
    return "none:待拆件盘点（auto 扫描未发现 /api/ 调用）"


def scan_page(path: Path) -> dict:
    """单页扫描 → {page_id, page_name, feature 扁平条目列表}。"""
    html = path.read_text(encoding="utf-8")
    pid = "P-" + path.stem.upper().replace("_", "-")
    m = PAGE_TITLE_RE.search(html)
    page_name = clean(m.group(1)) if m else path.stem

    titles: list[str] = []
    seen: set[str] = set()
    for regex in (SEC_TITLE_RE, CARD_H3_RE, LAB_RE):
        for raw in regex.findall(html):
            name = clean(raw)
            if not name or len(name) < 2 or name in seen:
                continue
            seen.add(name)
            titles.append(name)

    ref = scan_backend_ref(path.stem)
    entries = [
        {
            "id": f"F-{path.stem.upper()}-AUTO-{i + 1:02d}",
            "name": name,
            "page": path.stem,
            "module_id": f"{path.stem}-host",
            "file": f"core/{path.stem}.js",
            "backend_ref": ref,
            "status": "active",
            "auto_scanned": True,
        }
        for i, name in enumerate(titles)
    ]
    return {"page_id": pid, "page_name": page_name, "entries": entries}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际写入 frontend_map.yaml（默认 dry-run）")
    args = ap.parse_args()

    data = yaml.safe_load(MAP_FILE.read_text(encoding="utf-8"))
    features = data.setdefault("features", [])
    existing_pages = {f.get("page") for f in features}
    existing_ids = {f.get("id") for f in features}

    added, skipped = [], []
    for path in sorted(WEB_PAGES.glob("*.html")):
        scan = scan_page(path)
        if scan["page_id"].replace("P-", "") in existing_pages or path.stem in existing_pages:
            skipped.append(scan["page_id"])
            continue
        new = [e for e in scan["entries"] if e["id"] not in existing_ids]
        if not new:
            skipped.append(scan["page_id"])
            continue
        features.extend(new)
        added.append((scan["page_id"], scan["page_name"], len(new)))

    print(f"已在册页面（跳过）: {sorted(p for p in existing_pages if p)}")
    print(f"新增页面: {len(added)}")
    for pid, name, n in added:
        print(f"  + {pid} {name}（{n} 功能点）")

    if args.apply and added:
        data["updated"] = "2026-09-04"
        MAP_FILE.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=200),
            encoding="utf-8",
        )
        print(f"OK: 已写入 {MAP_FILE}")
    else:
        print("DRY-RUN（--apply 才落盘）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
