---
ttl: task_bound
rule_form: data
verifiability: manual
title: P-P2-01/03 做T配对判据重建与复测报告（TC-06 R4 卡 A 选项，裁定#399 二）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-22
session: st-t0-revival-20260922
---

# 做T 配对判据重建与复测（cost_trio 重建件，方法论工具非策略）

> 这是什么：原 cost_trio_exam.py 与基线快照随 `.runtime/tmp/exp/` 整棵灭失（TC-06 R4 卡「判据灭失」条）。
> 本批按裁定#399 二（做T 复活改裁：R4 由"只登记不重建"改"重建判据+条件化做T复活轴施工"）执行 A 选项，
> 判据脚本+基线重建落 docs（本目录），**禁 .runtime/tmp**——判据灭失病根第二次免疫。
> 本件只做成本配对方法论判据重建，不构成对任何被砍策略（#331 砍做T旧形态/#386 禁复试图救）的复活尝试；
> 复活唯一口=新预注册假设卡+考试制（分包2 已另行立卡）。

## 1. 判据真源与重建声明

| 项 | 真源 |
|---|---|
| 出结论土规 | REG-VALM-001 轻量土规：配对数 ≥30 才出结论，不足=insufficient_samples 禁硬出方向性结论 |
| 成本口径 | cost_model_registry.yaml `CST-T0-001`：佣金双边 6bp+印花 5bp（卖侧）+过户双边 0.2bp+滑点 2×10bp = **31.2bp rt**（固定口径）；最低佣金 5 元地板=已建模行为（matching_logic.py 实证），单列披露不折入固定口径 |
| 开仓前置 | CST-T0-001 open_precondition.min_expected_edge_rate=0.003 → 毛价差 ≥30bp |
| 材料 | `data/backtest_artifacts/bt-*.json` trade_log；锚点 D=2026-09-09（D 前全锁/D 后可考，P6.md 真源） |
| 配对规则 | 同 (symbol, trade_date) 双边计 1 配对；配对量=min(Σ买量,Σ卖量)；买卖全侧 VWAP 近似（原实现灭失，本规则为重建版，见 §2 复现对照） |

判据脚本：`scripts/audit/cost_trio_exam.py`（判据住 scripts/、产物住 docs/——目录契约 DCR-005 docs/_working 禁 .py/.json；预注册披露节在 docstring，改动须留变更记录）。
机读产物：`cost_trio_result.yaml` + `cost_trio_pairs.csv`（同目录）。

## 2. 基线复现对照（重建版 vs 09-17 P6 快照/biz2 归档）

| 机读判据值 | P6/biz2 快照（09-17/09-18） | 重建复测（09-22） | 一致性 |
|---|---|---|---|
| n_symbol_day_pairs | 24 | **24** | ✅ 逐位一致 |
| net_positive（净价差>0 配对数） | 0/24 | **0/24** | ✅ 逐位一致 |
| edge_ge_30bp（毛≥30bp 前置命中） | 0/24 | **0/24** | ✅ 逐位一致 |
| 毛价差 mean / p50 | −9.2bp / −5.13bp | **−9.2bp / −5.13bp** | ✅ 逐位一致 |
| 净价差 mean / p50（固定 31.2bp 口径） | （旧口径含 min5 抬升） | **−40.4bp / −36.33bp** | ⚠ 口径差见下 |
| 净价差 mean（旧披露口径） | −45.0bp | —（对账见下） | — |
| 材料 | 60 bt 文件/1467 笔 D 后 fill/4 交易日 | 60 bt 文件/1467 笔 | ✅ 完全一致（D 后无新回测产物，样本零增长） |

**口径差对账（如实披露，不构成判据失败）**：旧披露净 mean −45.0bp = 毛 −9.2 − 有效成本 ~35.8bp，
其中 min5 抬升被折入硬成本；重建版以 CST-T0-001 registry 固定 31.2bp 为主口径（净 −40.4bp），
实收佣金（逐笔 commission 字段，含 min5 抬升）单列披露列 `realized_comm_mean_bp`=40.52bp/配对（匹配量分母）。
两口径下土规门结论完全相同（见 §3）——差值只影响观察读数不影响判定逻辑。

## 3. 复测结果（2026-09-22 连材料实测）

- n_fills_after_d = 1467（09-10:290 / 09-11:57 / 09-14:593 / 09-15:527），60 个 bt 文件全量入组；
- **n_symbol_day_pairs = 24 < 30 → `INSUFFICIENT_SAMPLES`**（REG-VALM-001 轻量土规），禁硬出方向性结论；
- 观察披露（非结论）：净正 0/24；开仓前置 0/24 全不命中；毛 mean −9.2bp / p50 −5.13bp；
  净 mean（31.2bp 口径）−40.4bp / p50 −36.33bp；
- 配对日分布：有双边配对的交易日=09-14/09-15（09-10/11 无同日双边）；
- 材料解析跳过=0（60 文件全解析成功）。

机读产物：`cost_trio_result.yaml` + `cost_trio_pairs.csv`（24 行逐配对）。

## 4. 样本积累与重考（判据灭失免疫后的正门）

```bash
python scripts/audit/cost_trio_exam.py
```

- 出结论条件：第一数 n_symbol_day_pairs ≥30（新回测产物入库后原样重跑即可，判据件已落 docs 不再随 tmp 灭失）；
- 结论判据（样本足时，F02 口径）：开仓前置命中=edge_ge_30bp 占比；净期望=净价差 mean>0（31.2bp 固定口径）。

## 5. 附随工单（R4 卡列待办，不阻塞本件）

- kline_5min 8,195 零星行（时区劈叉残余）：按 #398-四-R4/#399 维持 `src/zephyr/data/config/known_data_gaps.yaml`
  登记，随数据卫生批顺带处理，本班不动。

## 6. 与裁定链的关系

- #331（原 #304 撞号勘误）：砍做T旧形态——本件零状态变更，不动 verdict/can_deploy；
- #386：禁复试图救（S-OWNER-001 策略级）——本件是工具层判据重建，非策略复活；
- #399 二：本件执行依据（重建判据+落 docs 禁 tmp）；条件化做T复活轴=分包2 预注册假设卡另走 E4 考试正门。

*复核命令：`python scripts/audit/cost_trio_exam.py`（只读材料，产物仅 docs/_working/kimi_audit/lane_reports/）。*
