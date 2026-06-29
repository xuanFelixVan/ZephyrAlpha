# 设计态迁移待人工补全清单（v2.0）

> 生成时间: 2026-06-18T20:23:20.817881
> 来源: MIG-4完整性审计差距报告 v2.0
> 缺失项总数: 171
> 信息不足项总数: 7
> 已成功补入: 159

## 说明

本清单记录了源MD文件中声明但depgraph.db中未找到对应设计态节点的模块。
v2.0版本支持11种ID格式的提取和补入：D-XXX-NN, C-XXX, GATE-XX-NN, HB-XXX-NN,
E-XXX-NN, AGG-XXX, CTR-XXX, VO-XXX, DD-XXX-NN, B-XXX, L-XXX。

## 信息不足项（缺模块名称，无法自动补入）

| # | 源MD文件 | ID格式 | 模块ID | 缺失字段 | 处置 |
|---|---|---|---|---|---|
| 1 | 01-跨域交叉点与因果链.md | B-XXX | B-020 | module_name | 记录到待人工补全清单 |
| 2 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-06 | module_name | 记录到待人工补全清单 |
| 3 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-001 | module_name | 记录到待人工补全清单 |
| 4 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-002 | module_name | 记录到待人工补全清单 |
| 5 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-003 | module_name | 记录到待人工补全清单 |
| 6 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-004 | module_name | 记录到待人工补全清单 |
| 7 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-005 | module_name | 记录到待人工补全清单 |

## 缺失项（源MD有声明，depgraph.db无匹配）

| # | 源MD文件 | ID格式 | 模块ID | 模块名称 | 缺失原因 |
|---|---|---|---|---|---|
| 1 | 00-总览与索引.md | VO-XXX | VO-001 | Money | path和功能名均未命中 |
| 2 | 00-总览与索引.md | VO-XXX | VO-002 | Price | path和功能名均未命中 |
| 3 | 00-总览与索引.md | VO-XXX | VO-003 | Quantity | path和功能名均未命中 |
| 4 | 00-总览与索引.md | VO-XXX | VO-004 | InstrumentId | path和功能名均未命中 |
| 5 | 00-总览与索引.md | VO-XXX | VO-005 | ISIN | path和功能名均未命中 |
| 6 | 00-总览与索引.md | VO-XXX | VO-006 | Exchange | path和功能名均未命中 |
| 7 | 00-总览与索引.md | VO-XXX | VO-007 | Timestamp | path和功能名均未命中 |
| 8 | 00-总览与索引.md | VO-XXX | VO-008 | DateRange | path和功能名均未命中 |
| 9 | 00-总览与索引.md | VO-XXX | VO-009 | Percentage | path和功能名均未命中 |
| 10 | 00-总览与索引.md | VO-XXX | VO-010 | IdempotencyKey | path和功能名均未命中 |
| 11 | 00-总览与索引.md | VO-XXX | VO-011 | LineageRoot | path和功能名均未命中 |
| 12 | 01-跨域交叉点与因果链.md | B-XXX | B-020 |  | path和功能名均未命中 |
| 13 | 01-跨域交叉点与因果链.md | B-XXX | B-002 | 交易安全 | path和功能名均未命中 |
| 14 | 01-跨域交叉点与因果链.md | B-XXX | B-003 | 交易安全 | path和功能名均未命中 |
| 15 | 01-跨域交叉点与因果链.md | B-XXX | B-004 | 交易安全 | path和功能名均未命中 |
| 16 | 01-跨域交叉点与因果链.md | B-XXX | B-005 | 交易安全 | path和功能名均未命中 |
| 17 | 01-跨域交叉点与因果链.md | B-XXX | B-006 | 交易安全 | path和功能名均未命中 |
| 18 | 01-跨域交叉点与因果链.md | B-XXX | B-008 | 自迭代安全 | path和功能名均未命中 |
| 19 | 01-跨域交叉点与因果链.md | B-XXX | B-009 | 自迭代安全 | path和功能名均未命中 |
| 20 | 01-跨域交叉点与因果链.md | B-XXX | B-010 | 自迭代安全 | path和功能名均未命中 |
| 21 | 01-跨域交叉点与因果链.md | B-XXX | B-011 | 数据隐私 | path和功能名均未命中 |
| 22 | 01-跨域交叉点与因果链.md | B-XXX | B-012 | 数据隐私 | path和功能名均未命中 |
| 23 | 01-跨域交叉点与因果链.md | B-XXX | B-013 | 数据隐私 | path和功能名均未命中 |
| 24 | 01-跨域交叉点与因果链.md | B-XXX | B-013.5 | 数据隐私 | path和功能名均未命中 |
| 25 | 01-跨域交叉点与因果链.md | B-XXX | B-013.6 | 数据隐私 | path和功能名均未命中 |
| 26 | 01-跨域交叉点与因果链.md | B-XXX | B-014 | 运维安全 | path和功能名均未命中 |
| 27 | 01-跨域交叉点与因果链.md | B-XXX | B-015 | 运维安全 | path和功能名均未命中 |
| 28 | 01-跨域交叉点与因果链.md | B-XXX | B-016 | 运维安全 | path和功能名均未命中 |
| 29 | 01-跨域交叉点与因果链.md | B-XXX | B-017 | 功能边界 | path和功能名均未命中 |
| 30 | 01-跨域交叉点与因果链.md | B-XXX | B-018 | 功能边界 | path和功能名均未命中 |
| 31 | 01-跨域交叉点与因果链.md | B-XXX | B-019 | 功能边界 | path和功能名均未命中 |
| 32 | 01-跨域交叉点与因果链.md | D-XXX-NN | D-DATA-05 | 数据质量监控 | path和功能名均未命中 |
| 33 | 01-跨域交叉点与因果链.md | C-XXX | C-036 | 群体博弈模拟 | path和功能名均未命中 |
| 34 | 01-跨域交叉点与因果链.md | C-XXX | C-040 | 系统性压力测试 | path和功能名均未命中 |
| 35 | 01-跨域交叉点与因果链.md | C-XXX | C-045 | 拥挤度检测 | path和功能名均未命中 |
| 36 | 01-跨域交叉点与因果链.md | C-XXX | C-044 | 成本治理 | path和功能名均未命中 |
| 37 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-RS-02 | BacktestCompleted | path和功能名均未命中 |
| 38 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-RS-03 | ModelValidated | path和功能名均未命中 |
| 39 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-SG-02 | SignalRevoked | path和功能名均未命中 |
| 40 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-SG-03 | SignalExpired | path和功能名均未命中 |
| 41 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-PF-02 | PositionLimitBreached | path和功能名均未命中 |
| 42 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-RK-02 | MarginCalled | path和功能名均未命中 |
| 43 | 01-跨域交叉点与因果链.md | E-XXX-NN | E-RK-03 | DrawdownAlerted | path和功能名均未命中 |
| 44 | 02-D-DATA-数据域.md | E-XXX-NN | E-DT-02 | DataGapDetected / E-DT-03 DataSchemaChanged | path和功能名均未命中 |
| 45 | 02-D-DATA-数据域.md | E-XXX-NN | E-DT-03 | DataSchemaChanged | path和功能名均未命中 |
| 46 | 03-D_FACTOR-因子域.md | DD-XXX-NN | DD-P3-02 | 因子IC入池阈值分级 | path和功能名均未命中 |
| 47 | 03-D_FACTOR-因子域.md | DD-XXX-NN | DD-P3-03 | 盘中快照仅保留3个月 | path和功能名均未命中 |
| 48 | 04-D-SIGNAL-信号域.md | D-XXX-NN | D-SIGNAL-115 | 策略模板库 | path和功能名均未命中 |
| 49 | 04-D-SIGNAL-信号域.md | D-XXX-NN | D-SIGNAL-154 | 信号去重模块 | path和功能名均未命中 |
| 50 | 04-D-SIGNAL-信号域.md | D-XXX-NN | D-SIGNAL-155 | 信号冲突解决 | path和功能名均未命中 |
| 51 | 05-D_PF_CORE-组合核心域.md | E-XXX-NN | E-CA-04 | / CTR-P1-014 | path和功能名均未命中 |
| 52 | 07-D_POSITION-仓位管理域.md | E-XXX-NN | E-POS-02 | DriftDetected / E-POS-03 RebalanceTriggered / E-PO | path和功能名均未命中 |
| 53 | 07-D_POSITION-仓位管理域.md | E-XXX-NN | E-POS-04 | CapitalCurveUpdated / E-POS-05 StateChanged | path和功能名均未命中 |
| 54 | 08-D_EX_CORE-执行核心域.md | E-XXX-NN | E-EX-08 | IdempotencyBlocked | path和功能名均未命中 |
| 55 | 10-D_REPORTING-报告域.md | L-XXX | L-007 | ；EU AI Act Art.12+MiFID II RTS 6 | path和功能名均未命中 |
| 56 | 11-D_RISK-风控域.md | C-XXX | C-020 | 渐进式全球扩展 | path和功能名均未命中 |
| 57 | 12-D_ML_TRAIN-训练域.md | E-XXX-NN | E-ML-02 | NewFactorDiscovered | path和功能名均未命中 |
| 58 | 12-D_ML_TRAIN-训练域.md | E-XXX-NN | E-ML-03 | RetrainTriggered | path和功能名均未命中 |
| 59 | 13-D_ML_SERVE-推理域.md | E-XXX-NN | E-ML-04 | ModelActivated | path和功能名均未命中 |
| 60 | 13-D_ML_SERVE-推理域.md | E-XXX-NN | E-ML-06 | InferenceDegraded | path和功能名均未命中 |
| 61 | 14-D-ALT-DATA-另类数据域.md | E-XXX-NN | E-AD-02 | AltDataQualityDegraded / E-AD-03 SentimentSignalRe | path和功能名均未命中 |
| 62 | 14-D-ALT-DATA-另类数据域.md | E-XXX-NN | E-AD-04 | FilingEventDetected / E-AD-05 SupplyChainDisruptio | path和功能名均未命中 |
| 63 | 15-D-DATA-ENG-数据工程域.md | E-XXX-NN | E-DE-02 | PipelineFailed / E-DE-03 DataQualityAlert / E-DE-0 | path和功能名均未命中 |
| 64 | 15-D-DATA-ENG-数据工程域.md | E-XXX-NN | E-DE-04 | FeatureStoreUpdated / E-DE-05 LineageGapDetected | path和功能名均未命中 |
| 65 | 15-D-DATA-ENG-数据工程域.md | E-XXX-NN | E-DE-06 | DriftDetected | path和功能名均未命中 |
| 66 | 16-D_CROSS_ASSET-跨资产跨市场域.md | E-XXX-NN | E-CA-02 | CorrelationRegimeShifted / E-CA-03 CrossMarketProp | path和功能名均未命中 |
| 67 | 17-D_COMPLIANCE-合规监管域.md | E-XXX-NN | E-CM-02 | RegulatoryReportGenerated / E-CM-03 ComplianceGate | path和功能名均未命中 |
| 68 | 17-D_COMPLIANCE-合规监管域.md | E-XXX-NN | E-CM-03 | ComplianceGatePassed | path和功能名均未命中 |
| 69 | 17-D_COMPLIANCE-合规监管域.md | L-XXX | L-008 | )，但2025-2026年EU AI Act的实施细则和ESMA监管指引已大幅细化，对AI自治交易系 | path和功能名均未命中 |
| 70 | 18-D_TRADING-交易运营域.md | E-XXX-NN | E-TR-02 | ReconciliationCompleted / E-TR-03 CorporateActionA | path和功能名均未命中 |
| 71 | 18-D_TRADING-交易运营域.md | E-XXX-NN | E-TR-03 | CorporateActionAdjusted / E-TR-04 MarginWarning / | path和功能名均未命中 |
| 72 | 18-D_TRADING-交易运营域.md | E-XXX-NN | E-TR-04 | MarginWarning / E-TR-05 MarginUnavailable / E-TR-0 | path和功能名均未命中 |
| 73 | 18-D_TRADING-交易运营域.md | E-XXX-NN | E-TR-05 | MarginUnavailable / E-TR-06 MultiAccountAllocated | path和功能名均未命中 |
| 74 | 18-D_TRADING-交易运营域.md | E-XXX-NN | E-TR-06 | MultiAccountAllocated | path和功能名均未命中 |
| 75 | 20-D-RESEARCH-研究基础设施域.md | E-XXX-NN | E-RH-02 | ExperimentReproduced | path和功能名均未命中 |
| 76 | 20-D-RESEARCH-研究基础设施域.md | D-XXX-NN | D-RESEARCH-09 | 合规审计 | path和功能名均未命中 |
| 77 | 23-D-AUT-PERM-自治保护域.md | D-XXX-NN | D-SECURITY-03 | 密钥管理器 | path和功能名均未命中 |
| 78 | 23-D-AUT-PERM-自治保护域.md | E-XXX-NN | E-AP-02 | TradingSessionSwitch | path和功能名均未命中 |
| 79 | 23-D-AUT-PERM-自治保护域.md | E-XXX-NN | E-AP-04 | PERMBudgetExemptionUsed | path和功能名均未命中 |
| 80 | 23-D-AUT-PERM-自治保护域.md | E-XXX-NN | E-AP-06 | DependencyUpgradeCompleted | path和功能名均未命中 |
| 81 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-02 | CapacityThresholdBreached | path和功能名均未命中 |
| 82 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-06 | E | path和功能名均未命中 |
| 83 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-03 | ProcessHeartbeatLost | path和功能名均未命中 |
| 84 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-04 | GPUOOMDetected | path和功能名均未命中 |
| 85 | 24-D-INFRA-RUNTIME-运行时基础设施域.md | E-XXX-NN | E-IF-05 | ConfigChanged | path和功能名均未命中 |
| 86 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-02 | VulnerabilityDetected / E-SC-03 UnauthorizedAccess | path和功能名均未命中 |
| 87 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-03 | UnauthorizedAccess | path和功能名均未命中 |
| 88 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-04 | ThreatAlert | path和功能名均未命中 |
| 89 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-05 | EncryptionKeyRotated | path和功能名均未命中 |
| 90 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-07 | AISGBlocked | path和功能名均未命中 |
| 91 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-08 | CollusionDetected | path和功能名均未命中 |
| 92 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-09 | IntegrityViolation | path和功能名均未命中 |
| 93 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-SC-10 | SandboxEscaped | path和功能名均未命中 |
| 94 | 24-D_SECURITY-安全域.md | E-XXX-NN | E-AUT-02 | PermissionChanged | path和功能名均未命中 |
| 95 | 25-D-INFRA-OPS-运维基础设施域.md | D-XXX-NN | D-INFRA-446 | 技术债务追踪 | path和功能名均未命中 |
| 96 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-04 | AlertFired | path和功能名均未命中 |
| 97 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-01 | BackupCompleted | path和功能名均未命中 |
| 98 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-02 | BackupFailed | path和功能名均未命中 |
| 99 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-03 | DeploymentStageAdvanced | path和功能名均未命中 |
| 100 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-05 | AlertEscalated | path和功能名均未命中 |
| 101 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-06 | DRDrillCompleted | path和功能名均未命中 |
| 102 | 25-D-INFRA-OPS-运维基础设施域.md | E-XXX-NN | E-IO-07 | LogAnomalyDetected | path和功能名均未命中 |
| 103 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-02 | ContractViolated / E-INT-03 SchemaVersionChanged / | path和功能名均未命中 |
| 104 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-03 | SchemaVersionChanged / E-INT-04 EventRoutingFailed | path和功能名均未命中 |
| 105 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-04 | EventRoutingFailed | path和功能名均未命中 |
| 106 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-05 | ContractFrozen | path和功能名均未命中 |
| 107 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-06 | IdempotencyKeyMissing | path和功能名均未命中 |
| 108 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-07 | APIGatewayRequestRouted | path和功能名均未命中 |
| 109 | 25-D_INTEGRATION-集成域.md | E-XXX-NN | E-INT-08 | SchemaValidationFailed | path和功能名均未命中 |
| 110 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-04 | AuditAnomalyDetected | path和功能名均未命中 |
| 111 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-05 | DDDViolationDetected | path和功能名均未命中 |
| 112 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-06 | DecisionArchived | path和功能名均未命中 |
| 113 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-07 | ComplianceAuditCompleted | path和功能名均未命中 |
| 114 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-08 | IncidentEscalated | path和功能名均未命中 |
| 115 | 27-D_GOVERNANCE-治理域.md | E-XXX-NN | E-GV-09 | TopologyDriftDetected | path和功能名均未命中 |
| 116 | 28-D_FRONTEND-前端域.md | E-XXX-NN | E-AU-05 | HealthDegraded | path和功能名均未命中 |
| 117 | 30-D_OPS-运维域.md | E-XXX-NN | E-OP-04 | RemediationExecuted | path和功能名均未命中 |
| 118 | 30-D_OPS-运维域.md | E-XXX-NN | E-OP-06 | SLOBreached | path和功能名均未命中 |
| 119 | 30-D_OPS-运维域.md | E-XXX-NN | E-OP-07 | SurvivalRuleTriggered | path和功能名均未命中 |
| 120 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-02 | SellArbitrated / E-SELL-03 SellExecuted / E-SELL-0 | path和功能名均未命中 |
| 121 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-04 | SellLoopFeedback | path和功能名均未命中 |
| 122 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-001 |  | path和功能名均未命中 |
| 123 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-002 |  | path和功能名均未命中 |
| 124 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-003 |  | path和功能名均未命中 |
| 125 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-004 |  | path和功能名均未命中 |
| 126 | 31-D_SELL_DECISION-卖出决策域.md | E-XXX-NN | E-SELL-005 |  | path和功能名均未命中 |
| 127 | 交易决策架构.md | C-XXX | C-041 | )                       │   ║ | path和功能名均未命中 |
| 128 | 交易决策架构.md | L-XXX | L-002 | B-017 不做HFT | path和功能名均未命中 |
| 129 | 交易决策架构.md | L-XXX | L-003 | B-004 非交易时段禁下单 | path和功能名均未命中 |
| 130 | 交易决策架构.md | L-XXX | L-004 | B-011 数据不外传 | path和功能名均未命中 |
| 131 | 交易决策架构.md | L-XXX | L-005 | B-013 版权合规 | path和功能名均未命中 |
| 132 | 交易决策架构.md | L-XXX | L-006 | AI生成策略合规 | path和功能名均未命中 |
| 133 | 数据架构.md | DD-XXX-NN | DD-P1-02 | L0不持久化原始推送 | path和功能名均未命中 |
| 134 | 数据架构.md | DD-XXX-NN | DD-P1-03 | Tick仅保留近3个月 | path和功能名均未命中 |
| 135 | 数据架构.md | DD-XXX-NN | DD-P4-02 | 跨源对账仅覆盖收盘价和成交量 | path和功能名均未命中 |
| 136 | 数据架构.md | DD-XXX-NN | DD-P4-03 | 质量检查自建而非Great Expectations | path和功能名均未命中 |
| 137 | 数据架构.md | DD-XXX-NN | DD-P5-02 | miniQMT+iFind双源互补 | path和功能名均未命中 |
| 138 | 数据架构.md | DD-XXX-NN | DD-P5-03 | tushare待开通而非立即接入 | path和功能名均未命中 |
| 139 | 数据架构.md | E-XXX-NN | E-FS-02 | FeatureValidated | path和功能名均未命中 |
| 140 | 数据架构.md | E-XXX-NN | E-FS-03 | FeatureRegistered | path和功能名均未命中 |
| 141 | 数据架构.md | E-XXX-NN | E-FS-04 | FeatureOnline | path和功能名均未命中 |
| 142 | 数据架构.md | E-XXX-NN | E-FS-05 | FeatureDecaying | path和功能名均未命中 |
| 143 | 数据架构.md | E-XXX-NN | E-FS-06 | FeatureDeprecated | path和功能名均未命中 |
| 144 | 数据架构.md | E-XXX-NN | E-FS-07 | FeatureDormant | path和功能名均未命中 |
| 145 | 数据架构.md | E-XXX-NN | E-FS-08 | FeatureReactivated | path和功能名均未命中 |
| 146 | 数据架构.md | E-XXX-NN | E-FS-09 | FeatureRetired | path和功能名均未命中 |
| 147 | 治理架构.md | GATE-XX-NN | GATE-FUT-01 | 期货账户已开通并完成程序化交易报告（通过中国期货市场监控中心报告系统） | path和功能名均未命中 |
| 148 | 治理架构.md | GATE-XX-NN | GATE-FUT-02 | §16.1监管合规映射已补充期货14项要求（报告管理/系统接入/主机托管/交易监测/风险管理/监督管 | path和功能名均未命中 |
| 149 | 治理架构.md | GATE-XX-NN | GATE-FUT-03 | 期货风控参数已硬编码（HB-GOV-08 Kill Switch覆盖期货层：保证金率/持仓限额/涨跌 | path和功能名均未命中 |
| 150 | 治理架构.md | GATE-XX-NN | GATE-FUT-04 | 变更审批流已覆盖期货策略上线（L3+审批，期货策略属human_gated） | path和功能名均未命中 |
| 151 | 治理架构.md | GATE-XX-NN | GATE-HK-01 | 港股通交易权限已开通 | path和功能名均未命中 |
| 152 | 治理架构.md | GATE-XX-NN | GATE-HK-02 | 已通过券商完成沪深股通程序化交易报告 | path和功能名均未命中 |
| 153 | 治理架构.md | GATE-XX-NN | GATE-HK-03 | §16.1监管合规映射已补充股通5项要求（报告路径/变更报告/穿透核查/内外资一致/责任追究） | path和功能名均未命中 |
| 154 | 治理架构.md | GATE-XX-NN | GATE-HK-04 | 港股交易时段限制已加入HB-GOV-04（港股9:30-16:00与A股不同） | path和功能名均未命中 |
| 155 | 治理架构.md | GATE-XX-NN | GATE-FPGA-01 | AUM≥5000万且策略包含日内高频交易 | path和功能名均未命中 |
| 156 | 治理架构.md | GATE-XX-NN | GATE-FPGA-02 | 共享内存方案实测延迟>1ms，无法满足交易需求 | path和功能名均未命中 |
| 157 | 治理架构.md | GATE-XX-NN | GATE-FPGA-03 | 有FPGA开发能力或外包预算 | path和功能名均未命中 |
| 158 | 治理架构.md | GATE-XX-NN | GATE-FCFT-01 | 系统使用自托管LLM（非API调用），具备微调能力 | path和功能名均未命中 |
| 159 | 治理架构.md | GATE-XX-NN | GATE-FCFT-02 | GPU算力可用（≥1张A100或等效） | path和功能名均未命中 |
| 160 | 治理架构.md | GATE-XX-NN | GATE-FCFT-03 | 金融安全标注数据集已构建（≥1000条金融违规/合规样本） | path和功能名均未命中 |
| 161 | 治理架构.md | GATE-XX-NN | GATE-FCFT-04 | FCFT微调后模型通过FinJailbreak基准测试（漏洞减少≥40%） | path和功能名均未命中 |
| 162 | 治理架构.md | GATE-XX-NN | GATE-GA-01 | A7多Agent架构激活（多Agent通信通道建立，存在Agent间交互需独立监控） | path和功能名均未命中 |
| 163 | 治理架构.md | GATE-XX-NN | GATE-GA-02 | 现有检查器+脚本模式实测发现Agent间交互监控盲区（被动触发无法覆盖主动规避行为） | path和功能名均未命中 |
| 164 | 治理架构.md | GATE-XX-NN | GATE-GA-03 | 待守护Agent独立运行环境就绪（独立沙箱+独立Hard-Gate接口+独立审计通道） | path和功能名均未命中 |
| 165 | 治理架构.md | GATE-XX-NN | GATE-SZP-01 | 系统升级至日内高频交易（决策频率≤1分钟，需轨迹级实时监控） | path和功能名均未命中 |
| 166 | 治理架构.md | GATE-XX-NN | GATE-SZP-02 | 多Agent工作流激活（需跨Agent能力分解与权限编排） | path和功能名均未命中 |
| 167 | 治理架构.md | GATE-XX-NN | GATE-SZP-03 | §3.2行为检测层实测发现轨迹级漂移盲区（现有决策路径偏离检测覆盖率<80%） | path和功能名均未命中 |
| 168 | 治理架构.md | GATE-XX-NN | GATE-TRUST-01 | A7多Agent架构激活（多Agent通信通道建立，Agent间信任利用攻击面产生） | path和功能名均未命中 |
| 169 | 治理架构.md | GATE-XX-NN | GATE-TRUST-02 | Agent间通信协议已定义（A2A/MCP协议，由A7 Agent架构定义） | path和功能名均未命中 |
| 170 | 治理架构.md | GATE-XX-NN | GATE-TRUST-03 | Meta-Governance架构设计完成（独立治理Agent监控运营Agent舰队，SafeAli | path和功能名均未命中 |
| 171 | ZephyrAlpha全系统模块清单.md | C-XXX | C-037 | 审计系统 | path和功能名均未命中 |
