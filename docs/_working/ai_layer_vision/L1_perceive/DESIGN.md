---
ttl: task_bound
title: L1 感知段真源设计稿 v1——外扫+内监（进化循环的点火器）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L1 感知段真源设计稿（design_v1）

> **一句话**：L1=进化循环的点火器——**内监**（五个既有探测器的事件信号）与**外扫**（源注册表
> 驱动的节拍浅扫）双通道，产出定向**搜索任务单**喂 L2 收集段；骨架即地图，骨架长一节搜索网密一层。
> 主文档锚点：ai_layer_vision_and_roadmap_v1.md §v1.1 定调 3/4/10 + §1.3(1)(5)；方法论真源=
> [mining_sop_policy.md](../../01_policies_and_standards/sop/mining_sop/mining_sop_policy.md)
> （六向寻路/四闸/矿脉枯竭/挖后自审闸，本轮全部照办）；下游契约对齐
> [L2 DESIGN.md](../L2_intake_library/DESIGN.md) §三（intake_ingest_due）。
> 本文是设计稿非施工清单：施工另走 construction_workflow_policy 15 步闭环。

---

## 一、六向寻路台账表

> 每向=内部反查+全网搜索双动作（SOP §2）；判定三态 signal/noise/受阻，受阻≠查无（SOP §3）。

| 向 | 内部动作（真实文件） | 全网动作 | 判定 | 关键产出 |
|----|---------------------|---------|------|---------|
| ①上游 | Grep 五探测器真实路径与信号名（§2.2 全数在档）；`config/strategy_production_map.yaml` E6/E9 节点+feedback_loops 段 | MLOps CT drift 触发器/MAPE-K Monitor——均在档（V1-R2/V0-R4），在档复用零新增引文 | signal | 内监五通道接线表（§2.2） |
| ②下游 | Read [L2 DESIGN.md](../L2_intake_library/DESIGN.md)：`intake_ingest_due` payload、T5 配额过渡件、`intake_kpi_alert` 阈值 | （下游契约已在档，外查无必要=查无） | signal | §三 L1→L2 履约契约 |
| ③算法/机制 | capability_lookup 反查：挖矿 SOP/排班 v1/ops_alert_feed | alphagen 仓库现址核验（ICT-FinD-Lab，旧址 RL-MLDM 已迁）；HuggingFace papers/trending 验证；SSRN 题录模式验证 | signal | 源注册表 v1（§2.1）12 源四闸齐 |
| ④后端 | Read `scripts/register_factory_lane_c_task.ps1`（触发器仅便利+每次实闸明文）；`generate_resource_profile_registry.py`（三真源收敛）；`git_commit_gateway.py` 堵点横幅 | （后端缺口=源注册表/矿脉清单生成器未建，属施工项非引文） | signal | §2.4 合规论证锚+§2.5 机制路径 |
| ⑤前端 | `ops_alert_feed.py`→通知板→`GET /api/ops-notifications`（promotion 页横幅先例） | 同类呈现惯例=查无必要（登记不施工，SOP §2⑤） | signal | 月度建议书的呈现走通知板+docs 双轨（§2.6） |
| ⑥数据字段 | 核对 `config/resource_profile_registry.yaml` 18 字段集（含 window_type/window_expr/measured/status）+L2 T5 字段 | （字段口径=注册表自身真源，已查无缺口） | signal | 源注册表字段定稿（§2.1 表头） |

**受阻记录**：RD-Agent 仓库核验搜索超时 1 次（改在档复用 V2-R3，arXiv 2505.15155 三来源已过闸）；
MLOps 白皮书与 arXiv cs.AI 列表页 WebFetch 直连超时（MLOps 改在档复用 V1-R1；cs.AI 降**长尾待核验**，
不入 v1 注册表）。全程 429 按挖矿 SOP 60-130s 单发退避 ≤6 次，无编造引文。

---

## 二、真源设计

### 2.1 源注册表 v1 定稿（12 源·四轨+治理轨）

> **真源落点（施工项 1）**：`config/ai_source_registry.yaml`（规则+配置=YAML，RULE-SSOT）。
> 本表为定稿内容。核验日=2026-09-17；"在档复用"=引文已过四闸在档（挖矿日志见
> ai_layer_vision/README.md §4），登记出处不重复挖。健康度枚举：`active/ degraded / blocked /
> retired`（墓碑不删除）；配额单位=每次点火进漏斗的候选上限。

| slug | 轨 | URL（全真实） | 抓取方式 | 频率 | 每日配额 | 健康度 | 最后核验 | 依据 |
|------|----|--------------|---------|------|---------|--------|---------|------|
| awesome-quant | GitHub | https://github.com/wilsonfreitas/awesome-quant | WebFetch 抓 README，diff 监视新条目 | 周 | 10 | active | 2026-09-17 | 当日验证（29k stars；主文档 §1.3 在档分级复用） |
| qlib | GitHub | https://github.com/microsoft/qlib | Releases/commits 监视+社区策略库扫描 | 月 | 5 | active | 2026-09-17 | 在档（2026-09-13 甄别轮+Kronos 官方 Qlib 微调管线依赖，config FAC-E1E） |
| rd-agent | GitHub | https://github.com/microsoft/RD-Agent （含 RD-Agent(Q) 产出流） | Releases 监视 | 月 | 5 | active | 2026-09-17 | 在档复用（V2-R3，arXiv 2505.15155） |
| alphagen | GitHub | https://github.com/ICT-FinD-Lab/alphagen | Issues/commits 监视 | 月 | 5 | active | 2026-09-17 | 当日验证（KDD 2023，arXiv 2306.12964；**旧址 RL-MLDM/alphagen 已迁=换皮监测点**，闸 5 防同名反复进货） |
| arxiv-qfin | 学术 | https://arxiv.org/list/q-fin/recent （细分 https://arxiv.org/list/q-fin.PM/current 、https://arxiv.org/list/q-fin.TR/current ） | WebFetch 抓题录，四闸预检后立卡 | 周 | 20 | active | 2026-09-17 | 当日验证（题录页族全可达） |
| ssrn-qf | 学术 | https://www.ssrn.com （Quantitative Finance 学科域，论文页形如 papers.ssrn.com/sol3/papers.cfm?abstract_id=NNN） | WebSearch 站内搜，**收费墙只登记题录**（SOP 闸 1） | 周 | 10 | active | 2026-09-17 | 当日验证（题录模式+学科页） |
| joinquant | 中文 | https://www.joinquant.com/ （社区/策略精选入口） | 精选帖人工+爬虫候选 Scrapling（config FAC-E1A 在档；C1 人工版已收 597 条） | 周 | 5 | active | 2026-09-17 | 当日验证（官方站） |
| myquant | 中文 | https://myquant.cn/ | 精选帖扫描 | 周 | 5 | active | 2026-09-17 | 当日验证（官方站） |
| bigquant | 中文 | https://bigquant.com/ | 精选帖/量化 wiki 扫描 | 周 | 5 | active | 2026-09-17 | 当日验证（官方站） |
| kronos-baseline | 基线 | https://github.com/shiyu-coder/Kronos （论文 https://arxiv.org/abs/2508.02739 ） | Releases/权重更新监视；**角色=机器对手盘**：任何候选先答"比 Kronos 基线强吗"（config FAC-E1E） | 月 | 2 | active | 2026-09-17 | 在档（MOD-BT-195 kronos_adapter 已登记接入件） |
| hf-papers | 治理（AI 工程） | https://huggingface.co/papers （趋势页 https://huggingface.co/papers/trending ） | WebFetch 抓日榜题录，只收治理/agent/工具族 | 日（轻） | 10 | active | 2026-09-17 | 当日验证（含 429 退避实录，见受阻记录） |
| gcloud-mlops | 治理（方法论） | https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning | 半年重读比对（CT 触发器语义参照） | 半年 | 1 | active | 2026-09-17 | 在档复用（V1-R2：MLOps CI/CD/CT Level 0-2） |

**长尾待核验**（不入 v1，下次核验班升级）：`arxiv cs.AI recent`（https://arxiv.org/list/cs.AI/recent，
同模板推定未直连证实）、米筐 https://www.ricequant.com/ 、Vibe-Trading/QuantCode-Bench 产出流
（config FAC-E1B design_refs 在档，作为 rd-agent/qlib 的子项扫描不单列）。

**配额治理三闸**（定调 10 落点）：①每源每日配额（上表）防单源刷屏；②总量闸=全注册表每日进
漏斗候选 ≤40；③贫矿降级闸=消费 L2 `intake_kpi_alert`（入考率 <5% 连续 2 周→配额减半，4 周→
quota=1 移长尾**禁清零**——多样性保底，主文档 §1.3(4) 闸 5）。**配额真源=本注册表**；
L2 T5 `ai_intake_source_quota` 自本表落地日起降级为只读缓存（生成器同步，L2 DESIGN §2.6 已预留此裁定）。

### 2.2 内部信号接线图（探测器→定向搜索映射表）

> 五通道全部是**已建件**（路径与信号名经 Grep/Read 核实）；翻译器（信号→任务单）是施工项 6。

| 探测器 | 真实路径 | 信号名/阈值（在档原文） | 触发的定向搜索（矿脉方向） |
|--------|---------|------------------------|--------------------------|
| E6 策略衰减认证器 | `src/zephyr/signal_ashare/strategy_signal/strategy_decay_certifier.py`（MOD-SIG-150；消费=src/zephyr/data/config/tasks.yaml `trading_lifecycle_weekly` 周扫，weekend_calibration 窗） | certified/probation/failed/retired/resurrected；`oos_years_decay≥0.5=failed`；连续 FAILED_WINDOWS=8 周→retired 建议；零行输入=`strategy_decay_gate_blind` critical | retired/failed 批量出现→按 `decay_cause` 枚举定向：crowding→搜同类因子拥挤度监控新章法；regime→搜 regime 切换检测；overfitting→搜泛化护栏（PBO/DSR 后继）；depletion→搜该机制族替代品 |
| E6 顾问线 | `scripts/backtest/strategy_lifecycle_advisor.py`（`DECAY_SUSPECT_LINE`）+ `scripts/backtest/sim_governance.py` | DECAY_SUSPECT 标记行（与 api_server._FACTORY_DECAY_SUSPECT 同数四线） | 同上，与上一行**合并节流**（同矿脉冷却期 30 天防重复开单） |
| E9 实盘归因 | `src/zephyr/pf_core/core/performance_attribution_engine.py`（MOD-PF-007，Brinson-Fachler+因子归因）+ `src/zephyr/reporting/attribution_calculator.py` | 配置/选股/风格-beta-alpha 分解结果；feedback_loops FAC-E9→FAC-E2 回灌（strategy_production_map.yaml §feedback_loops） | 某风格/因子族持续负贡献→定向搜该族改进机制（如动量崩溃防护）；归因结构性缺口→搜缺失归因维度的业界做法 |
| 月度偏离 | `scripts/backtest/sim_deviation_report.py`（MOD-BT-092） | verdict=sim_deviation(月度通过)/`monthly_breach`；连续两月 breach→`decay_proposal`；阈值 AGREE_MIN=0.90/MISS_MAX=0.10/GAP_MAX=0.30（提案值公开修订留痕可改） | 成交价偏差类 breach→搜执行/滑点建模新方法；信号一致率低→搜该策略机制更稳变体；漏单率高→搜数据/触发行的新做法 |
| 堵点本 | `.runtime/audit/commit_block_events.jsonl` + `scripts/governance/commit_perf_report.py --hours 24`（横幅=src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py D5 推模式） | commit_block_events（gate 拦截/慢提交），24h 滚动窗自动消失 | 同一 gate 高频拦截→搜"同类问题的业界解法"（堵点=设计矛盾富集区，SOP §6 变更热力选题信号的搜索版）；如 syntax gate 误报→搜 AST 解析健壮实践 |
| feedback_loop Detector 族 | `src/zephyr/feedback_loop/detectors/`：anomaly.{`AnomalyDetector`,`FlappingDetector`(AlertState),`HeisenbugDetector`,`IntermittentFailurePattern`} + correlation.`AgentTrajectoryAnomalyDetector`(TrajectoryEvent) + guard.`GuardOscillationDetector` + reliability.`MetricCardinalityGuard`；调度=`scheduler_collect_detect.py`（MOD-FEEDBACK_LOOP） | 各 Detector 告警事件经 alert_dispatcher/ops_alert_feed 出口 | flapping/振荡→搜告警治理与 SLO 实践（喂 OBJ_R 尺子升级提案）；agent 轨迹异常→搜 agent 安全/评测新方法（喂 OBJ_T/OBJ_S）；heisenbug→搜测试隔离与确定性实践 |

**接线纪律**：①内监**零定时器**——全部挂既有事件源（ops_alert_feed 出口/task_completed/月报生成）；
②翻译器只**开单**不执行（执行=L2 起的收集链+会话级深挖，深浅两档互不替代，主文档 §1.3(3)）；
③全部任务单共享每日预算（§2.3 budget），内监开单优先级高于节拍扫。

### 2.3 搜索任务 schema（任务单 v1）

> 任务单=运行态工件，落 `.runtime/ai_layer/perceive/search_orders/`（journal 模式，镜像
> zephyr/strategy_pipeline/pipeline_events.py 语义；施工前 clone_guard.check_before_write 预查）。
> 产出落 `.runtime/sessions/<sid>/staging/`，emit `intake_ingest_due` 进 L2（§三）。

| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | TEXT PK | 日期+序号（如 20260917-003） |
| vein_id / vein_family | TEXT | 矿脉 id 与族（=地图节点派生，§2.5；vein_family 默认=stage/E 域） |
| trigger | enum | `beat`（节拍扫）/`detector`（内监信号）/`l7_prior`（传承先验，挂起）/`manual` |
| trigger_ref | TEXT | 信号源指针（detector 模块+信号名/事件 id/会话 id） |
| keyword_groups | TEXT[] | 中英双语关键词组（从地图节点 decision_question+algo_note 派生种子） |
| source_scope | TEXT[] | 限定源 slug 列表（空=全注册表按轨轮询） |
| budget | JSONB | max_searches（默认 6）、每向 ≤20 分钟（SOP §4 限流节奏）、429 退避 60-130s 单发 ≤6 次→记受阻 |
| priority | NUMERIC | L7 先验权重（挂起，默认 1.0）+贫矿降级修正+内监高于节拍 |
| output.staging_path | TEXT | 产出落点（staging 纪律，宪法 §9.4） |
| output.expected_cards | INT | 预期候选卡数（对齐 intake_ingest_due.payload） |
| status | enum | `open/collected/blocked/no_vein/expired` |
| produced.search_order_ref | TEXT | 回填进 L2 候选卡的上游指针 |
| created_at / expiry | TIMESTAMPTZ | 任务单 TTL=7 天，过期重排（时区显式，RULE-SCHEMA-TZ 同义执行） |

### 2.4 事件触发合规论证（裁定留痕）

**问题**（骨架卡待挖清单 5）：外扫是周期性任务还是事件驱动？宪法 §9.3"事件触发禁定时器"是否阻断？

**论证**：
1. **禁令射程**：宪法 §9.3 原文="永久系统四要素……**reconciler 必须**事件触发，禁 cron/Timer/
   sleep-loop"——禁令的射程是 **reconciler（对账/自愈类永久系统）**，不是一切计划任务。
2. **在档先例链**（全部 Owner 已批、gate 已拦）：① FactoryLaneC=`scripts/register_factory_lane_c_task.ps1`
   （ZephyrAlpha_FactoryLaneC weekly Sat 10:00，文件头明文 "**The E0 compute gate re-checks
   trade_calendar at every fire, so the trigger schedule is convenience only and never bypasses
   discipline**"）；② `src/zephyr/data/config/schedule.yaml` 21 槽位 cron（weekend_calibration 等）；
   ③ `config/resource_profile_registry.yaml` 74 实体=生成器三真源收敛（register_*.ps1 触发器/
   schedule.yaml/MANUAL_ENTITY_SEED），resource_schedule_gate 查漂移。**日历节拍+每次点火实闸复核**
   是本项目已裁定的合规架构，外扫与周六挖矿同构。
3. **裁定**：外扫分两档——①**内监=纯事件驱动**（§2.2 五通道，零定时器）；②**外扫=日历节拍+
   实闸复核**（镜像 FactoryLaneC：计划任务只当闹钟，每次点火先过 E0 日历闸+配额闸，无活可干=
   静默空转退出；登记进 resource_profile_registry 三真源，禁自建排班表——README §1.6 排班归属
   裁定）。**禁 sleep-loop 自轮询，禁浏览器自动化常驻**。
4. **边界**：月度体检同走月度节拍（§2.6，与 schedule.yaml monthly_static 同窗族）。本裁定不推翻
   任何既有裁定，系执行 AI 自裁留痕（SOP §6 判定权）；若 Owner 认为外扫也须事件化（如"搜一次+
   攒一批手动点火"），本设计的任务单层不变，仅任务宿主替换——变更成本一处。

### 2.5 "骨架即地图"机制（骨架变更→自动增删矿脉）

**原则**（定调 4）：矿脉清单=各层骨架本身。真源三件：`config/strategy_production_map.yaml`
（E0-E9+E1A-E1E，FACTORY-MAP gate priority=142 触发式硬拦）、alignment_checklist.md
（align_all.py 单入口）、TDM+治理骨架+AI 层段卡（L1-L7/OBJ_*）。

**实现路径**（施工项 3/4，禁手工维护清单——宪法 §9.5）：
1. **派生生成器** `scripts/ai_layer/gen_search_veins.py`：读地图节点（node_id/decision_question/
   stage/algo_note 摘要）+TDM 域+段卡清单→产出**矿脉清单**（vein_id=node_id 派生、
   vein_family=stage、关键词种子=decision_question）。生成器产出挂 ROOR，再生幂等。
2. **触发挂点**（复用既有变更事件，零新定时器）：① FACTORY-MAP gate 拦截提示携带"矿脉待再生"
   （镜像 RENAME-DEPGRAPH-SYNC 模式）；② `generate_project_depgraph.py --force` 链路尾部挂
   vein 再生（文件重命名已强制走此路）；③ align_all.py 跑批尾部。
3. **增删语义**：地图新增节点→新增矿脉（优先级按终局缺口量尺，SOP §6）；节点退役→矿脉标
   `archived` **墓碑不删除**（镜像 L6 A 组退役制）；改名→git mv→depgraph --force→vein 重指向同链路。
4. **消费端**：外扫节拍每轮从矿脉清单取未封矿矿脉轮询；**矿脉封矿=结构判据**（SOP §3：六向全
   查无+无未挖长尾），非轮数判据。

### 2.6 月度 AI 层骨架体检（内监慢周期）

> 挂靠：ai_layer_vision/README.md §1.6 迁移清单⑤（月度体检→L1 内监慢周期；AI 层骨架月度建议书，
> 血肉级自动/骨架级 Owner）。

- **节拍**：每月 1 日 09:00（与 schedule.yaml `monthly_static` 同窗族），任务宿主按 §2.4 ② 档
  登记（FactoryLaneC 同构，施工项 8）。
- **产出=AI 层骨架月度建议书**，schema v1：
  - `kpi_summary`：每源配额消耗/429 受阻次数/候选产出/入考率（读 L2 视图 V3 `ai_intake_kpi_weekly`）
  - `vein_coverage`：矿脉总数/已挖/长尾/封矿数（读矿脉清单生成器产物）
  - `detector_digest`：本期 E6 衰减判定分布/E9 归因要点/sim_deviation verdict/堵点计数/
    feedback_loop 告警 top（§2.2 五通道月度聚合）
  - `proposals[]`：每条 `{level, title, evidence_ref, ask}`
    - **level=flesh（血肉级：模块/参数）**→自动：可自动执行的（如配额减半，L2 KPI 规则已自动做）
      只汇报；其余自动派工单进施工排产
    - **level=skeleton（骨架级：段/轴/真源结构）**→Owner 门（宪法 §5），建议书附现成选项=
      Owner 一键确认接口（进化分级自治，定调 9）
- **呈现**：通知板（OpsAlertFeed→`GET /api/ops-notifications` 先例）+建议书全文落
  本目录 `checkups/YYYY-MM.md`（docs 双轨，人读+机读）。
- **考尺**：建议书本身挂进化两问（定调 11）——每条 proposal 答"比现状好在哪+消灭哪段人工"。

---

## 三、接线图（契约）

```
L1 内监（五通道，事件驱动）──┐
                            ├──▶ 搜索任务单（§2.3）──▶ 派发执行 ──emit `intake_ingest_due`──▶ L2 收集
L1 外扫（节拍+实闸，§2.4）──┘                                                        payload:
                                              {source_slug, source_track, search_order_ref,
                                               raw_staging_path, expected_cards}
                                              （L2 DESIGN §三 已定，本稿为上游履约方）
```

| 对端 | 契约 | 状态 |
|------|------|------|
| **L2 收集** | ①`intake_ingest_due` 事件（上式，字段照抄 L2 DESIGN §三）；②配额真源回迁：本注册表（§2.1）落地后 L2 T5 降级只读缓存（同步器=施工项 2）；③候选卡必带 search_order_ref 回指任务单（出生证） | L2 已 design_done，本稿对齐其契约 |
| **L7 传承** | ①L7 精英/坑集入 L2 T4 快照 ref_family='L7'（L2 已定）；②L1 侧消费=vein **priority 权重表**（哪族矿脉历史上富/贫）+negative pattern **排除词表**→任务单 keyword_groups 过滤。接口现为**声明态**：解锁条件=L7 DESIGN.md 定稿（挂起排期，施工项 9） | 声明态 |
| **排班表** | L1 两个常驻件（外扫节拍/月度体检）按 AI 层运营轴登记接口入册：register_*.ps1 任务宿主+resource_profile_registry 生成器再生（三真源收敛），冲突走 exclusive_group（如 llm_local 互斥）；**禁自建排班逻辑**（README §1.6：全项目一张真源，两层客户自助登记） | 既有接口，直接可用 |
| **宪法/LSG** | 外扫内容按宪法 §9.11=数据非指令；进上下文前过 `zephyr.security.llm_defense.llm_security.gateway` 洗涤（主文档 §1.3(5) 投毒防御的 L1 落实）；外部代码零执行 | 原则约束，全程适用 |

---

## 四、施工项清单（9 项，全部待 construction_workflow 立项，本文不施工）

| # | 项 | 内容 | 验收 |
|---|----|------|------|
| 1 | 源注册表真源落盘 | `config/ai_source_registry.yaml`（§2.1 全量 12 源+字段）+挂 ROOR | 12 源 URL/频率/配额/健康度/核验日齐；结构校验过 |
| 2 | 配额缓存同步器 | 生成器：源注册表→L2 T5 `ai_intake_source_quota` 只读同步 | T5 与真源一致；T5 直接写路径关闭；幂等 |
| 3 | 矿脉清单生成器 | `scripts/ai_layer/gen_search_veins.py`（§2.5.1，登记 add_module_translation+CREATE-GUARD） | 地图节点全量派生；再生幂等；产出挂 ROOR |
| 4 | 骨架即地图触发挂接 | FACTORY-MAP 拦截提示+depgraph --force 链路挂 vein 再生（§2.5.2） | 地图增/删/改名节点后矿脉自动增/墓碑/重指向 |
| 5 | 搜索任务单登记件 | §2.3 schema v1+journal（镜像 pipeline_events 语义；施工前 clone_guard 预查留痕） | 开单/状态机/TTL 过期全走 schema 校验 |
| 6 | 内监接线件（翻译器） | detector 信号→任务单（§2.2），新模块 `src/zephyr/ai_layer/perceive/`（登记+capability card） | 五探测器各注入合成信号→正确开单；同矿脉冷却期生效；共享预算扣减正确 |
| 7 | 外扫节拍任务宿主 | `register_ai_l1_scan_task.ps1`（周窗+每次点火 E0 闸/配额闸内检）+resource_profile_registry 登记 | FactoryLaneC 同构；无活点火=静默退出；漂移被 resource_schedule_gate 可见 |
| 8 | 月度体检生成器 | `gen_ai_layer_monthly_checkup.py`+建议书 schema+骨架项 Owner 待办分流（§2.6） | 建议书 schema 校验过；血肉/骨架分流正确；checkups/ 落盘 |
| 9 | L7 先验消费接口 | vein priority 权重+排除词表读取件（§三） | **挂起排期**：解锁条件=L7 DESIGN.md 定稿；接口声明先行 |

依赖序：1→2/3→4→5→6→7→8；9 独立挂起。#6/#7 落地前，L1 以"会话级深挖"（挖矿 SOP）人工点火
过渡——常驻化本身就是消灭这段人工的量尺（SOP §6 主判据）。

---

## 五、挖矿日志表

| 轮次 | 矿脉 | 内/外 | 判定 | 关键产出 |
|------|------|-------|------|---------|
| L1-R1 | ①上游：内监探测器盘点 | 内 | signal | 五通道真实路径+信号名全数在档（§2.2） |
| L1-R2 | ②下游：L2 契约对齐 | 内 | signal | intake_ingest_due payload/T5 过渡裁定/kpi 阈值收编（§三） |
| L1-R3 | ③算法机制：监控循环对标 | 内(在档) | signal | MAPE-K（V0-R4）+MLOps CT（V1-R2）在档复用，零新增引文 |
| L1-R4 | GitHub 轨源核验 | 外 | signal | awesome-quant/alphagen 当日验证；**alphagen 旧址 RL-MLDM 迁移发现**（换皮监测点入册）；RD-Agent 搜索超时=受阻 1 次，改在档复用 V2-R3 |
| L1-R5 | 学术轨+中文轨源核验 | 外 | signal | arXiv q-fin 题录页族/SSRN 题录模式/聚宽/掘金/BigQuant/米筐官方站验证 |
| L1-R6 | 治理轨源核验 | 外 | signal（部分受阻） | HuggingFace papers/trending 当日验证（429 风暴退避后成功）；MLOps 白皮书+cs.AI WebFetch 直连超时=受阻：MLOps 改在档复用 V1-R2，cs.AI 降长尾待核验 |
| L1-R7 | ④后端：触发机制先例 | 内 | signal | FactoryLaneC ps1"触发器仅便利+每次实闸"明文=§2.4 合规论证锚 |
| L1-R8 | ⑥数据字段：注册表字段核对 | 内 | signal | resource_profile_registry 18 字段+生成器三真源+T5 字段核对齐 |
| L1-R9 | ⑤前端：呈现惯例 | 内 | signal（登记不施工） | 通知板先例 OpsAlertFeed→GET /api/ops-notifications 收编进 §2.6 |

---

## 六、挖后自审闸（三态裁定，留痕）

**主判据**：L1 常驻化消灭"每次靠 Owner/会话手动发起调研"的整段人工——终局全貌（Owner 只做四类事）
里有明确位置=进化循环的点火器，**好矿**。

**反驳者一问**（最强三反驳）：
1. *与业务层 E1 五车道重复？*——否。E1 收策略原料成品（车道对 E2），L1 供全域知识原料喂 L2 生食库
   （治理/交易/AI 工程/数据/成本五域）；边界=定调 2（消化系统归 AI 层，找策略归业务层点菜）。
2. *常驻扫烧光 API 配额？*——三闸封顶（每源每日/总量 ≤40/贫矿降级），定调 10 进化引擎自己在配额内。
3. *搜索会不会自我放大失控？*——矿脉清单派生自骨架（他指），根约束不参与自迭代（定调 8）；
   自指（L1 优化自己的搜索策略）按定调 9 最后放开带双保险。

**三态裁定**：**施工**（#1-#8 排期，依赖序见 §四）+ **挂起排期 1 项**（#9，解锁条件=L7 定稿）。
无封矿项。设计稿自身按 SOP §6"世界地图完备优先"挖尽后再统盘裁定，施工立项另走 15 步闭环。

## 修订记录

| 日期 | 版本 | 变更 | 批准 |
|------|------|------|------|
| 2026-09-17 | 1.0.0 | 初稿：六向台账（7 轮 signal+2 处受阻如实记档）+源注册表 v1（12 源五轨全真实 URL/四闸齐）+内监接线图（五探测器真实路径信号名）+任务单 schema v1+事件触发合规裁定（FactoryLaneC 先例链）+骨架即地图机制+月度体检 schema+三边契约+9 施工项+自审闸=施工(8)+挂起(1) | 设计稿（status: design_v1，Owner 审定后施工立项） |
