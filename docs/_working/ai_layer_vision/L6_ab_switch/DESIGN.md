---
ttl: task_bound
title: L6 切换段——真源设计稿（模块级影子运行框架第一优先）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L6 切换段真源设计稿

> 骨架卡 [README.md](README.md) 的挖干产出。定调依据：主文档 v1.1 增补定调 #7（A/B 蓝绿=进化
> 安全带）/ #9（进化分级自治）/ #12（进化留痕可回滚）+ 宪法 §5（risk_tier 人机门位）。
> **本段最大空白=模块级影子运行**（README 状态行自认），本稿把它挖到可直接施工粒度。
> **形态铁律**：B 组并行的一切产出只写对比区，永不回流生产决策路径——影子不下真决策是
> 本段第一不变量；自动化的是对比证据与回切执行，切换拍板分级走 §②-E。

---

## ① 六向寻路台账

| # | 向 | 矿脉 | 判定 | 关键产出（真源锚点） |
|---|----|------|------|---------------------|
| R1 | 内部反查·上（政策层） | 切换/门位/灰度的既有制度件 | signal | 定调 #7/#9/#12；`risk_tier_registry.yaml`（REG-RISK-TIER-001，9 个 high 域+human_gate 四动作：转 production/注册表净删/flag 出厂翻转/资金破坏性操作）；README §1.6 迁移项⑥"灰度=warn 先行→阻断 成文" |
| R2 | 内部反查·下（代码层） | 并行隔离/flag/前端拍板的真实机制 | signal | `session_worktree.py`（worktree 物理隔离：独立 index/branch/目录；pool lease 瞬时返回；merge 串行化+pre-merge gate）；`config/flags.yaml`（MOD-INF-015 flag 主开关）；`exempt_zone_frontmatter_gate.py` 头注释（post-commit warn→pre-commit 阻断+git ls-tree 渐进收敛）；`web/pages/promotion.html`+`promotion.js`（S13 建议卡：API 真源+二次确认+留痕回执+禁手工造建议） |
| R3 | 内部横查·同构参照 | 业务层与兄弟段的切换先例 | signal | 业务层 §7 A/B 联赛（晋升预注册/降级不退役/regime 标记复活/相关性闸）+§10 三级算法升级（血肉自动/锦标赛自动/骨 Owner）+实盘灰度（1/10 仓 1 个月坡道）；OBJ_R 重放器（gate 参数影子运行已覆盖，DESIGN §②）；OBJ_M 同任务双跑（§4.2，判据冻结+显著性）；OBJ_T 基准任务集（壳，契约预留） |
| R4 | 内部横查·事故与制度档案 | 墓碑与不演练的代价 | signal | 墓碑合并法：registry 计数"含 deprecated 全量"（registry_of_registries.yaml counting_rule×3）、OBJ_M model_registry status=tombstone"退役不删（对齐 L6 蓝绿纪律）"；反例 ARCH-046 全景图不保留墓碑（登记图≠资产登记，本稿墓碑只落资产登记层不落全景图）；884 死信积压 8 天=无监控无演练的同构代价 |
| R5 | 内部推理·方法裁定 | 状态机定形/观察节拍/分级映射 | signal（裁定） | 五态定形 shadow→canary→promote→champion→retire/tombstone（理由 §②-B）；A 股节奏=月度而非周度（对齐月度结算+月度体检既有节拍，周度撞盘中噪声）；审批分级映射 risk_tier 三档（§②-E） |
| R6 | 外部业界（补盲） | 蓝绿/金丝雀/影子部署做法 | signal | EX-R1：shadow=镜像流量零用户影响、晋升判据=同负载指标对齐；canary=分档放量 1%→10%→50%→100%+逐档指标门；blue-green=双环境瞬时互切；特性旗解耦部署与发布。EX-R2：SR 11-7/OCC 2026-13 champion-challenger 影子并行+有效挑战；观察期业界下限 14 天（原地替换）/30 天（架构级）；漂移告警=回滚触发器。EX-R2 子查询 429×1，退避重试成功 |
| REUSE | 在档复用 | V2-R1/迁移项⑥/L4 三查/L1 月度挂点 | signal | champion/challenger 业界名（V2-R1 在档）；灰度成文（README §1.6 ⑥）；"好得反常"三查（L4 卡）；回切演练挂月度体检（L1 内监慢周期） |

受阻记录：EX-R2 子查询 429×1（退避重试成功，全程无编造引文）。零查无。

---

## ② 真源设计

### A. 双版本并行不互染方案（按对象类型分——四家族走同一状态机，各用各的隔离件）

| 对象家族 | 并行方案 | 隔离件（真源） | 本稿角色 |
|---------|---------|---------------|---------|
| **代码/模块**（重点） | **worktree 双检出+对比跑**：A=主区 HEAD 快照、B=challenger 分支，各租一个 worktree，同一冻结回放集分别跑，B 输出只落对比区 | `session_worktree` 机制（pool lease/独立 index/merge 串行化） | **本节详设（A.1）** |
| 门禁参数 OBJ_R | 历史重放器=影子运行已覆盖：新阈值对历史提交集重放，Jaccard P1-P4 一票否决 | OBJ_R DESIGN §②（stub gateway 零仓库状态变更） | 引用，不重设 |
| 模型 OBJ_M | 同任务双跑：五层×20 件、判据冻结哈希、McNemar/Wilcoxon | OBJ_M DESIGN §4.2（dual_run.py） | 引用，不重设 |
| 工具 OBJ_T | 基准任务集沙箱：同一批标准任务新老工具比成功率/速度/成本 | OBJ_T README 待挖清单 2/3（壳） | 契约预留（§③），OBJ_T 挖矿后接线 |
| 规则/判据 OBJ_R 灰度 | 见 §②-G 三档成文 | EXEMPT-ZONE-FM 先例 | §②-G 详设 |

#### A.1 代码模块级影子运行框架（全骨架最大新机制，可直接施工）

**1) 双检出**：影子运行开工时以专用影子会话（`session_id=st-shadow-<switch_id>`）经
`session_worktree_start` 从 `WorktreePool` 租 **两个** worktree（pool 空则 fallback 直建，
机制现成）：

```
.aidrafts/st-shadow-<switch_id>-a/   → checkout 主区 HEAD（champion 快照，只读基准）
.aidrafts/st-shadow-<switch_id>-b/   → checkout challenger 分支（L5 施工交付的 session/<sid> 分支或其 tag）
```

理由：公平性要求 A/B 同环境——主区本身可能有其他会话在途脏文件（R2 隔离不变量正是为此
而生），双侧都进干净 worktree 才是"同负载对比"（EX-R1 晋升判据同款）。

**2) 冻结回放集（corpus）**：影子开工前 1 个体检窗，由输入捕获器记录该模块真实入参样本
N=200（脱敏），+ 该模块现有 tests 全量，构成 corpus；清单+固定 seed 哈希落判据 YAML
（§②-C 字段），**改 corpus=新 switch_id**（判据自改=根约束禁区，定调 #8 对齐 OBJ_M
freeze_rule 先例）。

**3) 对比跑**：同 corpus 分别喂 A/B 两 worktree 中同一模块——进程级隔离，`PYTHONPATH`
各自指向本 worktree 的 `src/`（禁 B import 主区代码）；触发=事件+周历窗口（挂排班表
light 档，**禁 cron/sleep-loop**，宪法 §9.3）；盘中 heavy 模块影子跑受 E0 算力闸互斥。

**4) 不互染三闸（本框架核心不变量）**：

| 闸 | 内容 | 依据 |
|----|------|------|
| 代码闸 | worktree 物理隔离（独立 index/branch/目录）；影子期 B 分支**永不 merge 回主区**（merge 只发生在 promote 后的正式通道） | session_worktree INVARIANTS（R2） |
| 数据闸 | A/B 读同一 corpus **只读快照**；写出各自独立目录（影子会话 staging 区）；**禁写 data/ 业务目录**；需 DB 的模块指向影子副本或标 `out_of_scope`（OBJ_R 重放域划分同款） | 宪法 §9.6 测试隔离 + OBJ_R §②-B |
| 消费闸 | 生产消费方只接主区版本；B 组零消费者——影子定义即"B 输出仅供对比器（L4）消费"，产出落审计链不进任何决策路径 | 定调 #7"影子模式不下真决策" |

**5) 分歧度量**：每 corpus 件记
`{a_digest, b_digest, latency_a/b, mem_a/b, diff_kind: identical|semantic_diff|error_a|error_b}`；
分歧率=非 identical 占比；语义判定用模块自有判据（tests/golden assert）或交 L4 裁定。

**6) 资源预算**：影子跑算力进配额池（定调 #10），配额越限→暂停影子（非回切信号）。

### B. 状态机（五态，进入/退出判据字段）

**裁定留痕（R5）**：五态取业界 canary 分档与银行 champion/challenger 的并集——本仓是
单机系统，流量分档=作用域分档（canary=限模块实例/限场景/仅 warn 档），不需要 1%→10%
的流量百分比档（EX-R1 的 K8s 语境不适用，取其"逐档指标门"精神）。

```yaml
switch_registry:            # 运营态架构数据 → DB（DatabaseService，禁裸 duckdb；RULE-SSOT 裁定留痕）
  switch_id: SW-<yyyymmdd>-<slug>
  object: {family: code_module|gate_param|model|tool|rule, ref: <module_id|gate_id|model_id|...>}
  domain: D_XXX             # risk_tier 查表键
  champion_ref / challenger_ref: <分支|tag|版本|model_id>
  criteria_yaml_ref + criteria_hash          # 预注册冻结
  state: shadow | canary | promoted | champion | retired | tombstone | aborted
  state_history: [{state, since<UTC>, evidence_ref}]
  observation: {start, min_months, signals{...}}   # §②-C
  rollback: {plan_ref, last_drill_date, drill_result}
  promotion_record: {approved_by: auto|independent_review|owner_one_click, receipt_ref, promoted_at}
  tombstone: {sealed_at, seal_ref, revival_conditions[], ttl_deadline}
```

| 态 | 进入判据 | 退出判据（→向） |
|----|---------|----------------|
| **shadow** | L5 施工完成回执 + L4 对比裁定卡（判据冻结哈希在案）+ 双 worktree 就绪 + corpus 冻结 | 影子期判据全绿且满 min_months → **canary**；判据败/好得反常未释疑 → **aborted**（L7 记档） |
| **canary** | shadow 毕业审批（按 §②-E 分级）+ 作用域限定方案在案（限实例/限场景/gate 类仅 warn 档） | canary 期零事故且满 canary 期 → **promote**；任一回切触发（§②-C 表）→ 退 **shadow** 或 **aborted** |
| **promote** | canary 毕业 + 分级审批通过（§②-E）——本态=B 升默认的一次性切换事件，状态即"已切换" | 切换满 1 个体检窗无回切 → **champion**；期内触发回切 → 一键回退，B 退回 **canary** 或 **aborted** |
| **champion** | promote 稳定期满 | 被下一代 challenger promote → **retire**；自身劣化触发 → 自身降级并复活前代（走墓碑复检） |
| **retire/tombstone** | 退位即封存：registry status=tombstone（deprecated 链不删先例），§②-D 规程 | 复活条件触发 → 回 **shadow**（复活≠直提，重走对比）；TTL 满且零复活动量 → 清理提案（Owner 净删门） |

### C. 观察期判据（量化信号+A 股节奏）

**节拍裁定（R5）**：观察期单位=**月度**（对齐 A 股月度结算+月度体检既有节拍；周度撞
盘中噪声且样本不独立）；样本量以交易日计（月内约 20-22 个交易日）。业界下限（14-30 天，
EX-R2）与本仓月度制相容：1 个月 ≥ 业界原地替换下限，high 域 3 个月 ≥ 架构级下限。

| 对象档 | 影子期 | canary 期 | 依据 |
|--------|--------|-----------|------|
| low/medium 域代码件 | ≥1 个月（含 1 个月度体检窗） | ≥1 个月 | 业界 14 天下限上取整到月度节拍 |
| high 域（9 域）代码件 | ≥1 个月 | ≥2 个月（跨 2 个结算周期） | risk_tier high 对齐业务层"6 个月模拟"的保守精神按对象风险缩放 |
| 规则类（OBJ_R） | 不等日历——重放器全量历史重放即完成 | —（上线后走灰度三档） | OBJ_R §②-E P1-P4 |
| 模型类（OBJ_M） | OBJ_M §4.4 判据表 | 路由表灰度 1 个月 | OBJ_M 引用 |

**自动提前回切触发器（预注册，触发即机检执行，人工只收报告）**：

| # | 信号 | 口径 | 动作 |
|---|------|------|------|
| T1 | 正确性事故 | 归因到 B 的生产故障/回滚 ≥1 起 | **立即一键回切**（RTO ≤1 交易日），B 冻结待查 |
| T2 | 分歧率 | B vs A 输出分歧占比 > 预注册上界（默认 5%，进判据 YAML） | 影子期=不许升 canary；canary 期=回切审议 |
| T3 | 性能劣化 | 延迟/内存中位差连续 5 个交易日 > +20% | 自动回切 |
| T4 | 成本上浮 | 单位产出成本 > +15% 且无补偿收益主张 | 回切审议（L4 复核） |
| T5 | 好得反常 | 收益/指标异常放大 | **冻结切换** → L4 三查（泄漏/隐性风险/运气），业务层 anomalous 同一条路线 |
| T6 | 资源冲突 | 影子跑配额越限 | 暂停影子（非回切），窗口顺延 |

### D. 墓碑操作规程（退役件三问：封存哪/何时复活/何时清）

- **封存位置（按对象家族）**：
  - 代码件：`git tag tombstone/<module_id>/<date>` 封存（git 历史=零成本永久库，物理文件不删）+ switch_registry status=tombstone；
  - 注册表条目：deprecated 链不删（墓碑合并法先例，计数"含 deprecated 全量"）；
  - 模型：OBJ_M model_registry status=tombstone（该卡已预留，直接对接）；
  - 文档件：`docs/_archive/`（豁免区前缀已在 EXEMPT-ZONE-FM 清单内）。
  - 边界留痕：**全景图不保留墓碑**（ARCH-046）——墓碑只落资产登记层，depgraph 照常生成器重建。
- **复活条件（任一触发→生成复检工单，L1 regime 门当复活裁判，业务层先例同构）**：
  ①regime 轮换：封存时必填"何种 regime/场景下失效"，该 regime 重现时触发；
  ②负载/规模形态变化：资源画像或负载分布漂移越阈（L1 内监信号）；
  ③champion 暴露同型失效：champion 在墓碑当年的强项场景翻车；
  ④Owner 手递复活卡。**复活≠直提**：一律回 shadow 重走对比（§②-B）。
- **清理条件（TTL）**：tombstone 满 2 个月度体检窗（≈6 个月）+ depgraph 反向依赖=0 +
  期间零复活触发 → 生成清理提案 → **Owner 净删门**（注册表净删=high human_gate，
  risk_tier 强制，AI 只提案）；git tag 永不清。

### E. 切换审批分级表（债类 × risk_tier 九域映射）

| 债类 | 覆盖 | 审批道 | 例 |
|------|------|--------|-----|
| **机械债类**（行为零变化） | 全域 | **全自动**：corpus 输出 byte-identical + gates 全绿 + 自动回切武装即 promote，commit message 声明（medium 域既有纪律） | 重构/依赖升级/性能优化（diff_kind 全 identical） |
| **逻辑债类**（行为变） | medium/low 域 | **独立复核**：L4 对比器独立于施工者裁定（运动员不兼任裁判）+ canary 满期零事故自动 promote | 算法/清洗/信号逻辑升级 |
| **逻辑债类·high 域** | D_EX_CORE/D_POSITION/D_RISK/D_TRADING/D_PLAN/D_DATA/D_GOV_ENFORCEMENT/D_GOVERNANCE/D_GOV_SCRIPTS | **Owner 前端一键**（promotion 页建议卡，§③） | 交易核心/风控/门禁引擎模块切换 |
| **规则类** | OBJ_R 尺子 | OBJ_R 四步流水线+重考历史一票否决 + Owner 修标 | 阈值/rubric/gate 参数 |
| **骨架级** | 增删环节/改层级 | AI 提案+Owner 一键（定调 #9；先他指后自指） | 排班表自身/循环结构变更 |

### F. 回切演练制度（安全带不演练=没有安全带）

- **挂点**：月度体检（L1 内监慢周期，README §1.6 ⑤先例）；round-robin 每月抽 ≥1 个
  在役 champion（优先最近 promote 的）+ 全部未满 TTL 的 tombstone 抽 1。
- **演练三查**（dry-run，不触生产）：①回切指令 dry-run——switch_engine revert 路径可执行、
  状态机回滚分支正确；②champion 快照可重建——git tag/worktree checkout 成功；③回执链
  完整——审计可追溯到最近一次切换。
- **判据**：演练成功率=**100%**，任一失败=事故立案（假安全带比没安全带更危险——884 死信
  积压 8 天无人发现的同构教训）；`rollback.last_drill_date` 超 2 个月度窗未演练 → 内监告警。
- **留痕**：演练报告随月度体检建议书归档，摘要回写 switch_registry。

### G. 灰度纪律成文（"warn 先行→阻断"升级路径，EXEMPT-ZONE-FM 先例）

EXEMPT-ZONE-FM 真实路径（R2 头注释）：前身=post-commit warn reconciler（仅记录报告）→
升级=pre-commit 阻断 gate，带**渐进收敛**（`git ls-tree HEAD`：存量违规跳过允许维护，
新引入违规阻断）+ fail-closed。把这条先例升格为一切新约束的出厂通用路径：

| 档 | 行为 | 最短驻留 | 升档条件 |
|----|------|---------|---------|
| ① shadow | 只记录不动作（触发率/误报统计积累） | ≥1 个月度体检窗 | 统计燃料齐 |
| ② warn | 留痕+审计+通知，不阻断 | ≥1 个月度体检窗 | 误报=0 且 Owner 知情 |
| ③ block | 阻断（flag 出厂翻转） | — | Owner 门位（risk_tier high："flag 出厂翻转"）+ 裁定登记（ruling_registry）+ 渐进收敛 grandfather 条款强制（存量豁免） |

降档（放松）同走 Owner 门位；每档进出留 ruling 痕。规则类对象的 canary 期即复用本表
（gate 类 canary=warn 档，promote=block 档）——灰度三档与状态机在规则对象上是同一条线。

---

## ③ 接线图（四契约+两辅）

| 对端 | 契约 | 方向 | 载荷 |
|------|------|------|------|
| **L5 排产** | 施工完成回执=shadow 入场券：工单关单+worktree 就绪+验收门绿才发 | L5→L6 | {work_order_id, module_id, challenger_branch, criteria_yaml_ref+hash, domain, tier_action} |
| **L4 对比** | 影子期=L4 判据的持续执行现场；L6 回传实测数据供 L4 终裁（升 canary/promote 的裁定出自 L4，评估者独立）；好得反常触发 L4 三查 | L6↔L4 | {switch_id, corpus 统计, disagreement_rate, evidence_pack（判据冻结哈希）} |
| **L7 传承** | 每次切换终局留档：胜者档案/败者档案/判据档案/墓碑登记/回切记录——"判据档案=当时为什么算它赢"直接消费本稿 criteria_yaml | L6→L7 | {promotion_record, tombstone_entry, 判据档案, 回切历史} |
| **promotion 前端页** | high 域/骨架级/规则类切换建议卡。真实先例=`src/zephyr/frontend/dashboard/web/pages/promotion.html`+`features/promotion/promotion.js`（S13：真源 `/api/promotion-advisories`、JS 渲染、**二次确认**、服务端留痕回执、**建议由流水线自动生成禁手工造**）。裁定：**复用该页**，advisory 增 `kind=switch`，不新建页面 | L6→前端 | 建议卡 {switch_id, A/B 对比摘要, 一键切换/一键回切按钮, 证据包链接} → 拍板回执 {approved_by, 时刻, 新状态} |
| L1 内监（辅） | 观察期信号=内监数据源；regime 变化触发墓碑复检（§②-D 复活裁判） | 双向 | drift/偏离信号 → 复检工单 |
| 排班表（辅） | 影子跑/演练任务注册 resource_profile_registry（生成器三源再生，**禁手工增条目**；全项目一张真源） | L6→排班 | 实体登记+周历窗口申请 |

---

## ④ 施工项清单（全部为设计交付，施工另走 construction_workflow_policy）

| # | 项 | 内容 | 依赖 | 备注 |
|---|----|------|------|------|
| S1 | switch_registry 表 | DatabaseService 迁移：§②-B schema 全字段（state/state_history/rollback/tombstone）；时间字段显式时区（RULE-SCHEMA-TZ） | 无 | RULE-SSOT：运营态=DB；禁裸 duckdb |
| S2 | 判据预注册 YAML | `config/switch_criteria.yaml`：per-family 判据模板+T1-T6 阈值族+corpus 冻结字段（常数预注册） | 无 | 改判据=新 switch_id；OWNER 批一次初值 |
| S3 | 影子运行执行器 | `src/zephyr/intelligence/switch_engine/shadow_runner.py`（新增模块）：双 worktree 租借（session_worktree 同款）+corpus 分发+三闸强制+分歧统计落盘 | S1/S2 | 事件+周历触发禁 cron；新模块走 CREATE-GUARD+add_module_translation+RULE-DEPGRAPH |
| S4 | 状态机引擎 | switch_engine 迁移器（五态+T1-T6 机检）+一键回切执行器（revert=状态回拨+消费指针还原，RTO≤1 交易日） | S3 | 回切执行须预演（S7 演练覆盖） |
| S5 | 墓碑管理器 | 封存登记（git tag+status=tombstone）/复活复检工单生成（regime 触发接 L1）/TTL 清理提案（Owner 门） | S1 | git tag 永不清 |
| S6 | 审批分流器 | risk_tier 查表→auto/independent_review/owner_one_click 三道分流；owner 道接 promotion 页 advisory（kind=switch） | S1/S4 | 复用 S13 前端先例，零新页面 |
| S7 | 回切演练任务 | round-robin 抽样+dry-run 三查+演练报告，挂月度体检 | S4 | `rollback.last_drill_date` 超窗告警 |
| S8 | 灰度三档执行件 | §②-G 升降档机检（驻留窗/误报统计）+渐进收敛 grandfather 校验+裁定登记挂接 | S1 | 对标 EXEMPT-ZONE-FM 现成机制 |

依赖序：S1→S2→S3→S4→{S5,S6,S7,S8 可并行}。全部走 worktree 隔离+网关提交+改前 claim。

---

## ⑤ 挖矿日志 + 自审闸

### 挖矿日志

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| R1 | 政策层反查（定调/risk_tier/灰度迁移项） | signal | 审批分级表+灰度三档的制度挂点 |
| R2 | 代码层反查（session_worktree/flags.yaml/EXEMPT-ZONE-FM/promotion 页） | signal | 双检出方案+flag/门位先例+前端契约 |
| R3 | 同构横查（业务层 §7/§10+OBJ_R/OBJ_M/OBJ_T） | signal | 状态机判据字段四家族复用与引用边界 |
| R4 | 事故与制度档案（墓碑法/ARCH-046/884 死信） | signal | 墓碑规程+演练制度的反例支撑 |
| R5 | 方法裁定（状态机定形/月度节拍/SSOT 落位） | signal（裁定） | 五态+canary 作用域化+registry DB 裁定 |
| R6 | 外部业界（EX-R1 部署策略/EX-R2 SR 11-7 观察期） | signal | 指标门精神+月度制与业界下限相容性 |
| REUSE | V2-R1/迁移项⑥/L4 三查/L1 挂点 | signal（在档复用） | 零重复挖矿 |

**判定统计**：signal=7（含 REUSE）/ 受阻=1 次（EX-R2 子查询 429，退避重试成功）/ 查无=0。

### 自审闸三态裁定

**裁定=施工**（本设计稿定稿+README 状态翻转）。理由：①模块级影子运行是骨架卡自认的
"全骨架最大空白"，不定形则 L5→L6 契约悬空、进化安全带缺位；②过度工程检查：不建独立
工作流引擎（状态机=一张 DB 表+一个迁移器）、不建新前端页（复用 promotion 先例）、不建
第二张排班表（全项目一张真源）、OBJ_R/OBJ_M 全部引用不重设；③无套娃：切换制度自身的
升级（灰度三档的升降档）终止于 Owner 门位，递归一层封顶；④两问自答——好在哪=把"影
子不下真决策"从纪律变成三闸可执行不变量、把回切从口头保证变成 100% 演练判据；消灭哪
段人工=观察期人工盯盘（T1-T6 机检自动回切）+回切通道可信度的人工抽查（月度演练）。

### 待 Owner（自裁不能处，3 项）

1. **观察期数值门槛预注册确认**：min_months（1/3 个月）、T2 分歧率 5%、T3 +20%、
   T4 +15% 均为设计定值非实测标定（同 OBJ_M 处置：首轮数据回来后按 OBJ_R 流水线提案修订）。
2. **墓碑 TTL 清理与注册表净删门**：清理判据（2 体检窗+零反向依赖+零复活动量）确认；
   净删行=high human_gate 系 risk_tier 强制，AI 永远只提案。
3. **CREATE-GUARD creation_token 补登**：本班硬边界"禁登记 token"，DESIGN.md 的
   creation_token 由主会话/Owner 补登。
