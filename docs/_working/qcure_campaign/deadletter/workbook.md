---
ttl: task_bound
title: QCure作业簿·deadletter
session: st-qcure-20260925
---
# deadletter 作业簿

## 1 环节定义与边界
死信与重投治理 = 队列项从"落地失败"到"复活或永久留痕"的全生命周期：生成（drain 判死）→ 三分类标记 → task_board 联动 → 积压/爆发告警 → 属主 requeue/--from-bag → 归档。边界：不含落地器为何判死（M5 落地器自校验班）、不含 gate 判据本身（M1/M2 预检班）；本环节只管"死后世界"。数据面 = `.runtime/commit_queue/dead*` 全家 + 告警状态文件。

## 2 六向台账
### ①上游输入
- 唯一生成点：drain 中 `LandingResult.ok=False` → 写 `dead_at`/`dead_reason` → os.replace 移 dead/，队列继续（DLQ 不堵队）scripts/commit_queue.py:1312-1320。
- 瞬态环境失败不走此路：landing 抛 `LandingEnvironmentError` 项退 pending（特征串真源 `_TRANSIENT_GIT_MARKERS` scripts/governance/commit_queue_landing.py:174-187、不变量 :8）——即 dead/ 里全是"非瞬态"判死。
- 上游实质：三条生产入口（裸 CLI commit_queue.py:2164、machine 车道 landing.py:2607、requeue :1425）零预检，死信=门禁失败的延迟交付（QCure 方案 §1.3-1）。
### ②下游消费
- 属主人工 requeue（commit_queue.py:1425-1534）：新 qid 排队尾、原项留痕 `requeued={new_qid,at}`（:1529-1531）、`--from-bag` 走 sha256 自校验原快照（:1486-1500）、requeue 豁免大批硬顶（:1523-1525）。
- task_board 逐项打标（:940-972）**仅当 meta.task_id 存在**——实测当前 396 笔死信 task_id=0，该通道覆盖率 0%（auto 同步项全是盲区，:1791-1793 注释自认）。
- 聚合告警：积压超阈 `emit_dead_backlog_alert`（:1865-1949，THD-ALERT-003/004，T-QUEUE-DEADLETTER 幂等自建 task 打 deadletter 标签）+ 爆发 `check_dead_burst`（:2081-2137，005 单日/006 单会话，日期键每日一声）；均挂 drain 收尾（:1329-1338）。
- done 7 天 TTL 清理；**dead/ 永不自动清理**（:1326-1328、:1537-1548）。
### ③机制现状（+业界参照）
- 现状：一次性 DLQ（无重试计数、无退避、无自动通知、无自动归档）；requeue 无限次可用。
- 业界参照：Azure Service Bus DLQ 每消息带 DeadLetterReason/Description 供排障（https://learn.microsoft.com/en-us/azure/service-bus-messaging/service-bus-dead-letter-queues）；SQS DLQ + maxReceiveCount 有界重试（https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html）；poison message 治理共识=分类错误+有界尝试次数+延迟重试+DLQ 深度告警（https://oneuptime.com；https://www.glukhov.org）；失败消息进 DLT 留原始载荷+异常+重试计数+首次/末次失败时间（https://www.redpanda.com）。
- 本仓对标缺口：无 retry_count/首末失败时间字段；重投无上限无退避；死因描述有（dead_reason）但属主收不到。
### ④代码面（实现/测试/调用方）
- 实现：commit_queue.py（生成 :1312-1320、三分类表 :240-286、classify :1797-1804、health :1807-1862、告警 :1865+/ :2081+、requeue :1425-1534、task_board 联动 :940-972/:1387-1422、slow_item 挂账 :1595-1612）。
- 归档史：dead_archive_* 七目录+dead_purged 均为人工搬运，scripts//src 零自动化（grep dead_archive 零命中）。
- 测试：tests/governance/test_commit_queue.py、test_commit_queue_base_head.py、test_commit_queue_ghost_pending.py。
- 调用方：git_commit.py --enqueue（唯一带 18 道预检的入口，L847-855）、belt daemon 事件驱动 drain。
### ⑤运维/呈现面
- 呈现仅两处：`commit_queue.py health` CLI（:2425-2432）+ task_board T-QUEUE-DEADLETTER 标签；前端 dashboard 零接线（grep commit_queue 于 src/zephyr/frontend 零命中）。
- 无 cron 级死信巡检：计划任务清单只有 ZephyrAlpha_BeltDaemon（事件驱动排空）；死信积压告警依赖 drain 收尾——**队列无事件时告警也不跑**（积压静止则永远沉默）。
### ⑥失败态与数据面（2026-09-25 实测）
- 现量：dead/=396 笔（含 st-stress 压测 31）；top 会话 sweep-tail 30、chainpile 27、metaq 21、commitspeed-tbl 19。
- 三分类实跑（复算 env/item markers）：env=19、item=279、**other=98（24.7%）**——other 主力=落地器自身两缺陷族：3WAY 合并 58 + NOTHING_TO_COMMIT/SNAPSHOT 29 + 基底不可知 5，全不在标记表内。
- 归档史（人工）：dead_archive(1)/20260830(61)/0914_closeout(25)/0919_x1(912)/x1b(48)/ulib3_zombie(52)/w8(506)/purged(113)≈1718 笔；triage 账 31+25+912+48 行。
- requeued 留痕 131/396=33%（重投后再死）；hold_st_gov2/hold_stress_phaseB 两目录游离四态之外，queue_health 的 _STATES 看不见（:1819-1820）。

## 3 缺陷与矿脉清单
1.【已知→M3.3】属主认领断链：task_id 覆盖 0% + 死亡无自动通知 → "死在队里无人认领"。挂点建议：**dead/ 项 JSON 增 `prescription`/`owner_session` 字段为主真源**（requeue CLI 与 health 直接可打印），preflight_events.jsonl 增处方字段为辅（预拒即带处方，两处不同源：前者是死后、后者是生前拦）。
2.【新矿脉】三分类表漏新死因族：landing RuntimeError 两族 87 笔全落 other，无 owner、无 requeue 政策——应扩 `_DEAD_REASON_*` 表或增 lander_class 字段（与 M5.1/M5.2/M5.3 判定联动的分类修正）。
3.【新矿脉】重投无界无退避：allow_oversize_batch 无条件豁免（:1523-1525）+ requeue 计数不存在；ulib3c 两晚 12 笔死因序列演化（MASS-DELETION→ORPHAN→LOOKUP→IMPORT→3WAY→PROTECTED×6）=每轮重投只暴露下一道门（whack-a-mole）；sweep-tail 30 笔同型。业界解=有界重试+退避（见③）。
4.【新矿脉】死信归档零自动化：≈1718 笔全人工搬运、无 manifest 对账（仅 w8/hold 目录有 _manifest.jsonl 先例）；建议归档动作脚本化+manifest 常态化。
5.【新矿脉】hold_* 目录游离健康快照视野——四态计数不含，属"暗仓"。

## 4 自审闸三态裁定
**施工**——M3.3 处方结构化+死信通知有现成挂点（dead/ 项字段+task_board 既有通道），与 M1 同夜可落；矿脉 2/3 建议挂期（M5 分类修正与重投熔断各立小件）。

## 5 长尾清单
- dead/ 项 396 笔无索引：按死因族检索每次全量扫盘，可生成 dead_summary 索引（生成器产出，禁手工清单）。
- 三分类表与 `_TRANSIENT_GIT_MARKERS` 两处特征串双真源（CQ:253-261 注释自认"只兜历史/直连路径"），漂移风险。
- blobs 19955 个只增不减（cleanup_done 不清理，:1553 注释）——M5.4 已登记。
- requeue 的 `--from-bag` 未校验会话归属：任何会话可取回任意 qid（qid 白名单只防路径穿越 :1454-1455），防误领可加 session 归属校验。
