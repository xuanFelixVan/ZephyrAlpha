---
ttl: task_bound
title: L2 收集段——原材料库 真源设计稿 v1
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L2 收集段真源设计稿：原材料库（分库分表，生熟分离）

> **一句话**：把 L1 感知抓回的生原材料（论文/开源/机制/基准）结构化入 PostgreSQL 原材料库
> （经 DatabaseService，禁裸连接），simhash 查重防换皮，MAP-Elites 行为格保多样性，
> 进货费两问机检防灌水，淘汰率 KPI 防贫矿——没过 L4 对比+门闸的卡永不进产线。
> 主文档锚点：ai_layer_vision_and_roadmap_v1.md §0.5 定调 5/6/11 + 附录 B 候选卡 schema v0。

---

## 一、六向寻路台账

| 向 | 内部发现（真实路径） | 外部发现（URL/发布方/年份） | 判定 |
|----|---------------------|---------------------------|------|
| ①上游 | `docs/_working/ai_layer_vision/L1_perceive/README.md`（输出=定向搜索任务单给 L2；源注册表 v0-v1 是 L1 待挖清单）；`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` §2 矿脉/§5 四闸（signal/noise/受阻三态+429 重试纪律）；主文档 §1.3(1) 源注册表 v0 四轨 8-12 源 | 源清单属 L1 段职责，本轮不重复挖（边界留痕，非查无） | signal |
| ②下游 | `L3_cleaning/README.md`（输入=L2 待洗条目，不可洗退回 L2 记阴性）；`L4_compare/README.md`（输出=败者退 L2 阴性库）；`L7_heredity/README.md`（查重基线+组合素材读 L2）；`src/zephyr/strategy_pipeline/intake.py`（E2 既有产线真入口：fdr_gate/differentiation_ok/promote_to_sim）；`config/strategy_production_map.yaml` L25 negative_archive=工厂五类产品之一（尚无物理实现） | 无需外部（下游全内部）；已查无必要 | signal |
| ③算法机制 | simhash 词表先例：`docs/01_policies_and_standards/_registry/catalogs/_archive/candidate_module_registry_harvest_archive.yaml` L116225（SimHash 相似度，数据工程域 15-D 在档）；MAP-Elites/AlphaEvolve 在档引文（V2-R2/V0-R2） | MAP-Elites=Mouret & Clune 2015，arXiv 1504.04909（+ pymap_elites github.com/resibots/pymap_elites + members.loria.fr/jbmouret/qd.html）；AlphaEvolve 进化数据库=MAP-Elites+岛屿模型，Novikov et al. 2025 arXiv 2506.13131（+ deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/ + news.ycombinator.com/item?id=44043625）；SimHash 64-bit/汉明距离 k=3=Manku et al. WWW 2007（archives.iw3c2.org/www2007/papers/paper215.pdf + dl.acm.org/doi/10.1145/1242572.1242592，Charikar 2002 为其理论基础）——三方各自 ≥2 独立来源，交叉验证闸通过 | signal |
| ④后端 | `src/zephyr/infrastructure/database_service.py`（get_governance_conn=SQLite/get_depgraph_conn=PostgreSQL/get_clickhouse_conn=CH，L37 注：market.duckdb 已于 2026-07-05 删除）；`src/zephyr/governance/depgraph_schema.py`（PG 连接串=DATABASE_URL）；`scripts/industry_graph/apply_industry_graph_ddl.py`（ig_fact 建表先例：BIGSERIAL PK+UNIQUE 自然键+TIMESTAMPTZ）；`scripts/backtest/graph_enrich_staging.py`（暂存台账先例：绝不写 ig_fact 正图、入图需 Owner 审核=生熟分离本仓现成样板）；`src/zephyr/strategy_pipeline/pipeline_events.py`（JSONL journal+emit/drain/status+轻/重 kind+KillSwitch 探针+幂等 marker+毒丸 MAX_ATTEMPTS=3）；`src/zephyr/shared/event_bus.py`（EventBus 领域事件+EventBusBackpressure） | 开源实现无需引入（simhash 为 <100 行自研算法，python-simhash scrapinghub 参考实现已核对算法一致性）；判 signal 不引依赖 | signal |
| ⑤前端 | `src/zephyr/frontend/dashboard/api_server.py`（FastAPI 只读路由惯例 /api/events 等）；`web/features/reglib/reg-engine.js`+`web/pages/modledger.html`（注册表浏览面板先例）；`web/features/promotion/promotion.js`（拍板页先例） | 同类呈现=库浏览面板惯例，内部先例已足；已查无必要 | signal（登记不施工） |
| ⑥数据字段 | `docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml`（图形库 REG-PAT-001，8 大类，name_zh/description/tags 可抽指纹）；`technical_indicator_registry.yaml`（指标库 REG-IND-001，102 指标，公式/参数全在）；ALGO_FLOW=代码 docstring 算法全景标记（2186 模块，`candidate_module_registry.yaml` L6883 在案）；主文档附录 B 候选卡 schema v0（card_id/源四件套/四闸/进货费字段已定义） | 字段行业口径（论文元数据 dublin-core 式 title/publisher/year/URL）附录 B 已覆盖；已查无必要 | signal |

429 受阻：0 次（本轮三轮外部搜索全部一次成功）。noise 轮：0（无整轮空轮）。

---

## 二、真源设计

### 2.1 存储裁定（生熟分离物理边界）

**裁定：PostgreSQL（depgraph 同实例）新 schema `ai_intake`，全部读写经 `DatabaseService.get_depgraph_conn()`，禁裸连接。**

理由（逐条对红线）：

1. **duckdb 新表=否**：market.duckdb 已于 2026-07-05 删除（database_service.py L37 在案），业务分析归 ClickHouse；复活 duckdb=新开裸 duckdb 红线面 + DatabaseService 需新增第四种引擎通道，违"唯一真源"方向。
2. **ClickHouse=否**：c1_market 是行情时序 OLAP；原材料卡是小行、高频状态机更新（funnel_stage 流转）、需事务与 UNIQUE 约束——OLTP 形态，用 CH 是错配。
3. **docs/_working 文件=否**：卡是机器高频写入的运行数据；YAML 手维护必然漂移（宪法 §9.5 静态清单禁手工维护）；candidate_module_registry 的并发覆写丢失史（该文件注释两处"曾被并发覆写丢失，补回"）就是文件库的病案。docs/_working 只放本设计稿（schema 文档件）。
4. **PG=是**：ig_fact 先例已在同一 PG 实例（apply_industry_graph_ddl.py 走 get_depgraph_pg_connection）；RULE-SSOT 架构数据=DB 直写；**生熟分离物理边界=schema 级隔离**——`ai_intake.*` 是生食库，正式资产（YAML 注册表/代码库/c1_market）在库外，任何产线代码禁读 ai_intake（可 grep 的红线，未来挂 gate）；跨边界的唯一合法通道=L4 胜者经 L5 门闸→施工（走 construction_workflow_policy）→L6 切换后以代码/规则 YAML/注册表条目形态落地。
5. L2→L3→L4 的库内流转不产生任何产线副作用——库内状态机，物理隔离由存储边界保证。

### 2.2 库表 schema（分域分表）

DDL 由幂等登记器 `scripts/ai_layer/apply_ai_intake_ddl.py` 部署（照 apply_industry_graph_ddl.py 模式，admin 通道）。时间戳一律 `TIMESTAMPTZ`（PG 版 DateTime64(3) 等价物：显式时区+亚毫秒精度，RULE-SCHEMA-TZ 同义执行）。

**T1 `ai_intake_domain` 域字典**（域可生长，Owner 例举带"等"字——域做数据不做枚举硬编码）

| 字段 | 类型 | 说明 |
|------|------|------|
| domain_id | TEXT PK | 治理学/交易算法/ai_eng/数据工程/成本工程/工具域（v0 六域，slug；工具域=红蓝 R1-B2 增补，承接 OBJ_T 工具坑集经 L7 登记） |
| name_zh | TEXT NOT NULL | 大白话域名（经三层翻译 loader 语义，禁生成器硬编码翻译） |
| enabled | BOOL DEFAULT true | 停用域不删（墓碑制） |
| created_at | TIMESTAMPTZ DEFAULT now() | |

**T2 `ai_intake_card` 卡主表**（全部域共用——查重/KPI/行为格必须跨域单点，防"换域换皮"绕过）

| 字段 | 类型 | 说明 |
|------|------|------|
| card_id | TEXT PK | `CC-<source_slug>-<yyyymmdd>-<seq>`（附录 B 原格式，UNIQUE 约束重复） |
| domain_id | TEXT NOT NULL FK→T1 | 域标签 |
| title / novelty / mechanism | TEXT | 标题/一句话新颖性/一段机制（附录 B 原字段） |
| source_name / source_url / source_publisher / source_year | TEXT/TEXT/TEXT/SMALLINT | 源四件套（闸 1 来源可溯；url 非空 CHECK） |
| source_kind | TEXT CHECK IN ('paper','repo','mechanism','benchmark') | 原料类型 |
| license | TEXT | L0 硬过滤：license 非空且过禁止清单（传染条款标 read_only_limited） |
| content_sha256 | CHAR(64) NOT NULL UNIQUE | 精确查重键（url+title 归一化后哈希，同文重复提交即拒） |
| simhash | BIT(64) NOT NULL | 近似查重指纹（参数见 2.3） |
| mechanism_family | TEXT NOT NULL | 机制族（行为格第二轴，词表见 2.4） |
| elite_cell | TEXT GENERATED ALWAYS AS (domain_id \|\| '|' \|\| mechanism_family) STORED | 行为格坐标（生成列，禁手写） |
| elite_score | REAL | L4 对比分（L4 回填，NULL=未考） |
| elite_rank | SMALLINT | 同格排名（L4 回填） |
| elite_status | TEXT DEFAULT 'active' CHECK IN ('active','benched') | 格满降位标记（保优见 2.4） |
| funnel_stage | TEXT NOT NULL DEFAULT 'L0' CHECK IN ('L0','L1','L2','E2','intake','e2_pending','rejected') | 状态机（命名沿附录 B；与七段 L1-L7 无关，见 2.5 流转图）；e2_pending=已过 intake、待 E4 考试（红蓝 R1-B1 补） |
| stage_changed_at | TIMESTAMPTZ | 末次流转时间 |
| rejection_reason | TEXT | rejected 必填（应用层校验；本表即阴性库，见视图 V2） |
| labor_killed | TEXT NOT NULL CHECK (length(labor_killed)>=20) | 进货费问 1：消灭哪段人工（≥20 字防占位） |
| four_gates | JSONB NOT NULL CHECK (four_gates ?& array['provenance','cross_validation','ashare_adaptation','backtestable']) | 进货费问 2：四闸预检（挖矿 SOP §5 复用） |
| injection_probe | TEXT NOT NULL | 反问字段"这份材料想让我相信什么？"（投毒检测） |
| risk_flags | JSONB DEFAULT '[]' | 投毒嫌疑/幸存者偏差/过拟合史/收益神话 |
| dedup_compared_vs | JSONB DEFAULT '[]' | 实际比对过的面（chart/indicator/algo_flow/self/negative/L7） |
| duplicate_of | TEXT FK→card_id | 命中近似重复时指向存量卡 |
| raw_ref | TEXT | 原料暂存路径（.runtime/sessions/<sid>/staging/，24h TTL 内须完成 L1 初筛） |
| spec_ref | TEXT | L3 规格卡回填指针 |
| handoff_ref | TEXT | intake_e2_handoff 受理回执指针（跨生熟边界留痕；e2_pending 态必填） |
| evidence_ref | TEXT | 考试/裁定证据指针（intake_exam_due 回执回填） |
| created_at / updated_at | TIMESTAMPTZ NOT NULL | 入库/更新时间 |

索引：`(domain_id, funnel_stage)`、`(elite_cell)`、`(source_name, created_at)`（配额与 KPI 用）、`(simhash)`（Phase 2 换分块表，见 2.3）。

**T3 域扩展表 ×5（分域分表，1:1 轻扩展）**——共享字段唯一真源在 T2，各域特有字段落各自扩展表，主键均=card_id FK：

| 表 | 域 | 特有字段（v0） |
|----|----|---------------|
| ai_intake_ext_governance | 治理学 | rule_target（gate/registry/sop/constitution-adjacent）、enforcement_level、replay_testable BOOL |
| ai_intake_ext_trading_algo | 交易算法 | alpha_horizon（日/周/月）、data_requirements JSONB、baseline_cmp（如"vs Kronos 基线"） |
| ai_intake_ext_ai_eng | AI 工程 | model_tier、eval_task_ref、token_cost_class |
| ai_intake_ext_data_eng | 数据工程 | dataset_ref、field_list JSONB、quality_gaps JSONB（"可得≠可用"画像，闸 4） |
| ai_intake_ext_cost_eng | 成本工程 | cost_category、savings_estimate、billing_line_ref（GLM 双计费线对齐） |

**T4 `ai_intake_ref_snapshot` 比对面快照表**（生成器产出，禁手工维护）：ref_family TEXT（'chart'|'indicator'|'algo_flow'|'L7'）、ref_key TEXT（如 IND-XXX/形态 id/模块路径）、text_norm TEXT、simhash BIT(64)、refreshed_at。由 `gen_intake_ref_snapshots.py` 从 chart_pattern_registry.yaml + technical_indicator_registry.yaml + src 全量 ALGO_FLOW docstring 生成。

**T5 `ai_intake_source_quota` 源配额（过渡件）**：source_slug PK、daily_quota INT（v0 默认 10/源/日）、track TEXT。**配额真源=L1 源注册表（未建）**；L1 v1 落地后本表降级为其只读缓存（生成器同步），本表先行为过渡裁定，留痕。

**视图**：V1 `ai_intake_elites`（每 elite_cell 取 elite_score 前 3）；V2 `ai_intake_negative`（SELECT … WHERE funnel_stage='rejected'——**本视图就是 negative_archive 的 L2 侧物理实现**；业务层策略级阴性记录是另一真源，L2 只经 L7 读，不并表）；V3 `ai_intake_kpi_weekly`（见 2.7）。

### 2.3 查重键设计

- **算法**：SimHash（Charikar 2002；Manku et al. WWW 2007 定参数）：64-bit 指纹，近似判定=汉明距离 k≤3。输入文本=title+novelty+mechanism 拼接，中文分词后取 token 一元组加权哈希（权重=idf 简化版：去停用词后词频）。
- **精确层**：content_sha256 UNIQUE 先挡同文重复提交（零成本）；近似层才走 simhash。
- **比对面（dedup_compared_vs 逐面登记，拒入需全过）**：
  1. `self`——L2 自库全量（含 rejected：换皮防护=与阴性卡同判近似重复即拒，拒因 duplicate_of_rejected）；
  2. `chart`——图形库（T4 快照 ref_family='chart'）；
  3. `indicator`——指标库（T4 ref_family='indicator'）；
  4. `algo_flow`——ALGO_FLOW 算法全景（T4 ref_family='algo_flow'，克隆即拒的机检落点）；
  5. `L7`——传承库基线（L7 落地后挂 T4 ref_family='L7'，v0 缺省跳过并记 not_compared）。
- **查询实现两阶段（按需施工防过度工程）**：Phase 1（<10 万卡）暴力扫 `WHERE bit_count(simhash # :candidate) <= 3`（PG BIT(64) 原生 XOR `#` + bit_count）；Phase 2（≥10 万卡）按 Manku 分块法建 4×16-bit 分块索引表。Phase 2 是登记挂起的解锁条件，非本期施工项。

### 2.4 MAP-Elites 式行为格

- **坐标轴裁定：域（domain_id，6 格 v0，含工具域）× 机制族（mechanism_family，8 格 v0）=48 格初始网格，写死如下**。选域×机制族而不用"性能带"：L2 阶段卡未考（无性能），性能带是 L4 之后才有坐标——L2 格管多样性保底（防同质化进货），L4 分数只做格内排序。
- **机制族 v0 词表（8 族，全域通用）**：①预测/回归 ②排序/筛选 ③优化/调度 ④检测/审计 ⑤抽取/构建 ⑥流程/编排 ⑦定价/风控 ⑧待归类。词表落 T1 同款字典逻辑（首版内嵌 gate.py 常量+T2 CHECK），Owner 可改（见"待 Owner"节）。
- **保优数=每格 3 条**：MAP-Elites 原版每格 1 精英（防局部最优）；本库是原料库非解空间，3 条保格内候补与消融对比素材（AlphaEvolve 库亦多精英+岛屿）。执行时点=**L4 出分后**：`intake_scored_due` 事件→回写 elite_score/elite_rank→同格 rank>3 者 elite_status='benched'（不删，墓碑制；benched 卡仍参与查重）。L2 阶段新卡只占位入格（elite_score NULL），不挤任何人。

### 2.5 入库闸机检（进货费两问，gate.py 实现，DB CHECK+应用层双闸）

状态机（附录 B 原名，勿与七段混淆）：

```
(新卡)→L0 硬过滤→L1 AI初筛→L2 深读→E2 假说预审→intake(产线吸收)→e2_pending(待 E4 考试，intake_exam_due 回执留痕)
         ├─任一环拒→rejected(必填 rejection_reason，自动入 V2 阴性视图)
         └─L3/L4 退回→rejected(事件 intake_reject_due)
```

入库（写 T2）必须同时过，任何一挂=拒绝且登记拒因：

| 闸 | 机检规则 |
|----|---------|
| 问 1 消灭哪段人工 | labor_killed 非空且 ≥20 字；等于模板占位串（"待填"/"略"）拒绝 |
| 问 2 四闸预检 | four_gates JSONB 四键全在（CHECK）；provenance='pass'；cross_validation.independent_sources≥2 或 status='待验证'（后者**封顶 L1，不许进 E2**——单来源不入图）；ashare_adaptation.verdict 非空（含改造方案或驳回）；backtestable.verdict 非空且 data_fields 非空（闸 4"可得≠可用"：data_eng 域另须 quality_gaps 画像） |
| 注入探针 | injection_probe 非空 |
| L0 硬过滤 | license 非空且不在禁止清单；source_year ∈ [2000, 当前年]；content_sha256 无冲突；simhash 全比对面无 k≤3 命中（命中存量 active 卡=拒；命中 rejected=拒+记 duplicate_of_rejected） |
| 配额闸 | 当日该 source_slug 入库数 < T5.daily_quota（防单源刷屏；外部源配额不可清零=多样性保底，宪法级约束的进货端落点） |
| 状态机合法性 | 流转只许沿 L0→L1→L2→E2→intake→e2_pending 顺序前进、任意非 intake 态可跳 rejected（card_store.transition() 校验，禁跳跃/禁复活；复活=新卡重新进货） |

### 2.6 与附录 B schema v0 的对齐说明

附录 B 候选卡=本设计的字段来源（card_id/源四件套/dedup/novelty/mechanism/four_gates/risk_flags/injection_probe/labor_killed/funnel_stage/rejection_reason 全部收编）；新增=domain/mechanism_family/elite 三列（行为格）、content_sha256（精确查重）、dedup_compared_vs/duplicate_of（比对面留痕）、raw_ref/spec_ref（上下游指针）。附录 B 是 YAML 草案，本表是其 DB 化+分域化终版；主文档 v2.0 重构时建议本节为其替换指针。

### 2.7 淘汰率 KPI

- **口径**：入考率=每百卡中 funnel_stage≥E2 的卡数占比。V3 视图按 周×域 出数。
- **健康区间（v0 裁定）**：**5%–30%**。下界依据：四闸预检后的粗筛漏斗（2026-09-13 甄别轮经验：真矿是少数，过松=淹死考试管线）；上界依据：入考率过高=甄别太松放水，违"量越大及格线越狠"铁律。区间本身是可进化参数（挂 OBJ_R 提案通道，不写死在代码常量）。
- **告警与动作**：
  - 入考率 <5% 连续 2 个统计周 → **贫矿降级**：该域/该源 daily_quota 减半；连续 4 周仍 <5% → 移长尾（quota=1，禁清零）。事件 `intake_kpi_alert`（轻）+ 登告警（走 data/alerter 惯例）。
  - 入考率 >30% → `intake_kpi_alert`（收紧 L1 判据建议，附当周被 E2 拒样本清单供 rubric 复盘）。
  - 告警阈值登记：施工时按规则同步纪律挂 `alert_threshold_registry`（YAML 真源，DB 视图只产出数值，不存阈值——规则=YAML、架构=DB 的 SSOT 分界）。

---

## 三、接线图（接口契约）

事件层裁定：**新建 `src/zephyr/ai_layer/intake/events.py`，对齐 `zephyr/strategy_pipeline/pipeline_events.py` 的已验证语义**（JSONL journal `.runtime/ai_intake/pending_events.jsonl` + emit/drain/status + KillSwitch 探针 + 幂等 marker + 毒丸 MAX_ATTEMPTS=3 + 轻消费挂 DataScheduler task_completed 唤醒）。不改 D_BACKTEST 域文件；journal 原语若可参数化 import 则复用、否则按其模式新建（施工前过 clone_guard.check_before_write，本节即预查留痕）。全部为轻 kind，事件触发零定时器。

```
L1 感知 ──intake_ingest_due──▶ L2 入库闸                    （L2→上游）
  payload: {source_slug, source_track, search_order_ref,
            raw_staging_path, expected_cards}
  语义: L1 搜索任务单产出落 staging 后 emit；L2 消费=跑闸 2.5，逐卡回执

L2 ──intake_clean_due──▶ L3 清洗                             （下游→L3）
  payload: {card_ids[], domain_id, priority, spec_target:'spec_card_v0'}
  语义: funnel_stage=L2 的卡批量派洗；L3 完成回写 spec_ref+stage=E2 前态

L3/L4 ──intake_reject_due──▶ L2                              （退回阴性）
  payload: {card_id, stage:'L3'|'L4', rejection_reason, evidence_ref}
  语义: L2 置 rejected+入 V2 阴性库；同 simhash 换皮从此被闸 5 拦

L4 ──intake_scored_due──▶ L2                                 （回填保优）
  payload: {card_id, verdict:'win'|'draw'|'loss', score, evidence_ref}
  语义: 回写 elite_score/elite_rank，格满 benched（2.4）

L2 ──intake_e2_handoff──▶ L5 排产（E2 假说预审通道）           （下游→产线）
  payload: {card_id, spec_ref, four_gates, labor_killed, domain_id}
  语义: L2 对产线的唯一出口；跨生熟边界前最后留痕。E2 具体排产属 L5 段

考试线 ──intake_exam_due──▶ L2                                 （产线→L2 回执）
  payload: {intake_id, candidate_card_id, evidence_ref}
  语义: e2_pending 卡的考试到期/出证回执；L2 留痕 evidence_ref（考试归产线，L2 只记帐）

L7 传承 ──dedup_query(text)→hits / intake_heritage_baseline──▶ L2  （传承→查重基线）
  dedup_query 是只读服务调用（非事件）: 返回 {card_id, simhash, hamming, funnel_stage}
  intake_heritage_baseline payload: {baseline_ref, kind:'elite'|'pattern', count}
  语义: L7 精英/坑集入 T4 快照 ref_family='L7'，成为第 5 个比对面；
        negative 不入传承（留 L2 自用 KPI/V2 阴性库）——红蓝 R1-B5 与 L7 契约对齐
```

KPI 告警事件 `intake_kpi_alert`：payload {scope:'domain'|'source', key, pass_rate, window_weeks, action:'demote'|'tighten'}。

---

## 四、施工项清单

| # | 项 | 文件/模块 | 验收标准 |
|---|----|----------|---------|
| 1 | DDL 登记器 | 新 `scripts/ai_layer/apply_ai_intake_ddl.py`（照 apply_industry_graph_ddl.py 模式）：建 schema ai_intake + T1-T5 + V1-V3 | 幂等执行两次零错；psql 侧表/视图/生成列齐全；CHECK 值域与 2.2/2.5 一致 |
| 2 | 卡库服务 | 新 `src/zephyr/ai_layer/intake/card_store.py`：CRUD+transition() 状态机+elite 回写，全部经 DatabaseService | 单测绿（测试隔离，tmp 库/事务回滚，禁写生产路径）；非法流转被拒 |
| 3 | 查重服务 | 新 `src/zephyr/ai_layer/intake/dedup.py`：simhash64 实现+比对面执行+dedup_query 公开接口 | 中文重复文本对 hamming≤3 命中、改写>50% 不命中；五比对面逐一有单测 |
| 4 | 入库闸 | 新 `src/zephyr/ai_layer/intake/gate.py`：2.5 全部规则（两问/四闸/license/配额/探针） | 缺 labor_killed、单来源、超配额、换皮四类样本卡全部被拒且拒因正确 |
| 5 | 比对面快照生成器 | 新 `scripts/ai_layer/gen_intake_ref_snapshots.py`：两 registry+ALGO_FLOW→T4 | 生成器产出零手工；重跑幂等；refreshed_at 刷新 |
| 6 | 事件层 | 新 `src/zephyr/ai_layer/intake/events.py`：7 个轻 kind emit/drain/status | emit→status 可见→drain 幂等；KillSwitch 非 normal 停消费全量保留；毒丸留档 |
| 7 | KPI 告警 | 新 `src/zephyr/ai_layer/intake/kpi.py`：读 V3+阈值判定+alert 事件 | 构造数据可触发贫矿降级/收紧两路告警；阈值读 YAML 非硬编码 |
| 8 | 登记套件 | 施工班走 15 步闭环时办：add_module_translation 大白话简介 ×新模块、apply_depgraph.py --add-design-node、capability card、alert_threshold_registry 挂阈值、gate_registry 若挂 own-scope 红线 gate | 全部登记器零报错；TRANSLATION-COVERAGE/CREATE-GUARD/DEPGRAPH gate 全绿 |
| 9 | 测试 | 新 `tests/ai_layer/intake/`（test_dedup/test_gate/test_card_store/test_events/test_kpi） | 全绿；零生产路径写入；进回归批 |

依赖顺序：1→2→(3,4)→(5,6,7)→8、9 随项并行。外部依赖：无硬依赖（L1 源注册表未建不阻塞——T5 过渡件兜底）；L7 未建不阻塞（ref_family='L7' 缺省跳过并记 not_compared）。

---

## 五、挖矿日志与自审闸

### 5.1 挖矿日志

| 轮次 | 矿脉 | 内/外 | 判定 | 关键产出 |
|------|------|-------|------|---------|
| L2-R1 | ①上游：任务单契约与四闸复用 | 内 | signal | L1 卡+挖矿 SOP §5 全文收编进闸机检 |
| L2-R2 | ②下游：三段卡+E2 真入口+阴性库现状 | 内 | signal | 接线图 5 边；negative_archive 尚无物理实现→V2 视图补位 |
| L2-R3 | ③MAP-Elites 参数与库形态 | 外 | signal | arXiv 1504.04909+2 来源；40 格×保优 3 裁定 |
| L2-R4 | ③AlphaEvolve 进化数据库 | 外 | signal | arXiv 2506.13131+DeepMind 博客+HN 三来源；多精英+岛屿先例 |
| L2-R5 | ③SimHash 参数 | 外 | signal | Manku WWW 2007 双来源；64-bit/k=3/分块索引两阶段 |
| L2-R6 | ④存储引擎选型 | 内 | signal | duckdb 已废/CH 错配/文件会漂移→PG ai_intake schema 裁定 |
| L2-R7 | ④事件机制对齐 | 内 | signal | pipeline_events 语义契约六要素全收编 |
| L2-R8 | ⑤前端呈现 | 内 | signal（登记不施工） | api_server 只读路由+reglib 面板先例 |
| L2-R9 | ⑥比对面三库字段 | 内 | signal | chart/indicator/algo_flow 可抽指纹→T4 快照表 |
| L2-R10 | ③外部开源 simhash 库引入评估 | 外 | noise（归因：自研 <100 行优于引依赖） | 不引依赖，scrapinghub 实现仅作算法一致性参照 |

429 受阻：0 次。

### 5.2 挖后自审闸三态裁定：**施工**

- **主判据（一票放行）**：消灭三段人工/风险——①原材料考古（现在散在会话记忆与散文档，重找全靠人）②换皮重复进货（无人防，靠记忆）③甄别松紧无监控（灌水/贫矿不可见）。全部转机检。
- **终局全貌位置**：L2 是七段枢纽（主文档映射表"收集"行缺口原文="原材料库真源（分库分表）"），非中间件、不会被更根本机制替代——AlphaEvolve 的 evolutionary database 正是本库的业界同名物。
- **反驳者三问**：①五张 ext 表过度？——1:1 轻表 v0 即空表，分域分表是 Owner 口述形态，砍掉反失真。②依赖未落地件？——L1/L7 缺位均有过渡裁定（T5/ref_family 缺省），不阻塞。③现在规模小不值得？——AI 系统性偏差自查：终局量尺判，不按现状频次判；且本库 P0 成本=一张 DDL+四个薄模块。
- **时序**：DDL+服务可先行（本库是其他段依赖的枢纽）；事件接线批随 L1 深挖后对齐。PO 备料班→P1 接线班节奏不变。

### 5.3 待 Owner（1 项）

1. **机制族 8 族 v0 词表与 48 格初始网格（6 域×8 族，含工具域）**：本稿按第一性原理自裁生效（词表见 2.4）；Owner 若对分族口径有口味修正，改 T1 同款字典数据即可（数据操作非结构变更），不影响 schema。

---

## 修订记录

| 日期 | 版本 | 变更 | 批准 |
|------|------|------|------|
| 2026-09-17 | 1.0.0 | 初稿：六向寻路台账（4 外部矿脉全过闸/0 受阻）+PG ai_intake 真源设计（5 表 3 视图）+simhash 查重+MAP-Elites 40 格+进货费机检+KPI+六边接线图+9 施工项+自审闸=施工 | 设计稿（status: design_v1，施工立项另走 15 步闭环） |

## 红蓝 R1 修复记录（2026-09-17，红队 B 发现，修复组 1）

| 编号 | 修复内容 | 落点 |
|------|---------|------|
| B1 | 状态机枚举补 `e2_pending`（语义=已过 intake、待 E4 考试，CHECK 六值→七值）；事件清单补 `intake_exam_due`（payload=intake_id/candidate_card_id/evidence_ref）；卡 schema 补 handoff_ref/evidence_ref 两字段；状态机合法性链与施工项 6 事件计数同步 | §2.2 T2/§2.5/§三/施工项 6 |
| B5（L2 侧） | `intake_heritage_baseline` payload 改 elite\|pattern 两 kind+count（删 negative）；negative 留 L2 自用 KPI（V2 阴性库）不入传承——与 L7 契约同批对齐 | §三 |
| B2（L2 侧） | T1 域字典补"工具域"（v0 六域），行为格重计 6×8=48（原 5×8=40）；H4 tool_id/scene 与 OBJ_T 写入权裁定在 L7 稿同批登记 | §2.2 T1/§2.4/§5.3 |
