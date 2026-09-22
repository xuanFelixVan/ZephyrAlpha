---
ttl: task_bound
---

# 环节6：死信通道与告警升级

> 挖矿：子代理 2026-09-22 凌晨（python 只读统计 + task_board sqlite ro 取证）；主会话裁定融合。

## A 职责与输入输出

1. **死信通道（DLQ）**：单项 landing 失败→附 dead_at/dead_reason 移入 dead/，队列继续前进；环境失败（LandingEnvironmentError）→项退回 pending 绝不死信（09-10 851 项误死信事故的治本分界）。
2. **死因三分类**：classify_dead_reason 按 env 标记串（16 个）/item 标记串（11 个）归 env/item/other，先 env 后 item。
3. **requeue 闭环**：新 qid 排队尾、快照基于当前工作区重建、双向留痕、永不删除。
4. **积压告警（队列级）**：drain 收尾（lease 外）+health CLI：dead_total≥THD-ALERT-003(50) 且距上次≥THD-ALERT-004(6h)→task_board 专 task T-QUEUE-DEADLETTER 打标；冷却写 health_alert_state.json（单键覆盖）。
5. **堵点本告警（守护级）**：belt daemon 逐条记账+≥20 条未清/最老>24h 写 alert 行（R-06 档位冷却）。

## B 代码地图

scripts/commit_queue.py：229-262 死信标记/task id/常量；876-908 _notify_task_board_dead_letter（meta.task_id 存在才联动，宁漏不误）；1214-1233 死信移入+告警；1282-1395 requeue 全家桶；1501-1559 classify_dead_reason/queue_health（含最老项龄）；1562-1663 emit_dead_backlog_alert（阈值 fail-closed 统读 load_alert_thresholds，链路 fail-open 不阻断排空）；1403-1440 cleanup_done（dead/ 永不触碰）。commit_belt_daemon.py：55-66 堵点本常量；111-139 记账；142-243 自检+R-06。threshold_loader.py:62-149 fail-closed 统读。alert_threshold_registry.yaml:437-473 THD-ALERT-003/004。task_board.py:332-366 tag_dead_letter+task_events append-only。

## C 六向台账（关键发现）

- **② 下游消费=被动查询面**：task_board list --label deadletter、health CLI——**无主动推送**。09-21 实际拉铃 4 次（本地 01:52/08:05/14:30/20:33，task_events 40 行实证，计数 101→175→299→353）——**机制没聋，是 Owner 不看板就听不见**。
- **③ 真源例外**：死因分类标记串与 belt daemon 堵点阈值为码内常量（前者有 triage md 口径锚，后者 Owner 自裁留痕）；health_alert_state.json 单键覆盖不可考古；task_events 是唯一完整告警历史。
- **④ 测试**：死信不卡队/异常转死信/task_board 打标/requeue 全家桶/dead 永不清理专测/告警四例/daemon 冷却/注册表接线——全链有锚。
- **⑤ 断流实证**：堵点本 4172 行最后一条 2026-09-18T06:00Z，之后 385→386 条死信零记账——daemon 死亡（见环节3）。
- **⑥ 数据画像**：dead/ 385 项（0921=285、0922=16）；09-21 死因分类 item=260/env=7/other=18；**env 盲区**：7 项 reason 自带"退回 pending"字样却已死信（landing 侧口径漏）+9 项中文 PermissionError/2 项 WinError 206 不在标记表全落 other。**最长连败链**：st-dloop 0001→0015 共 13 连败 92 分钟撞 13 个**不同**门禁；带 requeued_from 的再死项 69 个（重入队高流失）。小时分布 24h 全有死亡，峰值 08 时 37 项。

## D 升级机会清单（R6 施工蓝本）

1. 【快】**THD-ALERT-005/006/007 注册表条目**（照抄 003 结构）：005=单日死信增量≥50；006=单会话连败链≥10；007=升级告警冷却 21600s。消费=load_alert_thresholds fail-closed 统读。
2. 【快】**挂载点选 drain 收尾的 emit_dead_backlog_alert 旁**（daemon 已死不可依赖；drain 收尾=每轮排空必经）：聚合当日新增+同 session 连败链，超阈写堵点本 alert 行+日期键专 task。
3. 【快】**防轰炸**：日期键状态（{date}_{type} 每类型每天最多 1 声）+档位翻转立即出声（R-06 先例）；task 侧依赖 task_events append-only 留痕（覆写型标签是"事后考古"体感根源）。
4. 【快】env 标记补盲：增补"拒绝访问"/WinError 5/WinError 206/文件名过长；修 landing 侧"退回 pending"措辞与行为不符。
5. 【快】queue_health 补 max_session_death_chain/per_session_top 两键。
6. 🌑 主动推送面（中午摘要/通知）：涉交互面设计+M10 边界——挂起，由"看板专 task 当天可见"替代满足 Owner 诉求。
7. 🌑 死信率 ratio 阈值：dead/ 永不清理使积压数只升不降；单日增量口径即治本，ratio 口径挂起。

## E 挖矿日志表

符号定位→标记表→告警实现→daemon 全文→dead/ 0921/0922 统计→285/90 核实→最长链解析→堵点本画像→task_board DB（40 行 task_events 重建全天铃声）→triage/purge 4 批 1016 行→测试清点→env 盲区复核。12 步全 signal。

## F 自审闸三态裁定（主会话融合）

- **施工（本战役=Owner R6 原文）**：THD-ALERT-005/006/007 注册表条目+drain 收尾聚合检查+日期键防轰炸+env 标记补盲+health 两键。
- **挂起**：推送面/ratio 口径。
- **封矿**：无（本环节无封矿项）。
