---
ttl: task_bound
completes_when: L09 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L09_review（日循环复盘与出版）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L09_review`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **7**（S9-1…S9-7） | `grep -oE 'S9-[0-9]+' L09_review/SKEL.md \| sort -u \| wc -l` → 7 |
| _INDEX 声明叶 | **7** | `grep -c '^\| S9-' L09_review/_INDEX_MINE.md` → 7 |
| 盘上 `s*/MINE.md` | **7** | `find L09_review -name MINE.md \| wc -l` → 7 |
| 声明未落盘 / 盘上未声明 | **0 / 0** | 差集为空（`_INDEX_MINE.md` 给了目录路径列，含 `s2_premarket_chain/` → "实为 `s2_premarket_chain`"的斜杠注记） |

## 2. 叶子六向与封矿主张质量（1b）

7/7 片叶子六标号齐，行长 **82–129（全 campaign 最厚的一批）**；`_INDEX_MINE.md` 三态列 7/7 写"**封矿**（附 L09-Cxx 待裁口／随裁定／选型层封）"，并另立"§对 SKEL 的实测勘误 7 处"表（逐处给"SKEL 原述 ↔ 本批实测 ↔ 出处册"）——**这是九环节里唯一成体系的父册勘误面**。
**但父册自己没判封矿**：`SKEL.md:197` "> 封矿条件：§三 未挖清单 5 件读完＋L09-C01 Owner 裁定回来补录结果 → **转 SEALED**" ⇒ 叶层 7/7 宣称"封矿"、父层声明"两个前置未清"，**父子互斥**（P1）。
`SKEL.md:180` 另有检索状态声明（"5.3 post-trade 开源生态…非封矿阻塞项"）——即父册承认仍有未闭合的外部对表面。
**三扫 0 处／拉平 0 处／命令块 0 处**：7 片厚叶子写满了"实测"，却没写**一条可复跑命令**（`grep -rl '```' */*/MINE.md \| wc -l` → 0）。本环节尤其吃这个亏：它的核心证据是 **CH/账本读数**（`attribution_results` 0 行、`prediction_log` 35 行分布、`decision_daily` 72 行/66 单次批量、`intraday 20/20`、`brier_score 1/4`、`plan_quality_score 6/14`、schtasks 50 项状态）——**读数全部无查询原文与取数时刻**，事后无法复算（P1，H-03）。

## 3. 引用证据复跑（1c）

`cited=50 ok=50 not_in_head=0 line_beyond_eof=0` → **通过率 100%（与 L01/L03/L04 并列满分）**。
文件面抽验（本道实跑）：
- `git cat-file -e HEAD:scripts/governance/decision_chain_sentinel.py` → **OK**；`git cat-file -e HEAD:scripts/register_decision_chain_sentinel_task.ps1` → **OK**（注：注册器在 `scripts/` 根、**不在** `scripts/governance/`——本道第一版误按 governance 目录试，`fatal: path ... does not exist in 'HEAD'`，文档自身写法是对的）；`git ls-files \| grep decision_chain_sentinel` → 3 件（含 `tests/governance/test_decision_chain_sentinel.py`）。⇒ `_INDEX_MINE.md:38` 勘误第 1 行"SKEL 原述 TRD-A01/L09-C04 未落地 ↔ 实测已落地并在产"**在文件层成立**（schtasks 活态读数属运行态，本道不查，列 `assumed`）。
- 50 条 `path:line` 锚全部命中且行号在 HEAD 文件长度内（含 `pipeline_events.py:1026-1117`、`schedule.yaml:249-253`、`daily_loop_master_switch.py:337-368`）。

## 4. 施工项（1d）

`L09-C01…C09` **9/9 有定义行（全在 SKEL**：`grep -cE '^\|[[:space:]]*\*{0,2}L09-C[0-9]{2}' L09_review/SKEL.md` → 9），无孤儿号。
表头 `\| # \| 施工项 \| 对应子块 \| 沿用账本 \| 类型 \| 前置/门位 \|`（`SKEL.md:147`）⇒ **无验收判据列**：探测 **7/9 行无判据语、7/9 无归属语、1 行无态语（C09）**。有"类型"与"前置/门位"两列是本簿优点（C01 的 Owner 裁定门位显式在册）。

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L09-H1 | **P1** 叶 7/7 称"封矿"、父册 §封矿条件明写两前置未清 | §2 两处行号 | `_INDEX_MINE.md` 三态列改"封矿（父册前置：§三 5 件＋C01 裁定）"，或 SKEL 按叶层回写 |
| L09-H2 | **P1** 施工表无判据列（7/9 无判据语）＋无归属（7/9） | §4 | SKEL §施工表补"验收判据""归属"两列 |
| L09-H3 | **P1** 核心证据全是运行态/库内读数，零查询原文零取数时刻 | §2 | `_INDEX_MINE.md` 增"读数台账"列（通道＝`DatabaseService`/`ch_probe`，禁 `query()` 下标直取；schtasks 类须带取数时刻） |
| L09-H4 | P1 三扫/拉平零留痕 | §2 | 同 H-3 表加轮次与命令原文 |
| L09-H5 | P2 目录注记歧义（`s2_premarket_chain/` "实为 s2_premarket_chain（见下注）"） | `grep -n '实为' L09_review/_INDEX_MINE.md` | 注记归位到表列，去散文 |

**总判**：L09 的**结构（7/7/0/0）与 HEAD 文件面证据（50/50）双满分，勘误机制还是全 campaign 样板**；洞集中在**判据形式**（封矿口径父子不一致）与**读数复现**（库/盘态无原文）。它不需要重挖，需要**补一张"读数+命令+时刻"台账**。
