---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
title: L1 感知段真源设计稿 v1——外扫+内监（进化循环的点火器）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L1 感知段真源设计稿（design_v1）

> **一句话**：L1=进化循环的点火器——**内监**（五个既有探测器的事件信号）与**外扫**（源注册表
> 驱动的节拍浅扫）双通道，产出定向**搜索任务单**喂 L2 收集段；骨架即地图，骨架长一节搜索网密一层。
> 主文档锚点：ai_layer_vision_and_roadmap_v1.md §0.5 定调 3/4/10 + 本稿 §2（源注册表/投毒防御
> 细则已迁 L1/L2/L3 各稿 §2）；方法论真源=
> [mining_sop_policy.md](../../../01_policies_and_standards/sop/mining_sop/mining_sop_policy.md)
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
| awesome-quant | GitHub | https://github.com/wilsonfreitas/awesome-quant | WebFetch 抓 README，diff 监视新条目 | 周 | 10 | active | 2026-09-17 | 当日验证（29k stars；主文档 §0.5 与本稿 §2 在档分级复用） |
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
quota=1 移长尾**禁清零**——多样性保底，主文档 §0.5 与本稿 §2(4) 闸 5）。**配额真源=本注册表**；
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
②翻译器只**开单**不执行（执行=L2 起的收集链+会话级深挖，深浅两档互不替代，主文档 §0.5 与本稿 §2(3)）；
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
   任何既有裁定；初版系 AI 自裁留痕（SOP §6 判定权），红蓝 R2 复核按 OBJ_R T3"放松永不自动"
   自律升格为 **Owner 追认+裁定登记双前置**（文末修复记录），追认前不生效；若 Owner 不追认或
   认为外扫也须事件化（如"搜一次+攒一批手动点火"），本设计的任务单层不变，仅任务宿主替换
   ——变更成本一处。

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
  登记（FactoryLaneC 同构，施工项 8）。Owner 不追认外扫裁定（§2.4 双前置）时的降级路线=
  月度体检由高模型维护班人工开会话执行（排班表登记人工任务），自动化宿主解锁顺延。
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
| **宪法/LSG** | 外扫内容按宪法 §9.11=数据非指令；进上下文前过 `zephyr.security.llm_defense.llm_security.gateway` 洗涤（主文档 §0.5 与本稿 §2(5) 投毒防御的 L1 落实）；外部代码零执行 | 原则约束，全程适用 |

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
   （治理/交易/AI 工程/数据/成本/工具六域，L2 行为格 6×8=48）；边界=定调 2（消化系统归 AI 层，找策略归业务层点菜）。
2. *常驻扫烧光 API 配额？*——三闸封顶（每源每日/总量 ≤40/贫矿降级），定调 10 进化引擎自己在配额内。
3. *搜索会不会自我放大失控？*——矿脉清单派生自骨架（他指），根约束不参与自迭代（定调 8）；
   自指（L1 优化自己的搜索策略）按定调 9 最后放开带双保险。

**三态裁定**：**施工**（#1-#8 排期，依赖序见 §四）+ **挂起排期 1 项**（#9，解锁条件=L7 定稿）。
无封矿项。设计稿自身按 SOP §6"世界地图完备优先"挖尽后再统盘裁定，施工立项另走 15 步闭环。

## 修订记录

| 日期 | 版本 | 变更 | 批准 |
|------|------|------|------|
| 2026-09-17 | 1.0.0 | 初稿：六向台账（7 轮 signal+2 处受阻如实记档）+源注册表 v1（12 源五轨全真实 URL/四闸齐）+内监接线图（五探测器真实路径信号名）+任务单 schema v1+事件触发合规裁定（FactoryLaneC 先例链）+骨架即地图机制+月度体检 schema+三边契约+9 施工项+自审闸=施工(8)+挂起(1) | 设计稿（status: design_v1，Owner 审定后施工立项） |
| 2026-09-26 | 1.0.1（复原+对账） | **正文复原**：本稿正文曾被 L4 对比段稿整档覆盖（事故留痕见文末"错配事故与复原记录"），现按 git 真源逐字节回置（基底=提交 9e612ba38d 版本，sha256 前缀 2ff581c5e9a0，272 行零内容改写）；**正文追加**两节（§七 施工项现状对账、§八 事故记录）。设计判据/阈值/验收口径**零改动** | W4-D 文档修复车道（波3 派单=94 总筹裁定册 §三 AI-2"L1 DESIGN 正文实为 L4 稿"行）；状态行仍 design_v1，翻转待 Owner/总筹 |


## 红蓝 R1 修复记录

**R1-F2（2026-09-17，红蓝 R2 复核改判）**：施工项 7（外扫节拍宿主）开工前置由"本稿 §2.4
'外扫=日历节拍+每次点火 E0 实闸'自裁补进 ruling_registry（RULE-RULING 同 commit 原子）"
**升格为双前置：Owner 追认+裁定登记**——该裁定涉放宽宪法 §9.3 射程的解释，按 OBJ_R T3
语义级"放松永不自动"自律，AI 自裁登记不足以解锁，须 Owner 先追认、追认后按 RULE-RULING
同 commit 原子补进 ruling_registry。双前置齐前施工项 7 禁开工，**其余施工项（1-6/8）不受阻**；
本稿任务单层设计不变，若 Owner 不追认仅替换任务宿主（§2.4 边界）。真源登记批次见
README §3，全目录待 Owner 项对账见 README §3.5 处置总表。

## 红蓝 R2 修复记录（2026-09-17，红队 R2 发现）

**R2**：①节锚漂移修复——全文 5 处过时节锚（v2.0 已删该节）统一改指"主文档 §0.5
与本稿 §2"（内容已迁 L1/L2/L3 各稿 §2），grep 确认零残留；②§2.6 月度体检宿主补降级路线：Owner
不追认外扫裁定（§2.4 双前置）时，月度体检由高模型维护班人工开会话执行（排班表登记人工
任务），自动化宿主解锁顺延——消解 T3 双前置射程张力（外扫未追认不连带冻结月度体检）。

## 七、施工项现状对账（2026-09-26 实测追加；§四 判据零改动，只记"落到哪/缺什么"）

> 追加人=W4-D 文档修复车道；追加理由=本稿正文失而复得后，读者需要知道 9 个施工项在 2026-09-26
> 的落地面，避免按"全部待立项"的旧假设施工。**每一行路径均为当日盘上实测**（`ls`/`grep` 逐条核过，
> 非记忆）；标"缺位"者给判据。设计口径仍以 §四 为准，本节不改任何验收标准与阈值。

| §四 项 | 现态 | 实测出处（存在性已核） | 缺位判据（若未达） |
|--------|------|----------------------|------------------|
| 1 源注册表真源落盘 | **主体已落，ROOR 挂接缺位** | `config/ai_source_registry.yaml`（166 行；`sources` 12 slug=awesome-quant/qlib/rd-agent/alphagen/arxiv-qfin/ssrn-qf/joinquant/myquant/bigquant/kronos-baseline/hf-papers/gcloud-mlops；另 `longtail_candidates` 2 条 arxiv-cs-ai/ricequant 自带"核验通过前不入 sources"注） | `docs/registry_of_registries.yaml` 内 grep `ai_source_registry` 零命中＝"挂 ROOR"子句未达 |
| 2 配额缓存同步器 | **已落** | `scripts/ai_layer/sync_ai_source_quota.py`（179 行）；目标表 `ai_intake_source_quota` DDL 在 `scripts/ai_layer/apply_ai_intake_ddl.py`；测试 `tests/ai_layer/perceive/test_quota_sync.py` | — |
| 3 矿脉清单生成器 | **主体已落，ROOR 挂接缺位** | `scripts/ai_layer/gen_search_veins.py`（318 行）产出 `config/ai_search_veins.yaml`（416 行，`registry_id: REG-AIVEIN-001`，`total_veins: 27`/`active_veins: 27`）；测试 `tests/ai_layer/perceive/test_veins.py` | `docs/registry_of_registries.yaml` grep `REG-AIVEIN`/`ai_search_veins` 零命中 |
| 4 骨架即地图触发挂接 | **缺位（派生逻辑在、自动触发链未建）** | 派生腿实测在件内：`gen_search_veins.py:121-146`（段卡目录→`VEIN-AI-<段>`，`:140-141` 取该段 DESIGN frontmatter `title` 作 `name_zh`/`keyword_seed`）、`:15` 依赖声明、`:20` MODIFY-GUARD 指本稿 §2.5 | 全仓 grep `gen_search_veins`/`ai_search_veins` 的调用方仅 3 件（生成器自身＋`gen_ai_layer_monthly_checkup.py`＋`run_ai_l1_scan_tick.py`），无 FACTORY-MAP 拦截→矿脉再生的事件挂接点＝"地图增删改名后自动重生成"未达；现为"人工/节拍调 tick 才再生"的半自动态 |
| 5 搜索任务单登记件 | **已落** | `src/zephyr/ai_layer/perceive/search_orders.py`（400 行；`TRIGGERS` 含 beat/detector/l7_prior/manual，`:76`；priority 数值闸 `:216-222`）；测试 `tests/ai_layer/perceive/test_search_orders.py` | PG 归并未接（现=file/journal 形态；`ai_compare` 之外的 orders sink 属后续工单，口径见 `closure_wave2/AI2_scheduling_host_confirm.md` §五.4） |
| 6 内监接线件（翻译器） | **已落** | `src/zephyr/ai_layer/perceive/translator.py`（362 行）；包头 `src/zephyr/ai_layer/perceive/__init__.py` 明文声明"设计真源=本 DESIGN.md"；测试 `tests/ai_layer/perceive/test_translator.py` | — |
| 7 外扫节拍任务宿主 | **半落：注册器已建、双前置未齐＝不启用** | `scripts/register_ai_l1_scan_task.ps1`（94 行，AI2 车道新建、工作区面 `A`）内置 fail-closed 双闸；被调 tick `scripts/ai_layer/run_ai_l1_scan_tick.py`（69 行，零定时器） | P1 闸查 `config/resource_profile_registry.yaml` grep `ops_ai_l1_external_scan` 零命中；P2 闸查 `ruling_registry.yaml` grep `L1_EXTERNAL_SCAN_HOST` 零命中→`-DryRun` 实测 exit 2 拒绝注册；节拍值仍无实测依据（本稿 §2.4 未定值，门位=生产流转，禁在此填数） |
| 8 月度体检生成器 | **已落** | `scripts/ai_layer/gen_ai_layer_monthly_checkup.py`（371 行）；测试 `tests/ai_layer/perceive/test_monthly_checkup.py` | 建议书→骨架项 Owner 待办分流的呈现面是否走通知板，本节不复测（留待该子项专检） |
| 9 L7 先验消费接口 | **解锁条件已成文、实现面缺位** | 解锁条件（L7 DESIGN 定稿）已于 2026-09-26 达成：`../L7_heredity/DESIGN.md:7` `status: design_final` | 消费件缺位：`translator.py:18` 明文"trigger=l7_prior/手动路径不在本件射程（l7_prior 挂起=施工项 9）"；矿脉权重仍为常量 `VEIN_PRIORITY_DEFAULT`（`gen_search_veins.py:105/144`，产出面 `config/ai_search_veins.yaml` 全条 `priority: 1.0`）＝"历史富/贫→priority 权重表＋排除词表"未落 |

**对本稿的直接后果（施工 hazard，勿忽略）**：`gen_search_veins.py:140-141` 以**本文件 frontmatter
`title`** 作 `VEIN-AI-L1` 的中文名与关键词种子。正文失配期间（见 §八），若重跑生成器就会把 L1 矿脉
改名成 L4 标题——AI2 车道 dry-run 已实测复现该污染并回退（`closure_wave2/AI2_scheduling_host_confirm.md`
§一 异常披露）。当前盘上 `config/ai_search_veins.yaml` 的 `VEIN-AI-L1` 仍为正确标题
（`name_zh: L1 感知段真源设计稿 v1——外扫+内监（进化循环的点火器）`）＝污染未落地，本稿复原后
再生即安全。**再生动作属 `config/**`，本车道零代码零配置改动，登记为总筹一行**：
`python scripts/ai_layer/gen_search_veins.py --force`（再生后应见 `total_veins` 不变、
`VEIN-AI-L1.name_zh` 保持 L1 标题）。

## 八、错配事故与复原记录（2026-09-26，W4-D 车道）

**事实链（逐 commit 取证，非顺上一车道叙述）**：

| 时点 | 提交 | `L1_perceive/DESIGN.md` 内容 sha256 前 12 / 行数 | 说明 |
|------|------|--------------------------------------------|------|
| 2026-09-17 | fc3e1e2e5f（L1 挖干） | ab2738f12513 / 250 | L1 稿诞生（title=L1 感知段真源设计稿 v1） |
| 2026-09-17 | 18e472b0e2（红蓝 R1） | e931eb2a5705 / 263 | 含 R1-F2 双前置升格记录 |
| 2026-09-17 | c0f5cc47b8（红蓝 R2） | 3baf17e62e85 / 272 | — |
| 2026-09-17 | 9e612ba38d（红蓝 R3） | 2ff581c5e9a0 / 272 | **本次复原基底** |
| 2026-09-26 | 30505c93f6（AI 层 P1 终局大单 678 件） | ebd7269a5763 / 211 | **正文被 L4 稿整档覆盖**——L1 自有稿自此在 HEAD 消失 |
| 同日并行面 | `L4_compare/DESIGN.md` 自 c0f5cc47b8 起未变 | b1734c998616 / 211 | L4 自家文件仍是**旧版**：缺 2026-09-24 的 EX-R1 销账两行（该更新的 L4 稿当时只写进了 L1 路径） |

**判性=文档矛盾事故（非有意双稿）**，四条反证：
①`L1_perceive/README.md` §状态 明文"真源设计稿=DESIGN.md（源注册表 v1 十二源五轨…9 施工项）"，与
L4 主题无关；②`ai_layer_closure_report.md`（2026-09-24 只读结案）实证当时该路径仍是完整 L1 稿
（逐节点名 §2.1/§2.2/§2.3/§四/§六）；③代码侧消费者按 L1 语义读它——`perceive/__init__.py` 与
`gen_search_veins.py:32` 均声明"设计真源=本 DESIGN.md"；④`capability_canonical_file_registry.yaml`
条目 `ai_perceive_l1` 把该路径登记为 L1 能力真源。**无任何台账**记"临时挂名/待迁移"（LEDGER_final.md、
P1_* 清单、closure_wave2 四册 grep 双稿/待迁移零命中）⇒ 上一车道"原文不可得"的担心不成立：
原文在 git 完好，R1-F2 修复记录已随复原回到本文件。

**修复动作（最小改写）**：正文＝git 逐字节回置（零重写、零判据改动）＋追加 §七/§八＋修订记录一行；
连带把 L4 稿的新版两行（EX-R1 销账）归回 `L4_compare/DESIGN.md`，使"一份稿只有唯一一个家"。
连带受害面（本车道不改，登记待总筹/波3）：历史引用行锚在正文失配期已全部悬空——
`docs/_working/archive/2026-09/kimi_audit/lane_reports/C2.md` 引 `L1_perceive/DESIGN.md:75-90 / :156-163 / :195`
（内监五通道/月度体检/禁自建排班），复原后行号重新对位，无需回改被引方。
