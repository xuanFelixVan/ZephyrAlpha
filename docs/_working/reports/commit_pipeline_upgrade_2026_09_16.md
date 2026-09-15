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

> 创建：2026-09-16 ｜ 会话：st-commitspeed-20260916 ｜ 状态：**方案成稿待拍板**
> Owner 原始指令：提交太慢（点一次等非常久），十多个 AI 并发排队排太久；全面检查→临时文档→挖矿 SOP→升级方案。
> 前案：[2026-09-10-commit-pipeline-perf-plan.md](2026-09-10-commit-pipeline-perf-plan.md)（v1，P0/P1 全落地+P2 三 flag 已转正）。本文件=v2，只写增量，不重复 v1 已治项。

---

## 0. 结论速览

**一句话诊断：单次提交的代码路径没有变慢，变慢的是"失败税 + 并发挤兑"。** 2026-09-12 治本后单提交干净场景 22-49s 的结论在今天依然成立（实测见 §6），但当下 10+ AI 会话并发时：

1. **失败税（最大头）**：近 48h **527 次提交被门禁拦截**，每次平均白烧 79 秒门禁链才撞墙（P90=189s，最差 988s），然后 AI 改旗重跑全链，再失败再跑。这些失败绝大多数是**确定性违规**（没 claim/没登记/跨域/缺 TTL 头），本可以在拿锁前 3 秒内廉价发现。
2. **队列挤兑**：24h 队列落地延迟 **P50=38s / P90=230s / 最差 681s**。队列是严格 FIFO 单写者，每项落地都要在专用 worktree 过**全量门禁链**（"门禁一套不裁"），吞吐上限≈每项一个门禁链时长；机器伴生提交（reconciler 收编等，占 20%）与 AI 交互提交同队无优先级。
3. **门禁面膨胀**：gate 总数 9/11 的 106 → **166（+56%）**，own-scope 只有 22 个，缓存/预跑白名单各只有 10 个。§2.6 分级清单里 ~30 个 own-scope 候选至今只做了 2 个。

**方案表（详见 §5）**：P0=失败预检前移（锁外试跑+入队预校验+一过式失败清单）+ 基建故障治本（CREATE-GUARD ParserError 31 次误烧、perf 报带判绿矛盾）；P1=own-scope 第三批 + 缓存/预跑白名单扩面 + 竞争感知入队（不再空烧 60s 锁等待）+ 机器伴生车道隔离；P2=门禁并行车道（挂起排期）+ reconcile worker 降优先级 + 死信自动收敛。全落地预期：失败税释放 ~4h/日锁内算力、AI 单提交 P90 从 ~230s 压到 <60s。

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

### 3.3 P1-A own-scope 第三批推广（~30 候选池现成）

- 靶子按 48h 白烧榜排序：TABLE-NAME-REGISTRY、NO-LONG-PARAM-LIST、GATE-ERRCODE-CONSISTENCY、NO-HIGH-COMPLEXITY、ALGO-NOTE-SYNC、REGISTRY-MASS-DELETION 等（v1 §2.6 ☆ 清单为准，逐 gate 语义等价准入）。
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
- 本文件的落库提交本身=一次实测样本（实测数据见下方追记，首次提交后由审计日志回填；对照 9/12 干净场景 22-49s 与本文件 §1.2 并发场景数据）。

## 7. 证据文件清单

- `.runtime/audit/commit_block_events.jsonl`（692 事件，本分析只读）
- `.runtime/commit_queue/{pending,processing,done,dead}/`（队列台账）
- `config/flags.yaml`（三 flag production 现状）
- `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（166 gate/22 own-scope）
- `docs/_working/2026-09-10-commit-pipeline-perf-plan.md`（v1 方案+§2.6 分级总表）
- 项目自报表：`python scripts/governance/commit_perf_report.py`

---

## 附：挖矿 ③向外部引文（来源可溯闸，URL+发布方）

- Mergify：GitHub Merge Queue Was Step One——队列是调度问题（mergify.com/blog/github-merge-queue-was-step-one-real-ci-orchestration-comes-next，2024）
- Aviator：Merge Queues for Large Monorepos——affected targets 是队列性能标准解（aviator.co/blog/merge-queues-for-large-monorepos/）
- thoughtspile：How we made our pre-commit check 7x faster——缓存+只查变更文件+hooks 秒级预算（thoughtspile.github.io/2021/06/14/faster-pre-commit/）
- pre-commit.com 官方：hooks 默认只跑变更文件（pre-commit.com）
- GitLab 官方 monorepo 性能指南：path filters/浅克隆/并发控制（docs.gitlab.com/user/project/repository/monorepos/）
- dev.to：Monorepo CI 时间减半实录——lint 缓存+测试并行（dev.to/jimmyyeung/journey-of-systematically-cut-our-monorepo-ci-time-in-half-ec8）
