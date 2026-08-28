---
ttl: task_bound
---

# AI 架构层待施工清单（2026-08-24，T3 审查产出）

> 来源：`docs/02_enterprise_architecture/09_ai_architecture/` 21 份文档全量审查（结案报告 `.runtime/construction_20260823/reports/T3_aiarch_review.md`）。
> 范围纪律：仅列「未施工 / 部分落地」项；GP0（全局 Phase 0）已于 2026-08-22 全量落地并 M0 终审（E0-1~E0-8 全绿），本清单主体 = 各文档 Phase 1+ 设计内排期项。**不建议重造任何已落地件**。
> MOD 号段查证（2026-08-24 全仓 Grep）：MOD-INF 已用至 052 → 新号 MOD-INF-053+；MOD-ML 已用至 009 → 新号 MOD-ML-010+；MOD-AU 已用至 002 → 新号 MOD-AU-003+；MOD-GOV 已用至 047 → 新号 MOD-GOV-048+；MOD-RK 已用至 026 → 新号 MOD-RK-027+；MOD-MODEL_ROUTER_ORCH（06/11 号文声明）、MOD-VOTE_REVIEW_SHELL（12 号文 §4.1 声明）为文档已登记未施工号，直接沿用。

> **结案审查（2026-08-28 复核）**：未结案（P1 头部项约半数已落地，清单未核销）
> - 已实证落地（未核销）：1.1 `agentic_drift_guard.py`；1.2/2.2 `security/ops/incident_pipeline.py` + `ops_maturity.py`；1.4 `intelligence/model_routing/cascade_orchestrator.py`；W1 GP0 新件已随 B-007 全量转 production（2026-08-28 全战役闭环，production=2933/testing=0）。
> - 仍有效：W2~W5 Owner 窗口/裁定项 + 其余 P1/P2/P3 项；施工前须先 grep 实证当前状态再派单（防重造）。

---

## 0. P0（阻断）

**无代码缺口级 P0 项。** GP0 已 M0 达成，各域无「不建则阻断其他施工」的代码缺口。以下为 P0 级 **Owner 窗口/裁定项**（非代码施工，但其是 GP1/GP2 的硬前置，置顶登记）：

| # | 事项 | 来源 | 说明 |
|---|---|---|---|
| W1 | GP0 新件 testing→production 启用审批（宪章 B-007） | 17 号文 §4.3/§4.4；GP0 总收尾 §四-7 | 17 号文 GP2 进入条件 I2-2/I2-3 的硬前置；GP0 全部新件现态 testing/stable |
| W2 | commit_queue 改道 flag 翻开（`config/flags.yaml:82`，默认 `enabled:false=ALWAYS_OFF`） | 08 号文；66 号 §7 | 改道设施（MOD-GOV-047 `reroute_auto_commit_to_queue`+`assert_single_writer_dev_history`）已建成，翻开即生效 dev 单写者不变量 |
| W3 | DeepSeek 账户 402 欠费充值（tracker #253） | GP0 总收尾 §四-1 | 当前 Qwen 通道承载主链路 |
| W4 | 三套自治等级标尺统一裁定（15 号文 Q3）；A-L 成熟度与既有标尺映射裁定（16 号文 Q4） | 15/16 号文 §6 | 裁定项，AI 不替 Owner 拍板；裁定结果是 MOD-AU-003 与成熟度解锁件的定级输入 |
| W5 | 模块工厂 Phase 0→1 / 业务 Agent 细化排期裁定（13 号文 Q1 / 14 号文 Q1；00 号文 §6.2 已登记「U8/U7 前置已就绪，转 GP 排期待裁定」） | 00/13/14 号文 | 裁定后解锁清单第 10/11 项施工 |

---

## 1. P1（高——GP1 半自动主体，保障类优先）

### 1.1 Agentic Drift 防护四件套（15 号文 Phase 1）

- **来源文档**：`15_autonomy_boundary_risk.md` §3.2/§4.2（S1.1~S1.3）
- **设计声明摘要**：双维度阈值（置信度×意图偏差度）+Hard-Gate+行为基线+Agent Challenge（交叉会话复审为主、challenge 工单落盘/降级、人兜底，00 号文 Q6 已裁定）。三步：S1.1 行为基线（复用 gov_drift/baseline_manager + BM-RC-04-F 口径，轻量统计）；S1.2 操作链内联漂移检查（drift_tolerance=0.3、10 步窗口、类型熵>1.5、路径熵>2.0，WARNING→auto_guard / DETECTED→blocked+P0 告警，挂 S0.2 gate 链路，性能预算 ≈0.25ms 量级）；S1.3 深度语义复核（日/周频批量嵌入相似度，产出报告人审）。
- **建议模块落点**：`src/zephyr/autonomy_core/agentic_drift_guard.py`（与 MOD-AU-001/002 同域同族；语义复核批量件可放 `src/zephyr/autonomy_core/drift_semantic_reviewer.py`）
- **建议 MOD 号**：MOD-AU-003（顺延 MOD-AU-001/002）
- **优先级**：**P1**（自治安全前提，00 号文 §3.1 横切机制中最后一个零代码大件）
- **验收标准（源文档摘录）**：S1.1「对历史数据建基线；注入合成异常（单会话 commit 频率突增 10×、首次触碰从未涉及的 production 模块）能检出并告警」；S1.2「构造渐变操作链样例（read→write→delete 类型漂移、src/→config/ 路径漂移）分别触发 WARNING 与 DETECTED；正常施工链不误报（抽样人审）」；S1.3「周频跑批产出报告；误报率人审抽样评估后可接受」。

### 1.2 自治运维 Diagnose→Remediate 接线 + 知识库落盘（16 号文 Phase 1）

- **来源文档**：`16_ai_security_ops.md` §4.3（P1-1~P1-4）
- **设计声明摘要**：统一事件流（已建 MOD-SEC-EVENTBUS）驱动 failure_matcher/anomaly_diagnoser 自动生成 FailureDiagnosis；诊断命中 auto_fix_engine 三通道（结构类直通模板化/语义类过 LLM Bridge 必经 LSG/行为类 Block+Alert 永不自动修复）；知识库落盘 `data/fix_patterns/pattern_index.yaml`（REG-AFX-PATTERN-001）+`_fixer-registry.yaml`；白名单审批走 human_gated 对接 GOV-AI-001。
- **建议模块落点**：管线编排件 `src/zephyr/security/ops/incident_pipeline.py`（新子包，消费 security_event_bus 事件目录）；知识库落 `data/fix_patterns/`（数据资产，非代码模块）
- **建议 MOD 号**：MOD-INF-053
- **优先级**：**P1**（Detect 已贯通，闭环断点在「连」——16 号文 §2.1-3 原判）
- **验收标准（源文档摘录）**：P1-1「探针事件触发诊断记录；不可自动修的判决走 escalation 通道落盘」；P1-2「三类故障各一条探针全链路走通；行为类探针 100% 不触发自动修复（不变量验证）」；P1-3「库文件存在且 schema 经校验；每次修复动作自动向库写一条记录（记录优先，不做匹配）」；P1-4「白名单变更留痕；未经审批的豁免 0 条」。

### 1.3 llm_runtime_gateway Phase 1：预算硬门 + ModelRouter 接线 + LLMDeg 降级注入（10 号文 Phase 1）

- **来源文档**：`10_llm_infrastructure.md` §4 Phase 1（步骤 1.1~1.4）；`llm_runtime_gateway.py:30` 自标「不做预算硬门（GP1 范围）」
- **设计声明摘要**：门面入口统一调 BudgetEngine.pre_flight_check（DENY 阻断）；LLMDeg-0~4 五级降级注入 ModelRouter 路由决策；`LLMGateway.route()` 接 MOD-INF-024 perf-aware 决策（替换 hint 直映射）；LSG 同一闸门对齐（L2 无旁路，GP0 已由 lsg_gate 落地，本项只需对齐验证）。
- **建议模块落点**：`src/zephyr/integration/llm_runtime_gateway.py`（同模块演进，不新建）
- **建议 MOD 号**：MOD-INF-051 演进（既有号，不新分配）
- **优先级**：**P1**（个人资金成本硬门；M3-⑨ 已真跑消费，预算门缺失=无成本刹车）
- **验收标准（源文档摘录）**：1.2「预算 DENY 场景单测通过；LLMDeg-1~4 触发时路由走向符合 §3.6 降级表」；1.4「route() 返回含 tier/reason/performance_score 字段」；1.3「L2 调用经 LSG 闸门的 L6 审计记录可见；代码中无 L2 旁路配置项」。

### 1.4 模型路由级联控制器（11 号文 Phase 1）

- **来源文档**：`11_evidence_skill_router.md` §3.3/§4.3（P1-1~P1-5）
- **设计声明摘要**：级联编排层串联一次路由决策——L1 能力门（消费 CapabilityPassport，required 硬门+safe_capabilities 交集）→L2 任务适配排序（融合 JobMatcher match_score 与 task_model_learner composite_score）→L3 成本/层级路由（复用 MOD-INF-024 ModelRouter，本地优先 API 兜底）+级联降级链+时段/任务分派策略（12 类路由表+分时段显存+风控不可降级）。只做消费与串联，不改三基座结构。
- **建议模块落点**：`src/zephyr/intelligence/model_routing/`（新包，11 号文 §3.3 指定落点；实测目录不存在）
- **建议 MOD 号**：MOD-MODEL_ROUTER_ORCH（06 号文 §2.1 已声明引用，沿用）
- **优先级**：**P1**（06 号护照资产与 MOD-INF-024 的价值放大器；自我进化层 GP1 核心件）
- **验收标准（源文档摘录）**：P1-1「伪造/篡改护照→验签失败被拒；不满足 required 的模型不进入 L2」；P1-2「已知 benchmark 数据下排序结果与两源分数的手工复算一致；样本=0 时静态映射兜底生效」；P1-3「路由决策含 reason+估成本（RoutingDecision 字段完整）；MOD-INF-024 源文件零改动（git diff 佐证）」；P1-4「逐段故障注入：每次故障均有降级产物+告警，不中断路由返回」；P1-5「规则命中单测通过；配置变更不改代码；风控类任务路由到外部 API 的不可降级性由故障注入测试佐证」。

### 1.5 触发式考试调度器（06 号文 Phase 1）

- **来源文档**：`06_model_profiling_pipeline.md` §4 Phase 1（P1-1~P1-4）
- **设计声明摘要**：ModelDiscovery 发现新模型→自动 Quick 考试→QuickProfile 落盘；TaskGate 连续 low_accuracy 拦截超阈值→发出复核考试建议（只发建议，Standard/Deep 始终人工确认——对齐 human_gated）。
- **建议模块落点**：`src/zephyr/intelligence/model_profiling/exam_trigger_scheduler.py`（同包新增）
- **建议 MOD 号**：MOD-INF-054（或按 06 号文 P1-1 口径登记为 MOD-INF-036 子件——施工时由统筹裁定）
- **优先级**：**P1**（画像→考试→护照→门控闭环的最后一断点；增量学习 matrix 空矩阵回流可随本件一并接线）
- **验收标准（源文档摘录）**：P1-2「新模型自动产生 QuickProfile 落盘 data/brain/quick_profiles/」；P1-3「拦截日志含触发建议记录」；P1-4「测试通过后 depgraph status planned→production」。

### 1.6 Context Engine inject 段接线 + 压缩三档（07 号文 Phase 1）

- **来源文档**：`07_context_engine_build.md` §4 Phase 1（P1-1 等）
- **设计声明摘要**：`ContextInjector` 数据源接至 UnifiedMemoryAPI（D_INTELLIGENCE，经 VMSSearchProtocol 协议注入，不跨域硬编码），`inject_by_keyword()` 返回非空 InjectedContext（含 sources+provenances）；压缩从规则式单档升级为 llm_summary（本地 Qwen 分 slot 摘要）/rule_based/truncate 三档降级。
- **建议模块落点**：`src/zephyr/autonomy_core/context/context_injector.py`（既有件演进）+ `src/zephyr/shared/io/doc_compressor.py`（既有件增档）
- **建议 MOD 号**：不新分配（MOD-CONTEXT_ENGINE / MOD-INF-016 既有件演进）
- **优先级**：**P1**（四段流水线唯一生产空段；2026-08-23 进度核对报告 §4 明列归 GP1 Phase 1）
- **验收标准（源文档摘录）**：P1-1「inject_by_keyword() 返回非空 InjectedContext（含 sources + provenances）」；Phase 1 目标「inject 段从空占位升级为可用；压缩从单档升级为三档降级」。

### 1.7 LSG 蓝图剩余缺口收尾（09 号文 Phase 1，80%→95%）

- **来源文档**：`09_llm_security_integration.md` §4.3（P1-1~P1-5）
- **设计声明摘要**：①L6 飞书告警 Webhook（注意与 MOD-SEC-EVENTBUS 已建 FeishuAlertChannel 的覆盖关系，施工前先裁定复用还是 LSG 层内自建——**待复核**）；②CI 安全门禁 `.github/workflows/lsg_security_gate.yml`+golden 回归集落盘（实测均不存在）；③L5 `LSGPerformanceGuard` 性能预算管理（延迟埋点+超预算自动降级，永不可降级项 L1A/L3B/L4/L5 成本熔断除外）；④`phase_check_registry.check_lsg_security` 补挂；⑤蓝图注册表版本/完整度同步。
- **建议模块落点**：`src/zephyr/security/llm_defense/llm_security/`（L5/L6 层内）+ `.github/workflows/lsg_security_gate.yml` + `tests/llm_security/golden/` + `src/zephyr/governance/phase_check_registry.py`（补挂）
- **建议 MOD 号**：不新分配（MOD-LLM_SECURITY 蓝图内收尾）
- **优先级**：**P1**
- **验收标准（源文档摘录）**：P1-1「注入高危探针事件→Webhook 送达（含降级策略：不可达时本地持久化不丢事件）」；P1-2「PR 触发门禁：golden 回归集全绿才放行」；P1-3「压测验证 P95<50ms；人为制造延迟超预算→按 §40.4 降级顺序自动降级且永不可降级项不被降级」；P1-4「phase_manager Phase 1 门禁检查可正常消费 LSG 健康状态」。

---

## 2. P2（中）

### 2.1 KILLSWITCH 三级响应编排层（16 号文 Phase 2，P2-3）

- **来源文档**：`16_ai_security_ops.md` §3.4/§4.4 P2-3；00 号文 §3.3
- **设计声明摘要**：策略层三级响应与 15 号文两级编排（MOD-AU-002 已建）叠加映射——level_1 P1(high)→自治降级+技能熔断（暂降 IM 模式：读/查询放行，写操作一律人审）；level_2 P0(critical)→系统级单 Agent 阻断；level_3 global_critical→系统级全局熔断+交易级联动；KILLSWITCH.md 独立文件随任务落盘（§3.13）。全仓 Grep `KILLSWITCH|global_critical` 零命中（2026-08-24 实测）。
- **建议模块落点**：`src/zephyr/autonomy_core/killswitch_response_levels.py`（策略层，消费 MOD-AU-002 编排器）
- **建议 MOD 号**：MOD-AU-004
- **优先级**：**P2**
- **验收标准（源文档摘录）**：「三级各注入探针事件验证触发链；level_3 触发后 5 套 Kill Switch 收敛状态一致（无『只停次要回路』）；复位需 Owner 批准（15 号文不变量）；KILLSWITCH.md 变更记录写审计链」。

### 2.2 Learn 回写闭环 + 成熟度 A-L0→A-L2 解锁（16 号文 Phase 2，P2-1/P2-2）

- **来源文档**：`16_ai_security_ops.md` §4.4
- **设计声明摘要**：`fix_pattern_miner` 周期性挖掘修复记录→修复策略库更新→Diagnose 匹配命中率可观测；事件流只记录（A-L0）→告警（A-L1）→自愈建议（A-L2）逐级上线（A-L3 解锁条件按 §3.7 实证评估后单独裁定）。
- **建议模块落点**：`src/zephyr/security/ops/ops_maturity.py`（与 1.2 同子包）；挖掘任务复用既有 `fix_pattern_miner.py`
- **建议 MOD 号**：MOD-INF-055
- **优先级**：**P2**（依赖 1.2 知识库先有数据）
- **验收标准（源文档摘录）**：P2-1「连续 2 周挖掘任务运行；命中率在仪表板可观测（指标只观测不设目标值）」；P2-2「每级解锁有连续 N 周零 TNR 违规记录；A-L2 状态下人工采纳率留痕」。

### 2.3 ReflCtrl 频率闸门 + PreFlect 失败模式库（12 号文 Phase 1，P1-1/P1-3）

- **来源文档**：`12_reflexion_multi_agent.md` §3.4/§4.3
- **设计声明摘要**：ReflCtrl 显式触发规则集（L1 强制三条件/Agent-R 四场景阈值/分层频率：执行层 ~80%、战术层 ~50%、战略层 ~20%/决策矩阵参数+单任务反思轮次上限），规则可配置可审计；PreFlect 库（失败模式条目 schema：模式/触发条件/规避建议/来源反思 ID + 任务启动时检索注入）。
- **建议模块落点**：`src/zephyr/intelligence/reflexion/reflctrl_gate.py` + `preflect_store.py`（同包扩展）
- **建议 MOD 号**：MOD-REFLEXION_AGENT 演进（既有号，不新分配）
- **优先级**：**P2**（防反思 token 成本失控的闸门；依赖 GP0 反思记录积累）
- **验收标准（源文档摘录）**：P1-1「规则外触发请求被拒；每次放行可追溯到触发规则；token 消耗统计落盘」；P1-3「L2 产出可入库；注入内容含来源反思 ID；人工编辑接口可用」。

### 2.4 模块工厂 Phase 1：knowledge_classifier + module_mapper（13 号文 Phase 1）

- **来源文档**：`13_module_factory.md` §4.2（P1-S1 起）；19 号文附 C
- **设计声明摘要**：六环节中环节 2（分类）与环节 3 检索部分自动化——AI 分类（factor 10 类/strategy 6 类受控词表+多维适用性十字段）+AI 映射检索（schema_plan 语义抽象+既有库重复/变体/组合四选一裁决辅助）；人写模块、人入库不变。
- **建议模块落点**：`src/zephyr/research/module_factory/knowledge_classifier.py` + `module_mapper.py`（新子包）
- **建议 MOD 号**：MOD-INF-056（knowledge_classifier）/ MOD-INF-057（module_mapper）
- **优先级**：**P2**（前置：W5 排期裁定；19 号文 SOP 已跑通手动形态，自动化是效率件非阻断件）
- **验收标准（源文档摘录）**：13 号文 §4.2 Phase 1「AI 采集辅助+AI 分类+AI 映射检索；人写模块；AI 辅助验证；人入库」；P1-S1「apply_depgraph 登记 knowledge_classifier + module_mapper 两节点（planned），依赖边：→factor/strategy registry（读）、→embedding_model_registry（读）」。

### 2.5 涌现检测「告警→人工介入」末段接线（12 号文 §4.4 + 16 号文协同）

- **来源文档**：`12_reflexion_multi_agent.md` §2.2-4/§4.4；`security_event_bus` RuntimeDetectorAdapter（已承接 is_breached→high 告警）
- **设计声明摘要**：检测器→eventbus 告警已通（GP0 建）；缺口=告警后的人工介入 SOP/处置工单闭环（非预期涌现→告警→介入），深度安全语义归 15/16 号文，本项只做消费与介入接线；12 号文 §4.1 明确「涌现介入接线不新建节点——消费 MOD-RK-14 既有输出，接线改动落在既有告警/运维设施的消费侧」。
- **建议模块落点**：既有告警/运维设施消费侧（如 `src/zephyr/security/ops/` 处置工单件，可与 1.2 管线合并施工）
- **建议 MOD 号**：不新分配（按 12 号文 §4.1 口径不新建节点；若统筹决定独立成件则 MOD-RK-027）
- **优先级**：**P2**
- **验收标准（源文档摘录）**：12 号文 §2.2-4「is_breached 信号需要接告警与人工介入 SOP」；§4.4 涌现介入接线项（P2 段）。

### 2.6 MCP Client 动态发现 + 漂移对账入遥测（10 号文 Phase 2，步骤 2.1/2.2）

- **来源文档**：`10_llm_infrastructure.md` §3.2/§4 Phase 2
- **设计声明摘要**：MCP Client 连接后 `list_tools()` 拉取实况与 tool_contracts.yaml 契约 diff——发现即校验（未知工具告警+默认拒绝写操作，safety_level M/H 必须契约命中才放行）；传输层仅 localhost HTTP+SSE、STDIO 禁用；工具注册执行 MCP-Scan 剥离指令性语言；diff 结果 emit 遥测，漂移 >24h 升级告警。src 下 Client 侧 `list_tools` 实测零命中（2026-08-24）。
- **建议模块落点**：`src/zephyr/integration/mcp/client_discovery.py`（mcp 包新增）
- **建议 MOD 号**：MOD-INF-058
- **优先级**：**P2**
- **验收标准（源文档摘录）**：2.1「人为增删一个 mock 工具，diff 报告正确检出；STDIO 类型 server 配置被拒绝」；2.2「telemetry.metrics_snapshot 可见 drift 指标」。

### 2.7 技能库自动生成路径（AutoSkill+Voyager，11 号文 Phase 2）

- **来源文档**：`11_evidence_skill_router.md` §3.2/§4.4
- **设计声明摘要**：研究轨迹/已验证假设→轨迹挖掘器生成技能草稿→复用 skill_sandbox 沙箱测试→回测验证门（量化技能必须过回测，复用 backtest 域设施）→人工门→skill_constructor 式写盘入库；SKILL.md 渐进披露三级格式（Discovery ~100-200 tokens / Activation <5000 / Execution 按需）；退役指纹库（相似度 >90% 拒绝重注册）。全仓 Grep `trajectory_miner|voyager` 零命中（2026-08-24）。
- **建议模块落点**：`src/zephyr/autonomy_core/skills/skill_trajectory_miner.py`（skills 包新增，复用 58 个既有工程基座）
- **建议 MOD 号**：MOD-INF-059
- **优先级**：**P2**（依赖证据组件 production 化积累真实假设输入；W1 之后）
- **验收标准（源文档摘录）**：§3.2「未验证技能不得进生产库（回测验证门）」；§4.4 P2 段（技能草稿→沙箱→回测→人工门→入库全链路）；匹配延迟「任务分派匹配 <100ms；新技能注册全量扫描+冲突检测 <1s」。

### 2.8 04 号文遗留：boot watchdog 存量缺陷修复 + 冷启动 SLA 复测

- **来源文档**：GP0 总收尾报告 §四-5（tracker #255）；`architecture_issue_registry.yaml` #ARCH-163 adjudication
- **设计声明摘要**：`09a_governance_watchdog_start` NoneType 存量缺陷（与 GP0 工单零因果，存量项）；修复后补做冷启动 SLA 20 次连跑实测（boot P99<10s，当前仅单次 47ms 埋点实测）；另附 tests/automation AutoEvolution 3 项存量失败。
- **建议模块落点**：`scripts/construction/start_brain.py` boot 链路 / `src/zephyr/trading/` 对应 watchdog 件（存量修复，不新建模块）
- **建议 MOD 号**：不新分配（存量缺陷修复）
- **优先级**：**P2**
- **验收标准（源文档摘录）**：18 号清单 §6 波 3-04「冷启动 SLA boot P99<10s——start_brain.py --once 连跑 20 次实测留痕」。

### 2.9 task_gate 护照 ID 口径统一（06 号文遗留）

- **来源文档**：GP0 总收尾报告 §四-6（tracker #255）
- **设计声明摘要**：task_gate passports ID 口径（冒号 vs 下划线）不一致，Phase 2 接 dispatch 链前需统一；同批遗留：CE depgraph 边缺口 7 项登记在册。
- **建议模块落点**：`src/zephyr/trading/task_gate.py` + `data/brain/passports/`（口径对齐，不新建模块）
- **建议 MOD 号**：不新分配
- **优先级**：**P2**（1.4 级联路由消费护照前先收口，避免双口径）
- **验收标准（源文档摘录）**：GP0 总收尾 §四-6 原文「task_gate passports ID 口径（冒号 vs 下划线）Phase 2 接 dispatch 链前统一」。

---

## 3. P3（低/远期）

| # | 事项 | 来源文档 | 设计声明摘要 | 建议落点/MOD | 验收标准（摘录） |
|---|---|---|---|---|---|
| 3.1 | 投票评审壳 + 多会话投票 SOP（可选模式设施） | 12 号文 §3.6/§4.3 P1-2/P1-4 | 候选收集→调 A2AVoting 计票→选最优落盘，壳体 <100 行，默认不启用、人触发；#ARCH-OE-011 已定可选模式 | `src/zephyr/intelligence/reflexion/` 内；MOD-VOTE_REVIEW_SHELL（文档已声明） | 「3 候选构造集跑通 approve/reject/abstain+quorum 全路径；MOD-INF-025 源文件零改动；壳体行数实测 <100；无自动触发路径」 |
| 3.2 | L2 同类任务反思 + 数学反思闭环（scipy 约束优化） | 12 号文 §3.1/§4.4 P2-1 | N=5 累积触发，跨轨迹归纳共性失败模式；可形式化参数走 scipy.optimize 约束优化替代 LLM 直觉 | `intelligence/reflexion/l2_reflector.py`；MOD-REFLEXION_AGENT 演进 | 「构造 5 条同类轨迹→归纳产出含共性模式；不足 N=5 不触发」 |
| 3.3 | 08 号文 Phase 2 提交队列可观测性 | 08 号文 §4 Phase 2 | 队列运行指标/死信可观测 | `scripts/commit_queue.py` 演进；MOD-GOV-048 | 08 号文 Phase 2「优化可观测」段 |
| 3.4 | GGUF 模型管理件 + 本地推理质量基线 | 10 号文 Phase 2 步骤 2.3/2.4 | Ollama 模型清单登记+显存预算表（21.6GB 上限时段配额）；qwen3:8b 基线考试存档 | `config/` 显存预算表+model_profiling 复用；MOD-INF-060 | 「显存预算表落 config/（human_gated），超预算加载被阻断」；「基线成绩入库 data/model_profiles/」 |
| 3.5 | 09 号文 Phase 2 纵深增强（L3B 沙箱/L7 Threat Intel/L8 级联扩展/v2.0.0 signal_bus） | 09 号文 §4.4 + 蓝图 §0-升级 D6-D16 | signal_bus 全仓零命中；L8 本项目多 Agent 规模小蓝图自标低优先 | MOD-LLM_SECURITY 演进 | 09 号文 Phase 2 段；signal_bus 启动条件（蓝图 v2.0.0） |
| 3.6 | 13 号文 Phase 2 受控生成器 + 编排器 | 13 号文 §4.3 | 受控生成（DSL 约束+AST 沙箱+llm_safety_stack 五字段）+工厂编排；保留人工审核（C2 零审核=自杀） | `src/zephyr/research/module_factory/`；MOD-INF-061/062 | 13 号文 §4.3 Phase 2 段；G8 人工签批门不可降级 |
| 3.7 | 14 号文 Phase 1 四类入口半自动形态 | 14 号文 §4 Phase 1 | 依赖自我进化层件 production（W1 之后）；Agent Card/冷启动 6 步/退役指纹库形式化落地范围待复核 | `autonomy_core/agents/` 演进；MOD-EXE-AGENTS 演进 | 14 号文 §4 Phase 1 段 |
| 3.8 | ARS 双轨结算（Fee+Principal 防自利） | 15 号文 §2.1-5/00 号文 §3.2 | 全仓零命中，仅设计口径；检测侧可复用 `gov_drift/reward_hacking_rebound_detector.py`；15 号文 Phase 2 远期候选 | `src/zephyr/autonomy_core/ars_settlement.py`；MOD-AU-005 | 00 号文 §3.2「Fee+Principal 双轨，防止 Agent 自利行为」 |
| 3.9 | derived_graphs/ 派生图 6 篇生成 | 00 号文 §5.2 | 目录实测不存在；含 AI 层依赖拓扑/三层运行时编排/模型生命周期/上下文记忆流/多 AI 协作时序/LLM 安全栈纵深图 | 复用 `scripts/governance/` 派生图生成器族；MOD-GOV-049（若独立成件） | 00 号文 §5.2 六篇清单+源真源标注 |
| 3.10 | 举报人机制（whistleblower） | 16 号文 §3.9/00 号文 §3.3 | 已裁定远期 P4 降级（2026-08-18），MVP 设计保留 | 远期，不排期 | 16 号文 §3.9 MVP 设计段 |
| 3.11 | L3 跨任务反思 + 元反思 | 12 号文 §3.1 | 远期属性显式标注：反思记录积累不足时无统计意义，Phase 3 评估启动 | 远期 | 12 号文「频率硬约束 ≤1 次/周」 |
| 3.12 | 13 号文 Phase 3 模块工厂自我进化 | 13 号文 §4.4 | 远期 P4，ICL 路线锁定（17 号文 §3.5） | 远期 | 13 号文 Phase 3 段 |
| 3.13 | 数据增强（TimeGAN/扩散） | 10 号文 §2.2-5 | 归属 D-DATA 域 95 号能力，FWT 检索增强扩散要求 GPU≥40GB 超 3090 硬约束——10 号文只声明边界不承揽 | 归 D-DATA 域，不列入本清单施工 | 10 号文「本文只声明边界，不承揽实现」 |
| 3.14 | 01/02 号文快照刷新（维护项） | 01 §1/02 §2.1 | GP0 后「未施工」状态描述部分过期 | 文档维护，随下轮 AI-FILL 口径刷新 | —（非代码项） |

---

## 4. 优先级汇总与施工顺序建议

- **P0**：无代码缺口；Owner 窗口项 W1（production 启用审批）是一切 GP1 件转 production 的总闸门，建议优先安排。
- **P1（7 项）建议顺序**：1.1 Drift 防护 ∥ 1.2 运维接线 ∥ 1.7 LSG 收尾（保障三件可并行）→ 1.3 gateway 预算门 → 1.5 考试调度器 → 1.4 级联路由（依赖 1.5 的护照新鲜度与 1.3 的预算门）→ 1.6 CE inject。
- **P2（9 项）**：2.1/2.2 紧随 1.2；2.3 紧随 W1（反思记录积累）；2.4 待 W5 裁定；2.8/2.9 为存量收口可随手做。
- **P3（14 项）**：远期/可选/依赖链末端，不排期。
- **总口径**：本清单与 17 号路线图「全局 Phase 0→1」位置一致；全部 P1/P2 项的 depgraph L1 铁律（先登记 planned、验收后转 production）与各源文档 §4 既定纪律一致，施工时按 18 号清单 E2 裁定「新模块 testing 封顶，production 启用留 Owner」执行。
