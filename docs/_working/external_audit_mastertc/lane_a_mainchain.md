---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 A：纵向主链链路审计 findings

> 审计员：车道 A（纵向业务主链：数据供给→信号→回测→实盘）。被审对象=st-mastertc 系 2026-10-06 夜~10-07 施工。方法：一切结论以 git HEAD（`649a8c93c7` 时点）与 `.runtime/commit_queue/` 袋档实证为准；台账/工作簿/交付报告仅作"自述"引用。全程只读（仅 `git show/grep/ls-tree/log --all`、`ls/cat`、`python ast.parse` 纯读）。

## P0 候选

| # | 卡/袋 | P0 定性 | 一句话定谳 |
|---|---|---|---|
| P0-1 | C232/C234/C235（袋 recover-0005） | **假完成+断链** | 交付报告标 DONE"已施工"，HEAD 全树**零字节**；袋为死袋（四投四死：l6-0001→l6-0004→recover-0005 首投 GATE-ANY-ABUSE→重投 MAP-MOUNTS，`dead_at=2026-10-07T19:13:47+08:00`），字节仅存活于死信 blob 与工作区未跟踪文件。纵向主链信号段**不存在于 HEAD**。 |
| P0-2 | C75 接线件（袋 recover-0003） | **假完成+断链** | 交付报告 C75 DONE"CNS 消费接线 1 件"，`src/zephyr/factor/analysis/tech_factor_pipeline.py` HEAD 零字节；袋两投两死（l6-0002→recover-0003，`dead_at=19:20:40`，CREATE-GUARD"无 creation_token"——袋自述"token 已随注册表袋登记"与门禁实测矛盾）。 |
| P0-3 | C107 Fill 单一写者（袋 mini-0003） | **假完成** | 交付报告"Fill 单一写者落地，8/8+装配回归 47/47"标 DONE；HEAD `scripts/start_paper_session.py` 无 `_PaperFillJsonlWriter`（`git grep _PaperFillJsonlWriter HEAD` 仅 L7 工作簿自述 1 命中），测试件不在 HEAD；袋死于 GATE-PRECOMMIT-RUN（gate-naming）。实盘执行段写者纪律件**未落地**。 |
| P0-4 | C233 前视注入红证尺（袋 mini-0002） | **假完成** | 交付报告"前视注入红证尺 14 位，16/16 绿"标 DONE；`tests/backtest/test_lookahead_injection_red_ruler.py` HEAD 不存在；袋死于 ALGO-FLOW-LINK（为 grid_stats/lead_lag 恢复 ALGO_FLOW 外部锚指向不存在的 yaml）。 |

P0-1~P0-4 共性：**施工真实发生、自述口径真实记录了施工，但"完成"挂在死袋上**——台账三态（DONE/GREEN）与 HEAD 字节态脱钩，晨会按交付报告读数会全盘误判。

## 逐项 verdict

**项1 信号三模块（event_axis/swing_sequence/resonance_pair，自告"袋 recover-0005 完成"）——verdict：假完成（施工在途，落地死袋）。**
(a) 自告口径与袋真实状态：`git log --all --grep="recover-0005"` 零提交；袋档 `.runtime/commit_queue/dead/q-20261007-st-mastertc-recover-0005.json` 证实其为**死袋**（内容=三模块+三单测+capability 册，dead_reason=CREATE-GUARD MAP-MOUNTS 阻断，`recurrence_fused=true`，袋内补记自述首投死于 GATE-ANY-ABUSE 已修 `Any→object` 后重投再死）。原 L6 车道袋 l6-0001、l6-0004 同内容物亦均 dead。模块文件在 HEAD 零命中，工作区 `??`/`A` 态存活。
(b) 对应卡号：C232（event_axis，MOD-SIG-146）、C234+C253（swing_sequence，MOD-SIG-147）、C235+C252（resonance_pair，MOD-SIG-148）。桌面终态注记：交付报告 126 卡总表四卡全标 DONE（"已施工"）；环节总表挂接行标 G；120 卡表主环节=F017/F022。
(c) 结论：施工完成≠落地完成；以"HEAD 字节在+消费链可达"判据为**假完成**，工程本体待死袋清偿后重投。

**项2 tech_factor_pipeline（自告"袋 recover-0003"）——verdict：假完成（同构死袋）。**
`git log --all --grep` 零命中；`dead/q-20261007-st-mastertc-recover-0003.json` 证实死袋（另携同路径锁超时 env_retry=1 史）；原袋 l6-0002 亦 dead。HEAD 零字节、工作区 `??` 存活。挂接卡=C75（L6 车道，120 卡表主环节 F011 次挂 F120，标 G；交付报告标 DONE）。注意：HEAD 翻译登记册已有其条目（见下 P1-1），登记面先于本体落地。

**项3 grid_stats_engine + lead_lag_validator（abed5f7a1f）——verdict：真完成（观察轨/预注册口径），生产打通=按设计未点火，非断链。**
(a) HEAD 字节在位：两引擎+两单测四件全在（`git ls-tree HEAD` 命中 4 blob；`grid_stats_engine.py` 21732 字节）。
(b) 消费链：`git grep` 全仓剔除自引用后，消费者=①`tests/backtest/test_grid_stats_engine.py`/`test_lead_lag_validator.py`（单测）②`config/chart_resonance_prereg.yaml`（C237 预注册冻结件，L38/41/45 显式声明 `engine: scripts/backtest/grid_stats_engine.spa_reality_check/.stepm/.evaluate_grid/.half_split_reexam`，L90"与本册互为镜像"）③注册册（capability/translation）。**无生产调用方**——但模块头 `[INVARIANTS] ★READY_NOT_FIRED` 明文"禁点火/不入账本，正式跑推迟波 12（G-D.4 Owner 门位）"，`10_wave_plan.md` L190 真源行在 HEAD 同口径。lead_lag 头部明示"观察轨 P2 不接生产"。零生产消费是**规格内的诚实状态**。
(c) 三图挂点：`strategy_production_map.yaml`/`trading_decision_map.yaml`/`data_supply_chain_map.yaml` 三图 `git grep` **零挂点**——挂点义务载体为 prereg+10_wave_plan（均在 HEAD 且互为镜像），且 MAP-MOUNTS 强制面按其门禁口径限 `src/zephyr` 新建 .py，scripts/ 域两引擎不构成违规；但波 12 点火时须补图挂点。环节总表对应行：C238→F068、C236/C239→F023（次 F066），挂接在表。

**项4 fill writer / reaper 现算化（mini 系列）——verdict：reaper=真完成；fill writer=假完成；C233 红证尺=假完成。**
- reaper（C324）：袋 **mini-0004 done** → commit `a6ae287dab`。HEAD `src/zephyr/trading/process_reaper.py` L1332 `_compute_live_report()`、L1344 状态输出"默认现算（live 只读扫描），现算失败回退 last_run.json 文件（C324，2026-10-07）"在位；审查机构已实测 `python -m zephyr.trading.process_reaper --status` 输出 `source=live scan_mode=live_dryrun killed=0`（运行时证据，直接引用）。
- fill writer（C107）：袋 **mini-0003 dead**（GATE-PRECOMMIT-RUN/gate-naming）；writer 载体=`scripts/start_paper_session.py`（registered module，非新 src 模块），HEAD 该文件存在但**无 `_PaperFillJsonlWriter`**，测试件不在。
- C233 红证尺：袋 **mini-0002 dead**（ALGO-FLOW-LINK，为两引擎恢复的 ALGO_FLOW 外部锚指向从未存在的 yaml——注意 abed5f7a1f 已按"锚删除"方案落地，mini-0002 是反向恢复且被拦，HEAD 现态=两引擎无 ALGO_FLOW 锚，一致性成立）。
- 袋位总账（实为四袋非三袋）：mini-0001 done（L6 车道簿 docs 面）/mini-0002 **dead**/mini-0003 **dead**/mini-0004 done。

**项5 环节总表挂点完整性——verdict：读数真实（抽检 5/5 全对）、120 卡挂接无遗漏，但六卡终态注记与 HEAD 失真（P1）。**
读数抽检（`git grep -c "环节"` HEAD）：fullflow `00_orchestration.md`=**9** ✓、nightsweep=**10** ✓、workorders=**1** ✓；132 表状态轴 `已通=64/开口=57/等Owner=11`（逐行 grep -c 实测）✓；表体 F 行=**132** ✓；F123-F132 真源 `00_skeleton_verified.md` 在 HEAD ✓。指针小瑕：总表称 132 表"L22 起"，实为 L16（P2）。120 卡挂接表实数 119 C 行+X01=120 ✓；今晚新模块**无"有模块无卡"遗漏**（C232/C234/C235/C252/C253/C75/C236/C238/C239/C107/C324/C216 全部有行）。失真点：C232/C234/C235/C75/C107 六卡行注记 G/DONE，对应物在 HEAD 缺位（挂接真实、终态注记超前）。

**项6 消费链最小实测——verdict：通过。**
`git show HEAD:<file> | python -c "ast.parse(...)"` 纯读（零写盘）：`grid_stats_engine.py` **AST-OK 21732 bytes**、`lead_lag_validator.py` **AST-OK 7280 bytes**、`process_reaper.py` **AST-OK 53985 bytes**（Python 3.12.8）。HEAD 字节可载入。

## 证据块

**E1（项1/2 袋定谳）** `cat .runtime/commit_queue/dead/q-20261007-st-mastertc-recover-0005.json` → `"dead_at": "2026-10-07T19:13:47+08:00"`，dead_reason="CREATE-GUARD 阻断: 新建 src/zephyr .py 未申报挂图面（MAP-MOUNTS 必填）： event_axis.py, resonance_pair.py, swing_sequence.py"，files 含三模块+三测试+capability 册（blob_sha256 在档）；同法 recover-0003 → `"dead_at": "2026-10-07T19:20:40+08:00"`，dead_reason="CREATE-GUARD 阻断： 无 creation_token…tech_factor_pipeline.py"。`ls done|dead` → done={mini-0001, mini-0004, recover-0001(=abed5f7a1f 原袋)}，dead={mini-0002, mini-0003, recover-0002, recover-0003, recover-0004, recover-0005, l6-0001, l6-0002, l6-0004}。
**E2（项1 HEAD 零字节）** `git ls-tree -r HEAD --name-only | grep -iE "event_axis|swing_sequence|resonance_pair|tech_factor"` → 仅命中 grid_stats/lead_lag/fill_writer 文档，四模块零命中；`git status --short` → `A event_axis.py`、`?? resonance_pair.py / swing_sequence.py / tech_factor_pipeline.py / tests/signal_ashare/ / tests/factor/test_tech_factor_pipeline.py`（工作区存活，属在途面不计被审账）。
**E3（P1-1 悬空登记）** `git grep -n "module_path:" HEAD -- docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml | grep -E "tech_factor|event_axis|swing|resonance"` → L67723/L67731/L67739/L67747 四条，对应模块文件均不在 HEAD 树。
**E4（项3 字节+消费）** `git show HEAD:scripts/backtest/grid_stats_engine.py | head -30` → `[INVARIANTS] ★READY_NOT_FIRED…正式跑全推迟到波 12（G-D.4 Owner 门位）`；`git grep -n "grid_stats_engine" HEAD -- config/` → 仅 `chart_resonance_prereg.yaml` L10/38/41/45/90；三图 `git grep -E "grid_stats|lead_lag" HEAD -- config/strategy_production_map.yaml config/trading_decision_map.yaml config/data_supply_chain_map.yaml` → 零输出；`10_wave_plan.md` L190 G-D 行 ★READY_NOT_FIRED 在 HEAD。
**E5（项4 reaper）** `git show a6ae287dab --stat` → `src/zephyr/trading/process_reaper.py | 42 ±++, message 含 [GW:st-mastertc-mini:q-20261007-st-mastertc-mini-0004]`；`git grep -n "_compute_live_report" HEAD -- src/zephyr/trading/process_reaper.py` → L1332 定义+L1348 调用+L1344 注记"（C324，2026-10-07）"。运行时证据：审查机构实测 `python -m zephyr.trading.process_reaper --status` = `source=live scan_mode=live_dryrun killed=0`。
**E6（项4 fill writer 证伪）** `git grep -n "_PaperFillJsonlWriter" HEAD` → 仅 `HEAD:...L7_backtest/00_workbook.md:79`（自述）；`git ls-tree HEAD -- tests/ex_core/test_fill_jsonl_single_writer.py tests/backtest/test_lookahead_injection_red_ruler.py` → 零输出。`dead/...mini-0003.json` → dead_reason=GATE-PRECOMMIT-RUN（gate-naming）；`...mini-0002.json` → ALGO-FLOW-LINK"external 锚指向不存在的 yaml: docs/03_modules/_domain_backtest/algo_flow/grid_stats_engine.yaml"。
**E7（项5 读数）** 命令与读数：`git grep -c "环节" HEAD -- docs/_working/fullflow_mining/00_orchestration.md` =9；`…night_sweep_20260929/00_skeleton_nightsweep.md` =10；`…fullconnect_campaign/00_workorders.md` =1；`git show HEAD:<nightsweep> | grep -c '| 已通 |'` =64（开口=57、等Owner=11 同法）；`grep -cE '^\| F[0-9]{3} '` =132；总表 `grep -cE '^\| C[0-9X]'` =119（+X01=120）。
**E8（项6）** 见项6 读数（AST-OK ×3，Python 3.12.8）。
**E9（附验 C216）** `git grep -n "haircut_sharpe_harvey_liu" HEAD -- src/` → `deflated_sharpe_calculator.py` L436 定义在位——C216（02fc4d72a4）HEAD 真在位。

## 小结（六问）

1. **真完成？** 六项中仅 3 件真完成：C324 reaper 现算化（a6ae287dab，含运行时实测）、C238/C236 G-D 双引擎+四单测（abed5f7a1f，AST 可载）、C237 prereg 挂点（90d8e3b33c）；C216 剪发夏普 HEAD 在位（附验）。信号三模块/tech_factor/fill writer/C233 四件=假完成。
2. **真打通？** 生产消费链整体**零打通**：双引擎按 ★READY_NOT_FIRED 规格合法地"未点火"（波 12 Owner 门），信号段与实盘 fill 写者段因死袋**不存在于 HEAD**，谈不上打通。
3. **过渡？** 双引擎/lead_lag 为**明示观察轨**（头部声明+真源行+prereg 三面一致，合规过渡）；无未声明过渡件。
4. **不必要？** 车道 A 范围未发现违内收四判据产出（DSR/FDR 均委托既有真源，零第二实现）。
5. **遗漏？** 120 卡挂接对今晚新模块**无遗漏**；遗漏形态不存在，但存在更糟的**反向失真**：六卡注记 DONE 而载体是死袋。
6. **待证清单：** (a) recover-0002/0004 内容物与归属（车道 C 范围）；(b) 死信 blob sha256 ↔ 工作区文件一致性（车道 C"逐文件核实"范围）；(c) 各"16 测绿/8 测绿/72 绿"自述未复跑（纪律：默认不跑 pytest）；(d) C107 测试数口径矛盾（工作簿 8 测 vs mini-0003 袋 16 测）待清偿时并案。

**P1 建议：**
- HEAD `module_translation_registry.yaml` L67723/67731/67739/67747 四条悬空 module_path（登记-本体倒挂）：随死袋清偿自然消除；若撤卡则须登记行回退，否则任何 loader 全量扫描/TRANSLATION-COVERAGE 复核将命中断链。
- 交付报告 C232/C234/C235/C75/C107/C233 六卡改判"施工完成/落地失败（死袋在案，qid 见 E1）"，与环节总表 G 注记同步降级，防晨会按 126 卡总表误读为可消费资产。
- 四死袋清偿处方已由门禁给出（MAP-MOUNTS 补 map_mounts 或 no_mount_reason；CREATE-GUARD 补 token；mini-0002 放弃恢复锚或先建镜像 yaml；mini-0003 修 gate-naming 命名违规），建议移交高模型维护班单窗批量清偿。

**P2 建议：** 环节总表"132 表 L22 起"指针修为 L16；交付报告 §①"袋位终扫 done=31/dead=45/无在途"系报告时点读数，其后 recover/mini 班新增 6 死袋，引用时须带时点戳；C107 测试数口径统一（8 vs 16）。
