---
module_id: KE-module_blu-9_6_incident___skill_postmorte-003
title: 9.6 Incident → Skill Postmortem & Continuous Improvement
category: module_blueprint
---

# 9.6 Incident → Skill Postmortem & Continuous Improvement

9.6 Incident → Skill Postmortem & Continuous Improvement

```yaml
skill_postmortem:
  description: "AI Agent 事故的事后复盘必须触发对应的 Skill 更新——对标 Anthropic Claude Code 质量事故复盘标准"

  incident_classification:
    severity_S0: "生产数据丢失/破坏——立即 kill switch + 全量回滚 + 24h 内发布复盘报告"
    severity_S1: "服务降级（功能不可用但未丢数据）——48h 内复盘 + Skill patch"
    severity_S2: "质量问题（效率/准确性下降）——7 天内分析与 Skill 优化"
    severity_S3: "边缘案例——纳入 regression test suite 防止复现"

  postmortem_to_skill:
    S0_S1_flow:
      step1: "事故 Timeline 重建——Audit Trail 中提取从 Skill 加载到事故的完整工具调用链"
      step2: "根因分类——是 Skill 指令问题 / 蓝图错误 / 代码 Bug / 平台 Bug？"
      step3: "Skill 关联——根因是 Skill 问题 → 生成 Skill fix PR → 人工批准 → Canary 部署"
      step4: "Regression Test 扩展——事故场景加入该 Skill 的 L2 轨迹测试（永久化）"
      step5: "Knowledge Distillation——事故模式总结为一条 KE（Knowledge Entry）→ 存入 Knowledge Base"

    incident_to_skill_field:
      description: "Skill 的 frontmatter 中新增可选的 incident 追踪字段"
      fields:
        last_incident_date: "最近一次与此 Skill 相关的事故日期"
        incident_count: "历史事故总数"
        linked_incidents: "[incident_ids]"
        incident_driven_changes: "由事故触发的 Skill 修改次数"

  feedback_amplification:
    description: "一次事故可以同时触发多个 Skill 的联动修复"
    example: "数据库 specialist 的错误导致门禁丢失 → 触发 database specialist fix + gate specialist audit rule fix + governor on-call protocol fix"
```
