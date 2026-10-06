---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-01 | TDM-X-R1-03 护盘资产定向加仓白名单

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **S**（登记已由 T6 ④完成；启用=Owner 门位，AI 禁自填）
- 依赖: MOD-POS-026 `src/zephyr/position/core/defensive_asset_whitelist.py`；X-R1-01 熔断态（有接口未开，不在本卡范围）
- 真源: `config/trading_decision_map.yaml#TDM-X-R1-03`；t3 挖矿 §2-S4；executor T6 头注 ④

## 1. 机制定义

熔断期（L2/L3）三重门全过才开的"窄门"：①熔断态；②超跌反转信号（或国家队明牌：ETF 天量/
官方增持）；③金字塔分批（首笔 1/3 预算）。白名单=宽基 ETF（沪深300/中证500/1000/红利）优先，
银行/高股息次之；仓位上限总资金 5-10%（D107 尾部弹药预算）。proposed 假说，回测验证前不生效。

## 2. 计算式（回测可考子集）

```
defensive_universe = defensive_whitelist_assets()          # MOD-POS-026 模块常量，AI 禁自填
G_universe'        = G_universe ∪ defensive_universe       # 仅 defensive_leg 格点
cap_defensive[t]   = 0.05..0.10                            # 总资金帽（prereg 键，禁硬编码）
```

超跌反转触发器（日级代理）：`signal[t] = (index_ret_20d < -q_触发阈值) and (index_close < MA200)`
——具体阈值属 prereg 标定项，本卡不替 Owner 定值。

## 3. 向量化实现要点

白名单资产走 `load_etf`（`_c4_engine.py:222` 在册）装载 ETF close 宽表与个股面板拼列；
金字塔分批=K_capital_ramp 维 `pyramid` 取值语义（M4 线）复用，本卡不重写。

## 4. 引擎接法（S 级，现状）

- **已登记**（executor T6 ④）：`defensive_whitelist_assets()` 引用 MOD-POS-026 常量，
  t3 prereg `defensive_leg` 对齐校验漂移=SystemExit。登记≠启用。
- **剩余动作**：t3 prereg 增 `defensive_leg=true` 格点族 + 防御格内容（state_matrix
  euphoria/distribution 格）——**格子内容属 Owner 资金分配门位**（state_matrix
  mounted_reason 明示禁 AI 自填），本车道只登记到"可启用"状态。

## 5. 考法（T0 口径声明）

白名单资产为 ETF：stk_limit 无行 → 封板闸 fail-open 不闸（`_load_seal_masks` docstring
明示非股票标的不闸）。ETF 腿纯向量化、无路径依赖，**若 defensive_leg 单独成考维可沿用
0.53s/格口径**；但与 X_stop/X_breaker 联合格点仍受 M 级 T0 重标定约束（见 X-S1-02 卡）。

## 6. 数据列名

- ETF 日线：`load_etf` 消费表（CH）`trade_date/symbol/close`。
- 白名单内容：MOD-POS-026 模块常量（真源禁双头）。
