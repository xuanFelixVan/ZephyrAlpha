# [A_test] module_id=MOD-METAQ-EXAMLOOP-TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-METAQ-EXAMLOOP | docs/_working/chain_piling_campaign/infra_mining/20_management_policy.md | §2.1/§2.2 双轨留痕 + exam_loop/PENDING_ENUM_PATCH.md（扩展事件码过渡载体）
# [MODULE] tests.governance.meta_question.test_exam_loop_ledger
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] conftest 夹具 env/mq; zephyr.governance.meta_question.exam_loop.ledger/event_codes
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 红蓝对称自证：同一调用在"扩展码未落地/已落地"两态取值必须不同且各自闭环（防静默常量尺）；
#              双轨同键=PG 行与 JSONL 行的 what/evidence 完全一致（20§2.2 差集对账不因过渡载体扰动）
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未登记事件码必须 ValueError（不得静默落 update）
# [TESTS] self
# [TTL] task_bound
"""审计落账组合口测试：过渡载体双轨同键 / 落地即切换 / 未在册码拒写。"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from zephyr.governance.meta_question.exam_loop import event_codes
from zephyr.governance.meta_question.exam_loop.ledger import ExamLoopLedger


class TestPendingCarriage:
    def test_extension_code_lands_with_base_what_and_event_code(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """未落地扩展码：what=册内 base_what，event_code 同进 after JSONB 与 evidence 前缀。"""
        ExamLoopLedger(env["registry"]).write_event_standalone(
            event_codes.CODE_CLAIM_MISMATCH,
            q_id="PQ-0001",
            actor=mq.SESSION,
            after={"rejected": True},
            evidence="writeback_auth",
        )
        rows = mq.event_code_hits(mq.audit_rows(env), event_codes.CODE_CLAIM_MISMATCH)
        assert len(rows) == 1
        row = rows[0]
        assert row["what"] == event_codes.base_what_for_pending()
        assert row["after"][event_codes.event_code_key()] == event_codes.CODE_CLAIM_MISMATCH
        assert row["evidence"].startswith(event_codes.evidence_prefix() + event_codes.CODE_CLAIM_MISMATCH)

    def test_dual_track_same_key(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """双轨同键（20§2.2）：JSONL 轨 what/evidence 与 PG 轨逐字一致。"""
        ExamLoopLedger(env["registry"]).write_event_standalone(
            event_codes.CODE_ILLEGAL_TRANSITION, q_id="PQ-0002", actor=mq.SESSION, after={}, evidence="x"
        )
        pg = mq.event_code_hits(mq.audit_rows(env), event_codes.CODE_ILLEGAL_TRANSITION)[0]
        jl = [
            r
            for r in mq.jsonl_rows(env)
            if str(r.get("evidence", "")).startswith(
                event_codes.evidence_prefix() + event_codes.CODE_ILLEGAL_TRANSITION
            )
        ]
        assert jl, "JSONL 轨必须同键留痕"
        assert jl[0]["what"] == pg["what"]
        assert jl[0]["evidence"] == pg["evidence"]
        assert jl[0]["object"] == "PQ-0002"
        assert {"who", "when", "what", "object", "diff", "evidence"} == set(jl[0])

    def test_unregistered_code_refused(self, env: dict[str, Any], mq: SimpleNamespace) -> None:
        """未在册事件码=拒写（禁另立枚举）。"""
        ledger = ExamLoopLedger(env["registry"])
        with pytest.raises(ValueError):
            ledger.write_event_standalone("totally_new_event", q_id="PQ-0003", actor=mq.SESSION)
        assert all(r["what"] != "totally_new_event" for r in mq.audit_rows(env))


class TestLandedSwitch:
    """总包落地补丁后的行为（同一调用点零改动，what 直写真实事件码）。"""

    def test_passthrough_after_landing(
        self, env: dict[str, Any], mq: SimpleNamespace, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        code = event_codes.CODE_CLAIM_MISMATCH
        # _write_audit 的词表校验读的是 exam_ops 模块全局（补丁落点=真源模块，非 re-export 面）
        monkeypatch.setattr(
            "zephyr.governance.meta_question.exam_ops.AUDIT_WHAT_VOCAB",
            frozenset(event_codes.AUDIT_WHAT_VOCAB) | {code},
        )
        event_codes.mark_landed(code, True)
        ExamLoopLedger(env["registry"]).write_event_standalone(
            code, q_id="PQ-0004", actor=mq.SESSION, after={"rejected": True}, evidence="auth"
        )
        rows = [r for r in mq.audit_rows(env) if r["what"] == code]
        assert len(rows) == 1
        assert event_codes.event_code_key() not in rows[0]["after"]  # 落地后不再走过渡载体

    def test_same_call_site_differs_between_regimes(self, mq: SimpleNamespace) -> None:
        """两态取值不同 ⇒ "落地即切换"逻辑真在跑（否则本断言恒绿=静默成功尺）。"""
        code = event_codes.CODE_THRESHOLD_LOWERED
        assert event_codes.resolve(code).what == event_codes.base_what_for_pending()
        assert event_codes.resolve(code).landed is False
        event_codes.mark_landed(code, True)
        assert event_codes.resolve(code).landed is True
        assert event_codes.resolve(code).event_code is None

    def test_overlap_with_landed_vocab_fails_closed(self, mq: SimpleNamespace) -> None:
        """扩展册码若已被并入总册却仍留本册=双登记，装配期必须炸（20§2.1 唯一 SSOT）。"""
        assert not (frozenset(event_codes.EXTENSION_CODES) & frozenset(event_codes.AUDIT_WHAT_VOCAB))
        with pytest.raises(ValueError):
            event_codes.resolve(event_codes.CODE_SUPPLEMENT + "_not_in_book")
