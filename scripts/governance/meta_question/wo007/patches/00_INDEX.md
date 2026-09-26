# WO-007 件 3｜CKG 降级执行补丁包（待落地，本战役窗内不改 src/）

> 状态：**未落地**。并发改动 `src/` 下他人文件属硬约束禁区（AGENTS L0 §RULE-WORKTREE 降级直改=显式申请制），
> 故本包以「补丁 + 验收 + 回滚」形式交付，由落地批经 GitCommitGateway 逐笔执行。
> 口径真源：`data/registers/metaq_io_edge/ckg_structural_prior_tier.yaml`（档位/上限/义务清单）
> 消费点清单：同册 `consumption_points`（21 点，扫描生成）——本包覆盖其中 5 个「需先验化」点。

| 补丁 | 目标文件 | 用法性质 | 一句话改动 |
|------|---------|---------|-----------|
| wo007-ckg-prior-01.md | `scripts/industry_graph/igfact_fill.py` | 硬事实晋升 | CKG 事实晋升为 ig_edge 结构边时置信封顶 0.45 |
| wo007-ckg-prior-02.md | `scripts/backtest/three_high_screen.py` + `config/strategy_production_map.yaml` | 硬事实消费 | 咽喉度支柱降权 0.20→0.10 且按 source 过滤，登记面同步注 tier |
| wo007-ckg-prior-03.md | `src/zephyr/frontend/dashboard/api_server.py` | 间接硬事实 | galaxy 链对权重按来源乘 tier 系数 |
| wo007-ckg-prior-04.md | `src/zephyr/intelligence/chain_impact_resolver.py` | 间接硬事实 | 情绪扩散路径置信乘路径先验系数 |
| wo007-ckg-prior-05.md | `scripts/industry_graph/build_chain_exposure_matrix.py` | 间接硬事实 | 暴露度 BFS 邻接按来源乘权 + 出生证列 prior_edge_share |

统一验收（5 件全落地后）：
`python scripts/governance/meta_question/wo007/build_ckg_prior_tier.py --self-check`
→ `compliance_rate_c` 必须从 0.7619 升到 1.0，且 `pq_0065_criterion_restatement.verdict` 变 `PASS@prior`。
（c 的机械定义=按先验档处理或本不需先验化的消费点/全部消费点，未裁定点自动计不合规。）

统一不变量（写代码前先读）：
1. **零写库**：不改 `ig_fact` 存量 `confidence`（264,072 行字节零触碰）， caps 只在读取侧取 `min(库值, cap)`；
2. **零 DELETE**：在案 76 条 ckg 晋升 `ig_edge` 不追溯删除，由消费侧过滤（历史快照语义，删=篡改证据链）；
3. **反自证**：任何与 CKG 的一致性验证，对照侧必须排除 `source_doc LIKE 'ckg_2021%'`；
4. **可回滚**：每补丁独立一笔 commit，回滚=revert 单笔，不留半成品状态；
5. **gate 兼容**：改动均为 own-diff 作用域可过；若触发图谱质量线（S 系列）需同批登记 `quality_exemptions.yaml` 理由。
