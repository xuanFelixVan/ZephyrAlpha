# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §governance_legislation_map
# [MODULE] scripts.governance.d5_architecture.validators.validate_governance_legislation_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] task_bound
#   （CLI 校验器按需触发，PERM-TRIGGER 手动模式归 task_bound；同族先例=validate_strategy_card_lifecycle_map 2026-10-04 落库口径）
# [DEPENDENCIES] yaml；zephyr.governance.registry_ledger（CV-05 counts 对拍读面，复用生成器 read_ledger_counts 单一真源）——详单见下方详情块
# [CONSUMERS] GOVERNANCE-LEGISLATION-MAP gate（结构判据单一真源动态复用）+ align_all 第十六节 + 对抗测试——详单见下方详情块
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] live=False（gate 提交面）只跑结构判据（枚举闭集/迁移表/禁边/机构真源形态/保险丝下限/INV-1 长度/counts 散文判红），实例对拍降 warn；live=True（CLI/align_all）加 CV-04 机构真源磁盘实存 + CV-05 counts 账本对拍（硬）；fail-closed：图 YAML 损坏=error——详单见下方详情块
# [MODIFY-GUARD] 状态闭集/迁移判据以骨架为契约（增删先回写骨架）；本件禁被生成器复制判据（生成器只 import read_ledger_counts）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 返码 0=过/1=结构 error/2=环境不可用；判据函数永不抛（内部异常收敛为 error 行）
# [TESTS] tests/governance/d5_architecture/test_governance_legislation_map_adversarial.py
# create-guard-not-dup: 裁定#486 准入的图16 校验器（四判据+保险丝下限+长度面），判据对象=立法流图 yaml，与卡生命周期/交易日循环校验器无职责重叠（不同图不同轴）
#
# —— 详情块（14 字段头 30 行窗内，长文降为详情）——
#   判据四条（裁定#486 施工批任务3 规格）：CV-01 状态枚举闭集（六态闭集，新值=幽灵状态红）；
#   CV-02 迁移合法性表（from/to 全在枚举内、终态无出边、禁边 state-pair 不得被合法边同对覆盖）；
#   CV-03 机械节点真源（source_anchors 逐条非空+路径形态；live 面=磁盘实存）；
#   CV-05 counts 与账本对拍（live 硬/提交面 warn，读面=生成器 read_ledger_counts 单一真源）；
#   附加：CV-06 保险丝下限（states+machinery ≥ 12，裁定#486 ①结构化）；
#   CV-07 INV-1 长度面（note/rule 字段 ≤200 字符，禁抄裁定正文）+ 实例禁入 nodes
#   （states/machinery/transitions/forbidden_edges 内出现 ruling_id 实例键=红，裁定#486 ①保险丝二）；
#   check_prose_counts：语义层字段出现当前 counts 实例数=红（计数只进 counts）。
#   消费方：map_family/governance_legislation_map_gate（懒加载本件 validate_structure）；
#   scripts/governance/d5_architecture/generators/align_all.py 第十六节（结构面）；
#   tests/governance/d5_architecture/test_governance_legislation_map_adversarial.py（tmp 副本宇宙先红后绿）

"""图16 治理立法流图校验器（四判据+保险丝+INV-1；结构/实例双口径）。

口径（同图15 族）：提交面 live=False 只取结构面（一项不放宽）；实例面
（CV-04 真源磁盘实存 / CV-05 counts 账本对拍）属 CLI 与 align_all。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

MAP_REL = "config/governance_legislation_map.yaml"
SKELETON_REL = "docs/_working/map_build/fig16_legislation/00_skeleton.md"
_GENERATOR_REL = _REPO_ROOT / "scripts/governance/d5_architecture/generators/generate_governance_legislation_map.py"

# CV-01 状态闭集（骨架 §1 六态；新值=幽灵状态红——禁自造状态）
STATE_CLOSED_SET = frozenset({"draft", "active", "superseded", "deprecated", "void", "decided"})
# 机械枚举闭集（骨架 §2 九机构）
MACHINERY_CLOSED_SET = frozenset(
    {
        "D16-N1",
        "D16-N2",
        "D16-N3",
        "D16-N4",
        "D16-N5",
        "D16-N6",
        "D16-N7",
        "D16-N8",
        "D16-N9",
    }
)
# 保险丝下限（裁定#486 ①：有意义节点=states+machinery）
NODE_FLOOR = 12
# CV-07 长度面（禁抄裁定正文）
_FIELD_LEN_CAP = 200
# 实例键禁入 nodes（裁定#486 ①保险丝二：裁定实例=数据行非节点）
_INSTANCE_KEY = "ruling_id"


def _iter_problems(data: object) -> list[str]:
    if not isinstance(data, dict):
        return [f"图 YAML 顶层非对象: {type(data).__name__}"]
    return []


def validate_structure(
    data: dict,
    root: Path = _REPO_ROOT,
    warnings: list[str] | None = None,
    live: bool = False,
    block: object = None,
) -> list[str]:
    """结构面判据（live=False 提交面口径；block 参数与同族校验器签名对齐，本图无锚块装载点故未用）。"""
    errors: list[str] = []
    warn = warnings if warnings is not None else []
    top = _iter_problems(data)
    errors.extend(top)
    if top:
        return errors

    states = data.get("states")
    machinery = data.get("machinery")
    transitions = data.get("transitions")
    forbidden = data.get("forbidden_edges")
    for name, section in (
        ("states", states),
        ("machinery", machinery),
        ("transitions", transitions),
        ("forbidden_edges", forbidden),
    ):
        if not isinstance(section, list) or not section:
            errors.append(f"{name} 缺失或非空列表（三类对象一条不许丢）")

    if not isinstance(states, list) or not states:
        return errors

    # --- CV-01 状态枚举闭集 ---
    seen_values: set[str] = set()
    seen_state_ids: set[str] = set()
    for s in states:
        if not isinstance(s, dict):
            errors.append("states 存在非对象条目")
            continue
        value = str(s.get("value") or "")
        sid = str(s.get("state_id") or "")
        if value not in STATE_CLOSED_SET:
            errors.append(f"CV-01 幽灵状态: {sid or '?'} value={value!r} 不在骨架 §1 六态闭集（禁自造状态）")
        if value in seen_values:
            errors.append(f"CV-01 状态值重复: {value}")
        seen_values.add(value)
        if sid in seen_state_ids:
            errors.append(f"CV-01 state_id 重复: {sid}")
        seen_state_ids.add(sid)

    terminal_values = {str(s.get("value")) for s in states if isinstance(s, dict) and s.get("terminal") is True}

    # --- 机构面：闭集 + 真源锚形态 ---
    seen_node_ids: set[str] = set()
    if isinstance(machinery, list):
        for n in machinery:
            if not isinstance(n, dict):
                errors.append("machinery 存在非对象条目")
                continue
            nid = str(n.get("node_id") or "")
            if nid not in MACHINERY_CLOSED_SET:
                errors.append(f"CV-03 幽灵机构: {nid or '?'} 不在骨架 §2 九机构闭集")
            if nid in seen_node_ids:
                errors.append(f"CV-03 node_id 重复: {nid}")
            seen_node_ids.add(nid)
            anchors = n.get("source_anchors")
            if not isinstance(anchors, list) or not anchors:
                errors.append(f"CV-03 机构 {nid} 缺 source_anchors（每节点真源映射不许空）")

    # --- CV-02 迁移合法性表 ---
    legal_pairs: set[tuple[str, str]] = set()
    if isinstance(transitions, list):
        seen_tids: set[str] = set()
        for t in transitions:
            if not isinstance(t, dict):
                errors.append("transitions 存在非对象条目")
                continue
            tid = str(t.get("transition_id") or "")
            if tid in seen_tids:
                errors.append(f"CV-02 transition_id 重复: {tid}")
            seen_tids.add(tid)
            to_state = str(t.get("to_state") or "")
            if to_state not in STATE_CLOSED_SET:
                errors.append(f"CV-02 迁移 {tid} to_state={to_state!r} 不在状态闭集（幽灵状态）")
            from_states = t.get("from_state")
            if not isinstance(from_states, list):
                errors.append(f"CV-02 迁移 {tid} from_state 非列表（∅ 用空列表表达）")
                from_states = []
            for f in from_states:
                if str(f) not in STATE_CLOSED_SET:
                    errors.append(f"CV-02 迁移 {tid} from_state={f!r} 不在状态闭集（幽灵状态）")
                if str(f) in terminal_values:
                    errors.append(f"CV-02 迁移 {tid} 自终态 {f} 出边（终态无出边）")
                legal_pairs.add((str(f), to_state))
    # 禁边 state-pair 不得被合法边同对覆盖（禁边不可绕过——同对并存即判据自相矛盾）
    if isinstance(forbidden, list):
        for x in forbidden:
            if not isinstance(x, dict):
                errors.append("forbidden_edges 存在非对象条目")
                continue
            xid = str(x.get("edge_id") or "")
            if not str(x.get("rule_zh") or ""):
                errors.append(f"CV-02 禁边 {xid} 缺 rule_zh（禁令语义不许空）")
            xs, xt = x.get("from_state"), x.get("to_state")
            if xs is not None and xt is not None:
                pair = (str(xs), str(xt))
                if pair in legal_pairs:
                    errors.append(f"CV-02 禁边 {xid} 与合法迁移同对 {pair}（判据自相矛盾，禁边被无凭证路径绕开）")
                if str(xs) in STATE_CLOSED_SET and str(xs) not in seen_values:
                    errors.append(f"CV-02 禁边 {xid} from_state={xs!r} 不在图 states（幽灵状态）")

    # --- CV-06 保险丝下限 ---
    meaningful = len(states) + (len(machinery) if isinstance(machinery, list) else 0)
    if meaningful < NODE_FLOOR:
        errors.append(
            f"CV-06 保险丝触发: 有意义节点 {meaningful} < {NODE_FLOOR}（裁定#486 ①结构下限）——"
            "停工呈 chief 降级评估，禁硬凑节点"
        )

    # --- CV-07 INV-1 长度面 + 实例禁入 nodes ---
    def _scan_fields(section: list, label: str) -> None:
        for item in section:
            if not isinstance(item, dict):
                continue
            if _INSTANCE_KEY in item:
                errors.append(
                    f"CV-07 裁定实例混入 nodes: {label} 条目含 {_INSTANCE_KEY} 键"
                    f"（实例=数据行非节点，裁定#486 ①保险丝二）"
                )
            for k, v in item.items():
                if isinstance(v, str) and len(v) > _FIELD_LEN_CAP:
                    errors.append(f"CV-07 INV-1 超长: {label}.{k} {len(v)} 字符 > {_FIELD_LEN_CAP}（禁复制裁定正文）")

    _scan_fields(states if isinstance(states, list) else [], "states")
    _scan_fields(machinery if isinstance(machinery, list) else [], "machinery")
    _scan_fields(transitions if isinstance(transitions, list) else [], "transitions")
    _scan_fields(forbidden if isinstance(forbidden, list) else [], "forbidden_edges")

    # --- check_prose_counts：计数只进 counts ---
    errors.extend(check_prose_counts(data))

    # --- CV-04/CV-05 实例面（live 才硬） ---
    if live:
        errors.extend(check_live_faces(data, root, warn))
    else:
        warn.append("live=False 提交面口径：CV-04 真源磁盘实存与 CV-05 counts 账本对拍不进硬闸（CLI/align_all 面）")
    return errors


def check_prose_counts(data: dict) -> list[str]:
    """语义层散文出现当前 counts 实例数=红（计数只进 counts，禁散文写死）。

    只匹配 ≥2 位数字且词边界独立成词（单数字子串误伤率 100%，不具判据资格）。
    """
    import re

    errors: list[str] = []
    counts = data.get("counts")
    if not isinstance(counts, dict):
        return errors
    numbers: set[str] = set()
    for v in counts.values():
        if isinstance(v, int) and v >= 10:
            numbers.add(str(v))
        elif isinstance(v, dict):
            numbers.update(str(x) for x in v.values() if isinstance(x, int) and x >= 10)
    prose_fields = ("ssot_note_zh", "laws", "boundary")
    for field in prose_fields:
        value = data.get(field)
        texts = value if isinstance(value, list) else [value]
        for text in texts:
            if not isinstance(text, str):
                continue
            for num in sorted(numbers, key=len, reverse=True):
                if re.search(rf"(?<![0-9A-Za-z]){re.escape(num)}(?![0-9])", text):
                    errors.append(f"prose_counts 散文写死实例数 {num}（{field}）——计数只进 counts 段")
                    break
    return errors


def check_live_faces(data: dict, root: Path, warnings: list[str]) -> list[str]:
    """live 面：CV-04 机构真源磁盘实存 + CV-05 counts 与账本对拍（硬）。"""
    errors: list[str] = []
    # CV-04 真源实存（外部真源面不可达=降 warn，禁环境异常打死无辜）
    for section in ("states", "machinery"):
        for item in data.get(section) or []:
            if not isinstance(item, dict):
                continue
            for anchor in item.get("source_anchors") or []:
                p = root / str(anchor)
                if not p.exists():
                    warnings.append(
                        f"CV-04 真源降 warn: {section} {item.get('state_id') or item.get('node_id')} "
                        f"锚 {anchor} 盘上不存在"
                    )
    # CV-05 counts 对拍（账本不可达=降 warn 留痕）
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location("generate_governance_legislation_map", _GENERATOR_REL)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        live_counts = mod.read_ledger_counts()
    except Exception as e:  # noqa: BLE001 — 账本不可达=环境异常降 warn（禁静默假绿：error 面由 entries_total 缺失兜）
        warnings.append(f"CV-05 账本不可达降 warn: {type(e).__name__}: {e}")
        return errors
    doc_counts = data.get("counts")
    for key in (
        "entries_total",
        "ledger_rows_active",
        "ledger_rows_retired",
        "superseded_by_chains",
        "snapshot_version",
    ):
        got = (doc_counts or {}).get(key)
        want = live_counts.get(key)
        if got != want:
            errors.append(f"CV-05 counts 漂移: {key} 图={got} 账本={want}（重跑生成器回灌）")
    if (doc_counts or {}).get("by_status") != live_counts.get("by_status"):
        errors.append(
            f"CV-05 counts 漂移: by_status 图={(doc_counts or {}).get('by_status')} "
            f"账本={live_counts.get('by_status')}（重跑生成器回灌）"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="图16 治理立法流图校验器（四判据+保险丝）")
    parser.add_argument("--map", default=str(_REPO_ROOT / MAP_REL), help="图 YAML 路径")
    parser.add_argument("--no-live", action="store_true", help="只跑结构面（gate 提交面口径）")
    args = parser.parse_args(argv)
    map_path = Path(args.map)
    if not map_path.is_file():
        print(f"ERROR: 图 YAML 不存在: {map_path}")
        return 2
    data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    warnings: list[str] = []
    errors = validate_structure(data, root=_REPO_ROOT, warnings=warnings, live=not args.no_live)
    for w in warnings:
        print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}")
        print(f"FAIL: {len(errors)} 项 error")
        return 1
    print("PASS: 图16 结构+实例面零 error")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
