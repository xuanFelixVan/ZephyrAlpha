---
doc_type: audit_report
title: 候选模块清单 — D_PF_ALLOC
version: "1.0"
status: active
date: auto-generated
owner: auto-generator
ttl: permanent
---

# D_PF_ALLOC 候选模块清单

> [← 返回索引](index.md)

> 本域候选 **82** 条（原有 1 + harvest 81）。
> harvest 去重四态: likely_new=45 / likely_implemented=18 / likely_planned=12 / uncertain=6

## 完整清单

| ID | 名称 / Name | 大白话（干什么用） | 域 | 状态 | 四问卡点 | 优先级 | 触发信号摘要 | 下次复查 |
|------|------|------|------|------|------|:---:|------|------|
| CAND-HARVEST-0091 | A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 | / PA-06 / A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 / ✅ 能建 / / K=E(R)/sigma^2凯利变体+市场环境系数+个股确定性系数 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0162 | Meta-Strategy Router元策略路由 | / PA-01 / Meta-Strategy Router元策略路由 / ✅ 能建 / / 根据Regime选择策略组合+权重分配+多样性守门 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0163 | Strategy Screening 3D Evaluator策略筛选三维评估器 | / PA-02 / Strategy Screening 3D Evaluator策略筛选三维评估器 / ✅ 能建 / / 收益风险清晰性+参数稳定性+天然互补性 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0164 | Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 | / PA-03 / Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 / ✅ 能建 / / 6个月滚动窗口+尾部相关EVT+因子重叠率 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0165 | Multi-Strategy Capital Allocator多策略资金分配 | / PA-04 / Multi-Strategy Capital Allocator多策略资金分配 / ✅ 能建 / / 多策略资金分配+权重优化+风险预算分配 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0166 | Strategy Correlation Gate G12 Executor策略相关性门禁 | / PA-05 / Strategy Correlation Gate G12 Executor策略相关性门禁 / ✅ 能建 / / 相关性>0.85拒绝/因子重叠>60%警告 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0167 | A-Share Position Formula Calculator A股仓位公式计算器 | / PA-07 / A-Share Position Formula Calculator A股仓位公式计算器 / ✅ 能建 / / 仓位=市场环境系数x确定性系数x总资金 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0168 | A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 | / PA-08 / A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 / ✅ 能建 / / 凯利公式动态仓位+概率化仓位+胜率/赔率自适应 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0169 | Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 | / PA-09 / Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 / ❌ 不能建 / / 门禁: ①主力意图识别准确率>60% ②开发带宽释放 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0170 | Signal Synthesis Combiner信号合成器 | / PA-10 / Signal Synthesis Combiner信号合成器 / ✅ 能建 / / 多策略信号→重合加权重→输出合成信号 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0171 | Strategy Retirement Trigger策略退役触发器 | / PA-11 / Strategy Retirement Trigger策略退役触发器 / ✅ 能建 / / Sharpe 12m<0/Calmar 12m<0.3/连续6月亏损→退休 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0172 | Strategy Retirement Capital Recycler策略退役资金回收器 | / PA-12 / Strategy Retirement Capital Recycler策略退役资金回收器 / ✅ 能建 / / 策略退休后资金自动回收并重新分配 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0173 | MaxDDLimit Allocation Strategist最大回撤限制分配器 | / PA-13 / MaxDDLimit Allocation Strategist最大回撤限制分配器 / ✅ 能建 / / MaxDDLimit分配+最大回撤约束动态调整 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0174 | Position Limit Gate Checker仓位限制门禁检查器 | / PA-14 / Position Limit Gate Checker仓位限制门禁检查器 / ✅ 能建 / / G10单只股票仓位不能超限+仓位计算/阈值/告警 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0175 | Execution Feedback Bridge执行反馈桥 | / PA-15 / Execution Feedback Bridge执行反馈桥 / ✅ 能建 / / D-EXECUTION→ALLOC执行结果反馈+仓位偏差修正 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0473 | §30.1.4 D-PF-ALLOC 组合分配域（15个模块） | §30.1.4 D PF ALLOC 组合分配域（15个模块） | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0747 | Dynamic Capital Allocator 动态资金分配器 | 动态资金分配Kelly准则风险预算波动率目标回撤约束资金曲线 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0748 | Position Sizer 仓位计算器 | 仓位计算器固定比例ATR波动率风险平价凯利自适应仓位 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-0750 | Leverage Manager 杠杆管理器 | 杠杆管理器杠杆率计算杠杆约束杠杆调整融资成本杠杆风险监控 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3236 | PA-02 Strategy Screening 3D 策略 | 已合并入PA-05 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3237 | PA-03 Rolling Window Correlation PA-03滚动窗口相关性 | 已合并入PA-04 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3238 | PA-06/07/08 A-Share Position 仓位 | 3个已合并入PA-06 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3239 | PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | 已合并入D-RISK | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3240 | PA-11/12 Strategy Retirement 策略 | 2个已合并入PA-05 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3241 | PA-15 Execution Feedback Bridge 执行 | 已移除D-EX-CORE | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3242 | 体制自适应权重 Regime Adaptive Weight | 趋势体制→动量信号权重↑均值回归→反转信号权重↑ | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3243 | 策略指纹相似度 Strategy Fingerprint Similarity | 相似度>90%否决上线与PA-04联动 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3244 | 因子正交性 Factor Orthogonality | 因子正交性度量替代天然互补性 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3245 | 多策略投票 Multi-Strategy Voting | 信号驱动投票策略综合得分 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3246 | 共振融合 Resonance Fusion | 全部同向→强共振多数同向→中等分歧→弱 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3247 | 决策去重 Decision Deduplication | 同标的同方向多策略重复信号→合并为一条指令 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3248 | 跨策略仓位合并 Cross-Strategy Position Merging | 同标的多策略合并→取sum不超上限 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3249 | 信号冲突检测 Signal Conflict Detection | 多策略同时触发时的语义冲突检测+优先级裁决 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3250 | 风险预算范式 Risk Budgeting Paradigm | 组合风险预算→协方差分解→每标的风险配额 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3251 | 收缩估计 Shrinkage Estimation | 协方差估计收缩估计/因子模型/Copula-GARCH | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3252 | 因子模型 Factor Model | 协方差估计因子模型 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3253 | Copula-GARCH Copula-GARCH模型 | 协方差估计Copula-GARCH持仓≤50只 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3254 | 相关性体制监控 Correlation Regime Monitoring | 牛市相关性趋同→分散化失效预警 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3255 | 7状态生命周期 7-State Lifecycle | 草稿→回测→模拟→试运行→上线→降级→退役 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3256 | 冷启动协议 Cold Start Protocol | 初始仓位=风险预算仓位×冷启动系数30% | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3257 | 策略衰减检测 Strategy Decay Detection | 实盘-回测Sharpe偏差监控偏差>30%告警 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3258 | Kelly公式 Kelly Formula | f*=μ/σ²连续时间形式机构仓位管理标准 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3259 | 半Kelly硬上限 Half Kelly Hard Cap | f*×0.5行业惯例防止过度集中 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3260 | 组合级硬约束 Portfolio Hard Constraints | / 约束集 / 单标的≤min(5%,f*/2); 板块暴露≤20%; 组合VaR_95%≤净值×2%; MaxDD≤15% / 组合级硬约束 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3261 | 分批建仓 Batch Position Building | 市场驱动与策略新旧无关 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3262 | 策略同质化检测 Strategy Homogeneity Detection | 策略指纹相似度+市场拥挤度指标 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3263 | 隐性串谋检测 Implicit Collusion Detection | 行为相关性系数+反事实差异 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3264 | 尾部相关性飙升 Tail Correlation Surge | 条件相关系数+Copula尾部相关参数 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3265 | 因子重叠 Factor Overlap | 因子重叠率共享因子/总因子 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3266 | 股票池重叠 Stock Pool Overlap | 股票池重叠率+重叠标的行业分布 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3267 | 标的级拥挤 Target-level Crowding | 同标的活跃策略数/总策略数 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3268 | 板块级拥挤 Sector-level Crowding | 同板块活跃策略数/总策略数 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3269 | 资本传染 Capital Contagion | 策略间资本流动相关性单策略Hard Stop隔离 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3270 | 信号传染 Signal Contagion | 共享因子IC衰减联动因子失效→所有依赖策略同步降级 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3271 | 情绪传染 Sentiment Contagion | 同一时段止损策略数/总策略数止损错峰执行 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3272 | 模型间假设不一致 Inter-model Assumption Inconsistency | 同一风险因子不同分布假设 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3273 | 模型共振反应 Model Resonance Response | 对相同输入的共振组合尾部ES>单模型ES之和 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3274 | 模型叠加尾部放大 Model Stacking Tail Amplification | 尾部放大效应SR 26-2关注点 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3275 | 策略容量超限 Strategy Capacity Exceeded | 容量=f(ADV,参与率上限 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3276 | ST-006 量化踩踏 | 因子拥挤+策略同质化→同步抛售场景 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3279 | 目标权重向量输出 Target Weight Vector Output | 学习系统产出目标权重→PA-03消费执行 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3280 | 4级决策 APPROVE/REDUCE/REJECT/FLATTEN | PA-03执行权重分配风控4级决策 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3281 | 模块组合发现 Module Combination Discovery | 元学习组合发现结果作为PA-01路由辅助输入 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3282 | 数据流优化 Data Flow Optimization | 数据流跳数作为PA-02合成效率指标 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3283 | 策略权重进化 Strategy Weight Evolution | 元学习反馈策略效果→PA-03调整资本分配 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3284 | Module Registry 4状态映射 | / Module Registry映射 / 草稿+回测+模拟→trial, 上线→active, 降级→trial, 退役→deprecated→archived / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3285 | D-L0→D-L1 降级路径 | 分配权重偏向防御策略降低进攻型策略权重 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3286 | D-L1→D-L2 降级路径 | 仅分配给保命规则集允许的仓位总仓位≤30% | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3287 | D-L2→D-L3 降级路径 | 停止一切分配冻结资金 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3288 | P2 signal_engine 策略路由进程 | 策略路由进程归属核4-7 16GB | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3291 | 策略冲突检测 Strategy Conflict Detection | 多策略同时触发时的语义冲突检测+优先级裁决 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3292 | 盘中执行必做项 Intraday Execution Must-do | 策略信号合规检查+风控参数确认+仓位限额验证 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3294 | MOD-L05-001 蓝图 | 蓝图状态MOD-L05-001未建设partial | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3299 | IC加权 IC Weighting | IC加权w_i=IC_i/Σ/IC_j/ | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3311 | PA-04增量 隐性串谋检测扩展 | 需扩展隐性串谋检测行为相关性>90%且指纹相似度<80% | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3312 | PA-04增量 标的级/板块级集中度监控 | **PA-04增量**: 已覆盖尾部相关EVT+6个月滚动窗口。新增维度: 标的级/板块级策略集中度监控。PA-01路由时需考虑拥挤度。 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3313 | PA-05增量 传染路径检测与隔离 | 需扩展传染路径检测与隔离 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3314 | 安全隔离 Safety Isolation | / 安全隔离 / Python策略即使有bug，最多产生错误目标权重，物理上无法绕过风控 / 学习系统架构§11.3 / | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3315 | 解耦保证 Decoupling Guarantee | 学习系统与执行层完全解耦学习系统崩溃不影响已有仓位 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3316 | ESRB系统性风险向量 ESRB Systemic Risk Vector | 顺周期性+模型同质性+互联性PA缓解措施 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-HARVEST-3317 | 仲裁规则 Arbitration Rules | 冷启动vs风险预算/跨策略仓位合并vs单票仓位上限/风险预算仓位vs市场状态仓位上限 | D_PF_ALLOC | 候选待评（candidate） | 待评估 | P2 | — | 2026-11-30 |
| CAND-PFALLOC-001 | Min-Variance & Risk-Parity Rebalance Modes / 最小方差与风险平价再平衡模式 | 给组合分配加两种经典量化算法：最小方差（让组合波动最小）和风险平价（让各资产风险均摊）。现在枚举值定义了但方法没写，选了会偷偷退回等权。 | D_PF_ALLOC | 延后（deferred） | 四问全过 | P1 | 实盘需启用 min_variance/risk_parity 分配模式 等3条 | 2026-11-30 |

## 按四问卡点分组（为什么没开发）

> 四问过滤：q1已实现 / q2需求驱动 / q3域活着 / q4 AI替代。任一问「否」即不进 depgraph 设计态，登记在候选库。

### 待评估（81 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-HARVEST-0091 | A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 | / PA-06 / A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 / ✅ 能建 / / K=E(R)/sigma^2凯利变体+市场环境系数+个股确定性系数 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0162 | Meta-Strategy Router元策略路由 | / PA-01 / Meta-Strategy Router元策略路由 / ✅ 能建 / / 根据Regime选择策略组合+权重分配+多样性守门 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0163 | Strategy Screening 3D Evaluator策略筛选三维评估器 | / PA-02 / Strategy Screening 3D Evaluator策略筛选三维评估器 / ✅ 能建 / / 收益风险清晰性+参数稳定性+天然互补性 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0164 | Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 | / PA-03 / Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 / ✅ 能建 / / 6个月滚动窗口+尾部相关EVT+因子重叠率 / | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0165 | Multi-Strategy Capital Allocator多策略资金分配 | / PA-04 / Multi-Strategy Capital Allocator多策略资金分配 / ✅ 能建 / / 多策略资金分配+权重优化+风险预算分配 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0166 | Strategy Correlation Gate G12 Executor策略相关性门禁 | / PA-05 / Strategy Correlation Gate G12 Executor策略相关性门禁 / ✅ 能建 / / 相关性>0.85拒绝/因子重叠>60%警告 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0167 | A-Share Position Formula Calculator A股仓位公式计算器 | / PA-07 / A-Share Position Formula Calculator A股仓位公式计算器 / ✅ 能建 / / 仓位=市场环境系数x确定性系数x总资金 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0168 | A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 | / PA-08 / A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 / ✅ 能建 / / 凯利公式动态仓位+概率化仓位+胜率/赔率自适应 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0169 | Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 | / PA-09 / Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 / ❌ 不能建 / / 门禁: ①主力意图识别准确率>60% ②开发带宽释放 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0170 | Signal Synthesis Combiner信号合成器 | / PA-10 / Signal Synthesis Combiner信号合成器 / ✅ 能建 / / 多策略信号→重合加权重→输出合成信号 / | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0171 | Strategy Retirement Trigger策略退役触发器 | / PA-11 / Strategy Retirement Trigger策略退役触发器 / ✅ 能建 / / Sharpe 12m<0/Calmar 12m<0.3/连续6月亏损→退休 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0172 | Strategy Retirement Capital Recycler策略退役资金回收器 | / PA-12 / Strategy Retirement Capital Recycler策略退役资金回收器 / ✅ 能建 / / 策略退休后资金自动回收并重新分配 / | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0173 | MaxDDLimit Allocation Strategist最大回撤限制分配器 | / PA-13 / MaxDDLimit Allocation Strategist最大回撤限制分配器 / ✅ 能建 / / MaxDDLimit分配+最大回撤约束动态调整 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0174 | Position Limit Gate Checker仓位限制门禁检查器 | / PA-14 / Position Limit Gate Checker仓位限制门禁检查器 / ✅ 能建 / / G10单只股票仓位不能超限+仓位计算/阈值/告警 / | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0175 | Execution Feedback Bridge执行反馈桥 | / PA-15 / Execution Feedback Bridge执行反馈桥 / ✅ 能建 / / D-EXECUTION→ALLOC执行结果反馈+仓位偏差修正 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0473 | §30.1.4 D-PF-ALLOC 组合分配域（15个模块） | §30.1.4 D PF ALLOC 组合分配域（15个模块） | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-0747 | Dynamic Capital Allocator 动态资金分配器 | 动态资金分配Kelly准则风险预算波动率目标回撤约束资金曲线 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-0748 | Position Sizer 仓位计算器 | 仓位计算器固定比例ATR波动率风险平价凯利自适应仓位 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-0750 | Leverage Manager 杠杆管理器 | 杠杆管理器杠杆率计算杠杆约束杠杆调整融资成本杠杆风险监控 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3236 | PA-02 Strategy Screening 3D 策略 | 已合并入PA-05 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3237 | PA-03 Rolling Window Correlation PA-03滚动窗口相关性 | 已合并入PA-04 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3238 | PA-06/07/08 A-Share Position 仓位 | 3个已合并入PA-06 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3239 | PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | 已合并入D-RISK | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3240 | PA-11/12 Strategy Retirement 策略 | 2个已合并入PA-05 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3241 | PA-15 Execution Feedback Bridge 执行 | 已移除D-EX-CORE | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3242 | 体制自适应权重 Regime Adaptive Weight | 趋势体制→动量信号权重↑均值回归→反转信号权重↑ | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3243 | 策略指纹相似度 Strategy Fingerprint Similarity | 相似度>90%否决上线与PA-04联动 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3244 | 因子正交性 Factor Orthogonality | 因子正交性度量替代天然互补性 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3245 | 多策略投票 Multi-Strategy Voting | 信号驱动投票策略综合得分 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3246 | 共振融合 Resonance Fusion | 全部同向→强共振多数同向→中等分歧→弱 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3247 | 决策去重 Decision Deduplication | 同标的同方向多策略重复信号→合并为一条指令 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3248 | 跨策略仓位合并 Cross-Strategy Position Merging | 同标的多策略合并→取sum不超上限 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3249 | 信号冲突检测 Signal Conflict Detection | 多策略同时触发时的语义冲突检测+优先级裁决 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3250 | 风险预算范式 Risk Budgeting Paradigm | 组合风险预算→协方差分解→每标的风险配额 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3251 | 收缩估计 Shrinkage Estimation | 协方差估计收缩估计/因子模型/Copula-GARCH | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3252 | 因子模型 Factor Model | 协方差估计因子模型 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3253 | Copula-GARCH Copula-GARCH模型 | 协方差估计Copula-GARCH持仓≤50只 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3254 | 相关性体制监控 Correlation Regime Monitoring | 牛市相关性趋同→分散化失效预警 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3255 | 7状态生命周期 7-State Lifecycle | 草稿→回测→模拟→试运行→上线→降级→退役 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3256 | 冷启动协议 Cold Start Protocol | 初始仓位=风险预算仓位×冷启动系数30% | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3257 | 策略衰减检测 Strategy Decay Detection | 实盘-回测Sharpe偏差监控偏差>30%告警 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3258 | Kelly公式 Kelly Formula | f*=μ/σ²连续时间形式机构仓位管理标准 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3259 | 半Kelly硬上限 Half Kelly Hard Cap | f*×0.5行业惯例防止过度集中 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3260 | 组合级硬约束 Portfolio Hard Constraints | / 约束集 / 单标的≤min(5%,f*/2); 板块暴露≤20%; 组合VaR_95%≤净值×2%; MaxDD≤15% / 组合级硬约束 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3261 | 分批建仓 Batch Position Building | 市场驱动与策略新旧无关 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3262 | 策略同质化检测 Strategy Homogeneity Detection | 策略指纹相似度+市场拥挤度指标 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3263 | 隐性串谋检测 Implicit Collusion Detection | 行为相关性系数+反事实差异 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3264 | 尾部相关性飙升 Tail Correlation Surge | 条件相关系数+Copula尾部相关参数 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3265 | 因子重叠 Factor Overlap | 因子重叠率共享因子/总因子 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3266 | 股票池重叠 Stock Pool Overlap | 股票池重叠率+重叠标的行业分布 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3267 | 标的级拥挤 Target-level Crowding | 同标的活跃策略数/总策略数 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3268 | 板块级拥挤 Sector-level Crowding | 同板块活跃策略数/总策略数 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3269 | 资本传染 Capital Contagion | 策略间资本流动相关性单策略Hard Stop隔离 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3270 | 信号传染 Signal Contagion | 共享因子IC衰减联动因子失效→所有依赖策略同步降级 | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3271 | 情绪传染 Sentiment Contagion | 同一时段止损策略数/总策略数止损错峰执行 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3272 | 模型间假设不一致 Inter-model Assumption Inconsistency | 同一风险因子不同分布假设 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3273 | 模型共振反应 Model Resonance Response | 对相同输入的共振组合尾部ES>单模型ES之和 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3274 | 模型叠加尾部放大 Model Stacking Tail Amplification | 尾部放大效应SR 26-2关注点 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3275 | 策略容量超限 Strategy Capacity Exceeded | 容量=f(ADV,参与率上限 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3276 | ST-006 量化踩踏 | 因子拥挤+策略同质化→同步抛售场景 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3279 | 目标权重向量输出 Target Weight Vector Output | 学习系统产出目标权重→PA-03消费执行 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3280 | 4级决策 APPROVE/REDUCE/REJECT/FLATTEN | PA-03执行权重分配风控4级决策 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3281 | 模块组合发现 Module Combination Discovery | 元学习组合发现结果作为PA-01路由辅助输入 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3282 | 数据流优化 Data Flow Optimization | 数据流跳数作为PA-02合成效率指标 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3283 | 策略权重进化 Strategy Weight Evolution | 元学习反馈策略效果→PA-03调整资本分配 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3284 | Module Registry 4状态映射 | / Module Registry映射 / 草稿+回测+模拟→trial, 上线→active, 降级→trial, 退役→deprecated→archived / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3285 | D-L0→D-L1 降级路径 | 分配权重偏向防御策略降低进攻型策略权重 | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3286 | D-L1→D-L2 降级路径 | 仅分配给保命规则集允许的仓位总仓位≤30% | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3287 | D-L2→D-L3 降级路径 | 停止一切分配冻结资金 | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3288 | P2 signal_engine 策略路由进程 | 策略路由进程归属核4-7 16GB | D_PF_ALLOC | harvest待评估（likely_planned） |  |
| CAND-HARVEST-3291 | 策略冲突检测 Strategy Conflict Detection | 多策略同时触发时的语义冲突检测+优先级裁决 | D_PF_ALLOC | harvest待评估（likely_implemented） |  |
| CAND-HARVEST-3292 | 盘中执行必做项 Intraday Execution Must-do | 策略信号合规检查+风控参数确认+仓位限额验证 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3294 | MOD-L05-001 蓝图 | 蓝图状态MOD-L05-001未建设partial | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3299 | IC加权 IC Weighting | IC加权w_i=IC_i/Σ/IC_j/ | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3311 | PA-04增量 隐性串谋检测扩展 | 需扩展隐性串谋检测行为相关性>90%且指纹相似度<80% | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3312 | PA-04增量 标的级/板块级集中度监控 | **PA-04增量**: 已覆盖尾部相关EVT+6个月滚动窗口。新增维度: 标的级/板块级策略集中度监控。PA-01路由时需考虑拥挤度。 | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3313 | PA-05增量 传染路径检测与隔离 | 需扩展传染路径检测与隔离 | D_PF_ALLOC | harvest待评估（uncertain） |  |
| CAND-HARVEST-3314 | 安全隔离 Safety Isolation | / 安全隔离 / Python策略即使有bug，最多产生错误目标权重，物理上无法绕过风控 / 学习系统架构§11.3 / | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3315 | 解耦保证 Decoupling Guarantee | 学习系统与执行层完全解耦学习系统崩溃不影响已有仓位 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3316 | ESRB系统性风险向量 ESRB Systemic Risk Vector | 顺周期性+模型同质性+互联性PA缓解措施 | D_PF_ALLOC | harvest待评估（likely_new） |  |
| CAND-HARVEST-3317 | 仲裁规则 Arbitration Rules | 冷启动vs风险预算/跨策略仓位合并vs单票仓位上限/风险预算仓位vs市场状态仓位上限 | D_PF_ALLOC | harvest待评估（likely_new） |  |

### 四问全过（1 条）

| ID | 名称 | 大白话（干什么用） | 域 | 卡点理由 | 替代方案 |
|------|------|------|------|------|------|
| CAND-PFALLOC-001 | Min-Variance & Risk-Parity Rebalance Modes / 最小方差与风险平价再平衡模式 | 给组合分配加两种经典量化算法：最小方差（让组合波动最小）和风险平价（让各资产风险均摊）。现在枚举值定义了但方法没写，选了会偷偷退回等权。 | D_PF_ALLOC | 首次登记(修正错误登记后)。原误登记为独立策略文件节点 MOD-PF-004/MOD-PF-005,源码验证为枚举方法级缺口后软删除节点并改录候选。待实盘需启用 min-variance/risk-parity 分配时晋升为 DefaultEquityStrategy 代码补丁(非新 depgraph 节点) | 维持 equal_weight/signal_weight。代价:无法执行 min-variance/risk-parity 分配,实盘分配策略受限 |

## 复查时间表

> 按 next_review_date 升序。复查时重新过四问，触发信号命中则晋升到 depgraph 设计态。

| 下次复查 | 复查频率 | ID | 名称 | 域 | 状态 | 上次复查结论 |
|------|------|------|------|------|------|------|
| 2026-11-30 | quarterly | CAND-PFALLOC-001 | Min-Variance & Risk-Parity Rebalance Modes / 最小方差与风险平价再平衡模式 | D_PF_ALLOC | 延后（deferred） | 首次登记(修正错误登记后)。原误登记为独立策略文件节点 MOD-PF-004/MOD-PF-005,源码验证为枚举方法级缺口后软删除节点并改录候选。待实盘需启用 min-variance/risk-parity 分配时晋升为 DefaultEquityStrategy 代码补丁(非新 depgraph 节点) |
| 2026-11-30 | quarterly | CAND-HARVEST-0091 | A-Share Dynamic Position Coefficient Calculator A股动态仓位系数 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0162 | Meta-Strategy Router元策略路由 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0163 | Strategy Screening 3D Evaluator策略筛选三维评估器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0164 | Rolling Window Dynamic Correlation Analyzer滚动窗口动态相关性 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0165 | Multi-Strategy Capital Allocator多策略资金分配 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0166 | Strategy Correlation Gate G12 Executor策略相关性门禁 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0167 | A-Share Position Formula Calculator A股仓位公式计算器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0168 | A-Share Kelly Position Dynamic Calculator A股凯利仓位动态计算 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0169 | Stackelberg Game-Theoretic Follower Stackelberg博弈跟随策略 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0170 | Signal Synthesis Combiner信号合成器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0171 | Strategy Retirement Trigger策略退役触发器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0172 | Strategy Retirement Capital Recycler策略退役资金回收器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0173 | MaxDDLimit Allocation Strategist最大回撤限制分配器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0174 | Position Limit Gate Checker仓位限制门禁检查器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0175 | Execution Feedback Bridge执行反馈桥 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0473 | §30.1.4 D-PF-ALLOC 组合分配域（15个模块） | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-0747 | Dynamic Capital Allocator 动态资金分配器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-0748 | Position Sizer 仓位计算器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-0750 | Leverage Manager 杠杆管理器 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3236 | PA-02 Strategy Screening 3D 策略 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3237 | PA-03 Rolling Window Correlation PA-03滚动窗口相关性 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3238 | PA-06/07/08 A-Share Position 仓位 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3239 | PA-09 Stackelberg Game PA-09斯塔克尔伯格博弈 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3240 | PA-11/12 Strategy Retirement 策略 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3241 | PA-15 Execution Feedback Bridge 执行 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3242 | 体制自适应权重 Regime Adaptive Weight | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3243 | 策略指纹相似度 Strategy Fingerprint Similarity | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3244 | 因子正交性 Factor Orthogonality | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3245 | 多策略投票 Multi-Strategy Voting | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3246 | 共振融合 Resonance Fusion | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3247 | 决策去重 Decision Deduplication | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3248 | 跨策略仓位合并 Cross-Strategy Position Merging | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3249 | 信号冲突检测 Signal Conflict Detection | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3250 | 风险预算范式 Risk Budgeting Paradigm | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3251 | 收缩估计 Shrinkage Estimation | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3252 | 因子模型 Factor Model | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3253 | Copula-GARCH Copula-GARCH模型 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3254 | 相关性体制监控 Correlation Regime Monitoring | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3255 | 7状态生命周期 7-State Lifecycle | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3256 | 冷启动协议 Cold Start Protocol | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3257 | 策略衰减检测 Strategy Decay Detection | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3258 | Kelly公式 Kelly Formula | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3259 | 半Kelly硬上限 Half Kelly Hard Cap | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3260 | 组合级硬约束 Portfolio Hard Constraints | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3261 | 分批建仓 Batch Position Building | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3262 | 策略同质化检测 Strategy Homogeneity Detection | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3263 | 隐性串谋检测 Implicit Collusion Detection | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3264 | 尾部相关性飙升 Tail Correlation Surge | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3265 | 因子重叠 Factor Overlap | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3266 | 股票池重叠 Stock Pool Overlap | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3267 | 标的级拥挤 Target-level Crowding | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3268 | 板块级拥挤 Sector-level Crowding | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3269 | 资本传染 Capital Contagion | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3270 | 信号传染 Signal Contagion | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3271 | 情绪传染 Sentiment Contagion | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3272 | 模型间假设不一致 Inter-model Assumption Inconsistency | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3273 | 模型共振反应 Model Resonance Response | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3274 | 模型叠加尾部放大 Model Stacking Tail Amplification | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3275 | 策略容量超限 Strategy Capacity Exceeded | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3276 | ST-006 量化踩踏 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3279 | 目标权重向量输出 Target Weight Vector Output | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3280 | 4级决策 APPROVE/REDUCE/REJECT/FLATTEN | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3281 | 模块组合发现 Module Combination Discovery | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3282 | 数据流优化 Data Flow Optimization | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3283 | 策略权重进化 Strategy Weight Evolution | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3284 | Module Registry 4状态映射 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3285 | D-L0→D-L1 降级路径 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3286 | D-L1→D-L2 降级路径 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3287 | D-L2→D-L3 降级路径 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3288 | P2 signal_engine 策略路由进程 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_planned） |
| 2026-11-30 | quarterly | CAND-HARVEST-3291 | 策略冲突检测 Strategy Conflict Detection | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_implemented） |
| 2026-11-30 | quarterly | CAND-HARVEST-3292 | 盘中执行必做项 Intraday Execution Must-do | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3294 | MOD-L05-001 蓝图 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3299 | IC加权 IC Weighting | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3311 | PA-04增量 隐性串谋检测扩展 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3312 | PA-04增量 标的级/板块级集中度监控 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3313 | PA-05增量 传染路径检测与隔离 | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（uncertain） |
| 2026-11-30 | quarterly | CAND-HARVEST-3314 | 安全隔离 Safety Isolation | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3315 | 解耦保证 Decoupling Guarantee | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3316 | ESRB系统性风险向量 ESRB Systemic Risk Vector | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
| 2026-11-30 | quarterly | CAND-HARVEST-3317 | 仲裁规则 Arbitration Rules | D_PF_ALLOC | 候选待评（candidate） | harvest待评估（likely_new） |
