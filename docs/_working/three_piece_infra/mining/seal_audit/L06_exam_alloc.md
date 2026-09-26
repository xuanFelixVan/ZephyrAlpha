---
ttl: task_bound
completes_when: L06 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L06_exam_alloc（策略考试与条件共振上岗）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L06_exam_alloc`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **8**（L06-A…L06-H） | `grep -oE 'L06-[A-H]' L06_exam_alloc/SKEL.md \| sort -u` → 8 个号（SKEL 用三态表行 `L06-F 条件共振判定` 式列块，无 `### L06-` 标题：`grep -c '^### L06-' L06_exam_alloc/SKEL.md` → 0）；叶层 `_INDEX.md` 逐簿回指 `L06-A + L06-B` 等，映射可见 |
| _INDEX 声明叶 | **5** | `grep -c '^| \`' L06_exam_alloc/_INDEX.md` → 5 |
| 盘上 `*/MINE.md` | **5** | `find L06_exam_alloc -name MINE.md \| wc -l` → 5 |
| 声明未落盘 / 盘上未声明 | **0 / 0** | 差集为空；8 块压 5 簿有 `_INDEX` 第二列的显式块号（本环节是九环节里**唯一给了块号对表**的） |

## 2. 叶子六向与封矿主张质量（1b）

5/5 片叶子六标号齐，行长 79–104；`_INDEX.md` 另有"①…⑥ 六向 ✓ 矩阵 + 自审闸三态"逐簿打勾表（本 campaign 唯一）。
**封矿口径冲突**：`SKEL.md:157` "**簿级裁定：SEALED**——八子块六向全填、使命指定指针文件全读…深读尾差 3 件（不阻骨架封矿）"并逐条列出 3 件（`f06_e4_wfa_exam.py` 折切纯函数区、`deflated_sharpe_calculator` V[SR] 公式区、`mSPRT calibrate_tau`）；而 `_INDEX.md` 的逐簿三态写的是"**施工 C11 / 挂起 …**"类施工态、且叶层 §⑤ 把多数缺口判"施工"。⇒ SKEL 判 SEALED、叶层判"有待施工"——**不是互斥**（SKEL 明写"不阻骨架封矿"），是本次审计里**唯一一处父子口径自洽**的样板。
**但三扫 0 处／拉平 0 处／命令块 0 处**：`grep -c 三扫 L06_exam_alloc/*/*/MINE.md` 全 0；`grep -rl '```' L06_exam_alloc/*/*/MINE.md | wc -l` → 0 ⇒ "三扫收敛"这一封矿前置**依旧没有任何留痕**，只是它的 SEALED 有"深读尾差 3 件"的显式余量声明来替代，质量优于其他簿。

## 3. 引用证据复跑（1c）

`cited=44 ok=42 not_in_head=2 line_beyond_eof=0` → **通过率 95.5%**。

| 引用 | 命令 | 观察 | 判定 |
|---|---|---|---|
| `scripts/governance/apply_meta_question_ddl.py:147-166`（`exam_result_writeback/MINE.md:26`，写作"**DDL 真源**"）＋`:65`（同册 :32） | `git cat-file -e HEAD:scripts/governance/apply_meta_question_ddl.py`；`git -C /d/ZephyrAlpha status --porcelain --untracked-files=all \| grep apply_meta_question_ddl` | HEAD：`fatal: path ... does not exist`；主区：**`??` 未跟踪** | **P0**：被当"真源"的 DDL 件从未提交，`meta_question.meta_question_exam_result` 表结构论断在 HEAD 无据 |

其余 42 条锚（含 `exam_ops.py:102`、`condition_package.py`、`_c4_engine.py:46-48` 等）经后缀归一后全部命中且行号在文件长度内。

## 4. 施工项（1d）

`L06-C01..C19` **19 个号**，其中 **9 个无定义行**：`L06-C11, C12, C13, C14, C15, C16, C17, C18, C19`——只在叶子正文以"`L06-C11（…）`"形式被引用（`exam_result_writeback/MINE.md:78-93`、`exam_ruler_holdout/MINE.md:65-72`、`resonance_friction_assembly/MINE.md:72-73`），**SKEL 施工表只定义到 C10**；`_INDEX.md:43` 还另行引用 `L06-C16`（"prereg 预算重排=裁定门位，只登记不擅改"）。⇒ **半数以上本环节新立施工项处于"叶层有号、父层无账"状态**。
表头（`SKEL.md:161`）：`\| # \| 项 \| 内容+判据 \| 净零对价（替代/合并） \| 前置/门位 \| 优先 \|` ⇒ **九环节里契约最完整的一本**（判据列＋门位列＋优先级列俱全）；缺面仅 6/10 行判据语不足、7/10 无归属语。

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L06-H1 | **P0** "DDL 真源"件不在 HEAD（`??`） | §3 命令 | `apply_meta_question_ddl.py` 入 HEAD 袋（代码袋），随后 §② 复跑 |
| L06-H2 | **P1** 9 个施工项（C11–C19）叶层有号、父册无账 | §4 命令 | `SKEL.md` 施工表补 9 行（沿用既有表头，不加列） |
| L06-H3 | P1 三扫/拉平/命令块零留痕（虽 SEALED 声明自洽） | §2 | `_INDEX.md` 增封矿证据表 |
| L06-H4 | P2 6 个施工项判据格语不足 | §4 | 表内补格 |

**总判**：L06 的**结构、块号对表、施工契约三项是全 campaign 最好的**；它的两个洞一条在代码（P0 H-01）、一条在账（H-02）。其"簿级 SEALED"**不能按现状采信**，因 DDL 真源不在 HEAD。
