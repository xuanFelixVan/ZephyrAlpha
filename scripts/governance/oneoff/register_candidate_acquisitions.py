# [BLUEPRINT] MOD-GOV_ONEOFF_CANDREG | scripts/governance/oneoff/register_candidate_acquisitions.py | §cand-reg
# [MODULE] scripts.governance.oneoff.register_candidate_acquisitions
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] ruamel.yaml; scripts.governance.oneoff.load_acquisition_decisions (parse_decision_table, classify_acquisition)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 幂等：为49行无候选条目的候选态环节补登骨架候选条目（含acquisition）；按step_id去重，已存在条目不重复补登
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功; exit 1=失败
# [TESTS]
# [A_module] module_id=MOD-GOV_ONEOFF_CANDREG | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""register_candidate_acquisitions.py — 为49行无候选条目的候选态环节补登骨架候选条目

背景（裁定 2026-08-07）：
    候选态50行里，1行有候选条目（BM-RC-12-A→CAND-RSK-014，已回填 acquisition），
    49行无候选条目——环节在作战地图标记为候选态，但模块未登记到
    candidate_module_registry.yaml。本脚本为这49行补登骨架候选条目，
    让 acquisition 决策落地到 YAML SSoT（而非只留在决策表 md）。

数据流::
    inventory(候选态50行) + decision_table(候选态50行)
        → 按 step_id 关联
        → 排除已有候选条目（BM-RC-12-A）
        → 推断域（从 battle_map 文件名）
        → 生成 CAND-{缩写}-{序号} 骨架候选条目（含 acquisition）
        → 追加到 candidate_module_registry.yaml

骨架候选条目说明：
    只填关键字段（id/name/domain/description/status/acquisition/source_draft/original_id），
    其余字段留空/默认。等环节真正需要开发时，再补全 panorama_position/contracts 等。
    这符合"简单静态映射起步，逐步演进"原则。

用法::
    python scripts/governance/oneoff/register_candidate_acquisitions.py --dry-run
    python scripts/governance/oneoff/register_candidate_acquisitions.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: register_candidate_acquisitions.py — 为49行无候选条目的候选态环节补登骨架候选条目
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import sys
from datetime import date
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_ONEOFF_DIR = _THIS_FILE.parents[0]
if str(_ONEOFF_DIR) not in sys.path:
    sys.path.insert(0, str(_ONEOFF_DIR))

from load_acquisition_decisions import (  # noqa: E402
    classify_acquisition,
    parse_decision_table,
)

from zephyr.governance.persistence.battle_map_reader import BattleMapReader  # noqa: E402

# 源文档
_INVENTORY = _PROJECT_ROOT / "docs" / "_working" / "107_pending_steps_inventory.md"
_DECISION_TABLE = _PROJECT_ROOT / "docs" / "_working" / "107_decision_table_filled.md"
_CANDIDATE_REGISTRY = (
    _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    / "candidate_module_registry.yaml"
)

# battle_map 文件名 → (domain, id_abbrev) 映射
_FILE_TO_DOMAIN = {
    "battle_map_01_research_incubation": ("D_RESEARCH", "RES"),
    "battle_map_02_model_training": ("D_ML_TRAIN", "MLT"),
    "battle_map_04_simulation_validation": ("D_SIMULATION", "SIM"),
    "battle_map_05_stock_selection": ("D_SIGNAL", "SIG"),
    "battle_map_06_buy_flow": ("D_BUY", "BUY"),
    "battle_map_08_position_management": ("D_PF_ALLOC", "PFALLOC"),
    "battle_map_09_risk_control": ("D_RISK", "RSK"),
}


def parse_inventory_candidates(md_path: Path) -> list[dict]:
    """解析 inventory 的候选态段，返回 [{step_id, name_cn, name_en, layer, self_report, file_line}]。

    inventory 候选态段格式：
        | step_id | 中文名 | 英文名 | 层 | 自报 | 文件:行 |
    """
    text = md_path.read_text(encoding="utf-8")
    results: list[dict] = []
    in_candidate = False
    for line in text.splitlines():
        if line.startswith("### 🟨 候选态"):
            in_candidate = True
            continue
        if line.startswith("### 🟥 弃用态") or line.startswith("### 🟧 设计态"):
            in_candidate = False
            continue
        if not in_candidate or not line.startswith("|"):
            continue
        if line.startswith("|---") or line.startswith("|:--") or line.startswith("| step_id"):
            continue
        cols = [c.strip() for c in line.split("|")]
        cols = cols[1:-1]
        if not cols or not cols[0].startswith("BM-"):
            continue
        results.append({
            "step_id": cols[0],
            "name_cn": cols[1] if len(cols) > 1 else "",
            "name_en": cols[2] if len(cols) > 2 else "",
            "layer": cols[3] if len(cols) > 3 else "",
            "self_report": cols[4] if len(cols) > 4 else "",
            "file_line": cols[5] if len(cols) > 5 else "",
        })
    return results


def infer_domain(file_line: str) -> tuple[str, str]:
    """从 inventory 的'文件:行'推断 (domain, id_abbrev)。

    file_line 格式：battle_map_01_research_incubation.md:169
    """
    fname = file_line.split(":")[0].replace(".md", "")
    if fname in _FILE_TO_DOMAIN:
        return _FILE_TO_DOMAIN[fname]
    return ("D_UNKNOWN", "UNK")


def _step_ids_with_candidate_anchor() -> set[str]:
    """查询 battle_map_anchors，返回已有 candidate 锚点的 step_id 集合。

    这些环节由 load_acquisition_decisions.py 通过锚点→CAND-xxx 回填 acquisition，
    本脚本不重复为它们造骨架条目（避免 BM-RC-12-A 既更新 CAND-RSK-014 又造 CAND-RSK-021）。
    """
    sids: set[str] = set()
    reader = BattleMapReader()
    try:
        conn = reader._get_conn()
        cur = conn.execute(
            "SELECT step_id FROM battle_map_anchors WHERE target_graph = 'candidate'"
        )
        for row in cur.fetchall():
            sids.add(row["step_id"])
    finally:
        reader.close()
    return sids


def _next_seq(existing_ids: set[str], abbrev: str) -> int:
    """获取某缩写下的下一个序号（从已有 ID 推断最大值+1，最小 001）。"""
    max_seq = 0
    prefix = f"CAND-{abbrev}-"
    for eid in existing_ids:
        if eid.startswith(prefix):
            tail = eid[len(prefix):]
            try:
                n = int(tail)
                if n > max_seq:
                    max_seq = n
            except ValueError:
                pass
    return max_seq + 1


def build_skeleton_entry(
    cand_id: str,
    step_id: str,
    name_cn: str,
    name_en: str,
    domain: str,
    layer: str,
    self_report: str,
    file_line: str,
    method: str,
    source: str,
    today: str,
) -> dict:
    """构建骨架候选条目（最小字段，含 acquisition）。"""
    # status: 自报 production → deferred（待复核是否已实现）；design → candidate
    status = "deferred" if self_report == "production" else "candidate"
    name = f"{name_en} / {name_cn}" if name_en and name_cn else (name_cn or name_en)
    return {
        "id": cand_id,
        "name": name,
        "aliases": [step_id],
        "domain": domain,
        "domain_status": "active",
        "domain_node_count": 0,
        "sub_layer": layer,
        "panorama_position": {
            "depgraph": {"has_position": False, "note": f"候选态环节 {step_id}，未登记 depgraph"},
        },
        "description": f"候选态环节 {step_id}（{name_cn}）的骨架候选，承载 acquisition 决策。详情见 {file_line}",
        "capability": "",
        "problem_it_solves": "",
        "trigger_signals": [],
        "keywords": [step_id, "候选态环节补登"],
        "upstream_deps": [],
        "downstream_consumers": [],
        "contracts_to_produce": [],
        "contracts_to_consume": [],
        "prerequisites": [],
        "design_admission": {
            "q1_implemented": {"result": None, "evidence": "待复核"},
            "blocking_question": "none",
            "result": status,
        },
        "status": status,
        "priority": "P2",
        "created_at": today,
        "last_reviewed_at": today,
        "promoted_to": "",
        "source_draft": file_line,
        "source_section": "",
        "original_id": step_id,
        "estimated_complexity": "M",
        "estimated_effort": "",
        "tech_notes": "",
        "risks": [],
        "alternatives": "",
        "tags": ["候选态环节补登", "acquisition导入", f"layer:{layer}"],
        "search_terms": [step_id, name_cn, name_en],
        "related_candidates": [],
        "enables": [],
        "blocked_by": [],
        "next_review_date": "",
        "review_frequency": "yearly",
        "last_review_outcome": f"由 register_candidate_acquisitions.py 补登，承载 acquisition={method}/{source or '—'}",
        "acquisition_method": method,
        "acquisition_source": source,
    }


def main(dry_run: bool = False) -> int:
    """Entry point: parse args, run logic, return exit code."""
    # 1. 解析 inventory 候选态 + decision_table 候选态
    inv_candidates = parse_inventory_candidates(_INVENTORY)
    decisions = parse_decision_table(_DECISION_TABLE)
    cand_decisions = [d for d in decisions if d["category"] == "candidate"]
    print(f"[REG] inventory 候选态 {len(inv_candidates)} 行，决策表候选态 {len(cand_decisions)} 行")

    # 2. 按 step_id 关联
    inv_by_sid = {c["step_id"]: c for c in inv_candidates}
    dec_by_sid = {d["step_id"]: d for d in cand_decisions}
    all_sids = set(inv_by_sid) & set(dec_by_sid)
    print(f"[REG] 关联成功 {len(all_sids)} 行（交集）")

    # 3. 读取现有 YAML，获取已有条目 id + 已有 original_id（避免重复补登）
    from ruamel.yaml import YAML  # noqa: PLC0415

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    with _CANDIDATE_REGISTRY.open("r", encoding="utf-8") as f:
        data = yaml.load(f)
    entries = data.get("entries", []) or []
    existing_ids = {e.get("id", "") for e in entries}
    existing_originals = {e.get("original_id", "") for e in entries}
    print(f"[REG] 现有候选条目 {len(entries)}，已有 original_id {len(existing_originals)} 个")

    # 4. 为无候选条目的环节补登
    #    排除两类：(a) YAML 已有 original_id 匹配的；(b) battle_map_anchors 已有 candidate 锚点的
    #    （后者由 load_acquisition_decisions.py 通过锚点回填，本脚本不重复造条目）
    anchored_sids = _step_ids_with_candidate_anchor()
    print(f"[REG] battle_map_anchors 中已有 candidate 锚点的环节 {len(anchored_sids)} 个"
          f"（由 load 脚本回填，本脚本跳过）")
    today = date.today().isoformat()
    seq_counters: dict[str, int] = {}
    new_entries: list[dict] = []
    skipped_exists: list[str] = []
    skipped_anchored: list[str] = []
    skipped_no_classify: list[str] = []

    for sid in sorted(all_sids):
        if sid in existing_originals:
            skipped_exists.append(sid)
            continue
        if sid in anchored_sids:
            skipped_anchored.append(sid)
            continue
        inv = inv_by_sid[sid]
        dec = dec_by_sid[sid]
        method, source = classify_acquisition(dec["how_raw"], dec["source_raw"])
        if not method:
            skipped_no_classify.append(sid)
            continue
        domain, abbrev = infer_domain(inv["file_line"])
        # 序号：按缩写递增
        if abbrev not in seq_counters:
            seq_counters[abbrev] = _next_seq(existing_ids, abbrev)
        seq = seq_counters[abbrev]
        seq_counters[abbrev] = seq + 1
        cand_id = f"CAND-{abbrev}-{seq:03d}"
        existing_ids.add(cand_id)
        entry = build_skeleton_entry(
            cand_id, sid, inv["name_cn"], inv["name_en"], domain, inv["layer"],
            inv["self_report"], inv["file_line"], method, source, today,
        )
        new_entries.append(entry)
        print(f"  + {cand_id} ({sid}) {domain} = {method}/{source or '—'}")

    # 5. 追加到 YAML
    print(f"\n[REG] 补登 {len(new_entries)} 条，已存在跳过 {len(skipped_exists)} 条，"
          f"已有锚点跳过 {len(skipped_anchored)} 条，无法分类 {len(skipped_no_classify)} 条")
    if skipped_exists:
        print(f"  已存在(跳过): {skipped_exists}")
    if skipped_anchored:
        print(f"  已有锚点(由load回填): {skipped_anchored}")
    if skipped_no_classify:
        print(f"  无法分类: {skipped_no_classify}")

    if dry_run:
        print("\n[DRY RUN] 未实际写入。去掉 --dry-run 执行补登。")
        return 0

    if new_entries:
        for e in new_entries:
            entries.append(e)
        data["entries"] = entries
        with _CANDIDATE_REGISTRY.open("w", encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"\n[完成] 已追加 {len(new_entries)} 条骨架候选到 {_CANDIDATE_REGISTRY.name}")
        print(f"  候选条目总数: {len(entries)}（原 {len(entries) - len(new_entries)} + 新 {len(new_entries)}）")
    else:
        print("\n[完成] 无需补登（全部已存在）")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="为49行无候选条目的候选态环节补登骨架候选条目（含 acquisition）"
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印不写入")
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
