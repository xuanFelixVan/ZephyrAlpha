---
ttl: task_bound
---

# CNS 接线续跑收口案卷（复算＋定性＋补卷）

- 班次：LANE-CNS 续跑收口车道（总筹会话 st-qmine-20260925 统筹；前任车道撞 150 轮上限身亡、实现件在盘无案卷）
- 判据真源：`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` §七
- 普查真源：`docs/_working/decision_map_campaign_20260924/14_consumption_census.md`
- 电态口径真源：`docs/_working/trading_vision/2026-09-16-skeleton-coverage-audit.md` §一.4（接电三态判据）
- 待落清单：`docs/_working/decision_map_campaign_20260924/cmd_successor_20260925/landing/lane_cns.yaml`
- 纪律声明：本案卷只复算不重做实现；未达线一律写「未达标＋差多少」，禁按设计意图充数。

## 一、实测接入数 vs 判据 ≥20（逐条复算，非按设计意图）

### 1.1 三层计数口径（自数代码与注册面）

| 层 | 口径 | 实测 | 取证方法 |
|----|------|------|---------|
| L1 台账声明层 | `recipes.TECH_FACTOR_RECIPES` 去重指标 ID | **27 指标 / 19 因子 / 37 输出列** | `python -c "wired_indicator_ids()"` 机读复算（真源=`src/zephyr/factor/technical_indicator_factors/recipes.py`） |
| L2 注册面对账层 | factor_registry 内 19 条 FCT-TECH 是否回填 code_path/inputs | **0/19 回填（code_path 全空，status 全 candidate）** | 解析 `factor_registry.yaml` 逐条打印；声明的派生器 `scripts/governance/backfill_registry_consumption.py` **不存在** |
| L3 生产可达层（判据口径） | 实码 **且** 生产事件链/消费实证（§一.4） | **0** | 见 1.2 五件缺证 |

TDM 点名的 7 条（FCT-TECH-061/062/070/071/077/083/085）**全部在 L1 台账内**（`tdm_declared=True` 逐条核），`config/trading_decision_map.yaml` 的 `factor_refs` 引用面（296/1521 行等）与台账一致，未造数。

### 1.2 L3 判"未接电"的实证（五件缺证，逐件在盘核）

1. 日仓不存在：`data/offline_factor_store/`（`bridge.default_store_root()` 生产根）= 无目录 → 因子值零落仓。
2. 唤醒零执行痕迹：`.runtime/factor_tif/`（幂等记号+子进程日志目录，`daily_job.marker_path`）= 无目录。
   时序实证：CH 侧 `c1_market.technical_indicator` daily 已产出 **2026-09-25 / 5559 只**，而实现件 mtime=当日 22:28-22:36、
   本案卷复算时点 22:47——指标任务的 `task_completed` 唤醒早于钩子落地，**今晚必漏一棒，最早首发=下一唤醒点**（非缺陷，是时点，但意味着"零实证"）。
3. IC 取证件不存在：`scripts/backtest/eval_tech_indicator_ic.py`（`bridge.py:5 [CONSUMERS]` 与数据通路注释自declare 的消费方）
   → CNS-01 验收口径"FCT-TECH 至少 3 条出 IC 证据"实测 **0 条**。
4. 尺无自动执行面：`bridge.validate_recipes`（内含 `min_wired=20` 硬闸，正向设计）全仓**零生产调用方**
   （仅 `__all__` 导出）——`daily_job`/`write_daily_snapshot`/`framework_composer` 均不调它，故台账回退不会被自动发现（装饰尺风险，见 memory `decorative-guards-without-callers`）。本班以测试面补尺（§四）。
5. 回归网缺失：`[TESTS]` 头声明的 `tests/zephyr/factor/technical_indicator_factors/test_technical_indicator_factors.py` **不存在**（目录都没有）→ 实现件落地时零测试。本班补该文件（§四）。

### 1.3 列级消费扫描（14 号文普查同口径，供"上架无客"单调下降对账）

`src/ scripts/ config/` 共 5075 个 .py/.yaml 文件全词扫描（排除 producer 层 `data/implementations`、指标域实现 `factor/technical_indicators`、注册表本体、本新包）：

- 27 条接线指标中 **14 条列名零命中**（清单见 §三）；
- 13 条有命中，但命中文件类型=DDL 建表（`scripts/ch/apply_market_tables_ddl.py`）、回填脚本（`scripts/data/backfill_technical_indicator_dwm.py`）、demo（`scripts/backtest/indicator_consumption_demo.py`）与探针（`scripts/data/night_probe.py`）——**均属普查口径的 producer/infra/display 层，非决策消费**；
- 结论：消费面对"上架无客"清单的**实际净减少 = 0**（要等 §三 未接电清单转绿才算下降）。

### 1.4 定性（达标与否）

- 判据"CNS-01 首批 ≥20 指标接入 indicator_reader 消费链"：**L1 名义 27 ≥ 20 成立，但 L3 生产可达 = 0 → 按 §一.4 口径判"未达标"，差 20 条**。
- 电态：接线链的**代码与触发面齐备**（DataScheduler→`wire_data_scheduler`→`task_completed`→`daily_job` 增益钩子；唤醒词 `technical_indicator_incremental` 在 `tasks.yaml:2287` 真实在册；消费端 `framework_composer` multifactor-sleeve 嵌套路被 `daily_decision_orchestrator`/api_server 引用）——
  故不判"缺失"也不判"只有适配器没人调"，判 **"覆盖未接电（挂点已闭、零执行实证）"**：27 条全部记入未接电，转已接电的最小证据链=①一次成功快照落仓（`.runtime/factor_tif` 记号 + 日仓行）②`load_factor_panels` 在 composer 面板非空 ③≥3 条 IC 证据回填注册面。
- 转绿最小工作量与顺序见 §六。

## 二、宏观（cn_macro / D5 需求项 Shibor·利差·美债）实测消费代码条数

判据（17 号文 §七）："cn_macro 接线：D5 宏观需求项（Shibor/利差/美债）**消费代码 ≥3 条落地**"。

### 2.1 表名面复算

- 全仓（`src/ scripts/ config/ tests/`）**`cn_macro` 引用 = 0 文件**（14 号文族⑤"cn_macro 代码 0 引用，至今未变"经本班独立复算**仍然成立**）。
- 宏观值的实际落地面是长表 `c1_market.macro_data`（`akshare_provider.py:1198` 的 `("Shibor", _fetch_shibor_rates, _transform_shibor)` 等 8 个利率类 job 写它）。CH 只读实测（`zephyr.data.ch_reader.query`）：
  - `macro_data WHERE indicator_name LIKE 'Shibor%'` = **520 行**（供数侧活着）
  - `macro_data` max(report_date) = **2026-09-24**
  - `macro_data_vintage` = **16,091 行**（本批新件 `macro_vintage.py` 的存证镜像**已在产**——写侧旁路，`ch_writer.py:1036` 钩子）

### 2.2 三条读取面逐条定性（实测达标数 = 0）

| # | 读取/接线代码 | 性质 | 是否计入"D5 消费条数" |
|---|--------------|------|---------------------|
| 1 | `src/zephyr/data/ch_writer.py:893/1036 _maybe_mirror_macro_vintage` → `macro_vintage.mirror_from_legacy_rows` | 写侧存证镜像（producer 旁路） | **否**（不是消费） |
| 2 | `scripts/governance/meta_question/wo_b3_macro/audit_macro_vintage.py:180/309/315` 用 `PIT_LATEST_SQL` 抽测 | 本模块自证审计（读自己建的表） | **否**（自我循环，无 D5 需求方） |
| 3 | `src/zephyr/data/foreign_market_coverage.py:145/155` 探 `macro_data`（FRED_DXY / FRED_DGS10_US=美债10Y） | 供数覆盖率哨兵（infra 面，普查口径明剔） | **否**（但确是"美债"唯一现存读取面，如实登记） |

- **利差**：全仓无任何利差计算码（`market_china_bond_yield` 表除 DDL 外 0 消费；`scripts/ch/apply_market_tables_ddl.py:595` 建表后无读取方；`treasury/libor/sofr` 命中件=容量保障通道枚举，非宏观值消费）。
- **Shibor**：0 读取方（仅 producer `_transform_shibor`）。
- **美债**：0 决策消费（仅上表 #3 覆盖探针）。

### 2.3 定性

**实测 0 条达标，判据差 3 条**（前任实现的宏观件是"存证/ PIT 读法基础设施"，不是 D5 需求的消费接线——记"覆盖未接电·基础设施"，不充数）。
既有唯一真宏观实链仍是 14 号文族⑤点名的 `plan_engine/overnight_boundary_research`（us_index 隔夜涨跌幅）一条，本批未增。
另：`macro_indicator_registry.yaml` MAC-001~016 15 条**仍全 candidate、无 source_table 供数绑定**（`decision_map.py:104` 只做 macro_refs 对齐校验，不是消费）——CNS-04 宏观族总裁决口径未变。

<!-- SECTION-3:NO-POWER LIST -->

<!-- SECTION-4:TESTS AND RULER -->

<!-- SECTION-5:CONSOLIDATION -->

<!-- SECTION-6:RESIDUAL WORK -->
