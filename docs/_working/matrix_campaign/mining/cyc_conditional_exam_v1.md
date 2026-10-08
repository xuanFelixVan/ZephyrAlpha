---
ttl: task_bound
title: CYC 条件变量考场执行留档 v1（W3 车道读数与 verdict 逐项）
session: st-mx07-W3
---

# CYC 条件变量考场执行留档 v1

- 授权链: 裁定#489①（CYC 族 4 件留观改考条件变量考场，预注册一次定生死）+ 预注册卡 `docs/_working/matrix_campaign/mining/cyc_conditional_prereg_v1.md`（判据冻结，commit `dfcc8ec9548c6e827cacc7ee32e7c5f0a8d7d542`）
- 考册（冻结产出，判读唯一数值真源）: `docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml`（sha256 前 16 位 `35295851161fa80e`，generated_at_utc=2026-10-08 05:33:11+00:00）
- 检验器: `scripts/backtest/fexam/conditional_exam.py`（单测 12/12 合成真值通过：相位分桶边界/宽度阈值/N_fam 冻结/HAC 恰同调用对拍/植入异质性判活方向）
- 一次窗口纪律执行: 预注册卡 commit（dfcc8ec9，12:58+08:00）先于首跑（13:30 前后）✅；解盲前冻结文件 `.runtime/sessions/st-mx07-W3/staging/cond_exam_freeze_v1.json`（N_fam=11、K_eff={3,4,2,2}，物理写于任何层内 IC 计算前）✅；考试窗恰好执行一次，未换参/换窗/换基线 ✅

## 1. 基线有效性（卡 §3 顺序）

- B1（20 日动量）μ_all=**-0.051691**（236 有效日），|μ_all|≥0.01 → **用 B1，B2 不跑**（护栏是科目有效性检查非及格线；负值=考试窗动量整体反向，不影响条件增益科目）。

## 2. Bonferroni 校正族（卡 §5.2，解盲前冻结）

- K_eff=(3,4,2,2)（四指标全部层有效日数均 236≥30，零层剔除）→ N_fam=C(3,2)+C(4,2)+C(2,2)+C(2,2)=3+6+1+1=**11**，与卡预期一致；p_adj=min(1, p_raw×11)；显著性线 p_adj<0.05。

## 3. 考试窗读数原文（2025-10-09~2026-09-30，n_days=236/层）

### IND-CYC-001 HT_DCPERIOD（层 D1≤20 / D2 20-35 / D3>35）

| 层 | n_stockdays | mu_s |
|---|---|---|
| D1 | 347445 | -0.037187 |
| D2 | 580621 | -0.048843 |
| D3 | 359690 | -0.072249 |

mu_all=-0.051691，G=max|mu_s|-|mu_all|=**0.020558**（best=D3）

| 对 | mean_d | t_HAC | p_raw | p_adj |
|---|---|---|---|---|
| D1 vs D2 | 0.011656 | 1.227471 | 0.219646 | 1.000000 |
| D1 vs D3 | 0.035062 | 1.927008 | 0.053979 | 0.593766 |
| D2 vs D3 | 0.023406 | 2.133055 | 0.032920 | 0.362122 |

**verdict=fail**（无任何 p_adj<0.05；G>0 不单独判活——卡 §5.2 合取判据）

### IND-CYC-002 HT_DCPHASE（层 P1..P4=floor(phase/90)）

| 层 | n_stockdays | mu_s |
|---|---|---|
| P1 | 323214 | -0.052770 |
| P2 | 321438 | -0.048866 |
| P3 | 323341 | -0.049924 |
| P4 | 319763 | -0.055173 |

G=**0.003482**（best=P4）。p_adj 六对：P1P2=1.0、P1P3=1.0、P1P4=1.0、P2P3=1.0、P2P4=0.530570（p_raw=0.048234）、P3P4=1.0 → **verdict=fail**

### IND-CYC-004 HT_SINE（层 W0=sine≤leadsine / W1=sine>leadsine）

| 层 | n_stockdays | mu_s |
|---|---|---|
| W0 | 643973 | -0.053038 |
| W1 | 643783 | -0.050254 |

G=**0.001348**（best=W0）。W0 vs W1：mean_d=-0.002784，t=-1.009341，p_raw=0.312811，p_adj=1.000000 → **verdict=fail**

### IND-CYC-005 HT_TRENDMODE（层 M0=循环态 / M1=趋势态）

| 层 | n_stockdays | mu_s |
|---|---|---|
| M0 | 750346 | -0.050950 |
| M1 | 537410 | -0.052627 |

G=**0.000937**（best=M1）。M0 vs M1：mean_d=0.001677，t=0.390792，p_raw=0.695951，p_adj=1.000000 → **verdict=fail**

## 4. 族判定与 registry 动作（卡 §6 判死分支）

- **family_verdict=fail**（0 指标判活）→ 裁定#489①"一次窗口定生死，不过即整族归档"原文执行：**四件全部 status: active→retired**，evidence 字段登记 `conditional_exam_v1 FAIL 2026-10-08 best_p_adj=<..> G=<..> baseline=B1 ...`（引用本留档与考册），updated_at→2026-10-08；registry 修改与考册登记**同 commit 原子**。
- 注册册净删门位未被拦（status 翻转非净删）；判死不阻断复活通道（卡 §6 复活条款原文有效）。

## 5. 参照窗（2024-10-08~2025-09-30，report-only 零判死权重）

- baseline=B1（mu_all=-0.082481）；family=pass，唯一判活=IND-CYC-001（D 层异质：D1vsD2 p_adj=0.004254、D1vsD3 p_adj=0.0、D2vsD3 p_adj=0.000032；mu_s: D1=-0.056893/D2=-0.080143/D3=-0.122992）；CYC-002/004/005 参照窗亦全 fail。
- **与考试窗结论不一致**（CYC-001 参照窗显著、考试窗不显著）→ 按卡 §7 原文"不一致不影响生死"，evidence **不加 consistent 注**，考试窗判死维持。此分歧本身即预注册一次窗口纪律的存在理由，如实留档。

## 6. 自裁记录（客观架构师视角，留痕）

1. 卡 §5.1"两层层内 IC 均有效的交易日并集交集"措辞含混 → 取"两层均有效日的交集"读法（同日两截面共享市场波动，D_t 逐日相减语义要求配对）。本案四层有效日完全相同（各 236 日），交集=全集，读法对结果零影响。
2. statsmodels 未预装 → pip 安装 v0.15.0（卡 §5.1 强制"恰按此调用"，禁手搓 HAC 替代）；HAC 单测与 statsmodels 直调逐位对拍通过。
3. 退化护栏（卡未定）：len(D)<2 或 se=0 时记 degenerate=true、p_raw=1.0（零证据保守方向）。本案实际未触发（全部 236 对有效）。
4. 参照窗基线选择按"同管线"独立重算（卡 §7 未细言），零判死权重，不影响任何 verdict。

## 7. 红线自查

- 判据全部照卡硬编码（切点/宽度 100/层 30 日/HAC lag=10/族=11/判活合取），代码先于首跑 commit，未看分改判据 ✅
- 考试窗单次执行，无二次窗口 ✅
- 数据 CH 只读经 ch_data（TableRegistry 表名常量），零现算指标、零 DB 写 ✅
- 判死与考册同 commit 原子落地（见提交记录）✅
