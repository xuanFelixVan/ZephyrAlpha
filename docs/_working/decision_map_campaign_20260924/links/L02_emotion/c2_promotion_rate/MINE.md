---
ttl: task_bound
title: L02-C2 子类目挖矿簿 · 晋级率成分（C2_promotion，含恒 1.0 缺陷的实测定性）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（缺陷已从"叙述"升级为"活体数据实证"）
---

# L02 · C2 晋级率成分

**① 职责一句话**：昨日连板（consec_limit≥1）个股今日再度封板的比例，衡量接力资金的延续意愿。

**② 现状实测**：`emotion_index_builder.py:95-105`（`_SQL_PROMOTION` 自连接：t1=consec_limit≥1、t2=close_sealed=1、ON 次日同 symbol；`countIf(t2.symbol IS NOT NULL)/count()`）、成分行 :263-268。**缺陷实测（本册）**：查 `c1_market.emotion_index WHERE stage='auction'` 最新行 components，C2 实值＝`raw_value 1.0 / percentile 1.0 / obs 16 / weight 0.0 / status insufficient` → **CH 默认 `join_use_nulls=0` 下 `t2.symbol IS NOT NULL` 恒真，promo≡1.0**，与 emoreplay 报告 §5 D-1 判定完全一致；本册贡献=给出**活体行级证据**（非报告转述）。当前因 obs<120 被降档不参与，属**休眠地雷**：daban 史满 120（约 2027-03）后 C2 将以 percentile 恒 1.0 进入等权合成，直接把指数常数项抬高 1/6。

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：daban_board_event 自连接。外部：晋级率口径两源——连板天梯三日对照晋级率页（lianban.net，2026-09-22）https://lianban.net/tianti.html 与"89 股涨停！连板晋级率回升至 42.86%"（头条财经，2026-09-16）https://www.toutiao.com/a7686147145740763650/ → 两源一致：分母=昨日涨停（或连板）家数、分子=今日再封板家数，**与本仓公式同构**；差异点＝外部常按"昨日首板→今日二板"分层，本仓为单一总率（登记不改造，改=新卡） |
| ②下游 | 内部：C2→emotion_index；另 regime overlay `t3_leader_score(max_consec, promotion_rate)` 亦需晋级率（`overlay_features.py:1172`）→ **跨环节共用原料，断供双伤**（本册净新增发现） |
| ③算法 | 内部：日频总率。外部：**炸板率与晋级率的配对读法**——"A 股炸板率 36%，晋级率却腰斩，短线情绪怎么了？"（头条财经，2026-09-09）https://m.toutiao.com/article/7683485373804167726/ 、"收盘后如何复盘炸板率指标来判断市场情绪的短期顶部"（.yueniuzq，2026-06-20）https://ag.yueniuzq.com/market-review/review-broken-board-rate-to-judge-sentiment-top/ → 两源支持"炸板率应与晋级率并列为独立子项"，本仓晋级率单尺、炸板仅在 C1 的 seal_rate 内（改造候选登记） |
| ④后端 | 内部：SQL 语义修（join_use_nulls 显式化或改 `countIf(t2.sealed=1)` 型判据）属成分口径变更 → version v0.1.0→v0.2.0 → 考试族重开（L02-C08 在册）。外部：已查无 |
| ⑤前端 | 内部：同 C1。外部：已查无 |
| ⑥数据字段 | 内部：symbol/consec_limit/close_sealed/trade_date 在；质量画像=同 C1（16 日 + 复断） |

**④ 缺口清单**：D-1（emoreplay 报告在册，本册实证）；L02-C07/C08（在册）；**L02-C2-G1 炸板率未作独立子项（外部两源支持并列）**——册内未见；**L02-C2-G2 overlay `t3_leader_score` 与本成分共用晋级率但无共享件（两套 SQL 各写一遍）**——册内未见。

**⑤ 三态裁定**：D-1=**施工 P1（判据变更须 Owner 门位，禁 AI 自改公式）**，且与 C07 合并为一次重考事件；G1=**挂起排期**（解锁=随 v0.2.0 口径变更批一并预注册，禁单点改判据）；G2=**施工 P2**（晋级率取数收敛为一个供数件，净 -1 散落 SQL，属结构修复不改口径）。

**⑥ 挖矿日志**：R1 内部：活体行级证据（obs=16/恒 1.0）→signal；R2 内部：跨环节共用面 grep→signal（净新增）；R3 外部：晋级率口径两源→signal；R4 外部：炸板率并列读法两源→signal（单源时只能标待验证，此处两源）；R5 外部：英文 promotion rate→noise，归因=方向无矿（A 股特有制度件）。

**封矿判据**：六向封口 + 缺陷证据升级 → **子类目封矿**。
