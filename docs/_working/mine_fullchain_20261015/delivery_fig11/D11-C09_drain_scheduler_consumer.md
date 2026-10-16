---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C09
name_zh: 排空调度与消费端
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C09
---

# D11-C09 排空调度与消费端

## 1. 定义
提交车道第九环节（全图 4 个 partial 之一）：队列消费调度。决策问题=「这条队列项由谁消费？lease 僵尸回收、通道路由与池并发怎么定？」机制=SerializerLease TTL+僵尸 PID 回收；channel_key_for_files 通道路由（hot/shared 单通道）；k=4 池并行排空（drain_queue_pool+池级单 lease+单心跳线程，投机并行验证+串行落地）；belt daemon 事件触发自举补位。

## 2. 六向台账

### 2.1 输入面
- pending 队列（53 件实测）
- 池配置：thresholds commit_queue_landing_pool_workers（k=1=legacy 降级）
- 自举输入：status/drain CLI 触发+belt daemon 心跳自举

### 2.2 输出面
- processing 件+池工位：`.runtime/commit_queue/processing`（19 件实测在飞）+`.runtime/commit_queue/worktrees/`（w0-w3 实查在盘）
- 守护心跳：`.runtime/commit_queue/belt_daemon.heartbeat`（**mtime=2026-10-15 20:02 当日新鲜**，消费端活着）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C09`（build_status=built、wiring_status=partial、red_reason=unwired——partial 判定的现行依据需总包复核，见缺口）
- 骨架：06_入队排空与真落盘.md

### 2.4 代码模块
- `scripts/commit_queue.py:240` `def channel_key_for_files(`+`:1377` `class SerializerLease(`+`:2353` `def drain_queue(`+`:2607` `def try_bootstrap_drain(`（图记 :207/:769）
- `scripts/governance/commit_queue_landing.py:4079` `def drain_queue_pool(`（图记 :1938，行锚漂移 +2141——k=4 池主体现已落在 landing 侧）
- `src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`（实存在盘）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=laws 直连与队列不混抢+池级路径锁（同路径项门禁段前串行化防跨 session claim 冲突）

### 2.6 自动化触发
- belt daemon 事件触发自举（禁 cron 合四要素）；僵尸 lease PID 回收自动；status/drain 显式触发自举排空

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | pending+池配置+自举输入实存 |
| 输出面 | pass | processing 19 件+w0-w3+心跳当日新鲜 |
| SSOT真源 | warn | 图记 partial/unwired 与「池/守护全在产」的实况不符——2026-09-25 后 k=4 池与 belt daemon 大量演进（landing 行锚漂移 +2141），partial 红因待总包复核回写 |
| 代码模块 | pass | 五锚点实存 |
| 门禁约束 | pass | 路径锁+不混抢在码 |
| 自动化触发 | pass | daemon 心跳当日活跃 |

## 4. 缺口与建议
- 【账务复核】C09 的 partial 判定疑似过时（消费端全链活着），建议总包按「图11 还差的活」清单复核 4 个 partial 的现状（C09/C10 同批）。
- 【水位建议】processing=19 对 k=4 池偏高（每工位积压约 5 项），建议 health 输出 per-worker 队列深度。
