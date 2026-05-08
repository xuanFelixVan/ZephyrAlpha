---
task_id: "TASK-SYS-0018"
source_blueprint: "SYS-MASTER-001"
source_section: "§24 会话生命周期 + §25 环境管理 + §36 人机带宽优化"

title: "会话生命周期5状态 + 5环境(DEV/STAGE/UAT/PAPER/LIVE) + Human-AI带宽6维优化 体系"
description: |
  将 SYS-MASTER-001 §24 会话生命周期 + §25 环境管理 + §36 Human-AI 带宽优化三合一落地。
  §24: 5 状态——RUNNING→IDLE→INTERRUPTED→TIMED_OUT→CLOSED。
  每状态 valid_transitions[] + ttl_seconds + checkpoint_on_enter。
  §25: 5 环境——DEV(127.0.0.1)/STAGE(120.26.xxx)/UAT/PAPER(paper trading)/LIVE(production)。
  每环境 config_path/.env变量/数据库/broker_connection。
  §36: Human-AI bandwidth 6维——interrupt_overhead/context_switching/decision_fatigue/
  communication_latency/attention_span/cognitive_load→自动评分→建议任务粒度→focus_shift门禁。
  本卡搭建 session_lifecycle.py + environment_manager.py + bandwidth_optimizer.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\session_lifecycle.py"
    description: "§24 5状态——RUNNING/IDLE/INTERRUPTED/TIMED_OUT/CLOSED 状态机+TTL+checkpoint"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\environment_manager.py"
    description: "§25 5环境——DEV/STAGE/UAT/PAPER/LIVE——config/env/DB/broker+CLI `zephyr env switch`"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\bandwidth_optimizer.py"
    description: "§36 6维 bandwidth评分——自动建议任务粒度+focus_shift门禁"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\session_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\environment_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\bandwidth_optimizer.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§24 5状态会话 + §25 5环境(DEV→LIVE) + §36 Human-AI带宽6维"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 50

acceptance_criteria:
  - "SessionState 枚举 5 成员——每状态 valid_transitions[]+ttl_seconds+checkpoint_on_enter"
  - "SessionManager.transition(state)→验证 transition 合法性→更新 state+checkpoint"
  - "Environment: name/env_file/.env_vars/db_conn/broker_conn——5 env instant"
  - "CLI: `zephyr env switch {DEV|STAGE|UAT|PAPER|LIVE}`——LIVE=safety confirm"
  - "BandwidthScore 6维→normalize→composite→recommend(task_granularity/focus_shift_interval)"

rollback_instructions: |
  git rm src/zephyr/governance/session_lifecycle.py environment_manager.py bandwidth_optimizer.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0009"
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
