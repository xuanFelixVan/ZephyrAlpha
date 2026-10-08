---
ttl: task_bound
completes_when: 条目随各自 Owner 拍板批销账后整册归档
created: 2026-10-08
sid: st-mx07-L12
title: matrix_campaign 调度阻塞登记册
session: st-mx07-L12
note: 命名自裁注记——任务卡面名 DISPATCH_BLOCKERS.md 违反仓命名硬门（N-01/N-13 连续大写+非
  snake_case，lock_files acquire 实证拒绝），按宪法§8（TRAE-028）落盘为本 snake_case 名；
  后继车道按本路径追加，勿再建大写名件。
---

# matrix_campaign 调度阻塞登记（DISPATCH BLOCKERS，等 Owner 拍板项）

- [st-mx07-L12] R1/R2 名实错位修复待 Owner 拍板 / 简报=mining/r1r2_misalign_brief_v1.md / 建议=错位本体已治本（裁定#484③+fac9_04_followup§一，commit 9141a83d77/46652cc260），#489⑥ 实为销账+残余清理批：F1 销账裁定（fac9_05 §一 R1/R2 标 resolved+backlog P3-5 销行）＋F2 重跑 gen_search_veins 自愈 VEIN-FAC-E1A 残留 035 挂点（ai_search_veins.yaml:137）＋F3 FAC-E7-M-005 节点名去历史冲突注记（strategy_production_map.yaml:4126）＋F4 TDM-P-P1 补 module_id=MOD-POS-030（trading_decision_map.yaml:2899）＋F5 placeholder 轨再生防再引；全 S 级，建议并入地图值班队下一笔随批
- [st-mx07-W5] 双热册 gateway claim 被 W6 持有（capability_canonical+module_translation 两册，13:3x 实测 conflict held by st-mx07-W6）/ 影响=W5 的 .md token（sector-wiring-doc-…，worktree capability 册 :64324 已在盘）与翻译条目（worktree 翻译册 sector_surface.py 条目已在盘）无法自落 git，内容袋 .md/.py 两件押后 / 处置=W5 已还原工作区全量版（含 W6/wq87/rowvec 面，夜战常态归属各自认领），等 W6 袋落地吸收后 W5 内容袋续投；若 W6 袋死信则按 dead_reason 修正后由 W5 接手重投（其 claim TTL 过期后 gateway.release_files('st-mx07-W6', 两册) 精准释放）
- [st-mx07-chief] 主区暂存区无主 staged 删除险情待处置 / 现象=git status 含 D src/zephyr/backtest/accel/bootstrap_kernel.py（L3 已落地真源核被 staged 删）+bootstrap 三件套 MM，疑似死袋旧快照冲刷残留 / 处置=总包未 reset 未收编（防误伤在途袋）；建议=维护班排查 commit_queue 序列化器暂存区复位路径，收尾对照 HEAD 复核后 restore --staged
- [st-mx07-chief] EXEC-G1 factor_registry 净删在途面备份留证（10+/446-，条目 176→170）/ 位置=.runtime/tmp/st-mx07-chief/factor_registry_execg1_staged_backup.yaml（staged 快照原样，L7 代寄前外科备份）；归属其批；若其批已死建议按 classify_workspace_wip 判读后处置
- [st-mx07-chief] 队列工程债三项 / ①ghost_session 死信家族（L12 袋 q-20261008-st-mx07-L12-0001 死因=车道子代理强杀后属主注销→存活闸拒自动重投；本册 L12 条目已由总包活会话重投承接）；②belt daemon 活锁（L2 观察：心跳活跃但 done 冻结 40min+processing 50min+，堵点已自动登记）；③派单卡 T11"--priority 5 跳队"参数在 git_commit.py/commit_queue.py 均不存在（L11 实测，总包派单卡笔误勘误） / 建议=维护班根治 Windows 下 heartbeat 守护存活率+核对队列参数面口径
- [st-mx07-chief] reconciler critical_warn 24h 内 10 条待查 / 要点=GATE-WORKTREE-DRIFT-WATCHDOG（internal_compute_provider.py=B2 在途 hunks vs L5 切挂面、rowvec_promotion_v1.md）+GATE-DELETE-AUDIT 超时×2+SECRET-REGISTRY-DRIFT（REDIS_HOST/PORT/PASSWORD 缺） / 建议=维护班 query governance.db 取全清单
- [st-mx07-chief] L1 调查移交三施工单（backlog 性质非阻断）/ ①SQUEEZE 三处偏差修复（KC 中轨 EMA→SMA、通道 H-L→TR、动量补 Donchian 分量）+WAD 两行修复（Tulip TRH/TRL 口径）；②fexam v2 entry_role 路由立项（择时/状态零件与横截面因子分考场）；③TREND-036 注册表勘误（"三阶"系命名误读，实现与 Ehlers 官方等价，维持退役） / 证据=mining/classic_indicator_investigation_v1.md
- [st-mx07-chief] L8 情绪首考 verdict=有条件合格的投产前置 / 前置=快照器日批持续跑（scripts/data/emotion_index_snapshot.py 登 reaper 白名单/计划任务，运维面）+只追加读径；历史（≤2026-10-07）无逐日快照留痕不可回补如实声明 / 证据=mining/emotion_index_prereg_and_first_exam_v1.md
- [st-mx07-chief] L7 提交通道留痕 / 原提交在分支 session/st-mx07-L7（32c063db6a）；dev 侧 factor_registry 同窗演进致 worktree merge 真冲突+主区 499 他班 WIP 面拦 WORKSPACE-CLEAN-CHECK，按 st-fcd-merge 代寄先例外科重放（+4/-2 与分支后像逐块相等校验过）随本袋落地；分支拟 abort（内容已由本袋承载）
- [st-mx07-W2] HMM v3 verdict=conditionally_qualified≠qualified → 裁定#489② 判死已执行，HMM 体制识别方向永久退役 / 读数=①0.5520过 ②0.6129过 ③0.4789过 ④med10>5不过 ⑤①分量0.5520<基线0.6129不过（②③④分量过）/ 结果册=mining/hmm_v3_exam_v1.md（全量数值如实报） / 知会面=生产不替换（MOD-REGIME-001 维持现状）；本战役 HMM 体制线不再立项不出提案，体制信号需求回落 SMA200 基线路线或非 HMM 族（需新裁定授权）；v3 产物原地归档不 promote；ranging_low_vol 恒空观察第三次随册反馈（prereg 定义复核仍待 Owner，v2 REPORT 建议#3 顺延）
- [st-mx07-W4] 离场族 12 节点 P2-1 走③路径（prereg 草稿+缺失面呈批，宁缺毋假）/ 勘察=13 节点卡全在册（mining/m2_exit_sector/00_exit_sector_index.md §一）但 B1 schema 新维（X_tp/X_ladder/卖出路由维）"裁定前置"未裁、B2 冻结 prereg 考卡缺（t3b 通道已收官）、B3 考点判据证据冲突未裁（E 道 exit_sim_report_v1 有增益 vs T3b 终判 FAIL a46c937df1 死路钉死——两考卷窗/判据不同，冲突=考点未定）、B4 GPU 预算+T0 重标定窗未立项、B5 X-R1-03 Owner 资金门位 / 产物=mining/exit_family_12nodes_prereg_draft_v1.md（12 节点逐卡 prereg 草稿面+fire_grid 五门 fail-closed 检查单，零跑数零代码零新判据）/ 建议=Owner 一次裁定 B1-B5 后 12 节点即可照 E 道 template 开冻卡施工
- [st-mx07-W4] capability 册热冲突施工披露 / 本车道 creation_token（matrix-w4-exit-family-12nodes-prereg-draft-20261008）已入工作区在册满足 CREATE-GUARD 磁盘口径（先例 L5 a7f7c2b6f43"token 落册随其批"），但该册 gateway claim 在 st-mx07-W2 手中且暂存区驻留死快照（对 HEAD -928/+926 行序回卷，chief 同类险情条目在册）——本车道已做外科修复写（HEAD 版式+工作区纯增 7 条目块，_entry_identity_keys 三向核验零身份丢失，对 HEAD 净+35/-0）后让 claim 归还 W2，token 落 git 随 W2 批或后续 token 袋，本车道不抢写热册
- [st-mx07-W3] CYC 条件变量考场一次窗口执行完毕：family=fail 四件整族退役（裁定#489①）已随本车道主批落地（technical_indicator_registry 四条目 active→retired+evidence+考册 docs/_working/fexam/indicator_conditional_exam_scores_v1.yaml+检验器 scripts/backtest/fexam/conditional_exam.py+留档 mining/cyc_conditional_exam_v1.md；读数=IND-CYC-001 best_p_adj=0.362122 G=0.020558 / CYC-002 0.530570 / CYC-004 1.0 / CYC-005 1.0，基线 B1 mu_all=-0.0517，N_fam=11 解盲前冻结；参照窗 CYC-001 显著但 report-only 不改判，如实留档）/ 披露=capability_canonical_file_registry.yaml 与 module_translation_registry.yaml 两册 gateway claim 在 st-mx07-W6（活会话）手中：本车道两 token/条目（conditional-exam-cyc-scores 册 token+conditional_exam.py 翻译条目）已入工作区在册满足 CREATE-GUARD/TRANSLATION 磁盘口径（W4 同款先例），token 落 git 随 W6 批或后续 token 袋，本车道不抢写热册；registry 净删行为他会话在途治理批（工作区先在内容如实携带零丢失，[allow-mass-deletion] 旗已留痕）
