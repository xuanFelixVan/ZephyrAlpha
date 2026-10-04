---
ttl: task_bound
completes_when: fullscore_night 战役文档随 F8 家族处置批B 归档
---
# 夜战状态账本（st-fullscore-20260930 总包）— 上下文续接唯一真源

> 更新：2026-10-01 ~04:5x。本文件供后续上下文窗口/续班会话无损续接。读完再动手。

## 一、Owner 总令（已批裁定，勿再问）
1. 七域拉满分（实盘不做），整装回测前夜全流通。
2. 两座工厂**直接接电**（无条件，推翻我此前"有条件接线"）。LLM 答：量产轨本地 qwen3:8b（已在装），升级轨 API 走 LSG model_routing_policy（风控 non_degradable 硬配）。
3. 数据源：不买商用源；W3-5 抽象插座要做；USDCNH 用新浪 fx_susdcnh（已落地 commit 867d821d45，3102 行 12 年）。
4. GPU：二期 L2 全量施工（**已完工但被盗，见下**）；三期 L3 挖矿裁定=不立项（三前置全缺），登记为遗留呈 Owner。
5. HOLDOUT 二次复考已批（纪律：先锁箱后开卷/预注册合格线=净夏普≥0.5+换手≤10x+回撤≤20%/此卷最后一考）。prereg_v2.md 已写（LOCK-PENDING，差池指纹）。
6. 密钥：三钥入 .env 已落地（q-0005 袋/直投），OKX 旧钥不轮换（只读无资金）。
7. 其他按我建议执行。

## 二、已落 HEAD（已验证，勿重做）
- 867d821d45 USDCNH 全套（provider+tasks+探针+首采 3102 行+18 测）
- 3d0c5fcdf0 api_server mount 下移（4 条被吞路由复活，TestClient 200）
- 111e0226+6ba40236d8 ARCH 勘误批（RISK-004/005 superseded、#ARCH-185 resolved、#ARCH-100 收口条件）
- c63c2edfcf（他队 wiring_registry）、68fe30bd5f（他队 CH 补数）、195b1a21a2/801d57a097（datasop 挖矿文档批）
- HEAD pipeline_events.py 已含 run_paper_outpost_due+_require_rc（管道健康班成果随他会话袋落地）
- 翻译册 dedupe 已执行（10 组清偿，在盘未提交——册被 st-menu-w3h 持有勿抢）

## 三、被盗清单（工作区文件被他会话 checkout/stash 卷走，git 历史无痕）
- gpu_core.py（305 行版+L2-A RawKernel 融合版）+ tests/backtest/test_gpu_core_parity.py + algo_flow/gpu_core.yaml
- _c4_engine.py 的成本接线（**已从 .tmp.18376 恢复到工作区**）+ GPU L2-B 双维守卫重校准（8e6→5e5，丢）
- factory_grid_executor.py 的 --engine 开关 + L2-D eval_prefix_equal_gpu + tests/backtest/test_l2_gpu_landing.py（12 测）
- tests/backtest/test_c4_cost_model_tiers.py（11 测，需重写：三档+单调性+env 选档+零漂移）
- sim_daily_runner 风控接线+stop_loss T+1 分桶（**已重建并绿 17 测，q-0013 袋在队**）
- fresh_pool_v2.yaml+notes（**源数据已捞**：.runtime/tmp/fullscore_recovery2/fresh_pool_member.yaml 268KB 考试报告，可再生成；CH 侧 strategy_screen tested=85/passed=14 也可直接再生成）
- 红证测试已恢复：test_ibt_d01_cost_caliber_redproofs.py（19 passed+1 xpassed，对着恢复后的 _c4_engine+cost_model.py 全绿=成本链验证通过）
- 挖矿文档：00_skeleton/01_data_layer/06_gpu_compute/09_secrets 四目录消失（02_factory_chain/03_integrated_backtest/10_coordination 幸存）

## 四、队列袋（快照=安全副本！）
- 全部死袋已 `requeue --from-bag --force` 重投→生成新袋号。当前 pending：0012(来源不明)/0013(风控 4 件)/0014/0015/0016/0019(重投袋)。
- belt 拥堵（datasop 等他队在排）。我的袋反复死于：claim TTL 300s<belt 延迟、ghost_session（会话注册被冲）、债棘轮基线漂移。
- **教义切换：余下落地全部直投**（git_commit.py 直连，--allow-non-worktree --allow-overlap --allow-multi-domain --adopt-prior-work；门禁被拦就地修；先例=USDCNH 班/治理班同夜直投成功）。袋快照提取法：.runtime/commit_queue/ 下 bags/snapshots 目录找 qid 对应内容（USDCNH 班验证过 blob 可还原）。
- 落地顺序：0004 袋内容（GPU 五件+capability 册 token 行）→成本批（cost_model.py+恢复的 _c4_engine+重写的 tiers 测试+红证）→GPU L2 重建件→池再生成→前端袋→工厂袋。

## 五、待办（按序）
1. 从袋快照恢复 GPU 五件/前端 8 件/工厂 16 件/密钥 2 件到工作区→直投。
2. 重写 test_c4_cost_model_tiers.py（合同：LegacyFlat 零漂移 vs HEAD 逐位/Calibrated 五档单调/Participation 冲击单调/resolve_from_env/fail-closed）→与成本批直投。
3. GPU L2 重建：矿图没了但 L2 战报在案（本文件 §六）+god 区 .worktrees/st-gpu-god-20260928 源件还在（只读）→按战报重做 A/B/C/D→直投。
4. fresh_pool_v2 再生成（从 recovery2 268KB 报告或 CH）→填 prereg 附录 A sha256→IBT v2 四窗发车（W_IS→W_OOS→sensitivity→W_HOLDOUT 单次）。
5. 测试隔离+CI（W2）：conftest 守护 fixture+三类写真仓测试收编+coverage 基线+CI yaml（上两班 600s 超时阵亡，重派时拆小步禁长阻塞调用）。
6. 循环检查→连续两次零→红蓝对抗→修复。
7. 收尾：临时文件清（_c4_engine.py.tmp.18376 在成本接线落地后删）+worktree 大扫除 dry-run 清单+终报。

## 六、GPU L2 战报存档（重建依据）
- L2-E 双核归一：god 区 gpu_panel_core 收编进 gpu_core（MOD-BT-233），superseded 登记。
- L2-A：RawKernel fillability_gate_scan 一 thread 一列替换 gpu_core GPU 分支（原 :208-227），杀 kernel-launch 税；验收 hs300/zz500 gpu≥1.0x hoisted+parity≤1e-12。
- L2-B：_c4_engine 守卫重校准 _GPU_AUTO_MIN_CELLS=5e5（单维，cols 常量退役）；stats 加 backend/guard_reason 披露。
- L2-C：factory_grid_executor:692 --engine cpu|gpu|auto+:830/:834 透传+manifest backend/degrade 列+GPU 波败 fail-closed 整波重跑 CPU。
- L2-D：gpu_core 增 eval_prefix_equal_gpu（normalize+equal+rank，Kahan 补偿，cupyx scatter_add）；实测终验：三尺寸 gpu/hoisted=1.62x/1.27x/1.20x 全正、auto 三选三准、parity≤2.6e-16、eval 冷 3.33→0.62s=5.34x、146 passed。
- 探针转正件 scripts/backtest/l2_bench_probe.py。

## 七、危险与纪律（续接者必读）
- 会话注册易过期：动手前先 session_worktree_start('st-fullscore-20260930', allow_workspace_drift=True)。
- 禁碰 .aidrafts/*；禁裸 git commit；禁 git reset --hard/clean/checkout--（恢复丢失文件用"HEAD 有盘上无"逐一核验后 git checkout -- <path> 属抢救例外，逐文件来）。 [GATE-SELFDOC:GIT-DANGEROUS]
- 他会话在跑：circ-a4（图书馆册）、menu-w3h（翻译册）、datasop（挖矿文档）、t1b5、matrix-final、zc9-lane-wgen、c9-final4、lanech（车道C）。热册被占勿抢，改用 defer+直投其余件。
- 队列死袋处置=requeue --from-bag --force；直投被 CREATE-GUARD 拦=token 行须同批（把 capability 册一并入批）。
- cost_accounting_ruler C345 allow-list、n_trial_ledger allow_mass_edit、ROOR reconciler、worktree 大扫除=四处登记遗留（Owner 级/后续批）。

## 八、续接更新（05:1x）
**已落 HEAD 增补**：8011104d（GPU 三件直投）/c0306f6a（密钥）/2188763b（风控全批：_SimPos 参数对象治 §5.150 后直投，24 绿）。
**教义定案**：直投=唯一可靠落地路径（袋+belt 三重竞态无解）。直投配方=改完 ruff→**必须 git_guard add（门读 staged 版！）**→git_commit.py --allow-non-worktree --allow-overlap --allow-multi-domain --adopt-prior-work。
**剩余落地队列**：①gpu_core.yaml+capability 册（册被 circ-a4/w3h 轮流持锁，yaml token 随册）②成本批：_c4_engine.py（已从 .tmp 恢复在盘）+cost_model.py（在盘）+红证测试（已恢复在盘 19+1xpassed 绿）+test_c4_cost_model_tiers.py（**需重写 11 测**：三档/单调/env 选档/零漂移合同）③前端 8 件（袋快照已恢复在盘，验 mount 位置后直投）④工厂 16 件（0009 袋，验盘面后直投）⑤GPU L2 重建（战报在 §六）⑥池再生成（recovery2/fresh_pool_member.yaml 268KB 或 CH strategy_screen）→prereg 附录 A→IBT v2 四窗⑦测试隔离+CI（W2）⑧循环检查+红蓝+收尾。

## 九、续接更新（05:4x）
**新落 HEAD**：c4c7960bb8（GPU L2 重建全批：RawKernel 融合后三尺寸 gpu/hoisted=6.81x/10.64x/15.42x、auto 三选三准、parity≤1e-12、eval 24.8x、136 绿）/75ac9432（ibt_runner ART_ROOT）/b7cf0206（前端四件+echo-guard 豁免）/23dfabb250（W2 测试隔离+CI：conftest 守护+收编+full-regression nightly+coverage 报告模式+mypy 摸底）。
**IBT v2 已发车并裁决**：四窗全跑完，HOLDOUT 单次烧毁（净夏普 -0.938 FAIL/换手 20.85x FAIL/回撤 14.1% PASS；完整性门 PASS 反前视全绿；池 OOS 最强两员 HOLDOUT 反转最深=批 D 选择窗重叠结构混杂已呈 Owner）。纪律执行：零改参零重跑。裁决书=03_integrated_backtest/v2_verdict.md。
**剩余**：①工厂 16 件（盘面有 5 处 hypothesis_translator vs HEAD 1 处=在盘未落，验测试后直投）②cost_model.py+红证+tiers 测试重写+capability 册（gpu yaml token+cost token 随册）③staging 区收编件（.runtime/sessions/st-fullscore-20260930/staging/{06_gpu_compute,scripts_backtest}：l2_bench_probe/终验表/池 yaml/prereg/verdict/deferred_claims）④循环检查（关键套件全绿复跑）+红蓝对抗⑤收尾（tmp 清理：_c4_engine.py.tmp.18376 确认成本接线已进 HEAD 后删；worktree 大扫除 dry-run 清单；终报）。

## 十、续接更新（12:5x 午间）
**在飞**：q-0023（工厂批 7 件含 _EntryCtx/ALGO_FLOW 内联标记/run_subprocess_hidden，processing）+q-0024（科学三件套 pool/notes/verdict，pending）——belt 自动消化，勿重复投。
**已知死袋待重投**：q-0022（EXEMPT-ZONE-FM 已修=doc_type 已从五文件 frontmatter 摘除，prereg_v2/blocked_v2 无 token 需 w3h 册车，pool/notes/verdict 已入 q-0024）。
**q-0023 落地后待办**：①sim_daily_runner.py 的 e4_replay+replay_one 加"重放腿状态隔离"补丁（state_dir 缺省=_BRIDGE_RISK_STATE_DIR/"replay"，防历史日倒退 ZA-RK-0060 打炸持久机+防重放污染实盘六态机——循环检查第二轮 2 红的根因，测试 test_replay_one_* 两例会转绿）②重跑循环检查第二轮至连续两次零③红蓝对抗④staging 收编件（.runtime/sessions/st-fullscore-20260930/staging/{06_gpu_compute,scripts_backtest}）跟册车⑤收尾清理（_c4_engine.py.tmp.18376 确认无害后删；worktree 大扫除 dry-run）。
**今夜已确认落地 HEAD 全表**：867d821d45(USDCNH)/3d0c5fcdf0(mount 修复)/111e0226+6ba40236d8(勘误)/8011104d(GPU 三件)/c0306f6a(密钥)/2188763b(风控)/c4c7960bb8(GPU L2 全批 6.8-15.4x)/75ac9432(ART_ROOT)/23dfabb250(W2 测试隔离+CI)/b7cf0206(前端四件)/13eaba13ca+a03280dc6b(他队携我方 token 进 HEAD)。
**IBT v2 终局**：四窗跑完，FAIL 如实裁决（HOLDOUT 净夏普 -0.938/换手 20.85x 超标），完整性门 PASS 反前视全绿——链路真通、池中 alpha 未过终考，批 D 选择窗结构混杂已呈 Owner。
