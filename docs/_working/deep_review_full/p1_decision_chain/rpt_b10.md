---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——策略CPCV矩阵
owner: st-deeprev-20260918
created: 2026-09-18
reviewed_by: GLM-5.3-Flash/st-deeprev-20260918
---

# 深度审查报告：策略CPCV矩阵（B10）

- 状态: **已审**
- 级别: P1｜类型: 管线
- 基线 commit: 2fa92002c3（基线=HEAD=工作区一致，已验）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/strategy_cpcv_matrix.py:83`（StrategyCPCVConfig）
- 生产调用方: **全仓（src+scripts）零 import 调用方**——作业簿所记"backtest/core内部"经 grep 证伪；三处文件仅注释提及分工（funnel_portfolio_adjudicator.py:24、strategy_factory.py:26、strategy_cross_vote_funnel.py:23）
- 测试文件: tests/backtest/test_strategy_cpcv_matrix.py（16 用例实跑全绿）
- 变更热力: 5 commits（2026-06-01 以来）——含改铸史（MOD-BT-027→028 撞车改铸）
- 备注: 数学正确、测试充分，但属**未接线孤儿**（缺陷模式 #8）

## 1 对象快照

- 审查范围：全文件 307 行——打分矩阵（CPCV 切分复用）、降序平均秩稳健分、交集筛选三段。
- 排除项：cpcv.generate_cpcv_splits 内部数学（MOD-BT-001 域，B 系另有对象；本轮只核其校验与调用衔接）。
- 材料包缺项声明：无运行时证据（零调用方=零运行痕迹，本身就是发现）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 降序平均秩实现正确：mergesort 稳定排序+同值平均秩 `(i+1+j)/2`，秩 1=最优；稳健分=mean_rank/M∈[1/M,1] 与声明 (0,1] 一致 | :199-212,215-237 | 通过 | n=3 手算 ties 场景；单测覆盖 |
| A | PBO 同族口径换算注释正确：秩/(M+1) 中位 0.5 ↔ mean_rank/M 中位 (M+1)/2M≈0.5；且诚实声明"同族秩口径"而非 PBO 本体（LdP 的 CSCV logit/stochastic dominance 未实现，未冒名） | :218-219 | 通过 | 对照 LdP 2018 定义 |
| A | 三段不可跳级+确定性排序 ✓；report 重建字段一致 ✓ | :289-306 | 通过 | — |
| A.3 | 测试信任判定：16 用例断言强（边界/异常/ties/degraded 均覆盖），无 mock 掉核心逻辑、无日期依赖——**信任** | tests/backtest/test_strategy_cpcv_matrix.py | 通过 | 本轮实跑全绿 |
| B | performance 矩阵全量校验（矩形/非空/NaN/Inf/重复 id/行数=id 数）Fail-Closed ✓ | :142-163 | 通过 | 读码 |
| B | **隐式契约无强制**：t1=None=点标签语义；若调用方数据是重叠标签（triple-barrier）但没传 t1，purge 语义静默失效→OOS 前视。本件无法发现也无文档强制调用方自查 | :89,98 | P2 | 读 config docstring 与 generate_cpcv_splits 衔接 |
| C | 调用方 grep：`from zephyr.backtest.core.strategy_cpcv_matrix import` / `import strategy_cpcv_matrix` 在 src+scripts 零命中（排除测试与本件自身）；[CONSUMERS] 声称的"运行时装配批（策略池候选注入/筛选漏斗离线验证段接线）"不存在对应代码 | 全仓 grep | **P2（孤儿）** | `grep -rn "strategy_cpcv_matrix" src scripts --include=*.py` 排除 tests/ 后仅 3 处注释 |
| D | 兄弟分工声明（在线信号层 B10-01504 vs 本件离线层）与注释一致，非撞名非双承载 | :24-27; strategy_cross_vote_funnel.py:23 | 通过 | 两文件头部对照 |
| D | config 的 n_groups/k_test/embargo 未在 __post_init__ 校验（docstring 声称 >=2/[1,n)/>=0），非法值穿到 cpcv.py 抛 **CPCVError** 而非契约承诺的 StrategyCPCVError(ZA-BT-0037)——错误类型泄漏 | :104-110; cpcv.py:82-85 | P3 | `StrategyCPCVConfig(n_groups=1)` 直接构造不报错，进 build_score_matrix 才炸且型不对 |
| E | 对抗五问：无静默失败（全显式抛错）✓；稳健池空→degraded=True 不伪造放行 ✓；空折拒绝 ✓。**边缘语义**：池非空但全部候选票数<min_votes 时 selected_candidates=() 且 degraded=False——空结果无降级标记，消费方可能误读为"跑过了没选出"vs"没跑成"（当前无消费方，前瞻登记） | :257-286 | P3 | 读码+构造 votes={} 用例 |
| E | 重跑幂等（纯函数）✓；无时序/并发面 ✓ | 全文件 | 通过 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| CPCV（组合净化交叉验证，N 组取 k 组全组合+purge+embargo） | **对等已有**：López de Prado, "Advances in Financial Machine Learning" CSPCV 方法（2018）——本件切分复用 MOD-BT-001，策略级聚合是合理变体 | López de Prado (2018, Wiley)； methodology 对照 ml4trading/quant 连续读物 |
| 策略级 rank-based 稳健分（mean desc rank / M） | **对等已有（简化族）**：PBO 的 CSCV 用 rank logit 分布推断过拟合概率；本件取"平均秩占比"是同族单点简化，无分布信息——够用但不含 PBO 的概率语义，报告字段命名未冒充 PBO（诚实） | Bailey & López de Prado (2014, JPM "The Deflated Sharpe Ratio" 同族多重检验思想)；LdP 2018 CSCV 章节 |

## 4 缺陷清单

1. **P2｜孤儿死码（模式 #8）**：数学正确、测试全绿、[MATURITY]=production，但生产调用方为零；头部 [CONSUMERS]"运行时装配批"与事实不符。空转期间任何口径腐化（如 cpcv 语义变更）都不会被发现。
   - 现状→证据：grep 全仓零 import（仅 3 处注释提及）；作业簿"生产调用方: backtest/core内部"记载不实。
   - 影响：第五层筛选漏斗离线验证段实际缺位；给治理层"已接线"错觉。
   - 建议修法：由 strategy_factory/funnel_portfolio_adjudicator 真实接线，或 [CONSUMERS] 如实改"预留未接线+[MATURITY] 降 design/testing"（对齐 B14 处理方式）。
   - 验证法：`grep -rn "strategy_cpcv_matrix" src scripts --include=*.py | grep -v tests/`。
2. **P2｜t1 隐式契约无强制**：重叠标签调用方漏传 t1 → purge 失效 → OOS 混入重叠样本（前视）。建议：docstring 显著警告+（可选）t1 与样本数一致性断言。
3. **P3｜config 校验缺位+错误类型泄漏**：n_groups/k_test/embargo 越界穿层抛 CPCVError，违反 ERROR_CONTRACT 的 ZA-BT-0037 承诺。
4. **P3｜空候选 vs degraded 语义盲区**：池非空+票数不足 → 空候选且 degraded=False（:278-286），前瞻登记。

## 5 挂起疑问

- 改铸史（MOD-BT-027 撞车 028，:22-23）是否在 depgraph 里留有旧引用待收口方查图。
- robust_threshold=0.5 默认值的运营语义：median 恰好卡在 (M+1)/2M≈0.5 上方，严格大于阈值——即"严格优于中位才入池"，是否符合 A1 漏斗意图待 Owner 确认（数学上无错）。

## 6 完备性自评

- 六轴全查：A（秩/稳健分逐式验算）✓ B（矩阵校验+t1 契约）✓ C（零调用方实锤=本轮主发现）✓ D（与在线层分工+错误类型契约）✓ E（五问+degraded 边缘）✓ F（2 条带源对照）✓。
- 长尾：cpcv.generate_cpcv_splits 内部数学（对象归属他件）；真实接线后的性能矩阵注入质量（无调用方无从审）。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- 孤儿（零 import+假消费者声明）: 挂起登记（退役/接线裁定）。
- 修复提交: q-0024（B11 冲击腿）。
