# wo007-ckg-prior-04｜chain_impact_resolver.py：情绪扩散路径置信乘先验系数

- 目标文件：`src/zephyr/intelligence/chain_impact_resolver.py`（他单文件，L2 传导/情绪消费主链）
- 用法性质：`indirect_hard_fact_via_promoted_edges`（**先验最先落到个股的一处**）
- 在案证据：`_SQL_EDGES` 读 `ig_edge(from_node,to_node,edge_type)` → `_build_adjacency` 无向化 →
  BFS 扩散，置信 `= 种子 hit.confidence × hop_decay^hop × company_conf`。
  CKG 晋升的 supply 边在邻接表里与其他边同权（=1），于是「新闻打到某环节 → 沿 CKG 先验边扩散 →
  给出受影响标的与置信」全链把先验当硬事实输出给上层决策。

## 改动 1：边取数带 source_doc（L375 模块级 SQL 常量 + I3 元数据）

实测真源（本补丁按字节锚定，落地批照抄前先 grep 复核）：

```python
_SQL_EDGES: Final[str] = "SELECT from_node, to_node, edge_type FROM ig_edge"  # noqa: bare-sql  模块级 SQL 常量（集中化专项另行治理）
```

```diff
-_SQL_EDGES: Final[str] = "SELECT from_node, to_node, edge_type FROM ig_edge"  # noqa: bare-sql ...
+_SQL_EDGES: Final[str] = "SELECT from_node, to_node, COALESCE(edge_type, ''), source_doc FROM ig_edge"  # noqa: bare-sql ...
```

> 顺带发现（**不在本补丁范围，登记给落地批复核**）：该 SQL 无 `valid_to IS NULL` 过滤，
> 而已关闭边在 api_server 侧被明确排除（L2956 注释「2026-09-12: 已关闭边不参与 galaxy 链对权重」）。
> 情绪扩散是否应含已关闭边=独立口径问题，本补丁不改语义（改语义须另裁，防连坐）。
> 同步：模块 L49 区 I3 元数据 `fields: (from_node, to_node, edge_type)` 须增第四项 `source_doc`
> （元数据与代码不一致会触 CONSUMERS/元数据类 gate）。

## 改动 2：邻接表带权重（`_build_adjacency`）

```diff
 def _build_adjacency(
-    edges: Iterable[tuple[str, str, str]],
+    edges: Iterable[tuple[str, str, str, str | None]],
     node_table: dict[str, tuple[str, str, str]],
-) -> dict[str, set[str]]:
-    """无向邻接表（端点须为活节点；自环剔除）。"""
-    adj: dict[str, set[str]] = {}
-    for from_node, to_node, _edge_type in edges:
+) -> dict[str, dict[str, float]]:
+    """无向邻接表（端点须为活节点；自环剔除）。
+
+    WO-007 件 3：边权重=先验档系数——source_doc 前缀 ckg_2021 的晋升边按 structural_prior=0.45 计，
+    其余边 1.0。真源=data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml
+    （tiers.structural_prior.weight_multiplier）。
+    """
+    adj: dict[str, dict[str, float]] = {}
+    for from_node, to_node, _edge_type, source_doc in edges:
         f = str(from_node or "").strip()
         t = str(to_node or "").strip()
         if not f or not t:
             raise ChainImpactResolverError(f"边条目畸形（空端点）: {(from_node, to_node)!r}")
         if f == t or f not in node_table or t not in node_table:
             continue
-        adj.setdefault(f, set()).add(t)
-        adj.setdefault(t, set()).add(f)
+        w = 0.45 if (source_doc or "").startswith("ckg_2021") else 1.0
+        adj.setdefault(f, {})[t] = max(adj.setdefault(f, {}).get(t, 0.0), w)
+        adj.setdefault(t, {})[f] = max(adj.setdefault(t, {}).get(f, 0.0), w)
     return adj
```

## 改动 3：BFS 置信乘路径最小系数（扩散累乘改累乘 min，保守口径）

```diff
-            conf = seed_conf * (self._hop_decay ** hop) * company_conf
+            # 路径先验系数=沿途边权重最小值（min 而非乘积：多跳先验链不因边数叠加被过度惩罚，
+            # 但只要有 1 条先验边就封顶 0.45——口径与 OB-3 一致且可解释）
+            prior_w = min((edge_w[f, t] for f, t in zip(path, path[1:])), default=1.0)
+            conf = seed_conf * (self._hop_decay ** hop) * company_conf * prior_w
```

`ImpactTarget` 增字段 `prior_weight: float = 1.0`（默认值向后兼容，`frozen dataclass` 加尾字段安全）。

## 连带（同批或紧随一笔）

`src/zephyr/intelligence/news_chain_node_linker.py` 词表侧无需改（它是 `vocabulary_only`），
但**种子节点本身**若只由 ckg 激活链提供，应输出 `seed_source_tier` 供上层审计（可择机，非本补丁阻塞项）。

## 验收

1. `tests/intelligence/test_chain_impact_resolver*.py`（既有）全绿；纯函数注入路径的边元组须同步为四元组
   ——**注意**：注入契约变更是破坏性的，落地批必须同批改测试构造，否则连坐红；
2. 冒烟：同一 hits/polarity 输入，改后 confidence 单调不增，且全部先验路径结果 ≤0.45×原值；
3. `graph_size()` 诊断口径不变（节点/邻接/公司三数一致）；
4. `build_ckg_prior_tier.py --self-check` → 本文件 `currently_prior_compliant=true`。

## 回滚

revert 本笔（含测试构造同批回滚）；`prior_weight` 字段有默认值，回滚不影响调用方字节兼容。
