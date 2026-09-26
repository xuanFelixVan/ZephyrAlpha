---
ttl: task_bound
session: st-ec1-equity
---

# EC1 股权穿透接线 施工台账（st-ec1-equity）

> 役：业务链流通战役（00_orchestration.md）EC1 车道 | 工单：wo_equity_penetration_v1.md（已批准点火）
> 验收单：ACC-F-CHAINMAP-EQUITY-BADGE.yaml（rev1，冻结）| 设计真源：altdata_line/02_entity_graph_equity_person.md
> 底座：commit c007caac86（2026-09-20，scripts/entity_graph/ 三脚本 + PG depgraph 域六表）

## 0. 技术栈口径校准（工单滞后项，本车道按实际底座执行）

wo_equity_penetration_v1.md S1 写 ClickHouse DateTime64(3)+显式时区；**实际底座=PostgreSQL depgraph 域
entity_graph 六表**（DDL 真源=scripts/entity_graph/apply_entity_graph_ddl.py，PIT 双轴=valid_from/valid_to
DATE + ingested_at TIMESTAMPTZ）。接线按 PG 底座实现，此为口径校准记录，工单原文不改。

## 1. R1-R7 逐项销账

| 项 | 状态 | 要点 |
|---|---|---|
| R1 读真源 | done | 六表连接入口=`zephyr.governance.depgraph_schema.get_depgraph_pg_connection`（默认 depgraph_reader 只读角色，与 api_server._cm_pg 同入口同角色）；equity_penetration(TEXT,INT,DATE) 函数在库（routines 计 1 条，STABLE，现行版本=valid_to IS NULL） |
| R2 查询模块 | done | 新建 src/zephyr/frontend/dashboard/chainmap_equity_graph.py（只读）：resolve_entity（代码裸码/带后缀/entity_id/规范名四键变体）+ company_equity_summary（控 N/被 M 控聚合，LEFT JOIN node_company/node_person 富化）+ penetrate_upstream（PG 函数优先，sqlstate 42883 自动降级等价 WITH RECURSIVE，path 数组防环）+ penetration_paths（根→叶链重构，visited 防环+50 条帽）+ equity_domain_for_company / cluster_equity_badge_rows（ACC 契约兼容件） |
| R3 端点切换 | skipped+理由 | api_server.py 是共享热文件，git diff HEAD 实测**1079 insertions/523 deletions 非本会话外来未提交改动**（最后落库 commit=30505c93f6 st-ailayer-final-20260924；改前 lock_files 全表核查无人 claim、非 stash 遗物、作者不可归因）。按车道纪律"有改动且非你所属=只在独立模块实现+测试，端点切换登记跳过"。替代交付：模块已按 ACC 契约逐键对齐，接线补丁见 §3（api_server 空闲时 2 处小改即完成切换）；ig_equity_edge 旧路径未动（无连坐）。Owner 门位项（净删/退役 ig_equity_edge）不涉及——本次零删改 |
| R4 实弹验收 | done | 见 §2：两公司 3 跳穿透非空（pg_function 引擎）+ 20 边对源 20/20 PASS + API 契约函数实弹返回六表数据。全部只读 |
| R5 测试 | done | tests/frontend/test_chainmap_equity_graph.py：15/15 绿（mock 连接层，零真实 PG，零生产路径写入） |
| R6 登记 | done | depgraph 节点 node_id=15240370（MOD-ENTITY-GRAPH/D_FRONTEND/generated，file 粒度）；翻译条目 #7847（plain_zh 大白话）；creation_token chain_circulation 2 条（src 模块+本台账目录） |
| R7 入库 | done | 正门 git_commit.py 单袋落地；袋号/哈希见 §4 |

## 2. R4 实弹证据（2026-09-27，全部只读）

底座现状：node_entity=140,725｜edge_holding=1,500,341（现行 valid_to IS NULL=275,669）｜
node_person/node_company/edge_role/edge_link v1 空表（A 层 akshare 无 uscc，待 B/C/D 层富化——不阻断接线）。
数据源构成：akshare_top10 占 99.95%，ig_equity_edge 804 条已并入（其行 verification 标注=ig_equity_edge，provenance 诚实可见）。

### 2.1 两公司 3 跳穿透（penetrate_upstream，engine=pg_function）

| 根 | 跳分布(1/2/3跳边数) | 路径样本 |
|---|---|---|
| 600566 济川药业 | 59/127/854（共 1040 边，重构 50 链帽） | 济川药业 ← 兴业证券股份有限公司 ← 福建省财政厅（2 跳） |
| 600927 永安期货 | 34/244/67（共 345 边） | 永安期货 ← 财通证券股份有限公司 ← 浙江省金融控股有限公司（2 跳） |

### 2.2 20 条现行边对源核对（edge_holding vs CH fund_top10_shareholders=akshare 十大股东口径）

抽样=两公司被控侧按 rank 排序前 20 条；逐条按 source_ref（ch:表|symbol|report_period|股东norm）回 CH
FINAL 对 hold_ratio：**PASS=20 MISS=0**（含 2015-2026 各报告期，比例逐条吻合）。
观测注记：现行集含"最后观测即现行"历史边（如 2007-12-31 观测、valid_to=NULL）——DDL p_min_valid_from
参数即为此设；要最新快照口径传当期 report_period，模块签名已透传 min_valid_from。

### 2.3 API 契约函数实弹（端点切换延后，直接调函数=切换后同代码路径）

- equity_domain_for_company('600566')：n_held=59、source=entity_graph，
  held_by[0]={"symbol":"","name":"济川控股","stake_pct":66.13,"relation":"shareholder","verification":"akshare_top10","as_of":"2016-03-19",...}（ACC item1/3 键契约逐键兼容；person 对手方 symbol='' 靠 name 展示不可点）
- equity_domain_for_company('600927')：n_held=34，同构。
- cluster_equity_badge_rows(['CH-9e997055ba9f'])：800 行（簇级 LIMIT 生效），out=38/in=762，
  含 ig_equity_edge 并入行（verification=ig_equity_edge，name 如实为编码/HK 代码）。

## 3. R3 接线补丁（api_server.py 空闲后施用；本车道已验证函数实弹可用）

1) `_cm_equity`（约 L4321）整函数替换为一行委托：
```python
def _cm_equity(sym: str, names: dict[str, str]) -> dict[str, Any]:
    """股权域（entity_graph 六表现行版本，EC1 接线 2026-09-27；异常内部独立降级）。"""
    from zephyr.frontend.dashboard.chainmap_equity_graph import equity_domain_for_company

    conn = _cm_pg()
    try:
        return equity_domain_for_company(conn, sym)
    finally:
        try:
            conn.close()
        except Exception:
            pass
```
2) `/api/chainmap-cluster` equity 段（约 L3594 `_SQL_CM_EQ_AGG` 查询处）替换数据源：
```python
from zephyr.frontend.dashboard.chainmap_equity_graph import cluster_equity_badge_rows

eq_rows = [
    (r["node_id"], r["dir"], (r["symbol"] or ("UNLISTED:" + r["name"]) if not r["symbol"] and r["verification"] == "ig_equity_edge" else r["symbol"]) or "PERSON:" + r["name"] if not r["symbol"] else r["symbol"], r["stake_pct"], r["relation"], r["verification"], r["as_of"], r["name"])
    for r in cluster_equity_badge_rows(conn, ids)
]
```
（或保持聚合消费循环改读 dict 行形——消费字段 node_id/dir/symbol/name/stake_pct/relation/verification/as_of 已对齐，前端 js 零改动。）
3) 验收联动：ACC-F-CHAINMAP-EQUITY-BADGE execution.flow（起面板→C01 簇→徽章浮层逐条对）+
本台账 §2.3 复跑。

## 4. 落地袋

| 袋 | 内容 | qid | commit |
|---|---|---|---|
| EC1 主袋 | src/.../chainmap_equity_graph.py + tests/.../test_chainmap_equity_graph.py + 本台账 + algo_flow yaml + 两共册（token/翻译登记面，HEAD 纯追加零删行机检证明，含他会话在途条目随批披露） | 直连正门（allow-overlap+adopt 通道，无 qid） | **9fa01551f0** |

落地核账（git log -1 --name-only）：恰 6 文件零搭便车；会话无遗留 claim；队列 -0001..-0004 死信
payload 均已由 9fa01551f0 覆盖落地（q-0040 先例口径：payload 已落地=留档作废，不 requeue）。

落地波折全录（读 dead json 全文后修正非盲 requeue，q-0005 先例口径）：
1. -0001 预检三拦：SESSION 未注册（session_worktree_start 注册解决）/CREATE-GUARD+TRANSLATION 读落地
   仿真态需共册同批/--allow-non-worktree（2026-08-13 裁定通道）——修后入队。
2. -0001 死信 ORPHAN-MODULE（src 新 .py 零 import 消费者；真实根因=唯一消费者 api_server.py 接线因外来
   diff 登记跳过，与 R3 口径一致）。处方=playbook ORPHAN-MODULE 豁免面"含 __main__ guard 块"：补 _main()
   独立冒烟 CLI（python -m zephyr.frontend.dashboard.chainmap_equity_graph 600566 --depth 3，
   m11-perm-manual-legitimate 人工单次查询），实弹复跑绿。
3. -0002 死信 MUTABLE-CONST-WITHOUT-FINAL（__all__ 缺 Final）——改 `__all__: Final`，15/15 复绿。
4. -0003 死信 cascade_stale（capability/translation 两共册基底被他会话落地重置，快照失效）——收窄袋清单重排。
5. -0004 死信 GATE-PRECOMMIT-RUN/GATE-ALGO-FLOW（src 模块缺 ALGO_FLOW 锚）——drafter 产出校准后落
   algo_flow/chainmap_equity_graph.yaml（token 已登记）+docstring 单行锚（§4.16 P2-1）；ruff check/format
   全净（BLE001×3 契约性独立降级附理由豁免）；15/15 复绿。
6. 附带修复（共册治伤非本车道职责但挡路）：capability 册曾被陈旧整文件快照压盘，盘上较 HEAD 缺 16 条
   metaq token——按工具 fail-safe 指引"只把缺的这几条增量补回盘上基底"（safe_write CAS，append-only，
   11588→11604），随后 token 登记恢复可用。禁整片 checkout 覆盖的 B23 训条已遵守。

## 5. 遗留与移交

1. api_server.py 端点切换（§3 补丁）：待热文件外来未提交改动（1079 行）归属澄清/落地后施用——移交总筹或 fms 基建线。
2. ig_equity_edge 退役/净删：Owner 门位，本次不涉及（登记 99_skipped_for_owner.md 不需要——未做任何删改）。
3. 数据面（后续车道原料）：node_company/node_person 空（uscc 富化 P1①消歧桥）；股东名变体未合并
   （济川控股 vs 江苏济川控股集团有限公司 双实体并存，设计 §7 消歧坑在案）；现行集含历史最后观测边。
4. 前端 verification 中译映射：新 source 系（akshare_top10/ig_equity_edge）进浮层"核验状态"中译表，
   接线时顺带（chainmap-cluster.js showEqOverlay 映射）。
