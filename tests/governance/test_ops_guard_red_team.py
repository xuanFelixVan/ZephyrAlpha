# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [A_module] module_id=MOD-D5_ARCH_TOOLS | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
# [MODULE] tests.governance.test_ops_guard_red_team
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.ops_guard
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 红队攻击向量 100% 被拦截（S1 验收标准）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assert
# [TESTS] self
# [TTL] permanent
"""test_ops_guard_red_team.py — S1 删除拦截红队测试（wipe 事故治本验收）

验收标准（裁定书 S1）：红队测试"模拟 AI 构造批量删除命令"必须 100% 被拦。

攻击向量覆盖四类删除原语 × 保护区/白名单/授权三维度：
  1. PowerShell Remove-Item -Recurse（wipe 事故实际执行原语）
  2. CMD del /s / rd /s / rmdir /s
  3. Python shutil.rmtree / os.remove 批量模式
  4. git clean（git_guard 已拦，ops_guard 兜底）

另测 Python API（guard_rmtree/guard_remove）的阻断与放行。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# 确保项目根在 path 中
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts import ops_guard as ops_guard_mod  # noqa: E402
from scripts.ops_guard import (  # noqa: E402
    DeleteBlockedError,
    analyze_delete_command,
    guard_remove,
    guard_rmtree,
)

# 测试卫生治本（2026-08-27，Owner 裁定五a）：授权环境变量隔离。
# 病灶实证：ZEPHYR_COMMIT_GATEWAY=1 泄漏进 pytest 进程时，_is_authorized() 恒 True，
# 全部攻击向量"授权放行"→红队拦截率假读 0%（49 failed/38 passed 实测复现）；
# 干净环境 87/87 全绿。红队的职责是证明"未授权必拦"，故模块级固定剔除两个授权变量，
# 使本文件结果不再依赖宿主环境泄漏。
_AUTH_ENV_VARS = ("ZEPHYR_COMMIT_GATEWAY", "ZEPHYR_FORCE_DELETE", "ZEPHYR_DELETE_AUTHZ_NARROWED")


@pytest.fixture(autouse=True)
def _scrub_auth_env(monkeypatch):
    """每个用例执行前剔除授权环境变量（防宿主泄漏致授权放行假阴性）。"""
    for var in _AUTH_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    yield


# ============================================================================
# 红队攻击向量（必须 100% 被拦截）
# ============================================================================

# PowerShell Remove-Item -Recurse 攻击向量
PS_ATTACK_VECTORS = [
    # wipe 事故场景重现：三 worktree 被清空
    "Remove-Item -Recurse -Force .worktrees\\AI-BGT-001",
    "Remove-Item -Recurse -Force .worktrees\\AI-LIQ-001",
    "Remove-Item -Recurse -Force .worktrees\\AI-SELL-001",
    # .worktrees 根目录整体删除（二次删除场景）
    "Remove-Item -Recurse -Force .worktrees",
    "Remove-Item -Recurse -Force .worktrees\\",
    "Remove-Item -Recurse -Force D:\\ZephyrAlpha\\.worktrees",
    "Remove-Item -Recurse -Force D:\\ZephyrAlpha\\.worktrees\\AI-BGT-001",
    # src/ docs/ tests/ 递归删除
    "Remove-Item -Recurse -Force src",
    "Remove-Item -Recurse -Force src\\zephyr",
    "Remove-Item -Recurse -Force docs",
    "Remove-Item -Recurse -Force docs\\02_enterprise_architecture",
    "Remove-Item -Recurse -Force tests",
    "Remove-Item -Recurse -Force tests\\governance",
    # 仓库根递归删除
    "Remove-Item -Recurse -Force D:\\ZephyrAlpha",
    "Remove-Item -Recurse -Force .",
    # 带 -Path 显式参数
    "Remove-Item -Path .worktrees\\AI-X -Recurse -Force",
    "Remove-Item -Path src\\zephyr -Recurse",
    # PowerShell 别名
    "ri -Recurse -Force .worktrees\\AI-X",
    "rm -Recurse -Force .worktrees\\AI-X",
]

# CMD del/rd/rmdir 攻击向量
CMD_ATTACK_VECTORS = [
    "del /s /q src\\*",
    "del /s /q .worktrees\\AI-BGT-001\\*",
    "rd /s /q .worktrees",
    "rd /s /q src",
    "rd /s /q docs",
    "rd /s /q tests",
    "rmdir /s /q .worktrees\\AI-LIQ-001",
    "rmdir /s /q D:\\ZephyrAlpha\\.worktrees",
    "del /s /q D:\\ZephyrAlpha\\src\\*",
    "erase /s /q docs\\*",
]

# Python 删除攻击向量
PYTHON_ATTACK_VECTORS = [
    # shutil.rmtree
    "shutil.rmtree('.worktrees/AI-BGT-001')",
    "shutil.rmtree('.worktrees')",
    "shutil.rmtree('src')",
    "shutil.rmtree('docs')",
    "shutil.rmtree('tests')",
    "shutil.rmtree('D:/ZephyrAlpha/.worktrees/AI-SELL-001')",
    "shutil.rmtree('D:\\\\ZephyrAlpha\\\\.worktrees')",
    # os.remove 批量模式（循环删除——wipe 事故可能形态）
    "for f in Path('.worktrees/AI-X').rglob('*'): os.remove(f)",
    "for f in os.listdir('src'): os.remove(f)",
    # python -c 形式
    "python -c \"import shutil; shutil.rmtree('.worktrees/AI-X')\"",
]

# git clean 攻击向量（git_guard 已拦，ops_guard 兜底）
GIT_ATTACK_VECTORS = [
    "git clean -fd",
    "git clean -fdx",
    "git clean -f .worktrees/",
]

# 全部攻击向量
ALL_ATTACK_VECTORS = PS_ATTACK_VECTORS + CMD_ATTACK_VECTORS + PYTHON_ATTACK_VECTORS + GIT_ATTACK_VECTORS


class TestRedTeamAttackVectorsBlocked:
    """红队核心测试：所有攻击向量必须 100% 被拦截。"""

    @pytest.mark.parametrize("cmd", ALL_ATTACK_VECTORS, ids=lambda c: c[:60])
    def test_attack_blocked(self, cmd: str) -> None:
        """每个攻击向量都必须被 analyze_delete_command 阻断。"""
        verdict = analyze_delete_command(cmd)
        assert not verdict.allowed, (
            f"红队攻击未被拦截: {cmd}\n"
            f"  verdict.primitive={verdict.primitive}\n"
            f"  verdict.targets={verdict.targets}\n"
            f"  verdict.reason={verdict.reason}"
        )
        assert verdict.is_protected_zone, f"攻击未标记为保护区: {cmd}\n  targets={verdict.targets}"

    def test_attack_vector_count(self) -> None:
        """确保攻击向量覆盖面（防止意外删减导致测试空心化）。"""
        assert len(PS_ATTACK_VECTORS) >= 15, "PowerShell 攻击向量不足"
        assert len(CMD_ATTACK_VECTORS) >= 8, "CMD 攻击向量不足"
        assert len(PYTHON_ATTACK_VECTORS) >= 8, "Python 攻击向量不足"
        assert len(GIT_ATTACK_VECTORS) >= 2, "git clean 攻击向量不足"
        assert len(ALL_ATTACK_VECTORS) >= 33, "总攻击向量不足 33 条"

    def test_100_percent_interception_rate(self) -> None:
        """S1 验收标准：红队 100% 拦截率。"""
        total = len(ALL_ATTACK_VECTORS)
        blocked = sum(1 for cmd in ALL_ATTACK_VECTORS if not analyze_delete_command(cmd).allowed)
        rate = blocked / total * 100
        assert rate == 100.0, f"拦截率 {rate:.1f}%（{blocked}/{total}），未达 100%"


class TestWhitelistAllowed:
    """白名单路径必须放行（不误伤合法删除）。"""

    @pytest.mark.parametrize(
        "cmd",
        [
            "Remove-Item .runtime\\tmp\\cache_file.txt",
            "Remove-Item -Recurse .runtime\\tmp\\old_cache",
            "Remove-Item -Recurse __pycache__",
            "Remove-Item -Recurse .pytest_cache",
            "Remove-Item -Recurse .mypy_cache",
            "Remove-Item -Recurse node_modules",
            "Remove-Item README.md",
            "Remove-Item scripts\\temp_script.py",
            "del .runtime\\tmp\\file.txt",
            "del temp.log",
        ],
        ids=lambda c: c[:50],
    )
    def test_whitelist_allowed(self, cmd: str) -> None:
        """白名单路径和显式单文件删除必须放行。"""
        verdict = analyze_delete_command(cmd)
        assert verdict.allowed, f"白名单/单文件删除被误拦: {cmd}\n  reason={verdict.reason}"


class TestNonRecursiveSingleFile:
    """非递归单文件删除放行（目标在保护区目录下但已 tracked——docs/ untracked 见 T3② 专类）。"""

    @pytest.mark.parametrize(
        "cmd",
        [
            "Remove-Item src\\zephyr\\old_module.py",
            "Remove-Item tests\\test_old.py",
            "Remove-Item .worktrees\\AI-X\\temp.txt",
            "del src\\zephyr\\old_file.py",
        ],
        ids=lambda c: c[:50],
    )
    def test_single_file_allowed(self, cmd: str) -> None:
        """显式单文件（非递归）删除在保护区内也放行。"""
        verdict = analyze_delete_command(cmd)
        assert verdict.allowed, f"单文件删除被误拦: {cmd}\n  reason={verdict.reason}"
        assert not verdict.is_recursive


class TestDocsUntrackedGuard:
    """T3②（#ARCH-RECONCILER-AUTO-DELETE-GOV-001）：docs/ 下 untracked 文件
    删除/移动需人工确认——清风草稿丢失治本（三重无保护：不在 git/归档器可动/
    删除无追溯）。"""

    def test_untracked_docs_single_file_blocked(self) -> None:
        """untracked docs 草稿（git 索引中不存在）单文件删除 → 阻断。"""
        verdict = analyze_delete_command("Remove-Item docs\\temp_draft.md")
        assert not verdict.allowed, "untracked docs 草稿删除未被拦（清风案重演通道）"
        assert "untracked" in verdict.reason

    def test_gateway_env_does_not_bypass(self) -> None:
        """反架空：ZEPHYR_COMMIT_GATEWAY=1 不豁免（worker 继承 gateway 标记，
        若认 gateway 则全部 reconciler 天然已授权、闸门形同虚设）。"""
        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1"}):
            os.environ.pop("ZEPHYR_FORCE_DELETE", None)
            verdict = analyze_delete_command("Remove-Item docs\\temp_draft.md")
            assert not verdict.allowed, "gateway 标记错误豁免了 untracked docs 闸门"

    def test_force_env_allows(self) -> None:
        """人工确认标记 ZEPHYR_FORCE_DELETE=1 → 放行（仍落审计）。"""
        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            verdict = analyze_delete_command("Remove-Item docs\\temp_draft.md")
            assert verdict.allowed

    def test_tracked_docs_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """已 tracked 的 docs 文件单文件删除放行（T3② 不误伤 git 安全网内文件）。"""
        monkeypatch.setattr(ops_guard_mod, "_is_docs_untracked", lambda *a, **kw: False)
        verdict = analyze_delete_command("Remove-Item docs\\tracked_doc.md")
        assert verdict.allowed, f"tracked docs 单文件删除被误拦: reason={verdict.reason}"


class TestAuthorizedBypass:
    """授权环境变量放行（合法清理场景逃生通道）。"""

    def test_force_env_allows_protected_delete(self) -> None:
        """ZEPHYR_FORCE_DELETE=1 时保护区递归删除放行（但仍落审计）。"""
        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            verdict = analyze_delete_command("Remove-Item -Recurse -Force .worktrees\\AI-OLD-DONE")
            assert verdict.allowed
            assert verdict.is_protected_zone  # 仍标记保护区（审计用）
            assert "授权" in verdict.reason

    def test_gateway_env_never_allows_protected_delete(self) -> None:
        """#ARCH-279 翻硬拦终态：ZEPHYR_COMMIT_GATEWAY=1 保护区递归删除必拦。

        旧行为（本测试原位历史记录）：GATEWAY 标记曾构成删除授权——三起 3500+
        文件误删的授权面病灶（pytest 继承标记→"授权放行"→真删）。观测收尾
        （39,642 条零合法消费方+观测窗零命中）后永久退出删除域。
        """
        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1"}):
            verdict = analyze_delete_command("Remove-Item -Recurse -Force .worktrees\\AI-OLD-DONE")
            assert not verdict.allowed
            assert verdict.is_protected_zone


class TestNonDeleteCommands:
    """非删除命令不拦截。"""

    @pytest.mark.parametrize(
        "cmd",
        [
            "Get-ChildItem .worktrees",
            "git status",
            "git log --oneline",
            "python scripts/git_guard.py add file.py",
            "pytest tests/governance/",
            "ls src/zephyr",
            "cat README.md",
            "",
        ],
        ids=lambda c: c[:40] if c else "empty",
    )
    def test_non_delete_allowed(self, cmd: str) -> None:
        """非删除命令一律放行。"""
        verdict = analyze_delete_command(cmd)
        assert verdict.allowed
        assert verdict.primitive == "unknown"


class TestPythonAPI:
    """guard_rmtree / guard_remove Python API 测试。"""

    def test_guard_rmtree_blocks_protected(self, tmp_path: Path) -> None:
        """guard_rmtree 阻断保护区路径。"""
        with pytest.raises(DeleteBlockedError, match="OPS-GUARD"):
            guard_rmtree(".worktrees/AI-FAKE-001")

    def test_guard_rmtree_blocks_src(self) -> None:
        """guard_rmtree 阻断 src/ 路径。"""
        with pytest.raises(DeleteBlockedError, match="OPS-GUARD"):
            guard_rmtree("src/zephyr")

    def test_guard_rmtree_allows_whitelist(self, tmp_path: Path) -> None:
        """guard_rmtree 放行白名单路径（实际删除临时目录）。"""
        target = tmp_path / ".runtime" / "tmp" / "test_cache"
        target.mkdir(parents=True)
        (target / "dummy.txt").write_text("x")
        # 不阻断（白名单路径），实际执行删除
        guard_rmtree(str(target))
        assert not target.exists()

    def test_guard_remove_audit(self, tmp_path: Path) -> None:
        """guard_remove 单文件删除落审计并执行。"""
        target = tmp_path / "test.txt"
        target.write_text("x")
        guard_remove(str(target))
        assert not target.exists()

    def test_guard_rmtree_authorized(self) -> None:
        """授权环境下 guard_rmtree 放行保护区路径——但 pytest 上下文不得真删浅层（2026-08-27 三起误删治本不变量）。

        历史行为：FORCE_DELETE=1 时分析层放行且不 raise（目录不存在故无事）。
        新不变量：pytest 上下文中，即使授权放行，命中保护区浅层（.worktrees/X 深度2）
        的执行必须硬拦——本测试即回归该不变量（防止授权泄漏下测试真删 src/zephyr 同型复发）。
        """
        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            with pytest.raises(DeleteBlockedError, match="pytest 上下文禁止真删保护区浅层"):
                guard_rmtree(".worktrees/AI-FAKE-NONEXIST")

    def test_pytest_invariant_blocks_src_even_authorized(self) -> None:
        """核心回归（三起误删同型）：授权投毒环境下 guard_rmtree('src/zephyr') 必须硬拦。

        事故链：pytest 进程继承 ZEPHYR_COMMIT_GATEWAY=1 → 分析层"授权放行" →
        guard_rmtree 真删 src/zephyr 整包（03:27/08:24/12:27 三起）。修复后：
        pytest 上下文永不真删保护区浅层，与授权变量无关。
        """
        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1", "ZEPHYR_FORCE_DELETE": "1"}):
            with pytest.raises(DeleteBlockedError, match="pytest 上下文禁止真删保护区浅层"):
                guard_rmtree("src/zephyr")

    def test_pytest_invariant_ignores_deep_fixture_path(self, tmp_path: Path) -> None:
        """不变量不误伤深层测试 fixture 路径（tests/x/y 深度≥3 不触发）。

        tests/ 是保护区前缀，但测试自建 fixture 位于更深层级（前缀深度+2 及以上），
        不在不变量范围——guard_rmtree 按常规规则判定（此处经绝对路径落白名单/非保护区执行）。
        """
        from scripts.ops_guard import _enforce_pytest_never_delete_protected

        # 深度 3（tests/governance/tmp_x）> 前缀 tests 深度1+1 → 不触发不变量（不 raise）
        _enforce_pytest_never_delete_protected("rmtree", "tests/governance/tmp_x", "tests/governance/tmp_x")
        # 白名单深层同样不触发
        _enforce_pytest_never_delete_protected("rmtree", ".runtime/tmp/pytest_x/y", ".runtime/tmp/pytest_x/y")


class TestPrimitiveDetection:
    """原语识别正确性。"""

    def test_powershell_primitive(self) -> None:
        v = analyze_delete_command("Remove-Item -Recurse -Force .worktrees\\X")
        assert v.primitive == "powershell_recurse"
        assert v.is_recursive

    def test_cmd_primitive(self) -> None:
        v = analyze_delete_command("rd /s /q .worktrees")
        assert v.primitive == "cmd_recurse"
        assert v.is_recursive

    def test_python_rmtree_primitive(self) -> None:
        v = analyze_delete_command("shutil.rmtree('.worktrees/X')")
        assert v.primitive == "python_rmtree"
        assert v.is_recursive

    def test_python_batch_remove_primitive(self) -> None:
        v = analyze_delete_command("for f in Path('src').rglob('*'): os.remove(f)")
        assert v.primitive == "python_remove_batch"
        assert v.is_recursive

    def test_git_clean_primitive(self) -> None:
        v = analyze_delete_command("git clean -fd")
        assert v.primitive == "git_clean"
        assert v.is_recursive

    def test_absolute_path_resolution(self) -> None:
        """绝对路径正确解析为仓库相对路径。"""
        v = analyze_delete_command("Remove-Item -Recurse -Force D:\\ZephyrAlpha\\.worktrees\\AI-X")
        assert not v.allowed
        assert any(".worktrees" in t for t in v.targets)

    def test_repo_root_target(self) -> None:
        """仓库根本身作为删除目标被阻断。"""
        v = analyze_delete_command("Remove-Item -Recurse -Force D:\\ZephyrAlpha")
        assert not v.allowed
        assert v.is_protected_zone


class TestQuarantineProtected:
    """O4②（#ARCH-264，2026-08-26）：.runtime/quarantine 纳入保护区。

    drift watchdog 告警快照是事故取证存证——2026-08-25/26 两起带外裸删
    （drift_* 选择性清除、零审计）实证该目录需要与 src/docs/tests 同级保护。
    """

    def test_recursive_quarantine_delete_blocked(self) -> None:
        """递归删除告警快照目录 → 阻断（带外清柜通道封死）。"""
        v = analyze_delete_command("Remove-Item -Recurse -Force .runtime\\quarantine\\drift_20260825T165500")
        assert not v.allowed, "quarantine 快照目录递归删除未被拦"
        assert v.is_protected_zone

    def test_recursive_quarantine_root_delete_blocked(self) -> None:
        """递归删除整个 quarantine 目录 → 阻断。"""
        v = analyze_delete_command("rd /s /q .runtime\\quarantine")
        assert not v.allowed, "quarantine 根目录递归删除未被拦"
        assert v.is_protected_zone

    def test_force_env_allows_quarantine(self) -> None:
        """人工确认标记 ZEPHYR_FORCE_DELETE=1 → 授权放行（授权通道唯一化，仍落审计）。"""
        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            v = analyze_delete_command("Remove-Item -Recurse -Force .runtime\\quarantine\\drift_20260825T165500")
        assert v.allowed


class TestAuthzNarrowing279:
    """#ARCH-279 裁定A：GATEWAY_ENV 退出删除域（2026-08-27 观测收尾翻硬拦终态）。

    收尾实证：历史 39,642 条审计零合法消费方 + 观测窗 would_block_if_narrowed
    零命中 → GATEWAY_ENV 永久退出删除域（提交域防伪语义不受影响）；
    FORCE_ENV（人工显式）= 删除授权唯一通道；原 NARROWED 开关随转正退役。
    """

    def test_semantic_matrix_clean_env(self) -> None:
        """干净环境 → 未授权。"""
        from scripts.ops_guard import _is_delete_authorized

        assert _is_delete_authorized() == (False, False)

    def test_semantic_matrix_force_is_sole_channel(self) -> None:
        """FORCE_ENV=1 → 授权（人工显式=唯一通道）。"""
        from scripts.ops_guard import _is_delete_authorized

        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            assert _is_delete_authorized() == (True, False)

    def test_semantic_matrix_gateway_never_authorizes(self) -> None:
        """硬拦终态：GATEWAY_ENV=1 → 永不构成删除授权（无需任何开关）。"""
        from scripts.ops_guard import _is_delete_authorized

        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1"}):
            assert _is_delete_authorized() == (False, False)

    def test_semantic_matrix_gateway_with_dead_switch_still_blocked(self) -> None:
        """退役开关 ZEPHYR_DELETE_AUTHZ_NARROWED 不再有任何效力（防误信旧文档）。"""
        from scripts.ops_guard import _is_delete_authorized

        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1", "ZEPHYR_DELETE_AUTHZ_NARROWED": "1"}):
            assert _is_delete_authorized() == (False, False)

    def test_semantic_matrix_force_survives_narrowing(self) -> None:
        """FORCE_ENV=1（含 GATEWAY 同存）→ 仍授权（人工通道唯一且不受收窄影响）。"""
        from scripts.ops_guard import _is_delete_authorized

        env = {"ZEPHYR_FORCE_DELETE": "1", "ZEPHYR_COMMIT_GATEWAY": "1", "ZEPHYR_DELETE_AUTHZ_NARROWED": "1"}
        with patch.dict(os.environ, env):
            assert _is_delete_authorized() == (True, False)

    def test_analyze_gateway_poisoned_blocked_by_default(self) -> None:
        """硬拦终态：GATEWAY 投毒下保护区删除默认必拦——不再依赖 pytest 不变量单点兜底。"""
        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1"}):
            v = analyze_delete_command("Remove-Item -Recurse -Force src\\zephyr\\some_pkg\\sub")
        assert not v.allowed
        assert v.is_protected_zone

    def test_analyze_force_no_observation_mark(self) -> None:
        """FORCE 人工授权：放行且 reason 无观测标记（观测期已结束）。"""
        with patch.dict(os.environ, {"ZEPHYR_FORCE_DELETE": "1"}):
            v = analyze_delete_command("Remove-Item -Recurse -Force src\\zephyr\\some_pkg\\sub")
        assert v.allowed
        assert "would_block_if_narrowed" not in v.reason

    def test_sanitized_spawn_env_strips_auth_vars(self) -> None:
        """#ARCH-279 裁定A2：sanitized_spawn_env 剔除 GATEWAY/FORCE，保留其余变量。"""
        from scripts.ops_guard import sanitized_spawn_env

        base = {
            "ZEPHYR_COMMIT_GATEWAY": "1",
            "ZEPHYR_FORCE_DELETE": "1",
            "PYTHONPATH": "x",
            "PATH": "y",
        }
        env = sanitized_spawn_env(base)
        assert "ZEPHYR_COMMIT_GATEWAY" not in env
        assert "ZEPHYR_FORCE_DELETE" not in env
        assert env["PYTHONPATH"] == "x" and env["PATH"] == "y"
        # base 不被原地修改（返回副本）
        assert base["ZEPHYR_COMMIT_GATEWAY"] == "1"

    def test_sanitized_spawn_env_default_os_environ(self) -> None:
        """缺省取 os.environ 副本——投毒环境下派生环境被洗净。"""
        from scripts.ops_guard import sanitized_spawn_env

        with patch.dict(os.environ, {"ZEPHYR_COMMIT_GATEWAY": "1"}):
            env = sanitized_spawn_env()
        assert "ZEPHYR_COMMIT_GATEWAY" not in env
