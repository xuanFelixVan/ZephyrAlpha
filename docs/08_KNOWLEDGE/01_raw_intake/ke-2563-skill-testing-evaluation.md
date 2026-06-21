---
module_id: KE-2468---evaluation-000
status: active
title: 8.1 Skill Testing & Evaluation Framework（决策 D-019-06）
category: module_blueprint
---

# 8.1 Skill Testing & Evaluation Framework（决策 D-019-06）

8.1 Skill Testing & Evaluation Framework（决策 D-019-06）

> **决策 D-019-06（新增）**：每个 Skill 发布前必须通过两级测试——指令有效性测试（Skill 指令是否被 Agent 正确理解和执行）和执行轨迹测试（Agent 执行 Skill 时的工具调用链是否符合预期）。
>
> **决策依据**：
> - Galileo.ai 研究：40% 的 AI Agent 项目因评估缺失而失败。Agents 从单次 60% 成功率暴跌到 8 次连续运行的 25%
> - Anthropic 官方要求："No eval score should be taken at face value until someone reads the transcripts"
> - Agent 测试与传统软件测试有本质差异：概率性输出 + 组合爆炸的执行路径 + emergent behavior
> - AgentBench-RW 已形成社区标准化的 Agent 能力评估框架

```yaml
skill_evaluation_framework:
  description: "三层评估体系——对标 Galileo.ai 7维→25子维→130项 的工业级标准"

  L1_Instruction_Validity:
    description: "Skill 静态正确性——SKILL.md 本身是否完整、无歧义、可解析"
    checks:
      - "YAML frontmatter 结构完整性（必填字段: name/description/tools/model）"
      - "L3 references 交叉引用有效性（所有引用文件存在且路径正确）"
      - "Checklist 条目可操作性（每条必须有明确的断言式验证步骤）"
      - "Model Hint 字段对多模型均合法"
    tool: "skill_schema_validator.py——运行于 CI pre-commit 阶段"
    pass_criteria: "所有 L1 检查通过 → 允许合并"

  L2_Execution_Trajectory:
    description: "Agent 执行 Skill 时的行为轨迹——对标 trajectory_exact_match / trajectory_precision / trajectory_recall"
    metrics:
      trajectory_exact_match: "Agent 的工具调用顺序是否与预期序列完全一致"
      trajectory_precision: "Agent 的每一步是否都在 Skill Checklist 定义的合法操作中"
      step_completion_rate: "Checklist N 步中完成了 M 步（M/N ≥ 0.85）"
      tool_call_overhead: "非必要工具调用数 / 总工具调用数（≤ 0.15）"
    evaluation_method: "LLM-as-a-Judge（目标 Spearman ρ ≥ 0.80 with human）"
    dataset: "每个 Skill 附带 3-5 个 Test Scenario（含输入描述 + 预期工具调用序列）"
    benchmarks:
      - "SWE-bench Verified（代码生成场景）"
      - "WebArena（Web 交互场景）"
      - "GAIA（复杂推理场景）"
      - "domain-specific: ZephyrAlpha 自建 test suite（蓝图→代码的端到端验证）"

  L3_Outcome_Quality:
    description: "最终产出物质量——不只看执行过程，更要看结果是否正确"
    metrics:
      gate_pass_rate: "Skill 执行后 G0-G7 门禁通过率（目标 ≥ 0.95）"
      test_pass_rate: "产出的代码对应模块的 pytest 通过率（目标 ≥ 0.98）"
      lint_zero_rate: "ruff/mypy 零告警率（目标 1.0）"
      semantic_fidelity: "产出的代码是否语义等价于蓝图 §3 接口契约（LLM-as-a-Judge）"
    regression_detection: "CI 中积分——commit/scheduled/event-driven 三触发模式"

  benchmark_cycle:
    description: "每个 Skill 的生命周期评估周期"
    on_create: "全量 L1+L2+L3 评估（人工 + 自动）"
    on_update: "增量评估——只对变更的指令段重新跑 L2 轨迹测试"
    on_blueprint_change: "关联蓝图版本变更时触发全量 L2+L3 回归测试"
    periodic: "每 30 天自动重跑 L2 轨迹测试（检测模型升级导致的 Skill 执行偏差）"
```
