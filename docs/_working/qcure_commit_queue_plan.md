---
ttl: task_bound
title: QCure — 提交队列死信治本临时施工方案 v0.1
session: st-qcure-20260925
---

# QCure — 提交队列死信治本 临时施工方案 v0.1

> 会话: st-qcure-20260925 ｜ 日期: 2026-09-25 ｜ 状态: 待批
> 性质: 公共基建治本立项（临时方案，正式施工前按 construction_workflow_policy 补登记）
> 矿藏来源: 三路并行调查（门禁证据源 / 队列机械全谱 / 395 笔死信证据学）+ 承重代码精读

## 0. 一句话问题定义

提交队列的落地侧判官（门禁链）读的**证据状态/语言**，与会话侧证据所在的**状态/语言**不同源，
导致合法包"死在队里"，属主用人肉搬运证据（补 token、补裁定翻译、补 frontmatter、补调用量）
后重投——同一类死亡反复复发且在恶化。治本 = 把人肉搬运变成机械。

## 1. 矿藏总结（调查实证）

### 1.1 数据基线（2026-09-25 00:30-01:30 实测）

- 死信总量 **395**（全部 JSON 可解析）：09-23=116，09-24=**275（70%）**，两个夜间波峰
  （A: 09-23 22:00→09-24 07:00 共 139；B: 09-24 17:00→09-25 00:00 共 117）。
- pending 44→46（队列活跳），done 908。剔除 st-stress 压测 29 笔后真实业务死信 366。
- **今晚牺牲批预测：若 44 笔 pending 统一重投，预计 18 笔（41%）再死**
  （TTL 族 4 + CREATE-GUARD no-token 11 + 内容已被他会话落地的空转 3）；
  另 31 笔 base_head 落后、24 笔 meta.stale=true、5 笔触碰热册，落地时仍有 CAS/合并损耗。

### 1.2 系统性死因排行榜（按真实归因）

| # | 死因族 | 数量 | 占比 | 实质 |
|---|--------|------|------|------|
| 1 | 热册三向合并族（3WAY 58 + BASE-UNKNOWN 5） | **64** | 16.2% | 合并器对"ours 同侧身份键重复/判不了条目"的歧义保守策略，横跨 9 个 catalog；比 CAS 更大的热册病根 |
| 2 | 冲突标记残留（PRECOMMIT-HOOK 49，其中 47 笔检出实为冲突标记；含关联共 **50**） | **50** | 12.7% | 快照本身带着会话 worktree 未解决的合并标记入队，落地被各种 hook 名拦截——hook 名只是表象 |
| 3 | CREATE-GUARD | **36** | 9.1% | no-token 23 主导；两轮复发（09-23×4 → 09-24×19，恶化 4.8 倍），跨 13 会话，系统性流程缺陷 |
| 4 | SNAPSHOT-NOT-APPLIED | 31 | 7.8% | 落地器自身静默丢失防线（压测暴露），非会话侧问题 |
| 5 | TRANSLATION-COVERAGE | 27 | 6.8% | 新建 .py 缺大白话简介，与 CREATE-GUARD 同构（注册表状态分歧） |
| 6 | PROTECTED-PATHS 族（直拦 9 + hook 17） | 26 | 6.6% | 真违规与"语言不通"混合：正则只认 `[ARCH-APPROVAL:ARCH-*]`，裁定号机械上不被消费 |
| 7 | LANDING-ENV-GATE-AUTOREG | 19 | 4.8% | 裁定#351 fail-closed 把 gate 加载失败（环境故障）判成死信 |
| 8 | GATE-VOCAB 15 / CAS-BASE 15 / REFERENCE 10 / TTL 族 10 / CASCADE-STALE 8 / CAP-LOOKUP 5 | 63 | 15.9% | 各自门禁；TTL 与 CAP-LOOKUP 属"可前移快败"型 |

复发实证：PROTECTED-PATHS 两晚三波（sweep-tail 单会话 18 笔同类死、ulib3c 连续两晚 6 笔）——
"连投连死不修复"形态，即死亡发现滞后（排队数小时才死）使属主会话已收工、无法当窗修复。

### 1.3 关键机制发现（承重代码精读）

1. **enqueue 侧零门禁预跑（属实，边界精确）**：`scripts/commit_queue.py` 全文零 import
   gateway/preflight。三条生产入口全部裸奔：裸 CLI（CQ `_cmd_enqueue` L2164）、
   machine 车道（LAND `reroute_auto_commit_to_queue` L2607）、requeue（CQ L1425）。
   **唯一例外**：交互正门 `git_commit.py --enqueue`（L847-855）有 18 道白名单预检 + exit 8。
2. **现成预检机械可复用**：`commit_preflight.run_preflight`（rule_bridge）——锁外、只读、
   零写副作用（仅审计 jsonl）、18 道白名单 + 内联适配层（`_INLINE_PREFLIGHT_CHECKS`）、
   设计目标"锁外 3-5 秒快败"，铁律"预检=提前失败不是豁免，锁内权威链照跑"。
   死信榜已有战功（LOOKUP 门禁 1 秒快败消灭一个死信类、RULING-REFERENCE 悬空号前移）。
3. **CREATE-GUARD 适配器存在同源缺口（本次最关键发现）**：内联适配器
   `_check_inline_create_guard`（PF L202-249）调 `_check_creation_token(gateway,...)`，
   后者读 `gateway.project_root` 的**盘上 token 册**（会话盘面版，token 可见）→ 预检放行；
   落地侧读 serializer worktree 盘上册 = **HEAD 版**（袋未含注册表文件时）→ 冤杀。
   即现有预检是"会话口径"，不是"落地口径"——今晚 deaths 即使走了 --enqueue 也拦不住。
   修复抓手现成：`_check_creation_token` 有 `registry_data` dict 注入点（create_guard L856）。
4. **落地物化顺序**：`_apply_snapshot`（LAND L1326，注册表族走 `_merge_registry_file`
   条目级三向合并）→ `_prestage_snapshot`（L1369）→ `gateway.commit()` 全门禁。
   预检要同源，必须仿真"HEAD ∪ 袋物化"这一态，而非会话盘面态。
5. **depends-on 是弱约束非排序锁**：仅存 `meta.depends_on`（CQ L753），不等待前置，
   唯一消费点=落盘后级联 stale 标记（CQ L1025-1074）；且 09-24 base_blob 装表前重验恒空转
   （CQ L620-625 自认）。
6. **daemon 吃启动时刻代码**，纪元自检 re-exec 锚 HEAD 已提交态（DAEMON L643-713）——
   预检逻辑改动必须在落地后等纪元换血或手动重启，盘上热修对常驻 daemon 无效。
7. **PROTECTED-PATHS 不读裁定册**：保护清单硬编码于 `check_protected_paths.py` L71-82；
   标记正则 `\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]`（L69）只认 ARCH-* 议题号；
   message 经 kwargs 通道传入（GW L2498-2499），队列重建 message 时会丢标记。
   该 gate 整体 fail-open（import 失败降级内置 4 条最小清单）。
8. **裁定册无机判字段**：`ruling_registry.yaml` schema 无 scope/路径集/失效日；
   `affected_files` 只是信息性列表。**#410 条目三处失真**：`status: decided` 越四值枚举
   （合法值 active/superseded/deprecated/draft）；用 `related_files` 而非 schema 的
   `affected_files`；summary 自称"授权链补全 PROTECTED-PATHS 所需批文"但该门机械上不消费
   裁定号——这条授权链目前只对人类有效。
9. **CAPABILITY-LOOKUP 审计 store 已同源**：读写两侧收敛同一物理目录
   `<主仓>/.runtime/lookup_audit/<sid>.jsonl`（写端 strip_session_worktree、读端
   anchor_main_root，#ARCH-324 修过锚定）。它校验"过程"非"内容"——**不可由 blobs 合成**，
   预检只能查 store 里该 sid 有无有效 entry（秒级）。
10. **成本口径**：门禁全链平均 79s/P90 189s（含锁等待）；serializer worktree 实测单链
    ~5.9s（n_specs=102，大量 trigger_skip 摊薄）；元数据子集 3-5s 设计目标可实现。
    死信三分类标记表已存在（CQ L242-286，`classify_dead_reason`）。
11. **bags/blobs 只增不减**：`.runtime/commit_queue/blobs/` 19941 个文件，cleanup_done
    明确不清理（CQ L1553），内容寻址天然去重但无退役通道。

## 2. 根因模型（四因分类）

| 因 | 机制 | 覆盖死因 |
|----|------|---------|
| **A. 证据状态分歧** | 盘上 YAML 真源读 worktree HEAD 态，会话按未提交盘面态自检自以为过 | CREATE-GUARD 36、TRANSLATION 27、TTL 族 10、GATE-VOCAB 15 |
| **B. 信封字段丢失** | commit message / session_id 在队列转译中变形或丢失 | PROTECTED-PATHS message 通道、CAP-LOOKUP sid 断裂 |
| **C. 字节级污染** | 快照带冲突标记/私钥等坏字节入队，落地侧任何 hook 都会拦 | 50 笔（12.7%） |
| **D. 落地器自身缺陷与环境误判** | 静默丢快照、环境故障判死信、三向合并歧义保守 | SNAPSHOT 31、LANDING-ENV 19、3WAY 族 64 |

对应治本映射：A→同源预检（M1/M2）；B→信封契约（M3）；C→字节预扫（M2.2，性价比之王）；
D→落地器自校验与分类修正（M5）；跨 A/B 的"审批语言巴别塔"→裁定适配器（M4）。

## 3. 分期施工

### M1 预检挂线（第一夜，最小承重墙）

把既有 `run_preflight` 接到三条裸奔入口，挂点=CLI 生产者层（**不挂 `enqueue_item` API 层**——
该层"零 git 依赖"是在案不变量，CQ L620-625）：

- M1.1 `_cmd_enqueue`（CQ L2164）：`_read_files_from_worktree` 之后、blob 落袋**之前**调
  `run_preflight(GitCommitGateway(project_root=<入队 worktree>), mode="enqueue",
  extra_skip={"CLAIM-REQUIRED"})`（skip 集对齐 git_commit.py L852 先例）。
  blocking → exit 2 DENIED + 结构化死因处方。拒绝时零垃圾 blob。
- M1.2 `reroute_auto_commit_to_queue`（LAND L2607）同形态接入。
- M1.3 `requeue_dead_item`（CQ L1514 之前）接入；`--from-bag` 时先跑现成 sha256 自校验
  （CQ L1494-1499）。
- 预检自身超时 → degraded 放行 + 审计（对齐 PF fail-open 口径），绝不因预检故障堵队列。
- 立竿见影类（白名单已含）：CAP-LOOKUP、TTL×2、PROTECTED-PATHS、DIRECTORY-CONTRACT、
  RULING/ARCH-REFERENCE、EXEMPT-ZONE-FM——按今晚 pending 面≈覆盖 15+ 笔/月 死因。

### M2 同源化与字节预扫（第二夜）

- **M2.1 CREATE-GUARD 同源化（本方案核心件）**：适配器 token 判定基准从"会话盘面册"
  改为"**落地仿真态**"= HEAD 册 +（若注册表 ∈ 本袋 files）袋内注册表 diff，注册表族
  复用 landing `_merge_registry_file` 同一函数做条目级合并；经 `registry_data` 注入点
  （create_guard L856）喂给 `_check_creation_token`，检测核心零分叉（净零）。
  效果：token 不在册的袋在入队口 1 秒被拒，处方直给 `batch_creation_tokens.py` 命令。
- **M2.2 冲突标记字节预扫**：对袋内文本 blob 扫 7 类合并冲突标记（判据语义对齐
  pre-commit check-merge-conflict，含 `\ No newline` 等边角），命中即拒。
  纯 bytes 零状态零 git，一眼扫掉 12.7% 死因。**排进第一夜**（与 M1 同批，成本≈0）。
- M2.3 TRANSLATION-COVERAGE 同源适配（27 笔，PF 白名单注释"适配面大挂起待复测"——
  本次按 M2.1 同模式做落地仿真；head 比对复用 module_translation_registry）。
- M2.4 GATE-VOCAB 轻量预检（15 笔）：袋 .py 物化到一次性 tmp + 现成
  check_vocab_hardcode.py --files；注意该检测链整体 fail-open，预检同样只快败不豁免。
  优先级最低，可延后。

### M3 信封契约与结构化处方

- M3.1 袋 manifest 增 `envelope.final_message` 字段：enqueue 时快照最终 commit message
  （含 `[ARCH-APPROVAL:...]` 标记），landing 原样使用——根治 message 通道丢标记冤杀
  （`[GW:]` 标记不可伪造的现有防线不动，envelope 只增不覆）。
- M3.2 session_id 透传断言：landing 提交时校验 gateway 收到的 sid == 袋 session_id，
  不等即死信（防读错审计 jsonl）。
- M3.3 拒收处方结构化：每类死因附一键修复命令（token 登记/字段补齐/裁定引用格式），
  预检事件审计 jsonl 增处方字段——属主会话当窗修复，不再"死在队里无人认领"。
- M3.4 token 先行机械化：M2.1 同源判定的自然产物——"袋内文件 token 在盘面册有、
  HEAD 册无、且注册表不在本袋"→ 拒收 + 处方"先落 token 批或把注册表并入本袋"。
  后续（二期）可自动生成 token-only 前置袋挂 depends-on。

### M4 裁定适配器（审批语言统一）

- M4.1 ruling_registry schema 扩展：`approved_paths: [pattern...]` + `expires_at`（可选）。
  净零申报：**替代物 = `[ARCH-APPROVAL:issue]` 人肉翻译层**（每来一个裁定号就注册一个
  ARCH 议题的现流程）。
- M4.2 `protected_paths_gate` 增裁定查询：命中保护路径时查活跃裁定（status=active/decided
  且未过期）的 approved_paths 覆盖 → 放行 + 审计引用裁定号；marker 语言保留兼容。
- M4.3 #410 修补三失真（status 归位 decided→合法值、related_files→affected_files、
  补 approved_paths 接住清道三袋）——**替代明晨"注册 ARCH 议题"的人肉翻译**。

### M5 非预检类治本（独立小件，可分派并行班）

- M5.1 SNAPSHOT-NOT-APPLIED（31 笔）：`_apply_snapshot` 后写后读回逐文件 sha 比对
  （复用 CREATE-GUARD 的 safe_write 判据风格），不符→当场退 pending 不进 dead。
- M5.2 LANDING-ENV-GATE-AUTOREG（19 笔）：gate 加载失败从死信改判 `LandingEnvironmentError`
  （退 pending，有限次数后升级死信）——环境故障不该产生死信。
- M5.3 热册三向合并族（**64 笔，最大单一死因，本包只登记不挖**）：
  "ours 同侧身份键重复/身份判不了"是合并器歧义保守策略，需独立矿（合并器语义 + 9 个
  catalog 的键规范）另开专包。
- M5.4 blobs 退役通道：done/dead 关联 blob 引用计数 + 归档策略（低优先级卫生件）。

## 4. 验收口径

1. **历史回放**：395 笔死信逐一喂新预检 → 输出"应拦数 vs 实拦数"（目标：A/B/C 三因类
   拦截率 ≥95%）；**908 笔 done 回放误拦数必须 ≈0**（假阳性是本方案唯一不可接受失败）。
2. **对消统计**：周窗对比 preflight_events.jsonl 拒收数 vs dead/ 新增数，按死因族分列。
3. 性能：预检单件 ≤5s（P50），超时 degraded 放行率 <1%。
4. 回归：test_commit_queue.py + preflight 既有测试全绿；新增红蓝例含
   "袋含注册表 diff / 不含注册表 diff × token 在册 / 不在册" 2×2 矩阵。

## 5. 风险与边界

- **预检 ≠ 保证落地**：cascade_stale / CAS / 三向合并是时序类，enqueue 时刻判不了；
  M1-M4 后死信剩余预期=真竞态个位数 + M5.3 热册族（另治）。
- **daemon 纪元**：预检在 producer 侧（enqueue 进程）执行，不依赖 daemon 换血——
  这是挂 CLI 层的额外好处；但 M3 envelope 消费在 landing 侧，需 daemon 纪元换血生效。
- **白名单准入铁律**：每 gate 进预检前逐 gate 输入面审计（PF 在案铁律），M2 各件
  施工时各附一段输入面审计注释，沿用 PF 现有格式。
- enqueue 响应拉长 3-5s：可接受；拒绝发生在 blob 落袋前，零残留。
- 不动的东西：`enqueue_item` API 零 git 依赖、`[GW:]` 标记体系、锁内权威门禁链、
  serializer worktree 单写者语义、k=4 池 CAS 重放。

## 6. 登记与排期

- 施工登记：apply_depgraph 设计节点 + 本文档转正式 construction 包（待批后）。
- 排期建议：第一夜 = M1 全部 + M2.2；第二夜 = M2.1 + M2.3 + M3.1-M3.3；
  M4/M5 分派并行班（M5.3 热册族独立立项挖矿）。
- Token 登记：本文档 creation_token 已按"token 先行批"铁律单批登记
  （capability=commit_queue_cure，created-by=st-qcure-20260925）；
  提交时 token 册变更单批先行落 HEAD，本文档第二批。
