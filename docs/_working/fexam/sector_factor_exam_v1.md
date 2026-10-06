---
campaign: matrix-20261006
lane: E-exam-w2
ttl: task_bound
---

# sector_factor_exam_v1 — 板块因子首波 IC 考试分数册（C道 2026-10-06）

- campaign: matrix-20261006 | lane: C道-L2板块族首波 | 判据: prereg v1（|IC|>=0.02/ICIR>=0.3/retain>=0.5/coverage>=0.6，headline=5d）
- HOLDOUT 2025-10-09..2026-09-30；IS_REF 2024-10-08..2025-09-30；机判 verdict，禁现场改判据
- 数据: industry_class L1 现行快照（**无 PIT 历史**）+ kline_daily_hfq 等权行业聚合 + kline_sector（受限窗 2025-07 起）
- counts: {'total': 9, 'rework': 9}

| 因子 | 方向(预登记) | IC_5d(HOLDOUT) | ICIR | retain | coverage | verdict | reason |
|---|---|---|---|---|---|---|---|
| ks_idx_mom20 | long | +nan | +nan | nan | n/a | rework | insufficient_window: kline_sector 实际宽覆盖自 2026-03（每月>=100 码）起，全部落在 HOLDOUT 内；IS_REF 无参照（retain 不可判）且 code→行业映射无考前期拟合窗（窗内拟合=泄露，禁）——prereg 冻结窗下不可考 |
| sec_mom20_eqw | long | -0.0321 | -0.21 | 0.87 | 1.00 | rework | |ic|=0.0321(线0.02) icir=-0.21(线0.3) retain=0.87(线0.5) |
| sec_mom_multi | long | -0.0208 | -0.15 | 0.74 | 1.00 | rework | |ic|=0.0208(线0.02) icir=-0.15(线0.3) retain=0.74(线0.5) |
| sec_act_amount | long | -0.0117 | -0.06 | 1.23 | 1.00 | rework | |ic|=0.0117(线0.02) icir=-0.06(线0.3) retain=1.23(线0.5) |
| sec_struct_trend | long | -0.0308 | -0.25 | 18.40 | 1.00 | rework | |ic|=0.0308(线0.02) icir=-0.25(线0.3) retain=18.40(线0.5) |
| sec_div20 | short | -0.0179 | -0.09 | 1.18 | 1.00 | rework | |ic|=0.0179(线0.02) icir=0.09(线0.3) retain=1.18(线0.5) |
| stk_resid_mom20 | long | -0.0400 | -0.34 | 0.52 | 0.99 | rework | |ic|=0.0400(线0.02) icir=-0.34(线0.3) retain=0.52(线0.5) |
| sec_cond_mult | long | -0.0234 | -0.18 | 1.52 | 1.00 | rework | |ic|=0.0234(线0.02) icir=-0.18(线0.3) retain=1.52(线0.5) |
| stk_cond_gated | long | -0.0693 | -0.43 | 0.48 | 0.15 | rework | coverage 0.15<0.6 |

## 口径与风险（全文见 yaml）

- 方向预登记于考试前（脚本落笔时冻结）；判据与窗口同批1，未改动。
- proxy：stock_strength=个股20日动量百分位×10；行业指数=成员等权累积代理；flow 路/涨停子分/市场调节缺席按 in-spec fallback degraded。
- 主风险：industry_class 无 PIT 历史（幸存者/前视偏差）；kline_sector 实测宽覆盖自 2026-03（HOLDOUT 内，不可考）；广播后行业内同值。
- 动量族全负 IC=HOLDOUT 反转态（raw mom20 对拍同号佐证）；反向线索须走新 prereg 翻向重考，禁看分后改向。
- 引擎挂载层（executor `X_sector` 维、sector_conduction 段）留工单，本册仅因子可考层。

pass=0/9；详情: sector_factor_exam_v1.yaml
