---
ttl: task_bound
---

# LLM 模型注册三处对账 + mcp.json↔tool_contracts.yaml 漂移裁定报告（18号清单 §5 / 10号文 §4 Phase 0.2+0.3）

- 日期：2026-08-22
- 工单：18号清单 §5 波2（10号文 llm_runtime_gateway Phase 0 纯治理三件之②③；① depgraph 登记由统筹执行，不在本报告）
- 验收口径：10号文 §4 Phase 0.2「对账清单产出，不一致项全部有归属裁定」+ 0.3「漂移项收敛为 0 或登记为带理由的已知偏差」
- 纪律：纯对账不修改任何注册表/配置文件（不写 yaml 纪律）；dump 为 2026-08-22 实证（运行时 python 直读，非目测）
- 环境：Windows / Python 3.12.8 / Asia/Shanghai

## 一、对账对象（四源 dump 实证）

| 源 | 位置 | 性质 | 条目数（实证） |
|---|---|---|---|
| A. 运行时治理 dict（MOD-INF-039） | `src/zephyr/orchestrator/governance/model_registry.py` `MODELS` | LLM API 模型治理登记（provider/tier/token_limit，无价） | 6 |
| B. 定价表（MOD-INF-002 锚定） | `config/model_pricing.yaml` | 价格真源（元/千 token，updated_at 2026-05-08） | 10 |
| C. 运行时路由表 | `src/zephyr/infrastructure/pipeline/llm_gateway.py::_build_providers()` | 路由/降级/成本镜像（成本=元/千 token，字段名误称 cost_usd，见 §四-C） | 4 provider |
| D. REG-ML-001 | `docs/01_policies_and_standards/_registry/catalogs/model_registry.yaml` | ML 训练产物生命周期登记（SSoT，human_gated） | 8（声明 8 = 实证 8，账实一致） |

C 源 dump 实证（本机环境变量下）：`deepseek→deepseek-v4-flash（env DEEPSEEK_MODEL 实证值；fallback=glm）`、`glm→glm-4-flash（fallback=deepseek）`、`claude→claude-sonnet-4-20250514（fallback=None）`、`openai→gpt-4o-mini（fallback=None）`。注意 C 的 default_model 是环境变量函数，非定值。

## 二、三处模型注册对账清单（0.2 主产物）

### 2.1 逐项比对矩阵（模型名/提供方/定价/路由）

| 模型 | A 治理 dict | B 定价（元/百万 token，由元/千换算） | C 路由 | 不一致性质 | 归属裁定 |
|---|---|---|---|---|---|
| deepseek-chat | ✅ standard/65536 | ✅ 1.0/2.0 | ✅ deepseek 默认（成本镜像 1.0/2.0 一致） | 三方一致 | 无需裁定；A=治理真源，B=定价真源 |
| deepseek-reasoner | ✅ premium/65536 | ✅ 4.0/12.0 | ❌ 无默认路由（仅 DEEPSEEK_MODEL 环境变量可达） | C 缺省不含属有意（reasoner 非默认路由） | 一致登记，非漂移；B 定价覆盖完整 |
| claude-opus-4 | ✅ premium/200000 | ❌ 缺席 | ❌ 缺席 | A 超前登记（设计态预留），定价/路由未跟进 | **A 为登记真源不判错**；标注「定价/路由缺席」，启用前须先补 B（Owner 动作） |
| claude-haiku-3.5 | ✅ standard/200000 | ⚠️ 名变体 `claude-3-5-haiku` 4.0/20.0 | ❌ 缺席 | **名称漂移**：同一模型两名 | **以 B 的 Anthropic 官方命名（claude-3-5-haiku 系）为实证名**；A 滞后（别名体），建议 GP1 统一 |
| gpt-5.2 | ✅ premium/128000 | ❌ 缺席 | ❌ 缺席 | A 超前登记（同 opus-4） | 同 claude-opus-4 裁定 |
| gpt-4o-mini | ✅ standard provider=openai | ✅ 3.0/15.0 provider=**openai_azure** | ✅ openai 默认（成本 3.0/15.0 一致） | 价格一致；**provider 标签漂移**（openai vs openai_azure） | 登记为带理由已知偏差：B 的 openai_azure 为通道实证（Azure 代理），A 记供应商族名 openai；价以 B 为准 |
| glm-4-flash | ❌ 缺席 | ✅ 1.0/1.0 | ✅ glm 默认（成本一致） | **A 缺席**：降级链第二环未入治理登记 | **A 滞后**：建议补登（Owner/GP1 动作，本报告不改 yaml）；B/C 一致 |
| glm-4-plus | ❌ | ✅ 7.0/7.0 | ❌ | B 单方登记（可用非默认） | 一致登记，非漂移 |
| glm-4.5-free | ❌ | ✅ 0/0 | ❌ | 同上 | 同上 |
| deepseek-chat-free | ❌ | ✅ 0/0 | ❌ | 同上 | 同上 |
| gpt-4o | ❌ | ✅ 15.0/60.0 | ❌ | 同上 | 同上 |
| claude-3-5-sonnet | ❌ | ✅ 20.0/80.0 | ⚠️ 默认模型=claude-sonnet-4-20250514，成本却填 20/80（=3-5-sonnet 价） | **C 默认模型与成本错配**（路由 sonnet-4、计价 3-5-sonnet） | **以 B 为定价真源**；C 滞后/错配，登记待校准（GP1 接线时按实际默认模型对齐计价） |
| claude-sonnet-4-20250514 | ❌ | ❌ | ✅ claude 默认 | C 单方实证，A/B 均缺席 | **C 为运行时实证**；A、B 均滞后，建议补登（Owner 动作） |

### 2.2 附带发现（对账中实证，超出三源主清单但同源同因）

| # | 发现 | 裁定 |
|---|---|---|
| F1 | 第四定价源：`src/zephyr/intelligence/model_profiling/deepseek_v4_chat.py::PRICING_RMB`（v4-flash 1.0/2.0、v4-pro 3.0/6.0 元/百万）。v4-flash 与 B 的 deepseek-chat 同档一致；**v4-pro 3/6 在 B 缺席** | B 滞后（缺 v4-pro 档）或视为 profiling 内部口径；登记待 Owner 裁定是否并价 |
| F2 | 运行时实际模型别名：`DEEPSEEK_MODEL=deepseek-v4-flash`（.env 实证），A/B 均无 v4-flash/v4-pro 条目 | 别名漂移：v4-flash≈deepseek-chat 档（价实证一致）、v4-pro 无登记锚；MVP 内置价表按族映射兜底（见网关模块 docstring） |
| F3 | B 无谷/峰时段维度（2026-05-08 静态价），DeepSeek 官方存在时段价差 | 18号工单口径：MVP 内置谷峰表（谷=北京 18:00-次日 9:00，1.5/4.5 元/百万；峰=B 实证 1.0/2.0）。**谷>峰与公开「谷时折扣」方向相反，登记为待 Owner 校准项**；MVP 按工单口径实现并由单测锁定 |
| F4 | B 无任何 qwen 条目 | Qwen 通道成本 MVP 留 0 + 待校准标注（18号工单口径），真跑后回填 |

### 2.3 D 源（REG-ML-001）归属说明

D 的 8 条目全为训练产物 artifact（density×2 / llm_sft×1 / classifier×2 / regressor×1 / ranker×1 / anomaly×1，均 candidate），与 LLM API 模型目录**零重叠、正交**：D 管「产物生命周期」（晋升/衰减/部署锚点），不管「API 模型目录/定价」。裁定：**LLM API 模型治理真源=A（MOD-INF-039），定价真源=B（model_pricing.yaml），D 不承担 LLM API 登记职责**——「三处分裂」实质是 A/B/C 三源，D 参与对账是为确认正交边界无漏登（结论：无漏登，entry_count 账实一致 8=8）。

### 2.4 真源归属总结（一句话版）

- 治理登记（有什么模型/tier/限额）：**A=MOD-INF-039 为真源**；滞后项=glm-4-flash、claude-sonnet-4-20250514 缺席；漂移项=claude-haiku-3.5 命名；超前项=claude-opus-4、gpt-5.2（设计态预留，非错误）。
- 定价：**B=model_pricing.yaml 为真源**；滞后项=v4-pro 档缺席、谷峰维度缺席（MVP 内置补，待校准）；错配消费方=C 的 claude 成本镜像。
- 运行时路由实证：**C=_build_providers() 为实证**；其 default_model 受环境变量影响，dump 时点值已记录在案。
- 以上「补登/统一」均为 Owner/GP1 动作；本工单纪律=只出报告不改注册表。

## 三、mcp.json ↔ tool_contracts.yaml 漂移裁定（0.3 主产物，10号文 Q8）

实证基线：`config/mcp.json` servers 节 12 个 server；`src/zephyr/integration/mcp/tool_contracts.yaml` 12 个 server 契约块（v1.6.0，2026-08-17）。

### 3.1 Q8 四项逐一裁定

| server | mcp.json | tool_contracts.yaml | 裁定 |
|---|---|---|---|
| sandbox | ✅ implemented（2 工具，H 级，qps=2） | ✅ Server 12（v1.6.0 已补登，2 工具一致） | **漂移已收敛=0**（Q8 立题时点早于 v1.6.0 补登）；以 contracts 为契约真源、mcp.json 为部署真源，二者当前一致 |
| red_blue_validator | ✅ implemented（4 工具，含 RBAC/熔断/审计配置，module=`zephyr.security.adversarial_validation.mcp_endpoints`） | ❌ 缺席 | **以 mcp.json（实现真源）为准，contracts 滞后**——登记为待补偏差：应补登契约块（4 工具 schema）。附带张力标注：其 transport=stdio 与 10号文 §5「MCP STDIO 传输层禁用」裁定方向冲突，补登时需一并裁定传输层（GP1/Owner 动作） |
| clone_guard | ✅ implemented（5 工具，module=`zephyr.clone_guard.mcp_server`，co-located 守 red_blue_validator 先例） | ❌ 缺席 | **以 mcp.json（实现真源）为准，contracts 滞后**——登记为待补偏差：应补登契约块（5 工具 schema） |
| resource_optimization | ❌ 缺席 | ✅ Server 9（`implementation: pending`，设计预留，backend 引擎已实现、MCP server 未落地） | **以 tool_contracts.yaml（设计预留真源）为准，mcp.json 不登记属正确**（无实现体可部署）——有意分层，登记为带理由的已知偏差：server 落地之日 mcp.json 补登记 |

### 3.2 附带漂移（对账实证，非 Q8 四项，一句话级裁定）

| # | 项 | mcp.json | contracts | 裁定 |
|---|---|---|---|---|
| G1 | governance 工具计数 | tool_count=7（note「五+二工具」） | 实登 17 工具 | contracts 为契约真源，**mcp.json 计数滞后**（v1.6.0 补登 9 工具后未同步） |
| G2 | vector_memory server_id | `vector_memory`（下划线） | `vector-memory`（连字符，工具前缀同） | 命名漂移；以 contracts 工具前缀 `vector-memory.*` 为注册名实证，mcp.json 键名属部署别名——登记已知偏差 |
| G3 | governance version | 1.1.0 | 1.0.0 | mcp.json 为部署实证，contracts 滞后 |
| G4 | mcp_gateway | gateway 节（非 servers 节） | Server 11（3 工具） | 两边均有、语义一致，非漂移 |

### 3.3 收敛结论

Q8 四漂移项：1 项已收敛（sandbox），2 项裁定「实现真源为准、contracts 待补」（red_blue_validator/clone_guard），1 项裁定「有意分层已知偏差」（resource_optimization）。**未收敛残留=0 项无归属**——全部不一致项均有归属裁定，0.3 验收口径达成（收敛为 0 或登记为带理由已知偏差）。

## 四、口径与单位备忘（供网关 MVP 与日终对账消费）

- B 源价格单位=元/千 token（0.001 = 1 元/百万）；本报告矩阵已统一换算为元/百万。
- C 源 `LLMResponse.cost_usd` 字段名与数值口径（元人民币档）不符——字段命名历史偏差，登记（不改代码，GP1 对齐）。
- 网关 MVP 成本口径：内置价表（族映射：deepseek-chat/v4-flash 同档 1/2 峰、1.5/4.5 谷；reasoner 4/12；v4-pro 3/6；qwen 0 待校准；ollama 本地 0），ts 按 Asia/Shanghai 判定谷峰（18:00-次日 9:00 谷）。
- 日终对账接口 `reconcile_daily_calls(date)`：按 llm_call_log 落库行汇总（调用次数×单价=登记成本），与重算价对照出 delta，供防超额口径（44号 §9.14 联动）。
