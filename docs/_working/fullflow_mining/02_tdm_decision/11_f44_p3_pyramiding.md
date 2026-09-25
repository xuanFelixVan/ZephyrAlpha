---
ttl: task_bound
title: F44 P3 加仓决策——TDM 持仓流 P3 环节册（TD-B 后半）
session: st-ailayer-fullflow-td-b
date: 2026-09-25
status: mined
group: TD-B（F43-F52）
---

# F44 P3 加仓决策（TDM-P-P3 + P3-01..04）

> **一句话**：浮盈仓金字塔加仓：资格四重门→金字塔三规则→量级风险核算→时点执行，四步流水线；核心纪律=只加浮盈仓（补亏损仓=扩大错误，BM-BUY-08 红线）。
> **上游**：P1-06 体检动作清单（可加仓）、P2-03 做T闭环（edge feed）、L1-AGG 六段。**下游**：TDM-E-L4 建仓执行件（P3-04 复用下单流）。

## 一、环节定义与边界
- 只管存量浮盈仓的加仓，新开仓归 E 流 L4；euphoria 段无加仓权限（只卖不买，取严）。
- P 流三空白之三=金字塔规则（69 号 §2.26 参数真源）；P3-01/P3-02 红节点（编排缺口），C9/C10 施工（gw-tdm-20260909）已把 module_ref 落到 pyramiding_rules.py。

## 二、状态机血肉
| 节点 | 判定轴 | 离散状态/规则 |
|------|--------|--------------|
| P3-01 加仓资格门 | 四重门全过 | ①只加浮盈仓（现价>成本）②情绪段权限（仅 ignition/expansion）③策略亲和 strategy_affinity>0 ④非熔断禁加期（=X-R1-01 L1 及以上持续期间，M-36 收口统一定义）。D94 终裁：单票默认≤10%、凯利波段≤3%、earned 豁免≤20% 须本节点显式留痕豁免理由；D110：超跌反转信号仅限新信号开仓，严禁给套牢仓补仓 |
| P3-02 金字塔规则 | 三规则+停止条件 | 递减（首加占剩余预算 50% 逐次减半）+阶梯（较上次买价涨幅≥2.5-3% 才加）+限次（≤3）；跌破上次加仓价=停止后续计划；参数全 proposed；Case B 总 dollar risk 不超首仓风险预算。D58 欠账：批次止损合并风险预算制/批次账本"可卖时点"字段（T+1 FIFO 只能卖旧批）/涨停价加仓自动切排板模式（封单流通比>3% 门，m-16 与封成比分母不同勿混用）/批次计划持久化先于下单+恢复复验门 |
| P3-03 量级与风险核算 | 四轨融合+风险恒定 | 仓位引擎（风险预算/波动率目标/策略置信/现金约束）定加多少；加仓后总风险额≤首仓风险预算（止损等比上移）；加仓完成全部止损上移保本 |
| P3-04 时点与执行 | 时点二选一 | 缩量回调守住支撑即时加 ∨ 尾盘窗口（14:45 后，BM-PLAN-02 明日高开概率>70%）；下单复用建仓执行件（→E-L4 feed 边）；未成交不追价，次日重走资格门 |

## 三、六向台账
- **上游输入**：P1-06（daily feed）、P2-03（daily feed）、L1-AGG（daily state）。
- **下游消费**：P3-04→TDM-E-L4（intraday feed）。
- **自动化触发**：**零**——pyramiding_rules.py 唯一引用=position/core/__init__.py 导出，grep 全仓零生产调用方。
- **真源与注册表**：trading_decision_map.yaml:2982-3109；MOD-POS-027（pyramiding_rules 241 行）/MOD-POS-001（position_sizing_engine 944 行）/MOD-POS-010（position_limit_enforcer 387 行）均实测在盘；28 号+69 号 §2.26 doc_ref 在档（docs/_working/archive/2026-09/design_memos/）。
- **门禁与质量尺**：ai_autonomy P3-01/02/03=auto、P3-04=paper；RLM-POSITION-004/006/009/013/021+RLM-CONCENTRATION-001+RLM-KILL-SWITCH-006。
- **当前运行状态**：**红（未运行）**——三模块全在盘+测试锚 tests/position/test_pyramiding_rules.py，但无编排体、无调度、无生产调用。

## 四、子模块清单
| 模块 | 行数 | 消费方 | 状态 |
|------|------|--------|------|
| position/core/pyramiding_rules.py（MOD-POS-027） | 241 | 仅包 __init__ 导出 | 纯库（红节点承载） |
| position/core/position_sizing_engine.py（MOD-POS-001） | 944 | （P3-03 锚；四轨融合体） | 在盘，编排缺 |
| position/core/position_limit_enforcer.py（MOD-POS-010） | 387 | （P3-04 硬约束预检） | 在盘，编排缺 |
| tests/position/test_pyramiding_rules.py | — | 测试锚 | 在盘 |

## 五、堵点与病灶
1. **P3 全链零编排**（根因=P 流三空白之编排面；修法：与 P2 编排同批立"持仓流动作执行编排"工单，P3-01 资格门消费 P1-06 动作清单+X-R1-01 熔断态；量级 2-3 天；本车道可修）。
2. **金字塔参数全 proposed 无验证**（BT-P3-015/016 对象 plan=null 阈值未预注册禁跑；修法：批次决策点冻结验收阈值后走 agg_discrimination）。
3. **D58 四件欠账未清**（批次止损/可卖时点/排板切换/持久化复验）——均未落码，随编排工单一并立项。

## 六、提速与合并机会
P3-04 复用 E-L4 建仓执行件是地图既定口径——禁止再造加仓专用下单器；P3-01 的熔断禁加期直接读 X-R1-01 状态机输出，禁复算。

## 七、自审闸三态
**挖干可施工**（血肉逐节点+模块实测+测试锚+欠账清单齐）。

## 八、复核命令
```bash
grep -n "node_id: TDM-P-P3" config/trading_decision_map.yaml
grep -rln "pyramiding_rules" src/zephyr --include="*.py" | grep -v __pycache__   # 仅 __init__=零生产调用
python -c "import ast;ast.parse(open('src/zephyr/position/core/pyramiding_rules.py',encoding='utf-8').read())" && echo syntax-ok
```
