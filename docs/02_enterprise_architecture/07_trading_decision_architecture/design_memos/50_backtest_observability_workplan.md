---
ttl: permanent
doc_type: architecture_view
title: 回测可观测性体系工作计划
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.1"
date: 2026-08-15
topic: backtest_observability_workplan
scope: 07_trading_decision_architecture
parent: 10_regime_detector_spec.md
---

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**：M1（#ARCH-OBS-EXP-TRACK-001）于 2026-08-07~09 落地——`zephyr.experiment_tracking` 包 8 文件（config/models/experiment_tracker/fallback_tracker/query/adapters/c1_adapter）+ c1_runner 接入 track_c1_result；M2 经 [51 号](51_panel_experiment_history_mlflow_retirement.md)（2026-08-16，A/B/C 三工作流）落地——Panel「实验历史」Tab 建成 + mlflow 代码全删 + `pip uninstall mlflow 3.15.1` 执行，存储收敛为单一 FallbackBackend JSON（v1.1.0 路线逆转裁定生效）。
>
> **最终成果**（2026-08-19 代码实证）：`experiment_tracking` 包在位（`__init__.py` 正式包，无命名冲突）；`c1_runner.py` lazy import `track_c1_result` 接线在位；全 src `import mlflow|_MLflowBackend` grep 零命中；`app_panel.py` tabs_spec 11 项含「实验历史」（`_tab_experiment_history`）；`query.py` `download_artifact`/`download_artifact_text` 在位；`tests/experiment_tracking/test_experiment_history.py` 在位。
>
> **未做事项及原因**：
> - §3 ⑥ 其余五零件接入（regime_detector / regime_feature_builder / vectorized_engine / StrategyRunner / C2C3 建时即接入 + 全链路 lineage）未施工——`adapters/` 目录仅 `c1_adapter.py` 一个适配器（2026-08-19 实证）。这是本计划明示的**核心剩余工作**（预估 1.5 天），非烂尾；裁定=未来工程-小型（逐零件 adapter + 验收"每零件跑一次 list_runs 可查"，单批可闭环）。
> - §3 ⑤ 历史结果回灌评估未做——M1 的 2 个 smoke run 已按 51 号裁定丢弃重跑（§二.3），`logs/c1_repro/` 历史结果是否回灌 JSON 属"待评估"非承诺项，裁定=未来工程-小型（随 51 号施工时一并评估，当前无阻塞）。
> - §3 ⑦ 治理登记收尾未竟——`07_d_infra_telemetry.md` 中 experiment_tracking 措辞仍写"MLflow 薄包装"（v1.1.0 已登记不越界改）、51 号 C2 列的 creation_token/blueprint 同步项随 51 号收口，裁定=未来工程-小型（文档级，随下一治理批顺手）。

# 回测可观测性体系工作计划

> 状态: 工作计划（M1 已落地；MLflow 路线已被 51 号逆转为单一 JSON 后端；剩余=其余五零件接入）
> 日期: 2026-08-07（2026-08-12 更新：v1.1.0 逆转收敛——方案选型/命名冲突/依赖现状按 51 号裁定与代码实况改写）
> 作者: AI 提议，用户已裁定（MLflow 路线 → 51 号逆转为单一 FallbackBackend JSON）
> 关联: #ARCH-REGIME-DEADZONE-001（死区否决触发可观测性诉求）→ 本工作计划 → #ARCH-OBS-EXP-TRACK-001（M1 落地）→ [51_panel_experiment_history_mlflow_retirement](51_panel_experiment_history_mlflow_retirement.md)（M2 + MLflow 退役）
> 前序: 10_regime_detector_spec（regime_detector spec）

> ⚠️ **v1.1.0 路线逆转声明**：本文 v1.0.x 选定"方案 C：MLflow + 薄包装层"（§1.3/§1.4）。
> 2026-08-09 用户在 51 号裁定**完全卸载 MLflow、存储收敛为单一 FallbackBackend JSON、
> 可视化走 Panel「实验历史」Tab**——本计划的 MLflow 相关条目（§3 ①②、§5 依赖表）随之失效，
> 仅保留为决策历史。当前有效路线：**FallbackBackend JSON（已落地）+ Panel Tab（51 号，待施工）
> + 其余五零件接入（本文 §3 ⑥，待施工）**。

## 0. 一句话目标

**让每一次回测（每一个"零件"的运行）都有可追溯、可查询、可对比的版本化记录，人和 AI 都能通过统一入口查看——不再"只能听 AI 说"。**

大白话：造发动机（检测器）时先单独台架测试，整车造好再整车上路。每个零件、每次台架、每次上路，都要留一份能查、能比、能绑在一起的"体检报告"，统一一个入口看。

## 1. 背景与触发

### 1.1 死区优化的教训
死区验证（#ARCH-REGIME-DEADZONE-001）暴露可观测性短板：
- C1 结果用固定文件名覆盖（`c1_metrics.json` / `c1_repro_report.md`），跑一次盖一次，**无法横向对比版本演变**
- 用户无法自己查看回测效果，**只能听 AI 口述**，信任成本高
- "到底有没有真用业务库数据回测"需要 AI 反举证，而非用户自助验证

### 1.2 用户诉求（2026-08-07 对话）
1. 所有零件都要有日志，记录每次运行结果（六零件全覆盖）
2. 日志可查询、相互绑定、统一入口、统一查看入口
3. 人类可看 + AI 方便查
4. 最终能基于历史数据判断"哪个版本怎么样"
5. 这是个系统性工程，先查有没有开源项目，避免重复造轮子

### 1.3 开源项目调研结论（2026-08-07 新增）

**问：有没有现成的开源项目？还是自己造（写数据库新建表格）？**

答：通用领域有成熟开源，量化专门版没有，"自造薄层"是主流做法。用户的判断"很简单、写数据库就行"是对的——薄包装层就是干这个。

| 方向 | 代表项目 | 是否适合我们 |
|---|---|---|
| 通用 ML 实验跟踪 | **MLflow 3.0**（2025 发布，唯一全开源 + 内置 registry + 原生 tracing）| ✅ 首选，已定 |
| 通用 ML 实验跟踪（云） | Weights & Biases / Comet | ❌ 免费 100GB 上限 / 收费 / 数据外传 |
| 数据版本控制 | DVC | ❌ 管数据集版本，不是结果日志（另一层） |
| 量化专门可观测性 | gs-quant（logging+OpenTelemetry）/ akquant（pyo3-log）/ QS-Trader（IndicatorEvent 审计）| ⚠️ 都是通用栈自造薄层，无成熟专门项目 |
| 通用可观测性栈 | OpenTelemetry / OpenObserve / ELK | ❌ 管 logs/metrics/traces，非"结果版本化" |

**关键结论**：
- 无专门针对"回测结果版本化"的主流开源项目——量化框架要么用 MLflow/W&B，要么用 OpenTelemetry，要么自造 dataclass+落盘；MLflow 是自托管/本地/受监管环境的事实标准（2026 评测），Qlib（微软量化平台）默认用 MLflow Recorder。
- 据此当时定"MLflow + 薄包装层"（薄包装层=用户说的"写数据库新建表格"的工程化封装，主流做法非重复造轮子）——2026-08-09 已被 51 号逆转（§1.4）。

> ⚠️ v1.1.0 注记：本节为 v1.0.x 调研历史记录，"MLflow 已定"结论已被 51 号逆转（见 §1.4）。

### 1.4 方案选型（v1.0.x 已定 MLflow；2026-08-09 被 51 号逆转）
**~~C. MLflow + 薄包装层~~（已逆转）**。v1.0.x 调研结论（§1.3）保留为决策历史。
51 号逆转后有效方案：**单一 FallbackBackend JSON 存储 + Panel「实验历史」Tab 可视化**——
用户只在 Panel 看回测，不再碰 `mlflow ui`。逆转理由见 [51 号 §一/§四](51_panel_experiment_history_mlflow_retirement.md)。

## 2. 现状盘点

### 2.1 现有落盘机制（要改造）
- `c1_runner.save_c1_report`：写 JSON + MD 到 `logs/c1_repro/`，**覆盖模式**，无版本累积
- `c1_metrics.json` 含指标/verdict/backtest_config——结构良好，可直接转 metrics+params

### 2.2 要接入日志的"六零件"清单
| 零件 | 入口文件 | 职责 | 接入优先级 |
|---|---|---|---|
| C1 对比器 | `c1_comparator.py` / `c1_runner.py` | regime 开/关对比验证 | P0（样板）|
| regime_detector | `regime/core/regime_detector.py` | 市场状态检测 | P1 |
| 特征管道 | `regime/regime_feature_builder.py` | 生成 regime 特征 | P1 |
| 向量化回测 | `backtest/implementations/vectorized_engine.py` | 简化快速回测 | P1 |
| StrategyRunner | `pf_core/core/strategy_engine.py` | 全链路真实交易回测 | P2 |
| C2/C3 验证器 | 未建 | 未来验证器 | P3（建时即接入）|

### 2.3 命名冲突发现与裁定（2026-08-07 发现，v1.1.0 标注已落地）

排查发现项目里 **"observability" 是横切概念，已散落在 4 处**，原计划把 MLflow 包放顶层 `zephyr.observability` 会占用顶层命名空间、造成语义混淆：

| 位置 | 内容 | 性质 |
|---|---|---|
| `zephyr.infrastructure.observability` | notifier.py / trace_decorator.py | 通知 + trace 装饰器 |
| `zephyr.shared.observability` | metrics.py / tracing.py / metrics_server.py / dashboard/ | 指标 + tracing + Grafana 模板 |
| `zephyr.security.access_control.observability` | ObservabilityReporter / AnomalyResult | 安全审计可观测性 |
| `zephyr.observability`（曾新建）| config/experiment_tracker/fallback_tracker/models | MLflow 实验跟踪——当时缺 `__init__.py`，非正式包 |

**问题**：把"实验跟踪"独占顶层 `zephyr.observability`，会让"observability"这个横切词在顶层和子域同时出现，AI/人查代码时分不清。

**裁定结果（v1.1.0 补）：选项 A 已落地**——包名定为 `zephyr.experiment_tracking`，`__init__.py`
已就位（8 文件正式包），与现有 4 处 observability 零冲突。原三选项保留为决策历史：
- **A. 改名 `zephyr.experiment_tracking`（✅ 已采用并落地）**——语义最准（experiment tracking 本意），零冲突。
- 未选项：B. 保持顶层 `zephyr.observability`（独占顶层，与现有 4 处 observability 语义重叠）/ C. 降为子包 `zephyr.shared.observability.experiment_tracking`（实验跟踪不只是 shared 层）。

### 2.4 现有 dashboard 现状（2026-08-07 更新）
- 可视化技术栈已切换到 **Panel + HoloViz**（#ARCH-047，v3.0.0），`frontend/dashboard/app_panel.py` 是主入口
- 掘金 5-Tab 绩效渲染组件（`backtest_performance.py` 的 `backtest_result_to_performance_data` / `render_backtest_performance`）已就绪，**接受鸭子类型**，可从实验记录重建对象复用
- 结论：**复用 Panel + 掘金 5-Tab**（用户 2026-08-07 已定），不碰 Streamlit 旧骨架

### 2.5 依赖现状（v1.1.0 更正）
- 核心依赖已含：pandas / pyarrow / sqlalchemy / panel / holoviews / plotly
- ~~mlflow 放 `[project.optional-dependencies] observability = ["mlflow>=2.10,<4.0"]`（pyproject.toml 已落地）~~
  **v1.1.0 Grep 核实更正**：pyproject.toml **无** observability extras 组、**未声明** mlflow（与 51 号 §二.2 一致）——mlflow 当时是手动 `pip install` 的环境级安装，51 号 A4 `pip uninstall mlflow` 后即零残留，无需改 pyproject。
- 业务代码 lazy import + 降级（未装写本地 JSON，不崩业务）——51 号逆转后 FallbackBackend 成为**唯一**后端，lazy import 降级语义改写为"enable_tracking=False→NullBackend"

### 2.6 已动手进度（v1.1.0 按代码实况更新）
M1 已落地（#ARCH-OBS-EXP-TRACK-001），现状（Grep/Glob 核实）：
- ✅ 包正式化：`src/zephyr/experiment_tracking/` 含 `__init__.py`（命名冲突已按选项 A 解决）
- ✅ 8 文件就位：`config.py` / `models.py` / `experiment_tracker.py` / `fallback_tracker.py` / `query.py` / `adapters/__init__.py` / `adapters/c1_adapter.py`
- ✅ c1_runner 接入：`c1_runner.py` lazy import `c1_adapter.track_c1_result`
- ⚠️ mlflow 残留待清：`experiment_tracker.py` L137 `_MLflowBackend`、`query.py` mlflow 分支、`config.py` L45-46 `tracking_uri`/`experiment_prefix` 仍在——51 号工作流 A 负责移除
- ❌ Panel「实验历史」Tab 未建（51 号工作流 B，`experiment_history.py` 未创建）

## 3. 要做的事（工作清单）

> v1.1.0 状态总览：⓪✅已决落地 / ①②❌被 51 号逆转取消 / ③✅已落地 / ④移交 51 号待施工 /
> ⑤待评估 / ⑥待施工（**核心剩余工作**）/ ⑦部分完成

### ⓪ 决策 MLflow 包归属命名（✅ 已完成）
- ✅ 裁定选项 A：`zephyr.experiment_tracking`，`__init__.py` 就位、import 通、无命名冲突（§2.3/§2.6）

### ① ~~引入 MLflow 依赖 + 跑通本地 UI~~（❌ 已逆转取消）
- 51 号裁定完全卸载 MLflow——本项取消。存储=单一 FallbackBackend JSON，可视化=Panel Tab（不跑 `mlflow ui`）

### ② ~~设计薄包装层~~（✅ 已落地，MLflow 语义映射在 JSON 后端同样成立）
- 包与 8 文件已就位（§2.6）。"Zephyr 语义 → MLflow 映射"中的 experiment/run/metrics/params/artifacts/tags 概念**在 FallbackBackend JSON 中同样成立**（JSON 承载同一语义模型），此映射设计仍有效：
  - `experiment` = 零件类型（`c1-validation` / `regime-detector` / `feature-build` / `vectorized-backtest` / `full-chain-backtest`）
  - `run` = 一次运行（带时间戳 + git commit + 参数快照）
  - `metrics` = 指标（Sharpe / MaxDD / Calmar / Turnover / passed 等）
  - `params` = 配置（backtest_config / deadzone / 篮子 / 时间段）
  - `artifacts` = 产物（净值曲线 CSV / 报告 MD / shrinkage 序列 CSV）
  - `tags` = 语义标签（component / mode / passed / strategy_id / zephyr_domain），lineage 串联多零件 run
- 待清：`_MLflowBackend` 与 query.py mlflow 分支（51 号工作流 A）
- API 草案中 `get_tracker()` 单例/backend 选择逻辑随 51 号简化为 `enable_tracking=False→NullBackend / 否则 FallbackBackend`

### ③ C1 验证器接入（✅ 已落地）
- `c1_runner.py` track 开关 + `adapters/c1_adapter.track_c1_result` 已就位（§2.6）

### ④ 可视化接通（移交 51 号，待施工）
- 本项整体移交 [51 号工作流 B](51_panel_experiment_history_mlflow_retirement.md)：新建 `experiment_history.py`「实验历史」Tab + `query.download_artifact` + app_panel 注册
- 51 号关键差异：C1 双净值对比视图**自建**于 experiment_history.py（不碰掘金 5-Tab 单曲线）；`_get_run_fallback` 的 bytes artifact 缺口（只取 `local_path` 丢 `filename`+`artifact_path`）须先修
- 掘金 5-Tab 鸭子类型复用（`backtest_result_to_performance_data` L702 / `render_backtest_performance` L1420）按 51 号 §七.P0-3 先勘探后定

### ⑤ 历史结果回灌（待评估）
- 原方案：读 `logs/c1_repro/` 导入 MLflow。逆转后改为导入 FallbackBackend JSON 目录结构
- **待评估**：M1 的 2 个 smoke run 是合成数据（51 号 §二.3 裁定丢弃重跑）；`logs/c1_repro/` 历史结果是否值得回灌到 JSON，随 51 号施工时一并评估

### ⑥ 其余五零件接入（待施工——本计划核心剩余工作）
- regime_detector 运行时记录（输入特征统计 + 输出状态分布 + 模型参数）
- regime_feature_builder 记录（特征矩阵 schema + 缺失率 + 快照 artifact）
- vectorized_engine 记录（每次回测的 config + 指标 + 净值曲线）
- StrategyRunner 记录（全链路：含滑点/手续费/冲击成本细节）
- C2/C3 建时即接入
- 全链路 lineage：`run_c1_end_to_end` 的 tags 串联 regime→feature→backtest→C1 四个 run_id
- 验收：每个零件跑一次，`list_runs(component)` 都能查到对应 run
- 预估：1.5 天

### ⑦ 治理登记（部分完成）
- ✅ `#ARCH-OBS-EXP-TRACK-001` 已登记（architecture_issue_registry.yaml L12963，标题已含"单一 JSON 后端 + MLflow 退役收敛"）
- ✅ `functional_domain_registry` D_INFRA_TELEMETRY 已含 experiment_tracking（07_d_infra_telemetry.md 11 模块图在册）
- ⏳ 51 号 C2 列的后续登记项（experiment_history 组件 creation_token / blueprint 同步"单一 JSON 后端"）随 51 号施工完成
- ⚠️ 07_d_infra_telemetry.md 中 experiment_tracking 模块措辞仍写"MLflow 薄包装"——51 号施工完成后需同步改写（登记在 51 号，不越界改）

## 4. 不做的事（边界）

- ❌ 不做实时监控（realtime_pnl_dashboard 接通）——本计划只管"回测结果版本化"，实时监控是另一工程
- ❌ 不做模型 registry——当前无模型产物要管，只做 tracking
- ❌ 不做超参搜索（Optuna/hyperopt 集成）——等真有调参需求再做
- ❌ 不引入 mlflow 及任何外部实验跟踪服务——存储=单一 FallbackBackend JSON（51 号裁定）
- ❌ 不重写现有 Panel dashboard——只新增"实验历史" Tab，不碰掘金 5-Tab

## 5. 依赖与合规（v1.1.0 逆转后）

| 项 | 决策 |
|---|---|
| ~~mlflow 版本~~ | ~~`>=2.10,<4.0`~~ 已逆转：**不引入 mlflow**，51 号 A4 `pip uninstall mlflow` 清环境级残留 |
| 安装方式 | 零新增依赖——panel/plotly/pandas 已是核心依赖，FallbackBackend 纯标准库+json |
| License | 无新引入（原 MLflow Apache 2.0 不再相关） |
| 数据存储 | 本地 JSON 目录（`logs/experiment_tracking_fallback/`），不外传 |
| 业务侵入 | `enable_tracking=False→NullBackend`；默认 FallbackBackend 写 JSON，不崩业务 |
| 铁律#9 | 51 号逆转方向已由用户裁定（decided） |

## 6. 验收标准（整体，v1.1.0 逆转后）

1. ~~`mlflow ui`~~ Panel「实验历史」Tab 能看到所有 C1 历史 run（51 号施工后验收）
2. 每个 run 可查：指标 / 参数 / artifact（净值曲线/报告）——经 `query.list_runs`/`get_run`/`download_artifact`
3. 任意两个 run 可在 Tab 对比指标差异（51 号 P1-4 多选横向对比）
4. C1 跑一次，自动产生一个新 run（✅ M1 已落地：c1_adapter track_c1_result）
5. `enable_tracking=False` 时 C1 仍能正常跑（NullBackend 不写文件不抛）
6. Panel "实验历史" Tab 能列出 run 并看 C1 双净值对比视图（51 号施工后验收）
7. 六零件每个跑一次都能在统一入口查到（⑥待施工）
8. 用户能独立打开 Panel 验证"真回测了"，不依赖 AI 口述

## 7. 风险（v1.1.0 逆转后）

| 风险 | 缓解 |
|---|---|
| ~~命名冲突~~ | ✅ 已解决（选项 A `zephyr.experiment_tracking` 落地） |
| ~~mlflow 完整包依赖重~~ | ✅ 已消除（不引入 mlflow） |
| mlflow 残留清理不彻底 | 51 号 §五.2 `rg "import mlflow\|_MLflowBackend" src/zephyr/` 残留检查验收 |
| FallbackBackend JSON run 数膨胀后查询慢 | 51 号 P2-8 lru_cache + 前 50 条兜底；run>100 再评估 DuckDB 只读视图（51 号 §八.C 登记） |
| Panel 注入契约被破坏 | 只新增 Tab，不改现有"回测结果" Tab |
| 历史 result 格式不统一 | 回灌脚本做归一化，不完美也导入（打 backfill tag）；⑤待评估是否回灌 |

## 8. 执行顺序与里程碑（v1.1.0 逆转后）

```
M0（⓪）：命名归属决策 + 包归位                            [✅ 已完成]
M1（②+③）：FallbackBackend + 包装层 + C1 接入            [✅ 已落地 #ARCH-OBS-EXP-TRACK-001]
M2（④+A退役）：Panel "实验历史" Tab + mlflow 代码移除     [移交 51 号，待施工]
M3（⑤）：历史回灌评估                                     [待评估]
M4（⑥）：其余五零件逐个接入 + lineage                     [待施工，本计划核心剩余]
M5（⑦）：治理登记收尾                                     [部分完成，随 51 号收尾]
```

**M1 已完成核心存储链路**（C1 结果写入 JSON 可查）。M2 完成后用户能自助看回测——核心痛点全解。

## 9. 待用户决策点（v1.1.0 全部已决）

1. ✅ 方案选型：~~C. MLflow + 薄包装层~~ → **51 号逆转：单一 FallbackBackend JSON + Panel Tab**（2026-08-09 用户裁定）
2. ✅ 可视化路线：Panel 复用现有 + C1 双曲线对比视图自建（51 号工作流 B，掘金 5-Tab 鸭子类型按 P0-3 勘探后复用）
3. ✅ 命名归属：**选项 A `zephyr.experiment_tracking`** 已落地（§2.3）
4. ✅ 工作文档认可：M1 已施工落地（#ARCH-OBS-EXP-TRACK-001）；本计划 v1.1.0 转 active 继续承载 ⑥ 五零件接入

## 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 1.0.1 | 文件名 discussion_018_backtest_observability_workplan.md → 50_backtest_observability_workplan.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 1.0.2 | 文档头统一：frontmatter 补 title/owner/language，H1 去文件名前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 1.1.0 | **MLflow 路线逆转收敛改写 + 代码实况核实**（draft→active）：① 头部加 v1.1.0 路线逆转声明（51 号 2026-08-09 裁定完全卸载 MLflow、单一 FallbackBackend JSON、Panel Tab 可视化）；② §1.4 方案选型标注已逆转；③ §2.3 命名冲突标注选项 A 已落地（experiment_tracking 8 文件正式包）；④ §2.5 依赖现状更正（Grep 核实 pyproject.toml 无 observability extras、无 mlflow 声明，v1.0.x"已落地"描述不实）；⑤ §2.6 已动手进度按代码实况更新（__init__.py/query.py/c1_adapter 均已就位，mlflow 残留待 51 号工作流 A 清除）；⑥ §3 工作清单八项全量状态标注（⓪✅/①②❌逆转取消/③✅/④移交51号/⑤待评估/⑥待施工=核心剩余/⑦部分完成）；⑦ §5/§6/§7/§8 按逆转后改写（零新增依赖/验收走 Panel/风险收敛/里程碑 M0-M1 已完成）；⑧ §9 四个决策点全部标已决；status draft→active（方向全定、M1 已落地、剩余工作明确）。另注：本版修正曾遭并发会话回滚五次（含 f7c4ad2e commit 时 index 被还原漏收一次），此为重放写入 | 架构审查第 1-2 轮发现 50 号与 51 号根本矛盾（50 号写"MLflow 已定"而 51 号已裁定退役）+ 多处与代码实况脱节（命名冲突/依赖声明/已动手进度），按 51 号裁定与 Grep 实证收敛统一 |
| 2026-08-15 | 1.1.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——§1.3 关键结论 3 条散文并为 2 条（逆转指针并入，调研事实零丢失）；§2.3 未选项 B/C 并为一条（决策历史保留） | 8 类扫描 2 处（类别 2 过程性叙述×1、类别 5 冗余修饰×1）；被推翻的 MLflow 方案按 v1.1.0 既定"保留为决策历史"裁定不删 |

---

## 治理登记收尾（§3⑦，2026-08-20 登记）

> AI-NIGHT-001 包 Q2 派单：§3⑦ 三项治理登记项的实证收尾登记。结论：**两项闭环、一项为派生文档重生成滞后（非真源漂移）**。

| 登记项 | 状态（2026-08-20 实证） | 证据与口径 |
|---|---|---|
| ① `experiment_history` 组件 creation_token 登记 | ✅ **已闭环** | capability_canonical_file_registry.yaml L5434-5441：`src/zephyr/frontend/dashboard/components/experiment_history.py` token=`auto-frontend-experiment-history-20260816`、`tests/experiment_tracking/test_experiment_history.py` token=`auto-test-experiment-history-20260816`（created_by=session-ai-25808-20260815122313，51 号工作流 C 批） |
| ② blueprint 同步"单一 JSON 后端" | ✅ **已闭环** | `docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md` v0.2.0：title="Experiment Tracking 蓝图 — 单一 JSON 后端实验跟踪（MLflow 已退役）"，summary 明示"MLflow 已于 2026-08-16 退役卸载"，last_updated/last_verified=2026-08-16 |
| ③ 07_d_infra_telemetry.md 措辞同步 | ⏳ **派生文档滞后，真源已一致** | 真源（src/zephyr/experiment_tracking/ 各模块 docstring）已全部 v0.2.0 口径（"单一 JSON 后端/FallbackBackend，MLflow 已退役"——__init__/query/models/fallback_tracker/experiment_tracker/config 逐文件实证）；07_d_infra_telemetry.md 为 generate_domain_doc.py 从 depgraph（PostgreSQL）**自动生成**的派生文档——包级节点与"模块核心算法"节标题已同步新措辞，但全景图内 query/config/fallback_tracker/models 四节点描述仍为旧"mlflow vs fallback 双后端"措辞（depgraph 快照未全量刷新）。属"派生文档未重生成"滞后，**非真源漂移**；待下一次域文档重生成（全景图刷新批）自动收敛，本备忘不手改自动生成文件（改则下次重生成被覆盖，且违反派生产物纪律） |

**收尾裁定**：§3⑦ 整体标记为"登记闭环、一项观察中"——里程碑 M5（⑦治理登记收尾）达成口径以①②为准；③的收敛验证方式=下次 depgraph 全量重扫+域文档重生成后，grep 07_d 残留 "mlflow vs fallback"/"没装 mlflow" 措辞应零命中（标**待实证**，随生成器批次复核）。
