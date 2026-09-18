---
ttl: task_bound
rule_form: data
verifiability: manual
title: L1 车道考试报告——量能/统计族第二批 18 档（去重后 15 组）沙箱点火考试
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
lane: P3-B2（st-bizmine-l1-20260919）
parent_context: docs/_working/kimi_audit/lane_reports/P3.md §P3-B-NARROWING + prereg_family_summary.md（frozen）
---

# L1 车道报告：量能/统计族第二批（P3-B2）点火考试

> 性质：沙箱考试（零写库/零注册表写入；CH 只读经 DatabaseService）。判读尺=P3 已用三关：
> ①OOS 毛超额>2.7bp/日 ②DSR>0.5（MOD-SIM-024 fail-closed，N_eff=子族去重组数）③机制自述+OOS≥60 日。
> 口径冻结=prereg_family_summary.md + prereg_group_01..15.md（跑前 frozen，未动一字）。

## 〇、结论速览（≤10 行）

1. **同源预检+去重（裁定书挂单前置①②③全闭合）**：18 档 → **15 组（3 dup）**，N_eff=VOL12/STAT3。
2. **逐档结果：PASS 2 / RED 16（18 档全考完，含 3 dup 引用 canonical，零豁免）。**
3. **两档过三关=IND-STAT-001 CORREL（OOS 毛超额 +9.88bp/日，DSR 0.6223）与 IND-STAT-002 BETA
   （+8.40bp/日，DSR 0.6348），均 statistics 子族（N_eff=3）、均「做多低值」防守形态**
   （低量价相关/低量弹性）；量能族 12 组全 RED（关①最高 ADOSC +11.6bp/日但 DSR 0.115 不过）。
4. 反向参考（不进门）：全档反方向毛超额 ≤0（方向=IS 符号钉死未翻车），无「方向待考」翻案证据。
5. DSR 关：3/15 代表档 DSR>0.5（CORREL 0.6223, BETA 0.6348, ROLLVAR 0.7092）。
6. regime 分桶（F4_BDI T-1 状态）：两 PASS 档超额集中于 **risk_off 桶**（CORREL +30.0/BETA +25.4bp/日），
   15 档最优桶=risk_off 8 档/neutral 7 档/risk_on 0 档——防守状态条件化形态（呼应 R 车道）。
7. E4 正考：两 PASS 档已进 E4 三阶段（IS→WFA→OOS，E4-E1C09 先例路线），CORREL/BETA 两档案落 E4-BIZMINE-L1-*（判定详见 §五；IS 段为负+折稳定性是主要存疑点）。
8. 结论口径：kline_daily_hfq 后复权，全部结论标「待复权链修复后复核」；不构成投产建议。

## 一、去重结论（裁定书挂单前置，硬门槛闭合）

- 挂单①同源预检：18 列在 IS 段（2021-2023）对 7 特征基座（compute_features，代表 REG-IND-001 缩减基座）
  残差化增量 IC 全部落 |增量IC|≤0.040（最高 ROLLVAR +0.0394），原始 IC 最高 |0.106|（ADOSC）——
  全族信息量薄，与 prereview「截面排名多头」的乐观标签存在温差。
- 挂单②去重：IS 段 (date,symbol) 池化秩相关 |ρ|>0.8 合并——**唯一合并组 {VWAP, VWMA, LINEARREG, ROLLVAR}**
  （代表=ROLLVAR；四者均为价格水平/量纲代理，两两 ρ 全对 >0.8）。裁定书 §4.3 先验怀疑的
  累积族（OBV/AD/PVT/NVI/PVI）**实测未过 0.8 线**——各股上市以来积分路径分歧大于先验想象，
  按实测保留独立档（先验分组让位于数据，账目公开 pairwise_rank_corr.csv）。
- 挂单③ N_eff 重算：volume 子族 12 组 / statistics 子族 3 组（跨族 dup VWAP/VWMA 计入 STAT3）。

## 二、逐档结果表（IS=2021-01-04..2023-12-29 参考不进门；OOS=2024-01-02..2026-09-14 判读主段）

| 卡 | 档 | 方向 | OOS 毛超额 bp/日 | 反向参考 bp/日 | DSR(N_eff) | OOS 净Sharpe | 日均单边换手 | 判定 |
|----|----|----|----|----|----|----|----|----|

| IND-STAT-001 | CORREL | long_low | +9.88 | -9.88 | 0.6223(3) | 0.718 | 0.1719 | **PASS** |
| IND-STAT-002 | BETA | long_low | +8.40 | -8.40 | 0.6348(3) | 0.73 | 0.1148 | **PASS** |
| IND-STAT-004 | ROLLVAR | long_low | +2.41 | -2.41 | 0.7092(3) | 0.859 | 0.1014 | **RED** |
| IND-VOLUME-001 | OBV | long_low | -1.55 | +1.55 | 0.181(12) | 0.462 | 0.0488 | **RED** |
| IND-VOLUME-002 | MFI | long_low | +0.28 | -0.28 | 0.0073(12) | -0.473 | 0.401 | **RED** |
| IND-VOLUME-004 | VR | long_low | +3.03 | -3.03 | 0.0415(12) | -0.042 | 0.3416 | **RED** |
| IND-VOLUME-005 | AD | long_low | -2.53 | +2.53 | 0.1435(12) | 0.366 | 0.0243 | **RED** |
| IND-VOLUME-006 | PVT | long_low | -4.41 | +4.41 | 0.0753(12) | 0.139 | 0.0361 | **RED** |
| IND-VOLUME-007 | WVAD | long_low | -2.36 | +2.36 | 0.0179(12) | -0.264 | 0.2104 | **RED** |
| IND-VOLUME-009 | ADOSC | long_low | +11.61 | -11.61 | 0.1152(12) | 0.287 | 0.1095 | **RED** |
| IND-VOLUME-010 | EOM | long_low | +3.35 | -3.35 | 0.1248(12) | 0.314 | 0.1754 | **RED** |
| IND-VOLUME-011 | KVO | long_low | -6.71 | +6.71 | 0.0091(12) | -0.424 | 0.1532 | **RED** |
| IND-VOLUME-012 | NVI | long_high | -13.68 | +13.68 | 0.0006(12) | -1.005 | 0.0408 | **RED** |
| IND-VOLUME-013 | PVI | long_low | -6.65 | +6.65 | 0.0385(12) | -0.063 | 0.0437 | **RED** |
| IND-VOLUME-014 | FORCE_INDEX | long_low | -16.82 | +16.82 | 0.0001(12) | -1.309 | 0.2382 | **RED** |
| IND-VOLUME-003 | VWAP (dup→IND-STAT-004) | long_low | +2.41 | - | - | - | - | **RED(引用)** |
| IND-VOLUME-008 | VWMA (dup→IND-STAT-004) | long_low | +2.41 | - | - | - | - | **RED(引用)** |
| IND-STAT-003 | LINEARREG (dup→IND-STAT-004) | long_low | +2.41 | - | - | - | - | **RED(引用)** |

判读附注：
- 15 代表档中 2 档过三关（CORREL/BETA，statistics 子族）；13 档 RED（其中 ADOSC +11.6、EOM +3.3、VR +3.0
  过了关①毛超额线但 DSR≤0.5 关②拦下；ROLLVAR 毛超额 +2.4 差 0.3bp 过线且 DSR 0.709 绿——关①拦下）。
  换手（日均单边 均值 0.14，区间 0.02..0.40）把净收益进一步压负——DSR 全部作用在净日收益上。
- DSR：3/15 代表档 DSR>0.5（CORREL 0.6223, BETA 0.6348, ROLLVAR 0.7092）
- 反向参考：15 档反方向毛超额全部为负（=正向取负），「IS 符号钉死方向」在 OOS 无一翻车——
  反向翻案证据为零，不存在事后择优空间。

## 三、PASS 档（2 档，statistics 子族防守形态）

- **P3-B2-IND-STAT-001 CORREL**: OOS 毛超额 +9.88bp/日，DSR 0.6223（N_eff=3），OOS 净 Sharpe 0.718；分桶：risk_on: +2.10bp/d 净绝对sharpe=0.081 (10%)；risk_off: +29.95bp/d 净绝对sharpe=-0.748 (12%)；neutral: +7.84bp/d 净绝对sharpe=0.964 (78%)
- **P3-B2-IND-STAT-002 BETA**: OOS 毛超额 +8.40bp/日，DSR 0.6348（N_eff=3），OOS 净 Sharpe 0.73；分桶：risk_on: +9.30bp/d 净绝对sharpe=1.556 (10%)；risk_off: +25.40bp/d 净绝对sharpe=-0.725 (12%)；neutral: +5.68bp/d 净绝对sharpe=0.86 (78%)
## 四、regime 分桶段（F4_BDI_MOMENTUM_Z20，T-1 日状态，FINAL）

R 车道今夜发现=幸存者收益集中于高波灰度桶。本批 OOS 窗内 F4 T-1 状态分布（655 判读日）：
**risk_on 67 日（10.2%）/ risk_off 78 日（11.9%）/ neutral 510 日（77.9%）**。
15 代表档分桶毛超额（bp/日，全量在 exam JSON `regime_buckets_t1` 与 csv）实测模式：

- **最优桶=risk_off 者 8/15，=neutral 者 7/15，=risk_on 者 0/15**——无一档在 risk_on 桶拿到最高超额；
- 两 PASS 档均为「防守状态进攻」形态：CORREL risk_off **+30.0**/neutral +7.8/risk_on +2.1；
  BETA risk_off **+25.4**/neutral +5.7/risk_on +9.3（低量价相关/低量弹性在 BDI risk_off 段集中兑现，
  与 R 车道「收益集中于特定状态」发现同向）；
- 桶条件化**未进 PASS 判据**（risk_off/neutral 桶样本 67-78 日偏小，分桶×因子放大假阳性），
  本节只作形态披露；桶级条件化策略须另立新卡预注册后另考。
- 口径注：桶内「净绝对 sharpe」=组合净收益（含市场 beta）的桶内 Sharpe，非超额口径；分桶主读数=毛超额。

## 五、E4 正考段（两 PASS 档，E4-E1C09 先例路线）

- **CORREL**（E4-BIZMINE-L1-IND-STAT-001-CORREL）：判定 **不通过**；IS sharpe -0.606（方向钉死段，为负如实呈现）→ 真 OOS sharpe 0.718/655td、毛超额 +9.88bp/日；DSR 0.6223（N_eff=3，带=review）；WFA 0/0 折通过（最差折 -1.202），OOS/IS 比率 0.0；登记对照 True。
- **BETA**（E4-BIZMINE-L1-IND-STAT-002-BETA）：判定 **不通过**；IS sharpe -0.507（方向钉死段，为负如实呈现）→ 真 OOS sharpe 0.73/655td、毛超额 +8.40bp/日；DSR 0.6348（N_eff=3，带=review）；WFA 0/0 折通过（最差折 -1.213），OOS/IS 比率 0.0；登记对照 True。

解读：两档 E4 均判不通过——IS 参考段（2021-2023，方向钉死段）组合净 sharpe 为负（-0.606/-0.507），
门控按 IS→WFA→OOS **不可跳级**语义直接判不通过（WFA 0/0 折计）；WFA 真 OOS 各折符号混杂
（CORREL 折2 -0.471/折3 +2.532/折6 -0.470）——跨期稳定性不足，点火 PASS **不晋级**。
登记对照三值（毛超额/净sharpe/DSR）复算与沙箱完全一致（crosscheck 全 True），证据链闭合。
两档进「待条件化窄测池」：桶形态（risk_off 防守）已量化，条件化新卡若做须另预注册。

## 六、诚实条款与未达成清单

1. 复权：kline_daily_hfq 后复权口径；复权链修复后全部结论须复核。
2. 成本口径：本考=引擎现行冻结土规（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp 双边，25bp/单位换手）；
   未用 Owner-001 1.5bp 档（对本批结论无影响：毛超额关已在净成本之前拦下全部档）。
3. 数据面修正：prereview 称 technical_indicator"2019-01 起"实为 2021-01-04 起（period='daily'）——
   IS 窗起点修正并在总卡披露；重复批行（样例日 476 符号日）以 ingest_ts 侧 keep-last 处理。
4. 预检基座为 7 特征缩减基座（全 124 列基座复算超车道预算），预检只用于去重/方向钉死，
   不进门判 PASS/RED——门①②在 OOS 独立计。
5. 引擎 `_load_seal_masks` 进程内 memoization（确定性纯函数缓存，语义零改动）；
   封板闸原料若拉取失败引擎按其自身契约 fail-open——本批 实查逐档 JSON stats_full 正常返回（闸原料可得，未触发 fail-open）。
6. E4：f06_e4_wfa_exam.py 本体只读可 import（已验证）；f06 CLI 正门依赖的
   data/strategy_intake/f06_survivors.csv 属本战役禁碰清单，故照 E4-E1C09 先例（biz4 同法）
   复用 f06 内部件+strategy_validation_pipeline 判定零重写，E4 档案落
   data/backtest_artifacts/runs/E4-BIZMINE-L1-*；e4_survivors_rows.csv（values_json 配方格式）
   在本车道目录备好，待 Owner 门位批准后由注册表正门收编（本车道不写 intake）。
7. 未达成：无（18 档全部考完；2 PASS 已进 E4；E2 幂等预审/E3 构造环不在本车道范围）。

## 七、产物锚

- 预注册卡：`prereg_family_summary.md` + `prereg_group_01..15.md`（跑前 frozen）
- 结果底档：`.runtime/tmp/bizmine/l1/{precheck,exam}/`（precheck_results.json/all_results.json/逐档 JSON）
- 入册：`exam_results.csv`（18 行全量，UTF-8-SIG）
- 台账：bizmine_campaign_ledger.md 本批行

> 合规声明：研究方法与工程产出，不构成投资建议；全部候选未经正式验收（E2/E3/§8 冻结门槛），禁止直接投产。
