---
ttl: task_bound
completes_when: L08 环节 SKEL/_INDEX/叶层三方对表完成且封矿主张逐条复跑
---

# L08_risk（风控与熔断）· 封矿审计细则

基准 `HEAD = 3eeb9357437997468fa1e987b61597f990c38a6b`；目录 `docs/_working/decision_map_campaign_20260924/links/L08_risk`。

## 1. 结构对表（1a）

| 口径 | 数 | 命令 |
|---|---|---|
| SKEL 声明子块 | **9**（RSK-1…RSK-9） | `grep -oE 'RSK-[0-9]+' L08_risk/SKEL.md \| sort -u \| wc -l` → 9 |
| _INDEX 声明叶 | **9** | `grep -c '^\| RSK-' L08_risk/_INDEX_MINE.md` → 9 |
| 盘上 `s*/MINE.md` | **9** | `find L08_risk -name MINE.md \| wc -l` → 9 |
| 声明未落盘 / 盘上未声明 | **0 / 0** | 差集为空；`_INDEX_MINE.md` 第二列写全 `sN_*/MINE.md` 路径，号位一一对齐 |

## 2. 叶子六向与封矿主张质量（1b）

9/9 片叶子六标号齐，行长 64–86。**本环节是全 campaign 唯一在两个层级都如实判"未封矿"的簿**：
`_INDEX_MINE.md` 三态列 **9/9 = MINING**（RSK-1 行还明写"**自 SEALED 主动降级**"），`SKEL.md:157` "**计数：9 子块｜SEALED 2｜MINING 7｜BLOCKED 0**"、`:199` "本簿 **MINING**（7/9 子块有未读指针清单）…**封矿前置=清空 §3 各子块 MINING 清单后复核**"。
⇒ 洞在**口径不齐**而非"谎称封矿"：SKEL 说 SEALED 2、_INDEX 说 9 个全 MINING（连 SKEL 判 SEALED 的两块也被 _INDEX 降为 MINING）——**同一环节两份册子对"哪两块封了"给出相反答案**，无对表。
另：8/9 片叶子正文仍写"封矿判据…→ 子模块封矿"，与 _INDEX 的 MINING 判定**第三度冲突**（唯一没写封矿的是 `s1_system_killswitch_agent_behavior/MINE.md`，它是全 campaign 74 片叶子里唯一不宣称封矿的）。
**三扫 0 处／拉平 0 处／命令块 0 处**。

## 3. 引用证据复跑（1c）

`cited=229 ok=226 not_in_head=2 line_beyond_eof=1` → **通过率 98.7%（引用面最大、通过率次高）**。三条失败：

| 引用 | 命令 | 观察 | 判定 |
|---|---|---|---|
| `schemas/categories/market/market_stock_candidate_pool.py:37`（s8 册："候选池有真源列"） | `git cat-file -e HEAD:schemas/categories/market/market_stock_candidate_pool.py`；`git -C /d/ZephyrAlpha status --porcelain --untracked-files=all \| grep market_stock_candidate_pool` | HEAD 无此路径；主区 **`??` 未跟踪** | **P0**：否决链"头（真源列）在"的论断建在未提交件上 |
| `sim_daily_runner.py:978` | `git show HEAD:scripts/backtest/sim_daily_runner.py \| wc -l` | **892** ⇒ 978 越界 86 行 | **P0**（与 L07-H1 同根：该件在任何口径都是 892 行） |
| `risk_manager_orchestrator.py:373`（裸文件名） | `git ls-files \| grep default_risk_manager_orchestrator` → `src/zephyr/risk/implementations/default_risk_manager_orchestrator.py`（HEAD **443 行**） | 真身存在、行号在范围内，但文档未给可解析路径 | **P2**（可追溯性，非假证据） |

## 4. 施工项（1d）—— 本环节是"账裂"最严重的一本

全环节 `L08-C01…L08-C60` 共 **58 个号**：`grep -rhoE '^\|[[:space:]]*\*{0,2}L08-C[0-9]{2}' L08_risk | wc -l` → **57 条定义行**，其中 **SKEL 只 11 条**（`grep -cE '^\|...L08-C[0-9]{2}' L08_risk/SKEL.md` → 11，即 C01–C11），**其余 46 条长在叶子自己的 §⑤ 表里**；`L08-C60` **只在 `_INDEX_MINE.md` 被引用 3 次、无任何定义行**（`grep -rn 'L08-C60' L08_risk`）。
SKEL 表头 `\| # \| 项 \| 内容与真源 \| 沿用账本 \| 内收声明/优先 \|`（`SKEL.md:163`）⇒ **无判据列、无归属列**；叶子侧表更薄：`s2_five_level_circuit_breaker/MINE.md:59-64` 的 C17–C22 行**只有 3 格**（号｜内容｜优先），连"沿用账本"位都没有。
探测合计：**44/58 行无判据语、47/58 行无归属语、2 行无态语（C16、C29）**。

## 5. 本环节洞清单

| # | 洞 | 证明 | 关洞件 |
|---|---|---|---|
| L08-H1 | **P0** 候选池真源列件不在 HEAD（`??`），否决链头端论断无据 | §3 | `schemas/categories/market/market_stock_candidate_pool.py` 入 HEAD 袋 |
| L08-H2 | **P0** `sim_daily_runner.py:978` 越界（HEAD 892 行） | §3 | s? 册该行锚按 HEAD 重标 |
| L08-H3 | **P1** 施工账三层分裂：SKEL 11 条／叶 46 条／`L08-C60` 无定义 | §4 三条命令 | `SKEL.md` §施工项加"总账位"：把 46 条叶号并表（或声明叶表为真源＋SKEL 只留索引行），并给 C60 补定义 |
| L08-H4 | **P1** 三态三口径互斥（SKEL 2 SEALED ／_INDEX 9 MINING ／叶 8 写封矿） | §2 | `_INDEX_MINE.md` 三态列加"依据＋与 SKEL/叶差异说明"列，一次改齐 |
| L08-H5 | **P1** 判据与归属双缺（44/47），s2 叶表仅 3 格 | §4 | 各叶 §⑤ 表补"判据/归属"两格（不加新表） |
| L08-H6 | P2 裸文件名引用（orchestrator） | §3 | 补全路径 |
| L08-H7 | P1 三扫/拉平/命令块零留痕 | §2 | `_INDEX_MINE.md` 增封矿证据表 |

**总判**：L08 的**引用面最好（98.7%）而封矿主张最诚实（两层级都判未封矿）** ⇒ 它不是"假封矿"的洞，是"**账本结构裂成三层**"的洞：真正要关的是 H-3（施工项总账位）与 H-4（三态口径唯一化）。它同时也是本 campaign 里最接近"可开工"的一环——但前提是 H-1 的代码入 HEAD。
