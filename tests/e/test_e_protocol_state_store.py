# [A_test] module_id: MOD-GOV_e_protocol_state_store | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_protocol_state_store
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
import os

from zephyr.governance.persistence.protocol_state_store import ProtocolStateStore


class TestProtocolStateStore:
    def test_init_creates_dir(self, tmp_path):
        state_dir = str(tmp_path / "state")
        store = ProtocolStateStore(state_dir=state_dir)
        assert os.path.isdir(state_dir)

    def test_update_stores_value(self, tmp_path):
        store = ProtocolStateStore(state_dir=str(tmp_path / "state"))
        store.update("key1", "value1")
        assert store._state["key1"] == "value1"

    def test_save_writes_json(self, tmp_path):
        state_dir = str(tmp_path / "state")
        store = ProtocolStateStore(state_dir=state_dir)
        store.update("key1", "value1")
        path = store.save()
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert data["state"]["key1"] == "value1"
        assert "timestamp" in data

    def test_update_overwrites(self, tmp_path):
        store = ProtocolStateStore(state_dir=str(tmp_path / "state"))
        store.update("key1", "old")
        store.update("key1", "new")
        assert store._state["key1"] == "new"
