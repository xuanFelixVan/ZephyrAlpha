# [A_test] module_id: MOD-GOV_session_worktree_trusted_git_env | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ENFORCEMENT | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §fast-path-isolation
# [MODULE] tests.governance.rule_bridge.test_session_worktree_trusted_git_env
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_ENFORCEMENT | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_session_worktree_trusted_git_env.py — _trusted_git_env 进程级隔离单测（L2.2 验收）

#ARCH-GIT-SELF-HARM-GUARD L2.2（2026-08-04）。

测试 _trusted_git_env() 的进程级隔离不变量:
1. 调用前主进程 os.environ 不含 ZEPHYR_GIT_GUARD_FAST_PATH
2. 调用后主进程 os.environ 仍不含该标记（返回的是副本，不污染主进程）
3. 返回的 dict 含 ZEPHYR_GIT_GUARD_FAST_PATH=1
4. 多次调用幂等，主进程始终干净
5. 返回 dict 与 os.environ 是不同对象（浅拷贝）
6. 上游若污染 os.environ（契约违例），assert 触发 AssertionError

测试隔离: 纯函数测试，无 git 仓库依赖；env 清理用 monkeypatch 确保不残留。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.gov_enforcement.rule_bridge.session_worktree import (  # noqa: E402
    _FAST_PATH_ENV,
    _trusted_git_env,
)


# ============================================================================
# _trusted_git_env 进程级隔离不变量
# ============================================================================
class TestTrustedGitEnvIsolation:
    """L2.2: fast-path env 进程级隔离守护。"""

    def test_main_process_clean_before_call(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """调用前主进程 os.environ 不含 fast-path 标记（前置条件）。"""
        monkeypatch.delenv(_FAST_PATH_ENV, raising=False)
        assert _FAST_PATH_ENV not in os.environ, "前置: 主进程不应含 fast-path 标记"

    def test_main_process_clean_after_call(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """调用后主进程 os.environ 仍不含 fast-path 标记（核心不变量）。"""
        monkeypatch.delenv(_FAST_PATH_ENV, raising=False)
        env = _trusted_git_env()
        # 返回的 env 含标记
        assert env.get(_FAST_PATH_ENV) == "1", "返回 dict 应含 fast-path=1"
        # 但主进程 os.environ 仍干净
        assert _FAST_PATH_ENV not in os.environ, (
            "主进程 os.environ 不应被污染——fast-path 必须进程级隔离"
        )

    def test_returned_env_has_fast_path_flag(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """返回的 dict 含 ZEPHYR_GIT_GUARD_FAST_PATH=1。"""
        monkeypatch.delenv(_FAST_PATH_ENV, raising=False)
        env = _trusted_git_env()
        assert env[_FAST_PATH_ENV] == "1"

    def test_idempotent_multiple_calls(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """多次调用幂等，主进程始终干净。"""
        monkeypatch.delenv(_FAST_PATH_ENV, raising=False)
        for i in range(5):
            env = _trusted_git_env()
            assert env[_FAST_PATH_ENV] == "1", f"第 {i + 1} 次调用返回 dict 应含标记"
            assert _FAST_PATH_ENV not in os.environ, (
                f"第 {i + 1} 次调用后主进程不应被污染"
            )

    def test_returned_dict_is_copy_not_reference(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """返回的 dict 是 os.environ 的浅拷贝，非同一对象。"""
        monkeypatch.delenv(_FAST_PATH_ENV, raising=False)
        env = _trusted_git_env()
        assert env is not os.environ, "返回 dict 应是副本，非 os.environ 本身"
        # 修改返回的 dict 不影响 os.environ
        env["ZEPHYR_TEST_ONLY_KEY"] = "should_not_leak"
        assert "ZEPHYR_TEST_ONLY_KEY" not in os.environ, "修改返回 dict 不应泄漏到 os.environ"

    def test_inherits_existing_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """返回的 dict 继承 os.environ 现有键（PATH 等子进程必需）。"""
        monkeypatch.setenv("ZEPHYR_TEST_INHERIT", "parent_value")
        try:
            env = _trusted_git_env()
            assert env.get("ZEPHYR_TEST_INHERIT") == "parent_value", "应继承父进程 env"
            assert env[_FAST_PATH_ENV] == "1", "同时附加 fast-path 标记"
        finally:
            monkeypatch.delenv("ZEPHYR_TEST_INHERIT", raising=False)

    def test_warn_fires_when_main_process_polluted(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """上游污染 os.environ（契约违例）时，_trusted_git_env 记 [CRITICAL] warn 并仍返回安全副本。

        #64 裁定（2026-08-20）：assert 从未实现（双形态 git log -S 实证），
        采用 warn-only 检测（fail-visible 不 fail-closed），不再 xfail。
        """
        monkeypatch.setenv(_FAST_PATH_ENV, "1")
        with caplog.at_level("WARNING"):
            env = _trusted_git_env()
        assert any(
            "主进程 os.environ 已含" in r.message and _FAST_PATH_ENV in r.message
            for r in caplog.records
        ), "污染场景应记 [CRITICAL] warn"
        assert env[_FAST_PATH_ENV] == "1", "仍返回含标记的副本（不阻断）"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
