"""Sim2Real Calibration — v0.6.0 R56

Blindspot: Simulation accuracy degrades without recalibration.
Risk: R56 — Simulated repair success rate diverges from real success rate.
"""
from dataclasses import dataclass

@dataclass
class Sim2RealCalibration:
    sim_accuracy: float = 0.0
    real_accuracy: float = 0.0

    @property
    def gap(self) -> float:
        return abs(self.sim_accuracy - self.real_accuracy)
