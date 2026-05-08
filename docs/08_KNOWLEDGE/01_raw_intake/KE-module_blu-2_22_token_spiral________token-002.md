---
module_id: KE-module_blu-2_22_token_spiral________token-002
title: 2.22 Token Spiral 早期预警系统（Token Spiral EWS）
category: module_blueprint
---

# 2.22 Token Spiral 早期预警系统（Token Spiral EWS）

2.22 Token Spiral 早期预警系统（Token Spiral EWS）

> **决策 D-024-20（🆕 v0.6.0）**：TechAhead 2026 描述 token spiral 为"一个任务变成 47 次 API 调用"。传统的 Burn Rate 监控总速率——Spiral EWS 专门检测**每次调用都在放大下一步的调用量**的结构性扩张模式。

```yaml
token_spiral_ews:
  description: "检测请求量指数增长的螺旋模式——与 Burn Rate（总速率）互补"
  # Burn Rate 说"烧得快"；Spiral EWS 说"每一个请求让下一个请求更大/更多"

  spiral_markers:
    expanding_context:
      description: "每次 LLM 调用的 input token 比上次更大——可能是 context 积聚"
      detection: "last_5_inputs 呈递增趋势（Pearson r > 0.7）"
      action: "WARN '上下文在膨胀——建议立即 /compact'"

    multiplying_tool_calls:
      description: "每次 LLM 响应的 tool_call 数量递增——ReAct 循环失控前兆"
      detection: "last_5_turns 的 tool_call count 单调递增"
      action: "WARN '工具调用链在扩张——可能陷入 ReAct loop'"
      escalate: "连续 3 次递增 → L3_compress"

    depth_explosion:
      description: "agent-to-agent 委托深度超过安全阈值"
      detection: "delegation_depth > 4"
      action: "HALT delegation + 扁平化处理（不委托，直接执行）"

    time_per_turn_growth:
      description: "每轮耗时递增——模型在处理越来越复杂的问题"
      detection: "last_5_turns duration 单调递增"
      action: "WARN + 建议 Narrow Scope 或拆分任务"

  spiral_score:
    description: "综合螺旋风险得分 0-100"
    formula: "weighted_sum(expanding_context, multiplying_tool_calls, depth_explosion, time_growth)"
    thresholds:
      score_30: "L1_warning"
      score_60: "L3_compress + auto_narrow"
      score_80: "L6_kill_switch——强制中断 spiral"
```
