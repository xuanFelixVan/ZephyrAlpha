---
ttl: task_bound
---

# 【交接令】业务层 Alpha 挖掘·续班（建议 sid：st-bizmine2-YYYYMMDD）

> 交接自 st-bizmine-20260919 通宵战（23 车道全收口，交付 commit 9c4d67195d）。本令=完整的后续工作清单+前因后果+纪律，照单执行零提问。

## 0. 模型路由（全程生效）
执行模型=Flash；一切复杂裁定（方案取舍/放行/翻案/Owner 门位）登记交 Max/Owner；禁自裁、禁虚报（做不到写"未达成+原因"）、遇阻登记跳过继续。

## 1. 冷启动（每次新 shell 必做）
1. `export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"`，`python --version` 须 3.12.x
2. `python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`（reaper 不活禁写）
3. 会话注册+心跳+commit 同 shell 链：`python -c "from zephyr.security.access_control.session_concurrency import SessionRegistry; SessionRegistry().register('<sid>', pid=0)"` + `nohup python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> . 30 &`
4. 宪法 AGENTS.md 全程有效。

## 2. 前因后果（先读，按序，约 40 分钟）
1. `docs/_working/bizmine_night/owner_package.md` —— 上一夜汇编包（八节：覆盖度矩阵/考试结果册/做T终局/方法论/施工队列/数据债/待裁定 8 项）
2. `docs/_working/bizmine_night/bizmine_wakeup_report.md` —— 交付报告（23 车道×hash+诚实遗留）
3. `docs/_working/bizmine_night/bizmine_general_order.md` —— 战役总令（§1 禁碰/§2 诚实条款/§4 纪律/§7 高波做T/§8 全夜条款，全部沿用）
4. `docs/_working/bizmine_night/redblue_report.md` —— 红蓝判定（12 车道 10 PASS/2 已修，零头条被攻倒；复权复核优先序）
5. `docs/_working/bizmine_night/bizmine_campaign_ledger.md` —— 全夜台账（每行带 commit）

背景一段话：昨夜以"灰度状态选因子"为主纲跑了 23 条车道：做T四环证据链判死 510300 系但三宇宙绿区（栖息地=588200/513330/300561 簇）；图形引擎 43 处定义偏离坐实"引擎错不是形态死"（塔形底/双底 PASS）；指标库 163 列全扫闭环；另类 9 面板首挖；销账+数据债 8 条已登记。到 Sharpe 2.0 的账：缺口 ≈4 条 @H2 OOS Sharpe≥1.4（≈1-2 场 80+ 候选战役），MID 荒漠靠组合层条件化不靠换因子。

## 3. 硬事实（实测勿重查）
- **灰度轴统一**=`c1_backtest.regime_state_anchored.vol_pct`（T-1 PIT，桶边界冻结 0.3200/0.7040）；`alt_regime_signal` 是猪周期/台风/BTC 分信号**非大盘态，禁用**；`judgment_*`/`regime_state_anchored` 是 plain MergeTree **禁 FINAL**。
- **成本双口径**：引擎现行=佣金万0.854 双边+¥5 地板+印花税万5+滑点五分位（Q1 7.24..Q5 2.34bp/单边；Q5 往返 8.4bp；`matching_logic.py:69-76`、`cost_model_calibration.py:229-235`）；Owner-001 口径=滑点 1.5bp。报告必须写明口径。
- **复权链坏**（adj_factor 恒 1，修复归整改队，禁碰 `data_handler.py`/`akshare_provider.py`）——一切日线结论"暂定"。
- **tick**：`tick_data` 88.57 亿行 2025-01-02 起 21 个月（个股全深；ETF 带后缀变体 338 天、UTC 错标 +8h 可修；2022-2024 无）；`tick_depth_5` 07-24 起；`l2_tick` 空壳。**E:/zephyr_cold_archive=分钟冷归档未挂库**（1min 2000-2021、ETF 1min 2005-2018）。
- **做T终局**：510300 系四环判死（成本数学→条件化 uplift 1.284<1.5→振幅经济学绿区→tick 执行全灭/改善上限 2.4bp）；死因=缺信号；隔夜情绪→日内 IC +0.262（ALT-B）是信号侧首线索。
- **查库**：`DatabaseService.get_clickhouse_conn()` 返回 clickhouse_driver.Client 用 `.execute()`（无 cursor/query）；uniqApprox 不存在用 uniqCombined；ReplacingMergeTree 带 FINAL，plain MergeTree 不带。

## 4. P0 任务清单（立即施工，按序）
**[T1] 图形引擎工单移交 + PASS 卡规范版对照**
- 11 条工单：`docs/_working/bizmine_night/pattern_definition_audit/pattern_definition_audit_report.md` §6（T1 CDL 上下文过滤/T2 塔形三段重写/T4 Hikkake 分档/T6 地天板方向反传一行修/T7 classic3 horizon/T8 平台突破死腿等）。图形线会话活跃→挂单移交；不活跃→报 Max 定执行归属（禁自改 src/）。
- PATX PASS 卡补规范版对照：塔形底/双底按 `pattern_definition_audit/reexam_canonical_vs_engine.csv` 口径重写规范实现，重跑窄考，出"引擎版 vs 规范版"双 verdict（引擎版数字偏乐观已证）。
**[T2] ALGO top3 落地**（伪码=`algo_mining/algo_mining_digest.md` §6；全队列=`implementation_queue.csv`）
- ①OFI 代理（tick direction→5/15min 订单流不平衡；universe=ETFT0 绿区簇+高波个股 top20）②A股开盘半小时日内动量（1min 4.7 年，Chu 2019 证据；与隔夜情绪因子条件化交叉）③VWAP 偏离条件化做T（标的=588200/513330/300561 簇；双成本口径；预注册卡先 frozen）。每件：预注册→沙箱考（筛≠考）→PASS 升待考池→E4。
**[T3] E4 正考收口批次**（入口=`python scripts/backtest/f06_e4_wfa_exam.py` 已验证可运行；输入绑 `data/strategy_intake` 若工厂车道仍占则登记等位）
- ①MID 三独立卡：缺口ATR分级/二进三断板/UTAD（卡=`mid_valley/prereg_card_mid_valley_top10.md`）②L1 risk_off 条件化池：CORREL/BETA（survivors 行已备=`volume_family_l1/e4_survivors_rows.csv`）③F top20 待考池按 |IC_IR| 序（`factor_sop_screen/screen_report.md`）。验收=verdict.md 落 `data/backtest_artifacts/runs/E4-*`。
**[T4] 图形快考双星升卡窄考**（PB 产物）：开收反转/向上（+29.6bp/10日、6/6 年）与枢轴反转/向下（+20.8bp、6/6 年）→预注册卡→NW/bootstrap 窄考（协议照 `pattern_narrow_exam/`）；规范实现并行防引擎伪影。
**[T5] BT-P0-003 pending 重考**：P-P2-01/P-P2-03 做T配对样本满 30 后复考（现 24<30 insufficient，销账批已写回标注）。

## 5. P1 任务（裁定解锁后施工，勿先斩后奏）
- [T6] 有界 tick 矩阵第一波：规格=`algo_mining/matrix_necessity_verdict.md`+`tick_matrix/tick_matrix_protocol.md` v1.0（36 格/波、秒级裁掉、BH q=0.10、功效门 120 日、跨轮累计 N 账）——**先经 Owner 批规格（裁定⑥）**。
- [T7] 组队复核 B-15：Owner 批后按 `regime_axis/teaming_regime_brief.md` 三档名单组装复核（MID 桶降仓/降换手条件化）。
- [T8] 塔形顶做空可交易性：融券费率/券源核查（裁定②）→通过则其复权复核提前。
- [T9] 币圈 funding carry 二期：maker/返佣通道成本重建+资金槽利用率模型（裁定③后）；HL 实际费率核实。

## 6. P2 数据债驱动（等数到位按 `src/zephyr/data/config/known_data_gaps.yaml` 触发）
- ALT-B 8 观察档扩样本（auction ≥120 日、hot_rank 约 2026-12 达标即重测）；TICKM 月度滚动（每月按协议重跑，亮点连续两月存活升池）；money_flow(44日)/margin(35日) 功效达标重考；research_report 全文 20GB 搬运后做文本情绪/目标价/相似度因子（LLM 走 LSG）；cohort_daily_ledger 建表后入挖矿池。
- **E 盘冷归档挂回（裁定⑦，数据线正门工单）**→挂回后=26 年分钟深度：波段/分钟因子有界矩阵+`kline_etf_daily` 重建（现 1675 只仅 ~57 行/只）。
- **复权链修复当日**：按 RB 优先序全量复核——塔形顶空头→塔形底/双底→R 幅度→S8→ETFT0 rv20→F/MID 池（这是全部"暂定"结论的解除条件）。
- 96 条缺检测器图形（图表48/structure31/trendline8/chanlun6/SR2/candle1+DL套件8，清册=`pattern_backfill/pattern_backfill_inventory.csv`）→引擎施工批（归属 Max 定）。

## 7. 纪律（硬约束）
- 改前 `python scripts/lock_files.py acquire <file> <sid>`；新 .py/.md/.yaml/.json 先 `python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <路径> --created-by <sid> --capability bizmine_alpha_mining`（token 载体 `capability_canonical_file_registry.yaml` 随批同落；持锁冲突等 5 分钟勿硬闯）；.md 带 ttl frontmatter、文件名字母开头纯 snake_case。
- 提交唯一正门：`python scripts/git_commit.py --session <sid> --files <逗号清单> --message-file <.runtime/tmp 下 UTF-8 文件> --enqueue --allow-non-worktree --allow-multi-domain --wait 900`；重试带 `--adopt-prior-work`；**commit 后必 `git log -1 --name-only` 核归属；提交输出勿用 grep 过滤（会吞错误行——昨夜起床报告因此漏入队一次）**。
- 预注册纪律：卡先 frozen 再取数；改卡=带日期修订附录禁静默改；筛≠考（IC 筛/事件研究只升待考池）；全部结果含 RED 入册；多重检验必报（BH-FDR/严格档）。
- 禁碰：AGENTS.md、`docs/03_modules/**`、TDM、`config/trading_decision_map.yaml`、`tasks.yaml`、`pipeline_events.py`、`apply_market_tables_ddl.py`、N-5 件、`data_handler.py`/`akshare_provider.py`（复权归整改队）、`data/strategy_intake/**`（动工前 git status 复核工厂车道是否已释放）；生产表只 append；测试写 tmp_path；LLM 走 LSG；临时件一律 `.runtime/tmp/`。
- 诚实条款：数字必须注明三口径（成本/复权/窗）；红蓝勘误下游 5 件修订在途（algo_mining_digest/etf_lane_report/indicators_sweep_a 卡/pattern_backfill csv/survivor_regime_report——动工前先看是否已被 owner 修订）。

## 8. 完成判据
P0 全落→循环检查连续两轮 0 问题（commit 祖先核实+产物在盘+队列无新死信）→红蓝一轮→GitCommitGateway 全落地→临时件清→交付报告（六要素照 `bizmine_wakeup_report.md` 体例）。P1/P2 未解锁的登记不算失败，禁代裁。
