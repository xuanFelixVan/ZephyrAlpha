---
ttl: task_bound
rule_form: data
verifiability: manual
title: T0-CONDITIONAL E4 首轮考试 verdict 留档（fail-closed，裁定#399 二复活轴）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
session: st-t0-revival-20260922
---

# T0-CONDITIONAL · E4 首轮考试 verdict（2026-09-22）

> 卡真源：`t0_conditional_prereg_card.md`（frozen 先于取数）；机读产物：`t0_conditional_e4_result.yaml`；执行件：`scripts/audit/t0_conditional_e4_exam.py`（判据全部来自卡，脚本零判据裁量）。

## 1. verdict

## **`INSUFFICIENT_SAMPLES`**（fail-closed 五态枚举之一，卡 §5）

- 宏观门命中配对 **8 < 30**（土规线），禁硬出通过/不通过方向性结论；
- `emotion_gate=unevaluable`：丁线情绪六段**无持久化历史**（c1_market.sentiment_panel 实测仅 fear_greed_index 等异轴指标，禁顶替——卡 §2.2 + 词表立法件轴 E 披露），本场考试按卡降级单宏观门；
- 状态门判定本身可运行（asof 弃日 0，T-1 读数全命中）：门规则与材料窗相容，非 STATE_GATE_NEVER_TRIGGERED。

## 2. 实测读数（全量披露，观察面非结论）

| 集 | n | 毛 mean | 净 mean | ≥30bp 前置 | 净为正 |
|---|---|---|---|---|---|
| 宏观门命中（H 桶或 r3/r12，T-1） | 8 | −5.5bp | −36.7bp | 0/8 | 0/8 |
| 对照（门未命中） | 16 | −11.05bp | −42.25bp | — | — |
| 全体 | 24 | −9.2bp | −40.4bp | 0/24 | 0/24 |

- 门内命中日=2026-09-15 单日（T-1=09-14 状态允许）；09-14 配对全落对照组（T-1=09-11 状态禁做）。
- **诚实观察（不构成结论）**：门内毛边际优于对照组（−5.5 vs −11.05bp），方向与 H1（高波状态边际更宽）同向；但距 31.2bp 成本门槛仍差 ~37bp，且 0/8 前置命中。样本 8 对无统计意义。

## 3. 样本积累与复考路径（正门，禁改卡）

1. 样本积累=新回测产物入库（bt-*.json 增量）+ sentiment_panel 六段标签接线后，**原样重跑** `python scripts/audit/t0_conditional_e4_exam.py`；
2. 六段情绪持久化接线（前瞻义务）：TDM 六段标签落库（表设计挂 data 线工单，本班不施工）；接线后考试自动升双门模式（脚本已内置情绪门可用性核查，可用即按卡 §5 PASS-待考 枚举出 verdict——若届时仍单门跑=违规，脚本 fail-closed 拒绝）；
3. 复考判定须双门可用或显式 PASS-单门限定措辞（卡 §5 verdict 枚举）。

## 4. 与裁定链的回写

- 本 verdict 是 #399 二"条件化做T 复活轴"的首轮考试留档：**复活轴地基已建成（判据+卡+考试件），首轮 verdict=样本不足非方向判死**；
- 零状态变更：不动任何 verdict/can_deploy/台账行；#331/#386 口径不受影响；
- 后续考试不占本班窗口：等样本积累+情绪门接线，届时另开考试批（卡 frozen 不动）。

*复核命令：`python scripts/audit/t0_conditional_e4_exam.py`（只读，产物仅 docs/_working/t0_revival/）。*
