---
ttl: task_bound
title: QCure作业簿·bag_storage
session: st-qcure-20260925
---
# bag_storage 作业簿

## 1 环节定义与边界
袋与 blob 存储 = 队列项 JSON（袋/manifest）与内容寻址 blob（`.runtime/commit_queue/blobs/<sha256>`）的写入、读取、引用、清理全生命周期。边界内：manifest 字段全集与代际、blob 落袋/读袋/孤儿/退役、10MB 上限、blob 缺失路径、M3.1 envelope 字段兼容性。边界外：pending→processing→done/dead 状态机本身（队列机械）、落地合并语义（只涉及其读袋接口）。本环节是 M3.1 施工面 + M5.4 治理面。

## 2 六向台账
### ①上游输入（谁喂它）
唯一写入方=`_store_blob` scripts/commit_queue.py:489-494（下称 CQ，sha256 命名、exists 跳过去重、`_atomic_write` CQ:396-403 tmp+fsync+os.replace）；顺序上 blob 先于队列项落盘（CQ:689 注释"blob 入袋即内容不丢"）。manifest 唯一构造点=`enqueue_item` CQ:744-757。间接喂养：requeue 从 dead 项 blob 重建快照再入袋（CQ:1479-1500）。
### ②下游消费（它的输出被谁吃）
- 落地读袋：`_apply_snapshot` scripts/governance/commit_queue_landing.py:1348-1353（下称 LAND，blob_ref 读字节→worktree 文件）；`_noop_overwrite_paths` LAND:1168-1176（读袋字节算 git blob sha 判无操作覆盖）；假落地防线比对用 blob_sha256 对 git 对象（LAND:1836-1852）。
- requeue 读袋：`--from-bag` CQ:1486-1499（逐文件 sha256 自校验）。
- 只读观测：`queue_health` blobs 计数 CQ:1860。
- 已查无（归因）：compaction/级联标记/幂等判定均不读 blob 内容（只动 JSON 字段）——blob 唯二读者=落地与 from-bag requeue。
### ③机制现状+业界参照
现状：内容寻址天然去重（CQ:492）；done 项 7 天 TTL 清理但**明文不碰 blobs**（CQ:1553"内容寻址共享存储不在本清理范围"）；dead 永不清理（CQ:1552，66 号 §8 不变量）。业界：git 对象库同为内容寻址、不可达对象由 `git gc --prune` 按宽限期回收（https://git-scm.com/docs/git-gc ）——"先判可达再按龄回收"即引用计数+宽限期的同构做法；CAS 去重天然防重复存储（同 CQ 设计）。merge queue 类系统（GitHub https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue ）不持久化 payload，落地即弃——QCure 因"入袋即安全+死信回放"必须持久化，退役只能走归档不能走即时删。
### ④代码面（三重搜索）
- 实现：manifest 字段全集=qid/session_id/created_at/branch(恒 dev，CQ:181)/base_head(可 null)/message/files[{path,blob_sha256,blob_ref="blobs/<sha>",base_blob(null=新增或未填),action=modify|delete}]/meta{depends_on,supersedes,+meta_extra(lane/rerouted_from/task_id/interactive/oversize_batch/requeued_from)}（CQ:744-757+614-640）；落地侧追加：done+landed_at/landed_id（CQ:1301-1302，noop 前缀 CQ:122）、dead+dead_at/dead_reason（CQ:1314-1315）、requeue 留痕+requeued{new_qid,at}（CQ:1530）、级联+meta.stale/stale_by/stale_at（CQ:1054-1056）/stale_cleared_at（CQ:1272）、部分覆盖+meta.compacted_partial/compacted_at（CQ:591-592）。
- 测试：tests/governance/test_commit_queue.py（blob 去重/大小上限/requeue from-bag 校验）、test_commit_queue_landing.py、test_commit_chain_campaign_20260922.py:128/215（from_bag 通道）。**已查无**：blob 孤儿/退役无任何测试与实现（归因：功能不存在）。
- 调用方全集：blob 读=LAND:1351/LAND:1172/CQ:1488；blob 写=CQ:493；无第三方。
### ⑤运维/呈现面
`health` 子命令报 blobs 数（CQ:1860）但不报孤儿/容量；堵点本 `.runtime/audit/bottleneck_ledger.jsonl` 死信登记带 qid 可反查袋；主工作区收敛留痕 `.runtime/commit_queue/main_workspace_sync.jsonl`（375KB）；blob 缺失类死信历史 0 笔（grep dead/ "blob 读取失败"=0）——本环节不是死信主因，纯卫生面。
### ⑥失败态与数据面
异常路径全集：①落地读袋失败→RuntimeError→死信（LAND:1352-1353）；②from-bag 读袋失败/sha 不符→RequeueError（CQ:1489-1499）；③_noop 读不到→保守判冲突不短接（LAND:1172-1174）；④超 10MB→QueueReject exit 2"超限走人工"（CQ:476-481）。生产数据（2026-09-25 实测）：blobs=19955 个/3.2GB；被引用 8062、**孤儿 11893（60%）**；引用状态分解：仅 done 引用 5658（done TTL 过期后即成孤儿）、仅 dead 引用 1374（dead 永存→永被引用）、live（pending/processing）617、done+dead 混引 414。1353 项 manifest 代际：无 base_head=1074/有=279；base_blob 非 null 仅 190 条目；meta.lane 有 824；envelope 有 0。

## 3 缺陷与矿脉清单
1. 【已知·QCure M5.4】blobs 只增不减：19955/3.2GB 且 60% 孤儿。引用计数**机械上完全可行**——反查=遍历四态 q-*.json 的 files[].blob_sha256（实测 1353 文件秒级扫完，本作业簿已跑通原型）；难点在策略不在计算：dead 引用的 blob 不可回收（from-bag 依赖 CQ:1486-1499 + dead 永不清理不变量）；仅 done 引用的 5658 个在 done 过期后无读者（`_already_landed` 走 landed_id/is-ancestor 不读 blob，LAND:1082-1099）。安全最小件=只回收「孤儿 ∧ mtime>宽限期」，回收前重扫一次四态防竞态；**归档到备份仓优于删除**（宪法 §7 备份分工），删除需 Owner 门位。
2. 【新矿】`cleanup_done` 直接 os.remove done JSON（CQ:1577-1580）——引用计数随 JSON 消失，事后无法追溯该 done 项用过哪些 blob。若做 M5.4，建议 cleanup_done 先留 removed 清单或归档 JSON（.runtime 不落盘铁律例外走 .runtime/tmp 或备份仓）。
3. 【新矿·越界面】10MB 上限贴顶运行：实测最大 blob 10,483,594B（上限 10,485,760=10MiB，CQ:180），库内 4+ 个贴顶 blob——有生产者踩线成功，超 1KB 即拒；无分片/无替代通道，"走人工"无 SOP。另 `_read_files_from_worktree` 逐文件全量 read_bytes（CQ:2145-2161），40 文件×10MB≈400MB 内存峰值未设防（理论面，登记不施工）。
4. 【新矿】blobs 目录 19955 文件平铺无分桶，`queue_health` 每次全量 glob（CQ:1860）——当前量级可用，若增长 10 倍枚举成本进 status/health 延迟（长尾登记）。
5. 【M3.1 envelope.final_message 兼容性评估·结论=可施工零迁移】①manifest 是 JSON dict，读者全走 .get（item.get("message") CQ:1739 等），新增顶层键 `envelope` 对老袋（envelope 有 0 个）天然兼容，消费侧 `item.get("envelope",{}).get("final_message") or item.get("message","")` 回退即可；②compaction 部分覆盖写回 json.dumps(item) 保留顶层键（CQ:590-596）、整体覆盖走新项自带 envelope——两路无损；③**唯一丢失点=requeue**：CQ:1514-1527 重建新项只传 message，envelope 不会继承——M3.1 施工清单必须加"requeue_dead_item 复制旧袋 envelope（或按新 message 重建）"；④落地消费点=LAND:1739 `full_message=f"{message}\n\n{marker}"`——envelope 只替换 message 段，`[GW:]` 标记追加与 POST-COMMIT-GUARD 防伪链不动；PROTECTED-PATHS 标记丢失病根（方案 §1.3#7 GW L2498-2499）由 envelope 直治；⑤快照时机=enqueue 入参 message 已是最终态（三入口 message 来源：裸 CLI --message/--message-file CQ:2166-2173、reroute 直传、正门同）——envelope 即 message 冻结副本，无二次采集面。
6. 【已知·方案内】分支恒 dev 单目标（CQ:181）——envelope 若未来扩多分支信封需先破单分支约束（登记不施工）。

## 4 自审闸三态裁定
施工——M3.1 envelope 经五点兼容性评估确认零迁移可施工（唯一注意点=requeue 继承必须同批做）；blob 退役治理（M5.4）挂起排期：孤儿数据基础已备（60%），但删除策略涉 dead 永不清理不变量与备份门位，按方案原文定位为低优先级卫生件排并行班。

## 5 长尾清单
- blob 孤儿回收原型脚本本次只读跑通未落盘；正式化需登记临时脚本通道（.runtime/tmp）。
- 仅 dead 引用的 1374 个 blob 的会话分布/死因分布未拆——M5.4 设计宽限期时补。
- manifest JSON 无 schema 校验器（字段全靠 .get 容错），损坏项靠 _read_item 重试+人工（CQ:975-989）——袋结构 fsck 类工具缺位。
- branch 字段/多分支队列、blob 分桶、内存峰值设防：三件均登记不挖（③④⑥条）。
- preflight/landing 之外的袋读取者如有遗漏（如外部巡检脚本），引用计数上线前需再全仓 grep 一次 blob_ref 消费面。
