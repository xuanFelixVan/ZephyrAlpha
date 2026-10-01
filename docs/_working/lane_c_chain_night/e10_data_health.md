---
created: 2026-10-01
ttl: task_bound
title: E10 数据健康环普查簿（TI 214 列数值健康）
note: 20261001 删除事故后由总包按普查代理终报重建（原簿全文损失，核心实证数据保存完整）
---

# E10 数据健康环普查簿

## §1 含 Inf 列总表（12 列）

c1_market.technical_indicator 全列（215 基座列）× 全表 CH 列级 isFinite 普查：

| 列 | Inf 行数 | 归因 |
|---|---|---|
| pvt | ~257 万 | cumsum 累加无防护，单点毒化整链 |
| cti_12 | 89,537 | 递推分母病态 |
| correl_30 | 78,177 | 滚动相关除零 |
| vr_26 | 9,961 | 分母掩码缺失 |
| cvi | 12,309 | 同型 |
| vip_14 / vim_14 | 1,440 / 970 | 递推族 |
| pvi | 964 | cumsum 同型（NVI/OBV/AD/WAD 同型雷现值干净） |
| roc_12 | 24 | 除以近零 prev |
| trix | 12 | 多重 EMR 递推 |
| boll_pctb | 2 | 带宽除零 |
| md_14 | 23（daily 6 标的）+28（周月线） | McGinley 递推×价格断层（本战役根因，另有每事件前 ~28 根巨值发散带） |

全表 NaN=0（非有限值全为 ±Inf）。合计约 277.6 万 Inf 格。

## §2 高危交集（递推×Inf）

md_14、pvt、pvi 为"无防护递推/cumsum——单点脏值整链毒化"高危型；NVI/OBV/AD/WAD 同型但现值干净（潜伏雷，写链闸已兜底）。

## §3 断层普查（诱因面）

kline_daily 全历史单日 |涨跌幅|>50% 共 **788 行**，约六成集中 2020-2022 北交所挂牌/转板潮。md_14 六例 Inf 全部对应除权/拆股/转板型**真实公司事件**（如 920729.BJ 2021-05-13 44→12.6），非脏数据主导。处方落点=算法跳变免疫（已修）+复权口径（远期立项）。

## §4 复发机制（实证）

internal_compute_provider 的周末 full_refresh **周周重写 Inf**（md_14 ingest=09-21/22/27/28 连续四轮）。写链无 isfinite 闸。→ 只洗 DB 不修算法必复发。

## §5 修复处方与执行

- 算法修面 12/12 列：已落地（见 e10_fix.md，582c93ae）。
- 写链 sanitize_indicator_matrix 矩阵闸：已落地（同上）。
- 存量清洗：12 列 ALTER UPDATE 置 NULL，mutations 全 done 实证；残留 567 格=清洗窗口期 incremental 旧码新写入，待 merge 后复洗（写链闸生效后自稳）。
- 远期（登记不施工）：全表巨值发散带（1e12~1e300 区间）清洗口径与复权链口径修复=Owner 立项级。

## 六向台账

上游=kline_daily（不复权，含真实断层）+internal_compute_provider 全量/增量重算；下游=lane_c 挖矿基座 REG-IND-001+其他 TI 消费方；输入=technical_indicator 全表；输出=本簿+e10_fix；
真源锚=schemas/categories/market/market_technical_indicator.py+src/zephyr/factor/technical_indicators/；耗时账=普查 ~20min/修面代理 ~57min/清洗 mutations ~15min。

**自审闸：挖干**（12 列 Inf 全归因+复发机制实证+修复闭环；巨值发散带与复权口径登记移交）。
