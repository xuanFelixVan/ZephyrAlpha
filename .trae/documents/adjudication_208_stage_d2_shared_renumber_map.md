---
title: 裁定#208 阶段 D2 跨域共享模块重命名映射表
ttl: task_bound
purpose: MOD-SHARED/MOD-DATABASE/MOD-SHARECONTRACTS 三个违规片段重命名映射（D1裁定→D2映射→D3执行→D4验证）
source: stage_d_semantic_classification.md §9.2 + D2真源核实(scripts/_tmp_d2_verify.py)
adjudication: '208'
stage: D2
status: superseded
superseded_at: '2026-06-26'
superseded_by: 'D3 执行完毕 + D4 验证通过；真源已迁移至 depgraph.db(nodes.blueprint_id) + YAML(blueprint_registry.yaml 等 6 文件) + 代码头(51 文件) + 蓝图文档(5 文件)'
---

# 裁定#208 阶段 D2 跨域共享模块重命名映射表

> ⚠️ **SUPERSEDED（2026-06-26）**：本映射表已执行完毕（D3 执行 + D4 验证全部通过）。
> 真源已迁移至 DB + YAML + 代码头 + 蓝图文档。
> **禁止再次执行本表的改名操作**——会破坏已落地的 103 节点 + 29 级联 + 51 代码头 + 5 蓝图。
> 本文档仅作历史决策记录保留，供未来 AI 追溯 SH-DB-001 / SH-MAIN-001 / MOD-SHARED-002 的命名由来。

> **文档定位**：D1 语义分类裁定后的重命名映射表，**暂停确认点**（已确认并执行完毕）。
> **数据来源**：stage_d_semantic_classification.md §9.2 + D2 真源核实（scripts/_tmp_d2_verify.py，2026-06-26）。
> **前序工作**：D1 分类完成（3 违规 103 节点）+ N-06 SH-* 正则校验已扩展（治本门禁）。
> **本轮范围**：仅处理 MOD-SHARED/MOD-DATABASE/MOD-SHARECONTRACTS 三个单字格式违规片段。前一轮 D3（下划线格式 MOD_INF_012 等）已执行完毕，不在本轮范围。

---

## 一、映射表（3 个违规片段 → 3 个新 ID）

| # | 原 blueprint_id | 新 blueprint_id | 节点数 | ID 轨 | 裁定依据 |
|---|-----------------|-----------------|--------|-------|----------|
| 1 | MOD-SHARED | SH-MAIN-001 | 61 | 跨域共享轨 | layer=shared，跨域共享主模块（src/zephyr/shared/*.py 各工具），用 SH-{ABBR}-{NNN}；ABBR=MAIN |
| 2 | MOD-DATABASE | SH-DB-001 | 41 | 跨域共享轨 | layer=cross_layer，跨域数据库基础设施（4 域共享），用 SH-{ABBR}-{NNN}；ABBR=DB |
| 3 | MOD-SHARECONTRACTS | MOD-SHARED-002 | 1 | 派生轨 | layer=L0_infrastructure（非 shared），D-SHARED 域 contracts 子模块，用派生轨 MOD-SHARED-NNN；**修正：-001 已被 A2A 协议占用** |
| | **合计** | | **103** | | |

### 1.1 D2 真源核实修正

D1 分类表 §9.2 初版提议 MOD-SHARECONTRACTS → MOD-SHARED-001，但 D2 真源核实发现 MOD-SHARED-001 已存在（9 节点，A2A 协议模块），故修正为 MOD-SHARED-002。详见 stage_d_semantic_classification.md §9.5。

### 1.2 新 ID 冲突检查（真源核实）

| 新 ID | DB 中是否存在 | 状态 |
|-------|--------------|------|
| SH-MAIN-001 | 0 节点 | ✅ 无冲突 |
| SH-DB-001 | 0 节点 | ✅ 无冲突 |
| MOD-SHARED-002 | 0 节点 | ✅ 无冲突 |
| MOD-SHARED-001（现有，保留） | 9 节点 | 不改名（A2A 协议模块） |

---

## 二、影响范围（真源核实，非估算）

### 2.1 DB nodes.blueprint_id UPDATE（103 行）

| 原 ID | 域分布 | production | prototype/design | 小计 |
|-------|--------|------------|------------------|------|
| MOD-SHARED | D-SHARED (61) | 56 | 5 | 61 |
| MOD-DATABASE | D-GOVERNANCE (24) + D-INFRA_RUNTIME (14) + D-OPS (2) + D-AUDITTEST (1) | 15 | 26 | 41 |
| MOD-SHARECONTRACTS | D-SHARED (1) | 0 | 1 | 1 |
| **合计** | | **71** | **32** | **103** |

### 2.2 DB 级联清理

| 原 ID | type_specific_data 引用 | blueprint_path 引用 | 小计 |
|-------|------------------------|--------------------|----|
| MOD-SHARED | 0 | 0 | 0 |
| MOD-DATABASE | 27 | 2 | 29 |
| MOD-SHARECONTRACTS | 0 | 0 | 0 |
| **合计** | **27** | **2** | **29** |

**级联清理字段**：
1. type_specific_data JSON 中的 module_id 字段 + doc_references 数组
2. blueprint_path 缓存列（`docs/03_modules/MOD-DATABASE/` → `docs/03_modules/SH-DB-001/`）

### 2.3 代码文件头同步

| 原 ID | 文件数 | 路径模式 | 替换规则 |
|-------|--------|----------|----------|
| MOD-SHARED（无序号） | 50 | `src/zephyr/shared/**/*.py` | `# [BLUEPRINT] MOD-SHARED ` → `# [BLUEPRINT] SH-MAIN-001 ` |
| MOD-SHARECONTRACTS | 1 | `src/zephyr/shared/contracts/backpressure/_types.py` | `# [BLUEPRINT] MOD-SHARECONTRACTS ` → `# [BLUEPRINT] MOD-SHARED-002 ` |
| **合计** | **51** | | |

**边界保护**：替换 MOD-SHARED 时必须用正则 `MOD-SHARED(?![A-Za-z0-9_-])`（负向前瞻），确保不误改 `MOD-SHARED-001`（A2A 协议模块，8 文件头保留不动）。

### 2.4 蓝图文档同步

| 原 ID | 文件数 | 路径 | 替换内容 |
|-------|--------|------|----------|
| MOD-DATABASE | 5 | `docs/03_modules/_cross_layer/database/` 下 5 文件 | frontmatter `module_id: MOD-DATABASE` → `module_id: SH-DB-001` + 正文引用 |
| MOD-SHARED | 0 | 无蓝图文档 | — |
| MOD-SHARECONTRACTS | 0 | 无蓝图文档 | — |
| **合计** | **5** | | |

MOD-DATABASE 的 5 个蓝图文件：
1. `docs/03_modules/_cross_layer/database/blueprint.md`
2. `docs/03_modules/_cross_layer/database/index.md`
3. `docs/03_modules/_cross_layer/database/sub_blueprints/MOD-INF-012B-P2-postgresql-migration.md`
4. `docs/03_modules/_cross_layer/database/sub_blueprints/MOD-INF-012B-P3-postgresql-optimization.md`
5. `docs/03_modules/_cross_layer/database/sub_blueprints/MOD-INF-012B-P3-task-cards.md`

### 2.5 活文档引用

需执行时 grep 精确定位活文档中的旧 ID 引用（排除历史数据豁免清单）。

### 2.6 历史数据豁免（不改）

| 路径 | 不改原因 |
|------|----------|
| `src/data/telemetry/blueprint_reads.jsonl` | 遥测事件日志，历史事实记录 |
| `docs/08_knowledge/04_archived/*.md` | 知识库存档快照 |
| `docs/08_knowledge/01_raw_intake/*.md` | 知识库原始摄入 |

### 2.7 影响范围汇总

| 同步项 | 数量 | 处理 |
|--------|------|------|
| DB blueprint_id UPDATE | 103 行 | 必改 |
| DB type_specific_data 级联 | 27 处 | 必改 |
| DB blueprint_path 级联 | 2 处 | 必改 |
| 代码文件头 | 51 文件 | 必改 |
| 蓝图文档 | 5 文件 | 必改 |
| 活文档引用 | grep 确认 | 必改 |
| 制品刷新 | 2 文件 | 自动 |
| 历史数据 | 豁免 | 不改 |

---

## 三、执行顺序（D3，待确认后执行）

### 3.1 执行顺序设计原则

1. **先大后小**：先处理影响最大的 MOD-SHARED（61 节点 + 50 代码头），释放"MOD-SHARED"前缀
2. **独立并行**：MOD-DATABASE 与 MOD-SHARED 无交集，可独立执行
3. **最后创建新派生轨 ID**：MOD-SHARECONTRACTS → MOD-SHARED-002 必须在 MOD-SHARED 消除后执行，避免字符串替换冲突

### 3.2 步骤明细

| 步骤 | 操作 | 影响 | 验证 |
|------|------|------|------|
| 0 | git 备份 depgraph.db | — | GitCommitGateway |
| 1 | MOD-SHARED → SH-MAIN-001 | 61 节点 UPDATE + 50 代码头 | ro SQL + grep |
| 2 | MOD-DATABASE → SH-DB-001 | 41 节点 UPDATE + 27 TSD + 2 BP_PATH + 5 蓝图 | ro SQL + grep |
| 3 | MOD-SHARECONTRACTS → MOD-SHARED-002 | 1 节点 UPDATE + 1 代码头 | ro SQL + grep |
| 4 | 活文档引用同步 | grep 精确定位 | grep 验证清零 |
| 5 | 制品刷新 | 2 文件 | 自动 |
| 6 | ro SQL 复测 | 3 旧 ID = 0 | GLOB 精确 |
| 7 | 清理临时脚本 | _tmp_d*.py | 零残留 |

### 3.3 字符串替换安全规则

| 替换 | 正则模式 | 边界保护 |
|------|----------|----------|
| MOD-SHARED → SH-MAIN-001 | `MOD-SHARED(?![A-Za-z0-9_-])` | 不匹配 MOD-SHARED-001（A2A 协议保留） |
| MOD-DATABASE → SH-DB-001 | `MOD-DATABASE(?![A-Za-z0-9_-])` | 无冲突 |
| MOD-SHARECONTRACTS → MOD-SHARED-002 | `MOD-SHARECONTRACTS(?![A-Za-z0-9_-])` | 不匹配其他 ID |

---

## 四、容量预检

| 域 | 当前 production_nodes | 新增 | 合计 | 限制 | 状态 |
|----|----------------------|------|------|------|------|
| D-SHARED | 93 | +15（MOD-DATABASE 的 production） | 108 | ≤150 | ✅ |

**注**：MOD-SHARED 的 56 production 节点本就在 D-SHARED 域内，不新增。MOD-SHARECONTRACTS 仅 1 prototype 节点，不影响 production 计数。

---

## 五、验证步骤（D4）

### 5.1 DB 验证（ro SQL，GLOB 精确匹配）

```sql
-- 3 个旧 ID 应全部 = 0
SELECT blueprint_id, COUNT(*) FROM nodes
WHERE blueprint_id IN ('MOD-SHARED', 'MOD-DATABASE', 'MOD-SHARECONTRACTS')
GROUP BY blueprint_id;
-- 预期：0 行返回

-- 3 个新 ID 应存在
SELECT blueprint_id, COUNT(*) FROM nodes
WHERE blueprint_id IN ('SH-MAIN-001', 'SH-DB-001', 'MOD-SHARED-002')
GROUP BY blueprint_id;
-- 预期：3 行（61 + 41 + 1 = 103）

-- type_specific_data 中旧 ID 引用应 = 0（GLOB 精确）
SELECT COUNT(*) FROM nodes WHERE type_specific_data GLOB '*MOD-SHARED*' OR type_specific_data GLOB '*MOD-DATABASE*' OR type_specific_data GLOB '*MOD-SHARECONTRACTS*';
-- 预期：0（注意 MOD-SHARED-001 的 type_specific_data 不含字面 "MOD-SHARED"，需单独验证）

-- blueprint_path 中旧 ID 引用应 = 0
SELECT COUNT(*) FROM nodes WHERE blueprint_path GLOB '*MOD-DATABASE*';
-- 预期：0
```

### 5.2 代码文件头验证（grep）

```bash
# MOD-SHARED（无序号）应 = 0（排除 MOD-SHARED-001/002）
grep -r "\[BLUEPRINT\] MOD-SHARED[^-]" src/ --include="*.py" | wc -l
# 预期：0

# MOD-SHARED-001 应保留 = 8（A2A 协议模块不动）
grep -r "\[BLUEPRINT\] MOD-SHARED-001" src/ --include="*.py" | wc -l
# 预期：8

# MOD-SHARED-002 应新增 = 1
grep -r "\[BLUEPRINT\] MOD-SHARED-002" src/ --include="*.py" | wc -l
# 预期：1

# SH-MAIN-001 应 = 50
grep -r "\[BLUEPRINT\] SH-MAIN-001" src/ --include="*.py" | wc -l
# 预期：50

# SH-DB-001 应在代码头中出现（如果有 database 实现代码）
grep -r "\[BLUEPRINT\] SH-DB-001" src/ --include="*.py" | wc -l

# MOD-SHARECONTRACTS 应 = 0
grep -r "\[BLUEPRINT\] MOD-SHARECONTRACTS" src/ --include="*.py" | wc -l
# 预期：0
```

### 5.3 蓝图文档验证

```bash
# MOD-DATABASE 在蓝图文档中应 = 0（活文档，排除历史存档）
grep -r "module_id:.*MOD-DATABASE" docs/03_modules/ --include="*.md" | wc -l
# 预期：0

# SH-DB-001 在蓝图文档中应 = 5
grep -r "module_id:.*SH-DB-001" docs/03_modules/ --include="*.md" | wc -l
# 预期：5
```

### 5.4 N-06 门禁验证

```bash
# 验证 3 个新 ID 均通过 N-06 正则
python -c "
import re
LAYER_MASTER = re.compile(r'^MOD-[A-Z][A-Z0-9]{1,5}-\d+$')
DERIVED = re.compile(r'^MOD-[A-Z]+(?:_[A-Z]+)*(?:-\d+)?$')
SHARED = re.compile(r'^SH-[A-Z]+-\d+$')

for uid in ['SH-MAIN-001', 'SH-DB-001', 'MOD-SHARED-002']:
    ok = SHARED.match(uid) or DERIVED.match(uid) or LAYER_MASTER.match(uid)
    print(f'{uid}: {\"✅\" if ok else \"❌\"} ({uid.split(\"-\")[0]} 轨)')
"
# 预期：3 个 ✅
```

---

## 六、风险与缓解

| # | 风险 | 缓解 |
|---|------|------|
| 1 | MOD-SHARED 字符串替换误伤 MOD-SHARED-001 | 正则 `MOD-SHARED(?![A-Za-z0-9_-])` 负向前瞻；验证 MOD-SHARED-001 保留 8 文件 |
| 2 | MOD-DATABASE 级联清理遗漏（27+2 处） | GLOB 精确匹配 + 逐字段验证 |
| 3 | 蓝图文档正文引用遗漏 | grep 精确定位 5 文件中的所有 MOD-DATABASE 引用 |
| 4 | 活文档引用范围不确定 | 步骤 4 先 grep 生成清单，再批量替换，最后 grep 验证清零 |
| 5 | MOD-SHARED-002 新 ID 可能与其他引用冲突 | 真源核实确认 0 节点（§1.2） |
| 6 | 容量超限 | D-SHARED 108 ≤ 150 ✅（§四） |

---

## 七、暂停确认点

**D2 映射表已完成，请用户确认以下决策**：

### 7.1 映射方案总结

| # | 原 ID | 新 ID | 节点数 | 轨 |
|---|-------|-------|--------|-----|
| 1 | MOD-SHARED | SH-MAIN-001 | 61 | 跨域共享轨 |
| 2 | MOD-DATABASE | SH-DB-001 | 41 | 跨域共享轨 |
| 3 | MOD-SHARECONTRACTS | MOD-SHARED-002 | 1 | 派生轨（修正：-001 冲突） |
| | **合计** | | **103** | |

### 7.2 影响范围总结

| 同步项 | 数量 |
|--------|------|
| DB UPDATE | 103 行 |
| DB 级联 | 29 处 |
| 代码文件头 | 51 文件 |
| 蓝图文档 | 5 文件 |
| 活文档引用 | grep 确认 |
| 历史数据 | 豁免 |

### 7.3 请确认

1. **映射方案**：3 个违规 → 3 个新 ID（SH-MAIN-001/SH-DB-001/MOD-SHARED-002）—— 是否同意？
2. **MOD-SHARED-002 修正**：D1 初版 MOD-SHARED-001 与 A2A 协议冲突，修正为 -002 —— 是否接受？
3. **影响范围**：103 节点 + 29 级联 + 51 代码头 + 5 蓝图 —— 是否同意全量同步？
4. **执行顺序**：先 MOD-SHARED → SH-MAIN-001，再 MOD-DATABASE → SH-DB-001，最后 MOD-SHARECONTRACTS → MOD-SHARED-002 —— 是否同意？
5. **边界保护**：MOD-SHARED-001（A2A 协议，8 文件头）保留不动 —— 是否确认？

**确认后**：D3 执行 103 条 UPDATE → 级联清理 29 处 → 代码头同步 51 文件 → 蓝图同步 5 文件 → 活文档同步 → 制品刷新 → ro SQL 复测 → 清理临时脚本。
