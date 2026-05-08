---
module_id: KE-module_blu-2_4_ct-script-kb-001-003
title: 2.4 CT-SCRIPT-KB-001：脚本系统 ↔ 知识库
category: module_blueprint
---

# 2.4 CT-SCRIPT-KB-001：脚本系统 ↔ 知识库

2.4 CT-SCRIPT-KB-001：脚本系统 ↔ 知识库

```yaml
contract: CT-SCRIPT-KB-001
title: "脚本 Finding → 知识条目入库"
systems:
  - role: producer
    name: script_system
    path: "scripts/governance/"
    blueprint: "MOD-INF-005"
  - role: consumer
    name: knowledge_base
    path: "src/zephyr/kb/"
    blueprint: "MOD-KB-001"

data_flow:
  direction: "script → KB"
  mapping:
    - finding_severity: "MEDIUM"
      action: "自动创建 KE 草稿 → G1 Ingest → G2 Triage"
      ke_template: |
        title: "{finding.dimension}: {finding.message[:80]}"
        domain: "governance"
        tags: ["auto-generated", "{finding.dimension}", "finding-to-ke"]
        source_finding_id: "{finding.id}"
    - finding_severity: "CRITICAL|HIGH"
      action: "不自动创建KE——CRITICAL/HIGH 走任务卡流程（CT-ORC-SCRIPT-001）"
    - finding_severity: "LOW|INFO"
      action: "不入KB——仅记录到审计日志"
    - phase_C5_knowledge: |
        脚本系统 C5 知识沉淀阶段:
        CRITICAL/HIGH Finding 修复完成 → 提取经验教训 → G3 Analyze →
        人工确认后 → G4 Activate → KE 进入活跃知识库

quality_gate:
  - auto_generated_KE 必须经过 G2 Triage 人工确认 → 不得自动 G4 Activate
  - KE 来源字段标注 `source: "script_system_C4"`

ai_prompt: >
  你是CT-SCRIPT-KB-001的AI agent。当脚本系统产出MEDIUM severity Finding时：
  (1) 自动创建KE草稿，status=DRAFT，不要直接G4 Activate——必须经过G2 Triage人工确认；
  (2) KE的source字段必须标注"script_system_C4"——用于审计追溯；
  (3) CRITICAL/HIGH Finding不在此处理——走CT-ORC-SCRIPT-001创建OPS任务卡；
  (4) LOW/INFO Finding不入KB——仅记录审计日志，不要浪费KB存储；
  (5) C5阶段的知识沉淀（修复完成的CRITICAL/HIGH）需要人工确认后走G3→G4路径，不要全自动激活。

telemetry:
  metrics:
    - {name: "finding_to_ke_auto_create", type: counter, labels: [severity, dimension]}
    - {name: "ke_auto_create_latency_s", type: histogram, buckets: [1,5,10,30]}
    - {name: "c5_knowledge_extract_count", type: counter}
  traces:
    required_spans: ["finding_emit", "ke_draft_create", "ke_g1_ingest"]
```
