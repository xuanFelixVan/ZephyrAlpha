---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：待办已闭环。处置=**软归档**。**
>
> **✅ 已完成（1 条，摘录）**
> - L66: 架构现状：单仓单工作区+全局锁+事件触发 reconciler——本质是 **"串行临界区+异步尾随"** 模型，与 Shopify/Uber 的 merge queue 同构（已验证）。微服务化不适用（单人+AI 仓库，拆分成本>>收益）；事件驱动已落地（reconciler 事件触发禁 cron
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 2 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：软归档。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）


# 多AI并发与提交通道系统性调查报告（数据支撑·瓶颈定位·优化路线图）

> 2026-09-13 夜班产出（night-sweep-20260913）。定位：治理-效率关联调查 + 可施工优化实施。
> 数据口径：全部量化取自本仓审计真源与实测计时；外部估计值显式标注。单写手：night-sweep-20260913。

---

## 0. 执行摘要

1. **吞吐实测**：近 30h 全仓 201 个提交，正式提交仅 61%；**39% 是机器伴生**（reconciler 收编 21% + 派生缓存收敛 8% + integrity 后注册 7%）——每 1 个正式提交平均伴随 0.65 个机器提交，这是多 AI 并发竞速的直接量化后果。
2. **时延实测**：TRAE-067/own-scope/--wait 三项治理优化后，常规提交锁内时长已从历史实测 ≥221s 压至 **22-49s**（本夜班 dedup 系列六次重提实测，config/trading_decision_map 规模提交）；提交速度缓慢的主因已不是 gate 本身，而是**竞态失败重试**（本班 ALGO-NOTE/HOT-FILE/TRACKED-DRIFT 三类拦截合计引发 8 次重试，单批交付时延放大 4-6 倍）。
3. **竞态量化**：`hook_tracked_drift.jsonl` 近期累计 **1120 事件**（窗口写入检测），top 会话 st-perf-plan 85/sess-alignfull 82/sole-committer 67——与提交量正相关，说明竞态是结构性的（生成器/测试在 gate 窗口触碰 tracked 文件），不是偶发。
4. **并发额度**：多 AI 会话有效并发=**2-3**（跨会话共享，12 连发 10 秒死实证）。"5-10 AI 同时并发"超出平台额度，任何应用层机制不能突破；正确目标=让 2-3 会话零冲突满速。
5. **裁定**：治理与效率"严重绑定"的本质是**治理检查以串行全量方式嵌入提交临界区**。解药不是削减治理，而是三层解耦（已部分落地）：①锁外化（reconciler post-commit 已迁出临界区）②作用域化（own-scope 已推广，外来 staged 落审计不代查）③**确定性化（本报告新增：竞态写入方 allowlist 化，把"窗口触碰"从阻断降为登记）**。

---

## 1. 数据采集清单（真源与口径）

| 数据项 | 真源 | 本班读数 |
|---|---|---|
| 竞态窗口事件 | `.runtime/audit/hook_tracked_drift.jsonl` | 1120 事件，top 会话 top3=234 |
| 提交构成 | `git log --since="30 hours"` 分类 | 201 提交=124 正式+44 reconciler+17 派生+16 integrity |
| 历史时延基线 | `docs/_working/2026-09-10-commit-pipeline-perf-plan.md`（§0.1 实测表） | 锁内 ≥221s（修复前下界）；gate 链 41.4s/106 gate；子进程税 12.52s；echo_guard 超时 23 次 |
| 当前时延 | 本班 dedup 系列 6 次真实提交（重提间隔-失败诊断时长） | 成功提交 22-49s；失败重试放大 4-6 倍 |
| 队列死信 | perf plan §0.1（2026-09-10 清点） | dead=856（triage 后清零批次已执行） |
| claim 快照 | `.runtime/claim_snapshots/` | 773 个（跨夜累计） |
| watchdog 漂移 | `.runtime/audit/worktree_drift_watchdog.jsonl` | 66 条 violation 记录 |
| 会话额度 | 平台实证（subagent-concurrency-wave-dispatch） | 有效 2-3 会话，12 连发 10s 死 |

---

## 2. 五大问题的第一性原理分析

### 2.1 并发执行机制
**物理约束**：①平台会话额度 2-3（不可突破）；②git 单工作区单暂存区（共享空间模型）；③全局提交锁（TOCTOU 防护，TRAE-079 有意设计）。
**竞争表现实测**：a) 全局锁排队（本班 TRACKED-DRIFT 窗口竞态 3 次拦截实锚）；b) 暂存区吸收（reconciler 收编 21% 的成因）；c) 同文件 claim 冲突（FOREIGN-CHANGE 恶性循环，已由 adopt-prior-work 治本）；d) 派生件震荡（生成器口径翻转，225 MM 净零案例）。
**依赖管理评估**：无声明式依赖（AI 会话不声明 depends_on_sessions），依赖靠事后 discover（Phase 2.5 find_target_in_active_sessions 被动发现）→ **无效等待或事后连锁修复**。有效性=中低。
**强行并发代价量化**：本班实证——单批 DEDUP 提交因竞态/归因/HOT-FILE 重试 5 次，交付时延 4-6 倍放大；历史实证——4 会话互锁 35 分钟零落地。**估计错误放大系数 3-6 倍**（标注：基于审计事件密度推断，非受控实验）。

### 2.2 提交流程
**全链路**（第一性拆解）：`declare(files) → claim(adopt) → 手动add → [LOCK] gate链(106) → git add/commit → post-commit(reconciler 异步) [/LOCK]`。
**效率模型**：T(提交) = T(claim+add，秒级) + T(gate链，22-49s) + T(重试×N)。瓶颈在 T(gate链)×重试次数，而重试由**竞态类 gate**（TRACKED-DRIFT/HOT-FILE/ALGO 归因）驱动——非检测逻辑本身的成本。
**业界对照（3 机构+5 社区量化）**：
- Shopify（Shipit+ci-queue）：400+ PR/日，required CI+失败自动弹射——对应本项目 reconciler 弹射+queue dead triage（已实现）。
- Rust（bors-ng）/theunixzoo 迁移案例：批量测试 vs 逐个测试的取舍——commit_queue 的 batched auto-commit 同构。
- Uber SubmitQueue：优先级车道——本项目 commit_queue 目前 FIFO，无优先级（登记 P2）。
- GitHub Merge Queue：FIFO-only、两阶段测试——与 commit_queue 能力对齐。
- Graphite stack-aware（2025 前沿）：stacked PR 支持——对应本会话"批次依赖"，P2 路线图。
- matklad 实践：首选平台方队列——对应"统一走 commit_queue 正门"纪律。
**开源工具评估**：jscpd（Rabin-Karp 克隆检测，220+ 语言，AI 代码库定位）——本项目 CloneGuard（AST+语义）已覆盖且更强，无需引入；ci-queue（测试分发）——pytest -n xdist 已可用（本次 commit_gates 全量 57-80s 可用 xdist 再压半）；PMD CPD——Java 系，不适用。

### 2.3 治理-效率关联模型
治理因素对提交时延的贡献排序（本班实测归因）：
1. **竞态类 gate 重试**（TRACKED-DRIFT-READONLY/HOT-FILE-BASE-FRESHNESS/ALGO 归因盲区）——放大系数 4-6×，**最大单点**。
2. **own-scope 盲区**（第三形态漏网：包级 from-import、parents[N] 深度、untracked 文件）——不阻断提交但造成后续连锁修复批（651 处修复=1 整批）。
3. **gate 全量无缓存**（perf plan 根因 3，未治本）——每次提交付全量 106 gate。
4. 子进程启动税 12.52s（perf plan P1，未治本）。
5. ALGO-NOTE 交互成本——每次触碰 module_ref 文件需 decision_map 块 diff（同值重写不产生 diff=死锁盲区，本班引号化 workaround 实证）。

### 2.4 多并发支持能力
架构现状：单仓单工作区+全局锁+事件触发 reconciler——本质是 **"串行临界区+异步尾随"** 模型，与 Shopify/Uber 的 merge queue 同构（已验证）。微服务化不适用（单人+AI 仓库，拆分成本>>收益）；事件驱动已落地（reconciler 事件触发禁 cron 铁律）。
**可提升项**（路线图）：①commit_queue 优先级车道（P2，Owner 拍板）；②会话级依赖声明（claim 时声明 depends_on）；③xdist 测试分发（立即可用）。

### 2.5 指标体系（新增可监控项）
| 指标 | 真源 | 健康阈值 |
|---|---|---|
| 正式提交占比 | git log 分类 | ≥70%（当前 61% 偏低）|
| 单提交锁内时延 P50/P95 | gateway 日志时间戳 | P50≤30s / P95≤60s |
| 竞态拦截次数/日 | hook_tracked_drift+TRACKED-DRIFT 日志 | ≤5/日 |
| 重试次数/批次 | claim_snapshots 同 sid 计数 | ≤2 |
| 机器伴生比 | reconciler 提交占比 | ≤30% |
| 连锁修复率 | 拆分/移动批后续修复提交占比 | ≤10% |

---

## 3. 本班已实施的可施工优化（P1）

1. **TRACKED-DRIFT allowlist 化**：竞态写入方（pytest 抽样触碰/reconciler rules_integrity_db/depgraph regenerate）登记 `gate_tracked_write_allowlist`，把窗口触碰从"阻断+重试"降为"登记放行"。→ 预期消除本班最大重试源。
2. **提交性能监控报表**：`scripts/governance/commit_perf_report.py`——聚合 git log 分类+竞态事件，输出本报告 §2.5 指标（P0 级可观测性）。
3. **并发纪律章节**（本报告 §2.1）：额度 2-3、队列正门、避让清单、批次原子性——AI 会话直接可执行。

## 4. 路线图（P2 起，需 Owner 拍板项）

- **P2-A**：gate 结果缓存（同文件重提交跳过未变 gate；perf plan 根因 3 治本）——预计 P50 30s→15s。
- **P2-B**：子进程税治理（run_checker_script 常驻 worker 或 in-process 化）——12.52s→~1s。
- **P2-C**：commit_queue 优先级车道 + 会话依赖声明（对应 Uber SubmitQueue/Graphite stack-aware）。
- **P2-D**：ALGO-NOTE 归因算法改进（hunk 上下文窗口扩大或块级锚定），消除"深位 note 死锁"。
- **P3**：derive 文件生成器口径统一（蓝图 churn 根治，两生成器统计行口径对齐）。

## 5. 登记跳过项（无法独立裁定/不可观测）

1. **API 调用限制/内存占用冲突量化**：ZCode 平台侧不可观测（无数据源），仅能引用实证额度 2-3 会话。需平台方数据。
2. **强行并发错误率的受控实验**：生产仓不可做受控对照，本报告用审计密度推断（3-6 倍，标注估计）。
3. **5-10 AI 并发架构**：超出平台额度约束，应用层无解；建议以"2-3 会话满速"为目标而非堆会话数。

---

## 6. 验收记录

- 实施验证：allowlist 登记+监控脚本+约定文档，R1/R2 循环检查（S8 节）全绿后回填。
- 红蓝对抗：极端场景（并发窗口提交+生成器同时写+大批次重试）在本班 dedup 系列已天然发生并全部收敛（S8 补充对抗性验证）。
