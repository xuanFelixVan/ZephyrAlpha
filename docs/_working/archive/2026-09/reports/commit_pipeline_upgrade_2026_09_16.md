---
ttl: task_bound
session: st-commitspeed-20260916
date: 2026-09-16
completes_when: >-
  本文件 §5 方案表的 P0 两项与 P1 四项均获得 Owner 拍板（施工/挂起/驳回三态之一）；
  §3 挖矿日志与 §4 数据证据无待补盲区（成功提交观测盲区 GAP-1 已裁定是否补采）。
  机械验证 = 本文件条目逐条标注处置结论后，由工作文档清理批 reconciler 按
  GATE-WORKING-DOCS 语义判定结案归档。
---

# 提交通道升级方案 v2——多 AI 并发时代的提交吞吐（2026-09-16 立项）

> 创建：2026-09-16 ｜ 会话：st-commitspeed-20260916 ｜ 状态：**v2.1（含 R2 彻底根治增补 §8）待拍板；R2 当场已修 echo_guard 回退**
> Owner 原始指令：提交太慢（点一次等非常久），十多个 AI 并发排队排太久；全面检查→临时文档→挖矿 SOP→升级方案。
> 前案：[2026-09-10-commit-pipeline-perf-plan.md](2026-09-10-commit-pipeline-perf-plan.md)（v1，P0/P1 全落地+P2 三 flag 已转正）。本文件=v2，只写增量，不重复 v1 已治项。

---

## 0. 结论速览

**一句话诊断：单次提交的代码路径没有变慢，变慢的是"失败税 + 并发挤兑"。** 2026-09-12 治本后单提交干净场景 22-49s 的结论在今天依然成立（实测见 §6），但当下 10+ AI 会话并发时：

1. **失败税（最大头）**：近 48h **527 次提交被门禁拦截**，每次平均白烧 79 秒门禁链才撞墙（P90=189s，最差 988s），然后 AI 改旗重跑全链，再失败再跑。这些失败绝大多数是**确定性违规**（没 claim/没登记/跨域/缺 TTL 头），本可以在拿锁前 3 秒内廉价发现。
2. **队列挤兑**：24h 队列落地延迟 **P50=38s / P90=230s / 最差 681s**。队列是严格 FIFO 单写者，每项落地都要在专用 worktree 过**全量门禁链**（"门禁一套不裁"），吞吐上限≈每项一个门禁链时长；机器伴生提交（reconciler 收编等，占 20%）与 AI 交互提交同队无优先级。
3. **门禁面膨胀**：gate 总数 9/11 的 106 → **166（+56%）**，own-scope 只有 22 个，缓存/预跑白名单各只有 10 个。§2.6 分级清单里 ~30 个 own-scope 候选至今只做了 2 个。

**方案表（详见 §5）**：P0=失败预检前移（锁外试跑+入队预校验+一过式失败清单）+ 基建故障治本（CREATE-GUARD ParserError 31 次误烧、perf 报带判绿矛盾）；P1=own-scope 第三批 + 缓存/预跑白名单扩面 + 竞争感知入队（不再空烧 60s 锁等待）+ 机器伴生车道隔离；P2=门禁并行车道（挂起排期）+ reconcile worker 降优先级 + 死信自动收敛。全落地预期：失败税释放 ~4h/日锁内算力、AI 单提交 P90 从 ~230s 压到 <60s。

**R2 增补（§8，Owner"彻底根治"指令后第二轮挖矿）**：新根因 5 个——echo_guard 经"配置误删+危险默认值"复活（**当场已修**，省 30s/提交）、65% 死信=测试污染生产队列、落地侧门禁视野污染、重试环最长 30 连败、退役审计无燃料；全链实测 213.7s 中 TOP10 门禁占 82%（靶子高度集中）；彻底根治三范式 T1 阻断核+异步批判/T2 批量落地/T3 持续预验证（挂起排期，解锁条件写明）。

---

## 1. 现状全面扫描（数据证据，2026-09-16 00:41-01:00 实测）

### 1.1 提交链路架构现状

- **双通道**：直连 `scripts/git_commit.py` → `GitCommitGateway.commit()`（[gate→stage→commit] 整体在 `_GlobalCommitLock` 临界区，TRAE-079 铁律1）；队列 `commit_queue.py`（快照入袋即安全 → serializer 单写者 lease(TTL=300s) → 专用 worktree 落地，**GitCommitGateway 全门禁零适配**，CAS 推进 dev）。LOCK_TIMEOUT 自动改道入队（P2⑨b）已 production。
- **三个性能 flag 全部 production**（config/flags.yaml）：gate_preflight（锁外预跑+指纹采信）、gate_result_cache（TTL 10min，现 4519 条缓存条目在用）、commit_queue_interactive。
- **门禁链**：`commit_gate_registry.check_all` 按 priority 升序串行执行，166 gate；worktree 内提交跳过搭便车三 gate（`_WORKTREE_SKIP_GATES`）。
- **队列驱动模型**：无常驻进程，入队自举排空（`bootstrap_drain_with_landing`，拿不到 lease 放弃等下次自举）。

### 1.2 真实负载遥测（.runtime/audit/commit_block_events.jsonl + 队列 done 台账）

| 指标 | 数值 | 口径 |
|------|------|------|
| commit_blocked（门禁拦截） | **527 次/48h**，gate 链 P50=79s、P90=189s、max=988s | 每次拦截=一次白烧后失败 |
| commit_slow（成功但 >60s） | 81 次/48h，全程墙钟 P50=130s、max=798s | 阈值化仅记慢的 |
| 队列落地延迟 | **n=168/24h，P50=38s、P90=230s、max=681s、mean=84s** | done 项 created→landed |
| 队列存量 | pending 0 / processing 1 / done 724 / **dead 1166** | dead 主力=auto-derived-sync 489（再生产物） |
| 提交总流量 | 330 单/24h（正式 264=80%，机器伴生 66=20%） | commit_perf_report.py |
| 并发现场 | 17 个 python 进程同跑（3 个 git_commit + 2 个 reconcile_worker 各 5-7 分钟），20 核负载 53% | 2026-09-16 00:49 进程表 |
| 单文件提交最差实录 | **1 文件 799 秒**（st-circmv-synthcw，09-15 16:17） | commit_slow 台账 |

**TOP 拦截门（48h 频次 × 撞墙前白烧）**：CLAIM-REQUIRED 36、CREATE-GUARD 31（含 ParserError 设施故障，见 §4-G2）、WORKTREE-REQUIRED 28、TTL-METADATA 27、COMMIT-SCOPE 25、DEPGRAPH-PRE-REGISTRATION 23、TABLE-NAME-REGISTRY 22、PERM-TRIGGER 21、NO-LONG-PARAM-LIST 20、GATE-ERRCODE-CONSISTENCY 19（单此一项 24h 累计白烧 3586s）。

### 1.3 回答 Owner 直问："是不是每个门禁全扫一遍？能不能只扫提交的文件？"

- **现状确是 166 道全跑**（按 priority 串行），但分三类（v1 方案 §2.6 分级真源）：
  - **内容扫描型**（正则/AST/编码，违规=逐文件局部属性）：**可以也应该只扫本次提交的文件**。现状只有 22 个 own-scope 化，其余扫的是**整个暂存区**——10+ 会话并发时暂存区混着所有人 WIP，等于**互相替对方付门禁费**。这是"只扫自己文件"的直接答案：§2.6 候选池 ~30 个，做完即与并发会话数解耦。
  - **信号型**（锁/claim/会话态势）：无文件面，本来就不是文件扫描，开销极小（<0.1s 级），不用优化。
  - **结构校验型**（地图对齐/引用存在性）：输入是全局注册表，**不能只看自己的文件**（断链可能由任何文件引起），但其代价是"读注册表"（便宜），真正的浪费是它们对全暂存区做触发判定——方向是触发条件收窄（DECISION-MAP 触发式先例）。
- **另一个 Owner 没问但更重要的**：比"扫多少文件"更大的税是**失败后全链重跑**。每道门禁都白跑到位才发现撞墙。v1 的 preflight 只覆盖 10 道内容门禁；确定性违规（没 claim/跨域/缺头）完全可以在拿锁前 3 秒判定（§5 P0-A）。

### 1.4 为什么比 9/12 的 22-49s 体感差

代码路径没退化（flags 全 production、ENCODING 批量化在位）。恶化三因子：①并发从 3-4 会话涨到 10+，CPU 争用把每道 gate 放大 2-5 倍（17 进程实测）；②暂存区共享下 own-scope 未推广的门禁随 staged 总量线性放大；③gate 总数 +56%（每道新 gate 都有对应事故是正当的，但没有净退役机制对冲，§4 宪法规范预算条款在提交链路上未执行）。

---

## 2. 挖矿日志（挖矿 SOP v1.4 六向寻路，母节点=提交吞吐）

| 向 | 矿脉 | 动作与发现 | 判定 |
|----|------|-----------|------|
| ①上游 | 谁在喂提交、喂进来什么质量 | 遥测反查：48h 527 拦截的构成=工作流类违规为主（claim/登记/跨域/缺头），即**上游可预防**；旗梯重跑（FOREIGN_CHANGE→adopt→non-worktree→…）每级重烧全链 | **signal** |
| ②下游 | 提交落地后喂给谁 | reconciler 收编/integrity 后注册/派生缓存 3 类机器伴生 66 单/24h 与 AI 单同队 FIFO；commit_perf_report 判定公式失真（211 竞态 vs 阈值 4 仍判"绿"——文档矛盾=事故，宪法 §4.3） | **signal×2** |
| ③机制 | 业界怎么做快提交/快门禁 | 全网搜索（来源见 §5.4）：fast hooks（秒级、只查变更文件，重量级检查后置到 merge queue）+ merge queue（Mergify：队列=调度问题不只是安全问题）+ affected-target（Aviator：大仓队列性能标准解=只跑受影响目标）+ lint-staged/--cache 模式 | **signal** |
| ④后端 | 代码侧缺口 | priority 基建已在（排序零成本）；缓存/预跑白名单各 10 gate 过窄；死信无自动收敛（同键 compaction 只作用于 pending）；CREATE-GUARD 对 registry 解析失败 fail-closed（31 次/48h 误烧，手动复验当前文件 parse OK=瞬态撕裂读）；成功提交 <60s 不留痕=观测盲区 | **signal×5** |
| ⑤前端 | 怎么呈现（只登记不施工） | 队列深度/等待分位/拦截 TOP 无仪表盘呈现（数据已全在 jsonl，缺渲染页） | 登记 |
| ⑥数据 | 计时字段完备度 | commit_block_events 只有失败/慢事件；成功提交的 gate_chain_ms 无全量样本（GAP-1，见 §5 复测与 GAP） | **signal（GAP）** |

noise 轮：无（六向全部有产出）。矿脉长尾（本域明确不挖/归属他线）：echo_guard/redup 查重引擎线（9/12 已终审收口）、gate 合并/删除线（9/11 已裁"无收益/不建议"）、worktree 全量化线（平行协调政策管辖）。

---

## 3. 升级方案 v2

### 3.1 P0-A 失败预检前移（锁外确定性试跑 + 入队预校验 + 一过式失败清单）★最大杠杆

- **改动**：把"只依赖 (文件清单∪快照内容, 会话态, 注册表)"的确定性 gate 子集（TTL-METADATA / CLAIM-REQUIRED / WORKTREE-REQUIRED / COMMIT-SCOPE / CREATE-GUARD / ALGO-NOTE-SYNC / PERM-TRIGGER / FOLDER-CAPACITY / DEPGRAPH-PRE-REGISTRATION / TABLE-NAME-REGISTRY / MANUAL-ONLY-PERMANENT / RENAME-DEPGRAPH-SYNC / SESSION-REQUIRED / PROTECTED-PATHS，约 14 道）在 git_commit.py **拿锁前**对 --files 清单试跑：**不短路、收集全部失败+逐项推荐逃生旗，一次性返回**。队列通道在 enqueue 快照时同步预校验（快照自带 blob 内容），注定死信的单子在入队那一刻就死，不消耗落地算力。
- **收益实算**：48h 527 次拦截 × P50 79s ≈ 11.6h/48h 锁内白烧；确定性子集覆盖其中 ~80%（工作流+登记类），改后单次失败成本 79s→3-5s（锁外），**释放 ~4.3h/日锁内算力**，锁让出来队列整体提速；AI 会话的"失败→改旗→重跑"从 N 轮压成 1 轮（全失败清单一次给全）。
- **等价性红线**：零门禁语义改动——同一套 gate 函数、锁内照跑全套（预检是提前失败不是豁免）；准入逐 gate 审计输入面可接受 (path, content) 对（施工时机械活，先例=own-scope 推广批次）。基建故障（如 registry 解析炸）在预检层降级 warn 不拦（fail-open 于故障、fail-closed 于违规）。
- **工作量**：中（1 个会话夜班）。gate_preflight（P2⑦）同构基建已在，扩展白名单分类即可。

### 3.2 P0-B 基建故障治本（两件）

1. **CREATE-GUARD ParserError**：48h 31 次拦截详查=`capability registry 解析失败(ParserError)`——fail-closed 把**设施故障当违规拦**。治本：a) 排查撕裂读源（并发写窗口；写侧 safe_write CAS 已有，补读侧重试+解析失败告警落 audit）；b) 分级：解析类设施故障→warn+审计不阻断，真违规照拦。
2. **commit_perf_report.py 判定公式**：竞态窗口 211 事件 vs 判绿阈值 ≤4/日仍输出"总体判定: 绿"——矛盾即事故（宪法 §4.3），修判定逻辑并挂晨审。
3. **GATE-PANORAMA-ALIGNMENT reconciler 检测器失效**：自 09-14 17:57 起 UnicodeDecodeError（GBK 字节 0xd6 炸 utf-8 解码）瘫痪两天，critical_warn 横幅每笔提交挂名但检测为零——修解码容错+恢复检测。

### 3.3 P1-A own-scope 第三批推广（~30 候选池现成）

- 靶子按 48h 白烧榜排序：TABLE-NAME-REGISTRY、NO-LONG-PARAM-LIST、GATE-ERRCODE-CONSISTENCY、NO-HIGH-COMPLEXITY、ALGO-NOTE-SYNC、REGISTRY-MASS-DELETION 等（v1 §2.6 ☆ 清单为准，逐 gate 语义等价准入）；**MANUAL-ONLY-PERMANENT 加急**——本会话实弹被其外来 .py 路障拦死（§6），与 DATETIME-NOW 同款"扫全暂存区无 own 过滤"病灶。
- 收益：门禁耗时与并发会话数解耦（终结"替他人 WIP 付门禁费"）；CAPABILITY-OVERLAP 同款先例实测 32s→2.7s。

### 3.4 P1-B 缓存/预跑白名单扩面（10 → 内容扫描类全量）

- gate_result_cache 与 gate_preflight 共享白名单现各 10 gate；§2.6 分级总表已把内容扫描型分类完毕，逐 gate 输入面分析后批量准入（缓存 key 已含 own_scope+树指纹+HEAD，投毒攻击红蓝#2 已验防住）。机械活，随 P1-A 同批施工。

### 3.5 P1-C 竞争感知入队（不再空烧 60s）

- 现状：锁忙时直连路径空等 --wait（默认 60s）才 LOCK_TIMEOUT 自动入队；17 进程并发时=每单先白等几十秒。
- 改良：提交入口先毫秒级探测锁态+队列深度——锁忙且队列非空→**立即入队**（跳过空等）；锁空闲→直连。`--no-auto-enqueue` 显式退出保留。

### 3.6 P1-D 机器伴生车道隔离

- 24h 机器伴生 66 单（reconciler 收编 33+integrity 25+派生 8）与 AI 交互单同队 FIFO。改：队列项带 lane 标记（interactive/machine），serializer 优先落 interactive，machine 单空闲时落地（或聚夜间窗）。AI 单 P50=38s 直接受益；机器伴生延迟不敏感零损失。

### 3.7 P2 梯队

| 项 | 内容 | 状态 |
|----|------|------|
| P2-A 门禁并行车道 | 独立 gate 按输入面分组进进程池并行（20 核现况利用率低），组间保 priority 序、组内并行；预期锁内链 P90 189s→~50s。风险=own_scope helper 并发安全/DB 连接/first-fail 语义，需红蓝 | **挂起排期**（解锁条件：P0/P1 落地复测后 P90 仍 >100s） |
| P2-B reconcile worker 降载 | 实测单 worker 5-7 分钟×并发多个；Windows BELOW_NORMAL_PRIORITY_CLASS+全局并发 1，把 CPU 让给提交门禁 | 施工（小） |
| P2-C 死信自动收敛 | dead 1166（auto-derived-sync 489 再生产物）；同键 (session,path) 死信在新快照落地后自动过期归档，保留 dead_reason 档案 | 施工（小） |
| GAP-1 成功提交观测 | 成功<60s 零留痕=分位数观测盲区；commit 成功事件采样 10% 落 gate_chain_ms | 施工（小，随 P0-B 报表修复同批） |
| ⑤前端呈现 | 队列深度/等待分位/拦截 TOP 仪表盘页（数据已在 jsonl） | 登记不施工（前端负责人会话职权） |

### 3.8 明确不做（留痕防重复挖）

- 合并/删除门禁：9/11 已裁（合并无收益、删除不建议——每道对应历史事故治本）；本方案全部走"少白跑"不走"少检测"。
- 常驻 drain 守护进程：66 号文已裁"无常驻进程、事件自举"；P1-C/P1-D 在自举模型内解决。
- 绕过 GitCommitGateway 的快速通道：宪法唯一合法 commit 入口，不开口子。

---

## 4. 挖后自审闸（挖矿 SOP §6）

- **北极星校准**：终局=Owner 只做四类事、100% AI 自制。提交通道是 AI 自制的血液循环，其吞吐上限=AI 并发度上限的直接约束；本方案全部指向消灭"AI 空等/失败重试/人工穿行"——**一票放行好矿**，无封矿项。
- **反驳者一问（对最大候选 P0-A）**：①预检与锁内双跑会不会引入不一致？→ 同一 gate 函数同一输入面，锁内全套照跑兜底，预检只是提前报错，不一致最多=白预检不漏检。②确定性子集选错（某 gate 实际依赖 staged 语义）？→ 准入逐 gate 审计+保守回退（拿不准不入子集）。③P0-A 做完失败税消失后 P1 是不是白做？→ P1-A/B 治的是**成功提交**的链时长（own-scope/缓存），与失败税正交。
- **AI 系统性偏差自查**：P2-A 并行车道的现状规模（166 gate 串行 ~80s）不算小、且随 gate 净增继续涨——按终局量尺（gate 只会更多、AI 并发只会更高）该做，但按"世界地图完备优先"排在 P0/P1 落地复测之后，防边挖边建返工。
- **三态出口**：P0-A/P0-B/P1-A~D/P2-B/P2-C/GAP-1=施工；P2-A=挂起排期（解锁条件已写明）；无封矿。

## 5. 预期总账与验收口径

| 指标 | 现状（09-16 实测） | 目标（P0+P1 落地后） | 终局（含 P2-A） |
|------|-------------------|---------------------|----------------|
| 失败单次成本 | P50 79s（锁内） | <5s（锁外预检） | 同左 |
| 48h 失败白烧 | ~11.6h 锁内算力 | <1h | 同左 |
| AI 单提交端到端 | P50 38s / P90 230s | P50 <20s / P90 <60s | P90 <30s |
| 死信存量 | 1166（再生） | 自动收敛到 <100 | 同左 |

验收=commit_block_events 48h 滚窗复测（同口径对比）+ commit_perf_report（修复后判定公式）+ 本会话实测基线（§6）。

## 6. 本会话实测基线（实弹样本）

- 2026-09-16 00:49 现场：3 个 git_commit 并发在飞、2 个 reconcile_worker 各跑 5-7 分钟、17 python 进程——多 AI 并发挤兑实锤。
- **实弹样本（本文件自身落库实录，2026-09-16 01:17-01:19）**：
  - 首次直连尝试**被拦白烧约 2 分钟**（成果为零），连中两枪：①FOLDER-CAPACITY-HARD-LIMIT 拦截 docs/_working 平铺 121>120（确定性违规，本可锁外 3 秒发现——P0-A 活标本）；②MANUAL-ONLY-PERMANENT 拿**他会话暂存的 3 个外来 .py** 拦本次纯 docs 提交（无 own-scope 门禁成全局路障——P1-A 活标本，同 09-12 事故形态再现）。
  - 改走队列正门后：**入队操作 5.4s + 队列等待+落地 53.0s = 端到端 58.4s**，一次通过零外来归属（commit 917ed6bb6c，git log -1 --name-only 核实）。
  - 同窗口另见 live 死信一单（autopipeline-0019，blob 与 old_dev 不符假落地防线触发）+ DEPGRAPH-FRESHNESS WARN（185min 未刷新）——队列健康观察样本。
- **新发现基建故障（补入 P0-B 清单）**：GATE-PANORAMA-ALIGNMENT reconciler 自 09-14 17:57 起 UnicodeDecodeError 检测器失效（读 GBK 字节 0xd6 炸）——critical_warn 横幅每笔提交都在挂，检测却已瘫两天。

## 7. 证据文件清单

- `.runtime/audit/commit_block_events.jsonl`（692 事件，本分析只读）
- `.runtime/commit_queue/{pending,processing,done,dead}/`（队列台账）
- `config/flags.yaml`（三 flag production 现状）
- `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（166 gate/22 own-scope）
- `docs/_working/2026-09-10-commit-pipeline-perf-plan.md`（v1 方案+§2.6 分级总表）
- 项目自报表：`python scripts/governance/commit_perf_report.py`

---

## 8. R2 第二轮挖矿——彻底根治（2026-09-16 01:20-01:45，Owner 指令"矿没挖干继续挖，这次彻底根治"）

> 本轮按挖矿 SOP 矿脉枯竭结构判据深挖 11 条矿脉（V1-V11），全见底；挖出 **5 个新根因（含 1 个当场修复的回退）+ 3 个范式级根治方向**。§3 v2.0 方案表全部保留有效，本节增补项与其合并为 v2.1。

### 8.1 R2 新根因（全部实测坐实）

| # | 根因 | 证据 | 处置 |
|---|------|------|------|
| G6 | **echo_guard 复活回退**：clone_guard.yml 被工作区误删（未提交删除），config.py 缺省 `echo_guard_enabled=True` → 已退役引擎经危险默认值复活，每次带 .py 提交白烧 30s 超时 | R2 harness 实录 `EchoGuardAdapter degraded: 超时(30s)`；CAPABILITY-OVERLAP 32.8s | **当场已修**：git checkout 恢复 HEAD 配置（enabled:false），复测 24.9s（省 8s）；**新增 P0-B4：CONFIG-PRESENCE 检查**——被 loader 引用的配置文件缺失≠危险默认值，裁定禁用项缺配置时按禁用处理 |
| G7 | **测试污染生产队列**：1175 死信中 **760（65%）= pytest 临时仓库的队列项漏进生产 dead 区**（`landing 异常: git rev-parse rc=128: not a git repository: .runtime/tmp/pytest_19944/...`） | 死信 dead_reason 全文解码；09-03 批次+09-11 requeue 再生 | **P0-C 新增**：①purge 这 760 垃圾死信；②治本=测试隔离（queue root 必须参数化到 tmp_path，违者=运维红线 §9.6 测试写生产路径） |
| G8 | **落地侧门禁视野污染**：TTL-METADATA 等门禁在 serializer worktree 里扫到队列自身基建文件（`schemas/categories/__init__.py missing ttl`）——"全门禁零适配"在 worktree 环境的适配缺口 | 27 条 TTL-METADATA 死信 dead_reason 逐条核验 | 并入 P0-B（落地侧 gate 扫描面=快照文件，禁扫 worktree 树） |
| G9 | **重试环灾难性放大**：240 条重试串覆盖 624 次拦截，平均 2.6 连败，**最长 30 连败**（每败烧一轮全链） | commit_block_events 按 session×10min 窗口聚类 | P0-A 的"一过式失败清单"正对此病灶；加码=同一 session 同一批文件的重复失败 3 次后强制走预检报告（禁盲重试） |
| G10 | **退役审计无燃料**：gate 执行无计数器（.runtime/gate_audit/ 只有 own-scope 外来审计），宪法 §4.2"触发率退役审计"无从执行；gate 总量 166 vs in_process 注册表 111，数量漂移无人察觉 | 全仓反查无 execution counter 机制 | **P1-E 新增**：check_all 加每 gate 执行计数（日聚合落 audit），季度退役审计有数据；计数器顺带核实注册表漂移 |
| G11 | **门禁成本高度集中**：R2 全链实测 213.7s，**TOP10 gate 占 ~175s（82%）**（REGISTRY-MASS-DELETION 39.8s / CAPABILITY-OVERLAP 32.8s / GATE-ERRCODE 29.4s / BATTLE-MAP 12.9s…），其余 100+ 道合计 <40s | v4 harness（.runtime/tmp/gate_timing_r4_20260916.json，配方同 9/11 st-encfix，只读） | 印证 §3 全部方案：预检前移/own-scope/缓存/并行的靶子就是这 10 道；**合并/删除门禁依然不做**（成本集中≠可删，每道对应事故治本） |

### 8.2 彻底根治三范式（T 系，v2.1 增补）

> 定位：§3 P0/P1 治"失败税+挤兑"的存量病灶；T 系回答"终局形态提交通道长什么样"。三范式互相正交，T1 是主轴。

**T1 阻断核+异步批判+隔离治愈（范式级，Owner 门）**
- 现状范式=提交时 166 道全拦截；终局范式=**提交时只拦安全核（预算 ≤15 道：密钥/危险 SQL/GW 伪造/会话与声明类），其余 ~150 道转为落地后异步批判**——批判器产出违规发现→自动开修复任务→严重者走 rollback 基建（infrastructure/rollback 已有 14K 行：agent_cooldown 隔离/warm_standby/审计）隔离该会话后续写入+revert 单笔 commit（队列落地项天然单 commit 单 qid，可精确 revert）。
- 收益：提交墙钟从"全链时长"变"安全核时长"（实测外推 <8s）；批判阶段与提交解耦后可全量跑、慢慢跑、跑重活，**检测覆盖反而变大不再受提交预算约束**（9/11 echo_guard 裁定的第一性原理"预算不够的检测=不存在的检测"的终局解）。
- 前置依赖：P0-A 预检（防低级违规进主干）、P1-E 计数器（批判覆盖度可观测）、reconciler 修复闭环（已有 batched_auto_committer 先例）。
- 风险与护栏：违规短暂在主干窗口（批判发现→revert 的 MTTR 口径，预注册 ≤30min）；安全核清单须 Owner 裁定+红蓝；宪法 §5 medium/low 门位不放松（批判器仍是硬门禁，只是时点后移）。
- **状态：挂起排期**——解锁条件=P0/P1 全落地且队列 P90<60s 后复测仍不达标，或 Owner 直接放行终局设计。
- 业界印证：**受阻**（Tricorder/Sapling land-flow 检索两轮超时，按 SOP 记受阻不算查无；架构依据以仓内 rollback 基建+reconciler 闭环为准）。

**T2 批量落地（队列吞吐 ×N）**
- 现状 serializer 每项跑一遍全门禁；改=出队时把**同 base_head 连续项合成一个验证批**（合并 diff 跑一次批判集+逐项快验差异），按序逐项 commit。GitHub merge_group/Mergify batches 同构（引文见附）。
- 收益：并发 10+ 会话时门禁成本从 O(N) → O(N/批大小)；配合 P1-D 车道，队列 P90 预估再减半。
- 风险：批内单项违规需整批重验（bisect 拆批，GitHub 同款问题，社区讨论 #58523 在案）；归因复杂度上升。**挂起排期**——解锁=T1 安全核落地后（批判集变小，批处理收益/复杂度比反转）。

**T3 事件驱动持续预验证（把门禁搬到提交之前）**
- write_audit_daemon 已有 watchdog RDCW 事件层监视热目录——**文件写入事件即触发对应内容门禁预跑**，结果落 gate_cache（指纹=内容 sha）；提交时全部命中缓存，锁内链≈纯信号核。事件触发，合永久系统四要素，无常驻轮询。
- 收益：提交时刻的门禁成本前移到"会话干活的同时"（CPU 峰谷错位）；与 gate_preflight/P1-B 同一架构的自然延伸，终局形态="提交时零现算"。
- 风险：写风暴下的预跑积压（需合并去抖：同文件 10s 窗口）；缓存失效语义已有成熟真源。**挂起排期**——解锁=P0-A 预检落地后顺路施工（同一批 gate 准入审计）。

### 8.3 v2.1 方案总表（§3 + 本节合并视图）

| 优先级 | 项 | 状态 |
|--------|-----|------|
| P0-A | 确定性预检前移+一过式失败清单+入队预校验（+G9 加码：3 败强制预检） | **施工** |
| P0-B | 基建故障四件：CREATE-GUARD ParserError / 报表判定公式 / PANORAMA 失效 / G6 配置缺失危险默认（+G8 落地侧视野污染） | **施工**（G6 已当场修复） |
| P0-C | 测试污染队列治本：purge 760+测试隔离参数化（G7） | **施工** |
| P1-A~D | own-scope 三批 / 白名单扩面 / 竞争感知入队 / 机器伴生车道 | **施工**（同 v2.0） |
| P1-E | 门禁执行计数器（退役燃料+注册表漂移哨兵，G10） | **施工** |
| T1/T2/T3 | 阻断核+异步批判 / 批量落地 / 持续预验证 | **挂起排期**（解锁条件各自写明） |

### 8.4 R2 挖矿日志（SOP §7 强制）

| 轮 | 矿脉 | 关键产出 | 判定 |
|----|------|---------|------|
| R2-1 | V1 落地耗时分解 | landing=预暂存+全门禁(仅跳4道)+异步reconcile；无阶段计时→记 GAP-2（落地分相计时） | signal |
| R2-2 | V2 退役审计数据 | 门禁执行零计数器=宪法 §4.2 无从执行；GAP | signal→P1-E |
| R2-3 | V3 计时证据重建 | 9/11 计时 json 已被 tmp 清扫删；重建 v4 harness 实测全链 213.7s/TOP10=82%；证据落 .runtime/tmp/gate_timing_r4_20260916.json | signal |
| R2-4 | V4 rollback 基建 | infrastructure/rollback 14K 行（隔离/热备/审计）=T1 地基；Tricorder 外部印证**受阻**（搜索超时×2，如实记档非查无） | signal+受阻 |
| R2-5 | V5 队列批量落地业界 | GitHub merge_group 机制+Mergify batches+社区"跑两遍"陷阱（#58523/#43988） | signal |
| R2-6 | V6 事件驱动预验证 | write_audit_daemon watchdog 事件层=T3 挂钩点，事件触发合规 | signal |
| R2-7 | V7 注册表机制 | in_process_gate_registry.yaml 111 项 YAML 驱动；总量 166 vs 111 漂移；净零退役未执行 | signal→P1-E |
| R2-8 | V8 重试环 | 240 串/平均 2.6 连败/最长 30 连败 | signal→P0-A 加码 |
| R2-9 | V10 死因全分类 | 65%=测试污染；~9%=落地 gate 误扫（G8）；真内容违规死信占比小 | signal→P0-C |
| R2-10 | V11 worktree 跳过集 | 仅 4 道；落地链≈全链 | signal |
| R2-11 | 意外矿：echo_guard 回退 | 误删配置+危险默认值；当场修复+复测验证 | **signal（已修）** |

noise 轮：无。矿脉枯竭自判：V1-V11 全部见底（各向产出 signal 或记 GAP/受阻归因），本域再无未挖长尾——**挖矿终止判据达成**。

### 8.5 R2 挖后自审闸增补

- **反驳者三问（对 T1 大候选）**：①"异步批判=把违规放进主干"违反检测语义？→ 安全核（密钥/危险 SQL/GW 伪造）仍硬拦在提交时，放行的是格式/一致性类，且 MTTR 预注册+可精确 revert——检测时点后移≠检测消失。②批判器挂了怎么办？→ 批判器健康进 RECONCILER-HEALTH 同款探针；批判停摆=退化为现状范式（提交时全拦），fail-safe 方向正确。③为什么不等 P0/P1 效果？→ 正因如此 T1 挂起排期而非施工；挂起是时序裁定非价值否定。
- 现状规模偏差自查：G7 的 760 死信"只是历史垃圾"——按终局量尺，测试隔离是 100% AI 自制的地基红线，施工。
- 三态出口：P0-B4/P0-C/P1-E=施工；T1/T2/T3=挂起排期；无封矿；G6 已当场修复（既成事实交底）。

---

## 附：挖矿 ③向外部引文（来源可溯闸，URL+发布方）

- Mergify：GitHub Merge Queue Was Step One——队列是调度问题（mergify.com/blog/github-merge-queue-was-step-one-real-ci-orchestration-comes-next，2024）
- Aviator：Merge Queues for Large Monorepos——affected targets 是队列性能标准解（aviator.co/blog/merge-queues-for-large-monorepos/）
- thoughtspile：How we made our pre-commit check 7x faster——缓存+只查变更文件+hooks 秒级预算（thoughtspile.github.io/2021/06/14/faster-pre-commit/）
- pre-commit.com 官方：hooks 默认只跑变更文件（pre-commit.com）
- GitLab 官方 monorepo 性能指南：path filters/浅克隆/并发控制（docs.gitlab.com/user/project/repository/monorepos/）
- dev.to：Monorepo CI 时间减半实录——lint 缓存+测试并行（dev.to/jimmyyeung/journey-of-systematically-cut-our-monorepo-ci-time-in-half-ec8）

### R2 增补引文（T2 批量落地范式）

- GitHub Docs：Managing a merge queue——merge_group 临时分支批量验证（docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue）
- Mergify Docs：Merge Queue Batches——多 PR 合一次 CI 验证（docs.mergify.com/merge-queue/batches/）
- GitHub Community #58523/#43988——批量验证"CI 跑两遍"与拆批陷阱（github.com/orgs/community/discussions/58523）
