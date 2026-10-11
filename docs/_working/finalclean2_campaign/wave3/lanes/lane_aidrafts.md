---
ttl: task_bound
completes_when: ".aidrafts 逐目录案卷完成（体量分账/结构定性/四态构成/引用检查/处置倾向/净零线索），且机读表落 .runtime/tmp/st-fclean3-20261012/out/；零删除、零裁定，仅案卷。"
session: st-fclean3-20261012
lane: wave3-lane-aidrafts
role: read-only dossier（出案卷不出裁定）
generated: 2026-10-12T01:0x（骨架先落，边跑边 Edit 追加）
---

# 波三·车道案卷：`.aidrafts/`（只读调研，零删除）

## 0. 口径与红线（先声明，防后人误用）

- **体积口径**＝逐文件 `os.path.getsize` 求和（apparent bytes）。`du` 因簇开销虚高（在册实测 retired_lanes du 86.9MB vs 真值 12.9MB），本册所有 MB 均为 apparent。
- **活性真源**＝`SessionRegistry(Path('D:/ZephyrAlpha')).list_active_readonly()`（S4-D 分片面 `.runtime/session_registry/*.json`）。
  **禁用**单文件 `.runtime/session_registry.json`（S4-D 起只是只读兼容副本、允许滞后；实测看不见在飞的 `st-datalane-20261010`）。
- **在飞三件定窗**＝真源活性 ∧ 进程表现测 ∧ 目录 mtime 静默时长；任一为活 ⇒ 态④零动作。
- **四态口径**（沿用波二命名）：A＝原始字节==HEAD｜B＝仅行尾归一（`\r\n`→`\n`）后等｜C1＝有同名 HEAD 件但字节不等（独有字节＝增量/取证价值）｜C2＝git 查无同名件（**业务资产，Owner 门位，只登记不动**）。
- 工具红线：**禁对任何在册工具执行 `--help` 或裸跑**（波二 27 支仅 5 支带 argparse，其余 `--help` 即执行主逻辑，已酿成分支真删与 793 枚存证件 mtime 受损事故）。
- 本班动作：**零删除、零 `git add`/commit、零写 `.runtime` 根、未改任何判据/阈值/门禁代码**。

## 1. 纠偏：工令 §1 的"13 件"是**目录数**不是内容量

| 项 | 工令 §1 表述 | 实测（2026-10-12 01:08，本车道自量，全 16 目录逐文件 `os.path.getsize`） |
|---|---|---|
| 顶层目录 | 13 件逐件四态 | **16 个**（00:19 实测 14 个；新增 `st-fclean3-20261012`=本车道自身、`st-maint3-20261011`=今晚在飞维护三班） |
| 文件数 | 未给 | **327,659** |
| apparent 体量 | 未给 | **4,737.9 MiB（4.63 GB）**，为 `quarantine`(676MB) 的 **7.0 倍** |
| 隐藏件 | 未计 | `.carry_list.json`（192 B，2026-09-26，点件非目录，不计入上表） |

**与 00:19 旁测的交叉核对**（口径一致性证据）：327,659 − 286,575 = **41,084**；新增两目录件数之和
`st-fclean3`(20,533) + `st-maint3`(20,533) = **41,066**，差 **18 件**＝50 分钟内其他在飞目录的自然增长。
⇒ 工令的 286,575/4,143.9 MiB 与本课 327,659/4,737.9 MiB **同口径可派生**，"13→28.6 万件"四个数量级纠偏结论**成立**。
⚠ 但"13 件"这个分母本身也在漂（14→16，+21%）：**任何按固定件数写的处置清单一律失效**，本案卷按目录名集合逐件给。

**逐目录体量排序（apparent MiB，降序）**：

| sid | 件数 | MiB | 目录 mtime | 静默时长(至 01:08) |
|---|---|---|---|---|
| st-mineloop-20261010 | 21,568 | 311.7 | 10-11 01:10 | 24.0 h |
| st-regsolo-20261010 | 21,948 | 304.0 | 10-10 11:58 | 37.2 h |
| st-deadcure2-20261009 | 20,517 | 298.6 | 10-10 00:52 | 48.3 h |
| st-backfix-patrol-20261011 | 20,693 | 297.3 | 10-11 03:37 | 21.5 h |
| st-deadcure3b-chief-20261011 | 20,540 | 296.9 | 10-11 23:09 | 2.0 h |
| st-fclean3-20261012 | 20,533 | 296.9 | 10-12 00:55 | 0.2 h（=本车道） |
| st-maint3-20261011 | 20,533 | 296.9 | 10-12 00:58 | 0.2 h |
| st-backfix3-20261011 | 20,528 | 296.7 | 10-11 14:31 | 10.6 h |
| st-deadcure3-20261010 | 20,534 | 296.7 | 10-10 17:57 | 31.2 h |
| st-final4-20261010 | 20,437 | 296.3 | 10-10 05:13 | 43.9 h |
| st-nightmine-20261010 | 20,457 | 295.7 | 10-10 07:02 | 42.1 h |
| st-finalclean2-20261010 | 20,469 | 295.3 | 10-10 17:29 | 31.6 h |
| st-nightmine2-20261010 | 20,458 | 294.9 | 10-10 17:07 | 32.0 h |
| st-dexp-20261009 | 20,195 | 294.5 | 10-10 04:42 | 44.4 h |
| st-nightmine-20261010b | 20,387 | 293.7 | 10-10 08:47 | 40.4 h |
| st-fullflow2-20261008 | 17,862 | 271.9 | 10-08 18:20 | 78.8 h |

（每目录 top5 子目录分账＝机读表 `aidrafts_census.json`，复算见 §8 命令 1。）

## 2. 结构性前置结论：`.aidrafts/<sid>` 到底是什么（⚑ 头号发现，两条）

### 2.1 结论一：零 JUNCTION、零符号链接——全树 327,659 个节点递归扫 reparse point，命中 **0**

实测两层：
1. 顶层 16 成员 `Get-ChildItem -Force | Mode/LinkType/Target`：全部 `Mode=d-----`、`LinkType` 空、`Target={}`。
2. 递归 `os.walk(followlinks=False)` + `st_file_attributes & 0x400`（FILE_ATTRIBUTE_REPARSE_POINT）逐目录逐文件：
   **reparse_hits = 0**（脚本 `census_aidrafts.py`，输出 `aidrafts_census.json`）。

⇒ 波二在案先例 `st-mastertc-l8`（断链 JUNCTION）的"删 .aidrafts 面＝删他处真身"链接陷阱**在本面不存在**（顶层与深层都成立）。
⚠ 但真身确实"在他处"——见结论二，风险形态不是断链，而是 **git 工作树登记面**。

### 2.2 结论二：⚑ 每个 `.aidrafts/<sid>` 都是**主仓 git 工作树的注册根**（不是副本，不是草稿袋）

- 每目录根部 `.git` 均为 **gitfile**：`gitdir: D:/ZephyrAlpha/.git/worktrees/<sid>`（16/16 全中）。
- `git worktree list` 实测：`.aidrafts/st-*` **16 件全部在册**，各挂**独立分支** `session/<sid>`：

```
D:/ZephyrAlpha/.aidrafts/st-backfix-patrol-20261011  5052559681 [session/st-backfix-patrol-20261011]
... （16 条，全清单见 §8 命令 7）
```

**⇒ 判据后果（本案卷最重要的一条）**：
1. `.aidrafts` **不是"草稿袋"而是 16 个活工作树的 checkout 根**。直接 `rm -rf` 会留下
   `.git/worktrees/<sid>` 孤儿管理面（需 `git worktree remove`/`prune` 才干净），
   而 `prune` 后一旦有人跑分支清扫（在案事故主角 `sweep_merged_branches.py`），
   `session/<sid>` 分支可被删 ⇒ 该分支上**未并入 dev 的 commit 变不可达 ⇒ 被 gc 吞掉**。
   **这就是本面的真实数据丢失路径，与"目录里有什么"无关。**
2. 未并入 dev 的独有 commit 实测（`git rev-list --count dev..session/<sid>`）：
   - `st-deadcure2-20261009` **ahead=2**（branch 末提交 2026-10-09 21:45）
   - `st-mineloop-20261010` **ahead=1**（2026-10-11 01:09；⚑今晚在飞六班之矿考班）
   - 其余 14 个 sid **ahead=0**（behind 112–416 不等，即纯滞后基线）
   ⇒ **`ahead>0` 的 2 件禁按"冗余目录"处置**；`ahead=0` 的 14 件其目录内字节仍可能含未提交独有面（见 §3 四态）。
3. `.aidrafts` 与 `.worktrees` 的**同名交集只有 2 个**（`st-fclean3-20261012`、`st-finalclean2-20261010`），
   且这 2 个 sid 两侧**挂的是不同分支、不同 HEAD**：
   `st-fclean3`: `.aidrafts`=86f4c5ba6d(`session/…`) vs `.worktrees`=ccf6d852cc(`ai/st-fclean3-20261012/task-finalclean3-sweep`)
   `st-finalclean2`: `.aidrafts`=cfbebbf8dd(`session/…`) vs `.worktrees`=7b81f39121(`ai/…/task-finalclean2-loop`)
   ⇒ **"同字节双存"假设证伪**（详见 §7 净零方案）。


## 3. 活性三件定窗（逐目录，01:05–01:15 自量）

**尺一（真源活性）**＝`SessionRegistry(Path('D:/ZephyrAlpha')).list_active_readonly()` ⇒ **16 条活跃**，
其中 **12 条正好是 `.aidrafts` 的 12 个目录名**（另 4 条 = `st-gpuwo/st-gpux/st-gpux2`（不在 .aidrafts）+ `worker-e5a6077e`）。
未在册的 `.aidrafts` 目录只有 **4 个**：`st-backfix-patrol-20261011`、`st-deadcure3-20261010`、`st-nightmine2-20261010`、`st-regsolo-20261010`。

**尺一同源性核验（在册铁律"活死判定须与执行工具守卫同源"）**：`src/zephyr/gov_enforcement/rule_bridge/session_worktree.py:2199`
的清理/归档守卫正是 `registry.list_active()`（同 `_is_session_alive` 矩阵，只是 mutating=True 会写接管台账），
⇒ 本课用 `list_active_readonly()` 判得的"在册/不在册"与执行工具守卫**同一判据面**，可作处置输入。

**尺二（进程表现测）**：Win32_Process 实测 38 支 python，其中 **12 支 `heartbeat_daemon` 逐一对应上面 12 个在册 sid**，
且 9 支的第 4 参数**字面就是 `D:\ZephyrAlpha\.aidrafts\<sid>`**（fullflow2/deadcure2/nightmine/nightmineb/finalclean2/mineloop/deadcure3b/backfix3/fclean3）
⇒ 这 9 个目录**正被活进程当工作目录引用**，物理删除＝从运行进程脚下抽目录，属硬禁止。

**尺三（目录 mtime 静默）**：见 §1 表（0.2 h – 78.8 h）。

**⚑ 本课对"活性真源"的一条重要补充（波二证据链的弱点，方向与工令预期相反）**：
全部 16 个分片的 `last_heartbeat` 距今 **0.0 h**（含目录静默 78.8 h 的 `st-fullflow2-20261008`、静默 40 h 的两个 nightmine）。
原因＝这些会话注册时 `pid=0`（在册工法：短命进程必须 `register(pid=0)`），由常驻 `heartbeat_daemon` 每 30 s 续命，
**TTL 永不过期**。⇒ 真源面在这批资产上是**"常活面"而不是"在干活的证明"**：
它**不能**被用来证明"在飞"（进程面+目录面才是），更**不能**被用来证明"会话还活着所以在干活"。
波二"注册表命中 ⇒ 态④"的**结论方向可用**（保守侧、零动作），但**证据解释要换**：命中的是续命守护，不是施工活动。

**三窗合成判定**：

| sid | 尺一 在册 | 尺二 进程引用路径 | 尺三 静默 | 合成 |
|---|---|---|---|---|
| st-backfix3-20261011 | 活 | 活（daemon 指路径） | 10.6 h | **态④** |
| st-deadcure2-20261009 | 活 | 活（daemon+keeper2+monitor_a12） | 48.3 h | **态④**（⚑且 ahead=2） |
| st-deadcure3b-chief-20261011 | 活 | 活（daemon 指路径） | 2.0 h | **态④** |
| st-dexp-20261009 | 活（pid 24264） | 活（daemon） | 44.4 h | **态④** |
| st-fclean3-20261012 | 活 | 活（本车道） | 0.2 h | **态④**（自身） |
| st-final4-20261010 | 活（pid 53344） | 活（daemon+session_keeper） | 43.9 h | **态④** |
| st-finalclean2-20261010 | 活 | 活（daemon 指路径） | 31.6 h | **态④** |
| st-fullflow2-20261008 | 活 | 活（双 daemon，其一指路径） | 78.8 h | **态④** |
| st-maint3-20261011 | 活 | 活（daemon，今晚在飞六班之维护三班） | 0.2 h | **态④** |
| st-mineloop-20261010 | 活 | 活（daemon 指路径；今晚在飞矿考班） | 24.0 h | **态④**（⚑ahead=1 + 独有件最多） |
| st-nightmine-20261010 | 活 | 活（daemon 指路径） | 42.1 h | **态④** |
| st-nightmine-20261010b | 活 | 活（daemon 指路径） | 40.4 h | **态④** |
| st-backfix-patrol-20261011 | **死**（无分片） | **死**（无进程） | 21.5 h | 三窗全静 ⇒ 非态④候选 |
| st-deadcure3-20261010 | **死** | **死** | 31.2 h | 三窗全静 ⇒ 非态④候选（⚠分支末提交 10-11 22:25，见 §3.1） |
| st-nightmine2-20261010 | **死** | **死** | 32.0 h | 三窗全静 ⇒ 非态④候选 |
| st-regsolo-20261010 | **死** | **死** | 37.2 h | 三窗全静 ⇒ 非态④候选（⚑含唯一未落地交付件，见 §6.2） |

### 3.1 三窗全静的 4 件不能直接=态①：分支面仍被外部写

`git log -1 session/<sid>` 实测：`st-deadcure3-20261010` 分支末提交时间 **2026-10-11 22:25:40**（早于本课开测 2.7 h），
`st-nightmine2-20261010` 为 2026-10-11 01:19:21。目录 mtime 静默 + 无进程 ≠ 分支面无活动：
仍有批处理（归档/复活/清账链）在动这些分支。二者 ahead=0（内容已可被 dev 派生），
但**判"可删"必须有"无人在写该分支"的当窗证明**，本课未取到 ⇒ 只出态②/态③倾向，不出态①铁证（见 §6.1）。

## 4. 逐目录四态案卷（A/B/C1/C2 + 第二把尺拆分）

参照面两条，**都用**（这是本案卷与波二的机械差）：
- 尺 α：主仓 `HEAD`（dev tip `4ac4a602e2`）跟踪件集合，A/B/C1/C2 按此判；
- 尺 β：本车道自身 `session/<sid>` 的 ls-tree，把 C1 再拆 **C1_lag**（磁盘字节==车道自身 HEAD＝**基线滞后假差异**，零独有字节）
  与 **C1_unique**（对主仓 HEAD 与车道 HEAD 都不等＝**真独有字节**）；C2 再拆 **C2_lane**（车道分支跟踪件）与 **C2_orphan**（两侧 git 均查无）。
  依据＝在册教训"车道 HEAD 常落后 dev，脏里绝大部分是基线滞后的假差异"（`scan_dev_delta.py` 文首）。
- 每目录 `c1_check/c2_check` 均为 `true`（拆分集合守恒，无漏计/重计）。
- ⚑ **参照面是移动靶（本课实测坐实）**：四态尺 α 起批时主仓 `HEAD`＝`4ac4a602e2`、跟踪件 **20,547** 枚；
  本课收尾自量（01:2x）时同一条 `git ls-tree -r -z HEAD` 已变 **20,563** 枚（+16）——**今晚主仓仍在被别处提交**。
  ⇒ 本表所有 A/B/C1/C2 数字**只对 `4ac4a602e2` 这个参照点成立**，复算者必须先 `git rev-parse HEAD` 对齐参照点再比数值，
  否则会把"参照面漂移"误读成"车道新增独有面"。
  （正面副产品：`st-backfix3`/`st-deadcure3b-chief`/`st-maint3` 三个零独有字节目录的 A 恰为 **20,547**＝当时的 HEAD 跟踪件全量，
  件件对上，是尺 α 的一致性自证；`st-fclean3-20261012`（本车道自身）A=20,532＝缺 15 枚 HEAD 件在盘（未计入任何态，
  属"磁盘缺件"第五形，非独有面，本课如实记为残余见 §9）。
- 参照面解析自检：`selfcheck_headmap.py` 实测 NUL 记录 20,563／解析 20,563／bad 0／dups 0，
  与 `--name-only -z` 集合差为 0 ⇒ 尺 α 无漏计 HEAD 记录（排除"假 C2"）。

| sid | A 件/A MiB | B 件/B MiB | C1 计 | C1_lag | C1_unique | C2_lane | C2_orphan | 冗余(A+B+C1_lag) MiB | 独有面 MiB |
|---|---|---|---|---|---|---|---|---|---|
| st-backfix-patrol-20261011 | 20,418 / 289.2 | 0 / 0 | 65 | 65 / 6.4 | **0** | 0 | 209 / 1.7 | 295.6 | 1.7 |
| st-backfix3-20261011 | 20,547 / 297.0 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 297.0 | **0.0** |
| st-deadcure2-20261009 | 19,368 / 266.7 | 0 / 0 | 488 | 486 / 22.6 | **2 / 0.6** | 0 | 660 / 8.7 | 289.3 | 9.3 |
| st-deadcure3-20261010 | 20,493 / 291.8 | 0 / 0 | 26 | 26 / 4.7 | **0** | 0 | 14 / 0.1 | 296.5 | 0.1 |
| st-deadcure3b-chief-20261011 | 20,547 / 297.0 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 297.0 | **0.0** |
| st-dexp-20261009 | 19,428 / 269.9 | 2 / 0.0 | 446 | 446 / 20.2 | **0** | 0 | 318 / 4.3 | 290.1 | 4.3 |
| st-fclean3-20261012 | 20,532 / 296.9 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 296.9 | **0.0**（本车道） |
| st-final4-20261010 | 19,650 / 271.1 | 1 / 0.0 | 442 | 442 / 19.5 | **0** | 0 | 343 / 5.7 | 290.6 | 5.7 |
| st-finalclean2-20261010 | 20,398 / 288.8 | 0 / 0 | 70 | 70 / 6.6 | **0** | 0 | 0 | 295.4 | 0.0 |
| st-fullflow2-20261008 | 17,301 / 244.7 | 0 / 0 | 558 | 558 / 27.2 | **0** | 2 / 0.01 | 0 | 271.9 | 0.0 |
| st-maint3-20261011 | 20,547 / 297.0 | 0 / 0 | 0 | 0 | 0 | 0 | 0 | 297.0 | **0.0** |
| st-mineloop-20261010 | 20,405 / 284.8 | 11 / 0.2 | 69 | 64 / 6.2 | **5 / 4.2** | 0 | 1,082 / 16.3 | 291.2 | 20.5 |
| st-nightmine-20261010 | 19,894 / 272.9 | 28 / 1.0 | 450 | 434 / 15.7 | **16 / 4.0** | 0 | 84 / 2.1 | 289.6 | 6.1 |
| st-nightmine-20261010b | 19,897 / 273.0 | 28 / 1.0 | 447 | 444 / 19.6 | **3 / 0.04** | 0 | 14 / 0.2 | 293.6 | 0.2 |
| st-nightmine2-20261010 | 20,376 / 288.5 | 0 / 0 | 81 | 81 / 6.4 | **0** | 0 | 0 | 294.9 | 0.0 |
| st-regsolo-20261010 | 19,432 / 270.0 | 0 / 0 | 445 | 445 / 20.2 | **0** | 0 | 2,070 / 13.8 | 290.2 | 13.8 |
| **合计** | **319,233 / 4,499.0** | **70 / 2.2** | **3,587 / 184.0** | **3,561 / 175.2** | **26 / 8.8** | **2 / 0.01** | **4,794 / 53.0** | **4,676.4（98.7%）** | **61.8（1.3%）** |

**体量构成（哪一层吃掉了 4.7 GB）**：`docs` 2,432.7 MiB（51%）＞ `data` 709.2 ＞ `src` 706.2 ＞ `tests` 497.0 ＞ `scripts` 314.6
（每目录 top5 子目录分账＝`aidrafts_census.json`；例：regsolo 的 docs=149.0 MiB）。
⇒ 冗余主体是**整仓签出副本**，与"草稿/证据"语义无关。

**C2_orphan 的内部分层（⚑"业务资产＝Owner 门位"必须分层，否则 44 MiB 编译缓存冒充资产）**：

| 层 | 件数 | MiB | 定性 |
|---|---|---|---|
| derived_cache（`.pyc`/`__pycache__`/`.ruff_cache`） | 2,975 | 44.91 | 可再生派生物，零取证价值 |
| lane_local_runtime（`<lane>/.runtime/**`） | 1,794 | 7.98 | 车道本地审计/暂存台账（本班只登记） |
| docs_asset | 7 | 0.10 | **不可再生**（未落地交付件，见 §6.2） |
| data_asset | 13 | 0.01 | 状态快照（多为可再生） |
| code_asset / other | 5 | 0.01 | 含 `.env.clickhouse`/`.env.postgres`（与主仓**字节全等**的密钥件，见 §6.3） |
| 合计 | 4,794 | 53.0 | — |

（全量清单＝`aidrafts_c2_orphan_classified.csv`，25 件非缓存业务件逐条列于 §6.2。）

**硬链接/物理去重实测（第三把尺，防"apparent 虚高"误判）**：逐 (dev,ino) 去重后
`shared_with_main = 0.0 MiB`、`first_seen_here = 4,738.5 MiB`、`nlink>1 = 0`；
`fsutil hardlink list` 抽样自证（`.aidrafts/st-backfix3.../docs/registry_of_registries.yaml` 只列自身）。
⇒ **`.aidrafts` 与主仓零硬链接共享，apparent＝物理实占，4.7 GB 可回收量是真额度**；
唯一发现的硬链接对是 `config/.env.clickhouse` ↔ `.runtime/tmp/st-deadcure2-20261009/runlane_3/config/.env.clickhouse`（在他面，不在本面）。

## 5. 引用检查（台账 / 存证面 / 注册表册 / 裁定册 / 代码读者）

命令与实测（主仓 dev 工作区面，01:15）：

```bash
cd D:/ZephyrAlpha
sid=st-regsolo-20261010
grep -rl --include=*.md --include=*.yaml "$sid" docs/_working/            | wc -l   # 台账命中
grep -rl --include=*.yaml "$sid" docs/01_policies_and_standards/_registry/catalogs/ | wc -l
grep -rl "$sid" docs/01_policies_and_standards/rules/ docs/ruling_registry.yaml | wc -l
grep -rl --include=99_checkpoint.md "$sid" docs/ | wc -l
grep -rl "$sid" src/ scripts/ tests/ | wc -l
```

| sid | docs/_working 文件数 | catalogs | rules+ruling | 99_checkpoint | **代码面(src/scripts/tests)** | 独有件（波二记法交叉核） |
|---|---|---|---|---|---|---|
| st-backfix-patrol-20261011 | 2 | 0 | 0 | 0 | **0** | — |
| st-backfix3-20261011 | 3 | 0 | 0 | 0 | **0** | — |
| st-deadcure2-20261009 | 6 | 2 | 0 | 0 | **0** | 波二记 2 件 ⇒ 本课 C1_unique=2，**逐件全等命中** |
| st-deadcure3-20261010 | 3 | 1 | 0 | 0 | **0** | — |
| st-deadcure3b-chief-20261011 | 2 | 1 | 0 | 0 | **0** | — |
| st-dexp-20261009 | 11 | 1 | 0 | 0 | **1** | 波二记 4 件 ⇒ 本课仅 1 件仍在 C2_orphan，**3 件已被主仓吸收**（见下） |
| st-fclean3-20261012 | 1 | 1 | 0 | 0 | **0** | 本车道 |
| st-final4-20261010 | 2 | 1 | 0 | 0 | **0** | — |
| st-finalclean2-20261010 | 5 | 1 | 0 | 0 | **4** | — |
| st-fullflow2-20261008 | 10 | 3 | 0 | 0 | **4** | — |
| st-maint3-20261011 | 6 | 1 | 0 | 0 | **2** | 今晚在飞 |
| st-mineloop-20261010 | **46** | 2 | 0 | 1 | **5** | 今晚在飞矿考班 |
| st-nightmine-20261010 | 24 | 2 | 0 | 1 | **0** | — |
| st-nightmine-20261010b | 1 | 0 | 0 | 0 | **0** | — |
| st-nightmine2-20261010 | 9 | 2 | 0 | **2** | **0** | — |
| st-regsolo-20261010 | 5 | 2 | 0 | 0 | **18** | — |

- **裁定册零命中**：16 个 sid 在 `docs/01_policies_and_standards/rules/` 与 `ruling_registry.yaml` 全部 **0 命中**
  ⇒ 本面无任何裁定绑定的存证义务（不是"裁定资产"）。
- **代码有读者**的 6 个 sid（dexp 1 / finalclean2 4 / fullflow2 4 / maint3 2 / mineloop 5 / regsolo 18）：
  命中样例为 `.runtime/tmp/<sid>/...` 形式的路径字面量与台账互引（例：`regsolo` 18 支多为 `.runtime/tmp/st-regsolo-20261010/tools/…` 的被引），
  **不是对某个 `.aidrafts/<sid>` 的运行时读依赖**（本课 01:2x 实测：`grep -rl "\.aidrafts/st-" src/ scripts/ tests/` 命中
  **12 支**（`scripts/governance/wave2/lane_inventory.py`、`wave1b/dead_letter_prescriptions.py`、`wave1b/claim_gate_repro.py`、
  `d5_architecture/generators/generate_dev_delivery_map.py`、`wave11/w178_universe_facts_gen.py` 等＋同名 `.pyc`），
  命中的全是 **`.aidrafts/st-` 通配形态的面遍历/盘点型读者**；
  而 `grep -rl "\.aidrafts/<具体 sid>" src/ scripts/ tests/` 对 patrol/deadcure3/nightmine2/regsolo/mineloop **均为 0 命中**）。
  ⇒ 结论修正为两条：① 无任何代码按 sid 硬路径依赖这些目录；② **但 `.aidrafts` 作为"面"有 12 支在册读者**
  （车道盘点/死信处方/交付图生成），改面形状（少一棵树、路径形态变化）会落到这些生成器输出上 ⇒ 清理须同窗复跑这 12 支的产物校验。
  ⇒ 引用面判"文档史实"而非"运行依赖"；但 18 支对 regsolo tmp 面的引用意味着**该车道工具链仍被后续班当参考**，
  与"死车道"结论不完全自洽，本课如实记为**存疑**。
- ⚑ **波二"独有件"字段的时效性硬证**：波二给 dexp 记的 `data/audit-trail/vhdx_growth_series.jsonl` 等 4 件，
  本课实测主仓已有同名件且**车道字节==主仓 HEAD（落入 A 类）**，`c2_orphan/c1` 里查无此件；
  4 件中仅 `docs/_working/dexp_campaign/05_worktree_handoff_zongdui.md` 仍为 C2_orphan。
  ⇒ 波二快照的"独有件"清单**已被 dev 演进吸收**，禁止当现值沿用（工令"波二判读不可直接沿用"在机械层坐实）。


## 6. 处置建议（只给倾向＋证据等级；**禁裸删**；C2 一律"登记呈批"）

证据等级：**E3＝三源互证可复算**｜**E2＝两源**｜**E1＝单源/存疑**｜**E0＝未取到（禁止据此动手）**

### 6.1 逐目录倾向

| sid | 态倾向 | 证据等级 | 依据与前置 |
|---|---|---|---|
| st-backfix3 / st-deadcure3b-chief / st-fclean3 / st-maint3 | **态④**（在飞/自身） | E3 | 在册活 + daemon 指路径 + 静默 <11 h；四态 A=100%（C1=C2=0，**全仓零独有字节**，是"最可清但最不能碰"的形态） |
| st-mineloop / st-dexp / st-final4 / st-finalclean2 / st-fullflow2 / st-nightmine / st-nightmine-20261010b / st-deadcure2 | **态④** | E3 | 在册活 + 有 heartbeat daemon（其中 9 件 daemon 参数即该路径）；**mineloop 另加 ahead=1 与 5 件 C1_unique、deadcure2 加 ahead=2** ⇒ 双重不可动 |
| st-backfix-patrol-20261011 | **态③** 墓碑 30 天窗 | E2 | 三窗全静（无分片/无进程/21.5 h）；四态独有面仅 1.7 MiB 且**全部是 `.pyc`/`.runtime` 派生物**（C1_unique=0、非缓存 C2=0）；**E0 缺项**＝分支面无活动证明未取到 |
| st-deadcure3-20261010 | **态③**（附"分支面刚被写"红旗） | E1 | 三窗全静，但分支末提交 **10-11 22:25**＝2.7 h 前，说明仍有链在动该分支；独有面 0.1 MiB（无 C1_unique）；**须等当窗无写证明再议** |
| st-nightmine2-20261010 | **态③** | E2 | 三窗全静 32 h；C1_unique=0、C2=0（**除 A/B/C1_lag 外零资产**）；`99_checkpoint.md` 有 2 处引用 ⇒ 墓碑 `successor_of` 须指向该 checkpoint 族 |
| st-regsolo-20261010 | **态② 先救后清** | E3 | 三窗全静 37 h，但**唯一"仅存活于车道"的业务交付件**在这里：`docs/_working/regsolo_campaign/99_delivery.md` + `lanes/t1..t4.md` 5 件（67.8 KB）主仓查无同名（C2_orphan），且代码/台账 18+5 处引用该车道；**必须先 cp -n 存证＋呈批落地，再谈目录** |

### 6.2 本面唯一必须抢救的清单（非缓存 C2_orphan，25 件 / 0.11 MiB，逐件字节）

**救＝cp -n 到 `.runtime/tmp/<本班>/rescue/<sid>/<rel>` + 登记呈批，绝不等于删**。
标 ⚑ 者＝主仓同名件不存在（唯一存活处）。

```
⚑ st-regsolo-20261010  docs/_working/regsolo_campaign/99_delivery.md                     14,821 B
⚑ st-regsolo-20261010  docs/_working/regsolo_campaign/lanes/t1_direct_write_callgraph.md 14,315 B
⚑ st-regsolo-20261010  docs/_working/regsolo_campaign/lanes/t2_belt_materialization.md   18,264 B
⚑ st-regsolo-20261010  docs/_working/regsolo_campaign/lanes/t3_hot_registry_inventory.md 15,160 B
⚑ st-regsolo-20261010  docs/_working/regsolo_campaign/lanes/t4_ledger_debt_incidents.md  15,201 B
   st-regsolo-20261010  activate_env.ps1 355 B ／ data/red_blue/trigger_queue/*.json ×4（2,027 B）
   st-regsolo-20261010  config/.env.clickhouse 596 B ／ config/.env.postgres 451 B  ← 见 §6.3
⚑ st-dexp-20261009     docs/_working/dexp_campaign/05_worktree_handoff_zongdui.md         2,515 B
⚑ st-mineloop-20261010 docs/_working/mineloop_campaign/10_exam_recast_quintile.yaml      24,029 B
   st-mineloop-20261010 data/local_fallback/**（5 件 2,425 B）、data/cache·databases·runtime/state 4 件、logs 2 件
```

C1_unique 26 件（8.8 MiB）的方向定性（本课第三把尺，逐件 lane vs main 行/键/字节对比）：
- **22 件车道副本更小/更少行 ⇒ 陈旧快照，已被主仓超越**（`ruling_registry.yaml` lane 4,454 L < main 4,563 L、
  `capability_canonical_file_registry.yaml` lane 68,177/67,489 L < main 69,042 L、`exam_scores_v1.yaml` 408 L < 1,602 L 等）
  ⇒ 取证价值＝"历史版本"，不是增量资产；**别拿它当"必须救"，但要留 sha 指纹备案**（该快照 git 两仓都查无）。
- **2 件字节数与主仓完全相同而 sha 不同**（mineloop `rule_catalog_registry.yaml` 117,173 B、
  `exit_simulator.py` 26,487 B）⇒ 疑似**第三种行尾/空白口径**（`\r`-only 或尾随空白），非真增量。
  ⚑ 本案卷只登记"口径边界"，**禁改归一口径**（在册红线：不得改判据/阈值）。
- **2 件车道副本更大**：`nightmine build_news_sentiment_window.py`（198 L/8,507 B > 196 L/8,233 B）、
  nightmine 的 12 枚 `exam_cards/**` 校准 yaml（多 5–15 行、少 20–100 B）⇒ **形态互斥，必须逐件 diff 才能定增删**，
  E1 存疑，本班不出结论（nightmine 在册活 ⇒ 态④，本班无权限也无必要动）。

### 6.3 ⚑ 密钥面告警（独立于清理，须呈报）

`st-regsolo-20261010/config/.env.clickhouse`、`.env.postgres` 与主仓同名件 **sha256 全等**、
且主仓该两件为 **git 未跟踪**（`git ls-files` 查无）⇒ 密钥明文在 `.aidrafts` 面存在**第二份未纳管副本**。
本课零动作、只登记：任何后续"清理/打包/外发/镜像"动作都会把这枚密钥带出治理面（违反 RULE-SECRETS 三道 gate 的意图面）。
⇒ **呈 Owner 门位处置（不在 AI 权限内）**，且它同时是"本目录不是纯冗余"的反证之一。

### 6.4 净可回收额度（机械下界，供统筹排产，**不是删除指令**）

- 全面 apparent 4,738.5 MiB；A+B+C1_lag 冗余 = **4,676.4 MiB（98.7%）**；
- 扣掉 12 个在册活目录的体量（态④零动作）后，**三窗全静的 4 个目录合计 1,188.7 MiB**（patrol 297.3 + deadcure3 296.7 + nightmine2 294.9 + regsolo 304.0），
  其中"非缓存业务件"仅 78.7 KiB ⇒ **若态②抢救完成＋态③墓碑生效，本面单批最多回收 ≈1,188.6 MiB（占总面 25.1%）**；
  剩余 75% 挂在在册活目录上，**今晚一律不动**。

## 7. 净零线索：`.aidrafts` vs `.worktrees` 的收敛方案（统筹要的"合并/清理处理方式"）

### 7.1 判据先行（双存假设已证伪，别按"重复面"合并）

| 面 | 成员数 | 性质 | 分支命名 | 与 `.aidrafts` 同名交集 |
|---|---|---|---|---|
| `.aidrafts/<sid>` | 16 | 主仓注册工作树（`.git` = gitfile → `.git/worktrees/<sid>`） | `session/<sid>` | — |
| `.worktrees/<sid>` | 6 | 同为注册工作树，另一套 | `ai/<sid>/task-<slug>` | **仅 2 个**：`st-fclean3-20261012`、`st-finalclean2-20261010` |

且这 2 个同名 sid **两侧 HEAD/分支不同**（fclean3：86f4c5ba6d vs ccf6d852cc；finalclean2：cfbebbf8dd vs 7b81f39121）
⇒ **不是同字节双存**，是**同一会话被两套工法各开一棵工作树**（IDE 草稿工法开 `session/*` 到 `.aidrafts`，
治理工法 `session_worktree_start` 开 `ai/*/task-*` 到 `.worktrees`）。
字节层面的实测支持：fclean3 侧 `.aidrafts` 面 A=20,532/296.9 MiB、C1=C2=**0**（＝与主仓 HEAD 全等，零独有），
`.worktrees` 侧是本车道真正在写的面 ⇒ **`.aidrafts/st-fclean3` 这一棵是纯粹的"零独有字节影子树"**。

### 7.2 内收方案（按"同真源可派生→必并／零触发零消费→退役"铁律给倾向，不出裁定）

1. **唯一真源应定为 `.worktrees` + `ai/<sid>/task-*` 分支**（它才是 `session_worktree.py` 守卫/归档链/GW 计数消费的面；
   `.aidrafts` 面的 16 棵树在治理链里**无按 sid 的读依赖（§5 实测 0 命中），但面级通配读者有 12 支**（§5 末条）——
   这既是"可退役"的依据，也是"改面形状须同窗复跑 12 支产物"的约束）。
   ⇒ 对象=会话工作树根位置，跨域不同对象不并的例外判据**不适用**（同一对象：一次会话的工作树）。
2. **`.aidrafts` 的内收路径＝退役（轨 A）**，但**结构性前置三件**必须先满足（缺一即事故）：
   (a) 每棵树先跑 `git worktree remove`（**不是** `rm -rf`），避免 `.git/worktrees/<sid>` 孤儿管理面；
   (b) `session/<sid>` 分支的 `ahead>0` 者（deadcure2=2、mineloop=1）**禁随树清**，分支寿命与目录解绑；
   (c) §6.2 的 25 件非缓存 C2_orphan 先 cp -n 存证并呈批。
   ⇒ 建议对 **三窗全静 + 零独有字节** 的 `st-nightmine2`、`st-backfix-patrol` 先开**态③墓碑 30 天窗**试点
   （`successor_of` 指针指向 `.worktrees` 同 sid（若无则指向主仓 dev 工作区）＋ `docs/_working/finalclean2_campaign/wave3/lanes/lane_aidrafts.md`）。
3. **净零增长声明（本车道自身）**：`.aidrafts` 现在**多出 2 棵影子树**（`st-fclean3`、`st-maint3`）＝本班与今晚维护班各一棵，
   各自在 `.worktrees` 已有/将有正树。若 IDE 工法持续产出 `.aidrafts` 影子树，**每轮会话净增 ≈297 MiB / 20,540 件**，
   这才是 4.7 GB 的生成机制 ⇒ 净零的根不在"删旧"，在**停发第二棵树**：
   建议统筹呈报"会话工作树根唯一化（`.aidrafts` 停开新树）"为收敛项，替代"清 `.aidrafts`"的一次性动作。
   （⚠ 本课**未改任何门禁/判据代码**，此项只是案卷倾向。）
4. **`.worktrees` 侧不并入 `.aidrafts`**：`st-gpuwo/gpux/gpux2/maint2` 四棵无 `.aidrafts` 对应物，且在飞；
   `st-maint2-20261011` 与在飞的 `st-maint3-20261011` 是**不同 sid 的接续关系**（非重名冗余），
   合并判据应走 `successor_of` 而不是字节去重。

## 8. 复算命令清单（每条本班自测能跑；**全部只读**——逐条已查写面，见 §8.5 自纠）

```bash
# 1) 体量分账（件数/apparent MiB/top5 子目录/reparse 扫描）→ out/aidrafts_census.json
cd D:/ZephyrAlpha && python .runtime/tmp/st-fclean3-20261012/tools/census_aidrafts.py

# 2) 四态尺 α（对主仓 HEAD 判 A/B/C1/C2）→ out/aidrafts_4state.json + out/c1_<sid>.jsonl + out/aidrafts_c2.jsonl
python .runtime/tmp/st-fclean3-20261012/tools/four_state_aidrafts.py            # 全部 16 目录（约 90 s）
python .runtime/tmp/st-fclean3-20261012/tools/four_state_aidrafts.py st-regsolo-20261010   # 单目录

# 3) 四态尺 β（把 C1 拆 C1_lag/C1_unique、C2 拆 C2_lane/C2_orphan）→ out/aidrafts_delta.json
python .runtime/tmp/st-fclean3-20261012/tools/delta_vs_lane_head.py

# 4) 第三把尺：硬链接/物理去重量测（证 apparent=物理实占）
python .runtime/tmp/st-fclean3-20261012/tools/hardlink_measure.py

# 5) 活性真源（只读探针，禁换 list_active——它会写接管台账并收割分片）
python -c "import sys;sys.path.insert(0,'src');from pathlib import Path;\
from zephyr.security.access_control.session_concurrency import SessionRegistry;\
print([s.session_id for s in SessionRegistry(Path('D:/ZephyrAlpha')).list_active_readonly()])"

# 6) 进程表现测（Git Bash 会把 schtasks 斜杠吞成路径，故用 PS 形式）
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='pythonw.exe'\" | Select-Object ProcessId,CommandLine | Format-Table -AutoSize -Wrap"

# 7) 结构定性（工作树注册面 + 每棵树独有 commit 数 + 参照面件数）
git worktree list
git rev-list --count dev..session/<sid>          # >0 ⇒ 该分支有未落地 commit，目录禁按冗余处置
git rev-parse --short HEAD; git log -1 --format=%ci HEAD    # 先钉住参照点（本册＝4ac4a602e2）
git ls-tree -r --name-only HEAD | wc -l          # HEAD 跟踪件数：01:09=20,547 / 01:2x=20,563（移动靶，勿混用）
#    ⚠ 禁写成 `ls-tree -r -z HEAD | wc -l`：-z 用 NUL 分隔，wc -l 恒得 1（本课自纠出的假复算命令）

# 7b) 尺 α 参照面无漏计自证（NUL 记录数 == 解析数 == --name-only 集合）
python .runtime/tmp/st-fclean3-20261012/tools/selfcheck_headmap.py

# 8) 单件四态抽查复算（示例：A 类件与 C1_unique 件各一枚）
python - <<'PY'
import hashlib,subprocess
from pathlib import Path
rel="docs/registry_of_registries.yaml"
lane=Path(".aidrafts/st-backfix3-20261011")/rel
data=lane.read_bytes()
b=subprocess.run(["git","show",f"4ac4a602e2:{rel}"],capture_output=True).stdout   # 钉参照点，勿用 HEAD（移动靶）
def gitsHA1(x):
    h=hashlib.sha1();h.update(b"blob %d\0"%len(x));h.update(x);return h.hexdigest()
print("disk==HEAD blob sha1:",gitsHA1(data)==gitsHA1(b))
print("eol-normalized equal:",data.replace(b"\r\n",b"\n")==b.replace(b"\r\n",b"\n"))
PY

# 9) C2_orphan 分层与逐件清单（25 件非缓存业务件的权威表）
python -c "import json,collections;from pathlib import Path;\
items=[json.loads(l) for l in Path('.runtime/tmp/st-fclean3-20261012/out/c2_orphan_items.jsonl').read_text(encoding='utf-8').splitlines()];\
print(collections.Counter(Path(e['rel']).suffix for e in items).most_common(8))"
cat .runtime/tmp/st-fclean3-20261012/out/aidrafts_c2_orphan_classified.csv
```

### 8.5 复算命令自纠（在册"只读复核命令里藏写盘"教训）

- 命令 1–4 的脚本**只写 `out/` 与 `tools/` 两处本班 tmp**，对 `.aidrafts`、主仓、`.runtime` 根**零写**（源码可查：只有 `lstat/read_bytes` 与 `OUT/*.json|jsonl|csv` 落笔）。
- 命令 1 首轮曾因 `Path.is_dir(follow_symlinks=False)` 抛 `TypeError`（Python 3.12 无该参数）而**整批失败**，
  已修为 `os.lstat` 判目录后复跑 ⇒ 复算前请确认拿到的是 `dirs=16` 而非 traceback。
- `delta_vs_lane_head.py` **非幂等**：`c1_unique_items.jsonl`/`c2_orphan_items.jsonl` 为 append 模式，
  复跑前必须 `rm -f` 这两件（本班已按此流程做），否则计数翻倍——**这是本课自查出的唯一写盘面**。
- **命令 5 绝对不可换成 `list_active()`**：该方法 `mutating=True` 会**写接管台账并物理收割超宽限分片**（源码
  `session_concurrency.py:1516-1524` 明示），属"只读复核命令藏写盘"的标准形态。
- 本课**未对任何在册工具执行 `--help` 或裸跑**；`scan_dev_delta.py` 仅 `Read` 其源码复用哈希口径。
- ⚑ **本轮自纠（在册"只读复核命令藏写盘"同型预防）**：首版 §8 命令 7 曾把复算写成
  `git ls-tree -r -z HEAD | wc -l`——`-z` 用 NUL 分隔，`wc -l` 恒得 1，是**能跑但必给假数**的坏命令，已改正为
  `git ls-tree -r --name-only HEAD | wc -l` 并加 `selfcheck_headmap.py` 集合差自证。
  ⚠ 本课内部锚点（§5/§6 编号在追加中移位）已逐条 `grep` 复核改指（`§4 逐目录四态`/`§6 处置`/`§7 净零`/`§8 复算` 结构完整）。

## 9. 残余与未覆盖面（如实报，禁拿抽样当全集）

| 项 | 状态 |
|---|---|
| 四态扫描 | **全集完成**：16/16 目录、327,702 件逐件判态（每目录 `c1_check/c2_check=true` 守恒自证），无抽样 |
| `>64 MiB` 单件 | 实测 `pending_big_*` **空文件未生成** ⇒ 本面无 64 MiB 以上单件，无因内存红线漏判的件 |
| C1_unique 26 件内容级 diff | **未做**（本课只出行/键/字节方向指标定性）；nightmine 12 枚 exam_cards 与 1 枚 .py 需逐件 diff 才能定增删 ⇒ E1 残余 |
| 22 件"陈旧快照"的 git 可达性 | **未证**：它们既不在主仓 HEAD 也不在车道 HEAD，是否可从 blob/队列/存证面反查未核 ⇒ 若走态③需先按在册"path+blob_sha256 反查"手法确认唯一存活面 |
| `.git/worktrees/<sid>` 管理面体量 | **未量**（不在 `.aidrafts` 面内，属 `.git` 面；影子树的真实磁盘成本应含此项，统筹排产时勿混面） |
| 分支面当窗写活动证明 | **未取**：`st-deadcure3` 分支 2.7 h 前仍被写 ⇒ 4 个三窗全静目录的态①判定**全部 E0**，本案卷不出态①铁证 |
| 磁盘缺件（第五形） | 本车道 `st-fclean3-20261012` 面 A=20,532 而参照点跟踪 20,547 ⇒ **15 枚 HEAD 件不在盘**（不计入任何态）。本课未逐枚查明缺件名与成因（工作树创建点/部分 checkout），**若日后按"件数守恒"推体量，此处必漂** |
| 参照点漂移 | 四态数字全部锚 `4ac4a602e2`（01:09）；01:2x 复量 `git ls-tree -r --name-only HEAD`＝20,563（+16）⇒ 复算须先钉参照点 |
| 波二 14 面判读沿用性 | **不可沿用**已坐实（dexp 4 件独有件中 3 件已被 dev 吸收；活性面是 daemon 续命而非施工） |
| 本班删除动作 | **零**（含 `rm` 仅限本班自身 tmp 的重复产物，见 §8.5） |

