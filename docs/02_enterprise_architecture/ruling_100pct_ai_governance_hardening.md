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
- **R4(待实施)**: heartbeat 治本立项(2 周内 2026-08-02 前产出独立裁定 + smoke test)
- R5(已完成): 工作区卫生强制清理
- **R6(待实施)**: 6 层闭环模型正式化(AGENTS.md + `trae_067_preventability_layer.yaml`)

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

### 裁定 D-4: 第 6 层"可预防性"正式化(R6, 本周)

**问题**: 现有 5 层闭环模型(可知性/可达性/可观察性/可逃生性/可追溯性)只能"事后报告",无法"事前预防"。post-commit reconciler warn 无法挽回已 commit 的影响。

**治本方案**:
1. **AGENTS.md preamble 5 层 → 6 层**(补充 ⑥ 可预防性):
   - ⑥ 可预防性(Preventability): 机制能在问题发生前预防(pre-commit 阻断 + 自适应学习 + AI 行为模式库)
   - 与 ③ 可观察性的区别:可观察性是事后观察,可预防性是事前预防

2. **新增 `trae_067_preventability_layer.yaml`**(结构化规则):
   - rule_id: TRAE-067
   - title: 第 6 层可预防性 — pre-commit 阻断 + 自适应学习
   - prohibitions: 禁止 post-commit reconciler 作为唯一治理机制(必须有 pre-commit gate 配对)
   - requirements: 所有 post-only reconciler 必须评估是否可前移为 pre-commit gate

3. **`capability_canonical_file_registry.yaml` 登记 `preventability` capability**

4. **`rule_ai_perception_index.yaml` 重新生成**(66 → 67 rules)

5. **`gate_registry.yaml` 配对 gate**(pre-commit forgery gate,Phase 3 实施)

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
| P4-1 | 新增 `src/zephyr/governance/audit/ai_error_pattern_library.py` | AI 错误模式库(历史错误模式检索) | 8h |
| P4-2 | 新增 `src/zephyr/gov_enforcement/commit_gates/forged_marker_detection_gate.py` | pre-commit 检测 [GW:*] 标记合法性 | 4h |
| P4-3 | 新增 `scripts/governance/git_pre_receive_hook.py` | server-side pre-receive hook 拦截非 GW commit | 4h |
| P4-4 | `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py` | session 启动推送"近期高频错误"提醒 | 3h |
| P4-5 | 长期:GPG 签名强制 | server-side 强制 GPG 签名验证 | 待评估 |

**验证标准**:
- [ ] AI 错误模式库可检索历史错误模式
- [ ] forged_gw_marker pre-commit gate 阻断伪造标记
- [ ] non-GW commit server-side pre-receive hook 拦截
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