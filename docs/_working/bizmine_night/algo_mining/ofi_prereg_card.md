---
ttl: task_bound
title: ALGO件① OFI成交签名代理 预注册卡（frozen，先于实验落盘）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（2026-09-19，W2-T2，sid=st-final3-20260919）
lane: algo_mining
sid: st-final3-20260919
design_source: algo_mining_digest.md §6.1（真源伪码段）+ implementation_queue.csv id=1
protocol: 判读门=|t|≥3.29 双侧 + OOS 同号 + 全波 BH q=0.10（族=12格）+ 功效门 桶n≥120日
---

# ofi_prereg_card.md — 件① OFI 成交签名买卖不平衡

> 本卡先于实验落盘（卡先 frozen 再取数）。修实现缺陷可，改 frozen 参数不可。筛≠考：PASS 只升待考池，不构成部署结论。

## 1. frozen 输入

- **宇宙（考试宇宙）**：ETFT0 宇宙C 高波个股 top20（frozen 名单，源 `.runtime/tmp/bizmine/etft0/etft0_universes.json` stock_selected，20 只：300333/300563/300469/300843/301396/300399/300561/301082/688205/301306/301000/300757/300781/300622/688183/301076/300071/603716/300287/300159）。
- **宇宙降级披露（frozen，先于测量）**：ETFT0 绿区簇 ETF（A 簇 4 只+B 簇 13 只）的 `tick_data` 覆盖仅 28 日（miniqmt 时代 2026-07-10 起；588200 仅 5 日），远低于 120 日/桶功效门 → **ETF tick 面不入正式考试**，仅作观察档披露。任务面「ETFT0 绿区簇+高波个股 top20」中可考部分=高波个股 top20（tick 深样本恰为个股，与 digest §6.1「tick_data（个股 2025-01 起 21 个月）」一致）。
- **窗**：IS=2025-01-02..2025-12-31；OOS=2026-01-01..2026-09-18。桶级统计用全窗（IS+OOS）保功效，IS/OOS 同号另报。
- **数据**：`c1_market.tick_data`（3 秒成交快照切片，非逐笔——schema 注释「时间戳(3秒粒度)」，如实声明粒度）；`c1_market.kline_daily`（ADV20/Amihud20 分母）；`c1_market.kline_1min`（次日开→收收益）；`c1_backtest.regime_state_anchored.vol_pct`（桶）。
- **签名规则**：direction=买盘→+1、卖盘→−1、中性盘/空串→tick rule 兜底（价升=+1、价降=−1、平=延续前值；日首行无前值→0）。bdpan 时代（2025-01..2026-05）中文标签；miniqmt 时代（2026-07-10 起）direction 全空→全走 tick rule（tickm 卡先例）。
- **聚合**：w ∈ {1min, 5min, 15min}；`ofi_w(t) = Σ_w signed_vol / ADV20_shares`；ADV20_shares = 前 20 个交易日 kline_daily volume 均值（PIT：仅用 t−1 及以前；不足 20 日→该日降级用可得日均值并披露）。
- **价格变动**：`delta_p_w(t) = (P_end − P_start) / tick_size`；P=窗内最后成交价；tick_size=0.01（20 只全为沪深个股/科创板股，tick size 统一 0.01；digest「tick_size_adjusted」的机械落定）。
- **主检验 H2（进族 4 格）**：每日 15:00 用当日累计 OFI（=全天 Σsigned_vol/ADV20_shares）横截面排序 → **次日开→收收益**（次日 1min：close@15:00/close@09:30 − 1，日内比率复权免疫）Spearman 秩 IC。日度 IC 序列：pooled + vol_pct T−1 三桶（0.3200/0.7040 frozen；桶(d)=vol_pct 于 d 的前一交易日行）。判读：pooled 与各桶 |t|≥3.29（双侧 0.1%，plain t 主判+NW(5) 稳健参照）+ OOS 同号 + 全波 BH q=0.10 + 桶 n≥120 日（全窗）。
- **辅助检验 H1（不进族，文献复现）**：per symbol-day OLS Δp_w ~ ofi_w（有效窗≥20 才计日）；β_i=日内均值再按票平均；横截面 Spearman(β_i, ln ADV20_i) 预期<0、Spearman(β_i, Amihud20_i) 预期>0（Cont 2014：slope∝1/depth）。报告 p 值与符号，不设 PASS/RED。
- **数据缺口（frozen 披露）**：2026-06 个股 tick 在库无空窗（探针：300561 该月 21 日在库；tickm 卡「2026-06 空窗」仅限其三 ETF 标的）；2025-10/2026-02 月内覆盖日偏少按实际天数处理；tick=3s 切片非逐笔（功效按可得粒度如实判读）。

## 2. 家底事实（探针在先，2026-09-19 probe1/probe2）

- 宇宙 20 只 tick 覆盖 2025-01-02..2026-09-18，每只 413-416 日、单日行数中位 ≈3100（300561）；direction bdpan 时代≈2.7% 中性盘，miniqmt 时代全空。
- kline_1min 同宇宙覆盖 2021-09-01..2026-09-18（4 只次新 2021-10..2022-11 上市起），241 bar/日（09:30 首根含竞价、15:00 末根）。
- regime vol_pct 2025+ 共 833 日：LOW 187 / MID 384 / HIGH 262（边界 0.3200/0.7040）。
- 功效预算：全窗 21 个月≈420 交易日/股，分 3 桶后每桶≈120-190 日，踩 120 日功效门（digest §6.1 预期一致）。

## 3. 本卡预承诺

1. 考试跑完后本卡不再修改；全部结果（含烂格/负结果）写入 `ofi_exam_report.md` 与 `algo_top3_results.csv`。
2. verdict 三态：PASS（全门过，升待考池）/ RED（门挂，如实入册）/ INSUFFICIENT（功效门不达）。
3. 数字三口径必注：成本口径（本件不涉交易成本，IC 为毛口径）、复权口径（日内比率=复权免疫；ADV 用未复权量额不受影响）、窗口径（IS/OOS 界定如上）。
4. 引用：Cont-Kukanov-Stoikov 2014（JFE）；多重检验纪律=algo_mining_digest.md §4（HLZ t>3.0/BH-FDR）。
