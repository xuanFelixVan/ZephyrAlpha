---
ttl: permanent
doc_type: blueprint
title: LLM 基础设施施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.1"
date: 2026-08-17
topic: llm_infrastructure
scope: 09_ai_architecture
---

# LLM 基础设施施工图

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
| 状态 | draft（骨架填充完成，待施工） |

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

### 3.5 数据增强边界：归属 D-DATA 域，本文只声明集成点

**决策**：数据增强（TimeGAN/条件扩散/轻量增强）**不是 LLM 基础设施的职责**——其真源是 D-DATA 域 95 号能力「金融时序数据增强」（`docs/02_enterprise_architecture/09_ai_architecture/依赖图/02-D-DATA-数据域.md` L109，含轻量增强+TimeGAN/RTSGAN+FWT 检索增强扩散+GBM-Diffusion，P2）。本文只声明：L2 本地推理层为数据增强的生成模型推理提供运行时承载（若该能力未来落地且需要本地推理）。

**Why**：

- 规则 16（真源唯一）：数据增强的需求、选型、质量管理（KS test/增强比例 ≤30%/synthetic 标注）已在 D-DATA 依赖图登记，本文复制 = 双真源噪音。
- FWT 检索增强扩散要求 GPU≥40GB（同文件 L759），超出 3090 24GB 硬约束——该子项在本硬件上不可行，属远期/换硬件后再议；TimeGAN 与轻量增强（时间扭曲/幅度缩放/Jittering 等）可在 3090 运行，但归 D-DATA 域施工。

---

## 4. 施工计划

> 铁律（规则 19）：凡新建模块，第一步用 `scripts/governance/apply_depgraph.py` 将依赖关系登记到 depgraph 设计态（status=planned），最后一步验证通过后 planned→production。禁止先施工后补登记。
> 04 号文（AutoRuntime Core）尚未填充，本文与运行时机脑的接口按 §6 Q3 的假设先行，04 填充后对齐。

### Phase 0：登记与对齐（P1，纯治理无代码）

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 0.1 | **depgraph 设计态登记**：用 `apply_depgraph.py` 登记新模块 `llm_runtime_gateway`（拟名，L2/L3 统一门面，归属 D_INTEGRATION，依赖 MOD-INF-016 协议 + MOD-INF-019 网关 + MOD-INF-042 local_model + MOD-INF-024 ModelRouter），status=planned | depgraph 查询可见 planned 节点 + 4 条设计态依赖边 |
| 0.2 | 三处模型注册对账基线：dump MOD-INF-039 dict、REG-ML-001 entries、`_build_providers()` 输出、model_pricing.yaml，人工过一遍不一致项 | 对账清单产出，不一致项全部有归属裁定 |
| 0.3 | mcp.json ↔ tool_contracts.yaml 漂移项裁定（sandbox/red_blue_validator/clone_guard/resource_optimization 四个不一致 server 的归属，见 Q8） | 漂移项收敛为 0 或登记为带理由的已知偏差 |

### Phase 1：L2/L3 统一入口（P1，核心施工）

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 1.1 | 新建 `llm_runtime_gateway` 门面：对外暴露单一 `infer(messages/prompt, complexity, max_cost)` 签名；内部按 ModelRouter.route() 决策分发——ECONOMY/MINIMAL 且本地能力命中 → OllamaChat（L2）；其余 → LLMGateway.call（L3） | 单测：同一会话 L2/L3 切换对调用方透明；签名仅一套 |
| 1.2 | 预算门接线：门面入口统一调 BudgetEngine.pre_flight_check（复用 OllamaChat/DeepSeekChat 既有模式），DENY 阻断 | 预算 DENY 场景单测通过 |
| 1.3 | LSG 安全扫描对齐：L3 路径沿用 LLMGateway 内嵌 LSG；L2 路径输入/输出扫描策略待 09 号文裁定（Q4），当前先复用现有 LSG gateway 做输入扫描 | L2 输入扫描有明确开启/旁路配置项 |
| 1.4 | LLMGateway.route() 接 ModelRouter：替换现有「hint 直接映射」实现，接入 MOD-INF-024 的 perf-aware 决策 | route() 返回含 tier/reason/performance_score 字段 |

### Phase 2：MCP 动态发现与推理优化落地（P2）

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 2.1 | MCP Client 发现件：连接后 list_tools 拉取实况，与 tool_contracts.yaml 契约 diff；未知工具告警 + 默认拒绝写操作（safety_level M/H 必须契约命中才放行） | 人为增删一个 mock 工具，diff 报告正确检出 |
| 2.2 | 漂移对账入遥测：diff 结果 emit 到 telemetry（复用 MOD-INF-015），漂移持续 >24h 升级告警 | telemetry.metrics_snapshot 可见 drift 指标 |
| 2.3 | GGUF 模型管理件：登记 Ollama 已拉模型清单（ModelDiscovery 已有枚举能力）+ 显存预算表（每模型加载显存 vs 21.6GB 上限），新模型引入前查表 | 显存预算表落 config/（human_gated），超预算加载被阻断 |
| 2.4 | 本地推理质量基线：用 model_profiling 的 exam 链路对 qwen3:8b 跑基线考试，成绩单存档（为后续换模型/换量化档位提供对比基准） | 基线成绩入库 data/model_profiles/ |

### Phase 3：注册对账自动化与收口（P2）

| 步骤 | 内容 | 验收标准 |
|---|---|---|
| 3.1 | 注册对账脚本：MOD-INF-039 ↔ REG-ML-001 ↔ model_pricing.yaml 三向比对（模型名/tier/价格），CI 或 commit gate 挂载 | 对账脚本零误报跑通；人为改一处价格，对账检出 |
| 3.2 | 文档收尾：本文 Phase 完成状态回写；00_index §1 过期表述（MLflow/GPTQ）修订申请走 Q6 裁定 | Q6 有裁定结论 |
| 3.3 | **depgraph 状态翻转**：`llm_runtime_gateway` 全部验收通过后 planned→production | depgraph 查询状态=production |

**明确不在施工计划内**：数据增强实现（归 D-DATA 域）、llama.cpp/GPTQ 集成（§3.3 已否决）、MLflow 类平台（§3.4 已否决）。

---

## 5. 不做什么

| 不做项 | 理由（判定基准：system_charter §2 硬边界 + 实测） |
|---|---|
| 分布式推理 / 多卡并行 / vLLM 集群 | 单机单卡 3090 硬约束；无集群 |
| 模型训练（SFT/全量微调/MAML/EWC） | 训练轨归 `src/zephyr/ml_train/` 与 13 号备忘体系；本文只管推理侧 |
| GPU 集群调度 | 单卡无调度对象；既有 `gpu_consensus_scheduler.py` 已覆盖单机显存协调 |
| 高并发推理服务（连续批处理/多租户） | 个人项目低并发；LLM 不在交易实时路径（T+1 日频） |
| 重新引入 MLflow 或同类外部 MLOps 平台（W&B/ZenML/ClearML） | 51 号备忘已裁定 MLflow 退役并执行完毕，同类平台同根因排除 |
| llama.cpp 独立集成 / GPTQ INT4 / ExLlamaV2 | §3.3：Ollama 已含 llama.cpp 内核；GPTQ 在 3090（Ampere 无 INT4 tensor core）实证反减速 |
| 数据增强实现（TimeGAN/扩散/轻量增强） | 归 D-DATA 域 95 号能力；其中 FWT 扩散需 GPU≥40GB 属远期不可行项 |
| agent 编排系统 / L1 Trae 代码化 | 61 号备忘已裁定不做 agent 编排；L1 是人的工作层非代码 |
| 公共 MCP Registry 接入 | server 全部自建内网，公共注册中心无适用场景 |
| 13B+ 本地模型 FP16 常驻 | ≈26GB 超 21.6GB 显存硬上限 |

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | MCP 工具调用标准化的实现路径？ | 部分已定·细节待裁定 | 方向已定：静态契约（tool_contracts.yaml）为治理底座 + Client 动态发现做漂移对账（§3.2）。待裁定：「未知工具默认拒绝写操作」的放行审批流挂在哪个既有门禁（候选：capability gate / commit gate） |
| Q2 | llama.cpp+GPTQ INT4 的显存压缩是否在 RTX 3090 上验证过？ | 已实证·待裁定改表述 | 2026 实证：GGUF Q4_K_M 在 3090 上 7B≈4.1GB/约42tok/s；GPTQ INT4 显存收益相同但 B=1 反减速 1.3~2.2×。本文已按 GGUF 路径定决策；00_index §1「llama.cpp+GPTQ INT4」表述修订待 Owner 裁定（见 Q6） |
| Q3 | 与 04 号文（AutoRuntime Core）的运行时接口对齐 | 待 04 填充后对齐 | 04 尚未填充。本文假设：AutoRuntime Core 继续承担 Ollama 进程管理与本地模型栈 boot（现状代码已如此），`llm_runtime_gateway` 门面被 AutoRuntime Core 消费而非取代其编排职责。04 填充后需回读本节核对 |
| Q4 | L2 本地推理是否强制过 LSG 安全扫描？ | 待 09 填充后裁定 | 09 号文未填充。L3 路径 LSG 扫描已在 LLMGateway 内嵌；L2 本地模型输入多来自内部任务，全量扫描有延迟成本。假设：L2 输入扫描开启、输出扫描抽样，待 09 号文裁定 |
| Q5 | 11 号文（证据技能路由）对模型路由的运行时依赖 | 待 11 填充后对齐 | 11 未填充。假设：11 的技能路由消费 ModelRouter（MOD-INF-024）+ capability_passport（MOD-INF-034），不直接消费本文门面；若 11 需要统一推理入口，Phase 1 门面签名需回看 |
| Q6 | 00_index §1「模型注册(MLflow)」与「llama.cpp+GPTQ INT4」两处表述已过期 | 待裁定（本文无权改 00_index） | MLflow 已退役（51 号备忘 v1.2.13 执行完毕）；GPTQ 已实证否决（§3.3）。建议 00_index 修订为「模型注册(REG-ML-001+运行时注册对账)」「推理优化(GGUF 量化,Ollama 托管)」，由 AI-FILL-00 或 Owner 落笔 |
| Q7 | llm_gateway.py 头部蓝图标注不一致 | 待裁定 | 文件头 `[BLUEPRINT] MOD-INF-009` 与 docstring `MOD-INF-019: Agent Spec — LLM Gateway` 不一致；module_translation_registry/depgraph 真源需核对后订正其一 |
| Q8 | mcp.json ↔ tool_contracts.yaml 漂移项归属 | 待裁定 | sandbox/red_blue_validator/clone_guard 仅见于 mcp.json；resource_optimization 仅见于 tool_contracts.yaml。是有意分层还是漏登记，Phase 0.3 前需 Owner 裁定 |
| Q9 | 09_ai_architecture 目录被并行收口流程隔离搬迁事件 | 待裁定 | 2026-08-17 晚 coord 收口（reflog 3c9bb5a60b 前后）将整目录迁至 .runtime/quarantine/gova_leftover_20260817/（理由：66 文件缺 frontmatter 违反 TTL-METADATA 门禁 + DIRECTORY-CONTRACT 禁 csv）。本文已回迁原路径（frontmatter 合规），但同级 00/02/04 等文档仍在隔离区，本文相对链接暂不可解析；整树恢复待 GOVA 会话/Owner 裁定（恢复清单见 .runtime/ai00_audit_pause_20260817.md 第四节第 4 步） |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 背景+21 项已施工设施实测盘点+5 项实测缺口；§3 五项设计决策（三层运行时/MCP/推理优化/模型注册/数据增强边界）含替代方案；§4 Phase 0→3 施工计划（depgraph L1 铁律）；§5 不做清单；§6 开放问题 Q1~Q8 | AI-FILL-10 填充；关键实测修正：MLflow 已退役（51 号备忘）、GPTQ 在 3090 实证反减速（GGUF 替代）、数据增强归属 D-DATA 域；04/06/09/11 依赖文档未填充按降级处理（接口假设入 Q3~Q5） |
| 2026-08-17 | 0.2.1 | 开放问题新增 Q9（目录隔离搬迁事件记录）+ 拼接处空行修正 + doc_type 修正（implementation_plan→blueprint，按 doc_type_vocabulary 弃用映射 construction_plan→blueprint） | 并行 coord 收口流程将 09_ai_architecture 整树迁至 quarantine，本文回迁并记录事件待裁定；TTL-METADATA 门禁 hard block 要求合法 doc_type |

---

*维护者：AI 架构协调者*