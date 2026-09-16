---
ttl: task_bound
title: L5 排产段——门闸与派工编排真源设计稿 v1
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L5 排产段真源设计稿：门闸与派工编排（胜者进施工队列）

> **本文性质**：骨架卡挖干产出=可直接施工的设计真源。上承骨架卡（README.md）、主文档定调
> 九/十/十一与排班归属裁定 7.5、README §1.6 三段归属。**核心裁定 D-L5-01：L5 不建任何新
> 排班真源**——排班一张真源（资源画像注册表+周历+冲突闸）是 Owner 已批裁定，L5 只做三件
> 事：①门闸判定（成熟度/配额/算力三条件 AND）②胜者证据包→任务书自动套模板 ③派工编排
> （优先级/分流/登记）。登记走既有生成器种子源扩展，闸走 E0 拉式既有函数，堵点走堵点本
> 既有台账。**硬边界自守**：本轮只写 L5_schedule_gate/ 目录内文件，零代码。
>
> **考场边界声明（红蓝 R1，L4/L5 双稿同款）**：策略候选的考场止于 L4 证据包产出；转正/流转
> 归业务层 S12-S14 与 Owner 拍板，AI 层不设第二转正门；交易算法专域不在 AI 层自动流转范围
> ——L5 工单只承接 AI 层对象（模块/模型/工具/规则/门禁参数）的施工派工，策略候选胜出只
> 产生"施工类工单"，不产生任何策略转正/上线动作。

---

## 1. 六向寻路台账表

| # | 向 | 内部反查命中（真源路径） | 外部补盲 | 判定 |
|---|-----|------------------------|---------|------|
| ① | 上游（谁喂 L5） | `L4_compare/DESIGN.md` §3：双路胜者输入已锁（库内=INTAKE_E2_HANDOFF 事件加 evidence_ref；库外=experiment 卡 verdict='win' 即门闸输入）；L4 §2.2 带星胜（win*）指令"L5 排产降优先级"；L4 §2.3 锁定机制①指名"L5 工单生成器机检 hash 缺失/不匹配=不许派工"；`L2_intake_library/DESIGN.md`：INTAKE_E2_HANDOFF 事件（payload {card_id, spec_ref, four_gates, labor_killed, domain_id, evidence_ref}，末字段 R2 由 L2 稿补；"E2 具体排产属 L5 段"） | — | signal |
| ② | 下游（谁吃 L5） | `L6_ab_switch/DESIGN.md`：L5→L6 契约已锁 {work_order_id, module_id, challenger_branch, criteria_yaml_ref+hash, domain, tier_action}，两事件分工：work_order_shadow_ready（四闸全过+worktree 就绪→L6 影子上岗）与 work_order_closed_due（终局关单回执→L7 传承），R4 澄清勿混称；主文档 §3.5 维护班领单/关单四闸；堵点本 `.runtime/audit/bottleneck_ledger.jsonl`（{ts,kind:'dead_letter',qid,session_id,reason,protocol:'专人专事'} 实档结构） | — | signal |
| ③ | 算法机制（怎么闸/怎么排） | E0 真源 `scripts/backtest/compute_window_gate.py`：拉式闸门（check_gate() 纯函数+四理由码+fail-closed+四值词表 local/api/local_gpu/mixed，CONSTANT OPEN_BUFFER 09:00/CLOSE_BUFFER 15:30，exit 0/3/1）；belt_daemon `src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py`：watchdog 事件四件套（目录 file-created→0.5s 防抖→单例锁 PID+TTL 600s→bootstrap 排空，无常驻轮询）；`config/resource_profile_registry.yaml`+生成器 `scripts/governance/generators/generate_resource_profile_registry.py`：E0_CLASS_TO_RESOURCE 映射层、TRADING_SENSITIVE_CLASSES、幽灵池禁令、种子源 I3+`manual_lane_c_agentic_miner` AI 任务登记先例 | MLOps CT 触发器分类：schedule-based vs trigger-based 再训练排程（MLflow《Continuous Training in ML: A Practical MLOps Guide》mlflow.org/articles/what-is-continuous-training-ml/；Snowflake CT 页 snowflake.com/en/artificial-intelligence/machine-learning/mlops/continuous-training/——drift 触发+challenger 逐版治理；enhancedmlops.com 事件驱动再训练）。触发器思想收编为"胜者到达+资源释放"双事件源，schedule-based 排程被宪法"事件触发禁定时器"否定不收 | signal |
| ④ | 后端（落哪个仓/什么件） | 工单库表=PG 同实例**独立 schema `ai_scheduling`** 新表（与 L2 ai_intake schema 隔离，产线禁读界不破；对标 L2 apply_ai_intake_ddl.py/L4 ai_comparison_experiment 母版，全经 `src/zephyr/infrastructure/database_service.py` 禁裸连接）；事件层=`src/zephyr/ai_layer/intake/events.py` 六要素母版（JSONL journal+KillSwitch 探针+毒丸+task_completed 唤醒）；登记数据面=`config/evolution_schedule_seeds.yaml`（新增种子文件，生成器新源 I7 消费）；policy 常量=对标 `config/comparison_policy.yaml`（L4 C1 同款治理锚定头） | — | signal |
| ⑤ | 前端（Owner 门位呈现） | `src/zephyr/frontend/dashboard/web/features/promotion/promotion.js` 拍板页先例（L4/L2 两稿同判：登记不施工归本段消费）；骨架级"一键确认"=拍板按钮+只读路由惯例（api_server.py） | — | signal（登记不施工） |
| ⑥ | 数据字段（记什么） | 主文档附录 A 任务书 schema v0 十三字段；§3.4 配额自治调度四资源（子代理槽 2-3/LLM token/GPU 档/提交带宽）；risk_tier_registry.yaml（域→tier→human_gate，未列默认 low）；README §1.6 登记接口归属（AI 层运营轴）；registry 18 字段中 8 个可由工单自动推导 | — | signal |

**受阻记录**：EX-R1（CT 触发器分类核验）首轮 429 风暴（连续 5 次 rate limit），按挖矿 SOP
90s 单发间隔退避后第二轮成功——全轮次最终成功，无编引文。

---

## 2. 真源设计

### 2.1 工单自动生成器（D-L5-02）

**事件源（红蓝 R1 裁定：events journal=唯一真源）**：胜者落库即 emit
`evolution_winner_due` 事件（JSONL journal，intake/events.py 母版）→ 工单生成守护
`order_daemon` 只消费 journal（尾随+last_read_offset 断点续读），**无常驻轮询无 cron**。
**watchdog 双通道合并裁定**：watchdog 不再独立扫 winners/ 目录，降级为 journal 的
**补偿读指针**——守护重启/漏事件时从 last_read_offset 起补放未消费事件（belt_daemon 的
防抖/单例锁 PID+TTL 600s/僵尸检测机械照用，仅作用对象从目录改为 journal 文件）。
裁定理由（一行）：目录扫描与 journal 双通道=双真源，必然产生消费竞态与重复生成工单，
events.py 母版（journal+唤醒+毒丸）已足够承载，砍目录通道。守护非施工会话所有（专属
消费者，对标 belt"不属于任何 AI 会话的常驻消费者"设计）。

**字段映射表（胜者证据包→任务书附录 A schema v0）**：

| task_order 字段 | 来源（L4 证据包/L2 事件） | 机检 |
|----------------|--------------------------|------|
| schema_version / order_id | 常量 '0.1' / 生成器产 WO-YYYYMMDD-NNN | 全局唯一 |
| title | experiment 卡标题或候选卡 mechanism 一句话 | 非空 |
| contractor | {session: 空（派工时填）, model_tier: 分流器定, lane: B4} | — |
| objective | evidence_pack 利弊对照摘要+候选卡 mechanism | 非空 |
| definition_of_done | **criteria_ref: experiment_id#criteria_hash**（L4 判据预注册锚点）+L6 回执字段预登记 | hash 与 experiment 卡 frozen 值不匹配=拒派（L4 §2.3① 指名义务） |
| red_lines | 老组不动（champion_ref 反查 depgraph 文件清单冻结）+附录 C 永不触碰+域内禁碰清单 | 禁碰清单非空 |
| budget | {timebox: 按对象类常数, compute_class: §2.3 归类, max_commits, subagent_quota: ≤3} | 配额池余量核验（§2.6） |
| pre_rulings | ruling_registry 按域预查命中项 | 引用存在性核验 |
| acceptance | mechanical 三件套；reviewer 异会话异档 model_tier=strong（不可降档）；owner_gate=分流器判定 | §2.4 |
| rollback / constitution_discipline / honesty_clause | 固定模板（worktree abort+L6 回切引用） | — |

**缺字段不许派工**：必填字段机检（附录 A"机检 gate 校验必填"同款），任一缺失=工单落
`held_incomplete` 并发堵点本事件，禁静默降级。

### 2.2 区域成熟度门闸（D-L5-03，门闸=T0）

**区域划分口径**：区域=候选卡/实验卡既有 `domain_id` 词表（L2 入库登记，对齐
functional_domain_registry 域划分），不新造区域分类学；OBJ_M/OBJ_T/OBJ_R 各算一个专域；
七段骨架自身=骨架域（永远走 Owner 门，见 §2.4 R3）。

**阈值定义（v1 设计定值，全部进 policy 常量层，Owner 点头前为自裁建议值）**：

| # | 阈值 | 初值 | 统计底表 |
|---|------|------|---------|
| M1 | 该区域 win 计数 | N_win ≥ 2（单胜不开闸，防噪声单点） | ai_comparison_experiment 按 domain_id 聚合 |
| M2 | 对比胜率 | win/(win+loss) ≥ 60%（draw 不计分母；样本下限 N_total ≥ 3） | 同上 |
| M3 | 证据新鲜度 | 最新 experiment archived_at ≤ 90 天，超龄区域计数清零重攒（陈旧胜利不开门） | 同上 |
| M4 | 区域白名单（冷启动） | 首批 Owner 点头清单登记进 policy 文件；自治运行满一季可按 OBJ_R 流水线提案退役 | policy 常量 |

**阈值登记处（OBJ_R 约束）**：M1-M4 与一切闸参数进 `config/schedule_gate_policy.yaml`
（新增，治理锚定头+"尺子归治理层"声明）——受重考历史约束：改动走 OBJ_R 四步（AI 提案→
治理立案→Owner 修标→重考历史），AI 层不持尺（README §1.6 标准库归属裁定）。

**触发时点**：T0 门闸在胜者到达时评一次（不过=工单 `held_maturity` 挂起，区域每有新
experiment archived 事件重算，过线即自动转 pending——事件唤醒非轮询）。

### 2.3 与 E0/排班 v1 接线（D-L5-04）

**算力档归类规则（工单分段制）**——进化施工工单拆两段，各按 E0 四值词表归类（禁自造第五值）：

| 段 | 内容 | compute_class | E0 语义 |
|----|------|---------------|---------|
| 施工段 | AI 会话改码+本地轻量 tests | local→light | E0 永远放行（REASON_ALLOW_LIGHT），占子代理槽+token 配额 |
| 验收段 | C4 双窗批测/DSR/门禁重放/训练 | local_gpu→cpu_heavy / GPU 推理→llm_api_local / CH 大重放→db_heavy / API 评分→api→llm_api_paid | 受闸四类（TRADING_SENSITIVE_CLASSES 逐字对齐）：开工瞬间拉式问闸；llm_api_paid 免 E0 但免不了配额（定调 #10） |

**问闸方式=纯拉式（E0 INVARIANTS 同款）**：每段开工瞬间调一次
`check_gate(purpose='evolution_<order_id>', compute_class=<段>)`，exit 3=拒→工单转
**deferred**（§2.7），资源恢复事件重评回 pending（新 schedule 槽位 `evo_heavy_window_opener`
发 heavy_ok 窗开事件+复用 DataScheduler task_completed 唤醒，**不轮询不 sleep-loop**）。

**走排班登记接口的字段（README §1.6 ③使用=客户自助登记，AI 层运营轴供接口）**：登记=
自动写种子文件 `config/evolution_schedule_seeds.yaml`（新源 I7）+ 触发生成器
`generate_resource_profile_registry.py` 再生（每小时自检任务已存在，自动吸入）——GENERATED
注册表零手改。种子条目按 registry 18 字段子集：

| 字段 | 取值 |
|------|------|
| task_id | `evo_<order_id>_<seg>` |
| resource_class | E0 四值映射（生成器 E0_CLASS_TO_RESOURCE 同层） |
| pool | lanes 五档真池词表内（**幽灵池禁令**：禁 `light`；禁 cpu/gpu 空间维值作泳道） |
| peak_mem_gb / est_duration_min | 按对象类常数初估，sampler 实测回填 measured（禁编造） |
| exclusive_group | groups 词表按段选挂（gpu_default/llm_local/mine_vs_exam/ch_bulk_write） |
| window_type / window_expr | event（开工事件触发）/ null（人禁填字段留空） |
| trading_sensitive | 按 TRADING_SENSITIVE_CLASSES 推导，不手填 |
| schedule_truth_source / notes_zh | seeds 文件路径 / 工单 title |

先例=`manual_lane_c_agentic_miner`（llm_api_local+exclusive_group [llm_local]+manual 窗）。

### 2.4 骨架级分流器（D-L5-05）

**判定规则（三证据机检，任一命中骨架级即骨架级）**：

| # | 证据 | 模块级 | 骨架级 |
|---|------|--------|--------|
| R1 | 作用域 | 目标文件全部落在既有 module_id 的 depgraph 已登记范围内 | 出现新模块/新顶层文件/跨域新依赖边 |
| R2 | 风险 | risk_tier_registry 未命中 high（未列域默认 low） | 命中 high 九域；或触达宪法正文/规则 YAML 权限语义/根约束清单 |
| R3 | 自指 | 目标在 AI 层之外 | 目标=AI 层自身（src/zephyr/ai_layer/**、gate 体系、排班表）——定调 #9"先他指后自指"，v1 自指一律 Owner 确认 |

**路由**：模块级→owner_gate=false，自动派施工队（fresh worktree 会话）；骨架级→
owner_gate=true，生成**提案包**（利弊对照+两问打分展示）进前端一键确认页（promotion.js
惯例），Owner 点头后转工单派工，Owner 拒→工单作废归档（审计链留痕不删）。

### 2.5 排产优先级规则（D-L5-06）

**进化量尺两问打分法**：`score = labor_segments × advantage_bucket × demote`

- **两问①消灭人工段数** `labor_segments`：labor_killed 结构化拆段计数（1-4）
- **两问②对比优势幅度** `advantage_bucket`：L4 evidence_pack significance 分桶 large=2.0 /
  medium=1.5 / small=1.0（分桶线进 policy 常量）
- **带星降权** `demote`：win*（L4 公平性"带星胜"）×0.5 且排同分队尾
- 排序=score 降序→FIFO；**防饥饿**：pending 龄 >7 天一次性 +1.0 bump
- 骨架级提案同打分但仅用于确认页展示排序，不占自动派工队列
- **repair 工单不与进化比 score**：维护班独立队列（专人专事），但共享配额池；事故修复默认
  优先于进化（业务连续性>进化速度）

### 2.6 配额联动（D-L5-07）

**四读数（§3.4 配额自治调度四资源，全部既有件读出，不建新计量系统）**：
Q1 活跃施工会话数（gateway 活跃 claim 计数，上限=并发槽）；Q2 工单 subagent_quota（≤3）；
Q3 当日 token（cost_tracker usage_records 日累计 vs 预算线）；Q4 提交带宽（commit_queue
pending 深度）；另 GPU 档走 registry exclusive_group 冲突闸（既有件）。

**超限降级路径（梯度表，终点禁自我扩容=定调 #10）**：

| 超限 | 动作 |
|------|------|
| Q1 满 | 工单转 deferred（门闸保持关），会话释放事件唤醒重评回 pending |
| Q2 超 | 降单代理模式；任务确需多代理→拆单或 defer+堵点本 |
| Q3 超 | model_tier 降档 strong→flash（**仅限施工段**；验收 reviewer 恒 strong）；仍超→转 deferred 至次日窗+堵点本 |
| Q4 积压 | 暂停新派工（在途工单照常），belt drain 事件唤醒 |
| GPU 档冲突 | 验收段改排下一 heavy_ok 窗，exclusive_group 排队留痕 |

所有降级动作写工单审计字段；同一工单连续 3 次 defer→堵点本 CRITICAL（对标 belt
_ENV_ABORT_ESCALATE=3）。**T1 派工前置双预检**：①老组不动——champion 文件清单（depgraph
反查）有活跃 claim/在途会话=hold（HELD-OVERLAP 不硬闯，宪法规则 3 同语义）；②KillSwitch
探针（L2 events 同款，非 normal 全量保留停消费）。

### 2.7 工单状态机（红蓝 R1-B10 补全：defer 补态、dead 补进入判据）

**状态枚举**（C2 CHECK 同步）：`pending / held_maturity / held_incomplete / dispatched / deferred / done / dead`

| 态 | 入边事件 | 退出（→向） |
|----|---------|------------|
| pending | 胜者到达生成工单（order_created_due）；held 挂起解除/deferred 重评过线 | 派工→dispatched；缺字段→held_incomplete；成熟度不过→held_maturity |
| held_maturity | M1-M4 门闸任一不过（§2.2） | 区域新 experiment archived 事件重算过线→pending |
| held_incomplete | 必填机检缺失（§2.1） | 补齐回执→pending；超期→堵点本 |
| dispatched | 派工指令（order_dispatch_due，Q1-Q4 配额+E0 双预检过） | 关单四闸全过→done；施工失败/资源中断回执→deferred |
| **deferred**（红蓝 R1 补态） | 进入=**配额不足（Q1-Q4 任一超限）或算力窗关闭（E0 exit 3）**——此前 defer 只有 order_deferred_due 事件无对应态，就此补齐 | 退出=**资源恢复事件**（会话释放/heavy_ok 窗开/belt drain 唤醒）重评→pending；同一工单连续 3 次 defer→堵点本 CRITICAL（§2.6） |
| done | 关单四闸全过（own-scope/gate 绿/回归绿/独立复核） | 发 work_order_shadow_ready（→L6）+work_order_closed_due（→L7）；dead 分支另发 work_order_dead |
| **dead**（红蓝 R1 补进入判据） | 进入判据=**连续 N 次派工失败**，或**任务书机检连续三次不过**（N 初值 3，设计定值非实测标定——**进 OBJ_R 阈值盘点**，首轮运行数据回来后按 OBJ_R 流水线提案修订） | 终态：归档留审计不删；复活仅 Owner 手递重开（新 order_id，旧单不复活）；dead 回执事件 `work_order_dead`（payload={order_id, reason}）→L2 候选卡跳 rejected（R2 补终态回传，L2 稿同批补入边） |

---

## 3. 接线图（五契约+一底线）

| 对端 | 契约 | 方向 | 载荷 |
|------|------|------|------|
| **L4（胜者输入）** | 双路：①库内对象=L2 既有 `INTAKE_E2_HANDOFF`（payload 增 evidence_ref——R2 已经 L2 稿同批落地）；②库外对象=experiment 卡 verdict='win' 直达 | L4/L2→L5 | verdict + evidence_pack {experiment_id, criteria_hash, 判据结果, significance, too_good 结论, 公平性核验（含带星）} + {card_id, labor_killed, domain_id} |
| **L6（施工完成→切换）** | 影子上岗券 work_order_shadow_ready：**工单关单四闸全过**（own-scope/gate 绿/回归绿/独立复核，主文档 §3.5 既有定义）+worktree 就绪才发 | L5→L6 | {work_order_id, module_id, challenger_branch, criteria_yaml_ref+hash, domain, tier_action}（L6 DESIGN 已锁，本稿只消费） |
| **排班系统** | 四线：①E0 拉式问闸（每段开工一次 `check_gate()`，真源 compute_window_gate.py 零改造）；②登记接口=seeds 种子文件+生成器再生（§2.3 字段表）；③配额读数四源（§2.6）；④exclusive_group 冲突闸+周历可视（一库一闸一图既有件） | L5↔排班 | 种子 18 字段子集 / 理由码 gate_allow_light_always 等 / PoolStats / 冲突判决 |
| **堵点本** | 工单 held_incomplete/连续 defer/配额饥饿→append（{ts, kind, order_id, reason, protocol:'专人专事：高模型维护班清账'} 实档 schema 同款）；告警阈值复用 belt 语义（≥20 条或最老 >24h） | L5→堵点本 | JSONL 行 |
| **维护班队列** | kind=repair 工单同 schema 分队列（堵点告警/纠察退单/红蓝发现→自动生成，§3.5）；risk_tier 分级派工（机械债全自动/逻辑债强制复核/high 九域 Owner） | L5→维护班 | {order_id, kind, risk_tier, affected_module, recipe_ref（缺陷模式库命中带配方派工）} |
| **目标常数段（底线）** | 排班一张真源不变（README §1.6）；policy 常量=治理层资产走 OBJ_R；五道自我放大闸照用（施工会话无权改自己验收判据=附录 C #5，工单生成器对 definition_of_done 只读引用） | L5←常数 | M1-M4/分桶线/降级线/配额上限 |

---

## 4. 施工项清单（全部为设计交付，施工另派工，本轮零代码）

| # | 项 | 文件（新增/修改） | 验收标准 |
|---|-----|------------------|---------|
| C1 | policy 常量文件 | `config/schedule_gate_policy.yaml`（新增，治理锚定头+OBJ_R 管辖声明） | 全常数齐（M1-M4/优势分桶/降级线/配额上限/首批白名单区）；Owner 点头记录位 |
| C2 | 工单库表 | PG 同实例独立 schema `ai_scheduling` 新表 `ai_work_order`+DDL 登记器 `scripts/ai_layer/apply_ai_layer_scheduling_ddl.py`（L2 母版同模式；与 L2 ai_intake schema 隔离，产线禁读界不破） | 全经 DatabaseService；TIMESTAMPTZ；状态机 CHECK（pending/held_maturity/held_incomplete/dispatched/deferred/done/dead，迁移判据=§2.7）；append-only 审计字段 |
| C3 | 事件层 | `src/zephyr/ai_layer/scheduling/events.py`（对齐 intake/events.py 六要素） | 8 个轻 kind（evolution_winner_due/order_created_due/order_confirmed_due/order_dispatch_due/order_deferred_due/work_order_shadow_ready=done 出口影子上岗券→L6/work_order_closed_due=关单回执→L7/work_order_dead=死单回执→L2 rejected；红蓝 R3 补全 3 项，R4 计数校正 8）；KillSwitch 探针；毒丸；零定时器 |
| C4 | 工单生成守护 | `src/zephyr/ai_layer/scheduling/order_daemon.py`（journal 唯一真源：尾随+last_read_offset 断点续读；belt_daemon 防抖/单例锁 PID+TTL 600s 机械仅作 journal 补偿读指针，§2.1 裁定不扫目录） | §2.1 映射表全实现；criteria_hash 机检缺失/不匹配拒派；必填机检 held_incomplete |
| C5 | 成熟度门闸 | scheduling/maturity.py | M1-M4 可配置读 policy；新鲜度衰减；区域聚合 SQL 正确；held_maturity 自动转正留痕 |
| C6 | 分流器 | scheduling/router.py | R1-R3 三证据机检；骨架级必置 owner_gate=true；自指命中必 Owner 有测试 |
| C7 | 排产调度器 | scheduling/dispatcher.py | 两问打分+防饥饿+四读数+check_gate 拉式调用+老组 claim 预检；exit 3 回队不轮询；降级梯度全留痕 |
| C8 | 排班登记接口 | scheduling/seed_writer.py + 生成器新源 I7（消费 `config/evolution_schedule_seeds.yaml`） | 种子字段全过词表校验（幽灵池/空间维双禁令）；--check 再生自动吸入；GENERATED 注册表零手改 |
| C9 | 前端件 | `src/zephyr/frontend/dashboard/web/features/schedulegate/`（队列可视+骨架级一键确认页，promotion.js 惯例） | 确认按钮=唯一写路由（POST confirm）；其余只读；改判留痕 |
| C10 | 测试+登记套件 | `tests/ai_layer/scheduling/`（test_maturity/test_router/test_dispatcher/test_events/test_seed_writer）+add_module_translation/depgraph/capability card | 全绿；零生产路径写入（tmp_path）；登记器零报错；C8 跨 scripts 域施工走 --allow-multi-domain 留痕或独立单派 |

依赖序：C1→C2→C3→(C4/C5/C6 并行)→C7→(C8/C9/C10 并行)。全部走 worktree 隔离+网关提交+
改前 claim；新 .py 走 CREATE-GUARD+TRANSLATION-COVERAGE+RULE-DEPGRAPH。

---

## 5. 挖矿日志表+自审闸三态裁定

### 5.1 挖矿日志

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| IN-R1 | L4 设计稿胜者契约 | signal | evidence_pack 五元+win* 降权指令+criteria_hash 机检义务（§2.3①指名 L5 执行）——上游契约现成 |
| IN-R2 | L2 设计稿事件层与 e2_handoff | signal | payload 四字段+events.py 六要素母版+task_completed 唤醒先例——事件层零发明 |
| IN-R3 | L6 设计稿关单契约 | signal | L5→L6 载荷六字段已锁（work_order_shadow_ready=影子上岗券）——本稿只消费不改造 |
| IN-R4 | E0 compute_window_gate.py | signal | 拉式闸门四理由码+四值词表+fail-closed+exit 0/3/1——工单段闸直接调用零改造 |
| IN-R5 | resource_profile_registry+生成器 | signal | 18 字段/合并保全再生/E0_CLASS_TO_RESOURCE/TRADING_SENSITIVE_CLASSES/幽灵池禁令/种子源 I3+manual_lane_c_agentic_miner 先例——登记面全走既有件 |
| IN-R6 | belt_daemon+堵点本实档 | signal | watchdog 事件四件套（目录事件→防抖→单例锁→排空）+dead_letter schema+阈值 20 条/24h+ENV_ABORT_ESCALATE=3——守护与堵点协议照抄 |
| IN-R7 | 主文档附录 A/§3.4/§3.5/risk_tier_registry | signal | 任务书十三字段全可映射；配额四资源口径；维护班专人专事协议 |
| EX-R1 | MLOps CT 触发器分类 | signal | MLflow CT 指南（schedule vs trigger）/Snowflake CT（drift 触发+challenger 逐版治理）/enhancedmlops（事件驱动再训练）；首轮 429 风暴 90s 退避后第二轮成功（纪律内，无编引文）。schedule-based 排程被"事件触发禁定时器"否定不收 |
| REUSE | V1-R2 MLOps Level 2+BIZ-R2 排班归属+MAPE-K Plan 环 | signal（在档复用） | CT 触发器=Level 2 扩对象同源；一张真源裁定直接继承；Plan 环=L5 业界坐标（V2 在档） |

### 5.2 自审闸三态裁定

**裁定=施工**（本设计稿定稿+README 状态翻转）。理由：①骨架卡五项待挖清单全部落成可施工
设计，且零新真源——五样核心件四样是既有函数/台账的直接调用（E0 问闸/生成器种子/堵点本/
promotion 页），一样是常量文件（policy）；②过度工程检查：否决三样诱惑——自建排班表
（违反 §1.6 一张真源裁定）、常驻轮询派工循环（禁定时器铁律→双事件源唤醒）、自造算力档
第五值（E0 词表锁死）；③无套娃：policy 常量归 OBJ_R 流水线，L5 自身升级同走，配额上限
=Owner 定（§五）；④两问自答——好在哪=把"谁先施工"从人盯人排变成 成熟度阈值+两问打分+
配额降级的可机检门闸协议（现状：胜者无协议靠人盯）；消灭哪段人工=人工盯门闸时机/人工排
优先级/人工登记排班（种子自动写+生成器自动再生）。反省：M1-M4、优势分桶、降级线全是
**设计定值非实测标定**，全部收进 policy 常量层；首轮运行数据（held_maturity 占比/误开闸
率/降级触发分布）回来后按 OBJ_R 流水线提案修订，不在本轮拍死。

### 5.3 待 Owner（4 项）

1. **policy 常量初值点头**：M1-M4 阈值/优势分桶线/降级线/配额上限（配额是 Owner 定的，
   §五既有定调）——config/schedule_gate_policy.yaml 常数表。
2. **首批区域白名单点头**：冷启动 M4 的区域清单登记进 policy 文件 Owner 区（区域自治运行
   满一季后可按 OBJ_R 流水线提案退役白名单）。
3. **任务书 schema v0 增补 provenance 字段确认**：建议增 `provenance: {experiment_id,
   card_id, source_event}`（附录 A 版本化变更）；不增补则退化为 objective 内嵌引用，设计两可。
4. **creation_token 补登**：本班硬边界"禁登记 token"，DESIGN.md 的 creation_token 由主
   会话/Owner 补登（L4 稿同款先例）。

---

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-17 | design_v1 | 初稿：六向台账（8 signal/1 首轮 429 后成功）+两级门闸（T0 成熟度 M1-M4/T1 资源四读数）+工单分段算力归类+种子文件登记接口+三证据分流器+两问打分法+五契约接线+10 施工项+4 待 Owner |

---

## 红蓝 R1 修复记录（2026-09-17，修复组 2）

- **B9（工单库表落"ai_intake 同实例"未指 schema，违 L2 §2.1 产线禁读界）**：工单库表改落 PG 同实例**独立 schema `ai_scheduling`**（表=`ai_scheduling.ai_work_order`），两处同步（§1 台账④行、C2 施工项），均加"与 L2 ai_intake schema 隔离，产线禁读界不破"；仍同 PG 实例、全经 DatabaseService、禁裸连接。
- **B10 附带一（defer 有事件无态、dead 无进入判据）**：新增 §2.7 工单状态机——**deferred 补态**（进入=配额不足 Q1-Q4 超限/算力窗关闭 E0 exit 3；退出=资源恢复事件重评回 pending，连续 3 次 defer 仍走堵点本 CRITICAL），**dead 补进入判据**（连续 N 次派工失败，或任务书机检连续三次不过；N 初值 3，标注"进 OBJ_R 阈值盘点"）；C2 CHECK 枚举补 deferred；§2.3/§2.6 的 defer 措辞与 §2.7 对齐（exit 3/Q1 满/Q3 超一律转 deferred）。
- **B10 附带二（目录 watchdog 与 events journal 双通道过度工程）**：裁定合并——**events journal=唯一真源**，watchdog 降级为 journal 的补偿读指针（last_read_offset 断点续读，不再独立扫描 winners/ 目录；belt_daemon 防抖/单例锁机械照用、作用对象改为 journal 文件）。裁定理由一行：双通道=双真源，必然产生消费竞态与重复生成工单，events.py 母版已足够承载；§2.1 与 C4 同步改写。
- **第 7 项（跨稿边界声明，L4+L5 同款）**：稿首新增"考场边界声明"——策略候选的考场止于 L4 证据包产出；转正/流转归业务层 S12-S14 与 Owner 拍板，AI 层不设第二转正门；交易算法专域不在 AI 层自动流转范围。
- 连带核查：order_deferred_due 事件 kind（C3）与 deferred 态同名对齐零冲突；L6 关单契约载荷零变更；堵点本/配额降级梯度表语义不变，仅挂起态名归一。

## 红蓝 R2 修复记录（2026-09-17，红队 R2 发现）

- **R2（dead 终态无回传）**：§2.7 dead 行补回执事件 `work_order_dead`（payload={order_id, reason}）→L2 候选卡跳 rejected——L2 稿同批补 rejected 入边，dead 不再是无回传黑洞。连带核记：§1 台账①与 §3 库内路 `INTAKE_E2_HANDOFF` 的 evidence_ref 增补已经 L2 稿 R2 同批落地。

**红蓝 R3 修复记录**：C3 事件补全 3 项（shadow_ready/closed_due/dead）。
**红蓝 R4 修复记录**：C3 计数校正为 8 kind（R3 时误记 7）；§①/L198/L234 两事件分工澄清（shadow_ready→L6 与 closed_due→L7 勿混称）。
