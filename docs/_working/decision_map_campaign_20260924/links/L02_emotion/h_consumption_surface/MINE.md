---
ttl: task_bound
doc_type: log
title: L02-H 子类目挖矿簿 · 情绪消费面
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成（含 D13 已落地改判）
---

**① 一句话**：登记 emotion_index 被谁按什么口径读走（板块偏好第二轴 / 条件包五档 / 能力路由 / 考试卡）。

**② 实测**：① **D13 已接线**——`signal_ashare/sector/sector_state_aggregator.py:30-31,497-516` 实测为"无源=显式缺轴 fail-visible（`axis_status='missing_emotion'`，**D13 接线删除 mock 0.5 分支**）"，随 commit d27e0f0df3 进 HEAD（`git log` 实测），SKEL L02-C03 判"待施工"→ **改判已落地，待销口**；② 3×3 偏好规则表 :452、`emotion_band()` :473；③ 消费口：`data/sector_state_pipeline.py`（读 close_final@T）、`backtest/regime_validation/condition_package.py`（灰度五档边界冻结 (0.2,0.4,0.6,0.8]，实测闭卷最新值 0.456886/0.397086 落"温和/降温"档）、`internal_compute_provider.py` capability 路由；④ 实测偏好表产出：`c1_market.sector_preference` **仅 2 行**（09-23 OFFENSIVE tilt1.2 / 09-25 BALANCED tilt1.0，均由 pre_open 槽写）→ 情绪轴接通后**偏好面仍近乎空转**（缺 close_final 侧偏好行），本册净新增。

**③ 六向**：①上游 情绪双 stage（A 册）。②下游 见实测。③算法 外部：状态条件化消费为共识（沿用 06 号文冷水族）；本轮无新增可引件→已查无。④后端 **无"消费方清单机读件"**（靠 grep 现拼）。⑤前端 偏好/情绪卡。⑥字段 close_final 8,614 日可回测、**pre_open 仅 18 日不可回测**（A 册 G1 联动）。

**④ 缺口**：D13（**本册改判已落地**）；D2 NO_MAP（在册，情绪轴对板块偏好消费口径无效）；**L02-H-G1 sector_preference 只产 pre_open 侧、close_final 侧偏好行缺失→ 消费面覆盖≈0**；**L02-H-G2 情绪消费方无机读登记表**。

**⑤ 三态裁定**：D13=施工 P0 文档面销口；D2=挂起（判据不动，等 v2 卡/新预注册）；G1=**施工 P1**（补 close_final 偏好行或显式声明"偏好仅盘前语义"，二者都消灭人工误读）；G2=挂起（解锁=图书馆 potential_consumers 通道，裁定编号 410 已批增枝，走 L03-C08 同车）。

**⑥ 日志**：R1 内部：aggregator fail-visible + commit 归属→signal（改判）；R2 内部：CH 偏好表行数探针→signal（新缺口）；R3 外部：情绪条件化件→已查无。

**封矿判据**：六向封口 → **子模块封矿**。
