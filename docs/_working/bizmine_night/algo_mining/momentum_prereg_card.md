---
ttl: task_bound
title: ALGO件② A股开盘半小时日内动量 预注册卡（frozen，先于实验落盘）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（2026-09-19，W2-T2，sid=st-final3-20260919）
lane: algo_mining
sid: st-final3-20260919
design_source: algo_mining_digest.md §6.2（真源伪码段）+ implementation_queue.csv id=2
protocol: 判读门=|t|≥3.29 双侧 + OOS 同号 + 全波 BH q=0.10（族=12格）+ 功效门 桶n≥120日
---

# momentum_prereg_card.md — 件② 开盘半小时→尾盘/剩余段 日内动量

> 本卡先于实验落盘。修实现缺陷可，改 frozen 参数不可。出处：Gao-Han-Li-Zhou JFE 2018（市场版）；Chu et al. 2019 JEF（A 股个股版，动量+极端档反转凹型）。筛≠考：PASS 只升待考池。

## 1. frozen 输入

- **数据**：`c1_market.kline_1min`（2021-09-01..2026-09-18，全市场 5852 票在库）。仅取 4 个时间戳 bar 的 close：09:30 / 10:00 / 14:30 / 15:00（09:30 bar close=开盘集合竞价价，探针已验 241 bar/日、09:30 首根 15:00 末根）。
- **市场版 H1（进族 1 格）**：r_first_mkt(d)=当日全市场等权 mean(c1000/c0930−1)；r_last_mkt(d)=等权 mean(c1500/c1430−1)，两比率同掩膜（标的当日两根 bar 齐全才入均）。日有效门：入均标的数≥1000。检验：①Spearman(r_first_mkt, r_last_mkt) 全窗/IS/OOS；②主判读=五分位价差：mkt_r_first 的 IS 期五分位边界（IS=2021-09-01..2024-12-31 上算，frozen 后 OOS 不调），Q5−Q1 日均 r_last 差的 t 检验（plain 主判+NW(5) 参照），|t|≥3.29 + OOS 同号（OOS=2025-01-01..2026-09-18）+ BH（族内第 5 格）。方向预期：动量（Q5>Q1，Gao 2018）。
- **个股版 H2（进族 4 格：pooled+3 桶）**：个股 r_first_i(d)=c1000/c0930−1 截面五分位 → 当日剩余段收益 r_rest_i(d)=c1500/c1000−1；日度多空价差 spread(d)=mean(Q5)−mean(Q1)（当截面有效 n≥300 才计日）；spread 序列 t 检验（pooled=全窗 IS+OOS 合并计功效，IS/OOS 同号另报）；桶=vol_pct T−1 三桶（0.3200/0.7040 frozen）。判读：pooled 与各桶 |t|≥3.29 + IS/OOS 同号 + BH + 桶 n≥120。
- **动量/反转分段点（Chu 2019 凹型，IS 期钉死）**：IS 期内检验 Q5 内部上沿（r_first 分位 0.9 档 vs 0.8-0.9 档）是否现反转（r_rest 由正转负）；分段点（若存在）只在 IS 上定，落盘为 frozen 值后 OOS 原样套用，禁 OOS 挑段。分段点属描述性披露（辅助检验），不改 H2 主判对象（Q5−Q1 价差）。
- **桶**：`c1_backtest.regime_state_anchored.vol_pct`（T−1 PIT：桶(d)=前一交易日行；20日HV的250日滚动分位）。
- **成本/复权口径（三注）**：本件为信号考试（IC/价差毛口径，不含交易成本——升待考池后由下游 E4/窄测定成本）；全部收益为日内同日比率（开→收/段内），复权链恒 1 不影响日内比率，结论不挂「暂定」条款但如实注明。

## 2. 家底事实（探针在先，probe2）

- kline_1min 全表 14.81 亿行、5852 票、2021-09-01..2026-09-18；样例日截面 4338-5558 票（2021→2026 递增）。
- 功效预算：IS≈800 交易日 / OOS≈430 交易日；桶级 pooled 全窗 n≈1230 日，三桶各≈270-570 日，功效门无压力。
- 宇宙C 20 只个股 1min 全覆盖（供件③复用），本件截面=全市场。

## 3. 本卡预承诺

1. 考试跑完后本卡不再修改；全部结果写入 `momentum_exam_report.md` 与 `algo_top3_results.csv`。
2. verdict 三态：PASS（全门过，升待考池）/ RED / INSUFFICIENT。
3. 与既有资产关系：与 auction_gap 当日回吐（ALT-B）互证只作讨论，不做 ETF 做T 判定（归 T 协议）；件②市场级符号另作件③入场过滤（卡③引用，不重复计检验位置——过滤用法属件③格）。
4. 引用：Gao et al. JFE 129(2) 2018；Chu et al. 2019 Journal of Empirical Finance；多重检验=HLZ t>3.0/BH-FDR（algo_mining_digest.md §4）。
