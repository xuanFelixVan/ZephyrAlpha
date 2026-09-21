---
ttl: task_bound
title: 深度审查作业簿——数据域告警出口
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：数据域告警出口（I20）

- 状态: **已审**
- 级别: P2｜类型: 管线
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/alerter.py:65`（Alerter 类）
- 生产调用方: scheduler（:441 check_daily_failure_rate + 全程 notify）、integrity_checker、quality_sentinel、supply_sentinel、backfill_checker、catchup_guard、ch_parts_monitor、consensus_crosscheck、breadth_freshness_alerts、alt_source_bootstrap、pf_alloc/crisis_gate（crisis_gate.py:373 以 failures/ 为正门）、promotion_advisory（:448 webhook 自降级）
- 测试文件: tests/zephyr/data/test_alerter.py
- 备注: 2026-09-15 Owner 裁定裁撤飞书/SMTP 外推通道，前端页面为准

## 1 对象快照

- 审查范围：`alerter.py` 全文 245 行：notify（日志+ERROR 级写 failures/*.json）、冷却去重（300s/任务）、check_daily_failure_rate（>5% WARN）、check_consecutive_failures（≥3 天 CRITICAL）、failures 目录查询/读取。
- 排除项：api_server 的 failures 消费端点（归 I26，只审契约）；retire_tmp_artifacts 的 90 天 TTL（旁系确认存在）。
- 测试覆盖概况：单测在；冷却行为/并发写/文件名边界未见专项。
- 材料包缺项：无近 N 天 failures/ 文件实况统计（运行时证据包缺失，用消费端代码佐证通道活性）。
- 变更热力：19 次提交，中高热区（2026-07-13 刷 3000 文件事故治本 + 2026-09-15 通道裁撤两次大改）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | check_consecutive_failures 全仓零生产调用方——蓝图 §6.5"连续 3 天失败→升级 CRITICAL"从未自动执行，升级告警承诺空转（孤儿方法，模式 #8） | alerter.py:195-218 + grep 全仓仅定义无调用 | P2 | `grep -rn "check_consecutive_failures" src/ scripts/` 仅本体+测试即证 |
| C 下游 | check_daily_failure_rate 用 WARN 级 notify——WARN 不写 failures/ 文件（仅 ERROR/CRITICAL 落盘），"单日失败率超 5%"汇总告警只进日志，**前端永远看不到**；返回 True+docstring"已告警"=假完成 | alerter.py:186-193（level=LEVEL_WARN）+ :119（仅 ERROR/CRITICAL 写文件） | P2 | 跑 `check_daily_failure_rate(100,10)` 后查 data/failures/ 无新文件 |
| E 对抗 | 冷却去重表 `_last_failure_ts` 纯内存：进程重启即清零——crash-restart 循环场景每次重启后首个 ERROR 必写文件，循环重启仍可刷量（2026-07-13 事故的残余面）；对比：cooldown 机制只治进程内循环 | alerter.py:85, 140-145 + 头注 :135（事故史） | P3 | 循环 kill-restart 进程各触发一次 notify，观察文件数线性涨 |
| A 深度 | notify 返回值语义三态混一：冷却跳过返回 False、写失败返回 False、INFO 级直接 True——调用方（scheduler 等）几乎全忽略返回值，"告警是否送达"无单一事实 | alerter.py:104-121, 142-144, 166-169 | P3 | code review；grep notify( 调用点几乎无返回值检查 |
| E 对抗 | 写文件非原子（直接 open(w) 无 tmp+rename）：前端 50 条读取窗口可能撞上半写文件——api_server 侧若有 try 可救，侧写竞态存在 | alerter.py:163-164 + api_server.py:1363-1375（消费端，归 I26 复核） | P3 | 写入循环中并发读复现 JSONDecodeError |
| B 上游 | task_id 未消毒直拼文件名：含 `/` 或 `\` 的 task_id 会让 open 失败（告警丢失仅 log.error）或路径穿越写逃逸目录（内部输入，低危） | alerter.py:149, 162 | P3 | notify("_x/y","e") 观察异常路径 |
| D 旁系 | 告警出口三轨并存：Alerter failures 文件、quality_sentinel、supply_sentinel、breadth_freshness_alerts 各自的告警面——本对象是"正门"（crisis_gate.py:373 认可），但供应链哨兵等是否全走正门未强制 | alerter 消费方清单（§头）+ quality_sentinel.py 等 | P3 | grep 各 sentinel 是否直接写日志不走 notify |
| A 深度(测试) | 单测未覆盖：WARN 不落盘断言、冷却跨重启语义、并发 notify | tests/zephyr/data/test_alerter.py | P3 | grep 测试无 WARN 落盘负断言 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 告警去重/抑制（alert dedup/inhibition window） | **对等已有**：业界（PagerDuty Alert Grouping、Alertmanager repeat_interval）与本对象 300s 冷却同思路；业界冷却状态持久化在服务端（重启不丢），本对象内存态=低于业界 | Prometheus Alertmanager 文档（--data.retention 持久化 notification state）, prometheus.io, 2025（本条受 WebSearch 429 限流影响未实时核验，URL=官方文档域） |
| 告警分级落盘（severity→sink routing） | **立卡候选**：业界路由表（WARN→聚合页、ERROR→工单）按级别分发不同 sink；本项目 WARN 只进日志与"前端为准"裁定冲突——建议 WARN 级也落 failures/（加 summary 标记）或前端单独拉日志 | 同上受阻口径 |
| 文件型告警总线（file-based alert bus 供面板消费） | 对等已有：在小规模单机部署里文件总线+面板轮询是可行模式（如 Netdata alarm 日志）；规模上限=50 条窗口（retire_tmp_artifacts.py:43 自述），当前量级适配 | 受阻同上 |

## 4 缺陷清单

1. **D-1（P2）升级告警（连续 3 天失败）承诺空转**
   - 现状→证据：check_consecutive_failures 零调用方；蓝图 §6.5 三条触发条件只落地了一条半（立即告警=任务失败 notify 路径有、失败率=有但 WARN 不落盘、连续失败=死码）。
   - 影响：慢性劣化源（连续失败但单日率<5%）永不升级，运营依赖人看前端列表。爆炸半径=数据域慢性断供发现延迟。
   - 建议修法：scheduler 日报钩子接 check_consecutive_failures（progress_store 已有 FAILED 历史，数据现成）；或删方法+改蓝图（消承诺漂移）。
   - 验证法：接线后构造 3 天 FAILED 历史跑日报，观察 CRITICAL 落盘。
2. **D-2（P2）失败率汇总告警 WARN 级不落盘，前端不可见**
   - 建议修法：该路径 level 改 ERROR 或 notify 增 加 `force_file=True` 参数；docstring"已告警"改准确表述。
   - 验证法：同轴 C 行。
3. **D-3（P3）冷却态内存化**：crash-restart 残余刷量面；建议文件系统冷却（failures/ 目录里 mtime<300s 的同名 task 文件即跳过）。
4. **D-4（P3）写入非原子+task_id 未消毒**：tmp+rename 原子写（对齐 file_utils safe_write 惯例）+ 文件名消毒。
5. **D-5（P3）notify 返回值语义混一**：区分 skipped/written/failed 三态或至少 docstring 说明。

## 5 挂起疑问

- "通知以前端页面为准"裁定的落地件是 api_server 哪个端点（1312 行附近疑似 /api/source_health）？前端是否真有页面渲染 failures（app_panel 侧未查，归 I27 顺带核）。
- promotion_advisory 提到的 webhook（:448）与"外推通道已裁撤"是否矛盾（webhook 属策略域还是数据域）。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 有结论；数学四问=失败率公式 trivial（total<=0 防御已有，alerter.py:183-184）。
- 长尾：failures/*.json 的磁盘量与 90 天 TTL 执行频率未实证；scheduler 内 20+ notify 调用点的 level 分级合理性未逐个审（抽样 5 处正常）。
