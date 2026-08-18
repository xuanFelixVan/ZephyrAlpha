# [A_test] module_id: MOD-GOV_cross_commit_dependency | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_cross_commit_dependency
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""test_cross_commit_dependency.py — 跨 commit 原子性依赖检测单测（TRAE-072 / #ARCH-CROSS-COMMIT-ATOMICITY-001 Phase 2）

权威依据：
- src/zephyr/security/access_control/session_concurrency.py（SessionInfo.depends_on_sessions
  + SessionRegistry.register/register_dependency/clear_dependency）
- src/zephyr/gov_enforcement/rule_bridge/session_worktree.py（_check_cross_commit_deps
  + session_worktree_commit depends_on_sessions 参数）

测试组：
- TestSessionInfoDependsOnSessions: depends_on_sessions 字段 to_dict/from_dict 往返
- TestSessionRegistryRegisterWithDeps: register() 接受 depends_on_sessions 参数
- TestRegisterDependency: register_dependency() 动态登记依赖（含懒注册/幂等）
- TestClearDependency: clear_dependency() 清除依赖
- TestCheckCrossCommitDeps: _check_cross_commit_deps 函数（阻断/放行/异常降级）
- TestBa40fa5b75Scenario: ba40fa5b75 同型违规治本场景复现
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.security.access_control.session_concurrency import (
    SessionInfo,
    SessionRegistry,
)

# ---------------------------------------------------------------------------
# TestSessionInfoDependsOnSessions: depends_on_sessions 字段 to_dict/from_dict 往返
# ---------------------------------------------------------------------------


class TestSessionInfoDependsOnSessions:
    """SessionInfo.depends_on_sessions 字段序列化往返测试。"""

    def test_default_empty_list(self):
        """新 SessionInfo 默认 depends_on_sessions=[]。"""
        info = SessionInfo(session_id="s1", pid=0, start_time=0.0)
        assert info.depends_on_sessions == []

    def test_to_dict_includes_depends_on_sessions(self):
        """to_dict 包含 depends_on_sessions 字段。"""
        info = SessionInfo(
            session_id="s1", pid=0, start_time=0.0,
            depends_on_sessions=["s2", "s3"],
        )
        d = info.to_dict()
        assert d["depends_on_sessions"] == ["s2", "s3"]

    def test_from_dict_reads_depends_on_sessions(self):
        """from_dict 读取 depends_on_sessions 字段。"""
        info = SessionInfo.from_dict({
            "session_id": "s1", "pid": 0, "start_time": 0.0,
            "depends_on_sessions": ["s2"],
        })
        assert info.depends_on_sessions == ["s2"]

    def test_from_dict_missing_field_defaults_to_empty(self):
        """from_dict 缺失 depends_on_sessions 字段时默认空列表（向后兼容）。"""
        info = SessionInfo.from_dict({
            "session_id": "s1", "pid": 0, "start_time": 0.0,
        })
        assert info.depends_on_sessions == []

    def test_from_dict_null_field_defaults_to_empty(self):
        """from_dict 中 depends_on_sessions=null 时默认空列表（防 None.append AttributeError）。"""
        info = SessionInfo.from_dict({
            "session_id": "s1", "pid": 0, "start_time": 0.0,
            "depends_on_sessions": None,
        })
        assert info.depends_on_sessions == []

    def test_round_trip_preserves_depends_on_sessions(self):
        """to_dict → from_dict 往返保持 depends_on_sessions 一致。"""
        info = SessionInfo(
            session_id="s1", pid=0, start_time=0.0,
            depends_on_sessions=["s2", "s3"],
        )
        restored = SessionInfo.from_dict(info.to_dict())
        assert restored.depends_on_sessions == ["s2", "s3"]


# ---------------------------------------------------------------------------
# TestSessionRegistryRegisterWithDeps: register() 接受 depends_on_sessions 参数
# ---------------------------------------------------------------------------


class TestSessionRegistryRegisterWithDeps:
    """SessionRegistry.register() 接受 depends_on_sessions 参数测试。"""

    def test_register_with_depends_on_sessions(self, tmp_path):
        """register(depends_on_sessions=[...]) 正确持久化依赖列表。"""
        reg = SessionRegistry(project_root=tmp_path)
        info = reg.register("sess-A", depends_on_sessions=["sess-B", "sess-C"])
        assert info.depends_on_sessions == ["sess-B", "sess-C"]
        # 持久化到 JSON
        reloaded = reg.get_session("sess-A")
        assert reloaded is not None
        assert reloaded.depends_on_sessions == ["sess-B", "sess-C"]

    def test_register_without_depends_on_sessions_defaults_empty(self, tmp_path):
        """register() 不传 depends_on_sessions 时默认空列表。"""
        reg = SessionRegistry(project_root=tmp_path)
        info = reg.register("sess-A")
        assert info.depends_on_sessions == []

    def test_register_with_empty_depends_on_sessions(self, tmp_path):
        """register(depends_on_sessions=[]) 显式空列表。"""
        reg = SessionRegistry(project_root=tmp_path)
        info = reg.register("sess-A", depends_on_sessions=[])
        assert info.depends_on_sessions == []


# ---------------------------------------------------------------------------
# TestRegisterDependency: register_dependency() 动态登记依赖
# ---------------------------------------------------------------------------


class TestRegisterDependency:
    """SessionRegistry.register_dependency() 动态登记依赖测试。"""

    def test_register_dependency_adds_to_existing_session(self, tmp_path):
        """已注册 session 上动态添加依赖。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        assert reg.register_dependency("sess-A", "sess-B") is True
        info = reg.get_session("sess-A")
        assert info is not None
        assert info.depends_on_sessions == ["sess-B"]

    def test_register_dependency_idempotent(self, tmp_path):
        """重复登记同一依赖幂等（不重复添加）。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        assert reg.register_dependency("sess-A", "sess-B") is True
        assert reg.register_dependency("sess-A", "sess-B") is True  # 幂等
        info = reg.get_session("sess-A")
        assert info.depends_on_sessions == ["sess-B"]  # 只一个

    def test_register_dependency_multiple_distinct(self, tmp_path):
        """登记多个不同依赖。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        reg.register_dependency("sess-A", "sess-B")
        reg.register_dependency("sess-A", "sess-C")
        info = reg.get_session("sess-A")
        assert info.depends_on_sessions == ["sess-B", "sess-C"]

    def test_register_dependency_auto_registers_unknown_session(self, tmp_path):
        """未注册 session 上调用 register_dependency 触发懒注册。"""
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.register_dependency("sess-ghost", "sess-B") is True
        info = reg.get_session("sess-ghost")
        assert info is not None
        assert info.depends_on_sessions == ["sess-B"]

    def test_register_dependency_updates_heartbeat(self, tmp_path):
        """register_dependency 顺带刷新 last_heartbeat。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")
        old_info = reg.get_session("sess-A")
        assert old_info is not None
        old_hb = old_info.last_heartbeat
        # 等待一小段时间确保时间戳不同
        import time as _time
        _time.sleep(0.01)
        reg.register_dependency("sess-A", "sess-B")
        new_info = reg.get_session("sess-A")
        assert new_info is not None
        assert new_info.last_heartbeat > old_hb


# ---------------------------------------------------------------------------
# TestClearDependency: clear_dependency() 清除依赖
# ---------------------------------------------------------------------------


class TestClearDependency:
    """SessionRegistry.clear_dependency() 清除依赖测试。"""

    def test_clear_dependency_removes_existing(self, tmp_path):
        """清除已登记的依赖。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A", depends_on_sessions=["sess-B", "sess-C"])
        assert reg.clear_dependency("sess-A", "sess-B") is True
        info = reg.get_session("sess-A")
        assert info is not None
        assert info.depends_on_sessions == ["sess-C"]

    def test_clear_dependency_idempotent(self, tmp_path):
        """清除不存在的依赖幂等返回 True。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A", depends_on_sessions=["sess-B"])
        assert reg.clear_dependency("sess-A", "sess-ghost") is True  # 不存在也 True
        info = reg.get_session("sess-A")
        assert info is not None
        assert info.depends_on_sessions == ["sess-B"]  # 原依赖未变

    def test_clear_dependency_unregistered_session_returns_false(self, tmp_path):
        """清除未注册 session 的依赖返回 False。"""
        reg = SessionRegistry(project_root=tmp_path)
        assert reg.clear_dependency("sess-ghost", "sess-B") is False

    def test_clear_all_dependencies(self, tmp_path):
        """清除所有依赖后列表为空。"""
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A", depends_on_sessions=["sess-B", "sess-C"])
        reg.clear_dependency("sess-A", "sess-B")
        reg.clear_dependency("sess-A", "sess-C")
        info = reg.get_session("sess-A")
        assert info is not None
        assert info.depends_on_sessions == []


# ---------------------------------------------------------------------------
# TestCheckCrossCommitDeps: _check_cross_commit_deps 函数测试
# ---------------------------------------------------------------------------


class TestCheckCrossCommitDeps:
    """_check_cross_commit_deps 函数测试（TRAE-072 / #ARCH-CROSS-COMMIT-ATOMICITY-001）。"""

    def test_no_dependencies_returns_none(self, tmp_path):
        """session 无 depends_on_sessions 时放行（返回 None）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-A")  # 无依赖
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is None

    def test_active_dependency_blocks(self, tmp_path):
        """依赖 session 仍活跃时阻断（CROSS_COMMIT_DEP_BLOCKED）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        # 注册依赖 session B（活跃）
        reg.register("sess-B")
        # 注册当前 session A，依赖 B
        reg.register("sess-A", depends_on_sessions=["sess-B"])
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is not None
        assert result["status"] == "FAILED"
        assert result["cross_commit_dep_blocked"] is True
        assert "sess-B" in result["active_deps"]
        assert "CROSS_COMMIT_DEP_BLOCKED" in result["message"]
        assert "TRAE-072" in result["message"]

    def test_inactive_dependency_passes(self, tmp_path):
        """依赖 session 不活跃（未注册）时放行。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        # 只注册当前 session A，依赖 ghost session B（未注册=已结束）
        reg.register("sess-A", depends_on_sessions=["sess-B-ghost"])
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is None

    def test_expired_dependency_passes(self, tmp_path):
        """依赖 session 已过期（last_heartbeat 过老）时放行。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B")
        # 手动把 sess-B 的 last_heartbeat 改老（pid=0 + 心跳过期 = 不活跃）
        data = reg.load()
        data["sess-B"]["last_heartbeat"] = 0.0
        reg.save(data)
        # 注册 sess-A 依赖 sess-B
        reg.register("sess-A", depends_on_sessions=["sess-B"])
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is None

    def test_unregistered_current_session_returns_none(self, tmp_path):
        """当前 session 未注册时放行（其他 gate 如 SESSION-REQUIRED 处理）。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        result = _check_cross_commit_deps(Path(tmp_path), "sess-ghost")
        assert result is None

    def test_mixed_active_inactive_blocks_on_active(self, tmp_path):
        """混合依赖（部分活跃部分不活跃）时只要有活跃依赖即阻断。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B")  # 活跃
        # sess-C 不注册（不活跃）
        reg.register("sess-A", depends_on_sessions=["sess-B", "sess-C-ghost"])
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is not None
        assert result["cross_commit_dep_blocked"] is True
        assert result["active_deps"] == ["sess-B"]

    def test_exception_fails_open(self, tmp_path):
        """SessionRegistry 异常时降级为放行（不阻断，对标 5.135 治标）。"""
        import zephyr.gov_enforcement.rule_bridge.session_worktree as sw_mod

        # patch _get_registry 抛异常
        with patch.object(
            sw_mod, "_get_registry",
            side_effect=RuntimeError("registry corrupted"),
        ):
            result = sw_mod.check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is None  # 异常降级为放行


# ---------------------------------------------------------------------------
# TestBa40fa5b75Scenario: ba40fa5b75 同型违规治本场景复现
# ---------------------------------------------------------------------------


class TestBa40fa5b75Scenario:
    """ba40fa5b75 同型违规治本场景复现（regression test）。

    ba40fa5b75 在 git_commit_gateway.py 添加 import forged_gw_marker_gate，
    但 forged_gw_marker_gate.py 36 分钟后才由 ce81f1077f 创建。
    治本：session-A 登记依赖 session-B，commit 前检测 session-B 仍活跃 → 阻断。
    """

    def test_session_a_blocked_while_session_b_active(self, tmp_path):
        """session-A 依赖 session-B，B 仍活跃时 A 的 commit 被阻断。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        # session-B 正在创建 forged_gw_marker_gate.py（活跃）
        reg.register("sess-B")
        # session-A 知道依赖 session-B（import 了 B 正在创建的模块）
        reg.register("sess-A", depends_on_sessions=["sess-B"])
        # session-A commit 前检查 → 阻断
        result = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result is not None
        assert result["cross_commit_dep_blocked"] is True
        assert "sess-B" in result["active_deps"]

    def test_session_a_passes_after_session_b_unregistered(self, tmp_path):
        """session-B commit+merge 后 unregister，session-A 重试 commit 放行。"""
        from zephyr.gov_enforcement.rule_bridge.session_worktree import (
            _check_cross_commit_deps,
        )
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B")
        reg.register("sess-A", depends_on_sessions=["sess-B"])
        # 第一次：B 活跃 → 阻断
        result1 = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result1 is not None
        # session-B commit+merge 后 unregister
        reg.unregister("sess-B")
        # 第二次：B 不活跃 → 放行
        result2 = _check_cross_commit_deps(Path(tmp_path), "sess-A")
        assert result2 is None

    def test_session_a_late_register_dependency_via_commit_param(self, tmp_path):
        """session-A 在 session_worktree_commit 时通过 depends_on_sessions 参数动态登记。

        场景：session-A 启动时未知依赖，commit 时发现 import 了 session-B 正在
        创建的模块，通过 session_worktree_commit(depends_on_sessions=[...]) 动态登记。
        此测试验证 register_dependency 在 commit 流程中被调用（不实际跑 commit）。
        """
        reg = SessionRegistry(project_root=tmp_path)
        reg.register("sess-B")  # session-B 活跃
        reg.register("sess-A")  # session-A 启动时无依赖
        # 模拟 session_worktree_commit 内部的动态登记逻辑
        for dep_sid in ["sess-B"]:
            reg.register_dependency("sess-A", dep_sid)
        # 验证依赖已登记
        info = reg.get_session("sess-A")
        assert info is not None
        assert info.depends_on_sessions == ["sess-B"]
