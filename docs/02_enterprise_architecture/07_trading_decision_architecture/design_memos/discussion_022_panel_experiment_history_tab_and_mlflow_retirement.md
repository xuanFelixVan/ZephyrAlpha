---
ttl: permanent
doc_type: architecture_view
status: active
version: "1.1.0"
date: 2026-08-08
topic: panel_experiment_history_and_mlflow_retirement
scope: 07_trading_decision_architecture
parent: discussion_018_backtest_observability_workplan.md
---

# discussion_022 — Panel「实验历史」Tab + MLflow 退役施工计划

> 状态: 工作计划（待施工，M2 实施计划；方向已由用户裁定）
> 日期: 2026-08-08
> 作者: AI 提议，用户已裁定方向（Panel 集成 + MLflow 退役）
> 关联: #ARCH-OBS-EXP-TRACK-001（实验跟踪体系）→ discussion_018（上游工作计划）→ 本施工计划
> 前序: discussion_018（回测可观测性工作计划，M1 已完成）
> 依据: discussion_018 §3 ④（M2）+ 用户决策（完全卸载 MLflow / 自建 C1 对比视图）

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
    - 双净值曲线叠加图（plotly Scatter，baseline 蓝/experiment 橙，复用 `backtest_performance.py` 暗色调色板 `_BG/_BLUE/_ORANGE` 等——从该模块 import 常量，避免重定义）。⚠️ 画图前数据已按 §七.P0-1 归一化 + §七.P0-2 对齐；x 轴用对齐后交集时间戳。
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

## 五、Verification（验证步骤）

1. **单测**：`pytest tests/experiment_tracking/ tests/frontend/dashboard/components/test_experiment_history.py -v` 全绿。
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

## 七、施工流程/算法补遗（审查发现的 10 项缺口）

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
- **对本项目的价值**：100% AI 开发场景下，AI 能在对话里直接渲染/截图验证 Panel Tab，不用用户手动开浏览器。
- **建议**：**值得后续接入**（不阻塞当前 MVP）。理由：与项目"AI 可发现性"治理目标一致，且是 HoloViz 官方工具非外部依赖。登记为"Panel Tab 上线后评估接入 panel-live-server 做开发期可视化验证"。

### 验证当前选择正确的搜索证据
| 发现 | 来源 | 对本项目的意义 |
|---|---|---|
| Streamlit vs Panel（2026-04）：Panel 更适合 100+ widget 生产级仪表盘，Streamlit rerun 模型在复杂交互下脆弱 | theneuralbase.com | 选 Panel 集成而非另起 Streamlit，**正确**——项目已有 10+ Tab |
| Qlib 仍用 MLflowRecorder（2026-07） | CSDN/GitHub | 主流量化平台实验跟踪仍走 MLflow 薄包装，"薄包装层"思路与微软 Qlib 一致 |
| Plotly 是 2026 量化交互可视化首选（2026-03） | novaquantlab.com | 掘金 5-Tab + 双曲线图都用 plotly，技术栈对齐主流 |

## 九、修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-08 | 1.0.0 | 初稿落盘 design_memos | 从 `.trae/documents/` 工作稿定稿存入永久区；补 §七 10 项施工算法补遗（P0×3 / P1×4 / P2×3）+ §八 4 项后续增强登记（2026-08-08 全网搜索）；按 design_memo_management_spec §4.2 frontmatter 规范 + discussion_018 文档头范式定稿 |
| 2026-08-08 | 1.1.0 | 再审补遗 2 项缺口 | 缺口 A（P1 节流）：P1-4 多选回调补 `value_throttled` 防抖（来源 Panel 官方文档「Harnessing Throttling」）；缺口 B（P2 CSV 鲁棒性）：P1-7 `degraded_reason` 表补“NAV CSV 解析失败”触发源。第二轮全网搜索（A/B 仪表盘 / akquant / khQuant / PostHog / QuantStats）未发现更优方案，现行 Panel+FallbackBackend JSON 选择再验证正确 |
