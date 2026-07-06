# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_frame_negotiation
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_frame_negotiation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A ANP 帧协商协议 — Agent Negotiation Protocol 帧层协商

ANP (Agent Negotiation Protocol) — 对标 Google ANP 开放提案:
  两个 Agent 在通信前先协商:
  - 协议版本 (Protocol Version)
  - 能力交换 (Capability Exchange)
  - 帧格式 (Frame Format: JSON/Binary/Protobuf)
  - 压缩算法 (Compression: none/gzip/zstd)
  - 最大消息大小 (Max Message Size)

输出: NegotiatedFrame — 双方匹配后的通信参数
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FrameOffer:
    agent_id: str
    protocol_version: str = "0.10.0"
    frame_format: str = "json"
    compression: str = "none"
    max_message_size: int = 1_000_000
    supported_capabilities: list[str] = field(default_factory=list)


@dataclass
class NegotiatedFrame:
    protocol_version: str
    frame_format: str
    compression: str
    max_message_size: int
    agreed_capabilities: list[str] = field(default_factory=list)
    negotiation_successful: bool = False


class A2AFrameNegotiation:
    def __init__(
        self,
        supported_versions: list[str] | None = None,
        supported_formats: list[str] | None = None,
        supported_compressions: list[str] | None = None,
    ):
        self._supported_versions = supported_versions or ["0.10.0", "0.9.0"]
        self._supported_formats = supported_formats or ["json"]
        self._supported_compressions = supported_compressions or ["none", "gzip"]

    def negotiate(self, offer_a: FrameOffer, offer_b: FrameOffer) -> NegotiatedFrame:
        version = self._best_match([offer_a.protocol_version], [offer_b.protocol_version], self._supported_versions)
        fmt = self._best_match([offer_a.frame_format], [offer_b.frame_format], self._supported_formats)
        comp = self._best_match([offer_a.compression], [offer_b.compression], self._supported_compressions)
        max_size = min(offer_a.max_message_size, offer_b.max_message_size)

        caps_a = set(offer_a.supported_capabilities)
        caps_b = set(offer_b.supported_capabilities)
        agreed_caps = sorted(caps_a & caps_b)

        success = version != "" and fmt != ""

        return NegotiatedFrame(
            protocol_version=version,
            frame_format=fmt,
            compression=comp,
            max_message_size=max_size,
            agreed_capabilities=agreed_caps,
            negotiation_successful=success,
        )

    def _best_match(self, a: list[str], b: list[str], supported: list[str]) -> str:
        for s in supported:
            if s in a and s in b:
                return s
        return ""
