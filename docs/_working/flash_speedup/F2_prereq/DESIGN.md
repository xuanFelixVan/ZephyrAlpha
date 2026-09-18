---
ttl: task_bound
completes_when: F2 前置件设计已落地并复核
rule_form: data
verifiability: machine
title: F2 前置件作业簿——lease 续租+同域同文件双通道并发压测+热文件单通道闸+exit-burst（免签部分，通道数本身=Owner 门位）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: prereq_constructed_awaiting_owner_s18r3
---

# F2 前置件作业簿 — k=4 分区通道的前置四件（判据书 F2「前置（机读，缺一不开工）」行）

> **一句话结论**：前置四件中三件已施工完毕全绿——①lease 续租（F9 已交付，3c853303da）
> ②「同域同文件双通道并发」压测落地 test_commit_queue_landing.py（9 新测试全绿，46/46 文件全绿）
> ③跨域热文件单通道闸在案（commit_queue.py `channel_key_for_files` 域映射配置+不变量测试）
> ④exit-burst 场景测试落地（burst 中途注入+lease 释放瞬间双自举竞态，零丢失零双落实证）。
> 第四前置「夜间并发峰值连续 7 天>40 车道」=观察窗件，非施工件，只能自 flag 启用起算 7 天观察，
> 本夜无法物化——**如实登记留 Owner**。通道数 k=1→4 本身=S18-R3 Owner 门位，本簿只提案不自签。

## 0. 病灶（第一性原理）

P2 压测实证 24/h 是**门禁常数不是锁常数**（10 worker 870/h → 20 worker 540/h、饿死 45%），
故提速次序=先修门禁（F3）再谈通道（F2）。但通道扩容（k=1→4）若直接开工，有两个结构性风险：
**(a) 同域同文件被撕到两个通道并发写** → 丢失更新/CAS 风暴/dev 历史双写者；
**(b) 跨域热文件（注册表族/ROOR/AGENTS.md/standards.yaml）多通道并发写** → 注册表是全场
最高频争用面（本会话即实证：capability_canonical_file_registry.yaml 外来 staged 在途，
token 登记被卡），多通道只会放大。前置件=把这两个风险在 k=1 现状下**先物化为机器不变量**
（路由配置+压测），S18-R3 签署后 k=4 drain 按域取队 MUST 咨询本路由，风险面已封死。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|---|---|---|
| ①上游 | 谁入队 | `git_commit.py --enqueue`（直连改道）/`commit_queue.py enqueue`（CLI）/`reroute_auto_commit_to_queue`（reconciler 派生批，flag 门控）——全部经 `enqueue_item` 快照入袋（完整 blob 非 diff，66 号 §4 裁定 2） |
| ②下游 | 谁落地 | `drain_queue`（单写者主循环：SerializerLease O_EXCL+TTL 300s+逐项 renew 心跳【F9 3c853303da】→ FIFO/车道化取队 → `WorktreeLanding` 真 git 落盘 → done/dead 四态）；自举=事件触发非常驻 |
| ③算法机制 | 并发安全基础 | lease O_EXCL 原子创建=任一时间点活跃 drainer ≤1（`SerializerLease.__enter__`：僵尸 PID 即时回收/活体慢项绝不抢/TTL 兜底）；`renew()` 逐项心跳防慢项被 TTL 误抢（F9 治本 2026-09-17 11 条 pathspec 死信根因）；幂等=landed_id is-ancestor 短路+标记 grep 双路径（66 号 §8） |
| ④后端 | 通道池现状 | k=1 单 serializer worktree（`.runtime/commit_queue/worktree`）；k=4 worktree 池=F2 主体（Owner 门位），改动文件=commit_queue.py（drain 按域取队）+commit_queue_landing.py（k 通道池）+域映射配置 |
| ⑤前端 | 无 | 纯后端队列 |
| ⑥数据字段 | 路由键口径 | `channel_key_for_files(files) -> str`：热文件（`_HOT_PATH_MARKERS` 4 族）→`hot`；同域→域键（src/zephyr/<域> 三级，其余顶级目录）；跨域混合→`shared` 兜底。不变量=同域同文件双项必同键 |

## 2. 治本设计（前置四件×施工证据）

### 2.1 前置件清单×状态

| 前置件 | 判据书原文 | 施工件 | 状态 |
|---|---|---|---|
| ① lease 续租 | 「lease 续租机制落地」 | F9 交付：`SerializerLease.renew()` 逐项心跳+活体不抢分支（3c853303da，#ARCH-330 6ea82b9cfb） | ✅ 已落地 |
| ② 双通道压测 | 「test_commit_queue_landing.py 新增'同域同文件双通道并发'压测绿」 | `TestF2SameDomainDualChannelConcurrency`：双 drain 线程 barrier 同时起跑争 lease，同域同文件 v1→v2 双项——断言零丢失(done=2)/零死信/零丢失更新(终态=v2)/FIFO 定序(v1 是 v2 祖先)/单写者(落地窗内 dev 历史全队列标记) | ✅ 绿 |
| ③ 热文件单通道闸 | 「跨域热文件清单（注册表/ROOR/AGENTS.md/standards.yaml）强制走单一热通道的闸在案」 | `commit_queue.py` 域映射配置在案：`HOT_CHANNEL_KEY`/`MIXED_CHANNEL_KEY`/`_HOT_PATH_MARKERS`/`channel_key_for_files`（纯函数零行为变化，k=1 drain 不咨询；k=4 落地时 MUST 咨询——注释已钉）+`TestF2HotFileChannelGate` 7 例不变量测试 | ✅ 在案 |
| ④ exit-burst | Owner 施工令「退出突发场景必须测」 | `TestF2ExitBurst`：主 drain 在途 6 项时突发注入 6 项（belt 逐项 re-glob 同轮消化）+lease 释放瞬间双自举 barrier 竞态——断言 12 项全 done/零死信/零孤儿/零双落（commit 数==项数+landed_id 全唯一+全在 dev 历史）/单写者 | ✅ 绿 |
| ⑤ 7 天>40 车道 | 「夜间并发峰值连续 7 天>40 车道」 | 观察窗件非施工件——自 queue flag 启用起算连续 7 天观察，本夜无法物化 | ⏳ 留 Owner（如实登记） |

### 2.2 测试证据

- `pytest tests/governance/test_commit_queue_landing.py -k F2` → **9 passed**（闸 7+并发 1+burst 1）
- `pytest tests/governance/test_commit_queue_landing.py` → **46 passed**（既有 37 零回归）
- `pytest tests/governance/test_commit_queue.py` → **83 passed**（路由函数纯增量零回归）
- `pytest tests/governance/test_commit_queue_integration.py --timeout=900` → **29 passed（265s）**（真 gateway 全门禁链 50 提交零丢失；默认 120s 超时=首测超窗非回归）
- 单写者断言口径修正 1 处：`assert_single_writer_dev_history(since=base_sha)`——fixture init 笔是
  队列前直提，属断言函数文档的 since 豁免口径（非测试放水：落地窗内全量断言）

### 2.3 k=4 就绪判语（判据书要求原文）

**「k=4 通道就绪，待 Owner 签 S18-R3」**——前置①②③④施工完毕全绿；⑤=观察窗件如实登记。
通道数本身不动（Owner 门位）；签署后 F2 主体=drain 按域取队（咨询 `channel_key_for_files`）
+landing k 通道 worktree 池+每通道独立 lease 文件（`serializer-<key>.lease`），
机读判据（k=4 小时落地峰值≥76/同域冲突率不升/lease 双写者窗口=0）届时按判据书验收。

## 3. 自审闸三态

| 态 | 自检项 | 结论 |
|---|---|---|
| 红（必须挡） | 是否动了通道数/k=4 主体？ | **否**——`channel_key_for_files` 纯函数，k=1 drain 零咨询零行为变化；通道池未建 |
| 红（必须挡） | 是否动了门禁语义/lease 语义？ | **否**——SerializerLease 一字未改；测试只读断言其现行语义 |
| 黄（留痕） | 测试线程并发是否可能 flaky？ | barrier 同时起跑+lease_timeout=0.3s 确定性退避+补排空收敛——断言全是终态不变量（done 计数/内容/祖先链），不依赖线程时序；46/46 绿实证 |
| 黄（留痕） | 域键粒度（顶级目录）是否过粗？ | 是保守选择——粗粒度只会多串行不会多并发（安全侧）；k=4 落地时按实测冲突率细化，配置已留 src 三级先例 |
| 绿（放行） | 判据书前置行四件对得上？ | ①F9 hash 在册②③④本簿 §2.1 逐项对账，⑤如实登记非隐瞒 |

## 4. Owner 裁定项（只提案不自签）

- **S18-R3（裁定#320）③**：k=4 分区通道开工门位。前置四件已就绪（本簿 §2.3 判语），
  第⑤前置（7 天>40 车道观察窗）建议 Owner 裁定口径：自 queue flag 启用日起算 or 豁免
  （P2 压测已实证通道容量 870/h@10w，车道数观察的价值在防过度建设——AI 倾向按判据书原样执行观察窗）。

## 5. 施工日志

- 2026-09-18 ~05:00 挖矿：判据书 F2 前置行拆解→drain_queue/SerializerLease/WorktreeLanding 全链读通（lease O_EXCL+renew 逐项心跳+四态目录+车道化 FIFO）。
- 2026-09-18 ~05:10 施工：commit_queue.py 域映射配置段（safe 增量 44 行）+测试 3 类 9 例。
- 2026-09-18 ~05:20 验收：F2 9/9 绿→文件级 46/46 绿→test_commit_queue.py 83/83 绿；单写者断言 since 口径修正（init 笔豁免=断言函数文档口径）。
- 2026-09-18 ~05:40 integration 29/29 绿（--timeout=900，265s）；代码批落地 `727ad32a54`（q-0008，commit_queue.py+test+判据书行 3 件，零搭便车核实，HEAD 祖先）。本簿与其余工作簿同批挂 creation_token 待注册表外来在途清空。

## 6. 残余与交接

1. **integration 测试结果**：后台跑中，绿则回填 §2.2；红则按死信对症修（勿 requeue 判据书已死信项）。
2. **提交批次**：commit_queue.py+test_commit_queue_landing.py（跨域 --allow-multi-domain）+判据书验收行改写（harness 重建记录）走队列；本簿与其余 workbook 同批（creation_token 待注册表外来在途清空后登记）。
3. **k=4 主体**（Owner 签署后）：drain 按域取队+landing 通道池+每通道独立 lease+harness `--channels` 参扩展——改动文件与判据见判据书 F2 行，本簿路由配置是其地基。
4. **harness 已重建**：`.runtime/tmp/rb2/harness.py`（39193B，自 closeout_residue 保留件复制，py_compile+--help 通过）；判据书悬空验收行已改写（--channels 不存在→如实标注为 F2 落地后验收维）。
