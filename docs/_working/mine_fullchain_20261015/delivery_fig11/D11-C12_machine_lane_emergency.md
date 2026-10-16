---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C12
name_zh: 机器车道与紧急通道
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C12
---

# D11-C12 机器车道与紧急通道

## 1. 定义
提交车道第十二环节：非人工提交的两条特殊道。决策问题=「机器提交要不要按 flag 改道？emergency 通道什么时候合法、伪造标记怎么判？」机制=_commit_auto 按 serializer flag（commit_queue_serializer enabled=true，flags.yaml:112 实读）改道回队列（反馈环 C12→C08 已声明）；BatchedAutoCommitter 合批；emergency_commit 仅注册表/锁不可用时合法（commit-tree plumbing+落册审计，手写 [GW:] 标记判 forged）。

## 2. 六向台账

### 2.1 输入面
- reconciler auto commit 请求（C11 产物）
- flag 面：config/flags.yaml commit_queue_serializer（enabled=true production 实读）
- emergency 前置：注册表/锁不可用证据

### 2.2 输出面
- 改道件：队列项 meta.rerouted_from（图 exec_evidence 09-25 实查 53 件；**2026-10-15 复核 done/ 内 rerouted_from=0 件**——done TTL 轮换把 9 月老件收走，证据轮换非断链）
- emergency 落册审计（commit-tree 直落+审计面）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C12`（wired/production）
- 骨架：07_对账观测与紧急车道.md；宪法 §9.8（emergency 仅注册表/锁不可用时可用+手写标记判 forged）

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:5106` `def _commit_auto(`+`:5088` `def _reroute_commit_auto_to_queue(`（图记 :3845/:3827，行锚漂移 +1261）
- `src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py:427` `def emergency_commit(`（图记 :20，模块头语义在案）
- 单写者断言：assert_single_writer_dev_history（landing/gateway 双侧日检）

### 2.5 门禁约束
- gate_refs=[FORGED-GW-MARKER]：emergency 手写标记判 forged（宪法 §9.8）；改道语义受 serializer flag 支配（Owner 门位翻旗留痕）

### 2.6 自动化触发
- reconciler 产 commit→flag ON 自动改道（反馈环）；BatchedAutoCommitter 自动合批

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | auto 请求+flag+emergency 前置实存 |
| 输出面 | warn | 改道代码在位，但 rerouted_from 活体证据经 done TTL 轮换=0，短期不可从 done/ 直接复核改道实弹 |
| SSOT真源 | pass | 图/骨架/宪法一致 |
| 代码模块 | pass | 三锚点实存（行锚漂移 +1261） |
| 门禁约束 | pass | forged 判伪+flag 门位在案 |
| 自动化触发 | pass | 改道/合批自动 |

## 4. 缺口与建议
- 【证据轮换】建议把 rerouted_from 计数改为滚动累计台账（如 .runtime/audit/auto_reroute_ledger.jsonl 追加），不依赖 done/ 件存活期。
- 【建议】emergency_commit 合法性前置（注册表/锁不可用）建议留一次性取证快照要求（审计行含失败原因证据），防滥用面扩大。
