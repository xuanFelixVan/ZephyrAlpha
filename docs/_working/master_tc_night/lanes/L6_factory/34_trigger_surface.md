---
ttl: task_bound
title: "C400 接线普查宽口径——34 环节自动化触发面清单"
created: 2026-10-07
sid: st-mastertc-l6
creation_token: 待随批登记（batch_creation_tokens prefix=docs/_working/master_tc_night/lanes/L6_factory）
---

# 34 环节自动化触发面清单（C400）

> **一句话**：从 132 环节总表机械筛出"有自动化触发面"的 34 环节，逐项标三态（已接线/待接线/不适用）——接线普查的宽口径触发面视图。
> **机械筛规则（可复跑，禁手工增删）**：
> ①规则A=per-F 挖干卷含"自动化触发"台账行且行内容非零/非弱（grep `docs/_working/fullconnect_campaign/**/NN_fXXX_*.md` 的 `自动化触发` 行，F100-F132 共 33 卷，其中 23 行判非零）；
> ②规则B=环节名含触发语义关键词（调度/订阅/编排/常驻/循环/任务，命中 F001/F010/F013/F014/F066/F076/F077/F082/F084/F090/F094 共 11 环）。
> A∩B=∅（F100+ 与 ≤F094 无交），合计 **34=23+11**。
> **真源**：132 环节真源=night_sweep 00_skeleton_nightsweep.md；触发行真源=fullconnect per-F 卷；悬空/半接线判据=recovered_wiring_gap_inventory_20260927.md §1.6。

## 三态读数

| 态 | 数 | 环节 |
|---|---|---|
| 已接线 | 22 | F001 F010 F066 F076 F077 F090 F100 F101 F102 F103 F104 F105 F106 F107 F109 F111 F112 F117 F124 F126 F131 F132 |
| 待接线 | 7 | F013 F014 F082 F084 F110 F122 F129 |
| 不适用 | 5 | F094 F116 F118 F119 F120 |

## 逐项清单（34 行，规则A/B 标注）

| 环节 | 名称（基态/优先） | 规则 | 三态 | 证据锚（触发面） |
|---|---|---|---|---|
| F001 | 多源采集调度（built/P1） | B | 已接线 | DataScheduler 调度面在岗；余量缺口=C192 对账（57 缺口表）非触发面缺口 |
| F010 | 行情订阅分发（built/P1） | B | 已接线 | 订阅分发链已通（night_sweep 状态轴=已通） |
| F013 | E0 算力调度心跳（partial/P1） | B | 待接线 | partial：心跳/调度半建成，编排缺口同 F42 族 |
| F014 | E1 想法进货编排（partial/P1） | B | 待接线 | partial：进货编排无日循环入口 |
| F066 | 回测预注册与七步循环（built/P1） | B | 已接线 | 七步循环链已通（状态轴=已通） |
| F076 | Windows 计划任务群（built/P1） | B | 已接线 | schtasks 族在岗（reaper live 实证；C152 时区修 L3 在飞） |
| F077 | 数据调度常驻（built/P1） | B | 已接线 | DataScheduler 常驻已通 |
| F082 | 订单与结算常驻（partial/P0） | B | 待接线 | partial/P0：常驻编排半建成 |
| F084 | 反馈循环 FBL（partial/P1） | B | 待接线 | partial：反馈循环无自动触发面 |
| F090 | Agent 编排与 A2A（built/P2） | B | 已接线 | 编排链已通 |
| F094 | AI 层七段循环设计面（design/P1） | B | 不适用 | design 面=设计文档非运行件，无可触发体（施工后重归册） |
| F100 | 评测演练调度族 | A | 已接线 | game_day_scheduler+async_monitor+commit_trigger（事件/演练触发）+cold_start 自举 |
| F101 | 规则与裁定体系 | A | 已接线 | GATE-RULES-INTEGRITY 每 commit 恒真触发（M3 §3.3 :6741） |
| F102 | 审计体系 | A | 已接线 | 事件触发（commit/landing/reconcile）+merkle_hourly 小时链+log_rotation/retention |
| F103 | 代码质量与克隆守卫 | A | 已接线 | 提交链预查调用（check_before_write）+self_scanner/canary；无独立常驻（设计如此） |
| F104 | 会话并发治理 | A | 已接线 | 事件/调用触发（register/heartbeat/claim/release）+锁 TTL stale 判活 |
| F105 | 门禁执行面 | A | 已接线 | commit-time 三道 in-process gate（--no-verify 不可绕）+post-commit 对账 |
| F106 | 翻译覆盖门 | A | 已接线 | TRANSLATION-COVERAGE 门（gate_registry.yaml:1871，priority=59） |
| F107 | 回滚自举链 | A | 已接线 | rollback_bootstrap+boot_hooks 挂启动链+rollback_scheduler |
| F109 | 注册表族治理 | A | 已接线 | master_index=生成器 auto 维护+季度净零审计窗；无独立守护进程（设计如此） |
| F110 | 错误码治理 | A | 待接线 | GATE-ERRCODE 判悬空（recovered inventory §1.6"悬空 4"：无钩子无启动器承接；仅单一脚本顺带调=半接线） |
| F111 | 前端桌面壳 | A | 已接线 | 桌面壳 spawn api_server 8890+serve_docs 8765（main.js:31）；services_registry 在册 |
| F112 | 导入即启 daemon 族 | A | 已接线 | 导入即启 3 daemon（bt-strategy-warm/data-asset-audit 10min/ops-alert-feed 30s） |
| F116 | 方法论路由册 | A | 不适用 | 非运行件零调度——触发形态=会话冷启动/开工前人（AI）读（README"何时必读"列） |
| F117 | 规则目录注册表 | A | 已接线 | rule_catalog_registry maintenance=auto（generate_rule_catalog 生成器链） |
| F118 | 离场预案册 | A | 不适用 | 非运行件（文档真源）；其描述的备份/离场自动化面归 F009（M5 实测黄，缺口记 F009 名下） |
| F119 | 双引擎自动化总计划 | A | 不适用 | 本册自身=task_bound 文件桥；其调度的自动化面=计划任务族（归 F076 名下） |
| F120 | M0 进货设计面 | A | 不适用 | 骨架本体=文档件（design）；nightly_sentiment 双真源已结案（Disabled 槽厘清） |
| F122 | 管线路由 M1-M11 | A | 待接线 | 编排侧=进程内 300s 轮询但宿主不活=整链 idle；选读路由侧零计划任务零槽（M5 §3·5） |
| F124 | 状态词表注册 | A | 已接线 | 事件触发=每次提交（STATE-VOCAB-REGISTRY in-process 门，gate_registry.yaml:1311） |
| F126 | 注册表代码锚 | A | 已接线 | 随提交链触发（registry_code_anchor_gate 提交门+align_all 对账窗） |
| F129 | 模型训练线 | A | 待接线 | 弱（人工/CLI 为主）：M1 dir6 wide/narrow 双 false，ml_train 无自动触发链 |
| F131 | 数据安全供给 | A | 已接线 | 有一条真链但为三跳传递（schedule.yaml:205-208 nightly_sentiment 槽）——脆弱性注记：三跳任何一跳断=静默断供 |
| F132 | CH 库治理 | A | 已接线 | 计划任务 ZephyrAlpha_ConfigCheck State=Ready（机器实测在案 §六 A2） |

## 口径与局限（诚实声明）

1. 本清单只回答"哪些环节**有**自动化触发面+各自接线态"，不重算 132 环节的四态总账（真源=night_sweep 总表，禁双账）。
2. "已接线"含带缺口注记的项（F001/F131）——触发链在岗≠链上无缺口，缺口归各卡（C192 等）。
3. F110/F122/F129 三项待接线为本清单净新增指证（此前散落 §1.6/F 卷，未成触发面专项清单）。
4. 复跑命令：对 33 卷 grep "自动化触发"行+对总表 132 行 grep 环节名关键词，规则与判据见册首。
