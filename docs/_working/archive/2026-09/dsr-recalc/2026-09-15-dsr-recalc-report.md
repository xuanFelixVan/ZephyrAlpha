---
ttl: task_bound
---

# DSR 存量重算回填报告（A2+A3，2026-09-15）

执行会话：st-f06dsr-shift2-20260915（F-06/DSR 修口径总闸接班会话）
工具：`scripts/backtest/dsr_recalc_backfill.py`（一次性重算回填工具，裁定豁免 m11-perm-manual）
逐行明细（机器可复核）：`docs/_working/dsr-recalc/2026-09-15-dsr-recalc-rows.yaml`（261 重算 + 8 跳过 + meta）

## 1. 口径裁定（2026-09-15，锁定勿再议）

- **N 计数边界 = 可审计机器回测次数**：`strategy_screen` 中 `is_sharpe` 非空行（每行=一次机器回测成绩证据行；deferred_c4 挂起行/C2 粗筛未考行零 is_sharpe，不算试验）+ 台账外可审计批量（grid manifest/summary 可复核）显式登记。
- **人工历史试错**只入 known_floor 披露，永不入 count（不可审计的计数进判定=可伪造的门禁）。
- **阈值不放水**：0.95 通过线 / 0.5 存疑下界维持，不 relax 到 0.90。
- N 账本真源：`docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（MOD-BT-200，CAS 唯一机器写入口）。

## 2. 重算时点的累计 N（n_cum = 4481）

| 来源 | 试验数 | 凭据 |
|---|---|---|
| screen_runs（is_sharpe 非空台账行，25 个 run） | 269 | ClickHouse `c1_backtest.strategy_screen` group-by 可复核 |
| batch_records（F-06 批次 A 网格，5 批：6+8+200+1999+1999） | 4212 | `data/strategy_intake/grid_*/summary.json`（manifest=出生证） |
| **合计（count 口径）** | **4481** | N 账本 trial_ledger_registry.yaml |
| manual_population | 0 | 人工历史不可审计，仅 known_floor 披露位 |

## 3. 重算方法（无收益序列档案，两条路径）

run 档案只存聚合统计、无原始收益序列，故不直接重算 DSR 公式，而用两条可审计路径：

1. **反折叠（refold）**——已有 deflated_sharpe 的行：`DSR_new = Φ(Φ⁻¹(DSR_old) + E[maxZ(N_old)] − E[maxZ(N_cum)])`。数学恒等（同一 z 分位平移），无需收益序列。N_old 考证：优先取行上 num_trials；缺失时按 run 内 is_sharpe 非空且非 pilot 行数（pilot 行有 is_sharpe 但不参与批内 DSR，排除）。锚点校验 fail-closed（见 §5）。
2. **正态近似（normal_approx）**——is-only 缺口行（历史批 DSR 缺失，本组 51+ 条）：`SR = is_sharpe/√252`，`V[SR] = (1−SR²/4)/(T−1)`（γ=0、超额峰度=0 的保守缺省），`DSR = Φ(SR/√V[SR] − E[maxZ(N_cum)])`。T=窗口交易日数，从 `c1_market.kline_index`（symbol='000001'）按窗口计数，带缓存。近似口径在报告中逐行以 method 标记声明。

回填列：`deflated_sharpe`（DSR 新值）+ `num_trials`（批级 N，23 个 run 补齐）。 mutations 全部 `mutations_sync=1` 同步落定，无 pending mutation 残留。

## 4. 重算结果总览（20 个 run / 261 行）

| run_id | screen_batch | 行数 | 旧口径 | 方法分布 | 新 DSR max |
|---|---|---|---|---|---|
| SCR-C4-20260913-002056 | C4-translated-20260912 | 37 | dsr | refold×32 + approx×5 | 0.0793 |
| SCR-C4-20260913-013339 | C4-OOS-2024-2026 | 35 | is_only | approx×35 | 0.0158 |
| SCR-C4-20260913-014220 | C4-OOS2-20260913 | 35 | dsr | refold×32 + approx×3 | 0.0188 |
| SCR-C4-20260913-232100 | C4-2016-2019-sample3 | 4 | dsr | refold×4 | 0.0207 |
| SCR-C4-20260913-232609 | C4-2016-2019-sample3 | 1 | dsr | refold×1 | **0.0517** |
| SCR-C4-20260914-023406 | C4-translated-20260912 | 2 | dsr | refold×2 | 0.0000 |
| SCR-C4-20260914-034927 | C4-translated-20260912 | 6 | dsr | refold×6 | 0.0009 |
| SCR-C4-20260914-045225 | C4-translated-20260912 | 2 | dsr | refold×2 | 0.0506 |
| SCR-C4-20260914-051102 | C4-translated-20260912 | 2 | dsr | refold×2 | 0.0037 |
| SCR-C4-20260914-051809 | C4-OOS2-20260914 | 51 | dsr | refold×48 + approx×3 | 0.0197 |
| SCR-C4-20260914-070706 | C4-translated-20260912 | 1 | dsr | refold×1 | 0.0006 |
| SCR-C4-20260914-082130 | C4-translated-20260912 | 3 | dsr | refold×3 | 0.0001 |
| SCR-C4-20260915-012830 | C4-VAL2-20260915 | 6 | dsr | refold×6 | 0.0001 |
| SCR-C4-20260915-014654 | C4-OOS3-VAL-20260915 | 6 | dsr | refold×6 | 0.0000 |
| SCR-C4-20260915-025332 | C4-BACKLOG2-20260915 | 2 | dsr | refold×2 | 0.0000 |
| SCR-C4-20260915-025400 | C4-OOS3-BACKLOG2-20260915 | 2 | dsr | refold×2 | 0.0000 |
| SCR-C4-20260915-032455 | C4-BACKLOG3-20260915 | 14 | dsr | refold×14 | 0.0316 |
| SCR-C4-20260915-032916 | C4-OOS3-BACKLOG3-20260915 | 14 | dsr | refold×14 | 0.0001 |
| SCR-C4-20260915-112409 | C4-translated-20260912 | 33 | dsr | refold×33 | 0.1220 |
| SCR-C4-20260915-113344 | C4-OOS-2024-2026 | 5 | dsr | refold×5 | 0.1448 |

新分布：n=261，min=0.0000 / median=0.0000 / max=0.1448。**≥0.5 的行数=0；≥0.95 的行数=0**——与 2026-09-14 影响评估（`2026-09-14-dsr-enable-impact-assessment.md`）在累计口径下"0/133 存活"的预测方向一致且更严（累计 N 更大）。

## 5. 翻案声明（锚点行，Owner 裁定要求的显式推翻）

`SCR-C4-20260913-232609` / CAND-e3da6fa71af1（C4-2016-2019-sample3，oos_tested）：
is_sharpe=0.983，旧 deflated_sharpe=**0.9809**（N_old=1，solo run 零折减原点），新 deflated_sharpe=**0.0517**（N_cum=4481，refold N1→4481）。

该行是当时唯一 ≥0.95 的"通过"行，也是 145 条冻结的直接诱因（恐慌反弹假阳性）。重算后明确**翻案：0.9809 → 0.0517，远低于 0.5 存疑下界**，判不通过。工具内置锚点断言（若该行未跌破 0.5 即 RuntimeError fail-closed），锚点校验通过。

## 6. 诚实跳过（8 行，有声明不硬凑）

无窗口证据（无法取 T 计算近似，也无旧 DSR 可反折叠）：

- SCR-ADJ-20260913-012358：CAND-12286499cb19 / CAND-5efe26d1992e / CAND-d06cab686cef / CAND-eaddc3f9db4e（4 行，verdict=failed_obsolete——整族样本期漂移失效，DSR 无意义）
- SCR-DEV-20260914-031358 / SCR-DEV-20260915-065032 / SCR-DEV-20260915-065316 / SCR-DEV-20260915-065339：STR-VREV-025（4 行，verdict=sim_deviation——仿真偏差行，非成绩行）

处置=维持现状（DSR 保持 NULL），以 verdict 语义本身已足够判死/判疑，不强造数字。

## 7. 逐行声明：与历史值不可逐位比

**全部 261 个新值均为"2026-09-15 当日口径新值"**，与历史 deflated_sharpe **不可逐位比较**，原因有二：

1. **口径变更**（本裁定的本意）：N 从批内行数（甚至 solo=1）改为全局累计可审计 N=4481，折减基数根本不同。
2. **市场数据漂移**：2026-09-14 行情数据修正后，历史行上的 is_sharpe 已非当时落账值，任何"用旧 is_sharpe 重算"的结果都携带当日数据基底。

因此本报告不声称"重算还原历史"，只声称"按今日可考证 N 与今日数据给出当日口径新值，逐行留痕于 JSON"。历史值不做抹除留痕（台账只追加不删改铁律作用于行，本操作为 UPDATE 数值列，翻案以本报告+锚点断言留档）。

## 8. 冻结解除

145 条 DSR 冻结（2026-09-14 影响评估触发）自本报告落库起**解除**。后续约束：

- DSR 开关只对新批次开启（三步走第②步）；未注入 DSR 的判定记 `not_tested`，不记 `rejected`。
- 新批次必须写入批级 `num_trials`（c4_batch_screen 已实现）并累计进 N 账本。
- N_eff（effective_rank）随批次 B 落地，账本已预留 `n_trials_effective` 披露位。

## 9. 施工班状态回填

- A1 N 账本（MOD-BT-200）：已交付（commit f4d1ea4f），ledger 已同步 269+4212=4481。
- A2 台账 N 字段：num_trials 列已存在（S03-N1 前任会话建），本班完成 23 个 run 的可考证值回填。
- A3 存量重算：261 行重算 + 8 行声明跳过，本报告即交付物。
- 遗留给后续班次：A4 metrics.py 坏路径退役、A5 阈值三线 SSOT、_c4_engine 累计口径接线。
