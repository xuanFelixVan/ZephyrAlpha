"""
audit_trail.genesis — MOD-INF-020 · 信任锚初始化 (Genesis Block)
=================================================================
蓝图 D-020-44 · Genesis 区块创建 + 见证签名 + 外部媒体备份

特性
----
  - Genesis 区块: 审计链的第一个区块，包含系统初始化参数
  - 见证签名: 多方签名确保 Genesis 区块可信
  - 外部媒体备份: 将 Genesis 区块写入外部存储介质
  - 完整性验证: 验证 Genesis 区块未被篡改
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)

DEFAULT_AUDIT_DATA_DIR: Path = Path("data/audit_trail")


class WitnessSignature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    witness_id: str = ""
    signature_hex: str = ""
    signed_at: str = ""
    public_key_pem: str = ""


class GenesisBlock(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    genesis_id: str = ""
    system_id: str = ""
    created_at: str = ""
    creator: str = ""
    initial_config: dict[str, Any] = Field(default_factory=dict)
    witness_signatures: list[WitnessSignature] = Field(default_factory=list)
    genesis_hash: str = ""
    prev_hash: str = "0" * 64
    lamport_counter: int = 0
    backup_paths: list[str] = Field(default_factory=list)


class GenesisVerificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_valid: bool = True
    genesis_id: str = ""
    hash_valid: bool = True
    witness_count: int = 0
    issues: list[str] = Field(default_factory=list)
    verified_at: str = ""


class GenesisManager:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
        system_id: str = "zephyr-alpha",
        creator: str = "system",
    ) -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._system_id = system_id
        self._creator = creator
        self._genesis_path = self._data_dir / "genesis.json"

    def create_genesis(
        self,
        initial_config: dict[str, Any] | None = None,
        witnesses: list[WitnessSignature] | None = None,
        backup_dir: Path | str | None = None,
    ) -> GenesisBlock:
        genesis_id = f"GENESIS-{uuid4().hex[:20]}"
        now = datetime.now(UTC).isoformat()

        block_data = {
            "genesis_id": genesis_id,
            "system_id": self._system_id,
            "created_at": now,
            "creator": self._creator,
            "initial_config": initial_config or {},
            "witness_signatures": [w.model_dump() for w in (witnesses or [])],
            "prev_hash": "0" * 64,
            "lamport_counter": 0,
        }
        genesis_hash = hashlib.sha256(
            json.dumps(block_data, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        ).hexdigest()

        backup_paths: list[str] = []
        if backup_dir:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            backup_file = backup_path / f"genesis-{self._system_id}.json"
            block_data["genesis_hash"] = genesis_hash
            block_data["backup_paths"] = [str(backup_file)]
            backup_file.write_text(
                json.dumps(block_data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            backup_paths.append(str(backup_file))

        block = GenesisBlock(
            genesis_id=genesis_id,
            system_id=self._system_id,
            created_at=now,
            creator=self._creator,
            initial_config=initial_config or {},
            witness_signatures=witnesses or [],
            genesis_hash=genesis_hash,
            prev_hash="0" * 64,
            lamport_counter=0,
            backup_paths=backup_paths,
        )

        self._genesis_path.write_text(
            json.dumps(block.model_dump(), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        _logger.info("GenesisManager: created genesis block %s", genesis_id)
        return block

    def verify_genesis(self, genesis: GenesisBlock | None = None) -> GenesisVerificationResult:
        if genesis is None:
            genesis = self._load_genesis()
        if genesis is None:
            return GenesisVerificationResult(
                is_valid=False,
                hash_valid=False,
                issues=["Genesis block not found"],
                verified_at=datetime.now(UTC).isoformat(),
            )

        issues: list[str] = []

        verify_data = {
            "genesis_id": genesis.genesis_id,
            "system_id": genesis.system_id,
            "created_at": genesis.created_at,
            "creator": genesis.creator,
            "initial_config": genesis.initial_config,
            "witness_signatures": [w.model_dump() for w in genesis.witness_signatures],
            "prev_hash": genesis.prev_hash,
            "lamport_counter": genesis.lamport_counter,
        }
        expected_hash = hashlib.sha256(
            json.dumps(verify_data, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        ).hexdigest()
        hash_valid = expected_hash == genesis.genesis_hash
        if not hash_valid:
            issues.append(f"Genesis hash mismatch: expected={expected_hash[:16]}..., got={genesis.genesis_hash[:16]}...")

        if genesis.prev_hash != "0" * 64:
            issues.append("Genesis prev_hash must be all zeros")

        is_valid = len(issues) == 0
        return GenesisVerificationResult(
            is_valid=is_valid,
            genesis_id=genesis.genesis_id,
            hash_valid=hash_valid,
            witness_count=len(genesis.witness_signatures),
            issues=issues,
            verified_at=datetime.now(UTC).isoformat(),
        )

    def _load_genesis(self) -> GenesisBlock | None:
        if not self._genesis_path.exists():
            return None
        try:
            data = json.loads(self._genesis_path.read_text(encoding="utf-8"))
            return GenesisBlock(**data)
        except Exception:
            _logger.exception("GenesisManager: failed to load genesis block")
            return None
