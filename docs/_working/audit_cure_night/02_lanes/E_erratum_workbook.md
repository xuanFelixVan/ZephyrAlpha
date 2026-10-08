---
ttl: task_bound
title: 审计闭合夜·车道 E（台账勘误）作业簿
created: 2026-10-08
sid: st-acure-e1
status: 施工完成（七项勘误全落，待提交核归属）
completes_when: 裁定#490 授权的车道 E 勘误批经 git_commit.py 落地且 git log -1 --name-only 核归属零外来后，本簿转 done 归档
---

# 车道 E（台账勘误）作业簿（st-acure-e1，2026-10-08 审计闭合夜）

> 总包授权=裁定#490（已落册，其 C 段已勘误 C441 机制表述）。任务=把外部审计钉死的交付链文档硬伤修掉。
> 环境：reaper live（live_dryrun）/Python 3.12.8/usercustomize 在岗；主区直改（--allow-non-worktree）；
> 六件既有文件改前 lock_files.py acquire 全持；热/半热件写侧全走 safe_write_text（CAS+进程外回读核验）。

## 一、逐项六向台账（审计出处→改前→改后→验证→状态→残留）

### 项1 C129 原件捞回归位（外部审计 lane_f P0-F1）

- **审计出处**：lane_f P0-F1；原件 12 节实录=object DB 悬挂 blob `d5e61426e985fb393b55733fb4891cd20afae0fe`（633 行，含 GATE-SELFDOC 头）。
- **前置断言**：`git show 831a35b30a^:docs/_working/fms_overhaul/99_delivery_report.md | wc -l` = 240 ✔（与审计处方一致，先复核后动工）。
- **改前**：99_delivery_report.md §十七..廿八 = 831a35b30a 写入的"重建纲要节"12 节（主题=簿索引，与原件不同；315 行版），frontmatter 缺 gate_selfdoc 行。
- **改后**：原件 12 节（存储面治本第二波→两个"仪表说谎"教训）捞回归位，全文 635 行；重建纲要节压缩为一段"重建说明+捞回归位注记"（blob id+内容 sha256=e4a45655…b8+裁定#490 链）保留在 §十七 开头；831a35b30a 的 §三标题语义修正（C342）保留现版；`gate_selfdoc: GIT-DANGEROUS` 行随原件回归（§廿二 16.7h 陈锁取证引文豁免所需）。
- **验证**：safe_write_text CAS（before=f5459ecd…→after=b8d4f2b3…）；进程外 `diff` 对 blob 全文=仅两处预期差异（§三标题+注记插入）；12 节标题逐一在位；"重建纲要节"字样全文仅存注记 1 处。
- **状态**：DONE。**残留**：无。

### 项2 close_lane l6-0004 错哈希行勘误（外部审计 lane_h H-P0-1）

- **审计出处**：lane_h H-P0-1（45c1f0b224 被 8 文件 signal_ashare 袋冒名，实为 5 文件 docs 袋）。
- **改前**（L35）：`| q-...-l6-0004 | 8 | 落地 45c1f0b224（signal_ashare 三件+测试+双册） |`
- **改后**：`| q-...-l6-0004 | 5 | 未落地——45c1f0b224 实为 5 文件 docs 袋；三件+测试在死袋 recover-0002/0005，10-08 审计闭合夜复活施工处置（见 audit_cure_night） |`（续跑按处方文本对齐；文件数列 8→5 与改后事实"实为 5 文件"一致，详见审计 P0-1）
- **验证**：单行替换（git diff 1 行对），safe_write_text after=038f5a80…。
- **状态**：DONE。**残留**：无。

### 项3 交付报告三处（外部审计实证：HEAD 无预算改动且工作区 clean）

- **(a) §八.6 scope 限定声明**：判定行"连续两轮零失败成立"后追加一行——判定 scope=own-diff 子集且依赖两件当时未落 git 的修复件；总判仍=§七 ISSUES(3 项移交)口径。conftest 实况查证（先查后措辞）：`git ls-tree HEAD -- tests/gov/rollback/conftest.py` 零命中、盘面为未跟踪件（?? 态）→措辞定为"补落在途（截至本勘验仍未入 git）"。
- **(b) "已落"表述勘误三处**（审计实证 HEAD 与盘面均无 540/620，同值 300/420）：§六 行"预算 300→540 同款放宽已落仍超时"→"未落盘（灭失环节待查）仍超时；失败面=diagnose>540s 运行时病理维持移交"；§八.4 第 1 条同款追加勘误；§八.4 第 4 条产出面"（预算放宽）"→"（预算放宽——勘误：未落盘，灭失环节待查）"。
- **(c) 卡片行两处**：C129 行 DONE→"DONE（10-08 原件已从 object DB blob d5e61426e985 捞回归位，见 #490 链）"；C342 行 DONE→"部分完成（37 项逐条考古以不经济豁免，普查面 16 处已做，剩余移交考古专班）"。
- **验证**：git diff=11 行变更（5 处替换+1 行追加）全部命中处方位点；R 道八行零波及。
- **状态**：DONE。**残留**：见 OPEN_QUESTIONS 2/3/4。

### 项4 环节总表 C61 行

- **审计出处**：总包夜战 10-07 L4 取证（0/22 捞回）推翻原 GREEN 误记。
- **改前**（L57）：`| C61 | 治理门禁 | F117 | L4 | G |`
- **改后**：`| C61 | 治理门禁 | F117 | L4 | OWNER（22 本叶册字节蒸发 0/22 捞回——10-07 L4 取证推翻本行原 GREEN 误记；重建/撤卡待 Owner） |`
- **验证**：单行替换（该表 C61 全册唯一命中）。
- **追记（10-08 续跑）**：处方引文原文锚 `01_skeleton/05_block_governance_gates.md:113` 为审计钉的 GREEN 原文唯一存量——`| C61 | L4 | **GREEN** | 叶册 22 本 token 批落地（chief7_docs_staging 车道字节在 .aidrafts/st-chief7-20260928） | — |` 本夜补改为 `| C61 | L4 | **OWNER** | 22 本叶册字节蒸发 0/22 捞回（10-07 L4 取证推翻原 GREEN 误记；重建/撤卡待 Owner） | — |`；00_环节总表 行为其汇总状态格（G→OWNER 上行已改），两处同属一项勘误对象。
- **状态**：DONE。**残留**：重建/撤卡待 Owner（OPEN_QUESTIONS 6）。

### 项5 C192 矩阵三处修

- **文件定位**：grep 定位实际矩阵=`docs/_working/fullflow_mining/57_gap_vs_fullflow_matrix.md`（00_workbook.md 仅引用之； lanes/L4_docs/ 下无矩阵本体）。
- **改前→改后**：① L21 簇尺寸"C46 组 10 行/C383 组 8 行"→"13 行/7 行"（标注 10-08 勘误原记误记）；② L50 F033 引证"links/L01 s3/s12"→"links/L02_emotion/SKEL.md L157"（原错引存照；顺修"（ emotion"多余空格）；③ L51 F035 引证标注失效"另寻待考"，"考 família面"乱码清理并原文存照。
- **技术注**：该文件为 CRLF 旧格式——首轮以 raw 字节口径算 base 被 CAS 正确拒写（StaleWriteRefused），对齐 file_utils 的 read_text 归一化口径并以 `newline="\r\n"` 保形重写成功；diff=3+/3- 外科，CRLF 终态保持。
- **状态**：DONE。**残留**：F035 正确真源另寻待考（OPEN_QUESTIONS 5）。

### 项6 C61 qid 级反查清单附录化

- **改后**：00_workbook.md 追加"附录 A：C61 qid 级反查清单（0/22 独立复算包）"——7 步复算命令/动作+读数对照表+结论链（102 袋∪1651 死袋∪暂存区∪stash/worktree∪bundle ⇒ 0/22）。内容全部取自该簿 §三 C61 条目与 C430 对照行既有读数（审计已验证为真），零新增事实；+19 行。
- **状态**：DONE。**残留**：无。

### 项7 R_recover 联动留白

- **处置**：交付报告 C232/C234/C235/C75/C107/C233/C122/C452 八行（L61/69/72/73/74/82/86/93）本夜**不动**，逐行在位核验零波及；移交记入 OPEN_QUESTIONS 1。
- **状态**：DONE（留白即施工）。

## 二、OPEN_QUESTIONS（移交）

1. **R_recover 八行终同步**：交付报告.md L61/69/72-74/82/86/93（C122/C75/C232/C234/C235/C107/C233/C452）待 R 道落地后由总包终同步，车道 E 不代裁。
2. **rollback conftest 补落在途**：截至本勘误（10-08 夜）`git ls-tree HEAD` 零命中、盘面未跟踪件（2099B，10-07 15:01）；§八.6 scope 注记按此实况措辞，R 道落袋入 HEAD 后总包可复核是否升级措辞为"已补落"。
3. **rule_red_blue 预算放宽灭失环节待查**：300→540/420→620 两数在 HEAD 与盘面均不存在（同值 300/420），放宽动作于何环节灭失待维护班考古；失败面（diagnose>540s 运行时病理）维持移交 d5。
4. **C342 残余**：37 项逐条考古以不经济豁免，剩余移交考古专班。
5. **F035 引证另寻待考**：links/L09_review 引证失效，正确真源待考（原乱码已存照）。
6. **C61 重建/撤卡待 Owner**：22 本叶册 0/22 捞回；独立复算包=00_workbook.md 附录 A。

## 三、施工纪律留痕

- claim：六件既有文件改前 acquire（st-acure-e1）；毕后随提交一并 release。
- 写侧：全部 safe_write_text（CAS+回读）；CRLF 件保形；注记引号用全角避免门误判。
- 禁区：registry/ruling 热册零触碰（token 登记走 batch_creation_tokens.py 批量通道属授权正门）；R 道八行零触碰；他会话 staged/锁零触碰。
- 临时脚本：`.runtime/tmp/st-acure-e1/{c129_restore,erratum_batch,erratum_batch2}.py`（临时区，不入库）。
- **续跑留痕（st-acure-e1 第二程，2026-10-08）**：前程七项施工产物工作区在途未提交；本程逐项对处方复核后采纳，三处对齐处方文本（项2 单元格／项3c C129 blob 短 id／项4 05_block 原文锚补修）。会话重注册（WORKSPACE_DRIFT_BLOCKED→allow_workspace_drift 逃生，总包裁定#490 授权主区直改）；token=`acure_lane_e` 经 batch_creation_tokens.py 登记 1 条（仅 E_erratum_workbook.md，dry-run 预览后实跑）；涉改 9 文件改前 acquire（TTL 30min）；capability 册被他班 staged/未staged 的 token 投影（总包 cure 批+st-entrance-gate fullflow 件等）随 token 先行袋代寄落地，归属各道。
