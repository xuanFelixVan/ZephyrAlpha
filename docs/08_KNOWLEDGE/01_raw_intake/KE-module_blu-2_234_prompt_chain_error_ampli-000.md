---
module_id: KE-module_blu-2_234_prompt_chain_error_ampli-000
title: 2.234 Prompt Chain Error Amplification Monitor - prompt_chain_amplification.py (
category: module_blueprint
---

# 2.234 Prompt Chain Error Amplification Monitor - prompt_chain_amplification.py (

2.234 Prompt Chain Error Amplification Monitor - prompt_chain_amplification.py (🆕 v0.22.0 - 盲点283 — LLM调用链中错误的逐级放大效应)

**致命问题**：FLE的DETECT→DIAGNOSE→REPAIR→VERIFY→NOTIFY形成5跳LLM链。每个LLM调用的微小偏差（如DETECT将边界异常的severity高估了10%）→DIAGNOSE在错误severity输入下做诊断→偏差放大到25%→REPAIR选择过度激进的修复→VERIFY基于修复后的异常状态做评估→偏差累积到40%。这是氛围编程中prompt chain的经典陷阱：级联偏差（cascading bias）。目前没有任何监测点追踪链级误差传播。
**对标**：Microsoft PromptFlow Error Tracing + LangGraph State Graph Debugging + DSPy Chain Optimization + Anthropic Chain-of-Thought Faithfulness

```python
@dataclass
class ChainStepOutput:
    step_name: str           # "DETECT"|"DIAGNOSE"|"REPAIR"|"VERIFY"|"NOTIFY"
    input_confidence_interval: tuple[float, float]  # 输入的置信区间
    output_distribution: dict[str, float]  # 输出的概率分布
    deviation_from_calibrated: float       # 偏离标定基线的程度

class PromptChainAmplificationMonitor:
    MAX_AMPLIFICATION_FACTOR: float = 3.0  # 任一环节偏差放大超过3x→告警
    CHAIN_HALT_THRESHOLD: float = 5.0       # 累积偏差超5x→中断链

    async def monitor_chain_amplification(self,
                                            decision_id: str) -> ChainAmplificationReport:
        steps = await self._load_decision_chain(decision_id)
        cumulative_deviation = 1.0
        amplification_trace = []
        for i, step in enumerate(steps):
            if i == 0:
                step_deviation = step.deviation_from_calibrated
            else:
                prev = steps[i-1]
                # 度量此步输出相对于"如果前一步是完美输入"的偏差
                step_deviation = await self._compute_counterfactual_deviation(
                    step, perfect_input=prev.calibrated_output)
            cumulative_deviation *= (1.0 + step_deviation)
            amplification_trace.append({
                "step": step.step_name,
                "step_deviation": step_deviation,
                "cumulative": cumulative_deviation,
                "amplification": step_deviation / max(0.01, steps[i-1].deviation_from_calibrated)
                    if i > 0 else 1.0})
            if cumulative_deviation > self.CHAIN_HALT_THRESHOLD:
                self.FLE.notify_owner("CHAIN_AMPLIFICATION_CRITICAL",
                    f"Prompt chain cumulative deviation={cumulative_deviation:.1f}x at step "
                    f"{step.step_name}. Decision chain HALTED. "
                    f"Amplification trace: {' → '.join(f'{t[\"step\"]}:{t[\"cumulative\"]:.1f}x' for t in amplification_trace)}. "
                    f"Recommend: re-run with CALIBRATED mode (lower temperature, multiple samples, consensus).")
                return ChainAmplificationReport(halted=True, trace=amplification_trace)
        return ChainAmplificationReport(halted=False, trace=amplification_trace,
            final_amplification=cumulative_deviation)
```
