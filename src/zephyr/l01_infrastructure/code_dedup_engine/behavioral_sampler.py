# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.behavioral_sampler

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""行为采样验证器 — Stage 0.25 低成本快速验证."""

from __future__ import annotations

import ast
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class BehaviorSample:
    func_name: str = ""
    inputs: list[Any] = field(default_factory=list)
    output: Any = None
    is_pure: bool = False
    passed: bool = False


class BehavioralSampler:
    """行为采样——生成测试输入并验证行为一致性."""

    _SAMPLE_COUNT: int = 3

    def generate_samples(self, source: str) -> list[dict]:
        """AST分析→生成采样输入."""
        try:
            tree = ast.parse(source.lstrip())
        except SyntaxError:
            return [{"input": None, "type": "unknown"}]

        samples: list[dict] = [{"input": i, "type": f"sample_{i}"} for i in range(self._SAMPLE_COUNT)]
        return samples

    def verify_behavior(self, func_a: callable, func_b: callable, samples: list[Any]) -> BehaviorSample:
        """对相同输入调用两个函数→输出一致=PASS."""
        passed = True
        for inp in samples[:self._SAMPLE_COUNT]:
            try:
                a = func_a(inp) if inp is not None else func_a()
                b = func_b(inp) if inp is not None else func_b()
                if a != b:
                    passed = False
                    break
            except Exception:
                passed = False
                break

        return BehaviorSample(
            func_name=getattr(func_a, "__name__", "?"),
            inputs=samples[:self._SAMPLE_COUNT],
            passed=passed,
        )

    def is_pure_function(self, source: str) -> bool:
        """启发式纯函数判定——无global/nonlocal/print/副作用."""
        keywords = {"global", "nonlocal", "print("}
        return not any(kw in source for kw in keywords)
