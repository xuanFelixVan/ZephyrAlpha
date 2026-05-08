---
module_id: KE-module_blu-agent____n___agentprogress_obs-003
title: 基础规则：Agent 连续 N 次 AgentProgress.observation_hash 相同 → 陷入循环
category: module_blueprint
---

# 基础规则：Agent 连续 N 次 AgentProgress.observation_hash 相同 → 陷入循环

基础规则：Agent 连续 N 次 AgentProgress.observation_hash 相同 → 陷入循环
HALLUCINATION_RULES = {
    "loop_same_observation": {
        "threshold_count": 3,
        "window_seconds": 120,
        "action": "transition_to_hallucinating",
    },
    "no_progress_timeout": {
        "threshold_seconds": 300,  # 5 分钟无 progress 上报
        "action": "transition_to_hallucinating",
    },
    "token_budget_exceeded": {
        "threshold_multiplier": 3.0,  # 超预算 3 倍
        "action": "transition_to_hallucinating",
    },
    "repeated_same_file_edit": {
        "threshold_count": 10,  # 同一文件 10 次编辑
        "window_seconds": 600,
        "action": "transition_to_hallucinating",
    },
    "tool_call_explosion": {
        "threshold_count_per_minute": 50,
        "action": "transition_to_hallucinating",
    },
}
