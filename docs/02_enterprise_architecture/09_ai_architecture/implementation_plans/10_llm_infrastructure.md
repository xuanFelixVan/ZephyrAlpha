---
ttl: permanent
doc_type: architecture_view
title: LLM 基础设施施工图
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "0.4.0"
date: 2026-08-31
topic: llm_infrastructure
scope: 09_ai_architecture
---

# LLM 基础设施施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证）
> **实际开发**：Phase 0 三件+gateway MVP 落地——llm_runtime_gateway.py（MOD-INF-051：单一 infer 签名+DeepSeek/Qwen/Ollama 三通道优先级链+llm_call_log append-only 落库+LSG 入口闸门+LLMDeg-0~4 降级注入）；真实消费方 plan_engine/llm_premarket_analysis.py（M3-⑨/MOD-PLAN-007）接线；降级链生产实证（DeepSeek 402→Qwen 接管成功，llm_daily_analysis 落库）；model_pricing 谷时价按 DeepSeek 官网 2026-08-17 调价真源校准（42 用例绿）。
> **最终成果**：三通道降级链+成本对账+真跑验证全闭环（GP0 验收口径）。
> **未做+原因**：~~预算硬门/路由级联（Phase 1）属 GP1（文中已声明）~~ **已过时，见下方 2026-08-31 回填**；MCP 运行时动态发现、模型注册 SSoT 收敛方向裁定未完成（GP1+/开放问题）。

> ## 结案报告回填（2026-08-31 施工闭环，代码实证）
> **Phase 1（GP1）已收口**：预算硬门+路由级联落码——llm_runtime_gateway.py（MOD-INF-051）infer 入口统一调 BudgetEngine.pre_flight_check（DENY 阻断），LLMDeg-0~4 降级级别注入路由决策（§3.6 运行时镜像），route() 接 MOD-INF-024 ModelRouter perf-aware 决策返回 RoutingDecision（tier/reason/performance_score）；MOD-INF-051 [MATURITY] testing→production 翻转（#ARCH-301：2026-08-31 Owner 授权代判 GP1 验收口径甲 40/40 通过）。预算硬门主维度 token→元成本切换裁定登记（#ARCH-303，校准在途）。
> **Phase 2.3 显存预算表已施工**：config/gguf_vram_budget.yaml（human_gated）+ src/zephyr/intelligence/gguf_model_manager.py（MOD-INF-060，Ollama 已拉模型清单登记 + 加载显存 vs 21.6GB 上限预算阻断）。
> **Phase 2.4 qwen3:8b 基线已施工**：scripts/run_qwen3_baseline_exam.py 跑基线考试，成绩单落盘 data/model_profiles/（benchmark_20260830_154428.jsonl），tests/model/test_qwen3_baseline_profile.py 守卫。
> **Phase 3 已收口**：3.1 注册对账脚本 scripts/governance/audit_llm_registry_reconciliation.py 已施工（MOD-INF-039 ↔ REG-ML-001 ↔ model_pricing.yaml 三向比对）；3.2 文档收尾=本次回写；3.3 成熟度翻转已随 #ARCH-301 闭环（production）。
> **仍遗留**：Phase 2.1/2.2（MCP Client 动态发现 + 漂移对账入遥测）未施工，P2 排期待定；开放问题 Q1/Q6/Q7/Q8/Q9 待裁定（见 §6）。

> 本文定位：LLM 基础设施的施工——三层运行时（L1/L2/L3）、MCP 工具调用、推理优化、模型注册、数据增强。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，盘点见 [02_design_asset_inventory.md](02_design_asset_inventory.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | LLM 基础设施 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·基础设施层 |
| 依赖 | AutoRuntime Core 蓝图（04 号文） |
| 优先级 | P1——LLM 推理是所有 AI 能力的底层支撑 |
| 状态 | active（GP0+GP1 已施工：gateway MVP+三通道降级链+预算硬门/路由级联落地，MOD-INF-051 production（#ARCH-301）；Phase 2.3/2.4+Phase 3 已施工；Phase 2.1/2.2 MCP 动态发现属 P2 遗留） |

---

## 2. 背景

### 2.1 项目处境

LLM 调用能力在项目中**并非空白，而是"两套平行体系 + 若干散落件"**（2026-08-17 实测，逐条验证见 §2.4）：

- **L3 API 侧已收敛**：`src/zephyr/infrastructure/pipeline/llm_gateway.py`（LLMGateway）提供 deepseek / glm / claude / openai 四 provider 统一调用 + 降级链 + LSG 安全扫描 + 成本计量，协议面由 `src/zephyr/shared/contracts/llm_gateway_protocol.py`（LLMGatewayProtocol）锁定。
- **L2 本地侧另成体系**：`src/zephyr/integration/local_model/` 下 OllamaChat（qwen3:8b）/ DeepSeekChat / LocalModelScheduler（24/7 后台调度）/ EmbeddingRouter（BGE-M3 双维路由）/ CacheLayer，接口与 LLMGateway **互不相通**——local_model 层走 `ask()/inference(work_type)` 签名，LLMGateway 走 `call(messages)` 签名，两侧各自实现了重试、JSON 解析、预算预检。
- **L1 Trae 侧不是代码**：L1 = 人在 IDE 用 Trae 多会话施工（见 [04_architecture_principles_decisions/README.md](../../04_architecture_principles_decisions/README.md)「三层 AI 工作分配」），不产生运行时调用，不进入本文代码施工范围。
- **AutoRuntime Core 已承担三层编排入口**：`src/zephyr/trading/auto_runtime_core.py`（MOD-INF-035，系统大脑）内含 `_OllamaProcessManager`（Ollama 进程生命周期）与 `_LocalModelBootstrap`（本地模型栈启动编排），蓝图定位为「三层运行时运营中心」（`docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md`）。
- **MCP 工具调用已具规模**：`src/zephyr/integration/mcp/` 下 11 个 server 实现文件 + `tool_contracts.yaml`（10 个 server 契约）+ `config/mcp.json`（12 个 server 注册 + 1 个 gateway），但**注册是静态的**——新增工具需改 YAML/JSON 配置，尚未实现运行时动态发现。
- **推理优化未施工**：全仓 Grep `llama.cpp|llama_cpp|GPTQ` 在 `src/` 下零命中；[00_index.md](00_index.md) §1 提到的「llama.cpp+GPTQ INT4 显存 14→4GB」目前只是设计表述，无代码。
- **模型注册三处分裂**：运行时 `src/zephyr/orchestrator/governance/model_registry.py`（MOD-INF-039，6 模型常量 dict）、治理登记 `docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml`（REG-ML-001，8 条目，ML 训练产物 SSoT）、网关内嵌 `ProviderConfig`（llm_gateway.py `_build_providers()`）——同一模型的事实分散在三处，无对账机制。
- **MLflow 已裁定退役**：51 号备忘（[51_panel_experiment_history_mlflow_retirement.md](../../07_trading_decision_architecture/design_memos/51_panel_experiment_history_mlflow_retirement.md)）v1.2.13 记录 2026-08-16 完成 MLflow 全量卸载（代码删除 + `pip uninstall mlflow 3.15.1`），根因是过度工程（外部 UI 违反「集成到现有 frontend」偏好、全量包对个人项目过重）。00_index §1「模型注册(MLflow)」表述已过期。

### 2.2 核心问题

1. **三层运行时如何分工、在哪统一？** L2/L3 两套客户端平行存在，调用方需要知道用哪套；AutoRuntime Core 蓝图声称是「三层运行时运营中心」，但统一入口（一个 API 屏蔽 L2/L3 差异）尚未落到代码。
2. **MCP 如何动态发现工具？** 当前 mcp.json + tool_contracts.yaml 是静态注册（新增工具 = 改配置 + 重启），与 00_index §1「MCP 动态发现，新增工具零代码改动」的目标态有差距。
3. **推理优化在 RTX 3090 上的真实路径是什么？** 2026 年实证（见 §3.3）：3090（Ampere）无原生 INT4 tensor core，GPTQ INT4 在单流交互解码下反比 FP16 慢 1.3~2.2×，只有显存收益没有速度收益；GGUF Q4_K_M（llama.cpp/Ollama 内核）才是成熟路径。原「llama.cpp+GPTQ INT4」设计表述需要按实证修正。
4. **模型注册的 SSoT 在哪？** 三处分裂（运行时 dict / REG-ML-001 YAML / 网关内嵌配置）需要收敛方向，而不是再建第四套注册系统。
5. **数据增强的归属？** TimeGAN/扩散增强实测归属 D-DATA 域 95 号能力（`docs/02_enterprise_architecture/09_ai_architecture/依赖图/02-D-DATA-数据域.md` L109），且 FWT 检索增强扩散要求 GPU≥40GB（同文件 L759），超出 RTX 3090 24GB 硬约束——本文只声明边界，不承揽实现。

### 2.3 约束条件

| 约束 | 值 | 对 LLM 基础设施的含义 |
|---|---|---|
| 硬件 | 单机 RTX 3090 24GB（显存 <90% = 21.6GB 硬上限）、64GB RAM | 本地推理仅限 ≤8B 级模型量化版；FWT/扩散类增强（≥40GB）不可行 |
| 网络 | 30Mbps | 大模型权重下载需错峰；L3 API 调用无带宽压力但需考虑断网降级 |
| 部署 | Windows 单机、无集群/K8s、无热备、RTO<5 分钟 | 排除 vLLM 集群/Triton Server 等分布式推理栈 |
| 施工方式 | 1 人 + AI 协作、多 AI 多对话并发、代码 100% AI 生成 | 接口必须简单稳定，依赖锁定，禁止引入重型 MLOps 平台 |
| 业务节奏 | A 股 T+1、日频及以上根频率、miniQMT 10 笔/秒 | LLM 推理**不在交易实时路径**上，延迟敏感度低，成本敏感度中等 |
| 资金 | 个人资金双账户 | L3 API 调用需预算门控（已有 BudgetEngine pre_flight_check） |

### 2.4 已施工设施盘点

> 全部路径 2026-08-17 经 LS/Read/Grep 实测存在；状态以文件头 `[MATURITY]` 标注或注册表 status 为准。

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| L3 网关 | `src/zephyr/infrastructure/pipeline/llm_gateway.py` | LLMGateway：deepseek/glm/claude/openai 四 provider、降级链、LSG 输入/输出扫描、token+成本计量（头部标 MOD-INF-009，docstring 标 MOD-INF-019，不一致见 Q7） | production |
| 网关协议 | `src/zephyr/shared/contracts/llm_gateway_protocol.py` | LLMGatewayProtocol（call/route/list_providers/get_provider_config 四个 classmethod）+ LLMResponse/ProviderConfig 契约（MOD-INF-016） | production |
| 统一 HTTP 客户端 | `src/zephyr/shared/api/api_client.py` | ApiClient：超时/重试/熔断/幂等键/metrics hook，禁裸 aiohttp 的施工约定载体（MOD-INF-016 §2.10） | production |
| L2 本地推理 | `src/zephyr/integration/local_model/ollama_chat.py` | OllamaChat：qwen3:8b 默认（env `OLLAMA_INFERENCE_MODEL`），`/api/chat` 封装，work_type 路由（20+ 任务型 system prompt），预算预检（MOD-INF-042） | production |
| L3 DeepSeek 直连 | `src/zephyr/integration/local_model/deepseek_chat.py` | DeepSeekChat：requests 直调（绕过 openai 库 SSL 问题），接口与 OllamaChat 兼容（MOD-INF-042） | production |
| L2 调度器 | `src/zephyr/integration/local_model/local_model_scheduler.py` | LocalModelScheduler：24/7 后台线程，9 类本地能力分派（embedding/search/reranking/6 类 inference），有界队列 100（MOD-INF-042） | production |
| 嵌入路由 | `src/zephyr/integration/local_model/embedding_router.py` + `ollama_embedding.py` | BGE-M3 1024d（5 collection）/ bge-small（3 collection）双维路由，Ollama/SentenceTransformer 双后端，LRU 淘汰（MOD-INF-011/042） | production |
| 推理缓存 | `src/zephyr/integration/local_model/cache_layer.py` | CacheLayer：嵌入+查询结果 LRU（默认 1024），模型版本入键、换模型自动失效（MOD-INF-042） | production |
| MCP 服务群 | `src/zephyr/integration/mcp/`（11 个 server 实现文件 + `tool_contracts.yaml`） | tool_contracts.yaml 定义 10 个 server 契约（task_manager/gate_engine/session_handoff/intent_router/blueprint_search/governance/telemetry/vector-memory/resource_optimization/rule_discovery），含 safety_level/rate_limit/error_namespace | beta~stable 混合 |
| MCP 集中配置 | `config/mcp.json` | MCP Gateway 集中式配置 SSoT（MOD-INF-013 §12）：12 个 server 注册（含 sandbox/red_blue_validator/clone_guard）+ gateway 节点 | active |
| 模型路由 | `src/zephyr/governance/intelligence_governance/model_router.py` | ModelRouter：tier×complexity 路由 + benchmark perf-aware 评分（cost 0.5/speed 0.35/quality 0.15）+ 黑名单（MOD-INF-024） | production |
| 模型画像 | `src/zephyr/intelligence/model_profiling/`（profiler/exam_orchestrator/exam_judge/capability_passport/model_discovery/provider_data 等） | 画像→考试→护照链路 + Ollama/远程模型发现（MOD-INF-034），细节归 06 号文 | production |
| 运行时模型注册 | `src/zephyr/orchestrator/governance/model_registry.py` | MODELS 常量 dict（deepseek-chat/deepseek-reasoner/claude-opus-4/claude-haiku-3.5/gpt-5.2/gpt-4o-mini 共 6 模型，provider/tier/token_limit）（MOD-INF-039） | production |
| ML 模型登记表 | `docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml`（REG-ML-001） | ML 训练产物唯一真源：8 条目，晋升状态机 candidate/staging/production/archived（对标 MLflow Model Registry，但不用 MLflow） | active |
| 价格表 | `config/model_pricing.yaml` | 各 provider 输入/输出单价（glm/deepseek/openai_azure/anthropic），ModelRouter 成本归一化输入 | active |
| 嵌入模型登记 | `config/embedding_model_registry.yaml` | embedding 模型注册（含 local_path/gpu_memory_mb/latency_budget_ms），embedding_migrate.py 消费 | operational |
| 预算门 | `src/zephyr/governance/ops_governance/budget_engine.py`（+ `cost_router.py`/`cost_budget.py`） | BudgetEngine.pre_flight_check 被 OllamaChat/DeepSeekChat 调用，DENY 即阻断 | production |
| 运行时编排 | `src/zephyr/trading/auto_runtime_core.py` | AutoRuntimeCore（MOD-INF-035）：_OllamaProcessManager 管 Ollama 进程生命周期、_LocalModelBootstrap 编排本地模型栈启动、消费 DeepSeekChat/EmbeddingRouter/LocalModelScheduler | production |
| GPU 调度 | `src/zephyr/trading/gpu_consensus_scheduler.py` | GPU 共识调度（交易域与推理的显存协调） | production |
| NLP 推理 | `src/zephyr/nlp/nlp_inference.py` | 新闻情感零样本推理，复用 local_model 层 + CacheLayer（MOD-NLP-INFERENCE-001） | design（头部标注） |
| 实验跟踪 | `src/zephyr/experiment_tracking/`（FallbackBackend JSON 单一后端） | MLflow 已于 2026-08 退役（51 号备忘），run 记录存本地 JSON | production |

**实测缺口清单**（本文施工对象）：

| 缺口 | 实测依据 |
|---|---|
| L2/L3 统一入口缺失 | LLMGateway（L3）与 OllamaChat/DeepSeekChat（L2/L3 直连）签名不互通；LLMGateway.route() 仅按 hint 映射 provider，不接 ModelRouter |
| MCP 动态发现缺失 | tool_contracts.yaml / mcp.json 均为静态注册；`src/` 下无 MCP Client 侧 list_tools 动态发现实现 |
| 推理优化未施工 | `src/` Grep `llama.cpp|llama_cpp|GPTQ` 零命中；00_index §1「显存 14→4GB」无代码对应 |
| 模型注册三处分裂无对账 | MOD-INF-039 dict / REG-ML-001 YAML / llm_gateway `_build_providers()` 各自维护模型事实 |
| mcp.json ↔ tool_contracts.yaml 漂移 | mcp.json 有 sandbox/red_blue_validator/clone_guard 而 tool_contracts.yaml 无；tool_contracts.yaml 有 resource_optimization 而 mcp.json servers 段无 |

---

## 3. 设计决策

### 3.1 三层运行时设计：保留三层概念，统一入口只落到 L2/L3 代码侧

**决策**：L1 Trae / L2 Local Ollama / L3 API 三层分工维持 [04_architecture_principles_decisions/README.md](../../04_architecture_principles_decisions/README.md) 既定表述（L1 人在环免费 → L2 24/7 零成本 → L3 夜班/高价值付费），但**代码统一入口只做 L2/L3**——新建薄门面统一 `ask()` 与 `call(messages)` 两套签名，按 ModelRouter 路由决策分发到 OllamaChat（L2）或 LLMGateway（L3）。

**Why**：

- 成本三角是硬约束：L2 零边际成本但能力上限 qwen3:8b；L3 按 token 付费，个人资金约束下必须默认 L2、显式升级 L3。已有 BudgetEngine + ModelRouter 提供了门控件，缺的是单一入口把门控件串起来。
- L1 不进代码：61 号备忘已裁定不做 agent 编排系统（多 AI 协作 = 人调度多会话），L1 本质是人在 IDE 的工作方式，给它建代码接口 = 过度工程。
- 薄门面而非重写：LLMGateway 与 local_model 层均为 production，重写合并会破坏既有消费者（auto_runtime_core、nlp_inference、model_profiling）；门面只做协议适配 + 路由分发。

**考虑过的替代方案**：

| 方案 | 为什么不选 |
|---|---|
| 合并 LLMGateway 与 local_model 为单模块 | 破坏面大（MOD-INF-016/019/042 三蓝图消费者众多），收益只是少一层适配 |
| 简化为两层（本地+API），删 L1 概念 | L1 是施工方式事实（人+Trae），删概念不影响代码但会让架构图失真；保留概念、不建代码即可 |
| 引入 LiteLLM 等外部统一网关库 | 新增重依赖，且项目已有 LSG 扫描/预算门等自研横切件，外部库接入成本高、锁定风险大（约束六：依赖锁定） |

### 3.2 MCP 工具调用设计：静态注册为底，动态发现为增强

**决策**：维持 `config/mcp.json`（SSoT）+ `tool_contracts.yaml`（契约）静态注册为**治理底座**，Phase 2 起增加 Client 侧动态发现——MCP Client 连接后 `list_tools()` 拉取实况，与契约文件 diff，**发现即校验**（未知工具告警 + 默认拒绝写操作），不是绕过注册表直接放行。

**Why**：

- 静态注册是治理必需品：MCP Triple Gate（00_index §3.3）要求工具白名单可审计，纯动态发现会让「新增工具零代码改动」变成「新增工具零审查」，与 HB-SEC 硬边界冲突。
- 动态发现解决的是**漂移检测**而非**免注册**：mcp.json ↔ tool_contracts.yaml 已实测漂移（§2.4），运行时 list_tools 与静态契约对账能把漂移从「人工抽查」变成「每次连接自动校验」。
- 业界对标（2026 年登记）：官方 MCP Registry（registry.modelcontextprotocol.io REST API，2025-09 上线，2026 年已成生态骨干）与 Microsoft 365 Copilot 的 dynamic tool discovery 均采用「运行时拉取 + 逐工具校验（XPIA 检查）」模式——与本决策同构，校验环节不可省。

**考虑过的替代方案**：

| 方案 | 为什么不选 |
|---|---|
| 纯动态发现（无静态契约） | 违反 MCP Triple Gate / HB-SEC 工具白名单要求 |
| 接入官方 MCP Registry 公共注册中心 | 面向公共 server 生态；本项目 server 全部自建内网，公共注册中心无适用场景，且 30Mbps 网络下引入外网依赖 |
| 保持纯静态、不做发现 | 漂移问题无解（已实测发生），长期累积成隐性故障源 |

### 3.2.1 业务侧 MCP Server 规划（交易域）

> 源：集成架构 §5.2~5.4（草稿 `.runtime/aidrafts/09_drafts_audit/架构图/集成架构.md`，2026-08-17 读取核实）。现有 11 个 server 是施工治理侧设施；本节登记**业务侧**规划，两者共用 mcp.json 静态注册底座与 §3.2 的发现即校验机制。

| MCP Server | 提供能力 | 消费 Agent | 安全等级 | 建设时序（集成架构 §5.4） |
|---|---|---|---|---|
| 行情数据 Server | tools: get_kline / get_tick / get_financial | 策略/研究 Agent | 只读 | Phase 1 ✅能建 |
| 知识图谱 Server | resources: knowledge_graph / research_notes | 研究/进化 Agent | 只读 | Phase 2 ✅能建 |
| 因子计算 Server | tools: calculate_factor / backtest_factor | 研究/进化 Agent | 只读+计算 | Phase 2 ✅能建 |
| 运维监控 Server | tools: health_check / restart_service / query_logs | 运维 Agent | 写操作需审批 | Phase 3 ✅能建 |
| 交易执行 Server | tools: place_order / cancel_order / query_position | 策略 Agent（受限） | 写操作需人工审批 | **Phase 4 ❌不能建**（QP-02 门禁未满足，登记 §5 不做清单） |

**安全边界四规则**（集成架构 §5.3.2，Host 层强制执行）：①MCP Server 不可读取完整对话历史（Host 层过滤，仅传必要上下文）；②MCP Server 之间不可互相通信（Host 层隔离，跨 Server 交互由 Host 协调）；③交易类写操作必须人工审批（C-031 协作策略：写操作→推送审批→人工确认→执行）；④MCP 通信禁止传输持仓/策略数据（B-011/B-013.5 在 MCP 层同样生效）。

**无状态缓存**：适配 MCP 2026-07-28 规范 tools/list 缓存 ttlMs——行情数据 Server ttlMs=3000（3 秒 Tick 刷新）、知识图谱 Server ttlMs=3600000。

### 3.2.2 MCP Triple Gate 工程裁定

> 源：26-D-SECURITY §8.2.3（草稿 `.runtime/aidrafts/09_drafts_audit/依赖图/26-D-SECURITY-安全域.md`，2026-08-17 读取核实）。

- **llm_proxy.exe 双重角色**：所有 MCP 工具调用（无论本地/远程）必经 llm_proxy.exe 安全代理扫描——本地 MCP 调用走「Agent→llm_proxy.exe（安全扫描，不走出站白名单）→localhost MCP 服务器」；远程 MCP 调用走「Agent→llm_proxy.exe（安全扫描+出站白名单约束）→远程 MCP 服务」。llm_proxy.exe 同时承担安全代理（扫描全部 MCP 流量）与出站代理（仅远程流量受出站白名单约束）双重角色，Triple Gate 代理层复用该架构，不另建独立网关进程。
- **传输层裁定**：本地 MCP = localhost HTTP+SSE（不出站）；**STDIO 传输层禁用**——本系统为 Windows 单机，STDIO 无消毒执行 OS 命令的攻击面（2026.4-5 OX Security/CSA 披露 20 万+实例受 RCE 影响）在本部署形态下无存在必要。
- **注册时扫描**：MCP 工具注册时执行 MCP-Scan 扫描，剥离工具描述中的指令性语言；工具调用输出过 LSG G3 输出审查层验证（与 09 号文 P0 统一入口接线对齐）。
- **威胁证据（裁定依据登记）**：MCPTox（AAAI-26，2026-02）实测工具投毒攻击成功率 72.8%（o1-mini，拒绝率 <3%）；Snyk ToxicSkills（2026）实测 36.8% 社区 Agent 技能含安全缺陷（76 个已确认恶意载荷）。

### 3.3 推理优化设计：GGUF/Ollama 为主路径，GPTQ INT4 实证否决

**决策**：本地推理优化主路径 = **Ollama 托管的 GGUF 量化模型**（现状已是，qwen3:8b）；不引入 llama.cpp 独立集成（Ollama 内核即 llama.cpp）；**GPTQ INT4 不采用**。显存管理靠既有 EmbeddingRouter LRU 淘汰 + gpu_consensus_scheduler 协调，不新建显存调度器。

**Why（2026 年实证依据，规则 6 前沿扫描登记）**：

- RTX 3090 是 Ampere 架构，无原生 INT4 tensor core。TechRxiv 2026-02《De-quantization Penalties for Interactive LLM Inference on Prosumer GPUs》实测：AutoGPTQ 4-bit 在 B=1 交互解码下比 FP16 **慢 1.3~2.2×**（反量化开销超过带宽节省），只有显存收益；GGUF Q4_K_M（llama.cpp 成熟 LUT 内核）在 3090 上 7B 模型约 42 tok/s、显存约 4.1GB（对比 FP16 约 14GB）。
- 结论：00_index §1「llama.cpp+GPTQ INT4 显存 14→4GB」的方向对（量化压缩显存成立），但技术选型应修正为 **GGUF Q4_K_M**——GPTQ 在 3090 上显存收益相同、速度反而劣化。00_index 表述修订见 Q6（本文无权改 00_index）。
- 不引入独立 llama.cpp：Ollama 已封装 llama.cpp 内核并提供进程管理/模型拉取/HTTP API，auto_runtime_core 的 `_OllamaProcessManager` 已管其生命周期；绕过 Ollama 直装 llama.cpp = 重复建设 + 两套进程管理。

**考虑过的替代方案**：

| 方案 | 为什么不选 |
|---|---|
| GPTQ INT4（AutoGPTQ/ExLlamaV2） | 3090 无 INT4 tensor core，实证反减速；ExLlamaV2 对新模型 GQA 支持需 patched fork，维护成本高 |
| vLLM + AWQ 高吞吐服务 | 面向多并发 serving；项目低并发（个人项目），且 vLLM 对 Windows 单机支持差、显存常驻开销大 |
| bitsandbytes NF4 | 定位原型/notebook 场景，无生产 C++ 运行时，显存比 K-quants 多约 12% |
| 更大本地模型（13B+ FP16） | 13B FP16 ≈ 26GB 超 21.6GB 硬上限；8B Q4_K_M（约 5GB）是 3090 上的甜点位 |

**显存管理的时段维度（GPU 分时调度）**：

> 源：12-D-ML-TRAIN §8.1（训练视角）+ 24-D-INFRA-RUNTIME §8.3（运行时视角）+ 13-D-ML-SERVE §8（推理视角），草稿位于 `.runtime/aidrafts/09_drafts_audit/依赖图/`，2026-08-17 读取核实。本地 LLM 推理显存配额服从该时段表，由既有 gpu_consensus_scheduler 执行，本文不新建调度器。

| 时段 | GPU 模式 | 推理侧显存 | 训练侧显存 | 切换触发 |
|---|---|---|---|---|
| 盘前（08:30-09:00） | 推理模型加载 | 8-10GB | ❌禁止训练 | 定时加载推理模型 |
| 盘中（09:15-15:00） | 推理优先 | 8-10GB（Whisper+LLM-7B+风控NN） | **0GB**（HC-01 交易时段保护） | — |
| 午休（11:30-13:00） | LLM 最小集+轻量训练 | 4GB | 轻量训练（小模型） | 定时切换 |
| 盘后（15:00-15:30） | 推理→训练切换中 | 4GB→卸载 | 16-18GB 加载中 | 定时切换 |
| 夜间（15:30-08:30） | 训练优先 | LLM 最小集 4GB（与训练互斥时分共享） | 16-18GB 全量训练 | 定时切换 |

- **时段优先级**：回测 > 推理 > 训练（GPU Resource Manager 时段优先调度，15-D-DATA-ENG / 21-D-KNOWLEDGE 依赖图同口径登记）。
- **风控 NN 常驻**：风控 NN 常驻显存 2GB，任何时段（含 OOM 紧急卸载）不可卸载（24-D-INFRA-RUNTIME §8.3.2/§8.4.2）。
- **权重 CPU RAM 热备**：推理/训练模型权重在 CPU RAM 保持热备——首次加载后不释放、仅从 GPU 卸载，恢复约 5s；时段全量切换约 60s（16-18GB 权重经 CPU RAM DMA 到 GPU）。
- **异常处置矩阵**（24-D-INFRA-RUNTIME §8.3.2）：OOM→终止当前 GPU 任务+卸载非必要模型+保留风控 NN，释放显存后重载最小集；温度 >85°C（nvidia-smi 监控）→降频 GPU+减少并发推理+告警，<80°C 后恢复；推理延迟 >2×基线（P5 自监控）→切换轻量模型+告警，延迟恢复后切回原模型；驱动崩溃→P5 进程重启+降级 CPU 推理+告警。
### 3.4 模型注册设计：三处收敛对账，不建第四套，明确不用 MLflow

**决策**：模型注册 SSoT 分层固定——**ML 训练产物**归 REG-ML-001（`model_registry.yaml`，晋升状态机 G1-G9 门禁见 62 号文）；**推理运行时模型**归 MOD-INF-039（`model_registry.py` dict）；**provider 价格**归 `config/model_pricing.yaml`。施工内容 = 三者对账校验（脚本比对模型名/tier/价格一致性），**不新建注册系统，不重新引入 MLflow**。

**Why**：

- MLflow 退役是已定裁定（51 号备忘，2026-08-16 执行完毕）：外部 UI 违反「集成现有 frontend」偏好、全量包对个人+AI 项目过重。任何「轻量 MLflow 替代平台」（ZenML/W&B/ClearML）同属外部 MLOps 平台，一并排除。
- 三处分裂的正确解法不是合并而是**对账**：三处服务不同生命周期阶段（训练产物晋升 / 运行时路由 / 成本计费），强行合一会把治理登记（human_gated）与运行时配置（ai_modifiable）的自治等级搅混。
- REG-ML-001 自身定位已写明「对标 MLflow Model Registry 核心组件」——功能等价物已存在，无需外部平台。

**考虑过的替代方案**：

| 方案 | 为什么不选 |
|---|---|
| 重新引入 MLflow Model Registry | 已被 51 号备忘裁定退役并执行卸载 |
| 统一为单一 YAML 注册表 | 混淆 human_gated（治理登记）与 ai_modifiable（运行时配置）自治等级；62 号文晋升门禁依附 REG-ML-001，迁移成本高 |
| W&B / ZenML / ClearML 轻量平台 | 同 MLflow 退役根因：外部平台+重依赖，违反施工约束 |

**注册治理字段补充（对账校验口径）**：

> 源：12-D-ML-TRAIN §11.1 合规约束（草稿 `.runtime/aidrafts/09_drafts_audit/依赖图/12-D-ML-TRAIN-训练域.md`，2026-08-17 读取核实）。以下字段并入 Phase 3.1 三向对账脚本的校验维度，与 REG-ML-001 + 运行时注册（MOD-INF-039）对账口径对齐。

| 治理字段 | 口径 | 对账校验要求 |
|---|---|---|
| training_data_hash | 每次训练生成训练数据集 SHA-256 指纹，写入模型注册表 training_data_hash 字段（数据集加载时自动计算，不可变） | REG-ML-001 条目必填；对账校验非空且与训练日志记录一致 |
| 模型版本四元组 | 语义化版本号 + code_hash + param_hash + training_data_hash 四元组绑定，版本不可变 | 对账校验四元组完整性，缺一即判漂移 |
| 训练审计哈希链 | 每次训练的完整参数+数据集版本+性能指标+审批记录写入模型日志，哈希链保护，保留 ≥5 年 | 审计链完整性纳入对账抽检范围 |

### 3.5 数据增强边界：归属 D-DATA 域，本文只声明集成点

**决策**：数据增强（TimeGAN/条件扩散/轻量增强）**不是 LLM 基础设施的职责**——其真源是 D-DATA 域 95 号能力「金融时序数据增强」（`docs/02_enterprise_architecture/09_ai_architecture/依赖图/02-D-DATA-数据域.md` L109，含轻量增强+TimeGAN/RTSGAN+FWT 检索增强扩散+GBM-Diffusion，P2）。本文只声明：L2 本地推理层为数据增强的生成模型推理提供运行时承载（若该能力未来落地且需要本地推理）。

**Why**：

- 规则 16（真源唯一）：数据增强的需求、选型、质量管理（KS test/增强比例 ≤30%/synthetic 标注）已在 D-DATA 依赖图登记，本文复制 = 双真源噪音。
- FWT 检索增强扩散要求 GPU≥40GB（同文件 L759），超出 3090 24GB 硬约束——该子项在本硬件上不可行，属远期/换硬件后再议；TimeGAN 与轻量增强（时间扭曲/幅度缩放/Jittering 等）可在 3090 运行，但归 D-DATA 域施工。

### 3.6 成本治理设计：LLMDeg-0~4 五级降级 + Redis 预算池（BudgetEngine 语义扩展）

**决策**：BudgetEngine 由「pre_flight_check 二元门控」语义扩展为「五级成本降级 + 三维预算池」——DENY 不再是唯一终点，LLMDeg-1~3 提供渐退路径，LLMDeg-4 才是全阻断。降级数值按依赖图既定规格登记，本文不另立数值、不新建成本控制模块。

**预算额度与监控（源：13-D-ML-SERVE §8.3 A7 搬入段，草稿 `.runtime/aidrafts/09_drafts_audit/依赖图/13-D-ML-SERVE-推理域.md`，2026-08-17 读取核实）**：

| 维度 | 预算 | 监控频率 | 超预算处理 |
|---|---|---|---|
| 月度 API 总成本 | ¥500/月 | 日度 | >110% 降级至本地 LLM；>120% 暂停 API 调用 |
| 单日 API 成本 | ¥30/天（软限制） | 实时 | 超限→当日剩余时间降级至本地 LLM |
| 单次 API 调用成本 | ¥0.5/次 | 实时 | 超限→降级至本地 LLM 或拒绝 |
| 月度本地推理成本 | 电费 ~¥50/月 | 月度 | 无硬限制（电费可控） |

**五级降级策略（同源）**：

| 降级级别 | 触发条件（月度成本） | 降级行为 | 恢复条件 |
|---|---|---|---|
| LLMDeg-0（正常） | <80% 预算 | 全功能路由（API+本地） | — |
| LLMDeg-1（节约） | 80%~100% | 非关键任务 API→本地降级 | 回落至 80% 以下 |
| LLMDeg-2（严格） | 100%~110% | 仅战略层+反思 L2/L3 使用 API | 回落至 100% 以下 |
| LLMDeg-3（紧急） | >110% | 全部 API→本地降级+规则引擎兜底 | 人工确认后恢复 |
| LLMDeg-4（熔断） | >120% | 暂停所有 API 调用，仅本地+规则引擎 | 紧急人工介入+预算重置 |

**预算基础设施（源：25-D-INFRA-OPS §8.3.1 A7 搬入段，同草稿目录）**：

| 组件 | 实现 | 功能 |
|---|---|---|
| 预算池 | Redis Hash 存储 | 按月/按 Agent/按模型类型三维设置预算上限；超预算自动降级路由（API→本地） |
| Token 计数器 | Redis Counter + 持久化 | 实时统计 input/output token 用量，按 Agent/模型/时间维度聚合；每日快照至 Parquet |
| 成本仪表盘 | Grafana 仪表盘 5 视图 | ①日/周/月 LLM 成本趋势 ②各 Agent 成本占比 ③本地 vs API 成本对比 ④预算消耗速率 ⑤超预算告警 |

预算控制流程：每次调用前检查预算池余额 → 调用完成后更新 Token 计数器 → 消耗 ≥80% 触发告警 → ≥100% 自动降级（API→本地）→ 每日生成成本报告写 Parquet 归档。

**成本感知路由判据（13-D-ML-SERVE §8.3）**：API→本地降级成立条件 = 预算消耗 >80% 且性能损失 <5%；反向本地→API 升级条件 = 本地推理失败/质量不足。

**Why**：

- 个人资金约束下 ¥500/月 API 预算是硬上限，本地推理（电费 ~¥50/月）是降级的经济兜底；LLM 不在交易实时路径（§2.3），降级对交易业务无损。
- 与既有设施的关系：BudgetEngine.pre_flight_check 已被 OllamaChat/DeepSeekChat 消费（§2.4），五级降级是对 DENY 语义的细粒度化；落地点 = Phase 1.2 预算门接线时把 LLMDeg 级别注入 ModelRouter 路由决策，L2 默认优先与 LLMDeg-1「非关键任务转本地」同向。

---

## 4. 施工计划

> 铁律（规则 19）：凡新建模块，第一步用 `scripts/governance/apply_depgraph.py` 将依赖关系登记到 depgraph 设计态（status=planned），最后一步验证通过后 planned→production。禁止先施工后补登记。
> 04 号文（AutoRuntime Core）已填充 v0.2.1，其 §3.4 确认本文 Q3 接口假设成立，联动动作（大脑 LLM 调用点改经门面）列入 04 号文 Phase 1 步骤 1.4。

### Phase 0：登记与对齐（P1，纯治理无代码）

> **状态回写（2026-08-28 已闭环）**：0.1~0.3 三件已落地（depgraph 设计态登记 + 三处注册对账基线 + 漂移项裁定），见头部结案报告。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 0.1 | **depgraph 设计态登记**：用 `apply_depgraph.py` 登记新模块 `llm_runtime_gateway`（拟名，L2/L3 统一门面，归属 D_INTEGRATION，依赖 MOD-INF-016 协议 + MOD-INF-019 网关 + MOD-INF-042 local_model + MOD-INF-024 ModelRouter），status=planned | depgraph 查询可见 planned 节点 + 4 条设计态依赖边 |
| 0.2 | 三处模型注册对账基线：dump MOD-INF-039 dict、REG-ML-001 entries、`_build_providers()` 输出、model_pricing.yaml，人工过一遍不一致项 | 对账清单产出，不一致项全部有归属裁定 |
| 0.3 | mcp.json ↔ tool_contracts.yaml 漂移项裁定（sandbox/red_blue_validator/clone_guard/resource_optimization 四个不一致 server 的归属，见 Q8） | 漂移项收敛为 0 或登记为带理由的已知偏差 |

### Phase 1：L2/L3 统一入口（P1，核心施工）

> **状态回写（2026-08-31 已闭环）**：1.1 门面 `llm_runtime_gateway.py`（MOD-INF-051）已建（2026-08-28 GP0 批次）；1.2 预算硬门接线 + LLMDeg-0~4 注入路由决策已落码（infer 入口统一 `BudgetEngine.pre_flight_check`，DENY 阻断）；1.3 LSG 同闸门 fail-closed 已落地（L2 无旁路配置项）；1.4 route() 已接 MOD-INF-024 ModelRouter perf-aware 决策（返回 RoutingDecision 含 tier/reason/performance_score）。MOD-INF-051 [MATURITY] testing→production（#ARCH-301，2026-08-31）。预算门主维度 token→元成本切换见 #ARCH-303（在途）。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 1.1 | 新建 `llm_runtime_gateway` 门面：对外暴露单一 `infer(messages/prompt, complexity, max_cost)` 签名；内部按 ModelRouter.route() 决策分发——ECONOMY/MINIMAL 且本地能力命中 → OllamaChat（L2）；其余 → LLMGateway.call（L3） | 单测：同一会话 L2/L3 切换对调用方透明；签名仅一套 |
| 1.2 | 预算门接线：门面入口统一调 BudgetEngine.pre_flight_check（复用 OllamaChat/DeepSeekChat 既有模式），DENY 阻断；同时将 LLMDeg-0~4 降级级别（§3.6）注入 ModelRouter 路由决策 | 预算 DENY 场景单测通过；LLMDeg-1~4 触发时路由走向符合 §3.6 降级表 |
| 1.3 | LSG 安全扫描对齐：按 09 号文 v0.2.0 P0-1 裁定，L2/L3/Trae 三类通道同一 LSG 闸门（fail-closed），L2 本地路径**无旁路开关**（Q4 已闭环）；L2 路径经客户端工厂统一注入 LSG 网关（09 号文 §4.6 集成点假设，与本文门面同点落地） | L2 调用经 LSG 闸门的 L6 审计记录可见；代码中无 L2 旁路配置项 |
| 1.4 | LLMGateway.route() 接 ModelRouter：替换现有「hint 直接映射」实现，接入 MOD-INF-024 的 perf-aware 决策 | route() 返回含 tier/reason/performance_score 字段 |

### Phase 2：MCP 动态发现与推理优化落地（P2）

> **状态回写（2026-08-31）**：2.3 GGUF 模型管理件已施工（config/gguf_vram_budget.yaml + `src/zephyr/intelligence/gguf_model_manager.py` MOD-INF-060，超预算加载阻断）；2.4 qwen3:8b 基线考试已施工（`scripts/run_qwen3_baseline_exam.py`，成绩单落盘 data/model_profiles/ benchmark_20260830_154428.jsonl）。**2.1/2.2（MCP Client 动态发现 + 漂移对账入遥测）未施工**，P2 排期待定。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 2.1 | MCP Client 发现件：连接后 list_tools 拉取实况，与 tool_contracts.yaml 契约 diff；未知工具告警 + 默认拒绝写操作（safety_level M/H 必须契约命中才放行）；传输层仅 localhost HTTP+SSE、STDIO 禁用（§3.2.2）；工具注册时执行 MCP-Scan 扫描并剥离指令性语言 | 人为增删一个 mock 工具，diff 报告正确检出；STDIO 类型 server 配置被拒绝 |
| 2.2 | 漂移对账入遥测：diff 结果 emit 到 telemetry（复用 MOD-INF-015），漂移持续 >24h 升级告警 | telemetry.metrics_snapshot 可见 drift 指标 |
| 2.3 | GGUF 模型管理件：登记 Ollama 已拉模型清单（ModelDiscovery 已有枚举能力）+ 显存预算表（每模型加载显存 vs 21.6GB 上限，时段配额按 §3.3 时段表），新模型引入前查表 | 显存预算表落 config/（human_gated），超预算加载被阻断 |
| 2.4 | 本地推理质量基线：用 model_profiling 的 exam 链路对 qwen3:8b 跑基线考试，成绩单存档（为后续换模型/换量化档位提供对比基准） | 基线成绩入库 data/model_profiles/ |

### Phase 3：注册对账自动化与收口（P2）

> **状态回写（2026-08-31 已闭环）**：3.1 注册对账脚本已施工（`scripts/governance/audit_llm_registry_reconciliation.py`，MOD-INF-039 ↔ REG-ML-001 ↔ model_pricing.yaml 三向比对）；3.2 本文 Phase 完成状态回写 = 本条及头部 2026-08-31 回填；3.3 成熟度翻转已随 #ARCH-301 闭环（llm_runtime_gateway MOD-INF-051 [MATURITY] production，2026-08-31）。

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 3.1 | 注册对账脚本：MOD-INF-039 ↔ REG-ML-001 ↔ model_pricing.yaml 三向比对（模型名/tier/价格 + §3.4 治理字段 training_data_hash/版本四元组/审计哈希链），CI 或 commit gate 挂载 | 对账脚本零误报跑通；人为改一处价格或删一个治理字段，对账检出 |
| 3.2 | 文档收尾：本文 Phase 完成状态回写；00_index §1 过期表述（MLflow/GPTQ）修订申请走 Q6 裁定 | Q6 有裁定结论 |
| 3.3 | **depgraph 状态翻转**：`llm_runtime_gateway` 全部验收通过后 planned→production | depgraph 查询状态=production |

**明确不在施工计划内**：数据增强实现（归 D-DATA 域）、llama.cpp/GPTQ 集成（§3.3 已否决）、MLflow 类平台（§3.4 已否决）、交易执行 MCP Server（§3.2.1 Phase 4 裁定 ❌不能建）。

---

## 5. 不做什么

| 不做项 | 理由（判定基准：system_charter §2 硬边界 + 实测） |
|---|---|
| 分布式推理 / 多卡并行 / vLLM 集群 | 单机单卡 3090 硬约束；无集群 |
| 模型训练（SFT/全量微调/MAML/EWC） | 训练轨归 `src/zephyr/ml_train/` 与 13 号备忘体系；本文只管推理侧 |
| GPU 集群调度 | 单卡无调度对象；既有 `gpu_consensus_scheduler.py` 已覆盖单机显存协调（含 §3.3 时段维度） |
| 高并发推理服务（连续批处理/多租户） | 个人项目低并发；LLM 不在交易实时路径（T+1 日频） |
| 重新引入 MLflow 或同类外部 MLOps 平台（W&B/ZenML/ClearML） | 51 号备忘已裁定 MLflow 退役并执行完毕，同类平台同根因排除 |
| llama.cpp 独立集成 / GPTQ INT4 / ExLlamaV2 | §3.3：Ollama 已含 llama.cpp 内核；GPTQ 在 3090（Ampere 无 INT4 tensor core）实证反减速 |
| 数据增强实现（TimeGAN/扩散/轻量增强） | 归 D-DATA 域 95 号能力；其中 FWT 扩散需 GPU≥40GB 属远期不可行项 |
| agent 编排系统 / L1 Trae 代码化 | 61 号备忘已裁定不做 agent 编排；L1 是人的工作层非代码 |
| 公共 MCP Registry 接入 | server 全部自建内网，公共注册中心无适用场景 |
| 13B+ 本地模型 FP16 常驻 | ≈26GB 超 21.6GB 显存硬上限 |
| 交易执行 MCP Server（place_order/cancel_order/query_position 工具化） | 集成架构 §5.4 Phase 4 裁定 ❌不能建（QP-02 门禁未满足）；交易写操作维持 C-031 人工审批通道，不经 MCP（§3.2.1） |
| MCP STDIO 传输层 | 26-D-SECURITY §8.2.3 裁定禁用：Windows 单机，STDIO 无消毒执行 OS 命令的攻击面无存在必要；本地 MCP 一律 localhost HTTP+SSE（§3.2.2） |
| 独立 MCP 安全网关进程 | Triple Gate 代理层复用 llm_proxy.exe 双重角色架构（§3.2.2），不另建进程 |

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | MCP 工具调用标准化的实现路径？ | 部分已定·细节待裁定 | 方向已定：静态契约（tool_contracts.yaml）为治理底座 + Client 动态发现做漂移对账（§3.2）。待裁定：「未知工具默认拒绝写操作」的放行审批流挂在哪个既有门禁（候选：capability gate / commit gate） |
| Q2 | llama.cpp+GPTQ INT4 的显存压缩是否在 RTX 3090 上验证过？ | 已实证·待裁定改表述 | 2026 实证：GGUF Q4_K_M 在 3090 上 7B≈4.1GB/约42tok/s；GPTQ INT4 显存收益相同但 B=1 反减速 1.3~2.2×。本文已按 GGUF 路径定决策；00_index §1「llama.cpp+GPTQ INT4」表述修订待 Owner 裁定（见 Q6） |
| Q3 | 与 04 号文（AutoRuntime Core）的运行时接口对齐 | **已闭环（假设成立）** | 04 号文 v0.2.1 已填充，其 §3.4 确认本文假设成立：AutoRuntime Core 继续承担 Ollama 进程管理与本地模型栈 boot（`_OllamaProcessManager`/`_LocalModelBootstrap` production），`llm_runtime_gateway` 门面被 AutoRuntime Core 消费而非取代其编排职责；联动动作（大脑 LLM 调用点 DeepSeekChat/EmbeddingRouter/LocalModelScheduler 消费处改经门面入口）列入 04 号文 Phase 1 步骤 1.4，不新建模块 |
| Q4 | L2 本地推理是否强制过 LSG 安全扫描？ | **已闭环（09 已裁定：同闸门无旁路）** | 09 号文 v0.2.0 已填充，P0-1 裁定「本地 Ollama / API / Trae 三类通道同一 LSG 闸门」fail-closed 全量拦截——本文原假设（L2 输入扫描开启、输出扫描抽样）被该裁定取代，L2 不保留旁路配置项；09 号文 Q2 对本文集成点的假设（LLM 客户端工厂统一注入网关 + SecurityContext 传递 + MCP 工具调用过 L4 authorize_tool_call）与本文 Phase 1.3/2.1 方向一致，双向确认。Phase 1.3 验收标准已同步修订 |
| Q5 | 11 号文（证据技能路由）对模型路由的运行时依赖 | **已闭环（假设成立）** | 11 号文 v0.2.0 已填充：级联路由 L3 成本路由消费 MOD-INF-024 ModelRouter（只消费不改结构，MODIFY-GUARD），护照消费 `capability_passport.py`（MOD-INF-034），不直接消费本文统一门面——本文 Q5 假设成立，Phase 1 门面签名无需回看 |
| Q6 | 00_index §1「模型注册(MLflow)」与「llama.cpp+GPTQ INT4」两处表述已过期 | 待裁定（本文无权改 00_index） | MLflow 已退役（51 号备忘 v1.2.13 执行完毕）；GPTQ 已实证否决（§3.3）。建议 00_index 修订为「模型注册(REG-ML-001+运行时注册对账)」「推理优化(GGUF 量化,Ollama 托管)」，由 AI-FILL-00 或 Owner 落笔 |
| Q7 | llm_gateway.py 头部蓝图标注不一致 | 待裁定 | 文件头 `[BLUEPRINT] MOD-INF-009` 与 docstring `MOD-INF-019: Agent Spec — LLM Gateway` 不一致；module_translation_registry/depgraph 真源需核对后订正其一 |
| Q8 | mcp.json ↔ tool_contracts.yaml 漂移项归属 | 待裁定 | sandbox/red_blue_validator/clone_guard 仅见于 mcp.json；resource_optimization 仅见于 tool_contracts.yaml。是有意分层还是漏登记，Phase 0.3 前需 Owner 裁定 |
| Q9 | 09_ai_architecture 目录被并行收口流程隔离搬迁事件 | 待裁定 | 2026-08-17 晚 coord 收口（reflog 3c9bb5a60b 前后）将整目录迁至 .runtime/quarantine/gova_leftover_20260817/（理由：66 文件缺 frontmatter 违反 TTL-METADATA 门禁 + DIRECTORY-CONTRACT 禁 csv）。本文已回迁原路径且 implementation_plans/ 同级文档已恢复（00/02 等链接可解析），但 依赖图/架构图 子树仍在隔离区——§3.5 对 02-D-DATA-数据域.md 的引用暂不可解析（本轮 §3.2.1/§3.2.2/§3.3/§3.4/§3.6 新增引用的依赖图与架构图内容以 `.runtime/aidrafts/09_drafts_audit/` 草稿副本为读取源，已在各节标注）；子树恢复待 GOVA 会话/Owner 裁定（恢复清单见 .runtime/ai00_audit_pause_20260817.md 第四节第 4 步） |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景+21 项已施工设施实测盘点+5 项实测缺口；§3 五项设计决策（三层运行时/MCP/推理优化/模型注册/数据增强边界）含替代方案；§4 Phase 0→3 施工计划（depgraph L1 铁律）；§5 不做清单；§6 开放问题 Q1~Q8 | AI-FILL-10 填充；关键实测修正：MLflow 已退役（51 号备忘）、GPTQ 在 3090 实证反减速（GGUF 替代）、数据增强归属 D-DATA 域；04/06/09/11 依赖文档未填充按降级处理（接口假设入 Q3~Q5） |
| 2026-08-17 | 0.2.1 | 开放问题新增 Q9（目录隔离搬迁事件记录）+ 拼接处空行修正 + doc_type 修正（implementation_plan→blueprint，按 doc_type_vocabulary 弃用映射 construction_plan→blueprint） | 并行 coord 收口流程将 09_ai_architecture 整树迁至 quarantine，本文回迁并记录事件待裁定；TTL-METADATA 门禁 hard block 要求合法 doc_type |
| 2026-08-17 | 0.2.2 | Q9 表述更新：implementation_plans 已恢复、依赖图/架构图子树仍在隔离区 | 提交后复核发现 02-D-DATA-数据域.md 引用暂不可解析，修正事件记录准确性 |
| 2026-08-17 | 0.3.0 | 回填五项：§3.2.1 交易域 MCP Server 规划（5 Server+安全边界 4 规则+ttlMs，Phase 4 交易执行 Server ❌不能建登记 §5）；§3.2.2 MCP Triple Gate 工程裁定（llm_proxy.exe 双重角色/STDIO 禁用/MCP-Scan 注册扫描/MCPTox 72.8%+ToxicSkills 36.8% 威胁证据）；§3.3 显存管理补 GPU 时段分时维度（盘中训练 0GB/推理 8-10GB、夜间训练 16-18GB、风控 NN 常驻 2GB 不可卸载、CPU RAM 热备 ~5s、OOM/温度>85°C/延迟>2×基线处置、时段优先级回测>推理>训练）；§3.4 注册治理字段补充（training_data_hash/版本四元组/审计哈希链≥5 年，对齐 REG-ML-001+MOD-INF-039 对账口径）；新增 §3.6 成本治理（LLMDeg-0~4 五级降级+月¥500/日¥30/单次¥0.5 预算+Redis 预算池月/Agent/模型三维+Token 计数器日快照 Parquet+成本仪表盘 5 视图+API→本地降级条件预算>80%且性能损失<5%）；开放问题 Q3/Q5 闭环（04 v0.2.1/11 v0.2.0 确认假设成立）、Q4 按 09 v0.2.0 P0-1 裁定闭环（L2 同闸门无旁路）并同步修订 Phase 1.2/1.3/2.1/2.3/3.1 与 §5 不做清单 | AI-FILL-10-R2 回填；源：.runtime/aidrafts/09_drafts_audit 依赖图 12/13/24/25/26 + 架构图/集成架构 §5.2~5.4 + 04/09/11 号文接口复审；依赖图/架构图子树仍在隔离区（Q9），以草稿副本为读取源并逐节标注 |
| 2026-08-31 | 0.4.0 | 施工闭环状态回写（Phase 3.2 文档收尾执行）：头部结案报告追加 2026-08-31 回填（Phase 1 GP1 预算硬门/路由级联已落码 + MOD-INF-051 production 翻转 #ARCH-301；Phase 2.3 显存预算表 config/gguf_vram_budget.yaml + gguf_model_manager.py MOD-INF-060；Phase 2.4 qwen3:8b 基线 data/model_profiles/；Phase 3.1 注册对账脚本 audit_llm_registry_reconciliation.py）；原"预算硬门/路由级联属 GP1 未做"表述划除；§1 状态行 + §4 Phase 0/1/2/3 状态回写；frontmatter status draft→active | 长城任务 2026-08-30/31 施工完毕，文档状态与代码实证对齐；遗留仅 Phase 2.1/2.2 MCP 动态发现（P2）+ Q1/Q6/Q7/Q8/Q9 待裁定 |

---

*维护者：AI 架构协调者*