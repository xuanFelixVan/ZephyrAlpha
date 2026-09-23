---
ttl: task_bound
title: 板块线预注册考试判档报告 v1.0——S10 NO_EDGE ／ D2 主判 INSUFFICIENT·单轴降档 NO_MAP
created: 2026-09-23
sid: st-secbuild-20260923
lane: sector_line
card_source: sector_prereg_exam_cards_v1_frozen.md（FROZEN 2026-09-23，先于实跑落盘）
runner: scripts/backtest/sector_prereg_exam_runner.py
results: exam/prereg_exam_results_v1.yaml
discipline: 裁定#325 判档制；禁"全绿"表述；RED/INSUFFICIENT 如实通道；frozen 参数零改动
---

# 预注册考试判档报告 v1.0（2026-09-23 实跑）

面板：kline_sector_880 全史 1,584 日 × 469 板块（2020-03-17 → 2026-09-22）；等权截面；
T 日截面 → T+1 收益（PIT）；NW t lag=5（frozen）；成分<10 剔除以现行成分快照为代理
（frozen §F.2 披露）。

## 卡 S10 —— 判档：**NO_EDGE**（区分力不成立，如实记 RED）

| 判据（frozen 门） | 实测 | 达标 |
|---|---|---|
| 有效板块 ≥300 | 382（中位） | ✓ |
| 有效日 ≥500 | 986 | ✓ |
| W_full Q5−Q1 均值 >0 | **−0.2717%** | ✗ |
| W_full NW t ≥2.0 | **−0.571** | ✗ |
| W_recent 符号不反转 | −0.092%（反向） | ✗ |
| 分年度符号一致率 ≥60% | **0.20**（仅 2026 正号） | ✗ |

- 主判五项判据全不达，verdict=**NO_EDGE**。
- **预登记证伪风险兑现**（S10-1）：q20 权重 0.4 的中期动量在 A 股板块一日游生态下
  呈**反向**——分年度 2022/2023/2024/2025 四年全负、2026 微正，与"Top3 次日重合率 14.8%"
  的结构吻合：截面动量分层后 Q5 组次日跑输 Q1 组（短窗反转占优）。
- 电风扇条件分解（披露格）：快轮动日均值 −0.12% vs 慢轮动日 −0.34%——快轮动期负向收敛，
  未出现"动量只在慢轮动期有效"的救援结构。
- H1b 象限探索位（披露格，不进主判）：leading/weakening/lagging/improving 四组 T+1 均值
  明细见 results JSON。
- **预承诺执行**：本轮禁调权重（S10-6.2）；调权属下轮预注册新卡。
- 判档后果：momentum_pct 分位供料 L2 门三原料的"强弱排序"功能**未获考试支持**——
  sector_state 表继续产数（行情事实记录），但"按 momentum_pct 排 Top-N 当强势板块"的
  消费口径在本轮考试后应视为未验证档，不升待考池。

## 卡 D2 —— 判档：主判（双轴）**INSUFFICIENT**；单轴降档版 **NO_MAP**

- 双轴窗 W_map：regime∩emotion 真值日 = **16 日 < 120 日**（frozen §F.3 预登记兑现——
  emotion_index 真值 2026-09-15 起才有），verdict=**INSUFFICIENT**，落"差什么"清单：
  等情绪真值累积 ≥120 日（约至 2027-03）自动满足重考窗。
- 档位样本量（双轴 16 日）：FOLLOW 9 / OFFENSIVE 7——任一档位 <15 日同样触发 INSUFFICIENT。
- **单轴降档版**（D2-1 预承诺通道，regime-only，emotion=契约 mock）：
  - 窗：805 日（r1~r4 覆盖窗；r10~r12 未并源，frozen §F.4 如实）；
  - 指向组 T+1 相对收益差均值 = **−0.348%**，NW t = **−1.707**（方向为负，未过 ≥1.65 门）；
  - 命中率 = 0.517（对 0.5 随机基线超 +1.7pct，未过 >5pct 门；对 1/5 标签基线口径见 JSON）；
  - 档位分布：FOLLOW 839 / OFFENSIVE 441 / BALANCED 304 / DEFENSIVE 0 / CROWDING_WARN 0
    （后两档在单轴降档版下结构性不可达——emotion 冻结于温和档所致，如实披露）；
    分档命中：FOLLOW 0.540 / OFFENSIVE 0.479；
  - verdict=**NO_MAP**（三判据全不达）。
- 判档后果：偏好映射的"指向组次日占优"解释力**不成立**（单轴降档口径）；sector_preference
  表继续产数（契约+集成链路验证用途），preference_label/tilt 不作为任何消费方权重输入，
  banned_quadrant 作为保守过滤语义保留（未获正向证据，亦无放行语义）。

## 多重检验披露（frozen 格数）

- S10：主判 1 格 + 披露格 12（W_recent、象限 4、电风扇 2、分年度 5）=13 格，仅主判进族；
- D2：主判 1 格 + 披露格 8（消融以单轴版计 1、分档命中 5、档位分布 2）=9 格，仅主判进族。

## 预承诺兑现清单

1. frozen 参数零改动 ✓（卡面 v1.0 与 v0 逐条一致，仅增家底事实 §F）；
2. 考前先于实验落盘 ✓（冻结文件 commit 先于/同批于本报告）；
3. RED/INSUFFICIENT 如实入册 ✓（本报告即入册件）；
4. 判档后处置：两卡结论写入台账；sector_state/sector_preference 两表继续产数（事实记录
   +集成验证），消费语义按上述"判档后果"降档执行。

## 复考触发条件（预登记）

- 情绪真值窗 ≥120 日 → D2 双轴主判自动获得重考资格（集成夜换真值后为明晚集成窗首验点）；
- 板块动量口径迭代（如反转因子化）→ 下轮**新**预注册卡，本轮卡不复活。
