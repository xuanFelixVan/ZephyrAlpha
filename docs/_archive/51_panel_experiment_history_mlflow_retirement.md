---
ttl: permanent
---

> **归档注记（2026-08-30）**：自 design_memos/implementation_plans 归档（候选核销批 greatwall_20260830——内容全量施工完毕核销，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=Panel「实验历史」Tab + MLflow 退役施工计划 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.2.14 · date=2026-08-16 · topic=panel_experiment_history_and_mlflow_retirement · scope=07_trading_decision_architecture · parent=50_backtest_observability_workplan.md

## 结案报告（AI-NIGHT-001 复核 2026-08-19）

> **实际开发**：2026-08-16 三工作流全部落地——A：`_MLflowBackend` 类/query.py 5 个 mlflow 函数/config.py 两字段删除，`pip uninstall mlflow 3.15.1` 执行；B：`experiment_history.py` 新建（P0-1 归一化/P0-2 对齐/P1-5 polarity/P1-6 后缀剥离/P1-7 分级降级/P2-8 lru_cache+前50），`app_panel.py` 注册第 11 Tab；C：2 个 fallback run 重生验证 + 治理登记（translation 5 条目/capability 2 token/ARCH 订正/blueprint v0.2.0）。同日浏览器实测补修 2 个 widget 层 bug（MultiSelect unhashable / Tabulator CDN 离线失败→plotly go.Table，v1.2.14）。顺手修复 2 个预存 bug（RunSummary.passed 必填位 TypeError 静默返空 / `_get_run_fallback` bytes artifact 信息丢失）。
>
> **最终成果**（2026-08-19 代码实证）：`src/zephyr/frontend/dashboard/components/experiment_history.py` 在位（fetch/render/dataclass 契约）；`app_panel.py` tabs_spec 11 项含「实验历史」+ `_tab_experiment_history` 方法；`query.py` `download_artifact`/`download_artifact_text` 在位；全 src `import mlflow|_MLflowBackend` grep 零命中；`tests/experiment_tracking/test_experiment_history.py` 在位；Playwright+Chrome 终验单选双曲线/多选对比表/降级 Alert 全通过（memo v1.2.14 记录）。
>
> **未做事项及原因**：
> - PNG 退役 pending——`_render_nav_png` 仍在 `c1_adapter.py`（2026-08-19 实证 L132/L190）；§七.P2-10 退役条件 3「用户确认 Panel 看图够用」未达成，待 Owner 确认后删除（含 `test_with_portfolios_writes_png`），裁定=未来工程-小型（函数级删除，单批可闭环）。
> - 前端 C4 Container Diagram 未登记（§三.C2 登记项）——「实验历史」作为第 11 个 Container 随前端图一并补，治理面文档项，裁定=未来工程-小型（文档级，随前端 C4 批次）。
> - §八 后续增强（DTW 距离+Returns 相关性 / PBO-DSR 九门禁过拟合检测 / curve_smoothness / DuckDB 查询层 run>100 / Panel Live Server 或社区 HoloViz MCP 接入）——文档已逐项裁定"登记不做/MVP 不做"并给触发条件，非施工缺口，按既定条件评估。
> - §九 BM-RES-02-B 可复现性管理契约（repro_manifest.json 五字段落盘）与 §九 BM-RES-02-C 实验异常检测（PSI+CUSUM+阈值注册表）为 2026-08-12 补登的设计裁定，未落码——裁定=未来工程-小型（契约级，随 C1 verdict 体系升级或实验量达标后启用，重评条件=日均 run≥50）。

# Panel「实验历史」Tab + MLflow 退役施工计划

> 状态: 工作计划（**已施工**，M2 三工作流 2026-08-16 全部落地；剩余=PNG 退役 pending + §八 后续增强登记项）
> 日期: 2026-08-08
> 作者: AI 提议，用户已裁定方向（Panel 集成 + MLflow 退役）
> 关联: #ARCH-OBS-EXP-TRACK-001（实验跟踪体系）→ 50_backtest_observability_workplan（上游工作计划）→ 本施工计划
> 前序: 50_backtest_observability_workplan（回测可观测性工作计划，M1 已完成）
> 依据: 50_backtest_observability_workplan §3 ④（M2）+ 用户决策（完全卸载 MLflow / 自建 C1 对比视图）

> **施工进度核验（v1.2.7，2026-08-12 Grep/Glob 实证）**：A/B/C 三工作流**均未启动**——
> ① `_MLflowBackend`（experiment_tracker.py L137）、query.py mlflow 分支（L100/L170）、
> config.py `tracking_uri`/`experiment_prefix`（L45-46）全部仍在；② `experiment_history.py` 未创建，
> app_panel.py 仍 10 Tab（L300-310）无「实验历史」；③ `query.py` 无 `download_artifact`，
> `_get_run_fallback`（L198-226）仍只取 `local_path`（§二.5 缺口仍在）；④ pyproject.toml 无 mlflow
> 声明（§二.2 仍属实，环境级 `pip uninstall mlflow` 未执行）。**§二 Current State Analysis 与代码
> 现状仍完全一致**，施工条件未变，可直接开工。治理侧：#ARCH-OBS-EXP-TRACK-001 注册表标题已含
> "MLflow 退役"（C2-3 部分已做）；50 号 v1.1.0 已按本计划逆转收敛（MLflow 路线标失效）。

> **施工完成核验（v1.2.13，2026-08-16 实际执行）**：A/B/C 三工作流**全部完成**——
> ① A：`_MLflowBackend` 类/query.py 5 个 mlflow 函数/config.py 两字段已删，`pip uninstall mlflow 3.15.1`
> 已执行，`rg "import mlflow|_MLflowBackend" src/zephyr/` 零命中；② B：`experiment_history.py` 已建
> （P0-1 归一化/P0-2 对齐/P1-5 polarity/P1-6 后缀剥离/P1-7 分级降级/P2-8 lru_cache+前50），app_panel
> 注册第 11 Tab，组装冒烟 11 Tab 全通过且 Tab 已列出 run；③ C：2 个 fallback run 重生验证通过
> （旧 8-07 run 按 P1-7 降级正确显示 NAV 缺失），治理登记（translation 5 条目更新+1 新增/capability
> 2 token/ARCH 订正/blueprint v0.2.0）完成，53 测试全绿。顺手修复 2 个预存 bug：RunSummary.passed
> 必填位致 fallback 查询 TypeError 静默返空 + bytes artifact 信息丢失（_get_run_fallback 只取 local_path）；
> 旧 meta artifacts list[str] 格式已做防御。偏差注记 2 项：P1-4 节流——panel 版 MultiSelect 无
> value_throttled 参数（仅文本输入类有），退用 value 绑定；P0-3「看详情」按钮按文档预案砍
> （5-Tab 强依赖持仓/交易，nav CSV 无法重建）。PNG 退役 pending（§七.P2-10 条件 3 用户确认待）。

## 一、Summary（一句话目标）

**在原有 Panel 仪表盘新增「实验历史」Tab，从本地 JSON 读 C1 回测历史并自建开/关双净值对比视图；同时退役 mlflow（移除代码 + 卸载包），存储收敛为单一 FallbackBackend JSON——用户从此只在 Panel 看回测，不再碰 `mlflow ui`。**

两条工作流：
- **A. mlflow 退役**：移除 `_MLflowBackend` + query/config 的 mlflow 分支，存储=单一 FallbackBackend（JSON）；卸载 mlflow 包。
- **B. Panel Tab**：新建 `experiment_history.py`，query.py 增 `download_artifact`，注册到 app_panel.py。

## 二、Current State Analysis（基于实际探索）

1. **mlflow 耦合面**（`rg mlflow src/` 命中 8 文件，但真正 import mlflow 的只有 2 个）：
   - `experiment_tracker.py`：`_MLflowBackend` 类（L137-190，约 54 行）+ lazy import + `_make_backend` 三分支选择。
   - `query.py`：`_list_runs_mlflow`/`_get_run_mlflow` + lazy import + `_MLFLOW_AVAILABLE` 分支。
   - `config.py`：`tracking_uri`/`experiment_prefix` 字段（仅 `_MLflowBackend` 消费）。
   - `c1_runner.py`：**不直接 import mlflow**——只 lazy import `c1_adapter.track_c1_result`（L158），无需改动。
   - `c1_adapter.py`：通过 `get_tracker()` 间接用，不直接 import mlflow；docstring 提"mlflow run"属措辞。
2. **依赖声明**：`pyproject.toml` **没有** observability extras 组、**没声明** mlflow/matplotlib（workplan 声称"已落地"不实，mlflow 是手动 `pip install` 的）。→ 无需改 pyproject。
3. **现有 2 个 run**：在 `.runtime/tmp/mlflow_m1_9_test.db` + `mlruns/zephyr-c1-validation/`，是 M1-9 smoke test 的**合成数据**，非生产数据。→ 丢弃后重跑即可，无需迁移脚本。
4. **fallback 目录** `logs/experiment_tracking_fallback/` 当前为空。
5. **query.py 缺口**：`_get_run_fallback`（L198-226）只取 `a.get("local_path")`，但 `log_artifact_bytes` 写的 nav CSV 在 meta 里是 `filename`+`artifact_path`（无 `local_path`）→ **bytes artifact 信息丢失**，必须修复才能让 Panel 读到 nav CSV。
6. **models.py 类型 bug**：`RunDetail.artifact_paths` 声明 `dict[str,str]`，但 query.py 赋 `list[str]`——预存不一致。本次在下载层做防御性处理，不顺带修 models（超范围）。
7. **前端范式**（`task_progress.py` 范式）：`fetch_xxx(source)→dataclass` + `render_xxx(data)→dict payload`，payload 含 `_layout`（panel 对象）；`pn=None` 时返回纯 dict 便于测试断言。
8. **掘金 5-Tab**（`render_backtest_performance`）：只支持单曲线，workplan §4 明确"不碰"。C1 双曲线对比视图须自建于 `experiment_history.py`。
9. **C1 artifact 契约**（`c1_adapter.py` 固定）：`nav/nav_curve_baseline.csv`、`nav/nav_curve_experiment.csv`、`report/c1_summary.md`。CSV 格式 = `to_csv(index=True, header=["nav"])`（index 列 + nav 列）。
10. **C1 metrics 契约**（`_extract_metrics`）：顶层 `baseline_sharpe`/`experiment_sharpe` 等 + 每个 verdict 三元组 `<name>_baseline`/`<name>_experiment`/`<name>_passed`（name = verdict.name 小写归一化）。

## 三、Proposed Changes

### 工作流 A：mlflow 退役

#### A1. `src/zephyr/experiment_tracking/experiment_tracker.py`
- **删** `_MLflowBackend` 类（L137-190 整段）+ lazy import mlflow 块（L50-56）+ `_warn_once`/`_warned_fallback`（仅 mlflow 降级用）。
- **改** `_make_backend`（L224-237）：删 mlflow 分支，简化为 `enable_tracking=False→_NullBackend` / 否则 `FallbackBackend(fallback_dir)`。
- **改** `available` 属性（L239-242）：改为 `return self._config.enable_tracking`（不再依赖 mlflow）。
- **改** docstring/注释：把"MLflow 薄包装""mlflow 未装→降级"改为"单一 JSON 后端"。
- **保留**：`RunContext`、`ExperimentTracker`、`_NullBackend`、`get_tracker`、`reset_tracker` API 不变（c1_adapter/c1_runner/tests 依赖稳定）。
- 文件头 `[DEPENDENCIES]` 去掉 `mlflow(optional)`，`[INVARIANTS]` 改为"单一 FallbackBackend JSON；enable_tracking=False→NullBackend"。

#### A2. `src/zephyr/experiment_tracking/query.py`
- **删** lazy import mlflow 块（L37-44）+ `_MLFLOW_AVAILABLE`。
- **删** `_list_runs_mlflow`（L92-114）+ `_get_run_mlflow`（L164-195）+ `_exp_name`（L51-53，仅 mlflow 用）+ `_row_to_summary`（L76-89，仅 mlflow 用）。
- **改** `list_runs`/`get_run`：直接调 fallback 分支（去掉 `if _MLFLOW_AVAILABLE` 判断）。
- **修** `_get_run_fallback`（L198-226）：`artifact_paths` 改为收集完整 artifact 描述（含 bytes artifact 的 `filename`+`artifact_path`），不再只取 `local_path`——为 B 工作流的下载提供定位信息。
- **改** 文件头 `[DEPENDENCIES]` 去掉 mlflow/pandas，`[INVARIANTS]` 改为"单一 JSON 源"。
- **改** docstring：去掉"屏蔽 mlflow vs JSON"措辞，改为"统一查询本地 JSON 实验记录"。

#### A3. `src/zephyr/experiment_tracking/config.py`
- **删** `tracking_uri`（L45，仅 mlflow 用）+ `experiment_prefix`（L46，仅 mlflow 用）字段。
- **改** `load_config`：删 `ZEPHYR_TRACKING_URI` 读取（L55）。
- **保留** `fallback_dir`/`enable_tracking`/`artifact_logging`（fallback/Null 用；`artifact_logging` 留作未来开关，低风险）。
- 文件头 docstring 同步去掉 mlflow 环境变量说明。

#### A4. 环境
- `pip uninstall mlflow`（mlflow 不在 pyproject，仅环境级）。
- 清理：`.runtime/tmp/mlflow_m1_9_test.db`、`mlruns/` 目录、`.runtime/tmp/nav_curve_comparison.png`（mlflow smoke test 残留）。⚠️ 清理命令 + gitignore 确认见 §七.P2-9。

#### A5. 测试更新 `tests/experiment_tracking/test_experiment_tracker.py`
- `TestExperimentTrackingConfig`：`test_defaults`（L58-63）去掉 `tracking_uri`/`experiment_prefix` 断言；**删** `test_load_config_custom_uri`（L77-81）。
- `TestExperimentTrackerBackendSelection`：`test_mlflow_unavailable_uses_fallback`（L193-205）→ 重命名为 `test_enabled_uses_fallback`，断言 `isinstance(tracker._backend, FallbackBackend)`（现在恒为真）。
- 类 docstring "三 backend"→"两 backend（Fallback/Null）"；模块 docstring 同步。
- `test_c1_adapter.py`：检查是否有 mlflow 断言（探索显示其用 spy/duck-type，预期无需改；执行时确认）。

### 工作流 B：Panel「实验历史」Tab

#### B1. `src/zephyr/experiment_tracking/query.py`（续 A2）
- **新增** `download_artifact(run_id, component, artifact_path, filename, config=None) -> Optional[bytes]`：
  - 路径 = `{fallback_dir}/{component}/{run_id}/{artifact_path or ""}/{filename}`，读 bytes 返回；不存在/读失败返回 None + warning（契约一致：查询失败不抛）。
  - 加入 `__all__`。
- **新增** `download_artifact_text(...)` 薄包装（返回 str 或 None），便于直接读 c1_summary.md。

#### B2. 新建 `src/zephyr/frontend/dashboard/components/experiment_history.py`
- **设计参考**（v1.2.2 补，来源前端可视化讨论线 2026-08-02 调研）：屏幕布局可参考 [backtest-kit/ui](https://github.com/tripolskypetr/backtest-kit)（`@backtest-kit/ui`，2026-08 开源回测仪表盘，React18 + Material-UI + Lightweight Charts，5 小时前更新活跃）。该项目屏幕设计专为回测可视化——portfolio cards / KPI boards / candlestick+signal overlays / strategy heatmap / markdown reports / dump explorer，与「实验历史」Tab 需求高度重叠（KPI 卡片网格 ↔ 指标 diff 卡片；列表+详情切换 ↔ run 列表+多选对比；Markdown 报告折叠 ↔ c1_summary.md）。**参考其布局思路，不引入其代码**（技术栈 React/JS vs 本项目 Panel/Python，且它配套自家 backtest-kit 引擎）。
- **数据模型**：
  - `@dataclass ExperimentHistoryData`：`runs: list[RunSummary]`、`component: str`。
  - `@dataclass C1ComparisonView`：`run_id`、`run_name`、`start_time`、`passed`、`verdicts: list[C1VerdictRow]`、`nav_baseline: list[float]`、`nav_experiment: list[float]`、`metrics_diff: dict`、`summary_md: str`。
    - ⚠️ 字段按 §七.P0-2 调整：`timestamps: list[str]` → 拆为 `timestamps_baseline` + `timestamps_experiment` + `alignment_warning: Optional[str]`；按 §七.P1-7 增 `degraded_reason: Optional[str]`。
    - ⚠️ nav 值按 §七.P0-1 归一化后存入（原始值不保留）。
  - `@dataclass C1VerdictRow`：`name`、`baseline`、`experiment`、`passed`、`detail`（从 metrics 三元组解析）。
- **fetch**：
  - `fetch_experiment_history(component="c1-validation", config=None) -> ExperimentHistoryData`：调 `query.list_runs(component)`。⚠️ 缓存 + 前 50 条兜底见 §七.P2-8。
  - `fetch_c1_comparison(run_id, config=None) -> Optional[C1ComparisonView]`：调 `query.get_run` + `query.download_artifact` 读两条 nav CSV（`pd.read_csv(io.BytesIO, index_col=0)["nav"]`）+ 解析 verdict 三元组（找 `*_passed` key → 配对 `_baseline`/`_experiment`）+ 读 `report/c1_summary.md`。
    - ⚠️ 施工顺序：读 CSV → **§七.P0-1 归一化**两条 nav → **§七.P0-2 时间轴对齐校验** → **§七.P1-6 后缀剥离解析 verdict**（勿用 split）→ **§七.P1-7 分级降级**（按 nav 缺失情况设 `degraded_reason`）。
- **render**（panel 可用→payload 含 `_layout`；不可用→纯 dict）：
  - `render_experiment_history(data) -> dict`：左侧 run 列表（`pn.widgets.Tabulator` 或 `Select`，列=run_name/start_time/passed/baseline_sharpe/experiment_sharpe）；右侧详情占位。⚠️ 列表支持**多选**做横向对比（§七.P1-4）。
  - 用 `pn.bind` 绑定选择回调：选 0 个→空状态；选 1 个→`fetch_c1_comparison` + `_render_c1_comparison`（双曲线）；选 2-N 个→横向指标表格（§七.P1-4）。
  - **C1 对比视图**（`_render_c1_comparison(view) -> pn.Column`）：
    - 顶部：若 `view.degraded_reason` 非空 → `pn.pane.Alert(reason)`（§七.P1-7）；若 `view.alignment_warning` 非空 → 次级 Alert。
    - 双净值曲线叠加图（plotly Scatter，baseline 蓝/experiment 橙，复用 `backtest_performance.py` 暗色调色板 `_BG/_BLUE/_ORANGE` 等——从该模块 import 常量，避免重定义）。⚠️ 画图前数据已按 §七.P0-1 归一化 + §七.P0-2 对齐；x 轴用对齐后交集时间戳。y 轴：长跨度（>3 年）用**对数刻度**（equal vertical = equal percentage，避免早期被压扁；来源 alphanume.com 2026-06「How to Plot an Equity Curve」），短跨度线性即可（v1.2.0 补）。
    - 四项 verdict 对比表（plotly Table 或 pn.pane.Markdown 表格：指标/baseline/experiment/通过✅❌）。
    - 指标 diff 卡片（sharpe Δ、maxdd Δ、turnover Δ、calmar Δ，红绿色编码）。⚠️ Δ=experiment-baseline + `_METRIC_POLARITY` 正负向（§七.P1-5）。
    - "看 baseline/experiment 详情"按钮 → 重建 `_MinPortfolio` 喂 `render_backtest_performance`（§七.P0-3，**施工前先勘探 5-Tab 入参契约**，不可降级则砍按钮）。
    - c1_summary.md 折叠面板（`pn.pane.Markdown`）。
  - 空状态：无 run → `pn.pane.Alert("暂无 C1 实验记录。跑一次 C1（track=True）后会在此显示。")`。
- **文件头**：完整 `[BLUEPRINT]`/`[MODULE]` 元数据（MOD-L08-001，D_FRONTEND，CONSUMERS=app_panel，DEPENDENCIES=panel/plotly/pandas/zephyr.experiment_tracking.query），`__all__` 导出 fetch/render/dataclass。
- **降级**：`query` 调用全 try/except，失败显示空状态不抛（与现有 Tab 一致）。

#### B3. `src/zephyr/frontend/dashboard/app_panel.py`
- import `fetch_experiment_history`/`render_experiment_history`（L94-124 区块后追加）。
- 新增 `_tab_experiment_history(self)` 方法（仿 `_tab_task_progress` L228-231 范式：fetch→render→`payload.get("_layout") or pn.pane.Markdown(...)`）。
- `build_tabs` 的 `tabs_spec`（L300-311）在"回测结果"后插入 `("实验历史", self._tab_experiment_history)`。
- 文件头 docstring "10 个 Tab"→"11 个 Tab"。

#### B4. 新建 `tests/frontend/dashboard/components/test_experiment_history.py`（路径按现有测试布局，执行时确认目录）
- `fetch_experiment_history`：用 `FallbackBackend` 写 2 个 mock C1 run 到 tmp_path → 断言列出 2 条。
- `fetch_c1_comparison`：写 1 个含 nav CSV + verdict metrics 的 run → 断言解析出双 nav 曲线 + 4 个 verdict 行。
- `render_experiment_history`（pn=None）：返回 dict payload，断言含 runs 列表。
- `_render_c1_comparison` 纯函数：构造 `C1ComparisonView` → 断言 plotly figure 含 2 条 trace（baseline/experiment）。
- 用 monkeypatch `load_config` 指向 tmp_path fallback_dir，避免污染 logs/。

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-RES-02-A | 实验记录与对比 | 工作流 B 实验历史 Tab（B1-B4：list_runs 列表 + 多选横向对比）+ 工作流 A 单一 JSON FallbackBackend 存储（实验记录落盘）+ B2 C1 对比视图（`_render_c1_comparison` 双净值叠加 + verdict 对比 + 指标 diff） | design 待施工 |
| BM-BT-07-G | 回测结果对比 | §七.P1-4 多 run 横向对比视图（指标表格行=run 列=sharpe/maxdd/calmar/turnover/passed + 可选雷达图）+ B2 C1ComparisonView 双净值叠加对比 | design 待施工 |

### 工作流 C：数据重生 + 治理 + 提交

#### C1. 重生 fallback JSON run
- 跑 C1 smoke test（`.runtime/_smoke_m1_9_mlflow.py` 改名/调整为 fallback 版，或直接 `run_c1_mock(..., track=True)`）→ 在 `logs/experiment_tracking_fallback/c1-validation/{run_id}/` 生成 2 个可对比 run（含 nav CSV）。
- 验证 `query.list_runs("c1-validation")` 返回 2 条。

#### C2. 治理登记（项目硬约束）
- `module_translation_registry.yaml`：登记 `experiment_history` plain_zh="实验历史"。
- `capability_canonical_file_registry.yaml`：登记新组件 + creation_token。
- `architecture_issue_registry.yaml`：更新 `#ARCH-OBS-EXP-TRACK-001` status（M2 完成；mlflow 退役说明）。
- blueprint `blueprint_experiment_tracking.md`：同步"单一 JSON 后端"（去 mlflow）。
- `app_panel.py`/`experiment_history.py` 文件头元数据自检（MOD-L08-001 归属）。
- **前端 C4 Container Diagram 待登记**（v1.2.2 补，来源前端可视化讨论线）：将来用 C4-PlantUML 画前端 Container Diagram 时，「实验历史」作为第 11 个 Container 登记（D_FRONTEND 域，CONSUMERS=app_panel，DEPENDENCIES=query/panel/plotly）。注：C4 是通用架构图方法（非前端专用），项目后端已有 C4 组件图（`docs/02_enterprise_architecture/target_architecture/diagrams/` 4 个 C4 组件图 + 5 个序列图），**前端缺 Container Diagram**——此 Tab 随前端图一并补，闭环"纸面 vs 实际"断层。

#### C3. 提交
- 经 `GitCommitGateway` 提交（项目唯一合法入口；不用 `--no-verify`）。
- pre-commit 门禁全量通过。

## 四、Assumptions & Decisions

1. **mlflow 完全卸载**（用户选择）：移除 `_MLflowBackend` 代码 + `pip uninstall mlflow`；存储=单一 FallbackBackend JSON。`mlflow ui` 命令从此不再需要——用户只在 Panel 看回测。
2. **2 个 smoke-test run 丢弃重跑**：它们在 `.runtime/tmp/`（合成数据），非生产数据，无迁移价值。
3. **C1 对比视图自建**于 `experiment_history.py`，**不碰掘金 5-Tab**（workplan §4 约束 + 用户选择）。
4. **保留 c1_adapter 的 PNG 生成**：`_render_nav_png` 是 mlflow-UI 变通方案，mlflow 退役后无消费方，但移除会扩范围触碰 c1_adapter+其测试。本次**保留**（matplotlib 缺失自动跳过，零风险），列为后续清理项。⚠️ 退役触发条件见 §七.P2-10（Panel 双曲线图上线 + 测试全绿 + 用户确认 → 删 PNG）。
5. **models.py 类型 bug 不修**：`RunDetail.artifact_paths` dict/list 不一致是预存问题，超范围；下载层做防御性处理。
6. **`artifact_logging` 字段保留**：虽当前未消费，但属配置旋钮低风险；本次不顺带删（避免连带改测试）。tracking_uri/experiment_prefix 明确 mlflow 专属，删除。
7. **依赖声明**：pyproject 本就无 mlflow，无需改；panel/plotly/pandas 已是核心依赖，新组件零新增依赖。
8. **交互方式**：Panel Tab 用 `pn.bind` 绑定 run 选择回调（动态更新详情），与现有静态 Tab 不同但属 Panel 标准用法；pn=None 时返回 dict 保证可测。
9. **G0.5 过渡层定位**（v1.2.2 补，来源前端可视化讨论线 `docs/_working/frontend_visualization_discussion.md`）：本 Tab 属 **G0.5 Python 过渡层（开发工具/回测眼睛）**，非 G1 正式前端（React 网页版）。现有 Panel 仪表盘（10 Tab + 本 Tab = 11 Tab）即"高度集成前端"的 G0.5 形态——一个入口、多 Tab 联动，不另起 React。将来升级 G1 时，`fetch_c1_comparison` 返回的 dataclass（数据契约）可复用，render 层会重写。此定位防"纸面 VIEW-10 vs 实际 Panel"断层重演（项目最大架构认知差：架构文档说前端未建，实际 Panel 在跑）。

## 五、Verification（验证步骤）

1. **单测**：`pytest tests/experiment_tracking/ tests/frontend/dashboard/components/test_experiment_history.py -v` 全绿。⚠️ v1.2.0 补充断言：① P1-4 节流——"快速连选 3 个 run → 仅触发 1 次回调"；② P1-7 CSV 鲁棒性——"nav CSV 损坏/缺 `nav` 列 → `degraded_reason='NAV CSV 解析失败'` + Alert 显示"。
2. **mlflow 残留检查**：`rg "import mlflow|_MLflowBackend" src/zephyr/` 无命中（仅 docstring 历史提及可接受，执行时清理为"tracking run"措辞）。
3. **端到端**：跑 C1 mock 生成 2 个 fallback run → `python -c "from zephyr.experiment_tracking.query import list_runs; print(list_runs('c1-validation'))"` 返回 2 条。
4. **Panel 可视化**：`panel serve src/zephyr/frontend/dashboard/app_panel.py --port 5006` → 浏览器「实验历史」Tab 列出 2 个 C1 run → 选中 → 见双净值曲线叠加 + 四项 verdict 表 + 指标 diff + summary 折叠。
5. **降级**：`ZEPHYR_EXPERIMENT_TRACKING=0` 跑 C1 → 不写文件不抛；Tab 显示空状态。
6. **pre-commit 门禁** + **GitCommitGateway** 通过。

## 六、不做（边界）

- ❌ 不做历史 mlflow run 迁移脚本（smoke 数据丢弃重跑）。
- ❌ 不碰掘金 5-Tab 绩效组件（`backtest_performance.py`）。
- ❌ 不修 models.py 预存类型 bug。
- ❌ 不接入其余五零件（workplan ⑥，另一里程碑）。
- ❌ 不做历史结果回灌（workplan ⑤）。
- ❌ 不移除 c1_adapter 的 PNG 生成（留作后续清理）。

---

## 七、施工流程/算法补遗（10 个编号项；v1.1.0 在 P1-4/P1-7 内各补 1 项内容）

> 来源：2026-08-08 全网搜索 + 对照本计划逐条审查
> 分级：P0 必须补（影响正确性）/ P1 应该补（影响完整性）/ P2 建议补（影响可维护性）
> 落点：均落在工作流 B（`experiment_history.py`），不改动 A/C

### P0-1　NAV 归一化算法（落点：B2 `_parse_nav_csv` / `fetch_c1_comparison`）

**缺口**：原计划只读 nav CSV 存为 `nav_baseline`/`nav_experiment` 两个 list，未归一化。baseline 与 experiment 初始净值可能不同（1.0 vs 1.0001），直接叠加会误导。

**补法**：

```python
def _normalize_nav(nav: list[float]) -> list[float]:
    """归一到起点 1.0，消除初始净值差异。"""
    if not nav or nav[0] == 0:
        return nav
    base = nav[0]
    return [v / base for v in nav]
```

- `fetch_c1_comparison` 解析后对两条 nav 各调一次 `_normalize_nav`，归一到起点 1.0。
- `C1ComparisonView.nav_baseline`/`nav_experiment` 存归一化后的值；原始值不保留（双曲线对比只需相对走势）。
- 单测：`[1.0, 1.1, 1.21]` 归一化不变；`[100, 110, 121]` → `[1.0, 1.1, 1.21]`；空/首点 0 → 原样返回。

### P0-2　时间轴对齐算法（落点：B2 `C1ComparisonView` / `fetch_c1_comparison`）

**缺口**：原 `C1ComparisonView.timestamps` 只有一个 list，隐含假设 baseline/experiment 时间戳完全一致，无校验。

**补法**：
- `C1ComparisonView` 字段改为 `timestamps_baseline: list[str]` + `timestamps_experiment: list[str]`（不合并）；增 `alignment_warning: Optional[str] = None`。
- `fetch_c1_comparison` 增对齐校验：
  - `len(ts_b) == len(ts_e)` 且逐项相等 → 用 `ts_b` 作 x 轴（正常路径，无 warning）。
  - 长度不等或存在差异 → 取**时间戳交集**对齐两条 nav，设 `alignment_warning="baseline/experiment 时间轴不一致，已取交集对齐"`。
  - 交集为空 → 走 P1-7 降级（不画双曲线）。
- 画图 x 轴用对齐后的 `timestamps`（交集）。
- 单测：一致→无 warning；长度差 1→交集对齐 + warning；完全错位→降级态。

### P0-3　Portfolio 重建算法（落点：B2 "看详情"按钮回调）

**缺口**：原计划提"重建最小 Portfolio 鸭子对象喂 `render_backtest_performance`"，但重建算法完全未写——掘金 5-Tab 需要哪些字段？nav CSV 只有 `date,nav`，持仓/交易统计从哪来？

**补法**（先勘探 `render_backtest_performance` 真实入参契约，再定最小鸭子）：

1. **勘探**（施工第一步，禁止跳过）：读 `backtest_performance.py` 的 `render_backtest_performance` 签名 + 其内部访问的 Portfolio 属性（`portfolio.nav`/`portfolio.positions`/`portfolio.trades`/`portfolio.metrics` 等），列出**最小必需属性集**。
2. **最小鸭子**（基于勘探结果，预期形态）：

```python
@dataclass
class _MinPortfolio:
    """从 C1 run 的 nav CSV + metrics 重建的最小 Portfolio 鸭子对象。
    仅满足 render_backtest_performance 的净值/指标 Tab；
    持仓/交易 Tab 数据缺失时由 5-Tab 自身降级显示。"""
    nav: pd.Series          # 从 nav CSV 重建，index=date
    metrics: dict           # 从 run.metrics 取（sharpe/maxdd/calmar/...）
    # positions/trades 不重建（CSV 无此数据）→ 5-Tab 持仓/交易页显示空状态
```

3. **降级策略**：若 `render_backtest_performance` 强依赖 positions/trades 且无法降级 → "看详情"按钮**禁用**或点击提示"此 run 仅有净值数据，深度持仓分析请在回测结果 Tab 跑实时回测"。
4. **施工顺序**：先勘探→定最小鸭子→若 5-Tab 不可降级则砍"看详情"按钮（不硬做）。
- 这是 P0 但**风险可控**：最坏情况是砍按钮，不影响双曲线对比主功能。

### P1-4　多 run 横向对比（落点：B2 `render_experiment_history` 左侧列表）

**缺口**：用户要"指标对比"=多 run 横向比，原计划只有单 run 内部 baseline vs experiment。

**补法**：
- 左侧 run 列表支持**多选**（`pn.widgets.MultiSelect` 或 Tabulator `selection`）。
- 选 2-N 个 run → 右侧切换为"横向对比视图"：指标表格（行=run，列=sharpe/maxdd/calmar/turnover/passed/时间）+ 可选指标雷达图（plotly）。
- 选 1 个 → 走原 `_render_c1_comparison`（双曲线叠加）。
- 选 0 个 → 空状态提示。
- **节流防抖**（2026-08-08 再审补遗·缺口 A）：多选回调绑 `MultiSelect.param.value_throttled`（鼠标释放时触发）而非 `value`（实时触发），避免用户快速连点多个 run 时连续触发 `fetch_c1_comparison` + 重渲染导致 Panel 卡顿（同类问题曾致 MLflow UI 轮询卡死）。来源：Panel 官方文档「Harnessing Throttling for Performance」原文“the text is only updated when you release the mouse”+ 2026 最佳实践。备注：Panel 当前推荐 `pn.rx` 响应式表达式（比 `pn.bind` 更灵活），可选 `widget.param.value_throttled.rx()` 写法；MVP 先用 `value_throttled` 保证不卡，`pn.rx` 全量迁移列为后续优化（非阻塞）。
- 单测：选 2 个→表格 2 行；选 1 个→双曲线视图；快速连选 3 个→仅触发 1 次回调（节流生效）。

### P1-5　指标 diff 计算 + 正负向语义（落点：B2 `_render_c1_comparison` 指标 diff 卡片）

**缺口**：原"sharpe Δ、maxdd Δ"未定义 Δ 方向 + 正负向颜色编码。

**补法**：
- `Δ = experiment - baseline`（统一方向）。
- 指标正负向表（硬编码于 `_METRIC_POLARITY`，因指标集稳定且小）：

```python
_METRIC_POLARITY = {
    "sharpe": True,    # higher better → Δ>0 绿
    "maxdd": False,    # lower better（maxdd 是负值，越接近0越好）→ Δ>0（更负）红
    "calmar": True,    # higher better → Δ>0 绿
    "turnover": False, # lower better → Δ>0 红
}
```

- 颜色：正向指标 Δ>0 或负向指标 Δ<0 → 绿；反之红；Δ=0 灰。
- diff 卡片显示：`Sharpe 1.8 vs 1.5 (Δ +0.30 🟢)`。
- 单测：sharpe Δ=+0.3→绿；maxdd Δ=-0.05（变好）→绿；turnover Δ=+0.1→红。

### P1-6　verdict 三元组解析边界（落点：B2 `_parse_verdicts`）

**缺口**：原"找 `*_passed` → 配对 `_baseline`/`_experiment`"对 `max_dd` 含下划线 name 会切错。

**补法**：

```python
def _parse_verdicts(metrics: dict) -> list[C1VerdictRow]:
    verdicts = []
    for key in metrics:
        if not key.endswith("_passed"):
            continue
        name = key[:-len("_passed")]  # 后缀剥离，不用 split
        b = metrics.get(f"{name}_baseline")
        e = metrics.get(f"{name}_experiment")
        if b is None or e is None:
            continue  # 不完整三元组跳过
        verdicts.append(C1VerdictRow(
            name=name, baseline=b, experiment=e,
            passed=bool(metrics[key]), detail=""
        ))
    return verdicts
```

- 单测：`max_dd_passed`→name="max_dd"（非"max"）；`sharpe_passed`→name="sharpe"；缺 `_baseline`→跳过。

### P1-7　分级降级渲染（落点：B2 `fetch_c1_comparison` / `_render_c1_comparison`）

**缺口**：原"失败显示空状态不抛"未区分 run 不存在 / run 存在但 artifact 缺失。

**补法**：
- `fetch_c1_comparison` 返回 `Optional[C1ComparisonView]`，`C1ComparisonView` 增字段 `degraded_reason: Optional[str] = None`：
  - run 不存在 → 返回 `None`（列表层过滤）。
  - run 存在但 nav CSV 双缺 → `degraded_reason="NAV 数据缺失"`，nav_baseline/experiment=[]。
  - run 存在但仅 baseline 缺 → `degraded_reason="baseline NAV 缺失"`，只画 experiment。
  - summary 缺 → `summary_md=""`，不显示折叠面板。
  - nav CSV 解析失败（空/损坏/缺 `nav` 列/index 非日期）→ `degraded_reason="NAV CSV 解析失败"`，nav 置空走降级态（2026-08-08 再审补遗·缺口 B；本路径已被 P1-7 降级机制覆盖，此处仅点名触发源，不新增分支）。
- `_render_c1_comparison` 检查 `degraded_reason`：非空时在顶部显示 `pn.pane.Alert(reason)`，其余区域按可用数据渲染。
- 单测：双缺→Alert + 空 nav 区；单缺→Alert + 单曲线。

### P2-8　查询层索引/缓存（落点：B1 `fetch_experiment_history`）

**缺口**：每次开 Tab 全扫 `fallback_dir/{component}/*/run_meta.json`，run 100+ 会慢。

**补法（MVP 轻量版）**：
- `fetch_experiment_history` 加 `@lru_cache(maxsize=1)`（按 component 缓存），失效靠手动 `reset_experiment_history_cache()`（C1 新 run 后调）。
- 列表按 `start_time` 倒序后取**前 50 条**（首页够用，超 50 显示"仅显示最近 50 条"提示）。
- 不引入 DuckDB（见 §八 后续增强 C）。
- 单测：写 51 个 run→list 返回 50 条 + 倒序。

### P2-9　残留清理算法（落点：A4 环境）

**缺口**：原"清理 `.runtime/tmp/mlflow_m1_9_test.db`、`mlruns/`"未明确方式 + gitignore。

**补法**：
- 清理命令（手动执行，一次性，不入脚本）：

```powershell
Remove-Item -Recurse -Force .runtime\tmp\mlflow_m1_9_test.db, mlruns, .runtime\tmp\nav_curve_comparison.png
```

- 确认 `.gitignore` 含 `mlruns/` 和 `.runtime/tmp/`（防 AI 下次把残留当数据提交）。
- 验证：`git status` 无 mlruns/ 相关未跟踪文件。

### P2-10　PNG 退役触发条件（落点：补充 §四.4 决策）

**缺口**：原"保留 `_render_nav_png`"无退役条件，Panel 双曲线图上线后变死代码。

**补法**（补充 §四.4 决策）：
- 退役触发条件（满足即删 `_render_nav_png` + `test_with_portfolios_writes_png`）：
  1. Panel 双曲线图（P0-1 归一化 + P0-2 对齐）上线
  2. `pytest tests/frontend/dashboard/components/test_experiment_history.py` 全绿
  3. 用户确认"Panel 看图够用，不再需要 PNG"
- 登记到 `architecture_issue_registry.yaml` 的 `#ARCH-OBS-EXP-TRACK-001` 条目，记为"PNG 退役 pending"。

---

## 八、后续增强（2026-08-08 全网搜索，登记不做）

> 来源：2026-08-08 全网搜索 2026 年最新量化前端/实验跟踪方案
> 结论：当前"Panel 集成 + FallbackBackend JSON"选择经最新实践验证正确，无需推翻；以下 4 项登记为后续增强，MVP 不做。

### A. DTW 距离 + Returns Correlation（QuantConnect 工业级曲线相似度）
- **来源**：QuantConnect 官方 Reconciliation 文档（live vs OOS backtest 对比）
- **是什么**：用 DTW（动态时间规整）距离 + Returns 相关性，量化两条曲线的"形状相似度"和"幅度差异"。DTW<0.2 算好，相关性>0.8 算好。
- **对 C1 的价值**：当前 C1 verdict 只有 Sharpe/MaxDD/Calmar/Turnover 四项**静态阈值**判定。加 DTW + Correlation 能回答"实验有没有破坏 baseline 的行为模式"——比单纯看 sharpe 数值差更深。
- **建议**：登记为 C1 verdict 的第 5/6 项指标（后续增强），MVP 先不做。理由：需引入 `dtaidistance`/`fastdtw` 依赖，违反"向内收"。

### B. jQuantStats（Polars+Plotly portfolio analytics）
- **来源**：jQuantStats 0.5.2（2026-03 发布，QuantStats 升级版）
- **是什么**：从**价格+持仓**直接算 NAV（不只接受 return series），输出交互式 Plotly 图 + HTML 报告。
- **对掘金 5-Tab 的价值**：掘金 5-Tab 是自建手工指标计算。jQuantStats 提供工业级 portfolio analytics，能补"持仓级分析"（execution-delay、position-level）。
- **建议**：**不引入**。理由：① 掘金 5-Tab 已满足当前需求；② 引入新依赖违反向内收；③ jQuantStats 用 Polars，项目是 pandas 栈，会引入双 DataFrame 引擎。登记为"若掘金 5-Tab 指标深度不足再评估"。

### C. DuckDB 查询层（run>100 时）
- **来源**：DuckDB 金融仪表板（2026-06）+ xetrack（2026-05，SQLite+DuckDB 轻量实验跟踪）
- **是什么**：DuckDB 单文件零运维，可 SQL 查询所有 run。
- **对 FallbackBackend JSON 的价值**：run 到 100+ 时，JSON 全扫描慢，DuckDB 视图层能 SQL 过滤/聚合/跨 run 对比。
- **建议**：**MVP 不做，run 数到瓶颈再做**。理由：① 当前 run 个位数，JSON 扫描毫秒级；② 加 DuckDB=第二查询源，需维护"JSON 真源→DuckDB 派生缓存"单向派生关系。登记为"run>100 时引入 DuckDB 只读视图层"。MVP 阶段先用 P2-8 的 lru_cache + 前 50 条兜底。

### D. Panel Live Server（HoloViz 官方 MCP，开发期可视化验证）
- **来源**：Panel Live Server（2026-06，HoloViz 官方 GSoC 项目）
- **是什么**：HoloViz 官方 MCP server，AI 可直接在对话里渲染 Panel 可视化（validate→show→screenshot）。
- **社区实现补充**（v1.2.8 补，2026-08-12 第4轮搜索）：除官方 Panel Live Server 外，2026-03 已出现三个社区 HoloViz MCP 实现——[panel-viz-mcp](https://github.com/AtharvaJaiswal005/panel-viz-mcp)（15 工具，FastMCP+hvPlot+Bokeh，双向通信）、[HoloViz-MCP-Server](https://github.com/SuMayaBee/HoloViz-MCP-Server)（27 工具，5 层安全校验管线+SQLite 持久化+iframe 渲染）、[holoviz-viz-mcp](https://github.com/ghostiee-11/holoviz-viz-mcp)（23 工具 v0.4.0，Panel embed 模式产出自包含交互 HTML，89 测试）。三者均为 MCP Apps Standard 实现，成熟度已超"官方 GSoC 演示"阶段——接入时可对比选型（官方 vs 社区），holoviz-viz-mcp 的 embed 模式（无服务器自包含 HTML）对本项目单机场景最贴合。
- **对本项目的价值**：100% AI 开发场景下，AI 能在对话里直接渲染/截图验证 Panel Tab，不用用户手动开浏览器。
- **建议**：**值得后续接入**（不阻塞当前 MVP）。理由：与项目"AI 可发现性"治理目标一致，且是 HoloViz 官方工具非外部依赖。登记为"Panel Tab 上线后评估接入 panel-live-server 或社区实现做开发期可视化验证"。

### E. 过拟合检测体系（PBO / DSR / 多重检验校正）
- **来源**：deflated-alpha v0.3.0（GitHub 0scarito，2026-07-26，MIT）+ Bailey et al. PBO/CSCV (2017) + marketmaker.cc 控制实验 (2026-07)
- **是什么**：回测过拟合检测工具包，一个 `audit()` 调用封装 DSR(Deflated Sharpe Ratio) + PBO/CSCV(Combinatorially Symmetric Cross-Validation) + Harvey-Liu haircuts + White's Reality Check + Hansen's SPA。
  - PBO 的 null 是 **0.5**（不是 0）：PBO≈0.5 表示选择过程是抛硬币（过拟合），PBO<0.1 表示有真实信号。
  - 实测误报率（零假设搜索中）：原始"best Sharpe 显著吗"=1.000（每次误报）；DSR=0.001；Harvey-Liu Bonferroni=0.057；White's RC=0.022。
- **对 C1 的价值**：当前 C1 verdict 只有 Sharpe/MaxDD/Calmar/Turnover 四项**静态阈值**判定。这套工具能回答"跑了很多次实验后，这个 sharpe 是不是侥幸"——比 §八 A 的 DTW 更根本（DTW 看曲线相似度，PBO 看选择过程是否可信）。
- **建议**：**MVP 不做，登记为后续增强**。理由：① 属策略验证方法论层，非展示层，不落在 51_panel_experiment_history_mlflow_retirement 施工范围；② 需引入 deflated-alpha 依赖（或自行实现 CSCV，成本高）；③ 需 C1 记录"所有试过的配置"（当前只记最终 run，不记搜索路径），是 C1 verdict 体系的上游改造。登记为"C1 verdict 体系升级时评估接入 deflated-alpha 做过拟合检测"。
- **局限**（v1.2.1 补，来源 CSDN 2026-03）：PBO 自身有三重脆弱性：① 子样本构造偏差（须 Circular Block Bootstrap，滑动窗口违反零均值假设致 PBO 系统性低估）；② 平稳性幻觉（结构性断点如 2020 疫情/2022 加息致 PBO 低估过拟合风险）；③ 搜索空间覆盖不足（网格稀疏区最优解致基准分布失真）。单一 PBO 不具决策鲁棒性，工业实践推荐 **PBO + SRD（Sharpe Ratio Decay，滚动 12M Sharpe 斜率 < -0.03/年 警戒）+ DSR 三维交叉验证矩阵**——接入成本远高于单个 `audit()` 调用。
- **DSR 有效试验数难题**（v1.2.4 补，来源 marketmaker.cc 2026-07 受控实验「How Many Backtest Winners Survive Deflation?」）：DSR fed **raw trial count（试验数 N）** 会**错误拒绝真 edge**——受控实验中真 edge（年化 Sharpe 3.92）被 DSR 错判为不显著（0.748<0.95）。根因："有效试验数"不是单一数字，5 个估计器对同一矩阵**跨 1.6 到 370.0**（差两个数量级）——最小估计下 deflation 几乎失效，最大估计下过度 deflate。正确做法：用 **bootstrap-based 测试**（White's RC / Hansen's SPA）sidestep 有效试验数选择——有效试验数估计本身是开放问题，非"调一个 audit() 就行"。
- **九大门控完整菜单**（v1.2.4 补，来源 Student One 2026-06「The Full Menu: Every Out-of-Sample Test We Run」）：业界已系统化为 **9 个 OOS 门禁**，每个针对不同过拟合失效模式：① Holdout（参数过拟合，最弱）② Walk-Forward ③ Purged K-Fold（CV 泄漏）④ PBO（选择过拟合）⑤ Romano-Wolf（多重检验 FDR 控制）⑥ SPA/Hansen（studentized 多重检验）⑦ MC block-bootstrap（路径依赖）⑧ cluster stability（聚类鲁棒）⑨ FDR（假发现率控制）。本节原记 PBO/DSR/CSCV/White RC/Harvey-Liu **5 种**，补全为 9 门禁完整菜单；其中 PBO 是最贵门禁（0.45× cost multiplier）——完整门禁体系接入成本远超当前展示层范围；C1 verdict 体系升级时按此菜单逐项评估。

### F. 曲线平滑度指标（curve_smoothness，机读曲线质量判定）
- **来源**：july-backtester #151（zachisit，2026-04-30，`llm_verdict.json` PR #153 已合并）
- **是什么**：从净值曲线算 6 个标量 + 一个综合判定（SMOOTH/ACCEPTABLE/ROUGH），让"曲线质量"可机读（不依赖看图）：
  - `smoothness_r2`：log-equity vs OLS 线性趋势的 R²（1.0=完美线性增长，低=锯齿/erratic）
  - `monthly_return_std_pct`：月收益标准差（高=锯齿）
  - `positive_months_pct`：正收益月占比（高=稳健上行）
  - `max_monthly_drawdown_pct`：最大单月回撤（大负值=可见下挫）
  - `longest_flat_streak_months`：最长无新高平台期（≥12=可见平台）
  - `upthrust_count`：离群上涨月数（>3×std，>2=锯齿）
  - `smooth_verdict`：SMOOTH（全过阈值）/ ACCEPTABLE（差 1 项）/ ROUGH（差 2+ 项）；阈值：R²≥0.90 & positive_months≥60% & longest_flat≤11 & upthrust≤2 & max_monthly_dd≥−10%
- **对 C1 的价值**：当前 C1 verdict 只看 Sharpe/MaxDD/Calmar/Turnover 四项**终值**。curve_smoothness 能回答"experiment 的曲线是不是比 baseline 更平滑/更稳健"——两个策略同 Sharpe 可能曲线质量天差地别。与 §八 E 的 PBO 互补：PBO 看"选择过程可信吗"，curve_smoothness 看"这条曲线长得健康吗"。
- **建议**：**MVP 不做，登记为后续增强**。理由：① 属 verdict/指标计算层，非展示层，不落在 51_panel_experiment_history_mlflow_retirement 施工范围；② 需月度重采样（C1 nav 是日频，需 `.resample("M")`），是 c1_adapter 上游改造；③ 6 个阈值面向美股月度策略，需针对本项目策略类型校准。登记为"C1 verdict 体系升级时与 §八 E 一并评估"。

### 验证当前选择正确的搜索证据
| 发现 | 来源 | 对本项目的意义 |
|---|---|---|
| Streamlit vs Panel（2026-04）：Panel 更适合 100+ widget 生产级仪表盘，Streamlit rerun 模型在复杂交互下脆弱 | theneuralbase.com | 选 Panel 集成而非另起 Streamlit，**正确**——项目已有 10+ Tab |
| Qlib 仍用 MLflowRecorder（2026-07） | CSDN/GitHub | 主流量化平台实验跟踪仍走 MLflow 薄包装，"薄包装层"思路与微软 Qlib 一致 |
| Plotly 是 2026 量化交互可视化首选（2026-03） | novaquantlab.com | 掘金 5-Tab + 双曲线图都用 plotly，技术栈对齐主流 |
| 开源量化前端调研（8 项目，2026-08-02）：backtest-kit/ui（回测可视化最贴合，已在 B2 参考）/ Finanalyzer（国产 OpenBB，React+FastAPI）/ Tickflow Stock Panel（A股 Polars）/ QuantMuse（Streamlit）/ FinceptTerminal（C++/Qt 桌面标杆，难嫁接）/ MarketMind（Electron 桌面）/ backtrader-pyqt-ui（PyQt 桌面）/ Investing Algorithm Framework（HTML 报告） | 前端可视化讨论线调研（`docs/_working/frontend_visualization_discussion.md`） | 无完全可直接嫁接的（后端定制化），但 backtest-kit/ui 屏幕设计最贴合→已融入 B2；**Panel 集成仍是正确选择**，不另起 React/Streamlit |
| Streamlit/Dash/Panel 框架对比（2026）：Streamlit 是默认首选（Snowflake 收购，1-3 天出活），Dash 企业级（AG Grid 100万行），Panel 不落后但不主流首选 | usedatabrain.com 2026-06 + freemail.ai 2026-07 | 项目已有 10+ Tab 用 Panel，**不必现在换**；将来 G1 升级再评估 Streamlit/Dash |
| Lightweight Charts 仍是 2026 开源 K线首选（Canvas 渲染 10万+ 点，45KB，Apache 2.0） | hedgeui.com 2026-04 + thefrontkit.com 2026-06 | 项目 memory 已记在用，**继续用对**；本 Tab 用 plotly 做净值曲线不涉及 K线 |
| 桌面 vs 网页裁定：专业机构交易终端桌面版（Bloomberg/TWS/MT5），研究/回测网页版（QuantConnect），趋势混合；用户场景（一人看回测）网页版够用 | 前端可视化讨论线 | G0.5 用 Panel 网页版（已裁定），桌面感留待 G1 评估 Electron/Tauri 包层；与 §四.9 G0.5 定位一致 |
| DSR 有效试验数难题（2026-07）：DSR fed raw trial count 错误拒绝真 edge（Sharpe 3.92 被判 0.748<0.95）；5 估计器跨 1.6-370.0；正确做法用 bootstrap-based（White's RC/SPA）sidestep | marketmaker.cc 受控实验 | 进一步支持 §八 E "MVP 不做"——DSR 有效试验数估计本身是开放问题，非"调一个 audit() 就行" |
| 九大门控完整菜单（2026-06）：Holdout/Walk-Forward/Purged K-Fold/PBO/Romano-Wolf/SPA/MC block-bootstrap/cluster stability/FDR，9 门禁各针对不同过拟合失效模式；PBO 最贵（0.45× cost） | Student One | §八 E 原记 5 种补全为 9 门禁；C1 verdict 体系升级时按此菜单逐项评估，MVP 仍不做 |

## 九、实验域环节裁定补遗（BM-RES-02-B / BM-RES-02-C）

> 作战地图全覆盖补丁（2026-08-12）：研究孵化域 L0 两个 design 环节在此闭合，与 §六"不做"边界、§八 E"MVP 不做"纪律同一条线。

### 9.1 BM-RES-02-C 实验异常检测（design）

- **定位**：实验 run 指标超限时的异常检测→分类→响应（真源默认方案 isolation_forest，产出 E-RS-05 ExperimentAnomaly）。
- **裁定**：🔨 轻量路线——复用现有零件对实验 run 指标做异常检测：**PSI**（因子治理漂移监控既有口径，factor_registry `drift_psi` 字段）+ **CUSUM**（61 号 §3.3 漂移检测既有分量）+ **阈值注册表**（实验指标静态阈值，仿 C1 verdict 四门禁模式）。**显式不上 isolation forest**——理由：单人项目实验量级（当前 run 个位数，MVP 后日增 <10），孤立森林需百级样本才有统计意义，且引入 sklearn 级依赖违反"向内收"（与 §八 E 同一纪律）。
- **降级方案**：检测不可用时 = **Panel 实验历史 Tab 人工巡检**——本计划工作流 B 的多选横向对比表（§七.P1-4）即是人肉异常检测器。
- **重评条件**：日均实验 run ≥50（人工巡检失效、统计量足以支撑 ML 检测器）。
- **契约（设计）**：输入=FallbackBackend run 的 metrics JSON；输出=异常报告（run_id/指标名/观测值/阈值/判定/建议动作）；响应=**标记不暂停**（实验非实盘，无"实验暂停"硬动作）。

### 9.2 BM-RES-02-B 可复现性管理（design）

- **定位**：复现请求→环境快照+依赖锁定+种子管理→结果校验→复现报告（真源默认 env_snapshot=container）。
- **裁定**：复现报告 = **四要素**（超参 + 数据版本 + 代码 commit + 随机种子——[61_lifecycle_multi_ai](61_lifecycle_multi_ai.md) §3.2 核心纪律 3 已定为一键复现硬门禁）+ **pip freeze 依赖锁定**，二者合并即为一键复现包；**不建容器级环境快照**（真源默认 container 不采纳）——与 65 号"不引入沙箱/容器隔离（Docker/WSL 对量化交易开发过重）"裁定呼应；单机 Windows + 单开发者场景，git commit + pip freeze 已可完整重建环境。真源降级口径（环境快照不可用→降级环境记录）在本裁定下即常态路径。
- **重评条件**：出现复现失败实例（同 commit 同种子跑不出同结果）或跨机器迁移需求真实出现时，再评容器/conda-pack 级快照。
- **契约（设计）**：复现包落盘=FallbackBackend run 目录内 `repro_manifest.json`（params / data_version / git_commit / seed / pip_freeze_hash 五字段）；复现校验=重跑后核心指标（sharpe/maxdd）逐位相等。

## 十、修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-08 | 1.0.0 | 初稿落盘 design_memos | 从 `.trae/documents/` 工作稿定稿存入永久区；补 §七 10 项施工算法补遗（P0×3 / P1×4 / P2×3）+ §八 4 项后续增强登记（2026-08-08 全网搜索）；按 design_memo_management_spec §4.2 frontmatter 规范 + 50_backtest_observability_workplan 文档头范式定稿 |
| 2026-08-08 | 1.1.0 | 再审补遗 2 项缺口 | 缺口 A（P1 节流）：P1-4 多选回调补 `value_throttled` 防抖（来源 Panel 官方文档「Harnessing Throttling」）；缺口 B（P2 CSV 鲁棒性）：P1-7 `degraded_reason` 表补“NAV CSV 解析失败”触发源。第二轮全网搜索（A/B 仪表盘 / akquant / khQuant / PostHog / QuantStats）未发现更优方案，现行 Panel+FallbackBackend JSON 选择再验证正确 |
| 2026-08-08 | 1.2.0 | 第三轮再审：结构完善 + 登记过拟合检测 | 4 处调整：①§七标题澄清“10 编号项 + v1.1.0 补 2 项内容”；②§五验证补节流 + CSV 鲁棒性单测断言；③§八新增 E 过拟合检测体系（deflated-alpha PBO/DSR/CSCV/White RC，2026-07 开源）；④§三 B2 双曲线图补对数 y 轴（长跨度 >3 年）。第三轮全网搜索（PBO/DSR/多重检验校正/净值归一化）验证 P0-1 归一化算法正确，无新施工缺口 |
| 2026-08-08 | 1.2.1 | 第四轮再审：登记曲线平滑度 + PBO 局限 | 2 处补充（均落 §八 后续增强，不改施工计划）：①§八新增 F 曲线平滑度指标（july-backtester #151，2026-04，6 标量+SMOOTH/ACCEPTABLE/ROUGH 判定，与 PBO 互补看曲线健康度）；②§八 E 补 PBO 三重脆弱性局限（CSDN 2026-03：子样本/平稳性/搜索空间）+ PBO+SRD+DSR 三维验证矩阵。第四轮全网搜索（PBO/CSCV/DSR/曲线平滑度/对数刻度）验证 P0-1/P0-2 算法正确，核心施工（A/B/C 三工作流 + 10 编号项）无新缺口；新发现 2 项均属 verdict 层非展示层，登记为后续增强 |
| 2026-08-09 | 1.2.2 | 第五轮融合：前端可视化讨论线调研注入 | 3 处融合（来源 `docs/_working/frontend_visualization_discussion.md` 讨论线 + 2026-08-02 开源量化前端调研，非新全网搜索）：①B2 补 backtest-kit/ui 屏幕布局设计参考（tripolskypetr/backtest-kit，2026-08，React18+Lightweight Charts 回测可视化仪表盘，4 轮再审批漏覆盖——屏幕设计专为回测：KPI 卡片/列表详情切换/Markdown 报告，与「实验历史」Tab 重叠，参考布局不引代码）；②§四 Decisions 补第 9 条 G0.5 过渡层定位（本 Tab 属 G0.5 开发工具非 G1 正式前端，dataclass 契约可复用、render 层将来重写，防"纸面 VIEW-10 vs 实际 Panel"断层重演）；③C2 治理登记补前端 C4 Container Diagram 待登记项（C4 通用非前端专用，后端已有 C4 组件图，前端缺，此 Tab 随前端图一并补）。本轮不改 A/B/C 核心施工流程与 §七 10 编号项，仅做设计参考与定位/治理登记层面的融合 |
| 2026-08-09 | 1.2.3 | 第六轮融合：补全 §八调研留痕 | §八验证表补 4 行（来源前端可视化讨论线 2026-08-02 调研，非新全网搜索）：①开源量化前端 8 项目调研结论（backtest-kit/ui/Finanalyzer/Tickflow/QuantMuse/FinceptTerminal/MarketMind/backtrader-pyqt-ui/Investing Algorithm Framework——无可直接嫁接，Panel 集成正确，backtest-kit/ui 已融入 B2）；②Streamlit/Dash/Panel 框架对比（Panel 不落后不必换，G1 再评估）；③Lightweight Charts K线首选（项目已在用，本 Tab 不涉及）；④桌面 vs 网页裁定（G0.5 用 Panel 网页版，桌面感留待 G1 Electron/Tauri 包层，与 §四.9 一致）。本轮仅补 §八验证表留痕，不改 A/B/C 施工流程与 §七 10 编号项 |
| 2026-08-09 | 1.2.4 | 第七轮再审：补强 §八 E 过拟合检测论证 | 2 处补充（均落 §八 E 后续增强，不改施工计划）：①§八 E 补 DSR 有效试验数难题（marketmaker.cc 2026-07 受控实验：DSR fed raw trial count 错误拒绝真 edge，5 估计器跨 1.6-370.0，须 bootstrap sidestep）；②§八 E 补九大门控完整菜单（Student One 2026-06：Holdout/Walk-Forward/Purged K-Fold/PBO/Romano-Wolf/SPA/MC block-bootstrap/cluster stability/FDR，原记 5 种补全为 9 门禁）。验证表补 2 行留痕。第七轮全网搜索（PBO/DSR/多重检验/回测审计 2026-07/08）验证施工层（A/B/C + §七 10 项）算法完整无缺失，新发现 2 项均属验证方法论层，强化"MVP 不做"论证 |
| 2026-08-09 | 1.2.5 | 文件名 discussion_022_panel_experiment_history_tab_and_mlflow_retirement.md → 51_panel_experiment_history_mlflow_retirement.md（段位编号制），内容不变 | 文档体系重排，新旧名对照见 00_index_trading_decision §10 |
| 2026-08-09 | 1.2.6 | 文档头统一：frontmatter 补 title/owner/language，H1 去文件名前缀与 title 对齐；章节编号与正文零变更 | 15 篇有内容文档结构统一（骨架体系收尾），规范真源 01_design_memo_management_spec §4.2 |
| 2026-08-12 | 1.2.7 | 施工进度核验块注入（头部） | 架构审查第 1-2 轮 Grep/Glob 全量实证：A/B/C 三工作流均未启动（_MLflowBackend/query.py mlflow 分支/config.py tracking_uri 仍在；experiment_history.py 未创建；app_panel 仍 10 Tab；download_artifact 未建；_get_run_fallback bytes artifact 缺口仍在；pip uninstall mlflow 未执行）。§二 Current State 与代码现状仍完全一致，施工条件未变。登记 50 号 v1.1.0 已按本计划逆转收敛 + #ARCH-OBS-EXP-TRACK-001 注册表标题已含"MLflow 退役"（C2-3 部分已做）。正文施工计划零变更。另注：本版修正曾遭并发会话回滚一次，此为重放写入 |
| 2026-08-12 | 1.2.8 | §八.D 补三个社区 HoloViz MCP 实现（第4轮搜索） | 2026-08-12 第4轮 WebSearch 新发现：除官方 Panel Live Server 外，2026-03 已出现三个社区 HoloViz MCP 实现（panel-viz-mcp 15 工具/HoloViz-MCP-Server 27 工具/holoviz-viz-mcp 23 工具 v0.4.0 embed 模式 89 测试），成熟度超官方 GSoC 演示；holoviz-viz-mcp embed 模式（无服务器自包含 HTML）对本项目单机场景最贴合。登记性质增强（后续接入时对比选型），不改施工计划 |
| 2026-08-12 | 1.2.9 | 作战地图全覆盖补丁——闭合 BM-RES-02-C（§9.1 实验异常检测轻量裁定：PSI/CUSUM/阈值注册表，不上 isolation forest，重评=日均 run≥50）、BM-RES-02-B（§9.2 可复现性管理：四要素+pip freeze 即一键复现包，不建容器快照）；新增 §九，原 §九 修订记录顺延为 §十 | 实验域 2 环节补裁定，复用既有零件不新增依赖；施工计划 A/B/C 零变更 |
| 2026-08-12 | 1.2.10 | 作战地图环节映射补强——锚定 BM-RES-02-A | 工作流 B 末尾补映射块，环节级可追溯 |
| 2026-08-12 | 1.2.11 | 作战地图环节映射补强②——锚定 BM-BT-07-G 回测结果对比（§七.P1-4 多 run 横向对比 + C1ComparisonView 双净值） | 映射块补一行，环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.2.12 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-04）——B2 设计参考尾句过程性叙述删除（注入过程已由 v1.2.2 修订记录承载）；§八.E 三条"这进一步支持 MVP 不做"冗余收尾口号删除（"MVP 不做"裁定在条目内已声明，理由保留） | 8 类扫描 4 处（类别 2 过程性叙述×1、类别 5 冗余修饰×3）；施工步骤/算法/契约/参数零丢失 |
| 2026-08-16 | 1.2.13 | 施工完成核验注入（头部 v1.2.13 块）：A/B/C 三工作流全部完成实际执行——A=mlflow 代码删除+pip uninstall 3.15.1；B=experiment_history.py 建成+app_panel 第 11 Tab 注册冒烟通过；C=fallback run 重生验证+治理登记完成。53 测试全绿；顺手修复 2 个预存 bug（passed 必填位 TypeError 静默返空/bytes artifact 信息丢失）；偏差注记 2 项（P1-4 节流 value_throttled→value、P0-3 按钮按预案砍）；PNG 退役 pending（条件 3 待用户确认） | 51 号计划闭环——experiment_registry 施工前提（FallbackBackend JSON + Panel experiment_history.py）已达成 |
| 2026-08-16 | 1.2.14 | 浏览器实测抓 2 个 widget 层 bug 修复：① MultiSelect.options value 放 RunSummary 对象致回调 `TypeError: unhashable`（param.value 返回 value 非 label——options value 改 run_id + by_id 解析 + 契约回归测试锚定，pn=None 测试路径覆盖不到 widget 绑定故施工期未暴露）；② 多选横向对比表 `ReferenceError: Tabulator is not defined`（Tabulator JS 走 CDN，单机离线渲染失败——按 B2 文档备选方案改 plotly go.Table，离线零新增）。Playwright+Chrome 终验：单选双曲线/多选对比表/降级 Alert 全 ✅，控制台零异常；54 测试全绿 | 同 v1.2.13 commit 线追加；另记 IDE 内嵌浏览器会注入 /@vite/client（404 被当 JS 解析→SyntaxError→假白屏），Panel 验证须用 Playwright+本机 Chrome 或常规浏览器 |

---

## 十一、前端 C4 Container Diagram 登记（2026-08-20）

> §三.C2 登记项闭环（AI-NIGHT-001 包 Q2 派单）：前端 C4 Container Diagram（容器图，C4 模型第 2 层——可独立运行/部署单元的职责与依赖视图）尚未成图，按既定口径将「实验历史」Tab 登记为前端第 11 个 Container 的**描述登记**（文字级 C4 条目，成图时直接转 C4-PlantUML）；登记后"纸面 VIEW vs 实际 Panel"断层在册收敛。

**Container 条目（第 11 个 Container）**：

| 字段 | 内容 |
|---|---|
| Container 名称 | 实验历史 Tab（Experiment History Tab） |
| 所属系统/域 | D_FRONTEND 域——Panel dashboard 前端（G0.5 开发工具定位，非 G1 正式前端，§四.9 既定） |
| 载体文件 | `src/zephyr/frontend/dashboard/components/experiment_history.py`（production；creation_token=auto-frontend-experiment-history-20260816） |
| 职责 | 实验 run 的列表/详情/多选横向对比 + C1 双净值对比视图（baseline vs experiment 净值叠加 + verdict 指标 diff），是 FallbackBackend JSON 实验记录的唯一可视化消费面 |
| 技术栈 | Panel（pn）+ plotly（go.Figure/go.Table，离线零 CDN 依赖）+ pandas |
| 依赖（DEPENDENCIES） | `experiment_tracking/query.py`（list_runs/get_run/compare_runs/download_artifact 统一查询面）+ `experiment_tracking/models.py`（RunSummary/RunDetail）+ panel + plotly |
| 消费方（CONSUMERS） | `app_panel.py`（注册为第 11 Tab）；用户=Owner 复盘与 AI 开发期验证 |
| 数据存储 | 只读消费 `logs/experiment_tracking_fallback/{component}/{run_id}/` JSON + artifacts（不写） |
| 降级行为 | 查询失败/无 run→友好 Alert 降级面板（不崩 dashboard，§七 P1-7 degraded_reason 口径） |
| 既有同域 Container | 掘金 5-Tab 等前 10 个 Tab（Container 1-10，app_panel 既有注册） |
| 关联治理锚点 | #ARCH-OBS-EXP-TRACK-001（M2 完成）/ blueprint_experiment_tracking.md v0.2.0 / module_translation_registry plain_zh="实验历史" |

**登记口径注记**：① C4 为通用架构图方法（非前端专用），项目后端已有 4 个 C4 组件图（`docs/02_enterprise_architecture/target_architecture/diagrams/`），前端 Container Diagram 成图（C4-PlantUML）仍属后续批次——本节先行固化条目内容，成图时零返工转写；② 本 Tab 在 C4 分层中的准确位置=Panel dashboard 这一 Deployable 内的 Container 级视图单元（11 Tab 同进程同部署，"第 11 个 Container"为项目内部口径，非 C4 严格"独立部署单元"语义——保持与 §三.C2 原登记措辞一致，标**待实证**：成图时若按 C4 严格语义应落为 Component 级，届时一并校正措辞）。
