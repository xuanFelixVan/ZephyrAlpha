---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——盘前作战计划（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：盘前作战计划（P01）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（HEAD=068f04749e，目标文件基线后零漂移，HEAD 审查等价基线）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/daily_warroom_pipeline.py`
- TDM 节点: TDM-E-L0（gate）
- 生产调用方: **生产代码零调用方**（孤儿，见 C-1）
- 测试文件: tests/plan_engine/test_daily_warroom_pipeline.py（实跑通过）

## 1 对象快照
审查范围=MOD-PLAN-018 全文件（389 行）：日循环两段编排（盘前备次日预案 compute_and_record_scenario_plan / 盘后回写 writeback_outcome）+ 次交易日解析。排除项：scenario_plan_recorder 内部口径（MOD-PLAN-008 域，本件纯编排零判定）。测试覆盖：正常/跳过/异常路径有测试，合批实跑 100 passed。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 无算法主体（编排件）；次交易日解析 `is_open=1 AND cal_date>? LIMIT 1` 正确；TSV 解析防御（空串/坏行跳过/严格大于双保险） | daily_warroom_pipeline.py:99-101,244-253 | — | 造日历 TSV 边界行实测 |
| A 边界 | 日历空覆盖→None→`skipped:no_next_trading_day`（fail-open 有留痕）；date/phase 非法 fail-closed | :240-244,280-282,294-295 | 已查无 | 传 2026-12-32 应 ValueError |
| B 上游 | CH 通道异常→返回空串→与"日历真无次日"同判 `skipped:no_next_trading_day`，断供与真空日状态语义混叠（checklist #6 变体；trace.channels 有 `error:*` 留痕但 status 不分） | :209-223,293-295 | P3 | mock ch_client 抛异常，看 result.premarket_status 与 trace 差异 |
| C 下游 | **孤儿**：`grep -rln "run_daily_warroom_pipeline\|DailyWarroomPipeline" src/ scripts/` 仅命中本文件；config/trading_decision_map.yaml:141 仅声明注册（strategy_mounts: []，activation: premarket）；api_server.py:2315 对 TDM 仅只读渲染非执行器。声称消费方"57号日循环 SOP 环节④"未落码 | grep 实证；trading_decision_map.yaml:141-144 | **P2** | `grep -rln "run_daily_warroom_pipeline" --include="*.py" src/ scripts/` |
| D 旁系 | 日历表名双承载：table_registry 品类 + 硬编码 fallback `c1_market.trade_calendar`（checklist #4 变体；有 fallback trace 留痕，漂移风险低） | :94-95,193-207 | P3 | 改注册表品类值，验证 fallback 是否同步 |
| E 对抗 | 五问：①两段全 fail-open 仅 log.warning，叠加孤儿=失败无人知（与 C-1 复合）②幂等复用 prediction_log UNIQUE(payload 确定性) 成立 ③无心跳（未接线故暂无影响）④重跑安全 ⑤data_date 无 as-of 未来日期校验（传未来日期照跑） | :291-325 | P3 | 传 data_date=2030-01-01 观察 target 解析 |
| F 新鲜度 | 受阻/不适用：编排骨架无核心算法主张，无 SOTA 对照对象 | — | — | — |

## 3 SOTA 对照
不适用（纯编排/解析件，无算法主张）；次交易日取日历真源属数据工程常识口径。

## 4 缺陷清单
1. **P2 孤儿未接线**：模块自标 MATURITY=production、CONSUMERS 声称日循环环节④，但全仓生产代码零调用方，TDM 注册 strategy_mounts 为空。→ 现状：W0/W6 样本积累日循环实际不运转。建议：接线日循环调度或在 TDM 标注待接线。验证法：上述 grep。
2. P3 断供语义混叠（见轴 B）。
3. P3 fallback 双承载（见轴 D）。

## 5 挂起疑问
- 57 号日循环 SOP 的运行时载体是哪个进程？若属"手工/外部触发"则 C-1 降级为 P3 文档失真，需 Owner 裁定接线计划。

## 6 完备性自评
六轴全查。长尾：prediction_log UNIQUE 幂等键实际行为未复算（MOD-PLAN-008 域，另行审查）；运行时证据包/数据画像未取（孤儿状态下降义）。
