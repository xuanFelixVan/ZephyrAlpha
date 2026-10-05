"""图12 门禁对抗测试（st-vm12surg-20261003 手术批配套；先例 test_strategy_factory_map_gate）。

判据=自写校验必须先证明自己能红，再声称绿（六图终局卷 §5 防腐面）。
基座策略：加载真实 config/data_supply_chain_map.yaml 作底 → 深拷贝微扰 → 红用例；
绿用例=真实图原样过 gate+validator（blood_stage=f1_pending 期缺血肉键降 warn 不拦）。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[4]
VALIDATORS_DIR = REPO / "scripts" / "governance" / "d5_architecture" / "validators"
MAP_REL = "config/data_supply_chain_map.yaml"

sys.path.insert(0, str(VALIDATORS_DIR))

from validate_data_supply_chain_map import validate_structure  # noqa: E402

from zephyr.gov_enforcement.commit_gates.map_family.data_supply_chain_map_gate import _check  # noqa: E402


class _FakeGW:
    repo_root = str(REPO)


def _load_map() -> dict:
    return yaml.safe_load((REPO / MAP_REL).read_text(encoding="utf-8"))


def _first_stage_node(data: dict) -> dict:
    return next(n for n in data["nodes"] if n.get("node_type") == "stage")


# ── validator 层：CV-BLOOD 能红用例 ────────────────────────────────────────────


def test_f1_pending_blood_missing_downgrades_to_warns() -> None:
    """f1_pending：血肉键缺失=warn 不拦（分阶段开关防误伤——本批核心设计）。

    E-11 构造性夹具：真实图已是 f2_done 满血（dd686019c2），旧相位（缺键+pending）
    须构造再现——删首个非 gap 节点四字段键再置 f1_pending，禁依赖真实图相位。"""
    data = _load_map()
    node = _first_stage_node(data)
    for bf in ("purpose_tag", "casebooks", "trigger_facts", "consumers"):
        node.pop(bf, None)
    data["blood_stage"] = "f1_pending"
    warns: list[str] = []
    errs = validate_structure(data, REPO, warns)
    assert errs == []
    assert any("血肉未满" in w for w in warns)


def test_f2_done_missing_blood_keys_is_error() -> None:
    """能红：f2_done 后非 gap 节点缺 purpose_tag/四字段键=error。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(8)]
    warns: list[str] = []
    errs = validate_structure(data, REPO, warns)
    assert errs, "f2_done 且四字段全缺必须判红"
    assert any("CV-BLOOD" in e for e in errs)


def test_f2_done_tag_must_be_in_frozen_legend() -> None:
    """能红：purpose_tag 自造（不在图头冻结枚举）=error——禁贴图例外标签。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(8)]
    node = _first_stage_node(data)
    node["purpose_tag"] = "made_up_tag"
    errs = validate_structure(data, REPO, [])
    assert any("不在图头 purpose_tags 枚举" in e for e in errs)


def test_f2_done_production_requires_trigger_facts() -> None:
    """能红：production 节点 trigger_facts 必非空（实测触发数=在产证据位）。

    E-11 构造性夹具：真实图 production 节点已带 trigger_facts（dd686019c2），
    红前提须构造再现——pop 掉该键，禁依赖真实图相位。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(8)]
    prod = next(n for n in data["nodes"] if n.get("verified_scope") == "production")
    prod["purpose_tag"] = "tag_0"
    prod.pop("trigger_facts", None)
    errs = validate_structure(data, REPO, [])
    assert any("production 节点 trigger_facts 必非空" in e for e in errs)


def test_f2_done_legend_range_enforced() -> None:
    """能红：图例标签 8~12 条（7 条=f2_done 时红）。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(7)]
    errs = validate_structure(data, REPO, [])
    assert any("purpose_tags 须 8~12" in e for e in errs)


def test_red_reason_contract_sourced_legal() -> None:
    """contract_sourced 枚举合法（E-1：契约驱动真源型节点的 null 注记）。"""
    data = _load_map()
    node = next(n for n in data["nodes"] if n["node_id"] == "DSC-12")
    assert node["red_reason"] == "contract_sourced"


# ── gate 层：触发式/fail-closed/绿 ────────────────────────────────────────────


def test_gate_pass_on_real_map_with_notes() -> None:
    """绿：真实图过 gate。E-11 相位回归位：图12 已翻 f2_done 满血（dd686019c2），
    放行 detail 须无"血肉未满"注记——若此断言红=有人把 blood_stage 翻回了 pending。"""
    ok, detail = _check(_FakeGW(), [str(REPO / MAP_REL)])
    assert ok
    assert "血肉未满" not in detail


def test_gate_fail_closed_on_broken_yaml(tmp_path, monkeypatch) -> None:
    """能红：图 YAML 损坏=fail-closed 阻断（真源损坏必须先修）。"""
    import zephyr.gov_enforcement.commit_gates.map_family.data_supply_chain_map_gate as g

    broken = tmp_path / "broken.yaml"
    broken.write_text("nodes: [unclosed", encoding="utf-8")
    monkeypatch.setattr(
        g.Path,
        "read_text",
        lambda self, **kw: (
            broken.read_text(encoding="utf-8") if "data_supply_chain_map" in str(self) else Path.read_text(self, **kw)
        ),
    )
    ok, detail = g._check(_FakeGW(), [str(REPO / MAP_REL)])
    assert not ok
    assert "解析异常" in detail


def test_gate_skip_on_unrelated_files() -> None:
    """触发式收窄：不触及图输入面的 commit 跳过（先例 decision_map_gate）。"""
    ok, detail = _check(_FakeGW(), ["README.md"])
    assert ok
    assert "skip" in detail


def test_gate_mount_coverage_warn_leg() -> None:
    """落地即挂图 warn 腿（第一版不拦）：数据域蓝图 MOD 号未挂图→warn 注记非阻断。"""
    ok, detail = _check(_FakeGW(), [str(REPO / "docs/03_modules/_domain_data/transport/blueprint.md")])
    assert ok  # warn 腿不拦——F2 填满+覆盖账本绿后随裁定翻硬
    assert "落地即挂图" in detail


@pytest.mark.parametrize("bad_stage", ["f0_draft", "done", None])
def test_blood_stage_enum_enforced(bad_stage) -> None:
    """能红：blood_stage 非法枚举=error。"""
    data = _load_map()
    data["blood_stage"] = bad_stage
    errs = validate_structure(data, REPO, [])
    assert any("blood_stage 非法" in e for e in errs)
