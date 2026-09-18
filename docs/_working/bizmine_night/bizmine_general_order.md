---
ttl: task_bound
---

# 业务层 Alpha 挖掘通宵战 · 总包令 v2（st-bizmine-20260919）

> 战役窗口：2026-09-19 凌晨 → 09:00。总包=主会话（复杂裁定唯一归属）；车道执行=子代理。
> v2 修订（Owner 睡前定调）：①做T 不放弃，走「行情条件化」复活正路；②战役主纲=**灰度大盘状态 → 选因子选策略**（Owner 原话：先算准市场状态，再按状态选因子，这套不通夏普永远上不去）；③补挖因子 SOP；④另类数据入挖。

## 0. 战役主纲：灰度状态轴（Owner 论点，本战役第一优先）

- Owner 论点：市场状态是**灰度**（连续），不是 A/B 二值；大盘灰度→板块灰度→逐级选择当下最适合的因子与策略；状态突变（震荡 50→单边 100）时因子与策略选择跟着切。79 严选只活 1 条的疑似病根=考试不看行情状态。
- 实测家底（侦察已证）：regime 模块族已输出**连续灰度**（`src/zephyr/regime/core/regime_detector.py` GaussianHMM 7 维概率+confidence_signal）；`c1_backtest.regime_state_anchored` 4469 行（2017-07..2026-09-18）、`c1_market.alt_regime_signal` 10425 行、`regime_snapshot_history` 3621 行（PIT）；判定台账三表（排班表）已在产（`c1_market.judgment_*`，09-18 已出真行五态"进攻"p=0.72）。
- **断环**：没有任何"状态×因子条件化考试"。本战役把这一环接上（考试层），不碰生产层。

## 1. 禁碰清单（硬边界，违反即事故）

- 他队在飞件：`src/zephyr/backtest/core/{decision_gate,engine_base,overfitting_detector,strategy_validation_pipeline,data_handler}.py`、`src/zephyr/pf_alloc/**`、`src/zephyr/regime/regime_feature_builder.py`（**只读**，他队在改）、`src/zephyr/data/**`、`src/zephyr/trading/**`、`scripts/backtest/f06_e4_wfa_exam.py`（只可运行不可改）、`data/strategy_intake/**`、`scripts/backtest/crisis_drill_monthly.py`、`docs/03_modules/**`、AGENTS.md、`config/trading_decision_map.yaml`、tasks.yaml、pipeline_events.py、apply_market_tables_ddl.py、N-5 纠缠件。
- regime 切换器（分支 ai/st-sowner002-20260916）**不 merge 不 cherry-pick**（tdchain 车道任务，未到窗口）。
- #ARCH-344（Regime 断供三腿）是生产层裁定项：只登记引用，不禁用不修改生产行为。
- BT-P2-056 做T全矩阵维持 #304 关闭；复活唯一正路=新单假设预注册卡（Owner 快签 24 条），本战役**只做条件化窄测试+卡片**，不做全矩阵，不动实盘/模拟盘。
- 组队部署=Owner 门位（B-15）：只备料，禁出部署结论。
- 禁裸 git commit / git add -A / reset --hard / stash；禁 lock_files.py cleanup；禁写生产库；测试/探针全部只读查库。

## 2. 诚实条款（全战役适用）

- 复权：`kline_daily.adj_factor` 恒 1（回测日线路径未复权），一切日线结论=**暂定**，每份产出带「待复权链修复后复核」。
- 成本双口径并存：引擎现行=佣金万0.854 双向+¥5 地板+卖出印花税万5+滑点五分位（Q1 7.24..Q5 2.34bp/单边，`matching_logic.py:69-76`、`cost_model_calibration.py:229-235`；Q5 往返 8.4bp）；Owner-001 口径档=滑点 1.5bp。做T 件另用 `ex_sor/services/t0_cost_model.py`（HIGH_LIQUIDITY=10bp）。报告必须写明用的哪个口径。
- 多重检验：状态分桶×因子数会放大假阳性——桶边界/规则一律在 IS 期钉死（预注册），全部结果如实报告（含负结果），筛≠考。
- 做不到/被拦/数据缺 → 写「未达成+原因」，禁虚报禁降断言。

## 3. 车道清单

### R 车道：灰度状态×因子 条件化考试（st-bizmine-r，第一优先）
1. 灰度现状评估件：7 维 HMM 概率 vs 五态判定台账 vs confidence_signal 的关系一页纸（谁生产谁消费、PIT 口径、断供三腿 #ARCH-344 现状引用）。
2. **核心硬产出：17 幸存者×状态桶条件化重算**——逐日 OOS 净收益在 `.runtime/tmp/sharpe2a_oos_nets/*.csv`（73 份，date,net，2024-01..2025-08；TTL 件若被清，从 `data/backtest_artifacts/bt-*.json` 的 equity_curve 重构并如实记录）× `c1_backtest.regime_state_anchored`（无 FINAL，plain MergeTree）状态序列 → 每策略每状态桶 Sharpe/胜率/占比 → 「哪个因子在什么状态下赚钱」矩阵（csv+md）。桶规则预注册：按主力状态概率或 confidence_signal 的 IS 期分位切 3 桶，边界钉死。
3. 结论回答 Owner 论点：幸存者收益是否集中于特定状态（若各状态表现接近则如实说"状态条件化暂无证据"，不硬凑）。
4. 组队备料 regime 版：三档候选名单（稳健/均衡/进攻，全标观察档，引 B-15 待 Owner）+「按状态切换」组队示意（不部署）+弹药需求清单（到 2.0 还差多少条多少强度的 alpha）。
5. 板块灰度层（时间富余才做）：880 板块日线（6.5 年）板块强度灰度 v0 定义+数据探针，只出设计段。
落点：`docs/_working/bizmine_night/regime_axis/`。

### T 车道：做T 行情条件化复活轴（st-bizmine-t0）
1. **主观做T方法库挖矿**（Owner 令）：A股主观做T手法清单（底仓T/正T反T/竞价缺口/开盘脉冲/尾盘异动/网格/事件驱动/涨停撬板等，每个=适用行情+信号+仓位+风控+失败形态）。来源三路：仓内（docs/_working/tv2 或 factory/t_v2 设计稿、Owner 愿景文档、daban 链文档）+全网搜索（主观做T方法、知乎/雪球若可及，来源如实列）+模型知识（标注来源级别）。币圈对应物专节：永续 funding、网格、maker-taker 返佣、清算链、7×24 无涨跌停结构差异。
2. **转换表**：每方法 → 所需数据（映射到本仓真实表/字段，用已盘家底：kline_etf_1min 40万行/日、auction_book 267万、tick_depth_5、funding、清算流等）→ 算法伪码 → 可考假设卡草案；挑 1-2 个最可考的升正式预注册卡。
3. **Regime 条件化做T窄测（预注册后执行）**：新单假设卡="510300 做T 仅在高振幅/高波动灰度状态执行，其余空仓"。用 `kline_etf_1min`（至 09-18）复测：无条件基线 vs 条件化，双成本口径（Q5 8.4bp 往返 + Owner-001 1.5bp 档），按状态桶分解毛/净边际。**即便为负也如实入册**——这是翻案或终结 #304 的正式证据。禁碰实盘/模拟盘，禁下单。
4. 币圈做T研究报告：现有币圈数据盘点（daily_crypto/funding 465 万行/Hyperliquid 清算流）+与 A股做T的结构差异+2-3 张可考策略卡（只设计，不回测不实盘）。
落点：`docs/_working/bizmine_night/t0_regime/`。

### F 车道：因子 SOP + 大海选 + 另类数据（st-bizmine-f）
1. SOP 审计+补链：现有覆盖=通用挖矿方法论（mining_sop_policy v1.4）+回测七步循环（sop_b_node_loop：假设登记/预注册/宽窄测）+策略入库（sop_c）；缺"假设→IC筛→预注册→沙箱→E4→组队"全流程缝合册与 regime 条件化条款。产出《因子挖掘 SOP v0.1》工作稿（落 `docs/_working/bizmine_night/factor_sop/`，转正升 sop/ 走 Owner 过目，登记待裁定）+《挖策略 SOP 缺口报告》。
2. 宽表因子 IC 大海选：`prereview.csv` 因子库值得考（~126，剔除 L1 量能 14 档）→ 总体 IC + **按 regime 桶条件 IC**（alt_regime_signal 日度状态）双版；IS 2019-01..2023-12，前瞻 5/10/20 日，除权标的窗内剔除；全部结果入册，top-20 升「待考池」。
3. 另类数据快筛（时间盒 ≤3 小时）：top5 面板各挑 2-4 个构造因子做 IC 探针——stock_indicator（11.5 年 pe/pb/mv）、consensus_daily（9.7 年 EPS 修正漂移）、dragon_tiger_seat（4.6 年席位净买）、money_flow（3.5 月，标注功效低）、margin_trading（2 月，备选）。零结果也入册（另类挖矿 0/5 前科，这次留正式台账）。
落点：`docs/_working/bizmine_night/factor_sop_screen/`。

### L1 车道：量能族第二批 14 档（st-bizmine-l1，二波发车，车位空出即上）
前置同源预检+族内去重 → 预注册卡 → 沙箱三关 → 报告加 regime 分桶段。真源：`docs/_working/kimi_audit/lane_reports/P3.md` §P3-B-NARROWING、p3_prereg/ 模板、prereview.csv。

### Wave 2（总包派发）：红蓝对抗（四向：regime 分桶多重检验/前视 PIT/复权/成本口径混用）→ 销账（BT-P1-032 勘测销账+B0 15 条 exec_quality 写回，总包亲做注册表件）→ 起床报告 `bizmine_wakeup_report.md`。

## 4. 施工纪律（每车道必读）

1. 冷启动：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"` → python 3.12.x → `python -m zephyr.trading.process_reaper --status` 存活。
2. 会话注册+心跳+commit 同 shell 链（90s 活性窗）。
3. 改前 claim（lock_files.py acquire），毕后 release；注册表等热文件只文本式追加（safe_write_text CAS）。
4. 新文件 token 登记：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability bizmine_alpha_mining`，token 载体随批同落；.md 带 ttl frontmatter、字母开头纯 snake_case。
5. 提交唯一正门：`python scripts/git_commit.py --session <sid> --files <清单> --message-file <.runtime/tmp UTF-8 文件> --enqueue --allow-non-worktree --allow-multi-domain --wait 900`；重试带 `--adopt-prior-work`；commit 后 `git log -1 --name-only` 核归属。共享注册表若被 st-bizmine-20260919 持锁，等待重试勿硬闯。
6. 落点：`docs/_working/bizmine_night/` 各子目录 + `data/backtest_artifacts/runs/`；临时脚本/中间缓存一律 `.runtime/tmp/bizmine/<lane>/`。
7. 查库只读 FINAL（judgment_* 与 regime_state_anchored 是 plain MergeTree **不带 FINAL**）；CH 分块读取防内存；禁 LLM 调用。
8. 每完成一段落盘一段（台账行+commit），防 sweep 吞文件；台账=`docs/_working/bizmine_night/bizmine_campaign_ledger.md`。

## 5. 验收与收尾

- 每车道：产物落盘+台账行+commit hash；总包验收。
- 收官：循环检查连续两轮 0 问题；红蓝一轮；起床报告六要素（车道×状态×hash/证据链/端到端实录含失败/遗留声明/待 Owner 裁定清单/清理确认）。

## 6. Wave 2/3 指令（02:5x 增补，车道收口后由总包调度）

- W2.1 验收：每车道完成 → `git merge-base --is-ancestor` 祖先核实 + 产物抽验 + 台账记验收行。
- W2.2 红蓝对抗（红队单列代理，四向攻击今夜全部产出）：①regime 分桶多重检验（桶数×候选数假阳性估算+桶边界敏感性重跑）；②前视/PIT 抽查（T-1 落桶是否被违反、IS/OOS 渗漏）；③复权敏感性（adj 修复后可能翻转的结论清单）；④成本口径混用与门槛一致性。蓝队=各预注册卡 frozen 一致性复核（卡先于实验、参数零改动）。输出 `docs/_working/bizmine_night/redblue_report.md`，可修即修，不可修登记。
- W2.3 E4 正考收口：L1/S/P/E 各车道 PASS 候选汇总 → 逐个上 E4（`f06_e4_wfa_exam.py` 可运行前提下）→ verdict 全量入册。
- W2.4 MID 洼地深挖：F 车道条件 IC 落地后，专挖「中波灰度桶 IC 强」候选 top-10 并卡片化（依据 R 弹药账：MID 是 15/17 条的收益荒漠=最缺新 alpha）。
- W2.5 Owner 汇编包：R 组队备料+今夜全部新证据（T 终结判定/各车道待考池/币圈卡实测）汇成单本 `owner_package.md`（E7 评审包形态，待裁定集中列，禁部署结论）。
- W2.6 销账（总包亲做注册表件）：BT-P1-032 勘测销账、B0 15 条 exec_quality 判定按 P6 复算件写回、B1 三传感器结果写回。
- W2.7 起床报告六要素收尾。
- 附记：T 车道 T3 官方判定=**TERMINATE**（高波桶 uplift 1.284<1.5 门；条件化后所需捕获率 35.5% 仍为可持续带 2-3 倍）——#304 证据链第三环闭合，A股 ETF 15min 级做T 建议终结；唯一数学绿区镜头（日振幅宽捕获）指向的剩余空间=更大级别捕获（波段/60min+，归 E 车道）与币圈 7×24（归 st-bizmine-cry 实测车道，funding 小时级 466 万行在库、清算流空表=数据缺口登记）。
