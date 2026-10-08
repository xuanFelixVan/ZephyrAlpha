---
ttl: task_bound
title: CYC 条件变量考场预注册卡 v1
session: st-mx07-L10
---

creation_token: cyc-conditional-prereg-20261008
lane: st-mx07-L10（矩阵战役 2026-10-07 夜战 L10）| 授权: 裁定#489①（CYC 族 4 件留观改考条件变量考场，预注册一次定生死）
日期: 2026-10-08 | 性质: 只读设计冻结卡（本件零跑数、零 DB 写、零代码修改；跑数归第二波 W3，照卡执行禁止临场发挥）
持久化说明: 本区（docs/_working，临时区）门禁强制 ttl=task_bound（FILE-PLACEMENT-TTL 禁 permanent）；车道卡"# [TTL] permanent"意图经交付 promote 流程落地——本卡通过 W3 施工交付后随成果 promote 转永久区（同 L6 卡先例）
授权原文真源: docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml 裁定#489①——"CYC 族 4 件（CYC-001/002/004/005）留观：非方向预测器，5 日方向 IC 属科目错配；改考'条件变量考场'（预注册判据=分层增益显著性，一次窗口定生死，不过即整族归档）。复活条件：全网调查车道……若证伪我方实现或考法，按新条目复活重考"
指标册真源: docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml L3032/3065/3131/3164（IND-CYC-001/002/004/005，status=active，version=1.0.0，2026-09-14 冻结零改参）
实现真源: src/zephyr/factor/technical_indicators/cycle.py `_ht_core`（MOD-L02-029，相位累积口径，预热 63 根，周期钳位 [6,50]）

---

## 0. 一页结论

本卡把裁定#489① 的"分层增益显著性"落成一套零歧义、零随机数、CPU 可执行的判据：四指标各自把自己切成 2~4 个"周期相位层"（层切点全部是实现常数，零样本估计），在每层内逐日计算动量基线的截面秩 IC，对"层间 IC 均值两两之差"做 Newey-West(lag=10) t 检验；Bonferroni 校正族=4 指标全部层间两两对比，预期 3+6+1+1=**11 个检验**，p_adj=p_raw×11<0.05 为显著。**指标判活 = 名下 ≥1 对比 p_adj<0.05 且 max_s|μ_s|>|μ_all|（分层增益点判据）且各有效层 ≥30 交易日**。判过=≥1 指标判活（判活者 active+evidence 登记取得条件变量资格，同窗未判活者 retired）；**四指标全不判活=整族 4 件 retired**（裁定#489①"不过即整族归档"原文执行）。考试窗=2025-10-09~2026-09-30（与第一波同窗），一次执行，PASS/FAIL/VOID 均耗尽本卡执行权。本判据与裁定#489③ 及格线 v1（IC>0.02/ICIR>0.3/retain≥0.5）**相互独立**（§8）。

## 1. 考场定义：科目从"方向预测"改为"条件增益"

第一波考试（docs/_working/fexam/indicator_exam_scores_v1.yaml，verdict=retire_candidate，|ic_5d|=0.0014~0.0042）考的是**方向预测**：指标值本身对 5 日前瞻收益的截面秩 IC。CYC 四件是 Ehlers Hilbert 变换循环族**状态量**（entry_role=state，direction=neutral），其经济职能不是预测方向，而是**标记当前价格所处的周期相位/模式**——正确考法是条件变量考：**在指标划定的相位层内，一个已知有方向含量的基线信号是否表现出显著异质的 IC（分层增益）**。若分层后子窗 IC 与不分层无显著差异，则该指标作为条件变量无信息含量，判死；反之判活。

## 2. 四指标 definition 与相位分层（含无前视论证）

### 2.0 公共口径

- 数据来源：`c1_market.technical_indicator` 存量面板（trade_date×symbol，CH 只读，经 `scripts/backtest/fexam/ch_data.py load_panel`；列名解析走注册册 outputs：ht_dcperiod/ht_dcphase/ht_sine+ht_leadsine/ht_trendmode）。指标值由数据管道全历史预热后落库，考试侧**零现算**。
- 无前视论证（四件通用）：实现为 `_ht_core` 单遍前向递推——4 项 WMA 只用过去 4 根、EMA(span=10) 因果、4-tap Hilbert 只用滞后 0/2/4/6、相位逐根前向累积；t 日层标签只用 ≤t 信息。预热 63 根（NaN 屏障）。分层切点全部为**实现常数**（下表），不做任何样本分位数/参数估计→分层规则零前视、零自由度。
- 预测对象：r5(i,t)=close(i,t+5)/close(i,t)−1（`c1_market.kline_daily_hfq` 后复权 close，`forward_returns()` 同式）。t+1..t+5 属预测对象窗，与条件变量无泄漏。

### 2.1 IND-CYC-001 HT_DCPERIOD（主导周期，ht_dcperiod，整数根，钳位 [6,50]）

- definition：Ehlers 同质变换主导周期——当前价格摆动的主导循环长度（根数）。册内 formula："Ehlers 同质变换主导周期（平滑周期钳位 [6,50]）"。
- 经济含义：主导周期短=快摆动/均值回复环境（动量倾向失效）；主导周期长=慢摆动/趋势主导环境（动量倾向有效）。这是 Ehlers 循环理论中周期滤波切换趋势系统的原始用途。
- 相位分层（周期长度三层，切点=实现常数）：
  - 层 D1（短周期）：ht_dcperiod ≤ 20
  - 层 D2（中周期）：20 < ht_dcperiod ≤ 35
  - 层 D3（长周期）：ht_dcperiod > 35
- 切点论证：20 根≈1 个交易月、35 根≈7 周，均落在实现钳位 [6,50] 内部且远离钳位边界（6/50），保证三层在数据上可分；常数切点=预注册零自由度。

### 2.2 IND-CYC-002 HT_DCPHASE（主导周期相位，ht_dcphase，度，[0,360)）

- definition：当前相位角——价格在主导循环环内的相对位置。册内 formula："当前相位角（度，90° 偏移 ±180 归一）"；实现输出 dc_deg=degrees(accum mod 2π) ∈ [0,360)。sine=sin(phase)，故 phase=90° 为环内峰位、270° 为环内谷位。
- 经济含义：周期位置=价格在环内的相对位置（本车道任务卡指定考法）。Ehlers 用法：相位近 270°（谷区）与近 90°（峰区）分别对应循环买卖区。
- 相位分层（相位角四象限，切点=实现常数）：
  - 层 P1（峰前上行段）：0° ≤ ht_dcphase < 90°
  - 层 P2（峰后回落段）：90° ≤ ht_dcphase < 180°
  - 层 P3（谷前下行段）：180° ≤ ht_dcphase < 270°
  - 层 P4（谷后回升段）：270° ≤ ht_dcphase < 360°
- 可计算公式：bucket = floor(ht_dcphase / 90) ∈ {0,1,2,3} → P1..P4。边界值恰在 90/180/270 的归入下一层（floor 语义，机械唯一）。

### 2.3 IND-CYC-004 HT_SINE（正弦波，ht_sine + ht_leadsine 双列）

- definition：主正弦与超前 45° 正弦；册内 formula："主正弦与超前 45° 正弦；两线交叉标记周期转折"。实现：sine=sin(φ)，leadsine=sin(φ+45°)。
- 经济含义：两线相对位置=周期转折后的半程标记。封闭式：sine>leadsine ⟺ cos(φ+22.5°)<0 ⟺ φ∈(67.5°,247.5°)，即环内峰(90°)到谷(270°)的**下行半程**；补集为谷到峰的**上行半程**。两线交叉各发生一次于峰前(67.5°)与谷前(247.5°)，正是"交叉标记转折"的机械含义。
- 相位分层（相对位置两层）：
  - 层 W1（下行半程）：ht_sine > ht_leadsine
  - 层 W0（上行半程）：ht_sine ≤ ht_leadsine
- 无前视：逐 bar 两列比较，无估计量。

### 2.4 IND-CYC-005 HT_TRENDMODE（趋势循环模式，ht_trendmode，{0,1}）

- definition：主导周期窗口内正弦交叉计数模式开关。册内 formula："主导周期窗口内正弦交叉计数：少=趋势态 1，多=循环态 0"。实现：cross_count≤2→1（趋势态），否则 0（循环态），计数 ≥4 时衰减复位（实现的固定规则）。
- 经济含义：内建趋势/循环二态开关——直接检验"动量基线在趋势态是否系统性优于循环态"这一 Ehlers 原始命题。
- 相位分层（模式二态）：
  - 层 M1（趋势态）：ht_trendmode = 1
  - 层 M0（循环态）：ht_trendmode = 0

### 2.5 范围锁

四指标各自独立分层、独立检验；**跨指标联合分层（如 D×M 交叉）、其他 horizon（1/20 日）、市场级指数序列分层、参数网格一律不在本考场**——W3 实施任何一项即违规重跑，本卡作废。

## 3. 基线信号 B 与有效性护栏（void 线）

- **B1（主基线）20 日动量**：mom20(i,t)=close(i,t)/close(i,t−20)−1（后复权 close 面板，同 `load_close`+`shift(20)`）。选 momentum 的理由（先验经济原则，非看分）：Ehlers 循环族的原始用途就是给趋势跟随系统做开关，动量是其设计上的分层对象；20 日=册内最常用动量视野（ma_20/注册册惯例）。
- **B2（备用基线）5 日反转**：rev5(i,t)=−(close(i,t)/close(i,t−5)−1)。仅当 B1 触发 void 线时启用。
- **有效性护栏（void 线，非及格线）**：在考试窗上，基线不分层全截面日度 IC 均值满足 |μ_all(B)|≥0.01（=裁定#489③ 及格线 IC 下限 0.02 之半，仅作"基线活着"的科目有效性检查）。判定顺序机械唯一：先算 B1 的 μ_all；|μ_all(B1)|≥0.01 → 用 B1（B2 不跑）；否则算 B2；|μ_all(B2)|≥0.01 → 用 B2；双废 → 考场 VOID（§7）。**只允许被选中的一条基线进检验族**，族大小不因此翻倍。
- 基线冻结于本卡，W3 禁止换任何其他信号当基线。

## 4. 子窗划分规则与层有效性

1. **子窗=层**：层是股票×日条件（每股票按自身指标值落层），不是日历窗——同一交易日的股票被相位切成数个子截面，这是设计本体（相位分层），不是缺陷；禁改日历子窗。
2. **层内日度 IC**：对交易日 t 与层 s：IC_t^(s)=spearman(B_i,t, r5_i,t)，仅在层 s 内的股票截面上计算。当日该层截面宽度（非缺失三元组 {L,B,r5} 计数）<100 → 当日该层 IC 记缺失（宽度下限，防小截面秩相关噪声）。
3. **全截面 IC**：IC_t=all=全宇宙同式 spearman；当日宇宙宽度 <100 → 记缺失。μ_all=考试窗内 IC_t=all 有效日的均值。
4. **层有效性（天数下限）**：层 s 的有效日数 n_s（有 IC_t^(s) 的交易日数）≥30 才参检；n_s<30 → 该层剔除。指标剩余有效层 K_i^eff<2 → 该指标 VOID。
5. 层有效性判定只依赖 {指标值、B 非缺失、r5 非缺失} 的**计数**，不看任何收益实现数值——天然防 p-hacking，可在解盲前冻结。

## 5. 检验统计量与 Bonferroni 校正族（冻结口径）

### 5.1 层间两两对比（族成员）

对指标 i 的每对有效层 (a,b)：D_t^(a,b)=IC_t^(a)−IC_t^(b)，取两层层内 IC 均有效的交易日并集交集（按交易日时间序拼接，无插值、无成对剔除以外的处理）。检验 H0: E[D]=0：

```
t_HAC = mean(D) / se_HAC(D)，
se_HAC 由 statsmodels 恰按此调用取得：
sm.OLS(endog=D, exog=np.ones((len(D),1))).fit(
    cov_type='HAC', cov_kwds={'maxlags': 10}).tvalues[0]
p_raw = 双侧 t 检验 p 值（同一结果的 pvalues[0]）
```

同日两层的子截面来自同一横截面、共享市场波动，D_t 逐日相减已消去共同分量；lag=10 覆盖 r5 五日重叠+截面 IC 残余自相关。t_HAC 同式输出供留档。

### 5.2 Bonferroni 校正族（完整定义）

- **族 = 本考场一次执行中全部假设检验 = 4 指标各自全部有效层间两两对比**。族大小 N_fam = Σ_i C(K_i^eff, 2)；预期全层有效 K=(3,4,2,2) → N_fam=3+6+1+1=**11**。
- **解盲纪律**：N_fam 在任何 IC 数值算出**之前**按 §4 计数规则冻结并写入产出文件；p_adj=min(1, p_raw×N_fam)。
- **显著性线**：p_adj<0.05（Bonferroni 校正后）。
- 指标 i 判活 ⇔ (i 名下 ≥1 对比 p_adj<0.05) 且 (max_s|μ_s| > |μ_all|，点判据=最优层确比不分层强，防"显著异质但整体更差"的假阳) 且 (i 未 VOID)。
- 无检验进入族的其他统计量（μ_all、G_i=max_s|μ_s|−|μ_all|、参照窗重算）一律 report-only。

## 6. 判过/判死动作（同裁定#489① 6 件同款机制）

| 分支 | 动作 |
|---|---|
| **族判过**（≥1 指标判活） | 判活指标：technical_indicator_registry status 保持 active，evidence 字段登记 `conditional_exam_v1 PASS <日期> p_adj=<..> G=<..> baseline=<B1|B2>`，取得**条件变量资格**（可被策略层用作分层条件；不进方向因子池）。同窗未判活指标：status→retired（个体判死）。 |
| **族判死**（0 指标判活） | 四件全部 status→retired——裁定#489①"一次窗口定生死，不过即整族归档"原文执行。registry 修改与考试结果登记**同 commit 原子**（同裁定#489① 6 件退役先例：结果登记+状态翻转一批落地）。 |
| **VOID**（基线双废或 ≥2 指标 VOID） | 考场作废：产出文件 verdict=VOID，登记 `docs/_working/matrix_campaign/DISPATCH_BLOCKERS.md`（`- [st-mx07-L10] 问题/已试/建议` 格式），报 Owner 定夺。registry 零触碰。 |

- 判死执行的授权链：本卡（预注册）+裁定#489①（"一次窗口定生死"预授权）=Owner 事前批准；若 commit 时注册表净删门位（宪法 §5 high 域）被拦，则按门禁处方呈 Owner 晨会，判死分数先落 docs/_working/fexam/ 产出文件不丢。
- **复活条款**（沿裁定#489① 原文）：全网调查车道若证伪我方实现或考法，按新条目复活重考；判死不阻断该复活通道。

## 7. 样本窗与一次窗口时间定义

- **考试窗（判生死唯一窗）**：2025-10-09 ~ 2026-09-30（与第一波 indicator_exam_scores_v1 同窗：同窗可比、数据已就绪；且条件异质性统计量在第一波从未计算，无适应性污染）。
- **参照窗（report-only，零判死权重）**：2024-10-08 ~ 2025-09-30——同管线重算全判据并列报；与考试窗结论一致时在 evidence 加注 consistent，不一致不影响生死。
- **数据加载窗**：指标面板与 close 面板均自 2024-08-01 起（覆盖参照窗首日 + B1 的 20 日回看 + 冗余余量；指标值系存量列，预热由数据管道负责）。
- **一次窗口语义（冻结）**：本卡 commit 后，W3 对考试窗执行**恰好一次**完整判据计算并冻结产出（docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml）。PASS/FAIL/VOID 三种结局均**耗尽**本卡执行权；换参、换窗、换基线、加指标、跨指标联合的任何重跑，一律须新预注册卡+新裁定授权。跑数必须晚于本卡 commit（预注册先于首跑；W3 在产出文件记录本卡 commit hash 作锚）。
- **设备**：CPU（pandas spearman + statsmodels HAC；与第一波 device_policy 同口径；HAC Wald 无随机数，结果确定性可复算）。

## 8. 与裁定#489③ 及格线 v1 的关系声明

1. **判据独立**：条件考场判据（分层增益显著性，§4~§5）与裁定#489③ 及格线 v1（IC>0.02/ICIR>0.3/retain≥0.5）**相互独立、互不替代、互不抵扣**。及格线 v1 是**方向性**因子/指标进池及格线（科目=方向预测）；CYC 条件考场科目=**条件增益**（层间 IC 异质性），非方向科目，及格线 v1 对其不适用——CYC 四件不因 |IC_5d|≈0 在本考场失分，也不因本考场判活而取得方向因子池资格。
2. **校正族独立**：及格线 v1 的进池护栏（Bonferroni/DSR，143 候选族，裁定#489③ 原文）与本考场校正族（N_fam=11，§5.2）**分别计算，不合并**。
3. **唯一交集**：基线有效性护栏 |μ_all|≥0.01 借用及格线 IC 下限 0.02 之半作 void 线（§3）——护栏非及格判定，不构成对及格线 v1 的引用扩张。
4. 定位对齐：及格线 v1 为临时版（3 个月 paper 池回调，裁定#489③）；本卡判据同样一次冻结，任何回调走新预注册，不追溯本考场。

## 9. W3 施工手册（照卡执行，禁止发挥）

### 9.1 数据源映射（全部 CH 只读，经 DatabaseService/ch_data 同款口径）

| 数据 | 表.列 | 加载 |
|---|---|---|
| ht_dcperiod / ht_dcphase / ht_sine / ht_leadsine / ht_trendmode | c1_market.technical_indicator 对应列 | load_panel，2024-08-01~2026-09-30 |
| 后复权收盘 | c1_market.kline_daily_hfq.close | load_close 同窗 |
| r5 / mom20 / rev5 | 由 close 派生 | forward_returns 式 + shift(20)/shift(5) |

### 9.2 确定性算法步序（唯一合法实现顺序）

1. 加载指标面板与 close 面板 → 构造 r5、mom20。
2. 基线有效性判定（§3 顺序）→ 冻结 baseline_used；双废 → 写 VOID 产出并停止。
3. 逐指标构造层标签（§2 公式）→ 层有效性计数（§4.5，只看缺失掩码不看收益值）→ 冻结 K_i^eff 与 N_fam → **写入产出文件的 family_size 字段**。
4. 解盲：逐日层内 IC → 全截面 IC → 两两 D_t → HAC t 检验（§5.1 恰按所写调用）→ p_adj（×N_fam）。
5. 按本卡 §5.2 判活逻辑与 §6 分支落地产出文件；严禁第 4 步之后回头改 1~3 步任何选择。

### 9.3 产出文件 schema（冻结：docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml）

```yaml
doc_type: fexam_indicator_conditional_scores   # 产出在 docs/_working/fexam/（若门禁提示 doc_type 违规按门禁处方去字段）
version: v1
generated_at_utc: <执行时刻>
prereg_ref:
  card: docs/_working/matrix_campaign/mining/cyc_conditional_prereg_v1.md
  card_commit: <本卡 commit hash>
  ruling: 裁定#489①
baseline_used: B1 | B2
baseline_ic_all: <μ_all>
family_size: <N_fam，预期 11>
exam_window: ['2025-10-09', '2026-09-30']
per_indicator:
  IND-CYC-001: {strata: {D1: {n_days, n_stockdays, mu_s}, D2: {...}, D3: {...}}, mu_all: <..>, gain: <G>,
                pairs: [{a: D1, b: D2, mean_d: <..>, t_hac: <..>, p_raw: <..>, p_adj: <..>}, ...],
                verdict: pass|fail|void, void_reason: <..>}
  IND-CYC-002: {... }   # 层 P1..P4
  IND-CYC-004: {... }   # 层 W0/W1
  IND-CYC-005: {... }   # 层 M0/M1
family_verdict: pass | fail | void
ref_window_report: <同构摘要，report-only>
device_ledger: [{object: indicator_conditional_exam, device: cpu, statsmodels_hac_maxlags: 10, rng: none}]
```

### 9.4 禁改清单（违反=本卡作废+违规登记）

跨指标联合分层 / 其他 horizon / 换基线 / 日历子窗替代相位层 / 市场级指数序列 / 参数网格 / 改层切点 / 改 HAC lag / 改校正族定义 / 改判活逻辑 / 解盲后改 N_fam。

## 10. 冻结与变更控制

- 本卡自 commit 起冻结；任何修改（含笔误正名）=旧卡作废+新卡（版本号 v2+）+新裁定登记，禁止原地改。
- 判据真源唯一=本卡；W3 产出与 registry 判死动作引用本卡 commit hash。
- 自裁记录：①车道卡要求文件头 `# [TTL] permanent`，docs/_working 临时区 FILE-PLACEMENT-TTL 禁 permanent——沿 L6 卡同款处置（frontmatter ttl: task_bound+promote 意图留痕），非判据面变更；②"分层增益显著性"裁定#489① 未给计算口径，本卡按条件变量考场语义将其落为"层间 IC 均值两两差 HAC 检验+Bonferroni(11)"，是授权范围内的实现细化而非改判据；③部分判活时未判活成员按个体判死处置（裁定#489① 只明文了全灭分支，个体判死与"整族归档"不冲突且更符合注册表逐条 status 语义）。
