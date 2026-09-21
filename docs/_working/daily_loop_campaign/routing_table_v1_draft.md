---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-GAP4-ROUTING
completes_when: Owner 批准映射口径并授权 config 落地（本稿仅设计，不改 config）
---

# 路由表 v1 设计稿（缺口④）——状态→策略→因子

> 定位：设计稿。config 落地（trading_decision_map.yaml / 新路由注册表）= **Owner 门位**，
> 本班不落 config（§3 段B④ 明令）。原料=TDM 状态矩阵（只读）+ bizmine 判定 + PP-001。

## 1. 待闭合接口：六段↔五态映射（对账发现的未定义接口）

蓝图编排器/decision_daily 用**六段**（capitulation/accumulation/ignition/expansion/euphoria/distribution），
台账表1 盘中跟踪件用**五态**（低迷/防御/震荡/进攻/亢奋）。全仓无映射定义（蓝图审计矛盾点②）。

### v1 提议映射（机械、保守权向：五态→六段为多对一收敛，六段→五态取保守代表）

| 五态（intraday_l1_tracker payload.state_label） | 提议映射六段 | 理由（第一性） |
|---|---|---|
| 低迷 | capitulation | 冰点=投降段尾部，预算带 0-10% 一致 |
| 防御 | distribution | 防御=只守不攻，与 distribution"只卖不买/空仓"保守侧对齐 |
| 震荡 | accumulation | 底部换手蓄势；预算带 20-30% 温和敞口 |
| 进攻 | expansion | 主升段，预算带 50-70% |
| 亢奋 | ignition → euphoria 过渡带 | 需二阶信号（量速/宽度斜率）拆分：量增价升=ignition，量价背离=euphoria；v1 简化=**映射到 ignition**（euphoria 需 Owner 拍板阈值，见门位清单） |

反向（六段→五态，编排器消费盘中行时）：capitulation→低迷、accumulation→震荡、ignition→进攻、
expansion→进攻、euphoria→亢奋、distribution→防御。
**映射常量落点建议**：`plan_engine` 内 `_STATE_LABEL_MAP` 常量（代码）而非 config——
映射是语义定义非业务参数，改它=改代码走 review；业务阈值才进 config。

## 2. 路由表 v1 结构（状态→策略→因子三级）

```
Level0 大盘状态（六段，来自 regime_snapshot_history dominant + TDM-E-L1 双轴仲裁）
  ├─ Level1 策略包路由（真源=TDM state_matrix.cells，禁复制第二份）
  |    TDM-E-L1: capitulation→[STR-VREV-025,STR-VREV-027] accumulation→[STR-VREV-026,STR-VREV-027]
  |              expansion→[STR-MOMTREND-033]；ignition/euphoria/distribution=空格(pending-owner-adoption)
  |    TDM-P-P2(做T): accumulation+expansion→[intraday-surge-fall,orderbook-imbalance,vwap-reversion,STR-DABAN-023]
  |    TDM-E-L4(打板): ignition+expansion+euphoria→daban-sleeve
  ├─ Level2 配比（真源=PP-001 sleeves 只读；verified 6条各0.05起步×0.90 全域缩放）
  |    预算带（TDM-F-C1）：capitulation 0-10 / accumulation 20-30 / ignition 30-50 /
  |                      expansion 50-70 / euphoria ≤30只卖 / distribution 0%
  |    硬顶：60%（proposed，待 Owner 定稿）；过渡带（最大隶属度<60%）×0.5-0.7
  └─ Level3 因子面（bizmine 判定原料，只读引用）
       高波桶(1.12/0.21/2.48)+risk_off池(CORREL/BETA E4拦)+ETF T0绿区簇——
       禁直接挂载：TERMINATE#304 gate 禁翻案，激活走快签新卡（裁定#390②）
```

**消费序**：编排器 S4 查 state_matrix（挂谁）→ PP-001/alloc_budget_daily（给多少钱）→
盘中五态行（T3 预警降档，只写台账不换策略——盘中重判=明确不做）。

## 3. 落地路径（Owner 批后）

1. 映射常量入 plan_engine（代码批，等长替换）；
2. ignition/euphoria 拆分阈值 + 60% 硬顶 + 过渡带系数 → config（Owner 门位逐项批）；
3. 空格填格（TDM-E-L1 的 ignition/euphoria/distribution 三格）= Owner 资金分配门位（R41 封闭词表）。

## 4. 本班实证边界

- PP-001 快照读取已通（总扳手 pp001_snapshot：16 sleeves Σ=1.0，caps 1.0/0.25/0.7）；
- 拍板体已消费 expansion@1.00→cap=60%（decision_daily 实证行）；
- 五态行已产（09-18 盘中4行）+ 映射未落地（本稿=补定义，待批）。
