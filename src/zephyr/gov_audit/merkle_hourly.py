# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.gov_audit.merkle_hourly
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.integrity
# [CONSUMERS] zephyr.governance.integrity ; zephyr.gov_audit.bridge ; zephyr.gov_audit.__init__(lazy re-export)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""




audit-trail.merkle_hourly — MOD-INF-020 · 每小时 Merkle 聚合
==============================================================
蓝图 D-020-04 · 每小时生成 Merkle Root + 独立 .merkle 文件

特性
----
  - 每小时自动聚合审计事件哈希
  - 生成 Merkle Root 写入独立 .merkle 文件
  - 支持历史 Merkle Root 查询
  - 与主事件日志解耦，独立验证

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: data_dir 参数
#   fields: 参数 data_dir（无注解）
#   code: merkle_hourly.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① HourlyMerkleAggregator
#   name_en: HourlyMerkleAggregator
#   intro: class HourlyMerkleAggregator 源码 L114-L232
#   desc: 公共方法（定义序）: aggregate, get_roots, verify_root；源码 L114-L232
#   inputs: data_dir
#   outputs: 返回值
# - id: A2
#   name_zh: ② MerkleHourlyBridge
#   name_en: MerkleHourlyBridge
#   intro: Merkle hourly 桥接器——封装 HourlyMerkleAggregator 的错误处理与可用性检查。
#   desc: Merkle hourly 桥接器——封装 HourlyMerkleAggregator 的错误处理与可用性检查。 从 zephyr.governance.merkle_hour…；公共方法（定义序）: aggrega…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: HourlyMerkleAggregator, MerkleHourlyBridge
#   downstream: zephyr.governance.integrity ; zephyr.gov_audit.bridge ; zephyr.gov_audit.__init…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import hmac
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

from zephyr.gov_audit.integrity import MerkleAggregator
from zephyr.shared.io.paths import AUDIT_DATA_DIR  # 路径真源（SSoT）
from zephyr.shared.io.serialization import dumps, filter_dataclass_fields

_logger = logging.getLogger(__name__)

# 治本（AI-AUDIT12 路径SSoT收敛）：原 Path("data/audit-trail") 相对路径（cwd 漂移即
# 聚合空目录），收敛为 AUDIT_DATA_DIR 绝对真源，与 writer/integrity 同目录。
DEFAULT_AUDIT_DATA_DIR: Path = AUDIT_DATA_DIR
MERKLE_DIR_NAME: str = "merkle_hourly"


class MerkleHourlyRoot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hour_key: str = ""
    merkle_root: str = ""
    entry_count: int = 0
    first_entry_hash: str = ""
    last_entry_hash: str = ""
    computed_at: str = ""


class AggregationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hour_key: str = ""
    merkle_root: str = ""
    entry_count: int = 0
    output_file: str = ""
    success: bool = True
    aggregated_at: str = ""


class HourlyMerkleAggregator:
    def __init__(
        self,
        data_dir: Path | str = DEFAULT_AUDIT_DATA_DIR,
    ) -> None:
        self._data_dir = Path(data_dir)
        self._merkle_dir = self._data_dir / MERKLE_DIR_NAME
        self._merkle_dir.mkdir(parents=True, exist_ok=True)
        self._event_log_path = self._data_dir / "events.jsonl"

    def aggregate(self, hour_key: str | None = None) -> AggregationResult | None:
        if hour_key is None:
            hour_key = datetime.now(UTC).strftime("%Y-%m-%dT%H")

        events = self._load_events_for_hour(hour_key)
        if not events:
            _logger.debug("HourlyMerkleAggregator: no events for hour %s", hour_key)
            return None

        entry_hashes = [e.get("entry_hash", "") for e in events if e.get("entry_hash")]
        if not entry_hashes:
            return None

        merkle_root = MerkleAggregator.build(entry_hashes)

        root_record = MerkleHourlyRoot(
            hour_key=hour_key,
            merkle_root=merkle_root,
            entry_count=len(entry_hashes),
            first_entry_hash=entry_hashes[0],
            last_entry_hash=entry_hashes[-1],
            computed_at=datetime.now(UTC).isoformat(),
        )

        output_file = self._merkle_dir / f"{hour_key.replace(':', '-')}.merkle"
        output_file.write_text(
            dumps(root_record.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        result = AggregationResult(
            hour_key=hour_key,
            merkle_root=merkle_root,
            entry_count=len(entry_hashes),
            output_file=str(output_file),
            success=True,
            aggregated_at=datetime.now(UTC).isoformat(),
        )
        _logger.info(
            "HourlyMerkleAggregator: aggregated hour %s, root=%s, entries=%d",
            hour_key,
            merkle_root[:16],
            len(entry_hashes),
        )
        return result

    def get_roots(
        self,
        since: str | None = None,
        until: str | None = None,
    ) -> list[MerkleHourlyRoot]:
        roots: list[MerkleHourlyRoot] = []
        if not self._merkle_dir.exists():
            return roots

        for f in sorted(self._merkle_dir.glob("*.merkle")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                root = MerkleHourlyRoot(**filter_dataclass_fields(MerkleHourlyRoot, data))
                if since and root.hour_key < since:
                    continue
                if until and root.hour_key > until:
                    continue
                roots.append(root)
            except (json.JSONDecodeError, OSError):
                continue

        return roots

    def verify_root(self, hour_key: str) -> bool:
        merkle_file = self._merkle_dir / f"{hour_key.replace(':', '-')}.merkle"
        if not merkle_file.exists():
            return False

        try:
            data = json.loads(merkle_file.read_text(encoding="utf-8"))
            stored_root = data.get("merkle_root", "")
        except (json.JSONDecodeError, OSError):
            return False

        events = self._load_events_for_hour(hour_key)
        entry_hashes = [e.get("entry_hash", "") for e in events if e.get("entry_hash")]
        if not entry_hashes:
            return False

        computed_root = MerkleAggregator.build(entry_hashes)
        return hmac.compare_digest(computed_root, stored_root)

    def _load_events_for_hour(self, hour_key: str) -> list[dict[str, Any]]:
        if not self._event_log_path.exists():
            return []

        events: list[dict[str, Any]] = []
        with open(self._event_log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    ts = event.get("timestamp", "")
                    if ts:
                        event_hour = ts[:13].replace(":", "-")
                        if event_hour == hour_key.replace(":", "-"):
                            events.append(event)
                except json.JSONDecodeError:
                    continue

        return events


class MerkleHourlyBridge:
    """Merkle hourly 桥接器——封装 HourlyMerkleAggregator 的错误处理与可用性检查。

    从 zephyr.governance.merkle_hourly 迁入（域拆分 shim 消除，2026-07-14）。
    不实现 Merkle 逻辑，仅桥接 HourlyMerkleAggregator，桥接失败返回空结果。
    """

    def __init__(self) -> None:
        self._aggregator: HourlyMerkleAggregator | None = None
        self._available = False
        try:
            self._aggregator = HourlyMerkleAggregator()
            self._available = True
        except ImportError:
            _logger.warning("HourlyMerkleAggregator not available")
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.warning("HourlyMerkleAggregator init failed: %s", exc, exc_info=True)

    def aggregate(self, hour_key: str | None = None) -> dict[str, Any] | None:
        if not self._available or self._aggregator is None:
            return None
        try:
            result = self._aggregator.aggregate(hour_key)
            if result is None:
                return None
            return result.model_dump()
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error("MerkleHourlyBridge.aggregate failed: %s", exc, exc_info=True)
            return None

    def verify(self, hour_key: str, expected_root: str) -> bool:
        if not self._available or self._aggregator is None:
            return False
        try:
            result = self._aggregator.aggregate(hour_key)
            if result is None:
                return False
            return result.merkle_root == expected_root
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error("MerkleHourlyBridge.verify failed: %s", exc, exc_info=True)
            return False

    def is_available(self) -> bool:
        return self._available
