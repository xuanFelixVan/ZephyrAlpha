"""Amplification Guard — v0.10.0 R134

Blindspot: Multi-hop prompt chains amplify small biases into large errors.
Risk: R134 — Prompt chain amplification causes diagnosis cascade failure.
"""
from dataclasses import dataclass

@dataclass
class AmplificationGuard:
    max_amplification: float = 5.0

    def check(self, input_bias: float, output_bias: float) -> bool:
        return abs(output_bias / max(input_bias, 0.001)) <= self.max_amplification
