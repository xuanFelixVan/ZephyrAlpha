---
ttl: task_bound
completes_when: L01 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L01_regime（大盘状态判定）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L01_regime`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **10**（S1–S10） | `grep -c '^## [0-9]* · S' L01_regime/SKEL.md` → 10；`sed -n '23,37p' L01_regime/SKEL.md`（代码块全树） |
| _INDEX 声明叶 | **12** | `grep -c '^| \`s' L01_regime/_INDEX.md` → 12 |
| 盘上 `sNN_*/MINE.md` | **12** | `find L01_regime -name MINE.md \| wc -l` → 12 |
| 声明未落盘 | **0** | _INDEX 声明集 − 盘上集 = ∅ |
| 盘上未声明 | **0**（相对 _INDEX） | 同上取反 = ∅ |
| 相对 SKEL 的净增 | **2**（`s11_validation_family`、`s12_secondary_model_farm`） | `_INDEX.md` 明写 s12 为"SKEL 十子块树之外的净增矿脉"；SKEL §0 标题仍写"10 子块" |

**号位冲突（H-08）**：SKEL 的 S3–S10 与盘上 `s3–s10` 目录**指向不同子块**——SKEL S3=Shrinkage 链 / 叶 `s3`=overlay_signal_suppliers；SKEL S5=快照入库 / 叶 `s5`=shrinkage_risk_signals；SKEL S6=锚定态 / 叶 `s6`=snapshot_production_slot；SKEL S7=六段 / 叶 `s7`=anchored_state_track；SKEL S8=alt_regime / 叶 `s8`=six_phase_truth_chain；SKEL S9=消费面 / 叶 `s9`=alt_regime_channel；SKEL S10=验证族 / 叶 `s10`=downstream_consumer_surface。7/10 号位歧义，任何"S3 如何如何"的跨簿引用都需二次消歧。

## 2. 叶子六向与封矿主张质量（1b）

12/12 片叶子六标号（①–⑥）全在位，行长 42–68；`grep -c '封矿' 各叶` 全命中，句式＝"六向封口 → 子模块封矿"。
**三扫收敛证据：叶子 0 处**（`grep -c 三扫` 逐叶全 0）；仅 SKEL L325 有一句"**三扫收敛声明**：B1-B8 后 10 子块×六向每格均有路径行号出处或 MINING 明示"——该句把"扫过 B1–B8"当收敛证据，**但 B1–B8 是阅读批次不是三向**，且未给"第三向（HEAD 反查）无新增"的读数。**增长拉平论证：0 处**（`grep -cE '平坦|不再增长|收敛轮'` 全 0）。74 片叶子（全环节）**零命令块**：`grep -rl '```' L01_regime/*/*/MINE.md | wc -l` → 0。

**父子三态互斥（HOLE）**：SKEL L254 "**合计：10 子块=SEALED 7 / MINING 3**"（S2/S4/S10 判 MINING）↔ `_INDEX.md` L?"**合计 12 子簿：已挖干 12 / 在挖 0**"。叶层把 SKEL 的 3 个 MINING（S2→`s2`+`s3`、S4→`s4`、S10→`s11`）一律改判"已挖干"，理由是"公式级逐行对表属施工不属挖矿"（挖矿 SOP §3 口径）——**改判理由成立，但父册未回写**，两册并存即第二真源。

## 3. 引用证据复跑（1c，抽样面＝全量而非抽样）

`cited=86 ok=86 not_in_head=0 line_beyond_eof=0` → **通过率 100%**（探针见 `_VERDICT.md` §二 命令；后缀归一口径）。
定点复核 4 条（含两条被标"改判/未达"的 P0 级论断，全部**证实**）：

| 论断（出处） | 命令 | 结果 | 判定 |
|---|---|---|---|
| "六段切源已进 HEAD（commit d27e0f0df3）"（`_INDEX.md` s8 行） | `git cat-file -t d27e0f0df3`；`git log -1 --format='%h %ci %s' d27e0f0df3` | `commit`；`2026-09-25 06:35:58 feat(l02c03+l09c02): 状态轴合并批（六段+L2门+D13+核…）` | ✅ 真 |
| "six_phase_history_v1.csv 仍未落地（生成器在 HEAD、产物不在）" | `git ls-files \| grep -i six_phase` → 仅 `scripts/audit/t0_six_phase_materialize.py`＋MINE 自身；`find . -name 'six_phase_history_v1*'` → 空 | 产物确实不在 HEAD 也不在盘 | ✅ 真（自曝准确） |
| "schema 符号仍缺 → L01-C01 判据未达"（`_INDEX.md` s7 行） | `git show HEAD:schemas/categories/backtest/backtest_regime_state_anchored.py \| grep -c SQL_LATEST_ANCHORED_STATE` | 0 命中（exit 1） | ✅ 真 |
| SKEL §12 施工表全部行锚（如 `fw_backtest.py:117`、`print_regime_history.py:179-181`） | 86 条锚点全量 `git show HEAD:<path> \| wc -l` 比行数 | 全部落在文件长度内 | ✅ 无越界 |

## 4. 施工项（1d）

`L01-C01..C10` **10/10 有定义行**，表头 `\| # \| 项 \| 优先 \| 内收声明 \| 验收判据（对 17 号文纪律） \|`（`SKEL.md:260`）＝**唯一有独立验收判据列的环节**。
缺项：**无判据语 2 个**（`L01-C03`（其判据写在正文散句"窗口天数=唯一日数±0"，列位仍填）、`L01-C09`）；**无归属/门位语 4 个**（`L01-C05`、`C06`、`C08`、`C10`）。阻塞依赖列**整表缺失**（表头无"依赖/前置"列），仅 C04/C05 在正文里写了"落地前置=creation_token+模块翻译登记"。

## 5. 本环节洞清单（关它要建的那一个件）

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L01-H1 | P1 号位冲突（SKEL S3–S10 ≠ 叶 s3–s10） | §1 对照 | `_INDEX.md` 加一张"SKEL 号 ↔ 叶目录"对表 |
| L01-H2 | P1 父子三态互斥（7 SEALED+3 MINING vs 已挖干 12） | `sed -n '254p' SKEL.md` vs `_INDEX.md` 合计行 | SKEL §11 三态汇总按叶层回写（或叶层在合计行标注"父册判 MINING 的改判依据"） |
| L01-H3 | P1 封矿无三扫/无拉平（仅一句批次声明） | §2 命令 | `_INDEX.md` 增"封矿证据表"：逐叶 轮次/命令原文/新增=0 读数 |
| L01-H4 | P2 施工表无"依赖"列，4 项无归属 | §4 | SKEL §12 表头补两列（等长替换，勿加行数超预算） |
| L01-H5 | P2 CH 侧读数（"3,629=行数、1,819=唯一日、5 run"）无查询原文留痕 | 叶子无 ``` 块 | 同 H3 表的"读数通道+查询原文"字段（走 `DatabaseService`/`ch_probe`，禁 `query()` 下标直取） |
| L01-H6 | P3 frontmatter 违规 `doc_type: log` | `sed -n '9p' SKEL.md` | 就地删键 |

**总判**：L01 是九环节里**唯一可以按 HEAD 全量复跑通过的环节（86/86）**，其"已挖干"在**结构层与证据层成立**；不成立的是**封矿判据形式**（三扫/拉平/归属/依赖四缺）。
