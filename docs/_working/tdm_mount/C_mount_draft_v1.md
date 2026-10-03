---
ttl: task_bound
completes_when: 总筹逐行裁决后由总筹写图（本件只出稿禁改 config/trading_decision_map.yaml）
title: "任务C·未挂模块初挂草案 v1（机生）"
owner: st-tdm-mount-flash-20261003
generation: machine_generated
generator: .runtime/tmp/tdm_mount/task_c_mount_draft.py（一次性脚本不入产）
---

# 任务C·未挂模块初挂草案

> 输入=B_coverage_ledger_v1.yaml unmounted_orphan 全集；候选=施工单域→流段规则内按中文名二agram重叠打分取 1-2 候选；零命中行标 needs_chief；证据=翻译册 plain_zh / 蓝图正文原句（未改写）。

## 计数（字段）

- orphan_total: 233
- rows_emitted: 233
- needs_chief: 103
- text_matched: 130
- missing_in_population_index: 0

## needs_chief 行号清单

MOD-BT-018、MOD-BT-019、MOD-BT-020、MOD-BT-021、MOD-BT-022、MOD-BT-023、MOD-BT-024、MOD-BT-026、MOD-EX-002、MOD-EX-003、MOD-EX-049、MOD-EX-050、MOD-EX-055、MOD-EX-056、MOD-EX-057、MOD-EXE-AGENTS、MOD-INF-019、MOD-INF-021、MOD-L02-001、MOD-L02-027、MOD-L04-001、MOD-L11-001、MOD-L13-001、MOD-MKT-001、MOD-MKT-002、MOD-MKT-003、MOD-MKT-004、MOD-MKT-005、MOD-MKT-006、MOD-MKT-007、MOD-PA-002、MOD-PA-004、MOD-PA-006、MOD-PA-013、MOD-PF-001、MOD-PF-002、MOD-PF-003、MOD-PF-006、MOD-PF-008、MOD-PF-014、MOD-PLAN-002、MOD-POS-006、MOD-POS-007、MOD-POS-008、MOD-POS-009、MOD-POS-016、MOD-POS-017、MOD-POS-020、MOD-POS-029、MOD-REGIME-006、MOD-REGIME-011、MOD-RK-011、MOD-RK-043、MOD-RK-044、MOD-RK-05、MOD-RK-06、MOD-RK-07、MOD-RK-08、MOD-RK-10、MOD-RK-12、MOD-RK-13、MOD-RK-14、MOD-RK-15、MOD-RK-16、MOD-RK-18、MOD-RK-19、MOD-RK-20、MOD-RK-23、MOD-RK-26、MOD-RK-33、MOD-RK-34、MOD-RK-35、MOD-RK-36、MOD-RK-37、MOD-RK-38、MOD-RK-39、MOD-RK-40、MOD-SELL-006、MOD-SELL-008、MOD-SELL-009、MOD-SELL-015、MOD-SELL-016、MOD-SIG-144、MOD-SIG-145、MOD-SIG-146、MOD-SIM-002、MOD-SIM-003、MOD-SIM-005、MOD-SIM-012、MOD-SIM-021、MOD-SIM-022、MOD-SIM-023、MOD-SIM-024、MOD-TRADING-002、MOD-TRADING-003、MOD-TRADING-004、MOD-TRADING-011、MOD-TRADING-012、MOD-TRADING-015、MOD-TRIG-001、MOD-XS-008、MOD-XS-017、MOD-XS-019

## 逐模块草案（0 漏行验收=rows_emitted==orphan_total）

| module_id | 域 | depgraph 域 | 首选节点 | 次选 | 规则依据 | 蓝图/翻译册原句摘录 | 备注 |
|---|---|---|---|---|---|---|---|
| MOD-AU-001 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L1-AGG:市场状态判定（分 0.6） | TDM-E-L2-06-1:三级放行门槛（分 0.6） | 规则段 ALL（全图按简介文本匹配） | AutonomyBoundaryGate — 运行时写操作三分类判定门（MOD-AU-001）.设计真源：15号文（15_autonomy_boundary_r |  |
| MOD-AU-002 | _autonomy_core | D_AUTONOMY_CORE | TDM-X-R1-01:熔断分级判定（分 0.9） | TDM-E-L2-05-1:水温档推导（分 0.3） | 规则段 ALL（全图按简介文本匹配） | KillSwitchOrchestrator — Kill Switch 两级编排器（MOD-AU-002）.设计真源：15号文（15_autonomy_bou |  |
| MOD-AU-005 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-FLOW:输出建仓信号（分 0.6） | TDM-E-L0-03:收盘复盘与明日边界（分 0.6） | 规则段 ALL（全图按简介文本匹配） | 给每个 Agent 角色定一个自治级别：L0 只跑死规则、L1 只出建议、L2 要人批了才能动、L3 可以自主执行；同时规定 human_gated 和 imm |  |
| MOD-AU-006 | _autonomy_core | D_AUTONOMY_CORE | TDM-P-P3-02:金字塔加仓规则（分 1.2） | TDM-X-S2-03:执行时段路由（分 1.2） | 规则段 ALL（全图按简介文本匹配） | 每个 Agent 自带的一道门禁：它的 Agent Card 里写着能干哪些动作、不能干哪些动作、一笔单最多下多少钱、什么时段才准动；每次要动作前在内存里对一遍 |  |
| MOD-AU-007 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L4-07:条件触发队列（分 1.5） | TDM-E-L4-12:订单级预检（分 1.5） | 规则段 ALL（全图按简介文本匹配） | 盯着风控引擎状态的角色：实时看限额有没有破、回撤有多深、VaR 超没超；超了就给出降仓或停开的建议并写一条建议审计，真到硬越限且总停开关还没拉时，才通过确定性校 |  |
| MOD-AU-008 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L3-07-2:多因子打分链（分 0.9） | TDM-E-L9-D1:决策假设·因子组合挖掘（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 扮演研究员角色：把一个因子想法（假设）和实验跑出来的指标（IC/夏普/回撤/样本数）放在一起做确定性裁决——回撤或样本不达标直接否，IC和夏普双达标才接受，边缘 |  |
| MOD-AU-009 | _autonomy_core | D_AUTONOMY_CORE | TDM-F-C3-05:可靠度养成与信号健康（分 2.8） | TDM-E-FLOW:输出建仓信号（分 2.2） | 规则段 ALL（全图按简介文本匹配） | 扮演信号分析员角色：汇总信号工厂产出的信号，看两件事——最近IC相比基线衰减了多少、这个信号拥挤不拥挤；衰减或拥挤过了预警线就建议降权入漏斗，过了硬线就建议拦下 |  |
| MOD-AU-010 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L9-V1:状态变量快照·大盘（分 1.8） | TDM-P-P2:做T与加减仓（分 1.2） | 规则段 ALL（全图按简介文本匹配） | 扮演择时分析员角色：把大盘状态（趋势/震荡/波动）、大盘预测分和做T买卖点放在一起裁决——波动市不追单、预测破减仓线拆单减、碰到做T卖点限价减、预测和买点强共振 |  |
| MOD-AU-011 | _autonomy_core | D_AUTONOMY_CORE | TDM-P-P2-02:做T策略调度（分 2.2） | TDM-P-P2:做T与加减仓（分 1.9） | 规则段 ALL（全图按简介文本匹配） | 扮演做T交易员角色：收到做T买卖信号后当场裁决——没信号不做、当天做T次数到顶不做、预期价差太薄不做、卖出时没有T+1可卖底仓直接拒；能做就按可卖量和单笔上限截 |  |
| MOD-AU-012 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L0-03:收盘复盘与明日边界（分 1.3） | TDM-E-L2-05:水温响应（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 计量AI决策占全部决策权重的比例，超过30%硬顶就发出阻断新AI决策的信号，非AI决策永远放行；只发信号不直接下单阻断，审计双记录 |  |
| MOD-AU-013 | _autonomy_core | D_AUTONOMY_CORE | TDM-F-C3-05:可靠度养成与信号健康（分 0.9） | TDM-P-P2-02:做T策略调度（分 0.9） | 规则段 ALL（全图按简介文本匹配） | C-008运维自治判定核心：运维事件按禁区硬编码(交易时段重启核心进程/升级依赖/清理未归档日志必人工)、修复策略分级、TNR可撤销(无快照或不可逆必人工)裁决 |  |
| MOD-AUDITTEST-001 | _simulation | D_AUDITTEST | TDM-E-L2-07:回踩质量分级（分 1.3） | TDM-E-L2-05-2:信号响应三件套（分 1.0） | 规则段 ALL（全图按简介文本匹配） | QualityAssuranceSelfdrive — 质量保障自驱动器（MOD-AUDITTEST-001）。 |  |
| MOD-BT-018 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 策略衰减监控告警器——跟踪策略性能指标(Sharpe/收益/胜率等)随时间的变化, 通过短期vs长期均值对比和线性趋势检测识别策略衰减, 产出4级告警。 | needs_chief |
| MOD-BT-019 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 回测报告生成器——将回测结果(BacktestResult)转换为结构化 HTML 报告。 包含汇总指标表、元数据、过拟合警告、可选的权益曲线 SVG 图和交易 | needs_chief |
| MOD-BT-020 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 回测缓存管理器——对回测结果进行内存缓存与复用, 避免相同参数重复回测。 基于策略ID+参数哈希+日期范围计算缓存键, LRU淘汰策略管理缓存容量, 支持按键/ | needs_chief |
| MOD-BT-021 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 参数优化结果分析器——对多组参数回测结果执行显著性分析和过拟合检测。 识别最优参数组合, 评估各参数对目标函数的敏感度, 检测 IS/OOS 性能差距, 评估优 | needs_chief |
| MOD-BT-022 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 回测数据质量检查器——回测前/后对 OHLCV 数据执行质量检查, 输出结构化质量报告。 覆盖三大维度: 缺失检测(NaN/交易日gaps) + 异常检测(价格 | needs_chief |
| MOD-BT-023 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 回测异常诊断器——对回测结果指标执行异常检测, 输出诊断报告+修复建议。 覆盖性能异常(高Sharpe/高胜率/深回撤)、统计异常(交易不足/周期过短)、 一致 | needs_chief |
| MOD-BT-024 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 回测结果比较器——对两组(或多组)回测结果执行差异分析, 输出结构化比较报告。 覆盖三大维度: 绝对指标比较(年化/总收益/Sharpe/最大回撤/胜率/交易次 | needs_chief |
| MOD-BT-026 | _backtest | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 指标计算NaN处理器——回测指标计算中产生的NaN值进行智能填充与清洗。 提供6种填充策略(ffill/bfill/mean/median/linear/zer | needs_chief |
| MOD-BT-027 | _backtest | D_BACKTEST | TDM-E-L3-12:个股多维验证（分 1.9） | TDM-E-L9-E1:验证·一问一考考试链（分 1.3） | 规则段 ALL（全图按简介文本匹配） | 策略因子信号一提交就自动排队过安检：因子过V1、信号过V2加V5、策略过V3、全链路管线过V4，一层不过就停；再过过拟合门禁，最后把验证报告归档；门禁和引擎都用 |  |
| MOD-BT-028 | _backtest | D_BACKTEST | TDM-E-L3-07-2:多因子打分链（分 2.2） | TDM-P-P2-02:做T策略调度（分 1.9） | 规则段 ALL（全图按简介文本匹配） | 第五层多策略交叉验证的离线回测层：把多个策略在历史样本上的收益矩阵做组合净化交叉验证打分，算出每个策略的样本外稳健名次，再取多个稳健策略共同提名的股票交集，最多 |  |
| MOD-DT-001 | _digital_twin | D_AUDITTEST | TDM-E-L2-01-5:市场级调节注入（分 1.9） | TDM-E-L1-AGG:市场状态判定（分 1.6） | 规则段 ALL（全图按简介文本匹配） | 造一个虚拟市场陪练：一群按规则行动的交易代理互相撮合下单、情绪还会传染，用来事前压测策略，输出全部标注仿真不可实盘。 |  |
| MOD-EX-002 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 持仓跟踪器是"交易系统的账本"——每笔成交（Fill）进来，它就更新对应股票的持仓数量和平均成本， 同时扣减/增加现金。任何时刻都能拍一张"持仓快照"（Posi | needs_chief |
| MOD-EX-003 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 执行审计器是"交易系统的黑匣子记录仪"——每一笔订单从创建、提交、成交、撤销、被拒、过期， 到幂等性拦截，全部记进一条不可篡改的哈希链日志。任何时刻能查某个订单 | needs_chief |
| MOD-EX-049 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 聚合根管理器是"执行域的总调度台"——把订单仓储、成交处理、持仓跟踪三个独立组件拧成一股绳。 上层（Saga编排器/Fill处理器）只需调一个方法，它就自动完成 | needs_chief |
| MOD-EX-050 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 执行域仓储接口是"订单和持仓的保险柜"——定义一套标准接口，让订单（Order）和持仓快照 （PositionSnapshot）的存取方式与具体存储引擎解耦。现 | needs_chief |
| MOD-EX-055 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | <!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_pa | needs_chief |
| MOD-EX-056 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 持仓对账器是"交易系统的对账员"——定期把"系统自己记的持仓"（PositionTracker，靠成交回报一笔笔累计） 和"券商那边查回来的持仓"（miniQM | needs_chief |
| MOD-EX-057 | _execution_core | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | Saga 编排器是"单笔订单的事务经理"——每一笔订单从风控检查到报告生成，走六步标准流程。 任何一步失败，自动执行补偿操作（撤单/回滚），保证系统不会处于"半 | needs_chief |
| MOD-EX-063 | _execution_core | D_AUDITTEST | TDM-E-L4-11:部分成交与撤改处理（分 0.6） | TDM-E-L4-12:订单级预检（分 0.6） | 规则段 E-L4（E-L4执行段） | 每天开盘前先过四道关：限额基线是不是当天的且取值合法、纪律预检有没有违规、行情数据完整性达不达标、各子系统是否就绪；任何一关不过当日就不许开张，探针出问题也按不 |  |
| MOD-EX-064 | _execution_core | D_AUDITTEST | TDM-E-L4-14:执行成本反馈与选型回写（分 2.2） | TDM-E-L4:买卖点与执行（分 1.3） | 规则段 E-L4（E-L4执行段） | 定期复盘成交质量自动调优下单参数：用优化算法搜更好的拆单和等待参数，但风控硬阈值绝不自动改，调参结果必须人工确认才生效。 |  |
| MOD-EXE-AGENTS | _autonomy_core | D_AUTONOMY_CORE | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 执行层四类 Agent 薄入口（Phase 0 手动形态地基）：每张 <200 行纯组装入口，零新业务逻辑，复用既有判定/注册表/实验跟踪件；人手动 CLI 触 | needs_chief |
| MOD-EXSIM-001 | _execution_sim | D_AUDITTEST | TDM-E-L4-09:执行硬约束（分 2.4） | TDM-E-L4-14:执行成本反馈与选型回写（分 2.2） | 规则段 ALL（全图按简介文本匹配） | 估算大单买卖对价格的冲击成本：临时冲击按参与率非线性放大、永久冲击按平方根规律，用分钟成交额校准参数，给执行仿真提供成本真源。 |  |
| MOD-FAC-001 | _factor | D_AUDITTEST | TDM-E-L2-07-1:回踩ABC判定（分 0.3） | TDM-E-L3-07-2:多因子打分链（分 0.3） | 规则段 E-JUDGE（判据层(L2/L3)） | 把价量算子像积木一样批量组合出新特征，先过有效性初筛，最好的TopN送去人工确认才能入库。 |  |
| MOD-FAC-002 | _factor | D_AUDITTEST | TDM-E-L2-08:板块生命周期判定（分 0.3） | TDM-E-L3-02:九阶段选票主链（分 0.3） | 规则段 E-JUDGE（判据层(L2/L3)） | 用数学签名方法把一段价格路径压缩成固定长度的特征向量，保留路径的形状信息，同一段路永远算出同一个向量。 |  |
| MOD-FAC-003 | _factor | D_AUDITTEST | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.0） | 规则段 E-JUDGE（判据层(L2/L3)） | 用遗传规划进化出可读的交易公式：公式树交叉变异、按历史表现淘汰，过三重验证还得人工批准才入库。 |  |
| MOD-FAC-004 | _factor | D_AUDITTEST | TDM-E-L3-07-2:多因子打分链（分 1.9） | TDM-E-L3-12:个股多维验证（分 0.6） | 规则段 E-JUDGE（判据层(L2/L3)） | 让多个AI各自独立提因子方案再投票，过半数才算数，方案不够好就组织辩论，选出的因子还要过样本外验证。 |  |
| MOD-FAC-005 | _factor | D_AUDITTEST | TDM-E-L3-07-2:多因子打分链（分 2.5） | TDM-E-L2-01-1:结构强度评估（分 1.0） | 规则段 E-JUDGE（判据层(L2/L3)） | 双向打分：这个因子对模型贡献多大、这个模型把因子用得多好，产出淘汰名单和迭代方向建议。 |  |
| MOD-FAC-006 | _factor | D_AUDITTEST | TDM-E-L3-03-3:双策略合流体检（分 1.6） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（判据层(L2/L3)） | 让大模型当变异算子做策略进化：保守微调、激进探索、亲本合并三角色配合，小种群盘后运行，过门禁加人工裁决才上线。 |  |
| MOD-FAC-007 | _factor | D_AUDITTEST | TDM-E-L3-03-3:双策略合流体检（分 1.9） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（判据层(L2/L3)） | 看策略的体检报告开药方：哪类因子拖后腿就建议调权重，往哪个方向挖新因子能补短板，建议都登记进假设库。 |  |
| MOD-FACTORY-001 | _autonomy_core | D_AUTONOMY_CORE | TDM-E-L9-AGG:知识供给汇聚（分 1.9） | TDM-X-S1-01:信号收集与六桶分类（分 1.9） | 规则段 ALL（全图按简介文本匹配） | 给新知识贴标签的分拣员。一篇文章进来，它判断这是因子还是策略、属于哪一类、适用于什么行情，贴上规范标签；质量太差直接拒收。它只贴标签不入库，入不入由人说了算。 |  |
| MOD-FACTORY-002 | _autonomy_core | D_AUTONOMY_CORE | TDM-F-FLOW:输出组合信号（分 1.5） | TDM-F-C3-01:多维归因引擎（分 1.3） | 规则段 ALL（全图按简介文本匹配） | 查重裁判员。新点子先跟库里已有的 286 个因子/策略比对：是重复就拦下、是老相识的改款就记为变体、是几个老件的组合就标组合、都不是才准新建。写代码之前先过它， |  |
| MOD-INF-019 | _autonomy_core | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 本蓝图描述 Agent Spec——ZephyrAlpha 的 AI 能力发现与路由系统，采用 L0/L1/L2/L3 四层渐进披露架构。L0 永久加载核心规则 | needs_chief |
| MOD-INF-021 | _autonomy_core | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 本蓝图描述 ZephyrAlpha 回滚/撤销系统——它解决了 AI 自主操作下的安全恢复问题。核心职责包括：git-native+SQLite dump 双轨 | needs_chief |
| MOD-L02-001 | _factor | - | （段内零文本命中） | — | 规则段 E-JUDGE（判据层(L2/L3)） | 本蓝图描述 ZephyrAlpha **因子工厂**——采用 C-027 管理角色（发现/审批/入池/退役）+ C-009 执行角色（盘前全量+盘中增量计算）双 | needs_chief |
| MOD-L02-027 | _factor | - | （段内零文本命中） | — | 规则段 E-JUDGE（判据层(L2/L3)） | 案例库是"因子研究的错题本+答案本"——每次 LLM/人工提出一个因子假设并回测后， 把假设、因子表达式、IC/ICIR/换手率统计量和结论（成功/失败/失败→ | needs_chief |
| MOD-L02-LIFECYCLE | _factor | D_AUDITTEST | TDM-E-L2-08:板块生命周期判定（分 3.9） | TDM-E-L3-07-2:多因子打分链（分 2.5） | 规则段 E-JUDGE（判据层(L2/L3)） | 每周给因子库里一百多个因子按最近表现打分排位：表现好的盖认证章，连续不达标的自动盖退役章退出候选池，之后如果它业绩回升还能自动复活重返池子，全程机器自动不需要人 |  |
| MOD-L04-001 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 本蓝图描述 ZephyrAlpha 风险管理引擎——止损执行+风控校验+Kill Switch 熔断。核心职责：风险限额计算、Pre/Post-trade 风控 | needs_chief |
| MOD-L11-001 | _machine_learning_train | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 本蓝图描述 ZephyrAlpha 机器学习平台核心层——它解决了模型推理标准化和模型注册管理问题。核心职责包括：模型推理(InferenceEngineBas | needs_chief |
| MOD-L13-001 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 本蓝图描述 ZephyrAlpha 实验管理层——它解决了策略和因子验证缺乏标准化管线的问题。核心职责包括：实验管线抽象（ExperimentPipelineB | needs_chief |
| MOD-MKT-001 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 行情数据源注册表——管理所有已注册的 MarketDataVendor 实例。提供注册/注销/ 查询/默认源管理功能, 供 autoload(MOD-MKT-0 | needs_chief |
| MOD-MKT-002 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 行情数据源基类——定义所有行情数据 vendor 的统一抽象接口。提供状态管理 (ACTIVE/INACTIVE/DEGRADED/ERROR)、能力声明(支持 | needs_chief |
| MOD-MKT-003 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 行情数据连接器——MarketDataVendor 抽象基类的连接管理层扩展。在 vendor_base 定义的数据获取接口之上, 增加连接生命周期管理(con | needs_chief |
| MOD-MKT-004 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 故障切换——多数据源主备切换管理。当主数据源(primary vendor)健康检查失败时, 自动切换到备用数据源(secondary), 保障行情数据连续可用 | needs_chief |
| MOD-MKT-005 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 自动加载器——从配置列表自动创建 MarketDataVendor 实例并注册到 VendorRegistry。 通过 vendor_factory 回调解调解 | needs_chief |
| MOD-MKT-006 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | 原始数据缓存——行情数据标准化前的原始数据缓存层。从数据源拉取的原始行情 (FetchResult rows / vendor 原始响应)在标准化为 Norma | needs_chief |
| MOD-MKT-007 | _mkt_data | - | （段内零文本命中） | — | 规则段 E-SENSOR（判据数据输入(sensor)） | - **双 D-DATA-32 撞名裁定**：B10-02234（§30.3.1，竞价时段采集任务+CH 落地+命中率回放） 与 B13-04251（§17.1 | needs_chief |
| MOD-ML-010 | _machine_learning_train | D_AUDITTEST | TDM-E-L3-02:九阶段选票主链（分 1.3） | TDM-E-L1-AGG:市场状态判定（分 0.6） | 规则段 ALL（全图按简介文本匹配） | 第一阶段把所有股票的数据合在一起学一个通用的分位数模型，第二阶段给每只股票单独调一个缩放系数，市场风格切换时几分钟就能重新调好，不用重训整个模型。 |  |
| MOD-ML-011 | _machine_learning_train | D_AUDITTEST | TDM-P-P2-01:做T资格与成本前置（分 1.0） | TDM-E-L9-A09:源线·财经快讯情绪（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 把股票60天的历史数据切成小段，用数学方法提取关键特征，交给下游的密度预测模型用，让预测更准。 |  |
| MOD-ML-012 | _machine_learning_train | D_AUDITTEST | TDM-E-L1-S0-1:新闻情绪语义分析（分 0.6） | TDM-E-L3-12:个股多维验证（分 0.6） | 规则段 ALL（全图按简介文本匹配） | 训练出的每个模型版本在这里登记建档：训练完→验证过→影子跑过→人工批准才能启用，没经过影子验证的版本一律不准上线，旧版本可作废留档 |  |
| MOD-ML-013 | _machine_learning_train | D_AUDITTEST | TDM-E-L2-08:板块生命周期判定（分 1.8） | TDM-E-L4-10:订单生命周期状态机（分 1.2） | 规则段 ALL（全图按简介文本匹配） | 机器学习模型的全生命周期管家：从开发到退役每步状态流转，上生产前必须过对抗鲁棒门禁，灰度发布统一编排。 |  |
| MOD-ML-014 | _machine_learning_train | D_AUDITTEST | TDM-E-L9-D2:决策假设·登记与考试方案（分 1.9） | TDM-E-L3-10:可交易性预检（分 1.3） | 规则段 ALL（全图按简介文本匹配） | 记录每笔交易决策当时怎么想的：标的、时点、理由、情绪都入库，事后回填结果，可导出成训练样本和复盘数据。 |  |
| MOD-ML-015 | _machine_learning_train | D_AUDITTEST | TDM-E-L4-02:买入时序（分 1.3） | TDM-E-L1-AGG:市场状态判定（分 0.3） | 规则段 ALL（全图按简介文本匹配） | 给稀缺的历史行情造合理变体：时间扭曲、幅度缩放、切片混合等五种方法，合成样本必须过分布检验且训练占比不超三成。 |  |
| MOD-ML-016 | _machine_learning_train | D_AUDITTEST | TDM-E-L9-D2:决策假设·登记与考试方案（分 1.9） | TDM-E-L9-D1:决策假设·因子组合挖掘（分 1.3） | 规则段 ALL（全图按简介文本匹配） | 让机器学习老司机的决策：用历史决策日志训练梯度提升树，SHAP解释每个特征贡献，关键节点留人工干预口。 |  |
| MOD-ML-017 | _machine_learning_train | D_AUDITTEST | TDM-E-L0-04:明日情绪盘中滚动预测（分 1.3） | TDM-E-L9-A09:源线·财经快讯情绪（分 1.2） | 规则段 ALL（全图按简介文本匹配） | 用可学习的样条曲线替代固定激活函数做密度预测，参数少还能画出来看，作为QNN第一阶段的替换件。 |  |
| MOD-ML-018 | _machine_learning_train | D_AUDITTEST | TDM-E-L1-AGG:市场状态判定（分 1.2） | TDM-E-L2-01-5:市场级调节注入（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 防止模型学了牛市忘了熊市：重要参数加保护、各市场状态留代表样本回放，微调后旧状态性能掉超5%就回滚。 |  |
| MOD-ML-019 | _machine_learning_train | D_AUDITTEST | TDM-X-S2-04:本地条件单管理（分 1.0） | TDM-E-L1-S1:大盘指数传感器（分 0.6） | 规则段 ALL（全图按简介文本匹配） | 研究数据的版本管家：数据集快照带哈希形成版本链，血缘登记、质量评分、保留策略一条龙。 |  |
| MOD-ML-020 | _machine_learning_train | D_AUDITTEST | TDM-X-S2-04:本地条件单管理（分 1.0） | TDM-P-P1-01:持仓对账与台账快照（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 让每次实验能原样重跑：记录环境快照和全局种子，重跑结果逐项比对哈希，不一致出差异报告。 |  |
| MOD-ML-021 | _machine_learning_train | D_AUDITTEST | TDM-E-L1-S1:大盘指数传感器（分 0.6） | TDM-E-L9-B01:源线·卫星影像（分 0.6） | 规则段 ALL（全图按简介文本匹配） | 给研究划隔离区：独立工作目录，生产数据只读不许写，资源配额有限额，产出要回写必须先评审。 |  |
| MOD-ML-022 | _machine_learning_train | D_AUDITTEST | TDM-E-L9-Z2:治理·净零与资产对账（分 1.3） | TDM-X-R1-03:护盘资产定向加仓白名单（分 1.3） | 规则段 ALL（全图按简介文本匹配） | 因子、模型、策略统一按语义化版本管理：版本记录不可改，能按资产、版本、指标三个维度检索复用。 |  |
| MOD-PA-002 | _portfolio_alloc | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 信号合成器——多策略信号→加权投票→输出合成信号给 PF-CORE。多策略产出的 StrategySignal 列表(每策略每标的一条)→ 每标的一条 Synt | needs_chief |
| MOD-PA-004 | _portfolio_alloc | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | G12 策略相关性门禁——在策略上线/资金分配前, 检查策略两两之间的相关性、因子重叠、 股票池重叠、行业集中度、尾部相关性, 超阈值产出 PA-E03 Cor | needs_chief |
| MOD-PA-006 | _pf_alloc | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | <!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_pa | needs_chief |
| MOD-PA-013 | _portfolio_alloc | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | PA-13（A1 交易决策架构 §30.1.4）。回撤约束资金分配=机构风险预算标准实践。 场内现状：回撤跟踪/控制已有（MOD-RK-011 drawdown | needs_chief |
| MOD-PA-014 | _portfolio_alloc | D_AUDITTEST | TDM-F-C3-04:参数校准闭环（分 0.9） | TDM-F-C1:预算切分（分 0.3） | 规则段 F-FLOW（F流(C1-C3)） | 给候选策略打分入库：赚钱能力稳不稳、参数是不是过度拟合、和现有策略重不重复，三维加权评分够了才准入。 |  |
| MOD-PA-015 | _portfolio_alloc | D_AUDITTEST | TDM-F-C3-03:sleeve权重调权（分 1.9） | TDM-F-C3-05:可靠度养成与信号健康（分 1.9） | 规则段 F-FLOW（F流(C1-C3)） | 不同市场环境下信号准头不同：按当前市场体制查各信号过去250天的命中率，用贝叶斯方法分配权重，切换时平滑过渡。 |  |
| MOD-PF-001 | _portfolio_core | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 策略引擎——管理策略生命周期 + 产出目标权重,供 PC-02 组合优化器消费: - 生命周期状态机: registered → testing → activ | needs_chief |
| MOD-PF-002 | _portfolio_core | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 组合优化器——消费策略权重+约束, 产出 TargetPortfolio(CTR-007): - 主方法: 风险预算 (复用 MOD-RK-08 RiskBud | needs_chief |
| MOD-PF-003 | _portfolio_core | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 再平衡调度器——决定是否触发 PC-02 组合优化器重跑: - 四触发源: 漂移阈值 ±2%/±3% + 周五日历 + 事件驱动 + 风控 E-RK-01/03 | needs_chief |
| MOD-PF-006 | _portfolio_core | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 约束求解器——将风险限额(CTR-003)和拥挤检测结果转化为可执行权重约束,供 PC-02 组合优化器消费: - 7 约束链: 行业绝对≤30% / 行业相对 | needs_chief |
| MOD-PF-008 | _portfolio_core | - | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | Champion-Challenger 序贯晋升统计组件（BM-MT-02 通道的统计内核）——新模型不直接全量上线， 逐笔累加 challenger−cham | needs_chief |
| MOD-PF-009 | _portfolio_core | D_AUDITTEST | TDM-F-C3-04:参数校准闭环（分 0.6） | — | 规则段 F-FLOW（F流(C1-C3)） | 新策略从四个渠道（遗传规划/符号回归/大模型/因子挖掘）进来后走十道工序：先过回测三重门禁，再查过拟合，最后必须人工点头才给候选名分，全程没有自动上线的路子 |  |
| MOD-PF-010 | _portfolio_core | D_AUDITTEST | TDM-F-C2:组合聚合（分 2.2） | TDM-F-C2-02:组合约束栈（分 1.9） | 规则段 F-FLOW（F流(C1-C3)） | 从三十只候选里挑最终十只：太拥挤的降分、走势太像的去掉、同一行业同一市值档不能堆太多、组合波动和回撤不能超预算、风格不能偏太多，大盘合力偏空时整体仓位砍半 |  |
| MOD-PF-011 | _portfolio_core | D_AUDITTEST | TDM-F-C2:组合聚合（分 0.6） | TDM-F-C2-02:组合约束栈（分 0.6） | 规则段 F-FLOW（F流(C1-C3)） | 盯住组合比基准多配了哪些行业哪些风格：偏离超线就告警，再结合各行业动量排名给出增配维持减配建议，只出主意不直接下单 |  |
| MOD-PF-012 | _portfolio_core | D_AUDITTEST | TDM-F-C2-03:相关性聚类与cluster上限（分 0.3） | — | 规则段 F-FLOW（F流(C1-C3)） | 算算这个策略最多能管多少钱：按市场成交额的可参与比例和冲击成本容忍度推出规模上限，用到八成亮黄灯、超了亮红灯，并给出扩池子降换手等扩容建议 |  |
| MOD-PF-013 | _portfolio_core | D_AUDITTEST | TDM-F-C2-02:组合约束栈（分 2.2） | TDM-F-C2:组合聚合（分 1.9） | 规则段 F-FLOW（F流(C1-C3)） | 强化学习三件套：调组合、优执行、做T，全部在风险预算硬上限内微调，先过回测门禁才准用，只做离线评估。 |  |
| MOD-PF-014 | _portfolio_core | D_AUDITTEST | （段内零文本命中） | — | 规则段 F-FLOW（F流(C1-C3)） | 调仓花了多少钱拆明白：佣金印花税是显性成本，冲击价差是隐性成本，再加上税收和错过行情的机会成本，四笔账一目了然。 | needs_chief |
| MOD-PLAN-002 | _plan_engine | - | （段内零文本命中） | — | 规则段 E-L0（盘前预案(L0)） | <!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_pa | needs_chief |
| MOD-PLAN-004 | _plan_engine | D_AUDITTEST | TDM-E-L0-03:收盘复盘与明日边界（分 0.9） | TDM-E-L0:盘前作战计划（分 0.3） | 规则段 E-L0（盘前预案(L0)） | OvernightBoundaryReviser — 盘前隔夜边界修正器 (MOD-PLAN-004) 44号 §4 M3 盘前综合预判的"今晨修正"计算核心。 |  |
| MOD-PLAN-005 | _plan_engine | D_AUDITTEST | TDM-E-L0:盘前作战计划（分 0.9） | TDM-E-L0-03:收盘复盘与明日边界（分 0.6） | 规则段 E-L0（盘前预案(L0)） | ScenarioPlanner — 盘前多情景方案+竞价三细节 (MOD-PLAN-005) 44号 §4 M3-③ 落码：盘前"多情景方案整机"。 |  |
| MOD-PLAN-006 | _plan_engine | D_PLAN | TDM-E-L0-02:偏离监控与修订（分 0.9） | TDM-E-L0-03:收盘复盘与明日边界（分 0.6） | 规则段 E-L0（盘前预案(L0)） | BoundaryRevisionEngine — 盘中次日预案边界修正引擎 (MOD-PLAN-006) 44号 §3 M2 落码：盘中实时输入→当晚边界档位的 |  |
| MOD-PLAN-007 | _plan_engine | D_PLAN | TDM-E-L0-03:收盘复盘与明日边界（分 1.2） | TDM-E-L0:盘前作战计划（分 0.9） | 规则段 E-L0（盘前预案(L0)） | LlmPremarketAnalysis — LLM 盘前综合复盘与当日情景分析核心件 (MOD-PLAN-007) 44号备忘 §9.14 M3-⑨ 落码（9 |  |
| MOD-PLAN-019 | _plan_engine | D_PLAN | TDM-E-L0:盘前作战计划（分 1.5） | TDM-E-L0-03:收盘复盘与明日边界（分 1.2） | 规则段 E-L0（盘前预案(L0)） | 把九种开盘情景各配一套对策模板：能不能加仓、加多少、什么时候减仓、风控升几级。盘中根据市场状态和事件自动找出对得上的模板，人工确认后才算数，事后统计每套预案的命 |  |
| MOD-PLAN-020 | _plan_engine | D_PLAN | TDM-E-L0:盘前作战计划（分 0.3） | TDM-E-L0-01:计划生成（分 0.3） | 规则段 E-L0（盘前预案(L0)） | 把四路指令揉成统一口径：应急保命指令最大，人工指令其次，两路自动信号最后；两路自动同向算强共振取保守仓位，反向打架就不出指令升级人工审查，AI发现的信号一律要人 |  |
| MOD-PLAN-021 | _plan_engine | D_PLAN | TDM-E-L0:盘前作战计划（分 2.2） | TDM-E-L0-03:收盘复盘与明日边界（分 0.9） | 规则段 E-L0（盘前预案(L0)） | 把开盘前75分钟的准备工作排成标准工序表：8点先同步数据过质量门，8点半做隔夜复盘和情景预案，9点跑盘前检查，9点10分人工确认就绪。哪道工序失败就亮红灯指出来 |  |
| MOD-PLAN-023 | _plan_engine | D_AUDITTEST | TDM-E-L0:盘前作战计划（分 1.6） | TDM-E-L0-04:明日情绪盘中滚动预测（分 1.2） | 规则段 E-L0（盘前预案(L0)） | 把每天开盘前的准备工序编成流水线：数据同步、复盘、情绪扫描、预案、检查、就绪确认，哪步失败就停下，关键节点可人工接管。 |  |
| MOD-POS-006 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 资金管理器——管理资金流水与结算状态, 在 A 股 T+1 结算约束下计算可用资金头寸, 维护最低储备金/机会储备/节假日储备, 产出现金约束反馈 POS-01 | needs_chief |
| MOD-POS-007 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 资金曲线管理器——跟踪已实现盈亏驱动的净值曲线, 根据回撤分级动态调整仓位上限, 并在盈利期扩张、亏损期收缩资金基础。产出 E-POS-04 CapitalCu | needs_chief |
| MOD-POS-008 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 回撤控制器——消费组合回撤+系统性风险分级(VaR/CVaR)+黑天鹅模式信号，产出分级响应指令 (减仓/清仓/暂停新开/Kill Switch)，是仓位防守的 | needs_chief |
| MOD-POS-009 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 仓位审计记录器——D_POSITION 域的**审计基础设施**，监听仓位变更事件 (E-POS-01/02/03/05)，全量记录每笔仓位变更，通过哈希链保证 | needs_chief |
| MOD-POS-016 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 卖出-仓位双向链接——在卖出决策域与仓位管理域之间建立双向反馈通道: 正向根据仓位盈亏状态动态调整卖出阈值(盈利放宽/亏损收紧), 反向执行买入后即时验证(5m | needs_chief |
| MOD-POS-017 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | A股风险日历仓位约束——根据当前日期和A股风险日历事件, 生成临时仓位上限调整和否决指令。 覆盖期权交割日/年报截止/股东空窗期/财报发布等7类日历事件, W- | needs_chief |
| MOD-POS-020 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | 独立策略账本——A 模型（[30_multi_strategy_concurrency](../../../_working/archive/2026-09/d | needs_chief |
| MOD-POS-025 | _position | D_AUDITTEST | TDM-P-P1-05:组合级持仓体检（分 0.6） | TDM-P-P2:做T与加减仓（分 0.6） | 规则段 P-FLOW（P流(P1-P3)） | CFA推荐的核心-卫星组合结构：核心仓用Kelly长期持有不动，卫星仓最多占30%用来做T和换仓增强收益，卫星跌出前30%排名就触发换仓。 |  |
| MOD-POS-029 | _position | - | （段内零文本命中） | — | 规则段 P-FLOW（P流(P1-P3)） | F-06 组合层穷尽网格的**编译器雏形**——把「维度 schema + 求值上下文」确定性编译为 `PositionRecipe` 候选全集。对应全链路方案 | needs_chief |
| MOD-REGIME-006 | _regime | - | （段内零文本命中） | — | 规则段 L1（总闸层） | regime 层节流目前只看价格与波动状态（MOD-REGIME-001/002），无时间维度前瞻—— 变盘窗口盲视。A 股存在可统计实证的日历结构（月末/节后 | needs_chief |
| MOD-REGIME-007 | _regime | D_AUDITTEST | TDM-E-L1-S2:市场内部结构传感器（分 1.3） | — | 规则段 L1（总闸层） | 横截面结构特征（MOD-REGIME-007，ALG-01）——regime 特征集的横截面维度补强。 |  |
| MOD-REGIME-011 | _regime | - | （段内零文本命中） | — | 规则段 L1（总闸层） | A1 交易决策架构 §3 模块2。场内现状（TSV 对账）：HMM 体制识别已有 （MOD-REGIME-001 production），**GARCH(1,1 | needs_chief |
| MOD-REGIME-013 | _regime | D_REGIME | TDM-E-L1-S4:波动率传感器（分 2.9） | TDM-E-L1-S1:大盘指数传感器（分 0.6） | 规则段 L1（总闸层） | 专门抓'憋久了要爆'的行情：短长期波动比小于0.5且布林带宽处于历史最窄10%才算真压缩，然后用量价位置估突破方向概率，最后等波动放大、放量、同向连续3天才确认 |  |
| MOD-REGIME-014 | _regime | D_AUDITTEST | TDM-E-L1-AGG:市场状态判定（分 1.9） | TDM-E-L1-S2:市场内部结构传感器（分 1.3） | 规则段 L1（总闸层） | 识别市场现在偏爱哪种风格：大盘还是小盘、价值还是成长，用隐马尔可夫模型或规则分档判定，风格切换要连续多期确认防抖动。 |  |
| MOD-RK-011 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 回撤实时追踪器——盘中实时跟踪组合净值的最大回撤(峰值/谷值), 三级阈值告警, 回撤恢复检测, 资金曲线诊断。产出 E-RK-03 DrawdownAlert | needs_chief |
| MOD-RK-042 | _risk | D_RISK | TDM-E-L1:大盘总闸（分 0.3） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 敞口太大时生成对冲腿单：按股指期货或ETF算出该买空多少，必须风控和人工双确认才执行，事后回写对冲有没有效。 |  |
| MOD-RK-043 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 算VaR前先把数据批量读进内存：DuckDB扫Parquet预取收益率序列，环形缓冲控制内存，统计命中率和IO耗时。 | needs_chief |
| MOD-RK-044 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 风控规则落库管版本：每次修改版本加一旧版不改，激活版本原子切换，和内存里的风控限幅双向对账防漂移。 | needs_chief |
| MOD-RK-045 | _risk | D_RISK | TDM-E-L3-12-2:龙虎榜席位追踪（分 0.3） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 给VaR历史模拟拼SQL：窗口、标的、频段参数化生成，过滤条件下推提速，同持仓同窗口的结果走缓存防重复计算。 |  |
| MOD-RK-046 | _risk | D_RISK | TDM-F-C1:预算切分（分 0.3） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 模拟风险怎么传染：用相关性和产业链关系建网，一个板块出事沿边衰减传播，算出每个节点的传染评分供风控参考。 |  |
| MOD-RK-048 | _risk | D_RISK | TDM-E-L1-AGG:市场状态判定（分 0.3） | TDM-E-L3-05:顺位排序（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 计算Amihud非流动性指标和成交量萎缩比率，判断市场流动性是否恶化 |  |
| MOD-RK-05 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | VaR 风险价值计算器——Phase 1 实现参数法(方差-协方差)+历史模拟法并发计算, 取 max 作为保守估计。 供 RK-03 实时监控使用, 是组合潜 | needs_chief |
| MOD-RK-06 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 告警生成器——消费风控编排器产出的 `RiskReport`，将原始违规项按严重程度分为三级 （黄/橙/红），按级别路由到不同通道（日志/邮件/微信），并对同源 | needs_chief |
| MOD-RK-07 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 集中度风险监控器——计算持仓集中度三大指标(HHI/个股/行业), 三级告警, 供 RK-02 Pre-Trade Hard Block + RK-03 实时监 | needs_chief |
| MOD-RK-08 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 风险预算分配器——基于风险贡献(复用 RK-16)实现组合层风险预算分配: - 等风险贡献 (ERC / Risk Parity): 每资产贡献等量风险 pct | needs_chief |
| MOD-RK-10 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | A股系统性风险检测器——扫描5大系统性风险信号, 按触发信号数判定三级警报, LEVEL_3 时联动 RK-17 Kill Switch 执行清仓: - 5大信 | needs_chief |
| MOD-RK-12 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 压力测试引擎——D-RISK 分析引擎核心模块。评估组合在极端情景下的潜在损失: - 历史情景 (HISTORICAL): 2008 金融危机 / 2015 股 | needs_chief |
| MOD-RK-13 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 检测多个策略是否挤在同一个因子或同一批股票上，计算持仓重叠度和方向一致性 | needs_chief |
| MOD-RK-14 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | AI/Agent 行为越界监控器——检测交易 Agent 的 ASI/AST/MCP 隐性串谋和自治边界违反。 | needs_chief |
| MOD-RK-15 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 尾部风险监控器——D-RISK L2 实时监控核心模块。度量与监控极端损失风险: - 期望短缺 (Expected Shortfall / CVaR): 尾部条 | needs_chief |
| MOD-RK-16 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 风险分解引擎——将组合风险分解为可归因的成分, 供 RK-08 风险预算分配(复用 CCR)与 RK-20 日终归因报告使用: - 因子风险 (Factor R | needs_chief |
| MOD-RK-18 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 模型风险审计器——交易预测模型的漂移/衰退/偏差综合审计。 | needs_chief |
| MOD-RK-19 | _risk | D_RISK | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 操作风险审计阈值解释层——在 MOD-EX-003 `compute_operational_risk_stats()`产出的纯统计数据之上构建薄解释层，将统计 | needs_chief |
| MOD-RK-20 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 日终审计器——D-RISK 三层防线第三层 (L3 Post-Trade 盘后审计) 的核心模块。每个交易日收盘后执行: - 日终 PnL 对账 (预期 vs  | needs_chief |
| MOD-RK-21 | _risk | D_RISK | TDM-E-L1:大盘总闸（分 0.6） | TDM-C-L1:币圈大盘总闸（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 盘中实时监控单只股票是不是陷入流动性危机：看盘口卖方挂单占比和买卖价差有没有同时爆掉，涨跌停时按跌停等于卖不出特殊处理；真出危机先停新开仓，危机消了按比触发线更 |  |
| MOD-RK-23 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | D_RISK 域监控导向设施（drawdown_tracker 同族）——每日收盘后持续度量**实盘净值 vs 同期回测净值**的偏离度。 | needs_chief |
| MOD-RK-26 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | FHS（Filtered Historical Simulation）——GARCH(1,1) 拟合收益序列 → 标准化残差 → 有放回重采样 → 逐日递归乘条 | needs_chief |
| MOD-RK-28 | _risk | D_RISK | TDM-E-L0:盘前作战计划（分 0.6） | TDM-E-L1:大盘总闸（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 盘前先把明天的风险算清楚：用条件概率分布估出前瞻VaR/CVaR，再裹一层有数学覆盖率保证的共形安全垫，对照限额给出收紧倍数和是否坐出观望的建议，供三层风控盘前 |  |
| MOD-RK-29 | _risk | D_RISK | TDM-E-L0:盘前作战计划（分 0.3） | TDM-E-L1:大盘总闸（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 盘中盯住两件事：手里股票有多少变成卖不动的（非流动占比越线就发黄牌红牌），以及持仓之间是不是涨跌停一起动（相关性体制进入高位说明分散失效发橙牌），汇总成风险仪表 |  |
| MOD-RK-30 | _risk | D_RISK | TDM-E-L1-AGG:市场状态判定（分 1.5） | TDM-E-L0:盘前作战计划（分 0.6） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 把盘前预判和盘中监控拧成一股绳：盘前按市场状态收紧或放开限额并决定是否坐出，盘中按监控红黄橙牌分级降仓或禁开仓，黑天鹅来了只发Kill Switch建议交存量熔 |  |
| MOD-RK-31 | _risk | D_RISK | TDM-E-L0:盘前作战计划（分 0.3） | TDM-E-L1-AGG:市场状态判定（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 事前嗅出黑天鹅：把当下市场的波动、回撤、相关性、流动性、跳空、跌停潮、外围跌幅七项体征，跟七种历史危机模式的模板逐一比对相似度，像了就提前降仓；同时像两种以上或 |  |
| MOD-RK-32 | _risk | D_RISK | TDM-E-L1-AGG:市场状态判定（分 0.6） | TDM-F-C1:预算切分（分 0.3） | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 不光量拥挤还管动手：策略盈亏形态两两比DTW，长得太像或拥挤分超线就自动降杠杆降仓并给漏斗降权；一旦拥挤叠加回撤还在恶化，判定正反馈踩踏直接熔断式退出，保住本金 |  |
| MOD-RK-33 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 多标的联合分布 F=C(F₁..F_N)：边缘分布（GARCH 波动过滤 / 条件密度预测注入）+ Gaussian Copula（DCC 动态相关）捕捉**联 | needs_chief |
| MOD-RK-34 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | VaR/CVaR 分级预警（Basel III 逆周期缓冲思想）落码：把组合 VaR95/CVaR、单日亏损、 连续两日亏损统一映射为绿/黄/橙/红/黑 5 级 | needs_chief |
| MOD-RK-35 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | Wilder(1978) ATR 止损经典落码：止损间距以波动率自适应单位 k×ATR14 参数化 （替代固定百分比），体制自适应 k（趋势 3~4 / 均值回 | needs_chief |
| MOD-RK-36 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | kill switch 本体（MOD-INF-016）已建，缺口是**紧急操作的二次确认与不可篡改留痕**： 紧急停止（EMERGENCY_STOP）与强制平仓 | needs_chief |
| MOD-RK-37 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 绩效监控不只看盈亏：统一绩效归因（Brinson 配置/选择/交互 + 因子/风险归因）+ 策略退化检测闭环。归因与 IC 衰减计算分散三处（MOD-L07-0 | needs_chief |
| MOD-RK-38 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 候选 spec：输入持仓+风格/行业因子载荷，输出组合因子敞口矩阵+敞口超限预警 （业界对标 Barra USE3/CNE5、riskfolio-lib）。场内 | needs_chief |
| MOD-RK-39 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 候选 spec：庄股操纵**回避**检测——对倒放量/尾盘异动/价量背离/换手异常/筹码高度 集中五类统计特征 → 操纵风险评分 → 回避名单输出（风控禁开仓  | needs_chief |
| MOD-RK-40 | _risk | - | （段内零文本命中） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 候选 spec：买入后 T+5min（跌破买价>1% 且放量→观察标记）/ T+15min（跌破分时均线 反弹无力→减仓 50%）/ T+30min（反向>2A | needs_chief |
| MOD-RK-41 | _risk | D_RISK | TDM-E-L3-05:顺位排序（分 1.0） | — | 规则段 RISK-GATE（闸/风控环节(gate型+风控语义节点)） | 给风控事件和新信号排队定先后：风控否决/降级事件必须先于信号生效，信号撞上活跃阻断就压住不放行；如果发现信号先生效、更早发生的风控事件却后到，立刻撤销该信号并记 |  |
| MOD-SELL-006 | _sell_decision | - | （段内零文本命中） | — | 规则段 X-FLOW（X流离场(S1/S2/X1)） | 置换与再平衡卖出器——两种被动卖出驱动: ① 机会成本驱动(候选池有更优标的→卖A买B) ② 组合再平衡驱动(权重偏离>阈值→被动卖出超配)。产出 Replac | needs_chief |
| MOD-SELL-008 | _sell_decision | - | （段内零文本命中） | — | 规则段 X-FLOW（X流离场(S1/S2/X1)） | 买卖冲突仲裁器——同标的同时存在买入信号与卖出信号时, 按"卖出优先(保守原则)"仲裁, 并对冲突分级(强冲突立即执行 / 弱冲突延迟观察), 产出可审计的仲裁 | needs_chief |
| MOD-SELL-009 | _sell_decision | - | （段内零文本命中） | — | 规则段 X-FLOW（X流离场(S1/S2/X1)） | 卖出紧迫度评分器——基于卖出信号来源类型映射紧迫度(0~1), 并匹配执行策略(市价单/限价单+时间限制/限价单+耐心), 消费 SELL-08 仲裁结果增强( | needs_chief |
| MOD-SELL-015 | _sell_decision | - | （段内零文本命中） | — | 规则段 X-FLOW（X流离场(S1/S2/X1)） | 止损猎杀防护器——防护做市商/HFT 主动猎杀止损位: ① 止损位偏移(不精确设在技术位, 偏移1-2%) ② 软止损模式(触及→OBSERVING观察期→确认 | needs_chief |
| MOD-SELL-016 | _sell_decision | - | （段内零文本命中） | — | 规则段 X-FLOW（X流离场(S1/S2/X1)） | G45-1 治缺口件——09_f45 案卷实证 S1 全族纯库挂机（`from zephyr.sell_decision` 包外零消费者， 离场实际靠人）。本模 | needs_chief |
| MOD-SIG-058 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-1:结构强度评估（分 0.3） | TDM-E-L3-11:日内动态选股（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | MOD-SIG-058 — 期指基差情绪监测器（44号备忘录 §9.8 通道2，M1-⑧/M3-⑥）第一性原理：期货=机构带杠杆的实时投票机，价格发现领先现货（ |  |
| MOD-SIG-059 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-05-2:信号响应三件套（分 0.9） | TDM-E-L2-01:板块强度综合（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | MOD-SIG-059 — 期权情绪三件套（44号备忘录 §9.9，M1-⑨，华泰 2026-03 机构范式）A 股单边做多市场衍生品"少而精"只取 PCR+I |  |
| MOD-SIG-061 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-04:板块级市场状态（分 1.9） | TDM-E-L2-01:板块强度综合（分 1.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | MOD-SIG-061 — 主线候选榜（92号清单 §7.8，架构审查报告 §11.5 SEC-05，22号 spec 消费层）。 |  |
| MOD-SIG-063 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-5:市场级调节注入（分 1.9） | TDM-E-L2-04:板块级市场状态（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 从ClickHouse读取市场宽度分钟快照，30时点重采样后输出给相似日推演模块使用 |  |
| MOD-SIG-087 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-07-2:多因子打分链（分 1.9） | TDM-E-L2-05:水温响应（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 信号域想吃因子域算好的因子结果，不自己去翻因子仓库，而是经过这座桥：桥先看结果的契约版本对不对（完全匹配就放行，同大版本就兼容透传，不认识就拒收并标降级），再把 |  |
| MOD-SIG-088 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-09-1:事件图谱传导（分 1.9） | TDM-E-L2-09:催化剂识别（分 1.5） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 风险域一出事（比如VaR突破）会往消息流里扔事件，这个处理器就是信号域派去收件的：按消费组拉事件，凭幂等键认出重复件直接跳过，处理不了的扔进死信队列兜底，该给信 |  |
| MOD-SIG-091 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-4:形态结构识别（分 1.9） | TDM-E-L2-04-2:虹吸态识别（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 把双顶双底、平台突破、趋势线、支撑压力、缠论笔中枢这些各管一摊的看图手艺收进一个引擎：喂进去K线高低收，统一吐出图形事件——什么形态、朝哪个方向、把握多大、关键 |  |
| MOD-SIG-092 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-2:龙虎榜席位追踪（分 0.6） | TDM-E-L2-04:板块级市场状态（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 开盘跳空缺口有多大概率被补回来：把缺口按波动率分成小中大四档，查历史统计表给出回补概率、分批回补比例和止损参考价，供买入侧判断追高或抄缺口的风险 |  |
| MOD-SIG-094 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-05-2:信号响应三件套（分 2.2） | TDM-E-L2-01-4:板块资金流聚合（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 识别主力吸筹尾声的买点：吸筹阶段评分冲过门槛且买卖量差同步走高才发信号，并用因果检验确认是资金推动在先而不是价格自嗨，防止把因果搞反 |  |
| MOD-SIG-095 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-03-1:扩散指标进度追踪（分 1.3） | TDM-E-L2-08:板块生命周期判定（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 发现价格和指标唱反调的时刻：价格创新高但RSI或MACD或量能反而走弱就是顶背离，反过来是底背离，还能算背离几次后反转概率多大、多个周期共振时概率多高 |  |
| MOD-SIG-096 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12:个股多维验证（分 1.9） | TDM-E-L2-06-3:强度加权传导（分 1.5） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 筛出比大盘强的股票：看个股中期跑赢基准多少、均线是不是多头排列、离52周新高近不近、创新高时有没有放量，四项加权成一个0到100的强弱分并排名次 |  |
| MOD-SIG-097 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-07-2:多因子打分链（分 1.3） | TDM-E-L2-01-1:结构强度评估（分 1.2） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 看涨停板这锅水的生态结构：今天最高几连板、每个高度层有几只票、中间哪层断了档、大家封板封得早不早、昨天N板的票今天有几成晋级成功；另外用统计检验判断一只股票是不 |  |
| MOD-SIG-099 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-1:结构强度评估（分 0.6） | TDM-E-L2-03:调整周期进度（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 专门抓'恐慌到极点要反转'的时刻：情绪分数跌到历史最低两成多、大盘RSI也跌破30，两个冰点前后脚出现才算数；再用一张打分卡量当天有多恐慌（跌得多狠、量放得多异 |  |
| MOD-SIG-100 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-4:板块资金流聚合（分 0.9） | TDM-E-L2-02-2:单板块轮动预警（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给买入侧把关'这个突破是不是真的'：收盘站上过压力位且放量才算确认突破；突破后3天内跌回去就是假突破，跌回越快越可疑；再算一笔诱多账——缩量突破、量价背离（价格 |  |
| MOD-SIG-101 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-1:结构强度评估（分 0.6） | TDM-E-L2-01-3:多周期动量加权（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 量一量'情绪跑赢了价格还是跑输了价格'：把市场情绪指数和价格各自换算成相对自己近期水平的标准化分，再看最近几天两者的变化幅度差——情绪明显比价格涨得快是正向背离 |  |
| MOD-SIG-102 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-07-2:多因子打分链（分 3.8） | TDM-E-L2-06-3:强度加权传导（分 2.2） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给打板候选票算一个0到100的潜力分。它把连板高度、封单强度、板块动量、筹码集中度、龙虎榜、量能配合、市场情绪这七个分项先做过往预测力验证（IC和ICIR门槛） |  |
| MOD-SIG-103 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-4:形态结构识别（分 1.5） | TDM-E-L3-12:个股多维验证（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 判断股票是不是跌到底部区域、能不能右侧进场。它从价格超卖、量能萎缩后放量反弹、主力资金净流入、情绪极度低迷、Wyckoff弹簧这五个维度逐一点名，至少三个维度确 |  |
| MOD-SIG-104 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-06-1:三级放行门槛（分 1.6） | TDM-E-L2-05-2:信号响应三件套（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给每个交易动作先过一道概率门。新开仓要次日上涨概率到六成五、加仓六成、抄底七成、正T五成五、反T看下跌概率到五成五；碰到牛市、熊市、放量、缩量、利好落地前、黑天 |  |
| MOD-SIG-105 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.0） | TDM-E-L3-07:策略专属链（分 1.0） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 买卖点模式特征向量库，DTW历史案例匹配，胜率>50%且IC>0.03双门控决定模式是否启用 |  |
| MOD-SIG-106 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-4:板块资金流聚合（分 0.6） | TDM-E-L2-05-2:信号响应三件套（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 事件5类可预测性分类，价格/时间/资金/情绪4维透支度量化，落地前减仓信号 |  |
| MOD-SIG-107 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-05-2:信号响应三件套（分 0.3） | TDM-E-L2-06-1:三级放行门槛（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | E[次日收益]=P涨×E涨−P跌×E跌，E>0.5%门槛+盈亏比>1.5+成本优势>2ATR |  |
| MOD-SIG-108 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-07-2:多因子打分链（分 3.2） | TDM-E-L2-05-2:信号响应三件套（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 6源择时信号IC加权或BMA叠加，≥3同向共振高置信标记 |  |
| MOD-SIG-109 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 策略A/B/C三席YES/NO投票+C-034/C-036额外投票方+市场状态否决门 |  |
| MOD-SIG-110 | _fundamental_signal | D_AUDITTEST | TDM-E-L2-09-1:事件图谱传导（分 1.9） | TDM-E-L2-02-2:单板块轮动预警（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 财报公布后股价常常不会一步到位，而是沿着超预期方向慢慢漂移一两三个月。这个模块先把实际盈利和市场一致预期的偏离算成一个标准化意外值并分五档，再统计公告后二十个交 |  |
| MOD-SIG-111 | _fundamental_signal | D_AUDITTEST | TDM-E-L2-05-2:信号响应三件套（分 1.9） | TDM-E-L2-02:轮动序列追踪（分 1.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 一笔交易信号是从哪个因子批次、哪批原始行情算出来的，最后又下了哪笔订单，这个模块用一张轻量数据库表把整条链路的追踪编号串起来存好，支持按信号编号反向查出完整来龙 |  |
| MOD-SIG-112 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-09-1:事件图谱传导（分 2.8） | TDM-E-L2-09-2:冲击标的生成（分 1.2） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给事件标类型、接传导边：一个政策或公告出来后，按产业链上下游、同业、供应链三条路径推算影响会传到哪、强度还剩多少，可用反事实方法验证推理靠不靠谱。 |  |
| MOD-SIG-113 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-04-2:虹吸态识别（分 1.3） | TDM-E-L2-06-2:龙头识别定位（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 识别庄家操纵的六个阶段：建仓、洗盘、拉升、出货、对倒、护盘，用价量规则判定当前处于哪阶段，反庄策略只在沙盒里模拟，输出风险提示不直接下单。 |  |
| MOD-SIG-114 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-05-2:信号响应三件套（分 0.6） | TDM-E-L2-01-2:动量活跃度排名（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 模拟北向、公募、游资、散户四类玩家的行为规律，推演他们合力往哪走、分歧有多大，盘后运行结果只作参考信号。 |  |
| MOD-SIG-115 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-4:形态结构识别（分 2.2） | TDM-E-L2-05-2:信号响应三件套（分 1.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 把图形识别结果翻译成交易语言：这个形态该看多还是看空、信心多大、止损放哪，最后按标准信号格式输出给下游。 |  |
| MOD-SIG-116 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-07:回踩质量分级（分 0.6） | TDM-E-L2-01-1:结构强度评估（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 威科夫方法量化：上涨后缩量回踩不破前低是强势确认，结合38.2%和61.8%两个关键回调位的历史概率，判断趋势会延续还是反转。 |  |
| MOD-SIG-117 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-09-1:事件图谱传导（分 1.9） | TDM-E-L2-06:板块个股传导（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 隔夜美股等外盘涨跌对A股的影响量化：算传导系数、验证开盘后30分钟影响是否消退、按事件类型统计影响持续几天。 |  |
| MOD-SIG-119 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-02-2:单板块轮动预警（分 3.1） | TDM-E-L2-08:板块生命周期判定（分 2.5） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 量板块是不是太挤了：换手率、融资占比、持仓相关性都超过历史九成就是过热要预警；刚启动的板块要连续三天确认才采信。 |  |
| MOD-SIG-120 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-1:结构强度评估（分 1.9） | TDM-E-L3-12-4:形态结构识别（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 盯大小盘风格切换：大盘小盘收益差持续五天以上算风格确立；早盘前半小时的动量对后半小时有预测力，配合VWAP偏离和分时趋势强度使用。 |  |
| MOD-SIG-121 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-02-2:单板块轮动预警（分 1.5） | TDM-E-L2-03-1:扩散指标进度追踪（分 1.0） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 跟踪恐慌怎么传染：哪些票突然大幅回撤、同一个板块里是不是成片下跌、恐慌从一个板块传到另一个板块要多久。 |  |
| MOD-SIG-122 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-07-1:回踩ABC判定（分 0.9） | TDM-E-L3-12:个股多维验证（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 验证A股的时间规律：哪个月份、星期几、节假日前后、交割日真的存在统计上显著的涨跌效应，通过检验的节点编成效应日历。 |  |
| MOD-SIG-123 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-09-1:事件图谱传导（分 1.9） | TDM-E-L3-12-3:筹码分布分析（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 看不同类型事件发生后股价通常怎么分布：按事件类型分桶统计收益分布直方图和分位数，盘后批量处理不超过100只。 |  |
| MOD-SIG-124 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-3:筹码分布分析（分 1.9） | TDM-E-L2-04-2:虹吸态识别（分 1.0） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 识破主力的六种假动作：假拉升真出货、假突破真派发等，用七个维度打分，嫌疑超过85%就提示暂停追涨。 |  |
| MOD-SIG-125 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-09-1:事件图谱传导（分 2.2） | TDM-E-L2-06-3:强度加权传导（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 把公司和产业环节的投入产出关系存成图：谁是谁的上游、影响沿哪条链传导、强度逐级衰减多少，都能查。 |  |
| MOD-SIG-126 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-09:股票池分层维护（分 1.3） | TDM-E-L2-09-2:冲击标的生成（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 用三种关系图（供应链、同行业、概念共现）把邻居股票的信息聚合到本股票上，增强密度预测，纯内存实现不装重型图库。 |  |
| MOD-SIG-127 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-07-2:多因子打分链（分 0.6） | TDM-E-L2-01-4:板块资金流聚合（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 用因果机器学习回答「这个因子真的导致收益吗」：双重机器学习估效应、因果森林看异质性、反事实证伪、自动发现因果图，显著才采信。 |  |
| MOD-SIG-128 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-03:调整周期进度（分 0.3） | TDM-E-L2-05-1:水温档推导（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给预测区间在线校准：实际覆盖率不够就放宽、太宽就收窄，步长越调越小最终稳定，保证预测区间长期命中率贴近目标。 |  |
| MOD-SIG-129 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 看量做策略：缩量、平量、放量三种量能状态乘上趋势、均值回归、混沌三种市场体制，查表得出当前该怎么配仓。 |  |
| MOD-SIG-130 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.0） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 把量能、体制、风格三个维度组合成18个格子，每个格子存一套仓位、方向、持仓周期、止损参数，参数靠历史回测逐格填。 |  |
| MOD-SIG-131 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-05-2:信号响应三件套（分 2.8） | TDM-E-L2-01-5:市场级调节注入（分 1.0） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 按信号最近的实际表现动态调权重：胜率高、回撤小的信号加权，单次调整不超过两成，全程留审计，调坏了可按版本回滚。 |  |
| MOD-SIG-132 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-07:回踩质量分级（分 0.3） | TDM-E-L2-09-2:冲击标的生成（分 0.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 做T之前先算账：价差扣掉双边佣金、印花税、冲击成本还剩多少净利，给置信度，实际成交后回写校准成本参数。 |  |
| MOD-SIG-133 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 策略间共享的公共参数、市场状态、特征缓存只认一个真源：写就升版本并广播变更，读方定期对版本戳，不一致拉清单告警。 |  |
| MOD-SIG-144 | _signal | - | （段内零文本命中） | — | 规则段 E-JUDGE（E流判据层(L2/L3)） | sector_report_builder（MOD-L00-009 production）日频报告 → 本件四维跨截面排名归一 （结构强度/动量活跃/多周期动量 | needs_chief |
| MOD-SIG-145 | _signal | D_ASHARE_SIGNAL | （段内零文本命中） | — | 规则段 E-JUDGE（E流判据层(L2/L3)） | 统一图形识别引擎的 win_rate_provider 注入契约至今无实现侧（MOD-SIG-091 蓝图 明言"引擎不自建统计"）——MOD-SIG-115  | needs_chief |
| MOD-SIG-146 | _signal | D_ASHARE_SIGNAL | （段内零文本命中） | — | 规则段 E-JUDGE（E流判据层(L2/L3)） | 治本路径不开"第 10 大类"铺形态条目，而是造一个"换记账方式"的底座： OHLCV 时间序列 → 替代序列（Renko 砖块 / P&F 点数列 / Kag | needs_chief |
| MOD-SIG-147 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-01-5:市场级调节注入（分 0.6） | TDM-E-L2-06-3:强度加权传导（分 0.6） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 读取K线组合规则的YAML配置卡，把形态、支撑阻力位置、成交量三个条件组合成买卖方向和强度判断，供统一图形引擎使用 |  |
| MOD-SIG-148 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-12-4:形态结构识别（分 1.9） | TDM-E-L2-01-5:市场级调节注入（分 0.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 给图形库里每个形态的胜率成绩单盖真伪章的机器：它用四道纯数学关卡(多重检验校正/有效样本折扣/分市场状态对照/小样本收缩)自动判定哪些形态的成绩是真本事、哪些只 |  |
| MOD-SIG-149 | _signal | D_ASHARE_SIGNAL | TDM-E-L2-08:板块生命周期判定（分 3.9） | TDM-E-L3-12-4:形态结构识别（分 1.9） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 管形态生老病死的台账员：一个形态连续20天成绩不达标就盖'退役'章并记下死亡时的样子，之后它的每一分新数据都偷偷记着账——哪天死后新证据足够好(通过比初赛更严的 |  |
| MOD-SIG-150 | _signal | D_ASHARE_SIGNAL | TDM-E-L3-03-3:双策略合流体检（分 1.3） | TDM-E-L3-07:策略专属链（分 1.3） | 规则段 E-JUDGE（E流判据层(L2/L3)） | 定期检查已上线策略的成绩单：折减夏普还达标就继续留用，跌到警戒线以下就先观察，连续不达标就出退役建议单交给策略域管线执行，退役后成绩回升还能自动撤销退役建议 |  |
| MOD-SIGQC-003 | _signal_quality | D_AUDITTEST | TDM-E-L2-07-1:回踩ABC判定（分 1.2） | TDM-E-L4-01:分批建仓（分 1.2） | 规则段 ALL（全图按简介文本匹配） | SignalDedup — 信号去重器（MOD-SIGQC-003）。B11-02594（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CA |  |
| MOD-SIGQC-005 | _signal_quality | D_AUDITTEST | TDM-E-L0-02:偏离监控与修订（分 1.9） | TDM-E-L1-S0-1:新闻情绪语义分析（分 1.9） | 规则段 ALL（全图按简介文本匹配） | SignalQualityBenchmark — 信号质量基准对比器（MOD-SIGQC-005）。D-SIGNAL-157）：当前 IC/覆盖率/稳定性 vs |  |
| MOD-SIGQC-006 | _signal_quality | D_AUDITTEST | TDM-E-L2-05-2:信号响应三件套（分 0.6） | TDM-F-C3-05:可靠度养成与信号健康（分 0.6） | 规则段 ALL（全图按简介文本匹配） | SignalExplainabilityGuarantor — 信号可解释性强制保障器（MOD-SIGQC-006）。 |  |
| MOD-SIM-002 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 策略仿真器——策略沙箱, 在隔离环境中对模拟市场数据运行注入的策略, 仿真信号生成(L2)+组合构建(L3)两个流水线阶段, 产出 SimulationResu | needs_chief |
| MOD-SIM-003 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 风控仿真器——VaR(风险价值)模拟 + 回撤模拟 + 熔断模拟。基于收益率序列 计算多方法 VaR/CVaR、最大回撤及恢复期、熔断触发判定, 供风控评估和  | needs_chief |
| MOD-SIM-005 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 场景生成器——生成 what-if 市场场景(SimulationScenario), 供 SIM-01 市场仿真 / SIM-02 策略仿真 / SIM-04 | needs_chief |
| MOD-SIM-012 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 仿真结果分析器——对多个 SimulationResult(跨场景, 来自 SIM-02 策略仿真)执行聚合统计分析+分布检验+可视化数据准备, 输出 Simu | needs_chief |
| MOD-SIM-021 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 参数鲁棒性测试器——寻找参数**稳定区间**而非最优值, 输出参数敏感性曲线 + 扰动测试 + 稳定区间标注 + 过拟合风险评估。核心思想: 鲁棒参数在较宽范围 | needs_chief |
| MOD-SIM-022 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 未来函数风险检测器——检测回测中的 look-ahead bias(前瞻偏差), 确保所有判断 仅基于当时已知数据。扫描特征矩阵 + 截断重算验证特征函数, 产 | needs_chief |
| MOD-SIM-023 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | Sharpe 计算修正器——A股场景的 Sharpe 比率修正计算。解决标准 Sharpe 的5个问题: 1. 无风险利率用中国10年期国债(非美国T-bill | needs_chief |
| MOD-SIM-024 | _simulation | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | Deflated Sharpe Ratio (DSR) 计算器——多重测试偏差修正的 Sharpe 比率。 基于 Bailey & López de Prado | needs_chief |
| MOD-SIM-028 | _simulation | D_AUDITTEST | TDM-F-C3-04:参数校准闭环（分 1.5） | TDM-E-L3-07-2:多因子打分链（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 给因子、策略、信号、模型四道防过拟合检查：IC衰减、多重检验、缩水夏普、前向验证，任何一关不过就不准上线。 |  |
| MOD-TRADING-002 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 盈亏计算器——交易后盈亏核算基础设施。从成交回报(Fill)和持仓均价计算已实现盈亏, 从持仓+当前市价计算未实现盈亏, 含A股交易成本(佣金/印花税/过户费) | needs_chief |
| MOD-TRADING-003 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 结算对账器——盘后交易级对账基础设施。每日 15:30 后自动比对系统交易记录 (来自 D-EX-CORE 的 Fill)与券商结算单(Broker Settl | needs_chief |
| MOD-TRADING-004 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 公司行动处理器——A股公司行动事件处理基础设施。处理除权除息/现金分红/送股/ 配股/拆股等公司行动事件, 自动调整持仓数量和均价, 产出 E-TR-03 Co | needs_chief |
| MOD-TRADING-009 | _trading | D_TRADING | TDM-E-L4-10:订单生命周期状态机（分 3.1） | TDM-E-L2-08:板块生命周期判定（分 1.8） | 规则段 ALL（全图按简介文本匹配） | 交易运营域的订单大管家：一笔外部指令从接收到派发、执行、成交、结算、对账的全生命周期都记在一本账上；同一个幂等键重复登记不会建第二笔；每次状态变化都发一条不可变 |  |
| MOD-TRADING-010 | _trading | D_TRADING | TDM-F-C2:组合聚合（分 1.3） | TDM-P-P1-01:持仓对账与台账快照（分 1.2） | 规则段 ALL（全图按简介文本匹配） | 交易运营域的结算档案柜：每个结算日一份结算记录，从未核到一致、差异、核销、确认归档全程留痕；对账差异自动分三档，费用类只看不升级，价格和缺失类自动生成处理工单并 |  |
| MOD-TRADING-011 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 候选 spec：人工买入/卖出/调仓指令通道——指令 schema（标的/方向/数量/时限）+ 录入接口 （CLI/前端）+ 必经 C-004 风控与盘前边界校 | needs_chief |
| MOD-TRADING-012 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 候选 spec：价格快照 + NAV/P&L 确认 + 风险重估，挂 post_settlement_pipeline 15:30 链； 依赖前置 settle | needs_chief |
| MOD-TRADING-014 | _trading | D_TRADING | TDM-X-S2-04:本地条件单管理（分 1.0） | TDM-X-S2-02:T+1与涨跌停约束（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 证券基础信息唯一真源：代码、名称、行业、涨跌停规则、ST标记、交易日历统一维护，每天日终刷新版本加一，别处只准查不准抄。 |  |
| MOD-TRADING-015 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | 交易决策地图 V0 后端骨架——决策内容索引层（项目第 7 张地图性质）。回答"**什么市场情况、在决策链哪个环节、用哪个策略/因子、靠哪些数据、由哪段代码实现 | needs_chief |
| MOD-TRIG-001 | _trading | - | （段内零文本命中） | — | 规则段 ALL（全图按简介文本匹配） | <!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_pa | needs_chief |
| MOD-VOTE_REVIEW_SHELL | _autonomy_core | D_AUDITTEST | TDM-F-C3-02:升降级管线与退役评审（分 1.3） | TDM-E-L4-07:条件触发队列（分 0.9） | 规则段 ALL（全图按简介文本匹配） | 多开工位方案的唱票员。遇到拿不准的大事，人可以开几个 AI 会话各写一版方案放进文件夹，它负责收齐、按规则唱票、把胜出方案和计票报告落盘；它从不自己启动，只有人 |  |
| MOD-XS-008 | _ex_sor | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | P-4 裁定组件（90 号文档待定问题 P-4「RL 执行是否实施」的工程留痕）：RL 执行层**骨架**——gym 风格训练环境 + 硬边界包裹层 + 执行参 | needs_chief |
| MOD-XS-015 | _ex_sor | D_AUDITTEST | TDM-E-L4-14:执行成本反馈与选型回写（分 1.8） | TDM-E-L4-13:执行容灾对账（分 0.9） | 规则段 E-L4（E-L4执行段） | 订单的智能导航员：给一笔要买的单子挑最合适的券商通道，看延迟、成交率、手续费、盘口流动性四样打分，流动性太差的通道先踢掉；再把大单拆成小单（冰山、TWAP、量比 |  |
| MOD-XS-017 | _ex_sor | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 滑点分析器——成交后评估"实际成交价"相对"预期基准价"的偏离（滑点），是 TCA（交易成本分析）的核心组件。 | needs_chief |
| MOD-XS-019 | _ex_sor | - | （段内零文本命中） | — | 规则段 E-L4（E-L4执行段） | 交易成本优化器——计算 A 股交易的全成本（显性 + 隐性），分解到六项组件，并给出优化建议。 | needs_chief |
