---
ttl: task_bound
title: F47 R1 应急保命——TDM 风控横切环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F47 R1 应急保命（TDM-X-R1 + R1-01..03，横切全流）

> **一句话**：系统的'拔电源'：熔断五级状态机（判定）→梯度减仓（处置）→护盘白名单窄门（proposed 休眠）；kill switch 常驻任何档位不可移除，任何环节可触发。
> **上游**：F59 风控限额/F60 回撤 NAV、E-L0 broadcast、L4-09 成本（经 BT-P0-003 关联）。**下游**：全流 broadcast（P2-01 停做T/S1-06 强清/S2 执行/C2-01 聚合/P3-01 禁加期）。

## 一、环节定义与边界
- M-36 收口：熔断从模糊词变等级表（判定=R1-01 离散状态机，D108 设计原则）；梯度减仓=R1-02；护盘窄门=R1-03（proposed，回测验证前不生效=整节点休眠）。
- 与 F60/F61 分工：drawdown 全家桶与 kill switch 三实例的工程面归 M7/RC 车道（已挖干）；本册只管 TDM 节点判定语义与消费面。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| R1-01 熔断分级判定 | 组合日盈亏+组合回撤双轴（与六段情绪市场轴正交） | L0 正常/L1 警戒（日亏≥2% 禁加仓）/L2 禁开仓（日亏≥4%，白名单窄门开启）/L3 减仓（日亏≥6% 梯度减仓）/L4 保命（回撤≥25% 或生死线：清仓+Owner 人工接管）；迟滞解除：当日无新低+修复当日跌幅 50% 才降一级，禁 V 型回满；L4 仅 Owner 人工解除回 L0（fail-closed）；数据断流→维持当前级不降级（D103）；"熔断禁加期"统一定义=L1 及以上持续期间（P3-01 门④消费） |
| R1-02 熔断期减仓处置 | 梯度非一刀切 | L3 减仓顺序：重亏仓→高波动仓（ATR 大）→压舱石保留；减仓指令路由 P2-04 执行；恢复=回撤修复 50% 后逐级加回风险预算；L4 全清走 S1-06 绕过通道（既有边不动）；fallback=减仓通道故障降级 S1-06 单仓强清 |
| R1-03 护盘白名单窄门 | 三重门（D114 proposed 休眠） | ①L2/L3 状态 ②D110 超跌反转信号或国家队明牌（ETF 天量/官方增持）③金字塔分批（首笔 1/3 预算）；白名单：宽基 ETF（300/500/1000/红利）优先、银行高股息次之；仓位=D107 尾部弹药预算，上限总资金 5-10%；政策底≠市场底（滞后 40 天~半年）；fallback=尾部弹药预算未启用→整节点休眠 |
| R1 hub 治理面 | 档位豁免+人工通道 | kill switch 任何 ai_autonomy 档位下真实执行不随 paper（I-01/M-58）；复位=Owner 人工（fail-closed 重启后保持 HALTED，I-05）；风控心跳失联→默认降级安全态（I-06）；UP-5 尾部对冲建议通道（CVaR(5%)<-3% 阈值冻结禁挪门柱→DAL-TAIL-HEDGE trial 建议非指令，D107 回测验证前休眠）；M-55 欠账：paper 升档前 Owner 手动接管正式入口节点缺位（当前仅 kill switch 人工解除一条人工通道）；四层止损作用域×节拍（m-11）：单票连续价/做T价差时间/sleeve 月度净值 5% 减半 7.5% 冻结/组合日度+回撤 |

## 三、六向台账
- **上游输入**：NAV/回撤数据（F60/F63）、E-L0 broadcast、RLM-KILLSW/KILL-SWITCH×4+THD-DRAWDOWN×3。
- **下游消费**：边实测 6 条出边（X-S1-06 强清/X-S2 broadcast/P2-01 停做T/P2-04 减仓/C2-01 聚合/P3-01 经"禁加期"语义）+R1-02→P2-04、R1-03→E-L4。
- **自动化触发**：drawdown_state_machine（773 行）被 daily_gate_snapshot（strategy_pipeline 日链）、drawdown_session_persistence（会话持久化）、defensive_asset_whitelist（R1-03 自身）消费——判定件在 paper 日链内运行；**无盘中 continuous 扫描常驻**（M7/RC 车道领域，本册登记）。
- **真源与注册表**：trading_decision_map.yaml:3156-3289；DAL-CIRCUIT-5（production，code_ref=drawdown_state_machine.py）；algo_flow yaml 外迁件在盘（_domain_risk/algo_flow/drawdown_state_machine.yaml/drawdown_liquidation_guard.yaml）。
- **门禁与质量尺**：R1-01 auto/R1-02 paper/R1-03 paper；R1-01 note_confirmed 2026-09-16（消费方 AST 实测零在网后回填 [CONSUMERS]——判定件生产消费为空的书面证据）。
- **当前运行状态**：**黄**——判定件落码+测试在盘（tests/risk/test_drawdown_state_machine.py）+paper 日链消费；盘中保命扫描无常驻载体；R1-02 drawdown_liquidation_guard(209 行)**零外部消费方**（grep 实测）；kill switch 持久化待裁（M3 遗留，Owner 门位）。

## 四、子模块清单
| 模块 | 行数 | 消费方 | 状态 |
|------|------|--------|------|
| security/access_control/kill_switch.py（MOD-INF-018） | 341 | M3 已挖（持久化待裁） | 引用 M3 结论 |
| risk/core/drawdown_state_machine.py（MOD-RK-049） | 773 | daily_gate_snapshot/session_persistence/defensive_whitelist | wired（paper 日链） |
| risk/core/drawdown_liquidation_guard.py（MOD-RK-050） | 209 | 零外部消费 | 纯库挂机 |
| position/core/defensive_asset_whitelist.py（MOD-POS-026） | 327 | 消费 drawdown_state_machine | 在盘（整节点休眠语义） |
| risk/core/drawdown_broker_side_stop.py | 241 | （F60 面，M7 管） | 引用 |
| pf_alloc/core/tail_hedge_signal.py（DAL-TAIL-HEDGE trial） | 71 | UP-5 建议通道 | trial 休眠 |

## 五、堵点与病灶
1. **R1-02 减仓执行编排零消费**（guard 判了没人执行；修法=接 P2-04/X-S2 编排工单，与 F43/F46 同批；本车道可修）。
2. **盘中 continuous 保命扫描无常驻**（R1 判定轴=组合日盈亏需盘中 NAV 流；当前只有日链快照；修法归 RC/M7 车道+M5 常驻族，须登记 process_reaper_keep）。
3. **M-55 人工干预入口缺位**（paper 升档前无正式 Owner 接管节点——治理面欠账，Owner 门位）。
4. **R1-03 数据地基缺**（ETF 天量检测需 ETF 日线登记 D109；tail_hedge 回测验证未做——休眠是正确态，勿提前激活）。

## 六、提速与合并机会
熔断态是全流共享单点真源——P3-01/P2-01/C2-04 等消费方应读同一 R1-01 状态输出，禁各自复算日亏%；R1-01 与 F60 drawdown_state_machine 是同一文件，勿双登记。

## 七、自审闸三态
**挖干可施工**（判定语义/边/治理豁免/验证欠账齐；工程面归属 M7/RC 已划清）。

## 八、复核命令
```bash
grep -n "node_id: TDM-X-R1" config/trading_decision_map.yaml
grep -rln "drawdown_liquidation_guard" src/zephyr --include="*.py" | grep -v __pycache__   # 仅自身=零消费
grep -c "" src/zephyr/risk/core/drawdown_state_machine.py
```
