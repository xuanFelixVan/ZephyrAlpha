# [A_test] module_id: MOD-GOV_gate_approval_wiring | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.commit_gates.test_approval_wiring
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.commit_gates.{approval_resolver,create_guard,protected_paths_gate}
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/commit_gates/test_approval_wiring.py -q
# [MATURITY] testing
# [INVARIANTS] 裁定#480 手术③（合一+时序倒置）接线回归：①PROTECTED-PATHS 裁定通道在 serializer 落地链（专用 worktree 单数形态 <repo>/.runtime/commit_queue/worktree/，q-20261003-st-commitmap-chief-20261003-0013 死信实证）必须命中盘面 active 裁定 approved_paths（#461 明文覆盖 ruling_registry.yaml 场景，tmp_path 迷你裁定册）；②gate 层接线=protected_paths_gate.check 经 approval_resolver.resolve_approval 判定（无自有裁定遍历）；③归一不得放大授权面（未覆盖路径照拦）；④CREATE-GUARD registry 读取锚主区盘面（anchor_main_root）——linked worktree 内读到主区未提交的 creation_token（"登记完即可提交、无需先行批"）；全 tmp_path 沙盒，不触生产路径
# [MODIFY-GUARD] 裁定#480 手术批（车道A st-sA-surgery-20261003）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_approval_wiring.py — 裁定#480 手术③接线回归（PROTECTED-PATHS 裁定通道时序倒置治本）

权威依据：
- approval_resolver.py（_strip_worktree_prefix 单数/复数双形态；resolve_approval）
- protected_paths_gate.py（裁定通道收敛 resolve_approval，无自有裁定遍历）
- create_guard.py（_load_capability_registry anchor_main_root 主区盘面锚定）

病根（时序倒置）：serializer 落地链专用 worktree（单数 ``worktree/``，真源
``scripts/governance/commit_queue_landing.py::_WORKTREE_DIR_NAME``）内，命中路径
剥主仓根后带 ``.runtime/commit_queue/worktree/`` 前缀，旧 ``_strip_worktree_prefix``
只认复数 ``worktrees/<slot>/`` → approved_paths（仓库相对 posix 登记）恒不匹配，
盘面已有 active 裁定（#461 明文覆盖 ruling_registry.yaml）"有授权也审批不过"。
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from zephyr.gov_enforcement.commit_gates.approval_resolver import (
    SOURCE_NONE,
    SOURCE_RULING,
    resolve_approval,
)
from zephyr.gov_enforcement.commit_gates.create_guard import (
    _collect_registered_files,
    _load_capability_registry,
)
from zephyr.gov_enforcement.commit_gates.protected_paths_gate import make_protected_paths_gate

_CATALOGS = "docs/01_policies_and_standards/_registry/catalogs"
_RULING_REGISTRY_REL = _CATALOGS + "/ruling_registry.yaml"


def _make_ruling_registry(root: Path, rulings: list[dict]) -> Path:
    """tmp_path 造迷你裁定册（entries 最小形）。"""
    path = root / _CATALOGS / "ruling_registry.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"entries": rulings}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def _ruling_461(**overrides) -> dict:
    """#461 形态基模：active + 明文覆盖 ruling_registry.yaml 的 approved_paths。"""
    entry = {
        "ruling_id": "裁定#461",
        "status": "active",
        "summary": "三热册改动授权",
        "approved_paths": [_RULING_REGISTRY_REL],
        "expires_at": "2099-01-01",
    }
    entry.update(overrides)
    return entry


class _FakeGateway:
    """最小 gateway 桩：project_root（resolver/gate 审计/锚定用）。"""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root


def _serializer_worktree_hit(root: Path, rel: str, *, singular: bool = True) -> str:
    """构造 serializer 落地工作树形态的绝对路径（q-...-0013 死信同款）。"""
    parts = [".runtime", "commit_queue", "worktree" if singular else "worktrees", "w0"]
    if singular:
        parts = [".runtime", "commit_queue", "worktree"]
    p = root.joinpath(*parts)
    return str(p / rel)


class TestRulingChannelLandingWorktreeWiring:
    """裁定通道接线（resolver 层）：落地工作树路径形态必须命中盘面 active 裁定。"""

    def test_ruling_461_explicit_cover_hits_from_singular_worktree_path(self, tmp_path):
        """#461 明文覆盖 ruling_registry.yaml：单数 worktree 形态命中 → PASS（q-...-0013 重放）。"""
        _make_ruling_registry(tmp_path, [_ruling_461()])
        hit = _serializer_worktree_hit(tmp_path, _RULING_REGISTRY_REL)
        v = resolve_approval([hit], None, tmp_path)
        assert v.approved is True, "落地链命中路径剥前缀后必须命中 #461 approved_paths"
        assert v.source == SOURCE_RULING
        assert "裁定#461" in v.detail

    def test_plural_slot_form_still_normalized(self, tmp_path):
        """复数 worktrees/<slot>/ 形态回归（k=4 通道池不回退）。"""
        _make_ruling_registry(tmp_path, [_ruling_461()])
        hit = _serializer_worktree_hit(tmp_path, _RULING_REGISTRY_REL, singular=False)
        v = resolve_approval([hit], None, tmp_path)
        assert v.approved is True and v.source == SOURCE_RULING

    def test_serializer_worktree_form_does_not_widen_authorization(self, tmp_path):
        """归一不放大授权面：#461 未覆盖的路径（AGENTS.md）在落地形态下照拦。"""
        _make_ruling_registry(tmp_path, [_ruling_461()])
        hit = _serializer_worktree_hit(tmp_path, "AGENTS.md")
        v = resolve_approval([hit], None, tmp_path)
        assert v.approved is False and v.source == SOURCE_NONE


class TestProtectedPathsGateWiring:
    """gate 层接线：protected_paths_gate 判定经 resolve_approval（无自有裁定遍历）。"""

    def test_gate_passes_via_ruling_channel_in_landing_form(self, tmp_path):
        """#461 迷你册 + 落地形态 ruling_registry.yaml staged → gate 放行并引裁定号。"""
        _make_ruling_registry(tmp_path, [_ruling_461()])
        gate = make_protected_paths_gate()
        hit = _serializer_worktree_hit(tmp_path, _RULING_REGISTRY_REL)
        passed, detail = gate.check(_FakeGateway(tmp_path), [hit], commit_message="chore: 裁定册登记")
        assert passed is True, f"有授权也审批不过（时序倒置未治）: {detail}"
        assert "covered by active ruling" in detail and "裁定#461" in detail

    def test_gate_blocks_without_active_ruling(self, tmp_path):
        """缺册（无 active 裁定）+ 无逃生通道 → 维持硬阻断（fail 面不放宽）。"""
        gate = make_protected_paths_gate()
        hit = _serializer_worktree_hit(tmp_path, _RULING_REGISTRY_REL)
        passed, detail = gate.check(_FakeGateway(tmp_path), [hit], commit_message="chore: 无授权改动")
        assert passed is False
        assert "PROTECTED-PATHS" in detail


class TestCreateGuardRegistryAnchoring:
    """CREATE-GUARD 同型治本：registry 读取锚主区盘面（"登记完即可提交"）。"""

    def test_create_guard_reads_main_root_disk_from_linked_worktree(self, tmp_path):
        """linked worktree 内读 registry 必须锚主区盘面——主区未提交的 token 可见。

        构造：主区提交无 token 的基底册 → git worktree add（worktree 盘面=基底版）
        → 主区盘面补登 token（未提交=入队前登记语义）→ CREATE-GUARD 从 worktree
        调 _load_capability_registry 必须读到主区盘面版本。
        """
        main = tmp_path / "main"
        reg_rel = Path(_CATALOGS)
        (main / reg_rel).mkdir(parents=True)
        registry = main / reg_rel / "capability_canonical_file_registry.yaml"
        registry.write_text(yaml.safe_dump({"creation_tokens": []}), encoding="utf-8")

        def git(*args: str) -> None:
            subprocess.run(["git", "-C", str(main), *args], check=True, capture_output=True)

        git("init", "-q", "--initial-branch=dev")
        git("config", "user.email", "t@t")
        git("config", "user.name", "t")
        git("add", "-A")
        git("commit", "-qm", "init")
        wt = tmp_path / "wt"
        git("worktree", "add", "-q", str(wt), "HEAD")

        # 主区盘面登记 token（未提交——"登记完即可提交"的登记面）
        new_file = "src/zephyr/gov_enforcement/commit_gates/new_thing.py"
        registry.write_text(
            yaml.safe_dump({"creation_tokens": [{"file": new_file, "token": "auto-wiring-2026-10-03"}]}),
            encoding="utf-8",
        )

        data, err = _load_capability_registry(_FakeGateway(wt))
        assert data is not None, f"registry 不可达: {err}"
        assert new_file in _collect_registered_files(data), "worktree 内必须读到主区盘面登记的 token"
