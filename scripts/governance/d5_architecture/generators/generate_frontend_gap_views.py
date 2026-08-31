"""前端缺口视图派生器（四件套 4c）——两本缺口总账的机器派生替代。

真源：architecture_model/frontend/frontend_map.yaml（前端侧清单）+ depgraph nodes 前端覆盖三字段（模块侧）。
派生规则（四件套草案 §4.3）：
  - 前端有后端没有 = frontend_map 功能点 backend_ref 空/悬空
  - 后端有前端没有 = nodes.has_frontend='yes'/'planned' 但 frontend_ref 空或指向不存在的功能点
  - 对账异常       = has_frontend='no' 但 no_frontend_reason 空（"事出有因"必填）
输出：docs/_working/2026-08-31-frontend-gap-views-derived.md（派生物，禁手改； ttl=task_bound）
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts" / "governance"))
sys.path.insert(0, str(REPO / "src"))

from _shared.constants import get_depgraph_pg_connection  # noqa: E402

FRONTEND_MAP = REPO / "architecture_model/frontend/frontend_map.yaml"
OUT = REPO / "docs/_working/2026-08-31-frontend-gap-views-derived.md"


def load_frontend_features() -> dict[str, dict]:
    """frontend_map.yaml → {feature_id: {page, name, backend_ref, status}}。"""
    data = yaml.safe_load(FRONTEND_MAP.read_text(encoding="utf-8"))
    features: dict[str, dict] = {}
    for page in data.get("pages", []):
        pid = page["id"]
        for mod in page.get("modules", []):
            for feat in mod.get("features", []):
                features[feat["id"]] = {
                    "page": pid,
                    "name": feat.get("name", ""),
                    "backend_ref": feat.get("backend_ref") or [],
                    "status": feat.get("status", ""),
                }
    return features


def main() -> int:
    features = load_frontend_features()

    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        rows = conn.execute(
            "SELECT blueprint_id, has_frontend, no_frontend_reason, frontend_ref "
            "FROM nodes WHERE blueprint_id IS NOT NULL AND blueprint_id != '' "
            "AND (has_frontend != 'no' OR no_frontend_reason != '' OR frontend_ref != '')"
        ).fetchall()
    finally:
        conn.close()
    modules = [dict(r) for r in rows]

    # 派生：前端有后端没有
    gap_a = [(fid, f) for fid, f in features.items() if not f["backend_ref"]]
    # 派生：后端有前端没有（声明有/计划有前端，但 frontend_ref 空或指向不存在功能点）
    gap_b = []
    dangling = []
    for m in modules:
        refs = [r for r in (m.get("frontend_ref") or "").split(",") if r]
        f_refs = [r for r in refs if r.startswith("F-")]
        missing = [r for r in f_refs if r not in features]
        if m["has_frontend"] in ("yes", "planned") and not refs:
            gap_b.append(m)
        if missing:
            dangling.append((m, missing))
    # 派生：对账异常
    anomalies = [m for m in modules if m["has_frontend"] == "no" and not (m.get("no_frontend_reason") or "")]

    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    lines = [
        "---",
        "ttl: task_bound",
        "---",
        "",
        "> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，"
        "**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。"
        "取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。",
        "",
        f"# 前端缺口视图（派生活账） · {now}",
        "",
        f"## A. 前端有 → 后端没有（{len(gap_a)} 项：frontend_map 功能点 backend_ref 空）",
        "",
        "| 功能点 | 页面 | 名称 | 状态 |",
        "|---|---|---|---|",
    ]
    for fid, f in gap_a:
        lines.append(f"| {fid} | {f['page']} | {f['name']} | {f['status']} |")
    lines += [
        "",
        f"## B. 后端有 → 前端没有（{len(gap_b)} 项：has_frontend=yes/planned 但 frontend_ref 空）",
        "",
        "| 模块 | has_frontend | 说明 |",
        "|---|---|---|",
    ]
    for m in gap_b:
        lines.append(f"| {m['blueprint_id']} | {m['has_frontend']} | 声明有前端但未挂功能点 |")
    lines += [
        "",
        f"## C. 悬空引用（{len(dangling)} 项：frontend_ref 指向 frontend_map 不存在的功能点）",
        "",
        "| 模块 | 悬空引用 |",
        "|---|---|",
    ]
    for m, missing in dangling:
        lines.append(f"| {m['blueprint_id']} | {', '.join(missing)} |")
    lines += [
        "",
        f"## D. 对账异常（{len(anomalies)} 项：has_frontend=no 但未填理由）",
        "",
    ]
    for m in anomalies:
        lines.append(f"- {m['blueprint_id']}")
    lines += [
        "",
        "## 统计",
        "",
        f"- frontend_map 功能点总数: {len(features)}",
        f"- depgraph 已声明前端覆盖模块数: {len(modules)}",
        f"- A/B/C/D 四类缺口: {len(gap_a)} / {len(gap_b)} / {len(dangling)} / {len(anomalies)}",
        "",
    ]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: {OUT} (A={len(gap_a)} B={len(gap_b)} C={len(dangling)} D={len(anomalies)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
