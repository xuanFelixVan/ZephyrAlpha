# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.sensitivity_sweeper
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/security/test_sensitivity_sweeper.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_sensitivity_sweeper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""敏感性扫荡——threshold扫描→固化成new baseline（零假阳性+触达率保险）."""

from dataclasses import dataclass, field


@dataclass
class SweepResult:
    threshold: float
    detected: int
    confirmed_clones: int
    false_positives: int
    recall_rate: float
    precision_rate: float
    balanced: bool = False

    @property
    def f1(self) -> float:
        if self.precision_rate + self.recall_rate == 0:
            return 0.0
        return 2.0 * (self.precision_rate * self.recall_rate) / (self.precision_rate + self.recall_rate)


@dataclass
class SensitivitySweeper:
    thresholds: list[float] = field(default_factory=lambda: [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95])
    results: list[SweepResult] = field(default_factory=list)
    best_threshold: float = 0.80

    def sweep(self, threshold: float, detected: int, confirmed_clones: int, false_positives: int) -> SweepResult:
        precision = confirmed_clones / (detected) if detected > 0 else 0.0
        recall = confirmed_clones / max(confirmed_clones + false_positives, 1)
        balanced = precision >= 0.90 and recall >= 0.85

        result = SweepResult(
            threshold=threshold,
            detected=detected,
            confirmed_clones=confirmed_clones,
            false_positives=false_positives,
            recall_rate=recall,
            precision_rate=precision,
            balanced=balanced,
        )
        self.results.append(result)

        if balanced and result.f1 > self._best_f1():
            self.best_threshold = threshold
        return result

    def _best_f1(self) -> float:
        if not self.results:
            return 0.0
        return max(r.f1 for r in self.results)

    def get_baseline(self) -> float:
        return self.best_threshold
