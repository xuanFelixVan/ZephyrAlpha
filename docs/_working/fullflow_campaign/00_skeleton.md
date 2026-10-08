---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# 全流通战役·挖矿骨架（00_skeleton）

> 战役: fullflow_20261008 ｜ 总包: st-entrance-gate-20261007 ｜ 状态: 挖矿中
> 目标: 全链路环节无遗漏枚举 → 每环节挖干（六向台账）→ 封矿 → 施工/验证 → 全流通
> 挖干判据: 每本环节簿的六向台账齐 + 自审闸三态裁定（绿=可运行/黄=通道在但需数据或授权/红=断链）

## 一、环节枚举（骨架 v1）

全流通链路按数据流向分六段（S1-S6），每段一本环节簿：

| 段 | 环节簿 | 管线内容 | 挖矿代理 |
|---|---|---|---|
| S1 | 01_data_supply.md | 数据供给链：数据集成器（8 子命令）→ ClickHouse/PG 冷热库 → tick/分钟 K 线 → provider 层 | 子代理 D |
| S2 | 02_signal_tdm.md | 信号与决策：trading_decision_map（TDMAP-001）→ signal_ashare 源线六判据 → 策略 intake → 情绪概率 | 子代理 S |
| S3 | 03_backtest_exam.md | 回测与考试：layered_backtest → c4_exam × model_exam → factory_grid_executor 网格 → prereg 冻结 → GPU 路由 | 子代理 B |
| S4 | 04_risk_exec.md | 风控与执行：risk-status/regime → 仓位档 → ex_sor（滑点/下单执行）→ paper 模拟盘 | 子代理 R |
| S5 | 05_frontend_monitor.md | 前端与监控：dashboard api_server（路由面）→ 前端视图 → 台账/对账面 | 子代理 F |
| S6 | 06_gov_delivery.md | 治理与交付：数据→治理→交付链（本项目 L0 落地全程卡即其说明书，指向 commit_navigation_playbook L0-JOURNEY） | 总包自查（已有 L0 卡，薄补） |

## 二、六向台账模板（每本环节簿必填）

1. 输入面：上游环节与本段的输入物（数据/信号/配置）
2. 输出面：交付物与下游消费者
3. 入口面：可执行入口（CLI/API/模块 main）——逐个给出可运行验证命令
4. 模块面：核心模块清单（module_id → 路径）
5. 自动化面：哪些已自动触发/自动运行（永久系统四要素），哪些手动
6. 缺口面：断链/缺数据/缺授权/待办——每条标注三态色（绿/黄/红）

## 三、覆盖台账（封矿判据）

| 环节簿 | 状态 | 六向齐 | 自审闸 | 备注 |
|---|---|---|---|---|
| 01_data_supply | **已挖** | ✓（7 节齐） | **黄** | 15 入口实测（10绿4黄1红）；12 缺口原含 3 红，其中 **判重正门 check_tick_duplication 查询路径带伤已于 10-08 修复闭合**（三处手术 10-05/07 在码+复跑实弹 --month 202610 三腿全通 exit 0+守卫测试 11/11 绿，图12 DSC-GAP-DUPGUARD 已落改判注记，删重冻结令解除）；余 2 红=备份可还原性未证/研报停更；DataScheduler=Running 实证但 production 验证 10/43 |
| 02_signal_tdm | **已挖** | ✓（7 节齐） | 黄 | TDMAP-001 实测 186 节点/261 边/188 挂载（挂图手术已在 dev 二次确认）；loader+run_checks 全过（393 warn=63 红节点占位）；signal_ashare 149/149 import 绿；**源线判据 4/6 已落 dev（acure 车道落地中，A06/A09 不代修）**；吸收面卡点=592 策略 vs 10 候选 |
| 03_backtest_exam | **已挖** | ✓（7 节齐） | **绿**（主链健康） | factory_grid/c4_batch_screen/f06_wfa/run_fexam --help 全过；引擎 import 12/12；四张 prereg 冻结卡在簿；C4Exam+F06Grid 排程 Ready 有 10 月实跑日志；GPU 路由闭环。1 红=sector_prereg_exam_runner 无 --help 守卫（挖矿代理自误触开考已当场还原+核验无他队损失）+4 黄（model_exam 链三重断/ps1 旧路径/T3a-b owner_ruling_id 空/成本门 v1v2 双轨） |
| 04_risk_exec | **已挖+G7 已修** | ✓（7 节齐） | 黄→修复中 | ~~红洞 G7~~ **已修**（裁定#429 考古定谳 0.30 为 Owner 签发真值，代码 0.60→0.30 已入袋守卫 PASS）；G1 密钥轮换逾期仍 open（Owner 运维动作）；黄×5（熔断影子陈旧/regime 无日序/回撤无影子/daily_loss_limit 未配/模拟盘任务 DISABLED）；ex_sor 24 模块+风控 8 模块 import 全绿 |
| 05_frontend_monitor | **已挖** | ✓（7 节齐） | 绿（5 黄无红） | 路由 54 双实证；黄项=头注漂移×2（**10-08 已收口**：五写端点头注+35 启动项计数同步入码）+auto_scanned 待转正 |
| 06_gov_delivery | 已有 L0 卡 | ✓ | 绿 | 总包薄补 |

## 三·五、内收挂接（正典 taxonomy 指针——本骨架=现状验证视图，非新 taxonomy）

> 内收判据（可派生必并）：环节枚举正典=**F132 环节状态总表**（`docs/_working/night_sweep_20260929/00_skeleton_nightsweep.md`，132 行：已通64/开口57/等Owner11；基线 122=`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md` 13 段；+10=F123-F132 真源 `docs/_working/fullconnect_campaign/00_skeleton/00_skeleton_verified.md`）。本骨架 S1-S6 是 **2026-10-08 现状验证视图**（六段 roll-up+当日实测），正典块映射：S1↔数据供给块（F01-F12+F30-F36+F123/F125-F127/F131）/S2↔信号策略块（F13-F22+F29+F96+F120/F121+F129/F130）/S3↔回测考试块（F23-F28+F64-F75）/S4↔实盘执行块（F37-F63）/S5↔基础设施块子集（前端监控 F76-F86 等）/S6↔治理门禁块（F87-F110 等 49 卡）。工单真源=`docs/_working/fullconnect_campaign/00_workorders.md` §四（16 项已挖干未排产）。

## 三·六、移交与不可核登记（Owner 前置声明下按协议登记）

1. **G7 仓位硬顶漂移——已执行修复**（裁定#429 考古定谳 0.30 为 Owner 签发真值，代码常量 0.60→0.30 已入袋，守卫实测 PASS）；**G1 密钥轮换催办**仍 open（Owner 运维动作，非 AI 可代办）。
2. **四项不可核**（移交原会话/Owner）：291/21 对账裁决、车道A 批2 的 13 行终裁、D124、三张工单（全量考试/GPU 路由/整装回测）——全仓 docs/workbook/登记册/commit 史四轮检索无载体，**未落盘=对项目不可见**；工单域线索=fullconnect 16 项工单清单（无 D124 对应）。
3. **capital_flow_direction/news_sentiment 两判据**：实体全仓不存在（worktree/.aidrafts/staging/docs 均无），仅 st-tdm-chief 壳注册的 token+图谱节点在账——**从未建造**，token 可复用；归口=acure R 恢复道（信号三模块复活含此二）或后续车道按序新建。
4. **吸收面卡点呈报（R4，呈报不扩面）**：normalized 592 策略 vs translated_manifest 仅 10 候选——翻译/吸收产能=S2→S3 流量卡点（02 簿 §6 实测）。按交接令纪律**只登记呈报、禁自行扩面**：扩面排产（翻译吞吐/候选复筛/lane_f 6159 行消化序）须 Owner 批，随 10-08 晨报呈报。
5. **[完成] R1 三袋复核（st-fullflow2 10-08）**：entrance_gate_hook.py 含 L0-JOURNEY ✓／00_skeleton 含内收挂接 ✓／.zcode/config.json 含 PreToolUse ✓——前任三袋落地面抽查全过，未重做。

## 四、冲突纪律（五大队同窗）

- 各代理只写自己的环节簿文件，禁碰他段文件与共享登记册
- 主区在飞面（acure 源线落地、capability/ruling 登记册）一律不碰
- 交叉验证：他队已完成的成果按我方口径复验并记入缺口面
