---
ttl: task_bound
completes_when: v1.0 方案产出
session: st-maxexec-20260920
issue: UNIFIED-CAMPAIGN-001-INPUT
---

# Owner 四包原文（v1.0 重制的唯一完整输入真源，逐字录入 2026-09-20）

## ============ 包①：企架施工文档归置 ============

{我看到 Working 、里面还有一些文档，就是那些文档是什么？不是，我们是说计划把这个文档里面的东西全部做完吗？这些文档是新建的是吧。嗯。然后那些文档东西可以后面再全面检查一下。嗯。把这个文档里面的所有工作全部收尾，然后该归档的归档。D:\ZephyrAlpha\docs\02_enterprise_architecture\07_trading_decision_architecture\design_memos、D:\ZephyrAlpha\docs\02_enterprise_architecture\09_ai_architecture\implementation_plans 然后这两个文件夹下面的所有文档啊，虽然以前已经判定过一次啊，就是这里面的文档必须保留，但是我觉得保留在这里是不是也没有什么意义。因为他们是施工文档，施工完成之后，应该按理说他们要么就是归到去蓝图，对吧？要么就是完全归档。我感觉放在这里好像没有什么意义，放在这里好像是不规范的一种表现。它要么就是去蓝图，要么就是去归档了。它不是作为这个我们的全景图，因为我们整个这个大的文件夹里面应该是放的都是全景图一类的东西吧。所以他们说作为施工处放在这里好像不是很合适，虽然移不移动他们都呃没关系，并不会影响什么，但是我强迫症啊，终极强迫症，我觉得放在这里不规范。我感觉是不规范的，除非你觉得是规的，你规范的。如果你觉得是规范的也行。}

## ============ 包②：四路遗留排程裁定令 ============

# 【遗留任务总清欠·排程裁定班】四路遗留全盘点+执行顺序裁定+派工单生成（只裁定+出单，不施工）
# sid 建议：st-backlog-max-20260920 ｜ 落盘：docs/_working/backlog_clearance/ ｜ 模型=Max（裁定班）

## §0 使命（先读）
四个并行战役（dataqa 双审计/final3-maxexec/tilib-clear/历史悬账）产生了大量遗留任务，且已实测出资源冲突。你是总排程裁定班：把四路遗留全部盘点成一本总台账，裁定执行顺序与依赖，产出可直接发给 Flash 执行班的派工单。本班只裁定+出单+落盘，不施工不改代码（修库/修码全部留给执行班）。

## §1 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
会话注册+心跳 daemon（PowerShell Start-Process 独立进程，配方=docs/_working/rule_audit_campaign/2026-09-19-construction-handover-prompt.md 纪律 8 条）。
宪法 AGENTS.md 全程有效；裁号必 re-find max+1 入 ruling_registry（同 commit 原子）。

## §2 真源读序（按序读，勿背数）
1. docs/_working/dataqa_audit/ 四报告（今日刚完成的双审计：ch_health/gaps_registry_review/test_health/cross_findings + a1_progress）——A 路遗留全部细节与复验命令在此
2. docs/_working/final3_campaign/a1_campaign_ledger.md + git log --grep maxexec 近 48h——B 路现状
3. docs/_working/tilib_clearance/ 台账 + git log --grep tilib 近 48h——C 路现状（注意其 6 文件已 claim 待 Owner 口令的 136→138 批）
4. docs/_working/dataqa_audit/test_health_report.md §2/§3——测试侧真账/假红/疑似 bug 全编目
5. src/zephyr/data/config/known_data_gaps.yaml + data_supply_sentinel.yaml——缺口/哨兵真源
6. 悬账核实：git status（189 件 staged 现状）、governance 台账表——D 路逐条验活，陈旧条目标记作废

## §3 四路遗留总清单（开工先逐条验活再入台账，本清单是索引非真源）
【A 路·数据审计遗留】
A1(P0) index_valuation_daily 派生列 100% NULL+132 重复组复发——三选一：version 列单写者/internal_compute 接电唯一派生方/原始派生分表；修前估值消费禁用
A2(P0) daily_valuation 价格腿全 0+周六污染+mock 假绿——A1 改 Nullable(推荐)/A2 行情腿同步/A3 摘 9 列(Owner 门)；配套 0 行成功告警+交易日 gate
A3 tick 09-17 双通道全黑=永久缺口——登记留痕（QMT 已退役 bdpan 07-03 停更，禁止再试补）
A4 index_quote 09-16 停——采集链换桥重建（ZephyrAlpha_IndexMinuteEOD 已死）
A5 news_sentiment_window 09-14 停——run_nightly_sentiment 静默失败排查+接心跳日志
A6 auction 09-17 停——桥派生 socket 自愈重试（fetch_perf 09-17 WinError 10038 实锤）
A7 crypto_kline_daily 09-19 断——daily_crypto 任务排查
A8 stock_indicator 09-18 半日——重跑刷新补齐
A9 哨兵盲区——data_supply_sentinel.yaml 补 4 行(index_quote/news_sentiment/auction/tick_data)+新增交易日历逐日 diff 检查器（治"内部洞"原理性失明）
A10 technical_indicator 1339 parts——等 dwm 回填停→凌晨独占窗 OPTIMIZE FINAL（与 C 路合并）
A11(P2) 17 张备份污染表 35.41GB 清理（Owner 门；清单=R1 §5）
A12(P2) 1970 假日期 18 表 43.6 万行 PIT 关死或补真值（Owner 门；大头 restricted_shares 34.3 万）
A13(P2) 12 小表 parts 爆炸——写入端攒批+OPTIMIZE（清单=R1 §3.3）
A14(P2) 77 表未登记 data_asset_registry——生成器口径重建（禁手工）
A15(P2) known_data_gaps 8 条改册（清单=R2 §2.1；含 etf 时区已执行须改 completed）
A16(P2) 周末写入卡交易日 gate（sector_fund_flow+daily_valuation）
A17 测试真账 32 条——D38 三未登记库(domain_responsibility_layer_mapping/fail_open_register/standard_family_registry)+decision_map R24 复发+governance 9 文件（归 final3 W8 或独立批）
A18 疑似真 bug 14 条——逐条立小工单（SCD2×4 优先；全路径=R3 §2 C 类表）
【B 路·final3/maxexec】以其台账为准盘点（W7 股权穿透底座/W8 working 收尾/T1 复权链/registry staged p14 token 未落地/代裁 10 项），本清单不代列
【C 路·tilib-clear】136→138 待 Owner 口令；dwm 回填收尾+A10 合并；D 盘 28G(97%满)清理方案
【D 路·历史悬账】189 件 staged/判定台账 42 行 pending/backlog 140 条 B0/allow_empty 12 表收口——逐条验活，已解决标作废，活的入总台账

## §4 资源约束与冲突（排程硬输入）
1. D 盘仅剩 28G（97% 满）——一切大规模回填/备份/导出前必须先出清理方案
2. CH 内存 7.15GiB 上限；重 IO 操作（OPTIMIZE/大回填）只能 02:00-05:00 独占窗，互斥排程
3. 并发会话有效额度 2-3（跨会话共享）；st-maxexec 与 st-tilib-clear 可能仍在飞，开工先查 SessionRegistry list_active + git log 近 2h，活的避让
4. 长批任务必被 SIGTERM（实测 7 杀）——执行班工单必须写明：分片+每域独立 json+增量落盘+幂等 resume
5. 提交正门 git_commit.py --enqueue；docs/_working 新目录禁数字后缀（R5 门）；新文件禁 doc_type（EXEMPT-FM 门）；注册表净删须 message 加 [allow-mass-deletion:理由]

## §5 本班要裁定的问题（逐条给裁定+理由，入 ruling_registry）
1. A1/A2 两个 P0 谁先进、方案选型建议（A2 的 A1/A2/A3 三选一给推荐）
2. 四路遗留的执行波次：建议按"P0 数据正确性→断供止血→哨兵补盲→卫生清理→测试真账→疑似 bug"分波，每波列并行度与互斥关系（尤其 CH 独占窗与 D 盘约束）
3. A17 归属：final3 W8 吸收 vs 独立 Flash 批
4. 哪些必须 Owner 门位（A11/A12/A2-A3/净删类）单独列清单待批
5. 每包派工单的目标模型（Flash 执行为主，破坏性操作包标 Owner 在场）

## §6 交付物（全部落 docs/_working/backlog_clearance/，CREATE-GUARD token 同批）
1. backlog_master_ledger.md——总台账（四路来源/真源指针/依赖/状态/归属/工量）
2. execution_plan.md——波次执行计划（含互斥矩阵与 CH 窗口排期）
3. workorders/w1..wn.md——派工单（每单：目标/文件/处方/红证双向/验收/时间盒/模型/避让清单）
4. o_pending_owner.md——Owner 门位清单（拍板项+默认建议）
5. a1_progress.md——进度台账；裁定入 ruling_registry
自查循环：连续两轮 0 问题（台账每条有真源指针+路径存在+数字可复现）；红蓝一轮=随机抽 5 条台账反查原始报告核对。

## §7 纪律
纯裁定+落盘；禁改 src/代码/config/known_data_gaps/sentinel/任务表；禁动他会在途件（registry 上 st-maxexec 的 staged p14 token 是活例，勿吸收勿 reset）；四报告数字已红蓝验证可直引，超出范围的须自行实测再写；每报告回执六要素（路径+commit/覆盖面/复验命令/停手项/证据等级/未覆盖）。
（补充：①B 路明确"以其台账为准盘点"而不替它列死——final3 是活会话，遗留状态开工时验活最稳；②执行班用 Flash 没问题，但每张工单凡碰 CH 数据的（OPTIMIZE、回填、备份表删除），照 §4 独占窗和 D 盘约束跑。）

## ============ 包③：三会话遗留合并仲裁令 ============

# 【跨会话遗留任务·盘点与执行令总包】ZephyrAlpha 三会话遗留合并仲裁班
# sid 建议：st-legacy-arbiter-20260920 ｜ 执行模型：Max（判官活）；判完输出 Flash 分包执行令另开会跑
# 落盘：docs/_working/legacy_arbitration_20260920/（目录名禁数字后缀，用 legacy_arbitration/）

## §0 终极目标
把三个会话（tilib-clear / final3-maxexec / dataqa健康检查）的全部遗留任务摊牌、定序、出方案：
①产出《遗留任务总台账》（每行：来源会话/事项/完整路径/背景/依赖/建议执行序/预估工时/风险）；
②产出《数据库健康问题修复总方案》（以 dataqa 四报告为病历，逐条：复现命令→根因→修复处方→验收命令）；
③产出可机械执行的【Flash 分包执行令】（每包一个文件清单+验收判据+避让清单），交 Owner 派工。
本班只裁定与开方，不重施工（小修可顺手，大活切包）。

## §1 性质判定
判官活：排序与仲裁密度高，故用 Max。三个来源会话的已完成工作一律不重做、不翻案；先读账本再动嘴；涉及他会话在途件（final3 未提交的 TTL 删除等）只登记不代动。

## §2 冷启动（每 shell 必做）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"；python --version 须 3.12.x
python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status
会话注册+心跳+提交同 shell 链（session_worktree_start(session_id, allow_workspace_drift=True) + SessionRegistry().heartbeat）；
宪法 AGENTS.md 全程有效；提交唯一正门 scripts/git_commit.py --enqueue --files 白名单。

## §3 真源读序（按序读，勿背数）
1. docs/_working/tilib_clearance/tilib_clear_a1_ledger.md（tilib 班台账：波1-6+裁①..⑨+登记债）
2. docs/_working/tilib_clearance/tilib_clear_a5_delivery_report.md（终态对账+遗留 §5/§6a）
3. docs/_working/dataqa_audit_20260920/ch_health_report.md（CH 健康病历——数据库问题修复的输入真源）
4. docs/_working/dataqa_audit_20260920/test_health_report.md + gaps_registry_review.md + a1_progress.md
5. docs/_working/final3_campaign/a1_campaign_ledger.md + x1_dead_letter_report.md + w9_triage_ledger.md（final3/maxexec 账本）
6. docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md（v1.10.0 终态）
7. CH 实况自查（勿信报告旧数）：system.parts 水位/system.error_log 近 24h/D 盘 df -h

## §4 硬事实（2026-09-20 傍晚实测）
- tilib 班全部落地在 HEAD：注册表 138 条(v1.5.0)/宽表 210 列/测试 1079 passed/批9 数据批 000852 覆盖 100%（commit：7c7396cc69 波1+2、020728598c 波3、3424a718e7 a5、7fbec92e89 波5、509db008fb 波6）
- c1_market.stock_daily_basic 已建成：705.7 万行/5777 标的/四列 100%（tushare daily_basic 源）
- D 盘 732G 只剩 28G（97% 满），CH 占 423G；CH 26.6.1 uptime ~58h
- CH 26.6.1 新坑：CREATE TABLE 的 ORDER BY 多键必须元组形式 ORDER BY (a,b)，裸逗号被 Code 62 拒
- 东财历史接口傍晚整段拒连（RemoteDisconnected）→换手率类一律走 tushare daily_basic（token=secret_registry TUSHARE_TOKEN）
- 工作区有数百个 docs/_working 旧文件被 final3 TTL 扫除删除（大量未提交 D 状态）——归属 final3，本班只登记现状
- 提交门死因配方全集已沉淀 tilib 班记忆（R5 目录后缀/CREATE-GUARD 15字段/EXEMPT-ZONE-FM/N-16 基名唯一/#341 ruff/净删标记/租约停摆 drain 法/D-15 过滤器口径）

## §5 已知遗留任务清单（起点，本班须复核补全成总台账）
【tilib 班】①D 盘水位治理（需 Owner 拍板：4T 冷搬/退役 5.4G 备份表 kline_etf_1min_tz_bak_20260918/清理）②stock_daily_basic 每日增量挂 tasks.yaml（采集器 scripts/data/backfill_stock_daily_basic.py --source tushare）③批10 筹码族指标 CYQ/SCR/CYC（原料已就绪，配方=交接包 §3+16号 memo 批10）④今晚 02:30 夜跑 210 新列回填质量验收（探针=.runtime/tmp/tilib-probe/audit_all_cols.py 思路）⑤东财傍晚拒连（用 tushare 绕）；⑥reversal.py 行1 注释 stale+旧路径 token 残留（无害小尾巴）
【dataqa 班】CH/测试健康检查查出的问题全清单（读 §3.3/3.4 四报告，逐条复现定性——报告是死的库是活的，先复现再修）
【final3/maxexec】①szopen 一件移交未完（终局报告 e7531c2f3b 自述）②死信 q-0040 ALGO-FLOW 断链（decisiongraph_adapter.yaml 已删但有锚）③TTL 扫除数百删除未提交（现状登记，归属他们）
【共同】死信 dead_purged_20260920/ 内全部勿 requeue；capability 册旧路径 token 残留（无害可顺手清）

## §6 施工纪律（违反必炸，浓缩版）
长脚本一律 Write 落文件再跑（heredoc/内嵌引号会被 bash 吃）；热文件 safe_write_text+CAS+进程外核实；新文件先 CREATE-GUARD token（顶级 creation_tokens 节，锚 \ncreation_tokens:\n）+15 字段全头+module translation；docs/_working 文件 ttl 只许 task_bound、禁 doc_type；文件基名全局唯一；注册表大描述行改动带 [allow-mass-deletion:<理由>]；改前 lock_files.py acquire、会话注册+心跳+commit 同 shell；CH DDL 后必 system.columns 探针；他会话在途件避让（撞锁等 5 分钟）；测试禁写生产路径。

## §7 产出物（落 docs/_working/legacy_arbitration/）
a0_master_ledger.md（遗留总台账：全量逐行，含来源/路径/背景/序/工时/风险）
a1_db_repair_plan.md（数据库健康修复总方案：复现→根因→处方→验收，逐条）
a2_flash_dispatch.md（Flash 分包执行令：P0/P1/P2 分包，每包文件白名单+验收命令+避让清单——Owner 拿它直接开 Flash 会话）
每完成一件回执六要素：改动+commit hash/测试实测数/验收命令与数字/停手项/证据等级[亲验]/未完成原因。

## §8 自裁框架
遇分歧按"客观专业架构师+第一性原理+项目 100% AI 开发现实"自裁并登记；真无法裁=登记 o_pending_owner.md 跳过继续；只有阻塞不可绕才停。数据库破坏性操作三步验证（必要性/真实性/可逆性），Owner 门位项（资金/注册表净删/production 流转）留待批。

## §9 收官
循环检查连续两轮 0 问题→a0/a1/a2 三件 promote 落盘→向 Owner 交《执行顺序总令》一句话版："先修什么、再修什么、哪些等 Owner、哪些已派 Flash"。

## ============ 包④：磁盘重整+冷储备份自动化线 ============

# 【线任务包·磁盘重整+冷储备份自动化】交 Max 总梳理会话——整合入全项目统一施工方案
# 本包=磁盘线一条线的完整输入。接收方=Max 总梳理会话（统筹整合，不直接施工）。

## §0 你的任务（先读）
你是全项目施工方案总梳理会话。当前四条线：① st-final3 十战线（收尾清零：working 任务书归档+内收+复权链，在飞）② st-tilib-clear 分包A（指标库 34 指标"代码+测试+注册表"三件套清零，在飞）③ st-dataqa 分包B（数据质量+测试健康双审计，纯只读四报告 R1-R4，在飞）④ 本线=磁盘重整+冷储备份自动化（方案与总令已备好，待①②③收口后执行）
**你的产出**：《全项目统一施工方案》（落 docs/_working/unified_campaign/）——把④与①②③的交付物/遗留待办整合排序：全局波次网络（谁先谁后/可并行/必须窗口隔离）、Owner 签字汇总成一张单、每个任务带验收数字与复验命令、断点续班与回执六要素。**只产方案文档，不改代码、不动数据、不搬文件。**其他线若有各自任务包，同格式并入。

## §1 项目背景
ZephyrAlpha=Owner 个人量化交易系统，100% AI 开发，宪法 AGENTS.md 全程有效（硬规则/热文件 CAS/提交网关/禁 cron 事件触发等）。宿主 Windows+HyperV 虚拟机 zephyr-ch 跑 ClickHouse 26.6.1（行情库）。五盘：C=NVMe 系统；D=NVMe 731G（项目仓 D:\ZephyrAlpha 74.7G + CH 虚拟机磁盘 data.vhdx 599G=曾占 D 83%）；E=SATA SSD 931G（软件+热数据）；F=SanDisk 2T USB（实为 SSD，读 374/写 340 MB/s）；G=东芝 4T USB 机械（写 70 MB/s、小文件 11.5 files/s）。Owner 已拍板四盘分工：D=项目+CH 虚拟机、E=软件+热数据、F=冷储主库+working_vault 代码版本库、G=备份兜底+冷储镜像（3-2-1）。**数据安全第一公理：任何删除前必须有两份验证过的副本；drop 前必须行数 verify。**

## §2 硬事实（2026-09-19/20 实测；执行日重跑探针刷新台账，禁凭记忆）
- CH VM 内 /var/lib/clickhouse 631.9G：曾仅剩 6.6G→2026-09-19 晚已 TRUNCATE 全部系统日志释放 145G（现余约 151G）。业务活跃 426.5G=合规热层 361G（tick_data 141.5G=2025-01 起 21 个月、约 6.7G/月唯一增长源；technical_indicator 窗口内 151G；分钟线约 66G；日K/基本面/事件/元数据小）+尸体表 35.4G（news_data_corrupt_20260828 13.0G、news_data_pre_tz2_20260828 12.9G、kline_etf_*_tz_bak 8.1G、kline_1min_tzbak 0.95G 等约 12 张）+契约欠账 24.9G（TI 窗口外 19.4G+冷线 5.5G）。
- 热层有界证明：tick 过 2 年线后（2027 起）热层稳态约 350-400G；150G 冗余≈22 个月纯增长缓冲（Owner 定案按 150G 留，季度压缩巡检）。
- CH 凭据与坑：唯一真源=config/.env.clickhouse；库内仅 default/zephyr_reader/zephyr_writer 三账号，zephyr_writer 无 TRUNCATE system.* 权限（RBAC 设计勿改），系统表操作用 default 超户；>50G 表 TRUNCATE 被 max_table_size_to_drop=50G 保险丝拦——同 ?session_id=xxx 两连发（SET→SELECT 验证→TRUNCATE），禁全局关保险丝；CH 26.6 无 multiquery 参数；CH TSV 分区串带 \' 转义，元组分区解析先 strip 反斜杠；text_log 级别仍是默认 trace（~50G/月回涨，151G 余量约撑 2-3 个月——本线最急项）。
- 冷储现状：G:\zephyr_cold 抽屉库（00_manifest/drawers.jsonl 台账制，研报 90,243 件已入：F 盘 60,245+E 盘 29,998，零失败）；E:\zephyr_cold_archive 117.6G Parquet 冷库（c1_market 115.8+c3_fundamental 1.8）待迁 F；E:\数据下载\研报 84.7G 已复制进 G（2019_bundle 29,998=29,998 对齐），E 侧删除须等 30 天窗（2026-10-18 到期）。
- 代码引用 E:\zephyr_cold_archive 共 7+1 处须同 commit 改齐：scripts/ch/archiver.py:69,732、config/asset_inventory.yaml:139、docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml:200-203、docs/registry_of_logs.yaml:808、src/zephyr/frontend/dashboard/services_registry.py:118-120、scripts/backup/backup_config.yaml:88-89、核对 data_retention_contract.yaml。
- VM 内第二盘 /mnt/chbackup_local（1081G/余698G）物理身份未核实（疑似 F:\ch_backup 映射）——核实前禁动 F 盘任何搬运。
- 保留政策真源=data_retention_contract.yaml：Tick≥2年/分钟·资金面·衍生≥5年/新闻·日K≥10年 手动归档线；<1GiB 研究表永不归档；派生 TI 滑窗 3月/1年/3年/5年（执行极好，全库欠账仅 24.9G）；铁律 INV-RET-002"进冷层必须手动触发"与本线自动化目标冲突，修订路径已在方案 §2/§12。
- 挖矿三发现：①business_data_categories.yaml 114 品类全带 lifecycle 字段但 206 条 permanent 与契约脱节，tasks.yaml retention 字段零命中（身份证载体在、未启用）；②storage_tiering.py 纸面模块（CONSUMERS=scheduler 零引用，接线或退役待裁）；③backup_daily_trigger.ps1（06:00 兜底，post-commit 事件触发）=禁 cron 红线的合法先例，滚动归档挂备份成功事件链即合规。
- 主区状态：三队在飞收尾期，脏文件动态变化；一切提交只走 scripts/git_commit.py --enqueue --files 白名单。

## §3 本线资产与真源路径（全部已落盘+git add）
1. docs/_working/disk_reorg_plan_2026_09_19.md——勘察底数 v2（盘位/速度/库内三笔账/D/E 逐目录清单/软件不迁裁定/引用清单）（注：2026-09-20 final3 C 类归档批已移至 docs/_working/archive/2026-09/c_class_scattered/）
2. docs/_working/cold_backup_automation/00_master_plan.md——自动化方案 13 章（身份证机制/滚动归档 reconciler 五重安全阀/3-2-1-1-0 备份映射/vhdx 150G 专章/保留与清除总清单 17 行表/执行批 0-8/风险回滚/拍板清单）
3. docs/_working/cold_backup_automation/01_mining_findings.md——挖矿报告（9 行缺口表/数据资产清单/8 条意外发现/外部实践对照/20 条引用）
4. docs/_working/disk_reorg_campaign/a0_master_order.md——收口六波总令（三队收口后可粘贴直接执行：W1-W7 全文+验收数字+避让清单+自裁框架）
5. docs/_working/altdata_line/10_g_drive_cold_storage_sop.md——冷库 SOP（抽屉制+三红线 immutable/禁双真源/回测数据家不在冷库）
6. docs/01_policies_and_standards/_registry/contracts/data_retention_contract.yaml——10 层保留契约真源
7. scripts/backup/backup_config.yaml+backup.ps1+backup_reconciler.py——备份链现状（working_vault 14 天轮转/db_dumps 覆盖式缺口/ch 增量/offrepo 镜像）
8. scripts/ch/archiver.py——归档唯一通道（三阶段 export→verify→drop）
9. 探针脚本 .runtime/tmp/{ch_stats,ch_truncate_logs,bench_disk,parse_wiztree}.py（可能已被 TTL 清，可按 §3 真源重建）

## §4 本线已完成（勿重做）
1. CH 系统日志 9 表 TRUNCATE，释放 145G（5.7→151G），业务零触碰零停机（2026-09-19）
2. 研报 90,243 件迁移 G 抽屉库完成并抽样验证（另一会话执行）
3. 全套勘察+方案+总令落盘（§3 的 1-4 号文档）；D/E 盘软件不迁裁定成立（软件合计仅 16G，注册表手术不值）

## §5 本线待执行任务清单（大目标 S1-S7→波次 W1-W7；全文见 a0_master_order.md，此处浓缩）
**大目标**：CH 瘦身到位+日志滚动永久自动化+冷储主库迁 F+G 镜像+备份 3-2-1+宿主清偿+vhdx 季度压缩机制化；终态=五盘容量对照表全绿+热层约 360G 稳态+全自动无人值守+dashboard 冷储检测绿+恢复演练通过。
- W1 CH 库内清偿（S1）：12 张尸体表逐表 export Parquet 双副本（F+G）→行数 verify→凭批文 drop【M】；欠账 24.9G 走 archiver archive-range；验收=内部空闲≥200G+尸体清零。
- W2 日志滚动永久化（S2，最急）：text_log level 调低+各 system log 表原生 TTL（trace_log/query_log 7 天、其余 14 天）+max_size 轮转→低峰重启 CH【M】→24h 复测膨胀<1G/天。
- W3 冷储主库落 F（S3）：E:\zephyr_cold_archive→F:\zephyr_cold\50_archive\by_project\zephyralpha\（robocopy+文件数/字节/5% hash 对账）→引用 7+1 处同 commit 改齐【M】→dashboard 探针绿→E 侧留观 30 天；G:\zephyr_cold 整体迁 F 同配方。
- W4 F↔G 调换（S4）：首查 /mnt/chbackup_local 身份→暂停 backup.ps1→ch_backup_disk.vhdx 526G/db_dumps/offrepo 大镜像 F→G 对账→backup_config offrepo targets 更新+新增 F 冷储→G 镜像条目→恢复 backup.ps1 实跑成功。
- W5 宿主清偿（S5+S6）：.runtime 45G 走 classify_workspace_wip 流程；models/ 14.3G 先 rg 引用再处置；tmp_db_dumps 轮转；D:\nonexistent 等小目录三层验证后清；研报对账（≥2026-10-18 才删 E 侧）；验收=D 剩余≥60G。
- W6 vhdx 压缩（S7，Owner 在场窗）：F 新鲜备份前置→停 VM→Optimize-VHD Full→起 VM→全链健康探针→季度巡检自动化登记；验收=vhdx≤450G+内部空闲维持≥150G。
- W7 终验红蓝：五盘对照表+引用残留 rg 扫描+搬运抽 hash 复测+备份恢复演练两次（G vhdx 分区+F 冷储 parquet 分区）→交付报告。
- 依赖约束（供你排序）：W1 需 dataqa R1 基线先落（作前后对照）；W2 时间最急（2-3 个月窗）；W3 引用改齐宜在 final3 working 清零后（热文件竞争小）；W4 须夜间无备份触发窗；W6 须 Owner 在场；研报删除挂 10-18 日历窗。

## §6 冲突与窗口（整合时必须遵守）
三队在飞期本线全线禁动：drop/CH 重启/跨盘搬运/清 .runtime 全部延后。具体撞点：dataqa 给全库每表量行数（中途删表毁其 R1）；tilib 明文 technical_indicator 宽表白天禁写入（archiver 扫 TI 撞它）；final3 挖矿狂查 CH（重启=打断）；三队高频 commit 触发 backup.ps1（搬运被打断）；三队 staging/claim/心跳全在 .runtime（清理=拆台）。唯一例外已执行：09-19 晚日志 TRUNCATE（秒级/无中断/保护性排雷）。

## §7 Owner 签字清单（6 项，请汇总进统一签字单）
①契约 INV-RET-002 修订（三步走 shadow→半自动→全自动，ruling_registry 同 commit，INFRA-STORE-002/LOG-OPS-001 同步）；②尸体表处置（推荐 export→verify→DROP）；③vhdx 压缩复决+150G 定案；④offsite 异地副本形式（月度拔盘 vs 小体量上云）；⑤db_dumps 版本化保留天数（建议 14 天）；⑥批次排期（收口后批 0-3 是否连做+shadow 起算日）。

## §8 纪律
禁 cron/sleep-loop（事件触发，backup 成功事件链为合法先例）；数据第一公理（删除前两份验证副本）；热文件 safe_write_text+CAS；.md 带 ttl frontmatter 字母开头 snake_case；提交唯一正门 git_commit.py --enqueue --files 白名单；避让清单=ruling_registry/gate_registry/capability_registry/tasks.yaml/AGENTS.md/docs/03_modules/**/data/strategy_intake/**/data/crypto/**/data_handler.py/akshare_provider.py/apply_market_tables_ddl.py 本体+三队目录只读；回执六要素+证据等级[亲验]/[转报]/[推断]；禁虚报，做不到如实写原因。
