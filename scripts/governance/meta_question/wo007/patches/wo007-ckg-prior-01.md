# wo007-ckg-prior-01｜igfact_fill.py：CKG 事实晋升为图结构边的置信封顶

- 目标文件：`scripts/industry_graph/igfact_fill.py`（他单文件，本战役不直改）
- 用法性质：`promotion_to_graph_fact`（把先验写成事实——降级的主执行点，最重）
- 在案证据：CKG `ig_fact.supplies_to` 57,069 行（source='ckg_2021'，库内 confidence=0.6）；
  本件把同链两端晋升为 `ig_edge` supply 边，`source_doc='ckg_2021 供应链事实|ig_fact#<fid>|2021-10-26'`，
  批次置信 0.85，并以 ckg 来源激活链 → 在案 `ig_edge` 中 76 条自并入边即本件产物。
- 风险：晋升边一旦入 `ig_edge`，下游（暴露度矩阵、情绪扩散、galaxy 链对权重）把它与研报抽取边、
  官方结构边同等看待（各计 1）；这正是 PQ-0065「不剔除自并入边就 58/81=71.6% 假达标」的产地。

## 改动 1：新增先验档常量（模块常量区，`S_DOC` 附近）

```python
# 新增（WO-007 件 3：CKG 降级为结构先验，口径真源=data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml）
PRIOR_TIER = "structural_prior"
PRIOR_CONFIDENCE_CAP = 0.45   # relation_caps['ckg_2021']['supplies_to'].confidence_cap


def _prior_capped(conf: float) -> float:
    """读取侧封顶：不改 ig_fact 存量字节，只保证晋升边置信不越过先验档。"""
    return min(float(conf), PRIOR_CONFIDENCE_CAP)
```

## 改动 2：晋升边记录带 tier 与封顶置信（`build_chain_batch`，"type": "node_edge" 分支）

```diff
             records.append({
                 "type": "node_edge", "chain_name": chain_name_of[cid],
                 "from_node": s, "to_node": o, "edge_type": "supply",
                 "market": "cn", "source": "ckg_2021",
                 "source_doc": S_DOC.format(fid=fid),
+                "confidence": _prior_capped(0.85),
+                "evidence_tier": PRIOR_TIER,
             })
```

## 改动 3：链激活不得只靠 CKG（`activate` 路径，source_note 生成处）

要求：`source='ckg_2021'` 的链激活前置一个异源侧证检查——该链的供应边至少 1 条能在
非 CKG 侧找到同向佐证（`ig_edge` 中 `source_doc NOT LIKE 'ckg_2021%'` 的同端点边，
或 `io_edge_binding_loader.industry_pair_matrix()` 的对应行业对）。侧证缺失时降为
`status='candidate'`（不激活），并打印 fail-visible 行。落地面最小实现：

```python
def _has_non_ckg_corroboration(cur, node_names: set[str]) -> bool:
    cur.execute(
        """SELECT 1 FROM ig_edge e
           JOIN ig_node a ON a.node_id=e.from_node JOIN ig_node b ON b.node_id=e.to_node
           WHERE e.source_doc NOT LIKE 'ckg_2021%%' AND e.valid_to IS NULL
             AND a.name = ANY(%s) AND b.name = ANY(%s) LIMIT 1""",
        (sorted(node_names), sorted(node_names)),
    )
    return cur.fetchone() is not None
```

## 验收

1. 重跑 `python scripts/industry_graph/igfact_fill.py --dry-run`（该件既有 dry-run 通道）→
   晋升边记录 `confidence<=0.45` 且带 `evidence_tier='structural_prior'`；
2. 只读探针：`select count(*) from ig_edge where source_doc like 'ckg_2021%'` **保持 76**（零删除、零改写）；
3. `python scripts/governance/meta_question/wo007/build_ckg_prior_tier.py --self-check`
   → 本文件 `currently_prior_compliant` 由 false 转 true（检测锚=文件内出现 `structural_prior` 字面）。

## 回滚

revert 本笔 commit；无 schema 变更、无数据写入，回滚零副作用。
