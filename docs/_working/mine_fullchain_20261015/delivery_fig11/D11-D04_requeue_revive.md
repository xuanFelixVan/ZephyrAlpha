---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-D04
name_zh: requeue 复活链路
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D04
---

# D11-D04 requeue 复活链路

## 1. 定义
死信车道第四环节（反馈环起点 D04→C08）：死信复活。决策问题=「这条死信还能救吗？requeue 基于当前工作区重建快照后原项留什么痕？」机制=requeue_dead_item：先读 dead_reason 修因（宪法 §2.6）→基于当前工作区重建快照→新 qid 排 FIFO 队尾（回 C08 入队口）→原项留 requeued 指针（dead/{qid}.requeued.new_qid 与新件 meta.requeued_from 双向）；attempts>0 件不吸收进 C1 合批（不拖新内容陪葬）。

## 2. 六向台账

### 2.1 输入面
- dead 项+修正后的处置意图（修因后再 requeue 是标准处置）
- 当前工作区状态（重建快照基底）

### 2.2 输出面
- 新 pending 项（新 qid）；原 dead 项双向指针
- 活体样例：图记 dead/0031.requeued→0055 双向 trace（09-25 复核成立）；**2026-10-15 复核 dead/ 内 *.requeued 留痕=0 件**——样例已随清零战役轮换袋收走（证据轮换非断链）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D04`（wired/production；feedback_loops 第一条 D04→C08 在册）
- 骨架：08_死信全链.md；66 号 §6.4 语义（CLI help 实读：「死信取回重入队：基于当前工作区重建快照，新 qid 排 FIFO 队尾」）

### 2.4 代码模块
- `scripts/commit_queue.py:3222` `def requeue_dead_item(`（图记 :1387，行锚漂移 +1835）
- CLI：`:5487` `p_rq = sub.add_parser("requeue", ...)`（实读）
- SV 病历：B doctor 三铁闸（casebooks 在册）

### 2.5 门禁约束
- 图面 gate_refs=[]；约束=「死信也要死得明白」的逆面：复活必须留双痕（新 qid 可溯源自旧项）+修因前置（读 dead_reason）

### 2.6 自动化触发
- CLI 显式触发（人工/agent 修因后）；入队后走标准排空

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | dead 项+修因流程实存 |
| 输出面 | warn | 双向指针代码在位；活体样例经轮换=0，短期不可只读复核复活实弹 |
| SSOT真源 | pass | 图/骨架/66 号语义一致 |
| 代码模块 | pass | 函数+CLI 实存（行锚漂移 +1835） |
| 门禁约束 | pass | 双痕+修因前置在案 |
| 自动化触发 | pass | requeue→pending 自动回环 |

## 4. 缺口与建议
- 【证据留存】同 C12：requeue 双向 trace 建议沉淀滚动台账（requeue_ledger.jsonl），轮换袋不作为唯一证据面。
- 【建议】B doctor 三铁闸（判定/修因/复核）目前以病历约束存在，建议把「修因记录」结构化为 requeue 必填参数（--fix-note），无注记拒绝复活。
