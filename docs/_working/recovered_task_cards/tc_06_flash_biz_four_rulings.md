---
card_id: TC-06
title: Flash 业务施工班四项裁定题（ETF 时区放行 / E1C-09 / TradeRecord / 做T 配对）
verdict: 变形（置信度高：R1 已被执行完毕但三处登记未回写；R2/R3 存活；R4 变形——裁定 #304 已改号 #331 且新裁定 #386 禁复试图救；调查班本身零产物）
category: C类-文书收口批
priority: P1
size: 小（约半天文书作业）
source: 任务原文见 C:\Users\fanzi\Desktop\新建 文本文档 (2).txt 第 503-549 行（"六："节，原 st-review4r-20260920 调查取证班）
investigated_at: 2026-09-21
head_at_investigation: c968ad6042
ttl: task_bound
completes_when: 全部卡执行完毕并归档后转 archived
---

# TC-06 Flash 业务四项裁定题

> **进度提示（09-21 04:13 更新）**：已有接班会话产出四张裁定卡于 docs/_working/recovered_task_cards/tc06_ruling_cards/（r1 结案/r2 三选项/r3 立项/r4 变形重启，均 staged 待其落袋）——接手本卡先读这四件，勿重复产卡；剩余动作=Owner 对四卡点单+连库复测待办（步骤 5）。

## 0. 一句话结论

原调查取证班（产四张裁定卡交 Owner）**零产物**——.runtime/tmp/exp/review4r/ 不存在、git 零提交、docs 零归档。而且四题的客体现状在任务书写后已大幅变化：R1 的 ETF 五表时区修复**已于 09-18 由 st-tdchain 车道执行完毕**（4.12 亿行转正、备份在库），只是 known_data_gaps/实验台账/原工单三处登记都没回写；R4 的判据脚本与基线快照随 .runtime/tmp/exp/ 整棵消失，且做T 复活的引用口径已从裁定 #304 改号为 #331，另有新裁定 #386 判"300ETF 波段策略禁复试图救"。本卡的活=半天文书：R1 结案回写 + R2/R3/R4 三张裁定卡按新基线产出。

## 1. 背景与来龙去脉

前任 Flash 业务施工班（st-flashbiz-20260918）交付五份作业簿（biz1-biz5）后，交接令要求纯只读调查班对四项出裁定卡（禁自裁执行）：R1 时区修复放行、R2 E1C-09 存疑件后续、R3 TradeRecord 扩展立项、R4 做T 配对与零星异常。

## 2. 调查结论（2026-09-21 实测）

| 原文声称 | 实测现状 | 证据 | 等级 |
|---|---|---|---|
| 三笔前任提交未回退 | 7c9022f1/bbc242bb1d/4cceae33a1 全部 HEAD 祖先 | merge-base --is-ancestor 三笔 YES | A |
| known_data_gaps 含两标记 | 都在：bt_trade_log_attribution_fields_missing（status=no_source）、etf_minute_tz_split_pre_202607（status=monitoring）；工作区与 HEAD 零差异 | git show HEAD:src/zephyr/data/config/known_data_gaps.yaml | A |
| R1 修复待 Owner 批 | **已死（已执行）**：60ed3aa49c（09-18 07:22，HEAD 祖先）=执行终态；tdchain 作业簿回写五表对账（1min 修复 326,301,055 行…60min 5,962,194 行），五表 remaining_utc=0，备份 *_tz_bak_20260918 在库，RULE-DATA-OPS 三步验证全过。脚本在盘 scripts/ch/repair_etf_minute_tz_split.py | commit + docs/_working/tdchain_mine/e1_tdata_infra/workbook.md:38-48 | A |
| R1 登记一致性 | **脱节**：known_data_gaps 仍写"monitoring 等 Owner 批准"；归档 biz5 工单停点声明、experiments_ledger.md 第 61 行也仍"staged 等 Owner 门位"——三处登记均未回写已执行终态 | gaps 相关行 vs 60ed3aa49c | A |
| R2 E1C-09 档案 | 完全吻合且未动：verdict=存疑、can_deploy=false、折 2 Sharpe -1.953/maxDD -40.44%、DSR 0.732；E2/E3 无人开工（git log --all --grep E1C-09 仅 flashbiz 两笔）；预注册卡在盘 | data/backtest_artifacts/runs/E4-E1C09-P3-E1C-09/verdict.md | A |
| R3 TradeRecord 缺口 | 存活未施工：TradeRecord=src/zephyr/backtest/io/backtest_result_sink.py:70，已有 decision_price/order_type 字段位但**无 algo_id**；最新产物 order_type 恒 market、algo_id 全空；F03 判据件随 .runtime/tmp/exp/ 整棵消失；重建源=P6.md 判据节+gaps resolution_plan 文本完备 | 读源码 + grep 产物 | A |
| R4 做T 配对 | 变形：cost_trio_exam.py 与基线快照均不在（tmp 被清）；biz2 报告已 git mv 归档（7f1b68f384）；**裁定 #304 已改号 #331**（renumber_note 在册，09-20 P7 批量追认）；**新裁定 #386**：S-OWNER-001（300ETF 波段+底仓T）E4 OOS 不及格禁复试图救；kline_5min 8,195 零星行仍无独立登记条目 | ruling_registry 相关行 | A |
| 裁定卡产出面 | 零产物：review4r 目录不存在；git log --grep review4r 零提交；docs 无四卡归档 | ls + git log + grep | A |

### 病根

1. **登记闭环机制缺"执行回写"腿**：R1 从登记（04:36/05:16）到执行（07:22）仅隔 2 小时，但执行班只回写自己作业簿，不回写 known_data_gaps/原工单/实验台账——三处真源同时过期，这正是本任务被派出的直接原因。
2. .runtime/tmp 承载了不可再生判据（F03 件、cost_trio 脚本与基线快照），被清后 ledger 里指向 tmp 路径的产物锚全部悬空——**重建时判据件必须落 docs 或 scripts，禁落 tmp**。
3. 裁定引用无稳定性保障：#304 改号 #331 后，owner_fast_sign/归档 biz2/ledger 的旧引用未批量勘误，下游按旧号引用会错引。

## 3. 上下游

- 前置依赖：无硬前置（全部文书）；R4 的复测需连 CH（列待办，不阻塞出卡）。
- 下游消费方：Owner 四卡裁定；R3 挂 X 流验证批；R4-C 的 kline_5min 工单移交数据线；TC-10 的 P2 小活须吃本卡的 #331/#386 口径。

## 4. 剩余工作清单（可执行）

| 步骤 | 做什么 | 涉及文件全路径 | 验收判据 | 路由 |
|---|---|---|---|---|
| 1 | R1 结案卡+登记回写：known_data_gaps 该条目 status 改 resolved+补执行证据（60ed3aa49c）；experiments_ledger.md 回写 | src/zephyr/data/config/known_data_gaps.yaml、docs/_working/kimi_audit/experiments_ledger.md | 三处登记与执行终态一致；备份五表物理删除留 Owner 门位 | Flash 施工+Owner 确认 |
| 2 | R2 卡照产：选项 A=挂起等新数据/补样本重考；B=立项 E2/E3 走完整通道；C=放弃候选——各选项依据+建议+理由，引用预注册卡原文 | data/backtest_artifacts/runs/E4-E1C09-P3-E1C-09/、docs/_working/kimi_audit/lane_reports/p3_prereg/P3-E1C-09.md | 四值复核通过并与 P3 登记侧对照（oos sharpe 2.027/IS 1.469/DSR 0.732，全容差内）；禁改任何放行状态 | Owner 裁定 |
| 3 | R3 卡修正基线后产：注明 F03 原件已失、判据从 P6.md+gaps resolution_plan 重建；工作量=引擎产侧真实 order_type 枚举+algo_id 落地 | docs/_working/kimi_audit/lane_reports/P6.md、known_data_gaps resolution_plan 节 | 卡中基线与当前 HEAD 一致 | Owner 裁定（建议 A=挂 X 流验证批） |
| 4 | R4 卡变形重启：重建 cost_trio 判据（落 docs/scripts 禁 tmp）；#304 引用全部改 #331+勘误注记；披露与 #386"禁复试图救"的张力；kline_5min 8,195 行另开工单选项有效 | 新卡落 docs/_working/（禁 .runtime/tmp）；引用 docs/_working/archive/2026-09/flash_biz/biz2_t0_pairs_disclosure.md | 样本大于等于 30 复测需重建脚本后连库（列待办） | Owner 裁定 |
| 5 | 需连库复测项（写入卡待办，不阻塞）：五表 remaining_utc=0 抽验、kline_5min 零星行是否仍 8,195/扩大、*_tz_bak_20260918 五表在库核验 | CH（经 DatabaseService 只读） | 复测结果回填卡片 | Flash（连库时） |

## 5. 与其他任务卡的关系

- TC-01：其 A14 裁定编号链结论（#331 勘误+P7 追认）已被本卡独立实证，可直接互引。
- TC-10：P2 小活（做T/E1C 域）必须吃本卡的 #331 改号与 #386 禁复试图救口径。
- TC-08：B20（crisis_gate 日期修复）与四卡无直接交集，但同属"登记不回写"病灶家族。
- TC-04：S18-R1~R4 是另一族裁定书编号，勿与本卡四题混淆。

## 6. 风险与避让红线

1. 四卡引用一律写归档新路径 docs/_working/archive/2026-09/flash_biz/*（旧路径已 git mv 成死链）。
2. 判据件重建禁落 .runtime/tmp。
3. known_data_gaps 改前 claim + safe_write_text CAS + 进程外复核（~780 脏条目环境）。
4. R2 禁改任何放行状态（verdict/can_deploy 只读）。
5. 勿把 S18 族编号当本四题。

## 7. 执行冷启动提示

按 AGENTS.md 第 0 节冷启动；连库只读查询走 DatabaseService；长查询先报预计耗时；产出文档落 docs/_working/ 子目录（禁根平铺、禁 .runtime/tmp）。
