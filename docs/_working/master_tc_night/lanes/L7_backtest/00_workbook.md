---
ttl: task_bound
session: st-mastertc-l7
---

# L7 回测/考试车道作业簿（st-mastertc-l7，总包 st-mastertc-20261006）

> 冷启动合规：PATH=Python312（3.12.8 实测）✔；reaper 在岗（last_run 正常，dry_run=False）✔；
> session 注册+worktree（.aidrafts/st-mastertc-l7）+心跳 daemon ✔；
> capability_lookup 反查留审计 ✔；reaper keep 追加 st-mastertc-l7/r01_grid100bp_full_v1 ✔。

## 卡台账（六向台账+自审闸+施工记录）

### C216 16 例测试红（haircut_sharpe_harvey_liu / T0_BATCH_KIND / closed_book mock）
- ①处方：主卡=实现 haircut_sharpe_harvey_liu（案卷 §四口径）+T0_BATCH_KIND 常量补齐+closed_book mock 修，同批落测试；先跑 pytest 确认真红。
- ②HEAD 现状实证：`grep -rn haircut_sharpe` 全仓零命中；`git log --all -S T0_BATCH_KIND` 唯一史证=30094feeedf 卡面文字（源码全史零落地，st-sK-orphanarch 死袋 q-20261004 判"未落地特性规格件"已退役）；tests/backtest 旧测试件已被 tests 重组迁空——**红前提过时**（原 16 例不存在于 HEAD，真红无法复现）。
- ③上游依赖：deflated_sharpe_calculator（DSR SSOT）、n_trial_ledger、closed_book_gate（已建）。
- ④下游消费者：backtest/core/metrics 等三处 DSR 消费方（签名纯增不破坏）；fexam/考试判据（haircut 可作幅度面尺）。
- ⑤冲突面：test_closed_book_tick_gate.py 处于他会话 staged 删除+盘面 untracked 态（st-cure-p10 tests 重组在飞）——claim 后按盘面实态改（网关 own-diff 保护）；期间共享 index 有他会话 2700+ 件在飞 staged，全部提交走 commit_queue 序列化器（干净暂存区=结构免疫连坐）。
- ⑥残余与移交：无。
- **自审闸：GREEN（挖干后按主卡处方补齐落地）**。
- **施工记录**：commit `02fc4d72a48`（q-20261007-st-mastertc-l7-0001，7 文件零连坐）。三件套：
  1. haircut_sharpe_harvey_liu 落 src/zephyr/simulation/deflated_sharpe_calculator.py（bonferroni 闭式+HLZ2016 t>3.0 双口径；t_mult>t_single 全剪封顶不外推负 SR；N=1 零剪发精确特判；C251 口径入 docstring）+HLZ_MULTIPLE_TESTING_T_THRESHOLD+HaircutSharpeResult+7 测试；
  2. T0_BATCH_KIND+sync_t0_manifest_counts 落 n_trial_ledger（幂等+断点续跑单调前进+缺读数宁少计留痕）+T0 族 5 测试（**顺带清偿 st-ffchief 死袋 q-20261001-0019/0032/0073/0085 四轮"test_n_trial_ledger_t0_family 堵死跳过=缺 T0 发现面"**）；
  3. closed_book"mock 修"=真接线：ch_tick_replay/ChTickProvider 补 exam_ticket/audit_path 形参，enforce_closed_book_read 查库前拦截（SQL 次数恒 0），6 个 strict-xfail 摘帽转真绿 11/11（xfail reason 自述"转XPASS=接线落地须改判"，本批即改判）。
  验证=三测试册 72/72 绿+ruff 过。

### C237 G-D.1 chart_resonance_prereg.yaml
- ①处方：新建预注册族（config/ 下，token 先行），冻结后 diff==0，判据真源=10_wave_plan。
- ②HEAD 现状：config/ 无 resonance 族册；search_space_prereg.yaml=E7 模板（在飞他会话 MM，本卡只读未触）。
- ③上游：E7 模板结构；condition_package F4 三态选族口径；10_wave_plan 10.G-D 行。
- ④下游：G-D.2 引擎（同批）、波 12 正式跑、G-D.4 点火卡。
- ⑤冲突面：search_space_prereg.yaml 他会话在飞=本册独立新文件规避。
- ⑥残余：candlestick 外三族规模 pending_family_registry（点火前族登记=放行前置件，已在册内申报）。
- **自审闸：GREEN**。
- **施工记录**：config/chart_resonance_prereg.yaml 冻结（frozen_at=2026-10-07T05:30+08:00）；diff==0 自验两次读相等 PASS（sha256=b341dca0ac360cbc）；纪律首行=图形信号只作条件轴禁独立信号（Marshall 2006）；READY_NOT_FIRED 禁点火。随 C238 批落 HEAD。

### C238 G-D.2 逐格统计引擎 + C239 G-D.3 多重检验/滚动重考 + C251 案卷采纳
- ①处方：ext_01 G-D.2/G-D.3 规格（vectorbt 口径自实现，勿引新重依赖）；StepM/SPA（White RC 简版）+分半窗排程（事件触发非 cron）；判据回填 17_quantified_acceptance.md（§十一指针已存在只补引擎行）；C251=DSR 有效试验数与滚动重考口径入 docstring+17 册行。
- ②HEAD 现状：无逐格引擎；可复用件实测=e2_stationary_bootstrap（Politis-Romano）、n_trial_ledger.compute_effective_rank（熵广度）、deflated_sharpe_from_moments（DSR SSOT）、bhy_fdr。
- ③上游：10_wave_plan 10.G-D（★READY_NOT_FIRED 判据唯一真源）；⚑-2 B 案 A 股夏普口径四条（flag2_declaration_b.md：244 基准+ddof=0+LB 显著才 Lo 修正）。
- ④下游：G-D.4 点火卡（Owner）、波 12 正式跑、exam_cost_gate 邻接。
- ⑤冲突面：无（全新文件；DSR/夏普口径零克隆全委托）。
- ⑥残余：正式跑=波 12（禁点火已双保险：prereg status 位+引擎无 __main__ 红证测试）。
- **自审闸：GREEN（READY_NOT_FIRED 维持，零点火）**。
- **施工记录**：scripts/backtest/grid_stats_engine.py（四件套：样本/胜率+Lo2002 夏普[NW1994 自动截断]+c* 二分单调+DSR[N_eff]；spa_reality_check+stepm+half_split_reexam；INSUFFICIENT-N 30 地板；C_STAR_NON_MONOTONIC 单列）+16 单测（合成数据）绿+SPA/StepM 强格显著噪声格不显著红证；17 册 §十一 G-D 引擎落地行回填（safe_write CAS）。克隆闸自查：Lo 因子/LB χ² sf/Fisher z 为仓内无第二实现的最小自实现（零新依赖），DSR/FDR/bootstrap 全委托既有件。

### C236 G-C.4 lead-lag 统计验证器
- ①处方：观察轨最小实现（scripts/backtest/lead_lag_validator.py+单测），不接生产。
- ②HEAD 现状：无 lead-lag 验证件；bhy_fdr（全仓唯一 FDR 真源）在。
- ③上游：ext_01 G-C.4 规格；Curme 2015（FDR lead-lag 网络）/Fang 2025（案卷 §3.1/3.3）。
- ④下游：G-C 主体（观察轨 P2 报告消费）；负结果台账。
- ⑤冲突面：无。
- ⑥残余：正式接产=P2 排产（Owner 门位）。
- **自审闸：GREEN（观察轨零生产接线：无 __main__ 红证测试在场）**。
- **施工记录**：lead_lag_validator.py（滞后相关矩阵+BHY FDR 全族校正[复用 bhy_fdr 零克隆]+分窗稳定性；负结果原样保留）+6 单测绿（已知滞后对 best_lag=2 显著/纯噪声对保留不假阳性）。

### C233 G-C.1 前视注入红证尺（14 位）
- ①处方：chart_condition_package.py 已有 merge_asof backward PIT；补 14 处前视注入位红证尺测试（列清单→逐位反证），落 tests/backtest/。
- ②HEAD 现状：清单元源=wave10_base_audit_and_ga_wiring.md §3/§4——G-B.1×3+G-B.2×3+G-B.3×2+L1-L6=14 位（与卡面"14 处"恰合）。
- ③上游：六生产面=align_backward/trendline_sr_detector/false_breakout_trap_detector/candlestick_scanner/build_chart_daily_state/cell_win_rate。
- ④下游：G-B/G-C 未实现件的规格尺（尺先立于件）。
- ⑤冲突面：无（新测试文件）。
- ⑥残余：G-B.2-B/C 契约尺待实现面落地后转行为测试。
- **自审闸：GREEN**。
- **施工记录**：tests/backtest/test_lookahead_injection_red_ruler.py 16 测试绿（14 位全覆盖；阳性对照 leaky 参考实现必被尺逮住=尺非假绿；L6 锁 fwd_ret join 面 shift(1) 陷阱）。

### C251 dossier_academic 采纳
- **自审闸：GREEN（随 C238 批落地）**。施工记录：案卷 §四三口径（DSR 有效试验数=N_eff 熵广度折算禁 Bonferroni 除总格数；全试验披露入 N 账本；滚动重考分半窗）写进 grid_stats_engine docstring+17 册引擎行+haircut docstring。

### C107 Fill 写者 BF-5
- ①处方：wiring_A_fill_writer.md 处方实现单一写者（sim 域 env='sim' 硬断言），落代码+单测。
- ②HEAD 现状：_wire_position_book_feed 在但只接 tracker.apply_fill（写者腿缺失）；FillHandler.process_fill/fills_dir 落盘在 src；处方三测试文件均未落。
- ③上游：AsyncFillDispatcher、FillHandler、AppendOnlyDedupSet、OrderManager._on_fill（二次计数病灶）。
- ④下游：F57 对账读口（query_fills_by_date）、run_post_settlement（只读不写=非写者）。
- ⑤冲突面：scripts/start_paper_session.py 无他队锁。
- ⑥残余：生产 data/fills 首件真文件=下次模拟盘装配时自然产生（本卡零生产写入）。
- **自审闸：GREEN**。
- **施工记录**：_PaperFillJsonlWriter 落 start_paper_session.py（快照副本防二次计数/broker 键改 fill 侧键防静默丢/去重集持久分文件/env='sim' 硬断言）+接线消费线程；tests/ex_core/test_fill_jsonl_single_writer.py 8 测试绿（五钉+动态尺+静态尺 AST 全仓写者集合=={start_paper_session.py}）；既有装配回归 47/47 绿。

### C199 材料线收尾
- **自审闸：GREEN（挖干即收口，零缺件零施工）**。
- 施工记录：hypothesis_precheck.py+hypothesis_translator.py 在 HEAD（骨架台账已标 GREEN）；dead 袋反查（1598 袋抽样，"材料线"命中 15 袋）：q-20260925-st-cmd 三袋=战役文档+材料线报告（material_precapacity_report.md+sample20_stats.yaml 已在两 campaign 目录 tracked）；q-20261001-ffchief t0 族四袋的"test_n_trial_ledger_t0_family 堵死"堵点**已由本车道 C216 批清偿**（T0 发现面落地）；R48 台账=cmd ledger commit 467380883f7 在 HEAD。docs/材料类缺件=0。

### C33 139 新题首考 / C34 旧 283 复考
- ②HEAD 现状：exam_loop 全件在 HEAD（状态机+writeback PG 事务面+reexam_scheduler）；但**考题执行 runner CLI 不在 HEAD**（exam_loop=库件非跑批入口；139/283 题面在 PG meta_question 族）。
- ③环境实证：Ollama 本地（127.0.0.1:11434）**拒连**（WinError 10061，qwen3:8b 离线）；DEEPSEEK_API_KEY 在 env 但 meta_question 考试的 LLM 授权面（本地 qwen vs 云 API）无在册裁定，禁自择模型放宽判据。
- **自审闸：WAIT（环境不可跑，按主卡处方登记+试点命令写死）**。
- **WAIT 移交（试点命令，环境复活后按序执行）**：
  1. C33 5 题试点（禁放宽判据；writeback.py 唯一回填口）：
     `python -m zephyr.governance.meta_question.exam_loop.exam_plan --limit 5 --dry-run`（先核对题面计划）
     实跑经 ExamLoopWriteback.writeback（q_id 白名单显式传入，禁全表盲改）；OOM/LLM 选型须 Owner 补裁定。
  2. C34 insufficient 集抽 5：同上，`--qids` 显式列 insufficient 集 5 题；两卡同袋排产（低峰窗）。
  3. 复活条件：Ollama qwen3:8b 上线（hypothesis_precheck 同款通道）或 Owner 裁定云 API 授权面。

### C70 T2 900 格终审
- ②HEAD 现状实证：`t1_t2_handover.py --dry-run` → **STATUS=ALREADY_CLAIMED**；claim=grid_20260926-024947/t2_handover_claim.yaml（launched=true，2026-10-05 21:55，LANE-AUTO watchdog tick）；T2 跑=grid_20261005-215457 **已完赛**（summary.json evaluated=24/24，eval_dead=0，manifest+net_returns+negatives 四件齐）；双 pid（19360/4264）已自然退出。
- **自审闸：WAIT（登记诊断结论，禁重启）**。
- 诊断结论：裁定#446 机件 batch_b_subspace（24 格）**已于 10-05 完赛且产物齐全**——无可续跑面（断点续跑前提=有半程态，实际已完赛）；900 格全量 T2 终审属下波点火位（10.G-D READY_NOT_FIRED 同纪律，Owner 门位），非本夜可发车面。

### C205 做T 271 批
- ②HEAD 现状实证：manifest r01_grid100bp_full_v1（created_batch_run=271，batches_done=53/271）；末件时间戳 **09-26 06:04**；进程表无 t0 活体（四命中皆本查证 shell 假阳性）；CH 可达（SELECT 1 OK）；停跑原因=.runtime/logs 无该跑日志（孤儿前台跑，10-06 深夜总包 worker 换血期亡——与 04:1x 心跳 daemon 被误伤同窗）。
- **自审闸：GREEN（断点续跑入口存在且安全：--resume 逐批 manifest 锚+切分面漂移闸）**。
- **施工记录**：reaper keep 登记（r01_grid100bp_full_v1 追加行）；续跑已启动并监控首轮输出——**批 53 完赛实证**（733s，5 周期各 11.4k pairs，低优先档 below_normal 生效，checkpoint 逐批落盘）；余 218 批预计 ~43h 自续（长跑在 keep 名册，随会话心跳在岗）。

### C288 C2 晋级率（排期销账卡）
- **自审闸：WAIT（远期死线 2027-03，登记排期销账卡不动代码）**。
- 销账卡：**C288-C2-(promotion-rate)-due-2027-03**——C2 晋级率统计依赖 2026-10~2027-02 五个月滚动窗的 C2 考试实绩积累；到期动作=统计窗聚合+晋级率报告（消费 exam 成绩台账），前置=波 12 考试制点火；责任面=L7 车道继任/总排程台账。本夜零代码。

### C452 quant_methodology 07/08/12 号文
- ②HEAD 现状实证：现库 11 件（01-06+三附录+README，16d58a652d9 落地）；07/08/12 内容**三反查全零**（git log --all -S、dead 袋 1598、blobs 23367）。
- **自审闸：GREEN（按处方走占位骨架支线）**。
- 施工记录：三本占位骨架落 docs/_working/quant_methodology/（断号防御；溯源状态如实申报=从未被写出；主题命名/撤号=Owner 门位）+README 溯源行（safe_write CAS）。随 C107 批落 HEAD。

## OPEN_QUESTIONS

1. **C33/C34 考试 LLM 授权面**：meta_question 考试（139/283 题）用本地 qwen3:8b 还是云 API（DEEPSEEK_API_KEY 在 env）？无在册裁定，本车道不自择（禁放宽判据）——L10 裁定台/Owner 门位。
2. **C452 三号文主题**：quant_methodology 07/08/12 预定主题全史无记录，占位骨架待 Owner 补命名或宣布撤号。
3. **capability_canonical_file_registry 并发排水**：本车道 register_asset 于 05:00 写入的 2 条 token 行被他会话在飞重写 stomP（05:4x 复查已蒸发，重插后解析器可见）；热册 stomP 机制（在飞会话持陈旧整册重写）对所有并发写者是公共风险面，建议总包/L3 深挖（写侧 CAS 已有，读-改-写窗口在工具层）。

## CONFLICT_LEDGER

| 文件 | 态 | 处置 |
|---|---|---|
| config/search_space_prereg.yaml | 他会话 MM 在飞 | 本车道零触碰（C237 独立新文件规避） |
| tests/research/backtest/test_closed_book_tick_gate.py | 他会话 staged 删除+盘面 untracked（tests 重组） | claim 后按盘面实态修，网关 own-diff 保护，commit 02fc4d72a48 零连坐实证 |
| docs/.../capability_canonical_file_registry.yaml | 他会话 staged 净删面+并发 stomP | 本袋不带热册（防吸收他会话净删面），token 行盘面重插+解析器可见 |
| tests/backtest/fexam/test_bootstrap_gpu_parity.py | 他会话 staged add | 未列入本车道任何袋 |

## DONE_SUMMARY（终态 2026-10-07 07:5x）

- **已落 HEAD**：C216（`02fc4d72a48`，7 文件零连坐实证）；registry token 先行袋 `b0fe4b5940`（六卡 token/翻译行进 HEAD，历经并发翻面仍存活）。
- **内容袋死信待维护班**（袋快照=零丢失承诺，内容完好可整袋取回）：q-0005/0007/0009=G-D 五卡（C237/C238/C239/C251/C236/C233，7 文件）；q-0004=C107/C452+本册（6+1 文件）。死因三型均已根治到车道边界：①PERM-TRIGGER（`_chi2_sf while True` 有界化，修复测绿）②R5-DIGIT-SUFFIX（`master_tc_night` 目录名=总包 §三.3 指定，确定性死路非车道可解）③CREATE-GUARD 落地面（worktree 基册陈旧+注册表并发 stomper 翻面，`--base-head` 钉基未生效=战役级，同签名死信全仓 551+）。移交=L3 提交链/维护班/总包（`commit_queue status --session st-mastertc-l7` 即死信名册）。
- **WAIT 登记**：C70（T2 batch_b_subspace 已完赛 24/24 产物齐，900 格全量属下波点火位 Owner 门）、C33/C34（Ollama 拒连+考试 LLM 授权面无裁定，试点命令已写死本册 §C33）、C288（2027-03 销账卡在本册 §C288）。
- **长跑在岗**：C205 做T 271 批断点续跑实证推进（53→59+/271，manifest 逐批锚点，keep 在册，below_normal 档）。
- **测试读数**：C216 72/72；G-D 引擎 16/16；lead-lag 6/6；红证尺 16/16；C107 8/8+回归 47/47；W3 循环检查 158/158。
- **零放宽判据/零点火 READY_NOT_FIRED/零生产数据写入/零裸 commit**。

## 队列战役实录（共享热册并发 stomper）

capability_canonical_file_registry 在飞会话"基于 HEAD 重建"式落地（st-t3series 586203aa0a 等）周期性抹除并发插入的 token 行：本车道历经 q-0002 先行落地→被抹→重插→内容袋四投方过（M2.1 预检读 HEAD 册口径=袋不带 registry 时；带 registry 时读盘面=stomp 战场）。处方沉淀：**registry-only 先行袋（带 allow-mass-deletion 留痕）+内容袋不带 registry** 是并发夜的稳态路径。R5-DIGIT-SUFFIX 对 master_tc_night 目录的拦截与本车道无关（总包指定的车道目录名），作业簿随 q-0007 以"新文件在数字后缀目录"过闸与否如实留痕。
