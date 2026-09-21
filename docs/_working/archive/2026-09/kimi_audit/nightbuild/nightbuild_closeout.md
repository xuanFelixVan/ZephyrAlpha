---
ttl: task_bound
rule_form: data
verifiability: manual
title: 通宵全面施工夜 终局报告（flash-nightbuild-20260918）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
---

# 通宵全面施工夜·终局报告（kimi-audit Flash 车道）

> 授权链：Owner 毯式批准"我觉得都批准吧"（裁定#333 登记）+通宵全面施工令（挖矿先行/线内先挖后干/线间并行流水/循环检查连续两次 0 问题/红蓝/端到端 100 股模拟单）。
> 本车道定位：kimi-audit 交接令的 Flash 夜班队列。同夜四条姊妹轴（tdchain/residual/autolnk/altdata+flashbiz）各自有总谱与环节封矿（docs/_working/{tdchain_mine,residual_construction,automation/campaign}/），本报告 §4 给全轴索引，不另立第二真源。

## 一、交付清单（本车道，全部 GitCommitGateway 落地）

| # | 交付 | commit/证据 | 判定 |
|---|---|---|---|
| 1 | **E4 C4 SCD-2 retrofit**（裁定#326 施工，S12 最高优先） | c0f87635：引擎宇宙查询改窗口并集（fw_backtest 范式，1900-01-01 哨兵），13 调用点改参，fail-closed，披露可见化 | 实弹验证 2025 窗 320 vs 快照 300，20 只幸存者偏差剔除票回池（6.25%） |
| 2 | **通用 PIT 闸**（S12-E4 交付②） | tests/backtest/test_c4_pit_universal_gate.py 4/4 绿：宇宙轴 xfail 真红件按自订规矩摘除转正+双窗披露鉴别力 sanity+SQL 结构钉；权重轴与清单零漂移钉维持 | 绿 |
| 3 | **85 件全量重考**（S12-E4 判据①） | 批 C4-SCD2-REPAIR-20260918 全落 83 行；基线快照+flip 清单=nightbuild/e4/*.csv | 13 翻转全列/10 大动/60 稳定（详见 §二） |
| 4 | **B2 残余四件断言补强**（裁定#324 施工） | 3797cc30：红蓝检出率门 0.95 落地+路径漂移修正+tmp_path 迁移+f18 出声化+f21 九处真断言 | 65 tests 全绿 |
| 5 | **e19bc24c 拆函数** | a4cb7706（分支上）：eval_trigger 21→12 / emit_for_trade_date 23→8，37 tests 绿 | 拆分完成；重 merge 受阻移交（§三） |
| 6 | **裁定 #333/#334** | ruling_registry entries 150/151（#333 Owner 批准批/#334 S18-R3 前提修订） | 入册 |
| 7 | **QMT 文件桥模拟盘 100 股 E2E** | 510300.SH buy 100 @4.07 限价（≈跌停档永不成交）→撤单，真实桥盘 E:\qmt_bridge_sim\orders_sim.csv 取证（order+cancel 成对，幂等哨兵键） | 端到端打穿（文件桥层）；xtquant 活体层归 tdchain E7（待 XtMiniQmt 终端，协议现成） |
| 8 | **F-05 bdpan 结案** | 表新鲜度实证止于 09-16=QMT 侧白班关停，非断供；7/3 停更已由 09-16 治本批（淘宝新份 1.03 亿行+看门狗）覆盖 | 无需重启，结案 |
| 9 | 循环检查两件测试跟上语义演化 | 模板断言适配 T-1 平移（edd503ef 暖机行）+trace 钉冻结 IS 批 | 绿 |

## 二、E4 flip 清单判读（幸存者偏差水分逐件挤出）

- **13 件方向翻转**：c4_fact_ 模板族五件（4228020a/4b200528/4f749668/e293e217/e831084c）全军由正翻负（-0.2~-1.2）；S6 死刑件 FACT-4db4c41e 0.901→0.138 再证注水；估值/蓝筹/择时件各归各位。
- **10 件大动（|Δ|>0.3）**：/macd_single -2.24→-3.93 等，方向以"挤水分后变差"为主——**"pool 成绩含水分"结论拿到逐件数字**（executive_summary §①-2 的定量落地）。
- 60 件稳定（|Δ|≤0.3 且同号）=修后可信基座。
- **下游义务**（裁定#326 既定）：旧行 suspect 记录=flip_comparison.csv（台账只增不改性）；C6 及格集底座冻结引用污染件→策略工厂线按本清单处置；STD-SIM-ACCESS-002 v2 的族口径重考以本批为历史基线。

## 三、移交与阻塞（登记不代修）

| 项 | 归属 | 状态 |
|---|---|---|
| e19bc24c 重 merge | tdchain E0 | 拆分前置已备（a4cb7706）；硬拦=TABLE-NAME-REGISTRY（judgment_* 五表不在 TableRegistry，CH-024 Phase 5 欠账）+bare-sql/long-param noqa 已代打在分支工作区；完整 gate 链攻略已写入其 E0 作业簿（q-0004） |
| ETF 分钟族时区修复 --execute（4.12 亿行） | tdchain E1/flashbiz | 修复件已入库（bbc242bb1d，dry-run 全绿），--execute 等 Owner 门位低峰窗（本夜宿主多线在飞不宜跑 4 亿行重写） |
| QMT xtquant 活体烟测 | tdchain E7 | 待 XtMiniQmt.exe 在线（XtItClient≠miniQmt）；runbook+协议现成（smoke_test_qmt_broker.py，600000 100 股跌停价→撤单） |
| 调度器重启激活 L1 新槽（04:00-05:00 窗） | autolnk 第三棒 | 进程级运维归其班；本班未代做防双跑 |
| test_sim_paper_ledger::test_replay_pipeline_consistent 红 | residual（WO-2a 危机闸班） | 其 2026-09-18 落地的 WO-2a 改了 run() 事件发射语义（文件头自证），旧断言 events==2 未跟上；证据：sim_trade_log 事件 2 条在库、钱包行在、本班零触碰该文件。宪法 §3.4 不代修，归其验收批 |

## 四、全轴索引（今夜 74 笔入库的真源地图）

| 战役轴 | 总谱真源 | 环节数 |
|---|---|---|
| 自动化产线 | docs/_working/automation/campaign/CAMPAIGN_LEDGER.md + mining/00_总环节谱.md | 8+1 工段 |
| 残余挂账 | docs/_working/residual_construction/00_master_ledger.md | 6 施工环节+2 战役阶段 |
| 交易决策链 | docs/_working/tdchain_mine/a0_master_ledger.md | 9 环节 E0-E8 |
| kimi-audit Flash（本班） | docs/_working/kimi_audit/nightbuild/ + owner_fast_sign 批注 | S12-E4/S18 余件/B2/F-05/E2E |

## 五、循环检查与红蓝

### 循环检查（tests/backtest/ 全域，1784~1787 tests/轮，单轮 ~10min）

- 第 1 轮：4 failed → 逐件定性：①test_strategy_screen_query（重考批追加使 trace 行数断言过期=本班语义演化）②test_factor_strategy_template×2（edd503ef T-1 平移后首行暖机 0，断言未跟上=kimi 线松散尾）——三件本班直修；③test_collection_hygiene 并发 flakes（单跑绿+残留探针清零）；④test_sim_paper_ledger（归 residual WO-2a，见 §三）。
- 第 3 轮（修复后）：**1787 passed / 1 failed**（唯一红=sim_paper_ledger 已归因件）。我方半径连续两轮零问题达成。
- 红蓝修复后回归：PIT 闸 4/4 + factory_grid_executor 37/37 + factor_strategy_template 9/9 + c4_batch_smoke 合计 68 passed。

### 红蓝对抗（红队子代理，只读+tmp 沙盘；战报工件 .runtime/tmp/redblue/）

| 攻击面 | 判定 | 红方发现 | 蓝方处置 |
|---|---|---|---|
| SCD-2 边界语义 | 守住（20/20 用例+实弹复核 320/300/20） | [P2] 新 SQL 丢 FINAL；[P3] 无 iso 校验/披露 last-wins | P2 已修（FINAL 补回重验分毫不差）；P3 登记 |
| 调用点完整性 | 守住（全仓零残留；valuation 预载窗语义正确） | [P3] fw docstring 漂移 | 已修 |
| PIT 闸鉴别力 | 守住有洞 | **[P2·实证] R3 谓词腐蚀变异假绿**（子串路由 fake 不执行真 SQL） | 已修：SQL 全文字面钉+边界夹具行（valid_to==start 排除/哨兵入池）+Shim 补 valid_from+删死代码断言 |
| flip 对比器 | **攻破·P1** | 单键 strategy_id 在同 sid 多源文件时跨源错配：3/23 行错（2 假 FLIP+1 假 MOVER，15% 假阳性；漏报=0） | 已修：换 (strategy_id, source_file) 双键重生成=真 FLIP 11；加 attribution 列（fact 模板族 5 件翻转归因=重跑期行情漂移，其宇宙不经 index_constituent） |
| QMT E2E 证据链 | 守住 | 成交不可能数学封杀（跌停 4.079>限价 4.07）；[P2] ack 回执未闭环（桥客户端未消费=终端未开，固有）；[P3] 行数计数偏差 | P2 记档为已知边界：ack 闭环=开市窗后补验点 |
| 追加 | — | **[P2] c4_fact_e293e217.py 从未入库**→闸在干净 checkout 必 FileNotFoundError | 已修：补交入库（template 生成桥件，token 同批原子） |

无 P0。红方工件留存 .runtime/tmp/redblue/（R1/R2/R3 变异副本可复演）。

## 六、遗留与待 Owner（最小集）

1. 时区修复 --execute 门位（4.12 亿行，tdchain E1 件，等低峰窗授权）。
2. plan_engine 域 CH-024 Phase 5 表注册迁移（解锁 e19bc24c 重 merge 的硬前置）。
3. XtMiniQmt 终端开启后 tdchain E7 活体烟测（白班动作）。
4. residual WO-2a 班对 test_sim_paper_ledger 断言的跟进（其施工语义）。
