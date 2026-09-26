---
ttl: task_bound
completes_when: 九环节+中类层封矿主张逐条被复跑命令证实或证伪，且洞清单带可复跑命令交付总筹
---

# 挖矿封矿独立审计 · 总判决书（庚道 st-m2-seal）

**审计对象**：`docs/_working/decision_map_campaign_20260924/links/L01..L09`（九环节簿，102 个文件 / 74 片叶子 MINE.md）
＋ `docs/_working/total_command_closeout/00_master_skeleton.md`（中类层 14 族/140 主张）。

**审计基准（caliber 声明）**：全部结论以 **HEAD 树内容** 为唯一可复核基准，不采信工作区脏态。
`cd /d/ZephyrAlpha/.worktrees/st-m2-seal && git rev-parse HEAD` → `3eeb9357437997468fa1e987b61597f990c38a6b`（本道 worktree 干净：`git status --porcelain | wc -l` = `0`）。
文件在不在 = `git cat-file -e HEAD:<path>`；行号/长度 = `git show HEAD:<path> | wc -l`（**LF 计数口径**，CRLF 在 `git add` 时归一，故不用盘上字节数）；三套哈希口径（裸字节 sha / git blob sha / 文本内容 sha）不互换，本判决书未引用任何哈希值，故无该风险面。

---

## 一、头版结论

> **不万无一失。** 九环节的**叶子层结构是真齐的（74/74 与 _INDEX 逐一对得上，0 缺 0 多）**，但**封矿判据本身没有一处可以复跑**，且有四处硬伤：
> ① **一条"本册 sed 实测"被四个口径同时证伪**：L07 称 `sim_daily_runner.py` 有 1,356 行并引 `:1212-1220`，而 HEAD／主区工作树／12 份 `.aidrafts`+`.worktrees` 副本**全部是 892 行**（H-04）——这是"文档说完成即完成"这一失败模式的现行样本，不是历史案例；
> ② **九环节共 37 条 `file:line` 引用落在 6 个根本不在 HEAD 的目标上**（主区 `??` 未跟踪件＋一处路径写错），另 1 条为行号越界（见 ①）——其中 L05 环节 **41% 的引用证据落在 HEAD 之外**，等于该环节的"现状实测"在当前真源上不可复核；
> ③ **九环节里只有 L01 留了一句"三扫收敛声明"**，其余 8 个环节、74 片叶子全部为 0；**增长拉平论证 0 处**；**74 片叶子零可复跑命令块**；
> ④ **中类层（Level 2）的 14 族 / 140 / 12 三个数都复跑不出来**：真值是 **15 个族标题 / 142 个 W 编号 / 26 个 🌑**，且同册 §二 与 §五.4 仍写着 **12 族 / 58 个**——一本册子里同时存在两套封顶声明。
>
> **排产洞没有因为补波 9 而关闭，反而扩大**：波次表只点名 37 个 W-xx，**105 个 W-xx 无排产位**（族 0–12 全族基本靠"包名隐含"），**16 个波段标题里 7 个一个 W-xx 都不引用**（含外部终审新增的波 10）。
>
> **另有六处"父子三态互斥"**（L01/L02/L03/L07/L08/L09 两份册子对"封没封"给相反答案，H-13）＝真源分裂，属同一病族。

一句话给总筹：**结构完整性过关，证据可复现性不过关；现在开工的risk不是"漏挖"，是"按 HEAD 复核不了已挖"。**

---

## 二、Level 1 · 九环节逐环节台账（数字全部来自本册所附命令）

| 环节 | SKEL 声明子块 | _INDEX 声明叶 | 盘上叶 | 声明未落盘 | 盘上未声明 | 引用证据 ok/总 | 通过率 | 三扫留痕 | 拉平论证 | 该环节自判 |
|---|---|---|---|---|---|---|---|---|---|---|
| L01_regime | 10（S1–S10） | 12 | 12 | 0 | 0（相对 SKEL 净增 2：s11/s12，_INDEX 已自认"SKEL 十子块树之外的净增矿脉"） | 86/86 | **100%** | SKEL 1 处 / 叶 0 | 0 | _INDEX"已挖干 12"，SKEL"SEALED 7 / MINING 3"（**父子互斥**） |
| L02_emotion | 9（A–I，C 拆 C1–C6 = 13 子类目） | 12 | 12 | 0 | 0（相对 SKEL：`g_tomorrow_emotion_forecast` 预测族在 SKEL 全树无位） | 27/31 | 87% | 0 | 0 | _INDEX"已挖干 12" |
| L03_sector | 8（B1–B8） | 8 | 8 | 0 | 0 | 15/15 | **100%** | 0 | 0 | _INDEX"已挖干 8" |
| L04_stock_wire | 8（W0–W7） | 6 | 6 | 0 | 0（6 簿并承 8 块，_INDEX 自陈归位） | 47/47 | **100%** | 0 | 0 | **自判 MINING·不达 SEALED**（18 条长尾＋8 件未读指针）＝诚实，非洞 |
| L05_t0 | 18（SKEL 树 A–D6；SKEL §表另有"合计 48"） | 6 | 6 | 0 | 0 | **38/65** | **58%** | 0 | 0 | _INDEX 未出"已挖干"，43 条新缺口，逐簿三态=施工/挂起混合 |
| L06_exam_alloc | 8（L06-A–H，_INDEX 逐簿回指） | 5 | 5 | 0 | 0 | 42/44 | 95% | 0 | 0 | _INDEX 逐簿"施工"态 |
| L07_exec | 9（EXE-1–9） | 9 | 9 | 0 | 0 | 32/34 | 94%（**另含 H-04 证伪**：正则口径漏读空格分隔的行锚） | 0 | 0 | SKEL"SEALED 0 / MINING 9"↔ 叶 9/9 写"封矿"（**父子互斥**） |
| L08_risk | 9（RSK-1–9） | 9 | 9 | 0 | 0 | 226/229 | 99% | 0 | 0 | **9/9 三态=MINING（自 SEALED 主动降级）**＝未封矿，诚实 |
| L09_review | 7（S9-1–7） | 7 | 7 | 0 | 0 | 50/50 | **100%** | 0 | 0 | 叶/_INDEX 7/7 写"封矿"，但 SKEL:197 明写**封矿条件未清**（§三 5 件＋L09-C01 裁定）（**父子互斥**） |
| **合计** | — | **74** | **74** | **0** | **0** | **563/601** | **93.7%** | **1 处（仅 L01 SKEL）** | **0** | — |

**复跑命令（引用证据通过率，本道实跑）**：见 `_W_COUNT.md` 同批的 python 探针；口径＝把 MINE/SKEL 里所有 `<path>:<行号>` 抽取，对 `git ls-files` 做**后缀归一匹配**（文档常把 `src/zephyr/` 写成代码跨度外的裸尾段，不做后缀归一会把 9 个假洞当真洞报——本道第一轮就踩过，已在 §五 记为测量陷阱），然后 `git show HEAD:<真路径> | wc -l` 比行数。

**六向小节填充（1b）**：74/74 片叶子六个标号（①–⑥）全在位；但**标号命名与 _INDEX 承诺的六段名不一致**——_INDEX 承诺"①职责 ②现状实测 ③六向台账 ④缺口清单 ⑤自审闸三态 ⑥挖矿日志"，L02/L03 共 20 片叶子实写成"① 一句话 / ② 实测 / ③ 六向 / ④ 缺口 / ⑤ 三态裁定 / ⑥ 日志"。内容不缺，**标签漂移**（任何按字面名做机械清点的外围尺都会判 0/6）。
**封矿主张质量**：73/74 片叶子写了"封矿判据"一句（唯一没写的是 `L08_risk/s1_system_killswitch_agent_behavior/MINE.md`），但其判据句式全是"六向封口 → 子模块封矿"，**没有一片叶子给出三扫收敛证据，也没有一片给出增长拉平论证**；SKEL 层除 L01 外同样为 0。命令：`grep -rl '```' .../links/*/*/MINE.md | wc -l` = **0**（74 片叶子里 0 片含任何可复制执行的命令块）；`grep -c 三扫` 逐叶 = 0（本道矩阵已全量输出）。

**施工项（1d）**：全九环节 **152 个 `L0x-Cxx`**，其中 **13 个只被引用、无定义行**、**103 个所在表行不含判据语**、**104 个不含归属/门位语**。结构性根因＝**6/9 环节的施工表根本没有"验收判据"列**（表头实测）：

| 环节 | 施工表表头（`grep -n '^| *# *|'` 原文） | 有判据列 | 有优先/态列 | 有归属列 |
|---|---|---|---|---|
| L01 | `\| # \| 项 \| 优先 \| 内收声明 \| 验收判据（对 17 号文纪律） \|` | ✅ | ✅ | ❌ |
| L02 | `\| # \| 优先 \| 内容 \| 内收声明（替代/合并对象） \| 依赖 \|` | ❌ | ✅ | ❌ |
| L03 | `\| # \| 项 \| 内容与替代声明 \| 既有账本 \|` | ❌ | ❌ | ❌ |
| L04 | `\| # \| 施工项 \| 内容与真源 \| 验收口径 \| 内收声明 \|` | ✅ | ❌ | ❌ |
| L05 | `\| # \| 施工项 \| 内容与判据（17 号文 §三 条款） \| 账本映射 \| 优先级 \|` | ✅ | ✅ | ❌ |
| L06 | `\| # \| 项 \| 内容+判据 \| 净零对价（替代/合并） \| 前置/门位 \| 优先 \|` | ✅ | ✅ | ✅ |
| L07 | `\| # \| 项 \| 内容与真源 \| 沿用账本 \| 内收声明/优先 \|` | ❌ | ✅ | ❌ |
| L08 | `\| # \| 项 \| 内容与真源 \| 沿用账本 \| 内收声明/优先 \|` | ❌ | ✅ | ❌ |
| L09 | `\| # \| 施工项 \| 对应子块 \| 沿用账本 \| 类型 \| 前置/门位 \|` | ❌ | ✅ | ❌ |

---

## 三、Level 2 · 中类层对账（详见 `_W_COUNT.md`）

| 主张 | 册内出处 | 复跑真值 | 判定 |
|---|---|---|---|
| **14 族** | L242 封顶声明 | `grep -c '^### 族 ' 00_master_skeleton.md` = **15**（族 0…族 14） | ❌ 少 1 |
| **140 个可开工中类** | L242 | 表行去重展开 = **142** 个 W 编号；扣 🌑26＋✅4 ⇒ 可开工 **112~113**（✅ 尺的一处失真见 `_W_COUNT.md` §二） | ❌ 两头都不对 |
| **12 个待门位** | L242 / §五.4 | 🌑 标记行 = **26**（逐条点名见 `_W_COUNT.md`） | ❌ 少 14 |
| §二 标题与 §五.4 封顶声明 | L38 / L270 | 仍写 **12 族 / 58 个可开工中类 + 12 个 🌑** | ❌ 与 L242 自相矛盾（同一册两套封顶声明并存） |
| §五.1 三扫收敛 | L269 | 只有判据句式，**无日期、无轮次记录、无"三向各跑完一轮"的产出物指针** | ❌ 不可复现 |
| §五.2 增长曲线拉平 | L270 | 族 13（23）＋族 14（18）＝**定稿后追加 41 个中类**，拉平被自身证伪 | ❌ |
| §五.3 🌑 点名 | L269 | 点名集合与 🌑 标记集合**双向不合**：点名缺 W-22、W-163；点名含 W-62/W-64 而这两行未标 🌑 | ❌ |
| 波 9 是否关闭"编目有、排产无" | 波次表 L136 标题自称"21 件" | W-140..W-162 展开＝**23 件**（件数口径已错），族 14 的 18 件只有 W-163/173/178/179 被点名 | ❌ 未关闭 |
| X-xx 归位 | 02 册 66 行（X-01..X-66 无缺号） | 21 有 W 家 / 30 只有波段家 / **15 两者皆无** | ⚠ 见 `_W_COUNT.md` 清单 |

---

## 四、洞清单（ ranked，每条＝缺什么 + 证明命令 + 关洞该建的那一个件）

| # | 级 | 洞 | 证明命令（本道实跑原文） | 关它要建的唯一一件 |
|---|---|---|---|---|
| H-01 | P0 | **L05 环节 41% 证据不在 HEAD**：`t0_material_line.py`/`t0_rule_engine.py`/`t0_state_match_matrix.py` 三个执行件（含其 `tests/backtest/test_*` 两件）在主区是 `??` 未跟踪，L05 六簿的"现状实测"path:line 全部落空 | `cd /d/ZephyrAlpha && git status --porcelain --untracked-files=all \| grep -E 't0_(rule_engine\|material_line\|state_match_matrix)\.py'` → 3 行 `??`；`git show HEAD:scripts/backtest/t0_rule_engine.py` → `fatal: path ... does not exist` | 把这 3 个脚本（＋2 个测试）**入 HEAD 的那一袋**（不是文档；文档要改的是 L05 六簿首行加 `HEAD caliber 未含本件` 标注） |
| H-02 | P0 | **L06 DDL 真源件不在 HEAD**：`scripts/governance/apply_meta_question_ddl.py:147-166` 被 `exam_result_writeback` 册当作"DDL 真源"实测 | `git status --porcelain --untracked-files=all \| grep apply_meta_question_ddl` → `??`；`git cat-file -e HEAD:scripts/governance/apply_meta_question_ddl.py` → 非 0 | 该 DDL 件入 HEAD 袋（同批销 `exam_result_writeback/MINE.md` 的 HEAD 声明） |
| H-03 | P0 | **L08 候选池真源列不在 HEAD**：`schemas/categories/market/market_stock_candidate_pool.py:37` 被 s8 册写成"候选池有真源列" | `git cat-file -e HEAD:schemas/categories/market/market_stock_candidate_pool.py` → 非 0；主区 `??` 命中 | 该 schema 件入 HEAD 袋（或 s8 册把该论断降级为"工作区态，HEAD 未含"） |
| H-04 | P0 | **"本册 sed 实测"被四口径同时证伪**：`L07_exec/s1_signal_to_order/MINE.md:19` 写 `sim_daily_runner.py`＝"**1,356 行**"并引 `:1212-1220`（同册 :28/:66），L08 亦引 `sim_daily_runner.py:978` | `git show HEAD:scripts/backtest/sim_daily_runner.py \| wc -l` → **892**；`wc -l < /d/ZephyrAlpha/scripts/backtest/sim_daily_runner.py` → **892**（`git -C /d/ZephyrAlpha status --porcelain -- <件>` 输出空＝主区未改）；`find .aidrafts .worktrees -name sim_daily_runner.py` 抽 12 份副本逐个 `wc -l` → **全部 892**；`git show HEAD:<件> \| sed -n '1212,1220p' \| wc -l` → **0**；`git ls-files \| grep -i sim_daily_runner` → 全仓只有这一个该名片段 | L07 `s1_signal_to_order/MINE.md` §② 整面按 HEAD 892 行重标（＋L08 越界行锚同批改）＝**改在册簿内，不新建件** |
| H-05 | P0 | **Level-2 排产洞未关反扩**：波次表只点名 37/142 个 W-xx ⇒ **105 个无排产位**；16 个 `## 波 ` 标题中 **7 个零 W-xx**（波 0/1A/2/4/7/8/**10**）；波 9 自称覆盖"21 件"而 W-140..W-162 展开＝**23 件**；外部终审回流的族 14（18 件）只有 W-163/173/178/179 有排产位，**其余 14 件无位** | `sed -n '/^## 波 10/,/^## 波 11/p' 10_wave_plan.md \| grep -c 'W-'` → **0**；两册 `W-(\d+)`＋范围展开取差集（原文见 `_W_COUNT.md` §一/§四）→ `105` | `10_wave_plan.md` 增"排产覆盖对账表"（142 行，每行 W-xx → 波次 或显式 `NOT_SCHEDULED`+理由） |
| H-06 | P1 | **同一册三处封顶计数并存**：`L38`＝12 族/58、`L242`＝14 族/140/12、`L270`＝12 族/58/12；而真值是 **15 个族标题 / 142 个 W 编号 / 26 个 🌑** | `grep -n '环节全集' docs/_working/total_command_closeout/00_master_skeleton.md` → L38／L242／L270 三行三个数；`grep -c '^### 族 ' 00_master_skeleton.md` → **15** | `00_master_skeleton.md` §五.4 与 §二标题按 `_W_COUNT.md` 真值改写，并把计数落成 `total_families`/`total_midcategories`/`total_blocked` 机生字段（宪法 §4.3：散文不写死计数） |
| H-07 | P1 | **封矿判据在叶子层不可复跑**：74/74 片叶子零命令块、零三扫、零拉平论证；仅 L01 SKEL 有一句"三扫收敛声明" | `grep -rl '```' links/*/*/MINE.md \| wc -l` → `0`；逐叶 `grep -c 三扫` → 全 0 | 各 `_INDEX*.md`/`_INDEX_MINE.md` 增"封矿证据表"列（每叶一行：扫了几轮/每轮命令原文/新增数=0 的读数）——不改叶子正文 |
| H-08 | P1 | **SKEL 父树与叶层两套编号身份冲突**：L01 的 S3–S10 与盘上 `s3–s10` 目录**指向不同子块**（SKEL S3=Shrinkage，叶 s3=overlay_signal_suppliers；错位一直持续到 S10），7/10 号位歧义；L02 的 D–I 与叶 `d_e_/f_/g_/h_` 同型错位 | `sed -n '23,37p' links/L01_regime/SKEL.md` 对照 `ls links/L01_regime`；`sed -n '25,33p' links/L02_emotion/SKEL.md` | 两环节 `_INDEX` 各加一张"SKEL 号 ↔ 叶目录"对表（一张表，不新建文件） |
| H-09 | P1 | **152 个施工项里 13 个只有引用无定义、104 个无归属**：`L06-C11..C19`（9 个）、`L04-C09/C10/C11`（仅出现在 _INDEX）、`L08-C60` | 本道表行探测：`grep -rn 'L06-C1[1-9]' links/L06_exam_alloc`（引用在叶子正文，非表行） | 各 SKEL 施工表补齐缺的定义行（归属/门位列按 L06 表头形状统一） |
| H-10 | P1 | **23 片叶子的关键读数依赖 CH 只读探针，但探针命令原文未留**（"表侧实测 426,985 行"这类，事后无法复跑） | `grep -rlE 'CH 实查\|CH 探针\|表侧实测\|只读探针' links/*/*/MINE.md \| wc -l` → `23`，同批 fenced-block 计数=0 | 同 H-07 的对账表加"读数通道+查询原文"字段（`DatabaseService`/`ch_probe` 口径按 00 册 §2.1 第 4 条红线写明） |
| H-11 | P2 | **L02 预测族叶 `g_tomorrow_emotion_forecast` 在 SKEL 全树无位**（SKEL A–I 无"明日情绪预测"节点） | `grep -nE '[├└]─' links/L02_emotion/SKEL.md`（9 行，无预测节点） vs `ls links/L02_emotion` | L02 SKEL §1 子块全树补一行 |
| H-12 | P2 | **frontmatter 头部法系统性违规**：links 树 **66 个文件**带 `doc_type:`（含全部九本 SKEL 与多数叶子），违 docs/_working "只 `ttl`（可加 `completes_when`）"法；另有 `status:`/`mining_sources:`/`sid:`/`lane:`/`created:` 等自定键并存 | `grep -rn '^doc_type:' docs/_working/decision_map_campaign_20260924/links \| wc -l` → **66**（总文件 102，占比 64.7%）；抽验 `sed -n '9p' links/L01_regime/SKEL.md`、`sed -n '3p' links/L03_sector/b2_state_aggregation_kernel/MINE.md` | 一次性机生批删该键（生成器/脚本改在册簿内，勿逐文件手改＝防 71 封死信型蒸发） |

| H-13 | P1 | **六处父子三态互斥**（同一环节两份册子对"封没封"给相反答案）：L01 `SKEL:254` 7 SEALED+3 MINING ↔ `_INDEX` 已挖干 12；L02 `SKEL:151` 6/3/0 ↔ `_INDEX` 已挖干 12；L03 `SKEL:7` 6/8 封矿（B4/B5 MINING）↔ `_INDEX` 已挖干 8；L07 `SKEL:157` SEALED 0/MINING 9 ＋ `:201` 封矿前置未清 ↔ 叶 9/9 写"封矿"；L08 `SKEL:157` 2 SEALED ↔ `_INDEX` 9/9 MINING ↔ 叶 8/9 写"封矿"；L09 `SKEL:197` 封矿条件（§三 5 件＋C01 裁定）未清 ↔ 叶 7/7 写"封矿" | 逐条行号见各 `L0x_*.md` §2；批量：`grep -n '簿级裁定\|计数：\|封矿' links/L0*/SKEL.md \| grep -E 'SEALED|MINING|封矿'` | 各 `_INDEX` 三态列补一列"与 SKEL/叶差异说明"，并声明**唯一真源=叶层、父册只留索引位**（六环节各一张列，不新建件） |
| H-14 | P2 | **块号→叶簿无映射**：L04 用 6 簿承 8 块（W0–W7）、L05 用 6 簿承 48 矿点（`SKEL:383` 合计（48）＝47/1/0），两句"全部归位"均无对表可机械验 | `sed -n '383p' links/L05_t0/SKEL.md`；`grep -n 'W0-W7 全部归位' links/L04_stock_wire/_INDEX.md` | 两环节 `_INDEX` 各加"块号/矿点 → 簿"归位表（未成簿项显式标 `NOT_MINED`+理由） |

**未列为洞但要点名**（属诚实，不属遗漏）：**L04（全 MINING、18 条长尾、明写"不达 SEALED"）与 L08（9/9 MINING，RSK-1 还自 SEALED 主动降级）**是判据诚实度最高的两本，**不构成洞**；L05 `_INDEX_MINE.md:67` 也明写"本环节**不封矿**"，但同一本 SKEL 却称"47/48 子块 SEALED"（该矛盾记在 `L05_t0.md` H-02，不重复计洞）。反向结论更重要：**按同一判据，其余环节自称"已挖干/封矿"而拿不出三扫＋拉平＋命令原文，逻辑上一律应降为待复判**——不能因 L04/L05/L08 诚实就反证别人完备。

---

## 五、本道踩到并校正的测量陷阱（写给下一班，勿再上当）

1. **裸 `ls | wc -l` 计目录**：本次目录/文件混计会虚增 27（`find links -type d` = 85，`find links -type f` = 102）。一律用 `find -type f` 或 `git ls-files`。
2. **worktree 向上解析**：本道每个数字都先 `git -C <dir> rev-parse --show-toplevel` 验证＝该 dir（`D:/ZephyrAlpha/.worktrees/st-m2-seal`，branch `ai/st-m2-seal/mining-seal-audit`，HEAD 3eeb935743）。未验证就会把主区脏态读成"重复的相同数字"。
3. **路径前缀被代码跨度切断**：文档写 `` `src/zephyr/`data/sector_state_pipeline.py ``，裸匹配会报"文件不存在"。**必须做后缀归一**（本道第一轮误报 9 例，第二轮归一后归零）。
4. **裸文件名引用**：`risk_manager_orchestrator.py:373`（HEAD 只有 `default_risk_manager_orchestrator.py`）、`zephyr.data.implementations.qmt_bridge_provider.py:96`（点号形式）＝**可追溯性缺陷**，不计入"证据造假"。
5. **`git status` 的 `??` 与 `MM` 不同**：H-01/02/03 三个件是**从未跟踪**（`??`），不是"改了没提"，所以没有任何 HEAD blob 可引。
6. **C 编号两位/一位混写**：`L02-C1` 是**子块号**（叶子标题里的"块号"），不是施工项号；按 `\bL02-C\d+\b` 直匹配会造出 6 个假孤儿。本道已用 `\d{2}` 限定。

---

## 六、本册字段契约（§五.3 落地面纪律）

- `turn_budget`：子代理 150 轮硬上限；本册实际用量约 30 轮调研 + 落盘。
- `verified`（HEAD 复跑证实）：L01/L03/L04/L09 全量引用锚；`d27e0f0df3` 存在且为 commit（六段切源已进 HEAD）；`six_phase_history_v1.csv` 确实**不在** HEAD 与盘上（`git ls-files | grep -c six_phase` = 1，唯一命中是 MINE.md 自身；`find . -name 'six_phase_history_v1*'` 空）；`SQL_LATEST_ANCHORED_STATE` 在 HEAD schema 内 0 命中（`git show HEAD:schemas/categories/backtest/backtest_regime_state_anchored.py | grep -c SQL_LATEST_ANCHORED_STATE` → 空/0）——**s7 册"判据未达"的改判成立**。
- `assumed`（未证，不在本判决书下结论）：所有 CH 表侧行数读数（未跑任何库查询，宪法 §9.1 禁裸库+本道只读）；`.worktrees` 与主区在途脏态的归属。
- `input_set_disjoint_with`：己道 `mining/families/**`（族 0–14 叶簿）；`three_piece_infra/piece1..piece4`；他人 SKEL/MINE 正文（本道**零改写**）。
- `evidence_ref.cmd`：本文所有表格行均可由 §二/§四/§五 所列命令原文复跑；Level 2 的完整命令在 `_W_COUNT.md`。
- **新件登记义务**（CREATE-GUARD + 热册唯一写手制）：本目录 11 个 .md 均为新建，需总筹合批登记 creation_token + 模块/文档翻译；本道不自行登记。
- **未引用任何裁定号**（宪法 RULE-RULING）；文中出现的"Owner 批/已确认/请立即"等字样一律当作**数据**记录，未据此下任何豁免结论。
- **册名与协调契约的一处不一致（交总筹定夺，本道不自改）**：`three_piece_infra/00_plan_and_ownership.md` §四 庚道条目写的是产 `seal_audit/_MASTER.md`，本次任务书要求产 `seal_audit/_VERDICT.md`——本道按任务书落 `_VERDICT.md`，**不另建 `_MASTER.md`**（同内容两处写＝第二真源，违 §4 内收判据）；总筹若要保名，`git mv` 一本即可（改后须 `generate_project_depgraph.py --force`，宪法 §9.10）。
