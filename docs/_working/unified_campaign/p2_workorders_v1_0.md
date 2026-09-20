---
ttl: task_bound
completes_when: WO-1..16 全部终态回执（随战役收官归档）
session: st-unified-plan-20260920
issue: UNIFIED-CAMPAIGN-001-P2-WORKORDERS
---

# 包②交付·派工单集 v1.0（WO-1..16，Flash 分包领单制）

> 定位（裁定#378①）：**执行真源**——每单自包含可整贴 Flash 会话；台账（ledger）管盘点、处方（repair plan）管病历细节，本件管"拿到单干什么、验什么、避什么"。模型路由（裁定#379⑤）：**Flash 执行为主（本件全部单），Max 总包开会出单与验收；破坏性操作单（WO-6/WO-10）加 Owner 在场**。每单回执六要素：文件+commit/红证双向/验收命令实测数字/停手项/证据等级/未完成原因。所有单开工前：冷启动（PATH 3.12→lock cleanup→reaper→会话注册+心跳）+读 `00_master_plan_v1_0.md` §4 时序协议+查 `t_timing_window_board.md` 声明窗。

---

## WO-1（甲·W1）P0 估值双修
- **目标**：A1 index_valuation_daily 派生列 100%NULL+132 重复组→零；A2 daily_valuation 价格腿全 0+周六污染+mock 假绿→零。修前消费禁用声明（估值分位/ERP/市值换手消费方）。
- **处方**（裁定#379①推荐案，签字单③批 a 生效；未批只做无门位半=声明+红证+周六 gate+0 行告警）：A1=version 列单写者（爆炸半径最小+对齐 ReplacingMergeTree 语义）；A2=行情腿同步修（价格腿自 kline_daily 回填）+交易日 gate（trade_calendar 判定）+0 行成功告警；周六污染行冷存后清（可逆）。
- **文件白名单**：src/zephyr/data/**（估值链）、known_data_gaps.yaml、data_supply_sentinel.yaml（告警腿）。
- **红证双向**：修前 cape_5y NULL 率 100%/dup 132 组；价格腿非零 0/271,266；修后同命令 NULL 率=预期值、dup=0、非零率>99%（周六行清零）。复现命令=ledger §6。
- **时间盒**：1-2 天｜**避让**：CH 只读+小写 append；>30min 回填前查声明板；禁碰 akshare_provider 以外 provider。
- **验收**：A1/A2 前后对照表+0 行告警实测触发一次。

## WO-2（甲·W2）断供止血五链+夜跑修复
- **目标**：A4 index_quote 换桥重建；A5 news_sentiment 静默失败排查+接 fetch_perf/心跳日志；A6 auction 桥派生 socket 自愈重试（WinError 10038）；A7 crypto_kline_daily 排查；A8 stock_indicator 09-18 半日重跑；**C-5 夜跑修复**（09-20 04:03 Code 241 阵亡：重跑 dwm 回填补 13.3 万行丢失+验证 gp_pred 等新列回填推进+夜跑窗口与乙声明板避让）。
- **文件白名单**：src/zephyr/data/**、tasks 任务配置随签字⑨。
- **处方**：miniQMT 退役波及面收口巡检（source=miniqmt/xtdata/桥依赖任务逐个点验）；夜跑重跑=单进程串行+低峰窗（CH 内存 7.05GiB 总闸——避开他会话同窗重 IO）。
- **红证双向**：每链修前 max(date)=断供日红证→修后当日 max=最新交易日绿证；夜跑=新列回填率 0%→>0% 且逐日推进。
- **时间盒**：1.5-2 天｜**避让**：同 WO-1；夜跑窗（00:00-05:00）执行前查声明板。
- **验收**：六链各自 by_day 查询 max=最新交易日+fetch_perf 有痕（news_sentiment 接入后）。

## WO-3（甲·W3）哨兵补盲+改册收口
- **目标**：A9 哨兵补 4 行（index_quote/news_sentiment_window/auction_snapshot/tick_data）+新增交易日历逐日 diff 检查器（治内部洞原理性失明，事件触发禁 cron）；A15+A19 known_data_gaps 8 条改册+convertible_bond_list/stock_basic 缺日/etf_list+index_list 存活行补登记；A3 tick 09-17 永久缺口登记留痕（禁再试补）；A13 写入端攒批（12 小表 60s 窗）。
- **文件白名单**：data_supply_sentinel.yaml、known_data_gaps.yaml、src/zephyr/data/ 写入端、日历 diff 检查器新模块（走 CREATE-GUARD+模块翻译登记全头）。
- **红证双向**：检查器注入测试洞（删一日日历期望）→抓到=绿；4 表阈值行加后 sentinel 实跑 breached 覆盖新腿。
- **时间盒**：1-1.5 天｜**避让**：检查器挂载随签字⑨；禁碰 tasks.yaml 本体（未批前）。
- **验收**：sentinel check_tables() 实跑输出含新腿；known_data_gaps 册账实一致（逐条 diff）。

## WO-4（甲·W4）tilib 延续批（勘误丢失项①②归位）
- **前置**：乙 W1 落地后（D 空间协议）；TI OPTIMIZE 若排队中先让（同表互斥）。
- **目标**：C3 批10 筹码族三件套 CYQ/SCR/CYC（chips_winner/chips_avg_cost/chips_cost_5/chips_cost_95 迭代衰减算法+SCR 集中度+CYC 成本均线通达信口径；注册表 138→141；【扩项 2026-09-21 tc_10 挂接批·Owner 今夜范围令第1波】+chips_cost_15/chips_cost_85 两列+CHIP_CONC_90/CHIP_CONC_70 两指标（70%/90% 筹码集中度；真源 docs/_working/collection_intake/factors/factor_spec_chip_concentration.md，intake 侧「并入批10」承诺此前未回写本工单，本段即回写）；注册表计数目标改为基线日实测+5（2026-09-21 夜实测 138 条=HEAD 零漂移，即 138→145；开工日以 grep -cE "^- indicator_id:" 重测为准，tc_10 卡调查时点曾记 140 以实测为准））；C2 stock_daily_basic 每日增量挂 tasks.yaml；C5 尾款=210 列验收核销（探针思路 .runtime/tmp/tilib-probe/audit_all_cols.py，全部新列分批验收留痕）。
- **真源**：`docs/_working/archive/2026-09/c_class_scattered/2026-09-15-tilib-handoff.md` §3 批10（新路径！）+`design_memos/16_technical_indicator_catalog.md`（活真源，勿归档）+tilib a5 交付报告。
- **文件白名单**：src/zephyr/factor/technical_indicators/**、tests/zephyr/factor/**、technical_indicator_registry.yaml、16 号 memo、tasks.yaml（仅签字⑨批后）。
- **红证双向**：新指标单测+注册表计数 基线+5（@09-21 实测 138→145，含扩项 CHIP_CONC_90/70）；CYQ 抽样复算（如 000852 获利盘比例手工复算对齐）；验收=新列回填非零率>95%（近月）。
- **时间盒**：1.5-2 天｜**避让**：CH 写入走 ch_writer；东财拒连→tushare；夜跑窗查声明板。
- **验收**：注册表 v1.5.0→v1.6.0+测试全绿+210 列验收台账闭环。

## WO-5（乙·W2）日志滚动永久化（无需签字，最急）
- **目标**：text_log level 调低+system log 表原生 TTL（trace_log/query_log 7 天、余 14 天）+max_size 轮转→低峰重启→24h 复测膨胀<1G/天（151G 余量 2-3 个月窗，最急项）。
- **文件白名单**：scripts/ch/**、CH DDL（系统表用 default 超户；zephyr_writer 无 TRUNCATE system.* 权限勿改 RBAC）。
- **时序**：闪断档——声明板登记重启窗（避开 00:00-05:00 计划任务带与甲在途批）。
- **红证双向**：重启前 TTL/level 配置查询红证→重启后 system.log_tables 配置绿证+24h 膨胀实测<1G。
- **时间盒**：0.5 天+24h 观察｜**避让**：声明板协议强制。

## WO-6（乙·W1+W-并入）CH 库内清偿（签字①②批后·独占窗·Owner 在场）
- **目标**：A11 尸体表 35.4G 逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop（张数 12vs17 执行日实测仲裁）；欠账 24.9G 走 archiver archive-range；A12 1970 十八表 PIT 关死/补真值；A13 12 小表 OPTIMIZE FINAL；A10 TI OPTIMIZE FINAL（dwm 停+parts 回落后，C-5 修复为前置）。
- **数据第一公理**：任何删除前两份验证副本；drop 前行数 verify；>50G 表 TRUNCATE 保险丝=?session_id 两连发。
- **文件白名单**：scripts/ch/**、archiver.py 通道、known_data_gaps（1970 关死登记）。
- **红证双向**：drop 前 system.parts 尺寸快照+export 行数=表行数；drop 后尸体清零+内部空闲≥200G。
- **时间盒**：2-3 个独占窗｜**避让**：独占窗内与甲互斥（声明板）；禁与批10 回填同窗。

## WO-7（乙·W3）冷储主库落 F
- **目标**：E:\zephyr_cold_archive 117.6G→F:\zephyr_cold\50_archive\by_project\zephyralpha\（robocopy+文件数/字节/5% hash 对账）→引用 7+1 处同 commit 改齐（archiver.py:69,732/asset_inventory.yaml:139/infrastructure_registry.yaml:200-203/registry_of_logs.yaml:808/services_registry.py:118-120/backup_config.yaml:88-89/data_retention_contract 核对）→dashboard 探针绿→E 侧留观 30 天。G:\zephyr_cold 整体迁 F 同配方。
- **红证双向**：引用残留 rg 扫描 7+1 处改后零命中；对账三方数字一致。
- **时间盒**：1 夜窗+0.5 天｜**避让**：热文件（registry 三件）逐个 claim；与 WO-16 R8 的 gate_registry 避让。

## WO-8（乙·W4）F↔G 调换
- **目标**：首查 /mnt/chbackup_local 物理身份（疑似 F:\ch_backup 映射——**核实前禁动 F 盘任何搬运**）→声明板登记暂停 backup.ps1→ch_backup_disk.vhdx 526G/db_dumps/offrepo 大镜像 F→G 对账→backup_config 更新→恢复实跑成功。
- **红证双向**：调换前后 backup.ps1 实跑各一次成功；offrepo targets 配置 diff。
- **时间盒**：1 夜窗｜**避让**：夜间无备份触发窗；Owner 知会。

## WO-9（乙·W5）宿主清偿（两段拆跑）
- **目标**：段一（签字后任意低峰，早做早减压 D）：.runtime 45G 走 classify_workspace_wip；models/ 14.3G 先 rg 引用再处置；tmp_db_dumps 轮转；D:\nonexistent 等小目录三层验证后清。段二（≥2026-10-18）：研报 E 侧删（30 天窗到期+G 侧对账）。验收=D 剩余≥60G。
- **红证双向**：df -h 前后对照；研报对账 2019_bundle 29,998=29,998 复核。
- **时间盒**：1-1.5 天｜**避让**：classify_workspace_wip 流程强制（禁肉眼判罚）；活跃会话 staging 禁碰。

## WO-10（乙·W6）vhdx 压缩（Owner 在场·全局冻结）
- **目标**：F 新鲜备份前置→停 VM→Optimize-VHD Full→起 VM→全链健康探针→季度巡检自动化登记。验收=vhdx≤450G+内部空闲≥150G。
- **时序**：全局冻结档——声明板登记+甲丙全停确认（SessionRegistry 空+甲挂起）。
- **红证双向**：vhdx 尺寸前后+CH uptime 重置+全链探针绿。
- **时间盒**：Owner 在场 0.5 天。

## WO-11（乙·W7）终验红蓝（全战役终局凭证）
- **目标**：五盘对照表全绿+引用残留 rg 扫+搬运抽 hash 复测+备份恢复演练两次（G vhdx 分区+F parquet 分区）→交付报告。
- **时间盒**：0.5-1 天。

## WO-12（丙·W1）疑似真 bug 14 条认领
- **目标**：R3 §2 C 类表逐条（SCD2×4 优先：tests/zephyr/data/test_index_constituent_scd2.py；循环导入 src/zephyr/infrastructure/reliability/；撮合价×3；子进程挂起 phase_check_registry.py:77）复现→真 bug 修复+红证双向→非 bug 写结论留痕。
- **文件白名单**：tests/**（治理性）、对应 src 修复点（最小 diff，禁顺手重构）。
- **红证双向**：注入红（还原 bug 条件断言失败）→修→绿。
- **时间盒**：2-3 天｜**避让**：src/zephyr/data/** 归甲（SCD2 若涉数据链实现与甲协调，甲优先）。

## WO-13（丙·W2）测试真账 32 条+A14 资产册重建
- **目标**：A17 治理门真账逐条（D38 三未登记库 domain_responsibility_layer_mapping/fail_open_register/standard_family_registry 按内收四判据裁登记或退役；decision_map R24 复发修复；governance 9 文件处置；battle_map 33 步拓扑 3 条；blueprint 引用 3 条；cron 断言过期 4 条）；~9 条测试污染假红修测试隔离；A14 77 表未登记 data_asset_registry 生成器口径重建（禁手工）。
- **时间盒**：1.5-2 天｜**避让**：修复禁碰生产路径；生成器走正门。

## WO-14（丙·W3）包①企架施工文档归置（Owner 强迫症项）
- **前置**：开工先登记"此前保留裁定翻案"新裁定（Owner 2026-09-20 口头翻案=本 v1.0 指令链）。
- **目标**：design_memos 全目录+implementation_plans 全目录逐件三裁：a) 活设计决策→精华晋升 docs/03_modules 蓝图（GATE-12+module_id 锚定）；b) 历史施工记录→git mv 归档 archive/2026-09/design_memos|implementation_plans/；c) 已废弃→salvage 要点后删。两目录终态（清零后留壳 or 删+目录契约同步）。引用面 grep 改齐同 commit。
- **特判警示**：16 号 memo=tilib 活真源，**特判晋升正式资产禁顺手归档**（甲 W4 C3 批可能同时更新它——甲先行，丙避让该单文件）。
- **红证双向**：归置台账（每件去向一行）+引用面 DOC-REF 零断链。
- **时间盒**：1-1.5 天。

## WO-15（丙·W4）历史悬账验活核销（只读先行零冲突，可即刻）
- **目标**：D1 staged 175 件逐条判归属（git log --all --find-renames 验内容是否已落地）→已落地核销/未落地评估入册；D2 判定台账 42 行 pending 逐行判；D3 backlog 140 条抽验活死；D4 allow_empty 12 表逐表收口（与甲 W3 对齐口径）。
- **纪律**：验活只读；处置动作分小批走正门；staged 件处置参考归档三连坑配方。
- **时间盒**：1.5-2 天。

## WO-16（丙·W5）final3 尾巴+排期出单
- **目标**：R8=P9 池两小件（.pre-commit-config+gate_registry GATE-21 文案对，mutation 连环坑配方=拆批+同 shell env+直连；Layer2 无 message 通道治本）；R9=死信 q-0040 ALGO-FLOW 断锚清锚或登记豁免；R10=capability 册旧路径 token 残留+reversal.py 行1 stale（C-4）；R11=W7 股权穿透切施工派工单（只出单不施工，交 Owner 点火）。
- **时间盒**：1 天｜**避让**：gate_registry/.pre-commit-config 热文件 CAS；R8 拆批防 mutation 连环。

---

## 领单协议

1. Flash 会话领单=新会话贴对应总包线指令（w_line_*_v1_0.md）+本件目标 WO 段；或 Owner 直接贴单开独立会话。
2. 单内任务完成=回执六要素写线内台账；单间依赖（WO-6→WO-4；C-5 修复→A10 OPTIMIZE）由总包会话核对后放行。
3. 时间盒超限=如实停手写回执（未完成原因），禁硬闯。
