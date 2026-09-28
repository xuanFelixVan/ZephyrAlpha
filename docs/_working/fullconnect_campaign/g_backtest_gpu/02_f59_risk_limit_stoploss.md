---
ttl: task_bound
title: "F59 风控限额与止损引擎——REG-RLM-001 117 条九类+ATR/持仓风控"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F59 · 风控限额与止损引擎（总册状态 built/P0；本卷复核=登记面 built，执行面读取链半接线）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | NAV/持仓/成交流（风控计算原料）；ATR 波动率（atr_stop_engine）；柜台镜像（持仓风控） |
| 下游消费 | F47 R1 熔断判定（drawdown_state_machine 归 F60）；F41/F53 pre_execution_checker 风控闸；kill_switch 五级（F61） |
| 自动化触发 | 盘中=risk_layer_orchestrator.evaluate_intraday 由调仓线程内嵌调用（M7-02：**无独立盘中风控 runner**，audit TRD-A07 同判）；日级=daily_gate_snapshot 消费 drawdown_state_machine |
| 真源与注册表 | REG-RLM-001=docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml，schema v2.1，**risk_limits 条目=117（本日 yaml 解析实测，总册"117 条"核真）**，九类=position/concentration/drawdown/var/es/leverage/turnover/kill_switch/firm_risk（册 description 自述），ai_autonomy=human_gated |
| 门禁与质量尺 | reconciler 只能 warn/skip/fix-in-place 禁 commit（册头 INVARIANTS）；registry_code_anchor_gate/fingerprint 对账 gate 消费（gov_enforcement/commit_gates/） |
| 当前运行状态 | **登记面 built / 执行面黄**：限额库 117 条有人读（governance 面 6 消费者实测）；限额执行件（risk_limits.py/risk_manager.py）与库的**运行时读取链未证**——risk_manager.py 108 行 [CONSUMERS] 空，执行参数疑硬编码 |

## 二、子模块三级枚举（risk 域本日实扫：根 22 件+core 49 件+implementations 5 件+api/services/cross_asset）

- **登记面**：risk_limit_registry.yaml（REG-RLM-001，117 条实测）；消费方实测 6：autonomy_core/module_mapper、compliance/intraday_manipulation_detector（阈值入册草稿注 :41）、frontend/api_server、gov_enforcement/registry_alignment、commit_gates/registry_code_anchor_gate、trading/decision_map.py:109（R33 风险限额库映射）
- **执行面**：risk_limits.py（RiskLimitsCalculator）、risk_manager.py（108 行）+risk_manager_base.py、implementations/default_risk_limits_calculator.py（:51-57 继承链实测）+default_risk_validator.py（JsonStateStore 持久化，M7-02 已证读写全通）
- **止损引擎**：atr_stop_engine.py（358 行；消费者 4 实测：factor/analysis/bma_signal_weighter、risk/post_entry_instant_validator、risk/__init__、signal_ashare/ml_forecast/gap_fill_model）；core/ashare_stop_loss_engine.py（617 行；**唯一消费者=post_entry_instant_validator**）；stop_loss.py
- **核心族节选**（core/ 49 件）：var_calculator/var_backtester/var_breach_state_machine、stress_test_engine、risk_veto_engine、risk_budget_allocator、tail_risk_monitor、crowding_monitor、liquidity_crisis_manager 等

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 限额登记面 | built（在册+有人读+gate 对账） | 117 条实测；6 消费者 grep 实测 |
| 限额执行面 | **半接线嫌疑** | risk_manager [CONSUMERS] 空；无 risk_limit_registry 运行时读取实证（grep 限 src/ 内 6 命中均 governance/登记面）——限额值疑硬码于执行件，库↔码漂移无对账测试 |
| ATR 止损链 | built（码+消费 4 方） | atr_stop_engine 358 行；post_entry_instant_validator 消费链在 |
| A 股止损引擎 | 半接线（单消费方） | 617 行仅 post_entry_instant_validator 一消费者；无盘中常驻触发面（同 TRD-A07） |

### 骨架勘误
- 总册 F59 锚点未列 risk_limits.py/default_risk_limits_calculator.py——执行面真身在此两件，建议总册锚点补列（不阻断）。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 限额库↔限额执行件运行时读取链未证（117 条疑登记态自嗨） | 加 config↔常量一致性断言测试；或执行件启动时读库校验（XS-S） | P1 |
| 2 | 盘中独立风控 runner 缺（TRD-A07 老案） | 归 M5 常驻族+RC 车道；登记 process_reaper_keep | P1 |
| 3 | ashare_stop_loss_engine 单消费方、触发面窄 | 并入缺口 2 同批处置 | P2 |
| 4 | schema v2.0 多维标注"既有条目空值占位禁视为已填"（册头自注） | 逐条回填随条目重填计划（登记级） | P2 |

## 五、自审闸三态
**挖干可施工**（登记/执行/止损三面 file:line 实证；缺口 1=本卷新增判定，总册 built 态的细化修正非推翻）。

## 六、复跑命令
```bash
python -c "import yaml,io;d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/risk_limit_registry.yaml',encoding='utf-8'));print(len(d['risk_limits']))"   # 117
grep -rn "risk_limit_registry" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v test   # 6 命中均治理面
head -8 src/zephyr/risk/risk_manager.py                                # [CONSUMERS] 空
grep -rln "ashare_stop_loss_engine" src/zephyr --include="*.py" | grep -v __pycache__ | grep -v core/ashare   # 唯一 post_entry_instant_validator
```
