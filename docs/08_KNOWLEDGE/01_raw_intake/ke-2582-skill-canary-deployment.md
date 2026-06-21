---
module_id: KE-2487----000
status: active
title: 8.4 Skill Canary Deployment & A/B Testing（决策 D-019-09）
category: module_blueprint
---

# 8.4 Skill Canary Deployment & A/B Testing（决策 D-019-09）

8.4 Skill Canary Deployment & A/B Testing（决策 D-019-09）

> **决策 D-019-09（新增）**：Skill 的新版本不应直接替换旧版本——必须通过 Canary 部署逐步切换。新 Skill 先在 20% 的会话中灰度生效，观察门禁通过率无衰减后再全量切换。
>
> **决策依据**：
> - Agent 系统的非确定性意味着回归测试不能 100% 保证 Skill 升级不会引入问题
> - 金融/量化场景（ZephyrAlpha 的定位）对稳定性的要求极高——Skill 的 breaking change 可能导致因子计算错误

```yaml
skill_canary:
  description: "Skill 的灰度部署与 A/B 测试协议"

  deployment_channels:
    stable: "所有会话的默认通道——100% 流量"
    canary: "20% 会话的测试通道——新 Skill 版本先行验证"
    dev: "开发者的个人测试通道——100% 流量只对 Owner 的会话"

  canary_lifecycle:
    phase_1_launch:
      action: "新 Skill 版本部署到 canary 通道"
      duration: "≥ 24 小时或 ≥ 10 个有效会话"
      success_criteria: "Canary 通道的 gate_pass_rate ≥ stable 通道的 gate_pass_rate"

    phase_2_ramp:
      action: "Canary → 50% 流量"
      duration: "≥ 48 小时或 ≥ 20 个有效会话"
      rollback_trigger: "gate_pass_rate 下降 ≥ 5% 即自动回滚到 stable 版本"

    phase_3_full:
      action: "Canary → stable 通道（100% 流量）"
      precondition: "Canary 的 gate_pass_rate + test_pass_rate 均 ≥ stable"
      post_full_monitoring: "全量后持续监控 7 天——异常自动回滚"

  ab_testing:
    description: "对比两个 Skill 版本的效果——用于优化 Skill 指令的措辞"
    test_config:
      control: "Skill v1.0（现行版本）"
      treatment: "Skill v1.1（优化后的版本）"
      split: "50:50 随机分配"
      metrics:
        primary: "gate_pass_rate（门禁通过率）"
        secondary: "token_efficiency（完成相同任务消耗的 token 数）"
        guardrail: "test_pass_rate（必须 ≥ control 否则终止实验）"
      duration: "≥ 200 个有效会话"
      analysis: "统计显著性检验（Welch's t-test, p < 0.05）"
```
