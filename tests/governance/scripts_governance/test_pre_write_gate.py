# [BLUEPRINT] MOD-GOV-pre_write_gate | tests/governance/scripts_governance/test_pre_write_gate.py | §claim-fwd-overlap
# [MODULE] tests.governance.scripts_governance.test_pre_write_gate
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.pre_write_gate
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 测试隔离——mock SessionRegistry 源类，不触碰真实 .runtime/session_registry.json
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""test_pre_write_gate.py — _check_session_overlap 单元测试（claim 前移协议防线）

覆盖方案A（2026-06-30 第29轮调研）的核心检测函数 _check_session_overlap：
1. 无 --session → 跳过 overlap 检测（向后兼容，对标旧调用方/无 session 场景）
2. 被其他活跃 session 持有 → BLOCK (HELD_BY_OTHER)，消息含持有者 session_id
3. 被自己持有（session_id 匹配）→ PASS
4. 无人持有（find_session_by_file 返回 None）→ PASS
5. registry 构造/读取异常 → fail-open PASS (OVERLAP_WARN)，对标 held_overlap_gate

测试隔离：patch zephyr.security.access_control.session_concurrency.SessionRegistry 源类，
不读写真实 .runtime/session_registry.json，避免污染并发 session 状态。
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 导入 pre_write_gate（迁移后位于 scripts/governance/d5_architecture/pre_write_gate.py）
_REPO_ROOT = Path(__file__).resolve().parents[3]  # tests/governance/scripts_governance/ -> repo root
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
sys.path.insert(0, str(_SCRIPTS_DIR / "governance"))  # 供 _shared.constants（_shared 在 scripts/governance/_shared/，迁移后 pre_write_gate.py 在 d5_architecture/ 子目录）
sys.path.insert(0, str(_SCRIPTS_DIR / "governance" / "d5_architecture"))  # 供 import pre_write_gate

import pre_write_gate as pwg  # noqa: E402

# _check_session_overlap 内部 `from zephyr...session_concurrency import SessionRegistry` 是函数内 import，
# patch 源类即可拦截（import 时从源模块取属性）。
_SESSION_REG = "zephyr.security.access_control.session_concurrency.SessionRegistry"


class TestCheckSessionOverlap:
    """_check_session_overlap：claim 前移协议的 Edit 前 overlap 检测。"""

    def test_no_session_skips(self):
        """无 --session 时跳过 overlap 检测（向后兼容，对标旧调用方）。"""
        ok, msg = pwg._check_session_overlap("/tmp/foo.py", "")
        assert ok is True
        assert "skip" in msg

    def test_held_by_other_blocks(self):
        """目标文件被其他活跃 session 持有 → BLOCK，消息含持有者 session_id。"""
        holder = MagicMock()
        holder.session_id = "session-other-1"
        reg_mock = MagicMock()
        reg_mock.find_session_by_file.return_value = holder
        with patch(_SESSION_REG, return_value=reg_mock):
            ok, msg = pwg._check_session_overlap(
                str(_REPO_ROOT / "scripts" / "git_commit.py"), "session-me-1"
            )
        assert ok is False
        assert "HELD_BY_OTHER" in msg
        assert "session-other-1" in msg

    def test_held_by_self_passes(self):
        """目标文件被自己持有（session_id 匹配）→ PASS。"""
        holder = MagicMock()
        holder.session_id = "session-me-1"
        reg_mock = MagicMock()
        reg_mock.find_session_by_file.return_value = holder
        with patch(_SESSION_REG, return_value=reg_mock):
            ok, msg = pwg._check_session_overlap("/tmp/foo.py", "session-me-1")
        assert ok is True
        assert msg == "OK"

    def test_not_held_passes(self):
        """目标文件无人持有（find_session_by_file 返回 None）→ PASS。"""
        reg_mock = MagicMock()
        reg_mock.find_session_by_file.return_value = None
        with patch(_SESSION_REG, return_value=reg_mock):
            ok, msg = pwg._check_session_overlap("/tmp/foo.py", "session-me-1")
        assert ok is True
        assert msg == "OK"

    def test_registry_error_fail_open(self):
        """SessionRegistry 构造/读取异常 → fail-open PASS（对标 held_overlap_gate）。"""
        with patch(_SESSION_REG, side_effect=Exception("registry boom")):
            ok, msg = pwg._check_session_overlap("/tmp/foo.py", "session-me-1")
        assert ok is True
        assert "OVERLAP_WARN" in msg
        assert "registry boom" in msg
