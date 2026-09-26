---
ttl: task_bound
completes_when: L03 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L03_sector（板块状态与轮动）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L03_sector`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **8**（B1–B8） | `grep -cE '[├└]─ B[0-9]' L03_sector/SKEL.md` → 8 |
| _INDEX 声明叶 | **8** | `grep -c '^| \`b' L03_sector/_INDEX.md` → 8 |
| 盘上 `b*/MINE.md` | **8** | `find L03_sector -name MINE.md \| wc -l` → 8 |
| 声明未落盘 / 盘上未声明 | **0 / 0** | 差集为空 |

**号位一致**：L03 是九环节里唯一 SKEL 字母与叶目录**一一对齐**（B1↔`b1_index_data_foundation` … B8↔`b8_p1_conditional_tables`）的环节 ⇒ 无消歧洞。

## 2. 叶子六向与封矿主张质量（1b）

8/8 片叶子六标号齐；**行长 23–36（全 campaign 最短批次）**；标签同样为简写形（① 一句话／② 实测／③ 六向／④ 缺口／⑤ 三态裁定／⑥ 日志），与 `_INDEX.md` 承诺的六段名不符。
**三扫 0 处／拉平 0 处／命令块 0 处**：`grep -c 三扫 L03_sector/*/*/MINE.md` 全 0；`grep -rl '```' L03_sector/*/*/MINE.md | wc -l` → 0。封矿句式统一为"六向封口 → 子类目封矿"，未给扫矿轮次收敛读数，也未给"新增趋零"论证。
**关键：`b2_state_aggregation_kernel/MINE.md` 把表侧读数（`c1_market.sector_state` 426,985 行 / 986 唯一日 / rrg 空串 20,401 / 881 族仅 1 日）当封矿核心证据，但查询原文一字未留**——按 HEAD 口径本道无法复跑（且宪法 §9.1 禁本道裸查库）。这是"封矿=散文声明"的典型面。
父子三态：`SKEL.md:7` `status: SEALED（6/8 子块封矿；B4/B5 MINING 见 §9；…）` ↔ `_INDEX.md` "**合计 8 簿：已挖干 8 / 在挖 0**" ⇒ **互斥**（SKEL 点名的 B4/B5 两个 MINING 在叶层被并成"已挖干"，无改判依据留痕）。

## 3. 引用证据复跑（1c）

`cited=15 ok=15 not_in_head=0 line_beyond_eof=0` → **通过率 100%**。
`b2` 册的行号锚全部落位：`git show HEAD:src/zephyr/signal_ashare/sector/sector_state_aggregator.py | wc -l` ≥ 其引用的 :452/:473/:497-516（探针覆盖）。文档里 `data/sector_state_pipeline.py` 系 `src/zephyr/` 前缀被代码跨度切断的写法，后缀归一后命中真身（**若不归一会误报 1 个洞**）。

## 4. 施工项（1d）

`L03-C01..C10` **10/10 有定义行**；表头 `\| # \| 项 \| 内容与替代声明 \| 既有账本 \|`（`SKEL.md:243`）⇒ **既无"优先/态"列，也无"验收判据"列，也无归属列**——是九环节里施工契约最薄的一本。探测：**9/10 行无状态语、9/10 行无判据语、7/10 行无归属语**（唯一例外 C02/C03 在正文含"Owner 已批/预注册新卡"字样，属正文非列位）。
`grep -n '^| # | 项 | 内容与替代声明' L03_sector/SKEL.md` 复跑取表头。

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L03-H1 | **P1** 表侧 CH 读数为封矿主证却零查询原文（b2/b5 尤重） | §2；`grep -rlE 'CH 实查\|CH 探针\|表侧实测' L03_sector/*/*/MINE.md` | `_INDEX.md` 增"读数通道+查询原文"列（走 `DatabaseService`/`ch_probe`） |
| L03-H2 | **P1** 施工表三列皆缺（态/判据/归属） | §4 表头原文 | SKEL §施工项表头改造为 L06 形状（`\| # \| 项 \| 内容+判据 \| 净零对价 \| 前置/门位 \| 优先 \|`） |
| L03-H3 | P1 父子三态互斥（6/8 vs 8/8） | §2 | SKEL `status` 行按叶层回写并注明改判依据 |
| L03-H4 | P1 封矿无三扫/无拉平 | §2 命令 | `_INDEX.md` 增"封矿证据表" |
| L03-H5 | P2 六向段名与 _INDEX 承诺名不符；叶均长 25 行（最薄） | §2 | `_INDEX.md` 读法行改标号口径；薄叶按 H-01 补读数原文自然增厚 |
| L03-H6 | P3 frontmatter `doc_type: log` 违规 | `sed -n '1,10p' L03_sector/b2_state_aggregation_kernel/MINE.md` | 就地删键 |

**总判**：结构齐（8/8/0/0）、HEAD 证据 **100% 可复跑**（本环节是引用面最干净的两个环节之一）；但**封矿判据与施工契约双缺**，其"已挖干 8"在"证据可复核"这一维成立、在"判据可复现"这一维不成立。
