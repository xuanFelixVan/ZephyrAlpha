---
ttl: task_bound
title: L02-F 子类目挖矿簿 · 存量同域情绪簇（四件并存与内收）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

**① 一句话**：emotion_index 之外四件"档位计"式情绪件的盘点与内收边界（并存分层+内核单源化）。

**② 实测（行数/成熟度本册头注与 wc 实测）**：`signal_ashare/sentiment/sentiment_cycle.py` 1,334 行 **MATURITY=new**（CONSUMERS 头注：待 G07 相关性验证/G08 打板 sleeve/BM-SEL-03-B 软影响）；`signal_ashare/sentiment/market_sentiment_analyzer.py` 1,029 行 **production**；`signal_ashare/limit_up/youzi_relay_emotion_engine.py` 528 行 **production**；`data/intraday_sentiment_loop.py` 475 行 **production**（CONSUMERS 自注"常驻节拍交调度族挂接，本模块不注册任务"）；`alt_data/alt_regime_signals.py` F23 阈值 v1 provisional。**路径纠正（净新增）**：SKEL/09 号文把后两件记作 `signal_ashare/` 直属，实测在 `signal_ashare/sentiment/` 与 `signal_ashare/limit_up/`；且 market_sentiment_analyzer / youzi_relay 头标 **production**（非"未接电"），其生产语义与 sentiment_cycle=new 并存=成熟度与内收判定直接相关。

**③ 六向**：①上游 四件同源（涨停/连板/晋级率）——与 C1/C2 共用 daban 断供面（1 日缺口双伤，实证见 C2 册）。②下游 sentiment_cycle 三消费点未接线；intraday 环消费 market_breadth_snapshot。③算法 离散阶段（冰点/反核/主升/疯狂/退潮）vs 连续分位=两类对象，内收裁定=裁定编号 400（ruling_registry 已登记）"并存分层+内核单源化"。④后端 **三枚举同值不同 import 源**（sentiment_cycle 头注自曝）→ 单源化件未落=LK-02。⑤前端 情绪页/sentiment.html 已呈。⑥字段 无新缺字段。外部：三件已查无（查法：以"sentiment cycle stage classifier China institutional"及中文"情绪周期 五阶段 机构"检索，命中为自媒体复盘文，来源质量闸不过→登记不入图）。

**④ 缺口**：LK-02（枚举收敛移交治理班，在册）；G9 能力反查索引漏报（在册）；**L02-F-G1 四件中三件 production 却无"档位计 vs 温度计"消费口径词表（下游可能混用）**；**L02-F-G2 intraday_sentiment_loop 自称 production 但不注册任务=挂接真空**。

**⑤ 三态裁定**：LK-02=挂起（治理班排期，本车道跟办）；G9=施工（capability 索引重建，在册 L03-C08 同通道）；G1=**施工 P2**（词表登记，零代码）；G2=**挂起排期**（解锁=L09 编排器落地后的盘中节拍挂接，非本层可自决）。

**⑥ 日志**：R1 内部：四件路径/成熟度实测→signal（含两处路径纠正）；R2 外部：情绪周期机构件→noise，归因=来源贫矿（自媒体）。

**封矿判据**：六向封口 → **子模块封矿**。
