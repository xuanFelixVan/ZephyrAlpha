---
ttl: permanent
doc_type: architecture_view
title: 讨论稿：回测可观测性体系工作计划
owner: ZephyrAlpha-Owner
language: zh
status: 工作计划
version: "0.1.0"
date: 2026-08-07
topic: backtest_observability
scope: 07_trading_decision_architecture
---

---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.0.0"
date: 2026-08-07
topic: backtest_observability_workplan
scope: 07_trading_decision_architecture
parent: discussion_001_regime_detector_spec.md
---

# discussion_002 — 回测可观测性体系工作计划

> 状态: 工作计划（待用户确认后进入蓝图阶段）
> 日期: 2026-08-07（2026-08-07 更新：补开源调研结论 + 命名冲突发现 + 已动手进度 + Panel 决策落地）
> 作者: AI 提议，待用户裁定
> 关联: #ARCH-REGIME-DEADZONE-001（死区否决触发可观测性诉求）→ 本工作计划 → 实施蓝图 `.trae/documents/backtest_observability_mlflow_plan.md`
> 前序: discussion_001（regime_detector spec）

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
- 没有一个专门针对"回测结果版本化"的主流开源项目；所有量化框架要么用 MLflow/W&B，要么用 OpenTelemetry，要么自己 dataclass+落盘。
- MLflow 是自托管/本地/受监管环境的事实标准（2026 评测），Qlib（微软量化平台）默认就用 MLflow Recorder——量化领域权威背书。
- 我们的方案 = **MLflow（管存储/查询/UI）+ 薄包装层（把六零件的领域语义翻译成 MLflow 语义）**，正是主流做法，不是重复造轮子。薄包装层就是用户说的"写数据库新建表格"的工程化封装。

### 1.4 方案选型（已定）
**C. MLflow + 薄包装层**。详见 1.3。

## 2. 现状盘点

### 2.1 现有落盘机制（要改造）
- `c1_runner.save_c1_report`：写 JSON + MD 到 `logs/c1_repro/`，**覆盖模式**，无版本累积
- `c1_metrics.json` 含指标/verdict/backtest_config——结构良好，可直接转 MLflow metrics+params

### 2.2 要接入日志的"六零件"清单
| 零件 | 入口文件 | 职责 | 接入优先级 |
|---|---|---|---|
| C1 对比器 | `c1_comparator.py` / `c1_runner.py` | regime 开/关对比验证 | P0（样板）|
| regime_detector | `regime/core/regime_detector.py` | 市场状态检测 | P1 |
| 特征管道 | `regime/regime_feature_builder.py` | 生成 regime 特征 | P1 |
| 向量化回测 | `backtest/implementations/vectorized_engine.py` | 简化快速回测 | P1 |
| StrategyRunner | `pf_core/core/strategy_engine.py` | 全链路真实交易回测 | P2 |
| C2/C3 验证器 | 未建 | 未来验证器 | P3（建时即接入）|

### 2.3 ⚠️ 命名冲突发现（2026-08-07 新增，阻断项）

排查发现项目里 **"observability" 是横切概念，已散落在 4 处**，原计划把 MLflow 包放顶层 `zephyr.observability` 会占用顶层命名空间、造成语义混淆：

| 位置 | 内容 | 性质 |
|---|---|---|
| `zephyr.infrastructure.observability` | notifier.py / trace_decorator.py | 通知 + trace 装饰器 |
| `zephyr.shared.observability` | metrics.py / tracing.py / metrics_server.py / dashboard/ | 指标 + tracing + Grafana 模板 |
| `zephyr.security.access_control.observability` | ObservabilityReporter / AnomalyResult | 安全审计可观测性 |
| `zephyr.observability`（我新建）| config/experiment_tracker/fallback_tracker/models | MLflow 实验跟踪——**且缺 `__init__.py`，非正式包** |

**问题**：把"实验跟踪"独占顶层 `zephyr.observability`，会让"observability"这个横切词在顶层和子域同时出现，AI/人查代码时分不清。且新建包没 `__init__.py`，不规范，过不了治理门禁。

**待决策的归属选项**（详见 §9）：
- **A. 改名 `zephyr.experiment_tracking`**（推荐）——语义最准（MLflow 本就是 experiment tracking），零冲突。
- B. 保持顶层 `zephyr.observability`——独占顶层，但与现有 4 处 observability 语义重叠。
- C. 降为子包 `zephyr.shared.observability.experiment_tracking`——归入现有 shared.observability，但实验跟踪不只是 shared 层。

### 2.4 现有 dashboard 现状（2026-08-07 更新）
- 可视化技术栈已切换到 **Panel + HoloViz**（#ARCH-047，v3.0.0），`frontend/dashboard/app_panel.py` 是主入口
- 掘金 5-Tab 绩效渲染组件（`backtest_performance.py` 的 `backtest_result_to_performance_data` / `render_backtest_performance`）已就绪，**接受鸭子类型**，可从 MLflow 重建对象复用
- 结论：**复用 Panel + 掘金 5-Tab**（用户 2026-08-07 已定），不碰 Streamlit 旧骨架

### 2.5 依赖现状（2026-08-07 更新）
- 核心依赖已含：pandas / pyarrow / sqlalchemy / panel / holoviews / plotly
- mlflow 放 `[project.optional-dependencies] observability = ["mlflow>=2.10,<4.0"]`（pyproject.toml 已落地，2.x tracking 功能完备，3.x 兼容）
- 业务代码 lazy import + 降级（未装写本地 JSON，不崩业务）

### 2.6 已动手进度（2026-08-07 新增）
M1 已部分动手（在命名冲突未发现前），现状：
- ✅ `pyproject.toml` 新增 observability 可选依赖组
- ✅ 新建 5 文件：`config.py` / `models.py` / `experiment_tracker.py` / `fallback_tracker.py` / `adapters/__init__.py`
- ❌ **缺顶层 `__init__.py`**（非正式包，待命名决策后补）
- ❌ 缺 `query.py`（查询接口）
- ❌ 缺 `adapters/c1_adapter.py`（C1 接入）
- ⏸️ **暂停**：命名归属未定前不续写，避免改完又搬迁

## 3. 要做的事（工作清单）

### ⓪ 决策 MLflow 包归属命名（阻断项，先做）
- 在 A/B/C 三选项中裁定（§2.3、§9）
- 裁定后：补/改 `__init__.py`，让包正式化；已建的 5 文件按决策归位
- 验收：包名确定、`__init__.py` 就位、import 通、无命名冲突
- 预估：0.2 天（决策 + 归位）

### ① 引入 MLflow 依赖 + 跑通本地 UI（基础）
- `pyproject.toml` 新增 `[project.optional-dependencies] observability = ["mlflow>=2.10,<4.0"]`（✅ 已做）
- 开发机 `pip install -e ".[observability]"`
- 跑通 `mlflow ui --backend-store-uri sqlite:///logs/mlflow.db --port 5007`，浏览器能看到空 UI
- 验收：`mlflow ui` 启动，访问 `localhost:5007` 见到实验列表页（空）
- 预估：0.3 天

### ② 设计薄包装层（核心）
- 新建包（名待 ⓪ 决策）的 `experiment_tracker.py` / `query.py` / `models.py` / `config.py` / `fallback_tracker.py`（部分✅已做，待归位 + 补 query + 补 __init__）
- Zephyr 语义 → MLflow 映射：
  - `experiment` = 零件类型（`c1-validation` / `regime-detector` / `feature-build` / `vectorized-backtest` / `full-chain-backtest`）
  - `run` = 一次运行（带时间戳 + git commit + 参数快照）
  - `metrics` = 指标（Sharpe / MaxDD / Calmar / Turnover / passed 等）
  - `params` = 配置（backtest_config / deadzone / 篮子 / 时间段）
  - `artifacts` = 产物（净值曲线 CSV / 报告 MD / shrinkage 序列 CSV）
  - `tags` = 语义标签（component / mode / passed / strategy_id / zephyr_domain），lineage 串联多零件 run
- API（草案）：
  ```python
  tracker = get_tracker()  # 单例，自动选 MLflow / Fallback / Null
  with tracker.start_run("c1-validation", tags={"mode": "regime", "git_commit": "abc123"}) as run:
      run.log_params(backtest_config=..., basket=..., period=...)
      run.log_metrics(baseline_sharpe=..., experiment_sharpe=..., c1_passed=True)
      run.log_artifact_bytes(nav_csv_bytes, "nav_curve_experiment.csv")
  runs = list_runs("c1-validation")  # 屏蔽 MLflow vs 降级差异
  ```
- **lazy import + 降级**：mlflow 未装→FallbackBackend（写 `logs/observability_fallback/` JSON）；全局关闭→NullBackend
- 验收：单元测试覆盖（含降级路径）；list_runs/get_run 屏蔽双源差异
- 预估：1 天

### ③ C1 验证器接入（第一个零件，作样板）
- `c1_comparator.py` 加 2 个实例属性（`last_baseline_portfolio` / `last_experiment_portfolio`，镜像 `last_portfolio` 既有模式）
- `c1_runner.run_c1_with_provider` 加 `track` 参数（默认 False 向后兼容），调 `adapters/c1_adapter.track_c1_result`
- 保留原有 JSON/MD 落盘（向后兼容）
- 跑一次 C1，在 `mlflow ui` 见到 run，点开看 metrics/params/artifacts
- 验收：C1 跑两次（deadzone 开/关），UI/查询能对比两个 run 的指标差异
- 预估：0.5 天

### ④ 可视化接通（Panel 复用现有）
- 新增 `frontend/dashboard/components/experiment_history.py`："实验历史" Tab（不改现有"回测结果" Tab，避免破坏 #ARCH-047 注入契约）
- 数据流：`fetch_experiment_history(component)` → `query.list_runs` → 用户点 run → `get_run` + 下载 nav CSV artifact → 重建 BacktestResult/Portfolio 鸭子对象 → 复用掘金 5-Tab 渲染
- C1 run 特殊渲染：开/关双净值曲线叠加 + 四项 verdict 对比表
- `app_panel.py` 的 `build_tabs` 插入"实验历史" Tab
- 验收：`panel serve app_panel.py --port 5006`，"实验历史" Tab 列出 C1 run，点选看掘金 5-Tab；未装 mlflow 从 fallback JSON 读仍能列出
- 预估：1.5 天

### ⑤ 历史结果回灌
- 写脚本读 `logs/c1_repro/` 现有结果（c1_metrics.json + shrinkage_schedule.csv + 报告），导入 MLflow 作为历史 run
- 给历史 run 打 `tags.source = "backfill"` 标记，区分新跑的
- 验收：UI 能看到历史 run + 新 run，时间线连续
- 预估：0.5 天

### ⑥ 其余五零件接入（按 P1/P2 顺序）
- regime_detector 运行时记录（输入特征统计 + 输出状态分布 + 模型参数）
- regime_feature_builder 记录（特征矩阵 schema + 缺失率 + 快照 artifact）
- vectorized_engine 记录（每次回测的 config + 指标 + 净值曲线）
- StrategyRunner 记录（全链路：含滑点/手续费/冲击成本细节）
- C2/C3 建时即接入
- 全链路 lineage：`run_c1_end_to_end` 的 tags 串联 regime→feature→backtest→C1 四个 run_id
- 验收：每个零件跑一次，`list_runs(component)` 都能查到对应 run
- 预估：1.5 天

### ⑦ 治理登记
- 新建 ARCH 条目 `#ARCH-OBS-EXP-TRACK-001`（数字制，铁律#7）登记本工程
- 4 registry 登记：`functional_domain_registry`（D_INFRA_TELEMETRY 增 `experiment_tracking` subdomain）/ `module_translation_registry` / `capability_canonical_file_registry`（含 creation_tokens）/ `directory_registry`
- 蓝图 `blueprint_observability.md`（MOD-OBS-001）落地
- 验收：gate 校验通过，ARCH 条目 status=decided
- 预估：0.5 天

## 4. 不做的事（边界）

- ❌ 不做实时监控（realtime_pnl_dashboard 接通）——本计划只管"回测结果版本化"，实时监控是另一工程
- ❌ 不做模型 registry——当前无模型产物要管，只做 tracking
- ❌ 不做超参搜索（Optuna/hyperopt 集成）——等真有调参需求再做
- ❌ 不强制核心包依赖 mlflow——保持 optional，业务代码 lazy import 降级
- ❌ 不重写现有 Panel dashboard——只新增"实验历史" Tab，不碰掘金 5-Tab

## 5. 依赖与合规

| 项 | 决策 |
|---|---|
| mlflow 版本 | `>=2.10,<4.0`（2.x tracking 完备，3.x 兼容；pyproject.toml 已落地）|
| 安装方式 | `[project.optional-dependencies] observability`，`pip install -e ".[observability]"` |
| License | Apache 2.0 ✅ |
| 数据存储 | 本地 SQLite（`logs/mlflow.db`），不外传 |
| 业务侵入 | lazy import + 降级，mlflow 未装不崩 |
| 铁律#9 | 本工程为基础设施引入（非价值判断），但涉及架构边界，AI 提议 status=proposed，待用户确认转 decided |

## 6. 验收标准（整体）

1. `mlflow ui` 启动后，能看到所有 C1 历史 run（含回灌的 + 新跑的）
2. 每个 run 可查：指标 / 参数 / artifact（净值曲线/报告）
3. 任意两个 run 可在 UI 对比指标差异
4. C1 跑一次，自动产生一个新 run，无需手动操作
5. mlflow 未装时，C1 仍能正常跑（降级写本地 JSON，stderr 警告）
6. Panel "实验历史" Tab 能列出 run 并复用掘金 5-Tab 看详情
7. 六零件每个跑一次都能在统一入口查到
8. 用户能独立打开 UI/Panel 验证"真回测了"，不依赖 AI 口述

## 7. 风险

| 风险 | 缓解 |
|---|---|
| **命名冲突**（顶层 `zephyr.observability` 与 4 处子域 observability 混淆）| ⓪ 先决策归属（推荐 `zephyr.experiment_tracking`），决策前不续写代码 |
| mlflow 完整包依赖重 | 放 optional，核心包不污染；开发机一次性装 |
| 蓝图阶段发现 mlflow 语义不贴合量化 | 薄包装层隔离，必要时底层可换（Aim/自造）|
| Panel 注入契约被破坏 | 只新增 Tab，不改现有"回测结果" Tab |
| 历史 result 格式不统一 | 回灌脚本做归一化，不完美也导入（打 backfill tag）|
| nav CSV artifact 量大 | config.artifact_logging 开关 + 保留策略（M3+）|

## 8. 执行顺序与里程碑

```
M0（⓪）：命名归属决策 + 包归位                            [约 0.2 天，阻断]
M1（①+②+③）：MLflow 跑通 + 包装层 + C1 接入 —— 用户能看 C1 历史  [约 1.8 天]
M2（④）：Panel "实验历史" Tab —— 用户自助可视化验证          [约 1.5 天]
M3（⑤）：历史回灌 —— UI 时间线连续                          [约 0.5 天]
M4（⑥）：其余五零件逐个接入 + lineage                       [约 1.5 天]
M5（⑦）：治理登记收尾                                       [约 0.5 天]
```

**M1 完成即解决核心痛点**（用户能自己看 C1 回测结果）。M2-M5 是完善。

## 9. 待用户决策点

1. ✅ 方案选型：C. MLflow + 薄包装层（已确认）
2. ✅ 可视化路线：Panel 复用现有 + 掘金 5-Tab（2026-08-07 已确认，替代原 A/B/C 讨论）
3. ⏳ **命名归属**（阻断，§2.3）：
   - A. `zephyr.experiment_tracking`（推荐：语义最准、零冲突）
   - B. 保持顶层 `zephyr.observability`（独占顶层，但与 4 处子域语义重叠）
   - C. `zephyr.shared.observability.experiment_tracking`（归入现有 shared.observability）
4. ⏳ 工作文档本身是否认可 —— 认可后进入蓝图阶段（实施蓝图 `.trae/documents/backtest_observability_mlflow_plan.md` 已存在，需按 ⓪ 决策同步包名）
