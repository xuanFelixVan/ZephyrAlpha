# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §12

# [MODULE] zephyr.gov_audit.bridge

# [DOMAIN] D_GOV_AUDIT

# [DEPENDENCIES] zephyr.gov_audit.drift_bridge; zephyr.gov_audit.feedback_bridge; zephyr.gov_audit.delegation_bridge; zephyr.gov_audit.merkle_hourly; zephyr.gov_audit.trust_bridge; zephyr.gov_audit.tiered_storage_bridge

# [CONSUMERS] audit-orchestrator.*; pipeline_runner

# [STARTUP] imported

# [MATURITY] production

# [INVARIANTS] 统一桥接入口; 所有外部依赖通过此桥接访问

# [MODIFY-GUARD] 新增外部依赖必须在此注册

# [STABILITY] evolving

# [SAFETY] H

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] 桥接失败返回None或空结果

# [TESTS] tests/audit-orchestrator/test_bridge.py

# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

# [TTL] permanent

import logging
from typing import Any

logger = logging.getLogger(__name__)


__all__ = ["OrchestratorBridge", "write_to_core"]


def write_to_core(channel: str, payload: dict[str, Any]) -> str | None:
    """写入核心审计链——治本（裁定#18 G7 + 5.37.1）：真实落盘 events.jsonl。



    旧实现是 no-op（仅 log），_get_writer 恒返回 None，导致：

    - writer 可用时未写入也未返回 chain_hash

    - event_type / agent_id 默认逻辑缺失



    现委托到 _get_writer() 返回的全局 writer（5.37.1：懒初始化 get_audit_writer()，

    复用 AuditWriter 的 append-only JSONL + SHA-256 hash chain + HMAC，不新造实现），处理：

    - writer 为 None（初始化失败）→ 返回 None

    - event_type 设为 channel，agent_id 缺失时用 channel 兜底

    - writer 异常 → 返回 None（不传播）

    """

    writer = _get_writer()

    if writer is None:
        return None

    event: dict[str, Any] = dict(payload)

    event["event_type"] = channel

    if "agent_id" not in event:
        event["agent_id"] = channel

    try:
        return writer.write(event)

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("write_to_core failed channel=%s", channel, exc_info=True)

        return None


class OrchestratorBridge:
    def __init__(self) -> None:

        self._drift_bridge = None

        self._feedback_bridge = None

        self._delegation_bridge = None

        self._merkle_bridge = None

        self._trust_bridge = None

        self._storage_bridge = None

        self._init_bridges()

    def _init_bridges(self) -> None:

        try:
            from zephyr.gov_audit.drift_bridge import DriftBridge

            self._drift_bridge = DriftBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("DriftBridge init failed: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.feedback_bridge import FeedbackBridge

            self._feedback_bridge = FeedbackBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("FeedbackBridge init failed: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.delegation_bridge import DelegationBridge

            self._delegation_bridge = DelegationBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("DelegationBridge init failed: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.merkle_hourly import MerkleHourlyBridge

            self._merkle_bridge = MerkleHourlyBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("MerkleHourlyBridge init failed: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.trust_bridge import TrustBridge

            self._trust_bridge = TrustBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("TrustBridge init failed: %s", exc, exc_info=True)

        try:
            from zephyr.gov_audit.tiered_storage_bridge import TieredStorageBridge

            self._storage_bridge = TieredStorageBridge()

        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("TieredStorageBridge init failed: %s", exc, exc_info=True)

    def check_drift(self, metrics: dict[str, float]) -> dict[str, Any]:

        if self._drift_bridge and self._drift_bridge.is_available():
            return self._drift_bridge.check_drift(metrics)

        return {"is_drifting": False, "drift_score": 0.0, "available": False}

    def analyze_findings(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:

        if self._feedback_bridge and self._feedback_bridge.is_available():
            return self._feedback_bridge.analyze_audit_findings(findings)

        return []

    def report_delegation_failure(self, target: str, reason: str) -> dict[str, Any] | None:

        if self._delegation_bridge and self._delegation_bridge.is_available():
            return self._delegation_bridge.report_delegation_failure(target, reason)

        return None

    def verify_merkle(self, hour_key: str, expected_root: str) -> bool:

        if self._merkle_bridge and self._merkle_bridge.is_available():
            return self._merkle_bridge.verify(hour_key, expected_root)

        return False

    def health_check(self) -> dict[str, bool]:

        return {
            "drift": self._drift_bridge is not None and self._drift_bridge.is_available(),
            "feedback": self._feedback_bridge is not None and self._feedback_bridge.is_available(),
            "delegation": self._delegation_bridge is not None and self._delegation_bridge.is_available(),
            "merkle": self._merkle_bridge is not None and self._merkle_bridge.is_available(),
            "trust": self._trust_bridge is not None and self._trust_bridge.is_available(),
            "storage": self._storage_bridge is not None and self._storage_bridge.is_available(),
        }


def _get_writer(backend: str | None = None):
    """获取全局 writer——治本（裁定#18 G7 + 5.37.1）：供 write_to_core 委托。



    双 API 兼容（test_bridge.py TestGetWriterCaching）：

    - 测试通过 patch ``bridge._AVAILABLE`` (True) + ``bridge._CoreWriter`` 注入 mock。

      _WRITER 为 None 时通过 _CoreWriter() 实例化并缓存到 _WRITER。

    - 生产环境 _AVAILABLE=True 时路由到 writer._GLOBAL_WRITER（懒初始化）。

    - _AVAILABLE=False 时返回 None（向后兼容契约）。

    """

    global _WRITER

    if not _AVAILABLE:
        return None

    # Test API: if _CoreWriter is defined (patched), use _WRITER caching pattern

    if _CoreWriter is not None:
        if _WRITER is None:
            try:
                _WRITER = _CoreWriter()

            except Exception:  # noqa: BLE001
                logger.warning("_get_writer _CoreWriter init failed", exc_info=True)

                return None

        return _WRITER

    # Production API: route to writer._GLOBAL_WRITER

    from zephyr.gov_audit import writer as _writer_mod

    if _writer_mod._GLOBAL_WRITER is None:
        try:
            return _writer_mod.get_audit_writer()

        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("_get_writer lazy init failed", exc_info=True)

            return None

    return _writer_mod._GLOBAL_WRITER


# _AVAILABLE: bool — True when writer subsystem is available (test_bridge.py expects bool)

_AVAILABLE = True


# _WRITER: cached writer instance for test API (test_bridge.py patches _CoreWriter)

_WRITER: object | None = None


# _CoreWriter: None in production (test patches this via patch(create=True))

_CoreWriter: object | None = None
