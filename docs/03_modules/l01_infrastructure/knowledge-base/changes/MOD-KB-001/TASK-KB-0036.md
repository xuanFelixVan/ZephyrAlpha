---
task_id: "TASK-KB-0036"
source_blueprint: "MOD-KB-001"
source_section: "§17 已知风险与缓解(R1/R2/R3/R4) + §18 后果"

title: "R1-R4 四项风险缓解措施实现——对齐 §17 真实风险表 + 后果管理清单落地"
description: |
  实现蓝图 §17 定义的四项风险缓解措施（逐风险对齐 §17 风险表）：
  (1) R1 KE 质量退化（概率中/影响高）——长期积累导致低质量条目增多——缓解措施：G1-G5 五门禁全链路质量审查（G1 格式校验→G2 分类+去重→G3 深度评估+矛盾检测→G4 状态流转+向量化→G5 质量门控）+ 定期质量审查（weekly） + 使用率淘汰机制（adoption_count=0 超30d→推Owner降级）。此风险由 TASK-KB-0011（G1-G5门禁验证增强）和 TASK-KB-0016（Sentinel 1 死知识检测）共同缓解。
  (2) R2 知识库膨胀（概率高/影响中）——KE+Kd+KO 条目增长超出存储/检索预算——缓解措施：TTL 机制（half_life_days 自动衰减）+ compaction 定期压缩沉睡 KE + 冷热分层（in_memory→SQLite→ChromaDB 三层逐级倾斜）。此风险由 TASK-KB-0040（知识衰减模型）和 TASK-KB-0023（容量预估监控）共同缓解。
  (3) R3 检索精度不足（概率中/影响中）——纯向量语义检索在专业领域召回率偏低——缓解措施：混合检索（向量语义 70% + BM25 字面 30%）+ FTS5 关键词精确匹配 + Cross-Encoder 重排序。此风险由 TASK-KB-0039（三路索引检索）和 TASK-KB-0012（两阶段检索+重排序）共同缓解。
  (4) R4 知识冲突（概率低/影响高）——TB-TA 分类不一致/多人贡献产生冲突条目——缓解措施：provenance 溯源追踪（每条 KE 可追溯到源文档） + 四模型审计跨模型冲突检测 + 人工仲裁 Owner 裁决。此风险由 TASK-KB-0026（溯源追踪+依赖级联）和 TASK-KB-0013（四模型审计流水线）共同缓解。

  §18 后果——记录施工完成后的正面预期（知识可复用+减少重复问答+AI session 效率提升）和负面风险（过度依赖 KE→忽略源代码/模型幻觉传播到下游 session）——consequence-checklist.md 逐项标注触发条件和当前状态。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\risk-mitigation-status.md"
    description: "新建——R1-R4 风险缓解措施状态——逐R标注缓解任务ID+当前状态"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\consequence-checklist.md"
    description: "新建——§18 后果管理清单——5项严重后果的当前状态+触发条件"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\risk-mitigation-status.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\consequence-checklist.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\08_knowledge\\**\\*.md"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§17 四项风险 + §18 后果——全量缓解追踪"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "risk-mitigation-status.md——R1(质量退化)/R2(膨胀)/R3(精度不足)/R4(冲突) 四项各对应缓解任务链接——逐R标注缓解覆盖率"
  - "R1 缓解确认：G1-G5五门禁全部28项检查 IMPL status≥90% + Sentinel 1 死知识检测 30d 触发正常"
  - "R2 缓解确认：decay_model.py 半衰期公式正确+ capacity_monitor ChromaDB<75%阈值"
  - "R3 缓解确认：refine_search() 三路并发（ChromaDB+FTS5+标签）—RRF 融合—recall@10 CR≥0.70"
  - "R4 缓解确认：knowledge_provenance.py溯源链可追溯源文档 + 四模型审计冲突检测 ≥2 model disagree时 push 人工仲裁"
  - "consequence-checklist.md——5项正面+负面后果的 触发条件+当前状态+Owner notes"

rollback_instructions: |
  1. 删除 risk-mitigation-status.md, consequence-checklist.md

depends_on: ["TASK-KB-0011", "TASK-KB-0012", "TASK-KB-0013", "TASK-KB-0016", "TASK-KB-0023", "TASK-KB-0026", "TASK-KB-0039", "TASK-KB-0040"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
