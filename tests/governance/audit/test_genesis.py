# [A_test] module_id: SRC-TST-1049 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_genesis
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.gov_audit.genesis import (
    GenesisBlock,
    GenesisManager,
    GenesisVerificationResult,
    WitnessSignature,
)


class TestWitnessSignature:
    def test_create_witness(self):
        ws = WitnessSignature(
            witness_id="w1",
            signature_hex="abcd1234",
            signed_at="2026-01-01T00:00:00Z",
            public_key_pem="-----BEGIN PUBLIC KEY-----",
        )
        assert ws.witness_id == "w1"
        assert ws.signature_hex == "abcd1234"


class TestGenesisBlock:
    def test_frozen_model(self):
        block = GenesisBlock(genesis_id="G1", system_id="sys1")
        with pytest.raises(Exception):
            block.genesis_id = "G2"

    def test_default_prev_hash(self):
        block = GenesisBlock()
        assert block.prev_hash == "0" * 64


class TestGenesisManagerInit:
    def test_creates_data_dir(self, tmp_path):
        data_dir = tmp_path / "audit_test"
        manager = GenesisManager(data_dir=data_dir)
        assert data_dir.exists()

    def test_default_system_id(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g1")
        assert manager._system_id == "zephyr-alpha"


class TestCreateGenesis:
    def test_creates_genesis_block(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g2", system_id="test-sys", creator="tester")
        block = manager.create_genesis(initial_config={"key": "value"})
        assert isinstance(block, GenesisBlock)
        assert block.system_id == "test-sys"
        assert block.creator == "tester"
        assert block.genesis_hash != ""
        assert block.prev_hash == "0" * 64
        assert block.initial_config == {"key": "value"}

    def test_genesis_file_written(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g3")
        block = manager.create_genesis()
        genesis_file = tmp_path / "g3" / "genesis.json"
        assert genesis_file.exists()
        data = json.loads(genesis_file.read_text(encoding="utf-8"))
        assert data["genesis_id"] == block.genesis_id

    def test_with_witnesses(self, tmp_path):
        witness = WitnessSignature(witness_id="w1", signature_hex="ab", signed_at="2026-01-01T00:00:00Z")
        manager = GenesisManager(data_dir=tmp_path / "g4")
        block = manager.create_genesis(witnesses=[witness])
        assert len(block.witness_signatures) == 1
        assert block.witness_signatures[0].witness_id == "w1"

    def test_with_backup(self, tmp_path):
        backup_dir = tmp_path / "backup"
        manager = GenesisManager(data_dir=tmp_path / "g5")
        block = manager.create_genesis(backup_dir=backup_dir)
        assert len(block.backup_paths) == 1
        assert Path(block.backup_paths[0]).exists()

    def test_no_config_no_witnesses(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g6")
        block = manager.create_genesis()
        assert block.initial_config == {}
        assert block.witness_signatures == []


class TestVerifyGenesis:
    def test_verify_valid_genesis(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g7")
        block = manager.create_genesis()
        result = manager.verify_genesis(block)
        assert isinstance(result, GenesisVerificationResult)
        assert result.is_valid is True
        assert result.hash_valid is True

    def test_verify_tampered_genesis(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g8")
        block = manager.create_genesis()
        tampered_data = block.model_dump()
        tampered_data["genesis_hash"] = "tampered_hash"
        tampered_block = GenesisBlock(**tampered_data)
        result = manager.verify_genesis(tampered_block)
        assert result.is_valid is False
        assert result.hash_valid is False

    def test_verify_no_genesis_file(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g9")
        result = manager.verify_genesis()
        assert result.is_valid is False
        assert "Genesis block not found" in result.issues

    def test_verify_invalid_prev_hash(self, tmp_path):
        manager = GenesisManager(data_dir=tmp_path / "g10")
        block = manager.create_genesis()
        tampered_data = block.model_dump()
        tampered_data["prev_hash"] = "not_zeros"
        tampered_block = GenesisBlock(**tampered_data)
        result = manager.verify_genesis(tampered_block)
        assert result.is_valid is False
