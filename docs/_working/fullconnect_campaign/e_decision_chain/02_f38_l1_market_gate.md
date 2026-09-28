---
ttl: task_bound
title: F38 L1 大盘总闸+六传感器——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f38-l1-gate-20260927
---

# F38 L1 大盘总闸+六传感器——挖干案卷

> 一句话：全流唯一开闸裁定点（materiality=critical）——RegimeSnapshot 概率×六段情绪预算带×日级水温→总仓位上限+六段状态+策略路由三件套，一次判定 broadcast 全图。节点组=TDM-E-L1 gate+S0/S0-1/S1..S5/AGG 共 9 节点（今日 yaml:266-544 机数=9，零漂移）。总册 built｜P1｜T2；上游 A 段行情+F33，下游 F39-F41/C1/X 流。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | F33 L9 三快照（DS-150/082/098/059/107/108）；L01 regime 链 7 态概率（REGIME_STATES 今日实锚=src/zephyr/regime/core/regime_detector.py:107） |
| ②数据原料 | regime_state_anchored 表（AGG 消费切换终批 2026-09-23 Owner production 翻转，册引）；期权 IV/SyntheticVIX 双路径；新闻流水线 S0-1 |
| ③状态输出 | 当日总仓位上限+总暴露熔断曲线 cap=1−0.70×clamp((vol_pct−0.30)/0.70)（地图 L1-AGG 注，册引）；六段状态+策略路由 |
| ④下游消费 | L0（无裁定权）、C1 预算带、L2-05-1 月级封顶、L3-06 环境开关查六段表、daily_decision_orchestrator S2（regime_snapshot_history PIT）、X 流 S2 情绪退潮加权（地图 3405 行，册引） |
| ⑤自动化触发 | daily_kline SUCCESS 事件链 regime 刷新棒（册引 f38 册 §五）；新鲜度口径 D1=滞后>1 交易日=缺（09-21 Owner 对齐，册引）；S5 水温 9:35 首算盘中可更新（唯一盘中可变 L1 输入） |
| ⑥缺口债 | BT-P0-001 冻结未考/BT-P0-002 verdict 未回填；六段×五阶段双词汇映射散在调用方；S0 政策维人工录入；六段预算带全 proposed |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/regime/`：45 件 .py（实扫）。core/ 3 件：regime_detector.py（MOD-REGIME-001，1163 行册引）、anchored_state_machine.py（v2 波动率风险四档）、__init__.py。
- 9/9 module_ref 在盘（册引 f38 册 §四零缺件；今日抽锚 REGIME_STATES=7 态 r1-r4+r10-r12 实证）。分布：regime/core/regime_detector.py+anchored_state_machine.py；signal_ashare/core/index_sensor、limit_up_followthrough、daily_condition_sensor；signal_ashare/sector/lhb_premium_analyzer（DEDUP 抽 core/analysis_utils 册引）；regime/features/synthetic_vix（SVX-1-P0 治理册引）；policy_expectation_analyzer、news_sentiment_analyzer（L02 SKEL H 块：market_sentiment_analyzer.SentimentPhase 4+1 枚举同域簇）。
- 关联真源件：environment_switch.py:40 六段封闭集（L3-06 共件）；sentiment_cycle.py:52-65 五阶段 enum；framework_composer.REGIME_STATE_TO_ACTIVATION_PHASE=六段映射唯一真源（册引 2026-09-25 附录C 已切）。
- 表：c1_backtest.regime_state_anchored（anchored_state_machine.py:84 册引）；regime_snapshot_history（3,629 日 PIT，L03 SKEL §8 册引）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| AGG 状态输入源 | **生产接线** | regime_state_anchored 切换有实证批号（tasks.yaml:648 册引；夜批零缺勤+判据①机械复核，册引） |
| regime 刷新链 | **编排接线** | dloop 序 regime 刷新→…→编排器末棒（册引 f38 册 §五；L01 SKEL S9 消费面 11 点含总闸） |
| S5 水温 | **接线（盘中可变）** | daily_condition_sensor.py:45-52 WaterTempTier 五档（册引锚） |
| S4 波动率双路径 | **接线（带降级）** | 两路均败→None→消费侧回退 vol_pct（C1 不退化，册引） |
| S0-1 新闻情绪 | **半接线** | market 腿在产 185 日；symbol 腿止 2026-08-20（DU-06）；score 腿停 2025-09-09（DU-05）；LLM 旗标已立（09-23）对照期未核（L02 SKEL D 块） |
| 六段×五阶段归并 | **散线（漂移风险）** | environment_switch 只认六段、sentiment_cycle 输出五阶段，归并由调用方负责（册引 f38 册 §七-3） |

**骨架勘误（本日独立复核新得，登记待 D 线处置）**：
1. **L02 大盘情绪升格缺口（wiring_gap_inventory §1.2 已定桩未落位，登记本卷）**：L02 链路（emotion_index builder 主链+全史回放+成分族 C1-C6+消费面）已在 decision_map_campaign 定桩为独立状态变量层（L02_emotion SKEL 9 子块 6 SEALED），但 122 环节总册 D 段 F37-F52 无对应环节行、TDM 图亦无 L02 层节点——emotion_index 目前经 sector_state_pipeline:109（偏好第二轴）与 condition_package 灰度五档间接消费，属"层外供数"。处置建议：总册增补 L02 环节行或在本卷增设"情绪供数轴"附节挂账（Owner 裁-5 环节改写授权联动）。
2. f38 册 §三"情绪六段（列轴）"真源标"地图 state_matrix 列轴"：今日未逐列复核 state_matrix，列轴口径维持册引（不确定项进待裁节）。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G38-1 | BT-P0-001 总闸谨慎度分档判据冻结未考 | 按已冻结 plan 直接开考（零新施工），0.5 天 | **P0** |
| G38-2 | BT-P0-002 已有 first_valid_run 但 confidence 未回填 | runner 台账核查后回填，0.5 天 | **P0** |
| G38-3 | L02 情绪升格未落位（骨架勘误 1） | Owner 裁定环节改写授权（裁-5）后挂账；短期在 F38 卷以"情绪供数轴"名义登记 | P1 |
| G38-4 | 六段↔五阶段↔regime 三方映射无单一真源函数 | 钉进唯一真源件（framework_composer 已是六段映射唯一真源），1 天 | P1 |
| G38-5 | S0 政策维人工录入（最后人工口） | KS 组另类源线 F31 交界，不在本卷施工 | P2 |
| G38-6 | 六段预算带全 proposed 数值轴未回测 | C1 域交界登记 | P2 |

## 五、自审闸三态

**挖干可施工**（状态机血肉七套全数落码；两件 P0 欠账路径清晰均零新施工；L02 升格缺口已登记待裁）。

### 待裁
- L02 升格挂账形式（总册增行 vs 本卷附节）——归 Owner 裁-5 同窗。
- state_matrix 列轴口径亲核——本卷未做，留 D 线。

## 六、复跑命令

```bash
sed -n '107,110p' src/zephyr/regime/core/regime_detector.py             # 7 态实锚
grep -c "node_id: TDM-E-L1" config/trading_decision_map.yaml            # =9
sed -n '40,60p' src/zephyr/signal_ashare/core/daily_condition_sensor.py # 水温五档
sed -n '40p' src/zephyr/signal_ashare/core/environment_switch.py        # 六段封闭集
grep -n "emotion_index" src/zephyr/data/sector_state_pipeline.py        # L02 间接消费锚
```
