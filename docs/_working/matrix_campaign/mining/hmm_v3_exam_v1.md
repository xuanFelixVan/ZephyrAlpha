---
ttl: task_bound
---

creation_token: matrix-w2-hmm-v3-exam-v1-20261008
lane: st-mx07-W2（矩阵战役 2026-10-07 夜战第二波 W2）| 授权: 裁定#489②（HMM 封顶再攻一次 v3，不过线即永久退役）
设计卡: docs/_working/matrix_campaign/mining/hmm_v3_survey_and_prereg_v1.md（判据/超参/窗口全部冻结照卡）
日期: 2026-10-08（开跑 12:5x 前后，一次窗口）| 性质: 施工+跑数+判定结果册（增量写）
状态: 已判定——verdict=conditionally_qualified（≠qualified），裁定#489② 判死动作已执行（§4）

## 1. 施工 diff 摘要（v2→v3 恰好三外科，其余骨架逐字复用）

施工件：`.runtime/tmp/st-mx07-W2/hmm_v3/run_v3.py`（子命令 prep/fit/score 分阶段落盘中间产物；临时区 24h TTL，按设计卡 §7 判死则原地归档不 promote）。底稿=`scripts/matrix_rescued_tmp/hmm_retrain/{prep_data,retrain}.py`（v2 协议逐字复用面：特征构造器、realized_states、robust_scale、seeded_init 网格、anchor_by_seed_proximity、enforce_min_dwell 以外全部四表函数 table1/confusion/change_points/table3/c12/four_tables、SMA200 基线口径）。数据装载改为 DatabaseService reader 角色（只读 SELECT，表名走 TableRegistry `market_index_kline`），满足"数据读走 DatabaseService 只读"红线。

三外科（对照 §2 病灶表，全部照卡，零顺手优化）：

1. **攻点A 快特征（§5.2）**：特征 7→9 列，新增 `ret_10d = close.pct_change(10)`、`sma50_dist_z = (close/sma50-1)/(vol20×√252)`（sma50=50 日简单均线，min_periods=50）；标定行 dropna 列 (ret_60d, sma_dist_z, vol_ratio) → 加 sma50_dist_z 共 4 列（卡 §5.2 逐字）。
2. **攻点B 滤波+滞回替代 run-merge（§5.3/§5.4）**：解码弃 Viterbi，改手写前向滤波后验（α_t ∝ [Σ_j α_{t-1} a_ji]·N(x_t|i)，逐步归一，t 日只用 ≤t 观测=严格 PIT；diag 高斯发射手动计算，不触 hmmlearn 私有路径）；后验按槽位聚合成 3 质量向量 [p_tdn=P(dn_lovol)+P(dn_hivol), p_tup=P(up_lovol), p_rng=P(up_hivol)]；滞回状态机 R1-R5 冻结执行（进入 0.55/退出 0.30，逐日按序求值命中即止，一日至多一次迁移，t=0 初值=当日后验 argmax）；确认门保留 v2 逐字语义（输出 trend_down 需 t 日 sma_dist_z<0 否则改判 ranging_mid_vol）；**废除 enforce_min_dwell**；5 种子逐日多数表决 ≥3 票，无多数取 seed 101。
3. **攻点C q90 carve（§5.3）**：up_hivol 种子行 vol20 维 q70→q90（q90=np.nanpercentile 90 训练标定行缩放值）；其余 8 维网格值逐字照 v2。

超参冻结核（§5.3）：GaussianHMM n_components=4 / diag / n_iter=300 / tol=1e-4；transmat 对角 0.95（非对角 0.05/3，**冻结定死**，v2 的 0.90+U(0,0.08) 随机取中值）；startprob 均匀；扰动 N(0,0.10)，rng=default_rng(seed)，seeds={101,202,303,404,505}；匈牙利种子邻近锚定（成本=态均值欧氏范数，v2 逐字）。

自裁留痕（卡未逐字枚举处，按 v2 网格逻辑外推，不涉验证分布）：①新快特征 ret_10d/sma50_dist_z 在 2×2 种子网格中的分位档=随所在行的趋势档（dn 行 q30、up 行 q70），与 v2 网格"趋势特征随行趋势档"构造同构；②锚定成本卡文"均值欧氏距离"实现为 v2 的欧氏范数（对匈牙利指派单调等价）；③解码预热起点沿用 v2 的 2016-01-01（非验证超参，仅省内存的解码窗起点）。

## 2. 一次窗口读数原文（2026-10-08 执行，唯一一次，产物 JSON=`.runtime/tmp/st-mx07-W2/hmm_v3/hmm_v3_results.json`）

窗口与样本：训练 2019-04-01..2024-12-31（拟合行 1398/1398，标定行外多剔 0）｜验证 2025-01-01..2026-08-31｜realized n=403，fwd20 NaN 剔除=0｜realized 分布：trend_up 165 / trend_down 163 / ranging_mid_vol 75 / **ranging_low_vol 0（恒空，prereg 定义推论，v2 建议#3 顺延再反馈 J 道/Owner）**｜数据源 kline_index 000300（5282 行 2005-01-04..2026-09-30）+399106 涨跌家数（同覆盖，2026-07 起断供段 ffill 只用过去值）｜GPU 预检：3625/24576 MiB 占用 22%，本管线纯 CPU 不占卡。

fit：5 seeds 全收敛（101/23 iter、202/26、303/24、404/33、505/28），锚定映射五种子一致 {0:trend_down, 1:trend_down, 2:trend_up, 3:ranging_mid_vol}；transmat 对角 0.95 冻结执行。解码段 2611 日（2016-01-04..2026-09-30，无缺失行 fail-closed 核过）。

主表（v3 多数表决 vs SMA200 基线，同口径四表）：

| 模型 | ①up命中 | ②down命中 | ③对角 | ④滞后 med(\|lag\|) | \|lag\|≤5 占比 | P90 | max | 判定 |
|---|---|---|---|---|---|---|---|---|
| SMA200 基线 | 0.6129 | 0.6129 | 0.4541 | 20.0 | 0.2727 | 20.0 | 20 | （基线） |
| **hmm_v3** | **0.5520** | **0.6129** | **0.4789** | **10.0** | **0.3636** | **15.0** | **20** | ①②③过，④不过 |

⑤ 四分量 vs SMA200（≥/≤，无容差）：① 0.5520 < 0.6129 **不过**；② 0.6129 ≥ 0.6129 过（等值）；③ 0.4789 ≥ 0.4541 过；④ med 10 ≤ 20 过。realized 转折 11 个，v3 换挡点 36 个（基线 15），有符号 lag 逐项=[12, 0, -12, 10, 0, 20, -3, 0, -6, -13, 15]。

v3 逐态明细节选（table1/2 原文）：trend_up n=221（fwd20 均值 0.00579/中位 0.00636/win 0.5520）；trend_down n=31（均值 0.00361/中位 -0.00516/win 0.3871）；ranging_mid_vol n=151（均值 0.01532/中位 0.02160/win 0.7020）。混淆计数（pred 行 × real 列）：trend_up 行 {rng 6, td 99, tu 116}；trend_down 行 {rng 11, td 19, tu 1}；ranging_mid_vol 行 {rng 58, td 45, tu 48}。态分布 v3：tu 221 / rng 151 / td 31（基线：tu 372 / td 31）。

5 种子稳定性（不设门槛不作判据）：两两序列一致率 mean/min = 1.000/1.000，ARI mean/min = 1.000/1.000——五种子逐日序列完全一致（transmat 0.95+前向滤波下种子扰动被 EM 收敛吸收）；逐种子四表与多数表决版逐项相同（① 0.5520 ② 0.6129 ③ 0.4789 ④med 10）。

## 3. 四表逐项判定（判据冻结自 state_recognizer_exam_v1.yaml prereg_v1，设计卡 §4 逐字）

| # | 判据 | 线 | v3 实测 | 判 |
|---|---|---|---|---|
| ① | c1 P(fwd20>0\|trend_up) | ≥ 0.55 | 0.5520 | **过** |
| ② | c2 P(fwd20<0\|trend_down) | ≥ 0.55 | 0.6129 | **过** |
| ③ | c3 混淆对角占比 | ≥ 0.40 | 0.4789 | **过** |
| ④ | c4 转折滞后 median(\|lag\|) | ≤ 5 | 10.0 | **不过** |
| ⑤ | c5 对 SMA200 四指标全部不劣（无容差） | ≥ | ①分量 0.5520<0.6129 | **不过**（②③④分量过） |

## 4. verdict：conditionally_qualified ≠ qualified → **裁定#489② 判死，HMM 体制识别方向永久退役**

按 prereg verdict_rule：①②③ 全过、仅 ④⑤ 未过 → conditionally_qualified；非 qualified → 设计卡 §7 判死动作全部执行：

1. **生产不替换**：MOD-REGIME-001 维持现状，处置权归 Owner 既有门位（本车道零生产写入）。
2. **本战役内 HMM 体制线不再立项、不再出提案**；体制信号需求回落到 SMA200 基线路线或非 HMM 族（需新裁定授权）——已登记 `docs/_working/matrix_campaign/dispatch_blockers.md` Owner 知会条。
3. **v3 产物原地归档不 promote**：脚本+JSON+逐日态序列留 `.runtime/tmp/st-mx07-W2/hmm_v3/`（24h TTL 临时区，构造/协议全文已摘要于本册 §1-§2，可重建）；本册保持 ttl: task_bound 随袋归档。
4. 如实全报：全部数值无选择性披露（§2 原文含逐种子、逐 lag、逐态明细）；ranging_low_vol 恒空观察第三次随册反馈。

判死依据的如实注记（非申诉）：④ 10 较 v2 的 8 恶化——快特征+滤波滞回的机制性收益未兑现（v2 特征面固有响应延迟的处方被证伪）；⑤ ①分量 0.5520 仍差基线 6.1pp 且趋势_up 行中 99/221 日 realized=trend_down（trend_down 日被确认门+滞回压缩到 31 日后，②0.6129 系 31 日小样本上的等值达标）。三外科全部按卡执行到位，超参零改动，判定成立无基础设施保留意见。

## 5. 纪律留痕

- 窗口只跑一次（设计卡 §6）：计分恰执行一次（score 子命令单次产出 hmm_v3_results.json 唯一 verdict）。
- 全部超参/阈值/seeds/窗口开跑前冻结（设计卡 §5），跑数期间零改动；禁看分改参遵守——计分前仅发生两次基础设施故障修复（train_idx 读回列解析、hmmlearn 0.3.3 covars_ getter 返回 (K,D,D) 全矩阵需取内部 _covars_），均发生在任何验证分产出之前，无一次涉及数据性结论，按 §6.4 留痕。
- 数据读 CH 只读：DatabaseService reader 角色，表名走 TableRegistry `market_index_kline`；零生产写入、零既有文件改动。
- GPU 预检：3625/24576 MiB、util 22%，本管线纯 CPU（hmmlearn/numpy/scipy）不占卡。
- claim：hmm_v3_exam_v1.md / dispatch_blockers.md / capability_canonical_file_registry.yaml 三件均持 st-mx07-W2 claim，commit 后 release。
- 自裁记录：设计卡未逐字枚举新快特征在种子网格中的分位档→按 v2 网格"趋势特征随行趋势档"外推（§1 尾）；其余无自裁事项。
