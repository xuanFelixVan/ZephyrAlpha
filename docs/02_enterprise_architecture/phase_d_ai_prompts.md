# 阶段D：18个AI完整提示词

> 每个AI复制自己的提示词，在新对话中执行。
> 工作流程：创建详细任务卡 → 审查任务卡 → 循环修复 → 执行任务卡

---

## 通用背景（所有AI共享）

你是 ZephyrAlpha 项目的功能恢复AI。ZephyrAlpha 是一个 AI 自治量化交易系统，正在经历架构级大更新。你的任务是恢复一个功能模块到可独立运行状态。

**项目路径**: D:\ZephyrAlpha
**规则文件**: .trae/rules/project_rules.md（L0铁律）+ .trae/rules/onboarding_detail.md（L1施工指导）
**施工文档**: docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md
**任务系统**: TaskRepository（SQLite，data/databases/governance.db）

**RULE-TEN 14步统一流程**（你必须遵循）:
1. 读蓝图 → 2. 全量定位 → 3. 归属裁定 → 4. 蓝图设计 → 5. 位置校验 → 6. 修复断链 → 7. 补全头部 → 8. 运行测试 → 9. 修复失败 → 10. 红蓝对抗 → 11. 更新蓝图 → 12. 三方对齐 → 13. 更新索引 → 14. 报告

**你的工作分四个阶段**:
- 阶段A：创建详细任务卡（基于元任务卡拆分）
- 阶段B：审查任务卡（检查完整性+粒度+依赖）
- 阶段C：循环修复任务卡（直到全部通过）
- 阶段D：执行任务卡（按14步流程逐张执行）

---

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

---

## AI-02: F2 门禁引擎

```
你是AI-02，负责恢复F2 门禁引擎功能。

## 你的元任务卡
- task_id: DM-201002
- 功能: F2 门禁引擎
- 蓝图: MOD-INF-007
- 源码包: src/zephyr/governance/rule_enforcement/
- 包含子系统: PhaseManager + PhaseExecutor + 51门控检查 + GateEngine + G0-G7门禁

## 阶段A：创建详细任务卡

1. 读取元任务卡:
   python -c "import sys; sys.path.insert(0,'src'); from zephyr.governance.task_repo import TaskRepository; tr=TaskRepository(); t=tr.get('DM-201002'); print(t.description)"

2. 读蓝图: Grep "MOD-INF-007" docs/03_modules/ → Read蓝图

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

---

## AI-03: F3 任务系统

```
你是AI-03，负责恢复F3 任务系统功能。

## 你的元任务卡
- task_id: DM-201003
- 功能: F3 任务系统
- 蓝图: MOD-INF-006
- 源码包: src/zephyr/governance/
- 包含子系统: TaskRepo + TaskCard + BlueprintDecomposer + 10状态机 + 粒度门禁

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201003')
2. 读蓝图: Grep "MOD-INF-006" docs/03_modules/
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

---

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

---

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

---

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

---

## AI-07: F7 LLM安全网关

```
你是AI-07，负责恢复F7 LLM安全网关功能。

## 你的元任务卡
- task_id: DM-201007
- 功能: F7 LLM安全网关
- 蓝图: MOD-INF-014
- 源码包: src/zephyr/security/
- 包含子系统: L0-L8九层纵深防御 + InputSanitizer + ConstitutionEngine + RedBlueValidator

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201007')
2. 读蓝图: Grep "MOD-INF-014" docs/03_modules/
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

---

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

---

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

---

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

---

## AI-11: F11 上下文引擎

```
你是AI-11，负责恢复F11 上下文引擎功能。

## 你的元任务卡
- task_id: DM-201011
- 功能: F11 上下文引擎
- 蓝图: MOD-INF-008
- 源码包: src/zephyr/autonomy_core/
- 包含子系统: ContextPipeline四阶段 + 15个Context子模块 + Prompt注册表

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201011')
2. 读蓝图: Grep "MOD-INF-008" docs/03_modules/
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

---

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

---

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

---

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

---

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

---

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

---

## AI-17: F17 交易核心链路

```
你是AI-17，负责恢复F17 交易核心链路功能。

## 你的元任务卡
- task_id: DM-201017
- 功能: F17 交易核心链路
- 蓝图: MOD-L02
- 源码包: src/zephyr/ex_core/
- 包含子系统: ExecutionEngine + OrderManager + OMSRiskEngine(三层风控) + StopLossEngine + AlphaSignalPipeline + FactorRegistry + BacktestEngine

## 阶段A：创建详细任务卡

1. 读取元任务卡: tr.get('DM-201017')
2. 读蓝图: Grep "MOD-L02" docs/03_modules/
3. 拆分详细任务卡（序号从202701开始）:
   - DM-202701: ExecutionEngine恢复
   - DM-202702: OrderManager恢复
   - DM-202703: OMSRiskEngine三层风控恢复
   - DM-202704: StopLossEngine恢复
   - DM-202705: AlphaSignalPipeline恢复
   - DM-202706: FactorRegistry恢复
   - DM-202707: BacktestEngine恢复
   - DM-202708: 蓝图更新+三方对齐+索引更新

## 阶段B+C：审查+循环修复

## 阶段D：执行任务卡
按14步流程逐张执行:
- STEP 2重点: Grep "ExecutionEngine" + Grep "OrderManager" + Grep "OMSRiskEngine" + Glob src/zephyr/ex_core/**/*.py
- STEP 8重点: python -m pytest tests/ -k trading -v
- STEP 10重点: 测试超额下单、风控绕过、止损失效、回测作弊

每张卡完成后transition(COMPLETED)，全部完成后报告F17整体状态。
```

---

## AI-18: F18 治理脚本系统(7维度)

```
你是AI-18，负责恢复F18 治理脚本系统(7维度)功能。

## 你的元任务卡
- task_id: DM-201018
- 功能: F18 治理脚本系统(7维度)
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

---

## 统筹AI（你）的职责

```
你是统筹AI，负责协调18个功能AI的工作。

## 你的职责
1. 基础设施准备: depgraph.db建表 + conftest.py插件 + 静态存活地图
2. 依赖协调: 处理AI间的依赖冲突（如AI-17依赖AI-12的向量记忆）
3. 验收: 每个AI完成后审查其报告
4. 反馈处理: 收集P0/P1反馈，转发给对应阶段
5. 进度追踪: 记录18个AI的完成状态

## 启动顺序
- 第1波(无依赖): AI-02, AI-03, AI-04, AI-05, AI-06, AI-08, AI-09, AI-10, AI-16, AI-18
- 第2波(依赖第1波): AI-01, AI-07, AI-11, AI-13, AI-14, AI-15
- 第3波(依赖第2波): AI-12, AI-17
```
