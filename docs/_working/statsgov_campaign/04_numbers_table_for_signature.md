---
ttl: task_bound
---

# 预算册数值表（机生片段，呈 Owner 终签）

- 公式：`transitional_history_x1`（晨裁 M3-A：过渡帽=该族已实测历史消耗×1）
- 网格未入账试次 53090 次全部计入族 `B`（不平摊六族，免得一份数虚增六倍）
- 读数真源=`02_trial_budget_inventory_v1.yaml#numbers_table_for_terminal_signature`（本表由同一次运行派生）

| 族 | 账本(kind) | 磁盘未入账 | 成绩册行数 | 消耗合计 | 过渡帽×1 | 帽状态 | 红旗 |
|---|---|---|---|---|---|---|---|
| A 信号/因子族 | 34 | 0 | 1660 | **1694** | 1694 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['fexam_score_books', 'sector_line_prereg']→该行合计**偏低**；PG 面未测 1 处 |
| B 策略配方族 | 31959 | 53090 | 185 | **85234** | 85234 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['grid_oos_book', 'mom029_books']→该行合计**偏低** |
| C 组合/配置族 | 0 | 0 | 5 | **5** | 5 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['exit_sim']→该行合计**偏低** |
| D 状态识别/环境族 | 0 | 0 | 0 | **0** | 0 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['state_recognizer', 'emotion_index']→该行合计**偏低**；合计=0：帽若照抄=该族立即停，须先修册面读取再谈帽 |
| E 工程件族 | 0 | 0 | 412 | **412** | 412 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['exam_run_archive']→该行合计**偏低** |
| F 挖矿器元层族 | 0 | 0 | 5410 | **5410** | 5410 | owner_adopted_formula_pending_terminal_signature | 册面键名未命中(PARTIAL)['paper_pool']→该行合计**偏低** |

## 终签前必读的三条限制

1. **C/D 两族的低值是测量口径未修，不是真零消耗**（成绩册点名键不存在时本件如实报 PARTIAL 而非 0）。照抄这两行做帽会误停两族——要么先修 row_rule 复跑，要么这两族本轮判'帽待定'。
2. **账本面与成绩册面可能重叠**（考试卡既在 `kind=exam_card` 又在成绩册行数里）：本表三面分列不合并去重，合一口径需先点名去重规则。
3. **PG 面未测**（本件不连库，报 PG_NOT_PROBED）：A 族真实消耗 ≥ 表值；PG 侧计数须走 DatabaseService 只读口另开一跑。
