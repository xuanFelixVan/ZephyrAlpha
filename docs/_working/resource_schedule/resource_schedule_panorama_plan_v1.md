---
ttl: task_bound
completes_when: B1 批施工完成（资源画像注册表+采样器落库）后 promote 或归档
---

# [BLUEPRINT] | docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 资源排班全景方案 v1.1——施工前地图版（一库一器一闸一图 + 字段设计）

> 2026-09-16｜会话=st-schedmap-20260916｜状态=**方案稿 v1.1（字段挖矿+对齐挂接完成，方案级矿脉枯竭达成；B1 具备进入施工 SOP 条件，施工令待 Owner）**
> SOP 挂接：`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.3.0（本文=construction_workflow Step 1.9 方案件；挖后自审闸已过两轮，三态=**施工（分批）**，见 §7）
> 母节点：资源排班全景系统——Owner 2026-09-16 立项令 + 同日追加令："字段先设计、字段也要挖矿、和全图全库机制对齐、方案挖干，全干完才进施工 SOP"（本轮即执行此令）
> 排班对象扫描时点：2026-09-16；文中数字为时点快照，**增量以生成器为准**（静态清单禁手工维护红线）

## 1. 目标与范围

给全项目一切消耗 CPU/GPU/内存/LLM API/网络/数据库的实体建立四件套：**资源画像注册表（库）+ 实测采样器（器）+ 排班冲突检测 gate（闸）+ 周历全景视图（图）**，把现状"排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历）、互不可见、靠人脑避坑"收敛为单一真源。

本方案明确不管（防过度工程边界）：运行时强制调度（抖动由现有队列/线程池吸收）；分布式调度（单机终局）；K8s/消息队列/Slurm/Prometheus 服务器等重型基础设施引入。

## 2. 架构：一库一器一闸一图

### 2.1 库=资源画像注册表（字段设计 v1.1，挖矿后定稿）

- 路径（已裁决，见 §4.5-④）：`config/resource_profile_registry.yaml`，ROOR tier 0 登记。
- **字段总表**（纪律：每字段必须生产者+消费者双证，无双证不入表）：

| 字段 | 类型/枚举 | 生产者 | 消费者 | 口径锚（外部/内部） |
|---|---|---|---|---|
| task_id | str 唯一键 | 生成器抽真源/人补 | 全部 | 同名同义于 tasks.yaml `task_id` |
| module_id | MOD-*\|null | 人 | 对齐机制（翻译表/depgraph/图1-5） | module_translation_registry 七字段 |
| map_node_id | FAC-*\|TDM-*\|null | 人 | 工厂图/TDM 交叉锚 | strategy_production_map `node_id` |
| resource_class | cpu_heavy\|gpu\|llm_api_local\|llm_api_paid\|network_download\|db_heavy\|light | 生成器初值+人复核 | 闸/图/E0 映射 | E0 `compute_class` 四值映射层：local→light，local_gpu/mixed→heavy，api→按用途拆 llm_api_*；映射放生成器，E0 真源不动 |
| pool | heavy\|default\|realtime\|light | 人 | 闸并发档/图泳道 | schedule.yaml `executor` 六值裁剪四档 |
| peak_mem_gb | float | 人申报→采样器回写实测 max | 闸内存天花板 | **process_reaper `_DANGEROUS_MEM_GB`=10 红线**，超线申报 gate 拦；全局压力阈值仍归 resource_optimization.yaml（不收编） |
| est_duration_min | int | 人申报→采样器回写 P90 | 闸重叠判定 | SLURM `--time` 口径：整数分钟、机器可算（弃 v0 草稿"1-4h"字符串——区间重叠是数学运算） |
| exclusive_group | list[str] | 人 | 闸互斥 | 组名枚举收口在注册表头部 `groups:` 定义：ch_bulk_write / tick_drain / mine_vs_exam / repair_passport / gpu_default / llm_local |
| window_type | cron\|event\|manual\|dynamic | 生成器 | 闸/图 | dynamic=catchup/local_replay 类事件突发 |
| window_expr | str\|null | **生成器从真源抽取，人禁填** | 闸/图 | schedule.yaml cron 原样；ps1 解析 schtasks 触发器 |
| schedule_truth_source | path | 人 | 生成器/漂移检测 | 唯一时间真源指针，时间值不搬家 |
| trading_sensitive | bool | 生成器按 resource_class 推导+人复核 | 闸→E0 | E0 `OPEN_BUFFER`/`CLOSE_BUFFER`（09:00-15:30） |
| measured.peak_mem_gb | float（实测 max） | **采样器独占** | 闸/图 | GNU time `%M`（max RSS）口径 |
| measured.p90_duration_min | int | 采样器独占 | 闸 | VPA target percentile 口径 |
| measured.{samples,last_at} | int/ts | 采样器独占 | 审计 | — |
| samples_uri | path | 采样器 | 审计/图 | Prometheus 命名纪律的 JSONL 流（§2.2） |
| status | active\|planned\|retired | 人 | 闸（retired 不查） | 与 depgraph build_status 六态同型简化 |
| notes_zh | str | 人 | 人 | 翻译三层 plain_zh 同款纪律（CJK≥8 非模板） |

- **砍掉的字段（防过度工程留痕）**：priority（v1 无抢占）、cpu_cores（单机 pool 档已表达）、gpu_share（GPU 实体全进 gpu_default 互斥组）、owner（module_id+map_node_id 已锚归属）。
- **关键裁决（自裁留痕）**：①est_duration_min 机器可算；②measured 双轨——注册表内只存最新快照（低频 CAS 写），原始样本流落 `.runtime/logs/resource_samples/*.jsonl`（append-only），**不建新 DB 表**，符合"规则=YAML、运行数据=.runtime"SSOT 分层；③三套压力阈值口径（resource_optimization 百分比/resource_guard 比率/reaper 绝对值）**不收编**——真缺口在"实体挂接"不在"阈值统一"，统一口径=v2 议题挂起；④resource_class→E0 映射层放生成器，不双向同步。

### 2.2 器=实测采样器（零侵入设计）

- **v1 架构裁决：按 cmdline 模式匹配观察，不改任何脚本调用点**——技术=process_reaper 同款（cmdline 子串/正则匹配已实证），采样器是 reaper 的兄弟进程：读注册表 `schedule_truth_source`→映射观测模式→周期扫描进程表→匹配者记样本。包装式（wrap 入口）仅作可选精测模式。
- 输出字段（GNU time 口径）：`{ts, task_id, pid, elapsed_min, peak_mem_gb, cpu_pct_avg, exit_code, e0_gate_result}`；样本 JSONL 字段名按 Prometheus 命名纪律（前缀 zephyr_resource_ + base unit 后缀 `_seconds`/`_bytes`，禁 `_count` 手工后缀）。
- 回写规则：memory 取**实测 max +15% 安全边际**（VPA `recommendationMarginFraction` 口径；不取分位数——引证警示 P90 对尖刺负载失真，而批测/挖矿正是尖刺型）；duration 取 P90。percentile/margin 为采样器配置项，可调。

### 2.3 闸=排班冲突检测 gate

三个检查，作用时点=登记时/提交时结构校验（对齐 FACTORY-MAP gate 范式），**不是运行时调度器**；理由码沿用 E0 四码风格扩三个：`sched_overlap_group` / `sched_mem_ceiling` / `sched_e0_block`。

1. 互斥组重叠：同 exclusive_group 两任务时间窗交叠（window_expr+est_duration_min 区间数学）→ 告警；
2. 内存天花板：同窗各任务 peak_mem_gb 之和 > 物理内存安全水位 → 告警；
3. 交易时段：trading_sensitive 开工未过 E0 → 阻断（**复用 `compute_window_gate.classify_window` 纯函数**，不重写日历逻辑）。

另含漂移检测：生成器重抽 window_expr 与注册表快照比对，真源漂移即告警（防指针失效）。

### 2.4 图=周历全景视图

生成器产出周历网格/Gantt 泳道（左=实体泳道，横=时间轴，行业惯例见 §9-13）；数据真源=库+时间真源指针，视图禁手改；前端交互照抄 TDM/工厂页既有范式；若做成独立全景图页须按"新图必挂总线"在 alignment_checklist §3 登记（§4.5-⑥）。

## 3. 全景地图：排班对象总清单

三大层，扫描时点 2026-09-16（两轮只读盘点产出）。

### 3.A 固定排班层（已有班次，缺画像）

**Windows 计划任务（真源=scripts/register_*.ps1）**：

| 任务 | 触发 | 资源类别 | 备注 |
|---|---|---|---|
| FactoryLaneC | 周六 10:00（4h 上限） | cpu_heavy | 已过 E0 闸，mine→intake→construct→translate 四连 |
| C4Exam | 周六 14:00 | cpu_heavy | IS 失败短路跳过 OOS |
| IntradayFundFlow | 每日 10:05/11:05/13:35/14:35/15:05 | network/light | 盘中 |
| IndexMinuteEOD / PostSettlement | 15:10 / 工作日 15:30 | db light | |
| PatternMining / PaperSession | 每日 09:00（5min 上限）/ 09:25 | cpu light | |
| OllamaServe | AtLogOn 常驻 | gpu/llm_api_local | qwen3:8b 驻留 |
| TickSubscriber | AtLogOn 常驻 | network+db light | 盘中高频 WAL 写 |
| DataScheduler 守护链 + CHHealthProbe/DeadmanSwitch | AtLogOn | 混合 | |
| ProcessReaper / DriftWatchdog / RSSHub / TraeCacheCleanup | 每 10min / 每 5min / AtLogOn | light | |
| TradingWatchdog | 注册为 DISABLED | — | Owner 手动启用 |

**DataScheduler 数据槽位（真源=src/zephyr/data/config/schedule.yaml）**：

| 槽位组 | 时间 | 负载 |
|---|---|---|
| heavy 槽 5 个 | daily_kline 16:30 / daily_backfill 17:00 / nightly_financial 22:00 / weekend_backfill 周一 02:00 / weekend_calibration 周一 03:00 | 周末 calibration（指标库全周期刷新）=最重 DB 负载 |
| 盘中高频 3 槽 | realtime/minute/sector 每 5 分钟 + auction 10 秒级 | 交易时段敏感 |
| 长跑 2 槽 | research_nightly 20:30（~2h）/ news_slow（90-180min/轮） | |
| catchup_guard | 05:30 | **yaml 注释自证人工避坑："05:30 而非 03:30：周一凌晨已堆两件重活"——本方案要消灭的人脑避坑实证** |

### 3.B 常驻守护层（基础负载）

OllamaServe（显存/内存常驻，GPU offload 自动）、TickSubscriber（盘中高频写）、RSSHub、DataScheduler 本体（含 local_replay 启动排水）、Dashboard api_server（light，但 `backtest-run` 写端点=可远程引爆重回测的**隐藏入口**）、LocalModelScheduler（24/7 队列线程：Embedding+OllamaChat）、看门狗族（reaper/drift/probe/deadman）。

### 3.C 事件/手动层（**无排班记录的重算力——当前最大盲区**）

| 实体 | 类别 | 时长量级 | 风险注记 |
|---|---|---|---|
| factory_grid_executor（MOD-BT-196） | cpu_heavy | 小时级 | 单批最大算力实体（2 万配方），完全手动无登记 |
| kronos_adapter（MOD-BT-195） | gpu（CUDA auto）|cpu_heavy | 分钟/标的 | 手动，GPU 与 Ollama/桌面抢显存 |
| run_sentiment_batch | llm_api_local | 小时级 | 2010-2026 全历史批量 |
| run_sft_train / convert_gguf | gpu | 小时级 | 手动重训 |
| lane_c2_agentic_miner / MCTS / hypothesis_translator / lane_b | llm_api_local+cpu | 分钟-十几分钟 | 手动/夜批 |
| factory_grid_anova（MOD-BT-197）/ E4 考尺 / DSR 重算 | cpu | 分钟级 | 手动 |
| 大回补族：bdpan tick / BSE 分钟（死线 09-17）/ 水位 7600 万行 / tick_depth5 / lof / sector880 | network_download+db_heavy | 小时-天级 | 全手动，与 heavy 槽互不可见 |
| repair_kline_tz_monthly 等修复长事务 | db_heavy | 天级 | 15.6 亿行 DELETE+回插=全库最大破坏性负载，须"护照"级登记 |
| Dashboard `backtest-run` / `services-control` 端点 | cpu_heavy 触发器 | — | **无 E0 检查的远程重算入口，闸必须纳管** |

## 4. 填空对照表（设计件 × 已有件 × 缺口 × 处置）

| 设计件 | 已有可复用 | 缺口 | 处置 |
|---|---|---|---|
| 库 | 工厂图 compute_class 15 节点四档；resource_optimization.yaml 阈值+迟滞范式；daemon_registry 注册模式；process_reaper keep-list 外部注册表先例 | 无逐任务画像、无互斥组；工厂图外的实体（数据槽位/守护/回补）无挂载点 | **B1** 新建注册表（config/，§4.5-④），与工厂图节点交叉锚 |
| 器 | psutil 三处采样先例；resource_guard 四级降级；**reaper cmdline 匹配技术（零侵入采样直接复用）** | 无统一观测、无实测回写闭环 | **B1** 采样器（reaper 兄弟进程式） |
| 闸 | E0 classify_window/gate_decision 纯函数+理由码+fail-closed；own-scope gate 范式 | E0 只判日历不判任务重叠；backtest-run 端点无闸 | **B2** 冲突 gate（复用 E0 规则引擎）+端点接 E0（建议提前单独小批，见 §10-1） |
| 图 | TDM/工厂前端页交互全套先例；Gantt 泳道=行业惯例 | 无排班视图 | **B3** 生成器+只读前端页 |
| 告警 | 死信告警/服务总闸已上线 | 冲突告警未接线 | **B4** |
| （挂起）CH 并发护栏 | ch_writer 全局锁串行（现状可用） | 无池化/上限 | **挂起**：解锁条件=B1 实测显示锁等待成瓶颈 |

### 4.5 全图全库对齐挂接清单（v1 参与机制的方式，按施工序）

> 本节=Owner 问"要不要和全图全库机制对齐"的答卷：要，且七步全数进入施工批次验收标准。

1. **蓝图先行**：采样器/闸/生成器/视图四模块各建 `docs/03_modules/` blueprint.md（MOD-ID 按 validate_module_id_naming 双轨规范起号）——depgraph `--add-design-node` 校验蓝图存在，此步必须最前。
2. **depgraph 设计态**（trae_080 三步）：`apply_depgraph.py --add-design-node <path> <MOD-*> <D_域> planned` + `--add-edge` → `sync_panorama_module.py --all` → `align_all.py` 验干净，**然后才写第一行代码**（GATE-PANORAMA-ALIGNMENT 830 + NEW-FILE-DEPGRAPH-ENFORCEMENT 双拦）。
3. **翻译三层**：每个新 .py 用 `add_module_translation.py` 登记合格 plain_zh（TRANSLATION-COVERAGE gate 59 硬拦，fail-closed）。
4. **D38 二选一裁决（自裁留痕）**：注册表放 `config/` **不进** catalogs/——理由：被采样器/闸/生成器机器读写（运行时配置属性），config/ 有 REG-EMBED-001 同类先例，且不触发 TestNewRegistryGate 的 catalogs glob；**ROOR tier 0 登记条目**（registry_id/physical_path/format/maintenance=auto(生成器)/entry_count/counting_rule/status/description，CR-007 对账），尾注 ai_usage.create_new_registry 三步全走（先查重→定 tier→建后即登记）。不建 DB 表→`_XREF_SPECS` 业务库轴不触发，无需 _GOVERNANCE_EXEMPT。
5. **gate 登记**：新闸实现进 gate_registry.yaml + rule_enforcement 体系（B2 施工时做，方案期不动；own-scope 声明义务同步履行）。
6. **视图挂总线**：B3 若产出独立全景图页，在 alignment_checklist §3 登记一行（统一原则第 6 条"新图必挂总线"）；若只是现有 dashboard 加页则免。
7. **capability card**：v1 立一张（RULE-CAPABILITY-LOOKUP 检索物料），可选不强制。

## 5. 挖矿增补：还应该建什么

1. **隐藏入口纳管**：dashboard `backtest-run`/`services-control` 两写端点（远程触发重回测、无 E0）——建议从 B2 拆出提前单独小批补闸。
2. **LLM 画像分两档**：`llm_api_local`（Ollama qwen3:8b，零费用但显存常驻+推理抢核）vs `llm_api_paid`（DeepSeek，付费手动）；`nightly_sentiment` 08:20 走规则法不耗 LLM，登记时防误报。
3. **互斥组从实证归纳**：`ch_bulk_write`（大 DELETE+INSERT 互斥）；`tick_drain`（local_replay 排水 vs tick 回补）；`mine_vs_exam`（周六 10:00→14:00 串行=成功先例）；`repair_passport`（亿行级修复=护照登记+窗口+白名单三件套）；`gpu_default`（Kronos vs Ollama vs SFT 训练抢显存——字段挖矿新增）。
4. **内存天花板对齐 reaper**：申报 peak_mem 引用 `_DANGEROUS_MEM_GB`=10 红线，两套体系不各说各话。
5. **动态实体登记**：catchup_guard、local_replay `replay_batch` 类事件突发登记为 `dynamic`。
6. **规范预算净零声明**：本闸吸收替代 schedule.yaml 人工避坑注释 + ps1 时间散落的人工核对；注册表骨架由生成器产出。
7. **挂起登记（字段盘点挖出的真缺口，v1 不做防扩散）**：①reaper 无历史画像（one-shot 无状态，惯犯进程无累计档）——采样器上线后自然获得进程侧历史，届时再议合并；②daemon_registry 无资源占用字段——采样器外挂覆盖，不动 daemon 注册结构；③全库无 owner 字段——按"Owner 一人+AI 自制"终局，owner 字段永不做。

## 6. 挖矿日志（SOP §7 强制）

| 轮次 | 矿脉 | 向 | 判定 | 关键产出 |
|---|---|---|---|---|
| R0 | 机构/学术调度实践 | ③外部 | signal | 9 引文（§9-1~9-10）：WWT 量化基金 GPU 数据中心 / AWS Batch+Airflow / Symeta / Qlib 论文+TaskManager / Airflow Pools / K8s VPA / RUSH IPDPS 2022 / ACM 2023 内存预测 / WorldQuant BRAIN |
| R1 | 内部实体全景 | ①上游+④后端内部 | signal | 16 计划任务+21 数据槽位+15 工厂节点+7 守护+3.C 盲区；四缺口（无统一真源/无画像/E0 不判重叠/CH 无上限） |
| R2 | 量化平台调度机制 | ④外部 | signal | Qlib TaskManager（Mongo 任务队列）；AWS 官方回测调度架构 |
| R3 | 注册表字段口径 | ⑥外部 | signal | SLURM sbatch 四件套（SchedMD）+Airflow pool_slots → 单机五字段 |
| R4 | 前端呈现惯例 | ⑤外部 | signal | Gantt 泳道惯例（Frappe Gantt MIT / DHTMLX / Eleken / ServiceNow）；只登记不施工 |
| R5 | 下游消费方 | ②内部 | signal | E0/FACTORY-MAP/reaper/告警/晨审五挂接点；新发现盲区=backtest-run 端点 |
| R6 | 治理侧能力反查 | ③内部 | 查无 | capability_lookup 返回空——无现成能力卡，新建有据 |
| R7 | 交易时段适配 | A股闸 | signal | E0 窗档即 A 股日历产品化；tick 盘中敏感入互斥组 |
| R8 | 既有系统字段反查 | ⑥内部 | signal | 8 系统字段清单（schedule.yaml 槽位 4 字段+tasks.yaml 227 任务 20+ 字段/工厂图节点 15 字段/reaper 判定矩阵/resource_optimization 全键/E0 判决字段/daemon 字段/WAL 字段）；真缺口 5 条→2 条本方案处理、3 条挂起（§5-7） |
| R9 | 采样输出口径 | ③外部 | signal | GNU time 官方 man7：`%M` max RSS(KB)/`%E` elapsed/`%P` CPU%——采样器输出字段直接对齐 |
| R10 | Prometheus 长尾清偿 | ①外部 | signal | 命名纪律=前缀+base unit 后秒/字节+`_total`、禁手工 `_count`（官方 naming docs）——**v1 只借命名纪律给样本 JSONL，不引入 Prometheus 服务器（单机终局，挂起）**；上轮长尾正式清偿 |
| R11 | 画像回写算法锚 | ③外部 | signal | VPA recommender：p90 target/p95 upper + **15% margin**（Erik Zilinsky/Google）+ P90 尖刺失真警示（Scaleops）→ 裁决 memory 取实测 max+margin、duration 取 P90 |
| R12 | 对齐机制消费方 | ②内外 | signal | ROOR 三步官方流程/align_all 三层/TRANSLATION-COVERAGE(59)/GATE-PANORAMA-ALIGNMENT(830)/NEW-FILE-DEPGRAPH-ENFORCEMENT/_XREF_SPECS §4 与 TestNewRegistryGate 二选一/capability card 可选——沉淀为 §4.5 七步 |
| — | 受阻记录 | — | 受阻 | WebSearch 429 多轮（60-130s 间隔单发后恢复）；无模型 fallback 假引文入账 |

**矿脉枯竭判定（方案级，两轮累计）**：六向均有 ≥1 条 signal 或查无；字段级矿脉（R8-R11）与对齐机制矿脉（R12）全产出；长尾 1 条（Prometheus）已清偿并有归属（借纪律弃服务器）；未挖长尾清零 → **结构判据达标，方案级矿脉枯竭达成**。

## 7. 挖后自审闸裁定（三态出口，留痕）

- **主判据（一票放行）**：是否消灭人工参与？→ **是**。实证：schedule.yaml 05:30 避坑注释；每次手动排重活靠会话人脑记全局——终局全貌（Owner 只做四类事）里不存在"排班运维" → 好矿，**施工**。
- **字段预算纪律（本轮新增自审）**：18 个入库字段全部生产者+消费者双证（§2.1 表）；4 个候选字段被砍有痕；3 个真缺口挂起不扩面（§5-7）——字段数按终局任务量设计，不按现状裁剪（AI 系统性偏差自查通过）。
- **时序**：B1（库+器，零侵入）先行；B2 闸；B3 图；B4 告警。§4.5 七步对齐挂接分摊进各批验收。
- **封矿留痕**：分布式调度器/运行时强制调度器/K8s-MQ-Slurm-Prometheus 服务器（均单机终局错配，封）；CH 连接池化、阈值三口径统一、reaper 历史画像、daemon 资源字段（挂起，解锁条件各异，见 §4/§5-7）。
- **施工准入**：方案级矿脉枯竭达成（§6）+ 字段定稿（§2.1）+ 对齐清单就绪（§4.5）→ **B1 具备进入 construction_workflow Step 2 条件**，施工令待 Owner。

## 8. 施工批次建议（本件不施工，走 construction_workflow Step 2 起闭环）

| 批次 | 内容 | 验收标准 |
|---|---|---|
| B1 库+器 | 生成器从 register_*.ps1+schedule.yaml+§3.C 抽实体产注册表骨架；采样器（reaper 兄弟式零侵入）；§4.5-①~④挂接 | 全实体入库；采样器对 ≥2 个重活实测回写；ROOR 条目过 CR-007 对账；align_all 验干净 |
| B2 闸 | 冲突 gate 三检查+漂移检测；backtest-run 端点接 E0；§4.5-⑤gate 登记 | 人为构造重叠场景产出告警/阻断证据；gate_registry 在册 |
| B3 图 | 周历生成器+只读前端页；§4.5-⑥视图挂总线 | 视图渲染全实体，数据全部来自生成器；若独立全景图则 §3 登记在册 |
| B4 告警 | 冲突告警接既有通道+晨审挂接 | 告警可送达、晨审可见 |

每批独立可验收；B1 落地前 §3.C 手动实体行为零变更。

## 9. 引文清单（来源可溯闸：URL+发布方+年份）

| # | 引文 | 发布方 | 年份/版本 |
|---|---|---|---|
| 1 | [Quant Hedge Fund Builds Software-defined GPU Data Center](https://www.wwt.com/case-study/quant-hedge-fund-builds-software-defined-gpu-data-center-to-reduce-cloud-dependency) | WWT 案例库 | 访问 2026-09 |
| 2 | [Backtesting Systematic Trading Strategies with AWS Batch & Airflow](https://aws.amazon.com/blogs/industries/how-to-build-and-backtest-systematic-trading-strategies-on-aws-with-aws-batch-and-airflow/) | AWS 官方博客 | 访问 2026-09 |
| 3 | [Technical Analysis of Quant Trading Research Workload](https://symeta.medium.com/technical-anaylsis-of-quant-trading-research-workload-0ea59dbde4ed) | Symeta | 访问 2026-09 |
| 4 | [microsoft/qlib](https://github.com/microsoft/qlib) + [TaskManager and Distributed Execution](https://deepwiki.com/microsoft/qlib/6.2-taskmanager-and-distributed-execution) | Microsoft / DeepWiki | 访问 2026-09 |
| 5 | [Qlib: An AI-oriented Quantitative Investment Platform](https://www.microsoft.com/en-us/research/publication/qlib-an-ai-oriented-quantitative-investment-platform/) | Microsoft Research | 2020（arXiv:2009.11189） |
| 6 | [Pools — Apache Airflow 官方文档](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/pools.html) | Apache | stable（3.x） |
| 7 | [Vertical Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/vertical-pod-autoscale/) | Kubernetes 官方 | 访问 2026-09 |
| 8 | [RUSH: Resource Utilization Aware Job Scheduling](https://pssg.cs.umd.edu/assets/papers/2022-05-rush-ipdps.pdf) | UMD, IPDPS | 2022 |
| 9 | [Memory Usage Prediction of HPC Workloads Using Machine Learning](https://dl.acm.org/doi/fullHtml/10.1145/3578178.3578241) | ACM | 2023 |
| 10 | [sbatch — Slurm Workload Manager](https://slurm.schedmd.com/sbatch.html)（含 [GRES](https://slurm.schedmd.com/gres.html)） | SchedMD 官方 | 访问 2026-09 |
| 11 | [WorldQuant BRAIN 平台](https://worldquantbrain.com/consultant) | WorldQuant | 访问 2026-09 |
| 12 | [Frappe Gantt（MIT）](https://github.com/frappe/gantt) / [DHTMLX Gantt 开源版](https://dhtmlx.com/docs/products/dhtmlxGantt/open-source/) / [Timeline UI Design Patterns](https://www.eleken.co/blog-posts/timeline-ui-design) | 开源/Eleken | 访问 2026-09 |
| 13 | [time(1) — Linux man page](https://man7.org/linux/man-pages/man1/time.1.html)（`%M`/`%E`/`%P` 口径） | man7.org | 访问 2026-09 |
| 14 | [Metric and label naming best practices](https://prometheus.io/docs/practices/naming/) / [Metric types](https://prometheus.io/docs/concepts/metric_types/) | Prometheus 官方 | 访问 2026-09 |
| 15 | [VPA: The Recommender（p90/p95+15% margin 管线）](https://erikzilinsky.com/posts/vpa1.html)（Google VPA 组工程师）/ [The Definitive Guide](https://povilasv.me/vertical-pod-autoscaling-the-definitive-guide/) / [P90 尖刺失真警示](https://scaleops.com/blog/why-pod-rightsizing-fails-in-production-a-deep-dive-into-vpa-and-what-actually-works/) | Erik Zilinsky / povilasv / Scaleops | 访问 2026-09 |

## 10. 开放问题（已全部闭环，留痕备查）

1. **backtest-run 端点补 E0**：已按"提前"裁定执行——通宵班落地并实盘冒烟（api_server `_e0_gate_decision_for_backtest`，盘中请求被拒 reason=gate_deny_trading_hours）。
2. **交易窗边界**：**已裁定=维持现状**（E0 只管 heavy 重活、高频轻载走 DataScheduler 调度器守卫+trading_day_only 任务级守卫，两层既有机制已覆盖 auction 槽位，收口统一无增量收益）——2026-09-16 验收批 a51b959d07 备查登记，无后续动作。

（原问题 1"注册表归属"已按自裁协议裁决于 §4.5-④：config/ + ROOR tier 0，留痕不再开放。）
