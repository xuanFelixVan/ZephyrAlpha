---
ttl: task_bound
---

# 错误码改号影响面与稳定性战略裁定书（Owner 交办，2026-08-21）

> 授权：Owner 指令——"改号后 5 个模块日志输出的错误码变了……全部调研清楚，全面审查相关问题，从第一性原理思维出发，长远期战略考虑，针对 100% AI 开发情况，给出分析过程+裁定结果+治本施工方案"；附疑点"好像是另一个 AI 对话刻意修改的"。

---

## 一、调研实证

### 1.1 五个旧码的全仓消费面（grep 全量，含 yaml/md/py/config）

| 旧码 | 后引入者（已改号） | 功能性消费方 | 结论 |
|---|---|---|---|
| ZA-CMP-0006 | manipulation_stream_driver→0011 | 零（blueprint L42 为 canonical 侧契约） | 无告警同步需求 |
| ZA-GV-0050 | ai_behavior_baseline→0051 | 零（test_commit_gate_registry:356 断言的是 canonical 侧；ARCH 注册表两处为历史记录） | 同上 |
| ZA-INT-0001 | event_score→0005 | 零（tool_contracts.yaml/test_mcp_servers 均为 canonical sentinel 侧） | 同上 |
| ZA-INT-0002 | event_anomaly_detector→0006 | 零（同上） | 同上 |
| ZA-RK-0030 | deviation_attribution→0068 | 零（canonical var_breach_state_machine 侧完好） | 同上 |

- **全项目无任何按错误码路由的告警/通知/看板/runbook 机制**（alert_dispatcher 零命中、config 目录零命中、反馈环无码匹配逻辑）。错误码当前消费方式=人/AI 读日志+注册表对账门禁，无机器按码消费。
- audit_prompts_20_ai.md 20 处命中=后续会话把本案写成审计先例文本（历史引述，非功能依赖）。
- **结论：本次改号零事故面。Owner 担忧的"告警规则需同步"实证消解——不存在按码配置的告警规则。**

### 1.2 "另一 AI 会话刻意修改"疑点考古（git 取证）

5 个后引入者全部生于 **AI-NIGHT-001 第二批**三个大包围抄 commit（08-20）：

| 文件 | 引入 commit | 批次 |
|---|---|---|
| event_score.py / event_anomaly_detector.py | 54be465cb5（05:58） | 包F 26号事件驱动+13号 NLP（7 src+4 scripts+11 测试） |
| manipulation_stream_driver.py / deviation_attribution.py | 7b6d09ffac（08:38） | 包P 54/55/40/42/43号 16 项 |
| ai_behavior_baseline.py | b843aba06e（09:30） | 包Q1 50/61/62/17/15号收尾 10 项 |

**裁定：非刻意。** 三个 commit 消息通篇未提错误码分配；重码形态=大包围抄施工的"目测取号"事故——AI 给新模块异常类分配码时按目录内直觉取号（intelligence 域模块取 INT 前缀+小号），未查 error_code_registry.yaml SSoT。附带发现：**前缀语义同时漂移**——注册表 domain_prefixes 中 INT=D_INFRASTRUCTURE、IT=D_INTELLIGENCE，event_* 三模块（D_INTELLIGENCE）占了 INT 段（gate 只查前缀已声明、不查域匹配，故未拦）。

### 1.3 结构根因：门禁覆盖面与 AI 提交主通道结构性脱钩（关键）

1. GATE-ERRCODE（08-18 AI-ERR-001 建）**只挂在 `.pre-commit-config.yaml` 外部链**（硬阻断，files 触发）。
2. **GitCommitGateway 设计上永远 --no-verify**（precommit_offline_gate.py 文档 L26 明示："pre-commit hook 在合法路径不触发"）——gateway 的 in-process 门禁注册表（in_process_gate_registry.yaml，97 门实测）**无 ERRCODE 条目**。
3. 100% AI 开发的全部合法提交走 gateway in-process 通道 → **errcode 门禁对 AI 主通道等于不存在**。43 未登记+5 重号正是经此洞入仓（夜班批 commit 全带 GW 标记实证走的 gateway）。
4. 同类先例：#69 三 hook 与外部链不兼容、"外部链结构性不可过三根因"（merge 留痕）——外部链与 gateway 双轨脱节是已确认的家族病。

## 二、第一性原理

1. **错误码=可观测性 API 面，入册即 immutable**。改号是 breaking change——本次零消费面是运气（尚无按码告警），不是设计。长期战略：码只追加不回收；重号防控必须在写入点（commit gate），事后改号是止血不是制度。
2. **门禁的价值=在写入点阻断；存在于旁路通道的门禁=不存在**。100% AI 场景下"AI 会走哪条通道"就是全部通道——外部 pre-commit 链只是裸 git 的兜底，gateway 才是主防线。关键门禁必须 in-process 化。
3. **编号分配靠工具不靠纪律**。"先查注册表再取号"是人审软约束，AI 在大包围抄时必然跳过——拦截时必须直接给出可执行答案（下一可用号），把修复成本压到复制粘贴级。
4. **前缀-域语义是注册表契约的一部分**（INT=D_INFRASTRUCTURE vs 实际当 intelligence 用）——当前 gate 不查域匹配，属契约松弛观察项，不再改号（二次 breaking 代价>收益），登记观察。

## 三、裁定结果

1. **改号收口维持**（615df5b90c）——零消费面实证，无告警同步需求；Owner 记忆疑点澄清：非另一 AI 刻意修改，系夜班批目测取号事故。
2. **治本①（本批施工）**：GATE-ERRCODE 移植 gateway in-process 通道（新 commit gate，调用 tests/governance/test_error_code_consistency.py 六断言为判定 SSoT，不重实现），堵上主通道空洞。
3. **治本②（本批施工）**：阻断消息内嵌受影响前缀的下一可用号（扫描真源+注册表取 max+1），AI 被拦即得可执行答案。
4. **登记观察项**：前缀-域语义匹配（INT/IT 族）不强制，随注册表下次大修订评估；独立取号 CLI 不单建（gate 内嵌提示已覆盖主场景，若后续拦截频发再议）。

## 四、治本施工方案与落地状态

| 层 | 动作 | 状态 |
|---|---|---|
| A | errcode_consistency_gate.py（priority=131，硬阻断；files 触发=src/**.py 或 registry yaml 在 staged 才执行；非 Zephyr 项目 fail-open） | 本批 |
| A | 注册五件套：in_process_gate_registry（total 97→98）+ module_translation×2 + ARCH 条目 + creation_token×2 | 本批 |
| A | 测试：构造违规/放行/跳过三态 | 本批 |
| B | gate_registry.yaml 由 GATE-REGISTRY-SYNC reconciler（priority=830）post-commit 自动重生成，不手改 | 机制既有 |
| C | 前缀语义观察项入裁定书（本文 §二.4） | 已落 |

## 五、落地核验（机器可核）

- 施工 commit hash + 违规 fixture 阻断实证 + 当前仓放行实证 + commit_gates 关联域回归零新增红（见本批 commit 消息与 tracker 翻账行）。

---

**裁定人**：专项统筹（Owner 授权调研裁定）
