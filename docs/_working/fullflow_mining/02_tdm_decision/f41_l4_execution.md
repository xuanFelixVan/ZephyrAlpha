---
ttl: task_bound
title: F41 L4 买卖点与执行——环节册（TD-A 前半）
session: st-ailayer-fullflow-td-a
creation_token: f41-l4-exec-book-tda-20260925
date: 2026-09-25
status: mined
---

# F41 L4 买卖点与执行——环节册

> **一句话**：执行层总枢纽——管"什么时候、怎么把单下出去"：分批/时序/价格锚/资金分配/打板专项/SOR 算法/条件队列/突破降级/硬约束/订单状态机/部分成交/订单级预检/容灾对账/成本反馈 14 子环节。与 EX 组（F53-F58，M7 已挖干）强交界——本册挖 TDM 判据面，执行基建血肉引用 M7 册不重挖。
> 节点组：TDM-E-L4 + 01~14，共 15 节点。总册三态标 built｜**P0**｜T8。materiality=critical 2 处：L4-09 硬约束（crosscutting）。

## 一、环节定义与边界

- **供料方**：F40 候选池（带 sleeve 标签+顺位分）；F37 L0 时序窗口与边界约束；F59 风控限额（precheck 消费）。
- **消费方**：F53 订单生命周期（EX 组）、F57 结算对账、F58 成本反馈（EX 扩册）；kill_switch（precheck 消费）。

## 二、判定输入 / 辔回（判定输入 / 输出）

| 子环节 | 判定输入 | 判定输出 |
|--------|---------|---------|
| 01 分批建仓 | 置信度（回踩 A/B/C 为调节因子） | 高置信首批 70%/中 50%/低 30%，剩余等确认（涨 2% 或站稳分时均线） |
| 02 买入时序 | 时序窗口表 | 尾盘集中为主：决策侧 14:45-15:00 定加减仓；执行侧 batched_position_builder 14:50-14:57 挂单主窗+14:57-15:00 收盘竞价兜底；竞价铁律（9:15-9:20 可撤假象不参与/9:20-9:25 只看不动作）；开盘 30 分钟只执行计划单 |
| 03 价格锚定 | 盘口 | 限价为主（买=卖一+1 tick；突破买=突破价+0.5% 挂单）；市价仅应急（跌停逃命/强平） |
| 04 资金分配 | 顺位×置信度 | 多标的排序；资金不足按"置信度×顺位"加权；预留 10% 机动 |
| 05 打板专项 | 封单/流通盘、封单递减速率 | 三式：排板（>2% 才排）/扫板（只扫首封）/打回封；换手板>缩量板；撤单纪律=封单骤减 20% 立即撤 |
| 06 执行算法 SOR | 单额/流动性/暴露度 | EXA 六件选型（TWAP/VWAP/ICEBERG/IS/POV/ALT，algo_refs 全挂）；>500 万必拆；单笔≤盘口一档 50%；冲击预算 0.3%；参与率≤市场量 10-20% |
| 07 条件队列 | 价格/时间/指标/风控扳机 | 统一注册 tick 驱动，优先级 风控>卖出>买入（横切基础设施防各策略触发器打架） |
| 08 突破失败降级 | 收盘价 vs 首仓价/前低 | 双锚：连续 2 根 K 线跌破首仓价→暂停确认仓+止损评估；跌破前低（10 日回看）→暂停全部批次+止损卖出；**K≥3 次突破失败→强制清仓（最高优先级）** |
| 09 执行硬约束 | T+1/涨跌停/笼子/成本/资金/限额 | 五道全过才发单（成本模型实时估算：预期冲击+佣金不得吃掉预期收益 1/3） |
| 10 订单状态机 | 券商回报 | 状态流转+超时重试（节点散文：PendingNew>3 秒重发确认——**码面态名不同，见堵点 1**） |
| 11 部分成交 | 成交占比/价距 | <50% 且价远离=撤重挂；>50%=保留等剩余；撤改竞态=以券商回报为准+本地加锁 |
| 12 订单级预检 | 资金/持仓/风控/禁做清单/笼子 | 码面 gate 族：kill_switch_gate/live_env_gate/session_window_gate/snapshot_gate+verdict.rule_id；任一不过=拒单记录原因 |
| 13 容灾对账 | 本地订单簿 vs 券商委托 vs 成交 | 断线重连先全量对账再恢复；孤儿单立即同步评估；日终不平挂起次日竞价；RTO<5min |
| 14 成本反馈回写 | 成交回报 vs 发单前成本预估 | 滑点按方向拆冲击/时机/价差分量+质量三档（好/可/差）；按算法分桶累积喂选择器——**反馈环断链（见堵点 3）** |

## 三、判定用离散状态集合

| 状态集 | 离散值 | 真源 file:line | 判据-码面差异 |
|--------|--------|---------------|--------------|
| 订单生命周期 | 码面 **7 态**：PENDING/SUBMITTED/PARTIAL/FILLED/CANCELLED/REJECTED/EXPIRED；VALID_TRANSITIONS 显式封闭表（PENDING→{SUBMITTED,CANCELLED,EXPIRED}；SUBMITTED→{PARTIAL,FILLED,CANCELLED,REJECTED,EXPIRED}；PARTIAL→{FILLED,CANCELLED,REJECTED,EXPIRED}；终态无出边） | order_enums.py:52-63；order_manager.py:136-149 | **节点判据写"九态"（New/PendingNew/Accepted/…/Suspended，QMT 风格）**——码面无 New/Accepted/Suspended/PendingCancel 四态；节点散文">3 秒重发确认"超时策略未见码面对应。差异=判据先行未回写（S4 场景欠账） |
| 突破失败三档 | 暂停确认仓/暂停全部+止损/强制清仓 | breakout_failure_detector.py（batched_position_builder 双锚） | 一致 |
| 分批置信三档 | 70%/50%/30% | order_splitter.py | 一致（proposed 口径） |
| 执行算法六件 | EXA-TWAP/VWAP/ICEBERG/IS/POV/ALT-001 | ex_sor/core/algo_execution_selector.py | 一致（algo_refs 全挂） |
| 质量三档 | 好/可/差 | execution_quality_scorer.py | 一致 |
| 预检 gate 族 | kill_switch/live_env/session_window/snapshot+rule_id | pre_execution_checker.py:243-321 | 节点散文"五查"（资金/持仓/熔断/禁做/笼子）与码面 check_id 集合非一一对应——资金/持仓查在 snapshot_gate 与下游细则，禁做清单入口待核 |

## 四、子模块清单与实件校验

14/14 module_ref 在盘（零缺件）。EX 组交界（引用 M7 册，不重挖）：order_manager/pre_execution_checker/fill_handler/price_cage 的执行基建血肉=M7 已挖干 7/7 环节；order_splitter/pricing_policy/local_order_queue ALGO_FLOW 已外迁（2026-09-15）。

## 五、触发链与当日闭环证据

- **continuous 横切件**：L4-07 条件队列（tick 驱动）、L4-10 订单状态机、L4-13 容灾对账——事件驱动非 cron（宪法 §9.3）。
- **盘后**：L4-14 成本反馈回写（activation=postmarket）。
- **执行侧时序锚**：batched_position_builder 14:50-14:57 主窗+14:57-15:00 收盘竞价兜底（closing_session_decision 共件）。
- M5 交界地雷：order_daemon 建成未接线=全流通缺口（M5 册已记录，F82）；SimBridge 断链取证=S3 线索（M7/PR 组管辖）。

## 六、验证欠账清单（命中 13 件：L4 族 12 + cross 1——全组验证状态最好的一层）

| object_id | 对象 | 状态 |
|-----------|------|------|
| BT-P2-042 | L4 容器 | valid，testable=False |
| BT-P1-027/028 | 分批/时序 | **valid** |
| BT-P2-043~044 | 价格锚/资金分配 | valid |
| **BT-P2-045** | 打板执行 | valid；plan **冻结 2026-09-18**（exec_quality 土规 20/40bp，桶=order_type）；**caliber_note：现役 trade_log order_type 全 market 且无排板标记（60 件产物核查）→字段落地前按全量代理口径出数并披露"代理受限"，禁编造分桶**；缺口=known_data_gaps bt_trade_log_attribution_fields_missing |
| **BT-P2-046** | EXA 选型 | valid；plan 冻结同批；**caliber_note：trade_log 无 algo_id 归因字段**→同上代理受限 |
| BT-P2-047~053 | 条件队列/突破降级/状态机/部分成交/预检/容灾/成本反馈 7 件 | valid，但 **plan=None+plan_note"阈值未预注册"——confidence=valid 与验证计划缺失并存，标记-判据不对齐，复核时须核 c1_backtest.node_verdict 台账实际 verdict** |
| **BT-P0-003** | L4-09 成本模型（生死线三件套之一，cross：L4-09+P2-01/03+X-S2-01） | pending；plan 冻结 2026-09-12（exec_quality，cost_items=佣金+印花税+滑点+冲击+做T 额外，费率读实际账户配置禁硬编码） |

## 七、堵点与病灶

1. **订单九态判据-码面差异**（唯一 P0 级语义债）：节点散文 QMT 风格九态 vs 码面 7 态 OrderStatus——券商回报若真回 Accepted/Suspended 态，码面映射层缺失即状态机漏洞｜修法：a) 补券商态→内部态映射表（桥层，EX 组 F53 交界，1 天）+b) 节点注改写对齐码面（S4 场景 D 裁定）。
2. **trade_log 归因字段缺**（分桶考死穴）：order_type 全 market、无排板标记、无 algo_id——L4-05/L4-06 真判据无法出数，已登记 known_data_gaps｜修法：回测流水 schema 增字段（BT 组/M1 交界）+重放窗口。
3. **L4-14 反馈环断链（节点注自认，断链实证 2026-09-10）**：滑点分析器+质量评分器+算法选择器三零件全 production，但**选择器代码还没消费质量评分器**——闭环最后一米未接｜修法：选择器增评分输入（0.5-1 天，EX 组 F58 扩册交界）｜RL 执行=远期候选挂晨审（A 股 T+1/涨跌停约束需改造）。
4. **valid 标记与 plan 缺失并存**（BT-P2-047~053）：机械生成器疑按 exec_quality 出过数但未挂冻结判据——置信度可信度存疑｜修法：核 node_verdict 台账后补 plan 或降级标记。
5. **precheck"五查"散文与 gate 族码面口径漂移**：修法=节点注对齐码面 check_id 清单（0.5 小时，S4 场景）。

## 八、三态自审

**挖干可施工**（验证状态全组最佳；三件结构性欠账已定位：九态映射桥、归因字段、反馈环接线——均小施工，EX 组交界部分引用 M7/F58 不重复立工单）。

## 九、复核命令

```bash
sed -n '52,63p' src/zephyr/shared/contracts/enums/order_enums.py    # 7 态 vs 九态判据
sed -n '136,149p' src/zephyr/ex_core/order_manager.py               # VALID_TRANSITIONS
grep -n "check_id=" src/zephyr/ex_core/pre_execution_checker.py | head   # gate 族
grep -n "选择器代码还没消费" config/trading_decision_map.yaml         # L4-14 断链自认注
python -c "import yaml;d=yaml.safe_load(open('docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml',encoding='utf-8'));print([ (o['object_id'],o['confidence'],bool(o['plan'])) for o in d['objects'] if o['object_id'] in ('BT-P2-045','BT-P2-046','BT-P2-047','BT-P0-003')])"
```
