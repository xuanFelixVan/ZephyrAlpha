"""图11 门禁对抗测试（st-fig1113reg-20261004 转正批配套；先例 test_trading_day_cycle_map_gate）。

判据=自写校验必须先证明自己能红，再声称绿（六图终局卷 §5 防腐面）。
基座策略：加载真实 config/dev_delivery_map.yaml 作底 → 深拷贝微扰 → 红用例；
绿用例=真实图原样过 gate+validator（validator 层对抗面详见
tests/governance/d5_architecture/test_dev_delivery_map_adversarial.py——伪造节点/断链/
越车道挂载/缺口节点缺 red_reason 四攻击在彼处，本件只封 gate 层语义）。
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[4]
VALIDATORS_DIR = REPO / "scripts" / "governance" / "d5_architecture" / "validators"
MAP_REL = "config/dev_delivery_map.yaml"

sys.path.insert(0, str(VALIDATORS_DIR))

from validate_dev_delivery_map import validate_structure  # noqa: E402

from zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate import _check  # noqa: E402


class _FakeGW:
    repo_root = str(REPO)


def _load_map() -> dict:
    return yaml.safe_load((REPO / MAP_REL).read_text(encoding="utf-8"))


# ── validator 层：能红抽检（全集四攻击在 d5_architecture 对抗尺，此处防回归位） ─────────


def test_validator_red_on_dangling_edge() -> None:
    """能红：边引用断链（指向不存在 node_id，边=[from,to] 二元组）=error。"""
    data = _load_map()
    data["edges"].append(["D11-S01", "D11-NOPE"])
    errs = validate_structure(copy.deepcopy(data), REPO, [])
    assert any("边引用了不存在的节点" in e for e in errs)


def test_validator_red_on_gap_node_missing_red_reason() -> None:
    """能红：gap 节点缺 red_reason（CV-GAP）=error。"""
    data = _load_map()
    gap = next(n for n in data["nodes"] if n.get("node_id", "").startswith("D11-G"))
    gap.pop("red_reason", None)
    errs = validate_structure(data, REPO, [])
    assert any("red_reason" in e for e in errs)


# ── gate 层：触发式/fail-closed/绿 ────────────────────────────────────────────


def test_gate_pass_on_real_map() -> None:
    """绿：真实图过 gate（相位无关——图11 血肉分阶段口径由 validator 内部降 warn）。"""
    ok, detail = _check(_FakeGW(), [str(REPO / MAP_REL)])
    assert ok, detail


def test_gate_fail_closed_on_broken_yaml(tmp_path, monkeypatch) -> None:
    """能红：图 YAML 损坏=fail-closed 阻断（真源损坏必须先修）。"""
    import zephyr.gov_enforcement.commit_gates.map_family.dev_delivery_map_gate as g

    broken = tmp_path / "broken.yaml"
    broken.write_text("nodes: [unclosed", encoding="utf-8")
    monkeypatch.setattr(
        g.Path,
        "read_text",
        lambda self, **kw: (
            broken.read_text(encoding="utf-8") if "dev_delivery_map" in str(self) else Path.read_text(self, **kw)
        ),
    )
    ok, detail = g._check(_FakeGW(), [str(REPO / MAP_REL)])
    assert not ok
    assert "解析异常" in detail


def test_gate_blocks_broken_map_structure(tmp_path) -> None:
    """能红：触及图输入面的 commit，图结构 error>0 → 阻断（坏图装进 tmp 仓根，gate 指向 tmp 根读取）。"""
    bad = dict(_load_map())
    bad["nodes"] = [n for n in bad["nodes"] if n["node_id"] != "D11-S01"]
    (tmp_path / "config").mkdir()
    (tmp_path / MAP_REL).write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")

    class _TmpGW:
        repo_root = str(tmp_path)
        project_root = str(tmp_path)

    ok, detail = _check(_TmpGW(), [MAP_REL])
    assert not ok, detail
    assert "DEV-DELIVERY-MAP" in detail


def test_gate_skip_on_unrelated_files() -> None:
    """触发式收窄：不触及图输入面的 commit 跳过（先例 trading_day_cycle_map_gate）。"""
    ok, detail = _check(_FakeGW(), ["README.md"])
    assert ok
    assert "skip" in detail


def test_gate_fires_on_skeleton_input_face() -> None:
    """触发面实证：触及骨架（图11 三态列真源）即跑全量——真图在自家仓根应绿过。"""
    ok, detail = _check(_FakeGW(), [str(REPO / "docs/_working/map_build/fig11_delivery/00_skeleton.md")])
    assert ok, detail


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
