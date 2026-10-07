---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 B：治理横向面审计 findings

> 审计基准：git HEAD = `649a8c93c7`（2026-10-07）。被审对象=总包会话 st-mastertc 系（夜~10-07）。工作区 177 处漂移未计入本对象账。所有"绿/通过"类自述读数因禁跑 pytest 均标"待证"，仅静态可证部分作实。

## P0 候选

### P0-B1【交付完整性】R2 "own-diff 两件修复" 0/2 在 HEAD，终判定"连续两轮零失败成立"在 HEAD 不可复现

**子件 1：`tests/gov/rollback/conftest.py` 不在 HEAD，仅以未跟踪态存活于工作区。**
- 证据：`git ls-tree HEAD -- tests/gov/rollback/conftest.py` = 空；`git status --porcelain -- tests/gov/rollback/` = `?? tests/gov/rollback/conftest.py`；`git log --all --diff-filter=A -- "*rollback/conftest.py"` 全史唯一命中=`9a523ab8ee1`（2026-05-19，旧家=ARCH-029 废止的 tests+unit 旧目录下同名件，非本路径；字面旧路径拆写以免 GATE-NO-TESTS-UNIT 误伤审计文档）。
- 交付报告（HEAD 版 `docs/_working/master_tc_night/99_delivery/交付报告.md`）§六 R2 行自述（下同"自述"）："rollback 缺 conftest=own-diff 已修（新建 tests/gov/rollback/conftest.py……复跑 252P/7xF/2xP 净绿）"；§八.4："本班产出面：tests/gov/rollback/conftest.py（新）"。
- 实害：HEAD 上 `tests/gov/rollback/test_rollback_verifier_unit.py:188` 签名 `(self, live_gates_ddl, live_tasks_projection_ddl)`，两夹具唯一定义在未跟踪 conftest（工作区文件字节与自述 DDL 相符：`CREATE TABLE gates` migration 34 逐字+tasks 投影+`insert_live_gate_row` 3 夹具）——HEAD 检出即 fixture 收集错误，"R3 rollback 252P 零 F"读数依赖未提交文件。

**子件 2：`tests/gov/rule/test_rule_red_blue.py` 预算放宽（自述"300→540+marker 420→620，已落仍超时"）在任何位置都不存在。**
- 证据：HEAD 读数 `timeout=300`（L210）、`@pytest.mark.timeout(420)`（L337）、`@pytest.mark.timeout(900)`（L368）——无 540/620；`git log -3 -- tests/gov/rule/test_rule_red_blue.py` 最后落库= `4727fb87cd`（夜战前 P10 袋）；工作区该文件 `git status --porcelain` 输出为空（clean，与 HEAD 无差）。
- 即：交付报告 §六"预算 300→540 同款放宽已落仍超时"与 §八.4"产出面……test_rule_red_blue.py（预算放宽）"两处自述与 HEAD 及工作区双向不符。

**判定影响**：§八.6 终判定"own-diff 面连续两轮（R2 终态/R3）零失败成立"的测试态，一半建立在未提交工作区（conftest）、一半建立在不存在改动（rule_red_blue）上。按"一切以 git HEAD 实证为准"口径，该终判定**不成立**；交付报告 §七 原判"ISSUES(3 项移交)，非 TWO_ROUNDS_ZERO"反而是与 HEAD 相容的口径。verdict（终判定句）：**假完成**（就 HEAD 而言）；conftest 本体在工作区的实现内容=**过渡**（件在册未落 git）。

## 逐项 verdict（1~7）

### 1. C97 悬空锚（d2fb212a22）——**真完成**

- 3 处锚改指在 HEAD 全部实证：`git grep -n "ALGO_FLOW" HEAD` 命中 `scripts/governance/generators/generate_fms_deadref_baseline.py:45`、`src/zephyr/gov_enforcement/commit_gates/read_side/__init__.py:26`、`read_side/fms_hygiene_gate.py:60`，三处均指向 `docs/03_modules/_domain_gov_enforcement/algo_flow/commit_gates/f/fms_hygiene_gate.yaml`。
- 锚链真实可达：目标 yaml 在 HEAD 存在（blob `0c4c58e553`），头注含 `source_of_truth: src/zephyr/gov_enforcement/commit_gates/read_side/fms_hygiene_gate.py` 且该真源文件在 HEAD 实存（即上列 L60 锚所在文件）；yaml 含可解析 `algo_flow: |` 块。
- 旧悬空目标 `read_side_fms_hygiene_gate.yaml` 在 HEAD 树 0 实体（仅作业簿/报告文字提及）。
- 自检断言在位：`tests/gov/governance/commit_gates/test_algo_flow_link_gate.py` L586-596 `test_c97_read_side_live_anchors_resolve`，钉 3 文件 live 锚可达，注释含契据（born-dangling/改指依据）。

### 2. C157 相计时（cd6ad4f7d0 + 24635c2309）——**真完成（观测面）；非执法面；消费链=过渡（设计内）**

- 共享 helper 在 HEAD：`src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py:147` `_timed_phase`（contextmanager，fail-safe 吞异常）+ `_phase_ms`/`_PHASE_ACC`；`_stat_flush` L113 条件写 `rec["phases"]`（无相不写键，向后兼容）。
- 三台重门挂相在 HEAD：GATE-PRECOMMIT-RUN（`git_commit_gateway.py:3970/3984/4006` = index_build/hooks_run_fast/hooks_run_slow_tail）、CREATE-GUARD（`create_guard.py:1738/1770/1779` = registry_load/dup_lookup_build/keyword_overlap）、FMS-HYGIENE（`read_side/fms_hygiene_gate.py:285/294` = baseline_load/ref_scan）。
- 4 单测在 HEAD：`tests/gov/governance/rule_bridge/test_commit_gate_registry.py` L444/457/465/487（记账/异常吞噬/jsonl 落盘/无相省键）。
- sleep 修复在位：`24635c2309` diff `time.sleep(0.01)`→`0.05`，HEAD 测试 L438-442 含 GetTickCount64 15.625ms 根因注记。
- **下游消费判定：`phases` 字段当前零代码消费方。** `git grep -n gate_execution_stats HEAD -- scripts/ src/ tests/` 全部命中为写入面/规划文档（`docs/_working/ai_layer_vision/P1_construction_plan.md` S4 体检器=规划消费者，前置"gate_execution_stats 积累 ≥1 窗"未满）。产线数据面真实：`.runtime/audit/gate_execution_stats.jsonl` 现存 51 行含 phases（审计时点实测）。
- 结论：这是**真实运行的观测仪表**（代码、数据、测试三面齐全，卡面自declared"fail-safe 观测性质"），**不是执法面**（对放行/拦截零影响）；"谁读 phases"的答案是"今天没人读"。作为 C157 卡面交付=真完成；作为性能治理闭环=过渡（消费方 S4 未建成，属登记在案的既定排期，非隐性断链）。

### 3. C128 library_hygiene --check-new-files（e4e961b317）——**CLI 真完成；执法接线=遗漏（自告残留）；现态=过渡**

- 实际运行（只读）：`python scripts/governance/generators/library_hygiene.py --check-new-files` → `WARN: …rowvec_promotion_v1.md`、`WARN: …ext_05_minute_k_persistence_design.md`、`check-new-files: missing_created=2（warn 恒放行…）`，退出码 0。两 warn 件均他车道在途件（st-vm12final/st-mx07 面），不计本账。
- 挂册面查证：`git grep -rn "working-doc-created" HEAD` 全树唯一命中=`docs/_working/master_tc_night/lanes/L1_gov_a/00_workbook.md`（作业簿文字，含 q-0004 死袋案的旧自述".pre-commit-config.yaml 挂册"）。HEAD `.pre-commit-config.yaml` 的 hook id 清单（L64-478 逐条）**无** working-doc-created；gate_registry.yaml 亦无该门条目。
- 结论：该检查目前**仅有 CLI 孤立面，无任何常驻触发器**——未挂 pre-commit、未进 gate 链，无人调用则永不运行。commit message 自告"hook 挂册=卡面外残余留维护班"与实证一致（自述如实），但按"真被接线执法"标尺=**遗漏**；warn 恒 0 放行+无人触发，双护甲下实际执法力=0。

### 4. f95c1cd784 八卡逐项

| 卡 | verdict | HEAD 证据 |
|---|---------|-----------|
| C443 snapself 尺重钉 | **真完成（静态）**；7/7 绿=待证 | `tests/gov/governance/resilience/test_commit_queue_snapshot_selfconsistency.py` 7 个 test 函数（`git grep -c "def test_"`=7）；L39-50 契约迁移注记引 Owner 终裁+`7e737d7af6`（该 commit 实存，全路径合并仲裁治本）；H1 防回退=`commit_queue_landing.py:2196/2228` noop_audit 审计面、H2 防吃字=L2205 `RuntimeError("…双侧皆改真冲突…")`、H3 原断言保留（L329 test_h3）——"零放水"三性质的行为级锚全部在 HEAD |
| C338 RECONCILER-FILE-OPS own-diff 化 | **真完成** | 门本体 `reconciler_file_ops_gate.py:121-157 scan_own_diff_for_bare_primitives`：modified 只判 `_get_added_lines`（unified=0 新增行集合）、`head_text is None` 新文件退全文扫描、`if not added: return []` fail-open 放行——三分支与自述逐字吻合；新尺 4 函数 5 用例（parametrize×2）在 `test_reconciler_file_ops_gate.py`，判定语义逐条对齐 |
| C304 CREATE-GUARD files_trigger | **真完成** | `gate_registry.yaml:901-915`：`files_trigger: ['*.py','*.yaml']`+注记（tests/ 豁免、非 rules/ yaml 才有判责面）+own_scope: true，机生面在册 |
| C268 p2_five 设计稿 | **真完成（设计稿性质）** | `lanes/L2_gov_b/p2_five.md` 在 HEAD，frontmatter task_bound；施工件明示排队移交，无越权伪落地面 |
| C346 禁用期回溯案卷 | **真完成（案卷落地）**；0/30 结论=待证（抽样自述） | `c346_retrospect.md` 在 HEAD；方法=417 新建 .py 等距抽样 30 三检（token/同名/存活），可复算非全量——结论置信度受抽样法限定，卷面已如实写明方法 |
| C150 k=6 维持 | **真完成** | `commit_speedup_campaign/90_verification/decisions_log.md:40` 一行在 HEAD（746 commit/9 日吞吐、k=4 无瓶颈、维持不扩） |
| C461 销账 | **真完成（vacuous）** | 作业簿 L161-169：census 全量无 D 态，卡面"仅 2 件"前提消失；前提消失型销账合法 |
| C202 销账 | **真完成** | 抽复核两路吻合：`git ls-tree -r HEAD -- src/zephyr/ex_sor/ *.py`=29=`git log --all --diff-filter=A` ever=29；`.runtime/commit_queue/dead/` 1520 袋中 ex_sor 命中=0。缺件清单=空集自洽 |

### 5. C27 "mode=warn 待自动翻转"机制真伪——**评估器真实现；翻档=不存在也不承诺自动；无拖延性假承诺，但资格函数零调用零测试**

- 机制链：`fms_hygiene_gate.py:119 BLOCK_FLIP_CLEAN_STREAK=20`；L341-366 `consecutive_clean_commits()` 机读 `.runtime/gate_audit/fms_hygiene.jsonl` 尾部连零（保守计数：坏行/未扫查/有 findings 均中断）；L368-373 `block_flip_eligible()`=连零≥20。
- **自动翻转不存在，且代码明示这是设计**：L114-116"mode 翻转本身仍=OWNER-GATE（本常量保持 warn，改 block 须 Owner 批准）"；`FMS_HYGIENE_GATE_MODE="warn"` 为模块级硬编码常量；运行时判定仅 L352 `if FMS_HYGIENE_GATE_MODE == "block"` 分支——无任何代码路径在运行时改写 mode。
- **资格函数零消费者**：`git grep block_flip_eligible|consecutive_clean_commits HEAD -- src/ scripts/ tests/` 除本体外 0 命中（含测试 0 条）——机读资格评估建成但未接入任何巡检/呈报链。
- live 读数（审计时点复算）：连零=**2/20**（总 525 记录，PERM-EPHEMERAL 持续打断连零，与报告归因一致）。
- 交付报告口径诚实：§六 L183"判据 0/20 未满足不硬翻——待自动翻转不可得，须处方（基线收编或改道）"；骨架态=WAIT→Owner。**结论：非"YAML 注记式拖延"，是"评估器真+翻档权人工（Owner 门位）"的两段制；唯"自动翻转"一词若脱离报告上下文会被误读为自动化在途——实际自动化仅到"资格可机读"为止。**

### 6. "连续两轮零失败"自告复核（静态可证部分）

- (a) `tests/gov/rollback/conftest.py`：**不在 HEAD**（见 P0-B1）——自告"R2 补建"仅工作区未跟踪态成立。
- (b) trae_rules 48F 终修：**真完成（本项在 HEAD 成立）**。`git ls-tree tests/gov/trae_rules/ test_g_trae_*.py`=48 件；`tests/meta/fixtures/` yaml=48 件；抽 003/004/006/007 四件字节级核对：L16 `MOCK_YAML = PROJECT_ROOT/"tests"/"meta"/"fixtures"/"g_trae_00X_mock.yaml"`+L70 存在性断言，与 `5ed131fb1d`（48 件各 1 行重指）一致。480P 读数=待证。
- (c) 遗留 2 项如实移交：`tests/gov/session/test_session_concurrency.py:909 test_logical_request_exempt` 在 HEAD（docstring 自述"logical 豁免……不被限流"，与"裁定#480 chief-form 语义漂移"归因相容；语义对错静态不可判）；`tests/gov/rule/test_rule_red_blue.py:395` 硬断言 `detection_rate >= 0.95` + subprocess timeout=300（L210）/marker 420（L337）在位——">540s 病理致 8/9=0.888<0.95"失败面与代码结构相容，移交口径自洽。
- (d) 交付报告口径判定：**trae_rules 终修表述与 HEAD 相容；"零失败成立"表述=夸大**。同一文档内 §七 L217"判定=ISSUES(3 项移交)，非 TWO_ROUNDS_ZERO"与 §八.6 L240"own-diff 面连续两轮（R2 终态/R3）零失败成立"两判并存，后者靠 scope 收窄（把 3 项划出 own-diff）+P0-B1 两件未落 git 的修复支撑。按 HEAD 口径应维持 §七 的 ISSUES 判定。

### 7. 图10/图16（cdd1246dc6）——**真完成（时点快照口径）**

- 账本 304→305 实证：`git show cdd1246dc6^:config/governance_legislation_map.yaml` counts=`entries_total: 304` → HEAD=`305`（L232）；`by_status` 282+13+1+4+2=302=ledger_rows_active，内部自洽（entries_total 305 vs active 302 的 3 差=L243 D16-N6 在途窗口声明）。
- CV-05 对抗尺在 HEAD：`tests/governance/d5_architecture/test_governance_legislation_map_adversarial.py` 15 个 test 函数（含 `test_real_map_live_counts_tie`）="15/15"自述总数吻合；校验器 `validate_governance_legislation_map.py:265 check_live_faces` 为真实 live 对拍（经生成器 `read_ledger_counts()` 读 PG 账本逐键比对，硬 error）。
- 图10：`config/strategy_card_lifecycle_map.yaml:4594 cards_total: 105`=自述 cards=105 ✓；对抗尺 `tests/gov/governance/d5_architecture/test_strategy_card_lifecycle_map_adversarial.py` 70 用例="67绿/3红"总数相容（3 红移交面待证）。
- 审计期间只读复跑校验器：`python scripts/governance/d5_architecture/validators/validate_governance_legislation_map.py` → `ERROR: CV-05 counts 漂移: entries_total 图=305 账本=306（重跑生成器回灌）`。**此为 commit 后账本继续前进 1 笔的时点漂移**，图 laws 明示"实例对拍只对生成时点负责"，不计被审对象账；登记为待回灌项。

## 证据块

| # | 命令 | 读数 |
|---|------|------|
| E1 | `git grep -n "ALGO_FLOW" HEAD -- <3 文件>` | 3 行均指 `f/fms_hygiene_gate.yaml`（L45/L26/L60） |
| E2 | `git ls-tree HEAD -- …/commit_gates/f/` | blob 0c4c58e553 `fms_hygiene_gate.yaml` 实存 |
| E3 | `git show HEAD:tests/gov/governance/commit_gates/test_algo_flow_link_gate.py` L579-596 | `test_c97_read_side_live_anchors_resolve`+3 文件清单 |
| E4 | `git show HEAD:src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py` L127-172 | `_timed_phase`/`_phase_ms`/fail-safe 注记 |
| E5 | `grep -c phases .runtime/audit/gate_execution_stats.jsonl` | 51 行产线含 phases |
| E6 | `git show 24635c2309` diff | `-time.sleep(0.01)`→`+time.sleep(0.05)`+根因注记 |
| E7 | 实跑 `library_hygiene.py --check-new-files` | missing_created=2，exit 0 |
| E8 | `git show HEAD:.pre-commit-config.yaml` id 清单 | 64~478 行无 working-doc-created |
| E9 | `git show HEAD:config/.../gate_registry.yaml` L901-915 | CREATE-GUARD `files_trigger: ['*.py','*.yaml']` |
| E10 | `git show HEAD:reconciler_file_ops_gate.py` L121-157 | own-diff 三分支判定体（摘录见 §4/C338） |
| E11 | `git log --all --diff-filter=A -- "*rollback/conftest.py"` | 唯一=9a523ab8ee1（2026-05-19，tests/unit 旧家） |
| E12 | `git status --porcelain -- tests/gov/rollback/` | `?? tests/gov/rollback/conftest.py` |
| E13 | `git show HEAD:tests/gov/rule/test_rule_red_blue.py` grep timeout | 60/300/420/900，无 540/620；`git status` clean |
| E14 | 实跑 `validate_governance_legislation_map.py` | `CV-05 counts 漂移: entries_total 图=305 账本=306` |
| E15 | 复算 `fms_hygiene.jsonl` 连零（纯读脚本） | live_consecutive_clean_commits=2 / 525 记录 |
| E16 | `git ls-tree` 计数 | test_g_trae_*.py=48；tests/meta/fixtures/*.yaml=48；legislation 对抗尺=15；strategy 对抗尺=70；snapself=7 |

## 小结

**真完成**（HEAD 实证）：C97、C338、C304、C150、C461、C202、C268、C346（案卷面）、C443（静态三性质锚）、trae_rules 48F 终修（5ed131fb1d）、图10/图16 时点回灌、C157 的仪表本体、C27 的连零评估器。

**真执法**：C338（判定面真实从全文收窄到 own-diff，门行为改变）、C304（触发面登记真实收窄 CREATE-GUARD 触发集）。C157 不是执法（观测仪表，其价值待 S4 消费方兑现）。

**过渡**：C157 phases 面（有数据无消费方，排期内在途）；C128（CLI 孤立无触发器）；C27（资格评估建成、翻档权按设计留 Owner，但资格函数零调用零测试=半闭环）；P0-B1 的 conftest（件在工作区，未落 git）。

**不必要**：未发现（八卡均有真实对应物，无空转卡）。

**遗漏**：C128 hook 挂册（自告但仍是缺口）；P0-B1 两件"产出面"未落 git——这是本车道唯一硬伤。

**待证**：所有 pytest 绿读数（7/7、5/5、480P、252P、15/15、67/70——总数与静态结构全部吻合，失败面未见矛盾）；C346 的 0/30（抽样法自述，非全量）。

**P1 建议**
1. P0-B1 立即补救：conftest.py 走正常 claim+commit 入库；rule_red_blue 预算修改若确曾做过须查明灭失环节（队列袋/stash/未写盘），若未做过则更正交付报告 §六/§八.4 两处"已落"表述——交付报告矛盾=事故级（宪法 §4.3 自律条款）。
2. C128 挂册落地时同步把"warn 恒 0 放行"的升硬前置（存量清零+Owner 批）登记为可判据条目，避免 CLI 永久孤悬。
3. C27 资格函数补最小单测+一个定时读数出口（读数进既有审计面即可，勿立 cron——永久系统四要素红线），否则"机读资格"只是库函数。

**P2 建议**
1. C157 phases 消费方落地时在 `docs/_working/ai_layer_vision/P1_construction_plan.md` S4 处回链 phases 字段 schema，防消费时口径漂移。
2. 图16 待下次回灌（账本已 306）；strategy 图 3 红对抗项在移交窗内应有时限。
3. 交付报告 §七/§八.6 两判并存建议在 §八.6 加一行显式声明"本判定 scope=own-diff 子集，总判仍=§七 ISSUES"，消除双判读空间。
