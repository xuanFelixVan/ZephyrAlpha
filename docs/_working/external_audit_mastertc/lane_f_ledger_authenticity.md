---
created: 2026-10-07
auditor: st-extaudit-20261007
ttl: task_bound
completes_when: 总报告交付并经 Owner 查收后随战役树归档
---

# 车道 F：文档/台账真实性审计 findings

> 审计对象：总包会话 st-mastertc 夜战（2026-10-06 夜~10-07）文档/台账面六袋：831a35b30ab / eb358e0cfda / a621b977651 / ccbe57e6f33 / 01bf541fbbec / 0b38f7ca7ca。审计基准=git HEAD 649a8c93c7b7 + `--all` 全史 + object DB 全量 blob 扫描（360,345 blobs）。本审计只读，零写操作。

## P0 候选

### P0-F1 ｜C129"考古交付报告重建"标 DONE，但原 §十七..廿八 字节实际仍在 object DB 中可整卷捞回，且重建版内容与原件主题完全不同

三重实证：

1. **"蒸发"仅在 ref 可达史成立，字节未蒸发**。`git log --all --follow -- docs/_working/fms_overhaul/99_delivery_report.md` 全史仅 6 个 commit（8bed0bb10eb→5306c714c3d→831a35b30ab），`--diff-filter=D` 零命中——**"640 行版"从未入史**（240 行止 §十六 是 2026-09-27 5306c714c3d 的自然终态，非截断）。但 object DB 全量扫描（38-130KB 区间 29,802 个 blob 逐一解压）命中 **3 个 633/634/641 行的悬挂 blob**：
   - `b0c4b9e7fb52`（641 行）/ `d5e61426e985`（634 行，含 GATE-SELFDOC 豁免头=09-28 后产物）/ `e03473fff431`（633 行）
   - 三者 frontmatter `sid: st-fms-chief-20260927`，`git rev-list --all --objects` 零引用（悬挂态），**`git cat-file blob` 即可整卷捞回**。内容时标 2026-09-27/28，远早于 L4 审计窗（10-07 上午）——即审计当时技术上可捞回。在库先例：同战役 C73 结卡（07000832e43，09-29）已演示"blob 池 25,436 件全扫"技术；M5 工单（HEAD `final_delivery_campaign/workorders_docs_misc.md` C129 行）处方原文="**先从车道/死信 blob 捞回 §十七..廿八 字节（蒸发族）**"。
2. **重建版顶替了原版位、内容主题完全不同**。原 §十七..廿八（以 d5e61426e985 为准）=12 节 2026-09-27 午后事件实录：存储面治本第二波（含落地哈希 103b97dc11/5d5398e848）、镜像树迁移 W0 裁定、幻影区判据更正、csx-p3b 救援工单、st-p23-rebase 语义分叉裁定、16.7h 陈锁、cascade_stale、worktree 登记面泄漏、磁盘整文件回退 P0、_working 2,827 件陈化普查、记忆库体检、仪表说谎教训。**HEAD 831a35b30ab 写入的同号 §十七..廿八 却是 S2/S3/S5/S7/S8 簿索引+X2/95_external_review/_data 指针**——这些 S 簿本就在同报告 §二/§三 已有索引（内容重复），而真正丢失的 12 节实录在 HEAD 仍缺位。"重建过程零虚构"字面成立（所引指针 7/7 抽验在 HEAD 存在），但"重建"名不副实。
3. **义务未履行却标 DONE**。重建版 §廿七自陈"原件若有备份/死袋可考古，考古后以原件为准替换本纲要节"（或然句、无任何具体指针：无 blob 哈希/死袋 qid），workbook 移交项 4 亦将考古列为未竟事项——而 `99_delivery/交付报告.md` C129 行记 **"DONE｜考古交付报告重建"**。捞回义务（M5 处方+自家 §廿七承诺）未做、DONE 已记。

**定性：假完成（考古义务未履行+原件可捞回而未捞回+同号节顶替）。** 修复路径现成：`git cat-file blob d5e61426e985…`（最新版）捞回原件，与重建纲要节并存或按 §廿七承诺"以原件为准替换"。

## 逐项 verdict（1~7）

### 1. C129 重建版考古 → **假完成**（详见 P0-F1）

补充：(a) 原件蒸发判定="ref 史蒸发真、字节蒸发假"——无删除 commit（从未入史），但字节在库；(b) 重建版仅留或然句"若有备份/死袋可考古"，无任何具体原件指针。

### 2. C473 四簿重建考古 → **真完成**（作为"重建骨架"的声明如实、蒸发叙事与 git 证据一致）

- `git log --all --diff-filter=D -- "docs/_working/fms_overhaul/*"` **零命中**——全目录无删除史；四路径（S1/S4/S6/S9 README）各自在全史仅 1 个 blob=重建版本身（01bf541fbb 首次落地）。即"原件从未落地 git"与自述"挖矿波产簿未落地即失"**一致**。
- 蒸发史有独立前案佐证：07000832e43（2026-09-29 st-finaldel-cdocs3）"**C473 字节不可考结卡（S1469 四簿全域 0 本体+staged 说法证伪）**"。
- 原版 240 行报告 §三当时声称"S1-S9 九簿全挖干…任何后续会话拿簿可直接开工"（blob b47c8fc4a730 L39）——09-27 当时 4 簿即未落地，属历史假完成；今晚重建系对该缺陷的补救。
- 四簿头部均有 frontmatter `reconstruction` 声明+正文"**终态声明：本簿为重建版，原件蒸发…原件名不可考**"+"重建 vs 撤卡"以 `status: 重建骨架`+`completes_when` 收口条件声明。S1 交付物指针表 7/7 路径在 HEAD 逐一验证存在（fms_deadref_baseline.yaml/生成器/门本体/提取器/三 csv）。
- 小瑕疵：S1 自述"原件名不可考"，但原版报告 §三/§五实有"S1 簿 C 类映射候选 412 条""S4 §4"等原簿踪迹（b47c8fc4a730 L18/L171）——目录语义可考，细节名不可考，声明基本成立。

### 3. C61 蒸发结论复核（22 本叶册 0 捞回）→ **真完成**（取证与上抛成立），附 1 项 P1 矛盾 + 1 项 P2 缺口

独立复核结果（workbook `lanes/L4_docs/00_workbook.md` 六项关键主张逐条验证）：

| 主张 | 独立验证 | 结果 |
|---|---|---|
| chief7 零 commit 入史 | `git log --all -- "*chief7*"` 零命中 | ✓ |
| `.aidrafts/st-chief7-20260928` 不在盘 | 盘面实测目录不存在（仅剩 st-tdm-chief/st-tests-chief） | ✓ |
| 无 stash | `git stash list` 空 | ✓ |
| 反查面唯一 md 3 件=fig14 骨架 2+wave7 红面 1 | **与 st-construct-20261002 salvage 档案逐字吻合**：`.runtime/campaign_trash_20261001/worktree_salvage/st-chief7-20260928_increment/`（chief7_tracked.patch 108,409B+manifest.json）实测在盘，manifest 唯一 3 个 md 即 fig14 骨架 2 件+wave7 红面 1 件，无叶册 | ✓ |
| 盘面在册 10 本=首批 6+四族 4 | beb2da1d7d7（09-28，6 本：f02×3/f04/f06/f11）+d7e0200a93d（09-27，f05/f08/f09/f10）；capability 册 leaf_books 记录恰 11 条（含 f05 yaml） | ✓ |
| tag archive/session__st-chief7-20260928 | tag 存在；branches_ledger 记 0 独有 commit（无叶册字节可捞） | ✓ |

- **"重建 vs 撤卡"真上抛 Owner**：`99_delivery/交付报告.md` L47（OWNER 行"重建或撤卡待 Owner 定"）+L176；`lane_result.json` open_questions。**未进裁定#488**（L4242 起）——#488 scope="⏳ 卡全量处置"，C61 当时态=OWNER 非 ⏳，口径自洽，不算遗漏；close_lane §五 OPEN_QUESTIONS 未列 C61，移交面以交付报告+lane_result 为准，充分。
- **P1-F2（矛盾未清）**：`01_skeleton/05_block_governance_gates.md` L113 在 HEAD 仍载 **"C61 ｜ GREEN ｜ 叶册 22 本 token 批落地（chief7_docs_staging 车道字节在 .aidrafts/st-chief7-20260928）"** ——该行 600abe99917（09:22）落地后 L4 于 11:06 取证推翻（字节蒸发 0/22），但骨架未回改。HEAD 同战役内 C61 存在 GREEN（已落地）vs OWNER（蒸发）两个互斥终态，误导继任读者。
- **P2-F3（分母不可复算）**："22 本"在仓内无权威路径清单——22-token 批从未登记（capability 册无第二批 leaf_books 条目），唯一 Enumeration=卡面 staging 子目录名（f06/f07/f11/reports）与 96 册 R-1"补齐族 06/07/08/09/10/13/14"。"0/22"的 22 无法从 git 独立复算（依据在 .runtime 死袋元数据，workbook 未附 qid 级清单）。

### 4. C192 57 行对账矩阵 → **真完成**（主体机械可复跑、全行对源），附 3 处 P2 瑕疵

机械全量核对（非仅抽 10 行）：源骨架 `night_sweep_20260929/00_skeleton_nightsweep.md` 实测 132 行=已通 64/开口 57/等Owner 11 ✓；矩阵 57 行与 57 个开口 F 号**双向零差**（无缺行/无多行）✓；三态分布 31/23/3 与对账结论一致 ✓；**挂卡列 57/57 行与源骨架卡号逐一吻合** ✓；独立态 per-F 处方指针抽 6 行（F001/F019/F020/F028/F122/F130）`git cat-file -e` 全部 EXISTS ✓。

不符行（3 处，均 P2）：
- **F4-a 对账结论簇尺寸错**：自称"最大簇=C46 组 10 行/C383 组 8 行"，表体实为 **C46 组 13 行**（F005/006/030/042/043/045/046/047/053/073/074/075/092）与 **C383 族 7 行**（4+3）；合并总数 23=13+2+4+3+1(F096) 自洽，结论行数字错误。
- **F4-b 重复态 3 行中 2 行引证不实**：F033 称"状态变量快照=links/L01 s3/s12 已挖"，实查该内容在 `links/L02_emotion/SKEL.md` L157（引证错簿，L01 s3/s12 文内无"状态变量/快照"）；F035 称"一问一考=links/L09_review 已挖"，L09_review 全域无"一问一考/D1/D2 一考"对应内容。F032 部分成立（s12 存在且题名"次级模型农场+TDM 传感器阵列对表"吻合，但"图谱谱系"字面不在其文）。
- **F4-c 乱码**：行 23 三态依据含"（考 **família** 面）"——葡语词混入，未校对痕迹。

### 5. C266 裁定落册对账（OWNER_GATE 移交 40 项）→ **真完成**（抽 10 行全对）

- 行数：A 表实测 34 行、B 表实测 40 行，与自述"A 已覆盖打勾 34 ｜ B 移交 40"一致 ✓。
- 引用裁定号 #413/#419/#428/#431-#435/#437-#439/#441/#443-#446/#449/#450/#451-#453/#460 在 ruling_registry（全史 306 条，#1-#489）全部存在 ✓；#431 子项 ④⑧⑫⑮⑭、#439 子项 ①-⑨ 符号逐一在册 ✓。
- 抽 10 行对 #488（L4242 起）A/B 段与宪法 §5，**10/10 一致**：#488-B 四行逐字吻合（C300"维持现状（已 enabled）+窗口=下维护窗"/C398"并存至 2026-10-08 继任窗复核"/C445"AI 侧施工"/C38"维持现状+周报"）；#488-A 归属吻合（1A.5→A⑤ C267、F 盘摘除→A③ C109、实盘双卡→A①② C63/C287，Owner 保留定性正确）；宪法 §5 净删族/flag 出厂归 §C 独立列示正确；4.3-#22 usercustomize 与宪法 RULE-ENV 冲突定性属实（AGENTS.md RULE-ENV 确装 usercustomize），呈 Owner 正确。
- B 表"裁定册 grep=0"抽验：usercustomize/base_blobs/Kronos/paper_outpost/SettlementReconciler 真 0 ✓（heartbeat 有 #459 无关语境命中与 #ARCH-HEARTBEAT-001 标签，无"heartbeat 计划任务兜底"专裁，主张实质成立）。
- 语义抽验：#431④ 原文"CH 实弹三件批（#20 换源实弹/intake_ledger_recon rebuild/apply_market_tables_ddl --apply）"与 A 表两行逐字对上 ✓；GPU 成绩单行 #435（c* 五道门 B 主 C 并）+#446（T1 成绩单定稿追认）对上 ✓。

### 6. ccbe57e6f3 台账回填哈希核验 → **真完成**

- 三提交存在且内容相符：831a35b30ab23e919cd0939a51acfd074a3c3b19（10:35:06，6 文件=lane_result.commits 清单逐一吻合）/ eb358e0cfda64c213df4cea05133aa8ccddb2e78（10:57:59，capability 册 +25/-4 一文件）/ a621b9776517f6d76c302fc1c2e9d6b2628c2ed2（11:06:53，5 新件逐一吻合）。
- 死袋 q-0001 留痕在 HEAD：`lanes/L4_docs/lane_result.json` `dead_bags` 数组（含死因+处方）+ workbook §6"死袋留痕" ✓。
- 竞态移交注记（workbook §7 投影时序差归维护班）在 HEAD ✓。

### 7. C342 幽灵引用三态清单 → **过渡**（现存面清白且漂移已声明，但原卡处方未执行）

- 计数口径：mining 树 1 处 ✓（`seal_audit/_VERDICT.md:19` 逐字吻合）；docs/_working 全域 grep=29 行/17 文件，剔除自举册 c342_ghost_refs.md（12 行）后=16 文件——"16 处"为文件级口径，可接受 ✓。
- 抽 10 行：**9/10 原文逐字吻合**（#1/#2/#4/#5+#6 双副本/#7/#9/#10/#3 修复后标题"'万无一失不成立'复核的证据面"确在 HEAD L37，且 831a35b30ab diff 的被删行正是旧标题/workbook 自引 L22）。无一条虚构。
- **实质批评（降级理由）**：原卡（M5 工单 C342 行）处方="**按封矿复核清单逐条补实物或删引用（幽灵引用 37/142 项实数/封矿复核 11 份）**"；交付件将任务改写为 grep"万无一失"短语的 16 处普查，37 项逐处考古以"逐处考古不经济"豁免并移交"考古专班"。漂移有显式"普查面漂移声明"（非静默），现存面无敞口——但原卡 37 项的逐条补实物/删引用未做，属**过渡**（部分完成+明示降级），交付报告记 DONE 偏宽。

## 证据块

**E1（P0-F1 核心）** 原 §十七..廿八 悬挂 blob 三件：
```
b0c4b9e7fb52b93cb09134f9bd27396ce1a0cceb  641 行 51,834B
d5e61426e985fb393b55733fb4891cd20afae0fe  634 行 52,013B（最新，含 GATE-SELFDOC 头）
e03473fff43143cb6c72f4d80a6c44502efa421c  633 行 51,820B
git rev-list --all --objects | grep <hash>  → 0 命中（悬挂，ref 不可达，odb 可读）
frontmatter: sid: st-fms-chief-20260927；§十七 起始 L244-245「存储面治本第二波…Owner 批准"全部批准·全速"后开工」
```

**E2（P0-F1 辅）** 该路径 ref 史 6 blob 行数序列：116→165→202→227→240→315（HEAD）。240=5306c714c3d（09-27 14:07 §十六 收尾）；315=831a35b30ab 重建版。`--diff-filter=D` 零命中=无删除 commit。240 行版 blob=b47c8fc4a730，其 L39"S1-S9 九簿全挖干"即 C473 蒸发史的反证起点。

**E3（C61）** salvage 档案：`/d/ZephyrAlpha/.runtime/campaign_trash_20261001/worktree_salvage/st-chief7-20260928_increment/`（chief7_tracked.patch 108,409B + manifest.json + untracked/）；manifest untracked 面唯一 3 md=fig14_construction 2 件+total_command_closeout/wave7 1 件——与 L4 workbook"唯一 md 3 件"逐字同口径。tag `archive/session__st-chief7-20260928` 存在。

**E4（C61 P1）** HEAD `01_skeleton/05_block_governance_gates.md` L113：`| C61 | L4 | **GREEN** | 叶册 22 本 token 批落地（chief7_docs_staging 车道字节在 .aidrafts/st-chief7-20260928） | — |` vs 同战役 `99_delivery/交付报告.md` L47：`| C61 | L4 | OWNER | 22 本叶册字节蒸发（0/22 捞回）…`。

**E5（C192）** 机械核对脚本读数：skeleton 132 行{开口 57,已通 64,等Owner 11}；矩阵 57 行双向零差；三态{独立 31,合并 23,重复 3}；挂卡列 57/57 吻合；合并簇实测 C46×13+C383×4+C383/C43×3+C251×2+F096×1=23（结论行自称 10/8）。乱码证据：矩阵 L51"（考 família面）"。F033 实文位置=`links/L02_emotion/SKEL.md:157`（"L9-V2 状态变量快照"），非其引证的 L01 s3/s12。

**E6（C266）** #488 A 段七项（C63/C287/C109/C410/C267/C36/C37/C45）与 C266 §C/打勾行归属一致；#488-B 文本与 C300/C398/C445/C38 四行逐字吻合；#431④ 原文含"#20 换源实弹/apply_market_tables_ddl --apply"。

**E7（ccbe57e6f3）** `git show --stat` 三提交文件清单与 `lane_result.json.commits[].files` 三方一致；q-0001 死因（CREATE-GUARD 读 HEAD 册时 token 未先行）在 dead_bags 留痕。

**E8（C473）** 四路径 rev-list 各仅 1 blob（0f354e88/e82d8fce/54260ea5/64b86dec，均为 01bf541fbb 重建版）；前案 07000832e43（09-29）"C473 字节不可考结卡（S1469 四簿全域 0 本体+staged 说法证伪）"；S1 指针表 7/7 EXISTS。

## 小结 + P1/P2 建议

**总评**：七个受审项中 **5 项真完成**（C473 四簿、C61 取证上抛、C266 对账、ccbe57e6f3 台账、C192 主体）、**1 项过渡**（C342，明示降级）、**1 项假完成**（C129，P0-F1）。总包夜战的"蒸发声明"整体质量高于典型水账：C61 的六点式取证经受住了独立复验（包括对其不利的 salvage 档案核对），C266 的裁定号/子项引用无一虚构。但 C129 暴露了致命的审计方法论缺口：**"蒸发"结论在下结论前未做 object DB 全量 blob 扫描**——而该技术在同战役前案（C73，09-29"blob 池 25,436 件全扫"）已被演示过。凡"字节蒸发 0 捞回"类结论，在未做 `git cat-file --batch-all-objects` 全库扫描前不构成终局结论。

**P1 建议**：
1. **立即捞回 C129 原件**（P0-F1 修复）：`git cat-file blob d5e61426e985… > 原件`，按其 §廿七承诺"以原件为准替换"或与重建纲要节并存（原件 §十七..廿八 与重建节主题不同，宜并列+交叉注记）；交付报告 C129 行 DONE 改判。
2. **清除 C61 GREEN 残留**（E4）：回改 `05_block_governance_gates.md` L113 为 OWNER 态，与交付报告对齐。
3. **C342 原卡 37/142 项逐条考古**补做或由 Owner 明示销案（现 DONE 记录偏宽）。

**P2 建议**：
4. C192：修结论行簇尺寸（13/7）；修 F033/F035 引证（F033 指向 L02_emotion；F035 另寻 L09 对应内容或改判独立）；清理"família"乱码；建议此类机械表落生成器后跑 diff 自检（表尾已声明生成器 `.runtime/tmp/st-mastertc-l4/c192_matrix_gen.py`，但该件在 .runtime/tmp 属临时区，未随袋落地，复跑性存疑）。
5. C61：将 22 本叶册的 qid 级反查清单（102 袋枚举+1651 死袋扫描命令与读数）附录化入 workbook，使"0/22"可独立复算。
6. 制度面：对"蒸发族"结论设立机械前置——凡声称"全域 0 本体/0 捞回"，必须附 object DB 扫描命令+候选区间+命中数读数（C473 与 C61 的取证质量可作为模板，C129 为反例）。
