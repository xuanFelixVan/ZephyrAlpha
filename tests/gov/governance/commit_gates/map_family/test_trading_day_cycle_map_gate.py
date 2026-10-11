"""图13 门禁对抗测试（st-tclose-fig13reg-20261004 转正批配套；先例 test_data_supply_chain_map_gate）。

判据=自写校验必须先证明自己能红，再声称绿（六图终局卷 §5 防腐面）。
基座策略：加载真实 config/trading_day_cycle_map.yaml 作底 → 深拷贝微扰 → 红用例；
绿用例=真实图原样过 gate+validator（blood_stage=f1_pending 期缺血肉键降 warn 不拦）。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[5]
VALIDATORS_DIR = REPO / "scripts" / "governance" / "d5_architecture" / "validators"
MAP_REL = "config/trading_day_cycle_map.yaml"

sys.path.insert(0, str(VALIDATORS_DIR))

from validate_trading_day_cycle_map import validate_structure  # noqa: E402

from zephyr.gov_enforcement.commit_gates.map_family.trading_day_cycle_map_gate import _check  # noqa: E402


class _FakeGW:
    repo_root = str(REPO)


def _load_map() -> dict:
    return yaml.safe_load((REPO / MAP_REL).read_text(encoding="utf-8"))


def _first_stage_node(data: dict) -> dict:
    return next(n for n in data["nodes"] if n.get("node_type") == "stage")


# ── validator 层：CV-BLOOD 能红用例（f2_done 翻闸后的硬红面） ───────────────────


def test_f1_pending_blood_missing_downgrades_to_warns() -> None:
    """f1_pending：血肉键空默认值=warn 不拦（分阶段开关防误伤——schema 升级与灌肉不同窗）。"""
    data = _load_map()
    data["blood_stage"] = "f1_pending"
    warns: list[str] = []
    errs = validate_structure(copy.deepcopy(data), REPO, warns)
    assert errs == []
    assert any("血肉未满" in w for w in warns)


def test_f2_done_missing_blood_keys_is_error() -> None:
    """能红：f2_done 后非 gap 节点四字段键空默认值=error。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(13)]
    warns: list[str] = []
    errs = validate_structure(data, REPO, warns)
    assert errs, "f2_done 且四字段全空必须判红"
    assert any("CV-BLOOD" in e for e in errs)


def test_f2_done_tag_must_be_in_frozen_legend() -> None:
    """能红：purpose_tag 自造（不在图头冻结枚举）=error——禁贴图例外标签。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(13)]
    node = _first_stage_node(data)
    node["purpose_tag"] = "made_up_tag"
    errs = validate_structure(data, REPO, [])
    assert any("不在图头 purpose_tags 枚举" in e for e in errs)


def test_f2_done_production_requires_trigger_facts() -> None:
    """能红：production 节点 trigger_facts 必非空（实测触发数=在产证据位）。"""
    data = _load_map()
    data["blood_stage"] = "f2_done"
    data["purpose_tags"] = [{"id": f"tag_{i}", "plain_zh": f"标签{i}"} for i in range(13)]
    prod = next(n for n in data["nodes"] if n.get("verified_scope") == "production")
    prod["purpose_tag"] = "tag_0"
    prod["trigger_facts"] = None
    errs = validate_structure(data, REPO, [])
    assert any("production 节点 trigger_facts 必非空" in e for e in errs)


@pytest.mark.parametrize("bad_stage", ["f0_draft", "done", None])
def test_blood_stage_enum_enforced(bad_stage) -> None:
    """能红：blood_stage 非法枚举=error。"""
    data = _load_map()
    data["blood_stage"] = bad_stage
    errs = validate_structure(data, REPO, [])
    assert any("blood_stage 非法" in e for e in errs)


# ── gate 层：触发式/fail-closed/绿 ────────────────────────────────────────────


def test_gate_pass_on_real_map_with_notes() -> None:
    """绿：真实图过 gate（相位自适应——E-11 教训：禁依赖真实图相位。

    f1_pending 期血肉未满以 warn 注记放行；f2_done 满血（F2 批 864bfb1b99 翻闸后）
    零注记空串放行。若 f2_done 期重现"血肉未满"注记=validator 降级逻辑回潮，须查。"""
    data = _load_map()
    ok, detail = _check(_FakeGW(), [str(REPO / MAP_REL)])
    assert ok
    if data.get("blood_stage") == "f1_pending":
        assert "血肉未满" in detail
    else:
        assert "血肉未满" not in detail


def test_gate_fail_closed_on_broken_yaml(tmp_path, monkeypatch) -> None:
    """能红：图 YAML 损坏=fail-closed 阻断（真源损坏必须先修）。"""
    import zephyr.gov_enforcement.commit_gates.map_family.trading_day_cycle_map_gate as g

    broken = tmp_path / "broken.yaml"
    broken.write_text("nodes: [unclosed", encoding="utf-8")
    monkeypatch.setattr(
        g.Path,
        "read_text",
        lambda self, **kw: (
            broken.read_text(encoding="utf-8") if "trading_day_cycle_map" in str(self) else Path.read_text(self, **kw)
        ),
    )
    ok, detail = g._check(_FakeGW(), [str(REPO / MAP_REL)])
    assert not ok
    assert "解析异常" in detail


def test_gate_blocks_broken_map_structure(tmp_path) -> None:
    """能红：触及图输入面的 commit，图结构 error>0 → 阻断（坏图装进 tmp 仓根，gate 指向 tmp 根读取）。"""
    bad = dict(_load_map())
    bad["nodes"] = [n for n in bad["nodes"] if n["node_id"] != "D13-26"]
    (tmp_path / "config").mkdir()
    (tmp_path / MAP_REL).write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")

    class _TmpGW:
        repo_root = str(tmp_path)
        project_root = str(tmp_path)

    ok, detail = _check(_TmpGW(), [MAP_REL])
    assert not ok, detail
    assert "TRADING-DAY-CYCLE-MAP" in detail


def test_gate_skip_on_unrelated_files() -> None:
    """触发式收窄：不触及图输入面的 commit 跳过（先例 data_supply_chain_map_gate）。"""
    ok, detail = _check(_FakeGW(), ["README.md"])
    assert ok
    assert "skip" in detail


def test_gate_fires_on_scheduler_input_face() -> None:
    """触发面实证：触及 schedule.yaml（图13机生源）即跑全量——真图在自家仓根应绿过。"""
    ok, detail = _check(_FakeGW(), [str(REPO / "src/zephyr/data/config/schedule.yaml")])
    assert ok, detail


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
