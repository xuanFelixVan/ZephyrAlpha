---
module_id: KE-1809----------d-022-16-003
status: active
title: 2.23 Agent行为漂移检测（决策 D-022-16）
category: module_blueprint
---

# 2.23 Agent行为漂移检测（决策 D-022-16）

2.23 Agent行为漂移检测（决策 D-022-16）

> **决策 D-022-16**：引入Agent行为漂移（Prompt Drift + Concept Drift + Data Drift + Goal Drift）的四维检测体系。91%的ML系统会经历性能退化——升级协议必须能检测并响应AI自身的行为退化。
> **对标**：Comet Prompt Drift Observatory + Maxim AI Drift Prevention + IBM Agentic Drift Research。

```yaml
agent_drift_detection:
  # Agent漂移比规则漂移(#41)更宽泛——不只是规则变更，而是模型行为退化
  drift_types:
    prompt_drift:
      definition: "模型对相同系统提示词的解释随版本更新/上下文积累而变化"
      symptoms: ["工具调用错误", "推理步骤缺失", "参数构造不一致"]
      detection: "定期对比相同输入→输出语义相似度(cosine<0.85→告警)"
    
    concept_drift:
      definition: "输入输出关系随环境变化而改变——如市场条件改变导致风险评估行为漂移"
      detection: "Sliding window性能指标对比(当前周 vs 基准月)"
    
    data_drift:
      definition: "输入数据分布变化——市场数据格式/频率/范围改变影响AI判断"
      detection: "输入特征分布KS检验(p<0.01→数据漂移告警)"
    
    goal_drift:
      definition: "Agent在自我迭代中逐渐偏离原始目标——如为'效率'牺牲安全性"
      symptom: "同一任务类型的人工推翻率缓慢上升(周环比>5%)"
      defense: "核心目标const声明+定期目标一致性审计"

  drift_to_escalation:
    SLI_drift_link: "指标超过漂移阈值→自动创建升级事件"
    severity_mapping:
      prompt_drift_high: P0  # 直接影响代码质量
      concept_drift_medium: P1
      data_drift_low: P2
      goal_drift: P0  # 最高优先级——目标漂移是最危险的退化
    
    auto_correction:
      prompt_drift: "自动重新加载Baseline系统提示词+回滚到已知良好版本"
      concept_drift: "自动重新训练/校准置信度模型"
      data_drift: "通知Owner调整数据管道"
```

---
