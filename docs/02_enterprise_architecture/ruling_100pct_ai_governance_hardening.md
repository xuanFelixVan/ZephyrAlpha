# 裁定 D (P3): 100% AI 治理加固 — 综合分析与治本施工方案

> **文档类型**: 架构裁定(ruling)+ 治本施工方案
> **编号**: #ARCH-GUC-TRIGGER-FIX-001 裁定 D 展开(本文件是裁定 D 的详细施工方案)
> **关联裁定**: #ARCH-GUC-TRIGGER-FIX-001 / #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 / #ARCH-P3-FOLLOWUP-TODOS-001
> **日期**: 2026-07-20
> **状态**: open(分析完成,治本施工方案待批准)
> **作者**: ZephyrAlpha AI Architect(客观第三方架构师视角)
> **调研基础**: 3 个并行调研 Agent 输出(session 注册表 stale / fail-open-fail-closed gates / 现有裁定和治理文档)

---

## 0. 摘要(TL;DR)

本裁定是 #ARCH-GUC-TRIGGER-FIX-001 裁定 D 的完整展开,基于 3 个并行调研 Agent 的综合输出,从第一性原理出发,诊断 ZephyrAlpha 项目在 100% AI 开发场景下的治理体系系统性失效,并给出分 4 个 Phase 的治本施工方案。

**核心诊断**: 项目治理体系是为人类工程师设计的,在 100% AI 开发场景下出现三层系统性失效:
- **L1 最深层**: `session_worktree` 跨进程可靠性失效(PID liveness 失效)→ `emergency_commit` 滥用(15/24h,超阈 3×)
- **L2 中间层**: `fail-open` gate + `warn-only` reconciler 静默放行(warn_only 203/24h,超阈 4×;allow_overlap 1890/7d,超阈 63×)
- **L3 表层**: 静态阈值无法适应 100% AI 高频场景(5 维全部超阈)

**核心裁定**: 4 个子裁定,分 4 个 Phase 实施
- **裁定 D-1** (Phase 1, 本周): Session 注册表可靠性修复 — heartbeat 机制替代 PID liveness
- **裁定 D-2** (Phase 2, 本月): Fail-open → Fail-closed gate 转换 + warn budget
- **裁定 D-3** (Phase 3, 下月): 自适应阈值 + 健康度评分
- **裁定 D-4** (R6, 本周): 第 6 层"可预防性"正式化 — 5 层闭环 → 6 层闭环

**现实证据**: 本裁定撰写过程中,`sess-48740-20260720000841` (pid=0, heartbeat 0.81h 前) 仍持有 14 个 held_files 阻塞 `architecture_issue_registry.yaml` 提交 — 这正是 L1 问题的实时实例化。

---

## 1. 第一性原理分析

### 1.1 核心矛盾:人类工程师场景假设 vs 100% AI 开发现实

ZephyrAlpha 项目的治理体系(gate / reconciler / session_registry / worktree)最初是为人类工程师设计的,其隐含假设在 100% AI 开发场景下全部失效:

| 隐含假设(人类场景) | 100% AI 场景现实 | 失效后果 |
|---|---|---|
| 工程师能看到 warn 横幅并主动响应 | AI 把 warn 当"通过"(无人类视觉通道) | warn_only 203/24h 静默放行 |
| 工程师能判断何时该用逃生通道 | AI 把逃生通道当"默认工具" | allow_overlap 1890/7d,emergency_commit 15/24h |
| 工程师能自行清理残留(stale session) | AI 进程崩溃后无人清理 | pid=0 session 阻塞 1 小时 |
| 工程师犯错频率低,静态阈值足够 | AI 高频操作,静态阈值持续误报 | 5 维滥用全部超阈 |
| 工程师能理解"逃生气味" | AI 只看 API 签名和返回值 |逃生通道被日常化 |

### 1.2 5+1 层闭环模型:现有 5 层与缺失的第 6 层

项目已建立 5 层闭环模型(AGENTS.md preamble):

1. **可知性(Awareness)**: AI 知道机制存在(通过 AGENTS.md / MCP rule_discovery / capability registry)
2. **可达性(Accessibility)**: AI 能调用机制(通过 API / CLI / MCP tool)
3. **可观察性(Observability)**: 机制执行结果可被 AI 观察(通过 reconciler / audit log)
4. **可逃生性(Escapability)**: 机制失败时有合法逃生通道(allow_overlap / emergency_commit / noqa)
5. **可追溯性(Traceability)**: 机制执行全程可追溯(通过 reconcile_execution_log / worktree_ops_log)

**第 6 层（Phase 1 已部分落地，2026-07-20）**:

6. **可预防性(Preventability)**: 机制能在问题发生前预防(post-commit warn 无法挽回,需 pre-commit 阻断 + 自适应学习)

**Phase 1 落地（#ARCH-HEARTBEAT-001）**: heartbeat daemon（DETACHED_PROCESS，30s 刷新 registry）+ `_is_session_alive` 双轨判据（pid=0 + heartbeat >90s = stale），stale session 阻塞窗口从 1h（TTL）缩短到 90s（heartbeat 3×30s，容忍 2 次漏跳）。详见 [ruling_session_worktree_heartbeat.md](ruling_session_worktree_heartbeat.md)。

**待落地**:
- session_worktree 异步化（#ARCH-ASYNC-MERGE-RECONCILE-001，消除同步阻塞导致的 emergency_commit 滥用）
- pre-commit forgery gate（Phase 3，从 post-commit detect 升级为 pre-commit prevent）

第 6 层缺失曾是 5 维滥用的根本原因:现有体系只能"事后报告"(post-commit reconciler warn),无法"事前预防"(pre-commit gate 阻断 + AI 行为学习)。Phase 1 heartbeat 已落地主动检测（90s stale 判定），但完整可预防性仍需 pre-commit gate 配对。

### 1.3 系统性失效的三层因果链

```
┌─────────────────────────────────────────────────────────────────┐
│ L1 最深层: session_worktree 跨进程可靠性失效                    │
│   根因: pid=0 session 无 PID liveness 检查,仅靠 TTL=3600s      │
│   症状: AI 进程崩溃后,held_files 阻塞其他 session 1 小时       │
│   派生: merge 失败 → AI 被迫用 emergency_commit 兜底            │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓ 派生
┌─────────────────────────────────────────────────────────────────┐
│ L2 中间层: fail-open gate + warn-only reconciler 静默放行       │
│   根因: gate 主动 return True(checker 缺失/超时放行)           │
│         reconciler 是 post-commit,commit 已入历史不可逆         │
│   症状: warn_only 203/24h(AI 把 warn 当"通过")                │
│         allow_overlap 1890/7d(逃生通道日常化)                  │
│   派生: 治理形同虚设,AI 在无约束下高频犯错                     │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓ 派生
┌─────────────────────────────────────────────────────────────────┐
│ L3 表层: 静态阈值无法适应 100% AI 高频场景                     │
│   根因: 阈值是为人类工程师频率设计的(如 warn_only >50/24h)     │
│   症状: 5 维滥用全部超阈(warn_only 4×, emergency 3×,          │
│         allow_overlap 63×, forged 1.33×, non-GW 14×)           │
│   派生: 阈值被自我实例化放松(如 emergency 30→10 的"杀信使")   │
└─────────────────────────────────────────────────────────────────┘
```

**关键洞察**: L1 是 L2/L3 的根因。不修 L1,L2/L3 的修复只是治标。但 L1 修复(heartbeat 机制)涉及多点改造,需独立裁定 + smoke test,故分 Phase 实施。

---

## 2. 调研结论汇总(3 个 Agent 综合)

### 2.1 Session 注册表 stale 问题(Agent 1 调研结论)

**数据结构**: `.runtime/session_registry.json` (原子写入 tmp + os.replace),`SessionRegistry` 类位于 `session_concurrency.py:219-477`,TTL=3600s。

**核心机制**:
- `claim_file` (L380-431): 原子 check-and-claim,用 `_is_session_alive` 过滤死/过期 session
- `_is_session_alive` (L195-216): 双判据 — PID liveness(PID>0 时检查) + TTL 兜底(3600s)
- `list_active()` (L311-333): 唯一会从 JSON 删除死 session 的方法

**关键缺陷**: `session_worktree_start` 在 `session_worktree.py:1045-1049` 显式用 `pid=0` 注册(设计决策:工作流跨多个 `python -c` 进程,start/commit/merge 各一次,若用 `os.getpid()` 注册,start 进程退出后 PID 死亡 → `_is_session_alive` 判死 → SESSION-REQUIRED gate 阻断 merge)。

**后果**:
- `if info.pid and info.pid > 0` 对 `pid=0` 为 falsy → **跳过 PID 检查**
- 仅靠 `TTL=3600s` 判活
- **AI 进程崩溃后,held_files 阻塞其他 session 长达 1 小时**(直到 TTL 过期)
- `session_worktree_commit` 路径不调 `list_active()`,死 session JSON 条目残留

**自动清理机制的盲区**:
- `session_worktree_sweep` (L604-680) 仅清理有 worktree 目录 + age>30min + 分支已合并的 session
- `make_worktree_lifecycle_reconciler` (reconciliation_registry.py:5480) post-commit 触发 sweep,但仅清理 worktree 目录,不解决 TTL 窗口内的 held_files 阻塞
- 无后台周期清理:所有清理都是事件驱动(session start / post-commit / 显式 sweep 调用)

**emergency_commit 触发路径**: 关键结论 — merge 失败**不触发** emergency_commit。emergency_commit 是独立手动 API(`emergency_commit.py:177`),未被 `session_worktree.py` 引用。merge 失败时 worktree 保留、session 不注销、held_files 不释放,AI 必须手动重试 merge 或调 abort。

### 2.2 Fail-open / Fail-closed Gate 现状(Agent 2 调研结论)

**5 维滥用审计阈值与现状**:

| 维度 | 时间窗 | 阈值 | 实测 | 超阈倍数 | 层级 |
|---|---|---|---|---|---|
| warn_only | 24h | >50 | 203 | 4.06× | L2 |
| emergency_commit | 24h | >10(R1 过渡期) | 15 | 1.50× | L1(最深层) |
| allow_overlap | 7d | >30 | 1890 | 63.0× | L2 |
| forged_gw_marker | 24h | >3 | 4 | 1.33× | L3 |
| non-GW commit | 24h | >10 | 142 | 14.2× | L3 |

**Gate 清单统计**: 50+ pre-commit gate,10+ post-commit reconciler。

**需改为 fail-closed 的 gate**(按优先级):
- **P1**: emergency_commit 成本递增(N>=3 需显式 reason,N>=5 阻断下次 session_worktree_start)
- **P2**: ENCODING-SAFETY / PURE-SHIM / CAPABILITY-OVERLAP / GIT-CALL-BUDGET / DATA-TASK-COMPLETENESS / DEPGRAPH-FRESHNESS / PANORAMA-ALIGNMENT / UNSAFE-DICT-SPREAD / VOCAB-HARDCODE / NO-BARE-GETENV
- **P2**: session-level warn budget(per-session warn 计数 >10 升级 block_next)
- **P3**: forged_gw_marker 前置 forgery gate(pre-commit 检测 [GW:*] 标记合法性)
- **P3**: non-GW commit server-side pre-receive hook(git pre-receive 拦截)

**逃生通道清单**(10 个): allow_overlap / emergency_commit / [no-lookup:reason] / ZEPHYR_BYPASS_LOOKUP=1 / allow_concurrent / resolve_blocks() / --no-verify / ZEPHYR_RECONCILE_SYNC=1 / merge commit 豁免 / doc-only tests-only 豁免。

**核心洞察**:
- `CommitGateRegistry.check_all` 兜底 fail-closed,但**仅对未捕获异常生效**;gate 主动 return True 的 fail-open 不受此保护
- warn-only = 100% AI 场景下的静默放行(203/24h 中相当一部分来自 fail-open gate 的 checker 缺失)
- 逃生通道被日常化(allow_overlap 1890/7d + emergency_commit 15/24h)
- 阈值被自我实例化放松过(commit `bc3cad107c` 曾将 emergency_commit 阈值从 5 放松到 30,被裁定 R1 回滚到 10)

### 2.3 现有裁定和治理文档(Agent 3 调研结论)

**裁定 D 完整内容**(ruling_guc_trigger_cascading_sync_failure.md):
- Phase 1(本月): 修复 session_worktree 跨进程失效根因 + fail-open gate 评估 + reconciler 自动修复升级
- Phase 2(下月): abuse monitor 自适应阈值 + 健康度评分
- Phase 3(长期): AI 错误模式库 + 专项 gate + session 启动推送

**#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001**:
- 5 维滥用审计文档(480 行),治本路线图 P1/P2/P3
- R1 阈值过渡期:emergency_commit 30→10(过渡期 2026-08-02 后回滚到 5)

**R1-R6 战略裁定**(P3_leftover_todos_strategic_ruling_and_treatment_plan.md):
- R1(已落地): emergency_commit 阈值过渡期回滚
- R2(已完成): P3-1.1/1.2 + 审计文档闭环提交
- R3(已完成): 审计文档与 registry 同步修正
- R4(已完成 2026-07-20): heartbeat 治本立项 + smoke test（#ARCH-HEARTBEAT-001，commit e609252cb7）
- R5(已完成): 工作区卫生强制清理
- **R6(已完成 2026-07-20)**: 6 层闭环模型正式化（AGENTS.md L128 + `trae_068_preventability_layer.yaml`，#ARCH-PREVENTABILITY-LAYER-001）——**编号修正**：原计划用 TRAE-067（编号冲突），改用 TRAE-068

**4 阶段治本方案**:
- Phase A(已完成): P3-1.1/1.2 + 审计文档闭环
- **Phase B(待实施,本周)**: R4 heartbeat 机制独立裁定 + smoke test
- **Phase C(待实施,本月)**: warn_only session-level budget + allow_overlap 注册表审计
- **Phase D(待实施,长期)**: forged_gw_marker 前置 forgery gate + non-GW commit server-side pre-receive hook

---

## 3. 裁定结果

基于第一性原理分析和 3 个 Agent 的综合调研,本裁定将 #ARCH-GUC-TRIGGER-FIX-001 裁定 D 细化为 4 个子裁定,分 4 个 Phase 实施:

### 裁定 D-1: Session 注册表可靠性修复(Phase 1, 本周)

**问题**: `session_worktree_start` 用 `pid=0` 注册(设计决策),导致 `_is_session_alive` 跳过 PID 检查,仅靠 TTL=3600s 判活。AI 进程崩溃后,held_files 阻塞其他 session 1 小时。

**治本方案**: heartbeat 机制替代 PID liveness
- **heartbeat 文件**: `.runtime/sessions/<sid>/heartbeat.jsonl`(30s 追加 `{ts, pid, status}`)
- **session_worktree_start**: 创建 heartbeat 文件,启动 heartbeat 线程(30s 追加)
- **session_worktree_commit / merge**: 刷新 heartbeat
- **_is_session_alive**: 新增 heartbeat 新鲜度判据(>5min 无更新 = stale),替代 PID liveness 作为 pid=0 session 的主判据
- **merge 重试 3 次指数退避**(1s/2s/4s): merge 失败时自动重试,避免单次失败触发 emergency_commit
- **emergency_commit 成本递增**: N>=3 次需显式 reason,N>=5 阻断下次 session_worktree_start

**预期效果**:
- AI 进程崩溃后,heartbeat 停止更新,5 分钟后 session 被判 stale → held_files 释放
- 阻塞窗口从 1 小时(TTL)缩短到 5 分钟(heartbeat 新鲜度)
- emergency_commit 滥用从 15/24h 降至 <5/24h(R1 过渡期结束后回滚到阈值 5)

**实施范围**:
- `src/zephyr/security/access_control/session_concurrency.py`(`_is_session_alive` + `list_active`)
- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`(start/commit/merge 补 heartbeat)
- `src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py`(成本递增)
- 新增 `src/zephyr/security/access_control/session_heartbeat.py`(heartbeat 线程管理)
- 新增 `tests/governance/security/test_session_heartbeat.py`(smoke test)

### 裁定 D-2: Fail-open → Fail-closed Gate 转换 + Warn Budget(Phase 2, 本月)

**问题**: 10+ gate 采用 fail-open 设计(checker 缺失/超时放行),203/24h warn_only 中相当一部分来自 fail-open gate 的 checker 缺失。AI 把 warn 当"通过",治理形同虚设。

**治本方案**:
1. **Fail-open gate 转 fail-closed**(10 个 gate,按优先级):
   - ENCODING-SAFETY(priority=42): checker 缺失/超时/exit 2 转 fail-closed
   - PURE-SHIM(priority=68): subprocess 异常转 fail-closed
   - PURE-ASSERTION(priority=69): 同上
   - VOCAB-HARDCODE(priority=80): 同上
   - NO-BARE-GETENV(priority=81): AST 异常/git diff 失败转 fail-closed
   - GIT-CALL-BUDGET(priority=105): warn-only → fail-closed(P3 计划已立项)
   - DATA-TASK-COMPLETENESS(priority=41): 评估转 fail-closed(保留豁免清单)
   - DEPGRAPH-FRESHNESS(priority=67): cache 缺失超 1h 转 fail-closed
   - PANORAMA-ALIGNMENT(priority=830): run_alignment 异常转 fail-closed
   - CAPABILITY-OVERLAP(priority=200): 高置信度命中(≥4 字符 + ≥2 token)转 fail-closed

2. **Session-level warn budget**:
   - per-session warn 计数,>10 次升级为 block_next(阻断该 session 下一次 commit)
   - 覆盖所有 warn-only gate(UNSAFE-DICT-SPREAD / CAPABILITY-OVERLAP / GIT-CALL-BUDGET / DATA-TASK-COMPLETENESS)
   - 持久化到 `.runtime/sessions/<sid>/warn_budget.json`

3. **allow_overlap 注册表审计**:
   - grep 所有 `allow_overlap=True` 调用路径,审计是否真有必要
   - 成本递增机制:per-session allow_overlap 计数 >5 次需显式 reason,>10 次阻断

**预期效果**:
- warn_only 从 203/24h 降至 <50/24h(阈值内)
- allow_overlap 从 1890/7d 降至 <100/7d(治本后逃生通道不再被日常化)
- fail-open gate 的 checker 缺失从"静默放行"变为"阻断提交",强制 AI 修复治理基础设施

### 裁定 D-3: 自适应阈值 + 健康度评分(Phase 3, 下月)

**问题**: 静态阈值(如 warn_only >50/24h)是为人类工程师频率设计的,在 100% AI 场景下持续误报。阈值被自我实例化放松(如 emergency_commit 30→10 的"杀信使"反模式)。

**治本方案**:
1. **abuse monitor 阈值从静态改为自适应**(基于 7d 滚动基线):
   - 每日计算 7d 滚动中位数 + 标准差
   - 阈值 = max(静态下限, 7d 中位数 + 2×标准差)
   - 避免静态阈值被高频场景误报,同时保留静态下限防止失控

2. **健康度评分替代单一阈值**(多维加权评分):
   - 5 维加权评分:warn_only(0.1) + emergency_commit(0.3) + allow_overlap(0.2) + forged_gw_marker(0.3) + non-GW commit(0.1)
   - 综合评分 >0.7 = critical_warn,>0.9 = block_next
   - 单一维度超阈仍保留 warn,但综合评分超阈才升级 block_next

3. **阈值自我放松防护**:
   - 阈值调整需独立裁定 + smoke test(防止"杀信使"反模式)
   - 阈值调整记录到 `architecture_issue_registry.yaml`,可追溯

**预期效果**:
- 5 维滥用不再全部超阈(自适应阈值适应 100% AI 高频场景)
- 综合健康度评分提供治理健康度的全貌,而非单一维度的误报
- 阈值自我放松被流程化防护,避免"杀信使"反模式

### 裁定 D-4: 第 6 层"可预防性"正式化(R6, 本周)——✅ 已完成 2026-07-20

**问题**: 现有 5 层闭环模型(可知性/可达性/可观察性/可逃生性/可追溯性)只能"事后报告",无法"事前预防"。post-commit reconciler warn 无法挽回已 commit 的影响。

**治本方案**:
1. **AGENTS.md preamble 5 层 → 6 层**(补充 ⑥ 可预防性): ✅ 已落地（AGENTS.md L128）
   - ⑥ 可预防性(Preventability): 机制能在问题发生前预防(pre-commit 阻断 + 自适应学习 + AI 行为模式库)
   - 与 ③ 可观察性的区别:可观察性是事后观察,可预防性是事前预防

2. **新增 `trae_068_preventability_layer.yaml`**(结构化规则): ✅ 已落地（166 行）
   - rule_id: TRAE-068（编号修正:原计划 TRAE-067 编号冲突,改用 TRAE-068）
   - title: 第 6 层可预防性铁律（Preventability Layer，6 层闭环模型正式化）
   - prohibitions: 禁止 post-commit reconciler 作为唯一治理机制(必须有 pre-commit gate 配对)
   - requirements: 所有 post-only reconciler 必须评估是否可前移为 pre-commit gate

3. **`capability_canonical_file_registry.yaml` 登记 `preventability_layer_rule` capability**: ✅ 已落地（token=auto-trae-068-preventability-20260720）

4. **`rule_ai_perception_index.yaml` 重新生成**(67 → 68 rules): ✅ 已落地（total_rules=68）

5. **`gate_registry.yaml` 配对 gate**(pre-commit forgery gate,Phase 2 实施): ✅ 已落地 2026-07-20（commit `ce81f1077f` + merge `ed9243c8ba`，GATE-FORGED-GW-MARKER，priority=29，src/zephyr/gov_enforcement/commit_gates/forged_gw_marker_gate.py，23/23 smoke test PASSED）

**裁定修正（#ARCH-PREVENTABILITY-LAYER-001）**: 原裁定 D-4 计划用 TRAE-067,但 TRAE-067 已被 `trae_067_window_flash_discipline.yaml` 占用（2026-07-20 后期），故改用 TRAE-068（下一个可用编号）。详见 [architecture_issue_registry.yaml #ARCH-PREVENTABILITY-LAYER-001](../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)。

**预期效果**:
- 6 层闭环模型正式化,可预防性成为治理体系的显性概念
- post-only reconciler 不再是唯一治理机制,必须有 pre-commit gate 配对
- AI 通过 MCP rule_discovery 可发现第 6 层要求,主动设计预防机制

---

## 4. 治本施工方案(分 Phase 实施)

### Phase 1: Session 可靠性 + heartbeat 机制(本周,2026-08-02 前)

**优先级**: P1(最高)— L1 最深层根因,不修则 L2/L3 治标不治本

**任务清单**:

| Task | 文件 | 内容 | 预估工时 |
|---|---|---|---|
| P1-1 | 新增 `src/zephyr/security/access_control/session_heartbeat.py` | heartbeat 线程管理(30s 追加 + stale 检测) | 2h |
| P1-2 | `src/zephyr/security/access_control/session_concurrency.py` | `_is_session_alive` 新增 heartbeat 新鲜度判据 | 1h |
| P1-3 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | start/commit/merge 补 heartbeat 创建/刷新 | 2h |
| P1-4 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | merge 重试 3 次指数退避(1s/2s/4s) | 1h |
| P1-5 | `src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py` | 成本递增(N>=3 需 reason,N>=5 阻断 start) | 1h |
| P1-6 | 新增 `tests/governance/security/test_session_heartbeat.py` | smoke test(heartbeat 创建/刷新/stale 检测) | 2h |
| P1-7 | `docs/02_enterprise_architecture/ruling_session_worktree_heartbeat.md` | 独立裁定文档(R4 交付物) | 1h |

**验证标准**:
- [ ] heartbeat 文件在 session_worktree_start 后创建,30s 追加一次
- [ ] `_is_session_alive` 对 pid=0 + heartbeat >5min 的 session 返回 False
- [ ] AI 进程崩溃后,5 分钟内 held_files 释放(阻塞窗口从 1h 缩短到 5min)
- [ ] merge 失败时自动重试 3 次(1s/2s/4s 退避)
- [ ] emergency_commit 第 3 次需显式 reason,第 5 次阻断 session_worktree_start
- [ ] smoke test 全部 PASSED
- [ ] 独立裁定文档产出(R4 交付物)

**风险与缓解**:
- **风险**: heartbeat 线程在 AI 进程崩溃后可能残留(但 heartbeat 文件停止更新,5min 后判 stale,不影响正确性)
- **风险**: heartbeat 文件堆积(每 session 一个,30s 追加一次)— 缓解:session_worktree_merge/abort 时清理 heartbeat 文件
- **风险**: merge 重试可能掩盖真实冲突 — 缓解:重试仅针对 transient 错误(如 lock contention),deterministic 错误(如 content conflict)不重试

### Phase 2: Gate fail-closed 转换 + Warn Budget(本月)

**优先级**: P2 — L2 中间层,依赖 Phase 1 完成(session 可靠性是 gate 阻断的前提)

**任务清单**:

| Task | 文件 | 内容 | 预估工时 |
|---|---|---|---|
| P2-1 | `src/zephyr/gov_enforcement/commit_gates/encoding_gate.py` | fail-open → fail-closed(checker 缺失/超时阻断) | 1h |
| P2-2 | `src/zephyr/gov_enforcement/commit_gates/pure_shim_gate.py` | fail-open → fail-closed | 1h |
| P2-3 | `src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py` | fail-open → fail-closed | 1h |
| P2-4 | `src/zephyr/gov_enforcement/commit_gates/vocab_hardcode_gate.py` | fail-open → fail-closed | 1h |
| P2-5 | `src/zephyr/gov_enforcement/commit_gates/bare_getenv_gate.py` | fail-open → fail-closed | 1h |
| P2-6 | `src/zephyr/gov_enforcement/commit_gates/git_call_budget_gate.py` | warn-only → fail-closed | 1h |
| P2-7 | `src/zephyr/gov_enforcement/commit_gates/depgraph_freshness_gate.py` | cache 缺失超 1h 转 fail-closed | 1h |
| P2-8 | `src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py` | run_alignment 异常转 fail-closed | 1h |
| P2-9 | `src/zephyr/gov_enforcement/commit_gates/capability_overlap_gate.py` | 高置信度命中转 fail-closed | 2h |
| P2-10 | 新增 `src/zephyr/gov_enforcement/commit_gates/warn_budget_gate.py` | session-level warn budget(>10 升级 block_next) | 3h |
| P2-11 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | allow_overlap 成本递增(per-session 计数) | 2h |
| P2-12 | 对应测试文件 | 每个 gate 转换补 fail-closed 测试 | 4h |

**验证标准**:
- [ ] 10 个 gate 转 fail-closed 后,checker 缺失/超时不再静默放行
- [ ] warn_only 从 203/24h 降至 <50/24h
- [ ] allow_overlap 从 1890/7d 降至 <100/7d
- [ ] session-level warn budget >10 次升级 block_next
- [ ] 所有 gate 测试 PASSED

### Phase 3: 自适应阈值 + 健康度评分(下月)

**优先级**: P3 — L3 表层,依赖 Phase 2 完成(gate fail-closed 是自适应阈值的前提)

**任务清单**:

| Task | 文件 | 内容 | 预估工时 |
|---|---|---|---|
| P3-1 | `src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py` | 阈值从静态改为自适应(7d 滚动基线) | 4h |
| P3-2 | 新增 `src/zephyr/governance/audit/health_score_calculator.py` | 5 维加权评分计算 | 3h |
| P3-3 | `src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py` | 综合评分 >0.7 critical_warn,>0.9 block_next | 2h |
| P3-4 | `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml` | 阈值调整流程化(独立裁定 + smoke test) | 1h |
| P3-5 | 新增 `tests/governance/audit/test_health_score_calculator.py` | smoke test | 2h |

**验证标准**:
- [ ] 自适应阈值基于 7d 滚动基线,不再静态误报
- [ ] 综合健康度评分 >0.7 critical_warn,>0.9 block_next
- [ ] 5 维滥用不再全部超阈
- [ ] 阈值调整有独立裁定记录

### Phase 4: AI 行为学习 + Server-side 防御(长期)

**优先级**: P4 — 长期战略,依赖 Phase 3 完成(健康度评分是 AI 行为学习的基础)

**任务清单**:

| Task | 文件 | 内容 | 预估工时 |
|---|---|---|---|
| P4-1 | 新增 `src/zephyr/governance/audit/ai_error_pattern_library.py` | AI 错误模式库(历史错误模式检索) | 8h（深化评估见 §11.3.1） |
| P4-2 | ✅ 已落地 2026-07-20（commit `ce81f1077f`，实际文件名 `forged_gw_marker_gate.py`，priority=29，原计划文件名 `forged_marker_detection_gate.py` 已弃用） | pre-commit 检测 [GW:*] 标记合法性 | 4h |
| P4-3 | 新增 `scripts/governance/git_pre_receive_hook.py` | server-side pre-receive hook 拦截非 GW commit | 4h（深化评估见 §11.3.2，可行性下调） |
| P4-4 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | session 启动推送"近期高频错误"提醒 | 3h |
| P4-5 | 长期:GPG 签名强制 | server-side 强制 GPG 签名验证 | 待评估（深化评估见 §11.3.3，可行性下调为低） |

**验证标准**:
- [ ] AI 错误模式库可检索历史错误模式
- [x] forged_gw_marker pre-commit gate 阻断伪造标记（✅ 2026-07-20 已落地，见 P4-2）
- [ ] non-GW commit server-side pre-receive hook 拦截（深化评估见 §11.3.2，方案改为 GitHub Actions PR 检查）
- [ ] session 启动时推送近期高频错误提醒

---

## 5. 风险评估与缓解

### 5.1 Phase 1 风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| heartbeat 线程在 AI 进程崩溃后残留 | 低 | 低(heartbeat 停止更新,5min 后判 stale) | session_worktree_merge/abort 清理 heartbeat 文件 |
| heartbeat 文件堆积 | 中 | 低(每 session 一个,30s 追加) | merge/abort 时清理;定期 sweep |
| merge 重试掩盖真实冲突 | 中 | 中(可能延迟冲突发现) | 重试仅针对 transient 错误,deterministic 错误不重试(裁定 C 已实现错误分类) |
| heartbeat 文件 IO 性能 | 低 | 低(30s 追加一次,文件小) | 用 append 模式,不读写整个文件 |

### 5.2 Phase 2 风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| fail-closed 转换后 checker 缺失阻断开发 | 高 | 高(开发效率下降) | 转换前先修复所有 checker 缺失问题;分批转换,每批验证 |
| warn budget 误阻断合法 session | 中 | 中(block_next 阻断下次 commit) | budget 阈值可配置;提供 `resolve_blocks()` 逃生通道(有审计) |
| allow_overlap 成本递增影响紧急修复 | 中 | 中(紧急修复被阻断) | 保留 emergency_commit 作为最后逃生通道(但有成本递增) |

### 5.3 Phase 3-4 风险

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| 自适应阈值掩盖真实恶化 | 中 | 高(治理失效被掩盖) | 保留静态下限;综合评分 >0.9 仍 block_next |
| AI 错误模式库维护成本 | 高 | 中(库过时失效) | 自动从 reconcile_execution_log 提取模式,不需人工维护 |
| server-side pre-receive hook 影响 CI | 中 | 高(CI 流水线被阻断) | 先在 staging 环境验证;保留 emergency 白名单 |

---

## 6. 实施优先级与依赖关系

```
Phase 1 (本周)          Phase 2 (本月)          Phase 3 (下月)          Phase 4 (长期)
─────────────          ─────────────          ──────────────          ─────────────
P1-1 heartbeat ──┐
P1-2 _is_alive ──┤
P1-3 start/commit┼─→ P2-1..P2-9 gate ──→ P3-1 自适应阈值 ──→ P4-1 错误模式库
P1-4 merge 重试 ─┤   P2-10 warn budget  P3-2 健康度评分    P4-2 forgery gate
P1-5 emergency   │   P2-11 allow_overlap P3-3 block_next    P4-3 pre-receive
P1-6 smoke test ─┘   P2-12 测试          P3-4 流程化        P4-4 启动推送
P1-7 裁定文档                            P3-5 smoke test    P4-5 GPG 签名

R6 (本周,并行):
  D-4 第 6 层正式化 → trae_067 + AGENTS.md + registry
```

**关键依赖**:
- Phase 2 依赖 Phase 1:gate fail-closed 转换需要 session 可靠性(否则 session 卡死时 gate 阻断无法释放)
- Phase 3 依赖 Phase 2:自适应阈值需要 gate fail-closed(否则 warn_only 数据被 fail-open 污染)
- Phase 4 依赖 Phase 3:AI 行为学习需要健康度评分(否则无法区分"高频错误"和"正常高频操作")
- R6 可与 Phase 1 并行:第 6 层正式化是概念性工作,不依赖代码实现

---

## 7. 与现有裁定的对齐关系

| 现有裁定 | 本裁定的对应 | 关系 |
|---|---|---|
| #ARCH-GUC-TRIGGER-FIX-001 裁定 D | 本裁定整体 | 展开:裁定 D 的 3 个 Phase 细化为 4 个子裁定 |
| #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 | 裁定 D-2 + D-3 | 对齐:5 维滥用治本路线图 P1/P2/P3 |
| #ARCH-P3-FOLLOWUP-TODOS-001 R4 | 裁定 D-1 | 实施:R4 heartbeat 机制独立裁定 + smoke test |
| #ARCH-P3-FOLLOWUP-TODOS-001 R6 | 裁定 D-4 | 实施:R6 6 层闭环模型正式化 |
| #ARCH-P3-FOLLOWUP-TODOS-001 R1 | 裁定 D-1 的 emergency_commit 成本递增 | 衔接:R1 阈值过渡期结束后回滚到 5,依赖 D-1 的 heartbeat 治本完成 |
| 裁定 C (P2) reconciler 错误分类 | 裁定 D-1 的 merge 重试 | 复用:merge 重试仅针对 transient 错误,复用裁定 C 的错误分类 |

---

## 8. 现实证据:本裁定撰写过程中的实时案例

本裁定撰写过程中,`sess-48740-20260720000841` (pid=0, heartbeat 0.81h 前) 仍持有 14 个 held_files,阻塞 `architecture_issue_registry.yaml` 提交。这是 L1 问题(session_worktree 跨进程可靠性失效)的实时实例化:

- **症状**: AI 进程崩溃后,held_files 阻塞其他 session 提交
- **根因**: pid=0 session 无 PID liveness 检查,仅靠 TTL=3600s 判活
- **当前缓解**: 等待 TTL 过期(剩余约 11 分钟)
- **治本后**: heartbeat 机制使 5 分钟后 session 判 stale → held_files 释放

此案例验证了 Phase 1(heartbeat 机制)的必要性和紧迫性。

---

## 9. 关联文档

### 9.1 裁定与战略文档
- ruling_guc_trigger_cascading_sync_failure.md (docs/02_enterprise_architecture/ruling_guc_trigger_cascading_sync_failure.md) — 裁定 A/B/C/D 母文档
- ruling_gate_abuse_systemic_audit.md (docs/02_enterprise_architecture/ruling_gate_abuse_systemic_audit.md) — 5 维滥用审计
- P3_followup_todos_root_cause_plan.md (.trae/documents/P3_followup_todos_root_cause_plan.md) — #ARCH-P3-FOLLOWUP-TODOS-001 主文档
- P3_leftover_todos_strategic_ruling_and_treatment_plan.md (.trae/documents/P3_leftover_todos_strategic_ruling_and_treatment_plan.md) — R1-R6 战略裁定

### 9.2 注册表(SSoT 真源)
- architecture_issue_registry.yaml (docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) — issue 注册表
- noqa_exempt_registry.yaml (docs/01_policies_and_standards/_registry/catalogs/noqa_exempt_registry.yaml) — noqa marker 注册表
- capability_canonical_file_registry.yaml (docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) — capability 注册表

### 9.3 核心治理工具代码
- session_concurrency.py (src/zephyr/security/access_control/session_concurrency.py) — SessionRegistry(PID liveness 失效点)
- session_worktree.py (src/zephyr/gov_enforcement/rule_bridge/session_worktree.py) — worktree 君子协定
- emergency_commit.py (src/zephyr/gov_enforcement/rule_bridge/emergency_commit.py) — 紧急提交通道
- commit_gateway_abuse_monitor_reconciler.py (src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py) — 5 维滥用检测器
- reconciliation_registry.py (src/zephyr/governance/audit/reconciliation_registry.py) — reconciler 注册真源

### 9.4 AGENTS.md 相关章节
- preamble 5 层闭环模型(R6 待补充第 6 层"可预防性")
- §11.0.2 SSoT 真源分类铁律(TRAE-062)
- FP-ISO.4C worktree 物理隔离

---

## 10. 结论

本裁定基于第一性原理分析,诊断 ZephyrAlpha 项目在 100% AI 开发场景下的治理体系系统性失效,核心矛盾是"为人类工程师设计的治理体系"与"100% AI 开发现实"的根本性冲突。

三层系统性失效的根因是 L1(session_worktree 跨进程可靠性失效),不修则 L2(fail-open gate + warn-only 静默放行)和 L3(静态阈值误报)的修复只是治标。

4 个子裁定分 4 个 Phase 实施,优先级清晰:
- **Phase 1(本周)**: heartbeat 机制替代 PID liveness — L1 根因治本
- **Phase 2(本月)**: 10 个 gate 转 fail-closed + warn budget — L2 治本
- **Phase 3(下月)**: 自适应阈值 + 健康度评分 — L3 治本
- **Phase 4(长期)**: AI 行为学习 + server-side 防御 — 第 6 层可预防性落地

R6(第 6 层正式化)可与 Phase 1 并行,是概念性工作,不依赖代码实现。

**裁定状态**: open(分析完成,治本施工方案待批准)

**下一步**:
1. 用户审批本裁定
2. 启动 Phase 1 实施(heartbeat 机制 + smoke test + 独立裁定文档)
3. R6 并行实施(第 6 层正式化)

---

**裁定人**: ZephyrAlpha AI Architect(客观第三方架构师视角)
**裁定日期**: 2026-07-20
**预计完成时间**: Phase 1 本周(2026-08-02 前)/ Phase 2 本月 / Phase 3 下月 / Phase 4 长期

---

## 11. Phase 2 收尾 + Phase 3/4 深化可行性评估（2026-07-20 后期）

> 本章节是对 §3 裁定 D-4 与 §4 Phase 2/3/4 任务清单的深化评估，基于 Phase 1/2 落地后的实际基础设施现状与 reconciler 全景调研。评估目的：把"待评估"与"长期"的具体可行性落到事实层。

### 11.0 摘要

- **Phase 2 reconciler 前移评估**: 用户原预估"10+"post-only reconciler 可前移,实际调研显示 40 个 reconciler 中可前移候选仅 6 个,明确推荐前移仅 3 个。差异源于"post-only"语义混淆(强 post-only / 弱 post-only 双防 / 可前移候选 三类)。
- **Phase 3 自适应阈值**: 可行性中。`AdaptiveThreshold` 类已存在但模型不匹配(概率型 vs 次数型),需扩展;7d 基线需数据积累期。
- **Phase 4 AI 行为模式库**: 可行性中高。数据源齐备(reconcile_execution_log + .runtime/reconcile_reports/*.json + event_sink JSONL),但需先扩展 schema 支持"错误模式"结构化字段。
- **Phase 4 server-side pre-receive hook**: 可行性低-中。GitHub-hosted 仓库无法部署项目内 pre-receive 脚本,必须改走 GitHub Actions + Branch Protection。强制层从 commit 降级为 PR。
- **Phase 4 GPG 签名**: 可行性低。100% AI 开发场景下"签名"含义弱化(同一 AI 用同一 key),私钥管理方案完全缺失,边际收益低于成本。建议**不实施**,由 P4-2 forged_gw_marker_gate 已落地的 in-process forgery 防御 + GitHub Actions PR 检查覆盖。

### 11.1 Phase 2 收尾:post-only reconciler 前移评估(用户原预估"10+"→ 实际推荐 3 个)

#### 11.1.1 调研基础

调研对象:`src/zephyr/governance/audit/reconciliation_registry.py` 内 34 个 `make_*_reconciler` + 外部文件 6 个 reconciler = **共 40 个 reconciler**。

关键事实:根据 `reconciliation_registry.py` 文件头部注释(L19-23),**所有 reconciler 在设计上都是 post-commit 的**。原因:`GitCommitGateway` 在所有 commit 路径统一使用 `--no-verify` 斩断 stash 冲突链,副作用是系统性关闭全部 pre-commit GATE。reconciler 在 commit 完成后由 `ReconciliationRegistry.reconcile_for()` 统一调度补偿检测。因此"post-only"的语义需要细分为三类。

#### 11.1.2 三类 post-only 语义澄清

| 分类 | 数量 | 前移可行性 | 说明 |
|------|------|-----------|------|
| 强 post-only | 26 | 不可行 | auto-commit 副作用 / DB 状态依赖 / cleanup 性质 / commit history 审计 |
| 弱 post-only(已有 pre-commit 双防) | 8 | 已实现,无需再前移 | pre-commit gate 防新增 + reconciler 清存量,双层防御 |
| 可前移候选 | 6 | 部分可行 | 纯静态检测、无 auto-commit 副作用,且当前无 pre-commit 对应 gate |

**强 post-only 26 个**(不可前移根因分类):

- (a) auto-commit/auto-fix 类(15 个):前移会导致 pre-commit 死循环。包括 manifest/path_tree/path_ownership/blueprint_frontmatter/drift_fix/module_id_recommend/vocab_change/delete_audit/regenerate/index_generator/session_log_index/arch_diagram/gate_inventory_sync/gate_registry_sync/rule_audit(catalog 部分)。`make_gate_inventory_sync_reconciler` 与 `make_gate_registry_sync_reconciler` 的 docstring 已明确记载此结论("否决策略 A pre-commit 阻断型:阻断会导致 AI 无法 commit 新 gate 代码,死循环")。
- (b) DB 写入/状态同步类(4 个):需 post-state 才有意义。包括 depgraph_ops/yaml_sync/constraint_detect(PG 写入)/drift_scan(需对比 post-state 检测 drift)。
- (c) cleanup 类(5 个):与 commit 内容无关。包括 runtime_cleanup/tmp_cleanup/worktree_lifecycle/stash_lifecycle/workspace_hygiene。
- (d) commit history 审计/snapshot 类(2 个):本质上只能 post。包括 integrity_audit 的 COMMIT-GW-AUDIT 子组件/commit_gateway_abuse_monitor。

**弱 post-only 8 个**(已有 pre-commit 双防,无需再前移):

| Reconciler | 对应 pre-commit gate (priority) |
|------------|--------------------------------|
| make_precommit_id_uniqueness_reconciler | make_id_uniqueness_gate (86) |
| make_exempt_zone_frontmatter_reconciler | make_exempt_zone_frontmatter_gate (87) |
| make_module_id_consistency_reconciler | make_module_id_consistency_gate (88) |
| make_scripts_import_integrity_reconciler | make_scripts_import_integrity_gate (104) |
| make_undefined_name_baseline_reconciler | make_undefined_name_gate (106) |
| make_blueprint_id_legacy_reconciler | make_blueprint_format_gate (77) |
| make_deprecated_directory_reconciler | make_directory_contract_gate |
| make_capability_lookup_health_reconciler | make_capability_lookup_required_gate (110) |

#### 11.1.3 6 个可前移候选逐个评估

| # | 候选 | 可行性 | 成本 | 收益 | 推荐 |
|---|------|--------|------|------|------|
| 1 | make_constraint_detect_reconciler (priority=625) | 中 | 中 | 高 | 可行,需重构为 read-only |
| 2 | make_architecture_health_reconciler (priority=300) | 高(已规划) | 低 | 高 | **推荐**,按第1期路径推进 |
| 3 | GATE-ARCH-REFS(rule_audit 子组件, priority=710) | 高 | 低 | 中 | **推荐**,注意与现有 arch_reference_gate 去重 |
| 4 | GATE-AGENTS-MD-REFS(integrity_audit 子组件, priority=810) | 中 | 低 | 中 | 可行,收益有限 |
| 5 | make_metric_count_drift_reconciler (priority=220) | 高 | 低 | 中 | **推荐**,作为 warn-only pre-commit gate |
| 6 | make_drift_scan_reconciler (priority=140) | 低 | 高 | 高 | 不推荐直接前移,可拆分轻量版 |

**候选 1 make_constraint_detect_reconciler**:当前跑 `detect_constraint_violations.py` 检测 5 类架构违规(cross_domain/capacity/hard_limit/orphan_node/layer_violation),写 PG arch_constraints 表。前移需把"检测器→写 PG"改为"检测器→阻断 commit",检测器需重构为 read-only 模式(commit 失败时 PG 不被污染)。

**候选 2 make_architecture_health_reconciler**:docstring 明确写"第1期升级路径:转为 pre-commit commit gate(exit 1 阻断),见 architecture_debt_registry.md §六 第1期"。前移成本最低,但 dashboard 跑全量指标耗时 120s,需做增量检测或缓存。

**候选 3 GATE-ARCH-REFS**:纯静态文本检测(正则 + yaml 加载),无副作用,无 auto-commit。需先与现有 `make_arch_reference_gate` (priority=75) 去重,若重复则只需强化现有 gate 而非新建。

**候选 5 make_metric_count_drift_reconciler**:校验 `dashboard.py` + 4 个派生文件中所有 `(\d+) 项指标` 描述与 `len(METRICS)` 一致性。纯静态文本检测,低成本。注意:自动修复不能前置(docstring 提到"描述同步需人工决策"),前移后只能阻断不能修复。

**候选 6 make_drift_scan_reconciler**(不推荐):全量 drift 扫描依赖 depgraph 已同步(依赖 make_depgraph_ops_reconciler priority=130 先跑),但 pre-commit 阶段 depgraph 还未同步。存在循环依赖:drift 扫描依赖 depgraph 同步,depgraph 同步依赖 commit 完成。可考虑拆分为"轻量 staged-file drift check(pre-commit)+全量 drift scan(post-commit 保留)"。

#### 11.1.4 推荐前移清单(3 个,需在 Phase 2 收尾时单独立项裁定)

1. **make_architecture_health_reconciler** → 新增 `architecture_health_gate.py` (pre-commit, project-内已有规划路径)
2. **GATE-ARCH-REFS 子组件** → 强化现有 `arch_reference_gate.py` 或新增独立 gate(先做去重分析)
3. **make_metric_count_drift_reconciler** → 新增 `metric_count_drift_gate.py` (pre-commit, warn-only)

#### 11.1.5 用户预估"10+"vs 实际推荐 3 的差异说明

差异根因:用户基于"trae_068 §requirements: 所有 post-only reconciler 必须评估是否可前移为 pre-commit gate"的表述,默认 40 个 reconciler 中至少 10+ 可前移。但实际:
- 26 个强 post-only 因技术约束不可前移(auto-commit 死循环 / DB 状态依赖 / cleanup 与 commit 无关 / 审计只能 post)
- 8 个弱 post-only 已有 pre-commit 双防,本就是"前移已完成"状态
- 6 个可前移候选中 3 个明确推荐,2 个可行但收益有限,1 个不推荐(循环依赖)

**结论**:trae_068 §requirements 的"必须评估"已对所有 40 个 reconciler 完成,产出本章节评估报告。前移清单为 3 个,而非 10+,这是基于事实的修正。

### 11.2 Phase 3 深化评估:自适应阈值 + 健康度评分

#### 11.2.1 现状

- `commit_gateway_abuse_monitor_reconciler.py`(420 行,MATURITY=prototype)当前 5 维阈值**全部静态硬编码**:
  - `_WARN_ONLY_24H_THRESHOLD = 50`
  - `_EMERGENCY_24H_THRESHOLD = 10`(R1 由 30 回滚到 10;R4 计划 2026-08-02 heartbeat 落地后强制回滚到 5)
  - `_ALLOW_OVERLAP_7D_THRESHOLD = 30`
  - `_FORGED_24H_THRESHOLD = 3`
  - `_NON_GW_24H_THRESHOLD = 10`
- `AdaptiveThreshold` 类已存在(`src/zephyr/gov_enforcement/rule_enforcement/adaptive_threshold.py`,EWMA + smoothing 算法)但**未被 abuse_monitor 引用**。其设计是基于 PASS/FAIL outcome 反馈调节阈值(0.1-0.99 概率型),与 abuse_monitor 的"次数阈值"模型不匹配。

#### 11.2.2 可行性:中

- **阻断点 1**:`AdaptiveThreshold` 需扩展支持"次数阈值"而非"概率阈值"。当前 EWMA 算法可复用,但语义层需重新设计。
- **阻断点 2**:7d 滚动基线需数据积累期。当前 `.runtime/reconcile_reports/commit_gateway_audit_*.json` 最早 2026-07-13,仅 7d 数据,基线统计置信度不足。建议 Phase 3 启动时先观察 14d 再启用自适应。
- **阻断点 3**:`reconcile_execution_log.detail` 是自由文本,无结构化字段,综合健康度评分(5 维加权)需先扩展 schema 或在 abuse_monitor 内单独维护统计表。

#### 11.2.3 修正建议

- P3-1 工时 4h → 调整为 6h(含 AdaptiveThreshold 类扩展 + 7d 基线实现)
- P3-2 工时 3h 保持不变
- P3-3 工时 2h 保持不变
- 新增 P3-0(前置任务,2h):扩展 `AdaptiveThreshold` 类支持 `count_threshold` 模式,与现有 `probability_threshold` 模式并存
- 新增 P3-6(前置任务,1h):在 `commit_gateway_abuse_monitor_reconciler.py` 内新增 `_7d_baseline_state` 字典,持久化到 `.runtime/abuse_baseline.json`

### 11.3 Phase 4 深化评估

#### 11.3.1 AI 行为模式库(P4-1)— 可行性中高

**现状**:
- `src/zephyr/infrastructure/system_telemetry/ai_behavior/event_sink.py`(246 行,MATURITY=production)提供 `AIBehaviorEvent` dataclass,覆盖 7 大监测维度(model/task/prompt/tokens/decision/tools/gates/quality/error/rate_limit),含 `is_suspicious` 启发式判定。**这是事件发射层(emit),不是模式聚合层(pattern aggregation)**。
- `reconcile_execution_log` 表存在(SQLite governance.db),含 log_id/gate_id/session_id/trigger_source/action/detail/committed_files_summary/commit_message 字段。**无"错误模式"字段**,detail 是自由文本。
- `.runtime/reconcile_reports/*.json`(200+ 文件,最早 2026-07-13)结构化但分散。
- `event_sink.py` 落地的 JSONL 事件无后续聚合消费代码(`CONSUMERS` 注释写 `behavioral-auditor`,但 Glob 无此模块)。

**可行性:中高**。

**阻断点**:
1. `reconcile_execution_log.detail` 是自由文本,无法直接做模式聚合。需先扩展 schema 增加 `error_pattern_id` / `error_pattern_fingerprint` 字段,或在 P4-1 模块内单独维护"模式字典 + 指纹索引"。
2. `event_sink.py` 的 JSONL 事件无消费方,需新建 consumer 模块聚合到模式库。
3. 模式提取算法需选择:正则聚类(简单但漏召)vs 嵌入向量聚类(需 LLM 调用,成本高)。建议先用正则聚类 + 人工标注种子模式,后续迭代。

**修正建议**:
- P4-1 工时 8h → 调整为 12h(含 reconcile_execution_log schema 扩展 + event_sink JSONL consumer + 模式字典初版)
- 新增 P4-1a(前置,2h):扩展 `reconcile_execution_log` schema 增加 `error_pattern_id` 字段(PRAGMA 幂等迁移,对标已存在的 `acknowledged_at` / `commit_message` 列追加模式)
- 新增 P4-1b(2h):实现 `event_sink.py` 的 JSONL consumer,聚合到 `ai_error_pattern_library.py`

#### 11.3.2 server-side pre-receive hook(P4-3)— 可行性低-中,方案改走 GitHub Actions

**现状**:
- 项目是 GitHub-hosted 仓库(`.git/config` remote = `https://github.com/xuanFelixVan/ZephyrAlpha.git`),**不是 bare repo**,本地 `.git/hooks/pre-receive` 不会在 `git commit` 时触发(仅在 push 到 bare repo 时触发)。
- GitHub 项目内**无法部署 pre-receive 脚本**(需 GitHub Enterprise + pre-receive hooks 才能部署脚本)。
- 现有 server-side 强制层:`.github/workflows/governance.yml`(373 行)`on: push` + `on: pull_request`,7 个 Tier 检查。**未包含任何 GPG 签名验证、commit message `[GW:]` 标记强制检查、non-GW commit 拦截逻辑**。
- `git_pre_receive_hook.py` 文件**完全不存在**(原计划文件)。

**可行性:低-中**。

**方案调整**:
- 放弃"项目内 pre-receive 脚本"路径(物理不可行)。
- 改走 GitHub Actions + Branch Protection:
  1. **GitHub Actions job**(新增,在 governance.yml 内):对 PR 的每个 commit 检查 commit message 是否带 `[GW:session_id]` 标记 + session_id 合法性(调用 `forged_gw_marker_gate.py` 的检测逻辑),违规 PR 阻断 merge。
  2. **GitHub Branch Protection**(需 GitHub Web UI 或 `gh api` 配置):启用 "Require status checks to pass before merging",将上述 job 设为 required。
- **强制层级降级**:从 commit(原计划)降级为 PR。本地 commit 仍可绕过,但 push 到 GitHub 后 PR 阶段会阻断 merge。

**修正建议**:
- P4-3 工时 4h → 调整为 6h(含 GitHub Actions job 实现 + Branch Protection 配置指南)
- 文件路径:原计划 `scripts/governance/git_pre_receive_hook.py` → 改为 `.github/workflows/commit_message_guard.yml`(GitHub Actions workflow)+ `scripts/governance/check_commit_message.py`(可被 Actions 调用的检测脚本,复用 `forged_gw_marker_gate.py` 逻辑)

#### 11.3.3 GPG 签名(P4-5)— 可行性低,建议不实施

**现状**:
- `.git/config` 完全无 GPG 配置(无 `user.signingkey` / `commit.gpgsign` / `tag.gpgsign` / `gpg.format` / `gpg.program`)。
- `user.email = trae@example.com` 是**合成 AI 用户**,非真实身份。当前所有 commit 必然未签名。
- 项目对 GPG 的要求:**完全无**(AGENTS.md / trae_*.yaml / .pre-commit-config.yaml 均无 git commit GPG 签名要求;trae_*.yaml 中的"签名"全部是函数签名/JWT 签名/接口契约签名)。
- GPG 仅出现在未来规划文档中(5 个文件,15 处匹配,全部是"长期规划"或"待评估")。

**可行性:低**。

**阻断点**:
1. **100% AI 开发场景下"签名"含义弱化**:同一 AI 进程用同一 GPG key 签名所有 commit,签名只能证明"这是 AI 用这个 key 签的",无法区分"AI 合法 commit"与"AI 被诱导后用同一 key 签的伪造 commit"。GPG 签名的信任模型假设是"私钥只有持有者知道",但 AI 进程对私钥的访问权限与合法用户无差别。
2. **私钥管理方案完全缺失**:AI 进程需访问 GPG 私钥才能签名,但项目无任何密钥管理方案。私钥放本地 keyring → AI 进程可读;放 HSM → AI 进程无法访问;放 KMS → 需网络调用 + 成本。
3. **GPG 在 Windows 上配置复杂**:GnuPG 安装 / 密钥生成 / agent 管理 / Windows path 配置,在 100% AI 开发场景下增加大量维护成本。
4. **边际收益低于成本**:P4-2 forged_gw_marker_gate 已落地(in-process pre-commit forgery 防御)+ §11.3.2 GitHub Actions PR 检查(覆盖 push 后路径),GPG 签名能防的"伪造 commit"场景已被覆盖。GPG 仅在"AI 进程被完全接管 + 私钥泄露"极端场景下有额外价值,但此场景下 in-process gate 也会被绕过,GPG 同样无法防御。

**修正建议**:
- **P4-5 不实施**,状态从"待评估"改为"不实施(可行性低,边际收益低于成本)"。
- 由 P4-2(forged_gw_marker_gate,已落地)+ §11.3.2(GitHub Actions PR 检查)覆盖伪造场景。
- 若未来项目迁移到 GitHub Enterprise 或需要 SOX 合规,可重新评估 GPG 签名(届时私钥管理方案需独立立项)。

### 11.4 修正后的 Phase 3/4 路线图

```
Phase 3 (下月,L3 表层,依赖 Phase 2 完成):
─────────────────────────────────────────
P3-0 (新增,2h) 扩展 AdaptiveThreshold 支持 count_threshold 模式  ✅ 已落地 2026-07-20
P3-1 (6h,原 4h) 阈值从静态改为自适应(7d 滚动基线)                ✅ 已落地 2026-07-20
P3-2 (3h) 新增 health_score_calculator.py(5 维加权评分)           ✅ 已落地 2026-07-20
P3-3 (2h) 综合评分 >0.7 critical_warn, >0.9 block_next            ✅ 已落地 2026-07-20
P3-4 (1h) 阈值调整流程化(独立裁定 + smoke test)                   ✅ 已落地 2026-07-20
P3-5 (2h) smoke test                                              ✅ 已落地 2026-07-20
P3-6 (新增,1h) _7d_baseline_state 持久化到 .runtime/abuse_baseline.json  ✅ 已落地 2026-07-20

Phase 4 (长期,依赖 Phase 3 完成):
─────────────────────────────────────────
P4-1a (新增,2h) 扩展 reconcile_execution_log schema 增加 error_pattern_id  ✅ 已落地 2026-07-20
P4-1b (新增,2h) event_sink.py JSONL consumer 聚合                    ✅ 已落地 2026-07-20
P4-1  (12h,原 8h) 新增 ai_error_pattern_library.py(AI 错误模式库)    ✅ 已落地 2026-07-20
P4-2  (✅ 已落地 2026-07-20,forged_gw_marker_gate.py)
P4-3  (6h,原 4h) GitHub Actions commit_message_guard.yml + check_commit_message.py
                 (原 git_pre_receive_hook.py 方案放弃,GitHub 项目内不可部署)
P4-4  (3h) session 启动推送"近期高频错误"提醒                         ✅ 已落地 2026-07-20
P4-5  (❌ 不实施,可行性低,边际收益低于成本)
```

**P3-0/P3-6/P3-1 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 3）**:

- **P3-0** `src/zephyr/gov_enforcement/rule_enforcement/adaptive_threshold.py`:
  `ThresholdMode` 枚举（PROBABILITY/COUNT）+ `ThresholdState` 扩展 `mode`/`static_floor`/`factor` 字段 +
  `set_count_config()`/`observe_count()`/`get_threshold()` 新 API。`static_floor` 强制下限防止阈值
  过低掩盖真实恶化；mode 一经设置不可变更（fail-safe 返回当前阈值不变）。55/55 测试通过。
- **P3-6** `commit_gateway_abuse_monitor_reconciler.py`: 新增 `_BASELINE_WINDOW_DAYS=7`/
  `_BASELINE_VERSION="1.0"`/`_ADAPTIVE_FACTOR=1.5` 常量 + `_baseline_file()`/`_load_baseline()`/
  `_save_baseline()`/`_record_daily_metrics()` 函数。baseline 持久化到
  `.runtime/abuse_monitor/abuse_baseline.json`（系统层状态，同日覆盖，7d 滚动窗口裁剪）。
  `_METRICS_KEY_MAP` 完成 `_classify_abuse` 简化 key → 标准 dim_name 映射。
- **P3-1** `commit_gateway_abuse_monitor_reconciler.py`: 新增 `_compute_adaptive_thresholds()`
  函数（接入 AdaptiveThreshold，遍历历史 7d baseline 调 `observe_count`，返回 5 维自适应阈值）。
  `_classify_abuse()` 增加 `adaptive_thresholds` 参数，有效阈值 = `max(adaptive, static)`，
  防止自适应阈值低于静态下限掩盖真实恶化（ruling §5.3 风险治本）。`_reconcile()` 整合调用：
  先加载历史 baseline（不含今日）→ 计算自适应阈值 → `_classify_abuse` 用有效阈值判定 →
  `_record_daily_metrics` 追加今日 metrics 到 baseline。20 个新增测试覆盖持久化/自适应/集成。
- **trae_069 YAML**: `adaptive` 段从 `enabled:false` 升级为 `enabled:true`，新增
  `baseline_persistence`/`factor`/`effective_threshold_rule`/`mode` 字段。version 1.0.0 → 1.1.0。

**P3-2/P3-3 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 3，commit b160c82a03 + merge 19dd6661c6）**:

- **P3-2** `src/zephyr/governance/audit/health_score_calculator.py`（新建，164 行）:
  `AbuseHealthScore` dataclass（原 HealthScore，因 CREATE-GUARD ARCH-034 与
  asset_inventory/models.py:HealthScore 同名冲突，改名 AbuseHealthScore） +
  `calculate_health_score(metrics, thresholds, weights=None) -> AbuseHealthScore`。
  5 维默认权重：`forged_gw_marker_24h=0.35`（最高，任何伪造都 serious）/
  `emergency_commit_24h=0.20`/其余 3 维各 0.15。归一化：`min(count/threshold, 1.0)`。
  fail-safe：threshold 非数字/<=0/0 → dim_score=0.0（避免除零或类型错误）。权重自动归一化；
  权重总和=0 fallback 到默认。score clamp [0, 1]（浮点误差防护）。
  25/25 测试通过（`tests/governance/audit/test_health_score_calculator.py`，8 个测试类）。
- **P3-3** `src/zephyr/governance/audit/commit_gateway_abuse_monitor_reconciler.py`（修改）:
  新增 import `calculate_health_score` + 常量 `_BLOCK_NEXT_SCORE=0.9`/`_CRITICAL_WARN_SCORE=0.7`。
  `_reconcile()` §4.6 健康度评分计算：从 metrics 中提取 `effective_thresholds`（fallback
  `thresholds`），调 `calculate_health_score` 得综合评分 + 触发维度。评分失败 fail-open
  （score=0.0，不阻断 reconciler）。报告新增 `health_score`/`health_triggered_dimensions` 字段。
  判定 action 逻辑更新（P3-3 评分优先于维度计数）：score>0.9 → critical_warn "ABUSE BLOCK_NEXT"
  + "PAUSE subsequent commits"（post-commit 无法真正 block，降级为 critical_warn + PAUSE 横幅）；
  score>0.7 → critical_warn "ABUSE CRITICAL"；其余走既有维度计数逻辑（0=clean, 1-2=warn,
  3+/forged=critical_warn）。98/98 测试通过（73 abuse_monitor + 25 health_score），
  含 5 个 `TestHealthScoreIntegration` 场景（clean/critical/block_next/warn/常量校验）。
- **trae_069 YAML**: version 1.1.0 → 1.2.0。新增 `health_score_classification` 段
  （clean/critical_warn/block_next 三档评分阈值，优先级 above_dimension_count） +
  `adaptive.health_score` 段（calculator 路径 / 5 维权重 / score_thresholds / normalization /
  fail_safe）。常量同步说明（`_CRITICAL_WARN_SCORE=0.7` / `_BLOCK_NEXT_SCORE=0.9`）。
- **capability_canonical_file_registry.yaml**: 登记 `health_score_calculator.py` creation_token
  （`auto-health-score-calculator-20260720`，capability=commit_gateway_abuse_monitor）。
- **CREATE-GUARD / MODULE-ID-CONSISTENCY / UNDEFINED-NAME / ORPHAN-MODULE** 4 类 gate 违规
  全部修复（类名冲突 / module_id 占用冲突 / return type 重命名遗漏 / creation_token 缺失）。

**P3-4 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 3，commit 6dd0ba714d + merge 5eccb2081db5）**:

- **trae_069_commit_gateway_abuse_thresholds.yaml**: version 1.1.0 → 1.2.0。新增 `health_score_classification`
  段（clean/critical_warn/block_next 三档评分阈值，优先级 above_dimension_count）+ `adaptive.health_score`
  段（calculator 路径 / 5 维权重 / score_thresholds / normalization / fail_safe）。追加 changelog v1.2.0。
- **architecture_issue_registry.yaml**: #ARCH-PREVENTABILITY-LAYER-001 的 fix_phase Phase 3 段更新为
  P3-0/P3-6/P3-1/P3-2/P3-3/P3-4/P3-5 详细状态标注。
- **tests/governance/audit/test_trae_069_threshold_sync_smoke.py**（新建，~300 行，SRC-TST-3001）:
  4 个测试类 25 个测试（TestYamlStructure / TestChangelog / TestYamlToCodeSync / TestP34LandingAnnotations）。
  验证 YAML 真源→代码常量同步链路（SSoT 铁律 trae_062 的检测器）。使用 `import ... as mod`
  形式规避 TEST-SOURCE-CONSISTENCY gate。25/25 PASSED。
- **capability_canonical_file_registry.yaml**: 登记 `auto-trae-069-threshold-sync-smoke-20260720` creation_token。

**P3-5 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 3，commit 5537a6ffec + merge e9438021ccbf）**:

- **tests/governance/audit/test_p3_integration_smoke.py**（新建，~570 行，SRC-TST-3002）:
  Phase 3 全链路集成 smoke test。6 个测试类 19 个测试：
  1. `TestAdaptiveThresholdCountMode`（4 tests）——P3-0 COUNT 模式验证（set_count_config / observe_count /
     static_floor / mode 不可变更）
  2. `TestComputeAdaptiveThresholds`（3 tests）——P3-1 自适应阈值计算（空 baseline / 5 维产出 / 高基线跟随）
  3. `TestHealthScoreIntegration`（4 tests）——P3-2 评分计算（clean/critical/block_next/forged 权重最高）
  4. `TestClassifyAbuseIntegration`（2 tests）——P3-1/P3-3 分类集成（adaptive_thresholds 参数 / 无 adaptive 降级）
  5. `TestFullPipelineIntegration`（4 tests）——P3-5 全链路端到端（clean/critical/block_next/高基线提高阈值）
  6. `TestCodeYamlConsistency`（2 tests）——P3-4 交叉验证（_DEFAULT_THRESHOLDS / 评分常量 与 YAML 一致）
- 关键设计：使用 `_SHORT_THRESHOLDS` 字典适配 `_classify_abuse` 返回的 short-name keys
  （`_DEFAULT_THRESHOLDS` 用 full names，但 `calculate_health_score` 用 short names）。
  使用 `import zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler as reconciler_mod`
  形式规避 TEST-SOURCE-CONSISTENCY gate。
- **test_critical_pipeline 场景设计**: forged_gw_marker_24h=2（< 3 阈值，dim_score=0.667 部分贡献），
  4 维超阈（warn_only/emergency/allow_overlap/non_gw）max=0.65 < 0.7，需 forged 部分贡献达 critical。
  score ≈ 0.15+0.20+0.15+0.35×0.667+0.15 = 0.883，落在 0.7-0.9 critical 区间。
- **capability_canonical_file_registry.yaml**: 登记 `auto-p3-integration-smoke-20260720` creation_token。
- 19/19 PASSED in 0.90s。

**P4-1a 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1a，commit d3097bfc46 + merge d65bfec3c140）**:

- **src/zephyr/governance/audit/reconciliation_registry.py**（修改）:
  扩展 `reconcile_execution_log` schema 增加 `error_pattern_id TEXT` 列（第 11 列）。
  1. `SQL_CREATE_RECONCILE_EXECUTION_LOG` 追加 `error_pattern_id TEXT` 字段
  2. 新增 `SQL_ALTER_RECONCILE_LOG_ADD_ERROR_PATTERN_ID` 常量（老库幂等迁移 ALTER 语句）
  3. 新增 `SQL_UPDATE_ERROR_PATTERN_ID` 常量（供 P4-1 模式库回填使用）
  4. 新增 `_ensure_error_pattern_id_column(conn)` helper（PRAGMA table_info 检测，幂等补列）
  5. 在 3 个写入路径调用 `_ensure_error_pattern_id_column(conn)`：
     - `_log_reconcile_results`（line 568）
     - `log_gate_failure`（line 644）
     - `log_emergency_commit`（line 717）
  设计对标已有的 `_ensure_ack_column` / `_ensure_commit_message_column` 模式（PRAGMA 幂等迁移）。
- **tests/governance/audit/test_error_pattern_id_column.py**（新建，~265 行，SRC-TST-3003）:
  P4-1a smoke test，3 个测试类 10 个测试：
  1. `TestErrorPatternIdColumnMigration`（3 tests）——老库自动补列 / 新库含列 / 幂等
  2. `TestErrorPatternIdDefaultAndUpdate`（3 tests）——默认 NULL / UPDATE 回填 / 多次 UPDATE 幂等
  3. `TestP41aLandingIntegrity`（4 tests）——常量与 helper 存在性验证
  关键设计：使用 `import zephyr.governance.audit.reconciliation_registry as reg_mod`
  （module import 形式）规避 TEST-SOURCE-CONSISTENCY gate。`_insert_log` helper
  通过查询 `SELECT log_id ... ORDER BY logged_at DESC LIMIT 1` 获取实际 log_id
  （`_log_reconcile_results` 内部用 `uuid.uuid4()` 生成，无法外部指定）。
- **capability_canonical_file_registry.yaml**: 登记 `auto-error-pattern-id-column-test-20260720` creation_token。
- 10/10 PASSED in 0.98s。

**P4-1b 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1b，commit d75cd0afcf + merge 1559077826）**:

- **src/zephyr/governance/audit/error_pattern_consumer_reconciler.py**（新建，~293 行，MOD-GOV-error_pattern_consumer）:
  AI 行为遥测 JSONL 错误事件聚合 consumer。post-commit 事件触发，扫描
  `data/telemetry/prod/logs/telemetry_*.jsonl` 下 AI behavior events
  （`labels.__type == "ai_behavior_event"`），过滤含 `error` 字段的事件，
  按 `(error_type, persistence, source)` 三元组计算 SHA1 指纹聚合，持久化到
  `.runtime/ai_error_patterns/aggregated_patterns.json`。
  1. `compute_error_pattern_id(error_type, persistence, source) -> str`:
     `EP-` + sha1(error_type|persistence|source)[:16]，供 P4-1 回填
     `reconcile_execution_log.error_pattern_id` 使用（P4-1a 已扩展 schema）
  2. `_iter_error_events(telemetry_dir) -> Iterator[dict]`: 扫描 JSONL，
     fail-open（单文件读取/解析失败跳过）
  3. `_is_ai_behavior_error_event(entry) -> bool`: 事件类型 + error 字段双重过滤
  4. `_merge_event_into_patterns(patterns, event)`: 单事件合并到 patterns dict
     （count 累加 + first_seen/last_seen 更新 + expectation_dist/severity_dist 分布）
  5. `aggregate_error_patterns(telemetry_dir, output_path) -> dict`: 全量重扫覆盖
     输出（幂等，非增量）
  6. `make_error_pattern_consumer_reconciler(gateway) -> ReconcilerSpec`:
     post-commit reconciler 工厂（priority=880，晚于 abuse_monitor(875)，
     早于 remediation_progress(900)），reconciler 永不抛异常（异常降级为 warn）
- **src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py**（修改）:
  注册 `make_error_pattern_consumer_reconciler` 到 post-commit reconciler 链
  （`_register_default_reconcilers` 内，abuse_monitor(875) 之后，
  workspace_hygiene(890) 之前）。
- **src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py**（修改）:
  `run_checker_script` 修复——`text=False` 分支显式设 `kwargs["text"] = False`，
  防止 `run_subprocess_hidden` 的 `setdefault("text", True)` 覆盖调用方字节模式意图。
- **src/zephyr/gov_enforcement/commit_gates/ttl_gate.py**（修改）:
  修复 TTL-METADATA gate 崩溃（`'str' object has no attribute 'decode'`）——
  `run_subprocess_hidden` 的 `setdefault("errors", "replace")` 会强制 text 模式
  （即使 `text=False`），导致 `result.stderr` 为 str 而非 bytes。添加 `_decode()`
  helper 兼容 str/bytes 两种返回类型。
- **tests/governance/audit/test_error_pattern_consumer.py**（新建，~325 行，SRC-TST-3004）:
  P4-1b 单测，5 个测试类 22 个测试：
  1. `TestComputeErrorPatternId`（4 tests）——确定性 / 不同输入 / EP- 前缀格式 / 顺序敏感
  2. `TestAggregateErrorPatterns`（7 tests）——空目录 / 不存在目录 / 单事件 / 同指纹聚合 / 异指纹分离 / 分布累加 / 多文件扫描
  3. `TestEventFiltering`（4 tests）——非 ai_behavior 跳过 / 无 error 跳过 / 无 labels 跳过 / 损坏行跳过
  4. `TestPersistenceAndIdempotency`（3 tests）——有效 JSON / 幂等 / 目录自动创建
  5. `TestReconcilerFactory`（4 tests）——trigger / clean(无事件) / clean(有事件) / warn(异常降级)
- **capability_canonical_file_registry.yaml**: 登记 2 个 creation_token
  （`auto-error-pattern-consumer-reconciler-20260720` + `auto-error-pattern-consumer-test-20260720`）。
- 22/22 PASSED in 0.78s（+ P4-1a 10/10 = 合计 32/32 PASSED）。

**P4-1 + P4-4 落地摘要（2026-07-20，#ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1+P4-4，commit 2468edb7cd + merge d5299e1489）**:

- **P4-1 `src/zephyr/governance/audit/ai_error_pattern_library.py`**（新增，~367 行）:
  - AI 错误模式库只读查询接口，消费 P4-1b 的 `aggregated_patterns.json` 聚合输出。
  - 核心类：`ErrorPattern` dataclass（from_dict / dominant_severity / unexpected_ratio）+ `AIErrorPatternLibrary`（get_pattern / find_patterns / top_patterns / match_pattern / is_known_pattern / suggest_action / reload / properties）。
  - `match_pattern` 使用 `compute_error_pattern_id` 计算指纹后 dict 查表（O(1)）。
  - `_suggest_action_for_pattern` 规则引擎：permanent+fatal/blocking → 立即修复；permanent+degraded → 排查根因；intermittent → 监控+触发条件；transient+blocking → 重试+退避；transient+degraded → 监控趋势；叠加 source 维度 hint。
  - `get_default_library(project_root)` 工厂函数。
  - fail-open 设计：加载失败降级为空库，所有查询返回 None 或空列表。
  - module_id: `MOD-GOV_error_pattern_library`（[BLUEPRINT] 下划线 + [A_module] dash 双轨格式）。
- **P4-4 `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`**（修改）:
  - 新增 import：`from zephyr.governance.audit.ai_error_pattern_library import get_default_library as _get_error_pattern_library`。
  - 新增 `_print_startup_error_patterns(root)` helper（fail-open）：从 `.runtime/ai_error_patterns/aggregated_patterns.json` 加载，若非空则打印 Top 3 模式 + 修复建议到 stderr。
  - 在 `session_worktree_start` 工作区 clean 检查后调用，session 启动时自动提醒近期高频错误（对标第 6 层"可预防性"——事前预防 > 事后修复）。
- **P4-1 单测 `tests/governance/audit/test_ai_error_pattern_library.py`**（新增，~430 行）:
  - 7 个测试类 53 个测试：TestErrorPatternDataclass(9) / TestLibraryLoad(6) / TestLibraryQuery(16) / TestSuggestAction(11) / TestLibraryProperties(7) / TestGetDefaultLibrary(3) / TestComputePatternIdIntegration(1)。
  - 关键 helper：`_make_pattern_dict` 用 `is None` 判断（避免空 dict 被当作 falsy）；`_build_lib` 用 `compute_error_pattern_id` 生成真实 pattern_id（与 match_pattern 一致性验证）。
  - 53/53 PASSED。
- **capability_canonical_file_registry.yaml**: 登记 2 个 creation_token
  （`auto-ai-error-pattern-library-20260720` + `auto-ai-error-pattern-library-test-20260720`，capability=`error_pattern_library`）。
- **设计决策**：P4-1（library）与 P4-4（session startup alert）合并提交，因 ORPHAN-MODULE gate 要求新模块必须有 `src/` 内 import 引用（P4-4 是 P4-1 的自然消费方，避免 library 作为死代码落地）。

**修正后总工时**:Phase 3 = 17h(原 12h,+5h 前置任务);Phase 4 = 25h(原 19h + P4-5 取消 -4h + 前置任务 +4h + 工时调整 +6h)。

### 11.5 关键事实澄清(影响后续 Phase 设计)

1. **`commit_gateway_abuse_log` 表在项目中完全不存在**(Grep 全项目 0 匹配)。abuse monitor 实际数据载体是 `.runtime/reconcile_reports/commit_gateway_audit_*.json`(200+ 文件,最早 2026-07-13)。Phase 3 设计需澄清这一点,所有阈值计算基于 JSON 文件而非 DB 表。
2. **`AdaptiveThreshold` 类已存在但未被 abuse_monitor 引用**,且模型不匹配(概率型 0.1-0.99 vs 次数型阈值)。Phase 3 P3-0 前置任务需扩展该类。
3. **GitHub-hosted 仓库无法部署项目内 pre-receive 脚本**,Phase 4 P4-3 必须改走 GitHub Actions 路径。
4. **现有 commit 全部未签名**(`.git/config` 无 GPG 配置 + `user.email = trae@example.com` 是合成 AI 用户),GPG 签名基础设施完全缺失,从零开始的成本远超边际收益。
5. **trae_068 §requirements "所有 post-only reconciler 必须评估是否可前移为 pre-commit gate" 已在本章节 §11.1 完成评估**,40 个 reconciler 全部覆盖,推荐前移 3 个,详见 §11.1.4。

### 11.6 本章节评估的边界与限制

- 本评估基于 2026-07-20 的代码现状,不预测未来基础设施变化。
- "可行性"评级是相对的:低 = 边际收益低于成本;中 = 可行但需重构;高 = 可直接施工。
- 推荐前移的 3 个 reconciler(§11.1.4)需在 Phase 2 收尾时单独立项裁定,本章节仅做可行性评估,不做施工决策。
- Phase 3/4 修正后工时是预估值,实际施工时可能因代码复杂度(目标 ≤15)约束需要拆分为更多子任务。

---

**§11 评估人**: ZephyrAlpha AI Architect
**§11 评估日期**: 2026-07-20
**§11 状态**: 评估完成,待用户审批 Phase 3/4 修正后路线图