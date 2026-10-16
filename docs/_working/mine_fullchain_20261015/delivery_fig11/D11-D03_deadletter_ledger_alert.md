---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-D03
name_zh: 死信台账联动与告警
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D03
---

# D11-D03 死信台账联动与告警

## 1. 定义
死信车道第三环节：出域联动。决策问题=「这条死信在任务台账上有标吗？告警发出去了吗？」机制=_notify_task_board_dead_letter→scripts.task_board.tag_dead_letter（metadata 承载不改表）；watch task 固定 id=T-QUEUE-DEADLETTER（幂等自建）；requeue 同步标注；告警走 C13 积压告警通道（THD-ALERT-003/004）；task_board=任务治理域出域引用不吸收；联动异常吞掉不阻断排空。

## 2. 六向台账

### 2.1 输入面
- 死信事件（D01 分流时同步触发，:2246 调用点）
- watch task id：`scripts/commit_queue.py:270` `_DEADLETTER_WATCH_TASK_ID = "T-QUEUE-DEADLETTER"`（幂等自建注记实读）

### 2.2 输出面
- task_board 死信标注（metadata 承载）：`scripts/task_board.py:332` `def tag_dead_letter(`
- 告警：C13 通道（health_alert_state.json 冷却态）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D03`（wired/production）
- 骨架：08_死信全链.md；边界=task_board 出域（图层 handoff_zh：D03 出域到 task_board 引用不吸收）

### 2.4 代码模块
- `scripts/commit_queue.py:1538` `def _notify_task_board_dead_letter(`（图记 :930，行锚漂移 +608）+`:2246` 死信分流调用点（图记 :1349）+`:116` 协议注释（经 notify→tag 把死信上账）
- `scripts/task_board.py:332` tag_dead_letter（实存在盘）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=联动失败不阻断排空（可用性优先，异常吞掉+留痕）

### 2.6 自动化触发
- 死信产生即自动联动；requeue 时同步标注双向

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 死信事件+watch task id 实存 |
| 输出面 | pass | tag 接口+告警通道实存 |
| SSOT真源 | pass | 图/骨架一致，出域边界清晰 |
| 代码模块 | pass | 双侧函数实存（行锚漂移 +608） |
| 门禁约束 | pass | 不阻断排空语义在码 |
| 自动化触发 | pass | 事件触发全自动 |

## 4. 缺口与建议
- 【观测建议】tag 联动成功率无独立计数（异常吞掉静默），建议加一条 jsonl 计数防「联动长期失败无人知」。
- 【边界维持】task_board 侧字段演化不回流本图（出域引用不吸收）——维持现边界即可，无需动作。
