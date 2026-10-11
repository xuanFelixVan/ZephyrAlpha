# [A_test] module_id: MOD-GOV-tdm_mount_coverage_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §mount-coverage
# [MODULE] tests.governance.commit_gates.test_tdm_mount_coverage_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_tdm_mount_coverage_gate.py — TDM-MOUNT-COVERAGE 挂载义务门禁单测（工单 st-tdm-mountgate-20261005）

权威依据：tdm_mount_coverage_gate.py（make_tdm_mount_coverage_gate）+ 详版规格
docs/_working/tdm_mount/f_mountgate_spec_v1.md §9 测试矩阵。

红蓝矩阵（规格 §9）：
- 红1 新 .py 无任何裁决 → 拦（消息含三选一处方）
- 红2 撞号（module_id 已注册到他路径）→ 拦（消息含撞号对象）
- 红3 蓝图锚不一致（frontmatter ≠ .py [BLUEPRINT] 行）→ 拦
- 红4 幽灵挂载（staged 地图 diff 新增引用无蓝图锚）→ 拦
- 蓝1 module_id ∈ 图 module_mounts → 放
- 蓝2 module_id ∈ 豁免册 → 放
- 蓝3 blueprint 含 [not-trading:<理由>] → 放
- 蓝4 豁免册缺席（前置未落）→ skip 非拦
- 蓝5 外来 staged（他 session）→ warn 放行

测试隔离：MagicMock gateway（run_git 按 diff/show/unified=0 分派）+ tmp_path 真源 fixture +
monkeypatch depgraph 反查（零 PG 依赖）。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.tdm_mount_coverage_gate import (  # noqa: E402
    _is_py_in_scope,
    make_tdm_mount_coverage_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


_NEW_PY = "src/zephyr/signal/new_module.py"
_NEW_BP = "docs/03_modules/_domain_signal/new_module/blueprint.md"

_PY_ANCHORED = (
    '# [BLUEPRINT] MOD-NEW-001 | docs/03_modules/_domain_signal/new_module/blueprint.md | §x\n"""新模块。"""\n'
)


def _write_map(tmp_path: Path, extra_nodes: list[dict] | None = None) -> None:
    """tmp 图族 fixture：一张带节点的小图（挂载面真源）。"""
    nodes = [
        {"node_id": "N1", "module_id": "MOD-MOUNTED-ID-001"},
        {"node_id": "N2", "module_mounts": ["MOD-MOUNTED-MM-001"]},
    ] + (extra_nodes or [])
    cfg = tmp_path / "config"
    cfg.mkdir(exist_ok=True)
    (cfg / "some_map.yaml").write_text(yaml.safe_dump({"nodes": nodes}, allow_unicode=True), encoding="utf-8")


def _write_exemptions(tmp_path: Path) -> None:
    """tmp 豁免册 fixture（前置面存在=gate 激活）。"""
    reg = {
        "registry_id": "TDM-MOUNT-EXEMPT-001",
        "exemptions": [
            {"module_id": "MOD-EXEMP-001", "target_map": "图9 策略工厂", "conclusion_zh": "测试豁免", "basis": "test"}
        ],
    }
    cfg = tmp_path / "config"
    cfg.mkdir(exist_ok=True)
    (cfg / "tdm_mount_exemption_registry.yaml").write_text(yaml.safe_dump(reg, allow_unicode=True), encoding="utf-8")


def _make_gateway(
    tmp_path: Path, new_files: list[str], staged_contents: dict[str, str], map_diff_stdout: str = ""
) -> MagicMock:
    """mock gateway：run_git 按 diff-filter=A / show :path / unified=0 三态分派。"""
    gw = MagicMock()
    gw.project_root = tmp_path
    (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)

    def _run_git(args, **_kw):
        args = list(args)
        if "--diff-filter=A" in args:
            return _MockResult(0, "\n".join(new_files) + ("\n" if new_files else ""))
        if len(args) >= 3 and args[1] == "show":
            path = args[2].lstrip(":")
            if path in staged_contents:
                return _MockResult(0, staged_contents[path])
            return _MockResult(1, "")
        if "--unified=0" in args:
            return _MockResult(0, map_diff_stdout)
        return _MockResult(0, "")

    gw.run_git = MagicMock(side_effect=_run_git)
    return gw


def _run_gate(
    gw: MagicMock,
    files: list[str],
    monkeypatch: pytest.MonkeyPatch,
    bid_paths: dict | None = None,
    all_bids: set | None = None,
):
    import zephyr.gov_enforcement.commit_gates.tdm_mount_coverage_gate as gate_mod

    monkeypatch.setattr(gate_mod, "_depgraph_maps", lambda: (bid_paths or {}, all_bids or set()))
    gate = make_tdm_mount_coverage_gate()
    return gate.check(gw, files=files, session_id="test-sid")


class TestGateSpecFields:
    """gate_id / priority / isinstance(GateSpec)。"""

    def test_gate_id(self) -> None:
        assert make_tdm_mount_coverage_gate().gate_id == "TDM-MOUNT-COVERAGE"

    def test_priority(self) -> None:
        # 158=后到者让位定稿（61 撞 RULE-EXECUTION-PAIRING→150 撞 TASK-ORDER-DOCS-LOCK→158 真空位）
        assert make_tdm_mount_coverage_gate().priority == 158

    def test_is_gate_spec(self) -> None:
        assert isinstance(make_tdm_mount_coverage_gate(), GateSpec)


class TestIsPyInScope:
    """范围判断：tests/demos/test_ 前缀/__init__/_archive 豁免（同 TRANSLATION-COVERAGE 口径）。"""

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("src/zephyr/signal/a.py", True),
            ("scripts/tool.py", True),
            ("tests/governance/test_x.py", False),
            ("scripts/tests/smoke_x.py", False),
            ("src/zephyr/signal/test_a.py", False),
            ("src/zephyr/signal/__init__.py", False),
            ("src/zephyr/_archive/old.py", False),
            ("docs/notes.md", False),
        ],
    )
    def test_scope(self, path: str, expected: bool) -> None:
        assert _is_py_in_scope(path) is expected


class TestRedVerdicts:
    """红面：无裁决拦 / 撞号拦 / 锚不一致拦 / 幽灵挂载拦。"""

    def test_red1_no_verdict_blocks_with_prescription(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: _PY_ANCHORED})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is False
        assert "三选一" in msg and "not-trading" in msg and _NEW_PY in msg

    def test_red2_collision_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        py_text = _PY_ANCHORED.replace("MOD-NEW-001", "MOD-COLL-001")
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: py_text})
        passed, msg = _run_gate(
            gw,
            [str(tmp_path / _NEW_PY)],
            monkeypatch,
            bid_paths={"MOD-COLL-001": ["src/zephyr/signal/other_holder.py"]},
            all_bids={"MOD-COLL-001"},
        )
        assert passed is False
        assert "撞号" in msg and "other_holder.py" in msg

    def test_red3_anchor_mismatch_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        bp_text = "---\nmodule_id: MOD-BP-SIDE-001\n---\n# 蓝图\n"
        gw = _make_gateway(tmp_path, [_NEW_PY, _NEW_BP], {_NEW_PY: _PY_ANCHORED, _NEW_BP: bp_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY), str(tmp_path / _NEW_BP)], monkeypatch)
        assert passed is False
        assert "蓝图锚不一致" in msg and "MOD-BP-SIDE-001" in msg

    def test_red4_ghost_mount_blocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """地图单提交（无新增模块）同样触发幽灵挂载拦——9c 检视与新增裁决解耦。"""
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        map_rel = "config/some_map.yaml"
        gw = _make_gateway(
            tmp_path,
            [],
            {},
            map_diff_stdout=f"+++ b/{map_rel}\n+  - MOD-GHOST-001\n",
        )
        passed, msg = _run_gate(gw, [str(tmp_path / map_rel)], monkeypatch)
        assert passed is False
        assert "幽灵挂载" in msg and "MOD-GHOST-001" in msg


class TestBlueVerdicts:
    """蓝面：已挂放 / 豁免放 / 标记放 / 前置自锁 skip / 外来放行。"""

    def test_blue1_module_mounts_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        py_text = _PY_ANCHORED.replace("MOD-NEW-001", "MOD-MOUNTED-MM-001")
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: py_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True, msg

    def test_blue1b_module_id_anchor_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        py_text = _PY_ANCHORED.replace("MOD-NEW-001", "MOD-MOUNTED-ID-001")
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: py_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True, msg

    def test_blue1c_ref_direct_mount_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """ref 直挂面：staged 图节点 module_ref 精确指向新文件=已挂（零 DB 判定）。"""
        _write_map(tmp_path, extra_nodes=[{"node_id": "N3", "module_ref": _NEW_PY}])
        _write_exemptions(tmp_path)
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: _PY_ANCHORED})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True, msg

    def test_blue2_exemption_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        py_text = _PY_ANCHORED.replace("MOD-NEW-001", "MOD-EXEMP-001")
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: py_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True, msg

    def test_blue3_not_trading_marker_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        py_text = _PY_ANCHORED + "# [not-trading: AI 开发工具非交易域设施]\n"
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: py_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True, msg

    def test_blue3b_companion_blueprint_marker_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        bp_text = "---\nmodule_id: MOD-NEW-001\n---\n# 蓝图\n标记：[not-trading: 非交易域开发设施]\n"
        gw = _make_gateway(tmp_path, [_NEW_PY, _NEW_BP], {_NEW_PY: _PY_ANCHORED, _NEW_BP: bp_text})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY), str(tmp_path / _NEW_BP)], monkeypatch)
        assert passed is True, msg

    def test_blue4_missing_registry_selflocks(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """前置自锁：豁免册缺席=skip 非拦（工单A 前置未落运行时自证）。"""
        _write_map(tmp_path)  # 有图无豁免册
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: _PY_ANCHORED})
        passed, msg = _run_gate(gw, [str(tmp_path / _NEW_PY)], monkeypatch)
        assert passed is True
        assert "前置自锁" in msg

    def test_blue5_foreign_staged_passes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """外来 staged（他 session）warn+审计不阻断（宪法 §3.1 own 化）。"""
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        gw = _make_gateway(tmp_path, [_NEW_PY], {_NEW_PY: _PY_ANCHORED})
        import zephyr.gov_enforcement.commit_gates.tdm_mount_coverage_gate as gate_mod

        monkeypatch.setattr(
            gate_mod,
            "_split_own_foreign",
            lambda gw, touched, files, sid, gate_name: ([], touched),
        )
        gate = make_tdm_mount_coverage_gate()
        passed, msg = gate.check(gw, files=[], session_id="test-sid")
        assert passed is True


class TestFailOpen:
    """环境异常降级：git diff 失败放行。"""

    def test_git_failure_fails_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _write_map(tmp_path)
        _write_exemptions(tmp_path)
        gw = MagicMock()
        gw.project_root = tmp_path
        (tmp_path / "scripts" / "governance" / "d1_structure").mkdir(parents=True, exist_ok=True)
        gw.run_git = MagicMock(return_value=_MockResult(128, "fatal: bad"))
        gate = make_tdm_mount_coverage_gate()
        passed, _msg = gate.check(gw, files=[], session_id="test-sid")
        assert passed is True
