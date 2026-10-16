---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C08
name_zh: 入队即转活（快照入袋）
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C08
---

# D11-C08 入队即转活（快照入袋）

## 1. 定义
提交车道第八环节：队列入口。决策问题=「这条提交请求能过入队轻检（穿越/消息/体积/密钥名），并以内容寻址快照入袋吗？」机制=enqueue_item 轻检四规则+_store_blob 内容寻址去重+_create_item_excl O_EXCL 唯一 qid+_compact_pending 同键覆盖；C1 同会话短窗自动合批（commit_queue_c1_debounce，ZEPHYR_CQ_C1_DEBOUNCE env 同款缺省 ON）。

## 2. 六向台账

### 2.1 输入面
- 提交请求快照（session/message/files/meta{depends_on,supersedes}/base_head/base_blob——A 段不主动取 git 零依赖，CLI 提供）
- C04 改道件与人工 --enqueue 件同入口

### 2.2 输出面
- pending 项+袋：`.runtime/commit_queue/pending`（2026-10-15 实查 53 件）+`.runtime/commit_queue/blobs`（实查 8356 件；图记 09-25 为 37/19992）
- qid 即时返回（入袋即完成，调用方轮询 status）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C08`（wired/production，MOD-GOV-046，machine_facts.public_api 22 函数在案）
- 骨架：06_入队排空与真落盘.md；宪法 §2.6（优先 --enqueue 走队列）

### 2.4 代码模块
- `scripts/commit_queue.py:1154` `def enqueue_item(`（图记 :636，行锚漂移 +518）
- 同文件 `:562` `_store_blob`+`:607` `_create_item_excl`+`:709` `_compact_pending`（图记 :489/:534）；`:799` C1 debounce 资格闸（stale/attempts/depends_on/lane/task_id/base_head 异或不并）

### 2.5 门禁约束
- 入队轻检四规则（穿越/消息/体积/密钥名）；非法 request 拒收；blob 内容寻址 sha256 去重（同内容零重复存储）

### 2.6 自动化触发
- 锁争用自动改道（C04）与手动 --enqueue 双触发；同会话短窗自动合批（20 分钟窗）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 快照 schema+双触发入口实存 |
| 输出面 | pass | pending 53+blobs 8356 在盘在产 |
| SSOT真源 | pass | 图/骨架/宪法齐 |
| 代码模块 | pass | 四函数实存（行锚漂移 +518） |
| 门禁约束 | pass | 轻检四规则+寻址去重在码 |
| 自动化触发 | pass | 改道/合批全自动 |

## 4. 缺口与建议
- 【水位观察】pending=53（图快照 3）为高水位，处理见 C09/C13——非本环节缺陷但入队速率应与排空速率同图监控。
- 【建议】blobs 8356 件的 GC 口径（袋出 dead/ 即失该路引用可转清，2026-10-13 段二 Owner 批注已在 dead-archive help 在案）建议在 C13 health 输出孤儿 blob 计数。
