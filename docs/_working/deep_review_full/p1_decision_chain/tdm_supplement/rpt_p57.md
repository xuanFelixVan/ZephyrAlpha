---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——多维归因引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：多维归因引擎（P57）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_core/core/performance_attribution_engine.py:223`（PerformanceAttributionEngine；brinson_attribute:296 / attribute_full:591 / attribute_multi_period:668）
- TDM 节点: TDM-F-C3-01（aggregation，config/trading_decision_map.yaml:3883，归因汇聚改落引擎节点）
- 生产调用方: **链顶孤儿**——唯一实例化点=`risk/core/performance_attribution_degradation.py:124`（MOD-RK-37 包装层，声明 MOD-PF-007 为判定唯一真源），但 PerformanceAttributionDegradationGuard 全仓零实例化；header 声明的 D_REPORTING/D_GOV_ENFORCEMENT/MOD-PF-001 三消费方 grep 零实际调用（reporting/attribution_calculator.py:311 仅文档提及）
- 测试文件: tests/pf_core/test_performance_attribution_engine.py（92 passed 同批，与 P58/P59 合跑 5.69s）

## 1 对象快照

- 范围：PerformanceAttributionEngine 全文件（702 行）——Brinson-Fachler 三因子+因子归因+风险归因委托（MOD-RK-16）+IC 衰减降级检测+拥挤检测+OCP attribute 契约+多期算术链接。
- 排除项：RiskDecomposer（MOD-RK-16）与 StrategyCorrelationGate（MOD-PA-004）数学归各自对象；PerformanceAttributionReport 契约（shared/contracts）按消费口径引用。
- 测试覆盖概况：92 测试覆盖 Brinson 守恒/因子贡献/降级与拥挤分级/多期求和；**无权重和不等于 1 的解释性场景、无 baseline_ic=0 冷启动场景、无负相关拥挤场景**（三处恰为本报告发现）。
- 材料包缺项声明：运行时证据包未取（生产零调用）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **链顶孤儿**（checklist #8）：引擎仅被另一个孤儿（MOD-RK-37 包装层）实例化，包装层自身零生产调用方；TDM-F-C3-01 为归因汇聚节点（入边 5 条：E-L4-13/P2-03/S2-06/X-S2-06/E-L3-08），图上五路数据汇入、码上零路真实到达 | performance_attribution_engine.py:5-7；risk/core/performance_attribution_degradation.py:124；grep PerformanceAttributionDegradationGuard( 全仓零生产 | P2 | `grep -rn "PerformanceAttributionDegradationGuard(" src/ --include=*.py` |
| D | **TDM 节点声明语义大面积无承载**：algo_note 宣称「做T vs 持仓盈亏二分、IS 三分解（延迟/冲击/机会成本）」为节点核心能力，D84 列五条"正确性必改"（T+1 隔夜漂移切账/TWR 双轨/复权口径/孤儿成交 suspense/现金贡献行）——**七项全部零代码**；模块交付的是教材级 Brinson+因子+风险骨架。降级/拥挤检测与 TDM 另一声明的"策略降级检测（IC 衰减>50% 权重归 0 建议）"对齐 | config/trading_decision_map.yaml:3886-3921 vs performance_attribution_engine.py 全文（grep 做T/IS/延迟/TWR/复权 零命中） | P1 | 对照 TDM 节点逐项 grep 模块 |
| A | **多期归因用朴素算术求和，违反多期链接最佳实践**：attribute_multi_period 各期效应直接累加（:674-690 自注"简化为算术和"）——业界共识：算术效应跨期不可直接相加（复利口径漂移），须 Carino/Menchero/Frongello 平滑或几何法（CFA Institute 文献综述 2019 结论"无唯一正确法但朴素求和不在选项内"）。TDM-D84 自己也写明「策略 sleeve 用 TWR 几何链接」——代码与节点各自声明的正确口径双双未落地。月度跑一次的月间链接误差随期数累积 | performance_attribution_engine.py:668-702；CFA Institute（2019）Performance Attribution Literature Review, rpc.cfainstitute.org | P2 | 两期各 +5%/−5% 收益构造探针对比 naive 和与几何链接差 |
| A | Brinson 分解数学正确且守恒恒等式无条件成立（逐段代数验证 Σ三效应=Σwp·rp−Σwb·rb）；**但 B-F 配置效应口径要求 Σwp=Σwb（标准前置），模块不校验权重和**——部分组合/剔除现金场景下 allocation 项混入投资级效应，解释失真而守恒校验（is_consistent）恒真，假绿灯 | performance_attribution_engine.py:313-334,156-164 | P3 | 权重和 0.5 的两段输入跑 brinson_attribute 看 is_consistent=True 而口径已破 |
| A | total_return 字段名撒谎：报告字段 total_return=excess_return−cost_drag（净超额收益），非绝对收益；消费方按字面读=系统性高估（差额=基准收益+超额），月报/审计若直采即错账口径 | performance_attribution_engine.py:649-656 | P2 | 读 attribute_full 组装处+PerformanceAttributionReport 契约注释 |
| A | 风险归因结果计算后丢弃：attribute_full 调 risk_attribute 但结果不进报告（:643-647 仅日志降级）——TDM 声明的"风险归因"产出不存在，纯烧 CPU 的死计算 | performance_attribution_engine.py:642-647 | P3 | 读代码序确认返回值未接 |
| A | detect_degradation 的 baseline_ic≤0 分支把冷启动当死刑：baseline=0.0（无历史）+recent=0.10（走强）→ degraded=True 权重归零建议——注释"策略本就无效"对 baseline 恰为 0 的冷启动不成立，方向反（杀死新策略）。负 baseline（做空型 IC 语义）同样误判 | performance_attribution_engine.py:446-460 | P3 | detect_degradation('x', baseline_ic=0.0, recent_ic=0.10) 探针 |
| A | detect_crowding 用 |ρ| 绝对值判拥挤：ρ=−0.9（互相对冲的互补策略）被判 SEVERE 拥挤→建议归零——**杀掉分散化腿**，与拥挤检测的经济语义（同向扎堆）相反；声明在 docstring 但方向存疑 | performance_attribution_engine.py:510-523 | P3 | detect_crowding('A', {'B': -0.9}) 探针看 SEVERE |
| E | risk_attribute 包装把一切异常转 RiskDecompositionUnavailable（:417-420）——包括 KeyboardInterrupt 之外的编程错误（形状不匹配/NaN），统一"降级跳过+warning"：上游矩阵坏了=归因报告静默缺风险轴，仅日志可见 | performance_attribution_engine.py:417-420,646-647 | P3 | 传形状错误协方差看 warning 而非显式失败 |
| A(亮点) | Brinson 三公式与 B-F 教材一致；守恒校验 abs_tol=1e-9；因子归因 exposure 缺失安全取 0；阈值校验完备（ic_decay∈[0,1]/warn<severe） | performance_attribution_engine.py:319-334,270-273 | — | — |

## 3 SOTA 对照

- Brinson-Fachler 三因子：**对等已有（教材实现）**——B-F 模型（Brinson & Fachler 1985）为行业标准（Ortec Finance《Geometric attribution and the interaction effect》ortecfinance.com，2024-2026；Metricgate Multi-Period Attribution 文档，metricgate.com，2026）。单期实现合格。
- 多期链接：**立卡候选（缺陷修正依据）**——业界最佳实践=几何归因（Carl Bacon 几何 B-F 等价式）或算术+平滑算法（Carino 1999/Menchero/GRAP/Frongello）；CFA Institute 2019 文献综述结论"跨期链接无唯一正确法，但须显式平滑"（rpc.cfainstitute.org，2019；SSRN Gyger et al. 861844，2005；TSG Performance residuals 文，tsgperformance.com，2026）。本模块朴素求和属已知不良实践，且与 TDM-D84 自己声明的 TWR 几何链接冲突。
- IC 衰减降级+拥挤减半/归零：**对等已有**——IC 监控/衰减半衰期是量化风控标准作业（Alpha Architect《Information Decay》alphaarchitect.com，2019-2026 持续引用；FE Training IC 教材 fe.training，2026）；拥挤用 |ρ| 阈值参考 TDM 引 MOD-PA-004 阈值体系（项目内一致性引用，方向问题见轴 A）。

## 4 缺陷清单

1. **[P1] TDM-F-C3-01 七项声明语义（做T/持仓二分、IS 三分解、D84 五条必改）零代码承载**，图上归因汇聚节点与实际交付（教材 Brinson 骨架）差距巨大。建议修法：节点标注"骨架已建/七项缺口清单挂施工批次"（TDM 注释已有 D84 声明，需升级为显式缺口清单+红标），或收敛节点声明。验证法：§2 轴 D grep。
2. **[P2] 链顶孤儿**（引擎+包装层双孤儿）。建议修法：接报告域消费或声明退役候补（规范预算净零）。验证法：grep。
3. **[P2] 多期朴素算术求和**。建议修法：接 Carino 平滑或几何链接（对齐 TDM-D84 TWR 声明）；短期保留则 docstring 标注适用上限（如 ≤3 期）。验证法：两期复利探针。
4. **[P2] total_return 字段语义误导**。建议修法：改名 net_excess_return 或报告附 benchmark_return 行并文档铁律。验证法：读契约+消费方审计。
5. **[P3] 权重和不校验（B-F 口径前置）/风险结果丢弃/冷启动降级误判/负相关拥挤误判/异常统一降级**。建议修法：各一行级修复（sum 校验、接结果或删调用、baseline=0 单独分支、拥挤改只看正相关、异常分类）。验证法：各自探针。

## 5 挂起疑问

- 拥挤检测 |ρ| 方向语义（对冲策略被归零建议）需 Owner 裁定：若项目定义"策略拥挤"含反向重复暴露则维持，否则改 ρ>threshold 单侧。
- F-C3-01 的五条入边数据（做T 闭环/退出效率/选股漏斗）当前无生产者在线——归因引擎接线应与 P59（F-C3-05）和 P65（P2-03）的接线批次统一排期，避免单点先接。

## 6 完备性自评

六轴全查（A 数学四问：Brinson 恒等式代数验证+守恒/边界=空段/负权重/drag<0 已测、隐含假设=权重和相等已审、A 股口径=复权/做T 缺口已记；B 上游=SegmentReturn/协方差/契约逐参查；C 下游=消费链追到链顶判孤儿；D=与 attribution_calculator（reporting）的 BHB 声明分工+与 MOD-RK-37 双承载检查（判定委托唯一真源声明合格）；E 五问：静默失败=风险轴静默缺、假阳性=is_consistent 恒真、断供=RiskDecomposer 异常降级、重复触发=纯函数幂等、时序=clock 可注入）。长尾：①MOD-RK-16 RiskDecomposer 数学未查；②92 测试逐断言为抽查级；③真实月度归因产物画像无生产数据。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
