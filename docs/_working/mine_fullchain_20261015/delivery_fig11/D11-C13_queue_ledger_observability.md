---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C13
name_zh: 队列台账与运维观测
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C13
---

# D11-C13 队列台账与运维观测

## 1. 定义
提交车道第十三环节：观测与运维面。决策问题=「队列健康可观测吗？TTL、告警阈值与堵点账本各归谁守？」机制=四态目录协议（_STATES=pending/processing/done/dead）+queue_health 只读快照+dead 积压告警（阈值真源=告警阈值册 THD-ALERT-003：50 项+冷却 6h；THD-ALERT-007 belt daemon 离线>24h）+done TTL 清理（dead 永不自动清理不变量）+堵点账本 jsonl+归属核实纪律（git log -1 --name-only）。

## 2. 六向台账

### 2.1 输入面
- 四态目录实态：`.runtime/commit_queue/{pending,processing,done,dead}`（2026-10-15 只读实测：pending=53/processing=19/done=812/dead=378）
- 阈值册：`docs/01_policies_and_standards/_registry/catalogs/alert_threshold_registry.yaml`（THD-ALERT-003/004/007 实读在册）

### 2.2 输出面
- health 快照+告警冷却态：`.runtime/commit_queue/health_alert_state.json`（实查在盘）
- 堵点账本：`.runtime/audit/bottleneck_ledger.jsonl`（实查在盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C13`（wired/production，machine_facts.queue_state_dirs 四态计数=图快照 3/2/798/318）
- 骨架：07_对账观测与紧急车道.md；宪法 §2.6（队列项 dead 当日四态分诊不隔夜）

### 2.4 代码模块
- `scripts/commit_queue.py:179` `_STATES`+`:3567` `def cleanup_done(`+`:4228` `def queue_status(`+`:4552` `def queue_health(`（图记 :166/:1719/:1777，行锚漂移大）
- CLI 七子命令实读：enqueue/status/drain/requeue/cleanup/dead-archive/health（:5446-5553）+bootstrap-fill
- 复核纪律：health --no-alert 只读（禁 status/drain 触发自举排空——本车道实测遵守）

### 2.5 门禁约束
- 不变量：done/ 按 qid 唯一不双落、每项终有四态其一不丢失（commit_queue.py 头注释实读）；dead/ 永不自动清理

### 2.6 自动化触发
- health 即时快照；告警冷却态自动维护；done TTL 定期清理（cleanup_done 默认 N 天）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 四态目录+阈值册实存 |
| 输出面 | warn | 观测出口齐在；但实测 dead=378>THD-ALERT-003 阈值 50 且 pending=53 高水位——健康面亮黄，告警冷却态在用（非无告警） |
| SSOT真源 | pass | 图/骨架/阈值册一致（快照计数差异=时点差非漂移） |
| 代码模块 | pass | 四态协议+CLI 面实存 |
| 门禁约束 | pass | 三不变量在码 |
| 自动化触发 | pass | 快照/冷却/TTL 自动 |

## 4. 缺口与建议
- 【即时行动项】dead=378 件积压超阈值 7 倍：按宪法 §2.6 触发当日四态分诊（dead-archive --content-level 内容级判定，禁按条数估）；pending=53 建议观察排空速率是否跟得上（C09 k=4 池在飞 19）。
- 【建议】health 输出建议补三指标：blob 孤儿数、rerouted 累计、per-worker 深度（C08/C12/C09 三处建议的汇聚点）。
