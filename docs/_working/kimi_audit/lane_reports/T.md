---
ttl: task_bound
rule_form: data
verifiability: manual
title: lane T 报告——做T v2 复活路径单假设窄考试（预注册、已执行、RED）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
status: 完成（考试已执行，结果 RED）
lane: T
inputs: docs/_working/kimi_audit/adjudications/S2_做T_v2_战役裁定书.md「若不同意应看什么数据」第 2 条；docs/_working/kimi_audit/S5_定尺子.md（DSR 族口径）
---

# lane T：「三重共振极值点出手」单假设窄考试

> 一句话：**判红**。预注册单假设「510300 的 15min 三重共振极值点出手有正毛边际」被数据证伪——毛边际 +0.88bp/边（门槛 >12bp），与无差别每日出手对照组（+0.87bp）统计上不可区分。S2 裁定书第 3 条理由（毛边际为负）**未被推翻，反而被单假设窄考试加固**。

## 1. 预注册与冻结

- 预注册卡：[`T_preregister.md`](T_preregister.md)（frozen 2026-09-17 19:4x，先于任何实验运行落盘）。
- 判据（冻结）：毛边际均值 >12bp/边 且 DSR(N_eff=1)>0.5 且成交率 ≥30% 且共振组显著优于对照组（单侧 Welch p<0.05）；成交 <4 笔=不可判=红。任一不满足=红。
- 与 S2 原文的口径偏差披露：S2 第 2 条写的是 DSR（N=4562 累计口径）>0.5；本 lane 按 lane 卡指令采用 S5 v2 族口径 N_eff=1，并同时披露 N=4562 参考值（结果 JSON 内）。

## 2. 替代口径（降级声明， frozen 入卡）

| 腿 | 原设计 | 数据现实（本班复核实测） | frozen 替代 |
|---|---|---|---|
| ① ETF 自身极值 | 15min RSI(14)≤20 或（20 根新低且量比>2） | `kline_etf_15min` 510300 满覆盖 | 原样（无需替代） |
| ② 板块共振 | 880 板块分钟级共振 | 880 只有日线（`kline_sector_880` 仅 period='1d'，469 板块 2020-03→2026-09）；且宽基 ETF 无干净 880 映射 | 000300 日线状态过滤：信号日前一交易日日线 RSI(14)≤35（用 T-1 防未来函数） |
| ③ 大盘分钟 | 000300 分钟共振 | 000300 分钟源 1min/15min/60min 全 EMPTY（S2 在案，复核一致） | 510300 自身即 300 代理 + 510500 同 bar 15min RSI(14)≤35 确认（bar 缺失=信号作废） |

局限（入卡原文）：②从分钟共振降为日线超卖背景过滤，粒度粗化；③测的是"宽基普跌共振"而非"300 指数自身分钟形态"；000300 分钟补全后应重跑本考试（脚本在案，一条命令）。

## 3. 地形自查结论（启动前实测）

- 510300 15min（≥2023-01）：14,445 行 / 884 交易日 / 日均 16.3 bar / 中位成交额 ¥1.86 亿/bar（p25=¥1.14 亿，p75=¥3.20 亿）；510500 同级满覆盖（中位 ¥0.90 亿/bar）。**15min 充足，不降 5/30min**。
- 510300 15min 振幅（≥2023-01）：中位 24bp（p25=17/p75=35），与 S2 的 26bp（471 日窗）互洽。
- **新发现地形缺陷（已处置）**：`kline_etf_15min.trade_time` 时区劈叉——2026-06-30 及以前为 UTC 墙钟误标 Asia/Shanghai（日内小时∈[1,7]），2026-07-20 起为北京墙钟（∈[9,15]），逐行规则「小时≤7 → +8h」归一化（两区间不相交，无歧义）；510500 同。本批 510300 15,405 行中 14,752 行被 +8h。另有个别重复 bar（2026-09-11 双倍），按 (symbol, bar_time) 保留 ingest_ts 最新去重（336 行）。**建议移交数据线登记 known_data_gaps**。

## 4. 实现与启动证据

- 孤立测算：纯 pandas + CH 只读（`get_db_service().get_clickhouse_conn(role='reader')`），不依赖仓内回测引擎；DSR 复用 canonical kernel `deflated_sharpe_from_moments` / `expected_max_sharpe_z`（`src/zephyr/simulation/deflated_sharpe_calculator.py:327/:242`）。
- 执行仿真（frozen）：买入限价=信号 bar 收盘−1 tick（¥0.001）；下一根同交易日 bar 最低价触及即成交，否则弃权；退出=min(成交 bar+8, 当日末 bar) 收盘；同一时刻一笔；每月≤8 次（按信号计，run 内 cap 从未触达）；信号 bar 为当日末 bar 作废。
- 对照组（frozen）：样本内每交易日首 bar（09:45）无条件出手，同一 maker/退出规则，无月上限。
- 后台启动：reaper keep 关键词 `t_exam.py` 已登记 `data/runtime/process_reaper_keep.txt`；nohup 后台跑；哨兵 `.runtime/tmp/exp/t/t_exam.done`。
- 运行台账：run1（PID 1053, 19:50:44）发现对照组窗口实现缺陷（pandas `.indices` 位置被当标签用，对照组实际落在 2022-10 起窗，产物已归档 `*_run1_ctrlwindow_bug.*`）；修 bug 后 run2（PID 1650, 19:53:13，~1s 完成）为**官方结果**。两次 run 共振组逐笔完全一致（共振路径无此 bug），frozen 参数零改动——修实现缺陷不构成再检验。

## 5. 官方结果（run2，2023-01-03 → 2026-09-16）

| 指标 | 共振组 | 对照组 | 门槛 | 判定 |
|---|---|---|---|---|
| 信号/出手 | 腿①候选 300 → +②38 → +③33 → 持仓互斥后下单 15 | 884 日 | — | — |
| 成交 | 14（成交率 93.3%） | 798（90.3%） | ≥30% | ✅ |
| **毛边际均值** | **+0.88bp**（中位 −1.43，胜率 35.7%，std 47.5bp，区间 [−62.4, +88.2]） | +0.87bp（中位 −2.31，胜率 48.0%） | **>12bp** | ❌ |
| 净边际（−8.4bp 成本参考） | −7.52bp | −7.53bp | — | 双负 |
| DSR（N_eff=1） | 0.527（per-trade SR=0.0185，T=14） | — | >0.5 | ✅（贴线过） |
| DSR（N=4562 参考口径） | 0.00016 | — | — | 披露用 |
| Welch 单侧（共振>对照） | t=0.0007，p=0.4997 | — | p<0.05 | ❌ |

**Verdict = RED**（5 门过 3 挂 2：毛边际 0.88≤12；对照组不显著差于共振组）。

## 6. 解读（读数纪律：只读作单假设考试结果）

1. 三重共振过滤把 300 个自身极值候选压到 15 次出手，**选择性是真实的**（成交率 93%，信号稀疏），但**边际不存在**：+0.88bp/边 ≈ 对照组 +0.87bp/边，极值点出手与瞎出手无差别。
2. 15min 级 maker 极值策略的毛捕获量级 ~1bp，对中位 bar 振幅 24bp 的捕获率 ~4%，离成本线 8.4bp 一个数量级——与 S2 §3 的波动预算测算（所需捕获率 32%）互相印证。
3. DSR(N_eff=1)=0.527 贴线过门是族口径的数学性质（N=1 时 DSR>0.5 ⟺ per-trade SR>0，预注册卡 §7 已披露），不构成经济性证据；真正的牙齿（12bp 门 + 对照组）都挂了。
4. S2「若不同意应看什么数据」第 2 条现已有了答案：**这条预注册单假设没有推翻"毛边际为负"**。S2 裁定书三条理由全部维持。
5. 若 Owner 仍要追：剩余空间只剩①更低的成本参数假设（滑点档重谈）或②非 15min 的级别（60min 中位振幅 54bp，但已接近波段非做T）——两者都超出本卡 frozen 范围，须另开预注册。

## 7. 产物清单

| 文件 | 说明 |
|---|---|
| `docs/_working/kimi_audit/lane_reports/T_preregister.md` | 预注册卡（frozen） |
| `.runtime/tmp/exp/t/t_exam.py` | 测算脚本（含 frozen 参数常量） |
| `.runtime/tmp/exp/t/t_exam_result.json` | 官方结果（run2） |
| `.runtime/tmp/exp/t/t_exam_trades.csv` | 逐笔成交表 15+884 行（时间/方向/限价/成交否/持有 bar 数/毛边际 bp/各腿指标快照） |
| `.runtime/tmp/exp/t/t_exam.done` / `t_exam.log` | 哨兵与日志 |
| `.runtime/tmp/exp/t/*_run1_ctrlwindow_bug.*` | run1 缺陷产物（审计保留） |
| `.runtime/tmp/exp/t/terrain_probe.py` / `.out` | 地形探测脚本与原始输出 |

## 8. 合规注记

- 全程零 git 写操作（遵 lane 卡）；reaper 计划任务存活确认（19:34 在跑）；Python 3.12.8。
- 新文件 `T.md`/`T_preregister.md` 的 creation_token 登记属 commit 域动作，由协调方统一提交时处理。
- `.runtime/tmp/exp/t/` 内容有 24h TTL 语义；正式留存=本报告+预注册卡（JSON/CSV 如需长期归档请 promote 至 docs/_working/）。
