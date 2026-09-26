---
ttl: task_bound
completes_when: L07 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L07_exec（执行链路）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L07_exec`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **9**（EXE-1…EXE-9） | `grep -oE 'EXE-[1-9]\b' L07_exec/SKEL.md \| sort -u \| wc -l` → 9（**陷阱**：`grep -oE 'EXE-[0-9]+'` 会把战斗地图号 `BM-EXE-06` 捕成第 10 个号，本道已用 `\b`+一位数限定） |
| _INDEX 声明叶 | **9** | `grep -c '^| EXE-' L07_exec/_INDEX_MINE.md` → 9 |
| 盘上 `s*/MINE.md` | **9** | `find L07_exec -name MINE.md \| wc -l` → 9 |
| 声明未落盘 / 盘上未声明 | **0 / 0** | 差集为空；`_INDEX_MINE.md` 第二列给了目录路径（`s1_signal_to_order/`…），块号 EXE-1↔s1 全对齐 |

## 2. 叶子六向与封矿主张质量（1b）

9/9 片叶子六标号齐，行长 71–88；`_INDEX_MINE.md` 逐行给了"六向 = **6/6**"自评分列（本 campaign 唯一把六向填装度机读化的环节）。
**封矿主张层：9/9 片叶子写了"封矿判据"句，而父册 SKEL 判的不是封矿**：`SKEL.md:157` "**计数：9 子块｜SEALED 0｜MINING 9｜BLOCKED 0**"、`:201` "本簿 **MINING**（9/9 子块有正文级未读指针）…**封矿前置=清空 §3 清单后复核**"。⇒ **叶说封、父说明文未读满 9 块**，父子互斥（P1）。
**三扫 0 处／拉平 0 处／命令块 0 处**（`grep -c 三扫 L07_exec/*/*/MINE.md` 全 0；`grep -rl '```' */*/MINE.md | wc -l` → 0）。

## 3. 引用证据复跑（1c）—— **含本 campaign 最硬的一条 P0**

`cited=34 ok=32 not_in_head=2 line_beyond_eof=0`（正则口径）→ 表观通过率 94%。**但正则口径漏掉了"文件名与冒号之间隔空格"的锚**（本环节文档惯用 `` `sim_daily_runner.py` :544-565 `` 写法），逐条人工复核后翻出下列硬伤：

| 论断（出处） | 命令 | 观察（**四种口径全查**） | 判定 |
|---|---|---|---|
| `s1_signal_to_order/MINE.md:19`：代码件 `scripts/backtest/sim_daily_runner.py`，**"1,356 行"**，出处标"**本册 sed 实测**" | `git show HEAD:scripts/backtest/sim_daily_runner.py \| wc -l` | **892** | **P0 证伪** |
| 同上文件行数 | `wc -l < /d/ZephyrAlpha/scripts/backtest/sim_daily_runner.py`（主区工作树）＋ `git -C /d/ZephyrAlpha status --porcelain -- scripts/backtest/sim_daily_runner.py`（输出空＝未改） | **892**，且主区无该文件改动 | **P0：HEAD 与主区两个口径都是 892** |
| 同上文件是否另有其身 | `git ls-files \| grep -i sim_daily_runner` → 只有 `scripts/backtest/sim_daily_runner.py` ＋ 其测试；再 `find .aidrafts .worktrees -name sim_daily_runner.py` 逐个 `wc -l` | 抽 12 份副本**全部 892 行** | **P0：本仓不存在 1,356 行的该件** |
| `s1_signal_to_order/MINE.md:28/66`：`settle posture_check` 在 **`:1212-1220`**；常量区 `:98-165`、正文 `:490-660` | `git show HEAD:scripts/backtest/sim_daily_runner.py \| sed -n '1212,1220p'` | 空输出（文件只到 892 行） | **P0：行锚越界 320 行，"signal 级实读"记录无法成立** |
| `config\quarantine\qmt_trade_csv_quarantine_20260622\trade_stats.json:4`（`s2_order_pipeline/MINE.md:31`，反斜杠路径） | `git cat-file -e HEAD:config/quarantine/qmt_trade_csv_quarantine_20260622/trade_stats.json` | 不存在；该件属运行态隔离区产物，不在版本面 | **P2**：把盘面一次性产物当"实测"证据，无复现通道 |

⇒ **L07 是全 campaign 唯一被证伪"自称实测"的环节**：它标注"本册 sed 实测"的行数与行锚在任何可得口径上都不成立。按本次审计的判据（"复跑不出来的封矿主张就是洞"），L07 的 §②"现状实测"整面须重做。

## 4. 施工项（1d）

`L07-C01..C10` **10/10 有定义行（全在 SKEL，`grep -cE '^\|\s*\*{0,2}L07-C[0-9]{2}' L07_exec/SKEL.md` → 10）**；表头 `\| # \| 项 \| 内容与真源 \| 沿用账本 \| 内收声明/优先 \|`（`SKEL.md:163`）⇒ **无验收判据列、无归属列**：探测 **9/10 行无判据语、8/10 行无归属语**。

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L07-H1 | **P0** `sim_daily_runner.py` 行数与 `:1212-1220` 行锚在 HEAD/主区/12 份副本上全部证伪，"本册 sed 实测"不实 | §3 三条命令 | `s1_signal_to_order/MINE.md` §② 整面按 HEAD 892 行重标（就地改，不新建件） |
| L07-H2 | **P1** 叶 9/9 判"封矿"、父 SKEL 判"MINING 9/9 未读正文" | §2 行号 | `_INDEX_MINE.md` 或 SKEL §6 二者取一统一口径并注明依据 |
| L07-H3 | **P1** 施工表无判据列（9/10 无判据）＋无归属（8/10） | §4 表头 | SKEL §5 表头补列（等长替换） |
| L07-H4 | P2 运行态隔离件当证据（trade_stats.json） | §3 | 该册改引"盘面读数＋取数时刻"或降级为观察 |
| L07-H5 | P1 三扫/拉平/命令块零留痕 | §2 | `_INDEX_MINE.md` 增封矿证据表 |

**总判**：结构齐（9/9/0/0），但**证据面被正面证伪**（H-01 属 P0 级"文档说完成/实际不然"的教科书样本），且**父册自己就没判封矿**——叶层的"封矿"字样因此属越权表述。L07 **不得作为施工输入**，须先做 H-01 重标。
