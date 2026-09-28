---
ttl: task_bound
title: "F47 R1 应急保命——熔断分级/熔断期减仓/护盘白名单（横切全流，L06 复飞卷）"
session: zc-l06-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F47 · R1 应急保命（TDM-X-R1-01..03，横切全流）

> 上游=F59 限额/F60 回撤 NAV/E-L0 broadcast；下游=全流 6 条出边（S1-06 强清/S2 broadcast/P2-01 停做T/P2-04 减仓/C2-01 聚合/P3-01 禁加期）。
> 与 F59/F60/F61（G 段，g_backtest_gpu 卷）分工：工程面归彼；本卷管 TDM 判定语义与消费面。

## 一、六向台账（实证锚点）

| 向 | 实证 |
|---|---|
| 上游输入 | NAV/回撤（F60/F63）、E-L0 broadcast、RLM-KILLSW/KILL-SWITCH×4+THD-DRAWDOWN×3；地图锚 yaml:3193（R1-01）|
| 下游消费 | 出边 6 条实测；R1-02→P2-04、R1-03→E-L4；kill switch 常驻任何档位不可移除（I-01/M-58）|
| 自动化触发 | drawdown_state_machine.py 773 行被 daily_gate_snapshot（daily_gate_snapshot.py:382 `out["drawdown_state_machine"]` 实锚）、drawdown_session_persistence、defensive_asset_whitelist 消费——**paper 日链内运行；无盘中 continuous 保命扫描常驻**（本日复证无变化）|
| 真源与注册表 | 地图 yaml:3156-3289；DAL-CIRCUIT-5（production，code_ref=drawdown_state_machine.py）；algo_flow 外迁件 _domain_risk/algo_flow/ 两 yaml 在盘 |
| 门禁与质量尺 | R1-01 auto/R1-02 paper/R1-03 paper；R1-01 note_confirmed 2026-09-16（消费方 AST 实测零在网后回填）|
| 当前运行状态 | **黄**——判定件落码+paper 日链消费；R1-02 drawdown_liquidation_guard.py 209 行**零外部消费**（本日 grep 全仓仅自身文件命中，独立复证同判）；kill switch 持久化双轨待裁（M7-02 B1：tks state_store save 通/rebuild 断 vs DefaultRiskValidator JsonStateStore 全通）|

## 二、子模块三级枚举（本日实扫 wc -l）

- **risk.core**（判定+处置）：drawdown_state_machine.py 773（L0-L4 五级+迟滞解除，MOD-RK-049，wired paper 日链）｜drawdown_liquidation_guard.py 209（梯度减仓，零消费）｜drawdown_broker_side_stop.py 241（券商端双保险，F60 面）
- **trading.trading_contracts.risk**（交易级五级熔断）：trading_kill_switch.py 165（五级 KILL_SWITCHES 唯一真源 :52-112）+kill_switch_state_store（save 已接线/rebuild_from_disk 零调用=M7-02 B1 半接线）；磁盘影子 data/runtime/trading_kill_switch_state.json **本日实测存在，saved_at=2026-09-25T03:49**（写路径活体证据，比 M7 采样的 09-23 更新）
- **ex_core**：risk_layer_orchestrator.py 1827（盘中级联真源，start_paper_session 必装配）
- **position.core**：defensive_asset_whitelist.py 327（R1-03 护盘白名单，整节点休眠语义）
- **pf_alloc.core**：tail_hedge_signal.py 71（DAL-TAIL-HEDGE trial 休眠）

### 骨架勘误
总册 F47 行核心模块路径列 `security/access_control/kill_switch.py`——**锚点漂移**（M7-02 已勘误：该件是 AI Agent 行为熔断器，:27-33 自注"勿误用作交易熔断"；交易级真源=trading/trading_contracts/risk/trading_kill_switch.py）。建议骨架本行改指 trading_kill_switch.py+drawdown_state_machine.py 双件。

## 三、接线四态独立复核

| 面 | 四态 | 复核证据 |
|---|---|---|
| R1-01 判定 | 已接线（paper 日链） | daily_gate_snapshot.py:382 消费锚 |
| R1-02 减仓处置 | **码成闸空** | liquidation_guard 全仓仅自身文件（本日 grep 复证）|
| R1-03 护盘白名单 | 有意休眠 | D114 proposed；ETF 天量数据地基缺（D109）——休眠是正确态 |
| 交易五级 vs TDM L0-L4 | 双轨并存 | 双五级阈值口径不一无互认（TRD-A13，待裁 Owner）|

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | R1-02 判了没人执行 | 接 P2-04/X-S2 编排工单（与 F43/F46 缺口 1 同批）| P0 |
| 2 | 盘中 continuous 保命扫描无常驻 | 归 RC/M7+M5 常驻族，须登记 process_reaper_keep | P0 |
| 3 | M-55 paper 升档前 Owner 手动接管入口缺位 | 治理面欠账，Owner 门位 | P1 |
| 4 | kill switch 持久化双轨（B1①rebuild 一行接入可先行） | ①0.5 天可施工；②归并 JsonStateStore 待裁 | P1 |
| 5 | 双五级仲裁序未立法 | Owner 裁定（TRD-A13）| P1 |

## 五、自审闸三态
**挖干可施工**（判定语义/边/豁免/验证欠账齐；缺口 1/2 有归属；R1-03 休眠为正确态勿提前激活）。

## 六、复跑命令
```bash
grep -rln "drawdown_liquidation_guard" src/zephyr scripts --include="py" --include="*.py" | grep -v __pycache__   # 仅自身=零消费复证
grep -n "drawdown_state_machine" src/zephyr/strategy_pipeline/daily_gate_snapshot.py | head -2
head -3 data/runtime/trading_kill_switch_state.json   # 磁盘影子活体
grep -rn "rebuild_from_disk" src scripts --include="*.py" | grep -v state_store.py   # 零调用=半接线复证
```
