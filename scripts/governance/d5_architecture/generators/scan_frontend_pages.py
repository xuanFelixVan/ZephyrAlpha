"""前端页面扫描器（四件套 Phase 2）——pages/*.html → frontend_map.yaml 全量建账（半自动）。

职责：把"前端有什么"从人肉盘点变成机器普查。每个页面抽取：
  - 页面标题（h2.page-title）
  - 模块候选（data-mod 块 / sec-title 分区）
  - 功能点候选（card 内 h3/.lab 标题）
合并进 architecture_model/frontend/frontend_map.yaml：
  - 已有页面（手工精修的 stockq/overview）跳过不覆盖
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
MAP_FILE = REPO / "architecture_model/frontend/frontend_map.yaml"

TAG_RE = re.compile(r"<[^>]+>")
PAGE_TITLE_RE = re.compile(r'<h2 class="page-title">(.*?)</h2>', re.S)
DATA_MOD_RE = re.compile(r'data-mod="([^"]+)"[^>]*data-mod-name="([^"]*)"')
SEC_TITLE_RE = re.compile(r'<div class="sec-title"[^>]*>(.*?)</div>', re.S)
CARD_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
LAB_RE = re.compile(r'<div class="lab">(.*?)</div>', re.S)
BADGE_RE = re.compile(r'<span class="badge[^"]*">.*?</span>')
DIM_RE = re.compile(r'<span class="dim[^"]*">.*?</span>')


def clean(text: str) -> str:
    text = BADGE_RE.sub("", text)
    text = DIM_RE.sub("", text)
    text = TAG_RE.sub("", text)
    return re.sub(r"\s+", " ", text).strip()[:60]


def scan_page(path: Path) -> dict:
    """单页扫描 → {id, name, modules:[{id, name, features:[...]}]}。"""
    html = path.read_text(encoding="utf-8")
    pid = "P-" + path.stem.upper().replace("_", "-")
    m = PAGE_TITLE_RE.search(html)
    page_name = clean(m.group(1)) if m else path.stem

    modules: list[dict] = []
    seen_mods: set[str] = set()
    for mod_id, mod_name in DATA_MOD_RE.findall(html):
        if mod_id in seen_mods:
            continue
        seen_mods.add(mod_id)
        modules.append({"id": f"M-{mod_id.upper().replace('_', '-')}", "name": mod_name or mod_id})

    features: list[dict] = []
    seen_titles: set[str] = set()
    for regex in (SEC_TITLE_RE, CARD_H3_RE, LAB_RE):
        for raw in regex.findall(html):
            name = clean(raw)
            if not name or len(name) < 2 or name in seen_titles:
                continue
            seen_titles.add(name)
            features.append(name)

    # 模块为空时挂一个默认模块（页面级功能点直挂）
    if not modules:
        modules = [{"id": "M-MAIN", "name": "页面主体"}]

    feat_entries = [
        {
            "id": f"{pid}-AUTO-{i+1:02d}",
            "name": name,
            "code_ref": f"pages/{path.name}",
            "backend_ref": [],
            "interaction": "",
            "status": "已建",
            "auto_scanned": True,
        }
        for i, name in enumerate(features)
    ]
    # 功能点挂到第一个模块（粗粒度，翻新会话再细分）
    modules[0]["features"] = feat_entries
    return {"id": pid, "name": page_name, "route": f"#{path.stem}", "file": f"pages/{path.name}", "modules": modules}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际写入 frontend_map.yaml（默认 dry-run）")
    args = ap.parse_args()

    data = yaml.safe_load(MAP_FILE.read_text(encoding="utf-8"))
    existing_pages = {p["id"] for p in data.get("pages", [])}

    added, skipped = [], []
    for path in sorted(WEB_PAGES.glob("*.html")):
        page = scan_page(path)
        if page["id"] in existing_pages:
            skipped.append(page["id"])
            continue
        data["pages"].append(page)
        n_feat = sum(len(m.get("features", [])) for m in page["modules"])
        added.append((page["id"], page["name"], n_feat))

    print(f"已在册（跳过）: {sorted(existing_pages)}")
    print(f"新增页面: {len(added)}")
    for pid, name, n in added:
        print(f"  + {pid} {name}（{n} 功能点）")

    if args.apply and added:
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
