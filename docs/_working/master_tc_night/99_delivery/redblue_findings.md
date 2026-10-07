---
ttl: task_bound
completes_when: 红蓝发现表被总包晨会/维护班消纳（P1 修复已落 HEAD、P2 登记项移交后本簿归档）
created: 2026-10-07
sid: st-mastertc-rb
---

# 总包夜战 diff 面 红蓝对抗发现表（st-mastertc-rb，2026-10-07）

> 审查面：`git log --since="2026-10-07 03:00" --grep=st-mastertc` 全部 src/scripts 落地面（17 件已提交）
> + 任务点名的 8 件他队在途件（untracked/staged，owner 责任制只登记不代修）。
> 六维检查：①空集/None/除零 ②注入面 ③假绿 ④fail-open ⑤时区裸 now ⑥裸 getenv/密钥。

## 一、发现表

| # | severity | 文件 | 定位 | 病灶 | 处置 |
|---|----------|------|------|------|------|
| F1 | P1 | src/zephyr/simulation/deflated_sharpe_calculator.py | haircut_sharpe_harvey_liu bonferroni 支 | `p_single=2*(1-Φ(|t|))` 灾难性消去（\|t\|≳6 p 被压低→t_mult 虚高→过剪发）；\|t\|≳8.3 时 1-Φ 下溢 0 且 `1-p_mult/2` 塌成 1.0 → `_inverse_normal_cdf(1.0)` 抛 SimulationError——**合法强信号崩计算链** | ✅已修：p_single 走 `math.erfc`（无消去）+ 新增 `_erfcinv`（渐近种子+Newton，域 (0,1]）以恒等式 `Φ⁻¹(1−q)=√2·erfcinv(2q)` 求 t_mult；补 2 条回归测试（远尾不崩不过剪 + 与 NormalDist 中域对拍 1e-9） |
| F2 | P1 | src/zephyr/backtest/implementations/ch_tick_replay.py | fetch_historical SQL | f-string 内插 symbol/时间串直拼 SQL=注入面（RULE-DATA-OPS 禁拼值；姊妹件 ch_tick_provider 本就参数化） | ✅已修：`%(name)s` 参数化（clickhouse-driver 转义替身，与 ch_tick_provider 同口径）；测试改断言模板+params，新增注入载荷回归测试 |
| F3 | P1 | tests/legacy_zephyr/backtest/test_ch_tick_replay.py | 全文件（HEAD 基线 5 红） | C216 闭卷闸接线（切点=2025-09-09）后，旧测试窗 2026-09-08 属密封区，无 exam_ticket 的研究态读取在闸即抛 ClosedBookViolation——**L7 提交报"72/72 绿"漏跑本 legacy 件** | ✅已修：测试窗移至切点前合法研究段（2025-08-08；adapter 行为测试，闸语义归 test_closed_book_tick_gate），落注记；修后 6/6 绿 |
| F4 | P2 | src/zephyr/gov_enforcement/commit_gates/reconciler_file_ops_gate.py | _check L183-185 | 单文件扫描异常 `return True` 令**整个 gate 对余下文件失明**（fail-open 本身是 ERROR_CONTRACT 明示口径，但盲区放大超出台约） | 登记：建议改 collect+continue（对坏文件仍放行、余文件照扫）；属 L2 车道 C338 面，留维护班 |
| F5 | P2 | src/zephyr/backtest/core/n_trial_ledger.py | sync_t0_manifest_counts._mutate | `_cas_update` CAS 冲突重试会重入 mutate → `state["added"]/["updated"]` 重复追加（账本 records 本身无恙，仅回报面重复）；承袭既有 grid sync 同型 | 登记：回报列表去重或重试外移累计；既有模式，不单代修 |
| F6 | P2 | src/zephyr/ai_layer/scheduling/dispatcher.py | free_window_boost | 跨午夜窗（如 "23:00-01:00"）`start_m<=m<=end_m` 恒 False=窗静默死（保守方向=不加分不抛）；现网 config 02:00-07:00 不触发 | 登记：跨窗语义待 OBJ_R 修订窗补（wrap 判定）；出厂 enabled:false 无行为风险 |
| F7 | P2 | scripts/governance/generators/backfill_created_from_filename.py | main 计数面 | 无收尾 `---` 的 frontmatter 件被计入 has_created_skip（标签失真）；一次性器已实跑完毕（209 件），纯统计语义 | 登记：task_bound 一次性器不再改 |
| F8 | P2 | scripts/governance/generators/library_hygiene.py | filter_new_md_missing_created | 读磁盘工作区副本而非 staged index 内容（staged 后再改的极端序会读新文本）；warn 级恒放行门，精度损失可容忍 | 登记：升硬门位时一并改 `git show :path` |
| F9 | P2 | scripts/backtest/factory_grid_executor.py.tmp.2348.92a504f68dac | scripts/backtest/ 散落临时文件 | safe_write_text 崩溃残骸（项目零临时文件红线精神）；属 st-t3series 车道在途面 | 登记上报不代删（owner 责任制） |
| F10 | P2 | scripts/governance/scheduled_task_reconcile.py | main L241 | `datetime.now().astimezone()` 语义 aware 合规，但字面命中 RULE-SCHEMA-TZ 文本扫描器形态（建议 `datetime.now(timezone.utc).astimezone()` 同Retention件口径） | 登记：下轮顺带统一 |

## 二、他队在途件审查结论（只登记，零代修）

| 文件 | 归属 | 结论 |
|------|------|------|
| src/zephyr/signal_ashare/limit_up/event_axis.py (untracked) | L6/C232 | 干净：fail-closed 校验/eps 容差/互斥单选均落实；P2=date.fromisoformat 接受紧凑式（"20261007"）时归一化未回写横杠式 |
| src/zephyr/signal_ashare/swing_sequence.py (untracked) | L6/C234 | 干净：prev.price=0 除零有卫；极值检测复用 chanlun 单一真源 |
| src/zephyr/signal_ashare/resonance_pair.py (untracked) | L6/C235 | 干净：fired 恒 False 铁律落实，缺件显式降级态 |
| src/zephyr/factor/analysis/tech_factor_pipeline.py (untracked) | L6/C75 | 干净：空面板空 Series 不造信号，白名单双校验 |
| src/zephyr/governance/data_governance/entity_graph_uscc_bridge.py (staged) | C122 | 干净：参数化 SQL（%s）、只读提案器、多义禁自动择一 |
| scripts/governance/check_registry_field_legality.py (staged) | C156 | 干净：只读、退出码契约 0/1/2 与文档一致 |
| src/zephyr/trading/process_reaper.py (staged M) | C324 | 干净：_compute_live_report 零写态、现算失败回退文件不反噬状态通道 |
| scripts/backtest/grid_stats_engine.py (untracked) | st-t3series/G-D | 干净：χ² sf 自实现有界迭代、c* 单调校验、空格 fail-closed |
| scripts/backtest/lead_lag_validator.py (untracked) | st-t3series/G-D.3 | 干净：NaN/Inf 硬拒、分窗 MIN_OBS 卫、零除有卫 |

## 三、蓝队复跑读数

- `python -m pytest tests/gov/governance/red_blue_pkg14 -q`：**5 passed in 3.42s**（复跑 **5 passed in 4.11s**）。
  首轮出现 1 例收集期 ModuleNotFoundError（conftest 旧 `__pycache__` 瞬态，多会话 worktree 并发写场景），
  立即复跑稳定全绿，非代码面缺陷，零修。
- 修复后定向回归：test_deflated_sharpe_calculator.py + test_ch_tick_replay.py **64 passed**（含新增 3 条红队回归测）；
  test_c4_deflated_sharpe_runner.py 8 passed（DSR 委托面无回归）；ruff 4 文件双清。

## 四、修复清单（本车道 git_commit.py 落地）

1. src/zephyr/simulation/deflated_sharpe_calculator.py（F1）
2. src/zephyr/backtest/implementations/ch_tick_replay.py（F2）
3. tests/legacy_zephyr/backtest/test_ch_tick_replay.py（F3）
4. tests/trade/simulation/test_deflated_sharpe_calculator.py（F1 回归测）
