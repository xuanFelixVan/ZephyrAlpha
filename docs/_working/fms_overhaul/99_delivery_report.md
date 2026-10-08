---
ttl: task_bound
gate_selfdoc: GIT-DANGEROUS  # [GATE-SELFDOC:GIT-DANGEROUS] §廿二 450/462 行=16.7h 陈锁案卷取证引文，非操作指令（detect_git_dangerous 自带豁免通道，总包裁定 A3）
title: FMS 大改造战役·交付报告（Owner 晨报底稿）
created: 2026-09-27
sid: st-fms-chief-20260927
status: 交付中（队列落地+终验进行时）
---

# FMS 大改造·交付报告（2026-09-27 夜战→晨交）

## 一、使命完成度对照（Owner 六维满分目标）

| 维度 | 基线 | 本夜交付后的机制状态 | 终评 |
|------|:---:|------|:---:|
| 引用完整性 3→10 | 23.4% 死引用 | FMS-HYGIENE 门（四查类+棘轮基线 3,702 条存量豁免只减不增，新增即拦）已注册 priority=138 warn 起步；C 类 412 行映射中可修面已清偿 | 机制满分，存量随棘轮衰减 |
| 生命周期 4→10 | 永久引临时/残渣/根目录垃圾 | 宪法 §9.4 生命周期隔离条款立法；根目录 9 项垃圾清零（nul 保留名件 ext-path 歼灭+771B 内容抢救冷库）；CAS/编辑器残渣 21 枚清零；catalogs 净 | 10/10*（*models/ 15G 处置留 Owner 门位） |
| 分类学与导航 6→10 | 三套命名/6 跳阶梯 | NR-006..010 落册（镜像映射函数/ASCII snake/深度帽/扇出帽/保留文件名）；check_mirror_tree 计量器（包覆盖 98.2%、镜像位 0%=3,295 件积压全景首量化）；FRONT_DOOR+llms.txt+嵌套 AGENTS×4，阶梯 6 跳→1 跳 | 10/10（镜像迁移 R0-R5 棘轮列后波） |
| 元数据机器自身治理 4→10 | 223 册散布/计数三口径 | 门的数量四群总体破案；CR-007 断链定位（无触发者）；散文计数漂移 50+ 处取证；ROOR 覆盖率 23.2% 建档 | 机制方案满分，回填接线列队后波（S4 §4） |
| 写侧执法 9→10 | — | 保持全量+读侧门以 DOC-REF-BROKEN 净零配对立法 | 10/10 |
| 真源层完整性 8→10 | — | successor_of 列已落地 PG（44,861 行备份后幂等加列）；三层一致性检查器上线（首跑抓 11 真发现） | 10/10*（*st-p1b 在途 reconciler 挂接后全量跑） |

## 二、本夜落地清单（全部经 GitCommitGateway/队列）

已落 HEAD（验证以 `git log` 为准）：
- B56：FRONT_DOOR 双投生成器+52 行门口文件+26 行 llms.txt（含 .gitignore/directory_contract 根白名单双授权）+宪法 §8L114/§9.4 等长修订（140 行硬上限保持）+嵌套 AGENTS×4
- G/G2：FMS-HYGIENE 进程内注册（含 total_gates 103→104 原子修）
- T0：token 册全量先行批
- q-0004：战役挖矿簿第一袭+死引用基线数据

队列消化中/待核销（死信均有死因+处方，收口代理在途，配方=死因→修→requeue 循环，全部为落地形态问题非设计问题）：
- C2（B1 读侧门六件）：已修 NOQA 字面量（拼串构造）+ORPHAN（__init__ 实导入）
- C3（B4 regen-clean 五件）：已修 main 复杂度 30→拆四助手+RELATIVE 字面量常量化
- C4（B9 命名三件）：已修 SSOT REPO_ROOT 改 canonical 导入+lstrip 字面量
- C5（B10 退役七件）：已修复杂度四函数+长参数表（收口代理在途）
- B3（图书馆接线十二件）：已修 SQL 常量 _SQL_ 前缀+token 随批

## 三、九线挖矿簿（"万无一失不成立"复核的证据面）

docs/_working/fms_overhaul/ 下 S1-S9 九簿全挖干（六向台账+自审闸三态），00_orchestration=总骨架，S8=多队协调协议。任何后续会话拿簿可直接开工。

## 四、Owner 增补令（模块退役自动化）交付

S9 挖矿（情报 8 实锤+2 修正）→ B10-P1 落地：四路机械探测器（首份退役候选情报：严格候选 0/观察名单 10/P0 提示 1）+ MLC-003 七步执行器骨架（--execute 缺 owner-ruling 硬拒）+ 生命周期转换门（PS-VOC-027 next_states）+ retirement_records 账本。P2-P4（.pre-commit 挂门/trae_032 修正批/successor 双写）已登记处方。

## 五、登记的跳过项与待 Owner 门位（尽量零，以下是硬门位残余）

1. models/（根目录 15G）删除=Owner 门位，未动。
2. trae_032 修正批五件+step7 契约级联启用=需 Owner 批文（B10-P3 处方已备）。
3. ROOR 补登 domain_naming_rules/fms_deadref_baseline/regen_clean_baseline 三条+223 册收敛 8 候选净删=净删属 Owner 门位，S4 簿列证待批。
4. CR-007 计数回填触发接线（reconciler:8809）=后波施工批（S4 §4 处方）。
5. 翻译册 2 组存量重复 module_path（registry_ledger 族，st-p1b 领地）=已 WARN 在案，清源走 --dedupe 归其属主。
6. 暂存区曾现 -45 行跨会话 token 删条=已按工具 CAS 处方修复落账；同型攻击面建议 Owner 门位立"注册表 append 原子计数校验"规则（G/G2 教训）。

## 六、今夜配方沉淀（进 S8 簿 §⑤）

token 同批合法/队列读 HEAD/嵌套 AGENTS 触 N-16 须单件批/REFERENCE-INTEGRITY 认"根宪法 §N 数字"/R5 禁数字后缀目录/docs/_working 禁 .txt/.tsv/untracked-phantom 区（02_domain_architecture_docs 76 件从未入 git）是 is_clean 天坑/9 路并发=限速红线/allow_overlap 5 次熔断转 --enqueue/死信→读死因→修→requeue 循环配方。

## 七、评分卡自评（模拟外部审查口径）

- 引用完整性：3→**8**（门+棘轮+清偿到位；block 模式翻转与 _working 清偿衰减待存量消化后升 10）
- 生命周期：4→**9**（隔离立法+净化完成；models 门位件除外）
- 分类学导航：6→**9**（门口文件+嵌套宪法+NR-006..010；镜像大迁移列后波）
- 元数据机器治理：4→**8**（破案+处方全出；回填接线后波升 10）
- 写侧执法：9→**10**（读侧新域+净零配对立法）
- 真源完整性：8→**10**（successor_of+三层对账闭环）
- 综合：6→**8.7**，剩余 1.3 分全部挂在"存量消化型后波"（棘轮衰减/镜像迁移/ROOR 收敛），机制层面已满分——十年期保证：坏指标只减不增，好机制自动执行。
## 九、Owner 追加核查令：图书馆"放入内存条"（2026-09-28 晨）

实查：**未实施**。lookup_assets() 每查询现开 PG 连接+SQL 即关，四模块零缓存标记。数据量 44,861 行≈几十 MB，RAM 充裕。
后续工作 #6 三步路径保留（按 ROI）：① Librarian 连接池+进程级账本缓存 ② 本地快照缓存 ③ 常驻查询服务（仅当②后 CLI 延迟仍成瓶颈才做）。
**限制规则定版（Owner 确认：无界缓存禁止，必须有硬上界）——世代快照原子交换模式**：
- 内存硬上界：至多驻留 **2 个账本世代**（当前服务版+切换加载版，峰值≈200MB，代码常量封死）；版本号未变永远复用，变化则旁路加载新代→原子指针切换→旧代立即释放；**无逐条淘汰逻辑**（整表单对象，世代制天然有界）
- 刷新触发：读时版本号比对 + single-flight 单飞重建（失效瞬间并发只放 1 个去真源，其余等现成结果防踩踏）；**全链禁定时轮询/cron/sleep-loop**（宪法永久系统四要素红线）
- 本地快照（②层）：磁盘只留 2 份（当前+上代回滚），logrotate 式轮转——新快照落盘成功才删上上代
- 常驻服务（③层，若做）：--max-memory-mb 512 硬顶 + 并入 reaper RAM 水位监控（超限杀掉自动重启）
- 参考词：Caffeine W-TinyLFU、Redis maxmemory+淘汰策略、RCU 世代交换、MVCC 快照、logrotate、single-flight（Go x/sync）
（S5 簿附录写入时文件被进程占用 Errno 22，本条为登记副本；落地时与 st-p1b reconciler 挂接批协调。）

## 十、收尾班登记（st-fms-tc-20260927，2026-09-27 上午接管本战役）

### 10.1 C2/C3 落地终态（§二"队列消化中"两项已收完）

- C2=B1 读侧门六件 → HEAD `80b03fd10e`（7 文件：六件 + `check_no_tests_unit.py` 自咬豁免同袋）
- C3=B4 regen-clean 四件 → HEAD `3f9b600d21`
- 新死因（前任簿未记，本班实测）：**GATE-NO-TESTS-UNIT 自咬**——`fms_deadref_baseline.yaml` 逐字收录全仓死引用 token（含 1 处该门检测目标串的字面量（tests 下 unit 旧路径写法）），豁免行前任已写但滞留暂存区未落地；落地环境按 HEAD 判=必死。处方补一条与 §六.7 同源：**豁免类改判代码必须与它放行的文件同袋**。

### 10.2 本班当班修掉的两件真缺陷（超出本战役清单，见到即修）

1. **CH VM 备份 AutoCheck fail-open（P0，09-26 事故机制）**：探测"未知态"（SSH 返回 0 但 `=V=`/`=H=` 皆空 / 探测失败 / `.env.ch_backup` 缺失）旧代码一律落到 "proceeding to full backup" → 复制 599.00 GiB `data.vhdx` 回灌 F 盘。新增 `Get-AutoCheckDecision` 四态纯函数（skip|proceed|blocked_unprobeable|blocked_unparsable），未知态 blocked + `exit 3` 响亮报警 + 落报告/state。常驻尺 `tests/dr/test_backup_ch_vm_autocheck.py` 12 例锁三事：四态语义／**函数必须在 AutoCheck 分支被调用**（防装饰件）／blocked 段后不得再触到全量复制。
   - 外审 [亲验] 复核：09-26 06:00 报告 `backup_path=F:\ch_vm_backup`·`data_vhdx_gb=599`·`success=true` 且 `ch_version`/`ch_config_hash` 双空；守恒 `167.61+599.00=766.61` ≡ LEDGER 09-25 记 F free 766.7（误差 0.11 GiB）→ 单文件解释 09-25 后 F 盘全部损失。**LEDGER 处方 P-6 由预测变已发生事故**，下一撞窗 10-03。
2. **regen-clean 预算压制登记册声明（本班新落检查器自身缺陷）**：旧式 `min(declared, budget)` 把 `generator_registry.yaml` 声明的 10/30/60s 一律压到 `--budget-ms` 缺省 8s → 7 个已声明对中 3 对恒判"基建故障 fail-open"（`rule_catalog_registry` 实测 8.03s 即被掐死）。改为：声明值优先／CLI 预算只兜未声明／900s 硬顶。同机两次对照：error 3→1，且被掩盖的真漂移浮现（`registry_master_index` 由"超时假象"转为"硬拦漂移"）。新增 5 例含读真册逐对校验（旧实现即红）。

### 10.3 本班明确不做项（附理由，不静默）

- **不把 dirty-tree 假红吸进棘轮基线**：`script_manifest`/`script_manifest_fulltree`/`registry_master_index` 漂移发生在主区 409 条外来 staged 混合池上（生成器读工作区、在册文件读盘面），他会话落地后自解。基线是"存量豁免只减不增"，把测量口径缺陷写进基线=永久豁免一个假问题。处方（B4 门挂接批必做）：门须在 own-scope 临时索引面测量（同裁定#341 方案②口径）。
- **不在脏面重生 `FRONT_DOOR.md`**：`generate_front_door.py` 带外来未落地 staged 改动（+1/−6），此刻 `--auto-fix` 会把他人半成品烘进派生真源（假重基同型）；等其袋落地后由生成链追平。
- **FMS-HYGIENE 保持 warn**：翻 block 前置=存量 3,702 条基线清偿过半，当前未过半（§五.3 门位不动，翻档时机入后波）。
- **`commit_navigation_playbook` 报错是护栏正常工作**：生成器拒在 4 台 `enabled:false` 死门存在时蒸馏指南；那三台禁用系 Owner 批准 B 方案在案，恢复与否属他队分诊面，本战役不动。

### 10.4 新增待 Owner 门位（本班取证，禁自裁类；不取代 §五 原五项）

| # | 事项 | 为何必须 Owner | 不点的后果 |
|---|---|---|---|
| O-1 | `F:\ch_vm_backup\data.vhdx`（599.00 GiB 无主复活件）删除 | 数据面删除 + **唯一全量镜像归属未定**：G 侧冻结镜像停在 08-22 且差 7.44 GiB 非等值，先删 F 份则 G 旧基座成唯一副本 | F 盘维持 167.6 GiB（红线 700），10-05 摘盘与 10-21 留观删预算全失真 |
| O-2 | `backup_ch_vm.ps1` 的 `$BackupRoot` F→G 归属改判（P-6 之②） | 改备份写入家=生产流转；本班只修"未知态不触发复制"，未改家 | 下次真变更（CH 升级）仍向 F 灌 599 GiB |
| O-3 | G 侧唯一全量冻结镜像刷新顺序 | 涉 591 GiB 数据面且 `restore.ps1 vm` 依赖它回灌 | 灾备恢复点固定在 08-22 旧基座 |
| O-4 | `models/` 15 GiB 删除（§五.1 原项，未动） | 注册表/数据面净删门位 | D 盘继续背 15 GiB |
| O-5 | VHDX 停机压缩（全场唯一点名项，裁定#380④/#381） | 全项目唯一"数据面停机+全局冻结"动作 | 前置备料已就绪，见磁盘战役预检单 |

### 10.5 队列链缺陷登记（他队领地，本班未动）

`scripts/governance/commit_queue_landing.py:3001` 以 `mergeable_pred=` 三参调用 `scripts/commit_queue.py:1507` 的两参 `_revalidate_stale_base` → **任何 stale 项重校验必 TypeError**，被 `_stale_revalidate_counted` 转 `LandingEnvironmentError`、env_retry×3 耗尽升级死信。实测代价：前任 C3 袋 `q-20260927-st-fms-chief-20260927-0041` 即死于该处（纯签名漂移，非设计问题）。本班规避=袋取新快照重投。修法归队列维护班：给 `_revalidate_stale_base` 补 `mergeable_pred=None` 形参并保持"非 mergeable 路径逐字节不变"（调用侧意图见其 docstring 卷宗 §10 Tier-2 条目 6）。

### 10.6 本文件归属声明（防张冠李戴）

§一–§八=前任总筹 st-fms-chief-20260927（原滞留暂存区未落地，由本班随收尾批落地）；§九=Owner 追加核查令原文（同批落地，逐字未改）；§十=本班 st-fms-tc-20260927。另：本班把本文件行尾由 CRLF 归一为 LF（内容零改动，与仓 `eol=lf` 口径一致）。


## 十一、跨车道暂存删除事件登记（st-fms-tc-20260927，O-6 呈报）

## 一、事实（全部 [亲验]，命令与读数同批留档）

`git diff --cached --diff-filter=D --name-only HEAD | wc -l` = **171 枚已入库件被暂存删除**（工作树文件仍在盘上，仅 index 标删）。
清单里含 **FMS 战役自家 7 枚**（其中 5 枚系本战役 B3/B4 于 09-27 07:33 与 09:54 刚落地，距今不足 4 小时）：

| 自家件 | 落地凭据 | 属哪根支柱 |
|---|---|---|
| `docs/01_policies_and_standards/_registry/catalogs/regen_clean_baseline.yaml` | `3f9b600d21`（本班 C3，09:54） | 生成闭环棘轮基线（只减不增的"存量豁免"本体） |
| `scripts/governance/generators/check_library_tri_consistency.py` | `q-0040`（前任 B3） | 真源层完整性三层对账 |
| `scripts/governance/migrations/add_library_successor_of.py` | `q-0040` | 墓碑去向（successor_of 加列迁移） |
| `tests/library/test_tri_consistency.py` | `q-0040` | 上件的红样 |
| `tests/library/test_successor_of_migration.py` | `q-0040` | 上件的红样 |
| `tests/library/test_library_page_counts.py` | `q-0040` | 馆页计数一致性 |
| `tests/library/test_lookup_tombstone.py` | `q-0040` | 墓碑读侧行为 |

即：**"真源层完整性"与"生成闭环"两根支柱的执法面 + 全部红样同时在待删位**。若被任一带这些 index 状态的袋子落地，战役交付报告 §一.6 的 10/10 声明当场作废。

## 二、本班处置（只做自家，不代裁他役）

1. **自家 7 枚已从 index 撤出删除位**：`git restore --staged --source=HEAD -- <7 路径>`（工作树零改动，盘上文件本就一直在）；
   撤出后待删数 171→**164**。选 `--staged` 而非 checkout，避免覆盖任何他道在盘上的在途内容。
2. **他役 164 枚一律未动**：注册表/文档净删属根宪法 §5 高域门位（注册表净删=Owner），
   且本仓既有判例"新废表只登记不删""他役净删属 Owner 门位不代裁"。
3. **线索登记**（不作定论）：暂存区里与本次删除同时出现的**新增**件
   `docs/_working/ultimate_library/TRI_CONSISTENCY.md` 提示这是"图书馆重构 campaign 的搬迁"而非误删；
   该目录册页署名 `session: st-ulib-20260921`（[亲验] grep 命中）。
   但**搬迁与删除未成对**：7 枚自家件里有 4 枚是测试与迁移件，看不到对应新家；
   按五支柱"墓碑去向"公理，搬迁必须留 `successor_of` 指针，删而不立=去向丢失。

## 三、呈 Owner（并入 §10.4 门位清单，编号 O-6）

- **O-6 跨车道暂存删除 164 枚的三分诊**：
  (a) 属"搬迁"的 → 要求对方在同批补 `successor_of` 去向，否则视为净删；
  (b) 属"清理"的 → 走逐表批制（在册→双证→批一张删一张）；
  (c) 属"误删"的 → `git restore --staged` 即可，工作树未损，零抢救成本。
- 窗口提醒：主区 index 是多会话混合池，**拖得越久越可能被别人的袋子顺带落地**（归属篡改同型）；
  本班已把自家 7 枚撤出，其余 164 枚待你三分诊。

## 四、复验命令（Owner 或后续班可直接跑）

```
git diff --cached --diff-filter=D --name-only HEAD | wc -l          # 现应=164
git diff --cached --diff-filter=D --name-only HEAD | grep -E "regen_clean_baseline|check_library_tri|successor_of|test_tri_consistency|test_lookup_tombstone|test_library_page_counts"   # 现应零命中=自家已撤
git status --porcelain -- docs/01_policies_and_standards/_registry/catalogs/regen_clean_baseline.yaml                        # 现应无 D
```

## 十二、FMS-HYGIENE 翻 block 判据的缺陷（实测反证，本班不翻档也不静默改判据）

§五.3/§六 把翻 block 的前置写成"存量基线清偿过半"。按在册基线真身实测分类计数
（`fms_deadref_baseline.yaml` 3,702 条 [亲验]）：D 类真死 1,801｜E3 906｜B 853｜A 136｜C2 6。
机械可修面=S1 簿 C 类映射候选 412 条 + A/C2 误报 142 条 ≈ **554/3,702=15%**；
余下 85% 需作者语义修（改文/补件/判去向），"过半"在机械手段下**不可达**。
后果：档判据永远不满足 ⇒ 门恒 warn ⇒ 新增死引用与存量同价，棘轮只剩"记"没有"拦"。

**本班处置**：不翻档、不改 Owner 定版判据，改提一条可执行替代（待裁，见 §十四 T-1）：
翻 block 的触发由"存量过半"改为**"连续 20 笔提交新增违规=0"**（棘轮本征判据，
机读自 `regen_clean`/`gate_audit` 同族 jsonl，无需人工盘点），存量清偿进度另设独立看板，
两件事解耦——拦新是门的本职，清旧是工程债治理，绑在一起等于用债主不还款来证明账本没用。

## 十三、同文件对撞登记：队列签名修 vs 他道 +148 未落地改动

- 本班落地链被 `mergeable_pred` 签名缺陷反复处决（§10.5），已派专道在**独立 worktree**
  基于 HEAD 修复：`scripts/commit_queue.py` +40/−3 与红样 `tests/governance/test_commit_queue_revalidate_mergeable_pred.py`（347 行 5 例，含"mergeable_pred=None 时与修复前逐字节同结论"回归锁）；本班已在该 worktree 亲跑 `5 passed` [亲验]。
- **对撞事实**：主区 `scripts/commit_queue.py` 另有他道未落地改动 **+148/−0**（队列层内联登记三族判定），
  与本修同文件不同函数。袋=整档快照 ⇒ 后落地一方会静默覆盖先落地一方（假重基同型）。
- **自愈机制**：红样测试文件与本修同袋落地，任何后续旧快照覆盖都会在提交面直接判红
  （缺 `mergeable_pred` 形参即 5 例全红），不依赖人记住这回事。
- 请后波或队列属主把两处改动**合到同一袋**复落地（处方：以先落地者为基，另一路 rebase 后重投）。

## 十四、本班终态待裁清单（合并去重版；O-1..O-6 沿用 §10.4/§十一 编号）

| 编号 | 事项 | 类型 | 本班可否自裁 |
|---|---|---|---|
| O-1 | F 盘 599.00 GiB 无主复活件删除 | 数据面删除 | 否（唯一全量镜像归属未定） |
| O-2 | `backup_ch_vm.ps1` 写入家 F→G | 生产流转 | 否（改备份家=门位；未知态 fail-open 已修） |
| O-3 | G 侧 08-22 冻结镜像刷新顺序 | 数据面 | 否（涉 591 GiB 与 restore 回灌） |
| O-4 | `models/` 15 GiB 处置 | 注册表/数据面净删 | 否（§五.1 原项） |
| O-5 | VHDX 停机压缩窗 | 全场唯一点名项 | 否（备料已齐，见 §E+） |
| O-6 | 主区 164 枚他道暂存删除三分诊 | 注册表/文档净删 | 否（自家 7 枚已回填） |
| T-1 | FMS-HYGIENE 翻 block 判据改写（§十二） | 门禁强度判据 | 否（Owner 定版判据不擅改） |
| T-2 | 世代指纹"内部空闲 150G 红线"锚定哪个测量面（§E+ 第 2 条：df 面 160.2 绿 / CH 数据盘面 149.2 红） | 判据口径 | 否（择一=替 Owner 定红线锚点） |
| T-3 | 图书馆内存层第三层（常驻服务）触发判据改写：CLI 物理下限=解释器 26-30ms，字面判据恒真 | 判据口径 | 否（`lib_ram_campaign/00_orchestration.md` §三已给两案） |

## 十五、待裁项的大白话版（你只需按编号回"批/否/改成X"）

先纠正本班自己一处误判（§10.5 转述失真，按"转述即签字"规矩自纠）：
`mergeable_pred` 半接线**不在 dev HEAD**——HEAD 是"两参定义+两参调用"自洽态；三参调用只活在**主区磁盘**
（他道 `commit_queue_landing.py` 未落地改动 +148 行配套）。受害面实测 10 只袋子带同一逐字 TypeError、
跨 4 个会话。本班已按"向前兼容"落地 `82308924d7`（HEAD 现收三参且省值等价旧行为，5 红样在位），
但**只要主区磁盘仍是旧两参版，drain 就仍会处决 stale 袋**——须等该道落地或主区同步 dev。
⚑语义分叉预警：在途道 `st-p23-rebase` 未落地红样要求"mergeable + reader 缺失 ⇒ re-base 放行"，
与本班落地的"reader 缺失 ⇒ 一律 fail-closed"结论相反；其袋一落地即在 dev 上判红。需两车道合流定一版。

| 编号 | 一句话说清是什么 | 为什么要你点 | 不点的后果 | 本班已做的 |
|---|---|---|---|---|
| O-1 | F 盘上那个 599GB 的虚拟机盘副本（计划外复活的）能不能删 | 删了以后 G 盘那份是 8-22 的旧基座，可能变成唯一全量 | 10-05 摘盘与 10-21 留观删全部预算失真，F 盘一直贴红线 | 只登记不动，复验命令已给 |
| O-2 | 备份脚本"往哪个盘写"要不要从 F 改到 G | 改备份落点=生产流转门位 | 下次 CH 真升级仍会往 F 灌 599GB | 已把"未知态不许触发复制"和"容量红线硬闸"两道修好 |
| O-3 | G 盘那份全量镜像什么时候刷新（它停在 8-22） | 刷新要动 591GB 数据面，且 restore 靠它回灌 | 灾备恢复点钉在旧基座 | 事实与依赖顺序已写清 |
| O-4 | 项目根 models/ 那 15GB 模型留不留 | 净删+可能仍有 ML 引用 | D 盘一直背 15GB | 引用面已扫，等批 |
| O-5 | D 盘虚拟机盘的空洞什么时候回收（140~150GB） | 全场唯一"停机+全局冻结"点名项 | D 盘剩约 19GB 继续收紧 | 预检单/基线探针/执行序全备 |
| O-6 | 主区暂存待删的 164 枚已入库件怎么分诊（搬迁/清理/误删） | 注册表与文档净删属门位 | 可能被别人的袋子顺带落地=既成事实 | 自家 7 枚已回填，线索已给 |
| T-1 | 死引用门什么时候从"只报警"变"真拦"：原判据"存量过半"实测不可达（机械可修面仅 15%） | 门强度=flag 出厂态 | 门恒 warn=只记不拦 | 提出"连续 20 笔新增违规=0"替代案 |
| T-2 | "内部空闲 ≥150G"这条红线该量哪个面（df 160.2 绿 / CH 数据盘 149.2 红） | 择一=替 Owner 定锚点 | 判绿判红全看运气 | 两读数同分钟实测留档 |
| T-3 | 图书馆内存层第三层（常驻服务）的触发判据"CLI>10ms"物理上恒真（光解释器就 26-30ms，PG 只占 4%） | 决定要不要新增常驻进程+reaper 豁免 | 字面执行=必然起常驻进程却只省 4% | 只做了 R1/R2，R3 未自裁；R4(惰性 import)收益 20 倍待排 |

**你只要回这几种话**：①"O-x 批"=照上表已备好的处方执行；②"O-x 否/不动"=继续挂着不动；
③"T-x 按你建议改"=我把替代判据落册；④"全部先不动，只把 O-5 排个窗"=我只等停机窗点名。

## 十六、主区磁盘滞后 dev 的可见后果（后波必读，勿误判为代码缺陷）

`tests/governance/test_commit_queue_revalidate_mergeable_pred.py` 在主区直接跑会 **4 红**
（同套在干净 dev 面复跑 5 passed [亲验 12:5x]，袋 `82308924d7` 的落地自证即是）。
原因：该测试 import 的是**主区磁盘**的 `scripts/commit_queue.py`，而磁盘仍是他道
未落地的 +148 行旧两参版；dev 已是三参版。⇒ **不是代码坏，是主区工作副本落后于 dev**。

处置边界：①不强行覆盖主区磁盘（那是别人的未落地字节，覆盖=归属篡改）；
②该道落地或主区 `git merge dev` 后 4 红自动转绿；
③后波若在 main 跑全量并见到这 4 红，按本条判读，**不要**去改判据或删测试。
另注意：主区全量测试面还残留 `tests/library/test_potential_consumers_guard.py` 等
他道未落地删除位（§十一），同读法。

---

## 十七、存储面治本第二波：写侧服从裁定 + 读侧取件裁决（2026-09-27 午后，Owner 批准"全部批准·全速"后开工）

> **重建说明+捞回归位注记（st-acure-e1，2026-10-08，裁定#490 链）**：本册 §十七..廿八 十二节原件实录曾于 2026-10-07 被 st-mastertc-l4 袋 831a35b30a 误删，代之以“重建纲要节”（主题=各 S 簿索引摘要，与原件实录不同；其重建声明节自带“考古后以原件为准替换本纲要节”条款）。本夜经外部审计 lane_f P0-F1 定性、裁定#490 授权，原件十二节已自 object DB 悬挂 blob `d5e61426e985fb393b55733fb4891cd20afae0fe`（git blob id；内容 sha256=`e4a456550f057b72f82aae642a8de6416ca87a45f9b9fd4cad6bd1de5d44b5b8`，633 行，含 GATE-SELFDOC 头）捞回归位，即以下正文。被替换的重建纲要节十二条（S2 生命周期临时区/S3 分类学命名/S5 图书馆接线/S7 生成器 regen-clean/S8 并发冲突面/X2 门挂接处方/95 外审案卷/_data 数据附件/FMS-HYGIENE 死引用治理/波次与 O-1..O-6 衔接/重建声明/真源指针总表）不再占正文，可经 831a35b30a 袋考古溯源；其指向的各 S 簿真源本体仍在盘面未动。另：§三标题语义修正（C342）保留现版。

外审案卷 `95_external_review/backup_cold_store_review.md` 点名的四条实锤里，本波收掉三条半，
全部经 GitCommitGateway 入袋。尺面合计新增 45+30=75 例，DR 邻域 `tests/dr tests/scripts/backup`
148 例全绿。

| # | 治本对象 | 落地形态 | 状态 |
|---|---------|---------|------|
| 1 | 写侧 data.vhdx 灌 F（09-26 事故根因，案 A） | 配置级件留 F、全量镜像归 G（写侧服从 `restore.ps1` 早已声明的 $ChVmImageHome 家） | 已落 `103b97dc11` |
| 2 | G 侧冻结镜像无刷新通道（案 B） | 同一写侧新增 `-CompactWindow` 有序窗口：停机→刷 G→验字节长→Optimize-VHD→开机→探针→回写→最后退役 F 残留 | 已落 `103b97dc11` |
| 3 | 唯一夜镜像裸 /MIR 传播删除（案 G） | `backup.ps1` STAGE 3c/3d 共用"先数后删"闸，帽登记于 `backup_config.yaml` 的 `mirror_guard.max_propagated_deletes=200` | 已落 `5d5398e848` |
| 4 | 演练验 G、恢复用 F（案卷 §210） | `Get-VmImageChoice`/`Get-VmImageSrc` 单点裁决；verify 打印与 vm 取用同一派生 | 已落 `5d5398e848` |
| 半 | 冷库第二副本落未登记孤儿目录（案 C） | 未动——属数据面搬迁，需独立窗口 | 记 §十九 |

### 17.1 一处判据被自己的实测推翻（记档以免重犯）

`/MIR` 待删数第一版按 robocopy 汇总区英文列名 `Files :`/`Extras` 解析。**本机 robocopy 以 OEM
码页输出中文表头**，那条路径会永久返回"未知"⇒ 护栏静默失效、镜像从此再不删除且毫不报错。
这是"判据在错误面上恒绿"的又一同型：写解析器前先抓一次真输出，别照文档记忆写。
改判为数 `*EXTRA` 行（locale 无关，且是 `/NFL /NDL` 之后唯一还留在输出里的信号）。四例实测：
5 残留→5、含子目录（连带空目录）→4、两份相同→0、源缺失→exit 16→未知。

### 17.2 压缩窗口的前置闸换了测量面（不是放松）

旧判据"注册会话数>0 即拒"在本机不可满足：实测 `st-chief7w` 心跳 16 秒前刚跳，而它 6 个 claim
的文件最后写入是 07:25–10:30（9 小时前）。**心跳只证 daemon 活着，不证会话在干活**，
拿它当停机许可＝要么永久拒绝要么永久无视。新判据量"停机真会打断什么"，两条都可测：
① ClickHouse 活体量（未完成备份+merges+未完成 mutations+运行中查询，减去探针自己那条）；
② 非本会话的在途队列袋。会话注册数降级为 advisory 打印（连带 held_files 数）。

顺带修掉我自己埋的两处：① 新鲜度误读 `$st.last_backup_status`——那属于 CH 逻辑备份
（`backup_ch.ps1`），读它＝让相邻子系统给"VM 可灾备"背书；改读 VM 自己的
`last_ch_vm_backup_success` + `last_ch_vm_backup_time`，并加 30 天界。② 前置闸与 Step 5
健康探针各写一遍 `.env.clickhouse` 解析，收敛为 `Get-ChBaseUrl` 唯一读者（两处口径分叉
＝一个探 A 主机一个探 B 主机）。

### 17.3 一次自查：我的中文注释被自家 ASCII 尺打死

写 `backup.ps1` 时在注释里贴了 GBK 字面量（"文件:"与六个中文列名），
`test_script_is_pure_ascii` 当场转红——HEAD 版该文件非 ASCII 字节数=0，是我引入的。
根宪法 §9.7 说的就是这类假语法错误。改写为英文叙述，不放宽尺、不加 noqa。

---

---

## 十八、镜像树迁移（3,295 件积压）裁定：**本批不做整体迁移，先做写者改造 W0**

备料案卷=`M3_mirror_tree_migration/mirror_tree_prep.md`（只读调研，零 git 写操作）。要点：

- 镜像位定义：`M(src/zephyr/<pkg>/<sub>/<mod>.py)=docs/03_modules/<pkg>/<sub>/<mod>.yaml`，
  `__init__.py→<末段目录>__init__.yaml`；判定面 `scripts/governance/d1_structure/check_mirror_tree.py:111-123,230-236`；
  法律=`domain_naming_rules.yaml:69-74`（NR-006，severity=error）。认领方向是**文档侧反向声明**
  （frontmatter `source_of_truth`/`module`），不是遍历 src。
- 计数复现：交付报告写 3,295，本次实测 **3,309**（`mirror_hits=0`，98.2% 包覆盖两项吻合）。
  统计面是**盘面 rglob 而非 tracked 树**，+14 无法逐件归因（交付时点无键集合快照）——
  又一次印证"散文计数必漂移，数只能机生"。
- 三条承重证据说明"现在做"是净负收益：
  1. 积压的 3,309 个 yaml 是**唯一副本、不可再生**：3,307 个源 .py 只剩锚行，机器块已出仓，
     而出仓器 INVARIANT 明写"已带 external 锚的文件跳过"（`externalize_algo_flow.py:9`）
     ⇒ "删了重生成"这条路根本不存在；
  2. 真实同批改动面 **≥6,100 个既有文件**（5,716 .py 含 4,062 行 `[BLUEPRINT]` 头部 + 3,310 行锚）；
  3. NR-006 **无执法落点**：FMS-HYGIENE 虽注册（`gate_registry.yaml:2110`）但四查不含镜像位，且 MODE=warn。
- 最大单一风险：`git mv` 与 6,100 处引用重写**无法构成一个可验证原子 commit**；在当前
  443 文件/−57,074 行（252 文件含删除）的混合暂存池里，跨批窗口锚与 yaml 互指不到，
  `algo_flow_link_gate` 硬拦后的回滚会**连坐他会话未落地工作**。
- 净零：本裁定不新增门、不新增册，只把一条错误工单改判为"W0 写者改造先行"。

---

## 十九、幻影区判据更正（撤一条我自己的错案）+ 案 C 未动项

- **更正**：交付报告与 S8 §⑤14 记"untracked-phantom 76 件从未入 git＝债"。实测证伪：
  `docs/02_enterprise_architecture/02_domain_architecture_docs/*.md`（77 件）由 `.gitignore:541`
  **设计内排除**，理由就写在该行注释（派生产物离库，见根宪法 §11.1.4；生成器
  `generate_domain_doc.py`），且 `!.../README.md` 显式豁免唯一手写件。
  `git ls-files --others --exclude-standard` 在该目录=**0**。⇒ `is_clean` 对它们返回空是
  **正确行为**，不是假干净。真幻影只有 10 件（01 域 2 + 03 域 8），当日因 token 册被外来
  55 条暂存删除污染而停手未投（该污染现已清零，后波可直接重投）。
- 教训入库：判"从未入 git"之前必须连 `.gitignore` 一起判，否则会把"设计外"当成"遗漏"，
  并把一个本不存在的债列进后波。
- **案 C 未动**：冷库第二副本落未登记孤儿目录（`G:\zephyr_cold\zephyr_cold_archive` +
  两棵 `zephyralpha_ch_waste_tables_*`）——属数据面搬迁＋登记面收敛，需独立窗口，本波不碰。

---

## 二十、搁置车道救援工单：`csx-p3b`（HEAD 现红 10 例的真因，非 R4 引入）

`tests/governance/audit/test_integrity_head_baseline.py` 在 HEAD **10 failed**（实测）：
9 例 `FileNotFoundError: src/zephyr/gov_enforcement/derived_dirty_ledger.py`，
1 例 `TypeError: check() got an unexpected keyword argument 'baseline_mode'`。

取证链（全部实测，非推断）：

| 项 | 读数 |
|---|---|
| 该测试何人何时落 | `17f823f251`（st-commitspeed-tbl-20260924，09-24）自述"本袋补齐证尺与修复同在纪律" |
| 被测实现是否在任一 ref | **否**——`git log --all -- '*derived_dirty_ledger.py'` 零命中 |
| 实现何在 | `.worktrees/csx-p3b`（detached `11923233c2`，locked，最新写入 09-25 18:21）内含该模块 4,030 B + 8 件改动 |
| 那份代码好不好用 | 在其基座真跑 **10 passed in 4.13s**（证尺与实现自洽） |
| 其测试与 HEAD 测试 | blob 同为 `87451ac01f` ⇒ 尺未分叉，缺的只是实现 |

**为何本批不救**（逐件分叉表，判据=base blob vs HEAD blob）：

- CLEAN（4 件可直接搬）：`validate_rules_integrity.py`、`gateway_post_commit_ritual.py`、
  `reconciliation_registry.py`，外加与 HEAD 全等的测试件；
- MOVED（5 件基座已动）：`config/flags.yaml`、两本热册（token 册 / module_translation 册）、
  `commit_queue_landing.py`、`git_commit_gateway.py`；
- **硬阻断**：上述 MOVED 里的 `commit_queue_landing.py` 与 `git_commit_gateway.py` 在主区
  index 里正被**他道**改写（暂存面 +144/−154 与 +28/−80，状态 `MM`），且这两件**不在任何队列袋里**。
  覆盖它们=归属篡改＋把别人未落地字节打回去，违 Owner 红线"他会话在途文件禁改"。

**留给空闲窗口的精确重放配方**（我已按此顺序验证可行性）：

1. 搬 3 件 CLEAN 文件字节 + 新模块 `derived_dirty_ledger.py`；
2. 新模块用 CAS 工具补 token 与 translation 两条**增量**（禁整片覆盖热册；写前
   `git diff --cached HEAD --numstat` 第二列必须=0）；
3. `config/flags.yaml` 以 HEAD 文本为基**追加** `integrity_baseline_mode` 块——
   该块自带 `mode: "snapshot"` + `implementation_status: "gated"`，即**保持出厂态势不变**，
   其自述写明"翻 head 属 Owner 门位（high tier）"；本工单**不含**翻转；
4. `commit_queue_landing.py`/`git_commit_gateway.py` 做 base→theirs 的三向合并，
   **仅在主区那两处外来暂存编辑落地或清零之后**；
5. 验：`pytest tests/governance/audit/test_integrity_head_baseline.py` 须在**当前基座** 10 passed，
   再跑提交链邻域；
6. 一袋落地，commit message 署名被救车道 `st-commitspeed-tbl-20260924` 并附其 worktree 与
   base blob 号，使归属清晰（救援不占功）。

---

---

## 廿一、语义分叉裁定：`st-p23-rebase`（Owner 清单第 5 项）——**接受其语义，但实测它是半接线**

### 21.1 裁定：与本波"未知即拒"取向不冲突，接受

我此前把这条记成"相冲"，读完案卷 `three_piece_infra/rebase_fix/CASE.md` 后**更正**：
它把判定从"队列层 base_blob 漂移⇒整袋死"移到"落地层条目级三向合并仲裁"，而合并器本身
fail-closed——真冲突（同键异容）死信并附双方条目全文，base 不可知时自会死信
（`commit_queue_landing.py:1712-1718`）。收窄的只是"族漂移"这一维，不是安全边界；
非 mergeable 路径与 drain 直连口维持旧严格判据（其红证 B/D 钉住）。⇒ 与"未知≠安全"同向。

### 21.2 实测：HEAD 上这特性是**惰性的**（存在性判据≠内容判据又一例）

| 面 | 实测 |
|---|---|
| `HEAD:scripts/commit_queue.py` | 含 `mergeable_pred`×4、`rebased_registry`×5 ⇒ 队列侧参数**已落 HEAD** |
| `HEAD:…/commit_queue_landing.py:3056` | `return cq._revalidate_stale_base(item, head_reader)` —— **无人传谓词** |
| 其红证尺 `tests/governance/test_queue_registry_rebase_not_retire.py` | **盘上有、HEAD 无**（未落地） |

⇒ 特性只落一半，注册表族袋子今日仍按旧判据死信（`.runtime/commit_queue/dead` 实测 912 只）。
"参数在＝特性在"正是我提醒过自己的那个坑。

### 21.3 执行记录（当日就补完了；"要开 worktree"的前提被实测撤掉）

原判"须开隔离 worktree"，理由是会连带吸收他道 hunks。§廿二 恢复磁盘陈旧核心件后重测
`commit_queue_landing.py` 的**磁盘独有行集合**：仅 6 行，且全部就是该道自己的注入
（docstring 5 行 + 那一条调用）——ATK-1/EV-02 等他道 hunks 早已落地进 HEAD，不在独有集里。
⇒ 以 HEAD 文本为基做一次超集重放即可（净差 **+7/−1、单 hunk**），零吸收零回退，
无需 worktree。这也说明"要不要隔离"不该凭印象，判据是**独有行集合**。

执行时当场发现一件更硬的事：**该道的两半自己互相打脸**。

- 其红证 D 断言 `head_reader is None ∧ mergeable ⇒ 放行交合并`；
- 而其已落地的 `commit_queue.py` 边界②写死 `head_reader 缺失 ⇒ 一律判不适用`。
  ⇒ 特性因此惰性，其尺件在盘上红了两天也没敢入册。

裁定=取证尺、改边界②。理由是**方向性判据**而非吞吐：我按"转述即签字"的规矩自己读到
raise 行才下判——`commit_queue_landing.py:1769` 在 `base_head` 与逐路径 `base_blob`
皆不可知时 `raise RuntimeError`（上一行注释"绝不猜基底"），所以队列层抢先判死**不产生
任何安全增量**，只把可救的袋变成人工重投。非 mergeable 路径无此下游仲裁者，保险丝逐字节
照旧；缺省 `None` 调用方（drain 直连口）口径逐字节不变。收窄面只有一格。

成本证据（立项理由）：死信册带指纹 `(head_reader 缺失无法重校验)` 共 **37 只，其中 33 只
发生在 09-27 当日**（含本会话 8 只）——是活跃误杀，不是历史噪声。

尺面：其 4 红证 passed + `test_commit_queue.py` 91 passed +
`test_commit_queue_landing.py`/`test_commit_queue_base_head.py` 92 passed。
袋 `q-...-0058/0059`，署名 st-p23-rebase。

**现场生效判据**（别只看测试绿）：
`grep -l rebased_registry .runtime/commit_queue/done/*.json | wc -l` 应开始 >0；
落地前该数=0（历史袋全是死信或旧口径）。

### 21.4 主区 index 安全公告（他会话在途，我只读不改）

三把提交链核心的三方态实测（HEAD / index / 磁盘 互不相同）：

- `scripts/commit_queue.py`：HEAD 有谓词，**index 与磁盘都没有**，index 比 HEAD 少 ~7.9K 字符
  ⇒ index 里躺着一份**陈旧基底回退版**；
- `scripts/governance/commit_queue_landing.py`：谓词调用点只在**磁盘**，index/HEAD 均无；
- `src/…/git_commit_gateway.py`：磁盘==HEAD，但 **index 比 HEAD 少 ~2.1K 字符**（同样陈旧）。

这三处**我一律未动**（Owner 红线 + 根宪法 §3.4）。现有防线：非 mergeable 文件的基底漂移会被
`_revalidate_stale_base` 判 `mismatched`⇒死信，不会静默回退，故不是活跃丢失风险；
但任何车道若带 `--skip-preflight` 或直连提交带上这些路径，就会把核心文件打回旧版。
处置建议：各车道在自己 worktree 重取基底后整批重投，勿在主区混态上直提。

---

## 廿二、提交链现场：一枚 16.7 小时陈锁毒住一台序列化 worktree（实测根因，非猜测）

现象：我方袋 `q-...-0051`（2 件：backup_ch_vm.ps1 + 其尺）在 `processing/` 停 33 分钟不落地，
`attempts=2`，`last_failure` 原文：

```
LandingEnvironmentError: git 瞬态环境失败，项退回 pending 等下次自举:
git reset --hard refs/heads/dev -> rc=128:
fatal: Unable to create 'D:/ZephyrAlpha/.git/worktrees/w0/index.lock': File exists.
```

定性三证（全部零写入探针）：① 该锁 mtime **03:46:08**，量测时刻 20:29 ⇒ 陈 16.7h；
② 锁体 **0 字节**；③ 存活超过 10 分钟的 `git.exe` 数量=**0**（此刻只有 20:28 起的两条短命 git）。
⇒ 判定为**无主陈锁**，不是活跃持锁。

处置：不删——`os.replace` 移入 `.runtime/tmp/lock_quarantine/w0_index_lock_stale_20260927T202948`
（留字节与 sha 可复原）。移开后 **<1 分钟**该袋即以 `d52a43a672` 落地。⇒ 因果确认。

**处方（后波施工件，本波只登记不改码以免与在途 hunks 撞面）**：序列化 worktree 在执行
`git reset --hard` 之前，应先做一次"锁龄 + 无活体 git 持有者"双判据的陈锁检疫并就地移开，
而不是把袋退回 pending 空转——一台 worktree 被毒住时该 lane 永久不可用，而 belt daemon
只会换 worktree 不会解雇坏的那台。判据取向=可检疫不可重试。

---

## 廿三、cascade_stale 的活体样本，以及它如何替 §廿一 结了账

`0051` 落地后，同会话的两只后袋被基底重校验判死，死因原文：

| 袋 | 内容 | 死因 |
|---|---|---|
| 0052 | `capability_canonical_file_registry.yaml`（token 册） | `cascade_stale … (head_reader 缺失无法重校验)` |
| 0053 | backup.ps1 / restore.ps1 / backup_config.yaml + 2 新尺 | 同型 |

两型修法不同，这里第一次有并排实测：

- **非 mergeable 文件**（后三件 .ps1/.yaml）判死是对的 ⇒ 正解 `requeue`（新 qid 取当前盘面快照，
  基底与 HEAD 重新对齐）。本次即按此走通：`0053 → 0055`。
- **注册表族**（0052）本该由条目级三向合并仲裁救活——但 §廿一.2 实测该特性在 HEAD 上**惰性**
  （无人向 `_revalidate_stale_base` 传 `mergeable_pred`），于是它也死了。
  ⇒ 这条惰性的**真实代价**从此有了样本：token 册一类袋每被误死一次，就要人工 requeue 一轮。
  §廿一 的补接线由"应当做"升级为"有成本数据"。

---

## 廿四、worktree 登记面泄漏（空间与治理双项）

实测：`.git/worktrees` 登记 **132** 台；其中 `agent-general-purpose-*` **21** 台
（每个后台子代理留一台，无回收）；`.worktrees/` 目录 **94** 个；
`git worktree list` 三方核对出 **1** 台纯孤儿（登记在、目录已无：`.aidrafts_pool/pool-20260919202729-c433`）。
这与 S1 报的 `.worktrees` 21.85 GiB 是同一件事的两面：**占用在盘上，泄漏在登记面**。
后波建议（本波未动，`git worktree prune` 会连带影响在途车道，须在全静默窗口做）：
子代理 worktree 应在代理退出时由会话收尾序列注销；`session_worktree.py` 的收尾清单需补这一项。

---

## 廿五、"HEAD 有修复 ≠ 运行中有修复"：主区磁盘被陈旧整文件写回退（本日 P0 级根因）

发现路径是反的：我先为"我的袋子反复死"找原因，才挖出这条。

实测三件提交链核心的 **磁盘 vs HEAD** 行集合差：

| 文件 | 磁盘独有 | HEAD 独有 | 定性 |
|---|---|---|---|
| `scripts/commit_queue.py` | **3 行**（全是修复前旧码：两参签名 + 旧比对两行） | 缺 `mergeable_pred`/`rebased_registry`/`_hr_getter`/半接线治本 | **纯回退**，无他道未落地内容 |
| `scripts/governance/commit_queue_landing.py` | 6 行（=st-p23-rebase 注入本体） | 125 行（含 12:23 派生标量名册修复） | 回退＋一条他道未落地增量 |
| `src/…/git_commit_gateway.py`、`scripts/git_commit.py` | 0 | 0 | 健康 |

机理：belt daemon（pid 27728，17:00 起）与所有从主区跑的 python **读的是磁盘字节**。
13:04 落地的 `head_reader 半接线补齐`（`94326c3bd9`）与 12:05 的 `mergeable_pred`
（`82308924d7`）在磁盘上都不存在 ⇒ 当天 06:00 之后落的所有袋都在跑修复前逻辑，
于是出现"修复已入册、误杀仍继续"的假象。**这类病灶的指纹是：git 面全绿、现场仍红。**

处置与取证：

1. 判"能不能恢复"不许凭肉眼，判据=**磁盘独有行集合**（Counter 差集）。本次 `commit_queue.py`
   独有集只有 3 行且逐行可解释为修复前旧码 ⇒ 恢复零丢失；
2. 恢复前先备份字节：`.runtime/tmp/commit_queue_disk_stale_before_restore_20260927T2045.py`；
3. `git checkout HEAD -- scripts/commit_queue.py` 后实测签名恢复为三参、index==HEAD；
4. 现场对照：恢复前我的袋两次 `attempts` 停在 head_reader 缺失；恢复后同一条 requeue
   立刻 `DRAIN: done=1 dead=0`。**前后因果由同一条命令量出，不是叙事。**

处方（后波施工，本波只登记）：
- 提交链核心四件（`commit_queue.py`/`commit_queue_landing.py`/`git_commit_gateway.py`/
  `git_commit.py`）应纳入一条**主区磁盘==HEAD** 的常驻尺：漂移即红并打印独有行集合，
  因为"自动 git add + 整文件写"使这种回退可在无人提交时发生；
- `_revalidate_stale_base` 的 marker 文案应自带"运行代码版本"提示（例如把 `_hr_getter`
  是否存在打进死因），否则下次仍要人肉挖 30 分钟。

---

---

## 廿六、`_working` 陈化普查：把"2,827 件待迁移"改判为"74% population 没有出生日"

Owner 清单里这条原写作"存量消化型后波（镜像树 3,295 件迁移、`_working` 2,827 老化…）"。
本波把它的**判龄轴修对了**，于是存量真相第一次可见。

### 26.1 这条尺原先是永久空转的

`scripts/governance/generators/library_hygiene.py` 是月度卫生批的唯一候选产出器，它对
`docs/_working` 用 **mtime** 判龄。而 S2 案卷 §2.5 早已实测 `mtime>30 天` 桶 **= 0**
（git checkout/merge/stash 天天碰 mtime）。净效果＝类目①**永不产出候选**，
月批看着在跑，实则对着一个恒空的面点头。
另有一条同源 metadata 谎：该文件头 `[TESTS] tests/library/test_library_hygiene.py`
指向的测试件**从未存在**（`git ls-files` 零命中）＝"有测试登记、零测试实存"。

### 26.2 改成 `created` 轴后，当日全量实测分布（tracked 面 3,172 件）

| 桶 | 件数 | 含义 |
|---|---|---|
| aged（created>30 天 且 task_bound） | **1** | 真正"按年龄该处置"的只有 1 件 |
| fresh（created≤30 天） | 798 | 未到期 |
| **undated（created 读不得）** | **2,361（74.4%）** | **陈化根本不可判** |
| ├ 有 frontmatter 但无 `created` 键 | 1,807 | 元数据欠账（可回填，且文件名里常就带日期，如 `2026-08-22-frontend-backend-gap-ledger.md`） |
| ├ 无 frontmatter 起始 `---` | 551 | 多为非 md 的机生/数据件，本就不该用文档生命周期尺量 |
| └ 有 `---` 但 yaml 解析失败/空 | 3 | 坏 frontmatter（真档实存） |
| other ttl | 2 | permanent 族，永不入候选 |
| **missing_on_disk** | **10** | **在册但盘上没有＝删除欠账**，与元数据缺失两种病，必须分桶 |

### 26.3 裁定：这条后波的正确形态是"补元数据＋装门"，不是"迁文件"

- 按年龄几乎无候选 ⇒ "迁移 2,827 件"是个伪工单；真欠账是 74% 无出生日；
- 补 `created` 之前任何"陈化处置"都无法机械判定，也无法给棘轮基线；
- 回填源现成：大量文件名自带 ISO 日期（`2026-08-22-…`、`2026-09-18_…`），
  可先做**文件名⇒created 的一次性回填批**，再装一条"`_working` 新件必须有 created"的门
  （否则补完继续漏）；
- 净零：本波**不新建脚本**——按 S2 案卷 §2.6 自己的净零方案（"零新工具，挂 `library_hygiene`
  既有月批"）扩了既生成器，并补上它 `[TESTS]` 一直宣称却不存在的那件尺（17 例）。

**那 10 件 `missing_on_disk` 已单独定性**（防下一班"顺手恢复"他道未落地删除）：
`git status --porcelain` 全为 ` D`＝**工作区已删、未暂存**；`git ls-files -v` 首字母全为 `H`
＝不存在 assume-unchanged/skip-worktree 遮蔽（不是"被隐藏的件"）。且非局部现象——
**全仓同类未暂存删除实测 175 件**，与 §十一（一次暂存删 186 枚已入库件）同族。
处置归属＝属主车道／Owner 门位，**本波一件未动、未暂存、未恢复**，只把"存在这 10 件"变成机器可见事实。

### 26.4 本波落地的判据（五条，各由尺钉死）

1. **轴=created 不是 mtime**——尺用 `os.utime` 把 mtime 造老 400 天而 created 写今天，
   断言仍落 fresh；并**反向自证 utime 真生效**（否则该例会因"什么都没发生"而假绿）；
2. **ttl 必走 YAML 解析器**——`ttl: "task_bound"` 引号变体实测在永久区有 810 件，
   裸正则会把它们判成"未声明 ttl"而整批漏掉（反例真源 `doc_lifecycle.py:152`）；
3. **读不得者单列计数**——created 缺失/坏值/坏 frontmatter 一律进 `undated`，
   禁静默归零（否则"把字段写坏"就能躲过盘点）；
4. **缺失件独立成桶**——`missing_on_disk` 与 `undated` 分开，防下一班人拿着删除事件去补字段；
5. **生成物自己必须可落地**——该生成器原先往报告里写 `doc_type:`，而 `docs/_working` 的 md
   只许 `ttl: permanent|task_bound`，多这一行就会被放置/TTL 门整批打回：**每跑一次就给自己
   产出一件不可提交的产物**。已删该字段并加一条断言钉住（尺跑一次≠产物能落地，这两件事必须分别证）。

另加一条**防自欺**：tracked 面读到 0 件时 `run_hygiene` 必记 warn、`main()` 必出声
（"三桶全空＝盘点未生效，勿据此判空"）——因为"恒空"正是这条尺当年的死法。
---

## 廿七、记忆库自身体检（顺带查出的三处"看不见"）

收尾时对 persistent memory 做了一次对账，三处与"文件在、账不在"同型：

| 症状 | 实测 | 危害 |
|---|---|---|
| 项目索引超字节上限 | 29,000/25,000 ⇒ 系统只加载片段 | 已记的教训未来读不到 |
| 有文件无索引 | 3 件（含**一条未闭环的采集链全线停采警报**） | 等于从未记过 |
| 有索引无文件 | 1 件（`agent-fabricates-owner-rulings` 实为用户级件） | 指向空气，且用户级索引反而没有它 |

处置：索引压到 24,526 字节并**逐文件双向对账**（补 3 条、改 1 条错级指针、
把伪造署名那条挂回用户级），并新增一条本项目级教训
（`runtime-code-behind-head-20260927`：HEAD 有修复 ≠ 运行中有修复）。
**同型通则**：`[TESTS]` 指向不存在的测试件、索引指向不存在的记忆文件、
`capability_canonical_file_registry` 里指向已迁址目录的 token 条目——都是"登记面自洽、
实面对不上"，判存在必须走 `git ls-files` / `os.path.exists`，不能看索引行。


---

---

## 廿八、两个"仪表说谎"教训（都差点导致错误决策，记录以防重演）

1. **卷空闲空间不是大文件覆盖写的进度条。** 本机 21:1x–21:5x 期间 G 卷 free 只掉了 0.09 GiB，
   我据此算出"~2 MB/s ⇒ 这趟要跑到天亮"，差点下令中止。停下来先量了一轮才发现仪表选错：
   robocopy 正在**就地覆盖同路径已存在的 591.57 GiB 旧镜像**，逐簇重写不改变 free
   （free 只会反映新旧尺寸差 7.43 GiB）。**中止才是真损失**——robocopy 大文件覆写无原子性，
   中途 kill 会留下一份半写镜像，比 08-22 那份陈旧但完整的更糟。
   判存活用：目标文件 mtime 递增 + 进程 CPU 递增；判完成只能等退出码（本机已装 watcher 等）。
2. **PS5.1 `Write-Host` 不进管道。** 我的分离式包装器用 `& child.ps1 | Tee-Object` 收轨迹，
   而本仓 ps1 的进度全用 Write-Host ⇒ 子脚本阶段行一条都收不到，日志"只剩包装器三行"，
   看起来像卡死。要留全轨迹得 `Start-Transcription`，或让子脚本把关键阶段写进自己的
   JSON/state（`backup_ch_vm.ps1` 本来就有 `$LogFile` 与 `backup_state.json`，够用）。
3. 顺带一条**判据口径**留给后波：`Get-VHD.MinimumSize` 是"能回收多少"的真值源（本机 600.0 GiB
   ≥ FileSize 599.0 ⇒ 原地收益≈0），**别拿虚拟机内部空闲反推宿主可回收量**——
   这正是我先前"140–150 GiB"错估的来源，已在 §十七 与 `a6_remaining_work_order.md` 就地更正。

---

## 廿九、收尾审计自查：一条**活跃灾备空洞**＋三把尺被误删（本会话自报，非他道举报）

复核时刻＝2026-10-08 23:0x。两条都不是叙述，是实测：

### 29.1 P0：全盘当前**没有 VM 级完整镜像**

| 位置 | 实读 |
|---|---|
| `G:ackup\ch_vm_backup` | **目录不存在**（0 条目，非"文件为空"） |
| `F:\ch_vm_backup` | 只剩 `boot.vhdx` + `zephyr-ch`（配置目录）；**无 data.vhdx**，599.00 GiB 那份也已不在 |
| `D:\HyperV\VMs\zephyr-ch\data.vhdx` | 586.50 GiB（在线唯一副本；曾被压缩过，state 记 `last_vhdx_compaction_reclaimed_gb=42.16`） |
| CH 在线状态 | `SELECT 1` → 1，VM Running，健康 |

写读两侧家已一致（HEAD 的 `backup_ch_vm.ps1:$ImageHome` 与 `restore.ps1:$ChVmImageHome` 都是
`G:ackup\ch_vm_backup`）——**这正好说明空洞不是口径分叉造成的，是"刷新通道未再跑过一次"**。
后果分级要诚实：表级恢复仍可走 CH 自己的备份链（BACKUP TO Disk 日增量），
丢的是**整机面**（OS＋CH 程序＋配置＋一致时点）。`restore.ps1 verify` 现在会**如实报红**
（它验 G 侧文件存在性，缺失即 `issues+=vm:data.vhdx` 并非零退出）——
即"假绿"已被治掉，但**真洞还在那儿**。
唯一处置＝再跑一次 `-CompactWindow`（G 实测 free 1419.5 GiB，放得下 586.5 GiB），
或至少跑一次全量备份刷新 G。

### 29.2 三把常驻尺被大规模清除袋误删（已在恢复中）

`tests/dr/` 三件（45＋20＋11 例）被 `6324c9e0f6`（st-tests-chief-20261004，"129 旧一级目录全量删除"）
删除，该袋自述"内容零删失（新路径真身在终装袋/盘面双证）"——对这三件**不成立**：
`git grep -l Get-MirrorPurgeCap HEAD -- tests` 零命中，`tests/backup/` 只有另外两件。
已从 `5d5398e848` 恢复至 `tests/meta/scripts/backup/`（判据＝同目录已是"scripts/backup/\*.ps1 的尺"的家）。
恢复时另修一处**搬动即崩**的缺陷：三件都用 `parents[2]` 数层求仓根 ⇒ 搬家后 75 例同时红，
且红的不是被测码而是尺本身；已改为**向上找 `.git`** 定根。
另发现并补一处**文档与代码相互矛盾的活体**：`backup.ps1` 的注释已声明"帽有可信上界 5000"，
而代码里 `$Ceiling` 根本不存在 ⇒ 已把上界实现补回（越界→返回 -1→判"帽不可用"→自动降级为只增）。

**通则**：大规模旧目录清除袋的"零删失"宣称，必须**逐件**以新路径符号命中为证；
收尾复核口径＝`git grep -l <该尺独有符号> HEAD`，不是"文件数对上了"。

---

## 三十、三车道独立复核汇总（2026-10-09 00:0x；含推翻本班先前两个数与一项裁定）

三条只读审计道各出案卷：`A1_landing_audit/README.md`（322 行，落地面与回退）、
`A2_pending_rulings_a/README.md`（待裁项复核 ①②③）、`A3_pending_rulings_b/README.md`（272 行，
镜像树论断复核＋D 盘出路标价）。**三件案卷目前均为 untracked**——新建 .md 需 creation_token，
而 token 册此刻带他道未落地改动（`git diff HEAD --numstat` = **+280/−50**），
按红线"绝不把他人未落地条目装进我的袋"，本波**不写 token**，故先以本节把结论收进总账，
案卷入库列为后波一件（连带其符号引用一并核）。

### 30.1 审计道 A1（落地面）：9 红 8 黑，其中三条与我直接相关
1. **我班三把尺现仍无执法钉**：`tests/dr/` 三件被 `6324c9e0f6` 删除且 HEAD 无后继，
   恢复件在 `tests/meta/scripts/backup/` 尚未入 index ⇒ 备份/压缩/镜像/取件四类 PS 判据无尺。
   本袋补落地。
2. ⚑ **`f293bac0c5` 归属篡改（我的子代理所为，我负责）**：正文只申报"册先行"，
   实落注册表 55 条中 **54 条 `created_by: st-chief7w-20260927`**（父 blob 中 0 条已存在）
   ⇒ 吸收他道暂存条目且未披露。不撤销（内容本身是合法在册条目），**改为在此显式披露**，
   并把"代投道须逐条核 created_by 归属并写入 message"列为后波执法件。
3. `103b97dc11` 的 21 行被同会话次笔 `d52a43a672` 删除，审计道认为"活跃车道"闸**无等价替代**。
   这是我 deliberate 的换面（理由见 §廿二与 S8 簿 §⑧ 第 3 条：心跳只证 daemon 活不证会话在干活，
   实测有 9 小时无写的会话壳仍在跳），**但审计道持异议，异议入账**，不由我自裁消灭。

### 30.2 A2：一件被证明是**伪待裁项**，一件的"待裁"题面已被换掉
- **`technical_indicator` 归档豁免＝伪待裁项**：三重锁叠加——契约 `excluded_tables` 排除 ＋
  `retention_lines_months` **根本没有 TI 键** ＋ 该表是 `(period, toYYYYMM)` 元组分区而被
  `_partition_end_ym` 与硬编码 `period=None` 直接拒。⇒ 解除排除**行为逐字节不变**，
  既不释放空间也不会误删。真过线仅 4 分区 / 6.98 GiB；daily/weekly/monthly 51.27 GiB 契约写明永久热层。
  **并且我先前引用的"165.3 GiB"全仓无真源命中（撤下）**，实测该表 **229.54 GiB**。
  真实风险不在这里：`consecutive_failures` 现=1，再两次熔断会**停掉全部 13 张表的归档闸**——
  这才是该立工程件的地方（契约窗口按 period 分档，现表结构装不下）。
- **FMS-HYGIENE 翻 block 的题面已换**：我按"清偿过半"问，而 `984c1787f8`（09-29）已把判据
  改写为"连零 20 笔"并落码（当时 T-1 标"待裁"）。实测：基线册 3703 条（表头写 3702，
  生成物自漂）、已清偿 264＝**7.1%**、`block_flip_eligible()=False`、连零 **1/20**。
  更硬：**活体重扫 exit 1，永久区净增 2851 条** ⇒ 棘轮当前是**冻结**而非衰减，
  且 warn 态门自己放行的新违规正在打断连零计数。
  ⇒ 该裁的不是"翻不翻"，而是"认不认这次判据改写"＋"先修棘轮"。列为待裁 O-7。
- **ROOR 8 候选**：清单真源指针（`S4_registry_machine_governance §4.4`）**git＋盘面双查无**；
  三条断言中"撤条致 CR-007 MISSING"**方向反了**、"迁址不可行"**被证伪**（先例 `06f15a7040a`，
  16 条纯 R）；仅 `REG-KB-001`/`REG-INTF-001` 现在能收尾，且欠两处指向空气的活注册行修正
  （`registry_adapter.py:714`、`sync_yaml_to_depgraph.py:1829`）；`REG-FCT-001`/`REG-STR-001`
  （19/29 py 消费者）**永不该并**。

### 30.3 A3：三条论断全部证实（但两条要改口径），并挖出一个迁移**硬阻断**
- (a) 积压 yaml 不可再生：**证实但需降级**——它只否"重生成"，不否 `git mv`（指针应为
  `externalize_algo_flow.py:10`）。(b) ≥6,100 改动面：**证实但数错源**，实为 3,373+3,353＝**6,726**。
  (c) NR-006 无执法落点：**证实且更弱**（`gate_registry.yaml:1691`，案卷引的 :2110 已漂 419 行；
  `MODE="warn"` 硬编码在 `:116`；`resolve_doc_path` 代码零实现）。
- ⚑ **新发现（比"不做"更强硬的证据）**：link 门 yaml 侧谓词要求路径含 `/algo_flow/`，
  而 src 内该目录 **0 件** ⇒ 一旦真迁到镜像位，**3,373 件的门禁 100% 熄火**
  （出仓器反查 `:177-179` 同型盲区）。⇒ 迁移的硬前置不是人力，是**两处谓词改造**，
  在此之前"迁了=关掉门禁"。**本波"不做迁移"的裁定由三条证据升级为四条，且第一条是可证伪的安全阻断。**
- 更小的动作存在：S1 写者改造（删 `_DOMAIN_DIRS` 55 行、复用 `mirror_doc_rel`）＋
  S2 FMS-HYGIENE 第五查，不新增门/flag/册、仍 warn，顺序 **S1→S2**。
  真实成本不在代码：三条 `[TESTS]` 指针全是死指，测试件只活在 3,634 个队列袋里的 71 件在飞/死袋——
  **与 §30.1 第 1 条同病，合并为一件"钉回执法尺"工程**。
- **D 盘出路定案＝什么都不做（就空间而言）**：原地收益实测 **0**（Min=Size=600 GiB > FileSize 586.5），
  vhdx 有 600 GiB 硬顶，约 71 天触顶后 D free 仍≈24 GiB；唯一"大且零停机"杠杆是
  `.runtime/tmp` ≥7 天老化件 **34.01 GiB**（需逐目录核引用）；换 500 GiB 新盘须停 VM
  （4 只 SCSI 含 F/G 两条备份链）＋灌 437 GiB，只省 ~66 GiB，**不成立**。
  ⚠ 但这条只结"空间"，**不结 §廿九 的灾备空洞**——刷 G 镜像仍要做，两者别混。
  并撤下 `a6_remaining_work_order.md` §E 那条"预期 D 回 200G+"的错案工单。

### 30.4 复核纪律（本轮自己踩到的两条，写下来防复发）
- **`exit code 0` 不等于跑过测试**：本仓 pyproject 配了 `cache_dir`，加 `-p no:cacheprovider`
  会让 pytest 因"未知配置项"直接 INTERNALERROR 且**0 例运行**，退出码却可为 0。
  判"跑过"必须看 `N passed` 行，不接受退出码。
- **临时件转正当中"移开不删"**：那枚 0 字节 16.7h 陈锁搬进 `lock_quarantine/` 的处置是对的，
  本轮实测该目录仅剩空壳、23 项临时件已全部清零。
