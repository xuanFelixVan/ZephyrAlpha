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
| E:\数据下载\研报 | 30,159 件/84.7GiB，对账 Copied=0（全部与 F:\zephyr_cold_corpusesearch_reports 同等；较 09-2x 对账 29,998 件自然增长）| 已验证冗余副本→**早删**（原排期 10-18），E 回收 84.7G |
| E 盘回收合计 | **+202.3GB（free 241.9GB）** | 两项删前均 zero-unique 复验 |
| E:\ZephyrAlpha | **非仓库拷贝**——仅 deals_events.txt（2.8MB/83,237 行）=QMT 模拟端 Deal.csv 变更看门狗活动日志（交易时段每 3s 一行，15:05 收盘后停）| 活盘桥生态**保留**；重定向日志路径入 bridge backlog（实盘四禁不碰运行中进程） |
| E:\数据下载 其余 ~53G | 产业链数据 12.44+P1归一 2.81 / 新闻文本 11.52 / 指数分笔 8.29 / ETF分钟 3.81 / A股zip 3.21 / 1分钟 2.73 / 财务 2.59 / LOF 1.28 / 5分钟 0.80 / tick缺口件 1.07 | **未删**——每数据集需对 CH(c1/c3)/冷库做 ingest 核验后才能定性，登记为 E 盘数据集核验工作包（下一班）；tick 缺口件大概率已冗余（缺口 09-21 已修验证） |
| E 盘软件/个人 | 7-Zip/Lightroom/VS Code/Miniconda/QMT 端/QQ/Quark/1127锦晖运动会等 | ✅ 按设计保留（E=软件+个人） |
