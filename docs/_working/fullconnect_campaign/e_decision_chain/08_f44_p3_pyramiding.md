---
ttl: task_bound
title: F44 P3 加仓决策——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f44-p3-pyramid-20260927
---

# F44 P3 加仓决策——挖干案卷

> 一句话：浮盈仓金字塔加仓：资格四重门→金字塔三规则→量级风险核算→时点执行；核心纪律=只加浮盈仓（补亏损仓=扩大错误，BM-BUY-08 红线）；euphoria 段无加仓权限（只卖不买，取严）。节点组=TDM-P-P3+01..04 共 5 节点（今日 yaml P 段机数 P3=5，零漂移）。总册 built｜P1｜T6；上游 P1-06/P2-03/L1-AGG，下游 TDM-E-L4（P3-04 复用下单流）。
> **本卷核心发现（册引+今日双源复核）：P3 全链零编排零生产调用——红（未运行）。**

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | P1-06 体检动作清单（可加仓，daily）、P2-03 做T闭环（feed）、L1-AGG 六段（仅 ignition/expansion）；X-R1-01 熔断禁加期（M-36 收口统一定义） |
| ②数据原料 | 现价 vs 成本（浮盈判定）；strategy_affinity；69 号文 §2.26 金字塔参数真源（递减 50% 逐次减半/阶梯 2.5-3%/限次≤3，全 proposed）；风险预算四轨（风险预算/波动率目标/策略置信/现金约束） |
| ③状态输出 | 资格四态判定+加仓批次计划（Case B 总 dollar risk≤首仓风险预算）+加仓后全部止损上移保本 |
| ④下游消费 | TDM-E-L4 建仓执行件（feed 边，复用下单流——禁再造加仓专用下单器，册引 §六）；D94 终裁留痕豁免（单票≤10%/凯利波段≤3%/earned≤20% 显式留痕豁免理由） |
| ⑤自动化触发 | **零**——pyramiding_rules.py 唯一引用=position/core/__init__.py 导出（册引 grep；今日独立复核成立：全仓命中仅 pyramiding_rules.py 自身+__init__.py 2 文件） |
| ⑥缺口债 | D58 四件欠账（批次止损合并风险预算/批次账本可卖时点 T+1 FIFO/涨停加仓切排板模式 m-16/批次计划持久化先于下单+恢复复验门）；BT-P3-015/016 plan=null 禁跑 |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/position/core/`（29 件实扫）三核心：pyramiding_rules.py（MOD-POS-027，241 行，红节点承载）、position_sizing_engine.py（MOD-POS-001，944 行，P3-03 四轨融合体）、position_limit_enforcer.py（MOD-POS-010，387 行，P3-04 硬约束预检）。
- 测试锚：tests/position/test_pyramiding_rules.py（册引在盘）。
- P 流三空白之三=金字塔规则（69 号 §2.26 参数真源）；C9/C10 施工（gw-tdm-20260909）已把 module_ref 落到 pyramiding_rules.py（册引）。
- 关联：config/trading_decision_map.yaml:2982-3109（P3 组+4 节点血肉）；28 号+69 号 §2.26 doc_ref 在 docs/_working/archive/2026-09/design_memos/（册引）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| pyramiding_rules.py | **纯库挂机** | 今日 grep 全仓 2 文件（自身+__init__）=零生产调用（复核成立）；语法在盘（册引 ast.parse 通过） |
| position_sizing_engine.py | **半接线** | 在盘；P1-06 裁决链经 allocation_orchestrator 装配体间接可达（F42 卷已证接线），但 P3-03 语义调用无编排 |
| position_limit_enforcer.py | **域内接线（约束面）** | RLM-POSITION 家族约束消费面在册（册引 §三）；P3-04 时点执行无触发面 |
| P3-04→E-L4 feed 边 | **设计态** | 地图既定口径；无实际调用证据 |

**骨架勘误（登记待 D 线）**：
1. **总册 F44 状态"built"降格建议**：三模块全在盘+测试锚在盘（built"实件"面成立）但无编排体无调度无生产调用（册引"红（未运行）"+今日复核）——实际四态="实件 built/编排 missing"，与 F43 同型。建议总册行加注（同 F42/F43 处置路径，裁-5 同窗）。
2. f44 册头"P 流三空白之三"与 f43 册"三空白之二"（做T编排）、F42 卷"体检编排悬空"（之一）三处同根因=P 流编排面整体缺位——建议合并立"持仓流动作执行编排"单一工单（f44 册 §五-1 已建议，本卷联署）。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G44-1 | P3 全链零编排 | 与 P2 编排同批立"持仓流动作执行编排"工单：P3-01 资格门消费 P1-06 动作清单+X-R1-01 熔断态直读（禁复算）；量级 2-3 天 | **P0** |
| G44-2 | 金字塔参数全 proposed 无验证（BT-P3-015/016 plan=null） | 批次决策点冻结验收阈值后走 agg_discrimination | P1 |
| G44-3 | D58 四件欠账未落码 | 随编排工单一并立项（批次止损/可卖时点/排板切换/持久化复验） | P1 |
| G44-4 | euphoria 禁加仓权限的引擎侧硬约束位 | 资格门②情绪段权限已有查表语义（册引）；编排落地时加单测钉死 | P2 |

## 五、自审闸三态

**挖干可施工**（血肉逐节点+模块实测+测试锚+欠账清单齐；零编排双源复核成立）。

### 待裁
- 持仓流编排工单（P2+P3 同批）排期与载体（挂 dloop 链 vs 独立编排件）——归 Owner 排期裁定。

## 六、复跑命令

```bash
grep -n "node_id: TDM-P-P3" config/trading_decision_map.yaml   # :2612/:2982 起
grep -rln "pyramiding_rules" src/zephyr --include="*.py" | grep -v __pycache__  # =2 文件（仅导出）
python -c "import ast;ast.parse(open('src/zephyr/position/core/pyramiding_rules.py',encoding='utf-8').read())" && echo syntax-ok
ls src/zephyr/position/core/pyramiding_rules.py src/zephyr/position/core/position_sizing_engine.py src/zephyr/position/core/position_limit_enforcer.py
```
