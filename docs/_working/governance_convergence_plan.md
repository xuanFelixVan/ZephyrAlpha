---
doc_type: construction_plan
ttl: task_bound
title: 治理体系收敛施工计划（AD-GOV-001 治本）
status: active
created_at: '2026-06-30T13:30:00Z'
created_by: session-20260630-governance-audit
based_on: docs/_working/governance_audit_report.yaml
approved_decisions: A/A/A（用户 2026-06-30 决策）
prerequisite: 当前 200+ 未提交修改必须先 commit（硬约束：治本变更未提交前禁止并发 AI 对话）
completes_when: "阶段2-4施工完成(49门禁→30 + 17reconciler→12 + worktree隔离上线 + create_guard阻断生效) + 验证命令全部PASS + AD-GOV-001教训入册architecture_issue_registry"
---

# 治理体系收敛施工计划

## 执行摘要

本计划落实用户 2026-06-30 的 A/A/A 三决策：

| 决策 | 选项 | 目标 | 对应阶段 |
|------|------|------|---------|
| A-1 治理收敛 | ≤30（激进） | 49 门禁 → 30 | 阶段 2 |
| A-2 worktree | 立即实施 | 根除 stash 循环 + AD-001 | 阶段 3 |
| A-3 create_guard | 阻断 | 无 creation_token 不能提交 | 阶段 4 |

**施工前置条件**（硬约束，不可绕过）：
1. 当前分支 `trae-redteam-deadly-5` 有 200+ 未提交修改（含 project_rules.md / gate_registry.yaml / directory_contract.yaml 等核心真源）
2. project_memory 硬约束："治本变更未提交前禁止并发 AI 对话"
3. trae_060 §4 第一性原理："治本优先于治标：根因不除，症状反复"

**因此**：阶段 2-4 的大规模文件修改必须等当前 200+ 修改 commit 后执行。本计划给出精确的合并映射表 + 回滚方案，供 commit 后立即施工。

---

## 阶段 2：门禁合并（49 → 30）

### 2.1 合并映射表

| # | 合并簇 | 原门禁 | 合并后 | 节省 | 合并方式 | 影响文件 |
|---|--------|--------|--------|------|---------|---------|
| 1 | 架构门禁 | GATE-01/02/03/06/07 | GATE-ARCH | -4 | 5 门禁共用 check_architecture_gates.py，合并为单 hook + 子命令参数 | .pre-commit-config.yaml, gate_registry.yaml, check_architecture_gates.py |
| 2 | 命名门禁 | GATE-11/11-SSOT | GATE-NAMING | -1 | 2 门禁共用 check_naming_convention.py，合并为单 hook + --validate-ssot 参数 | .pre-commit-config.yaml, gate_registry.yaml |
| 3 | 重复去重 | GATE-19(line 222) + GATE-19(line 308) | GATE-19 + GATE-21 | -1 | line 308 的静态清单漂移重命名为 GATE-21 | gate_registry.yaml |
| 4 | 文档前置 | GATE-15/C1/SSOT-DOCS | GATE-FRONTMATTER | -2 | 3 门禁都触发 ^docs/.*\.md$，合并为单 hook 多维度校验 | .pre-commit-config.yaml, gate_registry.yaml, check_frontmatter_metadata.py |
| 5 | SSoT 代码 | GATE-SSOT/SSOT-SINGLESOURCE | GATE-SSOT-CODE | -1 | 2 门禁都触发 ^src/zephyr/.*\.py$ 且都查 SSoT，合并 module_path + 文件名双检测 | .pre-commit-config.yaml, gate_registry.yaml, check_ssot_gate.py |
| 6 | 测试门禁 | GATE-18/19(test) | GATE-TEST | -1 | 测试收集 + 测试结构合规合并 | .pre-commit-config.yaml, gate_registry.yaml |
| 7 | 编码门禁 | GATE-BOM/ENCODING | GATE-ENCODING | -1 | BOM 是编码子集，GATE-ENCODING 已覆盖 | .pre-commit-config.yaml, gate_registry.yaml, 删 validate_no_utf8_bom.py |
| 8 | 脚本质量 | GATE-SQ/DD07 | GATE-SCRIPT-Q | -1 | 八维度质量 + _shared API 重定义合并 | .pre-commit-config.yaml, gate_registry.yaml |
| 9 | 文档引用 | GATE-DOC-REF → GATE-FRONTMATTER | - | -1 | 断链检测并入前置校验（同触发范围） | .pre-commit-config.yaml, gate_registry.yaml |
| 10 | 词表派生 | GATE-GENERATE → GATE-VOCAB | - | -1 | 词表派生一致性并入 GATE-VOCAB | .pre-commit-config.yaml, gate_registry.yaml |
| 11 | 注册同步 | GATE-IDX → GATE-REG-BL | - | -1 | 索引同步并入注册审计基线 | .pre-commit-config.yaml, gate_registry.yaml |
| 12 | 契约漂移 | GATE-CONTRACT-PHYSICAL-PATH → GATE-C2 | - | -1 | 物理路径连字符检测并入契约漂移 | .pre-commit-config.yaml, gate_registry.yaml |

**删除（孤儿/失效）**：

| # | 门禁 | 删除原因 | 影响文件 |
|---|------|---------|---------|
| D1 | GATE-PATH-NAMING | 假门禁（entry 非命令），连字符路径已被 directory_contract 覆盖 | .pre-commit-config.yaml, gate_registry.yaml |
| D2 | GATE-STASH | stash 机制将被 worktree 替代（阶段 3） | .pre-commit-config.yaml, gate_registry.yaml, cleanup_stash.py |
| D3 | GATE-MUT | 手动触发，死库存已归档，无自动消费方 | .pre-commit-config.yaml, gate_registry.yaml |

**计算**：49 - (4+1+1+2+1+1+1+1+1+1+1+1) - 3 = 49 - 16 - 3 = 30 ✓

### 2.2 合并施工步骤（每簇独立可回滚）

**每簇施工模板**（以簇 1 架构门禁为例）：
```
STEP 1: 备份
  git add -A && git commit -m "chore(backup): pre-GATE-ARCH-merge backup"

STEP 2: 修改 .pre-commit-config.yaml
  - 删除 GATE-01/02/03/06/07 五个 hook 条目
  - 新增 GATE-ARCH 单 hook（entry: check_architecture_gates.py --all）

STEP 3: 修改 gate_registry.yaml
  - 删除 GATE-01/02/03/06/07 五个 gate 条目
  - 新增 GATE-ARCH 单条目（category: architecture_reachability）

STEP 4: 修改 check_architecture_gates.py
  - 新增 --all 参数，依次执行原 5 个检查

STEP 5: 验证
  python scripts/governance/d5_architecture/checkers/check_architecture_gates.py --all --ci
  pre-commit run GATE-ARCH --all-files

STEP 6: 提交
  git add .pre-commit-config.yaml gate_registry.yaml check_architecture_gates.py
  git commit -m "refactor(gate): merge GATE-01/02/03/06/07 → GATE-ARCH (AD-GOV-001 簇1)"

STEP 7: 回滚（如失败）
  git revert HEAD
```

### 2.3 Reconciler 合并（17 → 12）

| # | 合并簇 | 原 reconciler | 合并后 | 节省 |
|---|--------|--------------|--------|------|
| R1 | 删除检测 | GATE-GHOST + GATE-WORKING-DOCS | GATE-DELETE-AUDIT | -1 |
| R2 | 重建检测 | GATE-DOMAIN-DOC + GATE-ARCH-MODEL | GATE-REGENERATE | -1 |
| R3 | 规则审计 | GATE-RULE-CATALOG + GATE-RULE-FILE-AUDIT | GATE-RULE-AUDIT | -1 |
| R4 | 注册同步 | GATE-REGISTRY-INDEX + GATE-REG-BL | GATE-REGISTRY-SYNC | -1 |
| R5 | 完整性审计 | GATE-RULES-INTEGRITY + GATE-COMMIT-GW-AUDIT | GATE-INTEGRITY-AUDIT | -1 |

**计算**：17 - 5 = 12

**施工位置**：
- `src/zephyr/governance/reconciliation_registry.py`（合并工厂函数）
- `src/zephyr/governance/git_commit_gateway.py:505-521`（合并注册调用）

---

## 阶段 3：git worktree 物理隔离（根除 stash 循环 + AD-001）

### 3.1 病根分析

**stash 循环根因**：
- 多 AI session 共享同一工作目录 → session A 的未提交修改被 session B 的 git 操作覆盖
- 当前缓解：StagingArea 草稿模式 + stash 堆积治理（GATE-STASH）
- 根因未除：stash 是"临时栈非备份"，多 session 仍共享工作目录

**AD-001 根因**：
- git_commit_gateway.py 职责过重（2500+ 行，11 个硬编码 _check_*）
- 根因：in-process gate 与 pre-commit hook 职责重叠，gateway 试图补偿 --no-verify 绕过的 45 个 hook

### 3.2 治本方案：git worktree 物理隔离

**架构**：
```
d:\ZephyrAlpha\                          # 主 worktree（main 分支，只读基准）
├── .aidrafts/
│   ├── session-20260630-001/            # session 1 独立 worktree
│   │   └── (git worktree: session-20260630-001 分支)
│   ├── session-20260630-002/            # session 2 独立 worktree
│   │   └── (git worktree: session-20260630-002 分支)
│   └── ...
```

**每个 session 独立 worktree**：
- 物理隔离：session A 的修改不影响 session B
- 无需 stash：session 结束时 merge 回主分支或丢弃
- 并发安全：git worktree 原生支持多分支并发

### 3.3 施工步骤

```
STEP 1: 创建 worktree 管理脚本
  scripts/governance/worktree_manager.py
  - create_session_worktree(session_id) → 创建 .aidrafts/{session_id}/ worktree
  - merge_session_worktree(session_id) → merge 回主分支
  - cleanup_session_worktree(session_id) → 删除 worktree

STEP 2: 修改 GitCommitGateway
  - commit() 方法新增 worktree 检测：若在 session worktree 内，直接 commit（无需 stash）
  - 删除 stash 隔离逻辑（被 worktree 替代）
  - 删除 GATE-STASH 门禁

STEP 3: 修改 lock_files.py
  - 锁文件路径改为跨 worktree 共享（.runtime/locks/，不在 worktree 内）
  - 或改为 per-worktree 锁（session 内无需锁，跨 session 由 merge 保障）

STEP 4: 更新 project_rules.md RULE-ZERO
  - 新增"多 AI 并发协议（worktree 隔离）"
  - 废弃 StagingArea 草稿模式

STEP 5: GitCommitGateway 瘦身（AD-001 治本）
  - 删除 11 个硬编码 _check_*（已被 CommitGateRegistry 4 个 in-process gate 替代）
  - commit() 方法体仅保留 registry.check_all() 调用
  - 预期瘦身：2500 行 → ~800 行
```

### 3.4 回滚方案

```
# 若 worktree 隔离失败，回滚到 stash 模式
git revert <worktree-commits>
# 恢复 GATE-STASH
git checkout <pre-worktree> -- .pre-commit-config.yaml
# 恢复 stash 逻辑
git checkout <pre-worktree> -- src/zephyr/governance/git_commit_gateway.py
```

---

## 阶段 4：create_guard 阻断模式（无 creation_token 不能提交）

### 4.1 病根分析

**"造第二真源"根因**：
- 新建 .py 文件时，AI 可能复制已有实现（违反 trae_060 §2）
- 当前缓解：GATE-SSOT（module_path 冲突检测）+ GATE-SSOT-SINGLESOURCE（文件名检测）+ capability_overlap_gate（warn-only）
- 根因未除：检测在 commit 时，此时文件已写完；应在"创建前"阻断

### 4.2 治本方案：create_guard 阻断模式

**架构**：
```
新建 .py 文件 → create_guard 检查 creation_token
  - 有 token：放行（token 来自 CapabilityLookup 已登记）
  - 无 token：硬阻断（exit 1）
```

**creation_token 机制**：
- token 存储在 `capability_canonical_file_registry.yaml` 的 `creation_tokens` 字段
- AI 新建 .py 前，先 `CapabilityLookup.find("功能关键词")` 确认无可用现成实现
- 若确认需新建，通过 `scaffold.py` 生成 token（自动写入 registry）
- commit 时 create_guard 校验 .py 文件是否有对应 token

### 4.3 施工步骤

```
STEP 1: 新建 create_guard.py
  src/zephyr/governance/commit_gates/create_guard.py
  - make_create_guard() → GateSpec
  - check: 扫描 staged .py 文件，查 capability_canonical_file_registry.yaml 的 creation_tokens
  - 无 token → 硬阻断（exit 1），提示 "无 creation_token，禁止造第二真源（trae_060 §2）"

STEP 2: 扩展 capability_canonical_file_registry.yaml
  新增 creation_tokens 字段：
    creation_tokens:
      - file: src/zephyr/shared/io/file_utils.py
        token: auto-generated-<hash>
        created_by: session-20260630-001
        capability: atomic_write

STEP 3: 修改 scaffold.py
  - 新建 .py 时自动生成 creation_token 并写入 registry
  - 无 token 的 .py 无法通过 create_guard

STEP 4: 注册到 CommitGateRegistry
  git_commit_gateway.py:343-346 新增：
  registry.register(make_create_guard())  # priority=60

STEP 5: 集成到 .pre-commit-config.yaml
  新增 GATE-CREATE hook（pre-commit 层双保险）
```

### 4.4 回滚方案

```
# 若 create_guard 误阻断合法新建
git revert <create-guard-commits>
# 或临时降级为 warn-only
# 修改 create_guard.py: exit(1) → print(warning)
```

---

## 阶段 5：验证命令清单

### 5.1 门禁合并验证

```bash
# 1. 门禁数量验证
python -c "import yaml; r=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml',encoding='utf-8')); print(f'gates: {len(r[\"gates\"])}')"
# 预期: 30

# 2. reconciler 数量验证
python -c "import ast; t=ast.parse(open('src/zephyr/governance/reconciliation_registry.py',encoding='utf-8').read()); print(f'make_*_reconciler: {sum(1 for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name.startswith(\"make_\"))}')"
# 预期: 12

# 3. pre-commit hook 验证
pre-commit run --all-files
# 预期: 全部 PASS

# 4. GATE-19 去重验证
python -c "import yaml; r=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml',encoding='utf-8')); ids=[g['gate_id'] for g in r['gates']]; print(f'duplicates: {[x for x in ids if ids.count(x)>1]}')"
# 预期: []
```

### 5.2 worktree 隔离验证

```bash
# 1. worktree 创建验证
python scripts/governance/worktree_manager.py create test-session
ls .aidrafts/test-session/
# 预期: 独立 worktree 目录

# 2. 并发隔离验证
# session A 在 worktree A 修改文件
# session B 在 worktree B 修改同一文件
# 互不影响，merge 时无冲突

# 3. GitCommitGateway 瘦身验证
wc -l src/zephyr/governance/git_commit_gateway.py
# 预期: ≤800 行（原 2500+）
```

### 5.3 create_guard 验证

```bash
# 1. 无 token 阻断验证
echo "def fake(): pass" > /tmp/test_no_token.py
git add /tmp/test_no_token.py
git commit -m "test"
# 预期: 硬阻断，exit 1

# 2. 有 token 放行验证
python scripts/scaffold.py script test_with_token --capability test
git add scripts/test_with_token.py
git commit -m "test"
# 预期: 放行
```

---

## 阶段 6：教训入册（已完成）

已在 `project_memory.md` Hard Constraints 追加（2026-06-30）：
- 治理体系收敛期声明（AD-GOV-001）
- git worktree 物理隔离决策
- create_guard 阻断模式决策

**待入册**（施工完成后）：
- architecture_issue_registry.yaml 登记 AD-GOV-001（治理军备竞赛陷阱）
- trae_060_inward_consolidation.yaml §5 更新（合并簇已收敛 evidence）

---

## 施工时序与依赖

```
当前状态: 200+ 未提交修改（含核心真源）
    ↓
[前置] commit 当前 200+ 修改（用户决策：是否 commit）
    ↓
[阶段 2] 门禁合并 49→30（12 簇 + 3 删除，每簇独立可回滚）
    ↓
[阶段 3] git worktree 物理隔离（根除 stash + AD-001 瘦身）
    ↓
[阶段 4] create_guard 阻断模式（无 token 不能提交）
    ↓
[阶段 5] 验证 + 教训入册
```

**依赖关系**：
- 阶段 2 与阶段 3 可并行（互不依赖）
- 阶段 4 依赖阶段 3（create_guard 注册到瘦身后的 GitCommitGateway）
- 阶段 5 依赖 2/3/4 全部完成

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 合并后门禁漏检 | 中 | 高 | 每簇合并后跑 pre-commit run --all-files 验证 |
| worktree 兼容性 | 低 | 高 | 先在测试分支验证，main 分支保留 stash 模式兜底 |
| create_guard 误阻断 | 中 | 中 | scaffold.py 自动生成 token，避免手工遗漏 |
| 现有 200+ 修改冲突 | 高 | 高 | 前置 commit 后再施工，不叠加 |

---

## 附录：审计报告引用

本计划基于 `docs/_working/governance_audit_report.yaml` 的审计数据。关键发现：
- 49 门禁中 10 个 warn-only（假门禁）
- GATE-19 重复登记 2 次
- GATE-PATH-NAMING entry 非命令（假门禁）
- 17 reconciler 中 5 组触发条件重叠
- trae_060 §5 的 6 簇中 5 簇确证成立（多份独立实现）
