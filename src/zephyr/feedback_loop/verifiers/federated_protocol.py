"""Federated Protocol — v0.10.0 R129

Blindspot: Multi-FLE instances operate without coordination protocol.
"""
from dataclasses import dataclass

@dataclass
class FederatedProtocol:
    instance_id: str = ""
    peers: list[str] = []
