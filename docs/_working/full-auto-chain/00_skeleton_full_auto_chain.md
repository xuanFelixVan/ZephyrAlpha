---
ttl: task_bound
title: 全自动链路骨架——数据接入到转正拍板全环节清单（挖矿总纲）
owner: ZephyrAlpha-Owner
session: st-fullauto-20260915
date: 2026-09-15
status: active
---

# 全自动链路骨架（挖矿总纲）

> **Owner 指令（2026-09-15 夜）**：管一头一尾——一头=数据接入（API/账号/充值），一尾=前端转正拍板。
> 中间从数据落地→找因子→生成策略→回测→模拟盘→整装回测（交易决策全景图）→转正建议弹出，
> 全程无人值守全自动。本班任务：先挖矿把每个环节挖干（骨架+每环节子文档，万无一失零遗漏），
> 封矿后按施工 SOP 施工打通，红蓝对抗+循环测试全绿，QMT 模拟桥 100 股端到端实测。
>
> **北极星校准（挖矿 SOP §6）**：Owner 终局只做四类事=①数据类网站账号注册 ②API 申请 ③各类充值
> ④策略转正审批。本链两端=①③（数据）与④（拍板），中间一切人工参与都是要消灭的对象。

## 1. 环节清单（骨架定案 v1，挖矿中允许增补环节，增补须在此表登记）

| # | 环节 | 一句话职责 | 当前自动化 | 本班处置 |
|---|------|-----------|-----------|---------|
| S00 | 数据接入【Owner 一头】 | API 申请/账号注册/充值/QMT 登录 | Owner 管辖 | 边界登记，不施工 |
| S01 | 数据落地管线 | 下载/清洗/入库/巡检/补缺 | ✅ DataScheduler 16 时段常驻 | 挖矿+核验 |
| S02 | 因子/形态发现 | 公式轨/智能体轨/图形态/另类道找候选 | 公式道✅周窗自动；图形/另类道=AI 班次 | 挖矿+登记欠账 |
| S03 | 因子验证与认证 | 四闸/Wilson/FDR/DSR/ANOVA/阴性库 | 四闸+认证✅日链自动；DSR 链欠账 | 挖矿+核验对链路阻断性 |
| S04 | 假说进货与预审 | 五车道进货+E2 预审 | ✅ 周窗自动 | 挖矿+核验 |
| S05 | 策略构造与翻译 | E3 construct+C3 翻译成考卷件 | ✅ 自动（已实弹 1 件） | 挖矿+核验 |
| S06 | 回测批考 | E4 C4 周六批考+过拟合闸 | ✅ 双窗编排就绪（C0 落地；首跑=09-19 周六） | 挖矿+核验 |
| S07 | 入库升格 | C6 intake：FDR 门→candidate→预授权 sim→挂图 | ✅ 事件自动 | 挖矿+核验 |
| S08 | 模拟盘开户 | 新 sim 策略自动开钱包 | ❌ 断（账本硬编码单策略） | **施工 C1** |
| S09 | 模拟盘运行 | 账本日跑/健康日刊自动跑 | ❌ 断（全部 manual CLI） | **施工 C2** |
| S10 | 模拟盘成绩评估 | 月度偏离/连续 pass-breach 判定自动跑 | ✅ C2 已落地（月度档+治理告警+run 档案） | **施工 C2 已收口** |
| S11 | 整装回测接线 | sim 毕业→TDM 全景图 sleeve→参与整装组合回测→出证据 | ❌ 断（挂图有、参与整装回测无自动接线） | **施工 C3** |
| S12 | 转正建议生成与推送 | 证据包+告警推送 Owner | ✅ C4 已落地（建议包+真通道推送+token 生产化） | **施工 C4 已收口** |
| S13 | 前端转正汇报页+拍板 | 转正建议页+Owner 前端拍板按钮 | ❌ 未建（后端 OwnerTokenGuard 已有） | **施工 C5** |
| S14 | 实盘流转与 QMT 桥 | 拍板后流转+QMT 模拟桥下单实测 | ❌ 未实测（100 股模拟单） | **施工 C6** |
| S15 | 实盘后监控与衰减 | E6 判死/E9 归因/衰减回灌 | 部分（转正后闭环） | 挖矿+登记，边际施工 |

## 2. Owner 口述流程修正（本班骨架据此定案）

模拟盘跑通 → **填入整装回测（交易决策全景图 TDM，作为 sleeve 参与组合）** → 整装回测完毕=成功
→（整装组合进实盘前模拟）→ **前端页面弹出转正建议** → **Owner 前端拍板** → 实盘。
即：不是单策略直进实盘，是整装进实盘。

## 3. 本班施工项清单（挖矿封矿后执行；封矿增补=挖矿实证推翻初始清单）

| 项 | 内容 | 对应环节 | 封矿增补说明 |
|----|------|---------|------------|
| C0 | **OOS 复测自动化（全链咽喉）**：run_c4_exam.ps1 加 OOS 批（IS 及格∩缺 OOS 口径）+IS 批改 --auto-only；emit 时序保证双窗齐才发 c4_batch_completed | S06→S07 | 挖矿实证：无 OOS 批→fetch_bothwin 恒空→周六首跑零入库，链路必断 |
| C1 | 模拟盘自动开户：intake 升格 sim 时 emit sim_wallet_due 自动开钱包；账本多策略参数化 | S08 | 挖矿实证：2 条 sim 实为 STR-E-TIMING-001+STR-VREV-025；账本硬编码 |
| C2 | 模拟盘四件套排班：sim_ledger_daily/sim_journal_daily 挂 daily_kline 唤醒（事件触发合规）；月度 sim_deviation_monthly+sim_governance 收尾（run 档案+真告警通道） | S09/S10 | 挖矿实证：真告警通道=data/alerter（飞书+SMTP），AlertManager 是内存假送达；sim_memo_monthly 机制存在但 last_audit 无键从未触发 |
| C3 | 整装回测接线：STR-* 翻译件面板适配器+TDM→framework_plans 方案表生成器+fw_backtest_due 自动触发+regime 日序供给+证据包落档 | S11 | 挖矿实证：runner=framework_composer.run_framework_backtest 已存在（分钟级），断三座桥=方案表无 STR- 条目/build()与 generate_target_weights 两套接口/零自动触发 |
| C4 | 转正建议包 builder（三路证据合流）+data/alerter 飞书推送+owner_token 签发校验（secrets+常量时间比对，升级 OwnerTokenGuard） | S12 | 挖矿实证：owner_token 现状=非空即真（lifecycle_fsm.py:76-81），必须升生产级 |
| C5 | 前端转正建议汇报页+拍板按钮：GET /api/promotion-advisories + POST /api/promotion-decide + web/pages/promotion.html + features/promotion/ + 五步登记（loader.js/index.html/app1.js/manifest/frontend_map） | S13 | 挖矿实证：app_panel.py 已废弃禁挂 Tab，新页走 web/；lifecycle 无任何 API 透出 |
| C6 | QMT 模拟桥 100 股端到端实测：smoke_test_qmt_broker.py（远价单→撤单→CANCELLED），护栏=只读 QMT_SIM_*+TCP 配对辨识+blocks_live_trading | S14 | 挖矿实证：MiniQmtBroker 全套成熟，现成 smoke 协议，欠实弹 |
| C7 | 顺路小件：S02-N2 MIN_INCR_IC 0.0→0.01；S03-N1 strategy_screen 台账加 num_trials 列；S05-G1 creation_token --created-by 硬编码死会话号修复；S07-G2 CLASS_NODE_MAP 补 multifactor 键 | S02/S03/S05/S07 | 挖矿顺路项，均小 |
| —— | 挂起（解锁条件已入各环节文档 §5/§6）：DSR 解冻三步/批次A首跑/ANOVA/PBO；图形道自动量化器；账本消费 build() 契约重构；FSM paper 态词表统一；真信号源盘中会话；decay_certifier 周扫 | S15 等 | 转正后闭环或依赖 Owner 解锁，非本班链路咽喉 |

## 4. 挖矿纪律（对本班全体子代理）

1. 每环节按挖矿 SOP 六向寻路（①上游②下游③算法/机制④后端⑤前端⑥数据字段），内部反查优先+全网搜索补盲。
2. 外部发现必须 URL+发布方+年份；终止=矿脉枯竭（六向全查无+无未挖长尾，无轮数/深度/候选数上限，noise 只记档不终止——mining_sop v1.3.0）；受阻如实记档不算查无。
3. 每环节产出子文档放本目录对应子文件夹；挖矿日志表 MUST 写进文档（无日志=没挖过）。
4. 施工项写 concrete（文件/函数/验收标准），作为施工班输入。
5. 子代理禁改代码、禁登记 creation_token（由主会话统一批量登记防并发撞写注册表）。

## 5. 环节文档索引

| 环节 | 文档 |
|------|------|
| S01 | S01_data_pipeline/README.md |
| S02 | S02_factor_discovery/README.md |
| S03 | S03_validation_certification/README.md |
| S04 | S04_hypothesis_intake/README.md |
| S05 | S05_strategy_construction/README.md |
| S06 | S06_backtest_exam/README.md |
| S07 | S07_registry_promotion/README.md |
| S08 | S08_sim_onboarding/README.md |
| S09 | S09_sim_operation/README.md |
| S10 | S10_sim_evaluation/README.md |
| S11 | S11_assembled_backtest/README.md |
| S12 | S12_promotion_advisory/README.md |
| S13 | S13_frontend_approval/README.md |
| S14 | S14_live_qmt_bridge/README.md |
| S15 | S15_post_live_monitoring/README.md |

## 6. 施工班收口状态（2026-09-15 回填）

施工班（st-autopipeline-20260915 及兄弟班）当日落地，逐项对账（各环节细节见对应子文档文末"施工班状态回填"节）：

| 项 | 状态 | 证据锚点 |
|----|------|---------|
| C0 OOS 复测自动化 | ✅ 已落地 | run_c4_exam.ps1 双窗编排：Stage1 IS `--auto-only --defer-emit`+Stage2 OOS `--auto-oos-pending`，双窗齐才 emit c4_batch_completed |
| C1 模拟盘自动开户 | ✅ 已落地 | intake emit `sim_wallet_due`+pipeline_events handler（ensure_wallet 幂等）；sim_paper_ledger 参数化 `--strategy-id` |
| C2 模拟盘四件套排班 | ✅ 已落地 | sim_ledger_daily→sim_journal_daily 挂 daily_kline 唤醒（date-marker 日幂等）；sim_deviation_monthly 月度档+串行治理建议器；sim_memo_monthly 毒丸病根修复（C2/X2）；sim_governance 补 Alerter 推送+run 档案 |
| C3 整装回测接线 | ✅ 已落地（实弹） | translated_strategy_adapter+generate_framework_plan_from_tdm（fw-tdm-current 14 员 Σ=1.0）+run_fw_backtest_due 自动触发；实弹整装回测 ok=true（242 净值点、面板对账逐位过、36.8s）；已知边界=MOMTREND 指数腿无 hfq 行情不成交 |
| C4 转正建议包+token 生产化 | ✅ 已落地 | promotion_advisory 三路合流 builder+decide 全链（sha256 常量时间比对→FSM→注册表 CAS→台账指纹留痕→alerter 回执）；OwnerTokenGuard 升级（ZEPHYR_OWNER_APPROVAL_TOKEN+fail-closed）；decide 头部 KillSwitch 总闸补齐。飞书/SMTP 凭据=Owner 侧唯一缺口 |
| C5 前端转正页+拍板 | ✅ 已落地 | web/pages/promotion.html+features/promotion+GET /api/promotion-advisories+POST /api/promotion-decide+五登记；api_server [INVARIANTS] 头注扩容留痕（第四写端点） |
| C6 QMT 模拟桥 100 股实测 | ✅ 已收口 | 2026-09-15 10:52 全通过（connect→查仓→SUBMITTED→CANCELLED），双终端 TCP 配对辨识过，证据=evidence/qmt-smoke-result.yaml；实战治本 price_type LIMIT 0→11（#ARCH-XTQUANT-API-COMPAT-001）+限价改跌停价申报 |
| C7 顺路小件 | 全部收口 | S02-N2 MIN_INCR_IC 0.0→0.01 ✅；S03-N1 strategy_screen num_trials 列 ✅（c4_batch_screen 落库+DDL 部署件）；S05-G1 --created-by 硬编码 ✅ 已修（factory_intake_pipeline.py 改读 ZEPHYR_SESSION_ID env，缺省=factory_intake_pipeline(auto)，测试 12 绿）；S07-G2 CLASS_NODE_MAP multifactor 键 ✅ 已补（multifactor→TDM-E-L3-07-2 打分链+候选态 None，test_auto_mount 24 绿） |

链路现状一句话：S01→S14 事件链全部接通，**首次全自动双窗批考+入库已改排 2026-09-15（今日）两发一次性点火：15:35 FactoryLaneC_OneShot0915（全链首跑）+ 17:30 C4Exam_OneShot0915（双窗批考+自动 OOS 补测+入库+开钱包）；周六 10:00/14:00 例跑原样保留**（排期依据=E0 算力闸纪律：交易日 15:30 前拒 heavy，收盘后点火为设计内通道；两任务已 Get-ScheduledTask 实测 State=Ready/NextRun=09-15 15:35 与 17:30/LastResult=267011 未运行）。C7 两件未修项已于 2026-09-15 补班收口（见上表）；飞书/SMTP 凭据=Owner 侧唯一剩余缺口。
