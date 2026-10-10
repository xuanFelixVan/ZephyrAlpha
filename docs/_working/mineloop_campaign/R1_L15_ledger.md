---
ttl: task_bound
title: "矿考循环班 R1 L15 车道台账（TDM-E-L0-04 明日情绪盘中滚动预测 + TDM-E-L0-02 偏离监控与修订）"
created: "2026-10-10"
sid: st-mineloop-20261010
family_id: MENELOOP-CAMPAIGN
---

# R1 L15 车道台账

> 车道 = L15；总包 sid=st-mineloop-20261010；作业口径真源=`.runtime/tmp/st-mineloop-20261010/MINING_BRIEF_R1.md`。
> 本文件独占，禁他人写入。产出根=`D:/ZephyrAlpha/.aidrafts/st-mineloop-20261010`。

## 0. 情绪面在册约束（任务书 §3 + Owner 明示）

- `c1_market.emotion_index` 10 月**仅 pre_open 腿**；`stage='close_final'` 行数=0（候 QMT 终端复元）。
- 本车道卡二选一写实：**绑 pre_open 腿=preregistered** 或 **依赖 close_final=blocked_on_data + 缺哪段 + 解锁判据**。
- **禁把断供面写成可考**；**禁为凑数虚构可得性**（§5、§7 双条硬红线）。

## 1. 六向作业矩阵（mining_sop v1.7.0 §2 / v1.8.0 §3）

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡数 | 族分布 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-E-L0-04 | 已入卡（algo_note_zh 完整：四时点 10:00/11:00/13:30/14:30 + 悲观档差 ≥1 + D123 三处反哺）；决策问句独立可判面已入 3 卡；未挖长尾=外部文献 URL 未逐条核（Lou-Poli-Gao/Renault JBF 2017/SSRN 5599654，本车道 grep 未在仓文档取回 URL+发布方+年份可核实行 ⇒ 记"受阻非查无"） | 已反查：Grep `TDM-E-L0-04` in src/scripts/config → 命中 4 件；`intraday_tomorrow_forecast.py:5` [CONSUMERS] 明文 "L0-02 偏离监控（downgrade_warning 消费，**待接线**）；L3-06 环境开关（情绪档输入，**待接线**）"；edges：L0-04→L0-02/L1-AGG/L2-06-1/P-P2（D123 三处反哺）；`generate_trading_day_cycle_map.py`/`trading_day_cycle_map.yaml` 引用节点。已入卡 | 同族近亲：夜矿 L3 车道 `TDM-E-L0-04__comparison__02_intraday_rollback_downgrade.yaml`（三臂 ACT/RECORD_ONLY/ACT_DELAY_CLOSE，preregistered）；机构三件套=响应曲线（分桶档位差→次日收益）＋时滞（四时点触发时刻差）＋条件稳定性（牛/熊分档），本车以 calibration 补前两件套；未挖长尾=外部文献可核实行 | 后端件实测：`src/zephyr/plan_engine/intraday_tomorrow_forecast.py` **存在**（MOD-PLAN-025，纯函数核零 IO，头 [MODIFY-GUARD] 地图节点 TDM-E-L0-04）；`brier_calibration.py` **存在**；TDM 命名 `next_day_8state_forecast`/`similar_day_inference` 与 plan_engine 目录不匹配——真实路径已核实为 `src/zephyr/signal_ashare/ml_forecast/next_day_8state_forecast.py`（MOD-SIG-037）与 `.../similar_day_inference.py`（MOD-SIG-063），二者皆非 plan_engine；D123 三处反哺的消费侧接线（L0-02、L1-AGG、L2-06-1、P-P2）实测为"待接线" ⇒ 输入消融臂只能标 blocked_on_impl | 一句话：预警面板"明日降档预警"卡片（intraday 4 时点触发时刻+档位差+三处反哺开关状态），本卡族不阻呈现 | **§3 在册事实直引**：`emotion_index` 10 月仅 pre_open、close_final=0。pre_open 覆盖窗与总行数未查（禁 CH 重查询窗 21:00–22:30）⇒ 卡 `data_window_evidence: 待总包 22:30 后实测`。close_final 历史段（夜矿 §卡记 2019..2025=244/243/243/242/242/242/243+2026=186 天）与本次 §3 断供口径**冲突**，本车不复用夜矿数字，改写"§3 在册：close_final=0"并给出解锁判据 SQL | **2** | calibration×2（一 preregistered / 一 blocked_on_data） | 否 | 卡 B（close_final 目标）缺 `emotion_index stage='close_final'` 2026-10-01 起段；未挖长尾=外部文献可核实行/D123 三处反哺接线后的独立可判面 |
| TDM-E-L0-02 | 已入卡（algo_note_zh：偏离超阈触发 boundary_revision_engine 修订当日边界；跨日/过期消费拒发；计划外操作记执行不一致）；决策问句独立可判面：触发条件+修订权限两问，夜矿 L3 已入 comparison 一卡，本车补 calibration+ablation | 已反查：Grep `TDM-E-L0-02` in src/scripts/config → 仅 `trading_decision_map.yaml` 消费（无代码直接消费节点 id）；edges：L0-01→L0-02 sequence intraday；L0-02→L0-03 sequence daily；L0-04→L0-02 feed（"明日降档预警触发边界修订"，实测 [CONSUMERS] 记"待接线"）；L2-09-2→L0-02 feed intraday（新闻事件传导） | 同族近亲：夜矿 L3 `TDM-E-L0-02__comparison__02_deviation_revision_authority.yaml`（三臂 REV_ON/REV_OFF/REV_LEAK_TEST）；机构三件套=响应曲线（偏离分位→修订收益/越界暴露收缩）＋时滞（触发时刻对收盘前反应窗）＋条件稳定性（高偏离尾部分位独立成柱），本车 calibration 补响应曲线；未挖长尾=时滞柱 | 后端件实测：`src/zephyr/plan_engine/plan_deviation_monitor.py` **存在**（MOD-PLAN-022）；`boundary_revision_engine.py` **存在**（夜矿卡误写为"待逐件核"）；`premarket_constraint_loader.py` **存在**（过期拒发件）；夜矿卡 `signal_derivation` 未写死 boundary_revision_engine 路径（诚实禁虚构），本车实测已确认存在→写入 ablation 卡；D123 反哺输入 `downgrade_warning` 消费侧接线未落地（intraday_tomorrow_forecast.py [CONSUMERS] 明证） ⇒ 消融臂只能 blocked_on_impl | 一句话：作战室"计划外操作归因表"+ 当日边界修订流水账 | `judgment_daily_plan` 12 行 / `judgment_plan_verification` 24 行（夜矿卡实测引用，本车不重跑）⇒ 当日计划实录不构成长窗真源；本车 calibration 卡以**重放臂**（L0-01 同口径重放）落地并显式标注；emotion_index 断供对本卡无直接阻塞（本卡信号=偏离幅度，非情绪档），仅 D123 反哺消融卡间接受影响（且属"待接线"） | **2** | calibration×1 + ablation×1 | 否 | 卡 D（消融降档预警输入）blocked_on_impl=缺 L0-02 侧消费 downgrade_warning 的接线代码；未挖长尾=时滞柱 / 新闻事件传导输入侧消融 |

**说明**：两节点各只有 1 张**生成器骨架**（`__comparison.yaml`，`status: empty`、`generated: true`，受保护禁改）+ 1 张**夜矿 L3 手工对照卡**（`__comparison__02_*`，preregistered）。本车**不重复**其对照假设，另开 calibration（响应曲线/时滞）与 ablation（输入消融）两条腿。骨架件按任务书禁改（`generated: true` 受保护），故本车不改 `__comparison.yaml`。

## 2. 本车新卡一览

| card_id 全名 | family | status | 关键 data_binding |
|---|---|---|---|
| `TDM-E-L0-04/calibration/03_pre_open盘前先验与盘中档位差` | calibration | **preregistered** | 绑 `emotion_index stage='pre_open'`（§3 在册 10 月唯一可得腿）+ 盘中 8 态融合档（intraday_tomorrow_forecast.py 组合器）+ 510300 ETF 分钟代理；target=次日 CSI300 收益（执行器 shift(-1) 兼容） |
| `TDM-E-L0-04/calibration/04_close_final预警兑现率` | calibration | **blocked_on_data** | 目标依赖 `emotion_index stage='close_final'` T+1 段态；§3 在册 2026-10 起该 stage 行数=0；解锁判据 SQL 已写死；窗口不动 |
| `TDM-E-L0-02/calibration/03_偏离幅度分位响应曲线` | calibration | **preregistered** | 不依赖 emotion_index；signal=当日实际暴露相对盘前计划的偏离幅度十分位（重放臂）；target=次日组合收益 |
| `TDM-E-L0-02/ablation/04_降档预警输入消融` | ablation | **blocked_on_impl** | 双臂 WITH/WITHOUT L0-04 downgrade_warning 输入；缺实现=L0-02 侧消费 downgrade_warning 的接线（intraday_tomorrow_forecast.py [CONSUMERS] 明记"待接线"）；解锁判据=接线落地并留有回归样本 |

## 3. 与在册断供/执行器缺口的对账

- **执行器缺口**（§3）：calibration `_series_metrics` 硬编码 `shift(-1)`（仅次日目标） ⇒ 本车两张 calibration 卡 primary 都是 **次日**（指数收益 / 组合收益），可跑现器；ablation 双臂 comparison/ablation 已并入 `run_card`（须注 `signal`+`signal_b`） ⇒ 已按此约束写双列绑定。
- **卡面"或"字**（§3）：本车四张卡 signal_derivation 无"或"字未择一；`emotion_index` 用 stage 严格二分（pre_open vs close_final），禁混装。
- **窗口钉死**：两张 preregistered 卡窗口 IS/OOS 与夜矿 L3 同窗（2021-07-01..2025-09-30 / 2025-10-09..2026-06-30，由 kline_etf_1min 起点与 WINDOW_HOLDOUT 共钉）；blocked_on_data 卡窗口**解锁后不改**（G4-5）。

## 4. 复挖结论（对夜矿 L3 车道同节点前役）

- **推翻点 1（后端件）**：夜矿 L0-02 卡 `signal_derivation` 未写死 `boundary_revision_engine.py` 路径（"待逐件核"）；本车 ls 实测**存在** `src/zephyr/plan_engine/boundary_revision_engine.py` ⇒ 补写死（本车 ablation 卡）。
- **推翻点 2（命名漂移）**：TDM `algo_note_zh` 记 `next_day_8state_forecast`/`similar_day_inference` 位于 plan_engine 语义下；实测两文件在 `src/zephyr/signal_ashare/ml_forecast/` 下（MOD-SIG-037/063），plan_engine 下另有 `next_day_forecaster.py`/`similar_day_evaluator.py`（消费件）。 ⇒ 数据绑定必须写 signal_ashare 全路径，不能凭 TDM 措辞。
- **推翻点 3（消费侧接线）**：夜矿 L0-04 comparison 卡与 L0-02 comparison 卡均**未记**"L0-04→L0-02 downgrade_warning 消费待接线"；`intraday_tomorrow_forecast.py:5` [CONSUMERS] 明文 ⇒ D123 三处反哺是"卡片描述可考、代码接线未至"的半完成态，须 blocked_on_impl 单独成卡。
- **确认点 1（close_final 断供面冲突）**：夜矿 L0-04 卡 `data_window_evidence` 记 close_final "2019..2025=244/243/243/242/242/242/243，另 2026 实测 186 天（本卡 OOS 段内真值齐）"，与任务书 §3 "10 月仅 pre_open 腿、close_final=0" 冲突。本车**不复用夜矿数字**、按 §3 口径写。夜矿卡 OOS 终点 2026-06-30 落在断供后（2026-10 起 0 行）—— 若 2026-07..09 也在断供段则夜矿卡 OOS 真值面同样受损；因未查 §3 未列此段 ⇒ 本车仅登记冲突不解裁，交总包 22:30 后统一实测。
- **未挖长尾明列**：①外部文献 Lou-Poli-Gao / Renault JBF 2017 / SSRN 5599654 未在仓文档可核实行（grep 零命中 URL/发布方/年份）；②时滞柱（L0-02 触发时刻对收盘前反应窗的分辨率收益）；③新闻事件传导输入侧消融（L2-09-2→L0-02 feed）；④D123 三处反哺各自单独成卡（L1-AGG / L2-06-1 / P-P2 消费侧接线后的边际贡献）。

## 5. 交叉复挖建议（20% 名单）

- `TDM-E-L1-S3/calibration/04_情绪先锋四态`（Owner 明示"情绪先锋四态卡排首批"，与本车 L0-04 close_final 卡同受 §3 断供约束；建议复核其 `data_binding.signal_column` 是否绑了 stage='close_final'，若是须回补 blocked_on_data 与解锁判据；若已绑 pre_open 则确认）——具体：前役是否把 close_final 写成可得、是否声明了解锁判据。
- `TDM-E-L0-04/comparison/02_intraday_rollback_downgrade`（夜矿 L3）——OOS 段 close_final 冲突（§4 确认点 1），复核其真值面是否成立；不成立则本车 `calibration__04` blocked_on_data 需扩至 comparison 族同款处置。
- `TDM-E-L0-02/comparison/02_deviation_revision_authority`（夜矿 L3）——`signal_derivation` 未写死 boundary_revision_engine 路径（§4 推翻点 1），实际件存在，须由总包在下一轮以受保护标记另建"补充件"（非改，因禁改已存在文件）。

## 6. 汇总

- 本车道节点总数：**2**（TDM-E-L0-04 / TDM-E-L0-02）
- 新卡总数：**4**
- 族分布：calibration×3、ablation×1（不重复夜矿 comparison 族）
- status 分布：preregistered×2、blocked_on_data×1、blocked_on_impl×1
- 未挖长尾：见 §4 明列四条
- 假绿风险：见 §7 回报段（夜矿 close_final 数字 vs §3 冲突、D123 三处反哺未接线）

## 7. T4 监听车道触发清单（"QMT 复元即解锁可考"）

以下卡**只要 QMT 终端复元**（`c1_market.emotion_index stage='close_final'` 2026-10 起段行数 >0）即解锁开考，无需其它补件：

1. **`TDM-E-L0-04/calibration/04_close_final预警兑现率`**（本车新卡）——解锁判据 SQL 已写死。

以下卡是**次生解锁**（close_final 复元可让前役卡的 OOS 真值面恢复）：

2. **`TDM-E-L0-04/comparison/02_intraday_rollback_downgrade`**（夜矿 L3）——若其 OOS 段依赖 close_final 则同批解锁；本车不改，仅登记。

**非 QMT 触发**（不属 T4 清单，另轨）：
- `TDM-E-L0-02/ablation/04_降档预警输入消融`：解锁=L0-02 侧消费 downgrade_warning 的接线代码落地（intraday_tomorrow_forecast.py [CONSUMERS] "待接线" 消解），与 QMT 无关。
