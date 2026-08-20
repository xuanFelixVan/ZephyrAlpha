# [A_test] module_id: SRC-TST-2712 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ASSET_INDEX_RECONCILER | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001
# [MODULE] tests.governance.audit.test_downgrade_auto_committed_on_flush_failure
# [DOMAIN] D_GOV_AUDIT
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-GOV_ASSET_INDEX_RECONCILER | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_downgrade_auto_committed_on_flush_failure.py — flush 失败降级单测。

治本 #ARCH-ASSET-INDEX-FALSE-AUTO-COMMIT-001（2026-07-30）：

病根：BatchedAutoCommitter.buffer() 返回合成 CommitResult(status=OK,
commit_hash="BUFFERED")，reconciler 据此返回 action="auto_committed"。
但实际 git commit 在 flush() 中执行，可能因 NOTHING_TO_COMMIT /
COMMIT_FAILED 失败。此时 auto_committed 是误报，需降级为 warn。

测试组：
- TestNoDowngrade: flush 成功/None 时不降级
- TestDowngrade: flush 失败时降级 auto_committed → warn
- TestSelectiveDowngrade: 仅降级 auto_committed，其他 action 不变
- TestEdgeCases: 空列表/长消息截断/缺属性
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
_SRC_DIR = str(_PROJECT_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    ReconcileResult,
    _downgrade_auto_committed_on_flush_failure,
)

# CommitStatus 是 str Enum（_OK == "OK" 为 True），直接用字符串字面量
# 避免导入 git_commit_gateway（重量级模块，import 副作用会干扰其他测试的隔离）。
# 降级函数用 flush_status == "OK" 判断，字符串与 enum 等价。
_OK = "OK"
_NOTHING_TO_COMMIT = "NOTHING_TO_COMMIT"
_COMMIT_FAILED = "COMMIT_FAILED"


@dataclass
class _FakeFlushResult:
    """模拟 batcher.flush() 返回值（CommitResult 子集）。"""

    status: object
    message: str = ""


# ============================================================================
# TestNoDowngrade: flush 成功/None 时不降级
# ============================================================================


class TestNoDowngrade:
    """flush 成功或 None 时，auto_committed 结果保持不变。"""

    def test_no_change_when_flush_none(self):
        # flush_result=None（batcher 不可用/未调用 flush）→ 不降级
        results = [
            ReconcileResult(action="auto_committed", detail="regenerated", gate_id="G1"),
        ]
        _downgrade_auto_committed_on_flush_failure(results, None)
        assert results[0].action == "auto_committed"
        assert results[0].detail == "regenerated"

    def test_no_change_when_flush_ok(self):
        # flush 成功（status=OK）→ auto_committed 准确，不降级
        results = [
            ReconcileResult(action="auto_committed", detail="regenerated", gate_id="G1"),
            ReconcileResult(action="clean", detail="no drift", gate_id="G2"),
        ]
        flush = _FakeFlushResult(status=_OK, message="abc123")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "auto_committed"
        assert results[0].detail == "regenerated"
        assert results[1].action == "clean"

    def test_no_change_when_flush_ok_string(self):
        # status 是字符串 "OK"（非 enum）也应识别为成功
        results = [
            ReconcileResult(action="auto_committed", detail="regenerated", gate_id="G1"),
        ]
        flush = _FakeFlushResult(status="OK", message="abc123")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "auto_committed"


# ============================================================================
# TestDowngrade: flush 失败时降级 auto_committed → warn
# ============================================================================


class TestDowngrade:
    """flush 失败时，auto_committed 降级为 warn 并记录原因。"""

    def test_downgrade_when_flush_nothing_to_commit(self):
        # 典型病根场景：workspace_hygiene restore 了 buffered 文件 → flush NOTHING_TO_COMMIT
        results = [
            ReconcileResult(
                action="auto_committed",
                detail="unified-asset-index drift detected and auto-regenerated (batched, pending flush)",
                gate_id="GATE-ASSET-INDEX",
            ),
        ]
        flush = _FakeFlushResult(
            status=_NOTHING_TO_COMMIT,
            message="nothing to commit, working tree clean",
        )
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "warn"
        assert "flush() did not commit" in results[0].detail
        assert "NOTHING_TO_COMMIT" in results[0].detail
        # 原始 detail 保留在末尾
        assert "auto-regenerated" in results[0].detail

    def test_downgrade_when_flush_commit_failed(self):
        # flush COMMIT_FAILED（如 git commit 出错）→ 降级
        results = [
            ReconcileResult(action="auto_committed", detail="regenerated", gate_id="G1"),
        ]
        flush = _FakeFlushResult(
            status=_COMMIT_FAILED,
            message="git commit failed: exit code 1",
        )
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "warn"
        assert "COMMIT_FAILED" in results[0].detail
        assert "git commit failed" in results[0].detail

    def test_downgrade_preserves_gate_id(self):
        # 降级后 gate_id 保持不变（用于 _log_reconcile_results 追踪）
        results = [
            ReconcileResult(action="auto_committed", detail="x", gate_id="GATE-ASSET-INDEX"),
        ]
        flush = _FakeFlushResult(status=_NOTHING_TO_COMMIT, message="m")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].gate_id == "GATE-ASSET-INDEX"


# ============================================================================
# TestSelectiveDowngrade: 仅降级 auto_committed，其他 action 不变
# ============================================================================


class TestSelectiveDowngrade:
    """仅 action=='auto_committed' 的结果被降级，其他 action 不受影响。"""

    def test_only_auto_committed_downgraded(self):
        # 混合多种 action：只有 auto_committed 被降级
        results = [
            ReconcileResult(action="skip", detail="not relevant", gate_id="G1"),
            ReconcileResult(action="clean", detail="no drift", gate_id="G2"),
            ReconcileResult(action="auto_committed", detail="regenerated-1", gate_id="G3"),
            ReconcileResult(action="warn", detail="existing warn", gate_id="G4"),
            ReconcileResult(action="auto_committed", detail="regenerated-2", gate_id="G5"),
            ReconcileResult(action="critical_warn", detail="severe", gate_id="G6"),
        ]
        flush = _FakeFlushResult(status=_NOTHING_TO_COMMIT, message="m")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        # 非 auto_committed 不变
        assert results[0].action == "skip"
        assert results[0].detail == "not relevant"
        assert results[1].action == "clean"
        assert results[1].detail == "no drift"
        assert results[3].action == "warn"
        assert results[3].detail == "existing warn"
        assert results[5].action == "critical_warn"
        assert results[5].detail == "severe"
        # auto_committed 被降级
        assert results[2].action == "warn"
        assert "regenerated-1" in results[2].detail
        assert results[4].action == "warn"
        assert "regenerated-2" in results[4].detail

    def test_no_auto_committed_no_change(self):
        # 无 auto_committed 结果 → flush 失败也不影响其他
        results = [
            ReconcileResult(action="skip", detail="x", gate_id="G1"),
            ReconcileResult(action="clean", detail="y", gate_id="G2"),
        ]
        flush = _FakeFlushResult(status=_COMMIT_FAILED, message="fail")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "skip"
        assert results[0].detail == "x"
        assert results[1].action == "clean"
        assert results[1].detail == "y"


# ============================================================================
# TestEdgeCases: 边界场景
# ============================================================================


class TestEdgeCases:
    """边界场景：空列表/长消息截断/缺属性。"""

    def test_empty_results_list(self):
        # 空列表 → 无副作用，不抛异常
        results: list[ReconcileResult] = []
        flush = _FakeFlushResult(status=_COMMIT_FAILED, message="m")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results == []

    def test_long_message_truncated(self):
        # flush message 超 200 字符 → 截断到 200（避免 detail 过长污染日志）
        results = [
            ReconcileResult(action="auto_committed", detail="x", gate_id="G1"),
        ]
        long_msg = "E" * 500
        flush = _FakeFlushResult(status=_COMMIT_FAILED, message=long_msg)
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "warn"
        # message 被截断到 200 字符
        assert "E" * 200 in results[0].detail
        assert "E" * 201 not in results[0].detail

    def test_flush_result_missing_status_attr(self):
        # flush_result 无 status 属性（异常对象）→ getattr 返回 None → 不等于 "OK" → 降级
        results = [
            ReconcileResult(action="auto_committed", detail="x", gate_id="G1"),
        ]
        # MagicMock 默认属性返回 MagicMock，str() 不等于 "OK"
        flush = MagicMock()
        flush.status = None  # 显式 None
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "warn"

    def test_empty_detail_preserved(self):
        # 原 detail 为空字符串 → 降级后 detail 仍包含 original: （空）
        results = [
            ReconcileResult(action="auto_committed", detail="", gate_id="G1"),
        ]
        flush = _FakeFlushResult(status=_NOTHING_TO_COMMIT, message="m")
        _downgrade_auto_committed_on_flush_failure(results, flush)
        assert results[0].action == "warn"
        assert "original: " in results[0].detail
