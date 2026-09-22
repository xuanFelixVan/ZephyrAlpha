---
ttl: task_bound
title: 板块层骨架设计稿 v0——sector_state/sector_preference 最小蓝图
created: 2026-09-22
sid: st-secmine-20260922
lane: sector_line
status: draft（交下轮施工讨论，未开工）
doc_version: v0.1
algorithm_source: 22_sector_rotation_spec.md v1.9.8（公式级真源，本稿只做集成编排不重造算法）
---

# 板块层骨架设计稿 v0（最小板块层蓝图）

> 定桩背景：Owner-Max 2026-09-22——板块层=全链条最薄段（S9-S11 三问空白），大盘×情绪的输出、
> 情绪的输入，时间分层拆环后与情绪班并行。
> 本稿只设计不施工；全部输入为仓内已有表（盘点册②为准），算法全部复用 22 号 spec 与
> signal_ashare/sector/ 16 模块，**零新采集、零新算法发明**。
> 与 22 号 spec 的边界关系：spec 定义"板块=选股输入特征"；本次定桩将板块升格为独立层
> （排班表 S 层）——该边界升格本身已在缺口清单⑤登记待 Owner 追认，本稿按新定桩执行。

## §1 数据流全景（一张图）

```
c1_backtest.regime_state_anchored (dominant r1~r12, A态)──┐
                                                          ├─→ [D2 偏好映射层] sector_preference
c1_market.emotion_index (情绪班产出, 契约v0.1; 开发期mock)─┘      (大盘×情绪→板块偏好表)
                                                          │
c1_market.kline_sector_880 (日K六年, A态) ─→ sector_momentum(q3/q5/q20) ─→ [S10 强弱聚合层]
c1_market.kline_sector_880 ─→ sector_rrg(DualEma 10/26 四象限) ─→        sector_state
c1_market.sector_snapshot (实时截面, A态) ─→ sector_analyzer.evaluate_strength ─→ (每板块每日)
c1_market.money_flow × sector_constituent ─→ sector_breadth(资金性质聚合) ─→      强弱分位
c1_market.sector_fund_flow (行业净流入, 短史) ─→ 净流入分位 ─→                    +轮动标签
c1_market.limit_up_pool / daban_board_event ─→ sector_limit_up_ratio(涨停比) ─→
                                                          │
                                                          ▼
                                    sector_state(T, close_final) = T+1 盘前输入
                                                          │
                                                          ▼
                                              板块→个股选择（G05/现有 sector_rotation_score_mapping）
                                              + L2 板块门三原料（top/retained_sectors/score 首次有着落）
```

**防循环红线**（与情绪班对偶）：板块热度/sector_state **禁回灌** emotion_index（同 ts 循环
依赖禁令，总包 §2 时戳纪律）。

## §2 输入清单（全部已落库，零新采集）

| 输入 | 表/模块 | 盘点册态 | 用途 |
|---|---|---|---|
| 大盘状态 | regime_state_anchored（dominant 四档）+ regime_snapshot_history（r1~r12） | A | 偏好映射第一轴 |
| 情绪指数 | c1_market.emotion_index（契约 v0.1：0-1 灰度分位+stage 四态+components 明细+version） | D（在途，开发期 mock） | 偏好映射第二轴 |
| 板块日K | kline_sector_880（469 码，2020-03 起 1584 交易日） | A | q3/q5/q20 动量+RRG 序列 |
| 板块实时截面 | sector_snapshot（up_home/down_home/涨速） | A | evaluate_strength 结构强度+盘后定格 |
| 成分股 | sector_constituent（SCD-2，595 板块→6179 股） | A | 涨停比分母+资金聚合上溯 |
| 个股资金流 | money_flow（五层净流入） | A | 板块级净流入（money_flow×成分聚合，勿另建管道——spec §3.1⑥） |
| 行业资金流 | sector_fund_flow | C（仅 6 天史） | 净流入分位（短史窗降档如实标注） |
| 涨停原料 | limit_up_pool（含 industry 列）+ daban_board_event | A / C（断 09-15） | 涨停比归一化 |

## §3 sector_state——每板块每日状态（S10 强弱量化层聚合输出）

**口径**（算法全部指认 22 号 spec 公式级条目，不重造）：

| 成分 | 算法真源 | 输出 |
|---|---|---|
| 动量分位 | sector_momentum.multi_tf_momentum：0.4×q20+0.3×q5+0.3×q3（percentile_rank 截面归一，spec §3.1⑧） | momentum_pct ∈[0,1] |
| 轮动象限 | sector_rrg：JdK DualEma 10/26，RS-Ratio/RS-Momentum 四象限+尾部 8 日路径（spec §3.1④） | rrg_quadrant ∈{leading,weakening,lagging,improving} |
| 结构强度 | sector_analyzer.evaluate_strength（涨停比 40%+梯队 30%+趋势 30%，涨停比=涨停数/成分数，spec §3.1①） | strength ∈[0,100] |
| 资金维度 | sector_breadth.aggregate_capital_nature_to_sector + sector_fund_flow 净流入分位 | capital_score ∈[-1,1]+net_inflow_pct |
| 市场级状态 | sector_divergence：5 状态分类（CONSENSUS_CLIMAX/DISAGREEMENT_PULLBACK/HEALTHY_MAINLINE/DISTRIBUTION_RISK/NEUTRAL_MIXED）+ 电风扇速度计（spec §3.1⑨） | rotation_state（市场级单值）+ watch_score |

**v0 取最小集**：momentum_pct + rrg_quadrant + strength + net_inflow_pct + rotation_state
（市场级）五件；watch_score 与 capital_score 进 v0 但判"观察列"（不进主判）。

## §4 sector_preference——大盘×情绪→板块偏好表（D2 映射层）

**v0 规则表草案**（两轴离散化×映射，可解释优先、禁黑箱；阈值全部 proposed 待 E4 考试校准）：

- **情绪轴**（emotion_index 三档）：≤0.4 低温 / 0.4-0.7 温和 / ≥0.7 高温。
- **大盘轴**（dominant 三档合并）：r1/r2 震荡、r3/r12 上行、r4/r10/r11 下行修复。
- 映射输出=**板块风格偏好标签+权重倾斜**（非具体板块名单，名单由 sector_state 强弱分位
  取 Top-N 动态生成，防"静态名单一周失效"——22 号 spec §5.3 电风扇实证）：

| 情绪\大盘 | 震荡 | 上行 | 下行修复 |
|---|---|---|---|
| 低温 | 防御/低波+高股息倾斜 | 均衡 | 超跌改善象限优先（PANIC_REPAIR 同构） |
| 温和 | 主线跟随（HEALTHY_MAINLINE 加分） | 进攻：领先象限+动量Top | 均衡偏防御 |
| 高温 | 拥挤警示（CONSENSUS_CLIMAX 扣分同构） | 进攻+拥挤双示警（watch_score 抑制） | 分歧回调防御（DISAGREEMENT_PULLBACK 同构） |

- 偏好表输出形态：preference_label（5 档）+ tilt（权重倾斜系数 0.8~1.2 proposed）+
  banned_quadrant（该档位禁入的 RRG 象限，如 RISK_OFF 时 lagging 禁入——水温响应面
  sector_gate 同构）。
- **对齐声明**：本表是 sector_gate 水温响应面（emotion/regime→门参数）的**板块层兄弟件**——
  gate 管"放行门槛"，preference 管"偏好倾斜"，共享同一套两轴输入，输出不重叠。

## §5 落库表草案（DDL 形态对齐 emotion_index 模式）

```sql
CREATE TABLE IF NOT EXISTS c1_market.sector_state
(
    trade_date    Date                        COMMENT '交易日',
    stage         LowCardinality(String)      COMMENT 'pre_open/intraday_vN/close_final',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳（收盘态=15:10，盘前=09:15）',
    sector_code   String                      COMMENT '板块码（880xxx 主口径）',
    sector_name   String                      COMMENT '板块名',
    momentum_pct  Nullable(Float64)           COMMENT 'q3/q5/q20 加权动量分位 [0,1]',
    rrg_quadrant  LowCardinality(String)      COMMENT 'leading/weakening/lagging/improving',
    strength      Nullable(Float64)           COMMENT '结构强度分 [0,100]',
    net_inflow_pct Nullable(Float64)          COMMENT '板块净流入截面分位 [0,1]',
    capital_score Nullable(Float64)           COMMENT '资金性质板块级得分 [-1,1]（观察列）',
    watch_score   Nullable(Float64)           COMMENT '市场级 5 状态调节分（观察列，冗余存便于单表回放）',
    components    String                      COMMENT 'JSON 明细 [{name,raw_value,percentile,weight,status}]',
    version       LowCardinality(String)      COMMENT '语义化版本，口径变更必升版',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage, sector_code)
```

```sql
CREATE TABLE IF NOT EXISTS c1_market.sector_preference
(
    trade_date    Date                        COMMENT '交易日',
    stage         LowCardinality(String)      COMMENT 'pre_open/intraday_vN/close_final',
    ts            DateTime64(3, 'Asia/Shanghai') COMMENT '状态时戳',
    regime_dominant LowCardinality(String)    COMMENT '大盘档（r1~r12 原值透传）',
    emotion_index Nullable(Float64)           COMMENT '情绪指数快照（消费值留痕）',
    emotion_version LowCardinality(String)    COMMENT '所消费 emotion_index 的 version（契约追溯）',
    preference_label LowCardinality(String)   COMMENT '5 档偏好标签',
    tilt          Float64                     COMMENT '权重倾斜系数（proposed 0.8~1.2）',
    banned_quadrant String                    COMMENT '禁入 RRG 象限（可空/多个逗号分隔）',
    watch_score   Nullable(Float64)           COMMENT '市场级调节分透传',
    version       LowCardinality(String)      COMMENT '语义化版本',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stage)
```

（DateTime64(3)+显式时区合规 RULE-SCHEMA-TZ；ReplacingMergeTree 幂等重跑安全；DDL-as-Code
归 schemas/categories/ 施工班流程，本稿只定形态。）

## §6 stage 时点与更新时点（契约四态对齐情绪班）

| stage | 触发时点 | 内容 | v0 状态 |
|---|---|---|---|
| close_final | T 日 15:10 盘后 | sector_state 全量（q 系+RRG+强度+资金），**真源/定格态** | v0 实现 |
| pre_open | T+1 日 09:15 | =T 日 close_final 态+preference 重映射（消费 T-1 close_final 的 emotion_index 盘前态） | v0 实现 |
| intraday_vN | T 日盘中滚动（预留） | sector_snapshot 30s 轮询已有（采集层 production），盘中强度滚动 | 预留 |
| auction | T 日 09:25（预留） | 竞价截面映射 | 预留 |

**时戳纪律**：T 日收盘态=T+1 盘前输入；同一 ts 内禁循环（emotion 不吃板块、板块不吃当日
emotion 盘中值——只吃已定格的 T-1 收盘态与 T 日盘前态）。

## §7 版本纪律

- v0.1.0：五成分（动量/象限/强度/净流入分位/市场级状态）+偏好规则表 v0；成分或阈值变更
  升 minor，映射结构变更升 major。
- sector_fund_flow 短史（6 天）期间净流入分位如实降档（status=insufficient，权重重分配），
  对齐情绪班"禁硬凑"纪律。
- 每行 components JSON 带逐成分 status（ok/insufficient/missing）。

## §8 不做什么（硬边界）

1. 不采新数据、不改 16 个信号模块本体（只做聚合编排层）。
2. 不做板块→仓位直接分配（偏好=标签+倾斜系数，仓位归 firm/regime 层——spec §3.2 边界，
   升格裁定待 Owner 追认见缺口清单⑤）。
3. 不碰 emotion_line 写域；板块热度不回灌 emotion_index。
4. 施工须另走 construction_workflow_policy 十五步闭环+depgraph 登记（apply_depgraph
   --add-design-node）。
5. 开发期 emotion 用 mock（契约形态），集成夜换真值；集成前 sector_preference 的情绪轴
   输出判 INSUFFICIENT 不判 RED。
