---
campaign: matrix-20261006
lane: E-exam-w2.5
ttl: task_bound
---

# MOM-029 重考报告（N 道，prereg v2）

- **对象**: FCT-MOM-029「20日动量（代码锚）」 `Momentum20d`（`close.pct_change(20)`，截面秩 IC 口径）
- **重考原因**: B 道判 rework——direction 字段空 + 无经济假设文档（Owner 2026-10-07 批“先补假设再考”）
- **经济假设（事前冻结）**: 过去20个交易日涨幅越高的股票，短期被追涨资金推得越透支，随后数日到数周价格倾向均值回落——本因子赌的是A股月内短期反转（做多前期输家、回避前期赢家），不是动量延续。
- **direction**: **short**（依据=动量/反转文献通识，未引用任何实测 IC 符号；prereg v2 frozen_at=2026-10-06 19:26:43.660810+00:00, frozen_by=st-matrix-20261006）

## 判卷（HOLDOUT 2025-10-09..2026-09-30，headline=5d，direction 调整后）

| 判据 | 线 | 实测 | 结果 |
|---|---|---|---|
| \|eff IC_5d\|（=-IC） | >= 0.02 | 0.0516 | 过 |
| eff ICIR（=-ICIR） | >= 0.3 | 0.31 | 过 |
| retain（\|IC_hold\|/\|IC_isref\|） | >= 0.5 | 0.59 | 过 |
| coverage（HOLDOUT） | >= 0.6 | 97.81% | 过 |

- 原始（方向调整前）: IC_5d=-0.0516, ICIR_5d=-0.31, n_obs=236
- 其他窗: IC_1d=-0.0374(icir -0.23) / IC_20d=-0.0567(icir -0.34)
- 换手代理=0.0713；regime 帘子=sma200_default（report_only）

## Verdict: **PASS**

reason: prereg线全过

口径说明：判据全来自 prereg v2（冻结于考前，禁现场改）；窗口/及格线承 prereg v1 不变，仅 direction 由 null→short（经济假设补全）。verdict 只证明窗内表现，不证明可上线，上线另走晋升门。
