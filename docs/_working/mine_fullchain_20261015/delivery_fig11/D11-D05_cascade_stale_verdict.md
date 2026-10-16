---
ttl: task_bound
working_doc_type: fig11_step_ledger
map_node: D11-D05
name_zh: 级联失效判定（cascade_stale）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-D05
---

# D11-D05 级联失效判定（cascade_stale）

## 1. 定义
死信车道第五环节（全图 4 个未接线节点之一——**本车道复核：图判已过时**）：依赖声明有效性判定。设计语义=项 X 落盘后扫 pending：depends_on 含 X.qid 或 base_head/base_blob vs 当前 HEAD 仍适用→清标放行；不适用→dead_reason=cascade_stale 死信候选（不消耗 landing）；BaseException 面不涉。special_branches 第 2 条（图顶层）。

## 2. 六向台账

### 2.1 输入面
- landed_index（本轮落地序 qid→base_head）
- pending 项依赖声明：meta.depends_on+base_head/base_blob（**QUEUE-04 后由 landing resolve_base_blobs 真填充**，landing :2101/:4925）

### 2.2 输出面
- 级联标记：pending 项 dead_reason=cascade_stale（不消耗 landing）
- 活体证据：图记 09-25 dead/ 内 cascade_stale=10 件；2026-10-15 复核=0 件（10-13/10-14 两轮清零战役轮换收走）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-D05`（build_status=built、wiring_status=**unwired_slot_hollow**、red_reason=unwired；机生旧证据=「base_blob 恒 None＝重校验器结构空转」）
- **过时判定**：commit_queue.py:1238/:1256 注释明载「B 段填充接通（QUEUE-04）：调用方经 resolve_base_blobs 取 base_head 树上 git blob sha 入袋」；:984-989 docstring 自述「此前 base_blob 恒 None＝结构空转」为历史；:1845-1876 重校验器已真比对（base_blob 非空而 head_reader 缺失→fail-closed 判不适用）

### 2.4 代码模块
- `scripts/commit_queue.py:1754` `def mark_cascade_stale_batch(`（D1 批量化收口 st-commitspeed-d1-20260930）+`:1817` `_mark_cascade_stale` 一元包装+`:1845` stale 项基底重校验（mergeable_pred 注册表族三向合并）
- 接线闭环：`scripts/governance/commit_queue_landing.py:4271` `marked = cq.mark_cascade_stale_batch(root, stats.get("landed_index"))`——drain 落地后真调用
- 标记表收录：commit_queue.py:327 cascade_stale 在 ITEM 标记表

### 2.5 门禁约束
- 图面 gate_refs=[]；deadletter_class=[item(cascade_stale)]；约束=不消耗 landing（死信候选不死透，可修因复活）

### 2.6 自动化触发
- drain 每轮落地后自动扇出扫描（O(N) 段已移出池级锁，D1 手术单 §4.3）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | landed_index+base_blob 真填充实存 |
| 输出面 | pass | 级联标记面接线（landing :4271 真调用） |
| SSOT真源 | fail | 图 wiring_status=unwired_slot_hollow 与代码现实相反——QUEUE-04 已接通，图机生证据（base_blob 恒 None）已失效，账面与代码两处说法必有一假且假的是图（「账本必须对得上」违规） |
| 代码模块 | pass | 批量标记+重校验+接线三点闭环 |
| 门禁约束 | pass | 不消耗 landing 语义在案 |
| 自动化触发 | pass | 落地后自动扫描 |

## 4. 缺口与建议
- 【最高优先收口】D05 图注回写：wiring_status 应改 wired（或 partial+新红因），机生证据更新为「QUEUE-04 base_blob 填充+landing :4271 接线」；建议总包按骨架回写流程一次清（G02 同款「代码先修、图注未跟」）。
- 【观测建议】cascade_stale 现网 0 件可能=依赖声明本就稀少（depends_on A 段 schema 预留为主），建议 health 输出「带 depends_on/base_blob 的 pending 占比」，让该判定有活体可见度。
