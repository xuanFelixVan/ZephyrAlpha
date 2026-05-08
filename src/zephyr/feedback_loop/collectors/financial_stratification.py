"""Financial Stratification — v0.5.0 R50

Blindspot: One-size-fits-all diagnosis across asset classes.
Risk: R50 — Equity diagnosis applied to FX creates nonsense repairs.
"""
from dataclasses import dataclass

@dataclass
class FinancialStratification:
    asset_class: str = "EQUITY"
