---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-S01
name_zh: 会话冷启动与开班检查
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-S01
skeleton: docs/_archive/_working_cleared/map_build/fig11_delivery/00_skeleton.md
---

# D11-S01 会话冷启动与开班检查

## 1. 定义
会话车道第一环节：对话启动后、任何写操作前的开班检查序列。决策问题=「本会话该启动吗？启动前环境/守卫/隔离施工/能力反查就位了吗？」执行体=phase_manager.session_startup（对标 K8s Init Container / 航空 pre-flight checklist，quick=True 约 3s 快检子集 / quick=False 约 15s 全量）。

## 2. 六向台账

### 2.1 输入面
- 冷启动序列指令真源：`AGENTS.md` §0（RULE-ENV/RULE-GUARDIAN/RULE-WORKTREE/RULE-CAPABILITY-LOOKUP/RULE-DEPGRAPH/RULE-REGISTRY/RULE-SSOT 七步序）
- IDE 注入规则：`.trae/rules/project_rules.md`
- 检查项注册面：`src/zephyr/governance/ops_governance/phase_check_registry.py`（16 项 check_*：会话管理器/连续性/锁协议/蓝图/密钥泄漏/临时文件扫描等）

### 2.2 输出面
- 会话注册表（旧单表）：`.runtime/session_registry.json`（2026-10-15 实查 43329B 在盘可解析）
- 会话注册表（S4-D 分片新真源）：`.runtime/session_registry/<sid>.json`（实查 3 片在盘，2026-09-30 起 per-session 分片+旧表双写迁移窗）
- 开班检查结果 dict（ready/green/yellow/red/checks/next_action）返回调用方
- 能力反查审计面：`.runtime/lookup_audit/`（实查 918 件在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-S01`（机生，generator=scripts/governance/d5_architecture/generators/generate_dev_delivery_map.py，generated_at=2026-10-15T18:22:02+08:00，wiring_status=wired/production）
- 人工语义层契约：`docs/_archive/_working_cleared/map_build/fig11_delivery/00_skeleton.md` §1 D11-S01 + 作业簿 `01_会话启动与worktree池.md`

### 2.4 代码模块
- `src/zephyr/governance/ops_governance/phase_manager.py:248` `def session_startup(quick=True)`（实读：fast checks 引 phase_check_registry 16 检查器）
- `scripts/record_session_start_commit.py`（实存在盘，开班登记脚本）
- `src/zephyr/governance/audit/reuse_scan.py`（实存在盘，裁定#480 C-2 同类半成品预查，三源 fail-open 纯只读）
- 注：图内 source_anchors 行锚（:248）与现值一致。

### 2.5 门禁约束
- 本节点 gate_refs=[]（图面无挂门）；约束来自车道级 laws（正门唯一/队列是正门）与 AGENTS.md §0 硬序（reaper 计划任务不存在=禁写操作）
- 门禁双册挂靠：`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml`（total_gates=107）/`gate_registry.yaml`（total_gates=191）——本环节不直接消费

### 2.6 自动化触发
- 触发源=会话对话启动（人工/agent 依宪法 §0 执行）；无常驻 daemon
- reuse_scan 预查钩子活体证据在图（2026-10-04 start 输出「reuse_scan: 未提供 task_files，跳过预查」）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | AGENTS.md §0+phase_check_registry 16 检查器实存 |
| 输出面 | pass | session_registry.json 43329B+分片目录双轨在盘 |
| SSOT真源 | pass | 图节点 wired/production 与代码一致 |
| 代码模块 | pass | 三锚点文件全实存 |
| 门禁约束 | pass | 无挂门如实登记；宪法 §0 硬序兜底 |
| 自动化触发 | warn | store_refs 仍指旧单表 .runtime/session_registry.json；2026-09-30 S4-D 治本已把主真源迁 .runtime/session_registry/ 分片（session_concurrency.py:8 INVARIANTS），图注未跟 |

## 4. 缺口与建议
- 【账务漂移】S4-D 分片存储已 40 天，图 store_refs/骨架仍以旧单表为登记面；建议总包回写骨架 S01 行 store_refs 双轨并列（新真源在前）。
- 【迁移窗尾】旧表双写副本 43KB 仍在增长态，建议确认迁移窗退出条件（回退手柄 env ZEPHYR_SESSION_REGISTRY_SHARDS=0 保留）并设清理裁定。
