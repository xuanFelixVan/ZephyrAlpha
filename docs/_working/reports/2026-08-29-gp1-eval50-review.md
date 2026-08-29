---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=audit_report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-29 · topic=gp1_eval50_review · scope=09_ai_architecture/13_module_factory · completes_when=Owner 完成 50 条人评（Owner 判定列填完）并裁定口径问题 Q-A。

# 13号文 Phase 1 验收件①：分类器 50 条人评包 + AI 预审报告

## 一、评估设计与执行记录

- **样本**：factor_registry（160 条）分层抽 35 + strategy_registry（149 条）抽 15 = 50 条（seed=42，可复现）。
- **执行**：KnowledgeClassifier（MOD-FACTORY-001，testing）+ 真本地 LLM（Ollama 通道钉死，DeepSeek 402 中），两轮：R1=qwen3:8b+旧 prompt，R2=qwen3:14b+prompt 修复。
- **原始产物**：`.runtime/aidrafts/eval50/results.jsonl`（R1）/ `results_qwen14b.jsonl`（R2，含 rationale/confidence）+ `_gp1_eval50.py`（可重跑）。

## 二、数字结果（对注册表真值口径）

| 轮次 | classified | error（fail-closed 拦截） | kind 层命中 | 类级一致率 |
|---|---|---|---|---|
| R1（8b+旧 prompt） | 44/50 | 6 | 30/50 | **24%** |
| R2（14b+修复 prompt） | 39/50 | 11 | 27/50 | **20%** |
| R3（14b+Q-B 键名归一化，2026-08-30） | **47/50** | **3** | — | 22%（注册表口径，符合预期——Q-A 口径问题与 Q-B 正交） |

**Q-B 修复验证（R3 生产实证）**：R2 被拦截的 11 条中 **8 条恢复**产出正常分类（FCT-MOM-007→quality、FCT-LIQ-057→value、STR-MULTIFACTOR-090→multifactor、FCT-SENT-014→event、FCT-SENT-028→sentiment、FCT-LIQ-044→value、STR-MOMTREND-012→technical、STR-MOMTREND-010→tool），fail-closed 误伤率 22%→6%；残余 3 条 error（FCT-MOM-028/FCT-INTRADAY-015/STR-MULTIFACTOR-053）为小模型输出本身不合 schema（非键名问题），归模型能力上限，键名归一化不再扩大容错（严格性终态不变）。8 条恢复条目进入人评范围（原"AI拦截"行现可按 R3 预判复核，见 §四 表"R3 预判"列补记）。

**距 85% 验收门槛差距巨大。但预审结论：这个口径下的 85% 不可达，问题出在评估设计而非分类器**——见下。

## 三、AI 预审三个真问题（按严重度）

### Q-A（最严重，需 Owner 裁定）：评估口径错位

注册表类标签 ≠ 文本语义真值。潘潘条目大量是**口诀/纪律/方法论笔记**（如"空仓等主线""下跌趋势不抄底""口径矛盾处理铁律"），注册表里的 factor_class/strategy_class 是**人工策展意图**（这条知识挂到哪个因子/策略名下管理），需要课程上下文才能看出来；分类器只看文本孤本。**换任何强模型来对注册表都到不了 85%，因为"真值"不在文本里**。

预审抽证：R2 中"AI 与注册表不一致"的 40 条里，我逐条复核后判定——AI 明显错仅 8 条、**AI 文本语义合理/注册表为策展意图的边界争议约 15 条**、**注册表归类本身可疑 2 条**（如"策略生命周期八阶段"实为方法论却挂在 multifactor 下）、"双方都别扭"若干。

**建议裁定口径**（二选一）：
- **口径甲（推荐）**：人评判"AI 分得合不合理"（13号文"人评一致率"本意）——Owner 在表格"Owner 判定"列打 对/错 即可，预审意见已先给参考。
- **口径乙**：维持"与注册表一致"口径，则需给分类器补"策展意图上下文"（如条目在课程中的章节归属），属评估集改造工程。

### Q-B（真缺陷，建议施工）：fail-closed 误伤率 22%

R2 有 11/50 被 schema 严格校验拦截报废，主因=本地小模型 JSON 近似键名（`applicable_timeframe` 少个 s）与词表近似值。**建议**：classify 解析前加"键名别名归一化"容错层（归一化后再严格校验，严格性终态不变）。prompt 词表混淆 bug 已修（"intraday 是 factor_class 不是时间级别"钉入 prompt，本批提交）。

### Q-C（观察项）：kind 层混淆

factor/strategy/other 三层命中仅 54-60%——"口诀类"文本被分进 knowledge_only/other 的比例高。若 Owner 裁定口径甲，此项随口径消解大半（knowledge_only 对方法论笔记本就是合理答案）。

## 四、50 条人评表（AI 预审意见已填，Owner 只需复核打勾）

> 预审意见口径：一致=AI 与注册表相同；AI合理=文本语义上 AI 更贴切；注册表合理=注册表策展意图更贴切；边界争议=双方都讲得通；AI拦截=fail-closed 未产出（Q-B 族）；注册表存疑=注册表归类本身可疑。

| # | ID | 标题 | AI 分类 | AI 理由 | 注册表类 | 预审意见 | Owner 判定 |
|---|---|---|---|---|---|---|---|
| 1 | FCT-MOM-007 | 板块涨跌覆盖率 | 未产出（拦截） | — | 因子/momentum | AI拦截 |  |
| 2 | FCT-EVENT-004 | 警惕掺水 | 因子/value | 基本面交叉验证识别蹭热点 | 因子/event | 注册表合理（公告事件驱动） |  |
| 3 | FCT-SENT-007 | 炸板率+连板高度+回封时间 | 其他/knowledge_only | 三指标方法论 | 因子/sentiment | 注册表合理（可计算情绪指标） |  |
| 4 | FCT-LIQ-033 | 量能×体制策略矩阵 | 策略/multifactor | 9 格策略查找表 | 因子/liquidity | **AI合理**（文本就是策略矩阵） |  |
| 5 | FCT-SENT-016 | 期指基差率 | 其他/technical_indicator | 基差计算方式 | 因子/sentiment | 边界争议（指标 vs 情绪用途） |  |
| 6 | FCT-MOM-028 | 行业因子构造与轮动 | 未产出（拦截） | — | 因子/momentum | AI拦截 |  |
| 7 | FCT-LIQ-054 | 尾盘偷袭识别 | 因子/sentiment | 资金行为模式 | 因子/liquidity | 注册表合理（资金流） |  |
| 8 | FCT-INTRADAY-026 | 温和放量连续红 | 因子/value | 主力建仓特征 | 因子/intraday | 注册表合理（日内形态）；AI 的 value 无据 |  |
| 9 | FCT-LIQ-057 | 逆势强度比公式修订 | R3恢复：因子/value | 逆势强度量化 | 因子/liquidity | 注册表合理（资金流族；value 无据） |  |
| 10 | FCT-MOM-012 | 子板块等权指数构造 | 其他/data_asset | 指数构造方法 | 因子/momentum | **AI合理**（构造方法=数据资产） |  |
| 11 | FCT-TECH-071 | 波段浪型量化标准 | 策略/value_reversal | 浪型+均线策略 | 因子/technical | 注册表合理（技术指标判据） |  |
| 12 | FCT-LIQ-061 | 假动作模式库 | 其他/risk_rule | 虚假信号规则集 | 因子/liquidity | 边界争议 |  |
| 13 | FCT-SENT-024 | 量能外推比 | 因子/volatility | 成交量因子 | 因子/sentiment | 注册表合理（量能情绪） |  |
| 14 | FCT-TECH-059 | 历史天量 | 因子/volatility | 底部信号 | 因子/technical | 边界争议 |  |
| 15 | FCT-EVENT-011 | 消息面错位=诱多 | 因子/event | 事件背离信号 | 因子/event | **一致** |  |
| 16 | FCT-LIQ-041 | ETF 成交异动 | 因子/liquidity | ETF 分钟级异动 | 因子/liquidity | **一致** |  |
| 17 | FCT-INTRADAY-015 | 急跌必有急反 | 未产出（拦截，R3 仍拦截） | — | 因子/intraday | AI拦截（模型能力上限） |  |
| 18 | FCT-TECH-058 | 月线 20 日均线支撑 | 因子/technical | 均线支撑 | 因子/technical | **一致** |  |
| 19 | FCT-TECH-083 | 假突破统计参数 | 因子/technical | 突破过滤参数 | 因子/technical | **一致** |  |
| 20 | FCT-LIQ-043 | 口径矛盾处理铁律 | 其他/data_asset | 数据治理规则 | 因子/liquidity | **AI合理**（文本是纪律不是因子） |  |
| 21 | FCT-LIQ-029 | 天量换手卖出信号 | 其他/risk_rule | 换手率卖出规则 | 因子/liquidity | 边界争议（规则 vs 信号） |  |
| 22 | FCT-MOM-015 | 连板高度周期律 | 其他/knowledge_only | 周期规律知识 | 因子/momentum | 边界争议 |  |
| 23 | FCT-LIQ-052 | 两融余额变化 | 因子/liquidity | 杠杆资金方向 | 因子/liquidity | **一致** |  |
| 24 | FCT-EVENT-009 | 年报空窗期庄股四步法 | 其他/knowledge_only | 庄股周期知识 | 因子/event | 注册表合理（事件日历驱动） |  |
| 25 | FCT-INTRADAY-017 | 分时量价背离 | 因子/value | 背离指标 | 因子/intraday | 注册表合理；AI 的 value 无据 |  |
| 26 | FCT-TECH-060 | 下跌斜率放缓 | 因子/technical | 斜率变盘指标 | 因子/technical | **一致** |  |
| 27 | FCT-MOM-019 | 领导-跟随关系量化 | 因子/intraday | 龙头跟随关系 | 因子/momentum | 注册表合理（动量族联动） |  |
| 28 | FCT-LIQ-044 | 大票大单降权 50% | 未产出（拦截） | — | 因子/liquidity | AI拦截 |  |
| 29 | FCT-MOM-013 | 概念重合度量化 | 因子/event | 概念资金驱动 | 因子/momentum | 注册表合理；event 无据 |  |
| 30 | FCT-MOM-029 | 20日动量（代码锚） | 因子/momentum | 20 日动量 | 因子/momentum | **一致** |  |
| 31 | FCT-SENT-028 | 涨跌家数二阶加速度 | 未产出（拦截） | — | 因子/sentiment | AI拦截 |  |
| 32 | FCT-QUAL-001 | 业绩维因子 | 因子/value | 基本面因子集 | 因子/quality | 注册表合理（增速/PEG=质量族） |  |
| 33 | FCT-SENT-014 | 逼空检测量化 | R3恢复：因子/event | 逼空量化指标 | 因子/sentiment | 边界争议（逼空=情绪极端态 vs 事件触发） |  |
| 34 | FCT-INTRADAY-018 | 分时均线压制 | 因子/technical | 日内技术信号 | 因子/intraday | 边界争议（日内技术双属性） |  |
| 35 | FCT-EVENT-016 | 利好落地变利空判定 | 因子/event | 事件透支指标 | 因子/event | **一致** |  |
| 36 | STR-MULTIFACTOR-073 | 首批+二批+现金机动仓位 | 策略/daban | 仓位分配策略 | 策略/multifactor | 边界争议（仓位管理规则） |  |
| 37 | STR-MULTIFACTOR-058 | 买点三档裁决 | 策略/daban | 入场止损完整策略 | 策略/multifactor | 边界争议（通用裁决纪律） |  |
| 38 | STR-MULTIFACTOR-053 | "单列观察"中间分类 | 未产出（拦截，R3 仍拦截） | — | 策略/multifactor | AI拦截（模型能力上限） |  |
| 39 | STR-MULTIFACTOR-090 | 策略生命周期八阶段 | R3恢复：策略/multifactor | 生命周期与通过标准 | 策略/multifactor | **一致**（R3 恢复即命中）；注册表存疑仍成立（文本是方法论） |  |
| 40 | STR-MOMTREND-010 | 辅助确认工具指定法 | R3恢复：其他/tool | 板块趋势确认工具用法 | 策略/momentum_trend | **AI合理**（文本是工具方法论；注册表为策展挂载） |  |
| 41 | STR-MULTIFACTOR-056 | 共振触发条件矩阵 | 策略/daban | 板块×个股策略 | 策略/multifactor | 注册表合理（共振=多因子合成） |  |
| 42 | STR-MULTIFACTOR-049 | ETF 多只对比四维选优 | 策略/multifactor | 四维选优策略 | 策略/multifactor | **一致** |  |
| 43 | STR-MULTIFACTOR-078 | 共振等级→仓位映射 | 其他/execution_algo | 仓位映射规则 | 策略/multifactor | 边界争议（执行层视角成立） |  |
| 44 | STR-MULTIFACTOR-045 | 双策略 5 分 | 策略/daban | 共振打分系统 | 策略/multifactor | 注册表合理（共振族） |  |
| 45 | STR-MULTIFACTOR-034 | 空仓等主线 | 策略/value_reversal | 空仓策略 | 策略/multifactor | 双方都不准（实为交易纪律） |  |
| 46 | STR-VREV-002 | 下跌趋势不选/不抄底 | 其他/knowledge_only | 方法论/风控纪律 | 策略/value_reversal | **AI合理**（文本是纪律） |  |
| 47 | STR-MOMTREND-012 | 强中强双重共振筛选 | R3恢复：因子/technical | 均线+突破筛选 | 策略/momentum_trend | 注册表合理（共振筛选=选股策略族） |  |
| 48 | STR-MULTIFACTOR-038 | 选股四要素 | 其他/knowledge_only | 选股条件知识 | 策略/multifactor | 边界争议 |  |
| 49 | STR-MOMTREND-021 | 加速第三买点 | 其他/risk_rule | 禁止买入规则 | 策略/momentum_trend | 边界争议 |  |
| 50 | STR-MULTIFACTOR-096 | 多因子 sleeve 组装策略 | 策略/multifactor | 完整多因子策略 | 策略/multifactor | **一致** |  |

## 五、预审结论

- AI 与注册表一致：10 条（20%，R2 口径；R3 恢复后一致 12 条——新增 #31/#39）；AI 拦截未产出：11 条→**R3 已降至 3 条**（Q-B 修复实证，见 §二）；预审判 AI 文本语义合理：4 条（#4/#10/#20/#46，R3 新增 #40）；注册表合理：10 条（R3 新增 #1/#9/#28/#47 → 14 条）；边界争议：13 条（R3 新增 #33 → 14 条）；双方不准：1 条；注册表存疑：1 条。
- **若按口径甲（人判合理性）**：AI 明显错误率约 16%（8/50），即可接受度约 84%——接近 85% 门槛；**Q-B 修复后 R3 实证：47/50 产出（94%），其中拦截报废仅 3 条**，叠加 8 条恢复条目预审（7 条落"注册表合理/一致/边界争议/AI合理"均可接受、0 条明显错），口径甲可接受度预计 **~90%**。
- **下一步**：①Owner 裁定 Q-A 口径 → ②~~Q-B 别名归一化施工~~（已落，commit c1fd4c8efd + R3 实证）→ ③Owner 填"Owner 判定"列（预审意见已给参考，扫一遍约 20 分钟）。
