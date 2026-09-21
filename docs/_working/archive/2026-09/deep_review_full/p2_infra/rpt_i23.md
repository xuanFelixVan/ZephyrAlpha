---
ttl: task_bound
title: 深度审查作业簿——本地降级回放
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：本地降级回放（I23）【保命件】

- 状态: **已审**
- 级别: P2｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/local_replay.py:80`（save_fallback）；replay 主链 :388（replay_batch）/:485（replay_catchup）
- 生产调用方: ch_writer.write_tsv 三级降级末级（ch_writer.py:8, 762）、scheduler（:825 启动回灌、:852-859 周期回灌+积压>200 切 catchup，scheduler.py:71 阈值）
- 测试文件: tests/zephyr/data/test_local_replay.py（30 用例）
- 备注: 5510 件滞留史案主战场；近 5 次提交全是事故治本（2026-07-22/07-24/09-14×2/09-16）

## 1 对象快照

- 审查范围：`local_replay.py` 全文 519 行：save_fallback（原子落盘+manifest JSONL 追加）、replay_batch（分组回灌+manifest 合并写）、replay_catchup（追平档）、_adopt_orphans（孤儿收编自愈）、_manifest_fs_lock（跨进程 O_EXCL 锁+30s 陈锁强破）、_file_key（分隔符归一化）。
- 事故史（代码内锚点）：①2026-07-13 型刷文件→冷却；②2026-07-22 manifest 覆盖丢新增；③2026-07-24 skipped 条目永生；④2026-09-14 丢更新竞态（28 孤儿）+收编循环 NameError+Windows os.replace 句柄竞争；⑤2026-09-16 5510 文件 19h 零回灌（反斜杠/正斜杠双形态键打不中 exclude，:222-230）。
- 排除项：ch_writer 二级降级链与连接自愈（上游，另一对象）；scheduler 回灌循环（:825-859 只审接线）；progress_store DEFERRED 协同归 I19。
- 测试覆盖概况：30 用例，含 5510 案回归（反斜杠移除+混合分隔符去重）——事故驱动测试密度全仓少见的好的样板。
- 材料包缺项：当前积压实况（data/local_fallback 行数）未取（生产数据只读未授权）；无近 N 天回灌成功/失败率统计。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | **积压无告警出口**：scheduler 回灌循环只 log.info（scheduler.py:859），全程无 alerter.notify——5510 冻结 19h、884 死信积压 8 天同型：积压指标无主动推送，靠人看日志/面板发现 | scheduler.py:852-859 + local_replay.py 全文无 notify 调用 | P1 | grep local_replay/scheduler 回灌段无 notify；积压>阈值时无告警文件生成 |
| E 对抗 | save_fallback 的 manifest 追加不取跨进程 fs 锁（只持线程锁 :118）：与 _write_manifest 的"锁内读-合并-replace"并发时，追加可落在合并读之后、replace 之前→条目被 replace 吞掉成孤儿——fs 锁互斥体系有一角没封（自愈兜底=_adopt_orphans 下轮收编，延迟一次回灌周期） | local_replay.py:118（仅 _manifest_lock）vs :242-247（fs 锁内读合并） | P2 | 两进程并发压测：A 进程长循环 save_fallback，B 进程循环 replay_batch，统计孤儿数 |
| E 对抗 | at-least-once 重放无端内去重：write_tsv 超时但 CH 已提交→文件保留重试→重复行；幂等性约定转嫁给表引擎（ch_writer.py:8"幂等性由调用方决定"）——ReplacingMergeTree 表无恙，MergeTree 表（news_data 等非Replacing）重放即重复 | local_replay.py:370-382（失败保留）+ ch_writer.py:8 契约声明 | P2 | 对 MergeTree 目标表造可超时场景（timeout=120 拨小）观察重放后行数翻倍 |
| A 深度 | _manifest_fs_lock 锁等待超时（10s）返回 None→_write_manifest 无 fs 锁继续合并写（:209-210"兜底继续"）——2026-09-14 丢更新竞态在超时路径上原样复活；合并写有重读兜底但正是竞态窗口本身 | local_replay.py:208-211, 242 | P2 | 两进程各持锁>10s 场景压测 manifest 丢更新 |
| A 深度 | _file_key 归一化已覆盖三处汇合点（_write_manifest :253/257/259、_adopt_orphans known 集 :297-300）——5510 案根因修全；残余：replay_batch 内部 :458-465 合并用裸 file 键（raw-vs-raw 自洽，最终由 _write_manifest 归一并去重，无实害） | local_replay.py:222-231, 297-300, 253-259 vs :458-465 | P3 | code review + 5510 回归测试（已在 387b7ce588 落地 3 条） |
| E 对抗 | _replay_one_file 毒文件永生：数据坏行/schema 漂移类永久失败文件每次批次都消耗 max_files 预算并永远留 manifest（无重试计数、无死信隔离）——攒多后周期回灌预算被毒文件挤占，新鲜积压排队 | local_replay.py:381-385, 441-443（failed 无上限重试） | P2 | 造一个 schema 不匹配文件入 manifest，观察 10 个批次后仍 failed 且无隔离 |
| B 上游 | cols_clause=None 时的列数截断防御（:355-369）：按 TSV 首行字段数截取前 N 列——若 TSV 首行恰好少一列（半写行残留），后续所有行按错列序插入（静默错位） | local_replay.py:355-369 | P3 | 首行 5 字段其余 7 字段的 TSV 断言截取行为 |
| A 深度 | by_table 分组注释"同表合并回灌减少 INSERT 次数"（:411）与实现不符（只分组顺序回灌，每文件独立 INSERT）——注释漂移 | local_replay.py:411-414 | P3 | code review |
| E 对抗 | save_fallback rename→manifest 追加两步非原子：崩溃窗口产生孤儿→_adopt_orphans 收编（cols_clause=None 走列数截断）——自愈链完整，延迟一个周期 | local_replay.py:104-119, 287-327 | P3 | 单测模拟落盘后 kill，跑 replay_batch 验证收编 |
| A 深度(测试) | 30 用例覆盖三大事故回归；未覆盖：fs 锁超时路径、毒文件预算挤占、save_fallback 与 replace 并发 | tests/zephyr/data/test_local_replay.py | P3 | grep 用例名 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| Transactional Outbox / 本地兜底队列语义 | **对等已有**：本模块=标准 outbox 形态（业务写失败→本地持久化→relay 回灌），业界定论 at-least-once+消费端幂等（本项目靠表引擎幂等，契约已声明但未强制校验=缺口见 D-3） | AWS Prescriptive Guidance: transactional outbox, docs.aws.amazon.com, 2025：https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html ；event-driven.io Outbox, Inbox patterns and delivery guarantees, event-driven.io, 2025：https://event-driven.io/en/outbox_inbox_patterns_and_delivery_guarantees_explained/ |
| 多实例 relay 并发（SKIP LOCKED/分区认领/死信隔离） | **立卡候选**：业界 relay 标配=认领锁+重试计数+死信队列+可观测；本对象有跨进程锁与孤儿自愈（超出一般水平），缺重试计数与毒文件死信隔离（D-4）——立卡补 DLQ 化：failed≥N 次移入 `data/local_fallback/_poison/` 并告警 | Outbox retries/DLQ/observability 实践文, levelup.gitconnected.com, 2025；多实例 relay 重复与 SKIP LOCKED 讨论, stackoverflow.com, 2024 |
| outbox 行 TTL/清理 | 对等已有：manifest 条目与文件生命周期同删（成功即清），无泄漏面；TTL 清理不适用（兜底数据不可丢） | 同上 Medium Rigorous Examination, 2025 |

## 4 缺陷清单

1. **D-1（P1）积压指标无告警出口**
   - 现状→证据：回灌循环零 notify（轴 C 行）；5510 冻结 19h 才被发现正是该空洞的实证。保命件的"保命"闭环缺最后一环——兜底成功≠回灌成功。
   - 影响：CH 长时间不可用或回灌冻结时，数据滞留只留 log，运营无感知；叠加 I19 DEFERRED 水位前进，断供被账面掩盖。
   - 建议修法：scheduler 周期回灌后判 `backlog_file_count()`：>阈值（如 500）或连续 N 轮零进展→alerter.notify CRITICAL（复用 I20 通道，300s 冷却防刷屏）；可挂 backlog 趋势进 api_server 健康端点（I26 顺带）。
   - 验证法：积压造 600 条跑一轮，断言 failures/ 出现 ch_local_replay_backlog 类文件。
2. **D-2（P2）fs 锁体系两处旁路**（save_fallback 追加不取锁 + 超时无锁继续）：修法=save_fallback manifest 段包 _manifest_fs_lock；超时路径改 skip 本轮（下轮重试）而非无锁硬写。验证法=轴 E 并发压测两条。
3. **D-3（P2）重放幂等契约未强制**：对非 ReplacingMergeTree 目标表，重放重复风险真实存在；建议 manifest entry 记录目标表引擎判定（一次 query），MergeTree 表打 warning 或要求运维确认。
4. **D-4（P2）毒文件无死信隔离**：entry 加 fail_count，≥5 次移 `_poison/` 目录+告警一次；防预算挤占与无限重试。
5. **D-5（P3）列数截断首行依赖 + 注释漂移 + 两步非原子（已有自愈）**：卫生批。

## 5 挂起疑问

- 5510 案的 5510 个文件当前是否全部排干（需生产 data/local_fallback 实况）；若仍有残留在 _poison 化之前先人工核。
- scheduler 周期回灌线程与任务线程并发 replay_batch 的实际并发度（_REPLAY_CATCHUP_THRESHOLD=200 切换逻辑在低积压时的周期频率未逐行核）。

## 6 完备性自评

- 六轴全查：A（锁/归一化/截断防御逐分支）、B（cols_clause/表名补全/引擎幂等契约）、C（消费方=ch_writer+scheduler，告警出口缺失=最大发现）、D（与 ch_writer 三级降级链分工、与 I19 DEFERRED 协同）、E（五问逐条：静默失败=积压无告警、假阳性=skipped 计成功？否、断了没人知道=D-1、重放重复=D-3、时序=锁旁路 D-2）、F（三源带 URL）。
- 长尾：_poison 化对 5510 案回归测试的影响未评估；Windows os.replace 10×0.2s 重试在极端并发下的上限行为未压测。
- 总评：经五轮事故治本+红蓝对抗后，本模块已是全仓防御密度最高的管线件之一；当前最大残洞不在代码在**可观测闭环**（D-1）。
