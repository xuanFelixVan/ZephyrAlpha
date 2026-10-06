---
campaign: matrix-20261006
lane: A道 wave-2 alt_factor_exam
ttl: task_bound
---

# 另类因子考试成绩册 v1（wave-2，机生）

- 生成：2026-10-06 10:34:03.330999+00:00（.runtime/tmp/st-matrix-20261006/wave2_assemble.py）
- 真源规格卡：spec_SL-A13/A06/A08/A15（docs/_working/matrix_campaign/mining/m1_alt_sources/，照卡计算禁改卡）
- 判据（roster.PREREG_V1 冻结）：|IC|>0.02 且 ICIR>0.3 且 retain>=0.5 且 coverage>=0.6；HOLDOUT=2025-10-09..2026-09-30，IS_REF=2024-10-08..2025-09-30
- 总判：**0 pass / 4 rework / 5 retire_candidate**（9 对象）

| 因子 | 路线 | verdict | 关键量 |
|------|------|---------|--------|
| ALT-A13-CHG | cross_section_ic | **retire_candidate** | ic=-0.0019 icir=-0.04 retain=0.07 cov=0.99 n=221 |
| ALT-A13-CHG60 | cross_section_ic | **rework** | ic=0.0119 icir=0.26 retain=0.27 cov=0.99 n=221 |
| ALT-A13-STREAK | cross_section_ic | **retire_candidate** | ic=0.0039 icir=0.07 retain=0.15 cov=0.99 n=221 |
| ALT-A06-MAIN5D | cross_section_ic | **retire_candidate** | ic=-0.0002 icir=-0.00 retain=0.01 cov=0.95 n=76 |
| ALT-A06-SUPER5D | cross_section_ic | **retire_candidate** | ic=0.0045 icir=0.09 retain=0.18 cov=0.95 n=76 |
| ALT-A06-PERSIST10D | cross_section_ic | **rework** | ic=0.0119 icir=0.18 retain=0.60 cov=0.95 n=71 |
| ALT-A08-BDI-COND | conditional_bucket | **retire_candidate** | Sharpe差/MaxDD见册；方向证伪: Sharpe差=-0.052<=0（卡面OOS窗） |
| ALT-A15-FMED-COND | conditional_bucket | **rework** | Sharpe差/MaxDD见册；判据不可计算: HOLDOUT 拥挤桶 n=0<20（拥挤态在判窗未出现,桶空）；IS 段描 |
| ALT-A15-FEXT-COND | conditional_bucket | **rework** | Sharpe差/MaxDD见册；判据不可计算: HOLDOUT 拥挤桶 n=3<20（拥挤态在判窗未出现,桶空）；IS 段描 |

## 分族结论

### M1-ALT-A13（spec_SL-A13.md）
- 假设：股东户数下降=筹码集中（散户离场/机构吸筹），对个股未来 10-60 日收益有正向预测力
- 最优者：**ALT-A13-CHG60 = rework**——|ic|=0.0119(线0.02) icir=0.26(线0.3) retain=0.27(线0.5)
- 数据面：c3_fundamental.shareholder_count（514,395 行 / 5,906 票 / 1993-01-12..2026-09-30（CH 实测与卡面一致））；33 年全史，考试窗（2024-10 起）无缺口；asof 投影按 announce_date<t（禁 end_date 对齐）

### M1-ALT-A06（spec_SL-A06.md）
- 假设：大单/超大单净流入占比是知情交易者订单流代理，主力净流入率截面秩可预测 5-20 日相对收益
- 最优者：**ALT-A06-PERSIST10D = rework**——|ic|=0.0119(线0.02) icir=0.18(线0.3) retain=0.60(线0.5)
- 数据面：c1_market.money_flow（5,971,039 行 / 5,781 票（CH 实测与卡面一致））；数据可得窗=2021-01-04..2025-09-09 + 2026-06-01..2026-09-30；缺口=2025-09-10..2026-05-31（8.5 个月）→ HOLDOUT 有效段仅 2026-06-01..2026-09-30（窗口完整性~0.35），IS_REF 尾段 2025-09-10..09-30 亦缺——按任务纪律以数据可得窗如实标注，禁假装全窗；pass 需窗口完整性>=0.9，不足者降级 rework（本册冻结规则）

### M1-ALT-A08（spec_SL-A08.md）
- 假设：BDI 动量上行期出口链（航运/港口/出口制造）相对收益为正（轴+条件选股完整考法）
- 最优者：**ALT-A08-BDI-COND = retire_candidate**——方向证伪: Sharpe差=-0.052<=0（卡面OOS窗）
- 数据面：c1_market.alt_regime_signal(F4_BDI_MOMENTUM_Z20) + c1_market.kline_sector_880 + c1_market.alt_shipping_index（轴 9,301 条 1989-11-14..2026-09-30；BDI 14,010 行；冻结板块收盘面 2021-08-02 起）；桶边界=轴值卡面 IS(2006-01..2021-12) 三分位钉死 [-0.5299, 0.2076]；板块收益面仅 2021-08-02 起 → 卡面 IS 的板块收益段实际仅 2021-08..2021-12(~100 交易日)，如实标注；verdict 判窗=卡面 OOS(2022-01..2026-09)；卡面 multiplicity 3指数×2清单属后续完整预注册，本波按卡面计算式只考 F4 轴×冻结清单 1 组态

### M1-ALT-A15（spec_SL-A15.md）
- 假设：永续资金费率=加密杠杆多头拥挤度，拥挤桶收缩敞口/防守——A 股组合风险偏好条件轴，非选股 alpha
- 最优者：**ALT-A15-FEXT-COND = rework**——判据不可计算: HOLDOUT 拥挤桶 n=3<20（拥挤态在判窗未出现,桶空）；IS 段描述性证据仅卡内+牛市段禁升级（卡面自警伪象）→ 回S0-S3 等拥挤态样本/扩窗重考
- 数据面：c1_market.hl_funding_history（4,750,075 行 / 234 币 / 2023-05-12..2026-10-05（卡面真源；任务简报提及的 hl_perp_snapshot_daily 为对照记录，以卡为准））；边界/阈值=卡面 IS(2023-06-01..2025-12-31) 钉死；判窗=任务冻结 HOLDOUT(2025-10-09..2026-09-30)，卡面 IS 与 HOLDOUT 重叠 2025-10..12 如实声明；funding_time 列=UTC→北京+8h，窗口 (t-1 15:00, t 15:00] 右闭

## 数据面发现（影响判读，全部如实）

- c1_market.money_flow 存在 8.5 个月数据缺口（2025-09-10..2026-05-31），月度行数 202509=36,005（半月）后直跳 202606——A06 判据按数据可得窗+完整性降级
- c1_market.kline_sector_880.sector_name 全空（763,260 行 0 非空）——板块名经 c1_market.sector_code_name_map 典表解析（argMax by ingest_ts），v_kline_sector_880_named 视图经网关查询 404 不可用
- c1_market.hl_funding_history 实为逐小时结算（24 小时×~198K 条/时），卡面'8h 费率'描述与库内粒度偏差如实记录；聚合口径（中位数/占比）不受影响
- c3_fundamental.shareholder_count 同日多披露 18,464 对（2024 起）→ 按 (symbol,announce_date) 取 ingest_ts 末条（卡面规则）；holder_count 空值 687 条剔除
- 股东户数披露频率（2024-10-08 起/票）：p10=8 p50=8 p90=57 条——自愿披露混杂，样本构成漂移风险随卡面如实记
- kline_daily_hfq：10,097,728 行 / 5,912 票 / 1990-12-19..2026-09-30（全窗可用）；money_flow∩kline 符号格式一致（裸代码）
- 股东户数披露质量 flag：data_source=bdpan 501,958 / akshare 12,437

## 纪律留痕

- 跑数前冻结：出口链板块清单、bootstrap seed、A15 退化分桶规则、判据映射（册内 prereg_v1_frozen.frozen_before_run）
- 负结果纪律：0 pass 不掩盖；A13/A06 干净窗无 alpha、A08 方向证伪、A15 拥挤态在判窗未出现（判据不可计算≠证伪，回 S0-S3）
- 复算：计算式+PIT+表名+窗口+边界+seed 全量内嵌 YAML；checkpoint=wave2_ckpt.jsonl（幂等续跑）
- device：CPU pandas/scipy（spearman 无 GPU 核，逐条可解释），CH 只读经 ch_data

> 负结果纪律：全部 rework/retire/判据不可考结论如实入册，零隐藏
