---
task_id: "TASK-INF-0224"
source_blueprint: "MOD-INF-011"
source_section: "§12.3 Phase 4 vms_health_check.py cron 脚本 + §10.4 R14/R15 迁移零中断验证"

title: "VMS 运维基础设施收尾——cron 健康检查 + 迁移零中断 SLA 守夜人 + @api_version 合约护栏"
description: |
  收尾 VMS 的全部运维基础设施——连接 §12.3 Phase 4 和 §10.4 迁移风险缓解：
  1. vms_cron_monitor.py 最终版——集成 Phase 1-4 所有运维能力：
     - TTL 自动清理（R5/R8）
     - HNSW auto-compaction（R5）
     - SQLite WAL checkpoint + VACUUM + ANALYZE（V424）
     - Snapshot 自动备份 + cleanup 旧备份（R4）
     - 异常告警日志 + matrix REPORT（§12.5 最后 real-time 效果监控）
  2. 迁移零中断 SLA 守夜人（R14/R15 缓解 + V426）：
     - 轮询 kb/ 旧 Collection 和 VMS Collection 数据一致性（长 polling）
     - BridgeLayer 双读监控——双路径请求量/错误率/延迟 P95 → 对比趋势
     - 自动切换备选路径：双读→仅读 VMS 切换条件（双读 30 天无错误 + 所有 consumers 签收）
  3. @api_version 护栏激活——G1 门禁级版本冲突检测：
     - CE/Orc/FLE/KB/SessionManager 调用 VMS 时的 API 版本合约检查
     - 版本不匹配 → 不允许 context build（拒绝静默 construct）
  本任务卡是 VMS 施工的"最后一张任务卡"——代表蓝图 0.7.0 全部 scope 的运维层闭合。
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_cron_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\index_health_monitor.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\vms_cron_monitor.py"
    description: "最终版——7 步检查链(TTL+WAL+VACUUM+compaction+snapshot+审计+告警) + report输出"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    description: "追加零中断 SLA 守夜人——migration_watcher():双读指标收集+自动切换条件检查"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"
    description: "追加 @api_version gate——public API methods 均被 @api_version 包裹"

allowed_touch:
  - "D:\\ZephyrAlpha\\scripts\\governance\\vms_cron_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\in_process_vector_memory.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\**\\*.py"

applicable_rules:
  - module_id: "GOV-TASK-005"
    section: "全篇"
    reason: "关闭三步法——最终运维验收"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——运维指标 reporting 模型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§12.3 Phase 4(/§10.4 R14+R15) + §13.8 V423-V426——运维自动化的完整运维 checklist"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\vector_memory\\bridge_layer.py"
    reason: "当前桥梁实现——追加零中断守夜人 migration_watcher"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
  - "M4"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "vms_cron_monitor.py 执行 start → 输出 7-step health report to stdout + log file"
  - "TTL 清理: execution_traces > 30d → deleted(≥0 actual rows) / code_context > 90d → deleted / session_snapshots > 90d → deleted"
  - "WAL checkpoint: PRAGMA wal_checkpoint(TRUNCATE) 成功执行——无 SQLite error"
  - "VACUUM + ANALYZE: 每日定执行——reclaim disk space(without破坏数据)"
  - "compaction: HNSW index compaction 缩减 index size——post-compaction 大小 < pre-compaction * 0.9"
  - "snapshot: timestamped backup successfully stored in _snapshots/——verify by hash"
  - "bridge_layer.migration_watcher(): 最近 30 天双读请求数/错误率/延迟 P95 → 两条路径 trend comparison output"
  - "bridge_layer migration_watcher 自动切换条件：双读 30 天 0 error + CE 签收→自动切为 only VMS"
  - "@api_version 门禁冲突检测——version mismatch→禁止 context build"

rollback_instructions: |
  1. vms_cron_monitor 清除错误数据 → 从 _snapshots/ 恢复最新完整备份
  2. migration_watcher 自动切换 but VMS 不如 kb/ → 手动回退 bridge_mode=kb_only
  3. @api_version 冲突过于严格阻止正常 build → VMS_SKIP_API_GATE=1 临时跳水
  4. 逐步回滚——每一 component 有独立 feature flag 可禁用

depends_on:
  - "TASK-INF-0221"
  - "TASK-INF-0222"
  - "TASK-INF-0223"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "data"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
