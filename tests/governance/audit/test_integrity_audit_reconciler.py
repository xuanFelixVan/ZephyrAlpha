# [A_test] module_id: SRC-TST-2098 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_integrity_audit_reconciler
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_integrity_audit_reconciler.py — GATE-INTEGRITY-AUDIT reconciler 单测

AD-GOV-001 合并后测试策略（治本红蓝对抗 P0-3/P1-6/P1-7）：
- **_make_old_* 已删除（2026-06-30 元问题4治本）**：原私有函数已内联到
  make_integrity_audit_reconciler 闭包中，Python 无真私有，保留等于留可 import
  的绕过入口。内联后 reconcile 逻辑仅在 make_* 闭包内可见。
- **公共 API 测试**：make_integrity_audit_reconciler 的 spec 属性和 trigger。
- **compose 行为测试**：用 mock spec 验证 _compose_reconcilers 的 trigger OR /
  reconcile 串联 / action 取较严重 / priority=max（治本 P1-7 零覆盖）。
- **核心逻辑测试**：直接调用模块级函数 _audit_commit_history 验证裸 commit 检测，
  不通过 ReconcilerSpec 包装（_audit_commit_history 是 commit_gateway_audit 的
  审计逻辑真源，已提取为模块级函数供 integrity_anchors 保护）。

compose 策略说明（P1-4 文档化）：
  _compose_reconcilers(gate_id, spec_a, spec_b) 合并两个 reconciler：
  - trigger = spec_a.trigger OR spec_b.trigger（任一命中即执行）
  - reconcile = 串联执行 spec_a.reconcile → spec_b.reconcile；action 取较严重
    （severity: skip/nothing=0, clean=1, warn=2, auto_committed=2），detail 拼接
  - priority = max(spec_a.priority, spec_b.priority)
  _make_old_* 私有函数已删除（2026-06-30 元问题4治本），reconcile 逻辑内联到
  5 个 make_* compose 包装函数闭包中，无法被外部 import 绕过 compose。

测试隔离: 所有测试用 tmp_path 临时 git 仓库，不污染生产库。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway  # noqa: E402
from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcileResult,
    ReconcilerSpec,
    _audit_commit_history,
    _compose_reconcilers,
    make_integrity_audit_reconciler,
    make_rule_audit_reconciler,
)


# ---------------------------------------------------------------------------
# 辅助函数
# ---------------------------------------------------------------------------
def _init_git_repo(repo_dir: Path) -> None:
    """在 tmp_path 初始化一个 git 仓库（含初始 commit）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "Test"
    env["GIT_AUTHOR_EMAIL"] = "test@test.com"
    env["GIT_COMMITTER_NAME"] = "Test"
    env["GIT_COMMITTER_EMAIL"] = "test@test.com"
    subprocess.run(["git", "init"], cwd=str(repo_dir), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(repo_dir), capture_output=True, check=True)
    # 初始 commit
    (repo_dir / ".gitignore").write_text("*.tmp\n.runtime/\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init [GW:setup]", "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _make_commit(repo_dir: Path, message: str) -> None:
    """创建一个新 commit（修改 .gitignore 触发变更）。"""
    gitignore = repo_dir / ".gitignore"
    content = gitignore.read_text(encoding="utf-8")
    gitignore.write_text(content + f"# {message}\n", encoding="utf-8")
    subprocess.run(["git", "add", ".gitignore"], cwd=str(repo_dir), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", message, "--no-verify"], cwd=str(repo_dir), capture_output=True, check=True)


def _make_mock_spec(
    gate_id: str,
    trigger_ret: bool,
    action: str,
    detail: str = "",
    priority: int = 100,
) -> ReconcilerSpec:
    """构造 mock ReconcilerSpec 用于 compose 行为测试。"""
    return ReconcilerSpec(
        gate_id=gate_id,
        trigger=lambda files: trigger_ret,
        reconcile=lambda files, sid: ReconcileResult(action=action, detail=detail),
        priority=priority,
    )


# ---------------------------------------------------------------------------
# TestSpecProperties — 公共 API spec 属性
# ---------------------------------------------------------------------------
class TestSpecProperties:
    """make_integrity_audit_reconciler spec 属性正确。"""

    def test_gate_id(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.gate_id == "GATE-INTEGRITY-AUDIT"

    def test_priority_is_last(self, tmp_path):
        """priority=810 最后执行（审计非阻断，低优先级；元问题1治本后含 agents_md_refs=810）。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.priority == 810


# ---------------------------------------------------------------------------
# TestTrigger — 公共 API trigger
# ---------------------------------------------------------------------------
class TestTrigger:
    """trigger always True——rules_integrity 与 commit_gw_audit 均 always True，
    agents_md_refs 检测特定文件（非 always True），OR 仍 always True（前两个保证）。"""

    def test_trigger_empty_files(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.trigger([]) is True

    def test_trigger_any_files(self, tmp_path):
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        assert spec.trigger(["src/foo.py", "docs/bar.md"]) is True


# ---------------------------------------------------------------------------
# TestComposeTrigger — compose trigger OR 逻辑（P1-7 治本零覆盖）
# ---------------------------------------------------------------------------
class TestComposeTrigger:
    """_compose_reconcilers 的 trigger = spec_a.trigger OR spec_b.trigger。"""

    def test_trigger_both_false(self):
        """两个 trigger 都 False → False。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=False, action="clean")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=False, action="clean")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.trigger(["any"]) is False

    def test_trigger_a_true_b_false(self):
        """A trigger True, B trigger False → True。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=False, action="clean")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.trigger(["any"]) is True

    def test_trigger_a_false_b_true(self):
        """A trigger False, B trigger True → True。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=False, action="clean")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.trigger(["any"]) is True

    def test_trigger_both_true(self):
        """两个 trigger 都 True → True。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.trigger(["any"]) is True


# ---------------------------------------------------------------------------
# TestComposeReconcileAction — compose action 取较严重（P1-7 治本零覆盖）
# ---------------------------------------------------------------------------
class TestComposeReconcileAction:
    """_compose_reconcilers 的 action 取较严重值（severity 高者胜）。"""

    def test_action_clean_vs_warn_warn_wins(self):
        """A=clean(1), B=warn(2) → warn(2)。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean", detail="a ok")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="warn", detail="b bad")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        result = composed.reconcile([], "sess-test")
        assert result.action == "warn"
        assert "a ok" in result.detail
        assert "b bad" in result.detail

    def test_action_warn_vs_clean_warn_wins(self):
        """A=warn(2), B=clean(1) → warn(2)。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="warn", detail="a bad")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", detail="b ok")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        result = composed.reconcile([], "sess-test")
        assert result.action == "warn"

    def test_action_both_clean_clean_wins(self):
        """A=clean(1), B=clean(1) → clean(1)。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean", detail="a ok")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", detail="b ok")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        result = composed.reconcile([], "sess-test")
        assert result.action == "clean"

    def test_action_skip_vs_clean_clean_wins(self):
        """A=skip(0), B=clean(1) → clean(1)。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="skip", detail="a skip")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", detail="b ok")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        result = composed.reconcile([], "sess-test")
        assert result.action == "clean"

    def test_action_auto_committed_vs_clean_auto_committed_wins(self):
        """A=auto_committed(2), B=clean(1) → auto_committed(2)。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="auto_committed", detail="a auto")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", detail="b ok")
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        result = composed.reconcile([], "sess-test")
        assert result.action == "auto_committed"

    def test_reconcile_executes_both_in_order(self):
        """reconcile 串联执行 A→B（验证两者都被调用）。"""
        call_order = []

        spec_a = ReconcilerSpec(
            gate_id="GATE-A",
            trigger=lambda files: True,
            reconcile=lambda files, sid: (call_order.append("A"), ReconcileResult(action="clean", detail="a"))[1],
            priority=100,
        )
        spec_b = ReconcilerSpec(
            gate_id="GATE-B",
            trigger=lambda files: True,
            reconcile=lambda files, sid: (call_order.append("B"), ReconcileResult(action="clean", detail="b"))[1],
            priority=200,
        )
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        composed.reconcile([], "sess-test")
        assert call_order == ["A", "B"]


# ---------------------------------------------------------------------------
# TestComposePriority — compose priority=max（P1-7 治本零覆盖）
# ---------------------------------------------------------------------------
class TestComposePriority:
    """_compose_reconcilers 的 priority = max(spec_a.priority, spec_b.priority)。"""

    def test_priority_a_higher(self):
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean", priority=800)
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", priority=270)
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.priority == 800

    def test_priority_b_higher(self):
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean", priority=100)
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", priority=500)
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.priority == 500

    def test_priority_equal(self):
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean", priority=300)
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean", priority=300)
        composed = _compose_reconcilers("GATE-COMPOSED", spec_a, spec_b)
        assert composed.priority == 300

    def test_composed_gate_id(self):
        """compose 后 gate_id 为传入的新 gate_id。"""
        spec_a = _make_mock_spec("GATE-A", trigger_ret=True, action="clean")
        spec_b = _make_mock_spec("GATE-B", trigger_ret=True, action="clean")
        composed = _compose_reconcilers("GATE-INTEGRITY-AUDIT", spec_a, spec_b)
        assert composed.gate_id == "GATE-INTEGRITY-AUDIT"


# ---------------------------------------------------------------------------
# TestAuditCommitHistory — 裸 commit 检测核心逻辑（模块级函数直测）
# ---------------------------------------------------------------------------
class TestAuditCommitHistory:
    """_audit_commit_history 模块级函数——commit_gateway_audit 审计逻辑真源。

    直接调用模块级函数测试，不通过 _make_old_* 或 ReconcilerSpec 包装，
    治本红蓝对抗 P0-3（测试 import 私有函数反模式）。
    """

    def test_all_gw_commits_clean(self, tmp_path):
        """全部 commit 含 [GW: 标记 → violations 为空。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: add a [GW:sess-001]")
        _make_commit(tmp_path, "feat: add b [GW:sess-002:auto]")
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        assert violations == []

    def test_bare_commit_detected(self, tmp_path):
        """存在无 [GW: 标记的裸 commit → violations 非空。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: gateway commit [GW:sess-001]")
        _make_commit(tmp_path, "feat: bare commit no marker")  # 裸 commit
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        # init commit + 1 bare = 2 violations（init 也不含 [GW:）
        assert len(violations) >= 1
        assert any("bare commit no marker" in v["subject"] for v in violations)

    def test_multiple_bare_commits_detected(self, tmp_path):
        """多个裸 commit 都被检测到。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "bare one")
        _make_commit(tmp_path, "feat: ok [GW:s1]")
        _make_commit(tmp_path, "bare two")
        _make_commit(tmp_path, "bare three")
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        # init + bare one + bare two + bare three = 4 violations（init 也不含 [GW:）
        assert len(violations) >= 3
        subjects = [v["subject"] for v in violations]
        assert any("bare one" in s for s in subjects)
        assert any("bare two" in s for s in subjects)
        assert any("bare three" in s for s in subjects)

    def test_merge_commit_not_flagged(self, tmp_path):
        """merge commit 跳过（合并提交无作者意图，不误报）。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: on main [GW:s1]")
        branch_r = subprocess.run(["git", "branch"], cwd=str(tmp_path), capture_output=True, text=True)
        main_branch = "master" if "master" in branch_r.stdout else "main"
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=str(tmp_path), capture_output=True, check=True)
        _make_commit(tmp_path, "feat: on branch [GW:s2]")
        subprocess.run(["git", "checkout", main_branch], cwd=str(tmp_path), capture_output=True, check=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "feature", "-m", "Merge branch 'feature' [GW:merge]"],
            cwd=str(tmp_path), capture_output=True, check=True,
        )
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        # merge commit 被跳过，其他 commit 都有 [GW:（含 init）→ 0 violations
        assert violations == []

    def test_merge_without_marker_not_flagged(self, tmp_path):
        """merge commit 即使无 [GW: 标记也不误报（跳过 merge）。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "feat: ok [GW:s1]")
        branch_r = subprocess.run(["git", "branch"], cwd=str(tmp_path), capture_output=True, text=True)
        main_branch = "master" if "master" in branch_r.stdout else "main"
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=str(tmp_path), capture_output=True, check=True)
        _make_commit(tmp_path, "feat: on branch [GW:s2]")
        subprocess.run(["git", "checkout", main_branch], cwd=str(tmp_path), capture_output=True, check=True)
        subprocess.run(
            ["git", "merge", "--no-ff", "feature", "-m", "Merge branch 'feature'"],  # 无 [GW: 标记
            cwd=str(tmp_path), capture_output=True, check=True,
        )
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        # merge commit 被跳过，其他 commit 都有 [GW: → 0 violations
        assert violations == []

    def test_gw_marker_in_body_not_flagged(self, tmp_path):
        """[GW: 标记在 body 末尾（非 subject）也不误报。"""
        _init_git_repo(tmp_path)
        # 创建一个 subject 无 [GW: 但 body 有 [GW: 的 commit
        gitignore = tmp_path / ".gitignore"
        content = gitignore.read_text(encoding="utf-8")
        gitignore.write_text(content + "# body test\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=str(tmp_path), capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: body test", "-m", "[GW:sess-body]", "--no-verify"],
            cwd=str(tmp_path), capture_output=True, check=True,
        )
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        # body 含 [GW: → 不算裸 commit → 0 violations（init 也不含 [GW:... 等等）
        # init commit "init [GW:setup]" subject 含 [GW: → 不算违规
        # "feat: body test" subject 无 [GW: 但 body 有 → 不算违规
        assert violations == []

    def test_violation_dict_has_hash_and_subject(self, tmp_path):
        """违规字典含 hash 和 subject 字段。"""
        _init_git_repo(tmp_path)
        _make_commit(tmp_path, "bare commit for dict check")
        violations, err = _audit_commit_history(tmp_path, audit_window=20, gw_marker="[GW:")
        assert err is None
        assert len(violations) >= 1
        v = violations[0]
        assert "hash" in v
        assert "subject" in v
        assert "[GW:" not in v["subject"]


# ---------------------------------------------------------------------------
# TestAgentsMdRefs — 元问题1治本：AGENTS.md 引用有效性检测（2026-06-30）
# ---------------------------------------------------------------------------
class TestAgentsMdRefs:
    """GATE-AGENTS-MD-REFS 引用有效性检测——检测 AGENTS.md 中引用的
    make_*_reconciler 公共函数名是否在 reconciliation_registry.__all__ 中。

    治本病根：AGENTS.md 硬编码函数名，reconciler 重命名/合并后 AGENTS.md 不会
    自动更新，新AI按失效指引造幻觉。本检测在 commit 后自动告警失效引用。

    测试策略：直接调用 compose spec.reconcile，检查 detail 中是否含 agents_md_refs
    部分的结果（rules_integrity 在 tmp_path 无 validate_rules_integrity.py 会失败
    产生 warn，但不影响 agents_md_refs 部分的 detail）。
    """

    def test_agents_md_not_found(self, tmp_path):
        """AGENTS.md 不存在 → detail 含 'AGENTS.md not found'。"""
        _init_git_repo(tmp_path)
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert "AGENTS.md not found" in result.detail

    def test_agents_md_valid_refs(self, tmp_path):
        """AGENTS.md 引用全部有效（make_integrity_audit_reconciler 在 __all__ 中）→ detail 含 'refs all valid'。"""
        _init_git_repo(tmp_path)
        (tmp_path / "AGENTS.md").write_text(
            "see make_integrity_audit_reconciler for details",
            encoding="utf-8",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert "AGENTS.md refs all valid" in result.detail

    def test_agents_md_stale_ref(self, tmp_path):
        """AGENTS.md 含失效引用（make_baseline_aware_reconciler 已合并删除）→ detail 含 'stale' + 失效函数名。"""
        _init_git_repo(tmp_path)
        (tmp_path / "AGENTS.md").write_text(
            "see make_baseline_aware_reconciler for details",
            encoding="utf-8",
        )
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_integrity_audit_reconciler(gw)
        result = spec.reconcile([], "sess-test")
        assert "stale reconciliation_registry functions" in result.detail
        assert "make_baseline_aware_reconciler" in result.detail


# ---------------------------------------------------------------------------
# TestArchRefs — 元问题2治本：#ARCH-XXX 引用查重检测（2026-06-30）
# ---------------------------------------------------------------------------
class TestArchRefs:
    """GATE-ARCH-REFS #ARCH-XXX 引用查重检测——检测 committed_files 中的
    #ARCH-XXX 引用是否在 architecture_issue_registry.yaml 的 entries 中。

    治本病根：注册表铁律#6"任何 #ARCH-XXX 引用必须在本注册表有对应条目"是
    君子协定，无技术强制。#ARCH-027 冲突就是 AI 占位而不查重导致的。

    测试策略：直接调用 make_rule_audit_reconciler 的 spec.reconcile，检查
    detail 中是否含 arch_refs 部分的结果（catalog 在 tmp_path 无
    generate_rule_catalog.py 会失败产生 warn，但不影响 arch_refs 部分的 detail）。
    """

    _ARCH_REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml"

    def _setup_arch_registry(self, repo_dir: Path, entries_yaml: str) -> None:
        """在 tmp_path 创建 architecture_issue_registry.yaml。"""
        registry_dir = repo_dir / "docs/01_policies_and_standards/_registry/catalogs"
        registry_dir.mkdir(parents=True, exist_ok=True)
        (registry_dir / "architecture_issue_registry.yaml").write_text(
            entries_yaml, encoding="utf-8"
        )

    def test_arch_no_refs(self, tmp_path):
        """committed_files 无 #ARCH-XXX 引用 → detail 含 'no #ARCH-XXX refs'。"""
        _init_git_repo(tmp_path)
        self._setup_arch_registry(tmp_path, "entries:\n- issue_id: '#ARCH-008'\n  title: test\n  status: open\n")
        test_file = tmp_path / "test.md"
        test_file.write_text("no arch refs here", encoding="utf-8")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_rule_audit_reconciler(gw)
        result = spec.reconcile([str(test_file)], "sess-test")
        assert "no #ARCH-XXX refs" in result.detail

    def test_arch_valid_ref(self, tmp_path):
        """committed_files 含已登记的 #ARCH-008 引用 → detail 含 'all #ARCH-XXX refs registered'。"""
        _init_git_repo(tmp_path)
        self._setup_arch_registry(tmp_path, "entries:\n- issue_id: '#ARCH-008'\n  title: test\n  status: open\n")
        test_file = tmp_path / "test.md"
        test_file.write_text("see #ARCH-008 for details", encoding="utf-8")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_rule_audit_reconciler(gw)
        result = spec.reconcile([str(test_file)], "sess-test")
        assert "all #ARCH-XXX refs registered" in result.detail

    def test_arch_stale_ref(self, tmp_path):
        """committed_files 含未登记的 #ARCH-999 引用 → detail 含 'unregistered' + '#ARCH-999'。"""
        _init_git_repo(tmp_path)
        self._setup_arch_registry(tmp_path, "entries:\n- issue_id: '#ARCH-008'\n  title: test\n  status: open\n")
        test_file = tmp_path / "test.md"
        test_file.write_text("see #ARCH-999 for details", encoding="utf-8")
        gw = GitCommitGateway(project_root=tmp_path)
        spec = make_rule_audit_reconciler(gw)
        result = spec.reconcile([str(test_file)], "sess-test")
        assert "unregistered #ARCH-XXX ids" in result.detail
        assert "#ARCH-999" in result.detail
