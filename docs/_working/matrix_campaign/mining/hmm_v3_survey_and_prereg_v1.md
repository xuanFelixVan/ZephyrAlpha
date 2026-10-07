---
ttl: task_bound
---

creation_token: matrix-l6-hmm-v3-survey-and-prereg-v1-20261007
lane: st-mx07-L6（矩阵战役 2026-10-07 夜战 L6）| 授权: 裁定#489②（HMM 封顶再攻一次 v3，不过即永久退役）
日期: 2026-10-07 | 性质: 只读调研+预注册设计卡（本件零跑数、零 DB 写、零代码修改；跑数归第二波 W2）
持久化说明: 本区（docs/_working，临时区）门禁强制 ttl=task_bound（FILE-PLACEMENT-TTL 禁 permanent）；车道卡"# [TTL] permanent"意图经交付 promote 流程落地——设计卡通过 W2 施工交付后随成果 promote 转永久区，此后即永久资产
证据基线: docs/_working/matrix_campaign/rescued_tmp_20261007/hmm_retrain/REPORT.md（v2 门控+驻留5：down 0.840 / 对角 0.531 / 滞后 med 8，全胜 SMA200 于②③④；未过：④ 8>5、① 0.566<基线 0.613）
判据原文真源: docs/_working/fexam/state_recognizer_exam_v1.yaml prereg_v1 块（2026-10-06 开跑前冻结，逐字引用见 §4）

---

## 0. 一页结论

v2 已把 ②down/③对角/④相对基线 打到全胜，卡在两处：**④绝对滞后 med=8（须 ≤5）** 与 **⑤①分量 up 命中 0.566（须 ≥基线 0.613，无容差）**。全网调研结论：SOTA（Nystrup 系 jump models / BOCPD / L0 trend filtering / 混合 HMM）无一可直接整体替换 v2 骨架而不引入"需在验证窗上调参"的违规风险；**可直接借力的是三个思想件**——(a) 跳数惩罚/在线推理（Nystrup 2020a/2020b）支持"滤波概率+滞回门"替代 run-merge 驻留；(b) jumpmodels 论文特征面（EWM halflife 10-20 天）支持快方向特征 ret_10d / sma50_dist_z；(c) Ensemble-HMM 投票（2025）支撑 5 种子多数表决协议。据此 v3 = **v2 已证骨架 + 恰好三处外科改动**，全部超参事前冻结，验证窗只跑一次（§6），不过线即永久退役（§7）。

---

## 1. SOTA 全网调研（访问日期均为 2026-10-07）

### 1.1 GitHub 开源

| # | 资产 | 链接 | 一句话 | 许可/状态 |
|---|------|------|--------|-----------|
| G1 | jumpmodels（Shu，Princeton） | https://github.com/Yizhan-Oliver-Shu/jump-models | Nystrup 系统计跳跃模型官方实现：JumpModel / SparseJumpModel / CJM，sklearn 式 API，含 `.predict_online()` / `.predict_proba_online()` 在线（因果）推理 | Apache-2.0，pip `jumpmodels`，Python≥3.8 |
| G2 | trendfilter（dave31415） | https://github.com/dave31415/trendfilter | CVXPY 上的 ℓ1 trend filtering 通用库（L0-TF 的凸代理族） | 开源，CVXPY 依赖 |
| G3 | BOCPD 教学实现（Gundersen） | https://gregorygundersen.com | Adams-MacKay 2007 Bayesian Online Changepoint Detection 的 Python 复现教程（Gaussian 共轭） | 博客+代码 |
| G4 | fast-bocpd | 检索自 https://www.bing.com/search?q=fast-bocpd（PyPI 条目，本次未逐行审） | 多观测模型的高效 BOCPD 实现 | 未深审，仅备案 |
| G5 | RoRo 风险体制分类引擎 | https://github.com（检索词 "RoRo Cross-Asset Risk-Regime Classification Engine"，本次未逐行审） | Statistical Jump Model + 分位分类器混合体制引擎 | 未深审，仅备案 |
| G6 | mlfinlab（Hudson & Thames） | https://www.oreilly.com（经《Hands-On AI Trading》证实其 regime detection 模块存在） | HMM regime 检测模块完善但已转订阅墙，无自由借力面 | 不可借 |
| G7 | qlib（Microsoft） | 检索确认 | 无一方 regime detection 模块；regime 需自组 hmmlearn 管线 | 无可借 |

### 1.2 2020-2026 学术主线（含 2024-2026 近作）

| # | 文献 | 链接 | 与本车道相关的硬数字 |
|---|------|------|----------------------|
| P1 | Nystrup, Lindström, Madsen (2020a), "Learning hidden Markov models with persistent states by penalizing jumps", ESWA 150:113307 | 经 G1 README 引证（https://github.com/Yizhan-Oliver-Shu/jump-models） | HMM 持久性治本=把跳跃数作为惩罚项进目标函数（跳数惩罚解码），取代 transmat 手调+后处理驻留 |
| P2 | Nystrup, Kolm, Lindström (2020b), JFDS 2(3):25-39（在线推理） | 经 G1 README 引证 | 在线（滤波/贪心序贯）推理协议：体制信号实时因果产出，不依赖全样本平滑 |
| P3 | Nystrup, Kolm, Lindström (2021), "Feature selection in jump models", ESWA 184:115558 | 经 G1 README 引证 | Sparse JM：特征面可稀疏化，支持"少而快"的特征组 |
| P4 | Shu & Mulvey (2024), "Regime-Aware Asset Allocation: A Statistical Jump Model Approach"（2024-07 改题 "Downside Risk Reduction Using Regime-Switching Signals: A Statistical Jump Model Approach"）, JFDS 6(4) | https://arxiv.org/abs/2402.05272 （本次实读 HTML v3） | ①JM 目标=Σ损失+λ×跳数，坐标下降+线性 DP，n_init=10；②λ≈50-100 → <1 次换挡/年，而 HMM 即使 k=20 滑窗平滑仍 ~2 次/年；③特征=EWM 下行偏差 halflife 10d + Sortino halflife 20d/60d，标准化；④K=2；⑤λ 用逐月时序 CV（8 年回看、策略 Sharpe 目标）在线选——**此法与四表 prereg 冲突，故 v3 冻结 λ 类参数不走此路**；⑥JM vs HMM：Sharpe 0.68 vs 0.54、换手 44% vs 141%；HMM 新冠崩盘检出滞后约半月（引文基准 median 25 天） |
| P5 | Aydınhan, Kolm, Mulvey, Shu (2024), "Identifying Patterns in Financial Markets: Extending the Statistical Jump Model for Regime Identification", Annals of Operations Research | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4556048 | 连续 JM（CJM，κ 罚项），regime 识别主文献，引用 48+ |
| P6 | Wen et al. (2023), "ℓ0 Trend Filtering" | 经 RePEc/Ideas 检索条目 | L0-TF：函数值/导数自动检 knot 的非参平滑——离线全样本属性，因果性不内建 |
| P7 | "Hybrid Hidden Markov Model (HMM-WJ)"（2026） | https://arxiv.org/html/2603.10202v1 （本次实读） | 强制驻留机制 K~Poisson(λ*)（λ*=100, ε*=1e-4）复现增益/损失不对称；**警示数据：HSMM 基线驻留塌缩到 1.1-1.8 步**——显式时长机制在短样本上易退化为几何驻留，v3 不引入显式时长参数的直接依据 |
| P8 | "Multi-model Ensemble-HMM Voting Framework"（2025, Data Science in Finance and Economics） | https://www.aimspress.com/article/doi/10.3934/DSFE.2025019?viewType=HTML | 树模型集成与 HMM 投票融合检体制迁移——多模型/多种子多数表决的学术先例 |
| P9 | Polavarapu (2026), "Cross-Asset Market Regime Detection Using HMMs"（Kroniq Regime Radar） | SSRN 检索条目（本次未见全文，仅摘要面） | 9 特征×5 资产类跨资产 HMM——本车道 CH 只读单指数（000300），跨资产特征面不在授权内，备案不采纳 |
| P10 | Adams & MacKay (2007), "Bayesian online changepoint detection" | https://arxiv.org/abs/0710.3742 | run-length 隐变量的在线变点框架——2024 年市场冲击建模仍在用（arXiv "Online Learning of Order Flow and Market Impact", 2024-05 检索佐证） |
| P11 | R-BOCPD（Restarted BOCPD, 2026-09） | https://huggingface.co/papers（daily 2026-09-14 检索条目） | BOCPD 前沿变体，备案 |

**调研小结**：学术前沿 2024-2026 的主线是 jump models 家族（P1-P5）在持久性与延迟上系统性压过朴素 HMM（P4 的 44% vs 141% 换手、<1 vs ~2 次换挡/年），但其选参协议（策略 Sharpe CV）与本车道四表 prereg 的"一次窗口、禁看分改参"不可调和；BOCPD/L0-TF 属"变点/平滑"另一族，不产四类语义标签。故 v3 采取**借力不换骨**策略（§3）。

---

## 2. v2 病灶→处方→SOTA 对齐表

v2 REPORT 处方原文："下一步攻点=④（融合更快方向特征 sma50 距离/ret_10d，或概率滞回替代 run-merge）与①（up_hivol carve 收窄至 vol90 分位）"。

| 病灶（v2 实测） | 处方 | SOTA 借力评估 | v3 采纳 |
|---|---|---|---|
| ④滞后 med=8：特征集（ret_20d/ret_60d/sma_dist_z 最短视野 20 天）对 fwd20 符号翻转固有响应延迟；run-merge 驻留 5 再加系统性 +lag | 更快特征 sma50 距离/ret_10d | **直接借力**：P4 特征面 halflife 10-20 天 EWM 证明 10-20 天视野体制信号有效；P3 支持少而快的特征组 | 攻点 A：新增 ret_10d + sma50_dist_z（§5.2） |
| ④之二：run-merge 驻留（min dwell 5）是后处理硬切，短体制翻转必吃 ≥2-4 天惩罚 | 概率滞回替代 run-merge | **直接借力**：P1 跳数惩罚=持久性进目标/解码而非事后拼接；P2 在线滤波推理=严格因果的单遍决策；双门限滞回（Schmitt trigger 式）为其 HMM 原生实现 | 攻点 B：滤波概率+双门限滞回（§5.4），废除 run-merge |
| ①⑤up 命中 0.566<基线 0.613：up_hivol（q70 波分位以上强势日）被 carve 进 ranging_mid_vol，trend_up 态被稀释 | up_hivol carve 收窄至 vol90 | **借 v2 自证**：②有 0.27 垫（0.840 vs 0.55 线），把 carve 边界 q70→q90 换回的是 ① 的分子 | 攻点 C：up_hivol 种子波分位 q70→q90（§5.3） |
| （不修）realized ranging_low_vol 恒空属 prereg 定义推论 | REPORT 建议#3 反馈 J 道/Owner | 与四表冻结冲突，本卡不改判据 | 冻结原样执行（§4） |
| （备选不采纳）整体换 jumpmodels / BOCPD / L0-TF | — | JM K=4 需 λ 策略 CV 选参→违反一次窗口；BOCPD 不产四类标签→③对角语义断裂；L0-TF 离线全样本→因果性不内建 | 全部不换骨，理由留痕（§1） |

---

## 3. v3 命名与不变式

- v3 全名：**hmm_v3 = v2 骨架 + 三外科（快特征 / 滤波滞回 / q90 carve）**。
- 不变式：四表判据、考窗、realized 标签、lag 协议、SMA200 基线口径、CH 只读、PIT 纪律——与 J 道 prereg / v2 逐字同口径，任何一项不冻结即本卡作废。
- 判死前置：本卡为裁定#489② 授权的最后一次 HMM 攻击，W2 只许照卡施工，**禁止**临场加变体、改阈值、换特征（见 §6 一次窗口定义）。

---

## 4. 四表判据原文引用（冻结，逐字自 state_recognizer_exam_v1.yaml L32-L50）

```yaml
pass_criteria:   # 初拟待 Owner 校，全部事前冻结
  c1_trend_up_hit: P(fwd20>0 | HMM=trend_up) ≥ 0.55
  c2_trend_down_hit: P(fwd20<0 | HMM=trend_down) ≥ 0.55
  c3_confusion_diag: 混淆矩阵对角线占比（trace/N，HMM 行 × realized 列）≥ 0.40（四类随机基线 0.25）
  c4_switch_lag: 真实体制转折→HMM 换挡滞后 median(|lag|) ≤ 5 个交易日
  c5_baseline_dominance: 对 SMA200 土办法基线同口径四指标（①②③④）全部不劣于（HMM ≥ baseline，无容差）
verdict_rule:
  qualified: ①②③④⑤ 全过
  conditionally_qualified: ①②③ 全过、仅 ④ 和/或 ⑤ 未过（准头够、及时性/基线劣势）
  unqualified: ①②③ 任一未过
```

配套口径（同 yaml 逐字语义）：fwd20 = close(t+20)/close(t)-1（000300 交易日）；rv_pct = rv20 考窗截面百分位秩，tercile 边界 1/3、2/3；realized 四类标签定义、drop_rule（fwd20 NaN 尾行剔除如实报 n）、switch_lag_protocol（realized 变化点=前后段均 ≥5 交易日边界；HMM 变化点逐日不过滤；lag 取 |lag| 最小者，±20 截断，另报 |lag|≤5 占比/P90/max）、基线（close>SMA200→trend_up 否则 trend_down）——全部按 v2 复用实现（`rescued_tmp_20261007/hmm_retrain/retrain.py` 的 four_tables/table3 已对齐此协议，W2 可直接移植）。

---

## 5. v3 预注册规格（W2 照卡施工面）

### 5.1 数据与窗口（冻结）

- 数据源：c1_market.kline_index，symbol='000300'（close/volume），涨跌家数取 symbol='399106'（同 v2 口径；2026-07 起断供段 ffill 只用过去值，PIT 安全，如实标注）。CH 全程只读。
- 载入起点 2005-01-01（SMA200/250 分位预热）；**训练窗 2019-04-01..2024-12-31**；验证窗 2025-01-01..2026-08-31；前向缓冲 2026-09-30（fwd20 标签可用）。窗划分与 v2 逐日相同（可比性）。

### 5.2 特征清单（9 列，全 PIT，只用 ≤t 信息）

| # | 特征 | 定义 | 变动 | 归属攻击点 |
|---|------|------|------|-----------|
| 1 | ret_10d | close.pct_change(10) | **新增** | ④快方向 |
| 2 | sma50_dist_z | (close/sma50-1)/(vol20×√252)，sma50=50 日简单均线 | **新增** | ④快方向 |
| 3 | ret_20d | close.pct_change(20) | v2 原样 | — |
| 4 | ret_60d | close.pct_change(60) | v2 原样 | — |
| 5 | sma_dist_z | (close/sma200-1)/(vol20×√252)（SMA200 口径不变，确认门仍用它） | v2 原样 | — |
| 6 | vol20 | ret.rolling(20).std()×√252 | v2 原样 | — |
| 7 | vol_ratio | vol5/vol60 | v2 原样 | — |
| 8 | volume_z | (volume-mean20)/std20 | v2 原样 | — |
| 9 | ad_smooth | 399106 (adv-dec)/(adv+dec) 5 日均值，ffill | v2 原样 | — |

缩放：robust（median/IQR）**只用训练窗统计量**，同 v2。标定行（train 特征可用行）与 v2 同法 dropna(ret_60d, sma_dist_z, sma50_dist_z, vol_ratio)。

### 5.3 模型结构与超参（冻结，一个都不许在验证窗上动）

| 项 | 冻结值 | 来源/理由 |
|---|---|---|
| 模型 | GaussianHMM，n_components=4，covariance_type="diag"，n_iter=300，tol=1e-4 | v2 已证（序列一致率 0.929） |
| transmat | 对角 0.95（非对角均 0.05/3），startprob 均匀 | v2 搜索域 0.90-0.98 取中值定死；P1 思想=持久性进模型本体 |
| 初始化 | 分位数种子 2×2 网格（趋势×波动），扰动 N(0, 0.10)，seeds={101,202,303,404,505} | v2 已证种子级稳定 |
| 种子槽位语义 | dn_lovol→trend_down；dn_hivol→trend_down；up_lovol→trend_up；**up_hivol→ranging_mid_vol，其种子行的 vol20 维取训练窗 q90 分位（v2 为 q70）** | 攻点 C（REPORT 处方原文 vol90） |
| 锚定 | 匈牙利种子邻近锚定（anchor_by_seed_proximity，成本=均值欧氏距离） | v2 原样 |
| 解码 | **前向滤波后验**（model.predict_proba 的 forward 因果遍历），禁用 Viterbi 全局路径 | P2 在线推理；严格 PIT（Viterbi 的 t 态在严格意义被未来观测牵引） |

### 5.4 滞回状态机（冻结；替代 run-merge 驻留——攻点 B）

对每种子（滤波后验聚合后）逐日执行，t=0 初值=当日后验 argmax：

```
p_tdn = P(dn_lovol) + P(dn_hivol)      # 两 down 态合计
p_tup = P(up_lovol)                    # trend_up 态
p_rng = P(up_hivol)                    # ranging_mid_vol 态

规则（按序求值，命中即止，一日至多一次迁移）:
  R1 若 当前≠trend_down 且 p_tdn ≥ 0.55        → trend_down   # 进入阈值=c1/c2 同款 0.55（原则性锚点）
  R2 否则若 当前≠trend_up 且 p_tup ≥ 0.55      → trend_up
  R3 否则若 当前==trend_down 且 p_tdn < 0.30   → argmax(p_tup, p_rng)
  R4 否则若 当前==trend_up   且 p_tup < 0.30   → argmax(p_tdn, p_rng)
  R5 否则保持当前态                                           # 滞回带 [0.30,0.55) 内保持=抑抖
```

- 进入 0.55 / 退出 0.30 两值**事前冻结**（进入线与判据 c1/c2 同值，退出线为其 0.545 倍滞回带下沿；设计理由：v1 无门无驻留 argmax 的 ④=8 证明慢在特征不在解码，故进入线取低保速度，退出带宽保抑抖）。**禁止任何依据验证分布的再校准。**
- 确认门保留（v2 语义逐字）：滞回输出 trend_down 时，要求 t 日 sma_dist_z<0（SMA200 口径），否则改判 ranging_mid_vol——PIT 安全。
- 种子合成：5 种子各产全序列后**逐日多数表决**（≥3 票）；无多数时取 seed 101 当日标签。稳定性（序列一致率/ARI）照 v2 同报，不设门槛、不作判据。
- **废除** enforce_min_dwell（run-merge），P7 的 HSMM 塌缩证据亦支持不引入显式时长参数。

### 5.5 施工边界（给 W2）

- 复用 `docs/_working/matrix_campaign/rescued_tmp_20261007/hmm_retrain/` 的 prep/retrain/table 协议代码为底稿（four_tables/table3/confusion 与 J 道 prereg 已对齐），产物只写本车道新目录（如 `.runtime/tmp/<W2sid>/hmm_v3/`），CH 只读、零既有文件改动、零生产写入。
- 输出册必须含：四表全量数值（含 ⑤ 四分量 vs SMA200）、|lag|≤5 占比/P90/max、5 种子稳定率、realized n 与 fwd20 NaN 剔除数。
- 环境前置照宪法冷启动（Python 3.12 PATH、reaper、claim、git_commit.py）。

---

## 6. 一次窗口定义（冻结）

1. 本卡（§4 判据、§5 全部超参/阈值/seeds/窗口）在 W2 开跑前即为完整规格，**W2 开跑后禁改**。
2. 验证窗 2025-01-01..2026-08-31 的评分**只执行一次**：5 seeds × 1 管线 × 1 次四表计分，产出唯一 verdict（按 §4 verdict_rule）。
3. 禁止事项（违者视同判死）：看任何验证分后回头改特征/阈值/超参/种子；增补第二管线变体"再试一发"；用验证窗做任何模型选择。
4. 唯一例外：基础设施故障（代码崩溃、CH 断连）允许修复后原配置重跑一次，须在结果册留痕故障与修复；数据性结论（分数不佳）不构成重跑理由。

---

## 7. 判死动作（裁定#489② 落实）

- verdict ≠ qualified（即 ①②③④⑤ 未全过）→ **HMM 体制识别方向永久退役**：
  1. 生产不替换（MOD-REGIME-001 维持现状，处置权归 Owner 既有门位）；
  2. 本战役内 HMM 体制线不再立项、不再出提案，体制信号需求回落到 SMA200 基线路线或非 HMM 族（需新裁定授权）；
  3. v3 产物（脚本+结果册）原地归档不 promote，REPORT 结论栏写明"裁定#489② 判死，永久退役"。
- verdict = qualified → 进入正常生产化流程（独立裁定/门控语义登记按 v2 REPORT 建议#4，另行立项，不在本卡范围）。
- 无论生死，结果册必须如实报全部数值（禁止选择性披露），ranging_low_vol 恒空观察再次随册反馈 J 道/Owner（v2 REPORT 建议#3 顺延）。

---

## 8. 风险与如实预判

1. **④ 仍是最大险点**：快特征+滞回的机制性收益（视野 20d→10d、去掉 run-merge 的 +2~4 天硬延迟）方向正确，但 8→≤5 需要 ~3 天改善，无任何离线证据保证；若 realized 变化点多由"高位横盘后阴跌"触发，快特征也可能晚知。此为一次窗口赌注的固有风险，判死条款为真。
2. **③ 对角可能被 q90 回换反噬**：被换回 trend_up 的高波强势日若 realized=ranging_mid_vol，③ 单日恶化；对冲逻辑是 ② 垫厚（0.840）与 ①⑤ 是当前唯一可换分处。若 ③ 反降至 <0.40，按 §4 判 unqualified，照判死执行，不救。
3. **滞回退出带 0.30 的反弹延迟**：V 型反转底部修复信号会晚于 argmax；由快特征部分补偿，不再加机制。
4. 溢出面：ad_smooth 断供段 63 天 ffill、399106 真源口径等与 v2 同风险同口径，不新增。

---

## 9. 参考来源清单（全部外链，访问日期 2026-10-07）

- jumpmodels 库：https://github.com/Yizhan-Oliver-Shu/jump-models （2026-10-07 实读 README）
- Shu & Mulvey 2024（arXiv:2402.05272）：https://arxiv.org/abs/2402.05272 （2026-10-07 实读 HTML，λ/换挡/Sharpe/特征数字出自此文）
- Aydınhan, Kolm, Mulvey, Shu 2024（Annals of OR）：https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4556048 （检索确认，未读全文）
- Nystrup et al. 2020a/2020b/2021（ESWA 150:113307 / JFDS 2(3):25-39 / ESWA 184:115558）：经 jumpmodels README 引证条目确认题录
- Adams & MacKay 2007（BOCPD）：https://arxiv.org/abs/0710.3742 （题录确认）
- Gundersen BOCPD 实现：https://gregorygundersen.com （检索确认）
- trendfilter（CVXPY ℓ1-TF）：https://github.com/dave31415/trendfilter （检索确认）
- Hybrid HMM-WJ 2026：https://arxiv.org/html/2603.10202v1 （2026-10-07 实读）
- Ensemble-HMM Voting 2025：https://www.aimspress.com/article/doi/10.3934/DSFE.2025019?viewType=HTML （检索确认）
- Princeton 博士论文 Y. Shu 2025（体制分段）：https://dataspace.princeton.edu/handle/88435/dsp01g158bm716 （检索确认）
- mlfinlab/qlib 现状：经 O'Reilly《Hands-On AI Trading with Python, QuantConnect, and AWS》页与检索确认（前者订阅墙、后者无一方 regime 模块）
- 本仓证据：v2 结果册 `docs/_working/matrix_campaign/rescued_tmp_20261007/hmm_retrain/REPORT.md`；判据真源 `docs/_working/fexam/state_recognizer_exam_v1.yaml`（2026-10-07 本地实读）
