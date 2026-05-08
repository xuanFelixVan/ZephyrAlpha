"""Regulatory Audit Detector — v0.13.0 R184

Blindspot: FLE actions unseen by regulatory compliance framework.
Risk: R184 — Automated repair violates regulation (e.g., MiFID II best execution).
"""
from dataclasses import dataclass

@dataclass
class RegulatoryAudit:
    regulations: list[str] = ["MiFID II", "SEC Rule 606"]
