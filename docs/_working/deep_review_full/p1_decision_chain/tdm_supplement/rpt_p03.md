---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——偏离监控与修订（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：偏离监控与修订（P03）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/plan_deviation_monitor.py`
- TDM 节点: TDM-E-L0-02
- 生产调用方: **生产代码零调用方**（孤儿，见 C-1）
- 测试文件: tests/plan_engine/test_plan_deviation_monitor.py（实跑通过）

## 1 对象快照
MOD-PLAN-022 全文件（244 行）：盘中计划偏差 z 监控（|z|>2 判定，有利持有/不利纠错）+ 计划外强信号三重闸（z>3 且 E>0.5% 且 仓位≤20%）+ 留痕。Decimal-only 纯内存件。排除项：execution_deviation_attributor（事后归因，分工见蓝图§0）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | z=deviation/σ 数学正确；三重闸严格性（z>3、E>0.005 严格大于；ratio≤0.2 含等号）与 INVARIANTS 逐字一致；边界完备：Decimal-only 拒 float、is_finite 拒 NaN/Inf、σ>0、ratio∈[0,1] 全 fail-closed | :112-117,133-148,174-178,218-222 | 已查无 | 传 float/NaN/σ=0 逐项应抛 PlanDeviationError |
| A 文档 | 措辞含糊：docstring/INVARIANTS 写"\|z\|>2σ 判定"，z 已是 σ 归一量，实义为"\|z\|>2"（偏差超 2σ）——行为正确但表述自相矛盾，易误读为 z 阈值=2σ | :8,24,168 | P3 | 读 ：178 `abs(z_score) > self._deviation_z_threshold`（threshold=2 非 2σ） |
| B 上游 | 输入全调用方注入（planned/actual/sigma 无来源校验——σ 口径（窗口/复权）未约定，隐式契约未文档化） | :165-167 | P3 | 传不同窗口 σ 观察判定漂移 |
| C 下游 | **孤儿**：`grep -rln "PlanDeviationMonitor" src/ scripts/` 仅本文件；trading_decision_map.yaml:188 注册 activation:intraday 但 strategy_mounts:[]；governance_operations_map/thesis_survival blueprint 仅文档引用。盘中偏差监控实际不运转 | grep 实证；trading_decision_map.yaml:188-191 | **P2** | grep 命令如上 |
| D 旁系 | 与 execution_deviation_attributor 分工已文档化（事后归因 vs 盘中实时），无双承载；评级 human_gated 与 SAFETY=M 相称 | :30-32 | 已查无 | 读两 blueprint |
| E 对抗 | 五问：①留痕 sink 异常被吞（except+log，设计如此——留痕静默丢失无人知，P3）②假阳性无（闸条件齐备）③断链无人知=孤儿本体 ④重复评估幂等（纯内存 append，重放安全）⑤clock 默认 naive `datetime.now()`（本地时区语义未定，落 state_store 时有 RULE-SCHEMA-TZ 风险，P3） | :150,155-161 | P3 | 注入 record_sink 抛异常后查 records() 是否仍含本条 |
| F 新鲜度 | 受阻：2σ/3σ 阈值属统计过程控制（SPC）常识口径的内部裁量参数，本批未做独立检索，如实记受阻 | — | — | — |

## 3 SOTA 对照
受阻（见轴 F）：内部裁量阈值，未检索；如需对照可查 SPC 控制图（Shewhart）传统口径。

## 4 缺陷清单
1. **P2 孤儿**：TDM-E-L0-02 环节注册在案但生产零装配，盘中偏差三重闸不运转。建议：盘中监控循环接线或标注待接线。验证法：grep。
2. P3 留痕 sink 静默丢失（低危，设计取舍）。
3. P3 naive clock 时区语义。
4. P3 "|z|>2σ" 措辞（文档失真非行为错）。

## 5 挂起疑问
- σ 的真源口径（窗口/复权/年化）无人约定——接线前需 Owner 定契约，否则 2σ 判定漂移不可控。

## 6 完备性自评
六轴全查。长尾：未做运行时证据包（孤儿降义）；state_store 落库侧消费未审（未接线）。
