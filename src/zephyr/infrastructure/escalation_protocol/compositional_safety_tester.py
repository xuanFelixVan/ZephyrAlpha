"""Compositional Safety Tester — v0.14.0 组合性不安全测试器。"""
from __future__ import annotations

class CompositionalSafetyTester:
    INDIVIDUALLY_SAFE=["read_config","write_log","send_metric"]
    DANGEROUS_COMBOS=[({"read_config","write_log"},"config_modification"),
                       ({"read_config","send_metric"},"config_exfiltration")]

    def test_composition(self, operations:set[str])->list[str]:
        risks=[]
        for combo,description in self.DANGEROUS_COMBOS:
            if combo.issubset(operations):
                risks.append(description)
        return risks

    def is_safe_combination(self, operations:set[str])->bool:
        return len(self.test_composition(operations))==0
