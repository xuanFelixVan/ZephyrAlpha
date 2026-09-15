---
ttl: task_bound
completes_when: B1 批施工完成（资源画像注册表+采样器落库）后 promote 或归档
---

# [BLUEPRINT] | docs/_working/resource_schedule/resource_schedule_panorama_plan_v1.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# 资源排班全景方案 v1——施工前地图版（一库一器一闸一图）

> 2026-09-16｜会话=st-schedmap-20260916｜状态=**方案稿（挖矿完毕，施工未立项）**
> SOP 挂接：`docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md` v1.3.0（本文=construction_workflow Step 1.9 方案件；挖后自审闸已过，三态=**施工（分批）**，见 §7；施工令待 Owner）
> 母节点：资源排班全景系统——Owner 2026-09-16 立项令："排班表/资源库/全景图，所有模块的资源使用都要有记录有排班，防内存爆炸/数据库爆炸/并发混乱，压榨机器效率"
> 上游调研：全网机构实践+学术论文引证已于当日单独向 Owner 汇报（9 引文过来源可溯闸）；本文只引结论，清单见 §9
> 排班对象扫描时点：2026-09-16；文中数字为时点快照，**增量以生成器为准**（静态清单禁手工维护红线）

## 1. 目标与范围

给全项目一切消耗 CPU/GPU/内存/LLM API/网络/数据库的实体建立四件套：**资源画像注册表（库）+ 实测采样器（器）+ 排班冲突检测 gate（闸）+ 周历全景视图（图）**，把现状"排班真源散落三处（register_*.ps1 / schedule.yaml / E0 日历）、互不可见、靠人脑避坑"收敛为单一真源。

本方案明确不管（防过度工程边界）：运行时强制调度（抖动由现有队列/线程池吸收）；分布式调度（单机终局）；K8s/消息队列/Slurm 等重型基础设施引入。

## 2. 架构：一库一器一闸一图

### 2.1 库=资源画像注册表

- 路径建议：`config/resource_profile_registry.yaml`（挂 ROOR；初始骨架由生成器从现有真源抽取产出，人只补申报字段）。
- 字段设计（外部口径裁剪：SLURM 四件套 `--mem/--cpus-per-task/--time/--gres` + Airflow `pool_slots` → 单机五字段）：

```yaml
- task_id: factory_grid_executor        # 唯一键
  module_id: MOD-BT-196                 # 交叉锚（有则填，无则空）
  resource_class: cpu_heavy             # cpu_heavy|gpu|llm_api_local|llm_api_paid|network_download|db_heavy|light
  pool: heavy                           # heavy|default|realtime|light（对齐 DataScheduler 线程池四档）
  peak_mem_gb: 8                        # 申报内存天花板；红线=process_reaper 10GB 硬杀线，超线申报 gate 拦
  est_duration: "1-4h"                  # 预计时长（冲突判定的输入）
  exclusive_group: [ch_bulk_write]      # 互斥组：同组时间窗交叠只许一个在跑
  window: manual                        # cron|event|manual——**只存类型不存时间值**
  trading_sensitive: true               # true=开工前必须过 E0 窗档
  schedule_truth_source: "scripts/backtest/factory_grid_executor.py"  # 时间真源指针，防双真源漂移
  measured: {p90_mem_gb: null, p90_duration_min: null, samples: 0}    # 采样器独占回写区，人禁改
```

- 设计原则：**时间真源不搬家**——ps1/schedule.yaml 仍是时间唯一真源，库只存指针+画像；申报区（人填）与实测区（采样器填）分区隔离。

### 2.2 器=实测采样器

- 薄包装（psutil）：重活入口统一包裹，结束时回写 peak_mem/时长到 `measured` 区；画像值=滚动 P90——机制对标 K8s VPA Recommender"历史用量→建议值"思路（引文 §9）。
- 复用先例：psutil 采样点已散落 `api_server.py`/`meta/_concurrency.py`/`resource_guard.py`，本件是收口不是发明。

### 2.3 闸=排班冲突检测 gate

三个检查，作用时点=登记时/提交时结构校验（对齐 FACTORY-MAP gate 范式），**不是运行时调度器**：

1. 互斥组重叠：同 exclusive_group 两任务时间窗交叠 → 告警；
2. 内存天花板：同窗各任务 peak_mem 之和 > 物理内存安全水位 → 告警；
3. 交易时段：trading_sensitive 任务开工未过 E0 → 阻断（**直接复用 `compute_window_gate.classify_window` 纯函数**，不重写日历逻辑）。

### 2.4 图=周历全景视图

生成器产出周历网格/Gantt 泳道（左=实体泳道，横=时间轴，行业惯例见 §9）；数据真源=库+时间真源指针，视图禁手改；前端交互照抄 TDM/工厂页既有范式（只登记，施工走 B3）。

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
| 库 | 工厂图 compute_class 15 节点四档；resource_optimization.yaml 阈值+迟滞范式；daemon_registry 注册模式；process_reaper keep-list 外部注册表先例 | 无逐任务画像、无互斥组；工厂图外的实体（数据槽位/守护/回补）无挂载点 | **B1** 新建独立注册表挂 ROOR（不塞工厂图——排班对象远超工厂图边界），与工厂图节点交叉锚 |
| 器 | psutil 三处采样先例；resource_guard 四级降级 | 无统一重活包装、无实测回写闭环 | **B1** 薄采样器（scaffold 建模块） |
| 闸 | E0 classify_window/gate_decision 纯函数+理由码+fail-closed；own-scope gate 范式 | E0 只判日历不判任务重叠；backtest-run 端点无闸 | **B2** 冲突 gate（复用 E0 规则引擎）+端点接 E0（建议提前单独小批，见 §10-2） |
| 图 | TDM/工厂前端页交互全套先例；Gantt 泳道=行业惯例 | 无排班视图 | **B3** 生成器+只读前端页 |
| 告警 | 死信告警/服务总闸已上线 | 冲突告警未接线 | **B4** |
| （挂起）CH 并发护栏 | ch_writer 全局锁串行（现状可用） | 无池化/上限 | **挂起**：全局锁是"以串行避冲突"的降级解，排班闸先管"谁该几点跑"；解锁条件=B1 实测显示锁等待成瓶颈 |

## 5. 挖矿增补：还应该建什么（回答"一库一器一闸一图里还该有什么"）

1. **隐藏入口纳管**：dashboard `backtest-run`/`services-control` 两写端点是排班盲区（远程触发重回测、无 E0）——建议从 B2 拆出提前单独小批补闸。
2. **LLM 画像分两档**：`llm_api_local`（Ollama qwen3:8b，零费用但显存常驻+推理抢核）vs `llm_api_paid`（DeepSeek，付费手动）；`nightly_sentiment` 08:20 走规则法不耗 LLM，登记时防误报。
3. **互斥组从实证归纳**：`ch_bulk_write`（大 DELETE+INSERT 互斥：指标全量刷新 vs 日K vs 大回补）；`tick_drain`（local_replay 排水 vs tick 回补）；`mine_vs_exam`（周六 10:00→14:00 串行=成功先例）；`repair_passport`（亿行级修复长事务=护照登记+窗口+白名单三件套）。
4. **内存天花板对齐 reaper**：申报 peak_mem 引用 process_reaper 10GB 硬杀线作红线，两套体系不各说各话。
5. **动态实体登记**：catchup_guard、local_replay `replay_batch(100)` 这类事件触发突发负载登记为 `dynamic` 实体（无固定窗，冲突检测按"可能撞窗"处理）。
6. **规范预算净零声明**：本闸吸收替代 schedule.yaml 的人工避坑注释（实证 1 处）+ ps1 时间散落的人工核对（隐形人工，正是消灭对象）；注册表骨架由生成器产出，守"静态清单禁手工维护"红线。

## 6. 挖矿日志（SOP §7 强制）

| 轮次 | 矿脉 | 向 | 判定 | 关键产出 |
|---|---|---|---|---|
| R0 | 机构/学术调度实践 | ③外部 | signal | 9 引文：WWT 量化基金 GPU 数据中心 / AWS Batch+Airflow 回测架构 / Symeta 量化工作负载分析 / Qlib 论文+TaskManager / Airflow Pools / K8s VPA / RUSH (IPDPS 2022) / ACM 2023 内存预测 / WorldQuant BRAIN 队列 |
| R1 | 内部实体全景 | ①上游+④后端内部 | signal | 两轮只读盘点：16 计划任务+21 数据槽位+15 工厂节点+7 守护+3.C 盲区清单；四缺口（无统一真源/无画像/E0 不判重叠/CH 无上限） |
| R2 | 量化平台调度机制 | ④外部 | signal | Qlib TaskManager（Mongo 任务队列分布式执行）；AWS 官方回测调度参考架构 |
| R3 | 注册表字段口径 | ⑥外部 | signal | SLURM sbatch 官方四件套（SchedMD）+Airflow pool_slots → 裁剪单机五字段（§2.1） |
| R4 | 前端呈现惯例 | ⑤外部 | signal | Gantt 泳道=调度视图惯例（Frappe Gantt MIT / DHTMLX / Eleken timeline patterns / ServiceNow timeline）；只登记不施工 |
| R5 | 下游消费方 | ②内部 | signal | E0 闸/FACTORY-MAP gate/reaper/告警体系/晨审五处挂接点；**新发现盲区=backtest-run 端点** |
| R6 | 治理侧能力反查 | ③内部 | 查无 | `capability_lookup --find "资源 排班 调度 schedule resource 采样"`（session=st-schedmap-20260916，审计已落）返回空——无现成能力卡可复用，新建有据 |
| R7 | 交易时段适配 | A股闸 | signal | E0 现行窗档（交易日 09:00-15:30 light_only）即 A 股日历产品化；tick 盘中敏感专项入互斥组 |
| — | 受阻记录 | — | 受阻 | WebSearch 429 多轮（60-130s 间隔单发后恢复）；无模型 fallback 假引文入账 |
| — | 长尾（未挖，登记） | ①外部 | 长尾 | Prometheus/metrics 采集路线（机构怎么喂调度器）——挂起；解锁条件=B1 实测数据证明滚动画像不够用 |

矿脉枯竭判定：六向均有 ≥1 条 signal 或查无结论，未挖长尾 1 条已登记并注明解锁条件 → 结构判据达标，本批收尾。

## 7. 挖后自审闸裁定（三态出口，留痕）

- **主判据（一票放行）**：是否消灭人工参与？→ **是**。实证：schedule.yaml 05:30 避坑注释=人脑避坑现行犯；每次手动排重活（回补/批测/亿行修复）都靠会话自己记住全项目还有什么在跑——终局全貌（Owner 只做四类事）里不存在"排班运维"这个人工环节 → 好矿，**施工**。
- **终局位置**：单机全自动化工厂的调度层=终局必有位；且是"策略转正审批"门位（Owner 四类事之四）的上游供给（考试排班→及格者→审批队列）。
- **时序**：B1（登记+采样，只记录不改行为，零风险）先行；B2 闸；B3 图；B4 告警。施工令待 Owner。
- **封矿留痕（防后人重复挖）**：分布式调度器（单机终局，封）；运行时强制调度器（抖动由队列/线程池吸收，封）；K8s/MQ/Slurm 引入（重型基础设施与单机终局错配，封）；CH 连接池化（挂起，解锁条件见 §4）。
- **AI 偏差自查**：不得以"当前重活少"降级字段设计——工厂三轨满产后 3.C 层实体按周增长，字段按终局设计（§5-6 量尺=终局）。

## 8. 施工批次建议（本件不施工，走 construction_workflow Step 2 起闭环）

| 批次 | 内容 | 验收标准 |
|---|---|---|
| B1 库+器 | 生成器从 register_*.ps1+schedule.yaml+§3.C 清单抽实体产注册表骨架；scaffold 建采样器模块；对一个重活实测回写 | 全实体入库；采样器实测数据落 `measured` 区 |
| B2 闸 | 冲突 gate 三检查（互斥组/内存天花板/E0 复用）；backtest-run 端点接 E0 | 人为构造重叠场景产出告警/阻断证据 |
| B3 图 | 周历生成器+只读前端页（照抄 TDM 交互） | 视图渲染全实体，数据全部来自生成器 |
| B4 告警 | 冲突告警接既有告警通道+晨审挂接 | 告警可送达、晨审可见 |

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
| 10 | [A Machine Learning Approach for an HPC Use Case](https://www.sciencedirect.com/science/article/pii/S0167739X23000274) | ScienceDirect | 2023 |
| 11 | [sbatch — Slurm Workload Manager](https://slurm.schedmd.com/sbatch.html)（含 [GRES](https://slurm.schedmd.com/gres.html)） | SchedMD 官方 | 访问 2026-09 |
| 12 | [WorldQuant BRAIN 平台](https://worldquantbrain.com/consultant) | WorldQuant | 访问 2026-09 |
| 13 | [Frappe Gantt（MIT）](https://github.com/frappe/gantt) / [DHTMLX Gantt 开源版](https://dhtmlx.com/docs/products/dhtmlxGantt/open-source/) / [Timeline UI Design Patterns](https://www.eleken.co/blog-posts/timeline-ui-design) | 开源/Eleken | 访问 2026-09 |

## 10. 开放问题（待 Owner 裁定）

1. **注册表归属**：独立 `config/resource_profile_registry.yaml` 挂 ROOR（推荐——排班对象超工厂图边界）vs 扩展工厂图节点 schema（不推荐——数据槽位/守护/回补在工厂图无节点）。
2. **backtest-run 端点补 E0** 是否从 B2 提前为单独小批（带安全属性，建议提前）。
3. **交易窗边界**：E0 现行 09:00-15:30 vs auction 槽位 09:15-09:25 十秒级抓取已在盘中高频组——维持现状（E0 只管 heavy 重活、高频轻载走调度器守卫）还是收口统一，登记备查。
