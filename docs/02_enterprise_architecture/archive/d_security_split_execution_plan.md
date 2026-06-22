# D-SECURITY 拆分执行计划：D-BEHAVIORAL\_AUDIT 域创建

> **裁定依据**：ARCH-CAP-000 第一性原理 + ARCH-CAP-004 路径平铺原则
> **拆分方案**：方案B（拆出 D-BEHAVIORAL\_AUDIT）+ 物理迁移（选项A 平铺）
> **Owner 审批**：已同意（2026-06-21）
> **执行者**：Claude（单一会话内完成审查+执行，充分利用上下文缓存）
> **执行模式**：一口气模式——审查通过后直接进入STEP 1-6执行，不分轮次、不重新审查

## 0. 拆分概览

| 项目                      | 值                                                                     |
| ----------------------- | --------------------------------------------------------------------- |
| 源域                      | D-SECURITY（194 production 节点）                                         |
| 新域                      | D-BEHAVIORAL\_AUDIT（60 production 节点，从D-SECURITY迁出）                   |
| 拆分后 D-SECURITY          | 194 - 60 = **134** production 节点（80-150 区间 ✅）                         |
| 拆分后 D-BEHAVIORAL\_AUDIT | **60** production 节点（80-150 区间 ✅）                                     |
| 源路径                     | `src/zephyr/security/access_control/behavioral_auditor/`（D-SECURITY域） |
| 目标路径                    | `src/zephyr/behavioral_audit/`（平铺，FP-2/Fp-5）                          |
| 迁移文件数                   | 60 .py（D-SECURITY）+ 2 yaml（D-GOVERNANCE，迁移到新域）= 62 文件                 |
| import 更新数              | **169** 文件（89 src/ + 79 tests/ + 1 scripts/）                          |
| 删除副本数                   | **70** .py（governance/behavioral\_auditor/ 下的旧副本，0 独立价值）              |
| prototype 节点            | 87 个（path同步更新，非迁移）                                                    |
| design 节点               | 2 个（path同步更新，非迁移）                                                     |

> **拆分依据**：D-SECURITY=194 在 150-200 区间（ARCH-CAP-003 B区），四标准全部不满足 → 不是高度耦合域 → 主动优化拆分到 80-150 默认区（A区）。非强制拆分，是主动优化。
> **ARCH-CAP-000 说明**：ARCH-CAP-000 第一性原理已添加到 trae\_055（arch\_cap\_000\_first\_principles section），含5条标准 FP-1\~FP-5。

***

## STEP 0: 外部审查员审查（执行前强制门禁）

> **角色定位**：你（Claude）首先作为**客观中立、对抗性、反思性**的外部审查员，审查本执行计划本身。
> **铁律**：审查未通过，禁止进入 STEP 1 执行。你必须先证明这个计划是对的，才能执行它。
> **执行模式**：一口气模式——审查全部28项PASS后，**同一会话内直接进入STEP 1-6执行**，不分轮次、不重新审查，充分利用上下文缓存节省费用。

### 0.1 审查角色声明

你在**单一会话内**完成审查+执行，但有严格的阶段分离：

| 阶段       | 角色    | 职责               | 禁止            |
| -------- | ----- | ---------------- | ------------- |
| STEP 0   | 外部审查员 | 审查本计划是否正确、完整、无风险 | 禁止在审查阶段执行任何文件操作 |
| STEP 1-6 | 执行者   | 按审查通过的计划执行       | 禁止跳过审查直接执行    |

**审查中FAIL的处理原则（就地修复，不重新整体审查）**：
- 审查中发现的FAIL如果是**计划文档本身错误**（如数字错误、SQL口径错误）→ Claude直接修复计划文档，重新验证该项PASS后继续下一项审查
- 审查中发现的FAIL如果是**计划方案缺陷**（如遗漏prototype处理）→ Claude直接补充计划，重新验证该项PASS后继续下一项审查
- 审查中发现的QUESTION如果是**事实性疑问**（如字段是否存在、蓝图是否存在）→ Claude直接查询验证后判定PASS/FAIL
- **禁止**：审查中发现FAIL后跳过，留到执行阶段再修——必须当场修复当场验证

### 0.2 审查清单（7大类28项）

你必须逐项审查，每项给出 PASS/FAIL/QUESTION 判定：

#### A. 数据准确性审查（验证本计划的数据是否真实）

| #   | 审查项                                                                        | 审查方法                     | PASS标准                                                                                                                                                                    |
| --- | -------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | D-SECURITY production节点=194                                                | 查询depgraph.db            | `SELECT COUNT(*) FROM nodes WHERE domain_id='D-SECURITY' AND design_maturity='production'` = 194                                                                          |
| A2a | security/access\_control/behavioral\_auditor/下production节点=60（D-SECURITY域） | 查询depgraph.db            | `SELECT COUNT(*) FROM nodes WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%' AND design_maturity='production'` = 60                              |
| A2b | governance/behavioral\_auditor/下production节点=2（D-GOVERNANCE域，yaml文件）       | 查询depgraph.db            | `SELECT COUNT(*) FROM nodes WHERE path LIKE 'src/zephyr/governance/behavioral_auditor/%' AND design_maturity='production'` = 2                                            |
| A3  | 拆分后D-SECURITY=134                                                          | A1-A2a                   | 194-60=134，在80-150区间                                                                                                                                                      |
| A4  | 外部消费者=169个文件                                                               | Grep全项目                  | `zephyr.security.access_control.behavioral_auditor` 出现在169个文件中（89 src/ + 79 tests/ + 1 scripts/）                                                                          |
| A5  | governance/behavioral\_auditor/下70个.py副本0独立价值                              | 运行compare\_ba\_copies.py | 0个文件有独立符号                                                                                                                                                                 |
| A6  | 2个yaml文件内容确认                                                               | Read两个文件                 | \_detector\_registry.yaml是检测器注册表，migration\_plan.yaml是迁移计划                                                                                                                |
| A7  | prototype节点=87个，design节点=2个                                                | 查询depgraph.db            | `SELECT design_maturity, COUNT(*) FROM nodes WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%' GROUP BY design_maturity` 确认prototype=87, design=2 |

#### B. 方案合理性审查（验证拆分方案是否符合第一性原理）

| #  | 审查项                                          | 审查方法                    | PASS标准                                                  |
| -- | -------------------------------------------- | ----------------------- | ------------------------------------------------------- |
| B1 | 新域命名D-BEHAVIORAL\_AUDIT是否符合FP-4              | 读蓝图§0.1/§0.3            | 命名覆盖未来方向（verdict\_engine/admission\_controller等），不是当前子集 |
| B2 | 路径src/zephyr/behavioral\_audit/是否符合FP-2/Fp-5 | 检查路径层级                  | 平铺，无冗余嵌套                                                |
| B3 | 是否符合ARCH-CAP-004路径平铺原则                       | 读trae\_055 ARCH-CAP-004 | domain\_id与ssot\_path 1:1映射                             |
| B4 | 是否符合ARCH-CAP-006拆分审批协议                       | 确认Owner已审批              | Owner已同意（2026-06-21）                                    |

#### C. 风险审查（验证执行过程中可能的风险）

| #  | 审查项                    | 审查方法                       | PASS标准                                                       |
| -- | ---------------------- | -------------------------- | ------------------------------------------------------------ |
| C1 | depgraph.db SQL更新是否有风险 | 检查UPDATE语句                 | UPDATE有WHERE条件限定，不会误更新其他节点                                   |
| C2 | 169个import替换是否有遗漏      | Grep验证                     | 替换后`zephyr.security.access_control.behavioral_auditor`出现次数=0 |
| C3 | 70个文件删除是否安全            | 确认compare\_ba\_copies.py结果 | 70个文件全部在security/下有对应版本，0独立符号                                |
| C4 | re-export shim更新后是否兼容  | 检查\_\_init\_\_.py          | re-export路径指向新路径，旧import仍能工作                                 |
| C5 | 跨域依赖是否正确处理             | 查询edges表                   | behavioral\_auditor的跨域出边/入边在迁移后仍有效                           |
| C6 | 是否有循环依赖风险              | 运行diagnose\_depgraph.py    | 迁移后无新循环依赖                                                    |

#### D. 回滚方案审查（验证回滚是否完整）

| #  | 审查项                      | 审查方法       | PASS标准         |
| -- | ------------------------ | ---------- | -------------- |
| D1 | 每步是否有独立回滚方案              | 检查STEP 1-6 | 每步有回滚命令        |
| D2 | 总回滚方案是否覆盖所有步骤            | 检查总回滚      | 能恢复到STEP 1之前状态 |
| D3 | depgraph.db备份是否在STEP 1执行 | 检查STEP 1操作 | 第一步是备份         |

#### E. 验证命令审查（验证每步的验证命令是否有效）

| #  | 审查项                 | 审查方法       | PASS标准                          |
| -- | ------------------- | ---------- | ------------------------------- |
| E1 | 每步是否有验证命令           | 检查STEP 1-6 | 每步有验证命令和通过标准                    |
| E2 | 验证命令是否机械可判定         | 检查验证命令     | exit code或明确输出，无需主观判断           |
| E3 | STEP 5全量验证是否覆盖所有风险点 | 检查STEP 5   | 6项验证覆盖import/depgraph/注册/路径树/容量 |

#### F. 规则合规性审查（验证是否符合项目规则）

| #  | 审查项                               | 审查方法   | PASS标准               |
| -- | --------------------------------- | ------ | -------------------- |
| F1 | 是否遵循RULE-ZERO文件锁协议                | 检查执行计划 | 写入文件前加锁              |
| F2 | 是否遵循RULE-ONE原子写入                  | 检查执行计划 | 文件写入用tmp+rename      |
| F3 | 是否遵循RULE-FIVE零残留                  | 检查执行计划 | 临时文件清理               |
| F4 | 是否遵循RULE-SEVEN ThreadPoolExecutor | 检查批量操作 | 85个文件替换用线程池          |
| F5 | 是否遵循trae\_054 depgraph访问协议        | 检查DB操作 | 通过脚本访问，不直接Read/Write |

#### G. 遗漏检查（对抗性反思）

| #  | 审查项                                | 审查方法                                               | PASS标准                                  |
| -- | ---------------------------------- | -------------------------------------------------- | --------------------------------------- |
| G1 | 是否有未列出的消费者？                        | Grep更广泛的关键词                                        | 搜索behavioral\_auditor所有引用，确认无遗漏         |
| G2 | 是否有未列出的依赖？                         | 查询edges表全部边                                        | 确认所有依赖边都已处理                             |
| G3 | 是否有其他域的节点引用了behavioral\_auditor路径？ | 查询nodes表                                           | 确认无其他域节点path包含behavioral\_auditor       |
| G4 | blueprint文档是否需要更新？                 | 检查蓝图actual\_disk\_path                             | 蓝图已规划src/zephyr/behavioral\_audit/，确认一致 |
| G5 | script-manifest.yaml是否需要更新？        | 检查是否有脚本注册                                          | 确认无遗漏                                   |
| G6 | __init__.py导出是否需要更新？               | 检查security/__init__.py和access\_control/__init__.py | 确认导出路径更新                                |

### 0.3 审查报告输出格式

审查完成后，你必须输出以下格式的报告：

```markdown
# D-SECURITY 拆分计划外部审查报告

## 审查结论
- 审查项总数：28
- PASS：XX
- FAIL：XX
- QUESTION：XX

## 最终判定
[ ] 通过——直接进入STEP 1执行（一口气模式）
[ ] 不通过——就地修复FAIL项后重新验证该项，全部PASS后直接执行（不重新整体审查）

## FAIL项详情（如有）
### FAIL-X: [审查项名称]
- 问题描述：...
- 证据：...
- 建议修复方案：...

## QUESTION项详情（如有）
### QUESTION-X: [审查项名称]
- 疑问：...
- 需要Owner确认：...

## 对抗性反思
- 本计划最大的风险点是：...
- 我作为审查员认为还应该增加的检查项：...
- 如果我是Owner，我最担心的场景是：...
```

### 0.4 审查通过条件

| 条件        | 要求                    |
| --------- | --------------------- |
| FAIL数     | = 0（审查中发现的FAIL必须**就地修复**并重新验证该项PASS，不重新整体审查） |
| QUESTION数 | = 0（事实性QUESTION就地查询验证后判定，不留给Owner） |
| 对抗性反思     | 必须完成（不能跳过）            |

**28项全部PASS + 对抗性反思完成后，同一会话内直接进入STEP 1执行。**

### 0.5 审查阶段禁止事项

- 禁止在审查阶段执行任何**目标文件**的迁移/修改/删除操作（审查的是计划，不是执行计划）
- 禁止在审查阶段修改depgraph.db（仅允许只读查询验证）
- 禁止跳过任何审查项
- 禁止对FAIL项"先执行后修复"——必须当场修复计划文档、当场重新验证该项
- 禁止"审查完一轮再重新审查一轮"——一口气模式只审查一轮，FAIL就地修复后继续下一项，全部PASS后直接执行

***

## 6步执行计划

### STEP 1: 备份 + 创建新域注册

**操作**：

1. 备份 depgraph.db：`copy /Y data\databases\depgraph.db data\databases\depgraph.db.bak`
2. 查询 domains 表实际 schema：`PRAGMA table_info(domains)` —— 根据实际字段构造 INSERT
3. 在 depgraph.db domains 表 INSERT 新域 D-BEHAVIORAL\_AUDIT
4. 创建目标目录 src/zephyr/behavioral\_audit/

**新域定义**（参考语句，执行前 MUST 先 PRAGMA table\_info 确认字段名）：

```sql
-- 先执行 PRAGMA table_info(domains) 获取实际字段列表
-- 以下为参考语句，字段名根据实际 schema 调整（实测 domains 表有 lifecycle/build_status，无 status）
INSERT INTO domains (
  domain_id, domain_name, domain_group, ssot_path,
  layer_id, max_modules, current_modules, target_modules,
  blueprint_id, lifecycle
) VALUES (
  'D-BEHAVIORAL_AUDIT', '行为审计', '横切',
  'src/zephyr/behavioral_audit/',
  'L1_platform', 150, 0, 60,
  'MOD-INF-033', 'active'
);
```

> **注意**：blueprint\_id=MOD-INF-033 已存在于 docs/03\_modules/\_cross\_layer/behavioral\_auditor/blueprint.md
> **注意**：target\_modules=60（D-SECURITY迁出的production节点数），不含D-GOVERNANCE的2个yaml

**验证命令**：

```bash
python scripts/governance/extract_depgraph.py --summary
# 验证：域数从39变为40，D-BEHAVIORAL_AUDIT 出现在域清单中
```

**回滚**：

```bash
# 恢复 depgraph.db
copy /Y data\databases\depgraph.db.bak data\databases\depgraph.db
# 删除空目录
rmdir src\zephyr\behavioral_audit
```

***

### STEP 2: 迁移真实代码（62文件）

**操作**：

1. 将 `src/zephyr/security/access_control/behavioral_auditor/` 下全部60个.py 迁移到 `src/zephyr/behavioral_audit/`
2. 将 `src/zephyr/governance/behavioral_auditor/_detector_registry.yaml` 迁移到 `src/zephyr/behavioral_audit/`
3. 将 `src/zephyr/governance/behavioral_auditor/migration_plan.yaml` 迁移到 `src/zephyr/behavioral_audit/`
4. 更新每个.py文件头部的 \[MODULE] 路径：`zephyr.security.access_control.behavioral_auditor.xxx` → `zephyr.behavioral_audit.xxx`

**迁移清单**（60个.py，按字母序）：

```
absence_manager.py
ai_construction_detectors.py
ai_context_injector.py
alert_router.py
architecture_contracts.py
architecture_principles.py
backcompat_checker.py
baseline_manager.py
baseline_poisoning_guard.py
benchmark_integrity.py
brain_integration.py
canary_controller.py
cascade_detector.py
chaos_injector.py
code_review_ai.py
cold_start.py
config_consistency.py
contract_drift_detector.py
correlation_engine.py
credibility_engine.py
cross_env_consistency.py
cross_module_score.py
dashboard.py
data_classification.py
data_lifecycle.py
data_quality.py
data_source_reliability.py
dependency_manager.py
detector_dispatcher.py
drift_cron_scheduler.py
drift_engine.py
drift_hotfix_bypass.py
drift_infrastructure.py
drift_models.py
drift_result_types.py
drift_training.py
events.py
file_attr_checker.py
forensics_engine.py
gate_persistence.py
git_bisector.py
gitignore_auditor.py
handoff_manager.py
headless_scanner.py
incremental_scanner.py
integration_test_runner.py
ml_engineering.py
model_drift_monitor.py
naming_magic_checker.py
orphan_scanner.py
performance_baseline.py
python_compat.py
reconciler.py
regime_detector.py
resource_guard.py
roi_engine.py
rollback_bridge.py
runbook_generator.py
scan_mutex.py
self_check.py
self_test_verifier.py
state_machine.py
suppression_learner.py
symlink_checker.py
system_topology.py
tamper_proof_audit.py
test_fixture_checker.py
trend_analyzer.py
__init__.py
__main__.py
_analysis.py
_core.py
_drift.py
_infrastructure.py
_scanners.py
```

**验证命令**：

```bash
# 验证文件数
dir /B src\zephyr\behavioral_audit\*.py | find /C /V ""
# 预期：75（60个迁移 + __init__.py/__main__.py/_*.py 等）

# 验证旧目录已清空
dir /B src\zephyr\security\access_control\behavioral_auditor\*.py 2>nul
# 预期：无文件
```

**回滚**：

```bash
# 将文件移回原位置
move src\zephyr\behavioral_audit\*.py src\zephyr\security\access_control\behavioral_auditor\
move src\zephyr\behavioral_audit\*.yaml src\zephyr\governance\behavioral_auditor\
# 还原 [MODULE] 路径（用 git checkout）
git checkout -- src/zephyr/security/access_control/behavioral_auditor/
```

***

### STEP 3: 更新169个文件的 import 路径

**操作**：
将以下 import 路径全局替换（用 Python 脚本批量处理，遵循 RULE-SEVEN ThreadPoolExecutor）：

- `zephyr.security.access_control.behavioral_auditor` → `zephyr.behavioral_audit`
- `from zephyr.security.access_control.behavioral_auditor` → `from zephyr.behavioral_audit`
- `import zephyr.security.access_control.behavioral_auditor` → `import zephyr.behavioral_audit`

**消费者分类（169个文件）**：

| 类别                        |   文件数   | 说明                                                       |
| ------------------------- | :-----: | -------------------------------------------------------- |
| src/behavioral\_auditor自身 |    73   | 迁移后的新路径文件内部互相引用旧路径，需更新                                   |
| src/外部消费者                 |    16   | governance(12) + infrastructure(2) + ops(1) + trading(1) |
| tests/                    |    79   | 所有测试文件                                                   |
| scripts/                  |    1    | 脚本文件                                                     |
| **合计**                    | **169** | <br />                                                   |

**16个 src/外部消费者清单**：

1. `src/zephyr/governance/behavioral_auditor/__init__.py`（re-export shim，引用48处）
2. `src/zephyr/governance/audit_orchestrator/cli.py`
3. `src/zephyr/governance/audit_orchestrator/audit_admission_controller.py`
4. `src/zephyr/governance/audit_trail/cli.py`
5. `src/zephyr/governance/audit_trail/audit_admission_controller.py`
6. `src/zephyr/governance/budget_engine.py`
7. `src/zephyr/governance/drift_fix.py`
8. `src/zephyr/governance/governance/drift_fix.py`
9. `src/zephyr/governance/phase_check_registry.py`
10. `src/zephyr/governance/rule_enforcement/drift_detector.py`（引用7处）
11. `src/zephyr/governance/rule_enforcement/gate_engine.py`
12. `src/zephyr/governance/rule_enforcement/check_types/ct_drift_budget.py`
13. `src/zephyr/infrastructure/governance_server.py`（引用7处）
14. `src/zephyr/infrastructure/system_telemetry/contract_metrics.py`
15. `src/zephyr/ops/scheduler.py`
16. `src/zephyr/trading/circadian_scheduler.py`

> **注意**：实际消费者清单 MUST 在执行时用 Grep 实时生成，禁止手填（本次手填85已证明不可靠）。执行时运行：
> `Grep "zephyr\.security\.access_control\.behavioral_auditor" --output files_with_matches` 获取完整169个文件清单

**验证命令**：

```bash
# 验证无残留旧路径
python scripts/governance/verify_import_migration.py
# 预期：0 个残留

# pytest 收集测试
python -m pytest tests/ --collect-only -q
# 预期：无 ImportError
```

**回滚**：

```bash
# 用 git 恢复所有被修改的文件
git checkout -- src/zephyr/governance/
git checkout -- src/zephyr/infrastructure/
git checkout -- src/zephyr/ops/
git checkout -- src/zephyr/trading/
git checkout -- tests/
```

***

### STEP 4: 更新 re-export shim + depgraph.db 域归属 + prototype/design 节点 path 同步

**操作**：

1. 更新 `src/zephyr/governance/behavioral_auditor/__init__.py` 的 re-export 路径：
   - `from zephyr.security.access_control.behavioral_auditor.xxx` → `from zephyr.behavioral_audit.xxx`
2. 更新 depgraph.db 中60个 production 节点的 domain\_id（仅D-SECURITY的，不含D-GOVERNANCE的2个yaml）：
   ```sql
   -- 仅迁移 D-SECURITY 域的 production 节点（限定路径，避免误改 D-GOVERNANCE）
   UPDATE nodes
   SET domain_id = 'D-BEHAVIORAL_AUDIT'
   WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%'
     AND design_maturity = 'production';
   -- 预期：60 行受影响
   ```
3. 同步 87 个 prototype 节点和 2 个 design 节点的 path（物理文件已迁移，path 需更新）：
   ```sql
   -- prototype 节点 path 更新（87个）
   UPDATE nodes
   SET path = REPLACE(path,
     'src/zephyr/security/access_control/behavioral_auditor/',
     'src/zephyr/behavioral_audit/')
   WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%'
     AND design_maturity = 'prototype';
   -- 预期：87 行受影响

   -- design 节点 path 更新（2个）
   UPDATE nodes
   SET path = REPLACE(path,
     'src/zephyr/security/access_control/behavioral_auditor/',
     'src/zephyr/behavioral_audit/')
   WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%'
     AND design_maturity = 'design';
   -- 预期：2 行受影响
   ```
4. 更新 depgraph.db 中 D-SECURITY 和 D-BEHAVIORAL\_AUDIT 的 current\_modules

**验证命令**：

```bash
# 验证 re-export shim 指向新路径
python -c "from zephyr.governance.behavioral_auditor import drift_engine; print('OK')"

# 验证 depgraph 域归属
python scripts/governance/extract_depgraph.py --summary
# 预期：D-BEHAVIORAL_AUDIT 60 production 节点，D-SECURITY 134 production 节点

# 验证新路径直接 import
python -c "from zephyr.behavioral_audit import drift_engine; print('OK')"

# 验证 prototype/design 节点 path 已更新（无悬空路径）
python -c "import sqlite3; c=sqlite3.connect(r'd:\ZephyrAlpha\data\databases\depgraph.db'); print(c.execute(\"SELECT COUNT(*) FROM nodes WHERE path LIKE 'src/zephyr/security/access_control/behavioral_auditor/%'\").fetchone()[0]); c.close()"
# 预期：0（所有节点 path 已更新到新路径）
```

**回滚**：

```bash
# 恢复 depgraph.db
copy /Y data\databases\depgraph.db.bak data\databases\depgraph.db
# 恢复 __init__.py
git checkout -- src/zephyr/governance/behavioral_auditor/__init__.py
```

***

### STEP 5: 全量验证

**操作**：
运行完整验证套件，确认拆分无破坏。

**验证命令**（按顺序执行）：

```bash
# 1. pytest 收集（无 ImportError）
python -m pytest tests/ --collect-only -q

# 2. 关键模块导入测试
python scripts/governance/verify_key_imports.py

# 3. depgraph 诊断（无循环依赖）
python scripts/governance/diagnose_depgraph.py

# 4. 注册审计（无孤儿）
python scripts/governance/audit_registration.py

# 5. 路径树更新
python scripts/governance/generate_project_path_tree.py --write

# 6. 容量验证
python scripts/governance/extract_depgraph.py --summary
# 预期：D-SECURITY 134, D-BEHAVIORAL_AUDIT 60
```

**通过标准**：所有命令 exit 0，无 ImportError，无循环依赖，无孤儿。

**回滚**：

```bash
# 全量回滚到 STEP 1 之前的状态
copy /Y data\databases\depgraph.db.bak data\databases\depgraph.db
git checkout -- src/zephyr/security/access_control/behavioral_auditor/
git checkout -- src/zephyr/governance/behavioral_auditor/
git checkout -- src/zephyr/governance/
git checkout -- src/zephyr/infrastructure/
git checkout -- src/zephyr/ops/
git checkout -- src/zephyr/trading/
git checkout -- tests/
rmdir /S /Q src\zephyr\behavioral_audit
```

***

### STEP 6: 清理旧副本（70个.py）

**操作**：

1. 删除 `src/zephyr/governance/behavioral_auditor/` 下除 `__init__.py` 外的70个.py副本
2. 保留 `__init__.py`（作为 re-export shim，过渡期兼容）
3. 更新 `script-manifest.yaml` 和 `__init__.py` 导出

**安全删除依据**（全量审查结果）：

- 70个.py文件全部在 security/ 下有对应版本
- governance 版本0个独立符号（函数/类）
- security 版本覆盖全部符号且更多（6个文件有额外符号）

**验证命令**：

```bash
# 验证 governance/behavioral_auditor/ 只剩 __init__.py
dir /B src\zephyr\governance\behavioral_auditor\
# 预期：只有 __init__.py

# 验证无 import 残留
python scripts/governance/verify_import_migration.py

# 最终全量验证（同 STEP 5）
python -m pytest tests/ --collect-only -q
python scripts/governance/audit_registration.py
```

**回滚**：

```bash
# 从 git 恢复被删除的文件
git checkout -- src/zephyr/governance/behavioral_auditor/
```

***

## 执行顺序与依赖

```
STEP 0 (外部审查) → 28项全部PASS？ → YES → 直接进入 STEP 1 (备份+建域) → STEP 2 (迁移代码) → STEP 3 (更新import)
                        ↓ NO（发现FAIL）                                              ↓
                   就地修复计划文档 → 重新验证该项PASS → 继续下一项              STEP 4 (更新shim+DB)
                   （不重新整体审查，一口气模式）                                      ↓
                                                                   STEP 5 (全量验证)
                                                                        ↓
                                                                   STEP 6 (清理副本)
```

**禁止跳序**：STEP 0 审查未全部PASS禁止进入 STEP 1。每步必须验证通过后才进下一步。一口气模式：审查+执行在同一会话内完成，充分利用上下文缓存。

## 总回滚方案

如果任何步骤失败且无法修复：

```bash
# 1. 恢复 depgraph.db
copy /Y data\databases\depgraph.db.bak data\databases\depgraph.db

# 2. 恢复所有源码
git checkout -- src/zephyr/security/access_control/behavioral_auditor/
git checkout -- src/zephyr/governance/behavioral_auditor/
git checkout -- src/zephyr/governance/
git checkout -- src/zephyr/infrastructure/
git checkout -- src/zephyr/ops/
git checkout -- src/zephyr/trading/
git checkout -- tests/

# 3. 删除新目录
rmdir /S /Q src\zephyr\behavioral_audit

# 4. 验证恢复
python scripts/governance/extract_depgraph.py --summary
# 预期：回到39域，D-SECURITY 194 production 节点
```

## 执行者角色与职责

| 阶段       | 角色    | 执行者    | 职责                 | 铁律                     |
| -------- | ----- | ------ | ------------------ | ---------------------- |
| STEP 0   | 外部审查员 | Claude | 审查本计划7大类28项，输出审查报告 | 审查未通过禁止执行；禁止审查阶段做任何修改  |
| STEP 1-6 | 执行者   | Claude | 按审查通过的计划逐步执行       | 每步验证通过才进下一步；任何步骤失败立即回滚 |

**Claude 双重角色阶段分离原则**：

1. 先审查（STEP 0）：以对抗性视角找问题，输出审查报告
2. 审查通过后再执行（STEP 1-6）：以执行者视角按计划操作
3. 禁止合并两个角色——不能边审查边执行
4. 禁止跳过审查——即使你认为计划没问题，也必须完成28项审查并输出报告
