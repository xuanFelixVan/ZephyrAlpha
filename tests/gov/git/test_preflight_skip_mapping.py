# [MODULE] tests.git.test_preflight_skip_mapping
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.git_commit
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/git/test_preflight_skip_mapping.py
# [MATURITY] testing
# [INVARIANTS] 纯函数测试（无 git 仓/无 I/O）；验证逃生旗→预检跳过 gate 映射与 argparse 旗标一一对应（commit_preflight MODIFY-GUARD）
# [MODIFY-GUARD] 新增逃生旗映射须同步补断言
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] self
# [TTL] permanent
"""test_preflight_skip_mapping.py — _preflight_skip_set 逃生旗映射一致性验收。

2026-09-18 实弹（st-flashspeed）：--allow-overlap 已传入但预检仍 SESSION-REQUIRED
假阳性快败——gate 锁内认 allow_overlap 逃生（session_required_gate.py L70），
预检映射漏配。修复=allow_overlap → skip SESSION-REQUIRED。锁内权威判定不变。

2026-10-04 同族修（st-tdm-infrafix2）：CLAIM-REQUIRED gate 锁内同认 allow_overlap
逃生（claim_required_gate.py L59-61），预检漏映射致带旗假阳性快败（本日三次实战）。
修复=allow_overlap → skip CLAIM-REQUIRED。
"""

from __future__ import annotations

from types import SimpleNamespace

from scripts.git_commit import _preflight_skip_set


def test_allow_overlap_skips_session_and_claim_required():
    args = SimpleNamespace(allow_overlap=True)
    skip = _preflight_skip_set(args)
    assert "SESSION-REQUIRED" in skip
    assert "CLAIM-REQUIRED" in skip


def test_no_flags_skips_nothing():
    args = SimpleNamespace()
    assert _preflight_skip_set(args) == frozenset()


def test_existing_mappings_unchanged():
    args = SimpleNamespace(
        allow_non_worktree=True,
        allow_multi_domain=True,
        allow_promote=True,
    )
    skip = _preflight_skip_set(args)
    assert {"WORKTREE-REQUIRED", "COMMIT-SCOPE", "FILE-PLACEMENT-TTL"} <= skip
    assert "SESSION-REQUIRED" not in skip


def test_all_flags_full_mapping():
    args = SimpleNamespace(
        allow_non_worktree=True,
        allow_multi_domain=True,
        allow_promote=True,
        allow_overlap=True,
    )
    skip = _preflight_skip_set(args)
    assert {
        "WORKTREE-REQUIRED",
        "COMMIT-SCOPE",
        "FILE-PLACEMENT-TTL",
        "SESSION-REQUIRED",
        "CLAIM-REQUIRED",
    } == set(skip)
