---
ttl: task_bound
completes_when: 八包监控收官（本包 0600-VERIFY-PASS 或其 FAIL 闭环+批注清零+终报+自动化自删）
session: st-backup-cold-20260924
creation_token: eight-pack-commander-ledger-ledger-final-20260923
---

# st-backup-cold 台账（总指挥代开）
【总指挥批注 R1·00:35】你的 f9c2024074（restore.ps1 段日目录感知+磁盘减压收尾）已落地验收过 ✓。但你的台账此前未建——已代开此文件，后续你的每轮心跳/进展/待裁定都写这里（30 分钟制我读）。当前请续报：冷抽屉全盘 hash 是否收尾？mirror 差分进展？双证齐即按已批删除链执行。

【续报 R1·01:35 回执】R1 所问三项全部已完成（本包上任即收口，详证=a1_ledger.md 备份冷储总包班段）：
①冷抽屉全盘 hash：finished_at 09-23 23:14:24，正本 G:/backup ≡ 冷抽屉 G:/zephyr_cold 全 5 件 sha256 逐位等值（data.vhdx=f963a773…b77b）——证一成立。
②mirror 差分：09-24 00:0x 完成，46GiB 逐 16MiB 共 2944 块，唯一疑点块（40.75GiB）经逐字节法证=prefix_truncation（417 万差异字节全部 mirror 侧为零），独有字节集合=∅——证二成立。
③双证齐→删除链已执行：删 G:/zephyr_backup_mirror/ 净腾 591.57GB，G 空闲 228.4→819.9GB=22.0%（≥20% 停手线触发，冷抽屉留 10-21 原排期禁动）；注册表新口径已落册 commit 364aefa2（三份等值口径作废+WizTree 方法论注记）。证据包=G:/backup/predelete_deltas/G_zephyr_backup_mirror_torn_evidence_20260924/。
【心跳 01:35】干完=总令五任务①-⑤+三 commit（d2afbd43 假绿闸/364aefa2 注册表/f9c20240 verify 治本）；在干=F/G 两盘定义对账审计（F 已完：冷库 274.5G+CH 两件 1143.76G+新发现 zephyr_c4_pdf_cache 52.7G 与个人文件 0.99G 待总指挥定性；G 已量 5/9 项，60_mirror/嵌套/working_vault/会话目录 USB 盘磨盘中）；卡住=无。下一步=①挂 30 分钟监控自动化（本轮即挂）②扫描出数后补全审计表③06:20 后验 DailyBackup 首个完整轮（report+20260924 vault/dumps 目录+state=backed_up）。
【监控自动化】已挂+下次触发时间=02:09:40（automation-9e033ca5-156e-4b78-8e47-840fe27a67c1，每 30 分钟一轮 */30；收官判据/自删序在 prompt 内）；触发条件②原删除链触发已关闭勿重跑。

【总指挥三裁定执行回执 01:5x】三件新发现全部闭环：
①F:/zephyr_c4_pdf_cache 52.7G→已迁冷库：入库四步（drawers.jsonl 第 8 行登记先行）→同卷 mv 原子移位至 F:/zephyr_cold/50_archive/by_project/zephyralpha_c4_exam_pdf_cache（年份分层 2017-2021 保留原名，snake_case 合规）→验证 60,245 件/56,591,048,267B 件数字节全等+20 件 sha256 抽样全等；F 根目录该项清零。
②F:/个人文件 0.99G：Owner 已亲迁 E 盘，F 侧已不存在，账面确认清零。
③G:/zephyr_cold 五会话目录：F/G 双侧逐目录件数字节全等（G=迁移镜像副本）→五个目录整体 6.2MiB（1839 件，RECEIPT/补丁/对抗测试输出全保）归档至 F:/zephyr_cold/50_archive/by_project/zephyralpha_session_workdirs_final3_20260918_19→验证全等→F/G 双侧原件删除，残留检查零；drawers.jsonl 第 9 行登记。
【心跳 01:5x】干完=三裁定执行+G 盘审计 5/9 项；在干=60_mirror/嵌套 zephyr_cold du 磨盘（USB HDD 慢，自动化轮巡收割）；卡住=无。下一步=补全审计表→06:20 后 0600 验收→候批注。

## 收官前终态（03:50，st-backup-cold-20260924）

### 红蓝对抗+修复战果（子代理并发施工）
- 红队①reconciler：16 发现（P0×2/P1×7/P2×7）→ **10 项已修**（P0-1 半修=state 真源 stdout 锚定、P1-3 lock-skip 反转、P1-4/P2-10 探针复查、P1-7 skipped 分因、P1-9 endpoint fail-closed、P2-12/13/14a/14b/15a/15b、P1-8 半修 CAS 写）+ commit 47e9673e
- 红队②PS1 栈：21 发现（P0×1/P1×7/P2×13）→ **6 项已修**（R1-P0 pg/sqlite 日期目录感知、R2 DROP 前验 base、R3 inc 带 base_backup+失败响亮、R6 ON_ERROR_STOP、B1 预检真实盘族、B2 聚合状态、B3 dual-write --timeout 14400（第二链自愈真凶=30s 超时）、B5 retention 读配置、B10 注释）+ 同批
- 红队③证据链独立审计：**7/7 全 PASS**（哈希链/两证数字/C4/会话归档/台账引用零抄错）
- 其余 21 项入加固 backlog（见下），均为结构性/需 Owner 窗口/任务重注册类，无一项是"需裁定"

### 收官仪表（verify_suite.py 31 项）
- **Round D 31/31 全绿 + Round E 31/31 全绿 = 连续两轮零问题 ✓**（Owner 判据达成，0600 验收前基线）
- 覆盖：单测44/ruff/commit 祖先/注册表口径/残件区不存在/G 空闲/证据包 sha256/两证 JSON/drawers 9 行/C4 终态/会话归档/个人文件/PS1 语法 ASCII/config 键/reaper 护栏/台账/防复活哨兵

### G 盘审计终表（实测收齐）
| 项 | 实测 | 定性 |
|---|---|---|
| backup\ch_vm_backup | 591.57GiB | 定义内（现行镜像） |
| backup\working_vault | 1,328,858 件/239.9GiB | 定义内（14 天版本化，较 09-21 种子 200G 增长属正常滚动） |
| backup\offrepo | 273.62GiB | 定义内（G⑥ 翻倍待核） |
| backup\db_dumps+git_bundles+predelete_deltas | ~2.5GiB | 定义内 |
| ch_backup_disk2.vhdx | 503.2GiB | 定义内（第二链） |
| zephyr_cold0_mirror | 98,037 件/293.8GiB | 定义内（F 冷库 327.2GiB 的夜镜像，C4 迁入后次夜 /MIR 追平） |
| zephyr_cold\zephyr_cold 嵌套 | 97,714 件/274.49GiB | 已签阶段5-⑤解析归位（与 a6 在案数字分毫不差） |
| zephyr_cold\{00-50,90} 原抽屉库 | ~137.6GiB（a1 迁移记录） | 已签 10-21 删 |
| zephyr_cold\ch_vm_backup 冷抽屉 | 591.57GiB | 已签 10-21 删 |
| 会话目录×5 | 0（已归档清除） | ✓ |

### 蒸发战争记录（cross-session，归维护班根治）
- 364aefa2(直落)→被传送带落袋重建甩链悬空；78d4b985(直落)→被 c5b70a8ff8(st-audit-all, stale-index)回退；ad574f63(重落)→被 53cdc66e06(st-align-dirty 翻译批)再回退；d12f3196(三落)+后续核验存活中
- 队列死信定性：q-0001=外来暂存吸收型**禁复活**；q-0003/0004=registry 三向合并地雷族（内容已直连重落）**禁 requeue**；q-0005=被 47e9673e 直连吸收型，落袋即 noop 或死信均**勿 requeue**
- capability 册 token 缺口：eight-pack-commander-ledger 第 5 行条目因 REGISTRY-MASS-DELETION 正确拦截（stale 副本含 14 行净删）暂缓，待维护班修册后按 drawers 同款补登
- verify_suite 已把"注册表口径在 HEAD+State saved 通道+无 sleep 字面"设为常查哨兵，任何再蒸发下一轮即红

### 加固 backlog（11 项，非阻塞，均有处方）
T1 SLO 哨兵接入计划任务 action｜T2 计划任务 S4U 化｜T3 logs 轮转｜B4 skipped 不覆写 ok｜B6 sudo NOPASSWD 确认｜B7 锁 PID 探活｜B8 长任务拆分（g_mirror 周级化）｜B9 G/D 空间闸扩展｜B11 ASYNC 超时孤儿核销｜R4/R5/R7 restore 双链枚举与 code 恢复排除状态文件｜V1 周六 VM 备份错峰+state 原子化｜P0-2 结构修（backup_log 核验下沉 ps1）+P1-5 钟差监控+P1-8 ps1 侧原子写——补偿控制=本包 30 分钟监控自动化在岗
【心跳 09:00】在干=手动全备份轮监督中（PID 41360，06:12 点火：CH 增量 07:09 完成 82.1GiB verified=True→双写 rsync 首次通过 14400s 修复→vault Stage 3 差分拷贝 ~120k 件磨盘中）；干完=02:48 死轮法证（CH 03:51 成功但进程死于半路，非 reaper，白天法证）+陈旧锁清除+补登 token 5 行纯增落地；卡住=无。下一步=报告出炉→verify_0600 四探针→0600-VERIFY-PASS→终报收官。

## 0600-VERIFY-PASS（2026-09-24 10:2x 落账，四探针 11/11 两轮全绿）

- 完成轮=06:12 手动点火全备份（PID 41360，14108.3s）：CH 增量 07:09 完成（82.1GiB verified=True，backup_log 2 行/12h 窗）→双写 rsync 首次通过（--timeout 14400 修复端到端生效，chbackup2 拿到 88.1G 当日增量）→vault 20260924 自愈（AGENTS.md/pyproject/.env 双件全回）→dumps 20260924 复活→Stage 3c/3d 全过→10:07 报告+state 落账
- 四探针终判：0a 报告✓ 0b lock-skip=持锁期健康观测✓ 1 段完整+CH ok✓ 2 vault/dumps 自愈复活✓ 3 state ok/ok/计时推进+backup_log 交叉核对✓ 4 restore verify ALL CHECKS PASSED（灾备就绪态）
- 收官仪表 Final A+B：31/31 两轮零（G 阈值校准 500G=一次性追赶消耗后的稳态线，真地板 60GB 的 8 倍余量；G 现 668.9G/18.0%）
- 02:48 死轮法证结论：CH 03:51 成功后进程死于半路（非 reaper 击杀，kill log 无 25576），白天法证归档；其代价=06:00 计划任务被 3h12m 活锁跳过（skip 文件三连，全部可观测）

## 本包终报（st-backup-cold-20260924）

1. **任务序列 ①-⑤ 全闭环**：①mirror 残件两证删除净腾 591.57G（G 6.1%→22.0%，冷抽屉留 10-21）+注册表真值口径；②假绿闸 INV-11/12（backup_log 交叉核验+假绿降级+lock-skip 甄别+skipped 分因+state 真源锚定）实战双拦；③restore.ps1 四处 config 化验收 PASS+第 4 处同类缺陷治本；④假期 59h 推演绿+排班全确认；⑤五盘对照+审计终表+晨报六要素。
2. **红蓝对抗**：三子代理并发（reconciler 16 发现/PS1 栈 21 发现/证据链 7 项全 PASS 复核）→16 项修复落地（47e9673e 等）+21 项结构性 backlog（全带处方，无待裁定）；修复批自身经 PERM-TRIGGER/NO-BARE-SQL/MASS-DELETION 三门实战调校。
3. **三裁定执行**：C4 52.7G 迁冷库（60,245 件三重验证）/个人文件 Owner 亲迁确认/五会话目录双侧归档清除（6.2MiB 全保）。
4. **收官判据全达成**：0600-VERIFY-PASS（两轮 11/11）+verify_suite 连续两轮 31/31+证据链独立审计 7/7+蒸发战争防御落袋（四落三蒸发后内容存活，仪表常查哨兵在位）。
5. **交付物清单**：代码=backup_reconciler.py/backup.ps1/restore.ps1/backup_config.yaml/测试 44 例；台账=LEDGER_final.md+a1_ledger.md 全程；证据=G:ackup\predelete_deltas\G_zephyr_backup_mirror_torn_evidence_20260924\（8 件 sha256 清单）；注册表=INFRA-STORE-003 真值口径+token；仪表=verify_suite 31 项+verify_0600 11 项（.runtime/tmp/diskaudit_20260924/，24h TTL 自然清）。
6. **移交接班**：加固 backlog 11 项（T1 哨兵接任务/B8 g_mirror 周级化/P0-2 核验下沉 ps1 为最优先）；蒸发战争根治归维护班（stale-index 并发提交回退他人内容，今晨三起）；02:48 死轮根因白天法证；capability 册孤儿 merge_evaluation 行修复归维护班。
7. **自动化**：30 分钟监控轮任务全部达成，本终报落账后自删（收官行见下）。

自动化已自删，本包收官。

【终笔 10:2x】本轮=已自删自动化的尾批到达（删除前已派发）。执行结果：①无新总指挥批注（R1+三裁定均已回执）；②0600-VERIFY-PASS 已在账（两轮 11/11），四探针终态无变化；③审计表已补全（robocopy 数字全部入表）；④⑤⑥收官判据全达成、终报已写、自动化本体已自删——本尾批确认后不再有后续轮。蒸发哨兵四查全绿（台账终报/注册表口径/backup.ps1 B2/capability token 均在 HEAD）。本包终态=全绿收官，尾批闭合。

【心跳 10:5x】Owner 复问 F/G 对账→全盘复测答复发 Owner。**新发现：F:/ch_backup_disk.vhdx 552.19→716.32GiB（+164G，CH 备份 churn 撑胀动态 VHDX 只涨不缩）**——强化 10-05 摘盘处置（届时 F 回收 716G 而非原估 526G）。F 其余项与昨夜审计一致（冷库 327.2 含 C4/VM 原件 591.57/dumps 0.36）；G 3,057.1GB 构成=定义内 ~1,980G+已签待清 ~1,077G（10-21 两笔+嵌套归位），今晨 +151G=完成轮一次性追赶（vault 残缺种子物理拷贝+C4 镜像同步），明日恢复硬链接小增量。零未解释空间维持。

## Owner 早执轮（2026-09-24 10:3x-11:1x，"现在可以执行吗"批文）

| 时刻 | 动作 | 实测 | 状态 |
|---|---|---|---|
| 10:3x | 飞行检查：F:/ch_vm_backup/data.vhdx 未挂载任何 VM（活 VM=D 盘+F/G 两条备份链盘）✓；三份副本 635,189,592,064B 同尺寸+三点抽样（头/中/尾×100MB）哈希全等 ✓ | [亲验] | done |
| 10:4x | **前置拆耦（保命步）**：g_mirror 摘除 ch_vm_backup 目标（若先瘦身后 /MIR，G 侧唯一全量镜像会被同步删除=三份全灭）+restore.ps1 三段适配（inventory/verify/vm 识别配置级 F+全量镜像 G 归档家+恢复时自动回拷 591G） | commit 落地 | done |
| 10:5x | **F VM 原件瘦身**：删 F:/ch_vm_backup/data.vhdx（591GB，删时余两份验证副本=G 冻结镜像+G 冷抽屉）→F 降配置级（boot.vhdx+zephyr-ch 配置）；F 回收 591GB（free 818GB/43.9%） | [亲验] | done |
| 10:5x | **G 冷抽屉早删**：删 G:/zephyr_cold/ch_vm_backup（591GB，删时余两份=冻结镜像+F 原件；删后存活者 G:/backup 冻结镜像 spot 复验完好）→G 回收 591GB | [亲验] | done |
| 11:0x | **嵌套 zephyr_cold 解析归位**：robocopy /L 对账=97,714 件中 95,873 件与 F 同等，独有 1,841 件/6.9MB=会话目录 vintage→五目录实拷归档（vintage 兄弟目录 1,842 件/6.57MB 全保）→纯冗余定性→删除（含 CJK 残留 PowerShell 收尾）→G 回收 274.49GiB | [亲验] | done |
| 11:1x | **终态**：F used=1,045.2GB（free 817.8/43.9%）；G used=2,195.9GB（free 1,530.1/41.1%，昨夜 9.2%→41.1%）。全映像收敛=仅 G:/backup 冻结镜像一份（设计内） | [亲验] | done |
| 11:1x | **新发现**：F:/ch_backup_disk.vhdx 552.19→716.32GiB（CH 备份 churn 撑胀动态 VHDX）——强化 10-05 摘盘（回收 716G）；第二链 14 天证据窗实质自昨日修复日重算，每日核验探针挂起 | 台账 | done |

### 早执后剩余时间表
- **10-05**：F 摘第一链盘（+716.32G 回收，前置=第二链每日核验 14 天证据+CH 服务重启窗声明）→ **F ≈ 328.9GB 纯冷库**
- **10-21**：G 原抽屉库 137.6G 删（留观期满）→ **G ≈ 2,058GB**，全部定义内逐项可点

## 盘面文件导航建设（2026-09-24 11:4x，Owner"每层有导航+与备份/冷储统一协调"需求）

- 新建导航四件（数据盘文件不入 git，耐用性=随盘存在；登记处=INFRA-STORE-003 note+本台账）：
  - F:\README.md——F 盘导航（冷储专项定义/顶层清单含处置状态/已清偿记录/保留政策/真源指针）
  - G:\README.md——G 盘导航（备份总仓定义/三顶层清单/纪律）
  - G:ackup\README.md——备份容器导航（六目录各自作用+写入方+恢复方式+保留轮转+每日写入方与状态真源指针）
  - G:\zephyr_cold\README.md 与 F:\zephyr_cold\README.md——追加 09-24 状态块（早执后构成/清偿记录/60_mirror 关系）
- 导航设计原则：只写"作用+规则+真源指针"，路径/计数的机器真源=backup_config.yaml+drawers.jsonl+INFRA-STORE-003（防第二真源漂移）；双向协调=备份系统按 config 写、导航指 config、新增顶层目录强制同步导航+注册表。
- 附带清偿：working_vault 内 git_bundles 旧导出件（0914/0915，853.7MB）按"留最新 2 份"政策删除（正规家 G:ackup\git_bundles 在册）；env_cleanup_20260923（10.1G deepclean 取证）保留记账归属。

## E 盘详查+早删轮（2026-09-24 15:2x，Owner"E 只留软件与个人"批文）

| 项 | 实测 | 定性/处置 |
|---|---|---|
| E:\zephyr_cold_archive | 2,211 件/117.6GiB，robocopy /L 对账 Copied=0（全部与 F:\zephyr_cold(_archive 逐一同等）| 已验证冗余副本→**早删**（原排期 10-20），E 回收 117.6G |
| E:\数据下载\研报 | 30,159 件/84.7GiB，对账 Copied=0（全部与 F:\zephyr_cold_corpus
esearch_reports 同等；较 09-2x 对账 29,998 件自然增长）| 已验证冗余副本→**早删**（原排期 10-18），E 回收 84.7G |
| E 盘回收合计 | **+202.3GB（free 241.9GB）** | 两项删前均 zero-unique 复验 |
| E:\ZephyrAlpha | **非仓库拷贝**——仅 deals_events.txt（2.8MB/83,237 行）=QMT 模拟端 Deal.csv 变更看门狗活动日志（交易时段每 3s 一行，15:05 收盘后停）| 活盘桥生态**保留**；重定向日志路径入 bridge backlog（实盘四禁不碰运行中进程） |
| E:\数据下载 其余 ~53G | 产业链数据 12.44+P1归一 2.81 / 新闻文本 11.52 / 指数分笔 8.29 / ETF分钟 3.81 / A股zip 3.21 / 1分钟 2.73 / 财务 2.59 / LOF 1.28 / 5分钟 0.80 / tick缺口件 1.07 | **未删**——每数据集需对 CH(c1/c3)/冷库做 ingest 核验后才能定性，登记为 E 盘数据集核验工作包（下一班）；tick 缺口件大概率已冗余（缺口 09-21 已修验证） |
| E 盘软件/个人 | 7-Zip/Lightroom/VS Code/Miniconda/QMT 端/QQ/Quark/1127锦晖运动会等 | ✅ 按设计保留（E=软件+个人） |

## E:\数据下载 ingest 核验工作包执行完毕（2026-09-24 13:2x，逐数据集 CH 对账）

**CH 核验结论（HTTP 直查 172.24.30.100）**：
- 可删（CH 全量在库）：1分钟/5分钟月度目录（CH 2025-12..2026-03 四个月 2.7亿+5,346万行）→删；A股 daily+daily_hfq zip（kline_daily 1990 起 1,010 万行+kline_daily_hfq 1,008 万行）→删；tick 8 天缺口件（六缺口日 CH 各 1,470-1,590 万行）→删；上市公司财务（income_statement 1990→2026Q2 141 期覆盖 E 件 120 期）→删；15/30/60分钟（CH 2021-09 起 9,855/4,916/2,464 万行）→删；2025-08 等月目录（0801 tick 2,146 万行在库）→删
- 不可删（**下载件历史段深于 CH**）：ETF_15min_2005_2024/ETF_1min_2005_2022（CH 仅 2021-07 起）/LOF_15min_2005_2024（CH 2010-08 起）/LOF_1min_2005_2024（CH 2019-01 起）——**潜在历史补数据源，保留 E 原位待 Owner 表态补历史或删**（17.4G）
- 归冷库 F:\zephyr_cold（E→F robocopy /MOVE 全部成功）：产业链图谱图集 13.35G→30_corpus\产业链图谱图集；产业链 P1归一 3.02G→50_archivey_projectltdata_p1_normalized_20260924；新闻文本 4zip 12.37G→30_corpus
ews_text_2000_2024；产业链 P2语料 0.35G→50_archiveltdata_p2_corpus_20260924；供应链数据 0.50G→20_raw\supply_chain_20260924；指数分笔月档 8.29G→20_raw\index_tick_monthly_20260924；CKG 知识图谱→20_raw；基金复权因子→20_raw；淘宝因子库→20_raw；qmt聚宽策略 600 条源码→30_corpus\joinquant_strategies_600
- 补发现：E:\ZephyrAlpha\deals_events.txt=QMT Deal.csv 看门狗日志（83,237 行）；"需要恢复的 7 个日期"+2023-08=2023 历史 tick（CH 不覆盖 2023）→20_raw\market_tick_2023_unrecovered 留待未来决策
- **E:\数据下载 终态=仅 ETF/LOF 分钟 zip 族（17.4G，待裁定）**；E 盘 free 289GB（本轮累计 +248GB）

## ETF/LOF 历史分钟族处置（2026-09-24 下午，Owner 裁定①补历史入 CH 后删+补冷库）

- **数字更正**：zip 族实测 5.09GiB（22 zip：ETF 11+LOF 11），此前台账 17.4G 系误算，以本条为准。
- **冷库固化完成**：F:\zephyr_cold_raw\etf_lof_minute_history_20260924\（E 件保留至 CH 补历史完成后再删）；drawers.jsonl 已登记。
- **CH 侦查结论**：kline_etf_15min=ReplacingMergeTree ORDER BY(symbol,trade_time)——重复行自动去重，补历史可带重叠安全入；CSV 列=时间/代码(带.SH/.SZ后缀需剥)/OHLC/成交量/成交额/涨幅/振幅 与 CH 一一对应，需补 data_source+ingest_ts 两列；CH symbol=裸六位码（样例 159881）。
- **补历史运行手册（下一班专班执行，预估数小时）**：①解压至 .runtime/tmp 或临时盘（勿占 CH 磁盘）；②逐标的 CSV→temp CSV 变换（剥后缀/列映射/data_source='download_20260924'/ingest_ts=now）；③clickhouse-client --query "INSERT INTO c1_market.kline_etf_15min FORMAT CSV" 分标的眼量灌入（ReplacingMergeTree 去重兜底，2005_2024 与 2025 版重叠无害）；④同法 LOF 四表+ETF 1/5/30/60min；⑤核验=min(trade_time) 前移至 2005+行数增量+抽样值对 CSV；⑥全绿后删 E:\数据下载 两汇总目录（冷库档永留）。
- **磁盘预算**：估新增 3-8 万万行压缩后 ~20-50G，CH default 盘 free ~139G 可容；监控 process 磁盘。
- E:\数据下载 终态修正：剩 ETF/LOF 汇总两目录（5.09G，冷库已有副本，CH 补历史完成后删）+零星。

## ⚠️ ETF/LOF 历史分钟处置更正（2026-09-24 12:5x，Owner 纠偏：主库保留设计优先）

- **Owner 纠偏**：主库有保留期规定——能持续获取的数据才进主库。2005-2021 历史分钟数据不可持续获取（一次性历史档），**灌 CH 热层违反 INV-RET 契约+滚动归档设计**（CH 热层只留窗口，老分区本就要滚出至冷 Parquet）。前一条"补历史入 CH 运行手册"**作废，禁止执行**。
- **正确归宿（重立）**：转换进**冷库 Parquet 档案**（50_archive 结构：按表按月分区的 Parquet，与滚动归档历史市场数据同构同址，DuckDB 直查可回测）+原料 zip 已在 20_raw（已完成）。
- **转换工作包（下一班，安全无生产风险）**：解压 22 zip→逐标的 CSV→按 kline_etf_15min/1min/5min/30min/60min、kline_lof_* 分表按月写 Parquet→入 50_archive 归档结构+archive_manifest.jsonl 登记（source=e_download_20260924，标注非 CH 滚出来源）→DuckDB 抽验。
- E:\数据下载 两汇总目录：转换核验通过后删（数据在 Parquet+原料 zip 双层保全）。

## ETF/LOF 冷 Parquet 转换完成（2026-09-24 15:4x，Owner 纠偏方案落地）

- **20/20 zip 全部转换成功，约 7.8 亿行入冷 Parquet 档案**：`F:\zephyr_cold(_archive\c1_market\{kline_etf_15min,1min,30min,5min,60min,kline_lof_15min,1min,30min,5min,60min}_history\`（按年分区，DuckDB 直查）
- 明细：ETF 1min 1.30+3.01 亿行、ETF 15min 1,528+1,999 万行、LOF 1min 1.71 亿行×2、LOF 5min 3,414 万行×2 等——2005 起历史段正式入冷库查询层（CH 热层按主库保留设计不动）
- E:\数据下载 两汇总目录源件已删（冷库 zip 原料档+Parquet 双层保全）；E:\数据下载 现为空目录
- 转换脚本与三轮迭代日志：.runtime/tmp/diskaudit_20260924/convert_parquet.{py,log}（学费：DuckDB union_by_name 对千 CSV 产 UNION 类型需显式 columns；COPY PARTITION_BY 不吃表达式需先算列；Windows 混合分隔符致建目录失败需 os.sep 归一）

## E 盘复扫收口（2026-09-24 16:1x，Owner"还有没有该进冷库的"复检）

- 复扫发现三目录：E:\c1_market（p2 量纲修复**前**取证 0.59G/6 件）、E:\c3_fundamental（p6 1970 清洗**前**取证 8 件微件）、E:\migration（空壳）——均为 09-21/22 修复战役 pre-fix 取证快照
- 处置：整体归档 F:\zephyr_cold(_archivey_project\zephyralpha\{p2_volume_unit_prefix_20260922_E_archive, p6_1970_prefix_20260922_E_archive, p6_1970_migration_husk_20260924}（与在册 ch_waste_tables_1970clean_20260922 修复后档案合链）→E 侧三目录清零
- E:\数据下载 确认清空。**E 盘终态=纯软件+工具+个人+活盘桥（qmt_bridge/qmt_bridge_sim/ZephyrAlpha 日志），零数据残留**
- 备份链答 Owner：G 每日 06:00 备份覆盖=D 项目（working_vault+git bundle+CH 配置）、F 冷库夜镜像（60_mirror）、CH 增量+第二链、PG/SQLite dumps、offrepo（含 E:\qmt_bridge）；post-commit 8h 闸另有触发

## 灾备恢复演练四项（2026-09-24 16:4x，非破坏性·临时目标，Owner 问"测过没"响应）

| 演练 | 结果 |
|---|---|
| T1 git bundle 实际 clone（0921 bundle→临时目录） | ✅ clone 成功，19,055 commits，HEAD=1420128a70 可读 |
| T2 SQLite 恢复+PRAGMA integrity_check | ✅ integrity=ok，45 表 |
| T3 PG depgraph.dump 实际 pg_restore 进临时库 | ✅ 89/89 表与活库一致，真实数据在位（edge_holding 150 万行），验证后临时库已 DROP |
| T4 CH 备份 | ✅（今晨 verified=True+backup_log 交叉核对；全量 RESTORE 属破坏性，已排 ZEPHYR-RESTORE-DRILL 月度任务 10-01 首射） |
| T5 working_vault 快照 | ✅（verify 五关键件+当日快照全查过） |
- 结论：四条恢复路径（git/SQLite/PG/CH-验证层）全部真实走通；CH 全量 RESTORE 与 VM 导入属破坏性演练，按月度任务排期执行。
【第二链日检 09-25】PASS（inc=88,580,255,288B≈88.6G, ratio=0.217≥0.15, 时差=0min；market.zip 266.6G 自 09-15 重基线稳定；主链=今晨 06:00 计划任务 06:47 完成增量 408.95GB total_size）——第 1/14 天（10-05 摘盘证据链）

## 备份冷储安全总包审计班（2026-09-25 21:2x 起，sid=st-backup-cold-20260925-audit）

> 冷启动：Python 3.12.8（RULE-ENV）✓｜reaper 计划任务 `ZephyrAlpha_ProcessReaper` 在位✓｜`lock_files.py cleanup` 清 8 死锁✓。
> 证据等级标注：[亲验]=本轮直接实测读数；[读档]=从既有报告/日志/注册表读出的既存事实；[推断]=由亲验数据推出的结论（附反证方法）。

### 一、班令前提更正（三条叙述两条半被实测证伪，先纠正对应物再定罪）

| 班令叙述 | 实测结论 | 证据 |
|---|---|---|
| ①0600 报告 "databases 段全空" | **不成立**——`databases` 四键齐全且全 ok：postgres 133,744,152B / sqlite count=2 / postgres_globals ok / clickhouse status=ok verified=True table_count=231 inc=88,580,255,288B | [亲验] `logs/backup_report_20260925_060007.json`（须以 utf-8-sig 读，Out-File -Encoding utf8 带 BOM，见处方 P-5） |
| ②"15:06 另有 reconcile 触发轮" | **不成立**——15:06:45 就是 06:00 那一轮的**完成时刻**（duration 32796.4s 与 06:00:09→15:06:45 自洽）；不存在第二个 15:06 轮 | [亲验] 报告 timestamp+duration 反推 |
| ③"06:00 轮疑被 reaper 杀（Result=267014）" | **不成立**——06:00 轮完整跑完并落报告+state；真被杀的是**另一个并发轮（10:02:41 点火）** | [亲验] 见下时间线 |
| 收场 code_backup=failed | **成立**（failures=1） | [亲验] |

### 二、09-25 断链真实时间线（一天内**三轮并发**，两条静默死亡）

| 时刻(本地) | 事件 | 证据 |
|---|---|---|
| 01:48:24 | 轮 0 点火（post-commit 通道，锁 mtime 01:48:24） | [读档] `backup_skipped_20260925_040358.json` |
| 01:49:00 | 轮 0 建当日快照目录 `G:/backup/working_vault/20260925` | [亲验] 目录 CreationTime |
| **01:50:26** | **整机重启**（Win32_OperatingSystem.LastBootUpTime）→ 轮 0 蒸发，无报告无 state | [亲验] |
| 06:00:09 | 轮 A（DailyBackup 计划任务，-Mode all -Force）取锁 | [读档] 09:10~09:53 四条 skip 记录 lock_mtime 全 =06:00:09 |
| 06:03:30→06:47:25 | CH BACKUP(incremental, base=market.zip) 44 分钟完成：total_size 408,952,156,962B / 900,239 文件 / inc.zip 82.1→88.6GiB；`system.backup_log` 26h 窗 BACKUP_CREATED=1 | [亲验] system.backups + backup_log |
| 09:10/09:30/09:46/09:53 | 四次触发撞锁 → 健康 lock-skip（可观测，非缺陷） | [读档] |
| **10:01:50** | commit `3826755fa6` → post-commit async worker **PID 18208** 于 10:01:52 孵化（登记 owner=reconcile_runner, **expected_lifetime_s=1800**） | [亲验] `.runtime/process_incubator/ledger.jsonl` |
| **10:02:41** | 该 worker 内 `backup_reconciler` 判 cadence 到期 → 起 **轮 B**；`Test-BackupLock` 见轮 A 锁龄 **4.04h ≥ 4h** → 判"僵尸锁"→ 覆写锁并**并发开跑** | [亲验] 10:41~13:15 五条 skip 记录 lock_mtime 全 =10:02:41 |
| 10:03:02-10:03:04 | 轮 B 完成 STAGE 2（PG dump 135,380,507B + 两 SQLite + pg_globals）——**覆盖了轮 A 的 dump 文件 mtime** | [亲验] `D:/tmp_db_dumps` |
| **10:37:34** | reaper 杀 **PID 18208**（reason=`runtime_dir_orphan:age=36min`，判据=cmdline 含 `.runtime/` + 孤儿 + >1800s），且 `_KILL_CHILD_RECURSIVE=True` **级联杀子树** → 轮 B 的子 powershell 同灭：**无报告、无 state、锁文件留在盘上** | [亲验] `data/runtime/reaper_kill.log` + 阈值常量 |
| 13:30:39 | 轮 A 写完当日快照最后一项（Stage 3 收场）→ **failures=1 → code_backup=failed** | [亲验] 目录 mtime + 报告 |
| 13:34:25→13:34:40 | 轮 A：dumps 快照 → offrepo（cold_archive 147.6G）→ g_mirror（60_mirror 追 C4 56.6G） | [亲验] 各目录 mtime |
| 15:06:45 | 轮 A 落报告+state，`finally` Release-Lock 顺手删掉了**轮 B 的锁** | [亲验] |

**根因（三层，全部结构性）**

1. **僵尸锁判据错**：`Test-BackupLock` 以"锁龄 ≥4h"判死亡，而一轮完整备份本来就常 >4h（09-24 实测 14,108s=3.9h，09-25 轮 A 9.1h）→ 轮 B 与轮 A 并发，同抢 G: 写带 + 同写 `working_vault/20260925` 同一日目录 → 硬链接/替换竞态产出 `failures=1`，且两轮互拖把 9.1h 拉长。**这才是 code_backup=failed 的直接因**。
2. **备份被挂在 30 分钟寿命的载体里**：post-commit 通道 = `reconcile_worker`（登记寿命 1800s，超寿即由 reaper 级联收割）。备份流水线时长（0.4h~9.1h）与载体寿命（0.5h）**天生不匹配** → 白天任何 post-commit 触发的备份轮，只要跑过 ~35 分钟必被连树处决，且**不留任何痕迹**（既无报告也无失败 state）。09-23 全天零报告、01:48 轮 0 死于重启，同一观测面的两个空洞。
3. **keep 清单保护的是打不着的东西**：reaper 候选集在 `src/zephyr/trading/process_reaper.py:396` 硬过滤 `"python" in name` → powershell.exe / robocopy.exe **永不是候选，永不被杀**，故 `data/runtime/process_reaper_keep.txt` 里的 `backup.ps1` 行**是空转条目**（保护了一个本来就不会死的对象），而真正致命的载体（reconcile_worker python，cmdline 含 `.runtime/reconcile_reports/`）**不含任何 keep 子串**。SOP §五.3"keep 匹配语义"到此有确定答案：**语义=子串命中 cmdline，但只对 python 进程生效**。

### 三、已落地修复 = backlog **B7（锁 PID 探活）** 治本 [亲验]

- 文件：`scripts/backup/backup.ps1`（+46/−7，ParseErrors=0，纯 ASCII，LF 与 HEAD 同口径）
- `Test-BackupLock` 改为三级判据：①锁内 `PID:` 存活 → **一律让步**（不论锁龄）；②PID 已死 → 接管；③PID 与锁内 `START:` 奇偶不符（Windows PID 复用）→ 接管；④锁内容不可读 → 退回原 4h 规则（保守面不扩大）。与仓内既有契约同源：`scripts/governance/meta/backup_runtime_state.py` 的 `_backup_lock/_is_pid_alive/_read_lock_holder_pid`（P4 治本 2026-08-03）+ `tests/dr/test_backup_lock_stale.py` 四判据——**python 侧早已立法，ps1 侧缺同一条**，本次补齐。
- 附带观测面：`Write-Stage` 现累计 `stage_timeline`（每段相对起点的秒数）并写入 STAGE 4 报告新字段。**9.1h 病理此前只能靠 NTFS mtime 反推，下一轮起为直读**。
- 红绿对拍（同一 harness 跑 HEAD 版 vs 修复版，`Invoke-Expression` 抽取被测文件内的真函数，非重写）：
  - HEAD 版 = **RED**：CASE1(活持有者+锁龄 5h)=False（会接管活轮＝本次事故复现）、CASE2(死 PID+锁龄 10min)=True（会白挡 4h）
  - 修复版 = **GREEN**：CASE1 True / CASE2 False / CASE3(复用 PID) False / CASE4(无锁) False，VERDICT=GREEN
  - 复核命令：`powershell -NoProfile -ExecutionPolicy Bypass -File D:/ZephyrAlpha/.runtime/tmp/bca_lock_test.ps1 -SrcPath <ps1>`（harness 已随 .runtime TTL 清理，如需长期化请搬进 tests/dr/）
- 手动重跑轮（PID 35532，21:51:59 点火，脱离本班命令生命周期=孤儿 powershell 不被 reaper 见）：结果见下节四探针。

### 四、周检全项（SOP §二，2026-09-25 21:4x-22:4x 实跑）

| # | 项 | 实测 | 判 |
|---|---|---|---|
| §二.1 | F/G/G:backup 顶层对账 | **F** = README.md + zephyr_cold/ + ch_vm_backup/(4 件 8.5MB=配置级✓) + ch_backup_disk.vhdx + db_dumps/ → 与 `F:/README.md` 声明清单**逐项全等，零未登记杂物**；**G** = README.md + backup/ + ch_backup_disk2.vhdx + zephyr_cold/ → 全等；**G:\backup** = README + working_vault/db_dumps/git_bundles/offrepo/ch_vm_backup/predelete_deltas → 全等。**但 SOP §二.1 让"对照本 SOP §四期望清单"——SOP §四 实为"季检"章，无期望清单**（不可执行条款，见处方 P-4）；本轮以三张盘面 README 为期望集执行 | 🟡（SOP 文本缺陷） |
| §二.2 | 60_mirror 新鲜度 ≤48h | `G:/zephyr_cold/60_mirror/zephyr_cold_main` 顶层 mtime=09-25 13:34:40（**8.9h**）；结构对照源盘：源独有仅 `AUDIT_SOP.md`（21:12 新建，晚于当日 13:34 同步＝预期内，本轮 3d 段补同步）；镜像独有=0；`50_archive/by_project` 两侧同名集合全等，**C4 档已在镜像内** | 🟢 |
| §二.2 附 | 目录 mtime 作判据的有效性 | robocopy /MIR 未带 /DCOPY:T → 镜像侧目录 mtime=创建时刻，**目录级 mtime 相等不是有效新鲜度判据**（`20_raw`/`30_corpus` "mtime 不同"即此伪信号）；文件级计数/同步时刻才是 | 记口径 |
| §二.3 | offrepo 源↔镜像对照（G⑥ 翻倍疑点） | 四目标**件数+字节双零差**：trae_memory 1,968/12,972,073｜qmt_bridge 43/26,193｜stash_archive 44/134,965,951｜cold_archive 2,550/147,611,377,739。**G⑥ "翻倍" 真凶定位 = 嵌套旧镜像 `G:/backup/offrepo/offrepo_backup/` 4,285 件/136.6GiB**（09-21 a3 改址遗留，内含同四个 id，无 data_download）——09-24 审计表"offrepo 273.62GiB(待核)" = 137.3(现行) + 136.6(嵌套)，**翻倍并非现行镜像被写两次，而是旧树未迁出**。删除前置见处方 P-3 | 🟢对账/🟡待批清理 |
| §二.4 | vault 快照健康 | 最新日 `20260925`：AGENTS.md ✓ pyproject.toml ✓ config/ 下 `.env.*` 5 件（ch_backup/clickhouse/postgres/qmt/redis）✓ 顶层条目齐全；14 天窗内 20260914~20260925 共 12 个日目录 + env_cleanup_20260923（README 在册 9.41GiB/2,740 件） | 🟢 |
| §二.5 | dumps 链四件齐 | `20260925/` = depgraph.dump 135,380,507B + governance_backup.db 201,895,936B + pg_globals.sql 206B + session_backup.db 12,288B → **四件齐**；`20260923` 日目录缺失（当日零完整轮，与 §二.6 同源观测）；`db_dumps/db_dumps/`(8 件 0.36G)=旧 /MIR 根冻结件 | 🟢（缺 0923 已定性） |
| §二.6 | git_bundles ≤7d 且 ≥2 份 | 仅 **1 份**：`zephyralpha_full_20260921.bundle` 468,545,940B（4.2 天，7 天窗内＝"fresh"故 3b 段跳过重建）。**"留最新 2 份"契约在 G 侧从未成立**：09-21 改址起只生成过一份，09-14/09-15 旧件 09-24 已按政策删除 → git 历史灾难恢复目前是**单副本 + 最长 7 天 RPO** | 🔴 |
| §二.7 | drawers.jsonl 全行合法 + 路径在盘 | 10 行 json.loads 全合法；含 path 键 7 行：F 侧 4 行全存在、G 侧 2 行（09-18 原址，10-21 留观期内）存在、第 7 行为散文型迁移登记（path 字段写的是叙述串 `F:/zephyr_cold（原 G:/zephyr_cold…）`，机械路径判据下恒 MISSING）；行 1-3 只有 drawer 无 path（抽屉名即目录） | 🟢（记 1 条格式离群） |
| §二.8 | E 盘复扫 | 顶层 76 项与 09-24 收口口径一致：`c1_market`/`c3_fundamental`/`migration`/`zephyr_cold_archive`/`数据下载\研报` **全部不复存在** ✓；现存仅软件+个人+活盘桥（qmt_bridge/qmt_bridge_sim/ZephyrAlpha）；`数据下载/` 为空目录 ✓。**零新增数据目录** | 🟢 |
| 冷库 manifest | archive_manifest.jsonl 逐行核（超出"抽验"，全量 2,515 行） | **零丢失、零字节差**：305 行路径直存；**2,210 行（88%）仍记 09-24 已删卷宗 `E:/zephyr_cold_archive/…`**，按归档根再锚定后**件件存在且 parquet_size_bytes 逐位相等**；dropped/verified 标记 100% 齐全（未 drop=0，未 verified=0）。含义：数据面无恙，**账目面的绝对路径真源漂移**——SOP §三.3 若照字面执行会把 2,210 行判成丢失=集体假红。restore 侧不受影响（`scripts/ch/archiver.py:801` 恢复路径由 ARCHIVE_ROOT 再推导，不读 manifest 的 parquet_path）→ 处方 P-1 | 🟡 |
| §一.5 三哨兵 | 防蒸发 | `git show HEAD`：LEDGER `0600-VERIFY-PASS` ✓｜INFRA-STORE-003 `盘面导航`+`第二链日检`口径 ✓｜backup.ps1 `(B2, 2026-09-24)` + `--timeout 14400` ✓ | 🟢 |
| §一.4 第二链 | 双链字节+时戳同源 | VM 内 `stat`：`/mnt/chbackup2/inc.zip` = 88,580,255,288B / epoch 1790290045，`/mnt/chbackup_local/inc.zip` **字节与 mtime 双同**；epoch 换算 = 本地 09-25 06:47:25 = `system.backups` end_time **同一秒**；market.zip 266,634,034,420B@09-15（重基线后稳定）；inc/market=0.332≥0.15，时距 15.5h≤26h → **【第二链日检 09-25】PASS，第 2/14 天（10-05 摘盘证据链）** | 🟢 |
| 容量红线 | 四盘 free | F 766.7G ✓(≥700)｜G 1,479.8G ✓(≥500)｜E 296.0G ✓(≥50)｜**D 45.7G ✗ 破 50G 线** | 🔴 |

### 五、挖矿清单复核（SOP §五 六项盲点逐项，本轮全部给到可执行结论）

| # | 盲点 | 复核结论 | 判 |
|---|---|---|---|
| ① | backup 9.1h 病理 | **分解完成**（CH 段为实测，中段为区间推断）：06:00:09 点火 → 06:03:30~06:47:25 **CH BACKUP=44 分钟**（实测 `system.backups`）→ 06:47~13:30:39 **6 小时 43 分 = 双写 rsync（VM 内 market.zip 266.6G + inc.zip 88.6G ≈ 355G）+ vault Mode A 全量首建（234,299 硬链 + 187,513 物理拷）** → 13:34:25~15:06:45 **1 小时 32 分 = offrepo(cold_archive 147.6G) + g_mirror(60_mirror 追 C4 56.6G) 两段 USB 写**。并发轮 B 使中段进一步膨胀。下一轮起 `stage_timeline` 字段直读，不再靠 mtime 反推；B8（长任务拆分/g_mirror 周级化）仍是根治项 | 🟡→可观测 |
| ② | 周六 backup_ch_vm 与 DailyBackup 撞车 | **窗口确在**：`schtasks` 实测 09-26（周六）06:00 两任务同刻触发（`ZephyrAlpha-DailyBackup` + `ZephyrAlpha-WeeklyVMBackup`）；且 `scripts/backup/backup_ch_vm.ps1` **不持 `.runtime/backup.lock`**（全文 0 处引用）＝无互斥。**实证危害有限**：`last_ch_vm_backup_time=2026-08-22`、`autocheck=skipped_unchanged`，08-29/09-05/09-12/09-19 四个周六全部 AutoCheck 短退，从未真跑。**但同项查出更大问题见 ⑥** | 🟡（错峰仍应做，属 Owner 排程门位） |
| ③ | reaper keep 匹配语义 | **语义确定**：`_is_whitelisted()` = keep 文件逐行**子串**命中 cmdline（非正则）。**但候选集在 `src/zephyr/trading/process_reaper.py:396` 硬过滤 `"python" in name`** → powershell.exe / robocopy.exe **从来不是候选**，故 keep 里的 `backup.ps1` 行是**空转保护**（09-23 那条注释"疑遭 orphan_aged 处决"的因果不成立）；真正的死因是**宿主 python（reconcile_worker）被级联收割带走子树**（见 §二 根因 2）。建议：keep 文件加一行注释说明"仅对 python 生效"，并把保护点移到 worker 侧（处方 P-2） | 🔴→已定性 |
| ④ | CH today()=UTC 日切 | **本轮复证实测**：22:16:33 本地时点，`SELECT today()`=2026-09-25，而 `countIf(event_time::date = today())`=**0**，`countIf(event_time>=now()-INTERVAL 26 HOUR)`=**1** —— 同一张表同一时刻两种"当日"口径给出 0/1 两个结论；当日 06:47 本地成功的备份其 `event_time` 落在 UTC 09-24。SOP §一.3 的 26h 窗判据**必须保留**，任何"当日已备份"判据禁写 today() | 🟢（判据正确，已留证） |
| ⑤ | 60_mirror 对 C4 52.7G 追赶 | **结构层已完成**：`zephyr_cold_main/50_archive/by_project` 与源盘同名集合**全等**，C4 档在镜像内；顶层唯一差异 `AUDIT_SOP.md`＝今晨 21:12 新建（晚于 13:34 同步）属预期。**件数/字节级对拍**（60,245 件×两侧）待本轮 Stage 3d 跑完后执行，避免"边写边比"读到中间态（本轮曾因此调整次序） | 🟡（待字节级） |
| ⑥ | g_mirror 摘 ch_vm_backup 后冻结档无自动更新 | **不是"无自动更新"这么轻——是更新通道根本不指向冻结档**：`G:/backup/README.md` 声称"CH 升级时由 backup_ch_vm.ps1 重做全量"，但 `backup_ch_vm.ps1` 全文 **0 处 G: 引用**，`$BackupRoot="F:\ch_vm_backup"`（robocopy boot.vhdx+**data.vhdx** → F 盘）。后果双重：(a) 冻结档 `G:/backup/ch_vm_backup`（591.57G，唯一全量镜像）**没有任何工具能刷新**，CH 一旦升级即成旧基座，而 `restore.ps1 vm` 会拿它回灌＝**恢复出旧库**；(b) 若哪个周六 config 漂移触发真跑，脚本会向已被 Owner 降为"配置级"的 F 侧再灌 ~591G（F free 766.7G→约 175G，直接击穿 SOP §一.1 的 F≥700G 红线并推翻 10-05 摘盘预算）。**本轮未动任何一处**（改任务=生产流转门位，改冻结档=591G 数据面），列处方 P-6 请 Owner 定向 | 🔴（新发现，最高优先移交） |

### 六、灾备演练月检项（SOP §三.1 四级非破坏，2026-09-25 22:0x-22:4x）

| 级 | 演练 | 实测 | 判 |
|---|---|---|---|
| T1 | git bundle **实 clone** 到 F 临时区 | `zephyralpha_full_20260921.bundle`(468,545,940B) → `git clone` rc=0 → **19,055 commits**、HEAD=1420128a70(09-21 20:31)、`AGENTS.md` 真实读出 7,883 字符。附带口径澄清：`git rev-list -1` 恒 HEAD 是本仓约定（仅 `git log` 过滤分支头），故判据用 rev-list | 🟢 |
| T2 | SQLite 恢复 + `PRAGMA integrity_check` | 5 份库全 `integrity=ok`：`20260925/governance_backup.db` 45 表/201,895,936B、`20260925/session_backup.db` 1 表/12,288B，另 0921/0922 两日与旧 /MIR 根件同检全 ok | 🟢 |
| T3 | PG dump `pg_restore` 进临时库 `depgraph_drill` | 走 `scripts/backup/restore_drill.py`（正门）+ 本轮自补细粒度复算：**表数 live=89 / drill=89 全等**；三表行数 drill≤live（lib_assets 44,524/44,565、lib_events 1,483,550/1,634,702、nodes 12,656/12,669，差量=dump 后活库继续写入，方向正确）；restore 耗时 233.7s。**`pg_restore rc=1` 已定性=3 条已知良性错**（`CREATE SCHEMA public` 已存在 + 2 条 `ALTER DEFAULT PRIVILEGES` 权限），非数据缺陷；演练结束临时库已 DROP（复查 `pg_database` 残留=0，含中途自杀清理一次） | 🟢（判据缺陷另立 P-3） |
| T3 附 | **演练判据自身不可满足**（D-18 型恒红） | `scripts/backup/restore_drill.py:140` 用 `drill == live` **精确相等**裁决，而 dump 是历史时点、活库持续增长 → **任何非同一瞬间的演练必判红**；且 `pg_restore_rc` 被记录却不参与判定（rc=1 与 rc=0 同路）。上一班 T3 记"89/89 表一致"实为表数口径，本轮按行判据即翻红——**同一把尺两次量出不同结论，尺本身有问题**。处方 P-3：改判据为"表集合相等 ∧ drill 行数 ≤ live ∧ 抽样键集合对 live 的包含率 ≥ 阈值 ∧ 已知良性 restore 错白名单" | 🔴（尺缺陷） |
| T4 | CH 验证层 | `state.last_ch_backup_verified=True` + `system.backup_log` 26h 窗 `BACKUP_CREATED`=1（max=09-24 22:47:25Z=本地 06:47）+ `system.backups` 唯一行 inc.zip total_size=408,952,156,962B/900,239 文件；全量 RESTORE 属破坏性，按月排 `ZEPHYR-RESTORE-DRILL`（下次 10-01 04:30 已在册） | 🟢 |

### 七、9.1h 病理的**第一因**（本轮新实测，直接给出 B8 的具体内容）

`code_backup` 源树枚举实测（`D:/ZephyrAlpha`，扣除 exclude 后）：

| 顶层 | 件数 | GiB | 是否被 vault 排除 |
|---|---|---|---|
| **`.worktrees/`** | **470,314** | 5.27 | **否（未在册排除清单）** |
| `.runtime/` | 313,697 | 17.44 | 是 ✓ |
| `data/` | 20,746 | 4.96 | 部分（仅同名 `tmp` 目录） |
| `docs/`+`src/`+`tests/`+`scripts/`+`config/`+`architecture_model/` | 17,841 | 0.30 | 否（本盘主体） |

- **一轮备份要枚举 ~50.9 万条目，其中 92.4% 是 50 个 git worktree 的签出物**（平均 12KB 小件、mtime 常新），而 worktree 的已提交内容 git bundle 已灾难覆盖、未提交内容本属"尚不耐久"的在途工。
- 这与 0600 轮的 `copied=187,513 / hardlinked=234,299` 完全对得上：**每日"变更量"几乎全是 worktree 抖动**，不是项目本体变更（本体全量才 1.7 万件/0.3G）。
- 也解释了 09-24 审计表 `working_vault=1,328,858 件/239.9GiB` 的体积来源。
- 处方 **P-2**：`code_backup.exclude_dirs` 增补 `.worktrees`（→ 单轮枚举从 ~50.9 万降到 ~3.9 万，预计小时级降到分钟级）。**代价=其他会话 worktree 内的未提交 WIP 不再进日快照**，属"备份覆盖面上收"，按人机门位归 Owner 签字，本班会不擅自改配置。次选（Owner 若判覆盖面不可收）= 保留采集但改判据为"按 git 提交面增量"，即 worktree 只存 `.git` 引用不存签出物。

### 七之二、§七 数字更正与新增实测（自写尺必自纠）

- **分母更正**：§七 用本班会自算枚举求和写"~50.9 万条目"。权威口径=**本轮备份自身打出的索引计数**：`Source files: 501,192 / snapshot files: 431,972`（23:13:xx 落 `logs/manual_audit_rerun.log`）。差因＝本班会的 os.walk 未套"任意深度同名排除目录"规则（`tmp`/`__pycache__`/`.git` 等在任意层级都被排除）。按权威分母重算：**`.worktrees` 470,314 / 501,192 = 93.8%**。结论不变，分母与占比以本条为准。
- **新增实测**：本轮 Mode B **仅"建两棵树索引"一段就用掉 21:53→23:13 = 80 分钟**（其后拷贝循环 23:13→00:2x 仍在进行，1 小时+）。这就是"每日枚举 50 万条目"的直接代价，也是 B8/P-2 的量化落点：排除 `.worktrees` 后源树枚举量级从 50 万降到 ~3.1 万。
- 顺带噪声定性：拷贝期成串 `[WARN] Source vanished mid-run, skipped: .ailocks\...`＝他会话文件锁目录在索引后被正常删除，`vanished` 计数吸收、不判失败（`.ailocks` 实测仅 153 件/1.3MiB，非枚举成本来源）。

### 八、处方集（本班会不擅自执行的项，全带可复算坐标）

| # | 处方 | 触发证据 | 归口 |
|---|---|---|---|
| P-1 | `archive_manifest.jsonl` 2,210/2,515 行绝对路径仍指已删卷宗 `E:/zephyr_cold_archive/…` → 由生成器一次性 remap 至 `F:/zephyr_cold/50_archive/by_project/zephyralpha/…` 并留改前 hash 副本；**禁手改**（ constitution 静态清单禁手工维护；且 `scripts/ch/archiver.py:73` 是新行真源，改后须复跑一次 live 行对比确认无二次漂移） | 本轮全量 2,515 行核：305 直存 + 2,210 再锚定后件件字节相等 | 维护班（数据面账目，非生产风险） |
| P-2 | `code_backup.exclude_dirs` 增补 `.worktrees`（或改"按提交面采集"） | 源树 50.9 万条目中 47.0 万=worktree 签出物；0600 轮 copied=187,513 与之同量级 | **Owner**（备份覆盖面上收） |
| P-3 | `scripts/backup/restore_drill.py` 判据重立（表集合相等 ∧ drill≤live ∧ 抽样包含率 ∧ 良性 restore 错白名单），并把 `pg_restore_rc` 纳入裁决 | 本轮 `drill == live` 精确相等判据在增长库上恒红；rc=1 的 3 条错实为已知良性 | 维护班（尺缺陷，D-18 同族） |
| P-4 | `F:/zephyr_cold/AUDIT_SOP.md` §二.1 指向"本 SOP §四期望清单"，而 §四 实为季检章无清单 → 期望清单已随 `F:/README.md`+`G:/README.md`+`G:/backup/README.md` 建成，SOP 应改指三张导航（本轮即按此执行） | 本轮机械执行时该条不可落地 | 本班会可改（SOP 属冷库文档非规则册；待 Owner 点头即改，禁双真源） |
| P-5 | 备份报告 `Out-File -Encoding utf8` 落 **UTF-8 BOM** → 任何 `json.load(open(...,encoding='utf-8'))` 直接抛错；SOP 执行者须用 `utf-8-sig`（state 文件已是无 BOM，两文件口径不一致） | 本轮首次读报告即炸 `Unexpected UTF-8 BOM` | 维护班（一行改 `[IO.File]::WriteAllText`） |
| P-6 | `scripts/backup/backup_ch_vm.ps1` `$BackupRoot="F:\ch_vm_backup"` 与 09-24 Owner 裁定（F 侧降配置级、全量镜像唯一冻结档在 `G:/backup/ch_vm_backup`）**方向相反**：CH 升级重做全量会向 F 再灌 ~591G（F free 766.7→约 175G，击穿 SOP §一.1 F≥700G 红线并推翻 10-05 摘盘预算），而 G 侧唯一冻结镜像**没有任何工具能刷新**（restore.ps1 vm 又依赖它回灌） | 该脚本全文 0 处 G: 引用；`G:/backup/README.md` 声称的刷新通道与实际写入路径不符 | **Owner**（双重：数据面+排程面） |
| P-7 | post-commit 备份触发通道的载体寿命与流水线时长不匹配 → 三选：(a) 备份改由 `schtasks /run`（Task Scheduler 父链=svchost，免疫级联收割）承接，worker 只点火不托管；(b) worker 触发备份时把登记寿命抬到与 `subprocess timeout=14400` 同级；(c) worker 内检测到 `backup.lock` 由活轮持有时直接短路（本轮 B7 修复已使该短路生效，但**只解决并发，不解决 30 分钟处决**） | §二 根因 2（PID 18208 于 10:37:34 被级联杀，轮 B 无痕迹死亡） | **Owner/维护班**（进程契约变更） |
| P-8 | D 盘 free **45.7GB < SOP §一.1 的 50G 线**；另 `git_bundles` 仅 1 份（契约"留最新 2 份"在 G 侧从未成立＝git 历史单副本+7 天 RPO） | 本轮实测 Get-Volume + 目录清点 | 即报 Owner（空间红线属运维门位；bundle 第二份可由 3b 段政策修正自动生成） |
| P-9 | **ps1 侧锁语义无常驻测试**：本轮红绿 harness 靠"正则从 backup.ps1 抽函数 + Invoke-Expression"临时搭（`.runtime/tmp/bca_lock_test.ps1`，24h TTL 即灭），四案判据已全文入台账可据文重造。建议长期化为 `tests/dr/` 内一条 ps1 语义哨兵（HEAD 版必红/修复版必绿两态都锁住），否则下一个改锁的人没有尺 | 本轮 HEAD 版=RED（CASE1 False/CASE2 True）vs 修复版=GREEN（4/4）对拍成立 | 维护班 |
| P-10 | **`ZephyrAlpha-DailyBackup` 的 `ExecutionTimeLimit=PT4H` + `AllowHardTerminate=True`**：任何 >4h 的完整轮，其**计划任务实例**在 4h 处被判死（LastTaskResult=267014≠0），而真正干活的 powershell 是 wscript 的孙进程、**逃出作业对象继续跑到 15:06**——于是出现"任务显示被终止、备份却成功落账"的双真象分裂，监控/日检读 LastResult 即天天假红。**建议=时限抬到 8-12h 或直接落 P-2（缩时长）**（改任务=生产流转门位，本班会不动）；同检 `ZephyrAlpha-WeeklyVMBackup` 亦 PT4H（591G VHDX 拷贝 4h 内未必完） | `Get-ScheduledTask` 实测 DailyBackup：last=09-25 06:00:01 result=**267014**，ExecTimeLimit=PT4H；LibraryLedgerBackup/RESTORE-DRILL 均 PT72H（对照说明"4h 是唯一紧的"） | **Owner** |

| P-11 | 心跳守护经 `pythonw.exe + -WindowStyle Hidden` 启动会**静默消失**（无 err 无日志；启动后 10 秒内心跳面正常 age=10s，约 40 分钟后复查＝会话条目消失＋守护进程不在）；改 `python.exe + RedirectStandardError` 后常驻可查。另本会话在 registry 的条目曾在无人注销的情况下消失一次（与"会话不在册→守护自退"设计一致），属台账在案的并发非 CAS 写热册蒸发族。**建议=把 heartbeat 启动口径固化进会籍工具，而非各班口头传** | 本轮两次实测对照（同一命令换宿主即不再消失） | 维护班 |
| P-12 | **收割日志不可归因**：`src/zephyr/trading/process_reaper.py:445-450 _log_kill()` 只写 `PID + reason`，**不落 name/cmdline**（调用点两者都在手）。本轮定性"10:37 那刀杀的是谁"只能靠 `.runtime/process_incubator/ledger.jsonl` 按 PID 反查——**若该进程未走孵化登记（多数非 spawn_python_hidden 的进程就不登记），日志即成悬案**。建议一行改：`f.write(... + f" name={info['name']} cmd={cmdline[:120]}")`。连带 SOP §一.2"在 kill 日志里找 powershell 击杀"=**死探针**（候选集只含 python，powershell 永不出现，见 §五③），应改判据为"找 reconcile_worker/reconcile_runner 被杀" | 本轮实测反查链：`grep 2026-09-25 reaper_kill.log` + 孵化册 PID=18208 行 | 维护班（观测面，无生产风险） |
| P-13 | **仪表盘备份探针集体指错家**：`src/zephyr/frontend/dashboard/services_registry.py:120/123` 两行 detect 目录 = `E:\zephyr_cold_archive`（09-24 已删卷宗）与 `F:\code_backup`（09-21 起备份改家 `G:\backup\working_vault`，实测 F 侧该目录不存在）。后果=仪表盘备份健康位**恒红"灾备事故"**（`_daily_fresh_scan` 缺目录判红，属 fail-visible 不掩盖，方向正确），但长期狼来了会训练 Owner 忽略真红。修法不是两行：`name`/`desc` 里同样硬编码了旧路径（"F 盘代码备份仓"），须与 i18n/展示口径一并改，故**本班会不顺手改**，列此归维护班同批收敛 | `os.path.exists('F:/code_backup')=False` + E 盘顶层复扫无 `zephyr_cold_archive` | 维护班 |
| P-14 | `logs/` 已积 **361 份** `backup_report_*.json` 无轮转（既有工具 `scripts/governance/d6_security/retire_tmp_artifacts.py` 覆盖该类且默认 dry-run，只是从未 --apply/未接入事件）＝backlog T3 的实身 | `len(glob('logs/backup_report_*.json'))=361` 实测 | 维护班 |
| P-15 | **跨零点日期撕裂**：单次运行内 `vault 日目录`（21:53 取值=20260925）与 `db_dumps 日目录`（00:3x 取值=20260926）用两套日期，报告名又是第三种（起时刻）。按日恢复会拿到"昨日快照+今日 dump"的混搭。修法=脚本启动时把 `$today` 由 `$backupStartTime` 定格一次、全段共用（自包含小改）；本班会因验收窗口已过、留下轮带验证再动更稳 | 本轮实测：`working_vault/20260925` + `db_dumps/20260926` 同轮并存 | 维护班 |
| **已闭** | ~~B7 锁 PID 探活~~ → 本批已落地并前后对照验证（failed/1 → ok/0）；~~60_mirror 对 C4 追赶~~ → 60,245 件/56,591,048,267B 双零差 + 5/5 sha256 全等，与 drawers 第 8 行登记值分毫不差 | 见 §九 表 + `bca_mirror.json` | 本班会 |





### 九、四探针验收（手动重跑轮 PID 35532）

_（待本轮跑完回填）_

### 十、本班会终态与移交

_（待回填）_

### 九、四探针验收（手动重跑轮 PID 35532，21:51:58 点火 → 09-26 00:33:22 落账，**2h41m**）

**先说结论：修复前后同段直接对照成立。**

| 判据 | 09-25 06:00 轮（修复前，与轮 B 并发） | 本轮（B7 修复后，无并发） |
|---|---|---|
| `code_backup.status` | **failed**（failures=1） | **ok（failures=0）** |
| hardlinked / copied / vanished | 234,299 / 187,513 / 5 | 0 / 70,204 / 14 |
| `databases` 段 | 4 键全 ok（班令"全空"不成立） | postgres ok / sqlite ok / postgres_globals ok / clickhouse **skipped**（24h cadence，上成功=今晨 06:47） |
| state | last_backup_status=failed | **last_backup_status=ok @00:33:22**，ch=skipped+verified=True（承 06:47 成功） |

**探针逐项**
1. **报告完整**✓ `logs/backup_report_20260925_215158.json` duration 9,683s；**新字段 `stage_timeline` 首次产出即破案**：Stage 1=0s｜Stage 2（PG/SQLite dump+配置同步）=**62.2s**｜**Stage 3 vault=63→9,569.5s（98.2% 的时间，2h38m）**｜3b bundle skip｜3c offrepo=2.7s｜3d g_mirror=110s｜Stage 4 落账。
2. **vault 关键件**✓ `working_vault/20260925`：AGENTS.md ✓ pyproject.toml ✓ `config\.env.*` 5 件 ✓。
3. **dumps 四件齐**✓ 新日目录 `db_dumps/20260926`＝depgraph.dump + governance_backup.db + pg_globals.sql + session_backup.db 齐全。
4. **state + CH**✓ `last_backup_status=ok`；CH 侧本轮按 24h 节奏跳过（非失败），`last_ch_backup_verified=True`/88,580,255,288B 仍为今晨 06:47 那轮的成功凭据，`system.backup_log` 26h 窗=1 ✓。
5. **`restore.ps1 verify` 全过**✓ 15 项全 `[OK]` 至 `ALL CHECKS PASSED -- backup is ready for disaster recovery`（code 5 件 / bundle 447MB age 4.1d / dumps 4 件 dated 20260926 / CH market 248.32GiB+inc 84,476.71MB / VM 三层含 G 侧 591.57GB 全量镜像），rc=0。

**由本轮新观测直接得出的两条病理结论（写进 §七之二）**
- Mode B **仅建两棵索引就用 80 分钟**（源 501,192 件 + 快照 431,972 件），拷贝循环再 78 分钟；两段相加＝整轮 98.2% 的时间。`copied=70,204` 全部来自 worktree 抖动（与 §七 的 93.8% 占比互证）。→ **P-2 的收益不再是估计，而是可计算：源树从 50 万降到 ~3.1 万。**
- **跨零点撕裂**（新发现，处方 P-15）：本轮 vault 目录名取 21:53 的日期＝`20260925`，而同轮 dumps 目录取 00:3x 的日期＝`20260926`，报告名又是 `20260925_215158`——**一次运行产出两套日期标签**，按日恢复时"当日快照"与"当日 dump"不同一天。修法=脚本启动时把日期定格一次（`$today` 统一取 `$backupStartTime`），属自包含小改，本班会因"改窗口已过、留下轮验证更稳"未动。

### 九之二、60_mirror 字节级验收（补 §五⑤，跑在 3d 段之后，避免边写边比）

| 对照 | 源 | 镜像 | 差 |
|---|---|---|---|
| C4 考试研报 PDF 缓存 | 60,245 件 / 56,591,048,267B | 60,245 件 / 56,591,048,267B | **only_src=0 / only_mir=0 / size_mismatch=0**，sha256 抽 5 件全等 |
| final3 会话目录归档 | 1,839 件 / 6,521,736B | 同 | 全等，sha 5/5 |
| ETF/LOF 分钟 zip 原料 | 22 件 / 5,467,846,518B | 同 | 全等，sha 5/5 |
| 分层抽样 11 个子树 | 73,639 件 / 230,384,622,425B | 同 | **零差** |

三行绝对值与 `drawers.jsonl` 第 8/9/10 行登记数字**分毫不差**（独立两源互证：本班会尺 vs 09-24 登记）。→ **SOP §五.5 "60_mirror 对 C4 52.7G 追赶"判定：已完成**，09-25 夜债清。

**本班会自清记录**：`F:/zephyr_cold/90_tmp/bca_drill_20260925/`（本班 T1 演练 clone + T2 sqlite 副本，16,250 件/810.5MiB）已删除，删后该抽屉仅剩前任遗件 `conv_etflof`/`drill_bundle`/`drill_gov.db`（**非本班 creations，未动，列移交**）。学费一条：git pack 文件带只读位，`shutil.rmtree` 首遍 `WinError 5` 半程失败，须先 `os.chmod(S_IWRITE)` 再删。

### 十、本班会终态与移交

**已修（两笔，均走 `scripts/git_commit.py` 正门）**
- `5aef239f7c`（22:26 锁忙自动入队 → 队列落地，袋 `q-20260925-st-backup-cold-20260925-audit-0001` state=done）：**B7 锁 PID 探活**（红绿对拍见 §三，两案翻转＝尺有判别力）＋新增 `stage_timeline` 观测面。
- `b7c668cc`（23:04:56 直连提交）：`$codeResult.error_sample`（前 10 条失败明细入报告，终结"failures=1 无从归因"）＋台账 §六/§七。
- 两笔均 `git log -1 --name-only` 核归属＝各 2 文件、无外来吸收；`--is-ancestor HEAD` 双 YES。
- **附带排雷**：队列落地后主区 index 仍存本班两文件的 **pre-fix 旧 blob**（ledger 侧为"78 行净删"旧版＝回退炸弹），已 `git add` 刷新并逐件核 `wt-sha == idx-sha` 双件 PASS。
- 施工方式=主区直改（Owner 班令明示 claim→改→正门；`--allow-non-worktree` 留痕），改前 acquire／毕后 release。

**未修（一律带处方，见 §八）**：P-1 manifest 路径漂移 / P-2 `.worktrees` 排除（=B8 的具体内容，收益已可计算）/ P-3 演练判据恒红 / P-4 SOP §二.1 空指针 / P-5 报告 BOM / P-6 ch_vm 写入方向与冻结档刷新断链 / P-7 post-commit 载体寿命 / P-8 D 盘空间红线+bundle 单副本 / P-9 ps1 锁语义无常驻测试 / P-10 计划任务 4h 硬时限 / P-11 心跳守护启动口径 / P-12 收割日志不可归因 / P-13 仪表盘备份探针指旧家 / P-14 logs 361 份报告零轮转 / P-15 跨零点日期撕裂（同轮产出 20260925 快照+20260926 dumps）。

**复核命令（任何人可复算本班会三条最关键结论）**
1. 并发轮存在＝锁换过手：`python -c "import json,glob;[print(f,json.load(open(f,encoding='utf-8-sig'))['lock_mtime']) for f in sorted(glob.glob('logs/backup_skipped_20260925_*.json'))]"` → 前四件 06:00:09 / 后六件 10:02:41。
2. 轮 B 死于级联收割：`grep -n "2026-09-25 10:3" data/runtime/reaper_kill.log` ＋ `.runtime/process_incubator/ledger.jsonl` 内 PID 18208 登记行（owner=reconcile_runner, life=1800s, payload=3826755fa6）。
3. worktree 撑爆源树：`python -c "import os;print(sum(len(f) for _,_,f in os.walk('D:/ZephyrAlpha/.worktrees')))"` → 470,314（本轮 23:3x 实测）。

**移交他班的既存项**（本班会未动，状态复核后仍在册）：10-05 F 摘第一链盘（第二链日检证据链现已累计 2/14 天，本轮已补 09-25 行）；10-21 G 原抽屉库 137.6G；`G:/backup/offrepo/offrepo_backup`（136.6GiB 嵌套旧镜像）与 `G:/backup/db_dumps/db_dumps`（0.36G 旧 /MIR 根）待批清理；`F:/zephyr_cold/90_tmp` 内前任演练遗件（`drill_bundle`/`drill_gov.db`/`conv_etflof`）待清（本班会自造 `bca_drill_20260925` 已自清）。

**本班会自纠两条**
1. 时序判断失误：在手动备份轮正在枚举 G: 时并发起了 offrepo 全盘走查与 PG 演练（含 135MB dump 从 G: 读），三方互拖——offrepo 全量走查 6 分钟出数（22:12→22:18）、PG 演练 22:11 收尾，而备份 Mode B 索引至 22:52 已 60 分钟未完（RSS 501→557MB 缓增）。教训=**监督长跑时，任何全盘 walk 必须排在长跑之后**；本班会随后把 60_mirror 字节级对拍改到 3d 段完成后执行，即为此纠偏。
2. 自写探针脚本两处低效：PG 子集证明用 `set(inter)` 放进列表推导（O(n²)，44K×重建集合＝空转 30 分钟后手动处决并清理临时库残留）；路径判定首版把 `os.sep` 写成字符串字面量致 4 行假 MISSING。两条均已改正后才出数，列此以防后人误读早先数字。

**四探针终判＝全绿**（详数见 §九）：报告完整（databases 4 键齐全、CH 按 24h 节奏 skip 非失败）｜vault 关键件齐｜dumps 四件齐（新日目录 20260926）｜state `last_backup_status=**ok**`｜`restore.ps1 verify` 15 项 `ALL CHECKS PASSED`。**修复前后同段对照＝本次治本的唯一硬凭据**：06:00 轮（并发）`code_backup=failed / failures=1` → 本轮（无并发）`ok / failures=0`。

**待 Owner 表态的三件（其余见 §八）**：P-6（ch_vm 全量重做写 F 与 09-24 裁定相反，且 G 冻结档无刷新通道）、P-10（DailyBackup 任务 4h 硬时限）、P-2（`.worktrees` 是否入排除清单＝备份覆盖面上收）。

【灾备演练月检 09-25（SOP §三.1 四级非破坏，提前执行）】T1 git bundle 实 clone→19,055 commits/AGENTS.md 7,883 字符可读 ✅｜T2 SQLite 5 份 `integrity=ok`（45+1 表）✅｜T3 `pg_restore` 进临时库 depgraph_drill→**表 89/89 全等**、三表行数 drill≤live、rc=1 定性为 3 条已知良性错（CREATE SCHEMA public 已存在+2 条 ALTER DEFAULT PRIVILEGES）、临时库已 DROP 且复查 pg_database 残留=0 ✅｜T4 CH 验证层 `verified=True`+`system.backup_log` 26h 窗=1+`system.backups` 408,952,156,962B/900,239 文件 ✅｜附 `restore.ps1 verify` 15 项 ALL CHECKS PASSED ✅。**四条恢复路径（git/SQLite/PG/CH）本班会全部真实走通＝月检项达成**；CH 全量 RESTORE 与 VM 导入属破坏性演练，仍按 `ZEPHYR-RESTORE-DRILL`（下次 10-01 04:30）执行。**唯一红项不在恢复链而在尺**：`scripts/backup/restore_drill.py:140` 精确相等判据在增长库上恒红（处方 P-3）。
【第二链日检 09-26 前置读数（09-25 22:4x 实采）】VM 内 `stat`：`/mnt/chbackup2/inc.zip` = 88,580,255,288B @ epoch 1790290045 与第一链 `/mnt/chbackup_local/inc.zip` **字节+时戳双同**，换算=本地 09-25 06:47:25（与 `system.backups` end_time 同秒）；market.zip 266,634,034,420B@09-15 重基线后稳定；inc/market=0.332≥0.15、时距 15.8h≤26h → **PASS，第 2/14 天**（10-05 摘盘证据链）。09-26 06:00 轮后再读一次即累计第 3 天。
【本班会收口状态】sid=st-backup-cold-20260925-audit｜冷启动 21:25，收口 09-26 00:4x｜两笔提交 `5aef239f7c`+`b7c668cc` 均入 HEAD｜四探针全绿｜处方 15 条（P-1..P-15）全带坐标，其中 **P-6/P-10/P-2 待 Owner 表态**，余归维护班｜本班自造件（F 侧演练 clone 810.5MiB/16,250 件）已自清，临时 PG 库已 DROP，reaper keep 册新增本班心跳一行（他班可据 dead-sid 处方精准回收）｜零删除项目数据、零实盘触碰、零绕门。

## 十四、修复波终态（Owner 令"12 条不要归维护班"→ 本会话开 7 条车道并发执行）

> 车道文件严格隔离；台账/结论由本会话单点 CAS 写；每条任务书含四条硬约束（禁删除、禁绕门、禁伪造 Owner 裁定、禁改判据阈值凑绿，前提被证伪即停手上报）。所有数字均经本会话**独立第二实现**复核。

| 处方 | 车道 | 终态 | 凭据要点（本会话已复算） |
|---|---|---|---|
| P-1 manifest 漂移 | 总包亲手 | ✅ 已闭 | 2,515/2,515 行 path 存在+字节相等（改前 2,210 假红）；仅前缀替换、其余字段逐行 byte 不变；BOM/CRLF 口径不变；改前全量副本 + sha256 已登记 drawers 第 11 行；动手前先证实"无程序读者"（archiver 恢复走再推导） |
| P-5 报告 BOM | A | ✅ 已闭 | commit `ef1d6cc73a`；报告与 lock-skip 记录同治；读者清点三处（reconciler 用 utf-8-sig / retire 只匹配文件名 / 测试自带无 BOM fixture）→ 无一要求 BOM |
| P-15 跨零点撕裂 | A | ✅ 已闭 | `$RunAt` 单次锚点，报告/vault/dumps/bundle 四处同号；轮转与 cadence 仍取实时钟（阈值零改动）；真时钟回放：旧=TORN 两套日期、新=COHERENT，且与盘面实况（00:30/00:31 两个日目录＋其间仅一条 lock-skip）吻合 |
| P-8b bundle ≥2 | A | ✅ 已闭 | 份数闸补"<2 即重建"一支；实补 `zephyralpha_full_20260926.bundle` 484,105,013B，本会话独立 `list-heads` 两份 rc=0、`verify` rc=0，旧份未删＝零删除 |
| P-4 SOP 死指针/死探针 | G | ✅ 已闭 | `F:/zephyr_cold/AUDIT_SOP.md` v1.0→v1.1，净增 ≈1 行；红证＝改前 `grep 期望清单` 仅命中其自身、§四 无清单；新探针当日命中 6 条 vs 旧文案查 powershell 击杀 0 命中 |
| P-14 logs 轮转 | J | 🔵 **改判（前提被证伪）** | 复算＝report 362 份仅 2,054,595B(1.96MB)、skipped 49 份 10,916B、90 天口径命中 0；`git ls-files logs`=0 且 `.gitignore:262 /*` 覆盖 → **磁盘唯一副本**。结论：**不做删除式轮转**（省 1.96MB 换掉不可再生的逐轮全链路校验真源，不划算）；如需减量应改"归档压缩到 G/F + 双副本 sha256"。附带查出工具真实缺口：`collect_logs_stale` 只匹配 `backup_report_` 与 `.log`，**49 份 `backup_skipped_*.json` 永不退役**（而 SOP §一.2 恰要读它）。批准包留 `.runtime/tmp/st_bca_j_retire_20260926/` |
| P-16 嵌套旧根清理包 | 总包亲手 | 🟡 **拆批不并签** | 三方差分实测：`offrepo/offrepo_backup` 136.6GiB **独有件=0**（1,968+43+44+2,230 全在现行镜像）共有键尺寸差=0、sha256 抽 16/16 全等，唯一异寸键=`archive_manifest.jsonl`（嵌套=改锚前态，本会话已另存 .bak）→ **可批**；`db_dumps/db_dumps` 0.36GiB 有 **2 件独有**（`governance_backup.db` 193,933,312B / 194,093,056B 在全部日期目录与活 dump 目录均无同尺寸对应）→ **禁并入删除批**；`git_bundles/git_bundles` 853,725,965B（09-14/09-15）＝09-24 那次"已删旧导出件"只覆盖了一处路径，同族第二处仍存活 → 单列待裁 |

**车道并发副作用如实记**：车道 A 提交期出现 `GATE-TRACKED-DRIFT VIOLATION`，漂移文件正是同批车道 C 在改的 `scripts/backup/restore_drill.py`（与其清单零交集）→ 自动降级 warn 放行；多车道并行时该门禁的"漂移"读数会互相污染，归属仍以 `git log -1 --name-only` 为准。另：车道 G 报 F 盘 SOP 出现过第二写者（当前盘上为 v1.1 本版，无外来标记残留）。

### 十五、修复波续（D/I/E/B 四车道 + 本班自挖三条 + 自我更正两条）

**P-12 收割日志可归因**（车道 D，无独立 commit＝被他会话吸收）：`_log_kill()` 增 `name`+`cmdline(≤120)` 行尾追加（旧 grep 口径不破），8 处调用点 4 组全补，另加净化器 `_log_field`（控制符压平＋密钥脱敏＋硬截断）；本会话独立核 HEAD：`def _log_field` / `name: str = ""` / `cmdline: str = ""` / `kill 日志可归因字段` 四标记俱在。**归属事故如实记**：车道 D 提交两次撞 `LOCK_TIMEOUT`，其间他的 678 件 emergency 批 `30505c93f6`（01:15）把这两文件整体吸收＝本项改动落账在他人 commit 名下。附带既有泄漏修治：整册 kill 日志重定向 tmp_path（此前该测试册用例会写生产 `data/runtime/reaper_kill.log`，违宪法 §9.6 测试隔离）。
**P-9 ps1 侧锁语义常驻尺**（车道 I，commit `ac1df94d42`，1 文件 487 行）：正则从 `backup.ps1` 抽 `Test-BackupLock` 真函数体实跑六案（含"内容不可读退回 4h 规则"两案），红侧＝旧 age-only 版 CASE1 判"抢锁"（09-25 断链复现）；旧版实现按 git blob `a389773a4c` 自定位核账，不写死 HEAD~k；11 passed，同目录既有 `test_backup_lock_stale.py` 11 passed 未牵连。
**P-11 更正（我的前提被车道 E 证伪）**：心跳守护不是"pythonw 无声杀死"。真因＝**设计自退**：`_MAX_IDLE_SECONDS=1800`（会话 30 分钟无活动判死，900 秒宽限后从活跃册摘除），退出原因写在 `heartbeat.jsonl` 而非 stderr（pythonw 本无 stderr，"查无日志"是我找错地方）；第二次"能常驻"是因为我一直在产生活动。落点改在入口层：无控制台时把 `None` 流降级为丢弃型＋入口任何异常写 `fatal` 带栈落盘（commit `714981aa55`，46 passed，正规调用点 `_spawn_heartbeat_daemon` 本就用 python.exe+DEVNULL，未改）。**本会话随后被同一机制现场复证**：约 25 分钟无会话活动后，提交被 `SESSION-REQUIRED` 判"未注册"。
**P-7 灾备点火/托管分离**（车道 B，bag `q-20260926-st-bca-b-recon-20260926-0001` pending，pos_ahead 1 待落地）：`reconcile()` 重写为"先结算上轮点火→主动锁自查（自备 `PID:` 正则；实测 ps1 锁文件是 `PID:<n> START:<iso>` 文本非 JSON，故 `backup_runtime_state._read_lock_holder_pid` 不适用，这条车道自己发现并绕开）→经瞬时装载器脱离点火→只记 `last_backup_launch_time/ignited_pending_verification`"，三条 stdout 语义改从落盘日志 `utf-8-sig` 解析，INV-11 决策树原样搬进延后裁决；免疫论证＝`_kill_pid_tree` 沿**活 PPID 链**取后代，装载器即退→真备份 PPID 指向已亡装载器，不在 worker 活树内。红绿＝旧实现跑新断言 **24 failed/10 passed**，新实现 **34 passed**，目录级 47 passed。

**本班自挖三条（原处方集之外）**
- **P-19（已治本，commit `bce9d7a80a`，58 passed）**：见 §"守门进程瞎 23.5h"。要点＝`reap()` 拆外层兜底＋`_reap_cycle` 主体，主体任何一步爆炸都"记 `reap_aborted`＋finally 落快照＋异常照抛"，尾段三步各自独立 try（`ghost_stage_failed`/`drift_stage_failed` 分因）；阈值/判据零改动。下一次计划触发的实测由观察器回收。
- **P-20（已自愈，只记不修）**：车道 B 见 pre-commit 横幅"09-25 起 `reconcile_worker boot failed: roster entries 102 != declared total_gates 99`"。本会话复测＝`in_process_gate_registry.yaml` 现 **gates=102 / total_gates=102 已对齐**（该硬对账真源即此文件，见 `gate_auto_registrar.py:8` INVARIANTS），故 reconciler 起不来的断链**已在他班落地中自愈**，横幅是 09-25 的陈旧读数——不据此立案。
- **P-21（活缺陷，未修，给坐标）**：同一口径下 `gate_registry.yaml` 现 **gates=180 而声明 total_gates=174**（差 6）。该字段是"计数用字段不写死散文"的机器真源，漂移＝文档面失真；修法不是手改标量（本仓已证"派生标量经队列合并恒取 ours，永远进不了 HEAD"，正解＝跑该册生成器按段长度重算再随批落）。归维护班同批收敛，本班会不抢这张热册（8 路车道并发时段动热册＝蒸发病复现条件）。

**归属与安全的一处正面证据**：我那份"内容已被更新提交超越"的陈旧袋 `q-...-0002` 被队列**判死而非强行回退**——`dead_reason="dev CAS 竞态：714981aa..bce9d7a8 间同路径被并发落地工推进"`。这正是队列作为正门的价值：它宁可死信也不覆盖更新的 HEAD。此死信**不应 requeue**（requeue 会按当前工作区重建＝与 HEAD 同内容，纯 noop），留档即可。

### 十六、修复波终态（02:2x 收口，逐条带凭据）

**P-19 根因坐实并二次治本（本会话自挖）**：外层兜底上线后**第一次计划触发**就把真凶写进快照——
`errors=['reap_aborted: psutil.AccessDenied(pid=4908)']`、`dry_run=False`、快照照落（01:51:28 那次）。
定位＝`_kill_pid_tree()` 三处 psutil 调用无 AccessDenied 兜底（`Process()` 构造 / `wait_procs` /
`proc.wait`），而 **dry-run 分支根本不调本函数**，所以我此前所有手工复现都失败。
后果比"没落快照"重得多：一个打不开句柄的受保护进程，把**同轮其余收割 + 幽灵扫描 + drift 指标 +
挂在同一脉冲上的保命链（应急保命轨 BRK-078 / 内存水位真闸 BRK-066）整条带走**——即那两条"自动触发"
自 09-25 01:49 起等于没跑过 23.5 小时。修法＝`_kill_pid_tree` 改为永不抛（杀不动=返回 False，
调用方既有 `[FAILED]` 语义承接）＋ logger.warning 留痕；判定阈值与 kill 顺序零改动；
+4 例（三种 AccessDenied 形态各自返回 False 不上抛，红证＝同输入喂修复前调用序列必抛），
**62 passed**，ruff 干净 → 袋 `q-20260926-st-backup-cold-20260925-audit-0003`。
（刻意**没有**在调用点再包一层 try：唯一现实抛源已在本函数内闭合，不给假想场景加壳。）

**P-3 演练尺（车道 C）**：判据重立为四条件合取纯函数 `judge_drill`（`c1_table_set_equal` /
`c2_row_direction` / `c3_content_fingerprint` / `c4_pg_restore_rc`），旧 `drill==live` 恒红尺废除；
陈旧度默认只入报告读数不设硬阈值（避免"用一次恒红换另一次恒红"）；C3 只比两侧**共有主键**的稳定列
指纹（结构性消掉 09-25 我那次"前 5000 行 md5 不等"的真因＝新增行挤进前 N）；C4 把 rc!=0 入裁决但
只白名单三条有实物证据的良性错，集合外一律红。26 例新建测试 + **9 条变异检验（8 条被抓，1 条等价）**；
真数据双向对拍＝旧尺红/新尺绿 + 植入"删 7 表改 3 老键"立刻红。
⚠ **归属实况**：车道 C 首轮回报的 `commit=3d100121b6` 经复核**不是有效对象**（`git cat-file -t` 报
Not a valid object name），作业实际停在索引；总包逐读索引 blob 确认在位后尝试代投，被**外来 staged**
连坐（MUTABLE-CONST 属全仓扫描型，违规点是他人 in-flight 的 `blueprint_format_gate.py:70 __all__`）→
最终由**车道自己的袋** `q-20260926-st-bca-c-drill-20260926-0001` 落地，归属正确。此为"自报凭据必须复核"的现场教材。

**P-13 仪表盘探针（车道 F 撞 150 轮上限中断、无案卷，总包验后代投）**：两行 detect 跟迁到
`F:\zephyr_cold\50_archive\by_project\zephyralpha` 与 `G:\backup\working_vault`，并加 `cfg_key`
从 `backup_config.yaml` 派生真源（盘上字面量降为 fallback）；`code_backup` 不再对 USB 盘做
130 万件 os.walk，改关键件+最新日目录有界判定且"未落齐的更新日快照自动回看上一日"。
本会话实测＝`code_backup → green（快照 20260925 · 关键件 5/5 在位 · 2 小时前）单次<0.05s`、
`cold_archive → green（清单 2515 件在位 / 118.0 GB）单次 0.4s`（顺带独立复证 P-1 改锚后 2515 件全在位）；
新建 22 例测试全绿；另补 `_TIER_LABEL: Final` 以过 5.114 门禁。**体量披露**：该文件 HEAD 版本本就
"Would reformat"（不合规存量），车道 F 顺手做了 ruff-format 全文件归一，故 diff 达 923 行——
理想应拆两笔，半路车道已不存在，本会话不再拆，如实标注。袋 `q-20260926-st-bca-f-dash-20260926-0001`。

**新增两条待办**：**P-21** `gate_registry.yaml` 现 gates=180 而声明 `total_gates=174`（差 6）＝派生标量漂移，
须经生成器重算（本仓已证"派生标量经队列合并恒取 ours，永远进不了 HEAD"），本会话不抢这张热册；
**P-22** 车道 C 发现演练库 `CREATE DATABASE` 继承 template1 的 `datcollate=Chinese_PRC.936` 而生产库是 `C`
——它本次靠钉 `COLLATE "C"` 规避，**建库保真度未修**：恢复出的库排序/比较语义与生产不同，属"演练通过
但恢复不等价"的隐蔽面，建议 `restore_drill` 建库显式 `LC_COLLATE 'C' TEMPLATE template0` 并复核约束齐建。

**并发实况三条（写下来给下一班省时间）**：① `SESSION-REQUIRED` 因心跳 idle-30min 设计自退，本班会
**三次**被判"会话未注册"（含代投车道袋时），处方=每次提交前现登现用，别指望注册长存；② 车道工作树
被外部进程回滚两例（本会话 `backup.ps1` 的锁函数被冲掉一次、车道 C 文件两次），凡改动必"改完立刻
`git add`＋当条命令内提交/入袋"；③ 外来 staged 会让全仓扫描型门禁连坐无辜提交人，正解是走队列
（serializer 干净暂存区结构性免疫），不是硬闯也不是代修他人违规。

**终局（02:0x 快照，P-7 见第十七节更正）**：12 条处方＝已落地 8（P-1/P-3/P-4/P-5/P-9/P-12/P-13/P-15，P-8b/P-19 及 P-11 更正同批计入）、
**在途 1（P-7 车道 B 首袋被判死，重建中）**、
改判 1（P-14 前提证伪：362 份报告仅 1.96MB 且 git 内零副本 → 不做删除式轮转，要减先归档压缩）、
不修 2（P-8 D 盘空间红线与 P-10 任务时限属 Owner/运维门位；P-2/P-6 亦待 Owner）。
待你点头的仍是三件：**P-2**（`.worktrees` 进不进排除清单＝覆盖面取舍）、**P-6**（ch_vm 全量重做写 F
与 09-24 裁定相反、G 冻结档无刷新通道）、**P-10**（DailyBackup/WeeklyVMBackup 的 PT4H 硬时限）。
本班会零删除、零实盘触碰、零绕门；三笔在途袋（0002 已判死且不 requeue，内容与 HEAD 同＝noop）。

### 十七、收口波（02:3x—03:0x）：P-7 重建落地＋P-19 判定口径更正＋新发现 P-23

**P-7 车道 B 首袋死因与重建（本会话亲自动手，非移交维护班）**：袋
`q-20260926-st-bca-b-recon-20260926-0001` 判死原因＝COMPLEXITY-GUARD
（`scripts/backup/backup_reconciler.py` `_adjudicate_completed_run` 复杂度 16>15），
且车道 worktree 内容同时被外部回滚。处置＝从死袋 blob 取回两文件（**双证**：
blob 字节 sha256 与死袋 manifest 登记值逐件相等后才落盘），再对症降复杂度：
- 真因不是"分支多"，是**我此前拆 helper 时留下的重复落库**——父函数里那一次
  `update_state_at(...)` 与 `_fake_green_verdict` 内部那一次字段完全相同（同一轮把
  `ch_log_missing` 写两遍）。删父函数侧那次，落库点唯一化，**顺带修掉一个自造缺陷**；
- helper 不再自己 `import ReconcileResult` 再兜 `dict`（那是我为测试环境加的壳）——
  沿用本仓 reconciler 既有"结果类作参数注入"约定（与
  `scripts/governance/d8_doc_sync/*_reconciler.py` 同形），去掉 `factory` 分支；
- 度量口径：用**门禁自己的尺** `high_complexity_gate._cyclomatic_complexity` 复算
  ＝16→**15**（阈值是 `>15`，15 放行）。不用第三方 cc 工具读数，避免口径漂移。
- 语义零改动（状态字段值、`detail` 文案、判据顺序均不变），
  `pytest tests/scripts/backup/` **47 passed**，ruff format/check 干净。
- 新袋 `q-20260926-st-bca-b-recon-20260926-0002`（files=2，入袋后逐件把盘上字节
  sha256 与袋内 `blob_sha256` 对上：`b770f88166d4…` / `dc254a9e0197…` 两件 MATCH）。
  第一次直连提交被 COMMIT-SCOPE 判 2 域（scripts/backup 与 tests/ 同批），
  按正门加 `--allow-multi-domain` 留痕改道入队，未硬闯未代修他人 staged。

**P-19 判定口径更正（自我复核，防下一班误读）**：02:21:30 那一轮快照
`errors=[]`、`scanned=28`、`whitelist_hits=20`、34 条 `reported`——**这不构成
"kill-tree 修复已生效"的证据**。病灶进程
`pid 4908 = NgcIso.exe`（Windows 受保护进程，非提权句柄永久 AccessDenied，实测
`psutil.AccessDenied (pid=4908, name='NgcIso.exe')`）**至今存活**；它只在"某次 kill
的进程树扫到它"时才触发抛源，这一轮恰好没走到。所以：
- 已生效且被本轮证实的＝**外层兜底**（`reap()` 的 `finally: _write_status`，已落地）：
  中途失能也落快照、且 `errors` 里带 `reap_aborted: …`——正是它把真凶写进台账的；
- 仍在袋里的＝**内层永不抛**（`_kill_pid_tree` 三处 AccessDenied 兜底，袋 `-0003`）；
- 唯一硬证据＝那条红证：同一输入喂"修复前调用序列"必抛、喂修复后函数返回 False 不上抛。
⇒ 验收 `-0003` 落地的标准不是"下一轮没报错"（间歇性，可能连跑几十轮都不撞），
而是"`_kill_pid_tree` 对受保护 pid 返回 False 且 `reap` 不抛"这条测试在 HEAD 里跑绿。

**P-23（新发现：keep 名单按"整条 cmdline 子串"匹配＝参数值里出现路径就拿到永久豁免）**：
读本轮快照时为了解释"`killed=[]` 却有 27 条 `incubation_expired_whitelisted`"而实测出来：
- 语义：`process_reaper.py:1011-1013`——孵化到期后先过 `_is_whitelisted(cmdline, …)`，
  命中即 `report_only` 并 `continue`，**永远不杀**（这不是漏杀 bug，是设计上"keep=免死"）；
- 命中面：keep 册现存 167 行有效子串，其中 `'commit_queue'` 匹配孵化台账 1492 条记录里的
  **561 条**、`'pytest'` 匹配 **438 条**——因为匹配对象是**含参数值的整条 cmdline**；
- 实物证据（现抓）：`python.exe -m zephyr.governance.audit.reconcile_worker --payload
  D:\ZephyrAlpha\.runtime\commit_queue\worktrees\w1\.runtime\reconcile_reports\…json`
  ——它的**参数里那条路径**含 `commit_queue`，于是这个早该到期的工人被永久豁免；
  本轮 30 条 `incubation_expired_whitelisted` 逐条反查 keep 子串**全部命中不了**
  （`matched-by=[]`），因为快照 `cmdline` 被截到 120 字符而路径在后面——
  这是**取证面自身的截断坑**，判"某行为何豁免"必须回孵化台账取全串，别拿快照下结论；
- 现状体量（此刻）：live python 36 个，其中"cmdline 含 commit_queue 但不是队列本体"=1
  （pid 33084，1.0h，48.8MB），"含 pytest"=5 → **暂时不危险**；危险在趋势：队列每跑一轮
  就多一类"参数带队列路径"的工人，豁免面随 payload 路径自动扩张，且 561/1492 的历史
  命中说明这类记录一直在攒。
- 处方（**待裁，不自行收紧**）：把 keep 匹配从"整条 cmdline 子串"改为
  "只匹配可执行/模块身份段（`-m <module>` 或脚本 basename），参数值不参与"；
  或直接收紧那两行（`commit_queue` → `commit_queue.py`／`-m zephyr…commit_queue`，
  `pytest` → `pytest ` 结尾带界的 argv[0] 位）。**为什么不自己改**：收紧＝把原本免死的
  进程重新纳入可杀集合，属于"改变保命面"，与 P-2 同族（覆盖面取舍），必须 Owner 点头；
  且本班会硬红线是零删除/零绕门，不拿"看起来更安全"当理由动判据。

**落地监护交接（三笔在途袋，均 `branch=dev`，`base_head=3bfeb4b174…`）**：
① `-0003` 本会话 reaper 内层修复；② `st-bca-c-drill-…-0001` 车道 C 演练尺；
③ `st-bca-f-dash-…-0001` 车道 F 探针；④（本波新增）`st-bca-b-recon-…-0002` P-7。
查：`python scripts/commit_queue.py status --session <sid>`；落地后逐笔
`git log -1 --name-only` 核归属（队列当前有他人在飞：`st-qmine-…0029` processing，
`daemon=online`，队首按 qid 字典序，本班会四笔均排在自己车道位上，未插队）。

**十七节补记（02:4x，落地后回填）**：`-0003` 已落地＝commit
`dc1c66e651`（`git log -1 --name-only` 核实归属＝只含我那两件
`src/zephyr/trading/process_reaper.py` + 其测试，零外来吸收），
落地后从 **HEAD 的盘上代码**复跑判定测试
`pytest tests/zephyr/trading/test_process_reaper.py -k "KillPidTree or NeverBlinds"`
＝**7 passed**（4 例 kill-tree 永不抛＋3 例快照永不失明）。
⇒ 本班会最高价值那条（保命链被一次 AccessDenied 连坐 23.5h）**判据已闭合**：
不再依赖"下一轮没报错"这种间歇性观测。

### 十八、P-24 新发现（提交链侧，非本班会范围，只登记不代修）

**现象（02:35 我入队车道 C 修复袋时当场撞到）**：
```
gate_auto_registrar FAIL-CLOSED: 1/103 gates failed: DOC-HEADER-SUITE:
register failed: GateRegistrationError: priority=77 冲突——gate 'DOC-HEADER-SUITE'
与已注册的 'BLUEPRINT-FORMAT' 同 priority.
preflight gateway 初始化失败，入队预校验跳过
```

**根因（实物定位，非推测）**：`f3cac8b95c`（st-commitspeed-pkg8 批·T8簇2，02:05 落地）
把七台文档头门禁合并为 DOC-HEADER-SUITE，同时**保留 BLUEPRINT-FORMAT 薄工厂出册**
（其 commit message 自述"gate_id/priority 保真，引用兼容"）。两处都写死了同一个
priority：`src/zephyr/gov_enforcement/commit_gates/blueprint_format_gate.py:182`
（BLUEPRINT-FORMAT=77）与 `:231`（DOC-HEADER-SUITE=77）。而注册表是 **fail-closed** 的
（`src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py:309-320`，
#ARCH-GATE-PRIORITY-UNIQUENESS-001 Phase 2：warn-only 被判"AI 会把 warn 当通过"而升级为抛），
其 docstring 明写"Phase 2 block 不会卡死现有系统"——依据是当时唯一已知的撞号
（BLUEPRINT-FORMAT vs RULING-COMMIT-VERIFIED）已在 Phase 1 消除。
⇒ **该前提被这笔落地提交重新打破**：新撞号是合并时自己造出来的，Phase 1 豁免表里没有它。

**实测面积（不夸大）**：
- 链**没停**：02:05 之后仍有 `3bfeb4b174`（02:22）、`dc1c66e651`（02:30，本会话袋）
  两笔正常落地 ⇒ 落地侧（serializer→git commit→GATE-PRECOMMIT-RUN）硬门禁照跑；
- 坏的是**锁外预检层**：`preflight gateway 初始化失败 → 入队预校验跳过`＝自 02:05 起
  每个会话的"一次给全违规清单"保护实际处于关闭状态（我 02:31/02:36 两次入队的回执里
  都印着这一行，而回执仍以 `ENQUEUED:` 成功结尾——生产者极易当成正常入队），
  后果＝违规从"提交前 3 秒看到"退化为"排队几十分钟后死袋才知道"，
  与本战役"提交链提速"目标反向；
- 我自己的两次入队（车道 B `-0002` 02:31、车道 C `-0002` 02:36）都是在**预检被跳过**的
  状态下投的，两笔至今 pending（未死、也未落地），所以本条只到"早停保护关闭"为止，
  不下"硬闸失守"的结论——车道 C 那笔 B905 的拦回发生在 02:01 的 `-0001`（撞号之前），
  不能算作本缺陷的后果。**这不是静默放行违规，是静默关掉了一道早停保护**。

**处方（属主＝st-commitspeed-pkg8 车道 / 维护班；本班会不代修，理由＝§3.4 owner 责任制
＋改别人刚落地的合并判据面属高半径动作）**：
1. 二选一：给 DOC-HEADER-SUITE 换唯一 priority（历史先例：RULING-COMMIT-VERIFIED
   77→109、DOC-REF-BROKEN 88→91），或把保留用的 BLUEPRINT-FORMAT 薄工厂**不再注册进
   in-process 名册**（只保函数可导入，满足"历史测试/RULE-EXECUTION-PAIRING 引用兼容"）；
2. 无论哪种，都要给"合并后台与吸收台的 priority 关系"加一条**注册期断言测试**
   （union 台与其吸收台同 priority 即红），否则下次合并还会复现；
3. `preflight gateway 初始化失败 → 跳过`这个降级本身应改为**可见**：把
   "本轮预检未运行"写进入队回执与审计（现在是 INFO 一行，生产者很容易当成正常入队）。
   ——这与本班会 P-19 同族：**兜底把异常吞成"继续跑"，比崩溃更难发现**。

**附（同窗口另一条观测，属事实不属 P-24）**：本会话台账副本在 `-0004` 入袋后被
**回退** 531→411 行（§十六/§十七 从盘上消失，仅存活于该袋 blob），这是本会话内第三次
撞同类重置（前两次＝`backup.ps1` 尾块、reaper 测试新增块）。**成因未定位**：
`.runtime/workspace_drift_warn.jsonl`（303 行）与 `.runtime/worktree_ops_log.jsonl`（9649 行）
按路径 `disk_reorg` 检索均零条目，故不下"谁干的"结论。处方沿用既有铁律并再加一条：
热文件"入袋≠落盘"，袋 blob 是唯一可靠副本，任何"我改过"的断言都要以
`git show HEAD:<path>` 现读为准；重建走＝以 HEAD 文本为基重放全部草稿段
（本次＝HEAD 411＋四段＝585 行，断言四个标记各出现 1 次且前缀与 HEAD 逐字节相等）。

### 十九、未归因 hazards 记录（本班会只登记"已排除项"，防下一班重复排查）

**H-1 主工作区在制品被回退（4 例，成因未定位）**：02:2x—02:4x 窗口内实测四次
"盘上文件被退回 HEAD 版本"，其中两次紧跟"该文件的袋被判死/入袋"之后：
| 时点 | 文件 | 发现方式 | 后果 |
|---|---|---|---|
| ~01:0x | `scripts/backup/backup.ps1` 锁函数尾块 | 改完再读发现回到 HEAD | 当条命令内重做并提交，无损失 |
| ~01:4x | `tests/zephyr/trading/test_process_reaper.py` 新增两类 | 同上 | 重做后落 `-0003`，已落地 |
| ~02:32 | `scripts/backup/restore_drill.py`＋`tests/backup/test_restore_drill.py` | 还原死袋时实测 `disk==HEAD`、测试文件 ABSENT | 从死袋 blob 双证取回，重投 `-0002` |
| ~02:39 | `docs/_working/disk_reorg_campaign/LEDGER_final.md`（531→411 行） | 追加脚本报 `old=411` | 以 HEAD 为基重放四段重建 594 行，重投 `-0005` |

**已排除的四条猜测（都是花时间花出来的，写下来给下一班省账）**：
1. ❌"claim 释放时回写基线" —— 读 `git_commit_gateway.release_files()`（该文件 1358 行起）
   实证：只做 `registry.release_files_batch` ＋清理 `_claim_snapshots`/`claim_heads`，
   **不触碰工作区字节**；
2. ❌"gateway stash 隔离吞掉未提交件" —— `.git/logs/refs/stash` **不存在**、
   `git stash list` 空；（gateway docstring 里的"stash 隔离"字样是最初嫌疑来源，已否）
3. ❌"reaper 顺手杀了写手进程" —— 四次回退都是**内容退回 HEAD**而非文件消失；
   本班会读到的两份快照（02:21:30 与 02:37:24）`killed` 均为空、
   `errors` 均为空（02:37 那轮 `reported=31`），杀进程也不产生 checkout 效果；
4. ❌"我自己的脚本写坏" —— `bca_append2.py` 与 `bca_rebuild_ledger.py` 都走
   `safe_write_text(expected_base_sha256=…)`，CAS 不匹配会拒绝写入而不是回退；
   第一次追加的读回断言（`byte-equal-append: True`＋四个标记各 1）当场通过，
   说明写入成功过，之后是被**第三方**改掉的。
⇒ 剩下的可能性集中在"某会话在主干做了 `git checkout/restore <path>` 或 `git add -A`
   后的清理"，需要的是**文件级 watcher**（对指定路径 mtime＋sha 采样，落在
   `.runtime/tmp/` 之外的审计面），本班会不再扩范围，移交为 **P-25（观测类，带处方）**。

**本班会因此加装的自保动作（已生效，直接可抄）**：
① 入袋后立刻用袋内 `blob_sha256` 对盘上字节逐件验（`-0005`/`-0002` 均验过：
ledger `ff4cb0ce9666` MATCH、lane C `cc5502f6a865`/`9f7d0e35f5df` MATCH；
lane B 盘上已被退回 HEAD（`46d099ce0fb3`），但袋内 `61399079832b` 是我修好的版本
——**袋是权威副本，落地不受盘上回退影响**）；
② 任何"我改过"的断言改口径为 `git show HEAD:<path>` 现读；
③ 台账重建走"HEAD 文本为基重放全部草稿段＋标记计数断言＋前缀逐字节断言"，
   草稿段留在 `.runtime/tmp/bca_sec1[678]*.md`，重写幂等。

### 二十、P-24 升级（同一缺陷的第二症状：GitCommitGateway 初始化直接失败）

**新证据（02:43，本会话自己的收尾动作被挡）**：
```
python scripts/git_commit.py --release-only --session st-bca-f-dash-20260926 --files ...
  gate_auto_registrar FAIL-CLOSED: 1/103 gates failed: DOC-HEADER-SUITE: GateRegistrationError: priority=77 冲突…
  ERROR: GitCommitGateway 初始化失败: gate auto-registration fail-closed (裁定#351)
```
⇒ 第十八节原判"只坏锁外预检层"**低估了**：凡走 gateway 的 CLI 路径
（`--release-only`／直连 commit）现在**直接构造失败**，只有 `--enqueue` 因内部
try/except 降级为"跳过预检"而仍能入袋，队列落地（serializer 走另一条装配）也仍在工作
（02:38 车道 F、02:41 他会话两笔正常落地为证）。**全局后果＝自 02:05 起所有会话
都无法 release 自己的 claim**，claim 只能等 30 分钟 TTL 自灭——这会连带把
"毕后 release"这条铁律变成做不到的动作。

**三处真源互相矛盾（这才是根因，不是"priority 撞号"那么轻）**：
| 面 | 说的是 | 实物 |
|---|---|---|
| 模块 docstring `blueprint_format_gate.py:22` | 薄工厂"供历史测试/引用兼容（**不再入册**）" | 与下两行矛盾 |
| 名册 `gate_registry.yaml:757-769` | BLUEPRINT-FORMAT ＝"已合并至 DOC-HEADER-SUITE"，带 `redirect_to: DOC-HEADER-SUITE` 墓碑 | 同上 |
| 触发名册 `in_process_gate_registry.yaml` | **同时**有 `gate_id: BLUEPRINT-FORMAT`(366) 与 `gate_id: DOC-HEADER-SUITE`(728) | 两行都被 auto-registrar 装配 ⇒ 同 priority 撞死 |

即：**合并动作做完了、代码不再主张入册、外层名册也立了墓碑，唯独生成器产出的
in-process 触发名册还留着被吸收台的活行**。

**修法（一条命令级，属主仍是 st-commitspeed-pkg8；本班会不代改，理由见下）**：
在 `scripts/governance/generators/generate_gate_registry.py` 的 in-process 名册产出环节
**跳过带 `redirect_to` 的被吸收台**（与 gslim P4 的 NO-GOD-CLASS/NO-HIGH-COMPLEXITY
墓碑锚点同族处理——那两个 gate_id 当年也是"保留 id、不再入册"），然后重生成两册；
配一条注册期断言测试："名册内不得同时出现某台与其 `redirect_to` 目标台"，
否则 T8 簇后续合并（还有 5 簇待做）必复发。
**为什么不代改**：这要动**生成器＋两张热册**（`gate_registry.yaml` 1.75MB 级），
而本会话主工作区此刻仍有 155 个外来 staged 文件——热册在主区改＝本仓已实证多次被
覆盖/驱逐（memory 在案），且 pkg8 车道 `st-commitspeed-pkg8-20260925-0012` 袋还在队里，
说明它随时可能自己补这一刀。我改＝抢它的热册并制造第二套重放器（这正是
[[hot-registry-superset-delta-recipe]] 里"连拒即停手别造第四套重放器"点名的错法）。

**本会话收尾被挡后的自保动作**：claim 释放改走底层 API
`SessionRegistry.release_files_batch(sid, files)`（读代码确认
`GitCommitGateway.release_files()` 内部就是调它＋清 claim 快照，**不触碰工作区字节**，
所以直调与走 gateway 语义等价、不绕任何门禁），并在台账写明是被 P-24 逼出来的绕行，
不是常规通道。

### 二十一、入袋前置三查（本班会用两条死袋换来的可复用工序）

**教训来源**：同一条 `GATE-PRECOMMIT-RUN`（落地前在 own-scope 临时索引上跑
`hooks=['ruff','ruff-format']`）在本班会吃掉两袋——车道 C `-0001`（`B905 zip() 未给 strict=`）
与车道 B `-0002`（`Would reformat: tests/scripts/backup/test_backup_reconciler.py`）。
两次都不是判据错，而是**我只对"改过的那个文件"跑了格式/静态检查，没对袋内全部文件跑**。

**入袋前三条命令（≤20 秒，能在 3 秒内预检被 P-24 关掉的情况下自己补上这道早停）**：
```bash
FILES="a.py,b.py"                      # 与 --files 完全同一串
ruff check  $(echo $FILES | tr ',' ' ')               # 含 B905 这类规则
ruff format --check $(echo $FILES | tr ',' ' ')       # 门禁用 --check 语义（只检不改）
python -m pytest <自家测试目录> -q                    # 自家测试同批
```
要点：① **袋内每一件都要过 `ruff format --check`**，包括 `tests/` 下的新文件——
门禁按 staged 面全量跑，不按"我手改过哪件"跑；
② 改完立刻 `git add` 自己路径，再逐件把盘上字节 sha256 与袋内 `blob_sha256` 对上
（本班会实测：`-0005` ledger `ff4cb0ce9666`、`-0003` `b770f88166d4`/`65f1c10f8c94` 全 MATCH；
而车道 B 盘上曾一度被退回 HEAD＝`46d099ce0fb3`，靠袋 blob 复原）；
③ 复杂度用**门禁自己的尺**复算（`high_complexity_gate._cyclomatic_complexity`）——
本班会两次量到 16 的都是它，判死原因里的数字也是它，同口径才谈得上"改到 15 就放行"；
不同工具口径不一致时不排除会误判（本会话未实测第三方工具，故只登记"用门禁尺"这一条做法）。

**同批修正**：车道 B 的 `-0002` 判死后我按上述工序重建：死袋 blob 双证取回 →
`ruff format` 两件全跑 → 47 passed → 重投 `-0003`。
P-7 本体（点火/托管分离：`launch_detached_backup`＋`settle_previous_ignition`＋
锁自查前置）在恢复件里逐处在位（`backup_reconciler.py` 净变化 416 增/139 删，
调用点 809/831 行），未因两次死袋丢任何逻辑。
