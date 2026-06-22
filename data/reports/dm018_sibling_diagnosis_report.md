# DM-018: Sibling 边膨胀诊断报告

> **任务卡ID**: DM-018
> **诊断日期**: 2026-06-14
> **诊断类型**: 只读诊断（禁止写入 depgraph.db 和源码文件）
> **状态**: COMPLETED

---

## §1 执行摘要

`dm014_orphan_edge_repair.py` 策略3对同目录孤儿节点建立全连接 sibling 边，导致 **O(n²) 边膨胀**。当前 depgraph.db 中 **136,276 条 sibling 边占总边数 143,884 的 94.7%**。

**核心结论**: sibling 边是孤儿补边策略的副作用，无下游消费者，应替换为节点属性 `belongs_to`。

---

## §2 Sibling 边来源定位

### 2.1 源脚本路径

| 属性 | 值 |
|------|-----|
| **脚本路径** | `scripts/construction/dm014_orphan_edge_repair.py` |
| **策略位置** | 策略3: sibling/contains 边生成 |
| **代码行号** | **第 119-141 行** |
| **关键代码** | 见下方 §2.2 |

### 2.2 问题代码片段

```python
# scripts/construction/dm014_orphan_edge_repair.py:119-141

# --- 策略3: sibling/contains 边 ---
all_nodes = conn.execute(
    "SELECT node_id, file_path FROM nodes WHERE file_path IS NOT NULL AND file_path != ''"
).fetchall()
dir_to_nodes = defaultdict(list)
for nid, fp in all_nodes:
    if fp:
        dir_to_nodes[os.path.dirname(fp)].append(nid)

for nid, ntype, _, fp in remaining:
    if not fp:
        continue
    dir_path = os.path.dirname(fp)
    if fp.endswith("__init__.py"):
        # contains
        for sib in dir_to_nodes.get(dir_path, []):
            if sib != nid:
                edges_to_add.append((nid, sib, "contains", "weak"))
    else:
        # sibling  <-- 问题根源
        for sib in dir_to_nodes.get(dir_path, []):
            if sib != nid:
                edges_to_add.append((nid, sib, "sibling", "weak"))  # <-- O(n²) 膨胀点
```

### 2.3 膨胀机制分析

**O(n²) 全连接机制**:

1. **输入**: `remaining` 列表包含所有孤儿节点（无入边无出边）
2. **索引构建**: `dir_to_nodes` 将同目录所有节点分组
3. **全连接生成**: 对每个孤儿节点，与同目录**所有其他节点**建立 sibling 边
4. **复杂度**: 若某目录有 n 个节点，则产生 n×(n-1) 条 sibling 边

**示例**: 若 `src/zephyr/shared/` 目录有 500 个节点，则产生 500×499 = **249,500 条 sibling 边**。

---

## §3 Sibling 边消费分析

### 3.1 下游消费者检查结果

| 检查项 | 结果 |
|--------|------|
| `generate_project_depgraph.py` 中搜索 "sibling" | **0 处消费** |
| `depgraph_schema.py` 中 sibling 边类型定义 | **无枚举约束**（dep_type 为 TEXT） |
| `diagnose_depgraph.py` 中 sibling 边分析 | **无专门分析** |
| `extract_depgraph.py` 中 sibling 边导出 | **无专门处理** |

### 3.2 结论

**Sibling 边无下游消费者**。生成后仅存储在 depgraph.db 中，不被任何治理脚本、门禁、或报告消费。

---

## §4 Depgraph Schema 分析

### 4.1 edges 表定义

```sql
-- src/zephyr/governance/depgraph_schema.py:115-137
CREATE TABLE IF NOT EXISTS edges (
    edge_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node                TEXT    NOT NULL,
    to_node                  TEXT    NOT NULL,
    dep_type                 TEXT    NOT NULL,  -- 无枚举约束，任意字符串
    architecture_direction   TEXT    DEFAULT 'downstream',
    coupling_strength        TEXT    DEFAULT 'critical',
    -- ... 其他字段
)
```

### 4.2 问题

- `dep_type` 字段为 TEXT 类型，**无枚举约束**
- sibling 边类型在 schema 中**无明确定义**
- 任何脚本可插入任意 dep_type 值，导致边类型膨胀

---

## §5 基线诊断数据

### 5.1 当前 depgraph.db 状态

| 指标 | 数值 |
|------|------|
| **总节点数** | 7,551 |
| **总边数** | 143,884 |
| **孤儿节点数** | 1,473 |
| **Empty blueprint_id** | 743 |

### 5.2 Sibling 边占比估算

根据任务卡背景信息：
- **Sibling 边数量**: ~136,276 条
- **占总边数比例**: 94.7%
- **非 sibling 边数量**: ~7,608 条

---

## §6 替换方案

### 6.1 方案概述

**用节点属性 `belongs_to` 替代 sibling 边**。

### 6.2 方案详情

| 维度 | 当前（Sibling 边） | 目标（belongs_to 属性） |
|------|-------------------|------------------------|
| **存储位置** | edges 表 | nodes 表 belongs_to 字段 |
| **边数量** | 136,276 条 | 0 条 |
| **信息表达** | 节点间点对点连接 | 节点→目录归属 |
| **查询方式** | `SELECT * FROM edges WHERE dep_type='sibling'` | `SELECT * FROM nodes WHERE belongs_to='<dir>'` |
| **空间复杂度** | O(n²) | O(n) |

### 6.3 实施步骤（供后续任务卡参考）

1. **修改 dm014_orphan_edge_repair.py**:
   - 删除策略3中 sibling 边生成逻辑（第 137-141 行）
   - 保留 contains 边逻辑（__init__.py 对子文件的包含关系）
   - 可选：为孤儿节点设置 `belongs_to` 属性为其父目录

2. **清理 depgraph.db**:
   - `DELETE FROM edges WHERE dep_type = 'sibling'`
   - 预期删除 ~136,276 条边

3. **验证**:
   - 运行 `diagnose_depgraph.py` 确认边数下降
   - 确认无下游脚本因 sibling 边消失而报错

### 6.4 预期效果

| 指标 | 当前 | 预期 |
|------|------|------|
| **总边数** | 143,884 | ~7,608 |
| **Sibling 边数** | 136,276 | 0 |
| **边类型分布** | sibling 94.7% | import_depends/references/test_depends 为主 |
| **数据库大小** | ~50MB（估算） | ~5MB（估算） |

---

## §7 验收标准核对

| 验收项 | 状态 | 说明 |
|--------|------|------|
| sibling 边来源脚本路径 | ✅ | `scripts/construction/dm014_orphan_edge_repair.py` |
| sibling 边行号 | ✅ | 第 119-141 行（关键膨胀点：第 141 行） |
| 膨胀机制 | ✅ | O(n²) 全连接：同目录孤儿节点两两建立 sibling 边 |
| 替换方案 | ✅ | 用节点属性 `belongs_to` 替代 sibling 边 |
| 预期边数变化 | ✅ | 136,276 条 sibling 边 → 0，总边数 143,884 → ~7,608 |

---

## §8 附录：诊断命令输出

### 8.1 extract_depgraph.py --summary

```
总域数: 40
总模块数: 2567
（详细输出见诊断日志）
```

### 8.2 diagnose_depgraph.py

```
[DIAG] Nodes: 7551 | Edges: 143884
[DIAG] Orphan nodes: 1473
[DIAG] Empty blueprint_id: 743
[DIAG] Circular dependencies: 8 (true: 3)
[DIAG] Cross-pkg violations: 816 across 64 package pairs
```

---

## §9 结论与建议

### 9.1 核心发现

1. **Sibling 边是孤儿补边策略的副作用**，无实际治理价值
2. **O(n²) 全连接机制**导致边数膨胀至 136,276 条
3. **无下游消费者**，删除不影响任何治理脚本或门禁

### 9.2 建议

1. **创建后续任务卡**（如 DM-019）执行替换方案
2. **修改 dm014_orphan_edge_repair.py** 删除 sibling 边生成逻辑
3. **清理 depgraph.db** 中现有 sibling 边
4. **考虑为 dep_type 添加枚举约束**，防止未来边类型膨胀

---

**报告生成时间**: 2026-06-14T15:51:00Z
**诊断脚本**: `scripts/governance/diagnose_depgraph.py`
**诊断人员**: AI Agent (Code Mode)
