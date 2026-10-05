#!/usr/bin/env python3
# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §panorama_master_map
# [MODULE] scripts.governance.d5_architecture.generators.generate_panorama_master_map
# create-guard-not-dup: 本件=图之图渲染器（挂"图的索引"panorama_master_map）；CapabilityLookup 命中 panorama/sync_panorama 系词汇=同域邻居（全景图族各生成器各挂一图），非本能力第二实现，无 canonical 重叠。
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   （CLI 生成器按需触发，PERM-TRIGGER 手动铁律归 task_bound——q-0004 落库适配 2026-10-05
#   st-fig16-20261005 抢救批；原值=permanent 见死袋，同族先例=generate_strategy_card_lifecycle_map）
# [DEPENDENCIES] yaml; zephyr.shared.io.file_utils (safe_write_text, 延迟导入); docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md（§3 派生面，只读）
# [CONSUMERS] config/panorama_master_map.yaml（唯一真源，只读）; docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama_master_map.md（唯一产出物，禁手改后不回生成; 落点注记=chief 原定 config/*.mmd 撞 DCR-005 扩展名契约+架构图目录 gitignore 双墙，按图族范式改道与宪章§8 同址）; tests/gov/governance/generators/test_panorama_master_map.py（对抗三红）; alignment_checklist §3 注记行+align_all 第十七节
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 校验五条全绿才写盘（禁产半图）：①nodes 与 §3 在册图集双闭（多一张少一张都红；身份=map_id 直配否则 file stem 派生——TDMAP-001/DSCMAP-012/GOMAP-001 册面实名经 stem 对上 §3 行名）②file 实存+YAML frontmatter map_id 一致（无 map_id 键/非 YAML 锚=只验实存）③边端点在 node 集 ④axis ∈ {vertical, horizontal} ⑤relation_zh 非空；幂等=同输入两次产出逐字节等（禁 datetime.now()/time.time()，渲染零时间戳）；语义真源=master yaml 本件无内嵌图清单（禁双真源）；§3 派生=表行（blueprint.md 归一）∪「> 待转正」行 _map 词元（只扫 ## 3. 起 ## 4. 止）；写盘必经 safe_write_text（CAS）
# [MODIFY-GUARD] nodes/edges 增删改只动 config/panorama_master_map.yaml（新图准入：先落 §3 再落本图 nodes，双闭才放行）；产出渲染物禁手改后不回生成；「治理立法→GOMAP10」条件边待图16 立图裁定后随批增补，禁提前造边
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验 error>0=不写盘 exit 1（逐条 E1-E5 报因）；master YAML 缺失/损坏=exit 2 fail-closed；§3 区块不可解析（派生 0 图）=exit 2；写盘失败=exit 1；--check 零写入
# [TESTS] tests/gov/governance/generators/test_panorama_master_map.py（绿基线+三红：新图不入总图双向/边指幽灵/文件被删+幂等+fail-closed，tmp 副本宇宙）
"""全景总图（图之图）生成器：读 config/panorama_master_map.yaml → 校验五条 → 渲染 architecture_view .md（fenced mermaid）。

system_charter §8.3 AI 冷启动导航序的机生载体；节点集对账基准=alignment_checklist.md §3。
用法：
    python scripts/governance/d5_architecture/generators/generate_panorama_master_map.py          # 校验+渲染
    python scripts/governance/d5_architecture/generators/generate_panorama_master_map.py --check  # 只校验零写入
    python ... --root <repo_root> --master <yaml路径>                                              # 注入根（测试宇宙用）
退出码：0=全绿（--check 时零写入）；1=校验不绿/写盘失败；2=环境 fail-closed。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
MASTER_REL = "config/panorama_master_map.yaml"
RENDER_REL = "docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama_master_map.md"
CHECKLIST_REL = "docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md"
AXIS_ENUM = ("vertical", "horizontal")
_AXIS_SUBGRAPH_ZH = {"vertical": "纵轴·流程视图", "horizontal": "横轴·结构视图"}

_TABLE_ROW_RE = re.compile(r"^\|\s*\*\*([a-z0-9_.]+)\*\*（")
_PENDING_RE = re.compile(r"[a-z][a-z0-9_]*_map\b")
_SECTION3_START = "## 3."
_SECTION_END_RE = re.compile(r"^## \d")


def load_master(master_path: Path) -> dict:
    """读总图真源；缺失/损坏 fail-closed（exit 2 语义，由 main 落码）。"""
    if not master_path.is_file():
        raise FileNotFoundError(f"master yaml 不存在: {master_path}")
    data = yaml.safe_load(master_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        raise ValueError(f"master yaml 结构非法（缺 dict/nodes list）: {master_path}")
    if not isinstance(data.get("edges"), list):
        raise ValueError(f"master yaml 结构非法（缺 edges list）: {master_path}")
    return data


def parse_checklist_section3(checklist_text: str) -> set[str]:
    """从 alignment_checklist §3 区块派生在册图集（表行 ∪ 待转正行）。

    表行名归一：blueprint.md → blueprint（去 .md 尾缀）。派生 0 图=§3 结构漂移，调用方 fail-closed。
    """
    names: set[str] = set()
    in_section3 = False
    for line in checklist_text.splitlines():
        stripped = line.strip()
        if not in_section3:
            if stripped.startswith(_SECTION3_START):
                in_section3 = True
            continue
        if _SECTION_END_RE.match(stripped):
            break
        m = _TABLE_ROW_RE.match(line)
        if m:
            names.add(m.group(1).removesuffix(".md"))
            continue
        if stripped.startswith("> 待转正"):
            names.update(_PENDING_RE.findall(stripped))
    return names


def _node_identity(node: dict, section3_names: set[str]) -> str:
    """节点→§3 行名身份：map_id 直配，否则 YAML 真源图按 file stem 派生。"""
    map_id = str(node.get("map_id", ""))
    if map_id in section3_names:
        return map_id
    stem = Path(str(node.get("file", ""))).stem
    if stem in section3_names:
        return stem
    return map_id


def validate(master: dict, checklist_text: str, root: Path) -> tuple[list[str], list[str], dict]:
    """校验五条，返回 (errors, warnings, stats)。errors 非空=禁写盘。"""
    errors: list[str] = []
    warnings: list[str] = []
    nodes = master["nodes"]
    edges = master["edges"]

    section3_names = parse_checklist_section3(checklist_text)
    if not section3_names:
        errors.append("E0 §3 不可解析：alignment_checklist §3 派生 0 图（结构漂移，fail-closed）")
        return errors, warnings, {"nodes": len(nodes), "edges": len(edges)}

    # ① 节点集与 §3 在册图集双闭（含重复身份检测）
    identities: list[str] = []
    for n in nodes:
        identities.append(_node_identity(n, section3_names))
    dup = sorted({i for i in identities if identities.count(i) > 1})
    for d in dup:
        errors.append(f"E1 节点身份重复：{d}（两节点对到同一 §3 行）")
    missing = sorted(section3_names - set(identities))
    extra = sorted(set(identities) - section3_names)
    for mid in missing:
        errors.append(f"E1 少节点：§3 在册图 {mid} 未入总图")
    for mid in extra:
        errors.append(f"E1 多节点：总图节点 {mid} 不在 §3 在册图集（新图先落 §3 再落总图）")

    # ② file 实存 + YAML map_id 一致
    known_ids: set[str] = set()
    for n in nodes:
        map_id = str(n.get("map_id", ""))
        known_ids.add(map_id)
        rel = str(n.get("file", ""))
        f = root / rel
        if not rel or not f.is_file():
            errors.append(f"E2 文件缺失：node {map_id} 的 file 不存在: {rel}")
            continue
        if f.suffix == ".yaml":
            try:
                meta = yaml.safe_load(f.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                errors.append(f"E2 YAML 损坏：node {map_id} 的 file 解析失败: {rel}（{exc}）")
                continue
            if isinstance(meta, dict) and "map_id" in meta and meta["map_id"] != map_id:
                errors.append(f"E2 map_id 不一致：node 声明 {map_id}，file frontmatter 为 {meta['map_id']}（{rel}）")

    # ③④⑤ 边端点/轴枚举/关系非空（含必填字段结构面）
    for idx, e in enumerate(edges):
        label = f"edge[{idx}]"
        if not isinstance(e, dict):
            errors.append(f"E0 {label} 非对象")
            continue
        frm, to = str(e.get("from", "")), str(e.get("to", ""))
        if frm not in known_ids or to not in known_ids:
            errors.append(
                f"E3 边端点不在节点集：{label} {frm}→{to}"
                f"（缺{'from' if frm not in known_ids else ''}"
                f"{'+' if frm not in known_ids and to not in known_ids else ''}"
                f"{'to' if to not in known_ids else ''}）"
            )
        if e.get("axis") is not None:
            errors.append(f"E0 {label} 含非法字段 axis（axis 属节点不属于边）")
        if not str(e.get("relation_zh", "")).strip():
            errors.append(f"E5 relation_zh 为空：{label} {frm}→{to}")
    for n in nodes:
        map_id = str(n.get("map_id", ""))
        for field in ("name_zh", "file", "one_line_zh"):
            if not str(n.get(field, "")).strip():
                errors.append(f"E0 节点 {map_id} 缺必填字段 {field}")
        if n.get("axis") not in AXIS_ENUM:
            errors.append(f"E4 axis 非法：node {map_id} axis={n.get('axis')!r}（枚举 vertical|horizontal）")

    stats = {
        "nodes": len(nodes),
        "edges": len(edges),
        "vertical": sum(1 for n in nodes if n.get("axis") == "vertical"),
        "horizontal": sum(1 for n in nodes if n.get("axis") == "horizontal"),
        "section3_registered": len(section3_names),
    }
    pending = sorted({str(n.get("map_id")) for n in nodes if "待转正" in str(n.get("one_line_zh", ""))})
    if pending:
        warnings.append("待转正图在册（随转正批转正式）: " + ", ".join(pending))
    return errors, warnings, stats


def _mmd_node_id(map_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", map_id)


def render_mermaid(master: dict, stats: dict) -> str:
    """渲染 architecture_view .md（frontmatter+计数+fenced mermaid）；顺序=真源 yaml 顺序，零时间戳，幂等。"""
    nodes = master["nodes"]
    lines = [
        "---",
        "doc_type: architecture_view",
        "title: 全景总图（图之图）",
        'version: "1.0"',
        "status: active",
        "date: auto-generated",
        "owner: auto-generator",
        "ttl: permanent",
        "---",
        "",
        "# 全景总图（图之图）",
        "",
        f"> 机生渲染，禁手改后不回生成。真源: {MASTER_REL}"
        f"（nodes={stats['nodes']} edges={stats['edges']}"
        f" | 纵轴={stats['vertical']} 横轴={stats['horizontal']}）；"
        f"对账基准: {CHECKLIST_REL} §3（在册 {stats['section3_registered']} 图，双闭校验随生成器）。",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for axis in AXIS_ENUM:
        axis_nodes = [n for n in nodes if n.get("axis") == axis]
        if not axis_nodes:
            continue
        lines.append(f'    subgraph {axis.upper()}["{_AXIS_SUBGRAPH_ZH[axis]}"]')
        for n in axis_nodes:
            label = f"{n['name_zh']}<br/>{n['map_id']}"
            lines.append(f'        {_mmd_node_id(str(n["map_id"]))}["{label}"]')
        lines.append("    end")
    lines.append("")
    for e in master["edges"]:
        rel = str(e.get("relation_zh", "")).replace('"', "'")
        lines.append(f'    {_mmd_node_id(str(e["from"]))} -->|"{rel}"| {_mmd_node_id(str(e["to"]))}')
    lines.append("```")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="全景总图（图之图）生成器（校验五条+mermaid 渲染）")
    parser.add_argument("--check", action="store_true", help="只校验零写入")
    parser.add_argument("--root", default=str(_REPO_ROOT), help="仓库根注入（测试宇宙用）")
    parser.add_argument(
        "--master", default=None, help="master yaml 路径覆盖（默认 <root>/config/panorama_master_map.yaml）"
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    master_path = Path(args.master) if args.master else root / MASTER_REL
    try:
        master = load_master(master_path)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as exc:
        print(f"[FAIL-CLOSED] {exc}", file=sys.stderr)
        return 2
    checklist_path = root / CHECKLIST_REL
    if not checklist_path.is_file():
        print(f"[FAIL-CLOSED] 对账基准不存在: {checklist_path}", file=sys.stderr)
        return 2
    checklist_text = checklist_path.read_text(encoding="utf-8")

    errors, warnings, stats = validate(master, checklist_text, root)
    for w in warnings:
        print(f"[WARN] {w}")
    if errors:
        for e in errors:
            print(f"[ERROR] {e}")
        print(
            f"[RESULT] 校验不绿：errors={len(errors)} nodes={stats['nodes']} edges={stats['edges']}（禁产半图，零写入）"
        )
        return 1

    print(
        f"[OK] 校验五条全绿：nodes={stats['nodes']}（纵轴={stats['vertical']} 横轴={stats['horizontal']}）"
        f" edges={stats['edges']} §3在册={stats['section3_registered']}"
    )
    if args.check:
        print("[CHECK] 零写入模式，跳过渲染")
        return 0

    render_path = root / RENDER_REL
    content = render_mermaid(master, stats)
    from zephyr.shared.io.file_utils import safe_write_text  # 延迟导入（同族先例）

    result = safe_write_text(render_path, content)
    if not getattr(result, "ok", True):
        print(f"[FAIL] 写盘失败: {render_path}（{getattr(result, 'detail', '')}）", file=sys.stderr)
        return 1
    print(f"[RENDER] {RENDER_REL}（{len(content.splitlines())} 行，幂等渲染零时间戳）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
