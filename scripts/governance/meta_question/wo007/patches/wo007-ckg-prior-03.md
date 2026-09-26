# wo007-ckg-prior-03｜api_server.py：galaxy 链对权重按来源乘 tier 系数

- 目标文件：`src/zephyr/frontend/dashboard/api_server.py`（他单文件，前端服务）
- 用法性质：`indirect_hard_fact_via_promoted_edges`（字面不提 CKG，吃的是 CKG 晋升边）
- 在案证据：链对权重累加处
  `cur.execute("SELECT from_node, to_node FROM ig_edge WHERE valid_to IS NULL")` → 每条有效边计 1.0，
  含 `source_doc LIKE 'ckg_2021%'` 的 76 条晋升边与研报抽取边一视同仁；面板图与链对权重同源。

## 改动（`SELECT` 增列 + 权重乘系数）

```diff
-        cur.execute("SELECT from_node, to_node FROM ig_edge WHERE valid_to IS NULL")  # 2026-09-12: 已关闭边不参与 galaxy 链对权重
+        cur.execute("SELECT from_node, to_node, source_doc FROM ig_edge WHERE valid_to IS NULL")  # 2026-09-12: 已关闭边不参与 galaxy 链对权重
         pair_w: dict[tuple[str, str], float] = {}
-        for a, b in cur.fetchall():
+        for a, b, sdoc in cur.fetchall():
+            # WO-007 件 3：CKG 晋升边按结构先验乘权（真源 data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml）
+            w = 0.45 if (sdoc or "").startswith("ckg_2021") else 1.0
             c1, c2 = node_chain.get(a), node_chain.get(b)
             if c1 in chain_name and c2 in chain_name and c1 != c2:
                 key = (c1, c2) if c1 < c2 else (c2, c1)
-                pair_w[key] = pair_w.get(key, 0.0) + 1.0
+                pair_w[key] = pair_w.get(key, 0.0) + w
```

同一函数族内另一处 `SELECT from_node, to_node, COALESCE(edge_type, '') FROM ig_edge ...`（图谱面板取边）
**保持不改**（展示非决策），但面板边详情弹窗应显示 `evidence_tier`（有 `source_doc` 前缀即可判定，零 schema 变更）。

## 为什么不在这里删边

零删除原则：`ig_edge` 是历史证据链快照，删=篡改可追溯性；降级只作用于**权重语义**，
读方按 caps 取小（OB-2）。76 条边占比 76/1726=4.4%，降权后链对权重位移 <5%，面板视觉无感，
但下游若把链对权重喂给聚类/因子，先验就不再伪装成事实。

## 验收

1. 面板启动无异常（该函数是 fail-open 包裹：`except Exception` 已存在，改动不得吞掉新异常类型）；
2. 对账：`select count(*) from ig_edge where source_doc like 'ckg_2021%'` 仍=76（零改写）；
3. 链对权重快照对比（改前/改后同名链对）差值全部 ≥0 且 ≤ 0.55×原值；
4. `build_ckg_prior_tier.py --self-check` → 本文件 `currently_prior_compliant=true`。

## 回滚

revert 本笔（单点 SQL + 一行权重），无状态残留。
