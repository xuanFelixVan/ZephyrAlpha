---
ttl: task_bound
title: 深度审查作业簿——KillSwitch编排器
owner: st-deeprev-20260918
created: 2026-09-18
reviewed: 2026-09-18
---

# 深度审查报告：KillSwitch编排器（K02）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/autonomy_core/kill_switch_orchestrator.py:259`（单例 `:726`，boot 接线 `src/zephyr/trading/boot_hooks.py:591-600,662`）
- 生产调用方（实测 grep）: 仅 `killswitch_response_levels.py`（而它自身 src 零消费方）+ boot_hooks 初始化；**零自动触发源**；`RiskManagerAgent`（agents/risk_manager_agent.py:260 的 kill 回调）全仓零实例化
- 测试文件: tests/autonomy/test_kill_switch_orchestrator.py（21 用例全绿，路由/传播/一致性/approver 覆盖好）
- 运行结果: `python -m pytest tests/autonomy/test_kill_switch_orchestrator.py -q` → 21 passed（Python 3.12.8）

## 1 对象快照

- **范围**：编排器本体（trip/reset/route_incident/is_tripped/check_consistency/_trace）+ 五个适配器（system/skills/trading/rollback/capacity）与其被包装开关的接线状态。包装对象本体（security/access_control/kill_switch.py、trading_kill_switch.py 等）只审与本编排相关的状态承载与消费面。
- **排除项**：rollback KillSwitchManager / capacity fuse / skill_kill_switch 的内部实现细节（不在 9 对象清单）。
- **材料缺项声明**：运行时证据包未取；`.runtime/audit/kill_switch_orchestrator.jsonl` 实测不存在（=编排动作从未在生产发生，兼作证据）。
- **测试覆盖概况**：21 用例质量好（传播失败检测/复位门位/兜底路由均有）；缺 is_tripped fail-open 行为断言与真实 trading 域闭环（因生产根本无消费方，测试不可能覆盖不存在的东西）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | （无数学对象；FSM 审查）系统级 trigger 幂等（TRIPPED 再 trigger→NO_ACTION）；未知 level/事故类型 fail-visible 收 errors；边界处理完备 | kill_switch.py:293-296；kill_switch_orchestrator.py:368-376,463-470 | 已查无 | 读码+已有测试 test_route_unknown_kind_fails_closed |
| B | 上游适配对象质量：`KillSwitchLevel(scope)` 对非法 scope 抛 ValueError→收 errors（fail-visible）；rollback scope 无冒号时默认按 L2_SKILL 解析——传普通词被误绑定 skill 语义 | kill_switch_orchestrator.py:168,204-207 | P3 | trip("domain","rollback:foo") 看解析结果 |
| C | **trading 五级开关死端**：trading_kill_switch 的 get_switch/active_switches/KillSwitchLevel 在 src 生产代码中除编排器适配器外零消费（下单路径闸=DefaultRiskValidator.kill_switch_active+pre_execution gate，另一套承载）→ trip("domain","trading") 翻的旗没人读 | grep "KillSwitchLevel\|active_switches\|get_switch(" src/ 非测试零命中（除编排器与本体） | **P0** | `grep -rn "active_switches" src/ --include=*.py \| grep -v test` |
| C | **五域编排面板零使用**：自动触发源零（RiskManagerAgent 零实例化、response_levels 零消费、无事件订阅调 trip）；人工使用证据零（审计 jsonl 不存在）；boot_hooks 只初始化不触发 | boot_hooks.py:591-600；`.runtime/audit/kill_switch_orchestrator.jsonl` 不存在；grep RiskManagerAgent 实例化=0 | **P1** | `ls .runtime/audit/`；`grep -rn "RiskManagerAgent(" src/ scripts/` |
| C | 系统级总开关有真实消费方（daily_gate_snapshot.py:227 / pipeline_events.py:155 / genesis_bootstrap.py:241 / boot_hooks RBAC 钩子）——系统级域活、trading 域死，编排在 C 轴呈现半接线态 | 见锚点 | （并入上两条计） | 各 grep |
| D | kill switch 状态承载第 5/6 处：编排器五域 + K01 四处（validator/stop_loss/trading_kill_switch/DrawdownStateMachine）——缺陷模式 #4 双份承载全景；同项目存在**两套互不相通的"交易熔断"**（trading_kill_switch 注册表 vs DefaultRiskValidator kill_switch） | kill_switch_orchestrator.py:4；default_risk_validator.py:67 | **P1**（与 K01 D 轴合并计数） | 画承载清单对拍写读入口 |
| E | **假阳性过关（资金事故假处置）**：route_incident("funds") → trading 域先行 → 5 级旗全翻成功 → success=True 直接 return，不兜底系统级；而真实下单路径根本不读这些旗 → 资金事故被"成功处置"而交易照跑 | kill_switch_orchestrator.py:436-445 + C 轴死端证据 | **P0** | trip("domain","trading") 后走 start_paper_session 下单路径→完全不受影响 |
| E | 假阳性过关②：is_tripped 查询面 fail-open（本体异常→False+warning），头注自认；今日无下单闸消费故爆炸半径受限，但任何未来接线者会拿到"异常=未熔断"语义 | kill_switch_orchestrator.py:476-493 | P2 | mock adapter.is_tripped 抛异常→返回 False |
| E | 静默失败：默认注册失败仅 warning（boot 链吞掉）；审计写失败仅 warning（"动作仍生效"）——熔断动作可无审计发生 | kill_switch_orchestrator.py:291,719-720 | P2 | mock open 抛 OSError 调 trip→动作生效无痕 |
| E | 重复触发：system/trading 域幂等（test_trigger_idempotent）；重复 trip 不产生双副作用 | tests/trading/test_trading_kill_switch.py:128 | 已查无 | 已有测试 |
| E | 断了没人知道：check_consistency 能检测"系统级 TRIPPED 而 trading 域物理未生效"，但生产无定时巡检调用（唯一消费=未接线的 response_levels） | kill_switch_orchestrator.py:495-528；grep check_consistency 生产调用=0 | P2 | `grep -rn "check_consistency" src/ scripts/` |
| E | 触发状态持久化：**系统级开关纯内存**（无 state_store/jsonl 导入），重启即 NORMAL；对比 K01 validator 有持久化——同一项目两种口径 | kill_switch.py:38-46（imports 无持久化）；:150-160（内存字段） | **P1** | trip 后重启进程（或新解释器 get_kill_switch()）→is_global_tripped()=False |
| E | 时序攻击：本对象无高频判定路径，不适用；传播窗口内（system 已翻、domain 未翻）is_tripped(domain) 可能短暂 False——支配语义在查询面补齐（system TRIPPED 时域级查询恒 True），窗口已闭合 | kill_switch_orchestrator.py:486-487 | 已查无 | 读码 |
| D | 复位门位：approver 仅要求非空字符串，无身份核验（与宪法 §9.11"Owner 门位经正式通道"口径靠流程保证，非机械） | kill_switch_orchestrator.py:394-403 | P3 | reset("system","global",approver="任意人")→成功 |
| A | capacity 域在系统级传播中被自动 `trigger_shutdown()`——语义为"关停服务"的重副作用无二次确认，混在传播循环里执行 | kill_switch_orchestrator.py:244-246,555-561 | P3 | trip("system") 观察 capacity 副作用 |

## 3 SOTA 对照

- **两级 kill switch（系统总闸+域分闸+传播一致）**：与交易所/监管对算法交易 kill 功能的分级要求同构（MiFID II RTS 6 要求投资公司算法交易具备 kill switch 能力；中国程序化交易新规要求"一停二看三通过"式应急机制）。设计模式**对等已有**。
- **高频认定阈值 vs 代码注释口径**：沪深北交易所《程序化交易管理实施细则》（2025-07-07 施行，上交所官网 [细则原文](http://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20250612_10781696.shtml)，发布方=上海证券交易所，2025）认定高频=**每秒申报/撤单 ≥300 笔 或 单日 ≥2 万笔**（央广网 [报道](https://www.cnr.cn/jrpd/mxdj/20250707/t20250707_527248680.shtml)，2025；新华网 [报道](http://www.news.cn/money/20250407/3142c6f5fd1d4b1ebd9eb91910befc5e/c.html)，2025）。K01 清算链注释"**A 股 2026 新规限频 15 笔/秒**"与法规口径不符——15 笔/秒是内部保守值，非法规限额；注释把内部参数标注成法规要求=口径漂移（K01 已记，本报告给出来源）。**结论：限频值本身安全（远低于阈值），注释须改**。
- 熔断状态持久化（crash-only）业界对标：K01 已引 NautilusTrader；本对象系统级开关未做——立卡候选（复用 JsonStateStore 即可，改造点≈20 行）。

## 4 缺陷清单（按严重级排序）

1. **[P0] 资金事故响应假动作**：route_incident("funds"/"trading") 翻 trading 五级旗后即返回 success，无任何下单路径消费这些旗；真熔断载体（DefaultRiskValidator+编排闩+pre_execution gate）完全未被触达。现状→ designated 资金事故通道失效但自报成功。影响→资金事故时交易不停止；爆炸半径=全账户。建议修法→_TradingSwitchAdapter 桥接到 DefaultRiskValidator（trip 时调 validator.trigger_kill_switch + 置 KILL_SWITCH_STATE_NAMESPACE），或 route_incident("funds") 直接走 K01 的 _engage_kill_switch 链。验证法→trip 后调 DefaultRiskValidator.validate_order 断言 HALT（当前不拦）。
2. **[P1] 系统级总开关无持久化**：重启即解除，genesis/daily_gate/pipeline 四个消费面在重启后全部看到 NORMAL。建议→get_kill_switch 初始化时读 JsonStateStore（同 K01 机制）。验证法→trip→重建解释器→is_global_tripped。
3. **[P1] 五域编排面板整体零接线零使用**：无自动触发源、无人工使用痕迹、审计文件不存在——"五域总闸"目前是消防演习道具。建议→要么把 route_incident 接入真实事件源（RBAC 钩子/风控事件总线），要么在注册表标注"运维手动面板（未接自动源）"防止误以为有自动熔断。验证法→审计文件 mtime 与 grep 触发源。
4. **[P2] is_tripped fail-open + 审计可静默丢失 + check_consistency 无巡检**（E 轴三条合并）：任何未来把 is_tripped 用作下单闸的接线都会继承"异常=放行"。建议→is_tripped 增加 fail 计数与连续失败告警；check_consistency 挂入 boot 后定时任务或每日门禁快照。验证法→异常注入+断言告警。
5. **[P3] approver 无核验 / capacity 自动关停副作用 / rollback scope 误绑定 L2_SKILL / （跨对象）"15 笔/秒"注释口径漂移**：低危打包。验证法→各自单测/注释修正。

## 5 挂起疑问

1. trading_kill_switch 五级注册表的设计消费方是谁（MOD-INF-016 头注与 QMT 适配器是否曾规划读取）？若已废弃，按规范预算净零应申请退役或与 DefaultRiskValidator 合并（旁系合并建议，转挖矿节点）。
2. killswitch_response_levels 的目标用户是 Owner 控制台还是 Agent？src 零消费是否为已知状态（是否登记过 tracker）？
3. `.runtime/audit/` 的 TTL/清理策略是否会清掉熔断审计记录（宪法 §9.4 对 .runtime 的定位是暂存区）——熔断审计是否应改道永久区？

## 6 完备性自评

- 六轴全查：A/B/C/D/E/F 均有结论；数学类子问 N/A 已注明；E 轴五问逐条有结论。
- 长尾清单：① rollback KillSwitchManager 与 capacity fuse 本体实现未深审（不在 9 对象清单，仅审了适配面）；② skill_kill_switch 本体未审；③ boot_hooks 五域初始化失败表的运维可见性（是否有人看 warning）未核实；④ 系统级开关的触发器注册面（register_trigger/DEFAULT_TRIGGERS 的阈值合理性）未审——属 RBAC/Agent 治理域，非钱路径。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P0 route_incident('funds')五级旗无下单路径消费=资金事故假处置+系统级开关纯内存重启即丢: 挂起登记(接线+持久化裁定)。晨报置顶。
