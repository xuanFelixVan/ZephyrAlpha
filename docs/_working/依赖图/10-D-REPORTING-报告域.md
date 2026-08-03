# 10 — D-REPORTING 报告域

> **状态**: DRAFT | **核心层**: L07 | **成熟度**: L1 🔵骨架 | **简称**: RPT
> **域描述**: 绩效归因+风险报告+审计凭证生成
> **一句话**: 算出赚了多少钱、为什么赚——纯消费层，不发布领域事件，不拥有Aggregate Root
>
> **核心职责流**: CTR-005 Fill + CTR-006 PositionSnapshot接收 → PnL&归因计算 → CTR-P1-009 PerformanceAttributionReport输出 → 微信/Dashboard推送

## §0 域定义

| 维度 | 内容 |
|------|------|
| 域ID | D-REPORTING |
| 简称 | RPT |
| 核心Aggregate | 无（纯消费层，不拥有Aggregate Root） |
| 核心事件 | 无（纯消费者，通过ACL防腐层订阅上游域事件） |
| 开发状态 | 骨架——13个子模块待建 |
| 优先级 | P1（下游消费域） |
| 激活前提 | D-EX-CORE就绪(CTR-005/CTR-006可订阅) + D-DATA可访问 |
| 蓝图编号 | MOD-L07-001（未建设） |
| 域级模块裁定 | 35个模块 | P0=4 | P1=14 | P2=17 | ✅能建28(80%) | ❌不能建7(20%) |

## §1 子模块清单

### §1.1 P0 核心模块

| ID | 名称 | 职责 | C轨映射 | 建设状态 | 受限门禁 |
|----|------|------|---------|---------|---------|
| D-REPORTING-01 | TCA Engine | 交易成本分析(滑点/冲击成本/市场影响量化)。输入CTR-005+CTR-006 | C-010● | ✅可建 | — |
| D-REPORTING-02 | Attribution Engine | 绩效归因Brinson+多因子。收益归因(配置效应+选择效应+交互效应)+因子归因+风险归因+策略退化检测(IC衰减>50%=退化+拥挤度检测+自动降权)。输入CTR-005+CTR-006+CTR-P1-001 | C-010● | ❌部分受限 | 多因子归因+策略退化检测: D-FACTOR就绪(CTR-P1-001可订阅) |
| D-REPORTING-03 | Report Publisher | 报告生成/分发/归档+SQLite report_archive+Parquet数据文件+LLM摘要+ACL防腐层数据汇聚。所有分析结果汇聚至此发布。分发渠道:微信Webhook+邮件SMTP | C-010● | ❌部分受限 | LLM摘要: LLM服务可用(Ollama+qwen3:8b); Crypto-Shredding接口: GATE-004/GATE-006激活 |
| D-REPORTING-15 | A-Share Trading Review Engine | A股交易归因/盘前信号验证(因子IC>阈值∧信号一致性>阈值)/盘中异常检测(价格偏离>2σ∨成交量>3倍均值)/盘后归因分析(Brinson+因子归因)/绩效统计/大额交易异动检测(买卖金额≥X万元,席位集中度≥Y%) | C-010● | ❌受限 | D-EX-CORE执行报告可订阅(CTR-P1-007/CTR-ERR-005) |

### §1.2 P1 扩展模块

| ID | 名称 | 职责 | 建设状态 | 受限门禁 |
|----|------|------|---------|---------|
| D-REPORTING-04 | Real-time P&L Dashboard | 实时盈亏仪表盘(3s刷新)。实时PnL/持仓/订单/风控状态 | ✅可建 | — |
| D-REPORTING-05 | Report Publisher & Aggregation Hub | 报告聚合枢纽(与D-REPORTING-03合并，03为主发布器) | — | — |
| D-REPORTING-06 | Regulatory Report Generator | 监管报告生成器(证监会/交易所报告+数据完整性校验)。含程序化交易报告+异常交易自报+持仓报告+绩效报告 | ✅可建(基础版) | 自动化接口: GATE-002(AUM≥1000万)或GATE-003(跨市场) |
| D-REPORTING-08 | Risk Report Engine | 风险报告引擎(日度/周度/事件/月度4类风险报告生成)。消费D-RISK诊断结果 | ✅可建 | — |
| D-REPORTING-14 | Strategy Explainability Reporter | 策略可解释性报告器(SHAP+LIME双归因+可解释性门控) | ✅可建 | — |
| D-REPORTING-26 | A-Share Performance Audit & Optimization Trigger | A股绩效审计与优化触发器(绩效审计+自动触发优化建议) | ✅可建 | — |

### §1.3 P2 辅助模块

| ID | 名称 | 职责 | 建设状态 | 受限门禁 |
|----|------|------|---------|---------|
| D-REPORTING-13 | Report Version Manager | 版本存储器+差异引擎+快照管理器+审计链验证器 | ✅可建 | — |
| D-REPORTING-17 | Report Watermark Tracker | 报告水印追踪器(报告完整性+来源追溯) | ✅可建 | — |
| D-REPORTING-27 | A股交易记录模板引擎 | 11个必填字段模板+字段强制校验+模板版本管理 | ✅可建 | — |

### §1.4 P1/P2 ❌受限模块汇总

| ID | 名称 | 受限门禁 |
|----|------|---------|
| 监管报告自动化接口 | 自动化监管报送接口 | GATE-002(AUM≥1000万)或GATE-003(跨市场); 需券商/监管API对接+报送格式标准 |
| 税务报告 | 税务报告生成器 | 需税务系统对接 |
| 报告水印(协作版) | 协作平台水印 | 需协作平台 |
| 协作批注 | 报告协作批注 | 需协作平台 |
| PlantUML渲染 | 报告内嵌图表渲染 | 需协作平台 |
| ADR生成 | 架构决策记录自动生成 | 需协作平台 |
| 依赖变更日志 | 模块依赖变更日志 | 需协作平台 |

### §1.5 建设状态汇总

| 状态 | 模块/功能 |
|------|---------|
| ✅可建 | D-REPORTING-01(TCA); D-REPORTING-02(Brinson三因子归因); D-REPORTING-03(基础发布+归档); D-REPORTING-04; D-REPORTING-06(基础版); D-REPORTING-08; D-REPORTING-13; D-REPORTING-14; D-REPORTING-15(基础版); D-REPORTING-17; D-REPORTING-26; D-REPORTING-27; 日志独立加密基础设施; L2集合完整性; 差分隐私(ε=1.0,策略回测报告/因子统计发布时隐私保护) |
| ❌受限 | D-REPORTING-02(多因子归因+策略退化检测)→D-FACTOR; D-REPORTING-03(LLM摘要)→LLM服务; D-REPORTING-03(Crypto-Shredding)→GATE-004/006; D-REPORTING-15→D-EX-CORE执行报告; 监管报告自动化→GATE-002/003; Crypto-Shredding密钥销毁→GATE-004/006; L1事件完整性→D-AUTONOMY-CORE; L3外部可验证性→GATE-004/006; 合规证据图跨法规协调→GATE-006; 依赖图ZK证明→GATE-004/006; DORA ICT事件报告→GATE-006 |

### §1.6 术语转化记录

| 原术语 | 性质 | 量化框架术语 |
|--------|------|------------|
| 龙虎榜异动 | 主观交易经验 | 大额交易异动检测(量化阈值:买卖金额≥X万元,席位集中度≥Y%) |
| 盘前SOP | 主观操作流程 | 盘前信号验证(量化校验:因子IC>阈值∧信号一致性>阈值) |
| 盘中监控 | 主观盯盘经验 | 盘中异常检测(量化规则:价格偏离>2σ∨成交量>3倍均值) |
| 盘后复盘 | 主观经验总结 | 盘后归因分析(Brinson分解+因子归因) |
| 策略健康评分 | 半主观(评分模糊) | 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) |
| 优化建议 | 主观经验驱动 | 参数调整建议(量化驱动:IC衰减>50%→降权) |
| 教训知识 | 主观经验归纳 | 历史失效模式库(量化触发:模式匹配+统计显著性) |
| 异常决策自检 | 半主观 | 异常决策检测(统计偏离模型输出分布) |
| 做T复盘报告 | 主观交易经验 | 做T策略归因报告(胜率/盈亏比/与基准对比量化) |
| 执行质量报告 | 半主观 | TCA交易成本分析报告(滑点/冲击成本/市场影响量化) |

## §2 依赖关系

### §2.1 域内依赖

| 源模块 | 目标模块 | 依赖原因 |
|--------|---------|---------|
| D-REPORTING-01 | D-REPORTING-03 | TCA结果需发布 |
| D-REPORTING-02 | D-REPORTING-03 | 归因结果需发布 |
| D-REPORTING-04 | D-REPORTING-03 | 实时PnL需发布 |
| D-REPORTING-08 | D-REPORTING-03 | 风险报告需发布 |
| D-REPORTING-14 | D-REPORTING-03 | 可解释性报告需发布 |
| D-REPORTING-15 | D-REPORTING-03 | A股复盘需发布 |
| D-REPORTING-26 | D-REPORTING-02 | 绩效审计消费归因结果 |

### §2.2 域间接口

#### 消费依赖

| 契约ID | 来源域 | 契约内容 | 关键度 | 消费模块 | 关联事件(ACL) |
|--------|--------|---------|:------:|---------|--------------|
| CTR-005 | D-EX-CORE | Fill | P0 | D-REPORTING-01/02 | E-EX-04 FillReceived |
| CTR-006 | D-EX-CORE | PositionSnapshot | P0 | D-REPORTING-01/02 | — |
| CTR-P1-001 | D-FACTOR | FactorMonitorReport | P1 | D-REPORTING-02 | — |
| CTR-P1-006 | D-PF-CORE | StrategyLifecycleEvent | P1 | D-REPORTING-02 | E-PF-01 PortfolioRebalanced |
| CTR-P1-007 | D-EX-CORE | ExecutionReport | P1 | D-REPORTING-01/15 | — |
| CTR-P1-008 | D-RISK | RiskDashboardSnapshot | P1 | D-REPORTING-04/08 | — |
| CTR-P1-011 | D-RISK | RiskMetricsReport(VaR/CVaR/回撤) | P1 | D-REPORTING-08 | — |
| CTR-ERR-005 | D-EX-CORE | ExecutionRejectionError | P0 | D-REPORTING-15 | — |
| C-032诊断结果 | D-RISK | 资金曲线诊断数据 | P1 | D-REPORTING-08 | E-RK-03 DrawdownAlerted |
| 决策事件 | D-AUTONOMY-CORE | 决策溯源链 | P1 | D-REPORTING-14 | 决策事件 |
| — | D-RESEARCH | BacktestCompleted | P1 | D-REPORTING-15 | E-RS-02 BacktestCompleted |
| — | D-DATA | 交易记录+行情数据 | P0 | D-REPORTING-02/04 | — |
| CTR-TRACE-001 | D-DATA-ENG | 数据血缘链(source_id→transform→output_contract) | P1 | D-REPORTING-02/14 | — |

#### 产出依赖

| 契约ID | 目标域 | 契约内容 | 关键度 | 生产模块 |
|--------|--------|---------|:------:|---------|
| CTR-P1-009 | D-FRONTEND + D-COMPLIANCE + D-PF-CORE + D-AUTONOMY-CORE | PerformanceAttributionReport | P1 | D-REPORTING-02 |

#### 事件发布

报告域为纯消费层，不发布领域事件(D-RPT-D01)。

### §2.3 C-010能力卡片

| 维度 | 内容 |
|------|------|
| 能力描述 | 每日自动生成交易复盘报告：PnL按策略/按账户/按标的拆分→策略归因→持仓风险扫描→大额交易异动检测→微信推送摘要 |
| 输入 | C-002成交回报+订单记录+执行质量数据; C-017费率数据(PnL准确计算); C-009因子值+信号值(归因分析); C-004风控触发记录 |
| 输出 | 每日PnL报表(按策略/按账户/按标的)→C-007; 策略归因报告→C-007①; 因子表现报告(IC/ICIR/衰减曲线)→C-007②; TCA交易成本分析报告(滑点/冲击成本)→C-007③⑫; 做T策略归因报告(胜率/盈亏比)→C-007⑦; 大额交易异动报告→C-034主力画像更新; 微信推送摘要→用户审阅 |
| 成功标准 | ①清算在15:30前完成 ②大额交易异动报告在数据到达后30分钟内完成 ③归因准确(可追溯到每笔交易) |
| 降级模式 | C-017(P1)未就绪时，PnL计算不含费率扣除(使用0费率近似，PnL略高于实际)，归因准确性略降; C-017上线后自动接入费率数据 |
| 数据一致性SLA | 报告数据1小时内一致(事件驱动异步聚合); 超时→标记报告待更新 |

### §2.4 激活阶段

| 阶段 | 激活模块 | 前提 |
|:----:|---------|------|
| Phase 1 | D-REPORTING-01(Brinson) + D-REPORTING-03(基础) + D-REPORTING-04 | D-EX-CORE就绪(CTR-005/006) + D-DATA可访问 |
| Phase 2 | D-REPORTING-02(完整) + D-REPORTING-15 | Phase 1完成 + D-EX-CORE执行报告可订阅 + D-FACTOR就绪 |
| Phase 3 | D-REPORTING-14 + D-REPORTING-08 | D-AUTONOMY-CORE决策事件可订阅 + D-RISK诊断数据可消费 |
| Phase 4 | D-REPORTING-06 + D-REPORTING-26 | Phase 2完成 + 合规数据库就绪 |

## §3 设计决策

| # | 决策 | 影响 |
|---|------|------|
| D-RPT-D01 | 不发布领域事件 | 下游域通过CTR-P1-009消费归因报告 |
| D-RPT-D02 | 子模块骨架厚度 | 子模块从35+精简到13(含P0/P1/P2) |
| D-RPT-D03 | 归因模型：Brinson先行，多因子后期 | D-REPORTING-02分两阶段交付 |
| D-RPT-D04 | 事件订阅走ACL防腐层 | 新增域事件只需在ACL注册 |
| D-RPT-D05 | 所有子模块汇聚至Publisher Hub | D-REPORTING-03是唯一出口 |
| D-RPT-D06 | Decision Trace Collector独立子模块 | 与D-AUTONOMY-CORE解耦 |
| D-RPT-D07 | Capital Curve Analyzer消费D-RISK诊断结果 | RPT不做独立诊断 |
| D-RPT-D08 | 降级策略：C-017未就绪时PnL不含费率 | D-REPORTING-01需实现降级逻辑 |
| D-RPT-D09 | 硬依赖：D-AUTONOMY-CORE + D-DATA | 缺少任一硬依赖域无法完整激活 |
| D-RPT-D10 | 软依赖：D-INFRA-RUNTIME | 无INFRA-RUNTIME时使用本地事件总线替代 |
| D-RPT-D11 | 报告存储：SQLite+Parquet归档 | 与D-DATA存储架构对齐; 热SQLite+温Parquet+冷压缩归档7年 |
| D-RPT-D12 | 数据血缘：MVP用SQLite存储血缘 | 单机场景SQLite足够; 完整实现后适配OpenLineage标准 |
| D-RPT-D13 | 审计日志append-only | 事件溯源保证不可篡改，满足合规审计要求 |
| D-RPT-D14 | 报告数据一致性1小时SLA | 事件驱动异步聚合; 下单Saga Step 6:报告生成失败→标记报告待更新(异步) |
| D-RPT-D15 | 盘后报告走本地LLM | 无延迟约束，本地推理即可; 复杂推理走外部LLM API |

## §4 合规约束

> 对标EU AI Act Art.12(日志记录)、MiFID II RTS 6(算法交易审计)、SEC Rule 613(Consolidated Audit Trail)。核心目标：任何历史决策可在审计时完整重建，无需外部知识。

### §4.1 三层审计架构

| 层级 | 机制 | 报告域职责 | 建设状态 | 受限门禁 |
|------|------|-----------|---------|---------|
| L1 事件完整性 | 哈希链：每事件含前事件哈希+自身内容哈希，篡改导致后续哈希失效 | D-REPORTING-14收集与存储 | ❌受限 | D-AUTONOMY-CORE决策事件可订阅 |
| L2 集合完整性 | Merkle树：日/周/月批量完整性证明，删除/篡改可检测 | D-REPORTING-03归档与发布 | ✅可建 | — |
| L3 外部可验证性 | Merkle根锚定外部时间戳权威(可选)+零知识证明+选择性披露 | — | ❌受限 | GATE-004/006 |

> 参考VCP v1.1三层完整性架构，覆盖87% EU AI Act/MiFID II/MAR监管要求。Tamper-Evident设计(篡改可检测)，非Tamper-Proof(篡改不可能)，与SEC Rule 17a-4/FINRA/GDPR Art.5(1)(f)监管共识一致。

### §4.2 审计日志分类与保留

| 日志类型 | 保留期限 | 不可篡改机制 | 法规依据 |
|---------|---------|-------------|---------|
| 交易日志 | ≥7年 | 哈希链 | SEC Rule 613；证监会交易记录留存 |
| 决策日志 | ≥3年(GATE-006后≥7年) | 哈希链 | 能力定位书§6.6 L-007；EU AI Act Art.12+MiFID II RTS 6 |
| 合规日志 | ≥7年 | 哈希链 | SOX Section 404；Basel III Pillar 3 |
| 模型日志 | ≥5年 | 哈希链 | SR 26-2；EU AI Act Art.12 |
| 系统日志 | ≥1年 | 哈希链 | 证监会信息系统管理要求 |

### §4.3 审计日志查询与校验

| 校验类型 | 频率 | 范围 | 方法 |
|---------|------|------|------|
| 启动校验 | 每次系统启动 | 最近1棵Merkle树 | 根哈希比对+哈希链验证 |
| 每日校验 | 每日收盘后 | 全部Merkle树 | 完整Merkle树重建+根哈希比对 |
| 按需校验 | 安全事件触发 | 指定范围 | 哈希链遍历+Merkle包含证明(O(log N)) |
| 随机抽样 | 每周 | 随机10棵Merkle树 | Merkle包含证明验证 |

审计日志访问控制：仅追加(Append-Only); Trader/Administrator可读全部; AI_Agent仅读自身日志; 访问审计日志操作本身也记录到审计链(元审计)。

### §4.4 时钟同步

标准电子交易最大偏差1毫秒，NTP同步+本地时钟校准(MiFID II RTS 25)。D-REPORTING-14收集决策溯源链时，所有时间戳精度≤1毫秒。

### §4.5 Crypto-Shredding

**结论**：数据保密性≠数据完整性。加密个人数据(独立密钥)→哈希链基于密文→销毁密钥即GDPR合规，完整性不受影响。

| 实施项 | 建设状态 | 受限门禁 |
|--------|---------|---------|
| 日志独立加密基础设施(AES-256-GCM) | ✅可建 | — |
| 密钥销毁+销毁证书+被遗忘权响应 | ❌受限 | GATE-004/GATE-006激活 |

> 当前单人使用不触发GDPR被遗忘权。VCP v1.1 Crypto-Shredding PoC已开源(Apache 2.0，含Python实现+MQL5桥接，27项测试100%通过)。

### §4.6 决策溯源链

**证据图模型**：AI决策记录为DAG不可变节点，类型化边连接因果前驱/后继，边携带密码学证据包。节点链路：数据输入(数据指纹)→因子计算(因子指纹)→信号生成(信号指纹)→策略决策(策略指纹)→仓位裁决(仓位指纹)→订单执行(订单指纹)。

**TraceCompleteness指标**：TC=|D_r|/|D_t|≥0.997。D-REPORTING-14负责构建并维护证据图模型。

**决策日志结构**：

| 字段 | 类型 | 监管依据 |
|------|------|---------|
| decision_id | UUID | 可追溯性 |
| timestamp | ISO8601(毫秒精度) | MiFID II RTS 25 |
| input_hash | SHA-256 | 数据完整性 |
| model_version | string | EU AI Act Art.12 |
| feature_attribution | JSON(SHAP/LIME) | FINRA Rule 2210 |
| confidence | float | C-031分层决策 |
| human_approval | bool | EU AI Act Art.14 |
| prev_hash | SHA-256(DAG结构，单人单策略下退化为单前驱) | 不可篡改 |
| compliance_check | JSON | 合规审计 |

### §4.7 SHAP+LIME双归因架构

| 方法 | 优势 | 适用场景 | 延迟 |
|------|------|---------|------|
| SHAP | 全局稳定+理论保证(Shapley值) | 事后审计+模型验证 | 批量(非实时) |
| LIME | 局部可调+轻量 | 实时决策归因 | <12ms(缓存优化后) |

实时归因流程：C-031分层决策触发时同步调用LIME生成局部解释→写入决策日志feature_attribution字段→盘后SHAP批量计算校准LIME一致性。

### §4.8 监管报送

| 报送类型 | 频率 | 内容 | 建设状态 | 受限门禁 |
|---------|------|------|---------|---------|
| 程序化交易报告 | 一次性+变更 | 合规架构§1.4 | ❌受限(自动化) | GATE-002/GATE-003(自动化接口); 需券商/监管API对接+报送格式标准 |
| 异常交易自报 | 事件驱动 | 异常交易行为 | ❌受限(自动化) | GATE-002/GATE-003 |
| 持仓报告 | 月/季 | 持仓结构/集中度/行业偏离 | ❌受限(自动化) | GATE-002/GATE-003 |
| 绩效报告 | 季/年 | 收益/风险/归因 | ❌受限(自动化) | GATE-002/GATE-003 |

> 当前均为手动填报。DORA(ICT事件报告:4h初始→72h中间→1月最终)GATE-006后适用，当前由A9运维架构事件响应流程代管。

### §4.9 合规证据图

| 功能 | 建设状态 | 受限门禁 |
|------|---------|---------|
| 证据链完整性验证 | ✅可建 | — |
| 证据自动采集(从各系统模块自动采集+时序对齐) | ✅可建 | — |
| 证据图查询引擎(Neo4j图数据库驱动) | ✅可建 | — |
| 时序一致性验证 | ✅可建 | — |
| 跨法规证据协调器(DORA/MiFID II/GDPR 47%控制点重叠合并) | ❌受限 | GATE-006 |
| DORA ICT穿透依赖映射 | ❌受限 | GATE-006 |
| 依赖图ZK证明(证明合规但不暴露证据内容) | ❌受限 | GATE-004/006 |
| 合规条款依赖链验证(EU AI Act Art.9→15→11) | ❌受限 | GATE-006 |

### §4.10 合规审计时重建历史状态

审计重建流程：加载前一日收盘快照→加载当日增量快照→回放指定时段事件→重建完整状态(持仓+信号+风控+交易记录+因子截面)→生成审计报告。

审计保证：事件不可篡改(append-only+SHA-256校验)+状态可验证(事件回放结果与快照一致)+因果链完整(correlation_id+causation_id)+时间戳精确到微秒。

## §5 交叉架构约束

### §5.1 风险报告(来源:A4§4.3)

| 报告类型 | 频率 | 内容 | 消费者 |
|---------|------|------|--------|
| 日度风险摘要 | 每日收盘 | VaR/CVaR/因子暴露/否决统计/漂移状态/Amihud非流动性 | Trader+Risk Manager |
| 周度风险深度 | 每周五 | 压力测试+漂移趋势+策略拥挤度+模型健康度+反向RST | Risk Manager |
| 事件风险快报 | 事件触发 | 触发事件+影响评估+处置建议+历史类比 | Trader(即时) |
| 月度风险治理 | 每月末 | 风控参数变更审计+否决规则有效性+合规检查+Pod级止损统计 | Risk Manager+治理层 |

### §5.2 风控审计(来源:A4§5.3)

| 审计项 | 记录内容 | 保留期限 | 不可篡改机制 |
|--------|---------|---------|-------------|
| 否决日志 | 时间/规则/触发值/被否决指令 | ≥7年 | 哈希链+独立存储 |
| 参数变更日志 | 变更前/后/审批人/时间/理由 | ≥7年 | 哈希链+独立存储 |
| Kill Switch日志 | 触发条件/时间/恢复时间/人工确认 | ≥7年 | 哈希链+独立存储 |
| 漂移检测日志 | PSI/KS/CUSUM值/检测时间/处置动作 | ≥3年 | 哈希链 |
| Agent行为日志 | 行为记录/越界检测/OWASP ASI分类/处置动作 | ≥3年 | 哈希链 |
| Pod级止损日志 | 策略ID/回撤值/止损级别/处置动作 | ≥3年 | 哈希链 |

### §5.3 安全约束(来源:A5)

- 审批记录(机密L2)纳入审计报告须保持完整性
- 治理日志(机密L2)须含策略变更历史+权限变更历史
- 治理策略存储不可变(追加式日志+版本化)，消费时验证版本连续性
- 监管报送审批记录须含human_approval字段
- B-016: 禁止AI自动清理未归档交易日志和审计记录

| 资产类型 | 报告处理规则 | 信任等级 |
|---------|------------|---------|
| 治理策略 | 仅引用版本号+摘要 | 绝密(L3) |
| 自治权限定义 | 含权限变更审计记录 | 绝密(L3) |
| 审批记录 | 完整纳入，7年保留 | 机密(L2) |
| 治理日志 | 完整纳入，3年保留 | 机密(L2) |

差分隐私(ε=1.0)：用于策略回测报告/因子统计发布时的隐私保护。纯软件实现，✅可建。

### §5.4 Agent架构(来源:A7)

**归因Agent(Attributor)**：战略层Level 3全自主，盘后运行，延迟<60s。对应C-010+C-030。LLM路由：本地优先(结构化分析)。

| ✅能做 | ⚠️需审批 | ❌不可做 |
|--------|----------|---------|
| 归因报告/多维量化健康指标 | 策略参数/信号权重调整 | 改在线策略/绕回测应用优化 |

Agent Card: strategic-attributor | 归因Agent | 战略层 | 能力数2 | 技能数2 | Level 3

**归因Agent技能**：

| 技能ID | 技能名称 | 状态 |
|--------|---------|------|
| attribution-analysis | 归因分析 | ACTIVE |
| strategy-health-score | 多维量化健康指标(Sharpe+IC+MaxDD+Calmar加权) | ACTIVE |

**归因Agent消费映射**: D-DATA(交易记录)+D-REPORTING(报告数据) → D-REPORTING(归因报告)+D-PF-CORE(参数调整建议)

遗留问题裁定结果：

| 编号 | 裁定 | 与D-REPORTING关系 |
|:----:|:----:|-------------------|
| LP-007 | 🔴暂缓 | 归因Agent V3上线(V2稳定≥2月+AUM≥80万) |
| LP-019 | 🔴暂缓 | MVP替代:程序化交易披露由D-REPORTING处理 |
| LP-020 | 🔴暂缓 | MVP替代:EOD处理由D-REPORTING日终快照实现 |
| LP-021 | 🔴暂缓 | D-REPORTING产出CTR-P1-009→D-FRONTEND，前端暂缓不影响报告域产出 |

### §5.5 运维规格(来源:A9)

| 报告类型 | 指标 | 频率 | 数据源 |
|---------|------|:----:|--------|
| 系统可用率 | 交易时段≥99.99%/非交易≥99.9% | 日 | Prometheus |
| MTTR | 交易时段<5min/非交易<30min | 周 | P4事件日志 |
| AI自治成功率 | 常规故障≥95%/全部≥90% | 周 | P4修复日志 |
| 变更成功率 | 灰度≥95%/全量≥99% | 月 | CI/CD日志 |
| SLO达标率 | 各SLO指标达标率 | 月 | Prometheus |

灾备分级(L6日志审计)：RTO<240min, RPO≤24hour, 交易日志/操作日志/审计记录, 压缩归档+双副本。

### §5.6 学习系统(来源:A8)

**绩效归因**：

| 功能点 | 量化方法 |
|--------|---------|
| 收益归因 | Brinson模型：配置效应+选择效应+交互效应 |
| 因子归因 | 各因子对组合收益贡献 |
| 风险归因 | 各因子对组合风险贡献 |

**策略退化检测**：

| 功能点 | 量化方法 |
|--------|---------|
| IC衰减检测 | 因子IC 60日移动平均趋势，衰减>50%=退化 |
| 拥挤度检测 | 同策略参与者数量估计，上升=超额收益将消失 |
| 自动降权 | 策略退化时权重降为0 |

D-REPORTING-02产出策略退化检测数据→CTR-P1-009→D-PF-CORE(权重调整)+D-FRONTEND(退化预警)。

**效果反馈路径**：

| 反馈路径 | 接口 | 频率 |
|---------|------|:----:|
| C-010归因报告→学习系统知识效果评估 | CTR-P1-009 | 每日 |
| C-033过拟合检测→学习系统过拟合标记 | 归因报告 | 每周 |

**可解释性门控**：

| 门控层级 | 方法 | 建设状态 | 受限门禁 |
|---------|------|---------|---------|
| 基础 | SHAP/LIME解释+经济学原理→无法解释则拒绝部署 | ✅可建 | — |
| 因果(Causal SHAP) | 因果图计算Shapley值，区分真因果与伪相关 | ❌受限 | 因果发现引擎就绪(§5.2联动) |
| 概念级(Concept-Based) | 特征组合映射为人类可理解概念(如"动量反转""流动性枯竭") | ❌受限 | LLM-as-Explainer就绪 |
| 自然语言(LLM-as-Explainer) | LLM将SHAP/LIME数值解释转化为自然语言经济学解释 | ❌受限 | LLM服务可用 |

**v4.0+成功标准(报告域相关)**：

| 指标 | Phase 2 | Phase 3 |
|------|---------|---------|
| 可解释性门控覆盖率 | ≥60% | ≥90% |
| Causal SHAP一致性 | ≥60% | ≥80% |
| 概念解释可理解性 | ≥50% | ≥75% |
| Decision Audit Trail完整率(R-102) | ≥95% | ≥99% |
| 前视偏差检测率(R-95) | ≥80% | ≥95% |
| 过拟合检测多重检验调整率(R-94) | ≥80% | ≥95% |
| Signal Confidence校准度(R-96) | ≤15% | ≤10% |
| 实验记录完整率(R-92) | ≥95% | ≥99% |
| 可解释设计覆盖率 | ≥60% | ≥90% |
| 历史失效模式库预防规则命中率(R-115) | ≥50% | ≥70% |

### §5.7 数据血缘与可追溯性(来源:A3§9)

**血缘链全景**：数据源→L0接入→L1因子→L2信号→L3决策→L4执行→L5闭环，每层携带lineage_id+source+transform+timestamp。

**列级血缘**：

| 血缘层级 | 源列 | 变换逻辑 | 目标列 | 契约ID |
|---------|------|---------|--------|--------|
| L0→L1 | close(miniQMT) | 清洗+复权 | close_adj | CTR-001 |
| L1→L1 | close_adj | pct_change(20) | momentum_20d | CTR-002 |
| L1→L2 | momentum_20d_ranked | threshold>0.8 | momentum_buy_signal | CTR-004 |
| L2→L3 | momentum_buy_signal | risk_budget_alloc | buy_decision | CTR-005 |
| L3→L4 | buy_decision | risk_check+order_create | order_submitted | CTR-006 |

**OpenLineage标准适配**：

| OpenLineage概念 | 本系统对应 | 实现方式 |
|----------------|-----------|---------|
| Run | D-FACTOR-04 Pipeline批次 | run_id=batch_id |
| Job | 因子计算/信号生成/决策 | job_id=module_id |
| Dataset | Parquet分区/Redis Key | dataset_id=storage_path |
| Facet | 质量标记/版本号/IC值 | 自定义facet |

> MVP: SQLite存储血缘，覆盖L0→L1→L2。完整: OpenLineage标准+L0→L6全链路+血缘可视化查询。

### §5.8 数据架构补充(来源:A3§17.15)

| 模块ID | 模块名称 | 功能简述 | 建设状态 | 受限门禁 |
|--------|---------|---------|---------|---------|
| D-REPORTING-03 | Report Publisher | 报告生成/分发/归档+SQLite+Parquet | ✅可建 | — |
| D-REPORTING-13 | Report Version Manager | 版本存储+差异引擎+快照管理+审计链验证 | ✅可建 | — |
| D-REPORTING-27 | A股交易记录模板引擎 | 11必填字段模板+强制校验+版本管理 | ✅可建 | — |

### §5.9 治理架构契约(来源:A2§18.4)

| 治理相关契约/事件 | 来源域 | 治理架构对应 | 二元结论 |
|-----------------|--------|------------|:-------:|
| CTR-P1-009 PerformanceAttributionReport | D-REPORTING(L07) | §12成功指标(治理-任务解耦) | ✅ |
