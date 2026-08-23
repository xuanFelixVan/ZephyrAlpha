# [BLUEPRINT] MOD-INF-049 | docs/03_modules/MOD-INF-049/
# [MODULE] tests.intelligence.test_venra_double_lock_anchor
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/intelligence/test_venra_double_lock_anchor.py -q
# [TTL] permanent

"""VENRA 双锁锚定器（MOD-INF-049）单元测试——双锁确认/拒绝留痕/哈希链完整性。"""

from __future__ import annotations

import pytest

from zephyr.intelligence.venra_double_lock_anchor import (
    AnchorRecord,
    VenraDoubleLockAnchor,
    VenraDoubleLockError,
)


def _new_anchor() -> VenraDoubleLockAnchor:
    return VenraDoubleLockAnchor()


class TestPropose:
    def test_propose_returns_change(self):
        a = _new_anchor()
        ch = a.propose("CHG-1", target="risk_params", payload={"k": 1}, proposer="agent-a")
        assert ch.change_id == "CHG-1"
        assert ch.target == "risk_params"
        assert len(ch.payload_hash) == 64  # sha256 hex

    def test_propose_rejects_empty_fields(self):
        a = _new_anchor()
        with pytest.raises(VenraDoubleLockError):
            a.propose("", target="t", payload={}, proposer="agent-a")
        with pytest.raises(VenraDoubleLockError):
            a.propose("CHG-1", target="", payload={}, proposer="agent-a")
        with pytest.raises(VenraDoubleLockError):
            a.propose("CHG-1", target="t", payload={}, proposer="")

    def test_propose_duplicate_change_id_rejected(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        with pytest.raises(VenraDoubleLockError):
            a.propose("CHG-1", target="t", payload={}, proposer="agent-b")


class TestDoubleLock:
    def test_first_lock_pending_second_confirms(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        assert a.lock("CHG-1", actor="locker-1") == "pending"
        assert a.lock("CHG-1", actor="locker-2") == "confirmed"
        assert a.is_confirmed("CHG-1") is True

    def test_same_actor_twice_rejected(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        a.lock("CHG-1", actor="locker-1")
        with pytest.raises(VenraDoubleLockError):
            a.lock("CHG-1", actor="locker-1")

    def test_unknown_change_rejected(self):
        a = _new_anchor()
        with pytest.raises(VenraDoubleLockError):
            a.lock("NOPE", actor="locker-1")
        assert a.is_confirmed("NOPE") is False

    def test_reject_path(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        assert a.lock("CHG-1", actor="locker-1", approve=False) == "rejected"
        assert a.is_confirmed("CHG-1") is False

    def test_lock_after_terminal_rejected(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        a.lock("CHG-1", actor="locker-1", approve=False)
        with pytest.raises(VenraDoubleLockError):
            a.lock("CHG-1", actor="locker-2")

    def test_confirmed_appends_anchor_record(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        a.lock("CHG-1", actor="locker-1")
        a.lock("CHG-1", actor="locker-2")
        chain = a.anchor_chain()
        assert len(chain) == 1
        rec = chain[0]
        assert isinstance(rec, AnchorRecord)
        assert rec.decision == "confirmed"
        assert rec.lockers == ("locker-1", "locker-2")
        assert rec.prev_hash == "0" * 64

    def test_reject_also_appends_anchor_record(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        a.lock("CHG-1", actor="locker-1", approve=False)
        chain = a.anchor_chain()
        assert len(chain) == 1
        assert chain[0].decision == "rejected"


class TestAnchorChain:
    def test_chain_links_and_verifies(self):
        a = _new_anchor()
        for i in range(3):
            cid = f"CHG-{i}"
            a.propose(cid, target="t", payload={"i": i}, proposer="agent-a")
            a.lock(cid, actor="locker-1")
            a.lock(cid, actor="locker-2")
        chain = a.anchor_chain()
        assert [r.seq for r in chain] == [1, 2, 3]
        assert chain[1].prev_hash == chain[0].record_hash
        assert chain[2].prev_hash == chain[1].record_hash
        assert a.verify_chain() is True

    def test_verify_chain_detects_tamper(self):
        a = _new_anchor()
        a.propose("CHG-1", target="t", payload={}, proposer="agent-a")
        a.lock("CHG-1", actor="locker-1")
        a.lock("CHG-1", actor="locker-2")
        rec = a.anchor_chain()[0]
        tampered = AnchorRecord(
            seq=rec.seq,
            change_id=rec.change_id,
            target="evil-target",
            lockers=rec.lockers,
            decision=rec.decision,
            prev_hash=rec.prev_hash,
            record_hash=rec.record_hash,
        )
        a._records[0] = tampered
        assert a.verify_chain() is False

    def test_empty_chain_verifies_true(self):
        assert _new_anchor().verify_chain() is True
