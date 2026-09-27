---
ttl: task_bound
completes_when: 图15 封矿且 config/strategy_card_lifecycle_map.yaml 四件套（生成器+图 YAML+卡生命周期校验器+MAP-ALIGNMENT 子台+挂轴）与卡状态登记面（见 90_card_state_registry_spec.md）落地后，本件退役为归档参考
title: 图15 策略卡生命周期图·状态机总骨架（00_skeleton，本图唯一收敛基准）
owner: st-mapbuild-20260924
---

# 图15 策略卡生命周期图 00_skeleton

> 一句话域：**一张预注册卡（假设契约）从"起草"到"封卡/判死/毕业/作废"的状态序列，以及谁有权推动每一次迁移、凭什么凭证、哪些边永远不许走**——不管考试判据本身（那是 exam_policy），不管策略/因子入库后的衰减（那是策略工厂 E6 与图9）。
> 本图是**实例级状态机**（对象=一张卡，键=card_id），不是环节流程图；这是它与策略工厂图（环节级，对象=一道工序）的根本分轴，实证见 §0 门③。
> 普查判定原文=`docs/_working/map_census/00_panorama_map_census_v1.md:59`（图15 行：状态机形态 + 缺口="卡状态三处分裂"→四道门第④门不过）。**本骨架确认该判定成立，但实测把"三处分裂"改写成"三处零交集 + 状态词汇七套"**（数字见 §3），比普查描述更严重。
> 状态纪律=`sop/mining_sop/skeleton_mining_policy.md` §5：**每个 ✅ 必附实查路径/命令/行号**，凭印象标 ✅=审计事故。本件所有计数均在 worktree `.aidrafts/st-mapbuild-20260924` 于 2026-09-24 实测（复核命令见 §8）。
> **重要勘误先落**：任务简报与普查 §4 把"封卡/复活唯一口"的裁定坐标写作 #363/#399/#304。逐条读原文后：**#304 与封卡无关**（它是 Regime r4/r10 方向失真重校准，`ruling_registry.yaml:4120`）；做T 旧形态终止裁定的现行号是 **#331**（`:3765`，条目内 `renumber_note` 明书"原#304 与 Regime 重校准撞号…改号 #331"）。封卡/复活语义的真裁定组=**#363（重判一次后封卡）+ #389（快签通道）+ #390（封卡效力维持，禁以 #389 为凭重跑）+ #399 二 + #404 R4（复活唯一口=预注册新假设）**。详见 §2 迁移表凭据列与红条目 F-01。

## §0 域定义与四道门实证（宪章 §8.2 新图准入四问）

**域职责**：管"一份研究契约的可信生命周期"——预注册在先、冻结不可改、一次判定、一次性重判令牌、封卡即终、复活只能开新契约。这个域的存在理由不是"画图"，是**防 p-hacking 的制度化**：策略工厂三铁律第一条"运动员不兼任裁判，考试权只在 E4 咽喉"（`config/strategy_production_map.yaml:20`）要有执行载体，载体就是这张卡。

### 门① 独立触发与终点

| 项 | 实证（文件:行） |
|---|---|
| 触发 | `factor_mining_sop_policy.md:25` 八段生产线 S3="预注册卡"；`:55-58`「S3 预注册卡（输入：待考池因子）…每条升考因子写预注册卡（模板=§4）…输出：prereg 卡（frozen，启动后不得改动）」；`exam_policy.md:24-30` §1「考试准入」第 1 条"prereg 卡 frozen…事后挪门柱=本批作废"——卡的诞生=一次考试被允许点火的**唯一前置凭证** |
| 终点（四条，互斥） | ①封卡 SEALED（`ruling_registry.yaml:4708` 裁定#363；卡片实测 `docs/_working/archive/2026-09/bizmine_night/t0_regime/t0_prereg_funding_carry.md:9`）②判死归档（`exam_policy.md:60-66` §6 三态出口 + `:57` §5.4 死矿登记）③毕业出卡（`factor_mining_sop_policy.md:71` 三出口之"达标"→S6 备料→因子/策略册回写）④作废（`exam_policy.md:29` "中途加条目=重开预注册"，卡片头自述"改动即作废重开"**23 处**，见 §3-A） |
| 有独立状态机？ | **有，但目前只活在散文里**。卡 frontmatter `status` 头实测 22 种自由文本串（§3-A），归一后 5 个词元：frozen 33 / active 3 / draft 1 / 候选 1 / SEALED 1，另 **29 份无 status 头**（合计 n=68）；`SEALED` 在 `src/`+`scripts/`+`config/` 代码面**零命中**（`grep -rniE "SEALED|封卡" src scripts config` 命中全为涨停封板 `close_sealed` 语义，与卡无关）⇒ 状态机存在（人人在写、人人在用），但**无一格可机读** |
| 域边界自证（关键） | 卡制度**已溢出策略工厂 E2-E6**：同一套"预注册协议判据"被用于 regime 重校准（`ruling_registry.yaml:4121` 裁定#304 标题逐字"预注册协议判据"，协议件 `docs/_working/archive/2026-09/wyf3/wyf3_preregistered_protocol.md`）、复权链数据修复（`docs/_working/archive/2026-09/final3_campaign/x2_adjfactor_prereg.md`）、估计器口径校准（`docs/_working/2026-09-15-neff-estimator-preregistration.md`）。⇒ 本图域=**跨域研究诚信机制**，工厂图只是它最大的单一消费者（此点是门③成立的正面证据，也是"不该并进工厂"的理由） |

### 门② 跨模块交接（本域是一条流程线而非一堆散件的证明）

| 交接边 | 上游→下游 | 证据（文件:行） |
|---|---|---|
| J1 | 卡 → 考试执行件：脚本以卡为**判据真源**（反向锚已存在！） | `scripts/audit/t0_conditional_e4_exam.py:1` `# [BLUEPRINT] SH-SCRIPT-001 \| docs/_working/t0_revival/t0_conditional_prereg_card.md \| §2 状态门+§5 判据`；`:8` INVARIANTS「判据全部来自 frozen 卡（禁脚本内改判据=禁裸跑）」；`:9` `# [MODIFY-GUARD] 本脚本改动=考试判据变更，须先改卡并作废重开`。同形态另有 `t0_ceiling_capacity_exam.py:1`、`t0_gpu_condition_pack.py:1`、`t0_six_phase_materialize.py:1`；全仓带 `[BLUEPRINT]` 头的 .py 共 **4,524** 个（实测 `grep -rl "^# \[BLUEPRINT\]" --include=*.py src scripts \| wc -l`）⇒ 卡的"被引用面"天然挂在 depgraph 横轴上 |
| J2 | 卡 → 判定书/run 档案 | `src/zephyr/backtest/run_archive.py:53-61` `_STEP_FILES`（含 `verdict: verdict.md`、`errata: errata.md`）；`:67-72` `_REQUIRED_STEPS`（VAL/BACKTEST/SCREEN/ABLATION 四 kind 各必选步骤集）；`sop/backtest_system_sop/sop_d_run_archive_naming.md:28`「只增不改：run 目录落成后禁修改历史文件——发现错误追加 errata.md 声明」（与卡的"带日期附录"同构，实测 5 张卡用 §6/§7 附录形态承载勘误/修订） |
| J3 | 判定 → ClickHouse 判定台账 | `c1_backtest.hypothesis_precheck`（58 行，verdict 三值：precheck_rejected 26/precheck_passed 13/precheck_deferred 19）、`c1_backtest.strategy_screen`（1,340 行，verdict 七值）、`c1_backtest.node_verdict`（58 行，pending 41/valid 17）——实测经 `get_db_service().get_clickhouse_conn()`（宪法 §7 唯一正门）读 `system.tables`/`GROUP BY`；全库 237 表（c1_market 187/c3_fundamental 33/c1_backtest 16/c0_meta 1） |
| J4 | 卡 → 试验次数账本（DSR 原料） | `exam_policy.md:31`「试验台账行已开…Deflated Sharpe 的原料，后补=造假」；`docs/01_policies_and_standards/_registry/catalogs/trial_ledger_registry.yaml`（counting_rule=`screen_runs.total_trials + sum(batch_records.n_trials)`；实测 total_trials=269 / total_runs=25 / batch_records=8 条；`manual_population: 0` 注"人工历史试错不可审计"） |
| J5 | 卡状态迁移 → 裁定（人门位） | 封卡=`ruling_registry.yaml:4708` 裁定#363；封卡效力维持=`:5219` 裁定#390「任何会话禁以 #389 为凭重跑两卡」；复活唯一口=`:5409` 裁定#399 二 + `:5595` 裁定#404 R4「维持封卡（#363 封卡条款不破，复活唯一口=预注册新假设）」；候选卡升格门位=`:4755` 裁定#366 条件③「矩阵只产候选卡不出 PASS」；快签通道=`:5197` 裁定#389 ② |
| J6 | 卡结论 → 因子/策略册回写 | `factor_registry.yaml` 175 条（status：candidate 170/experimental 4/deprecated 1；algorithm_status：pending_backtest 154/None 19/quantized 2）、`strategy_registry.yaml` 161 条（lifecycle_status：candidate 151/backtest 8/sim 2；status：candidate 139/active 19/deprecated 3）；回写纪律=`exam_policy.md:64`「factor 回写 registry ic/ir/decay；strategy 走 sop_c C5-C6」 |
| J7 | 复活边（跨实例） | 实测落地件链完整：封卡 `t0_regime/t0_prereg_funding_carry.md` →（#399 二 授权）→ 新卡 `docs/_working/t0_revival/t0_conditional_prereg_card.md:1-14`（frontmatter `family_id: T0-CONDITIONAL`、`parent_context: 裁定#399 二（做T复活改裁授权）+ 裁定#331/#386…+ etft0_prereg_card.md（方法论母本）`）⇒ **"新卡指旧卡"的引用边已在人写层出现，但无 card_id 键可机读**（旧卡靠 parent_context 散文提及） |

### 门③ 不被现有图覆盖 —— 与 strategy_production_map E2/E4/E6 的实证切分（本图最大撞车风险，直答）

**结论：切得开，图15 单立成立；但必须钉三条硬边界（见下"切分成立的前提"），否则本图就是工厂图的散文副本。**

| 维度 | 策略工厂图（图9） | 图15 卡生命周期 | 实测证据 |
|---|---|---|---|
| 对象 | **环节**（工序，单例） | **个案**（一张卡，N 实例） | 工厂图 410 行 / 16 节点 / 16 边 / 10 层 E0-E9 / 3 laws / 2 feedback（实跑 yaml 计数）；节点键 `node_id: FAC-*` 唯一，**一张卡无法成为节点**（要 68 个节点才能表达 68 张卡的当前态，且下次再生要重写一遍） |
| 状态语义 | 节点的**建设进度** | 契约的**法律地位** | 工厂节点字段 `build_status`：built 4 / partial 11 / pending 1（实测 Counter），枚举真源 `validate_strategy_production_map.py:40 BUILD_STATUS`；与"冻结/封卡/作废"**无任何映射关系** |
| 词汇 | 全文零卡词汇 | — | `grep -n "卡\|prereg\|预注册\|frozen\|SEALED\|封卡" config/strategy_production_map.yaml` → **exit 1，零命中**（410 行全扫）；同文件 `考试` 命中 5 处，全部指"考试权/考卷/考试成绩"工序语义，无一处指契约对象 |
| 交接物 | E2 出"预审判定记录"、E4 出"考试成绩+判定书"、E6 出"衰减巡检" | 出"一份不可改的判据契约 + 该契约的终局地位" | 工厂 store_refs：`:233` 预审判定记录 `c1_backtest.hypothesis_precheck`、`:283-285` 考试成绩+判定书、`:320-321` 判定书/衰减巡检——**三处 store_refs 里没有"预注册卡"这个工件**；E4 `decision_question`（`:269`）="这策略在没见过的考卷上还活着吗"，问的是策略不是卡 |
| 键空间 | `candidate_id`（CAND-*，E2 面）/ `strategy_id`（E4/E6 面）/ `node_id`（TDM 面） | `card_id`（T0-PRERG-01/P3-E1C-09/T0-CONDITIONAL…） | 实测 CH 三表按卡号查：**`strategy_screen` 中 strategy_id LIKE '%E1C%' OR source_file LIKE '%prereg%' OR '%E1C%' = 0 行**；`hypothesis_precheck` candidate_id LIKE 'P3%' OR notes LIKE '%prereg%' = 0 行；`node_verdict` 键=TDM 节点号 ⇒ **两套键空间零交集**，内收判据"跨域不同对象→不并"（AGENTS §4.2）适用 |
| 是否工厂某段的展开？ | 若"是"，扩工厂节点即可 | **不是**：卡的 S01→S03→S05 段先于 E4 且跨越 E1-E6（同一张卡的 lifetime 内可发生 E2 预审、E4 正考、E6 衰减巡检）；卡还可由**非工厂**生产者产出（regime 重校准协议、复权链修复预注册，见门①） | `factor_mining_sop_policy.md:25` 八段 S0-S7 中卡只占 S3 一格，但其出口 S6/S7 又回到 E5/E6——**卡是纵切工厂的实例轴，不是工厂的某一层** |

**切分成立的前提（三条硬边界，写进图 YAML 的 boundary，违反即校验器判红）**：

1. **本图节点=状态，不写判据**。考试"怎么算过"（WFA/OOS/DSR/BH 阈值/regime 分桶）判据真源恒在 `exam_policy.md` + `factor_mining_sop_policy.md` + 卡正文，本图一律只放引用（INV-1 型条款，规格 CV-12；同 layering policy §2.1"地图只做索引，公式各归各库"）。
2. **E4/E6 的判定值不回填成本图状态**。`strategy_screen.verdict` 七值（screened_in/deferred_c4/rejected/translated_c4/oos_tested/sim_deviation/failed_obsolete）是**策略件**的工序结论，与本图**卡契约**状态是两个轴；图里禁止出现"screened_in ⇒ 某卡状态"的隐式派生（否则工厂台账一动，卡状态漂移无人知）。
3. **不吞图9 的环节，不吞图16 的裁定**。卡状态迁移的凭证=裁定号，但"裁定如何产生"（呈报→取号→登记→执行→取代链）属图16 车道；本图只允许存 `ruling_id` 引用值，禁复制裁定正文（实测：`funding_carry_rejudge.md:14` 已用 `ruling: 裁定#363（2026-09-19，ruling_registry 同 commit 原子）` 的引用形态，照此办理）。

**反向清单（若总包判定"该并入工厂图"，需要扩的节点清单，一并给出以免只出结论不出路）**：工厂图需新增 `FAC-E2X 预注册契约`（stage E2）、`FAC-E4X 判定书档案`（stage E4，接 run_archive 六段 verdict）、`FAC-E6X 死矿与封卡台账`（stage E6）+ 三条边 E2X→E4X→E6X + 一条 `feedback_loops: E6X→E1X（封卡知识反哺进货）`。**本骨架判定此方案劣于单立**：扩节点仍拿不到"每卡当前态 + 禁止边可机验"这两个交付物（工厂 schema 无实例位、无 forbidden-edge 概念，`validate_strategy_production_map.py:110-128` 只校边闭合与反向边声明），且会把工厂 v0.2 schema 从"环节表"改成"环节+实例混排表"，代价远大于单立一张实例轴。

### 门④ 登记面可建性 —— **当前不过（实测三处零交集）**

| 项 | 实测结论 |
|---|---|
| 有卡登记面吗？ | **没有。** 76 本 catalogs（`docs/registry_of_registries.yaml:881 total_registries: 76`，字段读值勿背数）中无卡宿主；六本最相近的册（experiment_registry / strategy_registry / factor_registry / trial_ledger_registry / backtest_backlog / chart_pattern_registry）全文扫描：**68 张卡的文件名 stem 命中 0 条**（实跑：`[s for s in stems if s in 六册文本] == []`） |
| 卡号进过机读面吗？ | **没有。** `experiment_registry.yaml` 全文 `bizmine` 命中 0、`prereg` 命中 0；CH 三表按卡号查 0 行（门③表第 5 行）；config/src/scripts/schemas 全域含卡号的文件仅 **13 个**，其中 5 个是 `scripts/audit/*` 的 `[BLUEPRINT]` 锚（人写注释，非登记）、其余 6 个是 Wyckoff `WYF-3` 同名撞词误命中 |
| 卡自己的 status 头机读吗？ | **不机读，且已越界。** `status_vocabulary.yaml` 受控三值 `{draft, active, deprecated}`（实跑 `load_vocabulary_values('status_vocabulary.yaml')`）；4 张样卡 status 头全部 `in_vocab=False`（funding='已封卡 SEALED（…）'、obv='frozen（考试启动前写死…）'、candidate='候选（…）'、sector v1='frozen（2026-09-23 开工令即冻结…）'）；字段册 `frontmatter_field_registry.yaml` 实测 58 个 field 条目（其自述字段 `total_registered: 53`——**册内字段与条目数已不一致**，F-08），无任何 `card_state`/`lifecycle` 类字段 |
| 结论 | **四道门第④门不过**（普查 §4 L59 判定成立，但缺口比"三处分裂"更深=三处零交集）。建图前必须先立卡状态登记面；施工规格见同文件夹 `90_card_state_registry_spec.md`（真源选型实测三案二否一选 + 校验项 CV-01…CV-18 + CLI exit 0/1/2 + 红证 18 条） |

## §1 状态全集（13 态，编号 D15-S1..S13；本图核心表）

**列口径**：「当前真源在哪」= 该状态**今天实际被记在哪**（多半是散文）；「机可读」= yes=有枚举/字段可判定，partial=有词元但自由文本，no=只在人写的表行/裁定里。状态编号一经定稿即契约，作业簿标题必须引用。

| 状态编号 | 状态名 | 语义定义 | 进入条件 | 退出/迁移去向 | 当前真源在哪（文件:行/字段名） | 机可读 |
|---|---|---|---|---|---|---|
| D15-S1 | 草案 draft | 卡已立、判据未写死，可自由改 | AI/人起草卡（`factor_mining_sop_policy.md:55-58` S3） | →S3（M03）；→S13（M16） | `docs/_working/sector_line/sector_prereg_exam_cards_v0.md` frontmatter `status: draft（先于实验落盘；施工开工时冻结为 frozen，冻结后禁改参数）`；`docs/_working/emotion_line/prereg_exam_cards_v0.md` 同形态 | partial |
| D15-S2 | 候选卡 candidate | 机器筛出、未升格，**禁出任何 PASS 语义** | 有界矩阵/宽筛产出（`ruling_registry.yaml:4755` 裁定#366 条件③"矩阵只产候选卡不出 PASS"） | →S3（M04，Owner 快签）；→S13 | `docs/_working/archive/2026-09/bizmine_night/algo_mining/candidate_card_open_momentum_market.md:9` `status: 候选（…升格=Owner 快签通道）` | partial |
| D15-S3 | 冻结 frozen | 考窗/阈值/桶边界/N_eff 全部写死，参数不可再改 | 卡面 frozen 落盘 + Owner 批或快签通道（`:5197` 裁定#389 ②） | →S5（M06）；→S4（M05）；→S13（M16） | 33 张卡的 frontmatter `status: frozen（…）`（§3-A 计数）；模板真源 `factor_mining_sop_policy.md:108` `status: frozen   # 启动后不得改动` | partial（词元可扫，语义在括号散文里） |
| D15-S4 | 冻结带附录 frozen-amended | 只增不改：勘误/裁定修订以**带日期附录**追加，frozen 参数零改动 | 出现事实修正或裁定修订（`sop_d_run_archive_naming.md:28` errata 同构） | →S5；→S10（M10/M11）；禁回 S1 | `t0_prereg_funding_carry.md` §6 勘误 + §7 修订附录（"其余 frozen 参数零改动"）；`tick_t0_prereg_card.md` status 头逐字"修订=带日期附录，禁静默改卡"；`momentum_prereg_card.md:14`"修实现缺陷可，改 frozen 参数不可" | no |
| D15-S5 | 在测 executing | 试验台账行已开、执行件跑数中 | `exam_policy.md:24-30` §1 四条准入全满足 | →S6/S7/S8（M07-M09） | **卡面无**。仅战役台账有：`docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md` 状态列 `running（首轮脚本 bug 已修，二轮跑中）`；`experiment_registry.yaml:78` `status: str # enum: running/...`（EXP-WALKFWD-001 实测 running） | no（卡侧）/yes（run 侧，但两套零交集） |
| D15-S6 | 判绿 green | 预注册阈值全过 + DSR 校正后仍显著 | 判定书 verdict 达标（`exam_policy.md:60-66` 出口"达标"） | →S12（M13）；→S10（M11） | 卡外报告面：`momentum_prereg_card.md:36`「verdict 三态：PASS…/RED/INSUFFICIENT」；`factor_registry.yaml` factors[].status（candidate 170/experimental 4）；`strategy_registry.yaml` lifecycle_status（backtest 8/sim 2） | partial（在报告与册里，不在卡里） |
| D15-S7 | 判红 red | 阈值未过（机制假设可修或不可修尚未定） | 同上，判据不过 | →S4（M10 一次性重判）；→S10；→S11（M12） | `docs/_working/archive/2026-09/bizmine_night/crypto_probe/funding_carry_rejudge.md:20`"verdict=RED 变硬"；`t0_regime/t0_regime_narrow_test_results.md` status 头"完成（考试已执行，判定=终结）"（TERMINATE 同族） | partial |
| D15-S8 | 不可判 insufficient | 样本/功效不足或 fail-closed 存疑，**既非绿也非红** | 桶 n<功效门 / 配对数<30 / 判据不可评 | →S9（M14）；→S10；→S5（重跑须新卡或触发条件） | `experiments_ledger.md` biz2 行"维持 insufficient_samples：0/24 毛价差≥30bp 前置"；biz4 行"verdict=**存疑**(fail-closed)…can_deploy=false 放行权 Owner"；`experiment_registry.yaml:102` `viability_verdict: str # enum: supported/refuted/inconclusive`（实测 11 条**全 null**） | partial（枚举在跑数侧已定义，从未回填） |
| D15-S9 | 挂起 suspended | 裁定"延后重考"，带显式触发条件，**禁被读成通过** | 裁定#398 R2 / 裁定#404 R2（`:5595`）"判挂起并入 IBT 批D 新鲜窗重考…触发=样本显著增厚或下个预注册考试窗" | →S5（M15）；→S13 | **只在裁定册 + `docs/_working/integrated_backtest/max_remediation_plan.md`**；卡 `P3-E1C-09.md:9` status 头**仍停留 frozen**（F-03 实证：裁定改了地位，卡头一字未动） | no |
| D15-S10 | 封卡 SEALED | 终态：不再重开、不再改参重跑；证据定版 | 裁定明判（`ruling_registry.yaml:4708` 裁定#363；`:5219` 裁定#390 维持封卡效力） | 唯一出路=**跨实例边** M17（新卡 S1 指回本卡）；禁任何就地复活 | 实测全仓 **1/68**：`t0_prereg_funding_carry.md:9` `status: 已封卡 SEALED（…裁定#363；修订见 §7，禁静默改）`；代码/配置面零命中（`grep -rniE "SEALED|封卡" src scripts config` 仅涨停封板语义） | no |
| D15-S11 | 判死归档 condemned | 终态：机制证伪/数据面不可修，入死矿账防复挖 | `exam_policy.md:66` 出口"判死归档" + `:57` §5.4 死矿登记（判死单须带 ≥3 个已排除候选与理由） | M17（带新机制假设或新数据面的新卡，`:57` "复挖须带新机制假设或新数据面，否则禁复挖"） | 散在各战役台账"挖干/TERMINATE"行（`docs/_working/archive/2026-09/tdchain_mine/a0_master_ledger.md` 状态列实测：执行中 4/挖干 1/挖干待合并 1/阻塞待终端 1/待 W1 1/待 E8 1）；无死矿专册 | no |
| D15-S12 | 毕业出卡 graduated | 终态：结论已回写因子/策略册，卡使命完成，原卡随即封存 | `exam_policy.md:64`「factor 回写 registry ic/ir/decay；strategy 走 sop_c C5-C6」 | 无（知识遗产转 E6 衰减监控，属工厂域） | `factor_registry.yaml`/`strategy_registry.yaml` 条目 status（candidate→experimental→…/backtest→sim）；**无一条能反查它来自哪张卡**（J3 键空间零交集） | partial（在册侧，断来源） |
| D15-S13 | 作废 void | 终态：挪门柱/中途加条目/N_eff 破/卡被改，本批结论作废 | `exam_policy.md:28`「事后挪门柱=本批作废」、`:29`「中途加条目=重开预注册」；23 张卡头自述"改动即作废重开" | M17（重开=新预注册，非改旧卡） | 实测**零登记**：`grep -rniE "作废" docs/_working/**/prereg*` 的"作废"全部只出现在**卡头条件句**（"改动即作废重开"），无任何一张卡被真标为作废态；最接近的活体=代码注释 `scripts/audit/t0_gpu_condition_pack.py:1`「V2 已作废，其 §2.2 六段接线由 V3 §2 逐字继承」——**卡的状态记在脚本注释里**（F-04） | no |

**计分板**：状态 **13**（终态 4：S10/S11/S12/S13；瞬态 1：S5；其余 8 为可驻留态）。机可读分解 **yes 0 / partial 6（S1,S2,S3,S6,S7,S12）/ no 7（S4,S5,S8,S9,S10,S11,S13）**。实测有卡片停在之上的状态：frozen 33、无头 29、active 3、draft 1、候选 1、SEALED 1 ⇒ **S1/S2/S3/S10 四态有个例，其余 9 态在卡面零实例（其证据全在报告/裁定/台账/脚本注释里）**；"无头 29"本身即"状态不可判"的第 6 个词元。

> 计数纪律：`13 态` 是本图契约数；作业簿不得自行增态。增态须过 `skeleton_mining_policy.md` §3 三问（生产者变/验证口径变→拆；只是标签变→不拆）并回写本件。已按此判据**主动合并/拒绝**的候选态见 §7 表末（如"已归档"判为文件生命周期属性而非状态，避免与 `ttl` 轴打架）。

## §2 迁移全集（17 条合法边 + 13 条禁止边）

**凭据列口径**：`裁定`=必须有 ruling_registry 在册条目；`测试绿`=必须有判定书/run 档案；`人`=Owner 门位；`机`=执行件自动推。

### 2.1 合法边（M01-M17）

| 迁移编号 | from→to | 触发者 | 凭据要求 | 真源（文件:行） | 实查 |
|---|---|---|---|---|---|
| D15-M01 | ∅→S1 | 人/AI | 无（起草自由） | `factor_mining_sop_policy.md:55-58` | ✅ 案例：`sector_prereg_exam_cards_v0.md` |
| D15-M02 | ∅→S2 | **机器**（矩阵） | 封闭族声明 + 不得写 PASS | `ruling_registry.yaml:4755` #366 条件③ | ✅ `bounded_matrix_wave1_report.md` → `candidate_card_open_momentum_market.md` |
| D15-M03 | S1→S3 | 人（Owner 批/快签） | 卡面 frozen + 批文或快签通道 | `ruling_registry.yaml:5197` #389 ② | ✅ `sector_prereg_exam_cards_v0.md`→`sector_prereg_exam_cards_v1_frozen.md`（v0 draft / v1 frozen 两份俱在，卡号未变） |
| D15-M04 | S2→S3 | 人（Owner 快签） | 同上 | 同上 + 候选卡头"升格=Owner 快签通道" | ⬜ 无活体（`candidate_card_open_momentum_market.md` 至今停在 S2，实测该文件存在且 status=候选） |
| D15-M05 | S3→S4 | 人 | 带日期附录 + 同批入册；frozen 参数零改动 | `t0_prereg_funding_carry.md` §6；`tick_t0_prereg_card.md` status 头 | ✅ 实测 ≥5 卡用 §6/§7 附录承载修订 |
| D15-M06 | S3\|S4→S5 | **机**（执行件） | 四条准入全绿：frozen 卡 / N_eff 封闭族 / 沙箱三关 / 试验台账行已开 | `exam_policy.md:24-30`；`t0_conditional_e4_exam.py:8` INVARIANTS | ✅ `t0_conditional_e4_result.yaml` + `t0_conditional_e4_verdict.md` 在盘 |
| D15-M07 | S5→S6 | 机判 + 人复判 | 判定书 + DSR 校正 | `exam_policy.md:62-64` | 🔨 有出口无实例（`experiment_registry` 实测 supported=0 条，11 条 viability_verdict 全 null） |
| D15-M08 | S5→S7 | 机判 | 同上 | `funding_carry_results.md` / `vwap_exam_report.md:13` | ✅ 多例（`status: 完成（考试已执行，结果 RED）`） |
| D15-M09 | S5→S8 | 机判（fail-closed） | 样本/功效不足须显式标 | `experiments_ledger.md` biz2/biz4 行；`experiment_registry.yaml:102` inconclusive | ✅ 2 例（insufficient_samples、存疑 fail-closed） |
| D15-M10 | S7→S4 **一次性重判** | 人（裁定） | **裁定必备** + 全局唯一令牌 `rejudge_used=true` + 只许改裁定明示项，其余零改动 | `ruling_registry.yaml:4708` #363「按真实费率重判一次后封卡」；卡 §7「修订项（唯一）」 | ✅ `funding_carry_rejudge.md`（"授权与唯一 diff"§1）——**全仓唯一活体** |
| D15-M11 | S6\|S7\|S8→S10 | 人（裁定） | 裁定必备（RULE-RULING 同 commit 原子） | #363；维持效力 `:5219` #390 | ✅ 1 例（funding） |
| D15-M12 | S7→S11 | 人 | 判死单（≥3 已排除候选+理由）+ 死矿登记 | `exam_policy.md:55`、`:57`；`sop_b_node_loop.md:73-77` ⑦ | 🔨 散在台账 TERMINATE/挖干行，无死矿专册（**负结果台账缺面**，F-06） |
| D15-M13 | S6→S12 | 人 + 提交正门 | 回写 factor/strategy 册 + 原卡封存 | `exam_policy.md:64`；`factor_mining_sop_policy.md:71` | 🔨 册侧字段在（factor status=experimental 4 条、strategy lifecycle=backtest 8/sim 2），**卡侧无从反查**（J3） |
| D15-M14 | S8→S9 | 人（裁定） | 裁定必备 + 必填 trigger 表达式 | `ruling_registry.yaml:5369` #398 R2；`:5595` #404 R2 | ✅ 1 例（E1C-09 挂起并入 IBT 批D）——但卡头未跟（F-03） |
| D15-M15 | S9→S5 | 机（事件触发） | trigger 达成；**禁改卡**，要改=新卡 | #398 R2 触发条款；宪法 §9.3（reconciler 事件触发，禁 cron/Timer） | ⬜ 零活体（宪法 §9.3 铁律下这是必建面，属作业簿 04） |
| D15-M16 | S1..S9→S13 | 人 | 挪门柱/加条目/N_eff 破/卡被改的事实认定 | `exam_policy.md:28-29`；23 张卡头条件句 | ❌ **零登记**（F-04：唯一近似记录在 `t0_gpu_condition_pack.py:1` 脚本注释） |
| D15-M17 | S10\|S11\|S13 →**新卡** S1 | 人（Owner 终审 + 裁定） | 跨实例边：新卡必填 `revives: <旧卡号>`；旧卡状态**不变** | `ruling_registry.yaml:5409` #399 二「复活轴=新预注册假设卡+考试制维持」；`:5595` #404 R4「复活唯一口=预注册新假设」；`:5219` #390「唯一前进路=信号侧新假设起草新卡」；`:3765` #331「复活路径=单假设窄考试先行（预注册卡制）」 | ✅ 活体链完整：funding SEALED → `t0_revival/t0_conditional_prereg_card.md`（新 family_id，parent_context 散文指旧证据链）；⬜ 但**无 card_id 键**，指针不可机读（F-05） |

### 2.2 禁止边全集（X01-X13，状态机图一半的价值在此）

| 禁止边 | 不许什么 | 凭据（谁说的） | 实查 |
|---|---|---|---|
| D15-X01 | S7→S6 就地改判 | 判定权在判据，AI 无翻案权；`config/strategy_production_map.yaml:20`「考试权只在 E4 咽喉」+ `strategy_screen` verdict 只增（`:310`「台账只增+判死行追加」） | 机验：状态流水里出现 red→green 即红（规格 CV-08） |
| D15-X02 | S3→S3 静默改 frozen 参数 | `factor_mining_sop_policy.md:108`；`exam_policy.md:28`；33 张卡头 | 机验：卡文件 frozen 段落字节级 sha 变更而 card_state 未过 M05/M16 ⇒ 红（先例工具 `src/zephyr/backtest/run_archive.py:44` `content_sha256`） |
| D15-X03 | S10→S5 就地复活重跑 | `ruling_registry.yaml:5219` #390「任何会话禁以 #389 为凭重跑两卡」；卡头「禁静默改」 | ✅ 该禁令是**真实事故后立的**：#389 批准开测时两卡早已测毕，#390 即日勘误（F-02 是本边唯一实弹案例） |
| D15-X04 | S11→S5 无新假设复挖死矿 | `exam_policy.md:58`「复挖须带新机制假设或新数据面，否则禁复挖」 | ⬜ 无机验面（无死矿册） |
| D15-X05 | S2→S6 候选卡直接出 PASS | `ruling_registry.yaml:4755` #366 条件③ | 卡头逐字已声明（candidate 卡 `status: 候选（矩阵只产候选卡不出 PASS…）`） |
| D15-X06 | S1→S5 未冻结先跑数 | `exam_policy.md:26`「不满足任一条=禁点火，跑了也白跑（结论作废）」+ `:28` prereg 卡 frozen | 机验：S5 时间戳 < S3 冻结时间戳 ⇒ 红（时间真源=git commit，`experiment_registry.yaml:98` 注"git commit 时间戳为证"） |
| D15-X07 | S5→S6 无试验台账行 | `exam_policy.md:31`「后补=造假」 | 机验：trial_ledger 无对应 batch_id ⇒ 红 |
| D15-X08 | S4→S4 无日期附录 / 附录里改 frozen 值 | `t0_prereg_funding_carry.md` §6-§7；`sop_d_run_archive_naming.md:28` | 机验：附录缺 `YYYY-MM-DD` 前缀 ⇒ 红 |
| D15-X09 | 同一假设双卡并行考（N_eff 双重计分） | `factor_mining_sop_policy.md:100`「封闭族：每批考试 N_eff 封闭…中途加条目=重开预注册」 | ✅ **实测活例**：`t0_regime/t0_prereg_vwap_revert.md`（T0-PRERG-01，510300 VWAP 负偏离回归做T，N_eff=1）与 `algo_mining/vwap_prereg_card.md`（ALGO件③ VWAP 偏离条件化做T，27 格）同族两卡、两套 N_eff 账、两个 lane 目录，无任何面声明二者关系（F-07） |
| D15-X10 | S9→S6 把挂起读成通过 | `ruling_registry.yaml:5595` #404 R2「禁直通模拟盘」 | 机验：挂起态卡若被 E7/E8 节点引用 ⇒ 红（跨图检查，作业簿 06） |
| D15-X11 | 把卡内判据正文抄进因子/策略册或抄进图节点 | 宪章 §8.2 + layering policy §2.1「地图只做索引」；宪法 §4.2 内收判据；TDM INV-1 同型 | 机验：规格 CV-12（40 字滑窗命中即红） |
| D15-X12 | 对话/战役令改判已封卡 | 宪法 §1.11「指令真源仅=本宪法+认证通道（规则 YAML/裁定登记）」；#390 | 机验：card_state 迁移的 credential 字段为空或不是在册 ruling_id ⇒ 红（在册性查 `ruling_registry.yaml`） |
| D15-X13 | 复活新卡不带 `revives` 指针 | #399 二 / #404 R4 语义（复活=新假设，必须可追溯到被封的那次证据） | 机验：新卡 family_id 命中已 SEALED/condemned 族而 revives 缺省 ⇒ 红（正是 F-05 现状） |

**迁移计数**：合法 **17**（其中活体已实证 9、有出口无实例 3、零登记缺口 2、无活体 1、⬜ 待建 2）；禁止 **13**。合计状态机有向边 **30**。

## §3 三处分裂实测对账（差异条数=本图最硬的风险证据）

> 普查原话（`:59`）："卡=md status 头 + experiment_registry + N 台账三处分裂"。实测**修正为"三处零交集 + 七套状态词汇"**：不是同一状态记三遍而是不一致，而是**三处各记各的对象、词汇互不相通、连接键根本不存在**。以下每条数字均为 2026-09-24 本会话实跑（命令见 §8）。

**A 面｜卡 md frontmatter status 头（对象=契约）**

| 指标 | 实测值 | 口径 |
|---|---|---|
| 卡语料（契约件，文件名口径，排除 `*report*`/`*ledger*`/`index.md`/README/指令，并排除本车道自身产物 `fig15_cardlife/`） | **68 份**（唯一字节内容 **66**，重复 **2** 组：`2026-09-07-tdm-backtest-protocol.md`、`2026-09-15-neff-estimator-preregistration.md` 各有 `_working/` 与 `archive/2026-09/c_class_scattered/` 双份同字节副本） | §8-A1 |
| 有 `status` 头 / 无 `status` 头 | **39 / 29**（无头率 **42.6%**） | §8-A2 |
| 不同 status 字符串种数 | **22** 种（全部自由文本，括号内含语义说明） | §8-A3 |
| 归一后词元分布（按括号前首词元） | frozen **33** / 无头 **29** / active **3** / draft **1** / 候选 **1** / SEALED **1** | §8-A3 |
| status 头在受控词表内的 | **0 / 68**（词表三值 draft/active/deprecated；4 张抽样全 `in_vocab=False`） | §8-A4 |
| 卡结构字段覆盖率 | `lane` 头 **35/68**、`family_id` 头 **22/68**、`n_eff` 头 **19/68** | §8-A5 |
| 报告→卡的 frontmatter `card:` 字段（已有萌芽） | **5 份**（1,816 份带 frontmatter 的 _working 文档中），字段未登记进 `frontmatter_field_registry.yaml` 的 58 个字段 | §8-A6 |

**B 面｜experiment_registry REG-EXP-001（对象=一次跑数实例）**

| 指标 | 实测值 | 口径 |
|---|---|---|
| 条目数 | **11**（`experiments:` 列表长度；册顶层键是 `experiments` 不是 `entries`） | §8-B1 |
| status 枚举 | 4 值 `running/completed/failed/archived`（`:78` 行内注释）；实测分布 completed **10** / running **1** | §8-B2 |
| 与"预注册"相关的既有字段 | `pre_registered: bool`（`:98`，实测 True **6** / False **5**）、`viability_verdict: enum supported/refuted/inconclusive`（`:102`，实测 **11 条全 null**）、`n_trials`/`dsr_value`/`pbo_value` 齐备 | §8-B2 |
| 与 A 面交集 | **0**。册全文 `bizmine` 命中 0、`prereg` 命中 0；68 个卡文件名 stem 在六本最相近的册中命中 **0** | §8-B3 |
| 唯一 FK 悬空记录 | `pending_fk` 1 条（UNI-BASKET-001，status=resolved）⇒ 该册有 FK 治理面可承接新键 | §8-B4 |

**C 面｜台账 + CH + 回写册（对象=战役事件 / 策略件 / 因子件 / 节点）**

| 台账/表 | 行数（实测） | 状态列与值域 | 卡号可反查？ |
|---|---|---|---|
| `docs/_working/archive/2026-09/final3_campaign/w9_triage_ledger.md` | 2 表 186 行 | 列名"态"：C 127 / D 20 / 已归档 12 / P 6 / C-3 5 / E 4 / B 3 | ❌ 单字母缩写字典未在任何册定义 |
| `docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md` | 4 表 41 行 | "状态"：done 4 / running（…）1；另一表 done 4 / staged（--execute 等 Owner）1 | ❌ |
| `docs/_working/archive/2026-09/tdchain_mine/a0_master_ledger.md` | 4 表 46 行 | "状态"：执行中 4 / 挖干 1 / 挖干待合并 1 / 挖干（前班已完成）1 / 阻塞待终端 1 / 待 W1 1 / 待 E8 1；另表 ✅ 7 + 带括号 ✅ | ❌（且与 `tdchain_mine_closeout/` 下同名文件**等值重复**） |
| `docs/_working/archive/2026-09/bizmine_night/bizmine_campaign_ledger.md` | 3 表 55 行 | 时刻/车道/事件/产物（无状态列，卡以产物路径出现在"事件"散文里） | ❌（卡词命中 59 次，全为散文） |
| `docs/_working/fullflow_campaign/COORDINATION_LEDGER.md` | 18 表 180 行 | "状态"：在飞 9 / 待裁（…）1 / 待总包裁（…）1 | ❌ |
| `docs/_working/integrated_backtest/IBT-CAMPAIGN-LEDGER.md` | 2 表 29 行 | 无状态列 | ❌ |
| `docs/_working/archive/2026-09/sharpe2_prep/d_ledger/…executability.md` | 10 表 163 行 | "台账状态（分包D①）"：整句散文（如"15 行 pending，全判可考（D1 批）"） | ❌ |
| CH `c1_backtest.hypothesis_precheck` | 58 行 | verdict 三值（rejected 26 / passed 13 / deferred 19） | ❌ 键=candidate_id（CAND-*），卡号查询 0 行 |
| CH `c1_backtest.strategy_screen` | 1,340 行 | verdict 七值（screened_in 381 / deferred_c4 321 / rejected 216 / translated_c4 206 / oos_tested 160 / sim_deviation 52 / failed_obsolete 4）；strategy_id 去重 574、source_file 去重 1,007、run_id 去重 79 | ❌ 卡号/`prereg` 查询 0 行 |
| CH `c1_backtest.node_verdict` | 58 行 | verdict：pending 41 / valid 17 | ❌ 键=TDM node_id |
| `strategy_registry.yaml` | 161 条 | lifecycle_status 三值 + status 三值（两列同表，见 §1-S12） | ❌ 无 card 字段 |
| `factor_registry.yaml` | 175 条 | status 三值 + algorithm_status 三值 | ❌ 无 card 字段 |
| `backtest_backlog.yaml` | 142 条（机生，generated_by=scripts/backtest/generate_backtest_backlog.py） | confidence：untested 123 / valid 16 / pending 2 / verified 1；**文件头注释声明 `threshold_status=draft` 为预注册真源字段，实测 142 条对象里 `threshold_status` 出现 0 次**（F-09：注释承诺的字段不存在） | ❌ |

**对账结论（差异条数）**

1. **A↔B 交集 0 条 / 68 张卡全部脱册**：卡状态在 experiment_registry 里**一条都没有**，反之 B 面 11 条实验**无一条指向卡**。
2. **A↔C 交集 0 条**：三张 CH 判定表 1,456 行判决中**带卡号的 0 行**；7 本战役台账 500+ 行事件里**带 card_state 语义键的 0 行**。
3. **状态词汇 7 套互不相通**（实测枚举）：卡头 5 词元 + 无头（22 串）／REG-EXP `status` 4 值／REG-EXP `viability_verdict` 3 值／`hypothesis_precheck.verdict` 3 值／`strategy_screen.verdict` 7 值／`node_verdict.verdict` 2 值／strategy+factor 册各 3+3 值／台账散文态（w9 单字母 7 值 + tdchain 7 值 + fullflow 3 值）。**没有一个词映射表**（layering policy Step1 的"融合"处置从未做过）。
4. **反向缺口（机读面有、卡面无）**：S13 作废、S10 SEALED、S9 挂起 三态在卡面分别有 0/1/0 个实例，但各有 ≥1 条裁定在册（#363/#390/#398R2/#404R4）⇒ **裁定的效力没有落点**。

### 红条目点名册（图15 专属，F 号）

| # | 类 | 断点 | 证据 | 实测结论 |
|---|---|---|---|---|
| F-01 | 引用错位 | 普查 §4 与本战役简报把"封卡/复活唯一口语义"系于 **#304** | `ruling_registry.yaml:4120` #304=Regime r4/r10 重校准；`:3765` #331 条内 `renumber_note` 明载撞号改号；`:5217` #389 `related_rulings` 仍引 '裁定#304' 并称"④裁定#304 对做T 现形态的关闭维持不变" | **在册裁定自身引用错号**（应为 #331）。真源组=#363/#389/#390/#399/#404。图15 校验器必须以在册条目为凭据，不得继承此错引 |
| F-02 | 禁令型事故活体 | #389 批准"两卡即刻开测"时两卡早已测毕 | `:5197` #389、`:5219` #390（"Owner 记忆正确，方案班核实失职"） | 本图最大价值论证：**没有卡状态登记面，Owner 与方案班都会对已封契约重复点火**；#390 只能靠人工勘误补救 |
| F-03 | 状态滞后 | E1C-09 被裁定挂起（S9），卡 frontmatter 仍是 `status: frozen` | `docs/_working/archive/2026-09/kimi_audit/lane_reports/p3_prereg/P3-E1C-09.md:9` vs `ruling_registry.yaml:5369`/#404 R2 `:5595` | 裁定的效力无落点；"卡说它在 S3，裁定说它在 S9" |
| F-04 | 作废无面 + 状态记在注释里 | 全仓无一卡被标 S13；唯一近似记录在脚本头注释 | `scripts/audit/t0_gpu_condition_pack.py:1`「V2 已作废，其 §2.2 六段接线由 V3 §2 逐字继承」；`exam_policy.md:28-29` | 作废态存在（判据要求）但**不可查**；V2/V3 卡的谱系只存在于代码注释 |
| F-05 | 复活边无键 | 新卡以 `parent_context` 散文指旧证据，无 `revives: <card_id>` | `docs/_working/t0_revival/t0_conditional_prereg_card.md:1-14` | 复活链不可追溯 ⇒ 同一死假设可被后来者当新假设再考（#390 想防的事） |
| F-06 | 承诺的账不存在 | 负结果台账/死矿登记被判据强制，但无专册专件 | `exam_policy.md:52-58` §5（"落点：战役台账行 + lane 目录全量 results 件"）；76 本 catalogs 中无 negative/dead_mine 册 | 判据 §5.4 的"防同一死矿被反复挖"目前靠人记 |
| F-07 | 同假设双卡（X09 实弹） | T0-PRERG-01（`t0_regime/t0_prereg_vwap_revert.md`，头写"本役不跑数"）vs ALGO件③（`algo_mining/vwap_prereg_card.md`，27 格已考 RED）；#390 却记"T0-PRERG-01 已按 frozen 参数零改动执行完毕，verdict=RED"（affected_files 指向 algo_mining 那份） | 三处文本互斥（见左） | **卡号↔文件↔判决三者错绑**；#390 的"已测毕"证据实际属于另一张卡 ⇒ 直接印证 F-02 类风险 |
| F-08 | 字段册自述与条目不符 | `frontmatter_field_registry.yaml` `fields` 实测 58 条 vs 顶层 `total_registered: 53` | 实跑 yaml 计数 | 宪章 §4.3"计数用字段勿写死散文"在字段册自身失守；本图校验器一律读条目集合，不读 total 字段 |
| F-09 | 注释承诺的字段不存在 | `backtest_backlog.yaml` 头注声明"预注册=可审计真源（threshold_status=draft…冻结后才可跑）" | 142 条对象实测**无一条有 `threshold_status` 键** | 该面被文档当作预注册真源引用，实则字段缺失 ⇒ 不可挂（块B §1 候选面 D 的否据之一） |
| F-10 | 判据真源灭失（最硬） | 三个 production 脚本的 `[BLUEPRINT]` 锚指向不存在的卡：`docs/_working/t0_matrix/t0_ceiling_prereg_card.md`、`docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md` | 实测：`[ -f ]`=NO、`git ls-files --error-unmatch`=NO、`git log --all --name-only -- docs/_working/t0_matrix/`（19,381 commit）列出的 8 个历史文件中**无此两名** | **被代码引为判据真源的卡从未进过版本控制**（`scripts/audit/{t0_ceiling_capacity_exam,t0_gpu_condition_pack,t0_six_phase_materialize}.py:1`）；正是 #398 R3 所点"判据灭失病根"的现行实例 |
| F-11 | 判定书面不在版本控制内 | 工厂图 FAC-E4 store_refs 指 `data/backtest_artifacts/runs/`；`.gitignore:586` 整目录忽略；本 worktree 该目录**不存在**（仅 `bt-8607ffc2.json` 一个 tracked 件） | `ls data/backtest_artifacts/`、`git ls-files` | 结论书的物理档案换机即断 ⇒ 块B 不得把 run_archive 当状态真源（只可借其"只增不改+errata"形态） |
| F-12 | 卡语料有静默重复 | 2 组同字节双份（A 面表）；tdchain_mine 与 tdchain_mine_closeout 的 a0_master_ledger 同名等值 | sha256 前 12 位比对 | 双副本=双真源，违反 AGENTS §4.2；本图校验器需按内容哈希判重 |

## §4 重叠判定（旁轴，处置五选一：吸收/融合/扩展/废弃/引用）

| # | 撞车面对象 | 撞什么 | 处置 | 落地要求 |
|---|---|---|---|---|
| O1 | `config/strategy_production_map.yaml`（图9 工厂） | 同属供给端、E2/E4/E6 与卡的诞生/判定/封存时序重叠 | **引用（并列新轴）** | 本图 `node_id=D15-S*`，与 `FAC-*` 不同值域；图 YAML `boundary` 逐字写"工厂图=环节轴（对象=工序，build_status），本图=实例轴（对象=契约，card_state）"；三铁律引 `:20`；节点**禁**复制 exam_policy/E4 判据正文（X11） |
| O2 | `exam_policy.md` + `factor_mining_sop_policy.md` §4 卡模板 + `sop_b_node_loop.md` ⑦ | 状态迁移的**判据**与出口的**语义**全在三册里 | **引用 + 模板升级** | 本图不重述判据；但 S3 的字段集（`factor_mining_sop_policy.md:105-126` 模板）**必须升级**为含 `card_id/card_state/family_id/n_eff/revives/rejudge_used/credential` 的机读形态——这是块B 的施工标的，模板改一处、图与册各引一处，零新真源 |
| O3 | 卡 md 本体（68 份） | 若把卡正文入图 = 第二真源（宪法 §4.2） | **吸收其"状态"半、保留其"内容"全** | 状态与参数分离：卡正文仍为契约真源（frozen 参数、考窗、阈值、机制陈述），图/册只存 `{card_id, card_state, 迁移流水, credential, path}`；派生面（图 counts、状态分布）一律生成器现算，禁手抄 |
| O4 | `experiment_registry.yaml`（REG-EXP-001） | 同为"一次考试/一份契约"的登记簇（内收判据"同域重复簇→收敛唯一"） | **扩展（选定为宿主，非新建）** | 详见 `90_card_state_registry_spec.md` §1；扩 `card_state` 枚举 + 卡条目类 + run↔卡 1:N 键，**不新建卡册**（净零对价见其 §11） |
| O5 | `data/backtest_artifacts/runs/*` + `run_archive.py` + `sop_d` | 判定书/errata 形态与本图的"只增不改"同构 | **借形态，拒宿主** | F-11 实测该面 gitignored、本 worktree 不存在 ⇒ 不能当状态真源；仅复用其 `_STEP_FILES`/`errata`/`content_sha256` 语义做"卡正文完整性指纹"（X02 的机验工具） |
| O6 | `task_card_meta_registry.yaml`（PS-REG-017） | 都叫"卡"，都有 `migration_rules` + `state_machines_note` 结构 | **不并（引用）**：跨域不同对象 | 该册对象=**任务卡**（legacy/v2_staging/sqlite_task_db/高层规划四套，MR-05 明令"四套并行体系数量永久锁定为 4"）；策略卡塞入即污染并触发 MR-05 违例。**但借其结构先例**：元层摘要 + `migration_rules[rule_id/description/applies_to]` 正是本图禁止边机读化的现成形态 |
| O7 | 词汇撞名："策略卡/任务卡/裁定卡/候选卡/考卷/判定书" | `docs/_working/recovered_task_cards/tc06_ruling_cards/*` 是**裁定卡**（TC-06 R1-R4），`_working/2026-09-11-news-chain-wiring-spec-cards.md` 是**规格卡**，与策略卡无关 | **融合（术语归位）** | 立法前须进 `terminology_glossary.yaml`：建议术语 `预注册契约卡（prereg contract）` 为本图对象名，图15 内所有"卡"字均指该术语；否则校验器扫 `*_card*.md` 会误纳（本骨架语料口径已在 §8-A1 显式排除并留痕） |
| O8 | 图16 治理立法流（`fig16_ruling/`，同战役车道） | 全部人门位凭证=裁定，两图都要读 ruling_registry | **引用 + 车道会签** | 本图只存 `credential: <ruling_id>` 值，"裁定怎么产生"归图16；请总包在波2 组织 D15-M11/M14/M17 ↔ 图16 环节的对照表（勿两图各写一遍裁定语义） |
| O9 | 图11 交付流水线 / 图12 数据供给链 / 图13 交易日循环 / 图14 施工升级流 | 轴不同：本图无时间片、无 commit 机制、无数据供料、无施工步序 | **不并（无连接点）** | 唯一交点=图12 的数据面实查（`exam_policy.md:28`「数据面以考试时点实查为准，禁抄 prereview 声称值」）：本图 S3→S5 边上标 `data_plane_probe → DS-*` 引用，判据归图12 |

## §5 批次志（四类批次 + 增量曲线 + 三扫收敛判定）

| 批 | 类型 | 视角/做法 | 本批产出 | 增量 |
|---|---|---|---|---|
| B1 | 需求批 | 从消费端反向挖：普查 §4 缺口（`map_census:59`）、`exam_policy.md:24-30` 准入四条、工厂三铁律 `strategy_production_map.yaml:20-22` 需要契约载体 | 定域=实例级状态机（非环节流）；状态候选 6 → 13 | +7 态（S2/S4/S8/S9/S12/S13 由消费端缺口反推） |
| B2 | 三重扫描·①按生产者 | 逐家过谁能产卡/改卡：AI 起草（S3 模板）、机器矩阵（S2）、Owner 快签/终审（#389/#404）、执行件（`scripts/audit/*`）、裁定（凭证） | 生产者 5 类，逐类对应迁移 M01-M17 的触发者列 | +0 态，+3 边（M02/M10/M14 由生产者差异定出） |
| B3 | 三重扫描·②按形态逐类过 | 卡语料 68 份逐份解析 status/family_id/n_eff/lane 覆盖率（§8-A1-A6）；按 §3 三面对账 | 无头率 42.6%、22 种串、7 套词汇、三处零交集；红条目 F-03~F-09、F-12 | +2 态（S4 附录态、S9 挂起态由"同一假设不同形态"实测逼出） |
| B4 | 三重扫描·③按消费者文献 | 核现有消费面：代码 `[BLUEPRINT]` 锚 4,524 处（其中卡锚 5 处）、报告 `card:` 字段 5 份、CH 三表、两册回写、`trial_ledger` | 确认消费端存在但**无键可 join**；F-01/F-10（引用错号、判据灭失）在此批发现 | +1 态（S13 作废——原以为可由"重开"替代，实测注释里确有独立作废语义 V2/V3） |
| B5 | 案例批（2-3 张真实卡复原一辈子，含被 #363 重判过的那张） | 见下三链 | 状态机与禁止边的实证闭包 | +1 边（M17 复活跨实例边只在案例 A 完整可见） |
| B6 | 考古批 | `interface_contract_registry.yaml` 已归档（`ruling_registry.yaml:2046` 僵尸处置批 R3，现路径 `_archive/`）而 `_registry/vocabularies/contract_status_vocabulary.yaml`（draft/frozen/deprecated 三值）仍 active；`scripts/_archive/governance/d3_metadata/validate_frontmatter_values.py` 是已归档的 frontmatter 值校验器 | 解释"为何卡的 status 头能长期越界无人拦"：**拦它的校验器已退役**，只剩 `validate_ssot.py:55-62,241-250` 的 P1-1 "无效 status" 报告面（是否扫 `_working` 视调用参数而定）⇒ 块B 复用 contract_status 词表的方案被否（宿主已退役 + 跨域） | +0 态，+1 否据 |

**案例 A（唯一走完 M10 一次性重判 + M11 封卡 + M17 复活全链的卡）**｜T0-PRERG-02 funding carry：
`∅ →(M01) S3` 设计冻结 2026-09-19（`t0_regime/t0_prereg_funding_carry.md`，头 `status: 已封卡 SEALED（…）`，§2-§4 判据 frozen）→ `S3 →(M05) S4` §6 勘误（funding 由 8h 改小时级口径，"判定门槛三关数值不变"）→ `S4 →(M06) S5` 首考（`crypto_probe/funding_carry_results.md`，另批）→ `S5 →(M08) S7` verdict=RED（占位费率口径 +4.09% < 5% 门）→ `S7 →(M10) S4` **一次性重判**（凭 #363 `ruling_registry.yaml:4708`；`crypto_probe/funding_carry_rejudge.md:14` frontmatter 含 `ruling: 裁定#363`；§7 附录"修订项（唯一）"，其余 frozen 参数零改动）→ `S4 →(M08) S7` RED 变硬（+3.03%，差距 0.91pp→1.97pp；原判方向零翻转）→ `S7 →(M11) S10` **封卡 SEALED**（"后续无论红绿不再重开"）→ **横向事故**：`#389`（`:5197`）批准该卡"即刻进入历史回测窄测"→ `#390`（`:5219`）即日勘误作废该款并宣告"封卡效力维持，任何会话禁以 #389 为凭重跑两卡"（⇒ F-02 的实弹来源，也是 X03 的全部理由）→ `S10 →(M17) 新卡 S1` 复活：`docs/_working/t0_revival/t0_conditional_prereg_card.md`（2026-09-22，`family_id: T0-CONDITIONAL`，头 `status: frozen（本卡于任何考试取数之前写死…）`，parent_context 逐字引"裁定#399 二（做T复活改裁授权）"）。**复原 8 步迁移、命中 4 条禁止边的 3 条（X02/X03/X13 中 X13 现为缺陷）**。

**案例 B（S9 挂起态与卡面脱节的样本）**｜P3-E1C-09：`∅→S3`（`p3_prereg/P3-E1C-09.md:9` frozen，`family_id: P3-E1C-STABLE13`、`n_eff: 13`）→ `S3→S5→S8`（`experiments_ledger.md` biz4 行 verdict=存疑 fail-closed，IS 1.469 过 / WFA 2/3 折 / DSR 0.732 落 review 带）→ `S8→(M14) S9` 裁定挂起（`ruling_registry.yaml:5369` #398 R2 + `:5595` #404 R2"并入 IBT 批D 新鲜窗重考…禁直通模拟盘"）→ **卡面至今停在 `status: frozen`**（F-03）。同族 13 张卡（P3-E1C-01..13 + P3-B-EXP-01..06）+ 一份"窄化裁定书" `P3-B-NARROWING.md`（族级工件，也标 frozen）⇒ 实测存在**单假设卡 / 族卡 / 窄化裁定书**三种粒度，作业簿 02 必须定粒度轴（本骨架把三粒度归为同一状态轴的不同 `entry_kind`，不增态）。

**案例 C（draft→frozen 迁移唯一活体）**｜sector 线：`docs/_working/sector_line/sector_prereg_exam_cards_v0.md`（`status: draft（先于实验落盘；施工开工时冻结为 frozen，冻结后禁改参数）`）→ `sector_prereg_exam_cards_v1_frozen.md`（`status: frozen（2026-09-23 开工令即冻结…frozen 参数禁改，实现缺陷可修）`）→ 报告 `exam/prereg_exam_report_v1.md` + 机读 `exam/prereg_exam_results_v1.yaml`。**注意 M03 的正解是"同一卡号换文件版本"**，而 §1-S3 的真源实测允许"v0→v1 两文件并存" ⇒ 卡号↔文件不是一一映射（块B CV-03 唯一键设计必须处理：以 card_id 为主键、path 为可追加的 `versions[]`，否则把正常的 M03 判成 F-12 重复）。

**增量曲线**：状态数 6（普查先验：预注册/开测/RED/GREEN/封卡/复活）→ 13（B1-B4）→ **13（B5-B6 零新增）**。边数 8 → 24 → 29 → **30**（B4 补 M17 跨实例边；B5/B6 零新增）。
**三扫是否收敛**：①按生产者=**基本收敛**（5 类生产者与 17 条边的触发者一一对上，无剩余生产者）；②按形态（卡语料逐份）**未收敛**——68 份只做了字段覆盖率统计与抽样语义读，**未逐份核 status 头与其真实裁定/报告是否一致**（F-03/F-07 说明这类不一致的密度不低，波2 必做）；③按消费者=**未收敛**——已扫 config/src/scripts/data/schemas 与 CH 三表，但 **git 历史消费面未扫**（哪些卡号曾在提交里被引用、哪些已随目录搬迁消失，F-10 提示这里有一批账）。**封矿四判据均未满足，本件为波1 v1，不封顶**（见 §7）。

## §6 待挖清单（作业簿领取入口；编号即文件名契约）

按"生产者变→拆；验证口径变→拆；只是标签变→不拆"定簿。**P0=块B 登记面落地前置**（不挖则四道门第④门永不过）。

| 簿号 | 文件名 | 覆盖状态/迁移族 | 优先级 | 本簿要答的唯一问题 |
|---|---|---|---|---|
| 01 | `01_S3冻结族_卡模板机读化.md` | S1/S2/S3/S4，M01-M05 | **P0** | `factor_mining_sop_policy.md:105-126` 模板要加哪 7 个字段才够机读（card_id/card_state/entry_kind/versions[]/revives/rejudge_used/credential）？68 份历史卡的 status 串 22→13 的映射表谁写（"融合"处置）？ |
| 02 | `02_卡粒度轴_单假设卡与族卡与窄化裁定书.md` | S3 的 N_eff 语义 | **P0** | P3 先例三种粒度（P3-E1C-09 单假设 / P3-E1C-STABLE13 族 / P3-B-NARROWING 窄化裁定）如何共享一个状态轴而不撞 unique_key？中途窄化算不算 X08？ |
| 03 | `03_S5点火族_exam_policy四条准入的可验化.md` | S3/S4→S5，M06，X06/X07 | **P0** | 四条准入（frozen 卡 / 封闭族 / 沙箱三关 / 试验台账行）各自**现在**由谁保证？能用哪些既有件（`trial_ledger_registry.batch_records`、`run_archive.py` meta）机械判红？ |
| 04 | `04_S9S13族_裁定效力到卡面的落点.md` | S9/S13，M14-M16，X10/X12 | **P0** | 裁定改了卡地位（挂起/作废）而卡头不动（F-03/F-04）——回写走"卡头追加 + 册登记"还是"册为唯一真源"？M15 触发重考如何做到事件触发（宪法 §9.3 禁 cron）？ |
| 05 | `05_S10S11族_封卡与死矿的引用面.md` | S10/S11，M11-M12-M17，X03/X04/X13 | P1 | 死矿/负结果无专面（F-06）：内收到 `trial_ledger_registry` 加 `dead_mines[]`，还是 `experiment_registry` 加条目类？复活指针（revives）的最小可机读形态？ |
| 06 | `06_跨图边_卡与E4E6E7E8的引用契约.md` | S6/S12，M13，X09/X10/X11 | P1 | 卡毕业→strategy/factor 册回写的**来源键**（card_id）加在哪？挂起/封卡卡被 E7/E8 引用怎么拦？与图9 的 `store_refs` 三处（`:233/:283/:320`）互指形态 |
| 07 | `07_判据灭失考古_F10族.md` | 全态（真源完整性） | P1 | 全仓 `[BLUEPRINT]` 锚 4,524 处里，指向 `_working` 卡的有几处、其中几处已断链（F-10 只查了 t0_matrix 两条）？`data/backtest_artifacts/runs/` 的历史判定书有多少可再生？ |
| 08 | `08_词汇归位_四类卡同名消歧.md` | 域边界 | P1 | 策略卡/任务卡/裁定卡/规格卡/候选卡的术语立法（O7）；术语进 `terminology_glossary.yaml` 的等长替换方案（宪法 §6 上下文预算） |
| 09 | `09_三扫补齐_git历史与报告面消费扫描.md` | 收敛判据 | P2 | 卡号在提交史里的引用密度；1,816 份 _working frontmatter 中 `card:` 5 份的规范扩展路径；把 §5 三扫第②③扫做干 |
| 10 | `10_案例簿_三链逐格复原与禁止边命中表.md` | 全边 | P2 | 把案例 A/B/C 逐格复原成 `(card_id, from, to, credential, ts)` 流水（13 态 × 17 边的覆盖度计分）；用它当校验器的黄金样本 |

簿数=10（P0×4 决定登记面能否落地；P1×4 决定图的可信度；P2×2 决定何时封矿）。

## §7 封顶声明与🌑点名

**本件不封顶**（波1 v1，§5 三扫第②③扫未收敛）。封顶声明草案（待波2 落定）：「此后增长=卡语料的逐份一致性核对与迁移流水的补齐，不再增态；增态须过 `skeleton_mining_policy.md` §3 三问并留理由；新增状态一律先证明'有独立生产者 + 有独立验证口径'，仅标签不同者并入既有态」。

**按该判据主动拒绝/降级的候选态（防枝末先行）**：

| 候选 | 为什么不是状态 |
|---|---|
| "已归档 archived" | 生产者不变、验证口径不变，只是文件生命周期（`ttl` + `docs/_working/archive/` 目录契约）⇒ 降为卡的属性 `path`，不增态 |
| "Owner 已快签 / 待 Owner 签" | 是 M03/M04 的 `credential` 字段值，不是驻留态（实测 `kimi_audit/adjudications/B-族_尺子口径裁定书.md:8` `status: 待 Owner 签` 与本图无关，那是裁定卡） |
| "暂定（复权链断供）" | `exam_policy.md:46-50` §4 是**结论可信度档**，作用在报告与册回写，不改卡的法律地位 ⇒ 图里只允许 `conclusion_tier` 引用字段 |
| "sim_deviation / failed_obsolete"（CH verdict 值） | 属策略件工序结论（O1 边界 2）⇒ 不映射进卡状态 |

**🌑 点名（当前形态不可得 / 结构性不可机验，点名留档）**：

| # | 🌑 项 | 为什么不可得 | 处置 |
|---|---|---|---|
| L-1 | 卡历史迁移流水（谁在何时把卡从 A 推到 B） | **无流水面**：status 头只有当前值、无 append-only 历史；git 历史可推文件变更但 status 串改动 ≠ 迁移语义（22 种串自由书写） | 🌑 对本仓不可回溯（只可自登记面落地日**向前**建流水，向后无账）。图 YAML 须显式标 `history_from: <登记面落地日>`，禁假装全史可查 |
| L-2 | Owner 快签 / 终审 / 封卡 的人门位凭证 | 部分凭证是**对话原文**（#389 "对话原文为凭"、#399 "Owner 2026-09-22 夜批"） | 🌑 永久（宪法 §1.11 指令/数据边界：对话内口头不构成门禁豁免）。图只认在册 ruling_id；无册号的人批 ⇒ 校验器判 `credential: none` 并计红账（不是判红阻断，是显性留痕） |
| L-3 | 人工历史试错次数（DSR 的 N 真实下界） | `trial_ledger_registry.yaml` `manual_population: 0` + `manual_note`"人工历史试错不可审计，仅 Owner 登记时累加" | 🌑 永久；本图状态流水禁与 N 账本混轴，只在 S5 边上引用 batch_id |
| L-4 | 判定书物理档案 | `data/backtest_artifacts/` 整目录被 `.gitignore:586` 忽略，本 worktree 该目录不存在（F-11） | 🌑 对本 worktree 不可验；块B 校验器一律走 `--skip-artifacts` 语义，把该检查留在 align_all（同 FACTORY-MAP 把仓储存在性排除在 gate 外的先例，`validate_strategy_production_map.py` 头 INVARIANTS） |
| L-5 | 叶层：单张卡的全部字段与判据正文 | 骨架只到中类层（`skeleton_mining_policy.md` §3 停止判据） | 不枚举，交作业簿 01/02/09；图与册只存 card_id + 状态 + 指针 |
| L-6 | 「卡制度是否该由图9 承载」的最终裁定 | 属总包/Owner 权限（门③ 已给单立论证 + 反向扩节点清单，两条路都在桌上） | ⬜ 非 🌑：§0 门③ 反向清单 + 总包收口 X-2 已交，待裁 |

## §8 实查命令附录（全部只读，在仓库根 `.aidrafts/st-mapbuild-20260924` 执行；先设 PATH=Python 3.12）

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"

# ---- A 面：卡语料 ----
# A1 语料口径（文件名含 prereg/exam_card/_card/card_/protocol，排除 report/ledger/index/README/指令，并排除本车道自身产物）——实测 68
python -c "import re;from pathlib import Path;P=re.compile('prereg|pre_register|pre-registration|exam_card|_card|card_|protocol',re.I);X=re.compile('README|index[.]md|master_directive|general_order|ledger|report|ruling_cards|skeleton|fig15_cardlife',re.I);print(len([p for p in Path('docs').rglob('*.md') if P.search(p.name) and not (X.search(p.name) or 'fig15_cardlife' in str(p.as_posix()))]))"
# A1b 内容哈希判重（F-12：实测 2 组同字节）
python -c "import hashlib,collections;from pathlib import Path;P=re.compile('prereg|exam_card|_card|card_|protocol',re.I);X=re.compile('README|index[.]md|ledger|report|skeleton|fig15_cardlife',re.I);h=collections.defaultdict(list);[h[hashlib.sha256(p.read_bytes()).hexdigest()[:12]].append(p.as_posix()) for p in Path('docs').rglob('*.md') if P.search(p.name) and not (X.search(p.name) or 'fig15_cardlife' in p.as_posix())];print(len(h),{k:v for k,v in h.items() if len(v)>1})"
# A2/A3 status 头计数（实测 有头 39 / 无头 29 / 22 种串；按括号前首词元 frozen33 active3 draft1 候选1 SEALED1）
python - <<'EOF'
import re,collections
from pathlib import Path
P=re.compile(r'prereg|pre_register|pre-registration|exam_card|_card|card_|protocol',re.I)
X=re.compile(r'README|index\.md|master_directive|general_order|ledger|report|ruling_cards|skeleton',re.I)
rows=[]
for p in Path('docs').rglob('*.md'):
    if not P.search(p.name) or X.search(p.name): continue
    t=p.read_text(encoding='utf-8',errors='ignore')
    m=re.match(r'^---\n(.*?)\n---',t,re.S); fm=m.group(1) if m else ''
    s=re.search(r'^status:\s*(.+)$',fm,re.M)
    rows.append(s.group(1).strip() if s else None)
print('n=',len(rows),'有头=',sum(1 for r in rows if r),'种数=',len(set(rows)))
print(collections.Counter([(r or '<无>')[:70] for r in rows]).most_common(30))
EOF
# A4 status 头是否越界（实测词表三值，抽样卡 in_vocab 全 False）
python - <<'EOF'
import sys,re,yaml
from pathlib import Path
sys.path.insert(0,'scripts/governance/d5_architecture/validators')
d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/vocabularies/status_vocabulary.yaml').read_text(encoding='utf-8'))
v={x['value'] for x in d['values']}; print('vocab:',sorted(v))
for c in ['docs/_working/archive/2026-09/bizmine_night/t0_regime/t0_prereg_funding_carry.md',
          'docs/_working/archive/2026-09/bizmine_night/volume_family_l1/prereg_group_01_obv.md',
          'docs/_working/sector_line/sector_prereg_exam_cards_v1_frozen.md']:
    fm=re.match(r'^---\n(.*?)\n---',Path(c).read_text(encoding='utf-8'),re.S).group(1)
    s=re.search(r'^status:\s*(.+)$',fm,re.M).group(1).strip()
    print(Path(c).name, s[:40], 'in_vocab=', s in v)
EOF
# A5 卡结构字段覆盖率（实测 lane35 / family_id22 / n_eff19，均 ≤68）
# A6 报告→卡 frontmatter `card:` 字段（实测 5 份 / 1816 份带 fm 的 _working 文档）
python - <<'EOF'
import re
from pathlib import Path
n=tot=0
for p in Path('docs/_working').rglob('*.md'):
    t=p.read_text(encoding='utf-8',errors='ignore'); m=re.match(r'^---\n(.*?)\n---',t,re.S)
    if not m: continue
    tot+=1
    if re.search(r'^card:\s',m.group(1),re.M): n+=1; print(p.as_posix())
print('fm docs:',tot,'with card: field:',n)
EOF

# ---- B 面：experiment_registry ----
# B1/B2 条目与枚举（实测 11 条；completed10/running1；pre_registered True6/False5；viability_verdict 全 null）
python - <<'EOF'
import yaml,collections
from pathlib import Path
d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml').read_text(encoding='utf-8'))
e=d['experiments']; print('entries',len(e))
for f in ['status','pre_registered','viability_verdict','experiment_type','target_type']:
    print(' ',f,dict(collections.Counter([str(x.get(f)) for x in e])))
EOF
# B3 与 A 面零交集（六册中卡名命中 0；experiment_registry 内 bizmine/prereg 命中 0）
grep -c "bizmine\|prereg" docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml    # 0
# B4 该册的 FK 治理面（pending_fk 1 条，已 resolved）
grep -n "unique_key\|pending_fk\|status: str  \|pre_registered:\|viability_verdict:" docs/01_policies_and_standards/_registry/catalogs/experiment_registry.yaml | head

# ---- C 面：台账 + CH + 回写册 ----
# C1 台账行数与状态列（§3 表逐本；命令见 §3 行内口径）
python - <<'EOF'
import re
from pathlib import Path
L=['docs/_working/archive/2026-09/final3_campaign/w9_triage_ledger.md',
   'docs/_working/archive/2026-09/kimi_audit/experiments_ledger.md',
   'docs/_working/archive/2026-09/tdchain_mine/a0_master_ledger.md',
   'docs/_working/fullflow_campaign/COORDINATION_LEDGER.md']
for f in L:
    t=Path(f).read_text(encoding='utf-8',errors='ignore')
    print(f,'| 表行数=',sum(x.count('\n') for x in re.findall(r'((?:^\|.*\|\s*$\n?)+)',t,re.M)))
EOF
# C2 CH 三表（经 DatabaseService 唯一正门，禁裸 duckdb）
python - <<'EOF'
from zephyr.infrastructure.database_service import get_db_service
c=get_db_service().get_clickhouse_conn()
print(c.execute("SELECT countDistinct(database,name) FROM system.tables WHERE database NOT IN ('system','INFORMATION_SCHEMA','information_schema')"))
for t in ['hypothesis_precheck','strategy_screen','node_verdict']:
    print(t, c.execute(f"SELECT verdict,count() FROM c1_backtest.{t} GROUP BY verdict ORDER BY 2 DESC"))
# 卡号是否进过 CH：三条全 0
print(c.execute("SELECT count() FROM c1_backtest.strategy_screen WHERE strategy_id LIKE '%E1C%' OR source_file LIKE '%prereg%'"))
print(c.execute("SELECT count() FROM c1_backtest.hypothesis_precheck WHERE candidate_id LIKE 'P3%' OR notes LIKE '%prereg%'"))
EOF
# C3 回写册枚举分布
python -c "import yaml,collections;from pathlib import Path;d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml').read_text(encoding='utf-8'));s=d['strategies'];print(len(s),dict(collections.Counter([x.get('lifecycle_status') for x in s])),dict(collections.Counter([x.get('status') for x in s])))"
python -c "import yaml,collections;from pathlib import Path;d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml').read_text(encoding='utf-8'));s=d['factors'];print(len(s),dict(collections.Counter([x.get('status') for x in s])),dict(collections.Counter([str(x.get('algorithm_status')) for x in s])))"

# ---- 门③：与工厂图的切分 ----
grep -n "卡\|prereg\|预注册\|frozen\|SEALED\|封卡" config/strategy_production_map.yaml      # exit 1：零命中
grep -c "考试" config/strategy_production_map.yaml                                          # 5
python -c "import yaml;from pathlib import Path;d=yaml.safe_load(Path('config/strategy_production_map.yaml').read_text(encoding='utf-8'));print(len(d['nodes']),len(d['edges']),len(d['layers']),len(d['laws']),len(d['feedback_loops']))"   # 16 16 10 3 2
sed -n '20,22p;269p;283,285p;310p;320,321p' config/strategy_production_map.yaml            # 三铁律/E4 判据问题/store_refs
python -c "import re;L=open('scripts/governance/d5_architecture/validators/validate_strategy_production_map.py',encoding='utf-8').read();import sys;print([l for l in L.splitlines() if 'BUILD_STATUS' in l or 'STAGES' in l][:4])"

# ---- 门④：登记面缺失 ----
python -c "import yaml;from pathlib import Path;d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml').read_text(encoding='utf-8'));print(len(d['fields']), d.get('total_registered'))"   # 58 53（F-08）
grep -n "field_name: card" docs/01_policies_and_standards/_registry/catalogs/frontmatter_field_registry.yaml  # 无命中
grep -n "threshold_status" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml | head -3  # 只有注释行，条目零字段（F-09）
grep -n "total_registries" docs/registry_of_registries.yaml                                                 # 76

# ---- 裁定原文（迁移合法性真源，禁凭记忆）----
grep -n "ruling_id" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml | grep -E "#(304|325|331|363|365|366|389|390|398|399|404|409)'"
sed -n '4708,4722p;5197,5242p;5369,5400p;5409,5432p;5595,5617p' docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml
sed -n '3765,3772p' docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml   # F-01: #331 renumber_note 原文

# ---- F-10 / F-11：判据灭失 + 档案不在版本控制内 ----
grep -rn "^# \[BLUEPRINT\].*\(prereg\|_card\|card_\|protocol\)" --include=*.py src scripts    # 5 处卡锚
for f in docs/_working/t0_matrix/t0_ceiling_prereg_card.md docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md; do [ -f "$f" ] && echo "EXISTS $f" || echo "MISSING $f"; done
git log --all --name-only --pretty=format: -- "docs/_working/t0_matrix/" | sort -u | head    # 历史 8 文件中无上述两名
grep -rl "^# \[BLUEPRINT\]" --include=*.py src scripts | wc -l                                # 4524
sed -n '584,588p' .gitignore                                                                  # data/backtest_artifacts/ 被忽略
ls data/backtest_artifacts/ ; git ls-files data/backtest_artifacts | head                     # 仅 bt-8607ffc2.json，无 runs/

# ---- 块B 施工坐标 ----
grep -n "def make_map_alignment_gate" -A 22 src/zephyr/gov_enforcement/commit_gates/panorama_alignment_gate.py | head -30   # subs L295-302（现 6 行）
sed -n '170,201p' scripts/governance/d5_architecture/validators/validate_strategy_production_map.py                            # CLI exit 0/1/2 母版
sed -n '24,28p;86,110p;135,146p' docs/01_policies_and_standards/sop/backtest_system_sop/sop_d_run_archive_naming.md            # 只增不改/errata + meta.json + verdict 六段
sed -n '44,72p' src/zephyr/backtest/run_archive.py                                                                          # _STEP_FILES/_REQUIRED_STEPS
sed -n '1,12p' docs/01_policies_and_standards/_registry/vocabularies/contract_status_vocabulary.yaml                          # draft/frozen/deprecated（否据：宿主已归档）
grep -n "D_FACTOR\|D_BACKTEST" -A 3 docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml                 # 均 medium（本图含 high 语义迁移，见 X-7）
sed -n '64,66p;86,89p' docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md                               # §3 图目录与图 9 行（挂轴形态）
```

## 总包收口请求（本车道禁直写共享面，逐条请总包落）

| # | 诉求 | 目标共享面 | 建议处置 |
|---|---|---|---|
| X-1 | **纠错**：普查 §4 L59 与本战役简报把"封卡/复活唯一口"系于 裁定#304，实测该号是 Regime 重校准；做T 终止裁定现行号是 #331（renumber_note 在案）。另 `ruling_registry.yaml:5217` #389 的 `related_rulings` 与正文第④款仍误引 #304 | `docs/_working/map_census/00_panorama_map_census_v1.md:59` + `ruling_registry.yaml` #389 条目 | 普查行改写为"#363 重判一次→封卡；#389/#390 快签通道与封卡效力；#331（原#304）复活路径=预注册卡制；#399 二/#404 R4 复活唯一口"；#389 误引以**追加勘误注**方式治（勿手改历史正文，勿造新裁定号——挖矿期禁造裁定） |
| X-2 | 门③ 结论确认：图15 **单立**（实例轴），不走"并入工厂图扩 3 节点"。本骨架已给反向扩节点清单以免只出结论不出路 | `config/strategy_production_map.yaml`（挖矿期全域禁碰）+ 裁定册（施工期取号） | 请总包在波2 明确一句"两图分轴不违一域一图"，写进 `alignment_checklist.md` §3 图15 行的"对齐 key"注记 |
| X-3 | 登记面施工授权：本图选定的宿主是**扩 `experiment_registry.yaml`（REG-EXP-001）既有面**——需改 `entry_schema`（+card_state/revives/rejudge_used/credential/versions）+ 新增卡条目类 + 新 `_registry/vocabularies/card_state_vocabulary.yaml` + `frontmatter_field_registry.yaml` 登记 `card:`/`card_state:`。四者全在本车道禁写清单内 | catalogs + vocabularies | 见 `90_card_state_registry_spec.md` §1（三案实测二否一选，含被否理由与净零对价）；请总包代落或授权 |
| X-4 | gate 接法确认：不建独立台，在 `panorama_alignment_gate.py:295-302` 的 `subs` 追加一行（现 6 行；图14 车道同批要第 7 行 ⇒ 本图排第 8），并给 `in_process_gate_registry.yaml` MAP-ALIGNMENT 条目的 `files_trigger` 追加触发面 | src + gate 册 | 施工期同批；`total_gates` 不动（净零） |
| X-5 | F-02/F-07 属**已发生的治理事故**（Owner 批准开测时卡已封；同假设双卡两套 N_eff 账，且 #390 的卡号↔文件↔判决三者错绑）。本车道只点名不修，修复需裁定语义且涉裁定册 | 裁定册 + `docs/_working/archive/2026-09/bizmine_night/{t0_regime,algo_mining}/` | 请总包排一个"卡号谱系补齐"专项（波3 之后），勿让图15 校验器上线即被判为"故意误伤" |
| X-6 | F-06 负结果台账 / 死矿登记无面（`exam_policy.md:52-58` 判据强制但零落点）。是否新建？本骨架倾向内收到 O4 选定的同一宿主，不另立册 | catalogs + `exam_policy.md` | 若总包判"新建专册"，须同时声明替代哪份散文清单（AGENTS §4.1 全资产净零），否则图15 施工期会出现第二个状态宿主 |
| X-7 | 门位口径：卡状态迁移里 M11（封卡）/M14（挂起）/M17（复活）实质决定"能否流向模拟盘/实盘"，但 `risk_tier_registry.yaml` 中 D_FACTOR=medium、D_BACKTEST=medium、human_gate 均空 | `risk_tier_registry.yaml` | 建议把这三条迁移显式挂 Owner（宪章 §5.2"production 流转=high"），或在图 YAML 节点上带 `human_gate: owner` 并在 §3 图行说明与人门位表的关系 |
| X-8 | F-10 判据灭失（3 个 production 脚本的 `[BLUEPRINT]` 锚指向从未入库的两张卡）与 F-11 判定书面被 `.gitignore:586` 整目录忽略 | depgraph/blueprint 面 + `.gitignore` + `data/backtest_artifacts/` | 属跨域修复（脚本侧归数据线，gitignore 归治理线）；请总包统一排产。图15 校验器上线后会把这两类判红（规格 CV-09/CV-14），**属预期行为不是噪声**，勿为变绿而删判据或强行入库大文件 |
| X-9 | token 需求（挖矿期本车道 2 份 MD；施工期另五件） | `batch_creation_tokens.py --prefix docs/_working/map_build/fig15_cardlife` | 施工期新件：`validate_card_lifecycle_map.py` / `generate_card_lifecycle_map.py` / `card_lifecycle_gate.py` / `config/strategy_card_lifecycle_map.yaml` / `tests/governance/commit_gates/test_card_lifecycle_gate.py` |
| X-10 | 图11/图12/图13/图14/图16 五车道会签：本图与图16 共享裁定凭证面（O8）、与图9 共享 E4/E6 面（O1）、与图12 共享数据面实查（O9）；请总包在波2 组织一次"轴与键"互认（谁存 card_id、谁存 run_id、谁存 DS-*） | 各车道骨架 + `alignment_checklist.md` §3 | 波2 会签，勿在波3 施工期现编 |

**自审裁定**：欠——六向台账中「上/下/内/旁/史」五向已做实（旁=§4 九项逐条处置，史=B6 考古批含 contract 面退役链），**「新」向欠**（未做外部对标：学术/同业对 research pre-registration registry 的成熟形态——如 OSF Registered Reports / AEA RCT registry / RepliKat 的条目 schema 与状态字段，一句话结论待作业簿 01 补）；**「内」向 partial**（68 份卡未逐份核一致性，见 §5 三扫第②扫欠账，作业簿 09/10 承接）。溢出条目：本骨架新增"卡粒度三形态（单假设卡/族卡/窄化裁定书）"发现，已回写本件 §5 案例 B 与 §6 簿 02，未增态（判据=同一生产者同一验证口径，仅对象粒度不同，符合 `skeleton_mining_policy.md` §3 第三问"不拆"）。
