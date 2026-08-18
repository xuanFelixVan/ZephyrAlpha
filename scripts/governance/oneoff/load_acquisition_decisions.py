# [BLUEPRINT] MOD-GOV_ONEOFF_ACQLOAD | scripts/governance/oneoff/load_acquisition_decisions.py | §acq-load
# [MODULE] scripts.governance.oneoff.load_acquisition_decisions
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.apply_depgraph (update_module_metadata); zephyr.governance.persistence.battle_map_reader (BattleMapReader); zephyr.governance.persistence.depgraph_reader; ruamel.yaml
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等导入：解析107决策表→设计态57行导入depgraph nodes_metadata(UPSERT)→候选态回填candidate_module_registry.yaml→弃用态跳过；emoji分类+step→path锚点解析；重复执行不报错
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_ACQLOAD | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""load_acquisition_decisions.py — 把 107 环节决策表的"怎么搞到手"导入模块生命周期

数据流（裁定 2026-08-07，分层 SSoT）::

    决策表 md (107行录入源)
        ├─ 设计态57行 → depgraph nodes_metadata.acquisition_method (PG 权威)
        ├─ 候选态50行 → candidate_module_registry.yaml.acquisition_method (YAML 意向)
        └─ 弃用态3行  → 跳过

设计态导入路径：
    step_id → battle_map_anchors(depgraph, primary) → MOD-xxx(blueprint_id)
            → nodes.path → update_module_metadata(path, {acquisition_method, acquisition_source})
    无 primary 时 fallback supplement（如 BM-BT-08 → MOD-BT-025）
    都无则跳过（决策表 md 暂存）

emoji 分类（枚举真源 = DDL CHECK 约束）：
    🔴 → self_build   🟢 → opensource   🟡 → borrow   ⬜ → deprecate
    🔄 或"后置" → acquisition_source 追加 " (后置)"，不另设枚举值

幂等：update_module_metadata 是 UPSERT；YAML 回填是覆盖写；重复执行不报错。

用法::

    python scripts/governance/oneoff/load_acquisition_decisions.py --dry-run
    python scripts/governance/oneoff/load_acquisition_decisions.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: load_acquisition_decisions.py — 把 107 环节决策表的"怎么搞到手"导入模块生命周期
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[3]  # d:/ZephyrAlpha
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_GOV_DIR = _THIS_FILE.parents[1]  # scripts/governance
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from apply_depgraph import update_module_metadata  # noqa: E402

from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402

# 决策表真源（107 行录入源，task_bound）
_DECISION_TABLE = _PROJECT_ROOT / "docs" / "_working" / "107_decision_table_filled.md"
# 候选模块注册表（YAML SSoT）
_CANDIDATE_REGISTRY = (
    _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    / "candidate_module_registry.yaml"
)

# emoji → acquisition_method 映射（枚举真源 = DDL CHECK，此处仅展示层映射）
_EMOJI_TO_METHOD = {
    "🔴": "self_build",
    "🟢": "opensource",
    "🟡": "borrow",
    "⬜": "deprecate",
}


def parse_decision_table(md_path: Path) -> list[dict]:
    """解析 107 决策表 markdown，返回决策列表。

    按 "## 一、设计态" / "## 二、候选态" / "## 三、弃用态" 分段，
    解析每段 markdown 表格行（| BM-xxx | ... | 🎯怎么搞 | ... | ... |）。

    弃用态表格是 4 列（无开源候选），设计态/候选态是 5 列。

    :return: [{step_id, category, how_raw, reason, source_raw}, ...]
    """
    text = md_path.read_text(encoding="utf-8")
    decisions: list[dict] = []
    category: str | None = None
    for line in text.splitlines():
        if line.startswith("## 一、设计态"):
            category = "design"
            continue
        if line.startswith("## 二、候选态"):
            category = "candidate"
            continue
        if line.startswith("## 三、弃用态"):
            category = "deprecate"
            continue
        if line.startswith("## ") or line.startswith("# "):
            # 其他章节（如"## 总览统计"/"## 四、按决策类型汇总"）——停止当前段解析
            category = None
            continue
        if not category or not line.startswith("|"):
            continue
        # 跳过分隔行（|---|---|...）和表头行（| step_id | ...）
        if line.startswith("|---") or line.startswith("|:--"):
            continue
        cols = [c.strip() for c in line.split("|")]
        cols = cols[1:-1]  # 去掉首尾空（line 以 | 开头/结尾产生空串）
        if not cols or not cols[0].startswith("BM-"):
            continue  # 表头或非数据行
        step_id = cols[0]
        how_raw = cols[2] if len(cols) > 2 else ""
        reason = cols[3] if len(cols) > 3 else ""
        source_raw = cols[4] if len(cols) > 4 else ""
        decisions.append({
            "step_id": step_id,
            "category": category,
            "how_raw": how_raw,
            "reason": reason,
            "source_raw": source_raw,
        })
    return decisions


def classify_acquisition(how_raw: str, source_raw: str) -> tuple[str | None, str]:
    """emoji → (acquisition_method, acquisition_source)。

    🔴→self_build, 🟢→opensource, 🟡→borrow, ⬜→deprecate
    🔄 或"后置" → source 追加 " (后置)"，不另设枚举值
    source_raw 去掉 ** 加粗；"—" 视为空。

    :return: (method, source)；无法分类时 method=None
    """
    method: str | None = None
    for emoji, m in _EMOJI_TO_METHOD.items():
        if emoji in how_raw:
            method = m
            break
    postponed = ("🔄" in how_raw) or ("后置" in how_raw)
    source = source_raw.replace("**", "").strip()
    if source == "—":
        source = ""
    if postponed:
        source = f"{source} (后置)" if source else "(后置)"
    return method, source


def _blueprint_id_to_path(blueprint_id: str, conn) -> str | None:
    """MOD-xxx (blueprint_id) → nodes.path。"""
    cur = conn.execute(
        "SELECT path FROM nodes WHERE blueprint_id = %s LIMIT 1", (blueprint_id,)
    )
    row = cur.fetchone()
    return row["path"] if row else None


def resolve_step_to_path(step_id: str, bm_conn) -> tuple[str | None, str]:
    """step_id → primary depgraph 锚点 → MOD-xxx → nodes.path。

    无 primary 时 fallback supplement（如 BM-BT-08 → MOD-BT-025 supplement）。
    都无则返回 (None, 'no_anchor')。

    :return: (path, role_used) 或 (None, 'no_anchor')
    """
    for role in ("primary", "supplement"):
        cur = bm_conn.execute(
            "SELECT target_id FROM battle_map_anchors "
            "WHERE step_id = %s AND target_graph = %s AND target_role = %s",
            (step_id, "depgraph", role),
        )
        rows = cur.fetchall()
        if not rows:
            continue
        tid = rows[0]["target_id"]
        path = _blueprint_id_to_path(tid, bm_conn)
        if path:
            return path, role
    return None, "no_anchor"


def update_candidate_yaml(
    step_id: str, method: str, source: str, yaml_path: Path, dry_run: bool
) -> tuple[bool, str]:
    """候选态：step_id → candidate 锚点 → CAND-xxx → YAML 条目回填 acquisition 字段。

    用 ruamel.yaml 保留注释/格式。幂等（覆盖写）。

    :return: (ok, msg) msg 为 CAND-xxx 或跳过原因
    """
    reader = BattleMapReader()
    try:
        conn = reader._get_conn()
        cur = conn.execute(
            "SELECT target_id FROM battle_map_anchors "
            "WHERE step_id = %s AND target_graph = %s",
            (step_id, "candidate"),
        )
        rows = cur.fetchall()
    finally:
        reader.close()
    if not rows:
        return False, "无candidate锚点，决策表暂存"
    cand_id = rows[0]["target_id"]

    from ruamel.yaml import YAML  # noqa: PLC0415 — 延迟导入，仅候选态回填需要

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096  # 防长行折行
    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    for entry in data.get("entries", []) or []:
        if entry.get("id") == cand_id:
            entry["acquisition_method"] = method
            entry["acquisition_source"] = source
            if not dry_run:
                with yaml_path.open("w", encoding="utf-8") as f:
                    yaml.dump(data, f)
            return True, cand_id
    return False, f"{cand_id} 在 YAML 未找到"


def main(dry_run: bool = False) -> int:
    """Entry point: parse args, run logic, return exit code."""
    if not _DECISION_TABLE.exists():
        print(f"ERROR: 决策表不存在: {_DECISION_TABLE}", file=sys.stderr)
        return 1
    decisions = parse_decision_table(_DECISION_TABLE)
    print(f"[LOAD] 解析决策表 {len(decisions)} 行（设计态/候选态/弃用态）")

    # 按 category 统计
    by_cat: dict[str, int] = {}
    for d in decisions:
        by_cat[d["category"]] = by_cat.get(d["category"], 0) + 1
    print(f"[LOAD]   分布: {by_cat}")

    reader = BattleMapReader()
    bm_conn = reader._get_conn()

    stats = {
        "design_ok": 0,
        "design_skip_no_anchor": 0,
        "design_skip_no_method": 0,
        "cand_ok": 0,
        "cand_skip": 0,
        "deprecate": 0,
    }
    skips: list[str] = []

    try:
        for d in decisions:
            sid = d["step_id"]
            method, source = classify_acquisition(d["how_raw"], d["source_raw"])
            if not method:
                stats["design_skip_no_method" if d["category"] == "design" else "cand_skip"] += 1
                skips.append(f"{sid}: 无法分类 how_raw={d['how_raw']!r}")
                continue

            if d["category"] == "design":
                path, role = resolve_step_to_path(sid, bm_conn)
                if path:
                    if dry_run:
                        ok = True
                    else:
                        ok = update_module_metadata(
                            path, {"acquisition_method": method, "acquisition_source": source}
                        )
                    if ok:
                        stats["design_ok"] += 1
                        print(f"  OK  {sid} -> {path} ({role}) = {method}/{source or '—'}")
                    else:
                        stats["design_skip_no_anchor"] += 1
                        skips.append(f"{sid}: update_module_metadata 失败 path={path}")
                else:
                    stats["design_skip_no_anchor"] += 1
                    skips.append(f"{sid}: 无 depgraph 锚点（决策表暂存）")
            elif d["category"] == "candidate":
                ok, msg = update_candidate_yaml(sid, method, source, _CANDIDATE_REGISTRY, dry_run)
                if ok:
                    stats["cand_ok"] += 1
                    print(f"  OK  {sid} -> YAML {msg} = {method}/{source or '—'}")
                else:
                    stats["cand_skip"] += 1
                    skips.append(f"{sid}: {msg}")
            else:  # deprecate
                stats["deprecate"] += 1
                print(f"  SKIP {sid}: 弃用态 ({method})")
    finally:
        reader.close()

    # 报告
    print("\n=== 导入报告 ===")
    print(f"  设计态成功:     {stats['design_ok']}")
    print(f"  设计态跳过(无锚点): {stats['design_skip_no_anchor']}")
    print(f"  设计态跳过(无分类): {stats['design_skip_no_method']}")
    print(f"  候选态回填YAML: {stats['cand_ok']}")
    print(f"  候选态跳过:     {stats['cand_skip']}")
    print(f"  弃用态跳过:     {stats['deprecate']}")
    if skips:
        print(f"\n  跳过明细 ({len(skips)}):")
        for s in skips:
            print(f"    - {s}")
    if dry_run:
        print("\n[DRY RUN] 未实际写入。去掉 --dry-run 执行导入。")
    else:
        print("\n[完成] 下一步: 重新生成作战地图 generate_battle_map_diagram.py")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="把 107 决策表'怎么搞到手'导入 depgraph nodes_metadata + candidate_module_registry.yaml"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
