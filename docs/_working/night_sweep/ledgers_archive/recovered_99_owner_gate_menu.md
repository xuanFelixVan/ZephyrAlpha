---
ttl: task_bound
title: 夜战总 Sweep 2026-09-29 OWNER-GATE 总菜单（SW17 汇编）
session: st-nightsweep-sw17-20260929
---

# 夜战总 Sweep 2026-09-29 · OWNER-GATE 总菜单（SW17 汇编）

> sid=st-nightsweep-sw17-20260929｜总筹=st-nightsweep-chief-20260929｜生成=2026-09-29
> 来源=canonical.json（st-legacy-audit-20260929，verdict=OWNER_GATE 75 条）×14 份 SW 车道台账×fullconnect 99_skipped_for_owner.md（现 #1-45，SW5 增 #42-45），去重汇编。
> 每项一行：编号｜事项｜等 Owner 什么决定｜处方/执行单位置｜紧急度。 ★=top5 时间敏感。
> 纪律：AI 侧零代裁零执行，全部待批文；紧急度=高（倒计时/断链风险）/中（阻塞工程链）/低（可攒批）。

## ① 资金与实盘

- A1｜F53 实盘接线（TradingSession 切 Saga 编排器）｜等：是否批准独立实盘装配通道立项｜处方：build_sim_saga 已 fail-closed 物理封死实盘路径（environment!=sim 一律拒绝），sim 五合规件装配+80 测绿在案（SW9 台账）｜低（宜等考试链绿）
- A2｜TRD-A10 两步走（99#29/C63）｜等：实盘拒单启用=Owner 亲手+30 交易日窗；沙箱 v16→v17 换版重启窗｜处方：工程面就绪；关联 F56 内核三选一销账（C42，B7 超集已落地）｜中
- A3｜实盘准入 live O-2~O-9（C287）｜等：模拟盘绿天数自然积累+G18+沙箱观察窗数据后批｜处方：准入清单在册｜低
- A4｜F92-序3 campaign 带占位立正式裁定（PQ-0099 §4，SW9）｜等：占位带是否转正式裁定｜处方：序1 已落地 3cb98bb6｜低

## ② 净删与退役（物理删除类，批前零动作）

- B1｜F127 data_eng 全包（16 件）净删三选一（99#42，SW5）｜等：①保 F08 删本包 ②本包取代 F08 ③保留待接线｜处方：16_f127 案卷+[DEPRECATED]+successor 注记已落｜中
- B2｜F128 data_security 三件净删或接线二选一（99#43，SW5）｜等：净删+known-gap 兜底 vs 定接入点（数据出口+LSG l1 前置）接线｜处方：12_f128 案卷｜中
- B3｜F130 ml_serve 四件净删+model_drift_monitor 双同名 clone 判定（99#44，SW5）｜等：净删批文+clone 归属裁走｜处方：13_f130 案卷｜中
- B4｜F62 ZephyrAlpha_PostSettlement 计划任务退役+AutoRuntime 重启运维窗（99#45，SW5）｜等：unregister 时钟腿批文+重启窗时点｜处方：事件触发腿已落地 35ca1d69（14 测绿），过渡期双腿并存安全｜中
- B5｜CN-MACRO 整族退役候选（SW10 §二+SW14 zero 复核维持）｜等：净删/整族退役（MAC-001~016 总裁 CNS-04 未动）｜处方：SW10_cns_chart_wiring.md §二｜低
- B6｜指标退役候选群：CHIPS 5 条+族⑩ residual 61+族⑤ macro zero 15（SW14 消化度终账，全部只登记禁删）｜等：批 retire 或批接线（CHIPS 转绿路径=D21 获利盘接线后幂等重跑）｜处方：cns_closeout_ledger.md｜低
- B7｜ROOR 223 册收敛 8 净删候选（C24）｜等：带 successor 去向打包批｜处方：S4_registry_machine_governance §4.4｜低
- B8｜翻译册 3 条 wo001_003 悬空条目净删（C35）｜处方：[allow-mass-deletion] 正门提交模板已备｜低
- B9｜RestartMiniQmt 残壳计划任务删除（C301）｜处方：删前留档｜低
- B10｜REG-MIGRATION-001 13 条 pending 退役（C379/F123 P0）｜等：退役排班或维持冻结｜低
- B11｜windows_service.py 退役候选（C394/99#37，SCM 未装实证零消费者）｜处方：99#37 判据全文｜低
- B12｜清盘真删授权（C410 乙方案）｜等：按清单勾选真删件｜处方：标记+隔离已做，删前字节对拍双证｜低
- B13｜F56 kernel 三选一正式销账（C42/99#36）｜处方：B7 超集 78982c4c81 已落地=事实封存，只欠 Owner 一句话｜低
- B14｜终局菜单④件（C490：FMS-HYGIENE 翻硬拦/8 候选净删/镜像树迁移/165GiB 归档豁免）｜处方：99 册菜单（165GiB 需先出归档处方再批）｜低
- B15｜空壳表逐表选型 9 张（C120：建采集腿 vs known_data_gaps vs 退役）｜等：逐表批注（CH 已复活，建腿可开工）｜处方：H-10 通道（X-53 已撤"请新批"）｜中
- B16｜I6:I34 陌生 blueprint 178 件物理删除（SW11）｜等：四路核数未复现该集合；若 Owner 持他源 178 清单请提供后按令甄别｜处方：SW11 台账甄别记录｜低
- B17｜qmine 非标 severity 变体余量定性（C18）＋W-163 ⚑菜单补位批 7+2 项（C133）｜等：逐项呈批｜低
- B18｜O-6 跨车道 164 枚暂存删除三分诊+_working 10 件/全仓 175 件在册被删定性（C124/C461/C462）｜等：按编号批搬迁/清理/误删｜处方：册面已落地｜中（主区脏面 253 与此直接相关）

## ③ 冻结判据与预注册（考试链）

- C1★｜T2 survival_floor 存活地板调整（SW4）｜等：裁 survival_floor 调整（声明通道）或批新 T1 搜索空间——cost_gate_spot 30/50 破 40bp 地板，归因=高换手高集中簇结构性（非修复引入）｜处方：sw4_t1_repair_pairing_report.md+SW4 台账 C1；修复后 5/6 判据绿已落 d094852ffa｜高（T2 唯一解锁闸）
- C2｜T1 成绩单 3698+2 定稿（C69 裁2）｜等：按 17 号文验收（R-2 幸存者分层抽查口径）出 T1 结论｜处方：93 册已加"2 阴格先补同窗对拍"前置；对拍已由 SW4 完成｜高
- C3｜⚑-2 考试成本门口径拍板（C71）｜等：一句话追认 93 册 B 案（判据对象=中位数≥40bp 功效 n≈82）或驳回→回写 17 号文+登记 ruling_registry｜处方：93 册建议全文｜高
- C4｜T2 发车 900 格终审（C70）｜等：C1-C3 齐后追认发车｜处方：t1_t2_handover 状态机已修（--subspace-json 传参 bug 修复随 d094852ffa，7 测绿），claim 原子防双发｜高（依赖 C1-C3）
- C5｜上岗规则 v1 激活（C76）｜等：Owner 填 state_matrix 或授权按成绩单填；euphoria/distribution 无防御 sleeve 结构性缺口决策｜低
- C6｜波12 统一点火窗口（C58/G33，五触发条件 0/5）｜等：条件①②③推进后呈点火批准卡｜处方：编排闸代码已在 HEAD；G-A.3 图形胞实弹与考试轴启用同窗（SW10 §四声明 prep 已落，冻结件零 diff）｜中
- C7｜成本口径四件（C345：手续费 5 处重复/印花税两侧过期/无规模参数致验收门恒过/阶梯双真源）｜等：⚑-2 口径拍板后先落对账尺再议数值｜中
- C8｜W-178 板块两口径合并/映射（SW4 C5：concept_board akshare 375 vs sector_constituent tqcenter 595）｜等：定合并/映射真源口径｜处方：w178_sector_universe_strict.md+w178_universe_facts.yaml（57 读数双通道一致+2026-09-29 重测互证，§E DRAFT_NOT_FROZEN）｜中
- C9｜时帽 single_job_wall_clock_cap_hours=12 口径追认（C91）＋补-1 限价单相位判据二选一（C445）＋补-2 盘后退出码拆 0/4（C446，牵 38 条冻结契约）｜等：逐项一句话｜低

## ④ 受保护路径与宪法

- D1★｜宪法两行落 HEAD（A37，SW2/总纲②：提交队列 4→6 子命令+数据集成器 7→8）｜等：[ARCH-APPROVAL:#ARCH-362] 通道被 PROTECTED-PATHS 机械门拒——真需要 Owner 正式批文/授权载体｜处方：blob 与 dev 恰差两行零过期（SW12 核），原袋 sw2-0001→sw12-0004 两死于机械门；批文后单件袋即落｜高（宪法计数失真过夜）
- D2★｜裁定册 PROTECTED-PATHS 拦截放行（nightclean 3f75191285e 披露：#421 条目+#419→#420 改号 hunk 就绪被正确拦下）＋裁-13/#420 decision_timestamp 正式注册（99#34，FLD-EXEC-011 补册件已落地）｜等：Owner 一句话或 ARCH-APPROVAL 载体（裁定册=审批权真源，AI 不自我授权写入）｜处方：晨报 V1 清单+工作树就绪件｜高（裁定追认链断）
- D3｜宪法入口三方冲突 F111（C399/99#26：AGENTS L110 仍指 app_panel）｜等：裁宪法入口唯一指向｜低
- D4｜宪法级裁定3：GATE-SELFDOC"门吃自己文档"豁免位立法（C117）｜等：三道门豁免位/统一拆写规范立法｜处方：夜战实证其价值——sw6-0004/sw8-0001 两死于正文取证引文误拦｜中
- D5｜.gitignore 忽略 data/backtest_artifacts 考卷灭失险（C321/甲-3）｜等：纳入版本控制或指定受保护真源位置｜中
- D6｜"_working 新件必须有 created"门立法（C128）｜等：建/不建（建议建，与 FMS-HYGIENE 同族挂接）｜低

## ⑤ 窗口与运维

- E1★｜裁定 #410 approved_paths 续期（C17：docs/01_policies_and_standards/rules/ 免检授权 2026-10-08 到期）｜等：续期或失效（过期 PROTECTED-PATHS 授权链断）｜处方：ruling_registry:5642 续期模板｜高（倒计时 9 天）
- E2★｜10-05 F 盘第一链摘除窗（C109：F:\ch_backup_disk.vhdx 716G 回收；CH 单链归 G=2026-09-28 Owner 终裁已下）｜等：假日批拍板+点停 VM（批文三段式，任何删除等批）｜处方：INFRA-STORE-003 存储地图｜高（6 天窗）
- E3★｜D 盘容量恶化（C38+SW15 R-7：现余 23.1G 持续恶化，commit_queue 占 8.1G）｜等：换小虚拟盘/加物理盘/车道清理三选一授权｜处方：C38 三选一+B02 models 残留+B14 421 件未入库清单｜高
- E4★｜k=4 落地池单工位卡点 ~1.3h/项（SW12 infra_finding：5 袋实证 53-73min，池吞吐坍缩至 ~4 项/1.3h）｜等：授权维护班排查 GATE-PRECOMMIT-RUN 落地面前置 pre-commit run 子进程超时缺失｜处方：SW12 台账 infra_finding 实证清单｜高（堵全队落地吞吐）
- E5｜flags 轮转执行（C110+SW11：feature_flags.jsonl 1.77GB/631 万条，写方唯一 flags.py 逐条 append）｜等：归档去向（G:/backup 或本地 .rotated 留 90 天）+执行时点｜处方：A 方案 rename+自动重建已评估（无常驻句柄，技术风险低，SW11 台账全文）｜中
- E6｜VM /root 两件施工残留处置（C36）｜等：VM 可达窗跑核验命令后批删（留档后删）｜处方：核验命令在 canonical.json C36｜中
- E7｜共享热册单写者收口窗+共享 index 陈旧 staged 面定性+并发写坏 actor 排雷（SW2 FIND-1/2/3：canonical 册 9 会话整文件快照竞速丢 token 实证）｜等：授权收口窗或落地侧处方｜处方：FIND-3 处方=落地侧对 base_blob 漂移强制 requeue 刷新快照｜中
- E8｜CAND-GOVTEST-005 双条撞号存量消解（sw12-0014/sw3-0004 两死同病：三向合并拒绝 ours 自身重复键，先有鸡先有蛋）｜等：授权 registry 去重对账器先消存量（登记面净删）或 Owner 面 manual 合并｜处方：sw12-0014 死袋+007 重编号意图留档｜中
- E9｜R-5 旗标名不匹配跨面施工（SW15：flags.yaml gate_precommit_run vs gateway 常量 gate_precommit_run_enabled，d5 图已带"未注册×恒 ON"实录）｜等：批跨面施工窗（改 gateway 常量对齐在册键+同批改 d5 生成器叙事+重生成图）｜处方：SW15 台账 R-5 配方｜中
- E10｜flag commit_queue_interactive 出厂翻转（C300/99#14）＋AutoRuntime 常驻化窗口（C21）｜等：翻转/开启窗口｜低
- E11｜灾备块（C296：P-6 ch_vm 全量重做 F 盘/P-10 PT4H 硬时限）＋甲-1 g_mirror ch_vm_backup 反向复活防回退锚（C319）｜等：补正式裁定+批防回退锚（禁只修不防）｜中
- E12｜ConfigCheck 日红安全窗重启+F132 计划任务三件（C401/C377/99#41：任务级 action 变更/对账宿主挂靠/重启窗）｜等：任务级三项批注（11:10 重启后 exit 0 回绿实证）｜中
- E13｜AI 排产账本落点 durability（C102）＋OrderFileStore 归档语义（C103）＋R5 三处真源收敛（C299）｜等：逐项裁定｜低

## ⑥ 裁定追认

- F1｜L09-C01 Z-C4 收拢令追认（C68）｜等：不推翻即按收拢令给 L09 补录封矿转 SEALED（推翻则按 (a)/(b) 重裁）｜处方：nightclean 3f75191285e 已补录判(b) 引裁定#421｜高（链上裁定已依赖）
- F2｜t0 甲位三版本分叉三选一（C80：定版本/合并/退役；auto_mount 写回未落 HEAD）｜处方：Z-C1 两硬前置补齐后单件批+脏口径下游重算清单｜中
- F3｜蒸发治本 EV-02~06 施工令（C78：裁定册 0 命中判未批；EV-01 黑匣子已迭代 v8 为唯一落地）｜等：签发施工令（建议与六段收编同批小手术族）｜中
- F4｜W-M1 72h 双轨翻转确认（C79：波0 四表+投影生成器已落，切主扳机等 Owner）｜处方：先修 bundle 契约 bug→补 72h 评估卷→翻转摘旗｜中
- F5｜AI 层通电二次开关（SW2 卡8+SW15 卡4 ⑧⑪③/C87 族）｜等：ai_secret_exposure per-key 标注+读取面断言+spawn 面接线批文；外扫宿主双前置追认；L5 白名单扩面｜处方：执法面本体 COMPLETE+17 测绿，超 09-27 批文语义故登记｜中
- F6｜F04 数据清洗四门（SW9/C66：C1 三引擎生产接线/C3 幽灵行清理/C4 隔离区回放清除/C6 AI 判净站花钱点）｜等：接线批文+花钱决策（分歧率统计出数后呈）｜处方：统一入口 cleaning_engines+manifest 桥已就位即插即用；ai_adjudicate fail-closed 零计费｜中
- F7｜GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER 两聚合台恢复启用（C331 族；Owner B 方案临时禁用中，"187 件落地后恢复"；其下 4 子台执法暂空窗=既批状态非新缺口）｜低
- F8｜GATE-MUT 立项或 mutation_test_reconciliation 整族退役（C370/99#39b；:84 路径一行修处方已备未动码）｜低
- F9｜SW13 战役整合批 272 件待整合（#414/#415 战役编号撞号让号机制重编）＋甲-2 图15 M11/M14/M17 迁移挂门（C320）＋SKIP-4/5（C521/C522）＋W-174 批文宿主注记（C246）＋emoreplay 交接确认（C93）＋账房单一写手正式裁定登记（C100）＋甲-3 相关 C321（见 D5）｜等：逐项呈批｜中（SW13 整合批阻塞六图收口尾）
- F10｜99_skipped_for_owner #1-45 存量全菜单逐项拍板（C65=#1-41 存量+SW5 增 #42-45）｜等：逐项批复（高频 10 项 #29/#34/#35/#36/#8/#14/#21/#25/#19/#20）｜处方：docs/_working/fullconnect_campaign/99_skipped_for_owner.md｜持续
- F11｜任务五七项（C151）＋波2 C 类 11 件（C316）＋族11 终局 Owner 门位簇（C406，归口 93_owner_menu 14 行）＋qmine R3 三密钥门死触发定性（C19，SW15 W-135 已改型治愈死触发面可销）｜等：逐项呈批｜低

## 附：本菜单与台账差异披露

- SW13/SW9 台账 verdict 记 DONE-LANED，但袋终态=dead（sw13-0001 死于 ROOR 基底冲突；sw9-0001 死于 cascade_stale 两册，死因已消）——内容未落 HEAD（SW17 逐一 git 判存核实），不影响本菜单；处置处方见 99_nightsweep_final_report.md §死账。
- canonical 75 条中已销账/被夜战消化者未重复入菜单（如 C45 CH 实弹批已被 SW5 DDL 落地部分兑现→余项并入 B15；C300 入 E10）。
