# Claude 架构债务执行指令（v1）

> **角色**：你是 ZephyrAlpha 项目的外部架构执行员，负责执行 9 项架构债务清理任务。
> **执行原则**：纯陈述句（见 trae_030 GOV-DOC-016）；最小变更（见 onboarding_detail.md §九）；搜索先行（RULE-EIGHT）；加锁写入（RULE-ZERO）。
> **裁定权限**：P1/P2 交 Owner 决策；P3 自主裁定（基于专业实践+量化数据）。

---

## 前置阅读（必读）

| 序号 | 文件 | 用途 |
|:---:|------|------|
| 1 | d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_055_arch_domain_capacity.yaml | 架构容量与域治理规则（9条裁定） |
| 2 | d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml §gov_doc_016_pure_assertion | 纯陈述原则（禁止否定陈述句） |
| 3 | d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml | depgraph 程序化访问协议（禁止直接 Read/Write depgraph.db） |
| 4 | d:/ZephyrAlpha/.trae/rules/onboarding_detail.md §一~§九 | 四条铁律+并发安全+反孤儿+任务粒度+修改原则 |
| 5 | d:/ZephyrAlpha/docs/02_enterprise_architecture/architecture_upgrade_discussion.md | 架构升级决策记录（D1-D78） |

**前置阅读确认**：读完上述 5 个文件后，输出"前置阅读完成，开始执行任务 X"。

---

## 任务 0：审查 trae_055 规则文档

**目标**：审查 trae_055_arch_domain_capacity.yaml 有无逻辑漏洞、表述歧义、规则冲突。

**审查清单**：

| # | 审查项 | 判定标准 |
|---|--------|---------|
| 1 | 9条裁定逻辑一致性 | ARCH-CAP-001~009 之间无逻辑矛盾 |
| 2 | 表述纯陈述性 | 无否定陈述句（"已废止"/"旧定义"等），见 GOV-DOC-016 |
| 3 | 数字准确性 | 802 production 节点、39域、80-150/150-200/200 等数字与 depgraph.db 一致 |
| 4 | 命令可执行性 | 所有 python scripts/... 命令路径正确且可执行 |
| 5 | 与其他规则冲突 | 与 trae_013/trae_028/trae_032 等无未解决的冲突 |
| 6 | 抽屉式扩展可行性 | ARCH-CAP-005 的 domains 表 INSERT 流程是否可行（需验证 domains 表 schema） |
| 7 | 拆分审批流程完整性 | ARCH-CAP-006 的 5 步流程是否覆盖所有边界情况 |
| 8 | 硬件上限表述准确性 | "64GB 内存可支撑 10万+ 节点"是否有量化依据 |

**输出格式**：

```
## trae_055 审查报告

### P1 问题（必须修复）
- [问题编号] 位置: 描述 → 修复建议

### P2 问题（建议修复）
- [问题编号] 位置: 描述 → 修复建议

### P3 观察（供参考）
- [观察编号] 描述

### 审查结论
- 通过 / 需修复后重新审查
```

**审查通过后**：继续执行任务 1-8。审查未通过时：修复 P1 问题后重新审查，连续两次零 P1 才能继续。

---

## 任务 1：extract_depgraph.py 升级（添加 production_nodes 字段）

**背景**：trae_055 ARCH-CAP-001 要求按 production 节点口径统计模块数，但 extract_depgraph.py --summary 当前只输出 module_count（含三态节点），没有 production_nodes 字段。

**目标**：升级 extract_depgraph.py，在 --summary 输出中添加各域的 production_nodes 字段。

**执行步骤**：

1. 读取 d:/ZephyrAlpha/scripts/governance/extract_depgraph.py，定位 --summary 命令的输出逻辑
2. 查询 depgraph.db 的 nodes 表，统计每个域的 production 节点数（WHERE design_maturity='production'）
3. 在 --summary 的 JSON 输出中，每个域对象添加 production_nodes 字段
4. 保留现有 module_count 字段（向后兼容）
5. 运行 `python scripts/governance/extract_depgraph.py --summary` 验证输出包含 production_nodes
6. 验证各域 production_nodes 之和 = 802（当前 production 节点总数）

**验收标准**：
- `python scripts/governance/extract_depgraph.py --summary` 输出每个域包含 production_nodes 字段
- production_nodes 之和 = 802
- 现有 module_count 字段保留不变

---

## 任务 2：容量策略重设（按 production 节点口径）

**背景**：trae_055 ARCH-CAP-002 要求单域 production 节点 80-150 默认 / 150-200 高度耦合 / 200 硬上限。当前 depgraph.db domains 表的 max_modules 字段是按 current_modules 反推的伪设计值。

**目标**：按 production 节点口径重设 39 域的 max_modules。

**执行步骤**：

1. 运行 `python scripts/governance/extract_depgraph.py --summary`（任务 1 完成后）获取各域 production_nodes
2. 按以下规则计算每个域的 max_modules：
   - production_nodes ≤ 80：max_modules = 150（预留增长空间）
   - production_nodes 80-150：max_modules = 200（默认上限）
   - production_nodes 150-200：max_modules = 200（高度耦合上限）
   - production_nodes > 200：标记为 NEEDS_SPLIT，max_modules 保持 200（拆分前不扩容）
3. 生成变更 JSON 文件（apply_depgraph.py 批量更新格式）
4. 运行 `python scripts/governance/apply_depgraph.py --batch changes.json --dry-run` 验证
5. 运行 `python scripts/governance/apply_depgraph.py --batch changes.json` 执行
6. 运行 `python scripts/governance/extract_depgraph.py --summary` 验证更新结果

**验收标准**：
- 39 域 max_modules 全部更新为 production 节点口径
- 仅 D-GOVERNANCE(406>200) 标记为 NEEDS_SPLIT；D-SECURITY(194) 在 150-200 区间需评估高度耦合四标准后决定；其余域 production<18 不拆分
- max_modules 计算规则：production=0→150 / 1-80→150 / 80-150→200 / 150-200→200 / >200→200+NEEDS_SPLIT
- dry-run 无错误

**注意**：此任务依赖任务 1 完成（需要 production_nodes 字段）。

---

## 任务 3：生成器动态化重构（ARCH-CAP-009）

**背景**：trae_055 ARCH-CAP-005 要求抽屉式扩展（新增域只 INSERT domains 表），但 generate_project_depgraph.py 有 3 处硬编码违反此原则。

**目标**：消除 3 处硬编码，改为从 domains 表动态加载。

**硬编码位置**：

| # | 硬编码名 | 位置 | 当前内容 |
|---|---------|------|---------|
| 1 | DOMAIN_NAME_TO_LAYER | generate_project_depgraph.py | 域→层映射字典 |
| 2 | NON_SRC_DOMAIN_MAP | generate_project_depgraph.py L221 | 16条旧域→父域映射 |
| 3 | UNREGISTERED_SRC_MAP | generate_project_depgraph.py | 78条旧域→父域映射 |

**执行步骤**：

1. 备份 generate_project_depgraph.py 到 .aidrafts/ 或 git stash
2. 创建 domain_mapping 表（存储旧域→新域归并/拆分/重命名映射）：
   ```sql
   CREATE TABLE IF NOT EXISTS domain_mapping (
       mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
       old_domain_id TEXT NOT NULL,
       new_domain_id TEXT NOT NULL,
       mapping_type TEXT NOT NULL,  -- merge/split/rename
       mapped_at TEXT NOT NULL,
       mapped_by TEXT NOT NULL,
       note TEXT
   );
   CREATE INDEX IF NOT EXISTS idx_domain_mapping_old ON domain_mapping(old_domain_id);
   CREATE INDEX IF NOT EXISTS idx_domain_mapping_new ON domain_mapping(new_domain_id);
   ```
3. 将 NON_SRC_DOMAIN_MAP 的 16 条旧域→父域映射 INSERT 到 domain_mapping 表（mapping_type='merge'）
4. 将 UNREGISTERED_SRC_MAP 的 78 条旧域→父域映射 INSERT 到 domain_mapping 表（mapping_type='merge'）
5. 重构 DOMAIN_NAME_TO_LAYER：改为从 domains 表 layer_id 字段动态加载
6. 重构 NON_SRC_DOMAIN_MAP：改为从 domain_mapping 表查询 `SELECT old_domain_id, new_domain_id FROM domain_mapping WHERE mapping_type='merge'`
7. 重构 UNREGISTERED_SRC_MAP：同上（与 NON_SRC_DOMAIN_MAP 共用 domain_mapping 表）
8. 运行 `python scripts/governance/extract_depgraph.py --summary` 验证输出与重构前一致
9. INSERT 一个测试域到 domains 表 → 运行生成器 → 验证测试域被正确识别 → DELETE 测试域

**验收标准**：
- 3 处硬编码全部消除
- domain_mapping 表创建完成，16+78=94 条映射数据导入
- 生成器从 domains 表动态加载 domain→layer 映射
- 生成器从 domain_mapping 表动态加载旧域→新域映射
- 测试域 INSERT 后能被生成器正确识别（抽屉式扩展验证）
- 重构前后 extract_depgraph.py --summary 输出一致

**注意**：架构升级期间禁止运行 generate_project_depgraph.py（会覆盖 depgraph.db）。使用 extract_depgraph.py --summary 验证。

---

## 任务 4：D-GOVERNANCE 拆分成 4 个平行域

**背景**：D-GOVERNANCE 有 406 个 production 节点（实测），超过 200 硬上限 2 倍。trae_055 ARCH-CAP-002/004 要求拆分成平行域。这是唯一超过 200 硬上限的域（D-SECURITY=194 在 150-200 区间，需评估高度耦合后决定是否拆分）。

**目标**：D-GOVERNANCE 拆分成 4 个平行域：D-GOV_AUDIT / D-GOV_DRIFT / D-GOV_RULE / D-GOVERNANCE（保留核心）。

**⚠️ Owner 审批要求**：此任务 MUST 经 Owner 详细讨论并同意拆分方案后才能执行（ARCH-CAP-006）。AI 先输出拆分方案，等 Owner 确认。

**执行步骤**：

1. 分析 D-GOVERNANCE 的 production 节点，按功能归类：
   - D-GOV_AUDIT：审计相关模块（audit/audit_trail/audit_orchestrator 等）
   - D-GOV_DRIFT：漂移检测相关模块（drift/detector/diagnose 等）
   - D-GOV_RULE：规则治理相关模块（rule/sync/registry 等）
   - D-GOVERNANCE：保留核心治理模块（_core/_delegation/_detection 等）
2. 输出拆分方案（含新域 domain_id/layer/blueprint_id、模块归属映射、跨域依赖迁移清单、回滚方案）
3. **等 Owner 确认拆分方案**
4. Owner 确认后，通过 apply_depgraph.py 执行：
   - INSERT 3 个新域到 domains 表（D-GOV_AUDIT/D-GOV_DRIFT/D-GOV_RULE）
   - UPDATE 受影响模块的 domain 字段为新域
   - UPDATE domain_dependencies 表迁移跨域依赖
5. 运行 `python scripts/governance/extract_depgraph.py --summary` 验证 4 个域的 production_nodes 均 ≤200
6. 运行 `python scripts/governance/diagnose_depgraph.py` 确认无循环依赖

**验收标准**：
- D-GOVERNANCE 拆分成 4 个平行域
- 每个新域 production_nodes ≤200
- 无新循环依赖
- 拆分方案经 Owner 确认

---

## 任务 5：跨域文件物理迁移

**背景**：22 个文件物理路径在 src/zephyr/governance/ 下，但 [DOMAIN] 字段指向其他域（D-TRADING/D-MKT_DATA 等）。trae_055 ARCH-CAP-004 要求物理路径与域归属对齐。

**目标**：将 22 个跨域文件迁移到正确的域目录。

**执行步骤**：

1. 提取 22 个跨域文件清单（Grep `\[DOMAIN\]` in src/zephyr/governance/*.py）
2. 读取每个文件的 [DOMAIN] 字段，确定目标域
3. 按目标域分组，输出迁移清单（源路径→目标路径）
4. **等 Owner 确认迁移清单**（涉及大量 import 更新）
5. Owner 确认后，按 RULE-TEN 治理流程执行：
   - STEP 1: 依赖图推演（确认无新循环）
   - STEP 2: 蓝图归属确认
   - STEP 3: 导入路径映射（Grep 全项目 import 引用）
   - STEP 4: 执行迁移（加锁+移动文件+更新 import）
   - STEP 5: 验证（extract_depgraph.py --summary + diagnose_depgraph.py）
6. 运行 `python scripts/governance/audit_registration.py` 确认无孤儿

**验收标准**：
- 22 个跨域文件物理路径与 [DOMAIN] 字段对齐
- 所有 import 引用更新正确
- 无新循环依赖
- 无孤儿文件

---

## 任务 6：God 模块拆分

**背景**：src/zephyr/governance/__init__.py 被 839 处依赖，是 God 模块。trae_055 ARCH-CAP-002 要求单域 ≤200，God 模块违反此原则。

**目标**：拆分 governance/__init__.py 为多个职责单一的小模块。

**⚠️ Owner 审批要求**：此任务影响 839 处依赖，MUST 经 Owner 确认拆分方案。

**执行步骤**：

1. 分析 governance/__init__.py 的内容，按职责归类
2. 输出拆分方案（新模块清单+职责划分+839处依赖更新计划+回滚方案）
3. **等 Owner 确认拆分方案**
4. Owner 确认后执行拆分（加锁+创建新模块+更新839处import）
5. 验证 `python -m pytest tests/ --collect-only -q` 无 ImportError

**验收标准**：
- governance/__init__.py 拆分为多个职责单一模块
- 839 处 import 全部更新正确
- pytest --collect-only 无 ImportError

---

## 任务 7：孤儿目录清理

**背景**：data/、orchestration/ 目录被识别为孤儿目录（无注册表引用）。

**目标**：评估并清理孤儿目录。

**执行步骤**：

1. 运行 `python scripts/governance/audit_registration.py` 获取孤儿清单
2. 按 RULE-THREE 三步审判评估每个孤儿：
   - STEP 1: 登记检查（是否在 manifest/registry/__init__.py 中被引用）
   - STEP 2: 重复检查（是否有另一个文件与它内容相同）
   - STEP 3: 功能价值检查（3a 独立功能价值/3b 客观原因/3c 重建成本）
3. 输出清理方案（删除/保留并接通/迁移）
4. **等 Owner 确认清理方案**
5. Owner 确认后执行清理

**验收标准**：
- 孤儿目录评估完成
- 清理方案经 Owner 确认
- audit_registration.py exit 0

---

## 任务 8：业务域互依审查

**背景**：1370 条跨域依赖边，部分业务域之间存在互依（违反 ARCH-001 向下依赖原则）。

**目标**：审查业务域互依，识别违规依赖并修复。

**执行步骤**：

1. 运行 `python scripts/governance/extract_depgraph.py --paths` 获取文件级依赖
2. 按域分组统计跨域依赖边
3. 识别向上依赖（业务域→平台域的反向依赖）和循环依赖
4. 输出违规依赖清单（源域→目标域+违规类型+修复建议）
5. **等 Owner 确认修复方案**（涉及模块迁移）
6. Owner 确认后执行修复

**验收标准**：
- 1370 条跨域依赖边审查完成
- 违规依赖识别并修复
- diagnose_depgraph.py 无循环依赖

---

## 执行顺序

```
任务 0: 审查 trae_055（前置）
  ↓ 通过
任务 1: extract_depgraph.py 升级
  ↓ 完成
任务 2: 容量策略重设（依赖任务 1）
  ↓ 完成
任务 3: 生成器动态化重构
  ↓ 完成
任务 4: D-GOVERNANCE 拆分（需 Owner 审批）
  ↓ Owner 确认后执行
任务 5: 跨域文件迁移（需 Owner 审批）
  ↓ Owner 确认后执行
任务 6: God 模块拆分（需 Owner 审批）
  ↓ Owner 确认后执行
任务 7: 孤儿目录清理（需 Owner 审批）
  ↓ Owner 确认后执行
任务 8: 业务域互依审查（需 Owner 审批）
  ↓ Owner 确认后执行
最终验证: extract_depgraph.py --summary + diagnose_depgraph.py + audit_registration.py
```

**并行可能性**：任务 1/2/3 可串行执行（有依赖）；任务 4-8 需 Owner 审批，可并行准备方案。

---

## 输出要求

### 每个任务完成后输出：

```
## 任务 X 完成报告

### 执行结果
- [步骤1] 完成/失败
- [步骤2] 完成/失败
...

### 验收结果
- [验收项1] 通过/未通过
- [验收项2] 通过/未通过
...

### 修改文件清单
- d:/ZephyrAlpha/... (修改类型)

### P1/P2 问题
- [问题编号] 描述 → 处置
```

### 需 Owner 决策时输出：

```
## ⚠️ 需 Owner 决策：任务 X

### 决策项
[问题描述]

### 方案选项
- 方案 A: [描述] → 影响: [影响范围]
- 方案 B: [描述] → 影响: [影响范围]

### AI 建议
[基于专业实践的建议]

### 等 Owner 确认
```

---

## 铁律提醒

| 铁律 | 要求 |
|------|------|
| RULE-ZERO | 写入文件前 MUST 加锁（python scripts/lock_files.py acquire） |
| RULE-FOUR | 创建新文件 MUST 走 scaffold.py |
| RULE-THREE | 删除文件前 MUST 三步审判 |
| RULE-EIGHT | 新建功能前 MUST 搜索已有 |
| RULE-SIXTEEN | 禁止直接 Read/Write depgraph.db，MUST 通过 extract_depgraph.py/apply_depgraph.py |
| GOV-DOC-016 | 规则文档只包含肯定陈述句，禁止否定陈述句 |
| §九 修改原则 | 直接修正为新规则，不留过渡文本 |
