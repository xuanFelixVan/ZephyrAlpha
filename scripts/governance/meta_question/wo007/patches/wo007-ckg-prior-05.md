# wo007-ckg-prior-05｜build_chain_exposure_matrix.py：暴露度 BFS 按来源乘权 + 先验占比出生证

- 目标文件：`scripts/industry_graph/build_chain_exposure_matrix.py`（他单文件）
- 用法性质：`indirect_hard_fact_via_promoted_edges`（**影响面最广**：产物直接喂线 A 因子构造
  上游成本冲击/生猪链/客户动量 与 E5 链感知聚类）
- 在案证据：模块自陈「只读 PG depgraph（ig_* valid_to IS NULL 现视图）；暴露语义=自身角色权重×
  (1+同链可达衰减和)，跳衰减 0.5/跳 ≤3 跳」——可达累加对**所有** ig_edge 边一视同仁，
  含 76 条 CKG 晋升边与 CKG 激活链内的结构边。因子侧看到的「暴露度」因此混入先验而无标注。

## 改动 1：边取数带 source_doc 并算先验系数

实测真源（L56）：

```diff
-SQL_EDGES: str = "SELECT from_node, to_node, edge_type FROM ig_edge WHERE valid_to IS NULL ORDER BY from_node, to_node"
+SQL_EDGES: str = ("SELECT from_node, to_node, COALESCE(edge_type, ''), source_doc FROM ig_edge "
+                  "WHERE valid_to IS NULL ORDER BY from_node, to_node")
```

```python
# 新增常量（真源=data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml）
PRIOR_EDGE_WEIGHT = 0.45   # tiers.structural_prior.weight_multiplier


def _edge_weight(source_doc: str | None) -> float:
    return PRIOR_EDGE_WEIGHT if (source_doc or "").startswith("ckg_2021") else 1.0
```

## 改动 2：邻接表与可达衰减和按边权缩放（衰减公式其余不动）

实测真源（`_bfs_reach` L102-123，关键行 `decay = HOP_DECAY**hops` / `w[nb] = decay`）：

```diff
-def _bfs_reach(adj: dict[str, list[str]]) -> dict[str, dict[str, float]]:
+def _bfs_reach(adj: dict[str, list[tuple[str, float]]]) -> dict[str, dict[str, float]]:
     """从每个节点出发沿 adj 的可达权重表: {node: {reachable: weight}}。"""
@@
-            decay = HOP_DECAY**hops
+            decay = HOP_DECAY**hops
             ...
-                    w[nb] = decay
+                    w[nb] = decay * edge_w          # edge_w=沿途边先验系数的路径累计（见下）
```

邻接表构造处（原 `up_adj[nid].append(nb)` 族）同步改为携带边权并累计：

```python
edge_w = prev_w * _edge_weight(source_doc)   # 路径上先验边连乘（3 跳全先验=0.45³，保守）
prior_reach[start] += decay * (1.0 - edge_w)  # 被先验折价的那部分，单列可审计
```

## 改动 3：CSV 增一列 `prior_edge_share`（出生证，不改既有列序）

`prior_edge_share = prior_reach / (exposure_reach + prior_reach)`，4 位小数，分母 0 记 0.0；
暴露度主列继续走 `role_w * (1 + sum(...))`（该件 L174/L177 现写法）不变。

> 因子构造侧（线 A）与聚类侧（E5）在 `prior_edge_share > 0.2` 的行上应降权或剔除——
> 本补丁只负责**把先验占比暴露出来**，不改因子口径（越界改他单语义是禁忌）。

## 验收

1. 确定性自校验不破：CSV 全行排序后哈希（该件 INVARIANTS 明写不含墙钟）——新增列须在同一哈希面内；
2. 对照：`prior_edge_share=0` 的行 `exposure` 与改前**逐位相同**（先验零污染的环节不受影响）；
3. `select count(*) from ig_edge where source_doc like 'ckg_2021%'` 仍=76；
4. `build_ckg_prior_tier.py --self-check` → 本文件 `currently_prior_compliant=true`。

## 回滚

revert 本笔；已产出的历史 CSV 不追删（`.runtime` 暂存物，TTL 自清）。
