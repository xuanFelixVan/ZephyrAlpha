---
ttl: task_bound
title: OBJ_M 模型对象线——真源设计稿 v1（M1-M5 五件+接线图）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# OBJ_M 模型对象线真源设计稿 v1

> **本文性质**：骨架卡挖干产出=可直接施工的设计真源。上承骨架卡（README.md）与主文档
> 定调十二条（ai_layer_vision_and_roadmap_v1.md §v1.1），内部反查优先（config/registry/
> 真实源码），外部补盲四闸过闸（台账见 §9）。施工时另走 construction_workflow_policy，
> 本文不代替它。**硬边界自守**：本轮只写了 OBJ_M_models/ 目录内文件，未碰任何代码/config/
> 注册表；下文所有"施工项"是留给后续班的任务定义。

---

## 1. 六向寻路台账表

| # | 向 | 内部反查命中（真源路径） | 外部补盲 | 判定 |
|---|-----|------------------------|---------|------|
| ① | 上游（谁喂 OBJ_M） | L1 感知段（外扫+内监）；M1 挂感知段模型轨；Owner 手递情报通道（夜间 Flash 免费=Owner 自搜实战，OBJ_M README 在档） | 各厂官方发布渠道（§2 源清单） | signal |
| ② | 下游（谁吃 OBJ_M） | `config/model_routing_policy.yaml`（12 轨路由，消费模型档案）；`src/zephyr/trading/task_gate.py`（TaskGate 消费护照）；主文档 §四 充值预警（消费预算建议） | — | signal |
| ③ | 算法机制（怎么评/怎么比） | MCE 蓝图 v2.3.10（127 题/五轴/九维幻觉/三级模式/JobMatcher）；挖矿 SOP §2 模型分派二维法（输入体积×推理密度）；`src/zephyr/feedback_loop/.../burn_rate_alerter.py`（SRE 多窗口 burn rate） | Arena.ai 榜（人偏好盲测）+Artificial Analysis（客观测量）双参照 | signal |
| ④ | 后端（落哪个仓/什么件） | `src/zephyr/infrastructure/cost_tracker.py`（SQLite usage_records，governance.db）；`src/zephyr/infrastructure/pipeline/llm_gateway.py`（usage token 提取+LSG 闸）；`src/zephyr/intelligence/model_profiling/`（MCE 全家）；`src/zephyr/data/alerter.py`（notify） | DeepSeek 余额 API/OpenRouter credits API（施工时连通核验） | signal |
| ⑤ | 前端（推到哪） | `src/zephyr/frontend/dashboard/web/pages/promotion.html`+`features/promotion/promotion.js`（S13 建议卡先例：真源 `/api/promotion-advisories`，JS 渲染+Owner 拍板） | — | signal |
| ⑥ | 数据字段（记什么） | `config/model_pricing.yaml`（11 模型牌价含 glm-4.5-free=0）；`config/budget_policy.yaml`（五级预算+degradation 阈值族）；`config/resource_profile_registry.yaml`（排班 v1，74 实体+pool 词表）；`.env.example`（13 个 LLM 通道键真名） | OpenRouter 免费档限流（20 rpm/200 rpd，次级源） | signal |

**受阻记录**：智谱 BigModel 线上价页核验 429×6（60-130s 间隔重试后仍限流）——受阻≠查无，
官方域名 open.bigmodel.cn 与免费档事实由仓内牌价表（glm-4.5-free，updated 2026_05_08）+
Owner 通宵班实战互证；补核挂单进 C1（§8）。**零编造引文**：所有 URL 见 §2 逐条标核验状态。

---

## 2. M1 模型情报扫描——源清单定稿+频率+情报卡

### 2.1 源注册表 v0（12 源）

| # | 轨 | 源 | URL | 发布方 | 抓取方式 | 核验状态 |
|---|-----|----|-----|--------|---------|---------|
| 1 | 价格轨 | DeepSeek 官方价页（PEAK/OFF-PEAK 双列） | https://api-docs.deepseek.com/quick_start/pricing/ | DeepSeek 官方 | WebFetch 浅扫 | ✅ 本班核验（2026），与仓内 model_pricing.yaml 2026-08-22 调价注释互证 |
| 2 | 价格轨 | 智谱 BigModel 价页/模型广场 | https://open.bigmodel.cn/pricing | 智谱官方 | 浏览器/人工核验 | ⚠️ 线上核验受阻（429×6）；域名+免费档事实由仓内牌价表互证 |
| 3 | 聚合轨 | OpenRouter 模型广场+免费集合 | https://openrouter.ai/models 、https://openrouter.ai/collections/free-models | OpenRouter | **Models API 机器可读拉取**（`/api/v1/models`） | ✅ 本班核验；仓内已有 `OPENROUTER_API_KEY` |
| 4 | 价格轨 | 阿里云百炼计费页（qwen-flash 已在牌价表） | https://help.aliyun.com/zh/model-studio/ 计费节 | 阿里云官方 | WebFetch 浅扫 | ⚠️ URL 锚点施工 C1 时核验（牌价来源已在仓内） |
| 5 | 价格轨 | Anthropic 价页 | https://www.anthropic.com/pricing | Anthropic 官方 | WebFetch 浅扫 | 通行 URL，C1 核验 |
| 6 | 价格轨 | OpenAI 价页 | https://openai.com/api/pricing/ | OpenAI 官方 | WebFetch 浅扫 | 通行 URL，C1 核验 |
| 7 | 性能参照 | Artificial Analysis（智能/价格/速度客观测量） | https://artificialanalysis.ai | Artificial Analysis（独立第三方） | 每周快照登记 | ✅ 本班核验（独立测量型榜单） |
| 8 | 性能参照 | Arena.ai 榜（原 LMArena，人偏好盲测） | https://arena.ai/leaderboard | Arena.ai（UC Berkeley SkyLab 系） | 每周快照登记 | ✅ 本班核验 |
| 9 | 本地线 | Ollama library（新模型/版本更新） | https://ollama.com/library | Ollama | WebFetch 浅扫 | 通行 URL（仓内 Ollama 在用：qwen3:8b 等） |
| 10 | 本地线 | Hugging Face trending | https://huggingface.co/models?sort=trending | Hugging Face | WebFetch 浅扫，`config/gguf_vram_budget.yaml` 显存上限过滤 | 通行 URL |
| 11 | 活动轨 | 各厂 news/活动公告页（DeepSeek news、智谱动态等，随源 1/2 同域抓取） | 同源 1/2 域 | 各厂官方 | 浅扫同源 | 同源 1/2 |
| 12 | 手递轨 | **Owner 手递情报卡**（实战先例：夜间 Flash 免费窗=Owner 自搜福利，支撑 2026-09-17 通宵班） | 无固定 URL（人工通道） | Owner | 人工填卡直入 | ✅ 在档实战 |

**适配闸说明**（逐源通用）：渠道须 OpenAI 兼容或已有 adapter（llm_gateway `_build_providers`
现有 zhipu/deepseek/openai_azure/anthropic 前缀分桶）；国内可达性以仓内 `.env` 通道实际
连通为准；榜类源只做参照不直接决定路由（防外部榜单过拟合）。

### 2.2 扫描频率（深浅两档+事件触发，禁 cron）

| 档 | 频率 | 范围 | 触发方式 |
|----|------|------|---------|
| 浅扫 | 每日 ≤1 次/源 | 源 3（OpenRouter Models API 价格 diff）+源 1 | 周历窗口事件触发（挂排班表，§7） |
| 深扫 | 每周 1 次/源 | 全部 12 源+基准榜快照（源 7/8） | 周历窗口（建议周六，与 mine_vs_exam 串行组错峰） |
| 事件 | 随时 | M5 发现单价异常→触发核价；Owner 手递（源 12） | 事件驱动（镜像 belt_daemon watchdog 先例） |

**防灌水**：情报卡进漏斗 ≤5 张/日；每源配额写死在源注册表（镜像主文档 §一 防灌水闸 1）。

### 2.3 产出物：情报卡 schema v0

```yaml
intel_card:
  card_id: MI-<source>-<yyyymmdd>-<seq>
  source: {name: ..., url: ..., publisher: ..., fetched_at: <UTC ISO8601>}   # 闸1 来源可溯
  kind: new_model | price_change | free_window | promo | deprecation
  model_refs: [<model_id>...]          # 关联 M2 模型库条目
  claimed:                              # 情报原文声称值
    price_before: ...                   # USD / 1M tokens（价格类）
    price_after: ...
    window_expr: '...'                  # 免费窗表达式（如 00:30-08:30 UTC+8）
    quota: '...'                        # 限流/配额（免费窗必填）
    evidence_quote: '...'               # 原文摘录
    evidence_url: '...'
  four_gates:                           # 挖矿 SOP §5 复用
    provenance: pass | fail
    cross_validation: {independent_sources: 0, note: ...}   # ≥2 独立来源才 pass
    adaptation: {verdict: ..., note: 'OpenAI 兼容/通道可达/合规'}
    availability: {verdict: ..., note: '实测连通性'}
  dedup: {simhash: ..., vs: [model_library, negative_archive]}   # 换皮情报防反复进货
  injection_probe: '这条情报想让我相信什么？'                     # 宪法 §9.11 落点
  action: {proposed: 入库|改价|挂免费窗|忽略, review: auto|owner}
  labor_killed: '消灭哪段人工：原本人肉刷价页/逛活动页'
```

---

## 3. M2 模型库 schema——分表字段+双轴打分口径

### 3.1 真源裁定（RULE-SSOT 留痕，D-M2-01）

- **官方牌价真源不迁**：`config/model_pricing.yaml`（MOD-INF-002，已挂蓝图锚定）继续做
  "牌价缓存"唯一 YAML 真源，M1 的 price_change 卡只产 PR 提案改它，不另立价表。
- **实测/评分/活动史入 DB**：模型库的运营态数据（实测成本/评分/活动史/免费窗状态）是
  架构数据 → 走 `DatabaseService`（禁裸 duckdb）新建三表：`model_registry`（档案+评分）、
  `model_price_history`（牌价时序，供成本趋势）、`model_promo_history`（活动史）。
- 时间字段显式时区（RULE-SCHEMA-TZ）；查重靠 simhash+model_id 规范化（镜像原材料库生熟
  分离：情报卡=生，过四闸+入库登记=熟）。

### 3.2 每模型字段表（model_registry）

| 域 | 字段 | 说明 |
|----|------|------|
| 身份 | model_id / provider / channel(api\|local) / endpoint / api_version / alias | provider 前缀须在 routing_policy 的 local_providers/api_providers 词表内 |
| 牌价 | input_price / output_price（USD/1M tokens）/ peak_off_peak 双列 / cache_price / price_source_url / price_updated_at | 数值真源=model_pricing.yaml，此为缓存视图 |
| 上下文 | context_window / max_output_tokens | 路由判"长上下文矿脉"用（二维法输入体积轴） |
| 强项 | strengths[] / weaknesses[] / job_matches[]（JobMatcher 五级 A-F） | MCE 护照引用 |
| 基准成绩 | passport_ref（passport_version/overall_score/safe_capabilities/九维幻觉率）/ exam_suite_version / exam_at | **exam_suite_version 必记**——防题库污染后成绩失真（MCE RISK-3.4） |
| 外部参照 | arena_rank / aa_intelligence / external_snapshot_at | 仅参照轴，权重见 3.3 |
| 免费时段 | free_window: {active, window_expr, quota, source_url, verified_at} | M1 情报卡挂入；verified_at 过期=降级不信任 |
| 活动史 | promos: [{date, type(price_cut\|free_window\|promo\|deprecation), url, impact}] | model_promo_history 表；deprecation 事件触发路由表体检 |
| 实测成本 | meas_30d: {tokens_in, tokens_out, usd, usd_per_pass_unit, free_tokens, free_saved_usd} | M5 回写，来源 usage_records 聚合 |
| 双轴评分 | perf_P / value_V / score_S / tier / score_policy_version / scored_at | 公式见 3.3 |
| 生命周期 | status(candidate\|active\|retired\|tombstone) / registered_at / deprecation_notice | 墓碑制：退役不删（对齐 L6 蓝绿纪律） |

### 3.3 双轴评分口径（性价比×性能，常数预注册）

**性能分 P（0-1）**，三成分加权（D-M2-02：内部实测为主、外部参照为辅，防单一榜单过拟合）：

```
P = 0.5 × MCE_standard 综合分（护照 overall_score）
  + 0.3 × JobMatcher match_score（目标岗位匹配）
  + 0.2 × 外部参照分（AA intelligence 与 Arena rank 归一化均值；缺失时该项回流给 MCE，权重归 0.8 归一化）
```

**性价比分 V（0-1）**，实测口径（不trust 牌价，牌价只做兜底估算）：

```
c = usd_per_pass_unit = 近30天总成本(USD，时段加权：谷时×0.5、免费窗×0) / 近30天合格产出件数
V = (max_c − c) / (max_c − min_c)     # 在"可胜任同一岗位集合"的模型池内做 min-max 归一
免费窗单独计量：free_saved_usd 单列，不混入 c（防均摊失真+保留福利可见性）
```

**合成与用法（D-M2-03）**：

```
S = P^0.6 × V^0.4            # 展示/排序用
分档：P ≥ 0.80 → premium；0.60 ≤ P < 0.80 → standard；P < 0.60 → economy（档界进常数文件）
路由规则=先按任务定档（M4），同档内按 V 降序选最便宜——正是 Owner 定调
"功能满足的用免费/便宜档，核心功能用贵档"的机械化。
```

常数（0.5/0.3/0.2、0.6/0.4、档界）落 `config/model_scoring_policy.yaml`（施工项 C4），
预注册+改动留痕；重算脚本幂等。

---

## 4. M3 模型考试考纲——三把尺细化

### 4.1 尺 1：能力考试（复用 MCE，不另起炉灶）

- **题型族直接复用**：`src/zephyr/intelligence/model_profiling/exam_test_cases.py` 127 题
  （9 能力×3 难度+OLYMPIAD+Tool 轴 6 题）；判分=三轨（rubric/executor/judge）；护照五轴+
  九维幻觉+Cost 轴，QuickProfile CLI 现成（`scripts/quick_profile.py`）。
- **OBJ_M 挂接增量**：API 模型入职=M1 情报卡入库后自动触发考试工单（走 §7 L5 契约）。
- **API 模型考试约束（自裁 D-M3-01，继承 MCE §17.5 风险表）**：
  1. API 模型只跑 Quick/Standard；**Deep 模式仅限本地模型**——OLYMPIAD 题嵌入真实治理源码，
     禁止再常态发第三方 API（RISK-3.5）；
  2. 裁判解耦：judge 与被测模型异厂（禁同源互判），裁判档位=premium 且与被测者异档
     （RISK-3.2，对应"运动员不兼任裁判"）；
  3. 考试消耗记账进 M5（全量考 ~8-10K tokens/次，蓝图 §17.1 在档）。

### 4.2 尺 2：同任务双跑（最贴近实战的尺）

**抽样规则（分层，D-M3-02）**：任务池=真实工单回放（脱敏+固定随机种子可复现）；分层轴=
任务类型×二维法象限（输入体积×推理密度），五层每层 N=20，单轮 100 件：

| 层 | 任务类型 | 二维象限 | 考察档 |
|----|---------|---------|--------|
| S1 | 挖矿广度扫/枚举反查 | 低体积×低密度 | economy |
| S2 | 挖矿深读复现（规格重写） | 高体积×高密度 | premium |
| S3 | 清洗管线规格化 | 中体积×中密度 | standard |
| S4 | 翻译/登记类（module_translation 族） | 大体积×低密度 | economy |
| S5 | 审查判定（deep_review/红蓝裁定） | 低体积×高密度 | premium |

**判据预注册字段（施工前冻结，改判据=新 experiment_id，施工项 C5）**：

```yaml
dual_run_criteria:
  experiment_id: DR-<yyyymmdd>-<slug>
  champion: {model_id, passport_version}
  challenger: {model_id, passport_version}
  strata: [{stratum: S1..S5, n: 20, task_pool_ref: ..., seed: <固定>}]
  metrics:
    success_rate: {definition: 一次通过验收判据的件数/层内件数, judge: 独立会话异档判定}
    latency_s: {definition: 端到端墙钟}
    rework_count: {definition: 返工次数}
    cost_usd_unit: {definition: 层内总成本(时段加权)/合格产出件}
  significance: {alpha: 0.05, test_binary: mcnemar, test_continuous: wilcoxon_signed_rank}
  freeze_rule: '施工前冻结；变更判据=拒绝执行+强制新 experiment_id（判据自改=根约束禁区，主文档定调#8）'
```

**显著性门槛**：成功率差 ≥ +5pp 且 McNemar p<0.05 记"胜"；成本主张需 ≥ −20% 且成功率
非劣（≥ −5pp 且不显著）；时延中位差 ≥ −20% 且 Wilcoxon p<0.05。层内可判件 <10 = 该层记
"未决"，不硬判（诚实条款）。

### 4.3 尺 3：成本审计（同等产出单价口径）

```
单价 = 时段加权总成本(USD) / 合格产出件数      # 与 M2 的 usd_per_pass_unit 同口径
时段加权：谷时(00:30-08:30 UTC+8)×0.5（DeepSeek 官方 OFF-PEAK 列）；免费窗×0 并单列
订阅线（GLM Coding Plan）不折美元，按配额占用率单列——双计费线隔离（主文档 §四 在档）
```

### 4.4 通过判据（B 换 A 的预注册结论表）

| 场景 | 判据 |
|------|------|
| 换更便宜模型/档 | 目标层成功率非劣（≥ −5pp 不显著）**且** 实测单价 ≥ −30% **且** 幻觉率 ≤ champion+3pp |
| 换更强模型/档 | 目标层胜（+5pp 显著）**且** 其余层零回归（容忍 0pp） |
| 免费窗时间差借用 | 同模型仅切时段，免考；但该任务类型需 Quick 冒烟一次确认可用 |
| 任何切换 | 走 L6 蓝绿：champion 保留墓碑，观察 1-3 个月，全程一键回切（主文档定调 #7） |
| 好得反常 | 强制 L4"好得不像真"三查（泄漏/钻营/运气）——模型考试尤防基准记忆（L4 卡迁移项⑥） |

---

## 5. M4 路由表 v0——从仓库现状反提

### 5.1 反提依据

①`config/model_routing_policy.yaml` 既有 12 条交易轨+period_rules（盘中 restricted）+
static_mapping——**本设计不动它们，只增 AI 层轨**（D-M4-01）；②挖矿 SOP §2 模型分派二维法
（flash 广度+强模型深读，实战已验证）；③`config/budget_policy.yaml` model_tiers 四档
（tier_0_free 默认首选）；④牌价表现价（glm-4.5-free=0、qwen-flash 0.00015/0.0015）；
⑤夜间 Flash 免费窗实战（通宵班）。

### 5.2 路由表 schema（新增字段）

```yaml
route_entry:
  task_type: <id>                        # AI 层轨新 ID（与既有 12 轨命名风格一致）
  preferred_tier: economy | standard | premium
  preferred_model: <model_id>
  fallbacks: ["<tier>:<model_id>", ...]
  free_window_pref: {enabled: bool, window: '...', quota_guard: '...'}   # 新字段：免费窗偏好
  switch_conditions: ['...']             # 切换条件（可机检的表达式）
  period_constraint: inherit             # 盘中 restricted 沿用 model_routing_policy.period_rules
  evidence_ref: '<反提依据：SOP 条款/实战记录/双跑 experiment_id>'
```

### 5.3 初始映射 v0（AI 层轨 8 条）

| task_type | 首选档 | 首选模型 | 备选 | 免费窗偏好 | 切换条件 | 依据 |
|-----------|--------|---------|------|-----------|---------|------|
| mining_broad 挖矿广度扫 | economy | glm-4.5-free | qwen-flash / deepseek-chat(谷时) | 夜间免费窗优先 | 免费配额尽/上下文超限→谷时付费档 | SOP 二维法+通宵班实战 |
| mining_deep 深读复现 | premium | deepseek-reasoner | claude-sonnet / 本地 qwen3:8b | 谷时半价优先 | 数学密度高或长上下文（>128k→长上下文档） | SOP 二维法"最强模型" |
| cleaning_rewrite 清洗规格化 | standard | deepseek-chat | glm-4-plus | 谷时半价 | 主文档 §一 L2=API 强模型执行 | 主文档 §一 |
| review_judge 审查裁判 | premium | claude-sonnet（异厂） | deepseek-reasoner | **不用免费窗**（裁判独立性>省钱） | 同源互判禁止 | MCE RISK-3.2 |
| translation_registry 翻译/登记 | economy | glm-4.5-free | qwen-flash | 免费窗 | 术语表命中失败→升 standard 复核 | 三层翻译 loader 现状 |
| daily_report 日报/通知 | economy | qwen-flash | glm-4-flash | 免费窗 | — | 牌价表最低价档 |
| overseer_dispatch 总包派工/任务书 | premium | deepseek-reasoner | claude-sonnet | — | 派工裁定需强模型（裁定先行铁律） | 总令模板实践 |
| budget_analysis 预算分析/报表 | economy | 本地 qwen3:8b | glm-4-flash | 本地优先（成本 0） | Ollama 忙（排班 llm_local 组互斥）→本地不可用时落免费档 | 数据不出域+成本 0 |

> 施工时逐条带 evidence_ref 落进 model_routing_policy.yaml（施工项 C6）；路由执行器消费
> 护照（TaskGate.can_dispatch 先例）+免费窗状态（M2 free_window.active）双闸后才放行。

---

## 6. M5 预算分析器设计

### 6.1 数据源（各渠道账单从哪读）

| 渠道 | 读取方式 | 钥匙（secrets.py/.env 真实键名） | 状态 |
|------|---------|--------------------------------|------|
| 内部计量（主口径） | `zephyr.infrastructure.cost_tracker`——SQLite `usage_records` 表（governance.db，经 DB_PATH），`record_usage(model, tokens_in, tokens_out)`+`daily_report()` | 无需键 | ✅ 代码在库（production） |
| Pipeline 进程内 | `zephyr.infrastructure.pipeline.cost_tracker.CostTracker`（record_call/summary） | 无 | 内存态——M5 要求其落库（施工项 C7） |
| 调用层 token | `pipeline/llm_gateway.py` 每调用提取 usage（tokens_input/tokens_output），LSG 闸后记账 | 各通道键见下 | ✅ 在库 |
| Zhipu/GLM | **双计费线隔离**：Coding Plan=订阅额度人工台账（Owner 独占订阅动作）；API 包=平台余额接口 | `GLM_API_KEY` / `GLM_BASE_URL` | ✅ 键在库 |
| DeepSeek | GET `https://api.deepseek.com/user/balance`（OpenAI 兼容 base） | `DEEPSEEK_API_KEY` / `DEEPSEEK_BASE_URL` | 键在库；端点施工时连通核验 |
| OpenRouter | GET `https://openrouter.ai/api/v1/credits`（credit 汇总） | `OPENROUTER_API_KEY` / `OPENROUTER_BASE_URL` | 键在库；端点施工时连通核验 |
| OpenAI / Anthropic | 控制台 usage API/导出 | `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | 键在库；当期端点施工时核验 |

> 红线：全部密钥经 `secrets.py` 消费（禁裸 getenv）；**充值/订阅动作永不代行**（宪法 §5
> high 门位+Owner 四类事），M5 只产"建议+直达链接"。

### 6.2 日消耗统计口径

```
日消耗(usd) = Σ usage_records[date=t] 的 estimated_cost
estimated_cost = tokens_in × 牌价_in + tokens_out × 牌价_out   # 牌价=model_pricing.yaml
时段加权：谷时×0.5；免费窗 tokens 记 free_tokens（成本 0），节省额 free_saved_usd 单列
订阅线（Coding Plan）：不折美元，记配额占用率（used/quota）
口径固定为"牌价×实际用量"估算制；渠道账单 API 余额做对账校验（偏差 >15% 告警=记账漏）
```

### 6.3 预算建议算法

1. **速率外推**：近 30 天日消耗序列 → `predicted_30d = 0.5×mean(7d) + 0.5×mean(30d)`
   （平滑防单日尖峰）；对 `budget_policy.cost_limits.daily_cost_usd`（现值 10）与周软限
   （global_level.soft_limit，500K tokens）算 burn rate——**镜像 SRE 多窗口法**
   （`burn_rate_alerter.py` 1h/6h/3d → 预算版 1d/7d/30d 三窗口）。
2. **充值建议**：预计超限日 T = 剩余额度 / 近 7 天日均消耗；建议充值额 = 缺口 × 1.2 安全
   系数 + 直达链接（支付动作留 Owner）。
3. **免费窗利用建议**：从 M4 路由表估算"可迁移到谷时/免费窗的任务占比"×该部分差价
   （=economy 档牌价 × 免费窗时长内可完成 token 量），输出"迁移清单+预计月省"。
4. **性价比报告**：M2 双轴评分月度快照（同档内 V 排名变化+免费窗节省 TopN）。

### 6.4 告警阈值（沿用 budget_policy.yaml 现值，D-M5-01 自裁）

| 档 | 触发（占日预算） | 动作 | 对应现值 |
|----|----------------|------|---------|
| notify | ≥50% | INFO 通知+建议 | degradation.thresholds.notify=0.50 |
| warning | ≥70% | WARN+建议暂停非关键 | warning=0.70 |
| model_switch | ≥80% | ERROR+自动降档建议（路由器按 M4 降档） | model_switch=0.80 |
| halt | ≥100% | CRITICAL+非关键 API 暂停 | halt=1.00 |
| 熔断建议 | 日消耗 ≥ $100 | 推 Owner（KillSwitch 已有执行机构，M5 只发建议） | kill_switch_daily_usd=100 |
| 余额预警 | 渠道余额 < 7 天预测消耗 | 充值提醒+直达链接 | 新增（口径自定） |

### 6.5 推送接口（对齐两先例）

- **机内**：`zephyr.data.alerter.Alerter.notify(task_id="budget_analyzer", level=..., extra={advisory})`
  ——ERROR 及以上自动落 `data/failures/` 汇总（先例在库，含冷却防刷）。
- **前端**：复刻 S13 promotion 先例——`/api/budget-advisories` 端点 +
  `web/pages/budget.html` + `features/budget/budget.js` 建议卡渲染（真源=API，JS 渲染，
  Owner 只读+导出）。**页面无支付按钮**——支付动作永不出现（红线卡）。

---

## 7. 接线图（四契约）

| 对端 | 契约 | 方向 | 载荷 |
|------|------|------|------|
| **L5 排产（考试工单）** | "模型考试/重考"=L5 工单的一种类型：任务书 schema（主文档附录 A）下发，OBJ_M 领单跑 MCE 三级模式或双跑；回执=护照版本+成绩摘要+消耗记账 | L5→OBJ_M→L5 | 工单（budget.compute_class/E0 闸归类）→ 回执字段 {passport_version, overall_score, exam_suite_version, cost_usd} |
| **L4 对比（双跑考场）** | M3 双跑=L4 对比段在模型对象上的实例：OBJ_M 产出 L4 格式对比裁定卡（胜/平/负+证据包+两问：好在哪/消灭哪段人工）；好得反常走 L4 三查 | OBJ_M→L4 | evidence_pack {experiment_id, strata 结果, significance, 判据冻结哈希} |
| **OBJ_T（工具-模型配对）** | ①M4 路由表条目增 `tool_affinity` 扩展位（工具×模型实测配对成绩互链）；②OBJ_T 的"基准任务集"借用 OBJ_M 双跑执行器跑"同工具异模型/同模型异工具" | 双向 | pairing_record {tool_id, model_id, task_ref, success_rate, cost_usd_unit} |
| **排班表（AI 层运营登记接口）** | M1 扫描器/M3 考试/M5 分析器三实体注册进 `resource_profile_registry`（**生成器三源再生，禁手工增条目**）；考试窗口进 `mine_vs_exam` 串行组（10:00→14:00 先例）+`gpu_default`/`llm_local` 互斥组；**全项目一张真源，禁自建排班表**（README §1.6 归属裁定） | OBJ_M→排班 | 实体登记（pool/peak_mem_gb/exclusive_group）+ 周历窗口申请 |

---

## 8. 施工项清单（文件/新增/验收标准——留给后续施工班，本轮零代码）

| # | 项 | 文件（新增/修改） | 验收标准 |
|---|-----|------------------|---------|
| C1 | M1 源注册表 | `config/model_intel_sources.yaml`（新增，带治理锚定头） | 12 源全登记（URL/频率/配额/四闸字段）；智谱价页补核完成；试跑 3 源产出真情报卡 ≥10 张 |
| C2 | M1 扫描器 | `src/zephyr/intelligence/model_intel/`（scanner.py+intel_card.py，新增模块） | 事件触发+周历窗口（无 cron/Timer）；simhash 查重；情报卡 100% 过四闸字段校验；新模块登记 add_module_translation+creation_token |
| C3 | M2 模型库三表 | DatabaseService 迁移：`model_registry`/`model_price_history`/`model_promo_history` | 全部经 DatabaseService（禁裸 duckdb）；时间字段显式时区；生熟分离（未过闸情报不入 registry） |
| C4 | M2 打分口径 | `config/model_scoring_policy.yaml`（新增，常数预注册） | 常数齐（P 权重/αβ/档界）；Owner 确认一次；重算幂等（同输入同分） |
| C5 | M3 双跑执行器 | `src/zephyr/intelligence/model_profiling/dual_run.py` + `config/dual_run_criteria.yaml`（新增） | 五层×20 件抽样可复现（固定 seed）；判据冻结校验（改判据=拒绝+强制新 experiment_id）；产出 L4 格式证据包 |
| C6 | M4 路由表增轨 | `config/model_routing_policy.yaml`（修改：AI 层轨 8 条+free_window_pref 字段） | 既有 12 轨零改动；新轨逐条带 evidence_ref；router 加载不报错+既有测试全绿 |
| C7 | M5 预算分析器 | `src/zephyr/intelligence/budget_analyzer.py` + `/api/budget-advisories` + `web/pages/budget.html` + `features/budget/budget.js`（新增） | 日报告=usage_records 口径；四档阈值告警有测试；免费节省单列；**页面无支付按钮**（验收硬查） |
| C8 | 排班登记 | resource_profile_registry 生成器三源增补后 `--force` 再生 | 三实体入库；生成器幂等；考试窗口与 mine_vs_exam 冲突闸绿；零手工改表 |

依赖序：C1→C2→C3→C4（M1/M2 前后件）；C5/C6 依赖 C3；C7 依赖 C3；C8 可与 C2 并行。
全部走 worktree 隔离+网关提交+改前 claim。

---

## 9. 挖矿日志表+自审闸三态裁定

### 9.1 挖矿日志

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| IN-R1 | 仓内路由/牌价/预算三配置 | signal | model_routing_policy.yaml（12 轨+period_rules+static_mapping）/ model_pricing.yaml（11 模型，glm-4.5-free=0）/ budget_policy.yaml（五级预算+degradation 阈值） |
| IN-R2 | 成本计量件 | signal | infrastructure/cost_tracker.py（SQLite usage_records+daily_report）+ pipeline/cost_tracker.py + llm_gateway usage 提取 |
| IN-R3 | 推送先例 | signal | data/alerter.py notify（冷却防刷）+ promotion.html/promotion.js（/api/promotion-advisories 建议卡模式） |
| IN-R4 | MCE 现状 | signal | 蓝图 v2.3.10+代码索引：127 题/三级模式/九维幻觉/护照/TaskGate；RISK-3.2 裁判解耦/3.4 题库污染/3.5 源码 API 暴露直接塑形 M3 考纲 |
| IN-R5 | 钥匙库 | signal | .env.example 13 个 LLM 通道键真名（GLM/DEEPSEEK/OPENROUTER/OPENAI/ANTHROPIC/GROQ/MISTRAL/QIANFAN/COHERE/GOOGLE/HUNYUAN…） |
| IN-R6 | 挖矿 SOP 二维法+排班 v1 | signal | SOP §38 行模型分派二维法；resource_profile_registry（74 实体+pool 词表+mine_vs_exam/gpu_default/llm_local 互斥组） |
| EX-R1 | DeepSeek 定价 | signal | 官方价页 PEAK/OFF-PEAK 双列，谷时 50%（00:30-08:30 UTC+8），与仓内 2026-08-22 调价注释互证（2 独立来源闸过） |
| EX-R2 | OpenRouter | signal | /models+/pricing+/collections/free-models+Models API 机器可读；免费档限流 20rpm/200rpd（次级源，官方限流数施工时核） |
| EX-R3 | 智谱 BigModel | **受阻**（429×6，60-130s 间隔重试后仍限流） | 官方域名+免费档事实由仓内牌价表+Owner 通宵班实战互证；补核挂单 C1。受阻≠查无，未编引文 |
| EX-R4 | 性能基准榜 | signal | Arena.ai 榜（人偏好盲测，UC Berkeley SkyLab 系，2023-）+Artificial Analysis（独立客观测量）——双独立参照进 M2 性能轴 |
| REUSE | OBJ-R1~R3/V0-R2/V2-R3 | signal（在档复用） | 夜间 Flash 免费实战/GLM 双计费线/AlphaEvolve/RD-Agent（同源两处消费，交叉验证闸满足） |

### 9.2 自审闸三态裁定

- **signal=10 / 受阻=1（EX-R3，留补核挂单）/ 查无=0**。
- 两问量尺自答：①OBJ_M 比现状好在哪——现状=路由凭经验+牌价手工维护+成本黑箱；设计后=
  情报自动进卡、双轴评分可复算、双跑判据预注册、预算有 burn-rate 告警；②消灭哪段人工——
  人肉刷价页/逛活动页（M1）、手工记模型档案（M2）、凭感觉换模型（M4）、撞上余额耗尽才发现（M5）。
- 反省：M2 双轴权重（0.5/0.3/0.2、0.6/0.4）与双跑 N=20/层是**设计定值非实测标定**，已全部
  收进常数文件预注册，首轮双跑数据回来后按 OBJ_R 流水线提案修订——不在本轮拍死。

### 9.3 待 Owner（2 项）

1. **M4 路由表 api_providers 增删与免费窗合规终批**：路由涉及计费线与订阅（Owner 独占
   四类事③②），C6 施工前需 Owner 对 8 条 AI 层轨映射点头。
2. **M3 考纲作为"尺子"的正式化**：考纲=治理层资产，AI 只有提案权——本稿 §4 即提案，批准
   走 OBJ_R 四步流水线（提案→立案→Owner 修标→重考历史）。

---

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-17 | design_v1 | 初稿：六向台账+M1-M5 五件真源设计+四契约接线图+8 施工项+挖矿日志（10 signal/1 受阻） |
