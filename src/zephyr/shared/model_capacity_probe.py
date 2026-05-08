"""
Model Capacity Probe — AI 模型静默升级探测 (盲点 #57)
特性：
  - 每日 07:00 金丝雀任务
  - 检测延迟 / Token / 代码行数漂移
"""
import time
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ProbeResult:
    model: str
    latency_ms: float
    tokens_output: int
    code_lines: int
    drift_detected: bool = False
    drift_details: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class ModelCapacityProbe:
    """
    模型容量探针 (盲点 #57)
    """

    LATENCY_DRIFT_THRESHOLD = 2.0
    TOKEN_DRIFT_THRESHOLD = 1.5
    CODE_LINE_DRIFT_THRESHOLD = 1.5

    def __init__(self):
        self._baselines: dict[str, ProbeResult] = {}

    def set_baseline(self, model: str, result: ProbeResult):
        self._baselines[model] = result

    def probe(self, model: str, latency_ms: float,
              tokens_output: int, code_lines: int) -> ProbeResult:
        baseline = self._baselines.get(model)
        result = ProbeResult(
            model=model, latency_ms=latency_ms,
            tokens_output=tokens_output, code_lines=code_lines,
        )

        if baseline:
            latency_ratio = latency_ms / max(baseline.latency_ms, 0.01)
            token_ratio = tokens_output / max(baseline.tokens_output, 1)
            code_ratio = code_lines / max(baseline.code_lines, 1)

            if latency_ratio > self.LATENCY_DRIFT_THRESHOLD:
                result.drift_detected = True
                result.drift_details.append(
                    f"Latency drift: {latency_ratio:.1f}x"
                )
            if token_ratio > self.TOKEN_DRIFT_THRESHOLD:
                result.drift_detected = True
                result.drift_details.append(
                    f"Token drift: {token_ratio:.1f}x"
                )
            if code_ratio > self.CODE_LINE_DRIFT_THRESHOLD:
                result.drift_detected = True
                result.drift_details.append(
                    f"Code lines drift: {code_ratio:.1f}x"
                )

        return result
