---
ttl: task_bound
session: st-nightsweep2-nc-20260930
created: '2026-09-30'
status: FROZEN_BY_OWNER_REF
ruling: 裁定#447
---

# W-178 板块宇宙真源声明（FROZEN_BY_OWNER_REF）+ 两口径映射表立项 + known 差异清单

> **授权链**：总筹 st-nightsweep-chief-20260929 第二夜 C 组派发裁定（tqcenter sector_constituent 595 为选股
> 真源、akshare concept_board 375 辅助展示）+ 裁定#431⑥（Owner 2026-09-30：行业成分股真源=880+881 两段
> 行业板块序列，概念板块 375 为独立一族不混入行业口径，零重合已复测）。两裁定**同向互补**：
> #431⑥ 定行业族=真源族、概念族=独立族；本声明在其框架内定**真源表**与**读法分工**。
> **冻结语义**：本声明冻结的是"选股读哪张表"的定向；数据本身的客观缺口（§3 known 差异清单）不因冻结消失，
> 仍按各自处方推进。

## 1. 真源定向（冻结面）

| 用途 | 真源 | 来源/表 | 规模（2026-09-26 strict 实测，双通道一致） |
|---|---|---|---|
| **选股宇宙（成分归属判定）** | **tqcenter 行业成分** | `c1_market.sector_constituent`（880 段 467 + 881 段 128 = **595 板块**） | 成分 95,124 行；行业族股票池 6,179 |
| 辅助展示（概念维度/主题标签） | akshare 概念板 | `c1_market.concept_board` / `concept_board_constituent`（**375 板块**） | 成分 32,659 行；概念族股票池 4,865 |
| 行情序列（板块 K 线） | tdx 板块日线 | `c1_market.kline_sector_880`（880 段 601 + 881 段 128 = 729） | 761,018 行 |
| 板块名册 | 名称映射 | `c1_market.sector_code_name_map`（729 行，880 段 601 全可解析） | 名册真源 |

**读法铁律**：选股/成分归属/宇宙统计一律读 `sector_constituent`（行业族）；`concept_board` 族只作展示层
与主题标签，**禁混入行业口径、禁作选股宇宙分母**（裁定#431⑥"独立一族不混入"原文执行）。

## 2. 两口径映射表立项（本件立项，表体另波施工）

- **命名空间事实**：行业族板块码 `880xxx.SH/881xxx.SH`（tqcenter）与概念族 `300xxx`（akshare）**零交叠**
  （code_overlap=0、name_overlap=0，w178_universe_facts.yaml derived.sc880_vs_concept_board 实测）⇒
  **任何映射只能按成分股集合对齐，禁按板块码/板块名对齐**。
- **立项物**：`board_pair_mapping`（行业板×概念板，按成员 Jaccard/重叠度对齐的股票级映射表）+
  **去重律声明**：同一股票跨族多归属时，选股口径按行业族归属计（概念归属只作标签并集，不重复计数）。
  两族股票池交叠 4,864 / 行业独有 1,315 / 概念独有 1（实测），映射表须覆盖三类处置。
- **施工位**：待映射表落地后另登记（消费面=展示层聚合与条件分层的"主题"辅助轴，不进考试判据分母）。

## 3. known 差异清单（冻结不消失的客观缺口，逐条带处方）

| # | 差异 | 实测值 | 处方/状态 |
|---|---|---|---|
| K1 | **134 板有行情无成分**（880 段缺口：8803=61、8804=71、8808=2） | gap_880_no_constituent=134（快照表并集后仍 134，快照通道零增量） | 补齐需新增采集腿（波 3 排）；名单真源=sector_code_bridge.py::TDX_INDUSTRY_BOARDS；缺口板禁入成分类判据分母 |
| K2 | **成分表业务滞后**：880 段 max(update_date)=2026-09-03（93 册披露"滞后 21 天"，选股宇宙唯一读取源） | sc_880_fresh | 波 3 追采集腿（93 册披露 #3③ 在册）；PIT 判据面在补齐前按 INDETERM 处理（fail-closed） |
| K3 | **PIT 深度不足**：sector_constituent_snapshot 仅 6 个快照日（2026-09-14 起）+ valid_to 全 NULL | scsnap_fresh | 波 12 PIT 回溯不依赖本表；深度扩充随采集腿 |
| K4 | **两族股票池规模差**：行业 6,179 vs 概念 4,865 vs 全池 sector_list 5,217（差 963 为算术差） | universe_axis_candidates | 集合差补测前置=2c/2b 逐码差（strict 案卷 §E 未决项保留）；映射表立项覆盖三类处置（§2） |
| K5 | **880 段 96 板无名/空名**（sector_constituent.sector_name 空），名册可解析面=sector_code_name_map 601/601 | name_resolution_880 | 展示层一律经 name_map 解析（禁直读成分表 name 列） |
| K6 | 概念族独有股票 1 只（only_in_concept_stocks=1） | derived | 映射表去重律覆盖；不构成行业族缺口 |

## 4. 冻结动作与回滚

- `w178_sector_universe_strict.md` §E 头标注 DRAFT_NOT_FROZEN → **FROZEN_BY_OWNER_REF**（冻结注记追加，
  实测数值零改动——数值仍是 2026-09-26 strict 事实面，引用须带 measured_at）。
- 本声明+裁定#447 同 commit 原子（原登#437撞号改号核订）（RULE-RULING）；回滚=revert 本 commit（裁定 superseded 通道）。
- 消费方变更面（factory G_universe 仍走 index_constituent，见 strict §E 轴 2a）不受本冻结影响——
  本冻结只定"板块口径"真源，G_universe 三池切换是另一议题（strict §E 轴 2 未决项保留）。
