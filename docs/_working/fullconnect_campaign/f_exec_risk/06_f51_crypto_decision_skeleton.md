---
ttl: task_bound
title: "F51 币圈决策骨架——TDM-C-L1..L4 第二实例（missing 空壳，L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F51 · 币圈决策骨架（TDM-C-L1..L4，market=crypto 第二实例）

> 同 schema 第二实例（D2.5），V0 有意空壳——"等 A 股链路验证后移植"是地图原文设计意图，非意外缺失。
> wiring_gap_inventory_20260927.md §1.4 missing 6 清单在案（F51 在列）——本卷独立复核确认 missing。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | 无（零入边，仅 L1→L2→L3→L4 三条内部 sequence）|
| 下游消费 | 无（零出边，与 A 股四流零耦合）|
| 自动化触发 | 零 |
| 真源与注册表 | 地图 yaml:4173/4193/4212/4231（TDM-C-L1..L4 本日实锚）；四节点 module_ref 全空+red_reason=not_built（本日 awk 复证 4/4）；BT-P3-048..051 backtest_backlog.yaml:1818/1832/1846/1860 本日实锚（plan=null）|
| 门禁与质量尺 | validation runner 排除：runner.py:64 `_L4_EXCLUDE_PREFIX = "TDM-C-"`（本日实锚 :64/:116 两处）|
| 当前运行状态 | **红（未运行，且属有意空壳）**——TDM-C-L1 节点文 algo_note_zh 原文"v1 空壳，等 A 股链路验证后移植"（yaml:4173 块本日实读）|

## 二、子模块三级枚举（本日全查 crypto 面——较 18 册口径扩容）

- **data 层（比 18 册"仅有 calendar/crypto.py"多 4 件，勘误登记）**：data/calendar/crypto.py（7×24 日历）｜data/implementations/crypto_provider.py（MOD-L00-004 §crypto）｜crypto_universe_selector.py（CONSUMERS=UNI-CRYPTO-001 Phase 2 扩池候选）｜crypto_event_calendar.py+crypto_profile_provider.py（CONSUMERS=zephyr.data.scheduler，STARTUP imported——**即已被数据调度面登记消费**）
- **执行层**：ex_core/adapters/okx_broker.py（testing，95 号 Phase 2 挂起）；ex_core/rules/crypto.py（研究域在盘未接，M7-04 裁定不挖）
- **观测/反馈层**：frontend/dashboard/web/features/cryptomarket（展示面）｜feedback_loop/forensic/crypto_bootstrap.py（法证引导件）
- **TDM 登记面**：TDM-C-L1..L4（module_ref 全空）｜C3-05 schema 预留（funding/basis 行 A 股实例恒 0+UTC 时间轴）
- **结论不变**：零**交易**模块（无交易所接入/无 WS 行情/无订单面/无钱包）——但"仅有一件真身"的旧口径已失真，crypto 数据面 6 件+调度登记 2 件是新的部分实件

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| TDM-C-L1..L4 节点 | missing（登记态） | module_ref 全空+red_reason=not_built 4/4 |
| validation 排除机制 | 已建成 | runner.py:64/:116 |
| crypto 数据源面 | **半接线（新发现）** | crypto_event_calendar/profile_provider CONSUMERS=data.scheduler+STARTUP imported——源线登记已达调度面，但无下游决策消费 |
| 交易执行面 | missing | 全链无交易所订单面 |

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 四节点空壳保留 vs 退役 | **待裁**（w5_1 零触发零消费 vs Owner D2.5 拍板保留；选项 A 保留登记/B 退役留日历与 schema/C 最小实件化 C-L1——18 册建议 A）| P2（Owner 裁）|
| 2 | crypto 数据面已到调度面但零决策消费 | 若保留：先 C-L1 单节点 paper 判定器（禁四节点齐上）| P2 |
| 3 | A 股链路未全通（"等验证后移植"前置未达成） | 非 F51 自身缺口，登记依赖 | P1（归 S/P 流编排工单）|

## 五、自审闸三态
**待裁**（空壳去留=Owner 门位；本卷贡献=把 18 册"仅一件真身"口径修正为"crypto 数据面 6 件+调度登记 2 件，交易面仍零"——若 Owner 裁退役，w5_1 判据须按新口径复核 data 件去留）。

## 六、复跑命令
```bash
find src/zephyr -iname "*crypto*" -name "*.py" | grep -v __pycache__   # 本日 7 件清单
grep -n "CONSUMERS\|STARTUP" src/zephyr/data/implementations/crypto_event_calendar.py | head -2
grep -n "_L4_EXCLUDE_PREFIX" src/zephyr/trading/validation/runner.py
awk 'NR>=4172 && NR<=4250 && /module_ref:|red_reason:/' config/trading_decision_map.yaml   # 4 组全空
grep -n "BT-P3-048" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
```
