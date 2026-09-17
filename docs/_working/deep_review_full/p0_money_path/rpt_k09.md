---
ttl: task_bound
title: 深度审查作业簿——清仓执行保护
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：清仓执行保护（K09）

- 状态: **已审**
- 级别: P1｜类型: 闸门
- 基线 commit: 2fa92002c3（目标文件基线后零漂移；6 commits=稳定）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/risk/core/drawdown_liquidation_guard.py:108`（check_cancel_rate :108-161；check_liquidation_timeout :164-209）
- 生产调用方（实测 grep）: **零**。头注声称的消费方"stop_loss.execute_kill_switch_liquidation 调用方（撤单前预检/全清轮询超时）"经查不成立——K01 的清算链（stop_loss.py+risk_layer_orchestrator._engage_kill_switch）无任何一处 import 或调用本件；grep check_cancel_rate/check_liquidation_timeout 全仓非测试命中=0
- 测试文件: tests/risk/test_drawdown_liquidation_guard.py（15 用例全绿）
- 运行结果: `python -m pytest tests/risk/test_drawdown_liquidation_guard.py -q` → 15 passed（Python 3.12.8）

## 1 对象快照

- **范围**：守卫双函数本体（撤单率预检+全清超时告警）+ 与 K01 清算链的声称接线面核实。
- **排除项**：cancel_rate_guard（下单侧撤单率冻结，ex_core 域，另一件——旁系见 D 轴）；"A股 2026 新规"撤单率红线的法规原文核验（挂起疑问 1）。
- **材料缺项声明**：运行时证据包未取；新规撤单率条款原文未检（本战役 2 次检索预算已用于 K02 高频认定阈值与 K05 VaR 样本量，本项如实记受阻）。
- **测试覆盖概况**：15 用例覆盖边界（total=0/负数/倒置/阈值关系/恰等边界）；数学语义锁死质量好（信任）；孤儿状态测试无法暴露。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿守卫（零生产调用方）**：双函数全仓零消费——撤单率预检没挂在 K01 清算的撤单阶段（stop_loss.py:429-452 撤单循环直接逐单 cancel，无预检），全清超时轮询没挂在清算后验证（K01 报告即终点的缺陷正是本件要补的环）。设计闭环缺最后一环：为清算保护而建、建完未接——与 rpt_k01 P1-1（受理≠成交+无复核）互为镜像 | drawdown_liquidation_guard.py:5（头注消费方声称）；stop_loss.py:427-521（清算全文无预检/无轮询）；grep 生产命中=0 | **P1** | `grep -rn "check_cancel_rate\|check_liquidation_timeout" src/ scripts/ --include=*.py \| grep -v test` |
| A | 撤单率数学正确含保守边界：rate=cancelled/total；budget=⌊15%×total⌋−cancelled；total≤6 时 floor=0 → 0 撤单额度=红线正确推论（1/6=16.7%>15%，任何一笔撤单都破线）——保守非缺陷；total=0 → 无约束语义正确 | drawdown_liquidation_guard.py:126-146 | 已查无 | 手算 total=6/7 两点对拍 |
| A | blocked 判定含预算联动（rate≥15% **或** budget≤0 双条件）；warning 阈值 12%<15% 关系校验强制；blocked 时 budget 归零口径一致 | drawdown_liquidation_guard.py:130-142,158-159 | 已查无 | 已有测试 |
| A | 超时守卫边界：elapsed≤timeout 不告警（恰等不触发）；时间倒置 fail-closed 抛错；残余检测兼容 dict/scalar 形态，qty=NaN ≠0 计入残余（保守正确） | drawdown_liquidation_guard.py:182-193 | 已查无 | 已有测试 |
| A | 参数匹配度：默认 30s 超时 vs 15 笔/秒限频清算——组合 >~200 标的（约 14 批≈27s+尾批）即常态超时告警；接线时应按组合规模自适应而非定值 | drawdown_liquidation_guard.py:63 vs stop_loss.py:459-506 清算时长算术 | P3 | ceil(N/15)+N/15-1 vs 30 算表 |
| B | 上游：cancelled_count/total_order_count 语义="当日"口径，调用方须自行从 broker 当日委托统计——本件不管数据源（纯函数契约清晰但把"当日"正确性责任全推调用方，接线时需防传成全量委托数） | drawdown_liquidation_guard.py:118-121 | P3 | 接线评审时核数据源口径 |
| D | 旁系：ex_core/cancel_rate_guard（下单侧撤单冻结，日声明+阈值）与本件（清算侧撤单率预检）同族不同责——两件撤单率口径（如何统计、阈值多少）无对表文档，未来接线时易漂移（模式 #4 预警） | drawdown_liquidation_guard.py:8-9 vs cancel_rate_guard 头注（order_manager.py:71 导入） | P3 | 两件口径对表 |
| E | 假阳性过关：不适用（无判定放行路径——孤儿状态下连"误放行"机会都没有，主缺陷已计 P1）；静默失败：无吞异常，CRITICAL/WARNING 日志级别使用正确；重复触发：纯函数幂等；时序：monotonic 节拍无墙钟依赖（设计自觉正确） | 全文 | 已查无 | 读码 |
| A.3 | 测试：15 用例断言强（含恰等边界/倒置/负数）；缺 NaN qty 残余用例与 total=6 零额度用例 | tests/risk/test_drawdown_liquidation_guard.py | P3 | 补用例建议 |

## 3 SOTA 对照（轴 F）

- **撤单率红线 15% 出处待证**：代码自认"A 股 2026 新规红线 15%"+12% 预警留 3% buffer（drawdown_liquidation_guard.py:58-61）；本战役 K02 检索已证新规高频认定阈值=300 笔/秒或 2 万笔/日（上交所实施细则，2025），**未直接检索到"单日撤单率 15%"条款原文**——如实记受阻，需收口方核细则原文（异常交易监控条款）后再定阈值真伪。同 K01/K08 的"15 笔/秒"口径问题一并核。
- 超时告警不自动强平（T+1 约束下宁人工不盲动）：与 K01 幽灵持仓处置原则一致，**对等已有**（保守方向正确）。

## 4 缺陷清单（按严重级排序）

1. **[P1] 双守卫零接线**：现状→撤单率预检与全清超时告警无生产调用方；K01 清算链的撤单阶段与清算后验证均未消费本件。影响→清算期间撞撤单率红线的风险无预检（小额组合 0 额度的保守语义也无人执行）、清算超时无告警（K01 P1-1 的"受理≠成交"缺陷缺最后一道探测网）；爆炸半径=熔断执行期。建议修法→①execute_kill_switch_liquidation 撤单循环前置 check_cancel_rate（blocked 时跳过剩余撤单并记入报告）；②清算完成后以轮询+check_liquidation_timeout 挂告警（复用 K01 建议的持仓复核循环）。验证法→接线后 mock 高撤单率场景断言 blocked 分支生效。
2. **[P3] 两条打包**：默认 30s 超时与限频清算时长不匹配（大规模组合常态告警→告警疲劳）；当日撤单口径责任全在调用方（接线评审项）。

## 5 挂起疑问

1. "单日撤单率 15% 新规红线"的条款原文出处？（本战役检索未直接命中，K02 检索到的细则文本是高频认定阈值——两者不同条款）。收口方核原文后回填本报告与代码注释。
2. 头注消费方声称（"execute_kill_switch_liquidation 调用方（撤单前预检/全清轮询超时）"）从未兑现——是施工排期未到还是接线被遗漏？建议查 35 号 memo §6.14 施工记录后裁定（与 K06 接线/退役二选一同批处理）。

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学四问过（撤单率/预算/超时/边界全部手算对拍）；E 轴五问逐条。
- 长尾清单：① cancel_rate_guard（下单侧）本体未审（旁系对表项）；② 新规撤单率条款原文未核（挂起 1）；③ 与 K09 同族的"清算后持仓复核"应在 K01 修复中一并设计，本报告不重复给方案。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P1 双守卫(撤单率预检/超时告警)零接线+头注K01消费方不存在: 挂起登记(与K01复核链一并)。撤单率15%条款出处受阻待证。
