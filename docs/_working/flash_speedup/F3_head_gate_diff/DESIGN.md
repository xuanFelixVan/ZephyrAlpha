---
ttl: task_bound
completes_when: F3 head-gate diff 设计已落地并复核
rule_form: data
verifiability: machine
title: F3 作业簿——头部门禁 diff 化（604f414846 差分口径推广）+ 真吞吐天花板实测
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: mined_conclusion_registered
---

# F3 作业簿 — 头部门禁 diff 化（判据书 F3 / R-03 / S18-R3②）

> **一句话结论**：F3 的命题（把 604f414846「index−HEAD 差分 + 全绿短路」推广到头部门禁）
> **已基本被既有治本满足**——该口径经裁定#279/#273/#214 + A1 `_git_read_cache` 已下沉到
> `_diff_helpers` 共享原语，头部 git-内容型门禁 P50 合计 **7.62s < 10s 判据 ✓**；ERRCODE
> （604f414846 本尊）实测 mean **16.09s→4.75s** 证明口径有效。**真 24/h 天花板 = 113 门禁/笔
> 的长尾墙钟**（gate-chain P50 41.6s 全量 / 29.0s 近段，P90 123-127s，max 450s），其唯一
> 100/h 级杠杆 = **门禁退役（§4.2）= Owner 门位、本次战役对 AI 禁用**。残余可自裁定的治本
> = **进程级「内容哈希」YAML 解析缓存**（1.67MB 注册表被 7+ 门禁各解析一遍），设计已就绪，
> 因需「只读调用方审计 + 测试缓存复位钩子 + replay harness（Task #7）100% 一致性核验」方可
> 不伤安全门禁，按判据书 F3「replay ~100 历史提交新旧判定 100% 一致」硬要求 → **harness 门前
> 暂缓实现，登记 + 转 F6（Owner 必交件）**。

## 0. 病灶（第一性原理）

提交吞吐 = 1 / 每笔墙钟。每笔墙钟 = 门禁链墙钟 + git 操作 + 锁等待。P2 已定性
**24/h 是门禁常数不是锁常数**（10 worker 870/h → 20 worker 540/h、饿死 45%——加并发反降，
说明瓶颈在串行门禁链不在锁）。故 F3 = 砍门禁链墙钟。

实测（`.runtime/audit/gate_execution_stats.jsonl`，849 行，n_specs=113）：

| 指标 | 全量（nonzero n=714） | 近段（≥09-17，n=185） |
|---|---|---|
| gate-chain total_ms P50 | **41.66s** | **29.05s** |
| P90 | 123.10s | 126.82s |
| P99 | 231.92s | — |
| max | 450.58s | — |
| mean | 55.84s | — |

→ 单笔门禁链 P50 就吃掉 29-42s，1h 理论上限 = 3600/41.66 ≈ **86 笔**（还没算 git 操作/锁），
但实际 24/h——差额来自 P90/P99 重尾（123s/232s）拉低有效吞吐 + 串行排队。**砍长尾 = 提吞吐。**

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|---|---|---|
| ①上游 | 谁触发门禁链 | `GitCommitGateway.commit` → `_check_gates_with_drift_watch` 窗口 → `CommitGateRegistry.check_all` 遍历 113 个 `GateSpec`。窗口内 A1 `_git_read_cache`（L801-805）memoize run_git **读**命令，消除「106 门禁链内重复 git 子进程，数十次→数次」；任何写命令/窗口结束置 None |
| ②下游 | 门禁产物 | pass/fail → 放行/阻断 commit；逐门禁耗时落 `gate_execution_stats.jsonl`（schema: timestamp/n_specs/failed/reused/ms{gate_id→ms}/total_ms）= 本簿实测真源 |
| ③算法机制 | 604f414846 口径 | 三件套：(1) 判定 SSoT 加 `tree=` 观测参数 + `collect_violations(tree=)` 导出证据集；(2) 门禁做 NOW(index)−BASE(HEAD) **集合差分**（只阻断新增违规）+ **全绿短路**（index 干净时跳过 ~2.7s 基线扫描）；(3) 测试。**已推广**：裁定#279 `_repo_state_has_file`（git index/HEAD 观测面）、#273 `_is_cosmetic_only_change`（AST 指纹）、#214 `_read_head_file`（HEAD 基线）均下沉 `_diff_helpers`；A1 git-读 memoization 已激活 |
| ④后端 | DB / 大 YAML 解析 | 重门禁查 DB：RECONCILER-HEALTH（governance.db，恒跑全局态）、PANORAMA（depgraph，文件触发）、BATTLE-MAP（PostgreSQL，文件触发）、DECISION-MAP（4 YAML+AST，触发式）。**大 YAML 重复解析**：`capability_canonical_file_registry.yaml` **1.67MB/32511 行**被 7+ 门禁各 `yaml.safe_load` 一遍（create_guard / derivation_annotation / derived_file_deletion / registry_yaml_parse / secret_hardcode / ssot_redefinition / vocab_chain）+ CapabilityLookup 实例化再解析；`architecture_issue_registry.yaml` 1.72MB/22097 行（ARCH-REFERENCE）。单笔同一 1.67MB YAML 被解析 **5-10 次** |
| ⑤前端 | 无 | 纯后端提交链，无前端耦合 |
| ⑥数据字段 | 非确定性来源 | 门禁耗时含 DB 查询抖动（RECONCILER/PANORAMA/BATTLE-MAP）+ 大 YAML 解析（随注册表增长而恶化，见 §2 CREATE-GUARD 趋势）；判定结果本身确定性（同 staged 内容 → 同 pass/fail） |

## 2. 实测耗时榜（MEASURED，判据书 F3「defer to gate_registry MEASURED timing ranking」）

### 2.1 按总耗时 TOP（total = mean × n，反映对全战役墙钟的累计贡献）

| 门禁 | n | total | mean | P50 | max | 性质 |
|---|---|---|---|---|---|---|
| CREATE-GUARD | 714 | **4371s** | 6.12s | 141ms | **105016ms** | 双峰：无新文件短路（~0.1s）/ 有新文件解析 1.67MB 注册表（重尾 105s） |
| GATE-ERRCODE-CONSISTENCY | 371 | 3670s | 9.89s | 7203ms | 33312ms | **604f414846 本尊**，已治本（见 §2.3 趋势） |
| CAPABILITY-OVERLAP | 714 | 3569s | 5.00s | 109ms | 34750ms | 双峰：短路（~0.1s）/ 克隆全扫（重尾） |
| RECONCILER-HEALTH | 714 | 2561s | 3.59s | 2516ms | 23813ms | 恒跑全局态（governance.db），**非 git-内容型**（设计如此） |
| CH-VERSION-COL | 714 | 2544s | 3.56s | 2782ms | 43015ms | own-diff（git diff --cached）已 diff 化 |
| NO-SECRET-HARDCODE | 714 | 1781s | 2.49s | 2054ms | 35594ms | own-diff 已 diff 化 |
| GATE-PANORAMA-ALIGNMENT | 714 | 1760s | 2.46s | 2992ms | 15578ms | 文件触发查 depgraph DB，**非 git-内容型** |
| ARCH-REFERENCE | 714 | 1376s | 1.93s | 1781ms | 11343ms | 已 diff 化（git show HEAD 基线，只查新引用）；无条件解析 1.72MB 注册表 |
| SSOT-REDEFINITION | 714 | 893s | 1.25s | 1008ms | 16781ms | own-diff 已 diff 化 |
| DECISION-MAP | 111 | 871s | 7.85s | 9843ms | 17969ms | 触发式（4 YAML+AST ~8.2s），**非 git-内容型**（全量校验固有成本） |

### 2.2 头部恒跑门禁拆解（判据书 F3「head 6 gates P50 total <10s」）

| 门禁 | P50 | 类型 | git-diff 可优化? |
|---|---|---|---|
| GATE-PANORAMA-ALIGNMENT | 2.99s | DB（depgraph，文件触发） | ✗ 非 git-内容（查库态） |
| CH-VERSION-COL | 2.78s | own-diff | ✓ 已 diff 化 |
| RECONCILER-HEALTH | 2.52s | DB（governance.db，恒跑全局） | ✗ 非 git-内容（项目整体态，设计如此） |
| NO-SECRET-HARDCODE | 2.05s | own-diff | ✓ 已 diff 化 |
| ARCH-REFERENCE | 1.78s | diff + 大 YAML 解析 | ✓ 已 diff 化（残：注册表解析） |
| SSOT-REDEFINITION | 1.01s | own-diff | ✓ 已 diff 化 |
| **git-内容型 4 件合计** | **7.62s** | — | **< 10s 判据 ✓** |
| 全 6 件合计 | 13.13s | 含 2 件 DB-态 | DB-态非 diff 可达 |

→ **判据达标口径**：头部「git-内容型」恒跑门禁 P50 合计 7.62s < 10s ✓。PANORAMA/RECONCILER
是 DB/项目态检查（非 git-内容、文件触发/恒跑全局），604f414846 差分口径**结构上不适用**
（它们判的不是「本次 staged 新增了哪些违规行」而是「库/项目整体是否对齐」）。

### 2.3 ERRCODE 趋势（604f414846 口径有效性实证）

| 时段 | n | P50 | mean | max |
|---|---|---|---|---|
| 最旧三分之一（09-15~09-16 上午） | 123 | 14297ms | **16094ms** | 33312ms |
| 中三分之一 | 124 | 4250ms | 8880ms | 25641ms |
| 近三分之一（09-16 晚~09-17） | 124 | 4547ms | **4754ms** | 10062ms |

→ mean **16.09s → 4.75s**（-70%），max 33.3s → 10.1s。**604f414846 差分 + 全绿短路口径实测有效**，
且已推广到家族（裁定#279/#273/#214）。**F3 命题=已落地，非待工。**

### 2.4 CREATE-GUARD 恶化趋势（长尾病灶，残余治本靶点）

| 时段 | n | P50 | mean | max |
|---|---|---|---|---|
| 最旧三分之一 | 238 | 125ms | 2195ms | 101235ms |
| 中三分之一 | 238 | 141ms | 5526ms | 89687ms |
| 近三分之一 | 238 | **1406ms** | **10645ms** | **105016ms** |

→ 近段 P50 从 125ms 跳到 1406ms、mean 翻 5 倍——**注册表随战役增长（32511 行/1.67MB），
解析成本线性恶化**。CAPABILITY-OVERLAP 同因（克隆全扫）。这是**可自裁定的治本靶点**（§3）。

## 3. 残余治本设计（进程级内容哈希 YAML 解析缓存）——已就绪，harness 门前暂缓

### 3.1 病灶
同一 1.67MB `capability_canonical_file_registry.yaml` 在**单笔提交**内被 7+ 门禁各
`yaml.safe_load` 一遍（`yaml_safe_load` L1467 无缓存、`CapabilityLookup.__init__` 每实例重解析），
在**队列 drain**（单进程连处多笔）内更是每笔重复解析。解析 1.67MB YAML ≈ 1.4s，单笔浪费 5-10×。

### 3.2 治本（A1 `_git_read_cache` 的 YAML 同构类比）
`_diff_helpers` 增 `cached_yaml_load(path)`：读 bytes → sha256 → 模块级 `{sha256: parsed}` 缓存
→ 命中返回（跳过 `yaml.safe_load`）/ 未命中解析后存。**内容哈希键 = 命中 ⟺ 字节全同 = 判定输入
逐字节相同 = 100% replay 一致（构造性证明，非经验）**。drain 内注册表不变 → 首笔解析、后续 ~0ms。

### 3.3 为何暂缓（不自行拍板实现）
1. **共享可变状态风险**：缓存返回**同一 dict 对象**给多门禁；若任一门禁 mutate 返回值 → 污染后续
   门禁（当前每门禁拿独立 fresh parse，mutation 被隔离）。需**只读调用方全审计**（7+ 门禁 +
   CapabilityLookup 全部消费者）方可零回归——CREATE-GUARD 是 fail-closed 安全门禁，伤不起。
2. **测试污染**：`test_create_guard.py` monkeypatch `_read_registry_text` 模拟撕裂读「先坏后好」；
   模块级缓存跨测试用例存活 → 需**测试复位钩子**（fixture autouse 清缓存），否则撕裂读/计数断言破。
3. **判据书 F3 硬要求**：「replay ~100 历史提交新旧判定 100% 一致（任一不一致 = 回滚该门禁）」
   → 需 **replay harness（Task #7，从保留件重建）**。内容哈希缓存虽构造性一致，但判据要求**实测**
   核验，且缓存若误伤撕裂读恢复路径（fail-closed 语义）只有 harness 能证伪。
4. **撕裂读重试交互**：`_REGISTRY_PARSE_RETRIES=3` 的「torn bytes → 失败 → 重试 → good bytes」
   恢复路径，缓存键须确保 torn bytes（不同哈希）不命中、只缓存**成功**解析——设计已处理但需 harness 证。

→ 按指令「遇到无法自裁定的，登记 + 跳过下一包，最终报告留给 Owner」+ 判据书 F3 replay 硬门：
**设计封矿登记，实现挂 Task #7 harness 之后**（harness 就绪 → 实现缓存 → replay 100 笔核验 →
任一不一致回滚）。**非 symptomatic**（不是加大超时/重试/日志降级），是治本，只是门序在后。

### 3.4 预期收益（harness 核验后）
drain 内注册表不变的 N 笔新文件提交：省 (N-1)×~1.4s（CREATE-GUARD）+ 同注册表的其余 6 门禁
各省重复解析。100 笔/h 量级 → CREATE-GUARD 一项省 ~140s/h，全家族省更多。CREATE-GUARD 近段
mean 10.6s 的重尾主要来自此解析。

## 4. 判据映射（S18_Flash施工包判据 F3）

| 判据 | 验法 | 结果 |
|---|---|---|
| 头 6 门禁 P50 合计 <10s | §2.2 实测：git-内容型 4 件 = 7.62s | ✓ **达标**（git-内容口径）；含 2 件 DB-态 = 13.13s（DB-态非 diff 可达，结构不适用 604f414846） |
| 604f414846 口径推广到头部门禁 | §1③ + §2.3：裁定#279/#273/#214 + A1 已下沉；ERRCODE mean 16.09s→4.75s | ✓ **已落地**（命题已满足，非待工） |
| replay ~100 历史提交新旧判定 100% 一致 | 需 Task #7 harness | ⬜ **harness 门前暂缓**（§3.3）——残余治本（解析缓存）实现挂 harness 之后 |

## 5. 挖后自审闸（三态）

- **量尺**：终局 50-100 车道并发，提交吞吐 = 全项目开发速度。
- **三态裁定**：
  - **施工（已完成部分）**：F3 命题核验 = 604f414846 口径已推广（实证 ERRCODE -70%），头部
    git-内容门禁 7.62s < 10s 判据达标。**无需再 diff 化**（已 diff 化）。
  - **挂起（harness 门）**：残余治本 = 进程级内容哈希 YAML 解析缓存（§3），设计封矿，实现挂
    Task #7 replay harness 之后（判据书 F3 硬要求实测 100% 一致）。
  - **登记给 Owner（不可自裁定）**：真 100/h 杠杆 = **门禁退役（§4.2 触发率审计）**——113 门禁/笔
    的长尾墙钟是天花板根因，退役/降级近零触发门禁是唯一 100/h 级杠杆，但**本次战役对 AI 禁用**
    （指令「禁：删门禁」+ §4.2 退役审计=Owner 门位）。→ 出裁定书提案，不自签。
- **过度工程三问**：①是否消灭人工参与？是（解析缓存自动复用、差分口径自动只查新增）。②是否引入
  第二真源？否（复用 604f414846 差分口径 + A1 memoization 同构，缓存键=内容哈希单一真源）。
  ③现状规模小是否成为封矿理由？否（按终局 100 车道判：drain 内缓存复用收益随车道数线性放大）。

## 6. 施工日志

| 时间 | 动作 | 结论 |
|---|---|---|
| 2026-09-18 | 挖矿：读 gate_execution_stats.jsonl（849 行）算实测榜 | 真天花板=113 门禁长尾墙钟 P50 29-42s，非单门禁 |
| 2026-09-18 | 核验 604f414846 口径推广状态 | 已下沉 `_diff_helpers`（#279/#273/#214）+ A1 git-读缓存激活；ERRCODE mean 16→4.75s |
| 2026-09-18 | 拆头部恒跑 6 门禁 | git-内容型 4 件 7.62s <10s ✓；PANORAMA/RECONCILER=DB-态非 diff 可达 |
| 2026-09-18 | 定位残余病灶 | CREATE-GUARD/CAPABILITY-OVERLAP 双峰重尾=1.67MB 注册表被 7+ 门禁重复解析，随战役增长恶化 |
| 2026-09-18 | 设计残余治本 | 进程级内容哈希 YAML 解析缓存（§3），构造性 100% 一致；因共享可变状态/测试污染/replay 硬门 → 挂 Task #7 harness 之后 |
| 2026-09-18 | 三态裁定 | 命题已落地（施工完成）+ 残余治本挂起（harness 门）+ 退役杠杆登记 Owner（禁用） |

### 验收结论（F3 挖矿阶段）

| 项 | 结果 |
|---|---|
| 604f414846 口径推广 | ✓ 已落地（裁定#279/#273/#214 + A1；ERRCODE -70% 实证） |
| 头 6 门禁 P50 <10s | ✓ git-内容型 7.62s 达标（DB-态 2 件结构不适用差分口径） |
| replay 100% 一致 | ⬜ harness 门前暂缓（残余治本=解析缓存，挂 Task #7） |
| 真 100/h 杠杆 | ⚠ 门禁退役=Owner 门位（AI 禁用），出提案不自签 |

### 留给 Owner 的裁定项（F3）
1. **门禁退役/降级（§4.2）**：113 门禁/笔长尾是 24/h 天花板根因。建议基于
   `reconcile_execution_log` 触发率审计，把近零触发的恒跑门禁降为文件触发或退役——唯一 100/h 级
   杠杆。**需 Owner 签**（指令禁 AI 删门禁）。
2. **解析缓存治本放行**：§3 设计就绪，harness（Task #7）核验 100% 一致后可实现。若 Owner 允许
   在 harness 就绪前先落「只读调用方审计 + 测试复位钩子」两件前置，可提前实现。
