---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：证据不足，保守处理。处置=**保留**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 0 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：保留。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）






# DEDUP 专项批分析报告——18 对 CloneGuard 豁免克隆的语义分级与合并图纸

> 2026-09-13 夜班产出（night-sweep-20260913）。豁免登记见 echo-guard.yml acknowledged 段
> （2026-09-13 schemas-split 批追加 18 对）。本报告把"18 对"从模糊债务变成可执行施工清单。

## 一、AST 级实证分组（ast.dump 哈希 + 逐对 diff）

### A 组：AST 全同（6 组 15 副本）——行为零差异，可直接合并

| 函数 | 副本分布 | AST-hash |
|---|---|---|
| `_as_date` | mainline_candidates / mainline_probability / position_sector_context / sector/sector_divergence / sector/sector_leader | `d414eccb` ×5 |
| `_daily_returns` | mainline_candidates / sector/sector_divergence | `e103ce0c` ×2 |
| `_resolve_table` | adjustment_cycle_tracker / ml_forecast/next_day_8state_forecast / ml_forecast/regime_change_detector | `72a05426` ×3 |
| `_resolve_query_fn` | 同上三件 | `d92f61a9` ×3 |
| `_safe_float` | plan_engine/llm_premarket_analysis / plan_engine/scenario_probability_model | `21f5d88c` ×2 |
| `_table` | plan_engine/llm_premarket_analysis ↔ signal_ashare/market_breadth_history_store | `7e0627b9` ×2 |

### B 组：AST 有差但语义全等（4 组）——变量改名/docstring 措辞级，统一拼写后即全同

| 函数 | 差异性质 |
|---|---|
| `_lead_streaks`（mainline_candidates ↔ sector_divergence） | `sorted_dates/dd` vs `all_dates/d` 纯变量改名 |
| `_rotation_speeds`（同上对） | 参数换行排版 + `22号/22 号` |
| `_parse_tsv`（llm_premarket ↔ market_breadth_history_store） | docstring 详略 |
| `to_dict`（boundary_revision_engine ↔ llm_premarket ↔ war_pool_generator） | 后两者全同；boundary 仅 docstring 措辞 |

### C 组：真语义差异（2 组）——禁盲合并

| 函数对 | 差异 |
|---|---|
| `similar_day_evaluator._parse_eval_date ↔ market_breadth_history_store._resolve_end_date` | 函数名不同即信号：解析语义有出入（回退日口径），须行为对齐后才能谈合并 |
| `fine_scoring_engine.compute_density_penalty ↔ screening/selection_funnel_skeleton.density_penalty_from_summary` | 输入形态不同（原始值 vs summary 字典），是"同一公式的两个适配器"而非重复 |

## 二、合并施工图纸（下一班可直接执行）

1. **落点**：A+B 组的 signal 域函数提取至 `src/zephyr/signal_ashare/core/`（建议单文件
   `analysis_utils.py`）；plan_engine 的 `_safe_float` 提取至 plan_engine 域共享处；
   `_table` 跨域（plan_engine ↔ signal）建议落 `zephyr/shared/` 层或保留双副本登记。
2. **方法绑定注意**：`_resolve_table/_resolve_query_fn` 是实例方法（绑定 `self._registry`），
   提取须改为模块级 `resolve_table(registry)` 并改 3 处调用约定——这是 A 组中唯一有
   接口变更的，建议单独小批。
3. **B 组前置**：先把变量名/docstring 统一（纯格式批），合并 diff 即归零。
4. **C 组**：不做合并；如需收敛，先写行为对照测试锁定两套语义，再裁去留。
5. **穿行成本预算**：波及约 12 文件 M 态。每个被 decision_map module_ref 指向的文件
   （adjustment_cycle_tracker/sector_divergence/sector_leader 等）触碰时需同步推进
   trading_decision_map 对应节点 note_confirmed 日期（ALGO-NOTE-SYNC 固有交互成本，
   配方见 memory govdocr018-flatdir-launch-night-20260913）。

## 三、本夜班裁定

按"登记优先、择窗批量合并"（量化机构治理实践：旺季不重构）：
- 本批不执行代码合并——12 行小函数的维护收益 < 12 文件 M 态穿行成本 + 实例方法
  接口变更的回归风险，且夜班剩余时间优先 WARN 目录清偿与全项目连锁检查。
- echo-guard.yml 豁免保持有效，无阻塞面。
- 本报告即施工图纸，下一班按 §2 执行预计 1-2 小时（配方已备）。
