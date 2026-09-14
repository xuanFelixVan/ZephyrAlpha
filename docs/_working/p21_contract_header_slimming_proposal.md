---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：设计/计划类且无落地证据，保守保留。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# P2-1 契约头减负——设计稿（先方案后动手，试点为零删除）

> 2026-09-14 st-btfix-p14-20260914 班｜外审遗留批 P2-1（审查报告路线图第 9 项）
> 硬约束：宪法 §4 规范总量净零增长——本稿**不做任何删除**，只做"可模板化"论证 + 单文件试点验证。

## 1. 结论（先说答案）

外审观测"22.2% 注释率 / 文件头 17 行契约块"经实查**基本属实但需修正口径**：
回测域 53 个 .py 中 48 个带 `[BLUEPRINT]`（90.6%），域内注释率 18.2%；"17 行"只计
`# [TAG]` 行——把 docstring 内嵌的 `# [ALGO_FLOW]` 机器块算上，域均头部负担实为
**~115 行**（最重文件头 260+ 行）。

**治本方向不是删，而是"迁移"**：契约行全部是机器消费面（BLUEPRINT-FORMAT /
MODULE-ID-CONSISTENCY / ALGO-NOTE-SYNC / FRONTEND-MAP 等门禁 + depgraph/panorama
生成器都在解析它们），删行=断机器链路。可减负的空间在于：**机器可再生的块不必驻留
在源码里**。

## 2. 逐标记消费方实查（2026-09-14 grep 实证）

| 标记 | 消费方（部分） | 能否迁移出源码 |
|---|---|---|
| `[BLUEPRINT]` 行 | blueprint_format_gate（裁定#208 module_id 格式）、depgraph/panorama 生成器 | ❌ 留守（1 行，成本极低） |
| `[MODULE]/[DOMAIN]/[A_module]/[TTL]` | module 翻译三层 loader、validate_module_id、TTL 分类器 | ❌ 留守 |
| `[INVARIANTS]/[MODIFY-GUARD]/[ERROR_CONTRACT]` | 蓝图合规检查、review 语义锚 | ❌ 留守（手写内容，删除=丢契约） |
| `# [ALGO_FLOW] … # [/ALGO_FLOW]` + 边表 | algo_note_sync_gate（AST 对照）、algo_flow_translation_reconciler、check_algo_flow | ✅ **可迁移**——由 AST 从代码再生成，是"生成物驻留源码" |
| `#   code:` 重复行（AST 提取的形参回写） | 同上 | ✅ 随块迁移 |

## 3. 方案：ALGO_FLOW 块出仓（generate→externalize→gate 校验替代驻留）

### 3.1 试点实况（event_driven_engine.py，500 行文件）

- 驻留 `# [ALGO_FLOW]` 块 + 边表 ≈ 60 行（占该文件注释量的 1/3）；
- 内容 100% 可由 AST 从源码再生（`code_algorithm_extractor.py` 已能提取同样的
  层/输入/算法/输出结构——生成器已在库）；
- 迁移后源码保留一行锚 `# [ALGO_FLOW] external: .runtime/contract_heads/<module>.yaml`
  （或 docs/03_modules/.../algo_flow/<module>.yaml），gate 改读外部真源做同样校验。

### 3.2 收益测算（回测域 48 文件外推）

| 指标 | 现状 | 迁移后 | 备注 |
|---|---|---|---|
| 域内头部负担 | ~115 行/文件均值 | ~55 行/文件 | ALGO_FLOW 块均值 ~60 行 |
| 注释率 | 18.2% | 预估 ~13-14% | 与"净零增长"目标同向 |
| 全域（3479 文件）外推 | — | 头部注释行数 −20 万行级 | 按 60 行/文件 × 命中率折算 |

### 3.3 实施序（后续班执行，本班不动手）

1. `algo_flow_externalizer.py`：对单文件抽 ALGO_FLOW 块 → 写 `docs/03_modules/<domain>/algo_flow/<module>.yaml` → 源码替换为 external 锚行（幂等，带 round-trip 断言）；
2. `algo_note_sync_gate` / `check_algo_flow` 加 external 锚分支：块在 yaml 真源里做同样 AST 对照；
3. 试点域=回测域（本域 48 文件），全量跑 `align_all.py` + 蓝图合规检查确认零漂移后，再裁定是否推广；
4. 宪法 §4 对账：净减 20 万行级注释的同时**新增**一个生成器 + gate 分支（规则条目等量替换：ALGO-NOTE-SYNC 的"源码驻留校验"改为"外部真源校验"，规范条目数不变）。

## 4. 明确不做（本稿边界）

- ❌ 不删任何 `[BLUEPRINT]/[INVARIANTS]/[MODIFY-GUARD]` 行——机器消费面，删=断链；
- ❌ 不改 `blueprint_format_gate` 的 module_id 校验语义；
- ❌ 不在本批大面积动 3479 个文件（试点为零删除的 1 文件验证，且本批仅交设计稿）；
- ❌ 不引入"注释率 KPI"类新规范（违反净零增长）。

## 5. 实施记录（2026-09-15，Owner 批准后同日实施）

Owner 裁定：三项遗留全部施工。实施结果：

| 步骤 | 状态 | 落地物 |
|---|---|---|
| ① extractor 支持 external 锚 | ✅ | `_load_external_algo_flow`（docs/ 前缀+.yaml 护栏）+ `_has_inline_algo_flow`（锚行不算内联块——实测锚行含 `[ALGO_FLOW]` 字面量会误判内联）+ `_strip_algo_flow_block` 同步剥锚行 |
| ① 试点迁移 | ✅ | `docs/03_modules/_domain_backtest/algo_flow/event_driven_engine.yaml`（块逐字节副本）+ 源码 docstring 换一行锚；round-trip 验证 nodes/edges 与迁移前一致；~50 行/docstring 减负 |
| ① 测试 | ✅ | 3 新例（锚加载+缺失降级+路径逃逸拒绝），27→30 全绿；generator/translation 零回归 |
| 存量推广 | 未启动 | 按净零增长原则分域分批推进，需后续班逐域出仓+round-trip 验证（416 模块量级，非一簇完成） |

边界澄清：ALGO-NOTE-SYNC 门禁管的是 decision_map 的 algo_note_zh（与 ALGO_FLOW 块无关），
translation_reconciler 经 extractor 读文字字段（锚行已剥离，语义不变），check_algo_flow
只查标记存在（锚行满足）——三消费方全部兼容，实测通过。

## 6. 验收口径（供 Owner 裁定）

- 试点文件：event_driven_engine.py 迁移后 compile+gate+ALGO-NOTE-SYNC 全绿、
  yaml 真源与源码 AST 再生内容逐字一致（round-trip 幂等）；
- 回测域测试与 governance 相关测试零回归；
- Owner 批准后方可进入第 3.3 节实施序。
