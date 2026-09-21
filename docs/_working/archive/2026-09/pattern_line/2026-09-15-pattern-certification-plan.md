---
ttl: task_bound
---

# [BLUEPRINT] | docs/_working/2026-09-15-pattern-certification-plan.md |
<!-- [MODULE] MOD-SIG-147 -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] M -->

# 反过拟合自动认证方案——把"读表人"变成状态机（st-patmine-20260914 续班，2026-09-15）

> 状态：**v1.0 冻结待施工**。缘起：Owner 问"形态会不会过拟合/读表的人是谁？我需要全自动"。
> 本方案把上一班交底的三个半堵统计洞（多重检验/样本重叠/regime 混淆）工程化为四道
> 自动闸门+一个认证状态机，零新增人工判断点。挖矿日志=§四。

## 一、问题定性（为什么现在的表不能直接读）

| 洞 | 机理 | 实例（图形库实测） |
|----|------|------------------|
| H1 多重检验 | 424 个合格切片在同源数据上各测一次"是否>基线"，必有纯运气赢家 | 胜率页前排被个位数小样本切片占满 |
| H2 样本重叠 | w 日前视窗逐日滚动，事件互相重叠，n 虚高且独立假设失效 | 双顶 n=5517 实际独立度远低；Wilson LB 因此不够保守 |
| H3 regime 混淆 | 事件在时间/regime 上扎堆，胜率反映"何时响"而非"响多准" | 高分行集中在 r11/r12 切片 |
| H4 权重回路易强化 | 幸运 streak→加权→更大影响→账面更好（若权重乘进强度） | 当前开环未接油门（115 human_gated 未动）——接通前必须过本方案认证 |

## 二、方案主体：pattern_evidence_certify 认证器（四闸机器化）

新模块（147 线，拟 MOD-SIG-148）+新任务块+新认证表。**全部判据从现有
market_pattern_win_rate 表可算，零新数据依赖、零人工输入。**

### 闸A 多重检验修正（FDR，堵 H1）
- 每切片：精确二项检验 H0: p ≤ baseline_p（取同 timeframe/direction/fwd_window[/regime]
  的 `__baseline__` 行），得 p_value；
- BH-FDR（Benjamini-Hochberg 1995）跨同族（同 timeframe+direction+fwd_window 全部切片）
  得 q_value；可选 Storey π0 自适应（二期）；
- 认证线：**q < 0.05**。谱系：Bajgrowicz & Scaillet 把 FDR 用于交易规则筛选（arXiv
  2006.04269）；White Reality Check/Hansen SPA/Deflated Sharpe（Bailey & López de
  Prado 2014 JPM，SSRN 2460551）=同问题族，DSR 思想"按试验次数 N 折扣统计量"由 FDR
  在二项语境落地。

### 闸B 有效样本（堵 H2）
- **n_eff = n_events / fwd_window**（w 日重叠窗的保守折扣）；
- 二项检验与 Wilson LB 一律用 n_eff（LB(n_eff) 比 LB(n) 更低=更诚实）；
- 认证线：**n_eff ≥ 30**（参数预注册；首月观察校准）。谱系：Hansen-Hodrick/Newey-West
  HAC（Hodrick 1992 RFS 长视界推断经典）；注意 Britten-Jones & Neuberger 实证 HH/NW
  在重叠语境仍偏低估——故取保守折扣而非精确修正。

### 闸C regime 混淆（分制度一致，堵 H3）
- 形态在其触发过的各 regime 内分别对照**该 regime 的基线行**（materialize 已按
  (timeframe,regime,direction,fwd_window) 出基线，现成可查）；
- 认证线：**within-regime edge 按事件占比加权 > 0**，且无单一 regime 贡献 >90% edge
  （防单切片独活）。

### 闸D 贝叶斯收缩读数（替代裸 hit_rate，堵"骗人读数"）
- **shrunk_rate = (hits + k·baseline) / (n_eff + k)**，k=先验强度（预注册 k=100）；
- "100%/76"这类读数经收缩后回到基线邻域，前端与加权统一用 shrunk_rate，裸 hit_rate
  保留仅作对账。谱系：Efron & Morris 1975（Stein 收缩棒球平均）→beta-binomial 经验
  贝叶斯（Variance Explained 系列教程化）。

### 认证状态机（替代读表人）
| 状态 | 判据 | 效果 |
|------|------|------|
| **certified** | A∧B∧C∧D 全过 | 权重可参与强度（未来接通时）；前端"认证"徽章 |
| **probation** | A+B 过、C 未过（regime 混淆嫌疑） | 只记账不接油门 |
| **failed** | A 或 B 不过 | 权重地板价；前端灰标 |
| **retired** | 连续 M=20 个物化窗 failed | 自动降权至地板，复活=重新认证 |

- 状态流转写只追加台账（MOD-BT-091 hypothesis_precheck 同款纪律：判定由代码生成
  禁手填、运动员不兼任裁判——认证器只读统计表，形态实现方不参与自身判定）；
- **全部阈值（q=0.05/n_eff=30/k=100/M=20）随本蓝图预注册，改动=裁定留痕，禁静默调**。

### 链序与持久化
- 任务块 pattern_evidence_certify（daily_kline 档，DAG 依赖 pattern_win_rate_materialize，
  先于 pattern_weight_sync；capability 三点注册同 W-C3 先例）；
- 认证结果落新表 c1_market.market_pattern_certification（五元组键+p_value/q_value/
  n_eff/shrunk_rate/within_regime_edge/certified/certified_at；ReplacingMergeTree 幂等；
  DDL 走 schemas/categories 注册，production 流转挂 Owner 门位）；
- weight_sync 消费口径升级：录样本用 shrunk_rate（替代 raw），仅 certified/probation
  参与调权；前端胜率页增"认证"列（certified 徽章/failed 灰标，双口径并列展示）。

## 三、施工批切分（按 construction SOP，方案冻结后走 15 步）
- **W-CA 统计核**：certifier 纯函数模块（二项精确检验/BH-FDR/n_eff/收缩/状态机）+已知
  向量单测（教科书 p 值与收缩例）
- **W-CB 落地批**：任务块+capability 三点+认证表 DDL+全量回填
- **W-CC 消费批**：weight_sync 换 shrunk 口径+前端认证列
- 明确不做：不改 mapper 强度公式（权重接油门=独立裁定，须过预注册+前向验证）；
  不做 PBO/CSCV（无参数网格重训场景，FDR 已覆盖本语境）。

## 四、挖矿日志（SOP §6）

| 轮 | 矿脉 | 内部半边 | 全网半边 | 判定 | 吸收 |
|---|------|---------|---------|------|------|
| R1 | 多重检验修正 | 424 切片同源=家族定义 | Deflated Sharpe/PBO/CSCV（Bailey & López de Prado 2014 JPM，SSRN 2460551；DSR=按试验数 N 折扣） | **signal** | 闸A：FDR 在二项语境落地 DSR 思想 |
| R2 | FDR 自动化 | family=同窗同向切片集 | Bajgrowicz & Scaillet FDR 筛交易规则（arXiv 2006.04269）+White RC/Hansen SPA/Storey π0（Quant Trader Journal 等） | **signal** | 闸A：BH 步骤+q 值认证线 |
| R3 | 重叠样本推断 | w 日窗逐日滚动=重叠源 | Hansen-Hodrick/Newey-West/Hodrick 1992 RFS；Britten-Jones & Neuberger：HH/NW 在重叠语境仍偏低估（Warwick PDF） | **signal** | 闸B：n_eff 保守折扣（比精确 HAC 更稳） |
| R4 | regime 混淆 | regime_tag 切片+分 regime 基线行现成 | 复用在库调研（st-c5promote 挂图可行性：regime-conditional activation 系，Wang 2020 HMM/SSRN Markov switching——同矿脉不重复挖） | signal(内部) | 闸C：分制度对照线 |
| R5 | 贝叶斯收缩 | "100%/76"读数实例 | Efron-Morris 1975+beta-binomial 经验贝叶斯（Variance Explained/MetricGate） | **signal** | 闸D：shrunk_rate 替代裸读数 |
| R6 | 工业认证管线 | 预注册设施 MOD-BT-091+holdout 锁窗纪律在库 | 复用在库 st-c5promote 调研（WorldQuant BRAIN 全 API 化自动入库管线/自相关簇拒绝） | signal(复用) | 状态机+台账纪律对齐工业先例 |

终止判定：R1-R5 新挖全 signal、R6 复用在库——**时间盒封批收敛**（继续挖的边际已进入
实现细节）。四闸结论：R1/R2/R3/R5 均 ≥2 独立来源；A股适配=全部判据只依赖既有统计表
（T+1/涨跌停语义已内嵌于事件表 PIT 口径）；可回测性=认证器本身输出可重放对账的
p/q/n_eff/shrunk 向量；字段全既有+一张新认证表（DDL 流程内）。

## 五、净零声明与不做清单
- 新增判据全部替代"人工读表"（本方案的本质是把人从回路里删掉），无新增规则/gate；
- 不做：mapper 强度接权重（独立裁定）、PBO/CSCV、Storey π0（二期可选）、多方向扩切片
  （另批）；retired 形态不从目录删（目录完整性优先，只降权+灰标）。
