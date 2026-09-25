---
ttl: task_bound
title: L02-A 子模块挖矿簿 · 情绪指数 builder 主链（合成核与契约）
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-MINE-A
status: MINE 完成
---

# L02 · A 情绪指数 builder 主链

**① 职责一句话**：把六成分原值统一折成 250 日滚动秩分位、按"可用成分等权"合成 emotion_index∈[0,1]，并落 `c1_market.emotion_index`。

**② 现状实测**

| 项 | 实测 |
|---|---|
| 件 | `src/zephyr/alt_data/emotion_index_builder.py`（全文精读关键段）：版本 `EMOTION_INDEX_VERSION="v0.1.0"` :71；stage 常量 close_final/pre_open :72-73；`_PCTL_WINDOW=250` :75、`_MIN_OBS=120` :76、`_MARGIN_CHG_DAYS=20` :77、`_NEWS_MEAN_DAYS=5` :78 |
| 取数 | 五表经 TableRegistry 唯一真源 :81-85（禁硬编码）；六条 `_SQL_*` 常量 :89-127（NO-BARE-SQL 合规） |
| 合成 | `_build_components` :234-325 → `build_emotion_index` :328-365：usable=status=='ok' 才参与（:348），`w_each=1/len(usable)` 等权重分配（:351，"禁硬凑"），index=Σ percentile×weight（:354），ts 带 +08:00 显式时区（:355-357，合 RULE-SCHEMA-TZ） |
| stage 语义 | pre_open→C1-C4 复用 T-1 收盘态 + C5/C6 as-of T（:341-342）；close_final→15:10 定格（:343-344） |
| DDL | `schemas/categories/market/market_emotion_index.py`：ReplacingMergeTree (trade_date,stage) 幂等；**source 列已在 HEAD**（:42 `source LowCardinality DEFAULT 'live'`，注释 :10 明写"source 不在 ORDER BY 内→回放班会结构性跳过"） |
| 任务 | `tasks.yaml:3452 emotion_index_close_final`（schedule=daily_kline）+ `:3466 emotion_index_pre_open`（pre_market 09:15）；**实测无第三条情绪任务** |
| 表实测（本册 CH 只读探针 2026-09-26） | close_final **8,614 唯一日**（live 18 + replay 8,596）1991-06-10→**2026-09-24**；pre_open 仅 live 18 日（→09-24）；**auction 17 行 live（→2026-09-23）**——见 D 册改判 |

**③ 六向台账**

| 向 | 发现 |
|---|---|
| ①上游 | 内部：五表；pre_open 腿无回放（18 日）→ 任何用 pre_open 轴的历史回测目前不可行（**新缺口 A-G1**）。外部：情绪指数合成的工业成例=CNN 七成分等权 + 中信建投 20+ 指标"等权+PLS 双轨"（两源已在 `emotion_line/external_methodology_review.md` §5 锚定，本册标沿用不重复收录） |
| ②下游 | 内部：`sector_state_pipeline.py`/`sector_state_aggregator.py`（3×3 偏好表 :452、emotion_band :473）、`backtest/regime_validation/condition_package.py` 灰度五档冻结 (0.2,0.4,0.6,0.8]、`internal_compute_provider.py` capability 路由。外部：已查无（下游=本仓自有消费方） |
| ③算法 | 内部：秩分位 + 等权 + 不足降档（<120 obs→insufficient，权重重分配禁硬凑）。外部：rank 分位合成为外部文册 §2"推荐目标方案"→ 现行即目标态，无返工；二期备选序 IC 加权→PLS→PCA（骨架 §3 在册，挂起） |
| ④后端 | 内部：全成分 status 已入 components JSON（可自动巡检）；**无"成分级断供哨兵"**（A-G2）。外部：已查无 |
| ⑤前端 | 内部：仪表盘情绪页 `web/pages/sentiment.html`（实测存在）。外部：已查无 |
| ⑥数据字段 | 内部：见 B/C1~C6 各册逐成分质量画像；合成层本身零缺失字段 |

**④ 缺口清单**：LK-01（IC 加权二期，在册）；**L02-A-G1 pre_open stage 无历史回放面（18 日）**；**L02-A-G2 成分级断供无哨兵**；**L02-A-G3 情绪双 stage 消费口径未统一（消费者各取 close_final 或 pre_open 无词表登记）**——三条均册内未见。

**⑤ 三态裁定**：G1=**施工 P2**（回放器已具备同公式重放能力，扩 stage 只需放开参数；终局要"任一 stage 可全史回测"）；G2=**施工 P2**（并入 known_data_gaps 既有哨兵面，净零）；G3=**挂起排期**（解锁=state_vocabulary_registry 情绪 stage 登记批，属治理班）；LK-01=挂起（考试通过后才启，判据不动）。

**⑥ 挖矿日志**：R1 内部：builder 全文键段行号 + DDL + 任务实测→signal；R2 内部：CH 探针（stage×source×日期分布）→signal（pre_open 无回放量化）；R3 外部：情绪合成等权成例→沿用（归因：已两源在册，重搜无增量）；R4 外部：stage 语义（盘前温度计）惯例→noise，归因=方向无矿。

**封矿判据**：六向封口 → **子模块封矿**。
