# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.security.metric_prompt_scanner
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Metric-Prompt Scanner — v0.15.0 R215

Blindspot: Metric values injected directly into LLM prompts; prompt injection via metric poison.
Risk: R215 — Attacker poisons metric value "ignore all previous instructions"; FLE executes.

Mitigation: Pre-LLM scan of all metric values for prompt injection patterns.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: metric_prompt_scanner.py
# 层: 算法
# - id: A1
#   name_zh: ① MetricPromptScanner
#   name_en: MetricPromptScanner
#   intro: class MetricPromptScanner 源码 L68-L85
#   desc: 公共方法（定义序）: scan；源码 L68-L85
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: MetricPromptScanner
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanResult:
    metric: str
    value: str
    suspicious: bool
    pattern_matched: str = ""


@dataclass
class MetricPromptScanner:
    patterns: list[str] = field(
        default_factory=lambda: [
            "ignore previous",
            "ignore all",
            "system prompt:",
            "you are now",
            "new instructions:",
            "your new task is",
        ]
    )

    def scan(self, metric_name: str, value: str) -> ScanResult:
        value_lower = value.lower()
        for pattern in self.patterns:
            if pattern.lower() in value_lower:
                return ScanResult(metric=metric_name, value=value, suspicious=True, pattern_matched=pattern)
        return ScanResult(metric=metric_name, value=value, suspicious=False)
