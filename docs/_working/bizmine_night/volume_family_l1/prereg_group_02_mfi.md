---
ttl: task_bound
rule_form: data
verifiability: manual
title: L1 第二批预注册卡 prereg_group_02_mfi（量能/统计族点火考试，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（考试启动前写死；启动后任何字段不得改动，改动即作废重开）
lane: P3-B2（L1 车道 st-bizmine-l1-20260919）
family_id: P3-B2-VOL12
n_eff: 12
parent_context: prereg_family_summary.md（族总卡，全族冻结口径）+ P3-B-NARROWING.md（第二批前置挂单）
---

# 组卡 02：IND-VOLUME-002 MFI 资金流量 的毛边际/DSR/经济解释三关点火考试

## 1. 假设（H1，唯一）

**REG-IND-001 注册列 `mfi_14`（IND-VOLUME-002 MFI 资金流量），按冻结方向【做多低值】构造的日频截面因子，
在 top50 等权多头口径下有正且过成本线的毛边际，且统计上非运气（DSR>0.5，N_eff=12）。**

零假设 H0：OOS 段日均毛超额 ≤ 2.7bp/日，或 DSR ≤ 0.5。

- 机制一句话（关③自述）：MFI 低=资金流出过度, 超卖反弹（资金流强度反转）。
- 方向钉死依据：IS 期（2021-2023）平均 raw IC 符号（总包令 §2 多重检验条款，IS 期钉死后预注册）；
  预检实测 IS 毛IC=-0.02721（负→做多低值）。
- 成员：代表档 IND-VOLUME-002（独立档）。

## 2. 预检证据（IS 段 2021-01-04..2023-12-29，fwd=5 日，7 特征基座残差化）

| 档 | 列 | IS 毛IC | ICIR | 增量IC(对7特征基座) | 增量ICIR | 覆盖率 |
|---|---|---|---|---|---|---|
| IND-VOLUME-002 MFI | mfi_14 | -0.02721 | -0.2537 | -0.00066 | -0.0112 | 0.9087 |

基座=compute_features 7 特征（ret_1d/ret_5d/ret_20d/vol_20d/turnover/amt_z20/close_ma20），
代表 REG-IND-001 全基座的缩减口径（预算披露，族总卡 §1）。

## 3. 考试口径与判据

全族冻结口径与三关门槛见 `prereg_family_summary.md` §2/§3（同判，数字先钉死）：
毛超额 >2.7bp/日；DSR>0.5（N_eff=12，MOD-SIM-024 fail-closed）；机制自述一致 + OOS ≥60 日。
考窗 IS=2021-01-04..2023-12-29 / OOS=2024-01-02..2026-09-14。

## 4. 产物锚

- 考试脚本：`.runtime/tmp/bizmine/l1/l1_volstat_exam.py`
- 结果：`.runtime/tmp/bizmine/l1/exam/P3-B2-IND-VOLUME-002.json` + 入册 `exam_results.csv`/`exam_report.md`
