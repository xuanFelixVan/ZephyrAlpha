# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §3.1
# [MODULE] zephyr.gov_audit.genesis
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] audit-orchestrator.integrity; cold_start
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 创世块不可变; 建立后永不修改
# [MODIFY-GUARD] 创世块格式变更需Owner审批
# [STABILITY] frozen
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 创世块损坏返回恢复失败
# [TESTS] tests/audit-orchestrator/test_genesis.py
# [A_module] module_id=MOD-INF-020 | layer=module | stability=frozen | safety=H | ai_autonomy=human_gated
# [TTL] permanent
"""
audit-trail.genesis — MOD-INF-020 · 创世块管理

提供创世块 (GenesisBlock) 的创建、持久化、验证能力，以及见证签名
(WitnessSignature) 与验证结果 (GenesisVerificationResult) 数据模型。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: data_dir 参数
#   fields: 参数 data_dir（无注解）
#   code: genesis.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: system_id 参数
#   fields: 参数 system_id（无注解）
#   code: genesis.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: creator 参数
#   fields: 参数 creator（无注解）
#   code: genesis.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① GenesisManager
#   name_en: GenesisManager
#   intro: 创世块管理器——负责创建、持久化与验证创世块。
#   desc: 创世块管理器——负责创建、持久化与验证创世块。；公共方法（定义序）: system_id, data_dir, genesis_path, create_genesis, verify_genesis…
#   inputs: data_dir system_id creator
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: GenesisManager
#   downstream: audit-orchestrator.integrity; cold_start
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

__all__ = [
    "GenesisBlock",
    "GenesisManager",
    "GenesisVerificationResult",
    "WitnessSignature",
]

GENESIS_FILE: str = "genesis.json"
DEFAULT_SYSTEM_ID: str = "zephyr-alpha"
ZERO_HASH: str = "0" * 64


class WitnessSignature(BaseModel):
    """见证者签名——附在创世块上以建立多方信任。"""

    model_config = ConfigDict(frozen=True)

    witness_id: str = ""
    signature_hex: str = ""
    signed_at: str = ""
    public_key_pem: str = ""


class GenesisBlock(BaseModel):
    """创世块——审计链的不可变起点。

    使用 pydantic frozen 模型确保建立后不可修改。
    """

    model_config = ConfigDict(frozen=True)

    genesis_id: str = ""
    system_id: str = ""
    creator: str = ""
    prev_hash: str = ZERO_HASH
    genesis_hash: str = ""
    initial_config: dict[str, Any] = Field(default_factory=dict)
    witness_signatures: list[WitnessSignature] = Field(default_factory=list)
    backup_paths: list[str] = Field(default_factory=list)
    created_at: str = ""


class GenesisVerificationResult:
    """创世块验证结果。"""

    def __init__(
        self,
        issues: list[str] | None = None,
        genesis_hash: str = "",
        *,
        is_valid: bool = False,
        hash_valid: bool = False,
        prev_hash_valid: bool = False,
    ) -> None:
        self.is_valid = is_valid
        self.hash_valid = hash_valid
        self.prev_hash_valid = prev_hash_valid
        self.issues = issues if issues is not None else []
        self.genesis_hash = genesis_hash


def _canonical_json(data: object) -> str:
    """生成确定性 JSON 字符串用于哈希。"""
    return json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)


def _compute_genesis_hash(block_data: dict[str, Any]) -> str:
    """根据创世块内容（排除 genesis_hash 字段）计算 SHA-256 哈希。"""
    payload = {k: v for k, v in block_data.items() if k != "genesis_hash"}
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class GenesisManager:
    """创世块管理器——负责创建、持久化与验证创世块。"""

    def __init__(
        self,
        data_dir: Path | str | None = None,
        system_id: str = DEFAULT_SYSTEM_ID,
        creator: str = "",
    ) -> None:
        # 治本（AI-AUDIT12 路径SSoT收敛）：cwd 相对默认锚定 REPO_ROOT 真源。
        from zephyr.shared.io.paths import REPO_ROOT

        self._data_dir = Path(data_dir) if data_dir is not None else REPO_ROOT / "data" / "audit_genesis"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._system_id = system_id
        self._creator = creator

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def system_id(self):
        """只读：system_id（Stage 4 公共化）。"""
        return self._system_id

    @system_id.setter
    def system_id(self, value):
        """写入：system_id（Stage 4 公共化）。"""
        self._system_id = value

    @property
    def data_dir(self) -> Path:
        return self._data_dir

    @property
    def genesis_path(self) -> Path:
        return self._data_dir / GENESIS_FILE

    def create_genesis(
        self,
        initial_config: dict[str, Any] | None = None,
        witnesses: list[WitnessSignature] | None = None,
        backup_dir: Path | str | None = None,
    ) -> GenesisBlock:
        """创建并持久化一个新的创世块。"""
        genesis_id = uuid.uuid4().hex
        created_at = datetime.now(UTC).isoformat()
        witnesses = list(witnesses) if witnesses else []
        config = dict(initial_config) if initial_config else {}

        backup_paths: list[str] = []
        if backup_dir is not None:
            backup_root = Path(backup_dir)
            backup_root.mkdir(parents=True, exist_ok=True)
            backup_path = backup_root / f"genesis-{genesis_id}.json"
            backup_paths.append(str(backup_path))

        block_data: dict[str, Any] = {
            "genesis_id": genesis_id,
            "system_id": self._system_id,
            "creator": self._creator,
            "prev_hash": ZERO_HASH,
            "genesis_hash": "",
            "initial_config": config,
            "witness_signatures": [w.model_dump() for w in witnesses],
            "backup_paths": backup_paths,
            "created_at": created_at,
        }

        genesis_hash = _compute_genesis_hash(block_data)
        block_data["genesis_hash"] = genesis_hash

        self._persist(block_data)

        if backup_dir is not None and backup_paths:
            backup_path = Path(backup_paths[0])
            backup_path.write_text(
                json.dumps(block_data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

        return GenesisBlock(**block_data)

    def _persist(self, block_data: dict[str, Any]) -> None:
        """将创世块写入 data_dir/genesis.json（原子写 + 落盘刷盘）。

        治本（AI-AUDIT12 耐久性对齐 5.74.4）：os.replace 前 flush+fsync，
        确保创世块内容真正落盘——崩溃后不会出现目标文件存在但内容空洞，
        破坏审计链不可变起点（本组件 SAFETY=H）。
        """
        self._data_dir.mkdir(parents=True, exist_ok=True)
        tmp_path = self.genesis_path.with_suffix(".json.tmp")
        content = json.dumps(block_data, indent=2, ensure_ascii=False, default=str)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        tmp_path.replace(self.genesis_path)

    def verify_genesis(self, block: GenesisBlock | None = None) -> GenesisVerificationResult:
        """验证创世块完整性。

        若未提供 block，则从 data_dir/genesis.json 加载。
        """
        if block is None:
            if not self.genesis_path.exists():
                return GenesisVerificationResult(
                    is_valid=False,
                    hash_valid=False,
                    prev_hash_valid=False,
                    issues=["Genesis block not found"],
                )
            try:
                raw = json.loads(self.genesis_path.read_text(encoding="utf-8"))
                block = GenesisBlock(**raw)
            except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
                return GenesisVerificationResult(
                    is_valid=False,
                    hash_valid=False,
                    prev_hash_valid=False,
                    issues=[f"Failed to load genesis block: {exc}"],
                )

        issues: list[str] = []
        block_data = block.model_dump()
        recomputed = _compute_genesis_hash(block_data)
        hash_valid = recomputed == block.genesis_hash
        if not hash_valid:
            issues.append("Genesis hash mismatch")

        prev_hash_valid = block.prev_hash == ZERO_HASH
        if not prev_hash_valid:
            issues.append("Invalid prev_hash: expected all-zeros")

        is_valid = hash_valid and prev_hash_valid
        return GenesisVerificationResult(
            is_valid=is_valid,
            hash_valid=hash_valid,
            prev_hash_valid=prev_hash_valid,
            issues=issues,
        )
