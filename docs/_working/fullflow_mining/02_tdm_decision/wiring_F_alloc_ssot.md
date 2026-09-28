---
ttl: task_bound
volume: wiring_F_alloc_ssot
session: st-ailayer-final-20260924
creation_token: w3-f-alloc-ssot-nomination-20260926
---

# W3-F：R-M2-6 配比真源单头化（`pf_alloc`=生效 ／ `auto_mount`=提名）

> 依据：`90_chief_rulings_wave1.md:37` R-M2-6（选①）＋ `91_chief_command_wave1.md` §三.3 接线类第 3 条（无门位）
> ＋ `94_chief_rulings_wave2.md` 门位边界（护栏 only-add 门与 SLE-1 Owner 门位保留不动）。
> 环节真源：总册 F27（E8 组装与资金分配，`partial`）/F48（C1 预算切分，`built`）。
> 工作面=worktree，零提交零入队。**未改任何配比数值、未改风险平价/再平衡判据。**

## 〇、开工前置核实（实测，非记忆）

1. **停手条件未触发**：`git status --porcelain src/zephyr/pf_alloc/` 空＋`git diff --cached --name-only src/zephyr/pf_alloc/` 空
   ＋主区 index `grep -c pf_alloc`=**0** ⇒ pf_alloc 侧**无他在途改动**（92 册 §一.4 把它列禁触是历史预防，本波实测已净）。
   即便如此，本车道**一行未改 pf_alloc 源码**（生效面单头化靠"提名侧改口＋机器闸"实现，不需要动 pf_alloc）。
2. **auto_mount 实体定位**（grep 而非猜）：真身=`scripts/backtest/auto_mount.py`（1045 行）；
   `src/zephyr/**` 内的 `auto_mount` 全是引用（`framework_composer.py`/`translated_strategy_adapter.py`/
   `daily_decision_orchestrator.py:115,538`/`screen_source.py`/`intake.py`/`pipeline_events.py`）。

## 一、现状双头写入链（每条 file:line，施工前实测）

**权重字段真源**＝`config/trading_decision_map.yaml` → `portfolio_plan.sleeves[].weight`
（现值 16 条 sleeve，Σ=1.0，plan_id=PP-001；`aggregator.max_single_sleeve=0.25`）。

### 腿 A｜auto_mount＝写手（现＝事实上的生效面）
| 步 | 动作 | 位点 |
|---|---|---|
| A1 | 新 sleeve 落图，权重写死起步档 `weight: 0.05` | `scripts/backtest/auto_mount.py:592-602`（常量 `NEW_SLEEVE_WEIGHT=0.05` 在 `:101`） |
| A2 | 存量权重原位改写（逐 sleeve 改 `weight` 字段） | `auto_mount.py:729-740`（`rescale_sleeves`） |
| A3 | 写入门＝only-add 语义门（含"新 sleeve 必 0.05 起步"断言） | `auto_mount.py:605-645`（`only_add_assert`，sleeve 面在 `:632-645`） |
| A4 | 真写生产真源文件（CAS） | `auto_mount.py:1006-1024`（`apply_ops`→`only_add_assert`→`safe_write_text(MAP_YAML, ...)` `:1020-1022`） |

### 腿 B｜pf_alloc＝配比计算与落库（现＝把腿 A 的产物降格为"先验"，并可自行造数）
| 步 | 动作 | 位点 |
|---|---|---|
| B1 | 只读 TDM `portfolio_plan` → sleeve 权重先验 | `src/zephyr/pf_alloc/allocation_inputs.py:184-218`（`load_pp001_plan`；路径声明 `allocation_config.py:102` 注"PP-001 sleeve 先验真源（只读）"） |
| B2 | **未命中即造数**：均值先验填充／等权 1.0 | `allocation_inputs.py:221-253`（`:240-242` `pp001_mean_prior_fill`、`:243-245` `equal_weight`） |
| B3 | 分配器归一→target_weight | `src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py:187-273`（入参 `signal_weight` `:119`，出 `target_weight` `:264`） |
| B4 | 编排队列先验→分配 | `src/zephyr/pf_alloc/allocation_orchestrator.py:809`（`build_base_weights`）→`:1084`（`base_weights=base.as_allocator_weights()`） |
| B5 | 落库（生效事实）＝CH 三表 | `src/zephyr/pf_alloc/allocation_persistence.py:141-159`（`alloc_budget_daily`/`alloc_shrinkage_daily`/`alloc_budget_change_log`） |

### 腿 C｜auto_mount 的**第二条声明权**（本案病根的显形，零生产消费者）
- `auto_mount.py:884-914` `allocation_request()` 出参含**归一后目标权** `weight`（Σ=1，`:912`），
  文档字符串 `:887` 自称"本件出**权重来源**"、`:893` 更明说"**归一与约束已在本件闭环，分配链不需重复实现语义门**"
  ＝向 MOD-PA-003 声明"别再算了，听我的"。这与腿 B（pf_alloc 自己算）＝**同一权重的两个作者**，
  落库行不可归因 → R-M2-6 所判 SSOT 违例成立。
- 实测消费面：`grep -rn "allocation_request" src/ scripts/ tests/` → 生产侧**零调用**，
  仅 `tests/backtest/test_auto_mount_sle3.py:241` 读它 ⇒ 属"声明了但没接"的第二头（一旦接线即双头并活）。

### 消费侧（证明"生效"确实外溢）
- 前端全量渲染真源：`src/zephyr/frontend/dashboard/api_server.py:2320-2326`（读同一 TDM 文件）。
- 地图校验门：`src/zephyr/gov_enforcement/commit_gates/decision_map_gate.py:69,86`（地图 YAML 在输入面内）。
- 整装回测权重另有真源：`config/framework_plans.yaml`（`framework_composer.py:105` 注"方案权重+regime_overrides 唯一真源"）
  ⇒ **第三处权重面**（回测装配），与 PP-001 由 `scripts/backtest/generate_framework_plan_from_tdm.py` 单向派生。

## 二、施工口径（提名≠生效，怎么改才不碰数值）

禁区自查：A1/A2 的**数值**（0.05 起步档、等比 rescale 因子）与 B2/B3 的**判据**（均值填充、归一、cap/step、风险平价、再平衡带宽）
一律不动；`only_add_assert`（A3）与 `--rebalance` 的 Owner 门位（SLE-1）**保留原样**。
因此"单头化"只能落在**契约面＋机器闸**，而这恰是病根所在（腿 C 的越权是文字契约，不是数字）：

1. `scripts/backtest/weight_ssot.py`（新建）＝权威声明与探针的唯一位点：
   - `EFFECTIVE_AUTHORITY="pf_alloc"` 单值；`binding` 枚举 `effective`/`nomination`；
   - `make_nomination()` 给权重出参打提名级标记（**只加字段不改数**）；
   - `assert_nomination_not_binding()`＝提名不得声明生效（越权即抛，机械可检）；
   - `find_weight_writer_conflicts()`＝同一权重字段 >1 作者即报（病根判据）；
   - `scan_weight_writers()`＝仓内文本扫描真实作者位点（file:line 可复核）。
2. `auto_mount.py` 侧：腿 C `allocation_request()` 出口套 `make_nomination()`，并把 `:893`
   的"分配链不需重复实现语义门"**改口为"提名仅供 pf_alloc 参考，生效判定归 pf_alloc"**；
   `main()` 写图前串 `assert_nomination_not_binding`＋`find_weight_writer_conflicts`（fail-closed，有真调用者非装饰）。
3. 红测两枚（见 §四）。

## 三、105 格权重矩阵空位清单（实测计数，禁造数填空）

`06_ibt_backtest.md:41` 称"7 态×15 员=105 格全空"。**实测现状与册面不符，以盘上为准**：
regime 态真源=`zephyr.regime.core.regime_detector.REGIME_STATES`=7（r1/r2/r3/r4/r10/r11/r12）；
`config/framework_plans.yaml` 成员并集=**16 员**（非 15，含 STR-* 与 sleeve 名混编）。

| 方案 | 成员 | 基准权重格 | regime 覆盖格（7×N） | 已填 | 空 | 空位的漏供腿 |
|---|---|---|---|---|---|---|
| fw-defensive | 8 | 8/8 | 56 | **32** | 24 | r1/r2/r11 三整行缺（24 格） |
| fw-balanced | 7 | 7/7 | 49 | **28** | 21 | r1/r2/r11 三整行缺（21 格） |
| fw-aggressive | 8 | 8/8 | 56 | **32** | 24 | r1/r2/r11 三整行缺（24 格） |
| fw-tdm-current | 16 | 16/16 | 112 | **0** | 112 | `regime_overrides` 段整体不存在 |
| 合计 | 16（并集） | 39 | 273 | **92** | **181** | — |

腿归因（可复核）：
- **r1/r2 空＝设计内**，非漏供：`daily_decision_orchestrator.py:115` 注"r1/r2 震荡态不路由=宁漏勿误"，
  且 `auto_mount.py:129` `R2SIX` 键集={r10,r4,r11,r3,r12} 确无 r1/r2。⇒ 无供数腿，**禁填**（填=造数）。
- **r11 空＝真漏供候选**：`R2SIX` 有 r11→accumulation（`auto_mount.py:129`）、六段相位有供数腿，
  但三个 `fw-*` 方案的 `regime_overrides` 均未落 r11 行（3×7+... 共 23 格）。
- **fw-tdm-current 112 格全空**：该方案是 TDM PP-001 的镜像件（`x_tdm_provenance` 字段在），
  其空位由 `framework_composer.py:26-31` 的**既有回退腿**承接（"未覆盖 regime/日期回退基准权重并披露 `regime_day_counts`"）
  ⇒ 已有供数腿在码不在册，**接法=登记披露，不新增数值**。
- 结论：**本波一格未填、一数值未造**（合法填法只存于"从已有真源派生"，而 7×N 空位中唯一有腿的 r11
  需 pf_alloc/composer 侧先给出 r11 的分配结果，属生效面数值 ⇒ 触"禁改配比数值"红线 ⇒ 待裁，见 §六）。

## 四、红测与结论（实测）

尺面两枚（任务书要求）＋护栏接线自证，共 **17 条**，全绿：
`PYTHONPATH=src python -m pytest tests/backtest/test_weight_ssot_single_authority.py -p no:cacheprovider -c py.ini -q --timeout=300`
→ `.................  [100%]`（17 passed）

| 尺 | 断言位点 | 结论 |
|---|---|---|
| 一：改提名不能改生效 | `test_nomination_claiming_effective_is_rejected`（auto_mount 行伪标 effective → 必抛）＋`test_weight_row_without_binding_is_unattributable`（缺权级标记=不可归因即拒）＋`test_effective_side_admits_only_pf_alloc`（生效面只认 pf_alloc）＋`test_nomination_author_may_not_write_effective_field` | 提名面被拒成立；生效面只剩 1 条路（`effective_writers()=={"pf_alloc"}`） |
| 二：两处同写同一权重可探出（病根判据） | `test_two_writers_on_same_weight_are_detected`（本案原形态：提名腿挤进生效字段与 pf_alloc 并写 → `nomination_overreach=True`、`attributable=False`）＋`test_two_effective_authors_on_same_weight_is_worst_case`（两个都自称生效 → `multi_effective=True`）＋`test_layered_writing_of_different_fields_is_not_a_conflict`（分层写法不误伤）＋`test_effective_path_must_stay_single_after_a_second_author_appears`（第二个生效作者冒头即红）＋`test_discover_probe_finds_unregistered_second_head`（tmp 迷你仓造野生写手，探针按 file:line 揪出） | 病根可机检；真仓普查 `single_effective_path=True`、`conflicts=[]`、野生写手=0 |
| 反"装饰性护栏"自证 | `test_alloc_authority_guard_fails_closed`（monkeypatch 尺→写图闸真的改行为；并断言 auto_mount 用的与测试是**同一模块对象**，两份实例=假绿源）＋`test_guard_is_wired_before_the_map_write`（源码序检查：闸在 `safe_write_text` 之前） | 护栏有真调用者且能拒 |
| 零漂移自证（禁区守门） | `test_allocation_request_output_is_nomination_grade`（权重逐位 == `sleeve_weights`，Σ=1 闭合）＋`test_caliber_numbers_untouched_by_this_lane`（0.05/0.25/6 三常量与 TDM 16 条 sleeve Σ=1 未变） | 未改任何配比数值/判据 |

回归：`tests/backtest/test_auto_mount.py`＋`test_auto_mount_sle3.py` = **76 passed**（既有断言零改动，
`allocation_request` 的 `stage/signal_weight/capacity/weight` 契约键全保留，只追加权级字段）。

**基线红登记（非本车道所致）**：`tests/pf_alloc/` 7 件红
（`test_sim_ledger_allocation_wiring.py` 6 件 `KeyError: 'capital'` ＋ `test_pf_alloc_event_wiring.py::test_business_day_resolves_from_latest_market_data`）。
归因证据三条：① `grep auto_mount\|weight_ssot tests/pf_alloc/*.py` = 0 命中；② 其 SUT
`scripts/backtest/sim_paper_ledger.py` 在本 worktree **未改动**（`git status` 净）且不 import auto_mount；
③ 该 worktree 载有他在途面 `src/zephyr/trading/decision_map.py`（staged 改）＋
`src/zephyr/{position,ex_core}/position_reconciler.py`（工作区改）。⇒ 按 §3.1 不代修，登记待其落地。

## 五、文件清单

| 态 | 文件 | 净变化 |
|---|---|---|
| 新建 | `scripts/backtest/weight_ssot.py` | 配比权级尺（判权不判数；`WEIGHT_PRODUCERS`/`PRODUCER_FIELDS` 作者真源＋四把尺＋两把探针） |
| 新建 | `tests/backtest/test_weight_ssot_single_authority.py` | 17 条红测（含 tmp_path 隔离，零生产写、零资金动作） |
| 改 | `scripts/backtest/auto_mount.py` | +79/−11：头注 DEPENDENCIES/INVARIANTS/③ 段口径、`allocation_request` 撤销越权契约并套提名标记、新增 `_weight_ssot()`/`alloc_authority_guard()`、`--apply` 写图前串闸、`--rebalance` 尾注改口 |
| 改 | `docs/_working/fullflow_mining/02_tdm_decision/wiring_F_alloc_ssot.md` | 本册（现状链＋空位清单＋验收） |

**未改**：`src/zephyr/pf_alloc/**`（一行未动）、`config/trading_decision_map.yaml`、`config/framework_plans.yaml`、
only-add 门（`only_add_assert`）、SLE-1 Owner 门位（`weight_adjust_assert`＋`--rebalance` 只读）。

## 六、待登项（总筹单点，本车道零提交零入队）

1. **creation_token**：`scripts/backtest/weight_ssot.py`、
   `tests/backtest/test_weight_ssot_single_authority.py`（册内 token=`w3-f-alloc-ssot-nomination-20260926`）。
2. **翻译册**：`scripts/backtest/weight_ssot.py` 大白话简介（TRANSLATION-COVERAGE gate 会拦新建 .py）。
3. **depgraph**：新产物节点＝`scripts/backtest/weight_ssot.py`（被 `auto_mount.py`＋自家测试消费），
   需登记设计节点；本车道未碰 PG。
4. **待接线一行**（护栏上提交面，`commit_gates/**` 是本波禁触件，故只登记不改）：
   在 DECISION-MAP 家族新增 `weight_ssot_gate`，触发条件=commit 触及
   `config/trading_decision_map.yaml` 或 `scripts/backtest/auto_mount.py`，
   动作=`weight_ssot.assert_effective_path_single()` ＋ `discover_weight_writers(REPO)["clean"]`。
   ⇒ 现网唯一真调用者=`auto_mount.main`（写图前），提交面拦截待总筹接。
5. **105 格空位待裁**（见 §三）：`fw-*` 三方案 r11 行共 23 格有腿无数值，补它=向生效面写新数 ⇒
   触"禁改配比数值"与资金面 Owner 门；r1/r2 空=设计内（宁漏勿误）禁填；
   `fw-tdm-current` 112 格由 composer 既有回退腿承接 ⇒ 只登记披露，不新增数值。
6. **06 册账面更正候选**：`m2_backtest_sim/06_ibt_backtest.md:41` 写"7 态×15 员=105 格全空"，
   实测为 4 方案 273 格（已填 92/空 181）、成员并集 16 员 ⇒ 文档矛盾＝事故（§4.3），待总筹改册面（本车道未改他册）。
7. **腿 B 造数位的归因补丁建议**（未落码，因属 pf_alloc）：`allocation_inputs.py:240-245` 的
   `pp001_mean_prior_fill`/`equal_weight` 已随 `sources` 字段落库，建议生效面把 `sources` 一并写进
   `alloc_budget_daily` 列，使"这一行的权是谁给的"在库里可查 ⇒ 属 pf_alloc＋DDL（Owner 门），只登记。
