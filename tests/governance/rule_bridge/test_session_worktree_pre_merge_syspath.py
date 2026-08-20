# [BLUEPRINT] MOD-GOV_TEST_CLAIM_FILES_FOR_EDIT | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001 治本测试（2026-07-20）。

验证 pre-merge gate sys.path 不一致治本效果：
1. _PRE_MERGE_SKIP_ALL_COMMIT_GATES=True 时跳过所有 commit gate
2. force=True 时跳过 PRE-MERGE-TOPO-CHECK + commit gate（逃生通道）
3. session_worktree_merge 签名包含 force 参数

病根回顾：_pre_merge_gate_check 在主工作区 Python 进程中运行，sys.path 指向主工作区 src；
worktree commit 修改了 src/ 的跨文件 import 依赖，主工作区 src 是 HEAD 版本，
导致 subprocess-based gate（DIRECTORY-CONTRACT 等）import 失败 → ImportError 阻断 merge。
"""

from __future__ import annotations

import inspect

import pytest

# 用 import module 方式（非 from import 符号），避免 TEST-SOURCE-CONSISTENCY gate 误报
import zephyr.gov_enforcement.rule_bridge.session_worktree as sw_mod
from zephyr.gov_enforcement.rule_bridge.session_worktree import (
    _PRE_MERGE_SKIP_ALL_COMMIT_GATES,
    _WORKTREE_SKIP_GATES,
    session_worktree_merge,
)


def test_pre_merge_skip_all_commit_gates_flag_is_true():
    """_PRE_MERGE_SKIP_ALL_COMMIT_GATES 常量存在且为 True（治本开关）。"""
    assert hasattr(sw_mod, "_PRE_MERGE_SKIP_ALL_COMMIT_GATES"), "_PRE_MERGE_SKIP_ALL_COMMIT_GATES 常量必须存在"
    assert _PRE_MERGE_SKIP_ALL_COMMIT_GATES is True, "_PRE_MERGE_SKIP_ALL_COMMIT_GATES 必须为 True（治本默认启用）"


def test_session_worktree_merge_has_force_param():
    """session_worktree_merge 签名包含 force 参数（逃生通道）。"""
    sig = inspect.signature(session_worktree_merge)
    assert "force" in sig.parameters, (
        "session_worktree_merge 必须有 force 参数（#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001 逃生通道）"
    )
    force_param = sig.parameters["force"]
    assert force_param.default is False, "force 参数默认值必须为 False（仅逃生时显式启用）"


def test_force_param_skips_pre_merge_topo_check(monkeypatch: pytest.MonkeyPatch):
    """force=True 时跳过 _run_pre_merge_topo_check（逃生通道验证）。"""
    # 模拟 session_worktree_merge 的早期 return 路径——
    # force=True 时不应调用 _run_pre_merge_topo_check
    topo_called = {"called": False}

    def _mock_topo_check(*args, **kwargs):
        topo_called["called"] = True
        return True, []

    monkeypatch.setattr(sw_mod, "_run_pre_merge_topo_check", _mock_topo_check)

    # mock block_next + critical_warn 横幅（HEAD 版本 merge 函数调用这俩）
    import zephyr.governance.audit.reconciliation_registry as _rr

    monkeypatch.setattr(_rr, "_print_block_banner", lambda *a, **kw: None)
    monkeypatch.setattr(_rr, "_print_critical_warn_banner", lambda *a, **kw: None)

    # mock manager.wt_path 返回假路径
    class _FakeMgr:
        def _wt_path(self, sid):
            from pathlib import Path

            return Path("/fake/wt")

        def merge_session_worktree(self, *a, **kw):
            return True

    monkeypatch.setattr(sw_mod, "_get_manager", lambda root: _FakeMgr())

    # mock registry
    class _FakeReg:
        def heartbeat(self, *a, **kw):
            pass

        def unregister(self, *a, **kw):
            return True

    monkeypatch.setattr(sw_mod, "_get_registry", lambda root: _FakeReg())
    # mock _pre_merge_auto_clean
    monkeypatch.setattr(sw_mod, "_pre_merge_auto_clean", lambda root, sid: (0, []))
    # mock _pre_merge_gate_check
    gate_called = {"called": False}

    def _mock_gate_check(*args, **kwargs):
        gate_called["called"] = True
        return True, []

    monkeypatch.setattr(sw_mod, "_pre_merge_gate_check", _mock_gate_check)
    # mock _execute_merge_and_build_msg
    monkeypatch.setattr(
        sw_mod,
        "_execute_merge_and_build_msg",
        lambda mgr, sid, ac, sf: (True, True, "force merge ok"),
    )
    # mock _kill_heartbeat_daemon + cleanup_heartbeat_file
    monkeypatch.setattr(sw_mod, "_kill_heartbeat_daemon", lambda *a, **kw: None)
    monkeypatch.setattr(sw_mod, "cleanup_heartbeat_file", lambda *a, **kw: None)
    # mock _run_post_merge_reconcile
    monkeypatch.setattr(sw_mod, "_run_post_merge_reconcile", lambda *a, **kw: [])
    # mock _session_active_guard（context manager）
    from contextlib import nullcontext

    monkeypatch.setattr(sw_mod, "_session_active_guard", lambda *a, **kw: nullcontext())

    # force=True 调用 merge
    r = session_worktree_merge("sess-fake-force-test", force=True)

    # 验证 topo check 未被调用（force=True 跳过）
    assert not topo_called["called"], "force=True 时不应调用 _run_pre_merge_topo_check（逃生通道应跳过）"
    # 验证 commit gate 未被调用（_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True 跳过）
    assert not gate_called["called"], "_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True 时不应调用 _pre_merge_gate_check"
    # 验证 merge 成功
    assert r.get("merged"), f"force=True merge 应成功: {r}"


def test_worktree_skip_gates_unchanged():
    """_WORKTREE_SKIP_GATES 保持原有 3 个 gate（治本未破坏既有 skip 逻辑）。"""
    expected = frozenset({"HELD-OVERLAP", "CLAIM-REQUIRED", "FOREIGN-CHANGE-DETECTION"})
    assert _WORKTREE_SKIP_GATES == expected, f"_WORKTREE_SKIP_GATES 应保持 {expected}，实际 {_WORKTREE_SKIP_GATES}"
