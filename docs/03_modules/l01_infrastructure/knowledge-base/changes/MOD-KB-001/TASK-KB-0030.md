---
task_id: "TASK-KB-0030"
source_blueprint: "MOD-KB-001"
source_section: "§9.15 知识合并冲突三级(L1/L2/L3) + §9.16 知识安全分级四级(S0-S3) + §9.16.1 Session Log写入前脱敏 + §9.17 Track C vs A/B冲突裁决 + §9.18 七项运营健康保障"

title: "知识合并冲突三级策略(L1/L2/L3) + 安全四级自动分级(S0-S3) + SessionLog脱敏 + TrackC裁决 + 七项运营健康保障"
description: |
  实现蓝图 §9.15-§9.18 定义的知识合并/安全/裁决/运营体系：(1)§9.15 知识合并冲突三级策略——L1向量相似度cosine>0.80→DUPLICATE直接拒绝/0.60-0.80→进入L2/≤0.60→非重复正常入库 + L2 Kimi K2.6四向判定SAME_TOPIC(完全同主题→合并到旧KE)/SUBSET(子主题→新KE depends_on指旧KE+旧KE追加child_kes字段)/OVERLAP(部分重叠→生成MERGE_PROPOSAL YAML推§7.7 L2 Owner审批)/DISTINCT(独立→入库) + L3合并执行(旧KE version bump或建子项或审批或独立入库) + ke_merge learn()记录合并事件以学习Owner偏好；(2)§9.16 知识安全四级自动分级——S0 PUBLIC(默认)/S1 INTERNAL(正则检测IP+端口+路径→仅内部session注入MCP对外隐藏body)/S2 RESTRICTED(正则检测API endpoint+config key→不写入ChromaDB向量索引仅SQLite metadata存储)/S3 SECRET(正则sk-/api_key/password/secret关键词+>20字符→拒绝生成KE或自动REDACT替换)；(3)§9.16.1 Session Log写入前自动脱敏——auto-handoff-log.py生成Session Log后S1敏感扫描(复用§9.16四级正则+truffleHog模式AWS_ACCESS_KEY/private_key/connection_string/JWT/OpenAI key)+S2自动脱敏→[REDACTED-SK]/[REDACTED-PW]+S3告警推送Owner，脱敏后写入文件→git_commit。月度Git历史安全扫描cron(每月1日6:00 kb_repo.scan_git_history_for_secrets使用git-secrets/truffleHog模式匹配)；(4)§9.17 Track C Owner偏好 vs Track A/B证据冲突裁决——每周APScheduler cron扫描→ChromaDB cosine>0.60检索相关A/B KE→Kimi K2.6逐条判定ALIGNED/MISALIGNED→冲突简报推Owner(§7.7 L2 HUMAN_GATED)→Owner选择更新偏好(C2 SUPERSEDED写新内容)或坚持(追加override_reason理由入C3)→90d冲突冷却；(5)§9.18 七项运营健康保障——§9.18.1静默期告警(>14d无KE→检查git hooks/scheduler/ChromaDB→附带修复指令推Owner)/§9.18.2一键自检(python -m zephyr.kb --self-test 13项红绿灯：SQLite/ChromaDB/MD一致性/幽灵向量/git hooks/scheduler/重复KE/断链/静默期/Embedding/Reranker/磁盘/KE编号)→输出summary+建议动作/§9.18.3 KE墓碑(ke_tombstones表保留original_ke_id/body_hash/embedding_vector/deletion_reason/superseded_by→G2去重增强cosine>0.85→推Owner)/§9.18.4全生命周期SLA(SLA-BIRTH 90d首次审查/SLA-CHECK 180d定期复查/SLA-DECIDE 365d终局裁决→新KE frontmatter字段lifecycle_sla)/§9.18.5引用活性检查(月度HEAD所有KE body中URL→>30%失效→quality_score×0.85+推Owner复查)/§9.18.6闲时记忆整合(6类后台任务：KO聚类审查/embedding重验/HDBSCAN全量重聚类/图谱连通性/索引预热/墓碑去重预计算→APScheduler低活跃度检测触发→nice(10)优先级)/§9.18.7冲突裁决模式学习(Owner裁决历史累积≥5次→提取模式→>80%同类→SUGGEST自动建议/否则UNCERTAIN保留推送)。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\content_safety_gate.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\merge_conflict.py"
    description: "新建——L1/L2/L3三级合并：cosine判定→Kimi K2.6四向→version_bump/child_kes/MERGE_PROPOSAL/ke_merge learn()"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_security.py"
    description: "新建——S0-S3四级自动正则分级+注入策略(S2无向量/S3 REDACT)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\session_sanitizer.py"
    description: "新建——S1/S2/S3三阶段脱敏→REDACTED→月度git历史扫描cron"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\conflict_arbiter.py"
    description: "新建——每周cron TrackC vs AB扫描→ALIGNED/MISALIGNED→简报推Owner→90d冷却"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ops_health_monitor.py"
    description: "新建——7项运营指标：静默期/自检13项/墓碑/生命周期SLA/引用活性/闲时整合/裁决模式学习"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\reference_monitor.py"
    description: "新建——月度HEAD所有KE body中URL→>30%失效→quality_score×0.85+推Owner(§9.18.5)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\kb\\conflict_learner.py"
    description: "新建——Owner裁决历史≥5次→提取模式→>80%同类→SUGGEST自动建议(§9.18.7)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\merge_conflict.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ke_security.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\session_sanitizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\conflict_arbiter.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ops_health_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\reference_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\conflict_learner.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\ingest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\triage.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§9.15-§9.18 知识合并(三级L1/L2/L3)+安全四级(S0-S3)+脱敏+裁决+七项健康保障"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 15000
timeout_minutes: 50

acceptance_criteria:
  - "merge_conflict.py——L1 cosine>0.80 DUPLICATE/0.60-0.80→L2 + L2 Kimi K2.6 SAME_TOPIC/SUBSET/OVERLAP/DISTINCT + L3 version_bump/child_kes/MERGE_PROPOSAL + ke_merge learn()"
  - "ke_security.py——S0-S3四级正则自动匹配+检测规则(IP/端口/路径/API endpoint/config key/sk-/api_key/password/secret>20字符)→S2无ChromaDB向量+S3 REDACT"
  - "session_sanitizer.py——auto-handoff-log生成后S1/S2/S3三阶段→REDACTED→写入→git_commit→月度cron git-secrets/truffleHog扫描"
  - "conflict_arbiter.py——每周cron TrackC vs AB→ALIGNED/MISALIGNED→简报推Owner→SUPERSEDED/override_reason→90d冷却"
  - "ops_health_monitor.py——7项运营健康：静默期检测/13项一键自检(python -m zephyr.kb --self-test)/ke_tombstones表/SLA生命周期/引用HEAD检查(>30%失效→quality×0.85)/闲时6任务/冲突模式学习>80%→SUGGEST"
  - "reference_monitor.py——月度HEAD扫描所有KE body中URL→>30%失效→quality_score×0.85+推Owner复查(§9.18.5)"
  - "conflict_learner.py——累积≥5次Owner裁决→Kimi K2.6提取模式→>80%同类→SUGGEST自动建议/否则UNCERTAIN保留推送(§9.18.7)"

rollback_instructions: |
  1. 删除 src/zephyr/kb/merge_conflict.py, ke_security.py, session_sanitizer.py, conflict_arbiter.py, ops_health_monitor.py, reference_monitor.py, conflict_learner.py

depends_on: ["TASK-KB-0021"]
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
