# [A_test] module_id: SRC-TST-0656 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_crypto_bootstrap
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.crypto_bootstrap
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_crypto_bootstrap.py
# [TTL] task_bound

from __future__ import annotations

import hashlib
import json

from zephyr.feedback_loop.forensic.crypto_bootstrap import CryptoBootstrap, HashLink


class TestHashLink:
    def test_creation(self):
        link = HashLink(index=0, timestamp=1.0, action_hash="abc", prev_hash="0" * 64, state_hash="def")
        assert link.index == 0
        assert link.action_hash == "abc"
        assert link.prev_hash == "0" * 64

    def test_default_timestamp(self):
        link = HashLink(index=1, timestamp=0.0, action_hash="a", prev_hash="b", state_hash="c")
        assert isinstance(link.timestamp, float)


class TestCryptoBootstrap:
    def test_instantiation_defaults(self):
        cb = CryptoBootstrap()
        assert cb.genesis_hash == ""
        assert cb.chain == []

    def test_genesis_creates_first_link(self):
        cb = CryptoBootstrap()
        state = {"version": "0.1.0"}
        ghash = cb.genesis(state)
        assert len(cb.chain) == 1
        assert cb.chain[0].action_hash == "GENESIS"
        assert cb.chain[0].prev_hash == "0" * 64
        assert ghash == cb.genesis_hash

    def test_genesis_hash_deterministic(self):
        cb1 = CryptoBootstrap()
        cb2 = CryptoBootstrap()
        state = {"key": "value"}
        h1 = cb1.genesis(state)
        h2 = cb2.genesis(state)
        assert h1 == h2

    def test_genesis_hash_differs_for_different_state(self):
        cb1 = CryptoBootstrap()
        cb2 = CryptoBootstrap()
        h1 = cb1.genesis({"a": 1})
        h2 = cb2.genesis({"b": 2})
        assert h1 != h2

    def test_append_creates_link(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        link = cb.append("action-1", {"step": 1})
        assert len(cb.chain) == 2
        assert link.index == 1
        assert isinstance(link, HashLink)

    def test_append_links_to_previous(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        link1 = cb.append("action-1", {"step": 1})
        link2 = cb.append("action-2", {"step": 2})
        assert link1.prev_hash == cb.chain[0].state_hash
        assert link2.prev_hash == link1.state_hash

    def test_verify_chain_valid(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        cb.append("action-1", {"step": 1})
        cb.append("action-2", {"step": 2})
        assert cb.verify_chain() is True

    def test_verify_chain_tampered(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        cb.append("action-1", {"step": 1})
        cb.append("action-2", {"step": 2})
        cb.chain[2].prev_hash = "tampered_hash"
        assert cb.verify_chain() is False

    def test_verify_chain_single_link(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        assert cb.verify_chain() is True

    def test_append_action_hash_deterministic(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        link = cb.append("same-action", {"same": "state"})
        expected_hash = hashlib.sha256(b"same-action").hexdigest()
        assert link.action_hash == expected_hash

    def test_append_state_hash_deterministic(self):
        cb = CryptoBootstrap()
        cb.genesis({"init": True})
        state = {"key": "val"}
        link = cb.append("act", state)
        expected = hashlib.sha256(json.dumps(state, sort_keys=True).encode()).hexdigest()
        assert link.state_hash == expected

    def test_empty_chain_verify(self):
        cb = CryptoBootstrap()
        assert cb.verify_chain() is True
