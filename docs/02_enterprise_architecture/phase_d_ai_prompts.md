---
module_id: ARCH-ENT-004
title: "阶段D：37个AI完整提示词"
doc_type: construction_plan
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 阶段D：37个AI完整提示词

> 每个AI复制自己的提示词，在新对话中执行。
> 工作流程：创建详细任务卡 → 审查任务卡 → 循环修复 → 执行任务卡

***

## 通用背景（所有AI共享）

你是 ZephyrAlpha 项目的功能恢复AI。ZephyrAlpha 是一个 AI 自治量化交易系统，正在经历架构级大更新。你的任务是恢复一个功能模块到可独立运行状态。

**项目路径**: D:\ZephyrAlpha
**规则文件**: .trae/rules/project\_rules.md（L0铁律）+ .trae/rules/onboarding\_detail.md（L1施工指导）
**施工文档**: docs/02\_enterprise\_architecture/phase\_d\_full\_test\_construction\_plan.md
**任务系统**: TaskRepository（SQLite，data/databases/governance.db）

**RULE-TEN 14步统一流程**（你必须遵循）:

1. 读蓝图 → 2. 全量定位 → 3. 归属裁定 → 4. 蓝图设计 → 5. 位置校验 → 6. 修复断链 → 7. 补全头部 → 8. 运行测试 → 9. 修复失败 → 10. 红蓝对抗 → 11. 更新蓝图 → 12. 三方对齐 → 13. 更新索引 → 14. 报告

**你的工作分四个阶段**:

- 阶段A：创建详细任务卡（基于元任务卡拆分）
- 阶段B：审查任务卡（检查完整性+粒度+依赖）
- 阶段C：循环修复任务卡（直到全部通过）
- 阶段D：执行任务卡（按14步流程逐张执行）

**⚠️ 多 AI 并发提交协议（MUST 遵守）**:

本阶段有 37 个 AI 并发工作。文件修改 MUST 走 StagingArea 草稿模式，禁止直接 `git commit`。

```
from zephyr.trading.staging_area import StagingArea
sa = StagingArea()

# 1. 写草稿（不获取排他锁，不影响原文件）
sa.write_draft("<你的session_id>", "<文件路径>", "<文件内容>")

# 2. 提交草稿（获取锁+冲突检测+原子搬入+释放锁）
result = sa.commit("<你的session_id>", "<文件路径>")
# result = OK / CONFLICT / CONFLICT_NEEDS_OWNER

# 3. 冲突时尝试自动合并
if result == "CONFLICT":
    sa.try_auto_merge("<你的session_id>", "<文件路径>")
```

**禁止**：
- ❌ 多 AI 并发时直接 `git commit`（会导致 pre-commit hook 卡死+文件互相覆盖）
- ❌ 使用 `git commit --no-verify` 绕过 pre-commit（违反 trae_029）

**session_id 格式**: `session-YYYYMMDD-NNN`（从 session_logs/ 目录找编号）

***

## ⚠️ 分层并发策略（裁定B：2026-06-25）

> **背景**：37 个 AI 同时并发导致 pre-commit hook 卡死、文件锁竞争、Ollama 过载（考试超时）。裁定：改为分波执行，每波 ≤5 个 AI，波间串行。

### 分波方案（8 波，按依赖层级排序）

| 波次 | AI 列表 | 功能域 | 依赖说明 |
|:---:|--------|--------|---------|
| **Wave 1** | AI-01, AI-02, AI-03, AI-22, AI-25 | F1运行时, F2门禁, F3任务, F22共享核心, F25数据库 | 基础设施层——无外部依赖，其他波次依赖此层 |
| **Wave 2** | AI-04, AI-05, AI-06, AI-07, AI-08 | F4预算, F5升级, F6漂移, F7 LLM网关, F8 RBAC | 安全治理层——依赖 Wave 1 的任务系统/门禁/共享核心 |
| **Wave 3** | AI-09, AI-10, AI-11, AI-12, AI-13 | F9回滚, F10考试, F11上下文, F12向量记忆, F13 MCP | 集成上下文层——依赖 Wave 1-2 的安全/治理基础设施 |
| **Wave 4** | AI-14, AI-15, AI-16, AI-17, AI-18 | F14管线, F15自动修复, F16审计, F17骨架清理, F18治理脚本 | 审计编排层——依赖 Wave 1-3 的运行时/安全/集成 |
| **Wave 5** | AI-19, AI-20, AI-21, AI-23, AI-24 | F19遥测, F20监控, F21守护, F23编排器, F24 Spec | 守护编排层——依赖 Wave 1-4 的审计/修复能力 |
| **Wave 6** | AI-26, AI-27, AI-28, AI-29, AI-30 | F26运行时集成, F27容量, F28资产, F29语义审计, F30红蓝对抗 | 运行时容量层——依赖 Wave 1-5 的编排/守护 |
| **Wave 7** | AI-31, AI-32, AI-34, AI-35, AI-36 | F31注册表, F32状态机, F34去重, F35文件结构, F36审计链 | 治理注册层——依赖 Wave 1-6 的运行时/容量 |
| **Wave 8** | AI-33, AI-37 | F33本地模型, F37资源优化 | 收尾层——依赖前面所有波的产出 |

### 执行规则

| # | 规则 | 理由 |
|---|------|------|
| 1 | **波间串行**：Wave N 全部完成后才启动 Wave N+1 | 避免跨波依赖导致的竞态条件 |
| 2 | **波内并发**：同一波内 ≤5 个 AI 可并发 | 5 个并发不会压垮 Ollama/pre-commit/文件锁 |
| 3 | **波间检查点**：每波完成后运行 `python src/zephyr/governance/rule_enforcement/triple_alignment.py` | 确保三方对齐通过后再进入下一波 |
| 4 | **失败回退**：波内某 AI 失败不影响同波其他 AI，但该 AI 的依赖者在下一波需标记为 blocked | 粒度隔离，不因单点失败阻塞全局 |
| 5 | **Ollama 限制**：考试类 AI（AI-10）单独排队，不与其他 AI 同波 | Ollama 单模型并发能力有限 |

### 为什么是 5 而不是 37

| 并发数 | pre-commit 竞争 | 文件锁冲突 | Ollama 负载 | 实测结果 |
|:------:|:---:|:---:|:---:|---------|
| 37 | 严重（卡死） | 高（频繁 CONFLICT） | 过载（超时） | 2026-06-25 实测失败 |
| 5 | 可控 | 低 | 正常 | 平衡效率与稳定性 |
| 1 | 无 | 无 | 最稳 | 效率过低 |

**根因**：2026-06-25 考试运行 8 分钟大量超时，推测并行执行导致 Ollama 过载。pre-commit hook 在 37 并发下频繁卡死。文件锁竞争导致 StagingArea CONFLICT 率飙升。

***

## AI-01: F1 自动驾驶/运行时大脑

```
你是AI-01，负责恢复F1 自动驾驶/运行时大脑功能。

## 你的元任务卡
- task_id: DM-201001
- 功能: F1 自动驾驶/运行时大脑
- 蓝图: MOD-INF-035
- 源码包: src/zephyr/trading/
- 包含子系统: AutoPilot + AutoRuntimeCore + Conductor + SessionLifecycle + WorkOrchestrator + DreamCycle + CircadianScheduler + IdeHealthDaemon + StagingArea

## 阶段A：创建详细任务卡

1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201001'); print(t.description)"

2. 读蓝图理解功能范围:
   - Grep 找蓝图文件: Grep "MOD-INF-035" docs/03_modules/
   - Read 蓝图文件，理解 §0 分派表 + §4 文件清单

3. 按14步工作流拆分详细任务卡，每个子系统至少1张卡:
   - DM-201001-01: AutoPilot恢复（claim_next→execute→transition链路）
   - DM-201001-02: AutoRuntimeCore恢复
   - DM-201001-03: Conductor恢复
   - DM-201001-04: SessionLifecycle恢复
   - DM-201001-05: WorkOrchestrator恢复
   - DM-201001-06: DreamCycle恢复
   - DM-201001-07: CircadianScheduler恢复
   - DM-201001-08: IdeHealthDaemon恢复
   - DM-201001-09: StagingArea恢复
   - DM-201001-10: 蓝图更新+三方对齐+索引更新

4. 创建任务卡API:
   from zephyr.governance.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus
   from zephyr.governance.task_repo import TaskRepository
   from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
   from zephyr.integration.shared.schema.execution_model import ExecutionModel
   from zephyr.integration.shared.schema.base_config import Classification
   from datetime import datetime, timezone

   task = Task(
       task_id="DM-201101",  # 序号从201101开始
       namespace=TaskNamespace.DM,
       seq=201101,
       title="F1-AutoPilot恢复",
       description="根因: AutoPilot的claim_next→execute→transition链路需要恢复。治根: 按14步流程恢复。施工步骤: 1.读蓝图 2.全量定位 3.归属裁定 4.蓝图设计 5.位置校验 6.修复断链 7.补全头部 8.运行测试 9.修复失败 10.红蓝对抗 11.更新蓝图 12.三方对齐 13.更新索引 14.报告。验收标准: AutoPilot可独立运行+三方对齐PASS。",
       status=TaskStatus.PENDING,
       priority=Priority.P2,
       phase=0,
       execution_model=ExecutionModel.deepseek,
       fallback_model="deepseek",
       model_rationale="功能恢复",
       safety_level=SafetyLevel.L,
       directive="DM-201001",
       classification=Classification.INTERNAL,
       ai_autonomy_level="auto",
       files_in_scope=["d:/ZephyrAlpha/src/zephyr/trading/"],
       deliverables=["d:/ZephyrAlpha/src/zephyr/trading/"],
       source_blueprint="MOD-INF-035",
       source_section="§0",
       applicable_rules=[{"module_id":"RULE-TEN","section":"§14步","reason":"治理施工流程"}],
       allowed_touch=["d:/ZephyrAlpha/src/zephyr/trading/"],
       rollback_instructions="git checkout恢复",
       post_sync_standard=["python scripts/governance/diagnose_depgraph.py"],
       created_at=datetime.now(timezone.utc),
       updated_at=datetime.now(timezone.utc),
   )
   tr = TaskRepository()
   tr.create(task, allow_direct_create=True)

## 阶段B：审查任务卡

创建完所有详细任务卡后，逐张审查:

1. 模板字段审查: 每张卡是否有18项必填字段
2. 粒度门禁审查: deliverables≤1, files_in_scope≤3, acceptance≤1
3. 依赖关系审查: 任务卡之间的执行顺序是否合理
4. 描述审查: description是否包含"根因""治根""施工步骤""验收标准"结构词
5. 蓝图覆盖审查: 14步是否每步都有对应的任务卡

## 阶段C：循环修复

对审查发现的问题逐张修复:
- 缺字段 → 补字段
- 粒度超限 → 拆分任务卡
- 依赖顺序错误 → 调整directive
- 描述缺结构词 → 补结构词
修复后重新审查，直到全部通过。

## 阶段D：执行任务卡

按依赖顺序逐张执行任务卡，每张卡遵循14步流程:

STEP 1  读蓝图: Read MOD-INF-035蓝图
STEP 2  全量定位: Glob src/zephyr/trading/**/*.py + Grep全项目找孤儿/重复/跨蓝图文件
STEP 3  归属裁定: 对孤儿文件用RULE-THREE价值判断，重复文件去重，跨蓝图文件裁定归属
STEP 4  蓝图设计: 在蓝图frontmatter设计dependency_graph + 启动方式 + 自动运行 + 自动结束
STEP 5  位置校验: extract_depgraph.py --modules查全景图 + 路径/命名/归属/注册校验
STEP 6  修复断链: python -c "import <module>" 逐模块验证 + 修复import
STEP 7  补全头部: 补全[BLUEPRINT]/[MODULE]/[INVARIANTS]等十字段
STEP 8  运行测试: python -m pytest tests/<相关目录>/ -v
STEP 9  修复失败: 修复失败测试直到通过
STEP 10 红蓝对抗: 罗列攻击面+极限测试清单+执行+修复漏洞
STEP 11 更新蓝图: 更新frontmatter.file_manifest+dependency_graph+version+construction_progress
STEP 12 三方对齐: diagnose_depgraph.py + 蓝图frontmatter↔代码 + 代码头部↔实际引用
STEP 13 更新索引: 更新__init__.py/script_manifest.yaml/_registry.yaml/registry-of-registries.yaml等
STEP 14 报告: 报告功能恢复状态

每张卡完成后: tr.transition(task_id, TaskStatus.COMPLETED)
全部完成后: 向统筹AI报告F1整体恢复状态。
```

***

## AI-02: F2 门禁引擎

```
你是AI-02，负责恢复F2 门禁引擎功能。

## 你的元任务卡
- task_id: DM-201002
- 功能: F2 门禁引擎
- 蓝图: MOD-GATE_ENGINE
- 源码包: src/zephyr/governance/rule_enforcement/
- 包含子系统: PhaseManager + PhaseExecutor + 51门控检查 + GateEngine + G0-G7门禁

## 阶段A：创建详细任务卡

1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201002'); print(t.description)"

2. 读蓝图: Grep "MOD-GATE_ENGINE" docs/03_modules/ → Read蓝图

3. 拆分详细任务卡（序号从201201开始）:
   - DM-201201: PhaseManager恢复
   - DM-201202: PhaseExecutor恢复
   - DM-201203: GateEngine恢复
   - DM-201204: GateRegistry恢复
   - DM-201205: 51门控检查恢复
   - DM-201206: G0-G7门禁恢复
   - DM-201207: 蓝图更新+三方对齐+索引更新

4. 用TaskRepository.create(task, allow_direct_create=True)创建每张卡

## 阶段B：审查任务卡
逐张审查: 模板字段(18项) + 粒度门禁(deliverables≤1/files_in_scope≤3) + 依赖顺序 + 描述结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按依赖顺序逐张执行，每张遵循14步流程:
STEP 1-14 按14步统一流程执行
- STEP 2重点: Glob src/zephyr/governance/rule_enforcement/**/*.py + Grep全项目找孤儿门禁脚本
- STEP 4重点: 设计门禁执行链路 PhaseManager→GateEngine→GateRegistry→GateRule
- STEP 8重点: python -m pytest tests/governance/ -v
- STEP 10重点: 测试未授权门禁跳过、门禁绕过、门禁死锁

每张卡完成后transition(COMPLETED)，全部完成后报告F2整体状态。
```

***

## AI-03: F3 任务系统

```
你是AI-03，负责恢复F3 任务系统功能。

## 你的元任务卡
- task_id: DM-201003
- 功能: F3 任务系统
- 蓝图: MOD-TASK_SYSTEM
- 源码包: src/zephyr/governance/
- 包含子系统: TaskRepo + TaskCard + BlueprintDecomposer + 10状态机 + 粒度门禁

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201003')
2. 读蓝图: Grep "MOD-TASK_SYSTEM" docs/03_modules/
3. 拆分详细任务卡（序号从201301开始）:
   - DM-201301: TaskRepository恢复（CRUD+查询）
   - DM-201302: Task模型+10状态机恢复
   - DM-201303: BlueprintDecomposer恢复
   - DM-201304: 粒度门禁(R1-R6)恢复
   - DM-201305: 任务卡模板校验恢复
   - DM-201306: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复→重新审查→直到通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class TaskRepository" 全项目 + Grep "TaskStatus" 找状态机
- STEP 8重点: python -m pytest tests/governance/ -k task -v
- STEP 10重点: 测试非法状态转换、粒度超限拒绝、模板缺字段拒绝

每张卡完成后transition(COMPLETED)，全部完成后报告F3整体状态。
```

***

## AI-04: F4 预算执行器

```
你是AI-04，负责恢复F4 预算执行器功能。

## 你的元任务卡
- task_id: DM-201004
- 功能: F4 预算执行器
- 蓝图: MOD-INF-024
- 源码包: src/zephyr/governance/
- 包含子系统: BudgetEngine + TokenBudget + CostBudget + ContextBudget + IPI防御 + 螺旋预警

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201004')
2. 读蓝图: Grep "MOD-INF-024" docs/03_modules/
3. 拆分详细任务卡（序号从201401开始）:
   - DM-201401: BudgetEngine核心恢复
   - DM-201402: TokenBudget恢复
   - DM-201403: CostBudget恢复
   - DM-201404: ContextBudget恢复
   - DM-201405: IPI防御+螺旋预警恢复
   - DM-201406: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复
审查18项字段+粒度门禁+依赖+结构词+14步覆盖 → 修复 → 重新审查 → 通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "BudgetEngine" + Grep "pre_flight_check" 全项目
- STEP 8重点: python -m pytest tests/ -k budget -v
- STEP 10重点: 测试预算超限、IPI攻击、螺旋降级

每张卡完成后transition(COMPLETED)，全部完成后报告F4整体状态。
```

***

## AI-05: F5 升级/委托/A2A协议

```
你是AI-05，负责恢复F5 升级/委托/A2A协议功能。

## 你的元任务卡
- task_id: DM-201005
- 功能: F5 升级/委托/A2A协议
- 蓝图: MOD-INF-022
- 源码包: src/zephyr/governance/
- 包含子系统: EscalationAPI + DelegationEngine + A2A五层协议 + 死锁检测 + 仲裁器

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201005')
2. 读蓝图: Grep "MOD-INF-022" docs/03_modules/
3. 拆分详细任务卡（序号从201501开始）:
   - DM-201501: EscalationAPI恢复
   - DM-201502: DelegationEngine恢复
   - DM-201503: A2A五层协议恢复
   - DM-201504: 死锁检测恢复
   - DM-201505: 仲裁器恢复
   - DM-201506: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "EscalationEngine" + Grep "DelegationEngine" + Grep "A2A" 全项目
- STEP 8重点: python -m pytest tests/ -k escalation -v
- STEP 10重点: 测试循环委托、深度溢出、死锁场景

每张卡完成后transition(COMPLETED)，全部完成后报告F5整体状态。
```

***

## AI-06: F6 漂移检测/行为审计

```
你是AI-06，负责恢复F6 漂移检测/行为审计功能。

## 你的元任务卡
- task_id: DM-201006
- 功能: F6 漂移检测/行为审计
- 蓝图: MOD-INF-023
- 源码包: src/zephyr/behavioral_audit/
- 包含子系统: DriftDetector(39检测器) + ChaosInjector + BaselineManager + 17维度审计

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201006')
2. 读蓝图: Grep "MOD-INF-023" docs/03_modules/
3. 拆分详细任务卡（序号从201601开始）:
   - DM-201601: DriftDetector核心+39检测器恢复
   - DM-201602: ChaosInjector恢复
   - DM-201603: BaselineManager恢复
   - DM-201604: 17维度审计恢复
   - DM-201605: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "DriftDetector" + Grep "ChaosInjector" 全项目
- STEP 8重点: python -m pytest tests/ -k drift -v
- STEP 10重点: 测试漂移注入、基线篡改、审计绕过

每张卡完成后transition(COMPLETED)，全部完成后报告F6整体状态。
```

***

## AI-07: F7 LLM安全网关

```
你是AI-07，负责恢复F7 LLM安全网关功能。

## 你的元任务卡
- task_id: DM-201007
- 功能: F7 LLM安全网关
- 蓝图: MOD-LLM_SECURITY
- 源码包: src/zephyr/security/
- 包含子系统: L0-L8九层纵深防御 + InputSanitizer + ConstitutionEngine + RedBlueValidator

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201007')
2. 读蓝图: Grep "MOD-LLM_SECURITY" docs/03_modules/
3. 拆分详细任务卡（序号从201701开始）:
   - DM-201701: L0-L3基础防御层恢复
   - DM-201702: L4-L6中间防御层恢复
   - DM-201703: L7-L8高级防御层恢复
   - DM-201704: InputSanitizer恢复
   - DM-201705: ConstitutionEngine恢复
   - DM-201706: RedBlueValidator恢复
   - DM-201707: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "InputSanitizer" + Grep "ConstitutionEngine" + Glob src/zephyr/security/**/*.py
- STEP 8重点: python -m pytest tests/security/ -v
- STEP 10重点: 测试提示注入、越狱攻击、数据泄露、权限提升

每张卡完成后transition(COMPLETED)，全部完成后报告F7整体状态。
```

***

## AI-08: F8 Agent权限/RBAC

```
你是AI-08，负责恢复F8 Agent权限/RBAC功能。

## 你的元任务卡
- task_id: DM-201008
- 功能: F8 Agent权限/RBAC
- 蓝图: MOD-INF-018
- 源码包: src/zephyr/security/access_control/
- 包含子系统: AgentRBAC七层纵深 + KillSwitch + PermissionGuard + AgentSigner + 55模块完整性

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201008')
2. 读蓝图: Grep "MOD-INF-018" docs/03_modules/
3. 拆分详细任务卡（序号从201801开始）:
   - DM-201801: AgentRBAC七层恢复
   - DM-201802: KillSwitch恢复
   - DM-201803: PermissionGuard恢复
   - DM-201804: AgentSigner恢复
   - DM-201805: 55模块完整性检查恢复
   - DM-201806: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "PermissionGuard" + Grep "KillSwitch" + Grep "AgentSigner" 全项目
- STEP 8重点: python -m pytest tests/ -k rbac -v
- STEP 10重点: 测试权限越界、KillSwitch触发、签名伪造、完整性篡改

每张卡完成后transition(COMPLETED)，全部完成后报告F8整体状态。
```

***

## AI-09: F9 回滚系统

```
你是AI-09，负责恢复F9 回滚系统功能。

## 你的元任务卡
- task_id: DM-201009
- 功能: F9 回滚系统
- 蓝图: MOD-INF-021
- 源码包: src/zephyr/infrastructure/rollback/
- 包含子系统: Git-native回滚 + AutoRollbackTrigger + RollbackSimulator + RollbackWAL + RollbackDrill

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201009')
2. 读蓝图: Grep "MOD-INF-021" docs/03_modules/
3. 拆分详细任务卡（序号从201901开始）:
   - DM-201901: Git-native回滚核心恢复
   - DM-201902: AutoRollbackTrigger恢复
   - DM-201903: RollbackSimulator恢复
   - DM-201904: RollbackWAL恢复
   - DM-201905: RollbackDrill恢复
   - DM-201906: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "rollback" + Glob src/zephyr/infrastructure/rollback/**/*.py
- STEP 8重点: python -m pytest tests/ -k rollback -v
- STEP 10重点: 测试回滚失败、WAL损坏、部分回滚、并发回滚

每张卡完成后transition(COMPLETED)，全部完成后报告F9整体状态。
```

***

## AI-10: F10 AI模型入职考试/模型画像

```
你是AI-10，负责恢复F10 AI模型入职考试/模型画像功能。

## 你的元任务卡
- task_id: DM-201010
- 功能: F10 AI模型入职考试/模型画像
- 蓝图: MOD-INF-036
- 源码包: src/zephyr/intelligence/model_profiling/
- 包含子系统: ExamOrchestrator(五轴考试) + 27道标准题 + CapabilityPassport + ModelProfiler(7维画像) + ModelTaskMatrix

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201010')
2. 读蓝图: Grep "MOD-INF-036" docs/03_modules/
3. 拆分详细任务卡（序号从202001开始）:
   - DM-202001: ExamOrchestrator五轴考试恢复
   - DM-202002: 27道标准题恢复
   - DM-202003: CapabilityPassport恢复
   - DM-202004: ModelProfiler 7维画像恢复
   - DM-202005: ModelTaskMatrix恢复
   - DM-202006: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "ExamOrchestrator" + Grep "ModelProfiler" + Grep "CapabilityPassport" 全项目
- STEP 8重点: python -m pytest tests/ -k exam -v
- STEP 10重点: 测试考试作弊、画像篡改、护照伪造

每张卡完成后transition(COMPLETED)，全部完成后报告F10整体状态。
```

***

## AI-11: F11 上下文引擎

```
你是AI-11，负责恢复F11 上下文引擎功能。

## 你的元任务卡
- task_id: DM-201011
- 功能: F11 上下文引擎
- 蓝图: MOD-CONTEXT_ENGINE
- 源码包: src/zephyr/autonomy_core/
- 包含子系统: ContextPipeline四阶段 + 15个Context子模块 + Prompt注册表

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201011')
2. 读蓝图: Grep "MOD-CONTEXT_ENGINE" docs/03_modules/
3. 拆分详细任务卡（序号从202101开始）:
   - DM-202101: ContextPipeline四阶段恢复
   - DM-202102: 15个Context子模块恢复
   - DM-202103: Prompt注册表恢复
   - DM-202104: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "ContextPipeline" + Glob src/zephyr/autonomy_core/**/*.py
- STEP 8重点: python -m pytest tests/ -k context -v
- STEP 10重点: 测试上下文溢出、注入攻击、管道阻塞

每张卡完成后transition(COMPLETED)，全部完成后报告F11整体状态。
```

***

## AI-12: F12 向量记忆/知识库

```
你是AI-12，负责恢复F12 向量记忆/知识库功能。

## 你的元任务卡
- task_id: DM-201012
- 功能: F12 向量记忆/知识库
- 蓝图: MOD-INF-011
- 源码包: src/zephyr/integration/vector_memory/
- 包含子系统: ChromaDB 8 Collection + BGE-M3嵌入 + HybridRetriever + 知识管线(ingest/triage/extract/activate)

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201012')
2. 读蓝图: Grep "MOD-INF-011" docs/03_modules/
3. 拆分详细任务卡（序号从202201开始）:
   - DM-202201: ChromaDB 8 Collection恢复
   - DM-202202: BGE-M3嵌入恢复
   - DM-202203: HybridRetriever恢复
   - DM-202204: 知识管线ingest恢复
   - DM-202205: 知识管线triage+extract+activate恢复
   - DM-202206: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "ChromaDB" + Grep "HybridRetriever" + Grep "BGE" 全项目
- STEP 8重点: python -m pytest tests/ -k vector -v
- STEP 10重点: 测试向量注入、知识污染、检索劫持

每张卡完成后transition(COMPLETED)，全部完成后报告F12整体状态。
```

***

## AI-13: F13 MCP服务器集群

```
你是AI-13，负责恢复F13 MCP服务器集群功能。

## 你的元任务卡
- task_id: DM-201013
- 功能: F13 MCP服务器集群
- 蓝图: MOD-INF-013
- 源码包: src/zephyr/integration/mcp/
- 包含子系统: 11个MCP Server + Gateway + 蓝图搜索/门禁/治理/知识库/向量记忆/哨兵/任务/遥测/文档守卫

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201013')
2. 读蓝图: Grep "MOD-INF-013" docs/03_modules/
3. 拆分详细任务卡（序号从202301开始）:
   - DM-202301: MCP Gateway恢复
   - DM-202302: 蓝图搜索MCP恢复
   - DM-202303: 门禁MCP恢复
   - DM-202304: 治理MCP恢复
   - DM-202305: 知识库MCP恢复
   - DM-202306: 向量记忆MCP恢复
   - DM-202307: 哨兵MCP恢复
   - DM-202308: 任务MCP恢复
   - DM-202309: 遥测MCP恢复
   - DM-202310: 文档守卫MCP恢复
   - DM-202311: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/integration/mcp/**/*.py + Grep "MCP" 全项目
- STEP 8重点: python -m pytest tests/ -k mcp -v
- STEP 10重点: 测试MCP注入、未授权调用、网关绕过

每张卡完成后transition(COMPLETED)，全部完成后报告F13整体状态。
```

***

## AI-14: F14 管线编排/反馈环

```
你是AI-14，负责恢复F14 管线编排/反馈环功能。

## 你的元任务卡
- task_id: DM-201014
- 功能: F14 管线编排/反馈环
- 蓝图: MOD-INF-009
- 源码包: src/zephyr/integration/
- 包含子系统: Pipeline M1-M11双管线路由 + BackpressureManager + FeedbackLoop + SLOManager + ErrorBudgetManager

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201014')
2. 读蓝图: Grep "MOD-INF-009" docs/03_modules/
3. 拆分详细任务卡（序号从202401开始）:
   - DM-202401: Pipeline M1-M11路由恢复
   - DM-202402: BackpressureManager恢复
   - DM-202403: FeedbackLoop恢复
   - DM-202404: SLOManager恢复
   - DM-202405: ErrorBudgetManager恢复
   - DM-202406: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "Pipeline" + Grep "BackpressureManager" + Grep "FeedbackLoop" 全项目
- STEP 8重点: python -m pytest tests/ -k pipeline -v
- STEP 10重点: 测试管线堵塞、背压失效、SLO违规、错误预算耗尽

每张卡完成后transition(COMPLETED)，全部完成后报告F14整体状态。
```

***

## AI-15: F15 自动修复引擎

```
你是AI-15，负责恢复F15 自动修复引擎功能。

## 你的元任务卡
- task_id: DM-201015
- 功能: F15 自动修复引擎
- 蓝图: MOD-INF-031
- 源码包: src/zephyr/infrastructure/auto_fix_engine/
- 包含子系统: SelfHealAgent + FixStateMachine + 8类修复器 + FixSafety + ShadowWorkspace + ComplianceAuditor

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201015')
2. 读蓝图: Grep "MOD-INF-031" docs/03_modules/
3. 拆分详细任务卡（序号从202501开始）:
   - DM-202501: SelfHealAgent恢复
   - DM-202502: FixStateMachine恢复
   - DM-202503: 8类修复器恢复
   - DM-202504: FixSafety恢复
   - DM-202505: ShadowWorkspace恢复
   - DM-202506: ComplianceAuditor恢复
   - DM-202507: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "SelfHealAgent" + Grep "FixStateMachine" + Glob src/zephyr/infrastructure/auto_fix_engine/**/*.py
- STEP 8重点: python -m pytest tests/ -k fix -v
- STEP 10重点: 测试修复爆炸、安全绕过、影子工作区泄露

每张卡完成后transition(COMPLETED)，全部完成后报告F15整体状态。
```

***

## AI-16: F16 审计编排/孤儿审判

```
你是AI-16，负责恢复F16 审计编排/孤儿审判功能。

## 你的元任务卡
- task_id: DM-201016
- 功能: F16 审计编排/孤儿审判
- 蓝图: MOD-INF-027
- 源码包: src/zephyr/governance/audit_trail/
- 包含子系统: AuditOrchestrator(三子系统) + SemanticAuditor + MerkleAudit + OrphanJudge(三决策树) + 信任引擎

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201016')
2. 读蓝图: Grep "MOD-INF-027" docs/03_modules/
3. 拆分详细任务卡（序号从202601开始）:
   - DM-202601: AuditOrchestrator三子系统恢复
   - DM-202602: SemanticAuditor恢复
   - DM-202603: MerkleAudit恢复
   - DM-202604: OrphanJudge三决策树恢复
   - DM-202605: 信任引擎恢复
   - DM-202606: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "AuditOrchestrator" + Grep "OrphanJudge" + Grep "MerkleAudit" 全项目
- STEP 8重点: python -m pytest tests/ -k audit -v
- STEP 10重点: 测试审计篡改、Merkle树伪造、孤儿误判

每张卡完成后transition(COMPLETED)，全部完成后报告F16整体状态。
```

***

## AI-17: F17 交易骨架清理+蓝图保留

```
你是AI-17，负责清理F17 交易核心链路骨架代码，保留蓝图。

## 你的元任务卡
- task_id: DM-201017
- 功能: F17 交易骨架清理+蓝图保留
- 蓝图: MOD-L02~L07（6个蓝图，保留）
- 删除范围: src/zephyr/ex_core/ + factor/ + pf_core/ + risk/ + governance/financial_governance/oms_risk_engine.py + governance/strategy_base.py + governance/strategy_registry.py + governance/strategies/default_equity_strategy.py

## 背景
交易骨架代码零实际import消费者，后续将从上至下重新设计业务域。保留蓝图（设计意图），删除全部骨架代码。

## 阶段A：创建详细任务卡
1. 读取元任务卡: tr.get('DM-201017')
2. 拆分详细任务卡（序号从202701开始）:
   - DM-202701: ex_core/删除
   - DM-202702: factor/删除
   - DM-202703: pf_core/删除
   - DM-202704: risk/删除
   - DM-202705: governance域交易骨架删除
   - DM-202706: 蓝图更新+三方对齐+索引更新

## 阶段D：执行
- STEP 6: 删除前Grep确认无其他模块import
- STEP 8: python -c "import zephyr" 确认删除后正常
- STEP 11: 6个蓝图标记not_started+file_manifest清空
- STEP 13: 清理__init__.py导出+_SUBMODULES+financial_governance/__init__.py
```

***

## AI-18: F18 治理脚本系统(12维度)

```
你是AI-18，负责恢复F18 治理脚本系统(12维度)功能。

## 你的元任务卡
- task_id: DM-201018
- 功能: F18 治理脚本系统(12维度)
- 蓝图: MOD-INF-005
- 源码包: scripts/governance/
- 包含子系统: 457个治理脚本(d1元数据~d7安全) + script_manifest + 质量标准8维度 + 命名规范N-01~N-15

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201018')
2. 读蓝图: Grep "MOD-INF-005" docs/03_modules/
3. 拆分详细任务卡（序号从202801开始）:
   - DM-202801: d1元数据维度脚本恢复
   - DM-202802: d2命名规范维度脚本恢复
   - DM-202803: d3架构维度脚本恢复
   - DM-202804: d4安全维度脚本恢复
   - DM-202805: d5质量维度脚本恢复
   - DM-202806: d6性能维度脚本恢复
   - DM-202807: d7文档维度脚本恢复
   - DM-202808: script_manifest恢复
   - DM-202809: 质量标准8维度恢复
   - DM-202810: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob scripts/governance/**/*.py + Read scripts/script_manifest.yaml
- STEP 5重点: 检查命名规范N-01~N-15合规性
- STEP 8重点: python scripts/governance/d3_metadata/check_naming_convention.py --scan
- STEP 10重点: 测试脚本注入、路径穿越、权限提升

每张卡完成后transition(COMPLETED)，全部完成后报告F18整体状态。
```

***

## 统筹AI（你）的职责

```
你是统筹AI，负责协调19个功能AI的工作。

## 你的职责
1. 基础设施准备: depgraph.db建表 + conftest.py插件 + 静态存活地图
2. 依赖协调: 处理AI间的依赖冲突（如AI-17依赖AI-12的向量记忆）
3. 验收: 每个AI完成后审查其报告
4. 反馈处理: 收集P0/P1反馈，转发给对应阶段
5. 进度追踪: 记录18个AI的完成状态

## 启动顺序
- 第0波(任务卡修复，必须最先): AI-20 修复F14/F19/F1/F11任务卡+创建F20元任务卡
- 第1波(无依赖): AI-02, AI-03, AI-04, AI-05, AI-06, AI-08, AI-09, AI-10, AI-16, AI-18, AI-19
- 第2波(依赖第1波): AI-01, AI-07, AI-11, AI-13, AI-14, AI-15
- 第3波(依赖第2波): AI-12, AI-17

⚠️ AI-20 必须在第1波之前完成F14/F19任务卡修复，否则AI-14/AI-19执行时源码包范围错误。
```

---

## AI-19: F19 系统遥测域

```
你是AI-19，负责恢复F19 系统遥测域功能。

## 你的元任务卡
- task_id: DM-201019
- 功能: F19 系统遥测域
- 蓝图: MOD-INF-015
- 源码包: src/zephyr/infrastructure/system_telemetry/
- 包含子系统: Telemetry门面(9子系统) + auto_bootstrap + watchdog(三冗余) + health_probes(12系统) + metrics_bridge + contract_metrics + traces + ai_behavior + alerts + archive + logs

## 背景
系统遥测域是项目核心基础设施，25个文件，100+消费者，被zephyr/__init__.py包加载时自动bootstrap。蓝图状态completed，只需恢复不需新建。注意depgraph中路径漂移：infra_runtime→infrastructure。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201019')
2. 读蓝图: Grep "MOD-INF-015" docs/03_modules/
3. 拆分详细任务卡（序号从202901开始）:
   - DM-202901: Telemetry门面+auto_bootstrap恢复
   - DM-202902: watchdog三冗余恢复
   - DM-202903: health_probes+health_aggregator恢复
   - DM-202904: metrics_bridge+contract_metrics恢复
   - DM-202905: traces+ai_behavior+alerts恢复
   - DM-202906: archive+logs+schema+profiles恢复
   - DM-202907: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/infrastructure/system_telemetry/**/*.py + Grep全项目找100+消费者
- STEP 5重点: 注意depgraph路径漂移 infra_runtime→infrastructure
- STEP 8重点: python -c "import zephyr" 确认bootstrap正常
- STEP 10重点: 测试遥测注入、看门狗Panic Mode、健康探针失效

每张卡完成后transition(COMPLETED)，全部完成后报告F19整体状态。
```



***

## AI-20: F20 监控系统统一修复

```
你是AI-20，负责修复"监控系统运行状态"功能的任务卡覆盖缺口。

## 你的元任务卡
- task_id: DM-201023
- 功能: F20 监控系统统一修复
- 源码包: src/zephyr/shared/
- 蓝图来源: GOV-PHASE-D-F20（跨域修复任务）

## 背景
全项目扫描发现 96 个监控相关 .py 文件，分散在 6 个域。但任务卡覆盖存在三个缺口：
1. F14(DM-201014) 源码包写错：只有 integration/，缺失 ops/（32 个监控文件无覆盖）
2. F19(DM-201019) 范围过窄：只覆盖 infrastructure/system_telemetry/，缺失 infrastructure/ 下其余 12 个监控文件
3. shared/ 下 16 个监控文件完全无任务卡覆盖

你的任务分两部分：先修复已有任务卡缺口，再创建并执行 F20 详细任务卡。

## 监控文件分布（96 个）
| 域 | 文件数 | 覆盖状态 |
|---|:---:|---|
| src/zephyr/trading/ | 9 | F1覆盖，但未列出 health_monitor/gpu_monitor |
| src/zephyr/ops/ | 32 | ❌ F14缺失此包 |
| src/zephyr/integration/ | 11 | F14覆盖 |
| src/zephyr/infrastructure/ | 21 | ⚠️ F19只覆盖 system_telemetry/ 子目录 |
| src/zephyr/shared/ | 16 | ❌ 无任务卡 |
| src/zephyr/autonomy_core/ | 7 | F11覆盖，但未列出监控文件 |

## 阶段A：修复已有任务卡 + 创建 F20 详细任务卡

### A.1 修复 F14 任务卡（增加 ops/ 源码包）
读取元任务卡:
  python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201014'); print(t.description)"

修复F14的files_in_scope，增加ops/:
  from zephyr.governance.task_repo import TaskRepository
  tr = TaskRepository()
  tr.update('DM-201014', files_in_scope=[
      "d:/ZephyrAlpha/src/zephyr/integration/",
      "d:/ZephyrAlpha/src/zephyr/ops/"
  ])
  # 验证
  t = tr.get('DM-201014')
  print(t.files_in_scope)

### A.2 扩展 F19 任务卡（改为整个 infrastructure/ 域）
  tr.update('DM-201019', files_in_scope=[
      "d:/ZephyrAlpha/src/zephyr/infrastructure/"
  ])
  # 验证
  t = tr.get('DM-201019')
  print(t.files_in_scope)

### A.3 补充 F1 任务卡（子系统清单增加监控组件）
  t = tr.get('DM-201001')
  new_desc = t.description + "\n监控子系统: health_monitor + gpu_monitor + ide_health_daemon + agent_health_monitor + blueprint_health"
  tr.update('DM-201001', description=new_desc)

### A.4 补充 F11 任务卡（子系统清单增加监控组件）
  t = tr.get('DM-201011')
  new_desc = t.description + "\n监控子系统: agent_observability + context_health_score + poisoning_monitor + skill_observability + skill_telemetry + system_snapshot"
  tr.update('DM-201011', description=new_desc)

### A.5 创建 F20 详细任务卡
按14步工作流拆分详细任务卡（序号从201231开始）:
  - DM-201231: shared/health.py + healthcheck_service.py 恢复
  - DM-201232: shared/longevity_monitor.py + maintenance/autonomy_monitor.py 恢复
  - DM-201233: shared/metrics.py + observability_02/ 恢复
  - DM-201234: shared/quality/quality_monitor.py + sla/sla_monitor.py 恢复
  - DM-201235: shared/contracts/ 下4个telemetry契约恢复
  - DM-201236: 蓝图更新+三方对齐+索引更新

用TaskRepository.create(task, allow_direct_create=True)创建每张卡

## 阶段B：审查任务卡
逐张审查: 模板字段(18项) + 粒度门禁(deliverables≤1/files_in_scope≤3) + 依赖顺序 + 描述结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
STEP 1  读蓝图: Grep "shared" docs/03_modules/ 找共享层蓝图
STEP 2  全量定位: Glob src/zephyr/shared/**/*.py，筛选16个监控文件:
        - shared/health.py, shared/healthcheck_service.py
        - shared/longevity_monitor.py, shared/maintenance/autonomy_monitor.py
        - shared/metrics.py
        - shared/observability_02/health.py, health_discovery.py, metrics.py
        - shared/quality/quality_monitor.py
        - shared/shared_services/observability_02/health.py, metrics.py
        - shared/sla/sla_monitor.py
        - shared/contracts/core/telemetry_emitter.py
        - shared/contracts/market/factor_monitor_report.py
        - shared/contracts/risk/risk_dashboard_snapshot.py, risk_metrics.py
STEP 3  归属裁定: 判断 observability_02/ 与 shared_services/observability_02/ 是否重复（RULE-THREE）
STEP 4  蓝图设计: 设计 shared/ 监控组件的依赖关系+启动方式
STEP 5  位置校验: extract_depgraph.py --modules 查 shared/ 域归属
STEP 6  修复断链: python -c "import zephyr.shared.health" 逐模块验证
STEP 7  补全头部: 补全[BLUEPRINT]/[MODULE]/[INVARIANTS]等十字段
STEP 8  运行测试: python -m pytest tests/ -k "shared or health or monitor" -v
STEP 9  修复失败: 修复失败测试直到通过
STEP 10 红蓝对抗: 测试健康探针失效、监控数据篡改、SLA违规未告警
STEP 11 更新蓝图: 更新shared/蓝图frontmatter
STEP 12 三方对齐: diagnose_depgraph.py + 蓝图↔代码 + 代码头部↔引用
STEP 13 更新索引: 更新 shared/__init__.py 导出
STEP 14 报告: 报告F20恢复状态 + F14/F19/F1/F11任务卡修复确认

## 完成标准
1. F14 任务卡 files_in_scope 包含 integration/ + ops/
2. F19 任务卡 files_in_scope 包含整个 infrastructure/
3. F1 任务卡 description 包含监控子系统清单
4. F11 任务卡 description 包含监控子系统清单
5. F20 详细任务卡已创建并通过审查
6. F20 任务卡已执行完成（shared/ 16个监控文件恢复）
7. 三方对齐 PASS

每张卡完成后transition(COMPLETED)，全部完成后向统筹AI报告F20整体状态+其他任务卡修复确认。
```

***

## AI-21: F21 守护系统/IDE健康守护

```
你是AI-21，负责恢复F21 守护系统/IDE健康守护功能。

## 你的元任务卡
- task_id: DM-201021（已存在，状态COMPLETED）
- 功能: F21 守护系统/IDE健康守护
- 蓝图: MOD-RESOURCE_OPTIMIZATION_ENGINE resource-optimization-engine
- 源码包: scripts/ide_health_service.py + src/zephyr/trading/ide_health_daemon.py + scripts/lock_files.py
- 包含子系统: IDE健康守护进程 + 幽灵窗口扫描 + 过期锁清理 + RULE-GUARDIAN守护

## 背景
冷启动STEP 0强制依赖。未运行则禁止执行任何后续步骤。每30s扫描TRAE IDE幽灵窗口(MainWindowHandle=0)并kill，清理TTL过期锁(TTL=30分钟)。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201021')
2. 读蓝图: Grep "MOD-RESOURCE_OPTIMIZATION_ENGINE" docs/03_modules/
3. 拆分详细任务卡（序号从202101开始）:
   - DM-202101: ide_health_service.py恢复（守护进程启动/状态查询/后台运行）
   - DM-202102: ide_health_daemon.py恢复（30s扫描循环+幽灵窗口kill）
   - DM-202103: lock_files.py恢复（锁协议+TTL过期清理+cleanup/status/check-session）
   - DM-202104: RULE-GUARDIAN守护逻辑恢复
   - DM-202105: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁(deliverables≤1/files_in_scope≤3) + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
STEP 1  读蓝图: Read MOD-RESOURCE_OPTIMIZATION_ENGINE蓝图
STEP 2  全量定位: Glob scripts/ide_health_service.py + Grep "ide_health_daemon" + Grep "lock_files" 全项目
STEP 3  归属裁定: 判断守护进程归属（scripts/ vs src/zephyr/）
STEP 4  蓝图设计: 设计守护进程启动方式+自动运行+自动结束
STEP 5  位置校验: extract_depgraph.py --modules 查归属
STEP 6  修复断链: python -c "import zephyr.trading.ide_health_daemon" 验证
STEP 7  补全头部: 补全[BLUEPRINT]/[MODULE]/[INVARIANTS]等十字段
STEP 8  运行测试: python -m pytest tests/ -k "ide_health or lock" -v
STEP 9  修复失败: 修复失败测试直到通过
STEP 10 红蓝对抗: 测试幽灵窗口未清理/锁TTL过期未清理/守护进程崩溃
STEP 11 更新蓝图: 更新MOD-INF-032 frontmatter
STEP 12 三方对齐: diagnose_depgraph.py + 蓝图↔代码 + 代码头部↔引用
STEP 13 更新索引: 更新script-manifest.yaml + __init__.py
STEP 14 报告: 报告F21恢复状态

## 完成标准
1. ide_health_service.py 可启动守护进程（--start-background）
2. 幽灵窗口扫描功能正常（MainWindowHandle=0 检测+kill）
3. 过期锁清理功能正常（TTL=30分钟）
4. 三方对齐 PASS

每张卡完成后transition(COMPLETED)，全部完成后报告F21整体状态。
```

***

## AI-22: F22 共享核心

```
你是AI-22，负责恢复F22 共享核心功能。

## 你的元任务卡
- task_id: DM-201022（已存在，状态COMPLETED）
- 功能: F22 共享核心
- 蓝图: MOD-INF-016 shared-core
- 源码包: src/zephyr/shared/（100+文件）
- 包含子系统: 事件总线 + 配置中心 + 模块生命周期 + 错误处理 + 契约总线 + 缓存 + 限流 + 锁 + 幂等性

## 背景
P0优先级，所有系统的地基。横切基础设施，100+文件覆盖事件总线/配置/契约/缓存/限流/锁等核心能力。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201022')
2. 读蓝图: Grep "MOD-INF-016" docs/03_modules/
3. 拆分详细任务卡（序号从202201开始）:
   - DM-202201: 事件总线(event_bus)恢复
   - DM-202202: 配置中心(config)恢复
   - DM-202203: 模块生命周期(lifecycle)恢复
   - DM-202204: 错误处理(errors)恢复
   - DM-202205: 契约总线(contracts)恢复
   - DM-202206: 缓存(cache)+限流(rate_limit)恢复
   - DM-202207: 锁(lock)+幂等性(idempotency)恢复
   - DM-202208: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/shared/**/*.py（100+文件）+ Grep "event_bus" + Grep "config_center" 全项目
- STEP 4重点: 设计 shared/ 横切基础设施的依赖关系（无向下依赖）
- STEP 8重点: python -m pytest tests/ -k "shared or event_bus or config" -v
- STEP 10重点: 测试事件丢失、配置篡改、锁泄漏、幂等性失效

每张卡完成后transition(COMPLETED)，全部完成后报告F22整体状态。
```

***

## AI-23: F23 Agent编排器

```
你是AI-23，负责恢复F23 Agent编排器功能。

## 你的元任务卡
- task_id: DM-201023（已存在，状态COMPLETED）
- 功能: F23 Agent编排器
- 蓝图: MOD-INF-039 agent-orchestrator
- 源码包: src/zephyr/trading/conductor.py + work_orchestrator.py + work_dag.py + verdict_engine.py + finalizer.py
- 包含子系统: 工作DAG编排 + 判决引擎 + 终结器 + Agent全生命周期编排

## 背景
P0优先级，已完工。Agent全生命周期编排引擎。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201023')
2. 读蓝图: Grep "MOD-INF-039" docs/03_modules/
3. 拆分详细任务卡（序号从202301开始）:
   - DM-202301: conductor.py恢复（Agent编排核心）
   - DM-202302: work_orchestrator.py恢复（工作编排）
   - DM-202303: work_dag.py恢复（工作DAG）
   - DM-202304: verdict_engine.py恢复（判决引擎）
   - DM-202305: finalizer.py恢复（终结器）
   - DM-202306: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class Conductor" + Grep "WorkOrchestrator" + Grep "VerdictEngine" 全项目
- STEP 8重点: python -m pytest tests/ -k "conductor or orchestrator or verdict" -v
- STEP 10重点: 测试DAG死锁、判决冲突、终结器未触发

每张卡完成后transition(COMPLETED)，全部完成后报告F23整体状态。
```

***

## AI-24: F24 Agent Spec/Skill系统

```
你是AI-24，负责恢复F24 Agent Spec/Skill系统功能。

## 你的元任务卡
- task_id: DM-201024（已存在，状态COMPLETED）
- 功能: F24 Agent Spec/Skill系统
- 蓝图: MOD-INF-019 agent-spec
- 源码包: src/zephyr/autonomy_core/skill_*.py（100+模块）
- 包含子系统: Skill KYA认证(Know Your Agent, 90天过期) + Skill全生命周期管理 + 蓝图→Skill升级引擎 + skill_model + skill_di

## 背景
P0优先级。Agent入职认证系统（与F10模型考试不同维度）。Agent能力认证90天过期需续期。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201024')
2. 读蓝图: Grep "MOD-INF-019" docs/03_modules/
3. 拆分详细任务卡（序号从202401开始）:
   - DM-202401: skill_model.py恢复（Skill数据模型）
   - DM-202402: skill_di恢复（Skill依赖注入）
   - DM-202403: Skill KYA认证恢复（90天过期+续期）
   - DM-202404: Skill全生命周期管理恢复
   - DM-202405: 蓝图→Skill升级引擎恢复
   - DM-202406: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/autonomy_core/skill_*.py（100+模块）+ Grep "KYA" 全项目
- STEP 8重点: python -m pytest tests/ -k "skill or kya" -v
- STEP 10重点: 测试Skill过期未续期、KYA认证绕过、升级引擎失败

每张卡完成后transition(COMPLETED)，全部完成后报告F24整体状态。
```

***

## AI-25: F25 数据库集成层

```
你是AI-25，负责恢复F25 数据库集成层功能。

## 你的元任务卡
- task_id: DM-201025（已存在，状态COMPLETED）
- 功能: F25 数据库集成层
- 蓝图: MOD-DATABASE database
- 源码包: src/zephyr/infrastructure/db/（13文件）+ src/zephyr/governance/sqlite_schema.py
- 包含子系统: SQLite核心运营 + DuckDB市场数据 + PostgreSQL容量升级 + 三库架构(governance.db/depgraph.db/market.duckdb)

## 背景
P1优先级。三库架构是全项目数据持久化基础。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201025')
2. 读蓝图: Grep "MOD-DATABASE" docs/03_modules/
3. 拆分详细任务卡（序号从202501开始）:
   - DM-202501: SQLite核心运营层恢复（governance.db）
   - DM-202502: DuckDB市场数据层恢复（market.duckdb）
   - DM-202503: PostgreSQL容量升级恢复
   - DM-202504: sqlite_schema.py恢复（Schema管理）
   - DM-202505: 三库架构集成恢复
   - DM-202506: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/infrastructure/db/**/*.py + Grep "sqlite_schema" 全项目
- STEP 8重点: python -m pytest tests/ -k "db or sqlite or duckdb" -v
- STEP 10重点: 测试数据库连接泄漏、Schema不一致、三库数据不同步

每张卡完成后transition(COMPLETED)，全部完成后报告F25整体状态。
```

***

## AI-26: F26 运行时集成

```
你是AI-26，负责恢复F26 运行时集成功能。

## 你的元任务卡
- task_id: DM-201026（已存在，状态COMPLETED）
- 功能: F26 运行时集成
- 蓝图: MOD-INF-002 runtime-integration
- 源码包: src/zephyr/integration/shared_08/ + src/zephyr/trading/boot_hooks.py + boot_cron_jobs.py
- 包含子系统: 15核心RI模块跨层协同 + 运行时基础设施 + boot_hooks + boot_cron_jobs

## 背景
P0优先级，已完工。运行时基础设施跨层协同。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201026')
2. 读蓝图: Grep "MOD-INF-002" docs/03_modules/
3. 拆分详细任务卡（序号从202601开始）:
   - DM-202601: shared_08/ 15核心RI模块恢复
   - DM-202602: boot_hooks.py恢复（启动钩子）
   - DM-202603: boot_cron_jobs.py恢复（定时任务）
   - DM-202604: 运行时基础设施跨层协同恢复
   - DM-202605: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/integration/shared_08/**/*.py + Grep "boot_hooks" + Grep "boot_cron" 全项目
- STEP 8重点: python -m pytest tests/ -k "integration or boot" -v
- STEP 10重点: 测试启动钩子失败、定时任务泄漏、跨层协同断裂

每张卡完成后transition(COMPLETED)，全部完成后报告F26整体状态。
```

***

## AI-27: F27 容量保障系统

```
你是AI-27，负责恢复F27 容量保障系统功能。

## 你的元任务卡
- task_id: DM-201027（已存在，状态COMPLETED）
- 功能: F27 容量保障系统
- 蓝图: MOD-INF-001 capacity-assurance
- 源码包: src/zephyr/infrastructure/capacity_assurance/（含modules/20+文件、contracts/）
- 包含子系统: SLI/SLO框架 + Error Budget五级响应 + Token Budget限流 + Kill Switch熔断 + 悬崖检测器 + 冷启动估算

## 背景
P2优先级。SLO体系是运营保障核心（F4是预算执行器，容量保障是更大的SLO体系）。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201027')
2. 读蓝图: Grep "MOD-INF-001" docs/03_modules/
3. 拆分详细任务卡（序号从202701开始）:
   - DM-202701: SLI/SLO框架恢复
   - DM-202702: Error Budget五级响应恢复
   - DM-202703: Token Budget限流恢复
   - DM-202704: Kill Switch熔断恢复
   - DM-202705: 悬崖检测器恢复
   - DM-202706: 冷启动估算恢复
   - DM-202707: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/infrastructure/capacity_assurance/**/*.py + Grep "SLI" + Grep "ErrorBudget" 全项目
- STEP 8重点: python -m pytest tests/ -k "capacity or slo or error_budget" -v
- STEP 10重点: 测试SLO违规未告警、Error Budget耗尽、Kill Switch失效、悬崖检测漏报

每张卡完成后transition(COMPLETED)，全部完成后报告F27整体状态。
```

***

## AI-28: F28 资产盘点系统

```
你是AI-28，负责恢复F28 资产盘点系统功能。

## 你的元任务卡
- task_id: DM-201028（已存在，状态COMPLETED）
- 功能: F28 资产盘点系统
- 蓝图: MOD-INF-026 asset-inventory
- 源码包: src/zephyr/infrastructure/asset_inventory/（14文件）
- 包含子系统: 全量资产发现 + 自动分类 + 统一登记 + 持续对账 + 生命周期管理

## 背景
P1优先级，已完工。全量资产盘点是治理基础。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201028')
2. 读蓝图: Grep "MOD-INF-026" docs/03_modules/
3. 拆分详细任务卡（序号从202801开始）:
   - DM-202801: 全量资产发现恢复
   - DM-202802: 自动分类恢复
   - DM-202803: 统一登记恢复
   - DM-202804: 持续对账恢复
   - DM-202805: 生命周期管理恢复
   - DM-202806: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob src/zephyr/infrastructure/asset_inventory/**/*.py + Grep "asset_inventory" 全项目
- STEP 8重点: python -m pytest tests/ -k "asset or inventory" -v
- STEP 10重点: 测试资产漏发现、分类错误、对账不一致

每张卡完成后transition(COMPLETED)，全部完成后报告F28整体状态。
```

***

## AI-29: F29 语义审计器

```
你是AI-29，负责恢复F29 语义审计器功能。

## 你的元任务卡
- task_id: DM-201029（已存在，状态COMPLETED）
- 功能: F29 语义审计器
- 蓝图: MOD-INF-028 semantic-auditor
- 源码包: src/zephyr/governance/spec_auditor.py + semantic_cache.py
- 包含子系统: 语义审计器 + 规则文档LLM桥接 + 语义缓存

## 背景
P1优先级，mostly_implemented。语义审计是规则文档与代码对齐的桥梁。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201029')
2. 读蓝图: Grep "MOD-INF-028" docs/03_modules/
3. 拆分详细任务卡（序号从202901开始）:
   - DM-202901: spec_auditor.py恢复（语义审计核心）
   - DM-202902: semantic_cache.py恢复（语义缓存）
   - DM-202903: 规则文档LLM桥接恢复
   - DM-202904: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class SpecAuditor" + Grep "semantic_cache" 全项目
- STEP 8重点: python -m pytest tests/ -k "spec_auditor or semantic" -v
- STEP 10重点: 测试语义缓存失效、LLM桥接超时、规则文档与代码不一致未检出

每张卡完成后transition(COMPLETED)，全部完成后报告F29整体状态。
```

***

## AI-30: F30 红蓝对抗验证器

```
你是AI-30，负责恢复F30 红蓝对抗验证器功能。

## 你的元任务卡
- task_id: DM-201030（已存在，状态COMPLETED）
- 功能: F30 红蓝对抗验证器
- 蓝图: MOD-INF-030 red-blue-validator
- 源码包: src/zephyr/governance/self_validator.py + infrastructure/auto_fix_engine/fix_safety.py
- 包含子系统: 红蓝对抗验证器 + 修复有效性确认 + self_validator

## 背景
P1优先级。修复有效性验证（F16是审计编排/孤儿审判，非红蓝对抗）。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201030')
2. 读蓝图: Grep "MOD-INF-030" docs/03_modules/
3. 拆分详细任务卡（序号从203001开始）:
   - DM-203001: self_validator.py恢复（红蓝对抗核心）
   - DM-203002: fix_safety.py恢复（修复有效性确认）
   - DM-203003: 红蓝对抗验证器集成恢复
   - DM-203004: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class SelfValidator" + Grep "fix_safety" 全项目
- STEP 8重点: python -m pytest tests/ -k "self_validator or red_blue or fix_safety" -v
- STEP 10重点: 测试修复失效未检出、红蓝对抗绕过、安全修复误判

每张卡完成后transition(COMPLETED)，全部完成后报告F30整体状态。
```

***

## AI-31: F31 注册表治理

```
你是AI-31，负责恢复F31 注册表治理功能。

## 你的元任务卡
- task_id: DM-201031（已存在，状态COMPLETED）
- 功能: F31 注册表治理
- 蓝图: MOD-INF-037 registry-governance
- 源码包: src/zephyr/infrastructure/registry_governance.py + governance/ssot_registrar.py
- 包含子系统: 注册表治理(48个注册表统一管理) + SSoT注册器

## 背景
P1优先级。48个注册表的统一管理是SSoT原则的落地。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201031')
2. 读蓝图: Grep "MOD-INF-037" docs/03_modules/
3. 拆分详细任务卡（序号从203101开始）:
   - DM-203101: registry_governance.py恢复（48注册表统一管理）
   - DM-203102: ssot_registrar.py恢复（SSoT注册器）
   - DM-203103: 注册表治理集成恢复
   - DM-203104: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class RegistryGovernance" + Grep "SSoTRegistrar" + Grep "registry_of_registries" 全项目
- STEP 8重点: python -m pytest tests/ -k "registry or ssot" -v
- STEP 10重点: 测试注册表不一致、SSoT违反、注册表孤儿

每张卡完成后transition(COMPLETED)，全部完成后报告F31整体状态。
```

***

## AI-32: F32 状态机引擎

```
你是AI-32，负责恢复F32 状态机引擎功能。

## 你的元任务卡
- task_id: DM-201032（已存在，状态COMPLETED）
- 功能: F32 状态机引擎
- 蓝图: MOD-INF-038 state-machine-engine
- 源码包: src/zephyr/shared/state_machine.py + governance/fsm_verifier.py
- 包含子系统: 通用状态机引擎 + 全项目状态机实例治理 + FSM验证器

## 背景
P1优先级。全项目状态机实例的统一治理。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201032')
2. 读蓝图: Grep "MOD-INF-038" docs/03_modules/
3. 拆分详细任务卡（序号从203201开始）:
   - DM-203201: state_machine.py恢复（通用状态机引擎）
   - DM-203202: fsm_verifier.py恢复（FSM验证器）
   - DM-203203: 全项目状态机实例治理恢复
   - DM-203204: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class StateMachine" + Grep "FSMVerifier" 全项目
- STEP 8重点: python -m pytest tests/ -k "state_machine or fsm" -v
- STEP 10重点: 测试非法状态转换、状态机死锁、FSM验证绕过

每张卡完成后transition(COMPLETED)，全部完成后报告F32整体状态。
```

***

## AI-33: F33 本地模型基础设施

```
你是AI-33，负责恢复F33 本地模型基础设施功能。

## 你的元任务卡
- task_id: DM-201033（已存在，状态COMPLETED）
- 功能: F33 本地模型基础设施
- 蓝图: MOD-INF-042 local-model
- 源码包: data/capability_cards/local_model_scheduler.yaml + ollama_chat.yaml + embedding_router.yaml
- 包含子系统: BGE-M3嵌入 + Ollama推理 + 调度 + 缓存

## 背景
P2优先级，scaffold。本地模型基础设施减少对外部API的依赖。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201033')
2. 读蓝图: Grep "MOD-INF-042" docs/03_modules/
3. 拆分详细任务卡（序号从203301开始）:
   - DM-203301: local_model_scheduler.yaml恢复（本地模型调度）
   - DM-203302: ollama_chat.yaml恢复（Ollama推理）
   - DM-203303: embedding_router.yaml恢复（BGE-M3嵌入路由）
   - DM-203304: 本地模型缓存恢复
   - DM-203305: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Glob data/capability_cards/local_model*.yaml + Glob data/capability_cards/ollama*.yaml + Glob data/capability_cards/embedding*.yaml
- STEP 8重点: python -m pytest tests/ -k "local_model or ollama or embedding" -v
- STEP 10重点: 测试模型不可用降级、嵌入路由失败、缓存失效

每张卡完成后transition(COMPLETED)，全部完成后报告F33整体状态。
```

***

## AI-34: F34 代码去重引擎

```
你是AI-34，负责恢复F34 代码去重引擎功能。

## 你的元任务卡
- task_id: DM-201034（已存在，状态COMPLETED）
- 功能: F34 代码去重引擎
- 蓝图: MOD-INF-017 code-dedup-engine
- 源码包: src/zephyr/governance/atomic_fixer.py + diff_detector.py
- 包含子系统: 代码去重 + 爆炸半径防护 + 原子修复

## 背景
P2优先级。代码去重防止重复造轮子。

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201034')
2. 读蓝图: Grep "MOD-INF-017" docs/03_modules/
3. 拆分详细任务卡（序号从203401开始）:
   - DM-203401: atomic_fixer.py恢复（原子修复）
   - DM-203402: diff_detector.py恢复（差异检测+代码去重）
   - DM-203403: 爆炸半径防护恢复
   - DM-203404: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
审查: 18项字段 + 粒度门禁 + 依赖顺序 + 结构词 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "class AtomicFixer" + Grep "class DiffDetector" 全项目
- STEP 8重点: python -m pytest tests/ -k "atomic_fixer or diff_detector or dedup" -v
- STEP 10重点: 测试去重误判、原子修复回滚失败、爆炸半径超限

每张卡完成后transition(COMPLETED)，全部完成后报告F34整体状态。
```

***

## AI-35: F35 文件结构治理引擎

```
你是AI-35，负责恢复F35 文件结构治理引擎功能。

## 你的元任务卡
- task_id: DM-201035
- 功能: F35 文件结构治理引擎
- 蓝图: GOV-FSTR-001
- 源码包: scripts/governance/restructuring/（计划路径）
- 蓝图路径: docs/03_modules/_restructuring/blueprint.md
- 包含子系统: 大文件拆分(>500行按职责拆分) + 跨目录重复合并 + 按需激活(延迟加载) + 安全搬家(不破坏导入链)
- 蓝图版本: v4.2.0, generation 3
- construction_progress: design_only（仅有设计文档，无代码实现）

## 背景
文件结构治理——全项目文件结构优化引擎。目标 LLM 友好上限 300 行/文件。当前规模约 20 个大文件 + 约 10 组跨目录重复。与 F17（交易骨架清理）不同：F17 限于交易域，F35 是跨层横切功能，覆盖全项目文件结构治理。

## 阶段A：创建详细任务卡
1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201035'); print(t.description)"
2. 读蓝图: Read docs/03_modules/_restructuring/blueprint.md
3. 拆分详细任务卡:
   - DM-203501: 大文件拆分引擎(>500行检测+按职责拆分)
   - DM-203502: 跨目录重复检测+合并引擎
   - DM-203503: 按需激活/延迟加载机制
   - DM-203504: 安全搬家(文件移动不破坏导入链)
   - DM-203505: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
逐张审查: 模板字段(18项) + 粒度门禁 + 依赖顺序 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 1: Read docs/03_modules/_restructuring/blueprint.md
- STEP 2: Glob src/zephyr/**/*.py 统计>500行文件; Grep 重复功能模块
- STEP 5: extract_depgraph.py --modules 查文件结构归属
- STEP 8: python -m pytest tests/ -k "restructure or file_split or dedup_merge" -v
- STEP 10: 测试拆分后导入断裂、合并后功能丢失、搬家后路径失效
- STEP 12: diagnose_depgraph.py + 蓝图↔代码 + 代码头部↔引用

## 完成标准
1. 大文件拆分引擎可检测>500行文件并按职责自动拆分
2. 跨目录重复检测可发现同功能多副本
3. 按需激活机制可实现未使用模块延迟加载
4. 安全搬家可保证文件移动后导入链不断裂
5. 三方对齐 PASS

每张卡完成后transition(COMPLETED)，全部完成后报告F35整体状态。
```

***

## AI-36: F36 审计追踪链（不可变审计链）

```
你是AI-36，负责恢复F36 审计追踪链功能。

## 你的元任务卡
- task_id: DM-201036
- 功能: F36 审计追踪链（不可变审计链）
- 蓝图: MOD-INF-020
- 源码包: src/zephyr/governance/audit_trail/（352个.py文件）
- 蓝图路径: docs/03_modules/_domain_governance/audit_trail/blueprint.md
- 包含子系统: JSONL唯一真源写入 + 哈希链防篡改 + HMAC系统级签名 + Ed25519 Agent级不可否认签名 + CoT推理链审计 + 13种异常行为签名检测 + Merkle小时级完整性 + 证据包(evidence_pack) + 重放引擎(replay_engine) + 分层存储 + 隐私脱敏 + 信任引擎
- 蓝图版本: v2.1.0, generation 9
- construction_progress: partially_implemented
- 功能域: D-GOV_AUDIT/audit-trail

## 背景
不可变动作审计与密码学完整性保证。与F6（漂移检测/行为审计）不同：F6检测基线偏离和行为边界，F36解决操作记录不可篡改+不可否认+密码学可验证。目标容量 100 AI并发 × 10,000脚本 × 峰值120条/秒写入。

## 阶段A：创建详细任务卡
1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201036'); print(t.description)"
2. 读蓝图: Read docs/03_modules/_domain_governance/audit_trail/blueprint.md
3. 拆分详细任务卡:
   - DM-203601: JSONL写入+哈希链防篡改恢复
   - DM-203602: HMAC系统级签名+Ed25519 Agent级签名恢复
   - DM-203603: CoT推理链审计+13种异常行为签名检测恢复
   - DM-203604: Merkle完整性+证据包+重放引擎恢复
   - DM-203605: 分层存储+隐私脱敏+信任引擎恢复
   - DM-203606: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
逐张审查: 模板字段(18项) + 粒度门禁 + 依赖顺序 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 1: Read docs/03_modules/_domain_governance/audit_trail/blueprint.md
- STEP 2: Glob src/zephyr/governance/audit_trail/**/*.py 定位352个文件
- STEP 5: extract_depgraph.py --modules 查audit_trail域归属
- STEP 6: python -c "from zephyr.governance.audit_trail import *" 逐模块验证导入
- STEP 8: python -m pytest tests/ -k "audit_trail or hash_chain or merkle or evidence" -v
- STEP 10: 测试哈希链篡改检测、签名伪造检测、重放攻击防护、并发写入冲突
- STEP 12: diagnose_depgraph.py + 蓝图↔代码 + 代码头部↔引用

## 完成标准
1. JSONL写入+哈希链可检测篡改
2. HMAC+Ed25519签名可实现不可否认
3. 13种异常行为签名检测全部可用
4. Merkle完整性验证通过
5. 证据包+重放引擎功能正常
6. 三方对齐 PASS

每张卡完成后transition(COMPLETED)，全部完成后报告F36整体状态。
```

***

## AI-37: F37 资源优化引擎

```
你是AI-37，负责恢复F37 资源优化引擎功能。

## 你的元任务卡
- task_id: DM-201037
- 功能: F37 资源优化引擎
- 蓝图: MOD-RESOURCE_OPTIMIZATION_ENGINE
- 源码包: src/zephyr/infrastructure/lifecycle/resource_optimization_engine.py + src/zephyr/shared/lifecycle/resource_optimization_engine.py + src/zephyr/trading/lifecycle_manager.py + src/zephyr/trading/gpu_monitor.py
- 蓝图路径: docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
- 包含子系统: MAPE-K闭环(Monitor→Analyze→Plan→Execute) + 进程池化 + I/O零拷贝缓存(LRU淘汰) + 智能调度 + 内存水位管理 + 缓存复用 + 流式处理 + 自愈闭环 + GPU监控(nvidia-smi) + DefensiveStrategyEngine(应急保护) + OffensiveStrategyEngine(主动提效)
- 蓝图版本: v5.4.0, generation 2
- construction_progress: partially_implemented
- 功能域: D-INFRA-OPS/resource_optimization

## 背景
MAPE-K驱动的资源优化引擎。与F21（守护系统/IDE健康守护）共享蓝图MOD-INF-032但职责不同：F21聚焦IDE幽灵窗口扫描+过期锁清理（守护进程层面），F37聚焦进程池化+I/O缓存+智能调度+自愈（资源优化层面）。与F27（容量保障）也不同：F27是SLI/SLO+Error Budget，F37是MAPE-K资源利用率优化。当前管理51模块，目标1,500模块/100 AI并发。

## 阶段A：创建详细任务卡
1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201037'); print(t.description)"
2. 读蓝图: Read docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
3. 拆分详细任务卡:
   - DM-203701: MAPE-K闭环(Monitor→Analyze→Plan→Execute)恢复
   - DM-203702: 进程池化+I/O零拷贝缓存(LRU)恢复
   - DM-203703: 智能调度+内存水位管理恢复
   - DM-203704: GPU监控+自愈闭环恢复
   - DM-203705: DefensiveStrategy+OffensiveStrategy双引擎恢复
   - DM-203706: 蓝图更新+三方对齐+索引更新

## 阶段B：审查任务卡
逐张审查: 模板字段(18项) + 粒度门禁 + 依赖顺序 + 14步覆盖

## 阶段C：循环修复
修复审查问题 → 重新审查 → 直到全部通过

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 1: Read docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md
- STEP 2: Glob src/zephyr/infrastructure/lifecycle/resource_optimization_engine.py + shared/lifecycle/ + trading/lifecycle_manager.py + trading/gpu_monitor.py
- STEP 5: extract_depgraph.py --modules 查resource_optimization域归属
- STEP 6: python -c "from zephyr.infrastructure.lifecycle.resource_optimization_engine import *" 验证导入
- STEP 8: python -m pytest tests/ -k "resource_optimization or mape_k or gpu_monitor or lifecycle" -v
- STEP 10: 测试进程池耗尽、I/O缓存失效、内存水位超限、GPU故障自愈、MAPE-K闭环中断
- STEP 12: diagnose_depgraph.py + 蓝图↔代码 + 代码头部↔引用

## 完成标准
1. MAPE-K闭环可自动Monitor→Analyze→Plan→Execute
2. 进程池化可避免子进程频繁创建销毁
3. I/O零拷贝缓存LRU淘汰正常
4. GPU监控可采集nvidia-smi数据
5. 自愈闭环可检测故障并自动恢复
6. Defensive+Offensive双引擎协同工作
7. 三方对齐 PASS

每张卡完成后transition(COMPLETED)，全部完成后报告F37整体状态。
```
