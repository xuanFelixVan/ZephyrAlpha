---
ttl: task_bound
---

# 业务层 Alpha 挖掘通宵战 · 总包令（st-bizmine-20260919）

> 战役窗口：2026-09-19 夜 → 09:00。总包=主会话（复杂裁定唯一归属）；车道执行=子代理（机械执行）。
> 立项依据：Sharpe2 差距三笔账（docs/_working/sharpe2_prep/a_reexam/gap_accounts.yaml）结论=**缺口在 alpha 不在工程**（alpha 缺口 0.796，距 2.0 剩 0.46）。本战役只做一件事：**供给新 alpha + 把既有弹药考完**。挖矿已由白日战役完成（P3 挂起件、撮合预审 305 条），本战役不重新挖矿，直接消费挖矿产物。

## 1. 禁碰清单（硬边界，违反即事故）

- 他队在飞件（今日实测 git status）：`src/zephyr/backtest/core/{decision_gate,engine_base,overfitting_detector,strategy_validation_pipeline}.py`、`src/zephyr/pf_alloc/**`、`src/zephyr/data/implementations/akshare_alt_provider.py`、`src/zephyr/data/source_health_check.py`、`src/zephyr/data_eng/data_anomaly_alerter.py`、`src/zephyr/regime/regime_feature_builder.py`、`src/zephyr/trading/**`、`scripts/backtest/f06_e4_wfa_exam.py`（他队 MM 在飞：**只可运行不可改**，运行前先确认可 import）、`data/strategy_intake/**`（工厂 intake 车道今晨 01:24 在飞）、`scripts/backtest/crisis_drill_monthly.py`、`docs/03_modules/**`、AGENTS.md、`config/trading_decision_map.yaml`、`src/zephyr/data/config/tasks.yaml`、`src/zephyr/strategy_pipeline/pipeline_events.py`、`scripts/ch/apply_market_tables_ddl.py`、N-5 纠缠件（22 schema 删+46 src 改+189 deeprev docs+stash aa43e3b530）。
- 复权链修复归整改队 T1：禁碰 `src/zephyr/backtest/core/data_handler.py`、`src/zephyr/data/implementations/akshare_provider.py`。
- BT-P2-056 做T 全矩阵已被裁定 #304 关闭（毛边际 +0.88bp/边 vs 门槛 12bp，Owner 快签 01 条），**禁复活**；复活唯一正路=新因子族新单假设预注册卡（Owner 快签 24 条），本战役最多起草卡片不执行。
- 组队部署=Owner 门位（B-15）：只备料，禁出部署结论。
- 禁裸 git commit / git add -A / reset --hard / stash；禁 `lock_files.py cleanup`；禁写生产库。

## 2. 复权缺陷诚实条款（全战役适用）

- 实证：`kline_daily.adj_factor` 恒 1（近窗 0/27795 非 1；akshare_provider.py:237 注释自曝 965 万行恒 1），回测日线路径未复权（data_handler.py:379-385 无 adj_factor 读取）。
- 因此今夜一切日线考试结论=**暂定（provisional）**，每份产出必须带「待复权链修复后复核」标注。
- 减缓措施：IC 快筛窗内剔除有除权事件的标的（`c3_fundamental.ex_dividend_event` 乘子链）；ETF/指数宇宙不受影响。

## 3. 车道清单

### L1 量能族第二批 14 档（P3-B-NARROWING 挂起件，弹药最熟，第一优先）
- 前置：同源预检+族内去重（P3 裁定书要求）→ 预注册卡 → 沙箱三关考试 → PASS 上 E4 正考。
- 真源：`docs/_working/kimi_audit/lane_reports/P3.md`（§P3-B-NARROWING+§1 再生脚本）、`docs/_working/kimi_audit/lane_reports/p3_prereg/`（卡片模板）、`.runtime/tmp/exp/p3/`（考试脚本模式，TTL 件可能已清，按 P3.md 内记录重建于 `.runtime/tmp/bizmine/l1/`）、候选清单=`docs/_working/sharpe2_prep/b_match_mine/prereview.csv` 中 indicator/volume+statistics 值得考档。
- 验收：14 档逐档有预注册卡+考试结果（PASS/RED+证据）；≥1 PASS 则产出 E4 survivors 行并尝试 E4 正考（f06_e4_wfa_exam.py 可运行时）；台账行全落。

### L2 因子库+图形库 IC 快筛（撮合预审 305 值得考的屏幕批）
- 范围：`prereview.csv` 中因子库值得考（~126）剔除 L1 已覆盖的 volume/statistics 档；图形库值得考（78）为延伸目标（事件对齐 IC，时间不够则留二波）。
- 协议（预注册后执行，禁改口）：Spearman 秩 IC，IS 窗 2019-01~2023-12，前瞻 5/10/20 日三档，月度聚合 IC_IR=mean/std，|t|>3 显著标记；**全部结果如实报告**（含负结果），按 |IC_IR| 排序；top-20 只升「待考池」不判 PASS（屏幕≠考试）；除权标的窗内剔除。
- 数据：`c1_market.technical_indicator`（162 列宽表，3.54 亿行，2019-01 起）分块读取 + `kline_daily`（FINAL）前瞻收益；中间缓存一律 `.runtime/tmp/bizmine/l2/`；CH 只读。
- 验收：screen_results.csv（全候选×统计量）+ screen_report.md（top-20 待考池+诚实节：多重检验警示/除权条款/数据缺口）。

### L3 组队复核备料（E7 评审包，Owner 门位只备料）
- 输入：`docs/_working/sharpe2_prep/a_reexam/reexam_results.csv`（17 幸存者）+ `teaming_schemes.csv`、`docs/_working/kimi_audit/lane_reports/P1.md` 重算件（机读 `.runtime/tmp/exp/p1/teaming_recalc.yaml`+`corr_matrix_u15.csv`，TTL 件若已清则从 reexam_results 底层日收益序列重算，如实记录重算口径）、`docs/_working/kimi_audit/lane_reports/P3.md`（13 E1C 清单）。
- 产出：①成本调整后逐成员稳健 Sharpe 表（含危机窗/最差滚动 12m）；②相关性聚类；③三档候选名单（稳健/均衡/进攻，全部标「观察档」，引裁定 B-15 待 Owner）；④到 2.0 的差距数学（给定池内相关性，还需多少条多少 Sharpe 的新 alpha 才够——给 Owner 一张「弹药需求清单」）；⑤E7 评审包 md。
- 禁部署结论；所有数字带复权条款标注。

### L4（二波，一波任一车道完成后由总包派发）
B2 板块族 L2 批脚本首批（BT-P1-008..013，880 日线 6.5 年齐）；一波 PASS 件的 E4 正考；红蓝对抗（PIT/过拟合/成本/多重检验四向攻击今夜产出）；销账（BT-P1-032 勘测销账+B0 15 条 exec_quality 判定写回，按 P6 lane 复算件）；做T 新假设卡草案（不执行）；起床报告。

## 4. 施工纪律（每车道必读）

1. 冷启动三件套：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"` → `python --version` 须 3.12.x → `python -m zephyr.trading.process_reaper --status` 须存活。
2. 会话注册+心跳+commit 同一 shell 链（90s 活性窗）：先 `python -c "from zephyr.security.access_control.session_concurrency import SessionRegistry; SessionRegistry().register('<sid>', pid=0)"` 再 `nohup python -m zephyr.gov_enforcement.rule_bridge.heartbeat_daemon <sid> . 30 &`。
3. 改前 claim：`python scripts/lock_files.py acquire <file> <sid>`；毕后 release。
4. 新文件（.md/.yaml/.json）必须 token 登记：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability bizmine_alpha_mining`，token 载体（capability_canonical_file_registry.yaml）随批同落；.md 带 ttl frontmatter、文件名字母开头纯 snake_case。
5. 提交唯一正门：`python scripts/git_commit.py --session <sid> --files <逗号清单> --message-file <.runtime/tmp 下 UTF-8 文件> --enqueue --allow-non-worktree --allow-multi-domain --wait 900`；失败重试带 `--adopt-prior-work`；commit 后必 `git log -1 --name-only` 核归属。
6. 产出落点：`docs/_working/bizmine_night/`（台账+卡片+报告）+ `data/backtest_artifacts/runs/E4-BIZMINE-*`（考试件）；临时脚本/中间件一律 `.runtime/tmp/bizmine/`（勿交付、勿提交）。
7. 数据库只读 FINAL；测试禁写生产路径；禁 LLM 调用（本战役不需要）。
8. 诚实条款：做不到/被拦/数据缺 → 如实写「未达成+原因」，禁虚报、禁降断言、禁改预注册协议口径。

## 5. 验收与收尾

- 每车道：产物落盘+台账行（`docs/_working/bizmine_night/bizmine_campaign_ledger.md`）+commit hash。
- 总包：循环检查连续两轮 0 问题；红蓝一轮；起床报告 `docs/_working/bizmine_night/bizmine_wakeup_report.md`（六要素：车道×状态×hash／证据链／端到端实录含失败／遗留声明／待裁定清单／清理确认）。
