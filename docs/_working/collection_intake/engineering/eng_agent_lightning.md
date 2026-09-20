---
ttl: task_bound
session: st-collintake-20260920
topic: collection_intake_20260920
---

# Agent Lightning v1.0（微软）——AI 层候选观察项 2026-09-20

> 剪报勘误 `[外部]`：剪报给的仓址 `agentlightning/agent-lightning` **404，真实仓库=microsoft/agent-lightning**。其余卖点全部证实：①"零改动接入 RL"属实（README 原文 "ZERO changes"，经 proxy 保留工具/上下文/控制流）；②SWE-bench Verified **41.8%→56.4% 属实，但绑定 Qwen3.5-9B 端到端工作流 + 6K 训练样本**——引用必须带此限定；MIT license；18.4k★；PyPI `agentlightning` v1.0.1（2026-08-24，Python≥3.12）；v1.0 系完全重构（~3500 行）。

## 本体速览 `[外部]`

- 定位：把现有 agent 接入强化学习训练回路——agent 照常跑任务，轨迹被收集为训练信号，反哺模型/策略。
- 安装：`pip install agentlightning`；训练路径用 `uv sync` + `scripts/setup_verl.sh`（verl 生态）。

## 内部挖矿 `[亲验]`

- **全仓无真 RL**：无 gym/DQN/policy gradient；最接近的是 `feedback_loop/session_learner.py`、`autonomy_core/skills/skill_learning.py`（会话学习，非 RL）。
- E1C 的 AlphaGen（RL 拼公式）在 production map 仅为 design_ref；实际落地=gplearn 遗传规划+本地 LLM 产 DSL。
- AI 层 v2.0 主文档：`docs/_working/ai_layer_vision/ai_layer_vision_and_roadmap_v1.md`（自我进化引擎愿景，含 OBJ_M 模型线）。

## 判定与行动

**C P2（AI 层候选观察项）**：
1. 不立即引入。触发条件：AI 层 v2.0 的"自进化环"立项时，Agent Lightning 作为候选底座评估（与 verl 生态、自研轨迹回流三选一比选）。
2. 潜在落点：用 RL 优化 E1C 挖掘 agent 的提示/工具策略（不是直接优化因子本身）；或优化 LSG 上多代理协作的调度策略。
3. 合规注意：任何接入经 LSG 网关；训练数据含策略轨迹=敏感资产，走 Layer2/密钥规范。
