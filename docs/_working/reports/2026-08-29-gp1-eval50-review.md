---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=audit_report · owner=ZephyrAlpha-Owner · language=zh · status=closed · version=1.1.0 · date=2026-08-30 · topic=gp1_eval50_review · scope=09_ai_architecture/13_module_factory · completes_when=已达成（2026-08-30：Q-A 口径裁定落地 + 50 条判定列填毕，见 §六 裁定书）。

# 13号文 Phase 1 验收件①：分类器 50 条人评包 + AI 预审报告 + 裁定书

## 一、评估设计与执行记录

- **样本**：factor_registry（160 条）分层抽 35 + strategy_registry（149 条）抽 15 = 50 条（seed=42，可复现）。
- **执行**：KnowledgeClassifier（MOD-FACTORY-001，testing）+ 真本地 LLM（Ollama 通道钉死，DeepSeek 402 中），三轮：R1=qwen3:8b+旧 prompt，R2=qwen3:14b+prompt 修复，R3=qwen3:14b+Q-B 键名归一化。
- **原始产物**：`.runtime/aidrafts/eval50/results.jsonl`（R1）/ `results_qwen14b.jsonl`（R2）/ `results_r3.jsonl`（R3，终审判定基准）+ `_gp1_eval50.py`（可重跑）。
- **判定基准**：§四 判定以 R3（现行生产分类器）输出为准；R2→R3 答案变动 16 行（8 条拦截恢复 + 8 条答案改变），变动行在"AI 分类"列标注 R3 值。

## 二、数字结果（对注册表真值口径）

| 轮次 | classified | error（fail-closed 拦截） | kind 层命中 | 类级一致率 |
|---|---|---|---|---|
| R1（8b+旧 prompt） | 44/50 | 6 | 30/50 | **24%** |
| R2（14b+修复 prompt） | 39/50 | 11 | 27/50 | **20%** |
| R3（14b+Q-B 键名归一化，2026-08-30） | **47/50** | **3** | — | 22%（注册表口径，符合预期——Q-A 口径问题与 Q-B 正交） |

**Q-B 修复验证（R3 生产实证）**：R2 被拦截的 11 条中 **8 条恢复**产出正常分类（FCT-MOM-007→quality、FCT-LIQ-057→value、STR-MULTIFACTOR-090→multifactor、FCT-SENT-014→event、FCT-SENT-028→sentiment、FCT-LIQ-044→value、STR-MOMTREND-012→technical、STR-MOMTREND-010→tool），fail-closed 误伤率 22%→6%；残余 3 条 error（FCT-MOM-028/FCT-INTRADAY-015/STR-MULTIFACTOR-053）为小模型输出本身不合 schema（非键名问题），归模型能力上限，键名归一化不再扩大容错（严格性终态不变）。

**R2→R3 变动全清单（16 行）**：8 条拦截恢复（见上）+ 8 条答案改变：#2 value→quality、#3 knowledge_only→technical_indicator、#20 data_asset→risk_rule（更贴切）、#22 knowledge_only→factor/sentiment（kind 升级）、#24 knowledge_only→strategy/event_driven（更贴切）、#26 technical→momentum（**退化**，原一致被打破）、#29 event→quality、#46 knowledge_only→strategy/momentum_trend（kind 对齐）。

**距 85% 验收门槛差距巨大。但预审结论：这个口径下的 85% 不可达，问题出在评估设计而非分类器**——裁定见 §六。

## 三、AI 预审三个真问题（按严重度）

### Q-A（最严重）：评估口径错位——已裁定（§六 裁定一）

注册表类标签 ≠ 文本语义真值。潘潘条目大量是**口诀/纪律/方法论笔记**（如"空仓等主线""下跌趋势不抄底""口径矛盾处理铁律"），注册表里的 factor_class/strategy_class 是**人工策展意图**（这条知识挂到哪个因子/策略名下管理），需要课程上下文才能看出来；分类器只看文本孤本。**换任何强模型来对注册表都到不了 85%，因为"真值"不在文本里**。

预审抽证：R2 中"AI 与注册表不一致"的 40 条里，逐条复核后判定——AI 明显错仅 8 条、**AI 文本语义合理/注册表为策展意图的边界争议约 15 条**、**注册表归类本身可疑 2 条**（#39"策略生命周期八阶段"实为方法论却挂在 multifactor 下、#45"空仓等主线"实为交易纪律挂 multifactor）、"双方都别扭"若干。

### Q-B（真缺陷）：fail-closed 误伤率 22%——已修复并生产实证（§二 R3）

R2 有 11/50 被 schema 严格校验拦截报废，主因=本地小模型 JSON 近似键名（`applicable_timeframe` 少个 s）与词表近似值。**已施工**：classify 解析前加"键名别名归一化"容错层（归一化后再严格校验，严格性终态不变，commit c1fd4c8efd）+ prompt 词表混淆修复。R3 实证拦截 11→3。

### Q-C（观察项）：kind 层混淆——随裁定一消解大半，残余并入达标路径①

factor/strategy/other 三层命中仅 54-60%——"口诀类"文本被分进 knowledge_only/other 的比例高。口径甲成立后此项消解大半（knowledge_only 对方法论笔记本就是合理答案）；残余 kind 错配（如可计算指标误分流 other）随 §六 裁定四路径①（策展上下文补全）一并复测验证。

## 四、50 条终审表（2026-08-30 架构师代裁终版，Owner 授权见 §六）

> 预审意见口径：一致=AI 与注册表相同；AI合理=文本语义上 AI 更贴切；注册表合理=注册表策展意图更贴切；边界争议=双方都讲得通；AI拦截=fail-closed 未产出（Q-B 族）；注册表存疑=注册表归类本身可疑。
> **判定口径（裁定二）**：对=人审原样接受该草稿（一致/AI合理/边界争议）；错=人审须改（注册表明显更贴切/双方不准）或无草稿（拦截）。AI 分类列=R3 现行输出。

| # | ID | 标题 | AI 分类 | AI 理由 | 注册表类 | 预审意见 | Owner 判定 |
|---|---|---|---|---|---|---|---|
| 1 | FCT-MOM-007 | 板块涨跌覆盖率 | 因子/quality（R3 恢复） | 板块强度衡量 | 因子/momentum | 注册表合理（宽度口径属动量族；quality 无据） | 错 |
| 2 | FCT-EVENT-004 | 警惕掺水 | 因子/quality（R3；R2=value） | 基本面交叉验证识别蹭热点 | 因子/event | 注册表合理（公告事件驱动） | 错 |
| 3 | FCT-SENT-007 | 炸板率+连板高度+回封时间 | 其他/technical_indicator（R3；R2=knowledge_only） | 三指标方法论 | 因子/sentiment | 注册表合理（可计算情绪指标，kind 错配） | 错 |
| 4 | FCT-LIQ-033 | 量能×体制策略矩阵 | 策略/multifactor | 9 格策略查找表 | 因子/liquidity | **AI合理**（文本就是策略矩阵） | 对 |
| 5 | FCT-SENT-016 | 期指基差率 | 其他/technical_indicator | 基差计算方式 | 因子/sentiment | 边界争议（指标 vs 情绪用途） | 对 |
| 6 | FCT-MOM-028 | 行业因子构造与轮动 | 未产出（拦截，R3 仍拦截） | — | 因子/momentum | AI拦截（模型能力上限） | 错 |
| 7 | FCT-LIQ-054 | 尾盘偷袭识别 | 因子/sentiment | 资金行为模式 | 因子/liquidity | 注册表合理（资金流） | 错 |
| 8 | FCT-INTRADAY-026 | 温和放量连续红 | 因子/value | 主力建仓特征 | 因子/intraday | 注册表合理（日内形态）；AI 的 value 无据 | 错 |
| 9 | FCT-LIQ-057 | 逆势强度比公式修订 | 因子/value（R3 恢复） | 逆势强度量化 | 因子/liquidity | 注册表合理（资金流族；value 无据） | 错 |
| 10 | FCT-MOM-012 | 子板块等权指数构造 | 其他/data_asset | 指数构造方法 | 因子/momentum | **AI合理**（构造方法=数据资产） | 对 |
| 11 | FCT-TECH-071 | 波段浪型量化标准 | 策略/value_reversal | 浪型+均线策略 | 因子/technical | 注册表合理（技术指标判据） | 错 |
| 12 | FCT-LIQ-061 | 假动作模式库 | 其他/risk_rule | 虚假信号规则集 | 因子/liquidity | 边界争议 | 对 |
| 13 | FCT-SENT-024 | 量能外推比 | 因子/volatility | 成交量因子 | 因子/sentiment | 注册表合理（量能情绪） | 错 |
| 14 | FCT-TECH-059 | 历史天量 | 因子/volatility | 底部信号 | 因子/technical | 边界争议 | 对 |
| 15 | FCT-EVENT-011 | 消息面错位=诱多 | 因子/event | 事件背离信号 | 因子/event | **一致** | 对 |
| 16 | FCT-LIQ-041 | ETF 成交异动 | 因子/liquidity | ETF 分钟级异动 | 因子/liquidity | **一致** | 对 |
| 17 | FCT-INTRADAY-015 | 急跌必有急反 | 未产出（拦截，R3 仍拦截） | — | 因子/intraday | AI拦截（模型能力上限） | 错 |
| 18 | FCT-TECH-058 | 月线 20 日均线支撑 | 因子/technical | 均线支撑 | 因子/technical | **一致** | 对 |
| 19 | FCT-TECH-083 | 假突破统计参数 | 因子/technical | 突破过滤参数 | 因子/technical | **一致** | 对 |
| 20 | FCT-LIQ-043 | 口径矛盾处理铁律 | 其他/risk_rule（R3；R2=data_asset） | 数据治理纪律规则 | 因子/liquidity | **AI合理**（文本是纪律不是因子；R3=risk_rule 尤贴切） | 对 |
| 21 | FCT-LIQ-029 | 天量换手卖出信号 | 其他/risk_rule | 换手率卖出规则 | 因子/liquidity | 边界争议（规则 vs 信号） | 对 |
| 22 | FCT-MOM-015 | 连板高度周期律 | 因子/sentiment（R3；R2=knowledge_only） | 连板高度与情绪周期关系 | 因子/momentum | 边界争议（R3 升级 factor/sentiment 亦通） | 对 |
| 23 | FCT-LIQ-052 | 两融余额变化 | 因子/liquidity | 杠杆资金方向 | 因子/liquidity | **一致** | 对 |
| 24 | FCT-EVENT-009 | 年报空窗期庄股四步法 | 策略/event_driven（R3；R2=knowledge_only） | 空窗期庄股操作四步法 | 因子/event | **AI合理**（R3：文本是事件驱动策略手法，非因子） | 对 |
| 25 | FCT-INTRADAY-017 | 分时量价背离 | 因子/value | 背离指标 | 因子/intraday | 注册表合理；AI 的 value 无据 | 错 |
| 26 | FCT-TECH-060 | 下跌斜率放缓 | 因子/momentum（R3；R2=technical，**退化**） | 斜率放缓作动量识别 | 因子/technical | 注册表合理（技术形态判据；R3 退化留痕） | 错 |
| 27 | FCT-MOM-019 | 领导-跟随关系量化 | 因子/intraday | 龙头跟随关系 | 因子/momentum | 注册表合理（动量族联动） | 错 |
| 28 | FCT-LIQ-044 | 大票大单降权 50% | 因子/value（R3 恢复） | 大单降权治理 | 因子/liquidity | 注册表合理（流动性治理；value 无据） | 错 |
| 29 | FCT-MOM-013 | 概念重合度量化 | 因子/quality（R3；R2=event） | 概念资金驱动 | 因子/momentum | 注册表合理；quality/event 均无据 | 错 |
| 30 | FCT-MOM-029 | 20日动量（代码锚） | 因子/momentum | 20 日动量 | 因子/momentum | **一致** | 对 |
| 31 | FCT-SENT-028 | 涨跌家数二阶加速度 | 因子/sentiment（R3 恢复） | 市场宽度情绪拐点 | 因子/sentiment | **一致**（R3 恢复即命中） | 对 |
| 32 | FCT-QUAL-001 | 业绩维因子 | 因子/value | 基本面因子集 | 因子/quality | 注册表合理（增速/PEG=质量族） | 错 |
| 33 | FCT-SENT-014 | 逼空检测量化 | 因子/event（R3 恢复） | 逼空量化指标 | 因子/sentiment | 边界争议（逼空=情绪极端态 vs 事件触发） | 错†（标准：无明确事件源的情绪极端→sentiment） |
| 34 | FCT-INTRADAY-018 | 分时均线压制 | 因子/technical | 日内技术信号 | 因子/intraday | 边界争议（日内技术双属性） | 对 |
| 35 | FCT-EVENT-016 | 利好落地变利空判定 | 因子/event | 事件透支指标 | 因子/event | **一致** | 对 |
| 36 | STR-MULTIFACTOR-073 | 首批+二批+现金机动仓位 | 策略/daban | 仓位分配策略 | 策略/multifactor | 边界争议（仓位管理规则） | 对 |
| 37 | STR-MULTIFACTOR-058 | 买点三档裁决 | 策略/daban | 入场止损完整策略 | 策略/multifactor | 边界争议（通用裁决纪律） | 错†（标准：通用裁决纪律非打板专属，AI daban 无据） |
| 38 | STR-MULTIFACTOR-053 | "单列观察"中间分类 | 未产出（拦截，R3 仍拦截） | — | 策略/multifactor | AI拦截（模型能力上限） | 错 |
| 39 | STR-MULTIFACTOR-090 | 策略生命周期八阶段 | 策略/multifactor（R3 恢复） | 生命周期与通过标准 | 策略/multifactor | **一致**（R3 恢复即命中）；注册表存疑成立（文本是方法论）→注册表修正待办 | 对（随注册表；存疑转治理） |
| 40 | STR-MOMTREND-010 | 辅助确认工具指定法 | 其他/tool（R3 恢复） | 板块趋势确认工具用法 | 策略/momentum_trend | **AI合理**（文本是工具方法论；注册表为策展挂载） | 对 |
| 41 | STR-MULTIFACTOR-056 | 共振触发条件矩阵 | 策略/daban | 板块×个股策略 | 策略/multifactor | 注册表合理（共振=多因子合成） | 错 |
| 42 | STR-MULTIFACTOR-049 | ETF 多只对比四维选优 | 策略/multifactor | 四维选优策略 | 策略/multifactor | **一致** | 对 |
| 43 | STR-MULTIFACTOR-078 | 共振等级→仓位映射 | 其他/execution_algo | 仓位映射规则 | 策略/multifactor | 边界争议（执行层视角成立） | 对 |
| 44 | STR-MULTIFACTOR-045 | 双策略 5 分 | 策略/daban | 共振打分系统 | 策略/multifactor | 注册表合理（共振族） | 错 |
| 45 | STR-MULTIFACTOR-034 | 空仓等主线 | 策略/value_reversal | 空仓策略 | 策略/multifactor | 双方都不准（实为交易纪律）→注册表修正待办 | 错 |
| 46 | STR-VREV-002 | 下跌趋势不选/不抄底 | 策略/momentum_trend（R3；R2=knowledge_only） | 下跌趋势避抄底、上涨趋势找拐点 | 策略/value_reversal | **AI合理**（文本是纪律；R3 kind 对类偏仍可辩护） | 错†（标准 R2：不选/不抄底=禁令纪律→risk_rule，AI 归策略类偏） |
| 47 | STR-MOMTREND-012 | 强中强双重共振筛选 | 因子/technical（R3 恢复） | 均线+突破筛选 | 策略/momentum_trend | 注册表合理（共振筛选=选股策略族） | 错 |
| 48 | STR-MULTIFACTOR-038 | 选股四要素 | 其他/knowledge_only | 选股条件知识 | 策略/multifactor | 边界争议 | 错†（标准策展口径：选股知识服务 multifactor 体系，knowledge_only 丢弃服务对象） |
| 49 | STR-MOMTREND-021 | 加速第三买点 | 其他/risk_rule | 禁止买入规则 | 策略/momentum_trend | 边界争议 | 对 |
| 50 | STR-MULTIFACTOR-096 | 多因子 sleeve 组装策略 | 策略/multifactor | 完整多因子策略 | 策略/multifactor | **一致** | 对 |

## 五、终审结论（2026-08-30 架构师代裁，替代预审估计）

- **判定分布（R3 基准，口径甲·原样接受）**：对 29 / 错 21 → **原样接受率 58%**。错 21 条构成：注册表明显更贴切 16（#1/2/3/7/8/9/11/13/25/27/28/29/32/41/44/47）+ 拦截未产出 3（#6/17/38）+ R3 退化 1（#26）+ 双方不准 1（#45）。
- **宽容口径（可辩护率，错仅计无据/双方不准/拦截/退化）**：约 39/50 ≈ **78%**。
- **更正预审估计**：预审期"口径甲约 84%~90%"作废——它误把"注册表合理"族整体计为可接受；逐条终审后该族人审均须改。数字以本节为准。
- **结论**：两个口径均未过 85% 线。未过线主因不是模型文本理解力，是**任务输入残缺**（分类器看文本孤本，答案是策展挂载）——达标路径与门槛处置见 §六 裁定四。

## 六、裁定书（2026-08-30，架构师代裁）

> 授权链：Owner 2026-08-30 指令"你作为客观专业架构师……给出分析过程和裁定结果"。本裁定自签署生效；Owner 异议可翻案，翻案前为执行依据。登记：architecture_issue_registry 待补条目（GP1-EVAL-CALIBER-001）。

**裁定一（Q-A 口径）**：验收口径采用口径甲"人判语义合理性"，废弃"注册表真值一致率"作为分类器质量口径。

- 依据①（设计原文）：13号文 §3.2/§4.2 原文为"50 条样本**人评一致率** ≥85%"——人评 AI 分得对不对本就是字面本意；注册表真值口径只是评估脚本的代理实现，证伪后回归原文，**不是降门槛，是回归设计本意**。
- 依据②（第一性原理）：注册表类标签=策展意图（知识挂在哪棵树上管理），该信息不在文本孤本内——以注册表为真值=要求分类器猜策展人未写下的脑内结构，测量工具本身错误，换 GPT-5 亦不可达。
- 依据③（行业实践）：机构 NLP 落地以"人工验收通过率 / 标注员间一致性（Cohen's κ）"度量分类器，从不拿另一套策展体系标签当真值；此类策展 taxonomy 的人工标注员间一致性经验值也仅 80~90%。

**裁定二（指标操作化）**：口径甲双指标——主指标=**原样接受率**（草稿零修改直接可用，拦截未产出计入不接受）；辅助=可辩护率。主指标映射系统价值命题（人审成本≈0），防"可辩护但总要改"的隐性人力泄漏。

**裁定三（当前成绩，如实登记）**：R3 实证原样接受率 **58%**（29/50）、可辩护率约 **78%**（39/50）。**未过 85% 线，不凑数、不降格、不 reinterpret 门槛**。

**裁定四（根因与达标路径，按杠杆率排序）**：根因=任务输入残缺（分类器只见文本孤本，而答案含策展挂载意图）。
1. **任务输入补全**（最高杠杆，行业标准做法 label description + exemplar prompting）：prompt 注入 16 个受控类的策展边界说明（每类一句话"什么挂这里"）+ 每类 2~3 条已终审示例（本批 50 条判定结果回喂为教学集）。
2. DeepSeek 主通道恢复后同流程复测（挂 W3 Owner 行动项；qwen3:14b 残余 3 条拦截归模型能力上限，换强模型可再收）。
3. 注册表 2 条存疑条目（#39/#45）转治理修正（文本实为方法论/纪律，现挂 multifactor）。
- **防过拟合铁律**：本批 50 条回喂后即"教学集"，复测验收必须新抽样本（新 50 条，seed 变更），严禁教学集当考试集。
- **复测门槛**：原样接受率 ≥85%（数值维持 13号文原门槛不降格）；若路径①+②完成后仍 <80%，转评审"分类器存废"——其定位是提效工具非生存项，fallback=纯人工分类（13号文 §3.2 已预留）。

**裁定五（Q-C 消解）**：kind 层混淆随裁定一部分消解；残余 kind 错配（可计算指标误分流 other 族，如 #3）并入路径①复测验证，不单独施工。

**裁定六（Owner 复核确认 + 标准复判，2026-08-30）**：Owner 逐题复核裁定一~五全部确认，补充如下——
1. **题1补充条款（词不达意豁免）**："我挂的可能词不达意，AI 能理解的正常也算对"——注册表挂载与文本语义冲突时以文本语义为准（已写入 PS-VOC-TAX-001 decision_rules R6）。
2. **题4执行变更**：DeepSeek 暂缓充值；生产分类器仍由本地模型担任（Kimi 属会话制不可调度不可复现，不当生产组件，角色=教师：定标准/审教材/裁疑难——强模型产教材、弱模型跑生产的行业标准蒸馏模式）；#6（行业因子构造与轮动）备注=换模型复跑时优先验证；DeepSeek 费用评估=本管线非持续运行（仅新知识条目进入时触发），全量 286 条跑一遍约元级成本，投产比不构成阻塞。
3. **路径①落地形式升级**：Owner 指令"把边界定清楚写入系统文档最核心地方让以后 AI 都看得见"——由 prompt 补丁升级为系统级标准：**PS-VOC-TAX-001 knowledge_taxonomy_vocabulary.yaml**（vocabularies/ 词表目录，全 AI 可见 SSoT），含分层链（数据→指标→因子→信号→策略→执行）+ 22 类边界 + 冲突裁决 R1~R6 + 主观术语锚定表（尾盘偷袭/温和放量/抗跌吸筹/急跌必有急反/量价背离/共振，Owner 口述定义+全网搜证）；knowledge_classifier 运行时直读注入 prompt（本批落码）。
4. **标准复判**：用新标准复判 50 条，6 条翻转（§五 † 标记），复判后原样接受率 46%——数字更难看但方向更对：翻转条全部死于"AI 无边界知识"，正是路径①要修的。
5. **注册表修正已执行**：#39/#45 于 2026-08-30 标 deprecated 迁出策略候选池（strategy_registry.yaml 注释留痕 + 指向本标准）。
