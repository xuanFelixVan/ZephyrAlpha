---
ttl: task_bound
title: F51 币圈决策骨架——TDM-C-L1..L4 第二实例环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F51 币圈决策骨架（TDM-C-L1..L4，market=crypto 第二实例）

> **一句话**：同 schema 第二实例（D2.5），V0 骨架空壳——四节点 module_ref 全空、red_reason=not_built，"等 A 股链路验证后移植"是地图原文设计意图，非意外缺失。
> **上游/下游**：无外部边——仅 L1→L2→L3→L4 三条内部 sequence（edge 实测），与 A 股四流零耦合。

## 一、环节定义与边界
- 四节点：C-L1 大盘总闸（BTC 200 日线+ALT/BTC 汇率）→C-L2 赛道选择（资金流排名前 3，A 股板块层弱化版）→C-L3 币对选择（市值+流动性+7 日动量，深度不足剔除）→C-L4 买卖点（7×24 无 T+1 无涨跌停，ATR 2×移动止损）。
- 全部 activation=continuous、point=持续、proposed 语义未挂任何 strategy_mount。

## 二、状态机血肉
| 节点 | 判定轴（设计态文字，零代码） | 缺什么才算 built |
|------|------------------------------|------------------|
| C-L1 | BTC 站稳 200 日线且斜率向上=趋势档；ALT/BTC 上行=山寨季进攻档；BTC 破位收总闸 | BTC 日线源+状态机代码+仓位档表 |
| C-L2 | 赛道资金流轮动排名前 3 | 赛道分类表+资金流源 |
| C-L3 | 市值+流动性+7 日动量排名；深度不足剔除 | 交易所行情源+深度口径 |
| C-L4 | 突破确认/回踩两类时点；2×ATR 移动止损 | 交易所接入+订单面（全链最大件） |

## 三、六向台账
- **上游输入**：无（零入边）。
- **下游消费**：无（零出边）。
- **自动化触发**：零。
- **真源与注册表**：trading_decision_map.yaml:4172-4248；回测欠账 BT-P3-048..051 四对象（crypto 另册语义，priority_legend" crypto 另册"）plan=null。
- **生态实测（2026-09-25）**：src/zephyr 无任何 crypto 交易模块；仅有 data/calendar/crypto.py（7×24 日历，供时间轴）+frontend/dashboard/web/features/cryptomarket（展示面）+C3-05 schema 预留（funding/basis 归因行 A 股实例恒 0、UTC 日历日——schema 不分裂的预留已做）。
- **门禁与质量尺**：validation runner 明确排除 TDM-C-*（_L4_EXCLUDE_PREFIX="TDM-C-"，无 A 股成交流水）。
- **当前运行状态**：**红（未运行，且属有意空壳）**。

## 四、子模块清单
| 资产 | 位置 | 状态 |
|------|------|------|
| 日历 | src/zephyr/data/calendar/crypto.py | 在盘（唯一真身） |
| 前端展示 | src/zephyr/frontend/dashboard/web/features/cryptomarket | 在盘（展示面） |
| TDM-C-L1..L4 节点 | trading_decision_map.yaml:4172-4248 | 登记态（module_ref 全空） |
| BT-P3-048..051 | backtest_backlog.yaml | plan=null 未预注册 |

## 五、堵点与病灶
1. **全链零基础设施**：无交易所接入/无 WS 行情/无订单面/无钱包——移植成本≈重建一条执行链，非"复制 A 股四流"。
2. **与内收判据的张力**（宪法 §四.2 w5_1：零触发零消费→退役候选）vs markets 声明=Owner D2.5 拍板保留——**本车道不裁，登记待裁**。
3. A 股链路尚未全通（见 10-17 册：S/P 流零编排）——"等 A 股验证后移植"的前置条件本身未达成。

## 六、提速与合并机会
若 Owner 决定保留：最小实件化路径=复用 validation runner 的 _L4_EXCLUDE_PREFIX 排除机制+data/calendar/crypto.py 时间轴+C3-05 的 funding/basis schema 预留，先做 C-L1 单节点 paper 判定器，禁四节点齐上。

## 七、自审闸三态
**待裁**（问题：TDM-C-L1..L4 空壳保留还是退役？已试路径：内收判据 w5_1 命中（零触发零消费），但 markets: [cn_a, crypto] 为 Owner D2.5 拍板+地图原文"等 A 股链路验证后移植"表设计意图；选项 A=保留空壳+本册登记（0 成本，容忍净零审计噪音）；选项 B=退役四节点保留日历与 schema 预留（净零合规，未来重建成本=重登记）；选项 C=最小实件化 C-L1 paper 判定器（违背"等 A 股验证"前置，不建议）。建议=A，待 Owner 晨报裁定。登记入本目录 pending_rulings.md）。

## 八、复核命令
```bash
sed -n '4172,4248p' config/trading_decision_map.yaml
grep -n "_L4_EXCLUDE_PREFIX" src/zephyr/trading/validation/runner.py
find src/zephyr -type d -iname "*crypto*" | grep -v __pycache__
```
