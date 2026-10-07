# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §test_alignment_gates_red_blue
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# [TESTS] tests/governance/test_alignment_gates_red_blue.py（本文件）
"""对齐门禁红蓝对抗——TDM 校验器 R13 规则族（图12收官批 st-vm12final-20261007-laneA）。

历史沿革：本路径原文件（TestRedDecisionMap/TestRedBusinessRegistry/TestRedBattleMap
等 9 类 755 行）在旧一级路径清理批 87cb48bf0e5 删除后未再落地；本文件按其文档锚位
重建——check_decision_map.py [TESTS]/decision_map_gate.py/battle_map_alignment_gate.py/
trading_decision_map_layering_policy.md Step 6 循环验收命令均指认本路径。
当前承载=R13 规则族红蓝对抗（挂载三字段形态 INV-1 指针制/目的标签图头枚举/满格节点
标签完备性/X-R1 拆钉通用形态）；历史用例真身归位归 tests 复权批职权
（git 考古=87cb48bf0e5~1 可检索）。

X-R1 拆钉语义（tdm_mount/g_tag_mount_report §三.1 处方）：段头节点持 PT-12、
其子节点持 PT-07 是合法形态——校验器不设"同段同标签"父子一致性检查，
任何父子女标签组合只要各自合法即放行（通用规则，无一次性特判）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))
from check_decision_map import (  # noqa: E402
    _check_r13_mounts_and_purpose_tags,
    run_checks,
)

_REAL_MAP = _REPO / "config" / "trading_decision_map.yaml"

# 最小合法图骨架（R13 层只需 purpose_tags + nodes 形态；结构字段供人读与未来扩测）
_BASE_MAP = """
schema_version: '1.2'
map_id: TDMAP-TEST
markets: [cn_a]
purpose_tags:
- id: PT-01
  tag_zh: 测试标签一
  meaning_zh: 测试意义一
- id: PT-07
  tag_zh: 持仓跌了怎么办
  meaning_zh: 预先想好退路，临场只会瘫痪
- id: PT-12
  tag_zh: AI 交易人把关
  meaning_zh: 自动化越深越要有一道人能踩死的刹车
nodes:
- node_id: TDM-X-T1
  name_zh: 测试节点
  market: cn_a
  flow: entry_flow
  layer: L1
  node_type: gate
  point: 盘前
  decision_question: 测试判定问题？
  algo_note_zh: 测试算法说明（含阈值口径）
  module_ref: src/zephyr/pf_core/strategies/daban.py
  module_mounts: [MOD-TEST-001, src/zephyr/x/y.py]
  purpose_tag: PT-01
"""


def _run_r13(tmp_path: Path, yaml_text: str) -> list[str]:
    p = tmp_path / "map.yaml"
    p.write_text(yaml_text, encoding="utf-8")
    return _check_r13_mounts_and_purpose_tags(p)


# ── 红测（能红）───────────────────────────────────────────────────────────


def test_red_purpose_tag_self_made_not_in_header_enum(tmp_path):
    """红①：自造不存在的标签（PT-99 不在图头枚举）——校验器必须红。"""
    fails = _run_r13(tmp_path, _BASE_MAP.replace("purpose_tag: PT-01", "purpose_tag: PT-99"))
    assert any("R13" in f and "PT-99" in f for f in fails), f"自造标签未红: {fails}"


def test_red_purpose_tag_out_of_enum_form(tmp_path):
    """红②：枚举外 purpose_tag（非 PT-ID 标量形态，散文值）——校验器必须红。"""
    fails = _run_r13(tmp_path, _BASE_MAP.replace("purpose_tag: PT-01", "purpose_tag: 紧急刹车优先"))
    assert any("R13" in f and "标量 PT-ID" in f for f in fails), f"枚举外形态未红: {fails}"


def test_red_mount_field_prose_copy(tmp_path):
    """红③：挂载字段抄正文（INV-1 指针制：散文抄入 module_mounts）——校验器必须红。"""
    fails = _run_r13(
        tmp_path,
        _BASE_MAP.replace(
            "module_mounts: [MOD-TEST-001, src/zephyr/x/y.py]",
            "module_mounts: [把正文散文整句抄进挂载字段就是违规样本]",
        ),
    )
    assert any("R13" in f and "非指针" in f for f in fails), f"挂载抄正文未红: {fails}"


def test_red_full_node_missing_purpose_tag(tmp_path):
    """红④：满格节点（四字段齐）缺 purpose_tag=error——校验器必须红。"""
    fails = _run_r13(tmp_path, _BASE_MAP.replace("  purpose_tag: PT-01\n", ""))
    assert any("R13" in f and "满格节点缺 purpose_tag" in f for f in fails), f"满格缺标未红: {fails}"


def test_red_purpose_tag_key_outside_nodes_section(tmp_path):
    """红⑤：purpose_tag 键落到 nodes 段之外（机贴批手术记录复发防线）——校验器必须红。"""
    stray = _BASE_MAP + (
        "portfolio_plan:\n"
        "  plan_id: PLAN-T\n"
        "  name_zh: 测试组合\n"
        "  confidence: proposed\n"
        "  sleeves: []\n"
        "  aggregator: {}\n"
        "  purpose_tag: PT-01\n"
    )
    fails = _run_r13(tmp_path, stray)
    assert any("R13" in f and "nodes 段之外" in f for f in fails), f"段外标签未红: {fails}"


def test_red_header_enum_itself_broken(tmp_path):
    """红⑥：图头枚举真源自坏（id 非 PT-NN / 双字段缺失）——枚举校验不可信必须红。"""
    broken = _BASE_MAP.replace(
        "- id: PT-01\n  tag_zh: 测试标签一\n  meaning_zh: 测试意义一", "- id: PTX\n  tag_zh: 测试标签一"
    )
    fails = _run_r13(tmp_path, broken)
    assert any("R13" in f and "id 非法" in f for f in fails), f"图头 id 非法未红: {fails}"
    assert any("R13" in f and "meaning_zh" in f for f in fails), f"图头缺双字段未红: {fails}"


# ── 蓝测（合法形态不误红）─────────────────────────────────────────────────


def test_blue_xr1_pin_removal_generic_form(tmp_path):
    """蓝①：X-R1 拆钉合法形态——段头 PT-12 + 子节点 PT-07 各自合法即放行（无特判）。"""
    xr1 = _BASE_MAP.replace(
        "  purpose_tag: PT-01\n",
        "  purpose_tag: PT-12\n"
        "- node_id: TDM-X-R1-01\n"
        "  name_zh: 熔断分级判定\n"
        "  market: cn_a\n"
        "  flow: entry_flow\n"
        "  layer: X1\n"
        "  node_type: stage\n"
        "  point: 持续\n"
        "  decision_question: 熔断几级？\n"
        "  algo_note_zh: 五级状态机说明\n"
        "  module_ref: src/zephyr/risk/core/drawdown_state_machine.py\n"
        "  module_mounts: [MOD-RK-049]\n"
        "  parent_node: TDM-X-R1\n"
        "  purpose_tag: PT-07\n",
    )
    assert _run_r13(tmp_path, xr1) == [], "X-R1 拆钉形态（段头PT-12/子PT-07）被误红"


def test_blue_real_map_r13_clean_and_xr1_form_on_graph():
    """蓝②：真实地图 R13 全绿 + X-R1 段头/子节点拆钉形态在图（拆钉回归锚）。"""
    assert _REAL_MAP.exists(), f"地图真源缺失: {_REAL_MAP}"
    assert _check_r13_mounts_and_purpose_tags(_REAL_MAP) == [], "真实地图 R13 误红"
    raw = yaml.safe_load(_REAL_MAP.read_text(encoding="utf-8"))
    by_id = {n["node_id"]: n for n in raw["nodes"]}
    head = by_id.get("TDM-X-R1")
    assert head is not None and head.get("purpose_tag") == "PT-12", "X-R1 段头标签漂移"
    for child_id in ("TDM-X-R1-01", "TDM-X-R1-02", "TDM-X-R1-03"):
        child = by_id.get(child_id)
        assert child is not None and child.get("purpose_tag") == "PT-07", f"{child_id} 子节点标签漂移"


def test_blue_mount_pointer_forms_legal(tmp_path):
    """蓝③：MOD-* 模块指针与仓库相对路径指针均为合法挂载形态（含下划线族 MOD-INT_X）。"""
    legal = _BASE_MAP.replace(
        "module_mounts: [MOD-TEST-001, src/zephyr/x/y.py]",
        "module_mounts: [MOD-TEST-001, MOD-INT_NEWS_CHAIN, src/zephyr/x/y.py]",
    )
    assert _run_r13(tmp_path, legal) == [], "合法指针形态被误红"


# ── 集成红测（run_checks 公共入口）────────────────────────────────────────


@pytest.mark.skipif(not _REAL_MAP.exists(), reason="地图真源缺失")
def test_run_checks_reports_r13_on_mutated_map_copy(tmp_path):
    """集成：真实地图副本注入枚举外标签后 run_checks 必报 R13（公共入口能红）。

    tmp_path 隔离（测试禁写生产路径）；DB 类子检查按设计 fail-open 不影响断言。
    """
    mutated = _REAL_MAP.read_text(encoding="utf-8").replace("purpose_tag: PT-04", "purpose_tag: PT-99", 1)
    assert mutated != _REAL_MAP.read_text(encoding="utf-8"), "注入失败：真实地图无 PT-04 可变"
    p = tmp_path / "trading_decision_map.yaml"
    p.write_text(mutated, encoding="utf-8")
    fails, _warns, _total = run_checks(map_path=p)
    assert any(f.startswith("R13") and "PT-99" in f for f in fails), (
        f"run_checks 未报 R13: {[f for f in fails if f.startswith('R13')][:3]}"
    )
