---
ttl: task_bound
---

# 提交落地链骨架——环节路由表 + 挖矿计分板（00 总册）

> 按 skeleton_mining_policy（四层/状态纪律/封矿五判据）+ mining_sop_policy 1.4.0（六向寻路/防噪音四闸/自审闸三态）执行。
> 对象：多 AI 并发提交的落地链（enqueue→lease→drain→landing→gates→dead-letter→observability→直连→worktree→业界对标）。
> 挖矿架构：环节=中类（完整性检查单元），环节内子类目=叶（每环节文档内的 E 节逐条列）；施工产物=90 设计 v1.0 + 代码。
> 状态标记：✅有证据在产 | 🔨在建 | ⬜空白 | 🌑不做（留理由）｜【快】=快赢。

## §1 环节路由表（11 环节，挖矿入口）

| # | 环节 | 文档 | 挖矿状态 | 核心痛点（数据实证） |
|---|------|------|---------|---------------------|
| 1 | 入队链 enqueue（快照/去重/反馈面） | 10_enqueue.md | 🔄 | 入队面无预检：终点才死（CREATE-GUARD 32 死全是可零成本前置的检查） |
| 2 | Serializer 租约（TTL/renew/僵尸/活体不可抢） | 11_serializer_lease.md | 🔄 | 活体可无限持锁；无 max-hold；租约事件不触发唤醒 |
| 3 | belt daemon 与触发拓扑（watchdog/epoch re-exec） | 12_belt_daemon_trigger.md | 🔄 | 漏唤醒窗（租约释放不 poke）；30s 空转零动作 |
| 4 | 落地执行体 landing（worktree 同步/materialize/门禁调用） | 14_landing_executor.md | 🔄 | 111 文件批磨 116 分钟死在终点；无 checkpoint |
| 5 | 门禁链全集（pre-commit hooks + commit_gates + registry） | 15_gate_chain.md | 🔄 | 杀手榜：PRECOMMIT-RUN 60 死/中位 6.7 分钟；顺序不分贵贱 |
| 6 | 死信通道与告警（分类/requeue/升级铃） | 16_deadletter_alerts.md | 🔄 | 285 死/日无人拉铃；告警只进 task_board 无 Owner 显式面 |
| 7 | 可观测面（status/租约文件/仪表盘） | 17_observability.md | 🔄 | processing=0 误导；无位置/ETA/租约持有者 |
| 8 | 直连/前台路径与会话-claim-心跳 | 18_direct_session_claim.md | 🔄 | 直连大提交绕队列直接占租约；processing=0 与租约被持并存 |
| 9 | worktree 隔离层（sync/materialize/合并回主区） | 19_worktree_layer.md | 🔄 | 每文件操作成本；clean -fd 互踩史；requeue 快照重建坑 |
| 10 | 业界对标（全网向：merge queue/bors/lint-staged/lease 调度） | 20_external_benchmark.md | 🔄 | Owner 自裁框架要求：机构实践/量化社区/GitHub 开源 |
| 11 | 数据考古批（09-21/22 全量死信+done 语料） | 本文档 §3（主会话亲挖） | ✅ | 数据地基，支撑 SC-3/SC-4 裁定 |

## §2 批次志（mining SOP §4 四类批次落账）

| 批次 | 类型 | 范围 | 产出 |
|------|------|------|------|
| 批① | 三重扫描批（按生产者=代码模块逐家过） | 环节1-9 各路子代理，B2 在飞 | 各环节 A-F 节 |
| 批② | 案例批（09-21 队列死亡螺旋日反向拆解） | 主会话 B3 考古统计 + 各环节背景注入 | 杀手榜/链长/时长分布 |
| 批③ | 考古批（66 号文 v1.2.0 + gate_registry + 死信 triage 档） | 各环节文档 C 节引用 | 设计原意 vs 现状差距 |
| 批④ | 需求批（消费端=等待方会话缺口反向挖） | 环节7/10 | status 增强+对标移植清单 |

## §3 数据地基（09-21 00:00 → 09-22 04:00 语料，机械统计）

- 语料：dead 301 项 + done 97 项（q-20260921-*/q-20260922-* 全量 JSON 解析）。
- **死因门禁杀手榜 top12**：GATE-PRECOMMIT-RUN 60 ｜ CREATE-GUARD 32 ｜ RULING-REFERENCE 17 ｜ NO-BARE-SQL 15 ｜ ALGO-FLOW-LINK 14 ｜ EXEMPT-ZONE-FM 11 ｜ TRANSLATION-COVERAGE 10 ｜ landing PermissionError 9 ｜ NEW-FILE-DEPGRAPH 7 ｜ CAPABILITY-OVERLAP 7 ｜ IMPORT-INTEGRITY 7 ｜ DEPGRAPH-PRE-REGISTRATION 7。→ **T0 可预检家族（CREATE-GUARD/RULING-REF/NO-BARE-SQL/ALGO-FLOW/EXEMPT-FM/TRANSLATION）合计 99 = 33%**，全部可在入队面零租约成本拦截。
- **done 项文件数**：p50=3，p90=110，max=114（>40 文件的全部是 workclean 归档迁移批）→ 拆批阈值 40（SC-3）。
- **requeue 连败链**（死信带 requeued_from）：code-doc 20 连 / dloop 15 连 / data-fix 12 连 / workclean 10 连 / taskcards 9 连。
- **单会话死信总量**：workclean 73 / data-fix 58 / code-doc 39 / ulib 37 / dloop 27 / taskcards 26 / disk-ch 22。
- **时长**：死尝试中位 6.7 分钟、p90 37 分钟、max 200 分钟（unified-plan 0007，05:xx 悬停至 08:00 回收）；成功落地共 1142 分钟租约时长的等待延迟。
- **09-22 当天（凌晨）已死 16**：FILE-PLACEMENT-TTL / CREATE-GUARD / EXEMPT-ZONE-FM / GATE-PRECOMMIT-RUN / PERM-TRIGGER / NOTHING_TO_COMMIT 快照异常——病谱与 09-21 同源，改善正当其时。

## §4 封矿五判据动态核查（skeleton_policy §6）

1. 三扫收敛：批①（生产者逐家=环节1-9）+批②（案例）+批③（考古）+批④（需求）四批全跑后核查 ⬜
2. 增长曲线拉平：环节清单 9→11 后停稳（新增须过停止判据三问） ⬜
3. 🌑 清点：各环节 E 节"不做"项汇总（预检不收 T2+/不做活体抢占 SC-5/不做队列优先级插队——违 FIFO 不变量） ⬜
4. 封顶声明：环节层到此封顶；此后增长=环节内子类目→施工项实现，不再增环节；增环节须过三问并留理由 ⬜（B5 落）
5. 封顶≠死亡：红蓝对抗/实战事故可触发批次重开（演化留门）

## §5 计分板

环节覆盖度：11/11 已立案（含数据批✅1）；文档齐备 1/11 → 目标 11/11（B4）；施工项待 B5 设计定稿统计。
