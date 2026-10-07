---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 D：回测考试审计 findings

**审计基准**： git HEAD = `649a8c93c7`（2026-10-07）；一切结论以 HEAD 字节为判准，工作区漂移不计账。被审五提交： `abed5f7a1f`(G-D 引擎袋B)、`90d8e3b33c`(C237 prereg)、`02fc4d72a4`(C216 三件套)、`3f752debdf`(红蓝 P1)、`b0fe4b5940`(token 先行)。审计全程只读（git show/ls-tree/grep/diff + stdin ast 解析 + 纯计算数值复算），零写操作、零状态变更、零 pytest 点火。

## P0 候选

**P0-1｜三卡状态账 vs HEAD 内容失真（假完成簇）**： HEAD 已提交的状态三源（`docs/_working/master_tc_night/99_delivery/交付报告.md`、`docs/_working/master_tc_night/01_skeleton/00_环节总表.md`、L7 workbook 施工记录）对三张卡声称 DONE/GREEN，而内容物在 HEAD（含全历史 `--all`）不存在：

| 卡 | HEAD 状态账声称 | HEAD 字节实证 |
|---|---|---|
| C107 Fill 单一写者 | 交付报告 L82 "Fill 单一写者落地，8/8+装配回归 47/47"；总表 L98 `C107…G` | `scripts/start_paper_session.py` @HEAD 零 `fills_dir`/`process_fill`/`JsonlWriter` 命中（写者腿整体缺席）；实现躺在死袋 q-0004，恢复会话 st-mastertc-recover 全史仅 `abed5f7a1f`(袋B) 一投，q-0004 未恢复 |
| C452 quant_methodology 07/08/12 | 交付报告 L93 "占位骨架落 HEAD"、L177 "占位骨架已在 HEAD"；总表 L97 `G` | `docs/_working/quant_methodology/` @HEAD 仅 01–06+三附录+README，**无 07/08/12**；且 token 册在 `capability_canonical_file_registry.yaml` L45510/45515/45520 已登记指向 `07/08/12_placeholder_skeleton.md` 的三条**悬空 token**（注册表-内容漂移） |
| C233 前视注入红证尺 | 交付报告 L86 "DONE 16/16 绿"；总表 L101 `G`；workbook 施工记录 "tests/backtest/test_lookahead_injection_red_ruler.py 16 测试绿" | `git log --all -- "*test_lookahead_injection_red_ruler*"` 零命中、`git log --all -S` 零内容史、capability 册零 token——该文件**从未进入任何 ref**；盘面仅有 untracked 遗留（属车道残余，不计 HEAD） |

缓解事实：L7 workbook DONE_SUMMARY 本身如实申报过 "内容袋死信待维护班（q-0005/0007/0009、q-0004）"，但 sweep/final2 落卷的交付报告与总表以 DONE/G 覆盖了该保留意见，且袋B 恢复只取了 G-D 七文件中的五个（引擎四件+prereg），C233 测试件与 17 册回填行未随袋恢复。**Owner 视角：HEAD 状态账当前不可信于这三卡，须落地内容或改判状态二择一。**

**P0-2｜HEAD 在册验收钉结构性红（推断，未执行）**： `tests/trade/ex_core/test_fill_jsonl_single_writer.py` 在 HEAD（早于夜战、由 st-cure-p05b `85896a0485` 落地），无 skip/xfail，其静态尺自述"同时构造 `FillHandler(fills_dir=…)` 且调用 `process_fill` 的文件必须恰好一个＝`scripts/start_paper_session.py`"——HEAD 该文件写者腿为零，按其自述判据该尺应红。这是 HEAD 基线上的现实红测试，与 C107 状态申报无关地存在。

## 逐项 verdict（1~6）

### 1. G-D 引擎四件套对照 ext_01 规格 —— 真完成（两处 by-design partial 如实申报）

**四件套实名**（`abed5f7a1f` --stat，1103 行 4 文件）：`scripts/backtest/grid_stats_engine.py`(600行)、`scripts/backtest/lead_lag_validator.py`(195行)、`tests/backtest/test_grid_stats_engine.py`(213行, 16 测试)、`tests/backtest/test_lead_lag_validator.py`(95行, 6 测试)。任务书猜测的"factory_grid_executor.py 接线"**不在四件套内**——该件在 HEAD 存在但属工厂旧批次（账本 kind=factory_grid_batch_a，09-15 起），与 grid_stats_engine 零接线（grep 零命中），与"观察轨/READY_NOT_FIRED 零生产接线"纪律相容。四件套逐件 HEAD 在位 + ast 语法过。

**规格真源**： `docs/_working/total_command_closeout/final_review_chartlib/ext_01_revised_construction_plan.md` G-D.1/G-D.2/G-D.3 行（L97-99）+ `10_wave_plan.md` 10.G-D 行。逐条判据：

| # | ext_01 关键要求 | 判定 | HEAD 证据 |
|---|---|---|---|
| 1 | 每格四件套：样本/夏普/c*/DSR（+胜率） | present | `evaluate_grid`→`CellStats` 全字段（n_samples/win_rate/sharpe_annualized/breakeven_cost_bp/dsr） |
| 2 | Lo2002 自相关修正年化+ddof=0+⚑-2 B 案 244 基准 | present | `lo2002_annualized_sharpe`：√244（`DEFAULT_TURNOVER_DAYS_BASIS` 同源禁√252）、`std(ddof=0)`、Ljung-Box(q=244) 显著才施修、NW1994 截断 `floor(4(n/100)^{2/9})`、n≤q 如实标 `lb_testable=False` |
| 3 | 样本<30 判 INSUFFICIENT-N 单列 | present | `MIN_SAMPLES_PER_CELL=30`；状态复合单列 |
| 4 | c* 二分+单调校验（非单调单列禁静默） | present | `breakeven_cost_bp` 探针单调校验→`C_STAR_NON_MONOTONIC` |
| 5 | DSR 代入有效试验数（禁 Bonferroni 除总格数，C251） | present | n_eff 缺省走 `compute_effective_rank` 熵广度；docstring 明写禁"除以 3700"；DSR 公式零自写全委托 `deflated_sharpe_from_moments` |
| 6 | StepM/SPA 识别全部显著格 | present | `spa_reality_check`（Hansen 2005 recentered lower-bound）+`stepm`（Romano-Wolf 简版，简化点 docstring 如实披露）；红证测试 `test_spa_strong_cell_significant_noise_not`/`test_stepm_identifies_all_significant` 在位 |
| 7 | 滚动重考分半窗+时间外推、事件触发禁 cron | present（排程半面 by-design） | `half_split_reexam` 返回 `reexam_task` 记录由消费方写 tasks 注册；全件零 Timer/cron；tasks.yaml 实登记推迟到波 12 消费方 |
| 8 | 负结果入 negatives.csv | partial | 报告结构内负结果原样保留（leadlag `NOT_SIGNIFICANT` 不删、reexam 保留翻号）；negatives.csv 写者不存在（消费侧面，点火前无对象可写） |
| 9 | 分层（换手×市场状态）只作报告维度 | partial | 引擎无分层代码；prereg 申报 `stratification: evaluation_only_not_in_training`——按 READY_NOT_FIRED 态可接受，波 12 须补 |
| 10 | G-D.1 prereg 轴（族×周期×状态）+E7 预算防火墙 | present | prereg `axes`（candlestick_83+三 pending 族×日/周/月×F4 三态）+`budget_caps`（25000/3700/900/59h/3.5s 对齐 E7）+`e7_defense`（dsr_floating/family_registry_required/ledger_required） |
| 11 | 纪律首行"图形信号只作条件轴"（Marshall 2006） | present | 文件头注释+机器可读位 `chart_signal_as_condition_axis_only: true` |
| 12 | 全试验入 n_trial_ledger（红证=漏记必红） | partial | prereg `budget_caps.trial_ledger` 申报+账本纪律引用；G-D 专属"漏记一例试验必红"红证测试未见（引擎不写账本，依赖 n_trial_ledger 既有纪律） |
| 13 | READY_NOT_FIRED：引擎无点火入口 | present | 模块无 `__main__`；红证测试 `test_ready_not_fired_no_main_entrypoint`（源码字符串断言）在位 |

ext_01 G-D.4 出口三条件之②"日频小样本离线冒烟"在 HEAD 无实证（仅合成数据 16 单测）——但被审卡主张的是引擎落地（C238/C239）而非 G-D.4 出口，状态停在 READY_NOT_FIRED 与此自洽：**过渡（就绪态申报），非缺陷**。

### 2. C237 prereg 冻结 diff==0 复测 —— 真完成

- `git diff 90d8e3b33c HEAD -- config/chart_resonance_prereg.yaml` = **0 行**（复测通过）。
- `90d8e3b33c --stat` 确认该提交仅落此一件（91 insertions）。
- 文件内冻结自校验字段：`frozen_at: '2026-10-07T05:30:00+08:00'`/`frozen_by`/`schema_version`/`status: READY_NOT_FIRED` 在册；**无文件内 sha 自校验字段**（冻结哈希是外部验证：workbook 记 sha256=b341dca0ac360cbc）。审计复算 HEAD blob（`545acfc913`）sha256 = `b341dca0ac360cbcf02dfb626c58e64d5b44e329c7d05c4c7078a60054c47cad`——**与 workbook 申报前 16 位逐字吻合**。
- `config/search_space_prereg_t3b.yaml` @HEAD 在位（`552ac18af5`，st-t3series 队 2026-10-06 袋C）——属他会话在途面，仅记录不计本账。

### 3. READY_NOT_FIRED 真未点火 —— 真完成（真未点火）

- 状态标记真身：prereg L25 `status: READY_NOT_FIRED`；全仓 24 文件命中均为文档/注册表/引擎 INVARIANTS 注记/测试断言，无一处运行态翻转。
- **点火产物零命中**：git 跟踪的台账 SSOT `docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml` 全部 batch_records（grid_20260915…grid_20261006-052748、fexam-strategies-20261006 等）中**无任何 chart_resonance/G-D 批次**；data/ 无 resonance 结果或 negatives 产物（现存 negatives.csv 全为 09-26/09-29 旧工厂批）。
- C33/C34 自告"考试执行器 CLI 不在 HEAD"交叉验证成立：`src/zephyr/governance/meta_question/exam_loop/` 全库件（exam_plan/exam_lifecycle/writeback 等）**无一含 `__main__`/argparse**（exam_plan.py 逐行核实至文件尾）；`scripts/governance/meta_question/wo_b1_examloop/run_exam_loop.py` 是 CLI 但仅 selftest/status/reconcile/upgrade-plan 四子命令，无开考腿；`reexam/a06|dsrhythm` 两个 `__main__` 是单题历史复考脚本，不构成 139/283 批 runner。总表 L183 "139 新题 0 开考"与此一致。**无 CLI+无账本行+无产物三重互证 = 未点火。**

### 4. C216 剪发夏普数值口径抽查 —— 真完成（口径经独立复算成立）

对 `src/zephyr/simulation/deflated_sharpe_calculator.py` @HEAD：
- **(a) bonferroni 闭式**：present。`p_single = math.erfc(|t|/√2)`（=2(1−Φ(|t|)) 精确恒等）、`p_mult=min(1,p_single·N)`、`t_mult=√2·_erfcinv(p_mult)`（即 Φ⁻¹(1−p_mult/2)）。
- **(b) HLZ2016 t>3.0**：present。`HLZ_MULTIPLE_TESTING_T_THRESHOLD=3.0`，`method="hlz_2016"` 恒 t_mult=3.0 且优先于 N=1 特判，出处（HLZ 2016 RFS+案卷 §四.3）注释在册。
- **(c) t_mult>t_single 全剪封顶**：present。`haircut=1.0`→剪后 SR=0；注释明写"禁 clamp 到 0（放水反方向）、不线性外推负 SR（负值须整序列重估）"——诚实地板语义正确。
- **(d) N=1 零剪发特判**：present。`t_multiple=t_single` 精确同值（绕开 cdf→Φ⁻¹ 往返浮点噪声），正确置于 hlz_2016 分支之后。
- **(e) erfc/erfcinv 治本在 HEAD**：present（注释署名 2026-10-07 红队 st-mastertc-rb）。`_erfcinv`=渐近种子两轮自洽+Newton 6 轮（步长 1e-12 早停），域检查 (0,1] fail-closed。
- **(f) 数学正确性（独立复算，从 HEAD 源码提取函数实测）**：恒等式 Φ⁻¹(1−q)=√2·erfcinv(2q) 解析成立；数值对拍 q∈{0.5,…,1e-10} 与 `NormalDist.inv_cdf(1−q)` 12 位一致；q=1e-14~1e-16 时 erfc 路径（7.9413/8.2221）**比** inv_cdf(1−q)（7.9414/8.2095，1−q 塌陷）**更精确**——正是治本点；远尾 p=1e-20…1e-300 往返 `erfc(erfcinv(p))` 相对误差 ≤7.4e-14 零崩；`erfcinv(1)=0`→t_mult=0→全剪（与 Φ⁻¹(0.5)=0 同像）；bonferroni 回收实测 t=6,N=2→t_mult=5.886<6（不过剪不崩）。**恒等式与实现均对。**
- **(g) 7 测试在 HEAD**：present 且为 9（7+2）。`tests/trade/simulation/test_deflated_sharpe_calculator.py` L554-634：C216 原七（bonferroni 单调增/N=1 恒等/[0,1)+恒等式/HLZ 定 3.0/负 SR 原样/fail-closed/frozen）+红蓝补二（`test_far_tail_t_does_not_crash_or_overhair`、`test_bonferroni_t_mult_matches_normaldist_midrange` 交叉对拍）。

### 5. T0 台账+closed_book 接线 —— 真完成

- `T0_BATCH_KIND` 闭合集常量 @`src/zephyr/backtest/core/n_trial_ledger.py` L81（rule_engine/material_line/state_match_matrix 三族）；`sync_t0_manifest_counts` L529（manifest `n_pairs_by_rule_period` 求和、幂等+断点续跑**单调前进禁回退**、缺读数宁少计 warning 留痕 fail-closed——函数体逐行核实）。
- closed_book 真接线：`ch_tick_replay.fetch_historical` 形参 `exam_ticket/audit_path`（L68-69）+ `enforce_closed_book_read` 查库前拦截（L95，注释"SQL 执行次数恒 0"）；`ch_tick_provider.py` L92-114 同构。红蓝批 SQL 参数化（`%(sym)s`）@HEAD 在位。
- xfail 摘帽：`02fc4d72a4` diff 实证删除 6 个 `xfail(strict=True)` 块（-24 行）；`tests/research/backtest/test_closed_book_tick_gate.py` @HEAD = **11 测试、0 xfail**（6 摘帽+5 原绿=11/11 与自告一致）。
- T0 族 5 测试 @`tests/backtest/test_n_trial_ledger_t0_family.py`（闭合集/求和发现/幂等-单调/缺读数跳过/不可读忽略）字节在位。

### 6. 与全景图挂点 —— 相容（挂接缺位=不必要；但总表三卡 G 标失真归入 P0-1）

- `config/strategy_production_map.yaml`、`config/panorama_master_map.yaml`：G-D 引擎/prereg **零挂接**（grep 零命中）。判定：**不必要**——READY_NOT_FIRED 件不进生产图符合纪律（G-D.4 Owner 点火卡才是入图入口）；建议把"补挂生产图"列入 G-D.4 点火前检查单防波 12 遗忘。
- `00_环节总表.md` 回测考试块：C33/C34/C216/C236/C237/C238/C239/C288/C70 行 G 标与 HEAD 落地物相容（F066 回测预注册↔C237、F068↔C238 挂接正确）；回测环节行"139 新题 0 开考"与未点火互证。**失真项**：C233(L101)/C107(L98)/C452(L97) 的 G 标与 HEAD 字节矛盾（见 P0-1）。

## 证据块

```
[提交面]
abed5f7a1f  4 files +1103（grid_stats_engine/lead_lag_validator/两单测）
90d8e3b33c  1 file +91（仅 chart_resonance_prereg.yaml）
02fc4d72a4  7 files +500/-24（haircut+T0+closed_book；-24=6 xfail 块）
3f752debdf  6 files +152/-12（erfc 治本+SQL 参数化+legacy 测试窗移回切点前）
b0fe4b5940  2 registry files +392（token/翻译先行）

[冻结验证]
git diff 90d8e3b33c HEAD -- config/chart_resonance_prereg.yaml → 空（0 行）
HEAD blob 545acfc913 sha256 = b341dca0ac360cbc f02d…（与 workbook 申报前16位吻合）

[未点火三重证]
trial_ledger_registry.yaml@HEAD：batch_records 无 chart_resonance/G-D 批
grid_stats_engine.py@HEAD：无 __main__（红证测试 L209-213 断言）
exam_loop 库件@HEAD：零 __main__/argparse；run_exam_loop.py 无开考子命令

[erfcinv 数值复算（HEAD 源码原样执行）]
√2·erfcinv(2q) vs inv_cdf(1-q)：q≤1e-10 十二位一致；q=1e-15 时 7.94134532617 vs 7.94144448742（erfc 路径为准）
p=1e-300：y=26.2095，erfc(y) 相对误差 4.97e-16
t=6,N=2 → t_mult=5.8864265329（不过剪不崩）

[测试在位计数]
test_grid_stats_engine.py=16（含 READY_NOT_FIRED 红证）
test_lead_lag_validator.py=6；test_n_trial_ledger_t0_family.py=5
test_deflated_sharpe_calculator.py haircut 族=9（7+2）；closed_book=11/0 xfail

[假完成簇反证]
git log --all -- "*test_lookahead_injection_red_ruler*" → 空
start_paper_session.py@HEAD grep "fills_dir|process_fill|JsonlWriter|jsonl" → 空
git ls-tree HEAD docs/_working/quant_methodology/ → 无 07/08/12
capability 册 L45510/45515/45520 → 三 token 指向不存在文件
17_quantified_acceptance.md 末次触达=3bbf966c46e（C250 指针版），§十一无引擎落地行
```

## 小结 + P1/P2 建议

**小结**：车道 D 五项指定审计（G-D 四件套/C237 冻结/READY_NOT_FIRED/C216 口径/T0+closed_book）全部 **真完成**，工程质量高于均值——erfc 治本的数学正确性经独立数值复算成立（远尾全精度、恒等式精确）、prereg 冻结哈希复算吻合、未点火有三重独立证据、测试面与自告读数逐项对上（16/6/5/9/11）。**但夜战总包的状态账存在一个真实 P0 簇**：C107/C452/C233 三卡在 HEAD 已提交的交付报告与环节总表中标 DONE/G，内容物却从未落任何 ref（死袋未恢复+袋B 恢复不完整），且 C452 还留下三条悬空 creation_token、HEAD 基线上躺着一把按自述判据应红的填写者验收钉。这不再是"在途面"，而是**已固化为 HEAD 的失真申报**——恰好落在"文档矛盾=事故"红线上。

**P1 建议**：
1. 三卡二择一收口：把 q-0004（C107/C452）与 C233 测试件真正恢复落地，或将交付报告 L82/L86/L93、总表 L97/L98/L101 改判 dead-letter pending；同步清偿三条悬空 token。
2. `17_quantified_acceptance.md` §十一 G-D 引擎落地行回填（workbook/C251 双处声称已回填，HEAD 无此行）——落卷或修订施工记录。
3. 处置 HEAD 上结构性红的 `test_fill_jsonl_single_writer.py`（随 C107 落地转绿，或临时降级申报），避免污染下一轮全量测试基线读数。

**P2 建议**：
4. workbook C33 移交的试点命令 `python -m …exam_loop.exam_plan --limit 5 --dry-run` 是**悬空指针**（exam_plan.py 无 main 守卫，执行=静默 no-op）——改写为真实入口或标注"须先建 CLI"。
5. G-D.4 点火前检查单建议增补两项：negatives.csv 写者与换手×市场状态分层报告面（现均 by-design 缺位）、strategy_production_map 挂接。
6. 计数类小漂移：fill 写者测试实为 9 个（自告 8）——建议状态账计数一律生成器产出（宪法 §9.5 自家纪律）。
7. workbook 自曝的 capability 册并发 stomper（读-改-写窗口在工具层）值得总包/L3 立专项——本车道 token 行一夜被抹重插两次是实证。
