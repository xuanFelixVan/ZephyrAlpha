---
ttl: task_bound
title: 板块线预注册考试卡 v1.0 FROZEN——S10 强弱量化卡 + D2 偏好映射卡
created: 2026-09-23
sid: st-secbuild-20260923
lane: sector_line
status: frozen（2026-09-23 开工令即冻结，先于考试实跑落盘；frozen 参数禁改，实现缺陷可修）
frozen_note: 本文件=v0 草案（sector_prereg_exam_cards_v0.md）的冻结版。除本头与 §F 家底事实
  增补外，全部假设/输入/检验程序/判定门/多重检验披露/预承诺逐条继承 v0，零参数改动。
  判定表述遵循裁定#325（禁"全绿"，一律判档三态/四态）。
---

# 预注册考试卡 v1.0（FROZEN 2026-09-23）

## F. 家底事实增补（冻结时点实证，防考后惊讶；2026-09-23 05:30 实测）

1. kline_sector_880：2020-03-17→2026-09-22，469 码，442,841 行，A 态（S10 主判窗足量）。
2. sector_constituent：SCD-2 现行快照 236,836 行（valid_from 2026-07 起）——**历史成分数
   不可得**，S10-2"剔除成分数<10"以现行快照为代理，如实披露为近似（880 轴同花顺板块
   最小成分数远大于 10，预期影响≈0，考后复核）。
3. emotion_index：真值仅 2026-09-15 起（51 行，含 stage 四态）——D2 双轴窗 W_map 预期
   **<120 日 → 主判 INSUFFICIENT**（v0 已预登记）；单轴降档版为本轮真正可判档部分。
4. regime_state_anchored：dominant 实测值域 r1~r4（anchored 表）；r10~r12 并源
   （regime_snapshot_history）不启用，如实按 r1~r4 窗跑。
5. 板块日K 收益以 880 收盘价 pct_change 计算，等权截面（v0 口径不变）。

## 卡 S10（frozen）——假设/输入/程序/判定门/披露/预承诺

**逐条继承 v0 §S10-1~S10-6，零改动**（q3/q5/q20 加权 0.4/0.3/0.3；W_full/W_recent 两档；
NW t lag=5；分年度符号一致率；RRG 象限探索位；电风扇条件分解；EDGE/NO_EDGE/INSUFFICIENT
三态门；13 格披露仅主判进族）。

## 卡 D2（frozen）——假设/输入/程序/判定门/披露/预承诺

**逐条继承 v0 §D2-1~D2-6，零改动**（映射表=v0 规则表 frozen 阈值；W_map<120 日或任一档位
样本<15 日 → INSUFFICIENT；MAP_OK 门=NW t≥1.65+命中率超随机基线>5pct；消融三版并行报；
9 格披露仅主判进族；情绪轴真值缺窗如实 INSUFFICIENT，禁异轴顶替）。
