---
ttl: task_bound
title: OBJ_R 标准与规则线——真源设计稿（历史重放器第一优先）
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# OBJ_R 标准与规则线——真源设计稿

> 骨架卡 [README.md](README.md) 的挖矿产出。定调依据：主文档 §0.5 核心定调十三条
> （#8 根约束不可自我迭代 / #9 先他指后自指 / #12 进化留痕可回滚）+ 宪法 §4（季度退役
> 审计=reconcile_execution_log 触发率）。**形态保守铁律：自动化的是提案和证据，不是裁决**
> ——本稿全部产出均为"AI 提案→治理立案→Owner 修标→重考历史"四步流水线的执行件设计。

---

## ① 六向寻路台账

| 向 | 矿脉 | 判定 | 关键产出（真源锚点） |
|----|------|------|---------------------|
| R1 内部反查·上（政策层） | 尺子升级的既有制度件 | signal | 宪法 AGENTS.md §4 季度退役审计；ruling_registry.yaml（entry_schema 九字段，#20-D 编号铁律）；EXEMPT-ZONE-FM warn→阻断灰度先例（README §1.6 ⑥） |
| R2 内部反查·下（代码层） | gate 框架真实结构与阈值现状 | signal | GateSpec(gate_id/check/priority)，check 签名 `(gateway, files, **kwargs) -> tuple[bool, str]`（commit_gate_registry.py）；check_all 按 priority 升序、单 gate 异常 fail-closed；gate_execution_stats.jsonl（.runtime/audit/，P1-E 触发率数据燃料）；**阈值=模块级硬编码常量**（_MAX_COMPLEXITY=15 / _HARD_LIMIT=120 / _LEDGER_ALERT_THRESHOLD=20），commit_gates 无一接 threshold_loader |
| R3 内部横查·同构参照 | 阈值外置化的仓内先例 | signal | alert_threshold_registry.yaml（REG-ATH-001）+ threshold_loader.py fail-closed 统读改造（AI-THD-001，2026-08-17 存量 9 模块清零硬编码）——重放器与 S3 施工项的直接同构母版 |
| R4 内部横查·事故档案 | 案例库首案与漏拦先例 | signal | 2026-09-17 传送带 serializer pathspec bug（首案，见 §⑤）；884 项死信积压 8 天无人发现→THD-ALERT-003/004 补课（REG-ATH-001 v1.4.0）；FOREIGN_CHANGE 恶性循环（宪法 §2.3） |
| R5 内部推理·方法裁定 | 重放评分量尺选型 | signal（裁定） | 拦截集合 Jaccard 主判据，否决 Kendall tau（裁定理由见 §②-E） |
| R6 外部业界（可选向） | policy 回归测试业界名 | 在档复用 | V2-R1 champion/challenger 同构 + policy-as-code 回归（shadow evaluation）常识；本班零实时外搜，零 429 受阻 |

---

## ② 历史重放器设计（第一优先，可直接施工）

### A. 目标与非目标

- **目标**：新阈值/新 rubric 上线前，对历史提交集重放，**证明拦截排序不变**——误拦不增、该拦不放走。重放不过=修标一票否决（卡内第 4 步"重考历史"的执行件）。
- **非目标**：不重放提交编排层（锁/stash 隔离/GW 标记/exit code 路由是 `GitCommitGateway.commit()` 的职责，与判定无关）；不做全自动裁决——delta 归因与最终修标归 Owner。
- **重放域**：仅**内容扫描型 gate**（own-scope staged diff 扫描，即 CONTENT_SCAN_CACHE_WHITELIST 同域）。依赖全局仓库状态/锁/DB 会话的 gate（WORKTREE-REQUIRED、CLAIM-REQUIRED、HELD-OVERLAP、SESSION-REQUIRED 等）标记 `out_of_scope`，不进判据。

### B. 输入：历史提交集抽样方案

- **时间窗**：`git log --since --until` 默认近 90 天（覆盖 gate 体系成熟期），全量提交数为分母。
- **分层抽样（默认 N=100）**：
  | 层 | 抽法 | 底表 | 配额 |
  |----|------|------|------|
  | ①已知拦截 | gate_runs.passed=0 的 task 对应提交 | gate_runs 表（GateRepo）JOIN reconcile_execution_log（含 commit_message/commit hash 字段）取回 commit_hash | ≥30（不足全取） |
  | ②正常通过 | gate_runs.passed=1 随机抽 | 同上 | 50 |
  | ③特殊形态 | merge / --allow-multi-domain / worktree 提交 | git log 元数据 | 10 |
  | ④随机一般 | 时间窗内均匀随机 | git log | 10 |
- **staged 快照重建方式评估（三案对比）**：
  | 方案 | 评估 | 裁定 |
  |------|------|------|
  | A. `git stash create` | 不可行：stash 只快照**当前**工作树/暂存区，无法重建历史时点；且不含 index 完整语义 | 否 |
  | B. detached worktree 重建（`git worktree add` 于 commit^，再 `checkout <commit> -- .` 使 index=commit 树） | 技术可行但重：每笔一次 worktree 增删，Windows IO 慢；且真实 gateway 路径会触碰锁与 stash 隔离副作用（本仓提交必经 GitCommitGateway 串行锁，scripts/git_commit.py 头部铁律） | 备用（仅当 gate 需要真实文件系统时降级使用） |
  | C. **内存 stub gateway（采纳）** | 历史提交的 own-scope diff 是纯数据：`git diff-tree -p <commit>`（first-parent diff）=当时 staged 内容——宪法 §2.5"commit 后核实暂存区归属"证实本仓 staged≈commit。构造鸭子类型 stub 服务 diff，**零仓库状态变更、零 worktree、可并行** | ✅ 主方案 |
- **本仓真实约束（读 scripts/git_commit.py 头部证实）**：全项目唯一合法 commit 入口=GitCommitGateway（串行锁+stash 隔离+GW 标记，裸 commit 被 GATE-COMMIT-GW 阻断）。因此重放**绝不走 gateway.commit()**，只复用其 check 层；历史上每笔提交的内容即 first-parent diff，这正是 check 函数的全部输入。

### C. 重放引擎：纯函数对照

- **复用的真实类/函数**（零新增框架）：
  - `zephyr.gov_enforcement.rule_bridge.commit_gate_registry.CommitGateRegistry / GateSpec / GateResult`——check_all 按 priority 升序调度，与生产同构；
  - 各 gate 工厂（`make_bare_getenv_gate()` / `make_secret_hardcode_gate()` / `folder_capacity_hard_limit_gate.make_...` 等）——按 in_process_gate_registry.yaml 的 `module_path + factory_function` 动态加载（gate_auto_registrar.py 同款）；
  - ReplayGateway stub 只需实现 gates 实际消费的 `run_git(args)` 接口（已核实 bare_getenv_gate 等消费三个调用族）：`git diff --cached --name-status --diff-filter=AM` → 预计算文件清单；`git diff --cached [-U0] -- <file>` → 预计算 patch；`git rev-parse --show-toplevel` → 固定哑值。diff 数据全部来自 B 方案的 diff-tree 预取。
- **对照协议（同一种子 diff × 两套阈值）**：
  1. 旧判定：gate 模块现状常量下 `spec.check(replay_gateway, files, session_id="replay")`；
  2. 新判定：`importlib.util.spec_from_file_location` 加载 gate 模块副本 + `setattr` 覆盖阈值常量 + 重建 GateSpec 后同输入再跑——**importlib 直载 gate 模块是 commit_gate_registry docstring 明示的 mutation-testing 既有先例**，非新发明；
  3. delta 四值：`both_pass / both_block / new_block(潜在误拦新增) / new_pass(该拦放走)`。
- **阈值注入现状缺口（如实登记）**：commit gate 阈值全部是模块级硬编码常量（R2 已核），无配置注入点——重放器用常量覆写绕行，同时把"阈值外置化"列为施工项 S3（对标 R3 统读母版）。

### D. 评分口径

| 指标 | 口径 | 数据源 |
|------|------|--------|
| 误拦率 | new_block 中经归因判"不该拦"的比例；自动化阶段先用新增拦截率（new_block 数/N）作代理 | 重放报告 + 逐案归因表 |
| 漏拦率 | 旧拦截集合（层①）中被新阈值放走（new_pass）的比例 | 层①重放报告 |
| 排序保持度 | 拦截集合 Jaccard = \|旧∩新\|/\|旧∪新\|，全局与单 gate 两个粒度 | 重放报告聚合 |

**评分选型裁定（R5，自裁留痕）**：主判据=**拦截集合 Jaccard**，否决 Kendall tau。理由：①tau 需要全序——gate 输出是二元 (passed, detail)，本项目无连续严重度分数，"排序"无定义域；②"排序不变"的业务语义在本场景就化为集合不变性：旧拦截集合基本保留（不误拦）+ 新拦截集合不膨胀（不添乱）；③Jaccard 可按 gate 分解归因、可解释给 Owner。tau 列为未来引入连续风险分后的升级项（登记于待 Owner）。

### E. 通过判据（数值门槛，预注册，重放前锁定）

| # | 判据 | 门槛 | 效力 |
|---|------|------|------|
| P1 | 该拦放走 | 层① new_pass 数 = **0** | 一票否决（放走=安全倒退，零容忍） |
| P2 | 误拦不增 | 新增拦截率 ≤ 2%（N=100 时 ≤2 笔）**且**逐案归因表确认误拦数=0（新增拦截可全归因为"正确收紧"则放行） | 误拦 ≥1 即否决 |
| P3 | 集合保持 | 全局拦截 Jaccard ≥ 0.98，且每个单 gate 触发集合 Jaccard ≥ 0.95（允许边缘抖动，禁全域漂移） | 一票否决 |
| P4 | 分层稳健 | 层①与层③分别复检 P1-P3 | 与主判据同效力 |

### F. CLI 设计草图（设计稿，不写代码）

```
python -m zephyr.governance.rule_replay replay \
  --since 2026-06-15 --until 2026-09-17 \
  --strata blocked=30,passed=50,special=10,random=10 \
  --gates ALL_CONTENT_SCAN            # 或 --gates NO-BARE-GETENV,FOLDER-CAPACITY-HARD-LIMIT \
  --new-thresholds new_thresholds.yaml  # [{module, const, value}] \
  --out .runtime/tmp/replay/<run_id>/report.jsonl

子命令：replay（跑重放落 jsonl）/ report（聚合→summary + 判据 P1-P4 判定）/ diff（两次 run 对比）
```

report.jsonl 每行字段：`run_id, commit_hash, commit_date, stratum, files[], gate_id, priority, own_scope_hash, old{passed, detail_digest}, new{passed, detail_digest}, delta, replay_ms, error, out_of_scope_reason`。

### G. 存储与留痕（裁定+理由）

- **原始报告落 `.runtime/tmp/replay/<run_id>/`**。理由：①测试隔离红线——工具默认输出禁写生产路径（data/ 业务目录）；②.runtime 已整体 gitignore（commit_queue.py 头部证实），落 data/ 会给审计区制造临时噪音；③报告可由 run_id 随时重生成（重放是纯函数）。
- **达标重放的 summary（判据结论+归因表）必须 promote 到 docs/_working/ 随裁定归档**——证据不落盘则修标裁定不可追溯，违反定调 #12 留痕可回滚。裁定条目在 ruling_registry 的 summary 字段引用 promote 后路径。具体落点目录待 Owner（见 §待 Owner-3）。
- 工具对 DB **只读**（抽样底表 gate_runs / reconcile_execution_log），禁写。

---

## ③ 标准资产盘点表（全量，v1）

| 尺子 | 真源路径 | 现值 | 最后修订 | 修订依据 | 体检指标（§④ 口径） |
|------|---------|------|---------|---------|---------------------|
| 堵点阈值 N=20/24h | src/zephyr/gov_enforcement/rule_bridge/commit_belt_daemon.py（_LEDGER_ALERT_THRESHOLD=20；>24h 告警） | 20 条 / 24h | 2026-09-16（belt_daemon 事件驱动化） | Owner 定调"传送带+堵点专人专事机制化" | 触发率（告警行频次）、堵点清账时延 |
| gate 优先级 | src/zephyr/gov_enforcement/commit_gates/*.py（priority 字段）+ in_process_gate_registry.yaml（gate_id/module_path/factory_function/enabled） | ~170 gate（gate_registry.yaml total_gates 机生） | 持续（新 gate 即改） | #ARCH-GATE-PRIORITY-UNIQUENESS-001（同 priority 撞号阻断） | 触发率/误拦率/单 gate Jaccard |
| own_scope 清单 | gate_registry.yaml `own_scope` 字段（机生禁手改，generate_gate_registry.py 产出） | 机生 | 2026-09-16 generated_at | 结构校验型 vs 内容扫描型分级（宪法 §3.3） | own-scope 覆盖率（新 gate 登记 compliance） |
| 容量/复杂度类阈值 | _MAX_COMPLEXITY=15（high_complexity_gate）/ _HARD_LIMIT=120（folder_capacity_hard_limit_gate）等模块常量 | 见各常量 | 各 gate 落地日 | 个案裁定 | **阈值余量漂移**（仓库增长外推触顶日） |
| 告警阈值（监控链路 11 类） | alert_threshold_registry.yaml（REG-ATH-001）+ threshold_loader.py fail-closed 统读 | v1.4.0 | 2026-09-11（死信积压阈值补课） | 55 号 §3.3"阈值不集中即不可审计" | 触发率/误报率/漏拦（事故反推） |
| 甄别 rubric（L1 初筛判据/四闸口径） | 未建（随漏斗建成即入本流水线）；四闸现行口径=挖矿 SOP 内嵌 | — | — | — | 建成后：漏斗噪声率 |
| 考纲（模型考试题型/双跑样本量/显著性门槛） | 未建（随 OBJ_M M3） | — | — | — | 建成后：考试成绩与实战相关性 |
| 模型分派二维法（→OBJ_M 路由表） | 挖矿 SOP 内嵌方法论（docs/01_policies_and_standards/sop/mining_sop/mining_sop_policy.md） | 经验值 | 随 SOP 修订 | 按战役修订 | OBJ_M 路由准确率 |
| 配额数值（子代理并发/token 预算/GPU 窗） | 人工口径（随配额池建库入 REG-ATH 同款注册表） | 2-3 并发等经验值 | — | — | 配额命中率/排队时延 |
| SOP（挖矿 v1.4.0/审查/施工） | mining_sop_policy.md（version: 1.4.0, 2026-09-15）等 | v1.4.0 | 2026-09-15 | 2026-09-14 Owner"把矿挖干"裁定沉淀 | SOP 修订频率 vs 执行偏差案例数 |
| 红线/负面清单 | OBJ_S 卡（未建真源）；现行散见宪法 §9 运维红线 | 人工 | — | 年审 | 违红线事故数（应恒 0） |
| 裁定档案（升级记录真源） | ruling_registry.yaml（#1-#285，entry_schema 九字段） | 全人工升级 | 持续 | #20-A/B/D 登记铁律 | 裁定频次/重放否决率 |
| 退役审计（流水线雏形） | 宪法 §4 + gate_execution_stats.jsonl（.runtime/audit/）+ reconcile_execution_log 表（governance.db） | 季度 | 2026-09-16（P1-E 数据燃料落地） | #ARCH-310 R4 规范预算 | 触发率持续近零→降级/退役 |

盘点结论：**门禁阈值类是唯一已有数据燃料（gate_execution_stats.jsonl）但缺执行件的尺子**——重放器补执行件；告警阈值注册表是外置化母版；其余尺子按"随宿主建成即入流水线"排期，不在本班铺开。

---

## ④ 月度标准体检设计（挂 L1 内监慢周期）

- **指标口径**：
  | 指标 | 统计窗 | 告警线 | 数据源 |
  |------|--------|--------|--------|
  | gate 触发率 | 滚动 30 天 | 连续两窗 <1% → 退役候选（宪法 §4 对齐）；>50% → 噪音候选（阈值过松） | gate_execution_stats.jsonl + gate_runs 表 |
  | 误拦率 | 滚动 30 天 | 单 gate ≥5% → 立案进案例库 | skip_gates/豁免审计记录 + 案例库误拦标签 |
  | 漏拦 | 事故驱动 | 任何漏拦事故即立案（884 死信积压=先例） | 案例库反向归因 |
  | 阈值余量漂移 | 月度 | 外推触顶 <90 天 → 预案 | 容量常量 vs 仓库增长 |
- **产出：标准建议书 schema（standards_proposal）**：`proposal_id / date / 尺子 id（盘点表行键）/ 现状值+真源路径 / 证据（jsonl 统计摘要+案例库引用）/ 提案值 / 重放判据预告（§②-E 模板）/ 预期影响（两问：好在哪+消灭哪段人工，定调 #11）/ 状态（draft→filed→ruled|rejected）`。
- **治理立案对接**：提案 file 后进治理层标准库变更流程；Owner 裁决后按 ruling_registry entry_schema 登记（ruling_id/title/date/category/summary/affected_files），summary 引用 proposal_id 与重放 summary promote 路径。**AI 层只持提案权与引用，不持尺**（README §1.6 归属裁定）。

---

## ⑤ 案例库 schema（事故归因→缺陷模式→阈值提案）

- **登记表起步于本目录 casebook.md（攒 ≥5 案后由 Owner 裁定是否升 catalogs 正式 YAML 注册表）**——避免未成熟即建注册表（规范预算 §4.1）。
- **schema**：`case_id / date / source_incident（事故登记引用）/ 死因归因 root_cause / 缺陷模式 defect_pattern（受控词表；真源=L7 heritage 词表，casebook 只引用不扩展）/ 复发签名 signature / 修复配方 recipe / 模式规范名 pattern_norm（与 L7 H4 具名三字段同名同义，pattern_norm=同案归并键）/ 波及面 affected_gates|registries / 阈值提案 → standards_proposal_id / 状态（open→patterned→proposed→ruled）/ 防复发验证（重放用例|体检指标挂钩）`。
- **三字段与词表边界（红蓝 R1-B6）**：signature/recipe/pattern_norm 与 L7 `ai_heritage_defect`（H4）同名同义——归并时模式登记落 L7（机读真源），casebook 只留 case+三字段引用；pattern 词表扩充一律在 L7 侧办理（L7 §2.1 五方地盘图同源裁定），casebook 禁自造新 pattern 值。
- **流程**：事故自动喂（L1 内监捕获告警行/死信/回滚）→ AI 归因填 root_cause → 模式归并（同 pattern 合案）→ 生成阈值提案进 §④ 流水线 → Owner 裁决 → ruling_registry 登记 → 重放验证闭环 → 回写 L7 传承。
- **首案（示例，写入卡内）**：
  ```yaml
  case_id: CASE-2026-0917-001
  date: '2026-09-17'
  source_incident: 传送带 serializer pathspec bug（Owner 口述在案；细节待补登）
  root_cause: commit_queue B 段 serializer 落盘的 git pathspec 处理缺陷——路径参数
    未过白名单语义校验即拼入提交命令（66 号备忘 §6.5 pathspec 白名单语境；enqueue
    侧轻检已对 .git/密钥路径 fail-closed，落盘侧未对齐）
  defect_pattern: 编排层路径参数未复用入队侧白名单（单侧防御）
  affected_gates: [commit_queue 入队轻检, FOREIGN-CHANGE, COMMIT-SCOPE]
  阈值提案: 落盘侧复用 §6.5 白名单校验 + dead_reason 结构化枚举（便于死信归因统计）
  status: open   # 死因细节待 Owner 确认后转 patterned
  ```
  （本班禁 git，无法回溯提交现场；死因按 commit_queue.py 头部协议推定，待 Owner-4 补登确认。）

---

## ⑥ 施工项清单 / 挖矿日志 / 自审闸

### 施工项清单（全部为设计交付，施工另派工）

| # | 项 | 内容 | 依赖 | 备注 |
|---|----|------|------|------|
| S1 | 历史重放器 CLI | ReplayGateway stub + importlib 阈值覆写 + 分层抽样器 + report.jsonl（§②-B/C/F） | 无（纯只读） | 新模块须走 CREATE-GUARD+登记+RULE-DEPGRAPH |
| S2 | 聚合与判据器 | report/diff 子命令 + P1-P4 判定 + 归因表模板（§②-E） | S1 | |
| S3 | 阈值外置化提案 | commit gate 硬编码常量→注册表条目清单（对标 AI-THD-001 统读） | 治理立案 | 改 gate 源码=治理层资产，非本卡权限 |
| S4 | 月度体检任务 | 触发率/误拦率统计器 + standards_proposal 生成器，挂 L1 内监慢周期 | gate_execution_stats 积累 ≥1 窗 | |
| S5 | 案例库起步 | casebook.md + 首案补登确认 | Owner-4 | |

**验收标准补全（红蓝 R1-F4）**：S1=对 ≥50 笔历史提交重放出 report.jsonl 且字段齐全可聚合；S2=同一报告两次聚合结果逐位一致+四判据 P1-P4 输出；S3=外置化提案清单覆盖全部硬编码常量且逐条标真源行号；S4=体检产出 standards_proposal 且含触发率/误拦率两指标；S5=casebook.md 含首案且 pattern_norm 字段可被 L7 引用。

### 挖矿日志

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| R1 | 政策层反查（宪法 §4/ruling_registry/灰度先例） | signal | 立案对接件全齐 |
| R2 | gate 框架代码反查（GateSpec/签名/stats/阈值现状） | signal | check 签名+硬编码清单 |
| R3 | 阈值外置化同构母版（REG-ATH-001 统读改造） | signal | S3 母版 |
| R4 | 事故档案反查（pathspec/死信积压/FOREIGN_CHANGE） | signal | 案例库首案+漏拦口径 |
| R5 | 评分量尺选型 | signal（裁定） | Jaccard 主判据 |
| R6 | 外部业界 | 在档复用 | champion/challenger 同构；零实时外搜零受阻 |

### 自审闸三态裁定

**裁定=施工**（本设计稿定稿+README 状态翻转）。理由：①重放器是四步流水线第 4 步"重考历史"的执行件，Owner 已定调"上线前强制"，缺执行件=流程空转；②过度工程检查：本班只产设计不产代码，CLI 仅草图，符合"自动化提案和证据、不自动化裁决"的保守形态；③无套娃：递归一层上限遵守（升级流程本身的升级=Owner 直管）；④两问自答——好在哪=把"重考历史"从纪律变成可执行判据（P1-P4 预注册），消灭哪段人工=退役审计与修标验证的人工抽样比对。

### 待 Owner（自裁不能处）

1. 重放通过判据数值（P1 放走=0 / P2 ≤2% / P3 Jaccard 0.98·0.95）预注册确认。
2. 评分裁定追认（Jaccard 主判据，Kendall tau 否决理由）。
3. 重放 summary 的 promote 落点目录（docs/_working 下何处/是否进审计区）。
4. 首案 CASE-2026-0917-001 死因细节补登确认（本班禁 git 无法回溯）。
5. S3 阈值外置化是否立案（触及 gate 源码=治理层资产变更）。
6. 案例库升格 catalogs 正式注册表的时机（攒案门槛）。
7. CREATE-GUARD creation_token 未登记留痕：本班硬边界"禁登记 token"，由主会话/Owner 补登 DESIGN.md 的 creation_token。

## 增补（2026-09-17 五轮，Owner 讨论定案：治理物 schema/枚举/模板第四族）

Owner 问"门禁/文档字段/规则文件/模板（如 TTL 枚举值）是否都进升级流程，规则能不能升级"。
裁定：**全部可升级，包括规则——差别不在能不能升，在笔在谁手里**。治理物按爆炸半径分三级：

| 级 | 例子 | 流程 |
|----|------|------|
| T1 参数级（旋钮） | TTL 枚举值新增、堵点阈值、模板字段增补、rubric 数值 | AI 提案（触发率/误拦率证据）→重考历史→治理立案，批得轻 |
| T2 结构级（家具） | 字段 schema 变更、模板重构、新 gate 引入、枚举值废弃 | AI 提案→治理立案→Owner 批；受宪法 §4 净零预算约束（新 gate 声明替代谁） |
| T3 语义级（承重墙） | 规则 YAML 权限语义（谁能批谁）、宪法正文、红线清单、fail-open/closed 翻转 | 永不自动——Owner 修宪笔，AI 只备料 |

**不对称规则**：收紧约束可走快车道；**放松约束的提案永不进自动通道**（治理物版利益冲突回避，防自我放大）。

**"不被规则限死"三条正门**（限死多半是忘了后两条）：①改规则（本流水线，慢而治本）；
②豁免通道（单次留痕，先例=--allow-non-worktree/--allow-overlap/no-lookup 白名单）；
③裁定成先例（进 ruling_registry 后续引用）。正解顺序=③解今天→②应急→①治本。

**连带义务**：治理物变更必须**同一 commit 自带迁移**（改 TTL 枚举=所有读 TTL 的门禁/清扫器/
模板同批改，禁止半拉子上线）——MODIFY-GUARD 三件套同步的同构纪律。

**盘点表扩充**：原"尺子清单"七项之外补第四族=治理物 schema 与枚举（frontmatter 必填字段/
templates/ 全部目录 8 件/TTL·status·doc_type 枚举/各注册表 entry_schema），每把尺真源路径入
盘点全量表。

**待 Owner 项主会话处置（夜批授权下自裁）**：#1 判据数值=按提案原值追认生效（红蓝轮复核）；
#3 重放 summary promote 落点=自裁 docs/_working/ai_layer_vision/OBJ_R_rules_standards/replays/
（ttl task_bound）；#4 首案按本卡记录登记 CASE-2026-0917-001；#7 token 已由主会话 wave1
ceremony 登记（capability ai_layer_vision）——该待办销项。#2/#5/#6 属治理立案类，保留待
治理流程（合规不越权）。

## 红蓝 R1 修复记录（2026-09-17，红队 B 发现，修复组 1）

| 编号 | 修复内容 | 落点 |
|------|---------|------|
| B6 | casebook schema 补 signature/recipe/pattern_norm 三具名字段（与 L7 `ai_heritage_defect` H4 同名同义，pattern_norm=同案归并键）；声明 pattern 词表真源=L7 heritage 词表、casebook 只引用不扩展（禁自造新 pattern 值） | §⑤ |
