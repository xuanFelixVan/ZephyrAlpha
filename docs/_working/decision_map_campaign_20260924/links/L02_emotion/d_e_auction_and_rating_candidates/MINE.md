---
ttl: task_bound
title: L02-D/E 子类目挖矿簿 · 竞价情绪 stage 与评级情绪候选（两条"原料通、腿未挂"候选类目合并一簿）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（SKEL §6 张力 1 以实测收口）
---

**① 一句话**：D=竞价阶段情绪（stage='auction'，原料 auction_snapshot/auction_book）；E=研报评级情绪（research_report rating 上调/下调净流，v0.2 候选）。

**② 实测（本册）**：① `c1_market.emotion_index` **stage='auction' 实测存在 17 行 live，2026-09-01→2026-09-23** → SKEL §6 张力 1（"auction 行有无未核"）**收口＝行在**；② 但 `tasks.yaml` 实测只有两条情绪任务（:3452/:3466），`emotion_index_builder.py` 只有 close_final/pre_open 两常量（:72-73），全仓 grep `"auction"` 在 `src/zephyr/alt_data/*.py` **零命中** → **数据面有 17 行、代码面无写手 = 半蒸发态**（EVAP-03 蒸发的 14 行 post_auction WIP 曾真运行并留下数据，处方①已批"骨架维持在途"）；③ 原料：auction_snapshot 实测 272,117 行（→09-24）、research_report 实测 146,769 行（→09-18，滞后 4 交易日）；④ stage='auction' 行 components 实测 C1/C2 status=insufficient、C3 weight 0.25 → 该 stage 合成分母仅 2-3 成分，**不可当完整温度计使用**（新发现）。

**③ 六向（合并）**

| 向 | 发现 |
|---|---|
| ①上游 | D：auction_snapshot/auction_book 双表通（06-01 前永久结构性缺口，12 号文在册）。E：research_report（rating 列有值、**rating_change 空列=DU-12**）。外部：竞价信号一线读法命中多为自媒体（"高开 3%+量比>5"，头条 2026-08-13 https://m.toutiao.com/w/1873359026977792/ ；"集合竞价数据怎么用：开盘异动的量化描述"，CSDN 2026-08-16 https://m.blog.csdn.net/2601_96703250/article/details/163791879 ）→ **来源质量闸不过（散户教程级、无方法论/无样本）**，判"已查无（可入图级）" |
| ②下游 | D：CNS-11 竞价强度因子待接线（14 号文在册）。E：零消费。外部：已查无 |
| ③算法 | D/E 均未冻结成分定义（骨架 §4 auction 预留位）。外部：已查无 |
| ④后端 | **D 的缺口是"写手不在 HEAD"**→ 复职须 scheduler 补 post_auction 分支 + 运行验证；E 前置=DU-12。外部：已查无 |
| ⑤前端 | 内部：无独立呈现。外部：已查无 |
| ⑥数据字段 | D：auction 17 行不可复现（无写手）＝**数据孤本风险**；E：滞后 4 日 + 空列 |

**④ 缺口**：G12（auction 挂载，在册）/G13（评级候选，在册）/DU-12/CNS-11；**L02-D-G1 stage='auction' 17 行数据无对应写手（数据孤本，重跑不可得）**；**L02-D-G2 auction stage 合成分母仅 2-3 成分却与 close_final 同表同契约（消费侧易误用）**。

**⑤ 三态裁定**：G12/G1=施工（L02-C06 在册；复职批同时给 17 行打 orphan 标记或导出留档，消灭"不可复现数据"）；G2=**施工 P2**（在 components 里已可判分母数，补一条消费侧断言"成分数<4 禁当温度计"，零判据变更）；G13/E=挂起（解锁=DU-12 修 + 候选预注册卡，终局要机构情绪代理）。

**⑥ 日志**：R1 内部：auction 行 + 写手零命中 + 合成残缺 →signal（张力 1 收口，两条新缺口）；R2 外部：竞价方法文→noise，归因=来源质量不足（教程级）；R3 外部：评级净流方法→已查无（本轮未做定向检索，如实记，列长尾）。

**封矿判据**：两候选类目均六向封口 → **封矿（D/E 合簿）**。
