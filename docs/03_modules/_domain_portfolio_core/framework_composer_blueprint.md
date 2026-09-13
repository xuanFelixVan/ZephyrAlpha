---
module_id: MOD-FWCOMP-001
blueprint_id: MOD-FWCOMP-001
responsibility_domain: 
design_maturity: production
build_status: stable
version: 1.1.0
status: active
owner: ZephyrAlpha-Owner
language: zh
ttl: permanent
doc_type: architecture_view
topic: framework_composer
scope: module
date: 2026-09-10
---

# MOD-FWCOMP-001 整装组合回测器 blueprint

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-FWCOMP-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-FWCOMP-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-FWCOMP-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-FWCOMP-001 | MOD-FWCOMP-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 定位（一句话）

把「整装方案」（N 个子策略的资金权重比例）× 各子策略日频权重面板线性合成组合权重面板，复用现有回测引擎跑出组合净值——二期整装回测后端核心算子。

## §2 方法论根据

system_charter.md §3 约束二「统一框架派：1 框架 × N 子策略 × regime 权重切换」。本模块是「按方案分配资金」的回测侧实现；三期 regime 动态权重联动已落地（2026-09-10）：α_i 来源从静态方案配置升级为逐日 regime 查表（compose_weight_panels 增 regime_by_date 参数），合成/回测链路不变，静态模式与二期逐位一致。

## §2.1 三期 regime 动态化语义（α_i(t)）

- **查表不做判定**：状态词表唯一真源 = `zephyr.regime.core.regime_detector.REGIME_STATES`（MOD-REGIME-001，r1 低波震荡/r2 中波震荡/r3 牛市趋势/r4 熊市阴跌/r10 CRISIS/r11 RECOVERY/r12 BREAKOUT 七态），非法状态 fail-closed 拒绝——regime 错=权重错（约束三生死线），本模块禁自造判定逻辑；日序生产责任 = 真源检测器离线回放（先例 `shrinkage_provider.build_schedule_from_detector`），当前无逐日持久化 regime 真源表（T1 盘点 2026-09-10），API 侧显式注入。
- **配置侧**：`config/framework_plans.yaml` 每方案 `regime_overrides` 段（键∈7 态、成员集合=基准、覆盖表 Σ=1）；未覆盖 regime 回退基准权重。
- **合成侧**：W(t,s)=Σ_i α_i(t)·w_i(t,s)，α_i(t)=当日 regime 查覆盖表（未覆盖日期归 `__base__` 组）；各组独立 Σ=1 校验与显式再归一化（`regime_day_counts`/`regime_rescale_factors` 落报告，禁静默）。
- **归因侧**：`per_regime_summary` 按组输出分段收益/回撤贡献（done 响应消费）。

## §3 姊妹算子边界（禁止合并）

| 算子 | 模块 | 语义 |
|---|---|---|
| ablate_weight_panel（剥离） | MOD-TDMVAL-001 | 从权重面板剥离 X 流动作做反事实对照（一减） |
| compose_weight_panels（叠加） | MOD-FWCOMP-001（本模块） | 按方案权重叠加多成员面板出组合面板（一加） |

两者共享 Σw=1 显式归一化纪律（禁静默再分配）与回滚式披露风格，职责正交。

## §4 公共 API

| 符号 | 说明 |
|---|---|
| `load_framework_plans(path=None)` | 加载 config/framework_plans.yaml 全部方案并校验（Σ=1 容差 1e-6；三期另校验 regime_overrides：键∈7 态/成员集合=基准/覆盖表 Σ=1） |
| `get_framework_plan(plan_id)` | 按 ID 取方案（不存在抛 FrameworkPlanError） |
| `compose_weight_panels(plan, panels, allow_partial=True, regime_by_date=None)` | 合成算子 → ComposeReport（panel/participants/skipped/rescale_factor/notes 全披露；三期 regime_by_date 非空=动态查表模式） |
| `per_regime_summary(plan, equity_curve, regime_by_date)` | 三期：per-regime 分段摘要（days/return_pct/max_drawdown_pct，未覆盖归 __base__） |
| `verify_weight_panel_identity(plan, panels, composed, regime_by_date=None, tolerance=1e-9)` | 面板级对账（#275 定案口径①）：独立复算 W(t,s)=Σα_i(t)·w_i(t,s) 逐位硬验收；run_framework_backtest 每次运行自动执行并落产物 metrics |
| `reconcile_composed_nav(composed, member_navs, plan)` | 组合净值 vs Σα_i·nav_i 逐日对账（验收判据 抽样≥5 日误差<0.01%；仅静态口径，动态用 per_regime_summary） |
| `run_framework_backtest(plan_id, symbols, start, end, ...)` | 全链路：成员面板 → 合成 → DefaultBacktestEngine → 产物 bt-fw-*.json（plan_id 落 metrics；cfg.regime_by_date 非空=动态，响应增 dynamic/regime_day_counts/per_regime） |

## §5 不变量（INVARIANTS）

1. 不重写撮合逻辑——复用 DefaultBacktestEngine / StrategyRunner（D_BACKTEST / 本域既有资产）。
2. Σw=1 显式归一化：参与权重合计<1 时 rescale_factor 落报告（allow_partial=False 严格拒绝），禁静默。
3. tick-only 成员跳过必须披露（skipped 落 artifact metrics），不做隐式换策略。
4. BacktestRunArtifact（CTR-P1-017）顶层 schema 冻结——plan_id/披露字段走 metrics 扩展。
5. 不写 market_signal_history（管道 A 语义=子策略权重面板真源；组合面板是派生物）。
6. 回测成本模型在引擎层透传，不绕过（system_charter §3 约束一）。
7. （三期）regime 查表不做判定：词表唯一真源 regime_detector.REGIME_STATES，非法状态 fail-closed；未覆盖 regime/日期回退基准权重并披露（regime_day_counts）。
8. （三期）静态模式（无 regime 序）行为与二期逐位一致（向后兼容锚；静态产物 metrics 不加动态键）。

## §6 消费者

- `src/zephyr/frontend/dashboard/api_server.py`：GET /api/framework-plans、POST /api/framework-backtest-run（三期 body 增 dynamic+regime_series）、GET /api/framework-backtest-run（task 轮询；done 响应增 dynamic/regime_day_counts/per_regime）。

## §7 测试

`tests/pf_core/test_framework_composer.py`（30 用例）：配置校验 / 合成数学性质 / 联合索引对齐 / 再归一化披露 / 严格模式 / 净值对账 / 端到端（打桩面板+真引擎+tmp_path 产物隔离）/ 三期动态（真源配置 overrides 解析、两 regime α 切换、Σw=1 恒成立、回退=静态逐位一致、fail-closed 拒绝、组级 rescale 披露、动态端到端、静态向后兼容锚）。

## §8 已知边界（如实披露）

- v1 仅向量化日频合成回测；tick 模式整装回测（逐成员 tick 回放+组合）为后续迭代。
- 成员回测参数同参透传（v1 简化）；方案级参数差异化留后续。
- 约束事件（涨跌停拒单/T+1）下组合净值与手工加权存在路径二阶差异——对账工具如实报告超容差日期，不粉饰。
- （三期实测 2026-09-10，**#275 定案**）组合净值 vs 成员净值混合（Σα_i·r_i）在活跃窗口存在恒定比率级偏差（同引擎 solo 成员路径复现，静态同样存在；归因=整手取整（高股价 100 股粒度）/成本/约束事件在组合与成员两组合间的非共享二阶效应）——面板级 α_i(t) 数学已单测逐位验证。**定案口径①（Owner 授权最专业方案自裁）**：面板级对账 `verify_weight_panel_identity` 逐位硬验收（1e-9，run_framework_backtest 每次运行自动执行并落产物 metrics）；NAV 层残差归因披露不设容差；方案② look-through 留待多账户/模拟赛马阶段自然成立（单一账户硬做不消除取整残差）。
- （三期）regime 日序为显式注入（无逐日持久化真源表）；内置检测器 walk-forward 自动回放另批立项。
