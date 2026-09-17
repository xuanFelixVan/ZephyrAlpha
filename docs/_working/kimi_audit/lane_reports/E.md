---
ttl: task_bound
rule_form: report
title: Lane E — S12 自证实验真跑（E1-E8）判读报告
owner: kimi-audit lane E（子代理执行）
created: 2026-09-17
---

# Lane E · S12 自证实验真跑报告

> 规格真源：`docs/_working/kimi_audit/S12_实验规格.md`。判读纪律：每个注入反例必须让对应门禁/不变式**真的变红**；不变红=假绿，记入文末「假绿追加」。
> 执行环境：用户 Python 3.12.8；cwd=仓根；零 git 写操作。改动既存文件仅 `scripts/run_backtest.py`（claim=kimi-audit-e，已 release）。

## 总览表

| 件 | 状态 | 判读 | 产物 |
|----|------|------|------|
| E1 metamorphic 三不变式 | ✅ 直连跑完 | **绿**（9 测试全过，3 条注入反例全红） | `tests/metamorphic/test_s12_metamorphic_invariants.py` |
| E2 CLI 现金对账接线 | ✅ 直连跑完+真冒烟 | **绿**（产物含对账章 within_tolerance=true；产物级反例红） | `scripts/run_backtest.py` 改动 + `tests/backtest/test_cash_ledger_cli_wiring.py` |
| E3 哨兵存活探针 | ✅ 直连跑完 | **红**（2 处哨兵悬空，阳性对照抓到） | `.runtime/tmp/exp/e3/sentinel_probe.json` |
| E4 C4 SCD-2 清单+PIT 闸骨架 | ✅ 交付两件（retrofit 本体不施工） | **宇宙轴对 _c4_engine 族=红（xfail 钉）**；SCD-2 范式=绿；模板族权重轴实测=绿 | `.runtime/tmp/exp/e4/affected_list.yaml` + `tests/backtest/test_c4_pit_universal_gate.py` |
| E5 regime 迟滞四臂 | 🔄 后台在跑（v2） | v1 零鉴别力（归因在案）；v2 全宇宙重跑中 | `.runtime/tmp/exp/e5/`（哨兵 `e5.done`） |
| E6 STD-002 双尺重考 | ✅ 直连跑完 | **62/81 可评；翻转 55 件全可解释；不可解释 0% → 可进 frozen 评审** | `.runtime/tmp/exp/e6/dual_ruler.yaml` |
| E7 极端日场景库+fillability | ✅ 直连跑完 | **红**（2 件涨停收盘买入成交=引擎洞实证） | `.runtime/tmp/exp/e7/e7_result.json` |
| E8 门禁失效探针 | ✅ 直连跑完 | **8 绿+1 真红**（REGISTRY-YAML-PARSE git rc≠0 静默放行） | `tests/governance/test_gate_failure_probes.py` |

---

## E1 metamorphic 增补三不变式（INV-5/6/7）

**落点**：`tests/metamorphic/test_s12_metamorphic_invariants.py`（新文件，9 测试）。合成数据 0.25 网格，不触库不触网。终验：`89 passed, 2 xfailed`（与 E4/E8 同批回归）。

- **INV-5 成本单调性**（佣金/滑点 ×2 → NAV 逐日不增 + 收益差≈成本差 ±5%）：绿。口径修正记录：收益差对照**零成本臂实测摩擦层**（摩擦对费率线性，冲击成本腿两臂相同在差值中抵消）；初版"从 trades_log 反推成本差"因滑点口径假设错误而偏 2.3 倍，已弃用（见假绿追加 §4）。注入反例（成本倒挂曲线）→ 判定器 AssertionError ✓。
- **INV-6 账本闭合**（引擎真跑后 reconcile_cash_ledger 残差≤0.01 且 within_tolerance）：绿。H3/H4 链测试提升为不变式层完成；CLI 路径经 E2 helper 钉（缺 cash_history/缺引擎→fail-closed False）。注入反例两件全红：删一笔成交→False ✓；首笔 total_cost 双计→False ✓。
- **INV-7 市值恒等**（逐日 nav==cash+Σqty×price，缺价结转成立）：绿。spy 取证 update_market_value 同刻快照逐日断言；容差 1e-9 相对（nav_series 存 float 的往返噪声 ≤1e-10，反例差 1 元=1e-7 远在界外，无鉴别力损失）。注入反例（连续 4 日全市场 NaN 缺价）→恒等仍逐日成立 ✓；伪造断裂快照→判定器红 ✓。

## E2 CLI 现金对账接线（S1-T1）

**改动**（`scripts/run_backtest.py`，四点位）：①新增 `_cash_ledger_reconciliation(engine)` helper——复用 `zephyr.backtest.core.portfolio.reconcile_cash_ledger` 真源，缺 cash_history/trades_log/initial_capital → `within_tolerance=False`（fail-closed）；②run_one 产物装配段 `artifact.metrics["cash_ledger_reconciliation"]=...`（tick 臂取 `runner._last_tick_engine`，vectorized/minute 臂取 engine）；③run_one 返回摘要增 `cash_ledger_within_tolerance`；④CLI 打印该行。GT-15 结构闸不受触（对账章是 dict 非时序键，不进 `_collect_timeseries` 名册）——`test_h3h4_cash_pit_exec_chain.py` 25 件全绿复核。

**验收（规格 §E2 写死判据）**：
- 真冒烟：`--strategy topn-momentum --symbols 600519.SH --start 2024-01-01 --end 2024-03-31 --factors momentum_20d` → run_id=`bt-dd63ca61`，equity_points=58，trades=1，`cash_ledger_within=True`。产物 `data/backtest_artifacts/bt-dd63ca61.json` 的 metrics 含 `cash_ledger_reconciliation`：samples=58、trade_rows=1、max_abs_residual=4.68E-11、within_tolerance=true ✓。
- 反例（产物级）：由产物 trade_log 重建 total_cost 流水后**删掉一笔成交**重算 → within_tolerance=False，max_residual=962,373.71 ✓（红得很大）。
- 钉测试：`tests/backtest/test_cash_ledger_cli_wiring.py` 5 件全绿（helper 闭合/缺腿 fail-closed/删成交反例红/接线点结构钉/真源空样本 fail-closed 语义钉）。

## E3 哨兵存活探针（S8-V3 收口）

**落点**：`.runtime/tmp/exp/e3/sentinel_liveness_probe.py`（探针脚本+机读产物 `sentinel_probe.json`+哨兵 `e3.done`）。
**扫面**：tasks.yaml 235 个 task_id（真源面）× src/**/*.py 的 `feed_task` 标签引用 × 注册表/数据配置的任务名形态引用；近 7 日运行记录查 `data/integrator_progress.db.task_runs`（只读）。
**判读=红（符合预期的真红）**：

1. `feed_task: "kline_index_breadth_refresh"`（breadth_freshness_alerts.py:236）→ tasks.yaml 无此 task_id。**阳性对照抓到 ✓**（探针不自证失效）。
2. **新发现第二处**：`feed_task: "breadth_freshness_sentinel"`（同文件 :256）同样悬空——S8-V3 修复面比已知多一件。
3. 近 7 日 task_runs：两件悬空任务 0 行（ dangling 的一致证据，非新信息）。
4. 注册表词形面线索（`*_refresh/*_sentinel` 形态词）全量入 JSON 的 `registry_taskish_dangling_clues`，供后续班次过筛（词形面噪声高，未计入硬红）。

## E4 C4 SCD-2 受影响清单 + 通用 PIT 闸骨架

**交付①清单**（`.runtime/tmp/exp/e4/affected_list.yaml`，grep 实证）：
- 宇宙受害 15 件 = 直接调 `load_hs300/load_index_constituents` 11 件 + 经 `_valuation_engine(universe="hs300"/"zz500")` 4 件（div_high/pb_low/pe_low/pe_zz500）——与 S14-1「11 直接+4 经估值引擎」逐件吻合；`universe="all"` 的 22 件估值族**不受害**（已核）。
- 模板族 7 件 = `factor_strategy_template.py` 本体 + 6 件 fact 消费方。gftd 无宇宙选取调用（指数行情择时），其同 bar 属 S14 V2/V3 另案，不在宇宙轴清单内。

**交付②闸骨架**（`tests/backtest/test_c4_pit_universal_gate.py`，3 绿+1 xfail(strict)）：
- `test_scd2_window_paradigm_pit_green`：fw_backtest SCD-2 范式在「X 后调出 vs 调出不发生」双世界下历史宇宙逐位相同——**绿**（正确范式锚）。
- `test_c4_engine_current_list_universe_pit_gate`：**当前对 _c4_engine 族=红**（双世界产出宇宙差 1 件=M_EXIT），xfail(strict=True) 钉扎——retrofit 落地后 XPASS 强制摘除，不会静默过期。
- `test_template_family_weights_pit_axis`：**实测=绿**（与任务卡「应红」预期不同——S14-3 已修 assemble_weights shift(1)+宇宙前向封闭，权重轴已 PIT 干净；含后置 sanity 防闸无鉴别力）。这是实测纠正预期的判读点，不是漏报。
- `test_affected_list_zero_drift`：清单与仓库实况零漂移钉（retrofit 后会红=提醒退役清单）。

## E5 regime 迟滞四臂对照（S13 F-3 / T1A-6）

**通道结论**：`framework_composer` 的 regime_overrides 回测通道**可直接调用**（FrameworkBacktestConfig.regime_by_date 注入 + regime 日序真源 `fw_backtest.load_regime_series`→`c1_backtest.regime_snapshot_history`，窗口 2024-01..2025-08 覆盖 806 行，新鲜度 2 日）。

**v1 已跑完但判读=无鉴别力**（`e5_result_v1_degenerate.json` 归档）：10 票小池上三方案 12 臂结果逐位相同。归因实证（三步）：迟滞变换有效（56/403 日改写）→ compose 动态覆盖对合成面板有效 → 真跑抓包发现成员面板在小池上**全部退化为等权**（top_n=10≥池大小、default-equity 天然等权、multifactor 同池等权），Σ=1 归一后任意 α 混合产出同一面板。若跳过归因直接报"迟滞收益=0"，就是一次判读级假绿（记入假绿追加 §2）。

**v2 修复在跑**：标的池改 HS300 SCD-2 窗口并集（resolve_symbols 真源），成员面板三方案只建一次、四臂共享（迟滞变换/成本开关仅作用在 compose+引擎层），判据=迟滞收益（开-关，成本计臂）>0 且配对 bootstrap CI(10000 次） 不含零；W2 暴动窗逐臂单列。产物 `.runtime/tmp/exp/e5/e5_result.json` + 哨兵 `e5.done`（完成态见文末「后台进程清单」）。

## E6 STD-SIM-ACCESS-002 双尺重考

**产物**：`.runtime/tmp/exp/e6/dual_ruler.yaml`（脚本 `dual_ruler_reexam.py`，DSR 数学=官方件 `run_deflated_sharpe_batch` 零重写）。
**口径**：v1 尺=DSR>0 @N=4562（全局累计）；v2 尺=DSR>0.5 @N_eff=81+策略历史 num_trials（manifest 真源）。输入=reexam_results.csv 81 行 × sharpe2a_oos_nets 39 件 + 行内在册值。
**判读**：
- 可评 62/81（19 件 status≠ok 或无 OOS nets 序列——逐件标注原因，未硬打分）。
- 翻转 55 件，**全部方向为「v1 放 v2 拒」**：DSR∈(0,0.5] 阈值带所致，与 N 口径无关；每件附 N 单调性校验（N 大→折减强→DSR 不增）全部一致 → 55/55 可解释。
- **「v1 拒 v2 放」=0 件**：裁定预期的"族口径折减减弱救活临界件"方向在本批**一次都没发生**——v2 尺的实际收紧力来自 0.5 阈值而非 N_eff。这是 frozen 评审必须带着走的事实。
- 不可解释件 0/62（0% ≤ 10% 线）→ 判据面**可进 frozen 评审**（但带上上一条）。

## E7 极端日反证场景库 + fillability

**产物**：`.runtime/tmp/exp/e7/e7_result.json`（脚本 `exp_e7_extreme_windows_fillability.py`）。基线三件沿用 S12-exp 机读框架原判据。
**判读=红**：
- 基线：W1 ρ̄=0.30（<0.50 过）；W2/W3 ρ̄=NaN（CAND-e3da6fa7 全零收益，S6 挂起件自证前置不变）；窗 maxDD 全过；无跑输指数 10pp。
- **新增 fillability 真红 2 件**（_c4_engine 向量化 T+1 无涨跌停闸=引擎洞实证）：
  - CAND-4440d07f973f 于 2024-09-25（924 暴动窗次日）买入 601162，当日收盘价=涨停价 3.30（封死不可成交却成交）；
  - CAND-e2e7f033d97c 于 2025-04-10（关税恐慌窗）买入 000016，收盘价=涨停价 4.64。
- 探针自我修正记录：初版把后复权价与原始涨停价直接比较，误报 4 件（4785 vs 7.72 单位错配）；改原始价口径后复核，初版 5 命中仅 2 件为真（601162/000016），另 3 件原始价未封板（误报消除）。fillability 类检查必须单位对齐原始价——记入假绿追加 §3。

## E8 门禁失效探针（S4-F7 收口）

**落点**：`tests/governance/test_gate_failure_probes.py`（8 绿 + 1 xfail(strict)）。fake gateway 的 project_root=tmp_path（审计写隔离，不触生产 .runtime）。

- **探针 1（git diff 故障注入 rc≠0/异常）**：`_diff_helpers._get_staged_py_files`、DATETIME-NOW-FORBIDDEN、UNSAFE-DICT-SPREAD 三件 fail-open 且 WARNING 留痕 ✓；REGISTRY-YAML-PARSE 异常分支有 warning ✓。
- **真红发现**：REGISTRY-YAML-PARSE 的 **git rc≠0 分支静默放行**（`registry_yaml_parse_gate.py:184` `return True, ""` 无 logger.warning——同文件仅异常分支留痕）。xfail(strict=True) 钉扎：修复=rc≠0 分支补 warning，届时 XPASS 强制摘除。
- **探针 2（YAML 破损注入）**：破损 watched 注册表→阻断且只点名该表 ✓（不连坐另一张 watch 表）；非 watch 表破损→放行不连坐 ✓；重复根键→阻断 ✓；合法 capability 注册表→放行 ✓（阳性对照防探针全红误报）。

---

## 假绿追加（本 lane 新发现的判读陷阱/静默通路）

1. **E8 真红**：REGISTRY-YAML-PARSE git rc≠0 静默放行（fail-open 零留痕）——S4-F7「全门禁静默失效的理论路径」在案实证一例，修复点 `registry_yaml_parse_gate.py:184`。
2. **E5 v1 判读陷阱**：四臂零差异若不做归因即报"迟滞无效"=假绿判读；实为小池上成员面板退化等权致实验无鉴别力（鉴别力自检必须前置：双臂输入确实有分歧+输出通道确实敏感，两者本 lane 均已钉）。
3. **E7 探针自体假绿风险**：fillability 初版 hfq/原始价单位错配误报 4 件——反例类探针必须先单位对齐，否则"红"是假的、"绿"也是假的。
4. **E1 INV-5 口径陷阱**：从 trades_log 反推"成本差"撞滑点内嵌口径（偏差 2.3 倍）——可操作口径=零成本臂实测摩擦层；规格"收益差≈成本差"的参照系必须实测不可估算。
5. **E6 方向性事实**：v2 尺的收紧力来自 0.5 阈值而非 N_eff（"v1 拒 v2 放"0 件）——若评审叙事是"族口径救活临界件"，本批数据不支持。

## 结论（≤10 行）

1. E1/E2/E4/E8 四件工程件全落地：21 个新测试全绿 + 3 个 xfail(strict) 真红钉（E4 宇宙轴、E8 rc≠0 静默、均带摘除条件）。
2. E2 冒烟产物 bt-dd63ca61 含对账章 within_tolerance=true；产物级删单反例必红——CLI 现金腿闭环。
3. E3 真红 2 处哨兵悬空（阳性对照 + 新发现 breadth_freshness_sentinel），进数据线索修复队列。
4. E7 真红 2 件涨停封死买入成交——_c4_engine 无涨跌停闸的引擎洞实证，建议进 S14 族 retrofit 范围。
5. E6：55 翻转全可解释、不可解释 0% → 双尺可进 frozen 评审，但须携带"v1 拒 v2 放=0 件"事实。
6. E5 通道可直调已证；v2 全宇宙四臂在跑，结果落 e5_result.json+e5.done（哨兵）。
7. 全部注入反例（删单/双计/倒挂/断恒等/NaN 缺价/破损 YAML/git 故障/涨停成交）均观察到对应闸真红；唯一"不红"是 E8 的 rc≠0 静默——已作真红钉入库。
8. 遗留义务：本 lane 未 commit（零 git 写）；新测试件入库提交时需走 GitCommitGateway 正链 + 模块大白话登记（tests/ 豁免 CREATE-GUARD）。
