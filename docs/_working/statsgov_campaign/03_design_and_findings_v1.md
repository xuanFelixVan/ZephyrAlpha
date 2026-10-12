---
ttl: task_bound
completes_when: 统筹/Owner 完成晨间包四件待裁项并给出六族帽值与主分母口径后，本件升正式版进 catalogs/
---

# 令 C 统计合法性班 · 设计稿与发现 v1（st-statsgov-20261012）

出品件：`01_f06_dsr_restatement_v1.yaml`（折减重述，机生）·`02_trial_budget_inventory_v1.yaml`（六族试次消耗，机生）
·`trial_budget_registry_draft.yaml`（预算册规则真源：族定义/口径声明/映射表，手改面）
·生成器 `scripts/backtest/statsgov_deflation_and_budget.py`＋自家测试 `tests/backtest/test_statsgov_deflation_and_budget.py`（10 passed）
— 注：生成器与测试已写好并全绿，但**未入库**（TRANSLATION-COVERAGE 的 loader 只读投影册、无 PG 第三源，投影落后账本 ⇒ 判"缺 plain_zh"；因 Owner 禁出"重打投影袋"，本班不带他车道登记的 1,506 行净增，改挂晨间包 M6 呈路由）。五件产物已落地 commit 2993a8e4，按 §7 命令可原样复现。

大白话：本批"最好的策略"是从 10,080 格里挑出来的。挑这个动作本身就会把分数抬高。本件量出
抬高了多久，并给出三样东西：① 每个分母口径下"及格线"该画在哪；② 按那些线，这批格子还剩
几格过关；③ 全仓六类挖矿各已经烧掉多少次试次——为下一步给每类定预算。

## 1. 令卡三数核实（实测，非引用）

| 令卡叙述 | 实测真源 | 判定 |
|---|---|---|
| F06 362,880 格 | `grid_20260916-123551/summary.json` n_raw=362880，同批 evaluated=10080；声明源 `config/position_recipe_grid_schema.yaml:6`＋`scripts/backtest/factory_grid_executor.py:2060`＋`tests/trade/position/test_position_recipe_compiler.py:132` | **口径误置**：362,880=名义设计空间（折叠 F/J/K 后），不是实跑次数。实跑=10,080 |
| 幸存者 Sharpe 1.72 | `data/strategy_intake/f06_survivors.csv:2` is_sharpe=1.721；出生批 manifest max=1.721（同分并列 fbfed6a29a5a，E5 已去重） | 成立（=best-of-10,080，IS 窗 2020-01-01..2023-12-31，net_days=1106） |
| OOS 0.831 | 同行 oos_sharpe=0.831（窗 2024-01-01..2025-08-31） | 成立；但同册另有 E4 自算真 OOS 拼接 0.859 / WFA 全路径 0.594 / 折均 0.704——四个数并存，登记面未注明谁是判据 |

补充前提修正：该幸存者 **已判不通过**（`data/backtest_artifacts/runs/E4-F06-38b453ca/verdict.md:9-13`：OOS/IS=0.499<0.70 硬否决 + OOS 精确 DSR 0.3046/0.0027<0.5，can_deploy=False）。本班只重述不改判。

## 2. 折减重述主表（全部由生成器实测，非手填）

分母口径集（每个都带出处与"这尺会往哪边偏"）：

| 口径 | N | DSR≥0.95 所需年化 Sharpe（T=970 / T=1106） | 全批 10,080 格过线条数 | 幸存者 1.721 |
|---|---|---|---|---|
| N_eff 登记位（相关性折算） | 9 | 1.6185 / 1.5152 | **2** | 过 |
| 出生批实评 | 10,080 | 2.8308 / 2.6483 | 0 | 不过 |
| N 账本累计（HEAD 字节面） | 26,767 | 2.9523 / 2.7617 | 0 | 不过 |
| N 账本累计（主区盘面面，含他车道在途条目） | 38,262 | 2.9953 / 2.8018 | 0 | 不过 |
| 账面 + 水位线后漏计 | 66,001 | 3.0595 / 2.8617 | 0 | 不过 |
| 账面 + 磁盘全部未入账 | 91,352 | 3.0970 / 2.8967 | 0 | 不过 |
| 名义设计空间 n_raw | 362,880 | 3.2505 / 3.0400 | 0 | 不过 |

同表另附剪发夏普（Harvey-Liu bonferroni 与 HLZ t>3.0 两式，官方件 `haircut_sharpe_harvey_liu`）逐格读数，见 01 号件 `candidate_restatement`。

## 3. 四条非显然结论

1. **换分母不改排行榜，只改过线与否。** DSR=Φ(z(SR,T)−E_max(N))，E_max(N) 对同批所有格是同一常数 ⇒ 名次位移与 N 无关。机生证据：01 号件 `rank_shift_by_caliber._order_invariance_across_N.distinct_orderings_across_calibers=1`；本批 131 候选中 92 个名次变了，**全部因逐格样本数 T 不同**（net_days∈{970,1106}），与选哪把尺无关。⇒ 预算册因此把统一口径写进**门**，不写进**榜**。
2. **PBO=0.4429（替代批实测）。** 同子空间 `grid_20261010-210933` 的 970×10,076 逐试验收益矩阵，CPCV 8 组取 4（70 折，委托 `cpcv.generate_cpcv_splits`/`compute_pbo`）：IS 最优格在 44.29% 的折里样本外跑输中位数。这是"挑最好的"这件事本身的失败率，量级上等于抛硬币。诚实边界：替代批与出生批配方交集实测 **0 个**，所以它不能重述 1.721 那一格，只能回答同一子空间的结构性问题。
3. **格子之间几乎是同一注。** 1,600 列等距子样的平均两两相关 ρ̄=**0.634**；由 ρ̄ 解析折算 N_eff≈1.58，官方熵广度估计器子样给 7（与登记位全量估计 7 同量级）。⇒ 相关结构真实存在、"独立试验数远小于格数"成立；但 N_eff 是由**被选中的同一批数据**估出来的，选择依赖，禁作唯一分母（在册风险声明见 01 号件 caliber_register.N_eff_registered.risk）。
4. **登记的两个 DSR 值不可复算。** 在 γ=κ=0 口径下：dsr_raw 登记 0.3002 vs 复算 0.3938（Δ−0.0936，反解需 T=960）；dsr_eff 登记 0.9593 vs 复算 0.9809（Δ−0.0216，反解需 T=910）。登记册未记 T/N/矩三项出处 ⇒ 无法证真也无法证伪（不等于数值必错，等于**没有复核路径**）。这正是 RB-STATS-01 证据充分性闸要防的形态。

## 4. PBO 对本班输入是否可算：不可算，三层卡点

| 层 | 卡点 | 证据 |
|---|---|---|
| 名单层 | `f06_survivors.csv` 只有 1 行，`compute_pbo` 要求 n_trials≥2 | `src/zephyr/backtest/core/cpcv.py:234` |
| 逐期层 | 出生批 `grid_20260916-123551/` 只有 manifest/negatives/summary/dual_dsr 四件，**无 net_returns.parquet**（该产物晚于此批才加） | 目录实测；本仓 56 个 grid 目录有 parquet，最早 grid_20260917-001854 |
| 成对层 | 其余成绩册只有每候选一组 (IS,OOS) 标量 ⇒ n_splits=1，PBO 退化成 0/1 | `docs/_working/fexam/grid_strategy_oos_v1.yaml`、`codesym_strategy_exam_v1.yaml` |

要真算 PBO：同空间同 seed 重跑出生批并持久化 net_returns.parquet ⇒ 属数据/算力依赖（非本班"零数据依赖"范围），已挂晨间包呈批。本班已把 PBO 管线在替代批上打通并留下可复核配置（8 组/4 折/70 split/无 purge 的理由=矩阵是日净收益非标签窗）。

## 5. 三条试次漏计通道（现网仍在；本班只量化不修，理由见末段）

| # | 通道 | 位置 | 面积（实测） |
|---|---|---|---|
| 1 | exploration 分支与 N 账本记账互斥 | `scripts/backtest/factory_grid_executor.py:2745` `if not smoke and _EXPLORATION_LEDGER:` … `:2769 elif not smoke:` | 走探索分册的批次只追探索账、**整批不进 N 账本**：10-10 的 232435/233721 两组分片共 10 批 = **27,423 次** |
| 2 | 分片批次 batch_id 撞名 | `:2798-2804` record_run 用 `f"grid_{summary['run_ts']}"`，而 6 个分片的 run_ts 完全相同 | 三组分片撞名：run_ts 20261007-032540 / 20261010-232435 / 20261010-233721（后者 6 分片≈24,960 格）——通道 1 修好后仍会漏 5/6 |
| 3 | 台账自动同步自 2026-09-15 未再运行 | 账本 `screen_runs.last_synced_at=2026-09-15T05:43:43Z`，`sync_screen_counts` 无人调 | screen 面试次冻结在 269 |
| 4 | **护栏把账本的合法整册 CAS 写常驻拒掉** | `src/zephyr/shared/io/file_utils.py:596-622` `registry_mass_edit_guard`：预算=`max(1, ceil(旧行数×0.5%))`，329 行的册=**2 行**；而 `_cas_update` 是整册 `yaml.safe_dump` 重放，长 note 折行＋`previous` 嵌套块被重排 ⇒ 删除行数 >2 必拒 | `.runtime/audit/safe_write.jsonl` 实测该册自 09-22 起 **refused 1,690 次**（10-09 单日 1,150 次）；`n_trials_effective` 披露位因此冻结在 `2026-10-07T10:59:22Z value=16`；调用方 `except Exception` 只 warning ⇒ **静默** |

量化：`--verify-counts` 官方报告=批次 68 / 在账 12 / **缺账 14** / 水位线前已知缺口 42 / 台账无产物批 37；生成器按磁盘逐批实测=未入账 56 批 **53,090 次**，其中水位线后 **27,739 次**＝27,423（通道 1 的探索分片）＋316（10-11 四批小跑）。分母虚低 ⇒ 每批结果都显得比实际更显著（同族病根 09-27 记档、10-08 复记、10-11 追记护栏因由，本次是第四次同形并已定因）。

通道 4 决定了一条次序：**补账之前先让账本写得进去**。护栏自带的放行口径是"批量编辑请走外科脚本/裁定通道并显式传 `allow_mass_edit=True`"（`:622`），但把该旗常挂在 `TrialLedger._cas_update` 上等于为该册永久拆闸；按本仓"改喂给闸的输入而非弱化闸"的正解，应改**追加型外科写入**（只插入新条目行，不整册重放），净删除行数判据的标定修正已在册移交维护线（护栏标定不属本班域，未代修）。

**为什么本班不当场修**：`scripts/backtest/factory_grid_executor.py` 与 `tests/research/backtest/test_l2_gpu_landing.py` 等件正被 `st-deadcure3b-chief-20261011` 等车道持有在途未落地字节（进场时 `lock_files.py cleanup` 现场所列）。袋=整档快照，我改它会把他们的未落地内容扫进我的 commit（归属篡改），或他们后落地时把我的修复静默抹掉。正解=按 §5 呈批通道定车道与顺序。

## 6. 全局试次预算册设计（交付②）

三层，零第二真源：

- **L0 试次记账**=N 账本（`trial_ledger_registry.yaml`，写入口 `TrialLedger` 唯一）。不动、不另记。
- **L1 预算治理**=本册：族→帽→消耗→状态。族消耗=L0 的 `batch_records.kind` **按映射表聚合派生**（02 号件实测：A=exam_card 34＋册面 1,660；B=grid 31,878 账面＋53,090 磁盘未入账＋重考/复验 81；C/D/E/F 由成绩册行数派生）。规格件已含 `ledger_kind_coverage` 自检（账本里存在但没归族的 kind=漏计，反向差集=零触发）。
- **L2 折减判据**=口径声明（`caliber_declaration` 段）：主尺=全仓累计可审计试次（**跨族合并**，防止"换个族再挖一遍把分母清零"）；N_eff 只披露不作分母；名义空间禁作分母只作最保守对照；0.95 线沿用在册裁定（2026-09-15 不放水到 0.90）；PBO 门值留 null，但在册既有值 0.05（`correlation_overfitting_audit.py:64`）列为待裁候选——同域重复簇按 §4.2 应收敛唯一。

帽值全 null=`pending_adjudication`（判据面不自裁，令 C 纪律）。状态机三态：`UNSET_FAIL_CLOSED`（无帽可挖但每批出声"该族无帽"，禁静默扩张）/ `BLOCKED_AWAITING_RULING`（达帽停批，禁靠放宽口径续跑）/ `DENOMINATOR_FORK`（盘面与 HEAD 两读法分母不等时，登记态分母不可信，先收口再判显著——本次实测 26,767≠38,262 已触发此态）。

净零声明（§4.1）：本册不新建记账通道，派生自 L0；`config/search_space_prereg*.yaml` 的 t3_points/墙钟/显存帽=**工程帽**（对象=跑得起），与本册**统计帽**（对象=显著性可信）跨域不同对象→不并，冲突取严；本册只在其上开引用位（B 族 `engineering_caps_referenced_not_duplicated`），不复制数值。

落地路线：今晚只在工作区（task_bound）；帽值与主尺裁定后由生成器 render 正式版进 `catalogs/` 并登记 ROOR——须走册主车道（ROOR 同路径双挂号是本仓在案高危，他班代打投影＝归属篡改面）。

## 7. 复核命令（零写入）

```
python scripts/backtest/statsgov_deflation_and_budget.py restatement --repo-root /d/ZephyrAlpha --head-ledger-root . --out <tmp>/01.yaml
python scripts/backtest/statsgov_deflation_and_budget.py budget --repo-root /d/ZephyrAlpha --spec docs/_working/statsgov_campaign/trial_budget_registry_draft.yaml --out <tmp>/02.yaml
python -m pytest tests/backtest/test_statsgov_deflation_and_budget.py -q
python scripts/backtest/factory_grid_executor.py --verify-counts        # 在册只读对账尺，缺账报红 rc=1
python -c "from zephyr.backtest.core.n_trial_ledger import TrialLedger as T; print(T().cumulative_trials())"   # 分别在工作树/主区跑=两读法
```

同输入两次跑出同字节（本件禁 datetime.now()/time.time()，as_of 取输入 mtime）——机生件可比对。

## 8. 本班限制（如实）

1. 矩（偏度/峰度）按 γ=κ=0 正态近似：出生批无逐期序列可复算矩，先例=`dsr_recalc_backfill.py:approx_dsr_from_sharpe` 同口径。若用真实厚尾矩，DSR 会更低（折减更狠），本表因此是**欠折减侧**的下限。
2. 及格线倒推用 T=970（本批 n_eff_meta common_T）与 T=1106（幸存者可交易天数）两值并列，未取第三值。
3. PG 成绩册面（exam_scores_v1 等 6 表）本班不连库，02 号件报 `PG_NOT_PROBED`——禁止把它读成"零消耗"。
4. 六族清单真源目前只有统筹工作稿 §9.1（本案卷实测：catalog/config 层无唯一真源）；本册是其第一个机器可读形态，若统筹改口径需以统筹为准并同步本规格件。
