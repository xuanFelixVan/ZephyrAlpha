---
ttl: task_bound
title: 深度审查作业簿——板块级市场状态（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：板块级市场状态（P19）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/core/sector_ecology_judge.py`
- TDM 节点: TDM-E-L2-04
- 生产调用方: sector_strength_wiring.py（真实消费方，grep 实证）；TDM-E-L3-06/L2 候选池排序两消费方声明"待接线"
- 测试文件: tests/signal_ashare/sector/test_sector_ecology_judge.py（合批 49 passed）

## 1 对象快照
MOD-SIG-143（139 行）：三态生态判定（MAINLINE_CLEAR/CLIMAX/CHAOS）纯函数，优先级 CLIMAX>MAINLINE>CHAOS（风险方向优先）。阈值全部引已锚定模块文档值（裁定留痕 :26-29）。测试实跑通过。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 判定序（高潮→主线→混沌）与 INVARIANTS 一致；阈值溯源纪律（零自创数字，架构师自裁留痕）为治理正例；边界 fail-closed（isfinite/越界/负连击）完备 | :8,26-29,102-110 | 已查无 | 三态各造边界样本 |
| A 边界 | `int(lead_streak)` 截断洞：float 2.7→2（静默截断）；**负小数 -0.5→int→0 绕过负值检查**（契约"连击为负抛错"对 -0.5 不触发） | :102-104 | P3 | `judge_sector_ecology(-0.5, 0.5, 50)` 应抛但返回 CHAOS |
| B 上游 | 三输入全调用方注入；lead_streak 真源=mainline_candidates、高潮分真源=sector_rotation_state（≥90 双源锚定声明）——集中度输入无真源模块锚（调用方自算 Top2 占比，口径未锁定：按成交额还是涨跌幅占比、全板块还是活跃板块分母） | :3-4,122-122 | P3 | 对两调用方注入口径差样本 |
| C 下游 | sector_strength_wiring 真消费（生态系数进板块候选池排序）；CLIMAX 误判→降仓预警误发（爆炸半径=板块池排序+环境开关待接线后扩大） | grep 实证 | 已查无 | grep 复跑 |
| D 旁系 | 与 P20 五状态分工：本件三态=生态大类（风险方向），P20 五状态=轮动细类——分层清晰但"高潮"概念两件皆有（本件 climax_score≥90 vs P20 CONSENSUS_CLIMAX hhi>0.30∧up_ratio>0.70 判据不同源）——**同名词不同判据**，接线后易混（P3 登记） | :42-43 vs sector_rotation_state.py:55,101-103 | P3 | 对读两件高潮判据 |
| E 对抗 | 五问：①无吞异常（全 fail-closed）②优先级风险优先防误买（好）③无监控面 ④纯函数幂等 ⑤无时序面 | 全文件 | 已查无 | — |
| F 新鲜度 | 受阻/不适用：1-2 板块吸 30% 成交=主线生态判据为 A 股题材周期本土口径（节点真源），无外部对照对象 | — | — | — |

## 3 SOTA 对照
受阻/不适用（本土题材周期口径，节点真源锚定）。

## 4 缺陷清单
1. P3 int() 截断绕过负值校验（建议 math.floor 后判负或拒非 int）。
2. P3 集中度输入口径未锁定（无真源模块锚）。
3. P3 "高潮"名词双件异义（本件 vs P20 判据不同源）。

## 5 挂起疑问
- 阈值 proposed 待实盘标定（:8 自声明）——与族内标定欠账同型，合并立项。

## 6 完备性自评
六轴全查（全文件 139 行逐行）。无长尾。
