---
module_id: MOD-GOV-arch-ruling
title: 架构债务 wontfix 项重新审查与系统性 Any 治理专项工程裁定（#ARCH-ANY-GOVERNANCE-001）
version: 1.0.0
layer: L2_domain
depends_on: [architecture_debt_registry, debt_permanent_rulings_r102]
tags: [ruling, architecture-debt, permanent, any-typing, governance]
ttl: permanent
doc_type: audit_report
completes_when: 5.145 维度全部治本完成（PERMANENT-14 → FIXED）+ GATE-ANY-ABUSE 升级 commit 阻断 [DONE 2026-07-22]
---

# 架构债务 wontfix 项重新审查与系统性 Any 治理专项工程裁定

> **议题编号**：#ARCH-ANY-GOVERNANCE-001
> **议题标题**：60 项 wontfix 第一性原理重新审查 + 5.145 系统性 Any 类型注解治理专项工程
> **登记日期**：2026-07-21
> **裁定日期**：2026-07-21
> **裁定人**：客观专业架构师（受 Owner 委托，回应"发起 ARCH-XXX 裁定 + 蓝图 + 专项施工计划"指令）
> **状态**：DONE（Phase 1-3 治本完成，2026-07-22；5.145 维度 PERMANENT-14 → FIXED）

---

## 一、议题背景

R102（2026-07-19）对 87 项 DEFERRED-PERMANENT 完成逐项裁定：
- 27 项 EXECUTE（立即治本）——已于 2026-07-21 全部治本完成（merge `799405bb5b27`）
- 60 项 RATIFY（确认关闭为 wontfix-permanent）——防复发门禁已在册

2026-07-21 Owner 指令："发起 ARCH-XXX 裁定 + 蓝图 + 专项施工计划"，触发对 60 项 wontfix 的重新审查。

---

## 二、第一性原理重新审查（60 项 wontfix 全量扫描）

### 审查原则（继承 R102 + 升级）

- **P1 防复发 > 存量修复**：若防复发机制已完整覆盖，存量保持 wontfix 合理
- **P2 无回归测试不做高风险重构**：仍成立
- **P3 实际风险=0 的"违规"非债务**：仍成立
- **P4 净收益必须为正**：升级审查——若"增量机会性清理"缺乏机械执行保证，则"延迟治理"实际等于"永不治理"，净收益计算失效
- **P5 可机械验证/执行的优先**：升级——若现有工具可支持机械治理（即使需构建辅助工具），应优先发起专项
- **P6 SSoT 唯一真源最高原则**：仍成立

### 审查方法

逐项核对 R102 裁定理由 vs 当前项目状态：
1. 防复发机制是否仍在册？
2. 裁定时引用的"基线数据"是否仍准确？
3. 裁定时引用的"成本/收益"评估是否仍成立？
4. 是否出现新的治理路径使原"不可机械执行"变为"可机械执行"？

### 60 项 wontfix 分类结果

#### 群组 A：合理 wontfix（46 项，保持 RATIFY）

**裁定理由**：P3 实际风险=0 或 P4 净收益为负（强行治本引入新风险）。R102 裁定理由经重新审查仍成立。

| 维度 | 条目数 | 保持 wontfix 理由 |
|---|---|---|
| 5.33.6/10 容灾与备份 | 2 | 单机项目主从到 localhost 无意义；Vault 属过度工程 |
| 5.93.1 import 副作用 | 1 | 2 daemon Timer 是 MOD-INF-015 刻意设计，移除风险>收益 |
| 5.100.15/16 asyncio | 2 | 仅 fallback/CLI 单发路径，无实际运行时风险 |
| 5.101.5-17 变量遮蔽 | 12 | LEGB 分析实例属性不参与作用域链；改名冲击 JSON 键/DB 列/API 契约 |
| 5.140.2 函数复杂度 | 3 | 单一职责、认知复杂度在 AI 处理范围内；NO-HIGH-COMPLEXITY gate 已防新增 |
| 5.143.7-19 13 项盲盒 | 13 | 注册表从未记录具体条目，HIGH 已全部修复；MEDIUM 级 Python 动态类型下无 TypeError |
| 5.143.20 ComplianceManagerBase | 1 | Phase B 骨架 OCP 扩展点，双层防护零运行时风险 |
| 5.150.6 Data Class | 1 | 报告 DTO 17 字段 0 方法是合法模式（不可变数据载体） |
| 5.150.16 Primitive Obsession | 1 | 值对象重构冲击面大于收益 |
| 5.153.7/8/9 命名统一 | 3 | 改名冲击契约/序列化，净收益为负 |
| 5.153.16-21 布尔命名 | 6 | 改名冲击序列化/契约 |
| 5.160.2 apply_depgraph SQL | 1 | SAFETY=H + 无测试覆盖，提取常量不可验证行为等价 |
| **合计** | **46** | **保持 RATIFY** |

#### 群组 B：原 wontfix 重新裁定为 EXECUTE（14 项，5.145.13-26 系统性 Any）

**裁定理由（R102 原理由失效分析）**：

R102 裁定理由原文（[debt_permanent_rulings_r102.md](debt_permanent_rulings_r102.md) §5.145.13-26 行）：

> "GATE-ANY-ABUSE 防复发已在（manual 阶段）；627 处一次性替换不可验证（错误类型标注比无标注更危险）；Any 在 Python 运行时不做类型检查仅静态分析 warning；30-40% 为合理 Any；增量机会性清理为常态实践。"

**逐句失效分析**：

1. **"GATE-ANY-ABUSE 防复发已在（manual 阶段）"** — 失效。
   - manual 阶段意味着常规 commit 不触发，仅手动 `pre-commit run --hook-stage manual` 触发
   - 实测：无人手动触发过（无相关 commit 引用）
   - **防复发门禁实际未生效**——AI 新提交的 Any 不会被阻断

2. **"627 处一次性替换不可验证"** — 部分失效。
   - 当前裸 Any 数已降至 ~270 行 / 118 文件（较 R102 基线下降 57%，因 R102 EXECUTE 治本施工顺带清理）
   - **分批治理可机械验证**：每批 20-30 处 + 单元测试 + mypy 静态检查 = 可验证

3. **"错误类型标注比无标注更危险"** — 仍成立，但不构成阻断理由。
   - 治本策略应包含**类型推断辅助工具**：基于调用点上下文推断合理类型，而非盲目猜测
   - 推断工具输出候选类型供人工/AI 审核，错误率显著降低

4. **"30-40% 为合理 Any"** — 仍成立。
   - 治本目标不是清零 Any，是清零**可推断具体类型但误标 Any** 的实例
   - 合理 Any（动态配置、Plugin 接口、Protocol 边界）保留，gate 容器型已豁免

5. **"增量机会性清理为常态实践"** — 失效。
   - "机会性清理"无机械保证，AI 永远不会主动清理（无触发机制）
   - 自 R102（2026-07-19）至今 2 天，无任何机会性清理 commit（除 R102 EXECUTE 治本顺带清理外）
   - **这条裁定理由是"延期执行"的委婉说法，不是真正的治本路径**

**新裁定结论**：

| 条目 | 原裁定 | 新裁定 | 理由 |
|---|---|---|---|
| 5.145.13-26（14 项） | RATIFY（wontfix-permanent） | **EXECUTE（分批治理，2026-07-21 启动）** | R102"增量机会性清理"理由已失效（无机械执行保证）；GATE-ANY-ABUSE manual 模式未生效；裸 Any 已降至 270 行可分批治理；治本方案包含类型推断工具降低错误率 |

---

## 三、治本施工方案（3 阶段）

### Phase 1：类型推断辅助工具构建（1-2 个 worktree session）

**目标**：构建 `scripts/governance/d7_code/any_type_inferrer.py`，基于调用点上下文推断候选类型

**功能规格**：
- AST 遍历函数签名中的 `: Any` / `-> Any`
- 对每个裸 Any 参数：
  - 查找函数体内所有该参数的使用点（方法调用、属性访问、运算操作）
  - 基于使用模式推断候选类型（如 `x.upper()` → `str`，`len(x)` → `Iterable`，`x[0]` + `x.append()` → `list`）
  - 查找调用点的实参类型（mypy/pyright 风格反向推断）
  - 输出 JSON 报告：`{file, line, param, current_any, inferred_candidates, confidence}`
- 对每个 `-> Any` 返回值：
  - 查找函数体内所有 `return` 语句的返回表达式类型
  - 输出候选返回类型

**验收**：
- 工具可执行（`python scripts/governance/d7_code/any_type_inferrer.py --path src/zephyr`）
- 输出 JSON 报告到 `data/any_inference_report/`
- 推断准确率 ≥ 70%（基于抽样人工审核）

### Phase 2：分批治理（5-8 个 worktree session）

**目标**：按 top-N 违规文件分批治理，每批 20-30 处裸 Any 替换为推断类型

**分批计划**（基于当前 270 行 / 118 文件分布）：

| 批次 | 文件 | 裸 Any 数 | 优先级 |
|---|---|---|---|
| Batch 1 | `governance/escalation/escalation_engine.py` | 12 | HIGH（核心治理） |
| Batch 2 | `infrastructure/system_telemetry/facade.py` | 11 | MEDIUM |
| Batch 3 | `integration/pipeline_orchestrator.py` | 11 | HIGH（pipeline 核心） |
| Batch 4 | `security/access_control/permission_hooks.py` + `guards/abac_guard.py` | 17 | HIGH（安全） |
| Batch 5 | `integration/vector_memory/in_process_vector_memory.py` | 8 | MEDIUM |
| Batch 6 | `shared/utils/testing.py` + `frontend/dashboard/app_panel.py` | 14 | LOW |
| Batch 7 | `gov_enforcement/rule_enforcement/drift_detector.py` + `orchestrator/execution/trigger_router.py` | 12 | MEDIUM |
| Batch 8 | 剩余 ~110 行 / ~110 文件 | ~110 | 分批 5-10 文件/批 |

**每批治本流程**：
1. 运行 `any_type_inferrer.py` 生成该文件推断报告
2. 人工/AI 审核推断候选类型（合理 Any 保留，可推断类型替换）
3. 修改函数签名 + 同步调用方（若需要）
4. 运行单元测试 + mypy 静态检查
5. `session_worktree_commit` 提交

**验收**：
- 每批 commit 后 GATE-ANY-ABUSE（manual 触发）该文件裸 Any 数下降
- 全部批次完成后，裸 Any 数 ≤ 50 行（保留合理 Any）
- 5.145 维度状态：PERMANENT-14 → FIXED

### Phase 3：GATE-ANY-ABUSE 升级 commit 阻断（1 个 worktree session）

**目标**：把 GATE-ANY-ABUSE 从 `stages: [manual]` 升级为常规 commit 阻断

**施工内容**：
1. 编辑 `.pre-commit-config.yaml`：移除 `stages: [manual]`，改为常规 hook
2. 编辑 `scripts/governance/d7_code/check_any_abuse.py`：
   - 保留 `--ci` 模式（hard-block）
   - 移除 manual 触发限制
3. 添加 `# noqa: any-abuse` 行级豁免机制（为合理 Any 提供 escape hatch）
4. 更新 `noqa_exempt_registry.yaml`：登记 any-abuse marker
5. 更新 `gate_registry.yaml`：mode 从 manual → block

**验收**：
- `git commit` 新增裸 Any 会被阻断（exit 1）
- 合理 Any 可经 `# noqa: any-abuse` 豁免
- 5.145 维度防复发机制从"建议性 manual"升级为"强制性 commit 阻断"

---

## 四、防复发机制

| 防复发点 | 机制 | 状态 |
|---|---|---|
| 新增裸 Any 阻断 | GATE-ANY-ABUSE 从 manual 升级为 commit 阻断 | 🔒 Phase 3 |
| 合理 Any 豁免 | `# noqa: any-abuse` 行级 marker + noqa_exempt_registry 登记 | 🔒 Phase 3 |
| 类型推断辅助 | `any_type_inferrer.py` 工具永久可用 | 🔒 Phase 1 |
| 存量治理可验证 | 每批 commit 后 manual 触发 GATE-ANY-ABUSE 验证下降 | 🔒 Phase 2 |

---

## 五、向内收原则验证

- **复用 check_any_abuse.py**（已有脚本，仅升级模式），不新建独立检测器
- **复用 noqa_exempt_registry.yaml**（已有豁免登记表），不引入新豁免机制
- **复用 gate_registry.yaml**（已有注册表），仅更新 mode 字段
- **不新建 reconciler**（静态 AST 检测在 commit 时阻断，无需 runtime 事件驱动）

---

## 六、与其他裁定的关系

- **R102（debt_permanent_rulings_r102.md）**：本裁定是对 R102 中 5.145.13-26 的重新审查，其他 46 项 wontfix 保持 R102 裁定不变
- **裁定 3（强制消费链做成 AST 门禁）**：本裁定 Phase 3 把 GATE-ANY-ABUSE 从"建议性 manual"升级为"强制性 commit 阻断"，是裁定 3 的延续
- **#ARCH-WORKTREE-002（session_worktree 四重缺陷治本）**：本裁定治本施工全程使用 session_worktree 流程，继承 #ARCH-WORKTREE-002 的防复发机制

---

## 七、执行计划与里程碑

| 阶段 | 目标 | 预计 session 数 | 依赖 |
|---|---|---|---|
| Phase 1 | 类型推断工具构建 | 1-2 | 无 |
| Phase 2 Batch 1-8 | 分批治理 270 行裸 Any | 5-8 | Phase 1 |
| Phase 3 | GATE-ANY-ABUSE 升级 commit 阻断 | 1 | Phase 2 完成 |
| 验证 | 最终回检 + registry 状态回写 | 1 | Phase 3 |

**执行规则**（继承 R102 + session_worktree 君子协定）：
- 每 phase 每 batch MUST 走 `session_worktree_start` → `session_worktree_commit` → `session_worktree_merge`
- 每 batch MUST 运行单元测试 + mypy 静态检查
- 每 batch 完成后更新 `architecture_debt_registry.md` 5.145 状态行
- 全部完成后更新 §一当前状态摘要 + §四维度表 + §5.145 节
