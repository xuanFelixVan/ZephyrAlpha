"""Federated Security — v0.10.0 R131

Blindspot: Multi-instance FLE deployments share no security context.
Risk: R131 — One compromised instance poisons federation.
"""
from dataclasses import dataclass, field

@dataclass
class FederatedSecurity:
    trusted_peers: set[str] = field(default_factory=set)

    def verify_peer(self, peer_id: str) -> bool:
        return peer_id in self.trusted_peers
