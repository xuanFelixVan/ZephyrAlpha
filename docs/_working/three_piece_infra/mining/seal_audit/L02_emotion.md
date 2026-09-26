---
ttl: task_bound
completes_when: L02 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L02_emotion（大盘情绪链路）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L02_emotion`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **9**（A–I；C 再拆 C1–C6 ⇒ 13 子类目） | `sed -n '25,33p' L02_emotion/SKEL.md`（`├─ A … └─ I 消费面`） |
| _INDEX 声明叶 | **12** | `grep -c '^| \`' L02_emotion/_INDEX.md` → 12 |
| 盘上 `*/MINE.md` | **12** | `find L02_emotion -name MINE.md \| wc -l` → 12 |
| 声明未落盘 | **0** ｜ 盘上未声明 | **0**（相对 _INDEX） | 同上取差集为空 |
| 相对 SKEL 全树的无位叶 | **1** | `g_tomorrow_emotion_forecast`（"明日情绪预测"族）在 SKEL A–I 树中无节点；`_INDEX` 合计行写"覆盖 13 个子类目"也未列预测族 |

**号位冲突（同 L01 型，更重）**：SKEL 的字母与叶目录字母**语义不同**——SKEL `D`=新闻情绪窗、`E`=两融温度、`F`=竞价情绪、`G`=评级情绪候选、`H`=存量同域簇、`I`=消费面；而叶目录 `d_e_auction_and_rating_candidates` 的 title 自述"D=竞价阶段情绪…E=研报评级情绪"（=SKEL 的 F+G），`f_legacy_emotion_cluster`=SKEL 的 H，`g_tomorrow_emotion_forecast`=SKEL 无位，`h_consumption_surface`=SKEL 的 I。SKEL 的 D/E（新闻/两融）实际落在 `c6_news_sentiment`/`c5_leverage_margin`。**6 个字母号位歧义，无对表**。

## 2. 叶子六向与封矿主张质量（1b）

12/12 片叶子六标号齐；行长 23–43（全环节最短的一族，见下表）。**标签漂移**：L02 叶把六段写成"① 一句话／② 实测／③ 六向／④ 缺口／⑤ 三态裁定／⑥ 日志"，而 `_INDEX.md` 承诺的段名是"①职责 ②现状实测 ③六向台账 ④缺口清单 ⑤自审闸三态 ⑥挖矿日志"——按 `_INDEX` 字面名做机械清点会得到 0/6（本道第一轮即误判 20 片叶子"缺六向"，第二轮按标号口径校正）。
**三扫：0 处｜拉平论证：0 处｜命令块：0 处**（`grep -c 三扫` 逐叶 0；`grep -rl '```' L02_emotion/*/*/MINE.md | wc -l` → 0）。封矿句式全为"六向封口 → 子类目封矿"。
父子三态：SKEL L151 "**总判：MINING（6 SEALED / 3 MINING / 0 BLOCKED）**，MINING 余量共 6 条（D 块 2+F 块 1+H 块 3）" ↔ `_INDEX.md` "**合计 12 簿：已挖干 12 / 在挖 0**" ⇒ **互斥**（且 SKEL 余量点名的 D/F/H 三块在叶层已改挂到 c5/c6/f/g/h 目录名下，无人对表）。

| 叶 | 行 | 叶 | 行 | 叶 | 行 |
|---|---|---|---|---|---|
| a_builder_kernel | 43 | c3_breadth | 33 | c6_news_sentiment | 32 |
| b_history_replay_line | 41 | c4_volume_energy | 31 | d_e_auction_and_rating_candidates | 32 |
| c1_limitup_temperature | 33 | c5_leverage_margin | 32 | f/g/h（三片） | 23 |

## 3. 引用证据复跑（1c）

`cited=31 ok=27 not_in_head=4 line_beyond_eof=0` → **通过率 87.1%**。
失败面（2 个唯一目标，均在 `SKEL.md`）：

| 引用 | 命令 | 观察 | 判定 |
|---|---|---|---|
| `config/data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml:138`（SKEL.md，标 ✅ 面） | `git cat-file -e HEAD:config/data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml` | `fatal: path ... does not exist` | **P0 双重错**：路径前缀 `config/data/` 在本仓不存在（真身是 `data/strategy_intake/…`），且真身在主区是 `??` 未跟踪 → `git status --porcelain --untracked-files=all \| grep t0_condition_matrix_v1` = `?? data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml`。HEAD 视角零证据 |
| `t0_condition_matrix_v1.meta.yaml:29`（同上裸名第二次引用） | 同上 | 同上 | 同一 P0（可追溯性另计 P2） |

## 4. 施工项（1d）

`L02-C01..C11` **11/11 有定义行**；表头 `\| # \| 优先 \| 内容 \| 内收声明（替代/合并对象） \| 依赖 \|`（`SKEL.md:155`）⇒ **有优先、有依赖，但没有"验收判据"列**：探测结果 **10/11 行无判据语**（仅 C05 正文自带"红测"字样），**7/11 无归属/门位语**（C02,C03,C04,C06,C07,C09,C10）。
`grep -rn '^| \*\*L02-C' L02_emotion/SKEL.md \| wc -l` 可复跑取行数。
（注：`L02-C1..C6` 是**子块号**出现在叶 title 里，不是施工项号；机械 `\d+` 匹配会造出 6 个假孤儿，本道已用两位号限定剔除。）

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L02-H1 | P0 `t0_condition_matrix_v1.meta.yaml` 引用**既走错前缀又不在 HEAD**，而它被当"✅ 已挖干"的证据面 | §3 两条命令 | 该 meta 件入 HEAD 袋 + SKEL 两处路径改真身 |
| L02-H2 | P1 字母号位 SKEL↔叶 6 处语义冲突 + 预测族叶无 SKEL 位 | §1 | `_INDEX.md` 增"SKEL 字母 ↔ 叶目录"对表；SKEL §1 补预测族一行 |
| L02-H3 | P1 父子三态互斥（6/3 vs 已挖干 12） | §2 | SKEL §三态汇总按叶层回写 |
| L02-H4 | P1 施工表无验收判据列（10/11 无判据） | §4 表头原文 | SKEL §施工项表头补"验收判据"列（等长替换） |
| L02-H5 | P1 封矿无三扫/无拉平/零命令块；12 片叶子是九环节里最短的一批（23–43 行） | §2 | `_INDEX.md` 增"封矿证据表"（逐叶轮次+命令+新增=0 读数） |
| L02-H6 | P2 六向段名与 _INDEX 承诺名不符（标签漂移） | §2 | `_INDEX.md` 读法行统一改标号口径，或叶子补全名 |

**总判**：结构齐（12/12/0/0），证据面 87%，**封矿判据不可复现**且**存在一条被当证据的 HEAD 外文件** ⇒ L02 的"已挖干 12"不能按 HEAD 采信，需补 H-01 入 HEAD 后复扫。
