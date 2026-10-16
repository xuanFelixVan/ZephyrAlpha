---
ttl: permanent  # st-docconsol-20261014 改：原 task_bound 随 _working 搬迁落 _archive permanent zone 按 DCR-003 转 permanent（正文字节零改动）
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·股权穿透域
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 从仓内股权底座（edge_holding 150 万行＋质押双载体）装配三信号族——同实控人联动/牛散跨票/质押链传导，供龙虎榜席位归并与卖出域负面否决消费
  output_contract: equity_link_signal 三信号族事件流（表名走 TableRegistry 派生，P2 定形）；验收=关联事件命中率＋消融考卡 TDM-E-L9-G3__ablation__02 lift≥0.05
  exam_ref: 事件研究协议与传导链域（10_chain_workbook §5.5）同批预注册；消融 with_penetration/random_pairs/top10_only，keep_if_lift≥0.05
  campaign_ref: st-infoaxis-20261013（裁定#516）
---

# 股权穿透域作业簿（11_equity_workbook.md）

## §1 问题定义（它出什么）

股权关系底座（持股/实控/质押/牛散席位）产出**三类关联信号**：
1. **同实控人/一致行动人联动**：人物利空→名下公司、同实控人多票联动（词表 concert_party/actual_control 已设计未落数）；
2. **牛散跨票**：高频自然人跨票持仓同动——注意外部实证：粗粒度"跟单"无 alpha，alpha 在席位/实体画像＋协同网络识别层（§3）；
3. **质押冻结链传导**：大股东质押率/司法冻结→崩盘风险，恒负向。

供：①龙虎榜 L3-12-2 席位↔实体归并（feed 边已挂 quarterly）；②卖出域 X-S1 委托（负面/禁买池）；
③传导链域标的扩展（10_chain_workbook 互引）。
信号清单九项真源=docs/_working/altdata_line/02_entity_graph_equity_person.md §5:59-61（牛散跨票/
龙虎榜席位背后公司/同实控人联动/质押冻结链传导/定增利益链/人物利空→名下公司/核心技术人员
流动/一致行动人网络重建/二代接班）——P2 首批只装配三信号族，其余六项按底座成熟度滚动。

## §2 输出契约 v0

```
equity_link_signal 信号族流（表名走 TableRegistry 派生，P2 定形）：
  signal_family ∈ {same_controller, nium_san_cross, pledge_chain}
  subject(person|company entity_id), trigger_ts,
  targets[(code, relation, path_hops, evidence_edge_ids)],
  pit_anchor(edge_holding valid_from/valid_to 快照位), freeze_batch_id
方向语义：
  same_controller / nium_san_cross = 联动方向由触发事件极性决定（人物利空→名下公司 -1）
  pledge_chain = 恒负向（质押→崩盘风险先验，hanspub 35558 实证）
强度先验：stake_pct × path 衰减；验收不做绝对强度，先考 lift（消融考卡）
```

## §3 外部对标（2026-10-13 车道回报，URL 在案）

| 来源 | 可借鉴点 |
|---|---|
| Riyanto/Toolsema/Zhang 2008 (JFE, S0378426608000381) | 金字塔持股 tunneling/propping＋两权分离度定价因子——分离度因子化直接可借 |
| A股大股东质押→崩盘风险实证（hanspub 35558） | 质押链信号的事件研究判据范本 |
| 牛散跟单实证（知乎 zhuanlan 561750991） | 粗粒度龙虎榜跟单 alpha 基本不存在——警示：本域价值不在"跟单"层 |
| 席位/实体画像＋协同网络（wallstreetcn 3643764） | alpha 在席位/实体画像＋协同网络识别层——牛散跨票信号的正确定位 |
| 天眼查/启信宝（kdniao 横评） | 疑似实控人/股权穿透 API 按量 0.15 元起；启信宝便宜 T+2——留采购替换接口（花钱门只报价） |
| zzp1012/neo4j-enterprise-KG | 亿级企业图谱穿透算法形态对照 |
| lemonhu/stock-knowledge-graph | 股票知识图谱 schema 对照 |

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面
- 六表 DDL 真源=scripts/entity_graph/apply_entity_graph_ddl.py:54-223：node_entity/node_person/
  node_company/edge_holding/edge_role/edge_link＋穿透函数 equity_penetration(TEXT,INT,DATE)@177-223
  （递归向上 path 防环）。
- 实查（2026-10-13）：edge_holding 1,500,341 行=akshare_top10 1,499,537＋ig_equity_edge 804；
  role 仅 shareholder/invests_in/shareholding 三值；现行对 valid_to IS NULL=275,669；
  node_entity=140,725；**edge_role/edge_link=0 空**。
- ig_equity_edge 表已不存在（#424 墓碑=ruling_registry.yaml:3389-3403＋trading_decision_map.yaml:5836，
  备份 F:/zephyr_cold/retired_tables/ig_equity_edge_20260929/）——804 条已并入 edge_holding。
- source_ref 全链可回溯（ch:c3_fundamental.top10_shareholders|...）。

### 4.2 模块面
- equity_penetration.py CLI 三步 merge-ig/compare/penetrate（:20-34）production——但 merge/compare
  源表已退役，**仅 --penetrate 有效**；输出 .runtime/entity_graph/ig_equity_compare_report.json＋
  penetration_samples.json(48,341)。
- 信号清单真源=docs/_working/altdata_line/02_entity_graph_equity_person.md §5:59-61 九项（§1 已列）。

### 4.3 接线面
- TDM-E-L9-G3 module_ref=equity_penetration.py＋MOD-ENTITY-GRAPH，strategy_mounts=[]（yaml:5844）、
  factor/data/algo_refs 全空；feed 边 G3→TDM-E-L3-12-2 席位↔实体归并（6430 quarterly）。
- 消费者全集：l9_readiness(171-185)、frontend chainmap_equity_graph（api_server.py:3622/4480 已实接
  徽章＋公司卡）、entity_graph_uscc_bridge.py:25、depgraph_write_path_gate、wo009 三脚本；
  **src/zephyr 信号/因子侧零引用**。
- 消融考卡已立 TDM-E-L9-G3__ablation__02_股权穿透关联收益.yaml（with_penetration/random_pairs/
  top10_only，keep_if_lift≥0.05）。

### 4.4 词表面
- role 词表仅注释级（ddl:126-128：shareholder/invests_in/subsidiary/actual_control/gp/lp/
  concert_party——后四值库里未出现）；link_type@ddl:167（same_phone/same_email/same_address/
  co_director/co_holder/same_school/former_employer，随 edge_link 一同空置）。
- pledge/judicial_frozen 排除出持股边（equity_penetration.py:51，设计边界在案）。
- 质押两载体：CH c3_fundamental.equity_pledge_detail（schemas :38-52）＋PG
  metaq_pledge.pledge_event_version 实查 112,822 行已回填（WO-009 双时态）＋
  v_holder_edge_version_timeline。
- 牛散/实控人无任何枚举实体（无词典/无标注表）。

## §5 六向台账（后两向）

### 5.5 判据面
- 事件研究协议与传导链域同批预注册（10_chain_workbook §5.5：CAR 窗看数前冻结＋多重比较校正）；
  股权域事件日=关联事件触发日（人物利空/质押爆仓/冻结公告）。
- PIT：edge_holding valid_from/valid_to 双时态——现行对 valid_to IS NULL=275,669 即当前快照；
  质押走 WO-009 双时态（pledge_event_version）。
- 验收主判据=消融考卡：with_penetration vs random_pairs vs top10_only，keep_if_lift≥0.05；
  辅判据=关联事件命中率（信号后方向命中）。

### 5.6 消费面
- 龙虎榜 L3-12-2 席位↔实体归并（feed 边已挂，quarterly 刷新）——席位画像层消费。
- 卖出域 X-S1 委托：pledge_chain 恒负向进禁买/否决候选；人物利空→名下公司联动进负面清单。
- 现行只读消费：l9_readiness(171-185)、frontend chainmap_equity_graph（徽章＋公司卡）——P2 增量
  是信号侧消费（strategy_mounts=[] → 装配后挂 selection）。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| D1 | edge_role/edge_link=0 空——同实控人/一致行动人信号（actual_control/gp/lp/concert_party）无数据底座 | 阻断级 | P2 治本：从 top10_shareholders 文本实控链推断补 role（待裁 C3） |
| D2 | role 词表注释级七值 vs 实库仅三值——4 值未落，实控人识别无词表支撑 | 阻断级 | P2：role 判定件＋词表固化（DDL 注释→枚举真源） |
| D3 | equity_penetration.py merge/compare 两步源表已退役（ig_equity_edge #424 墓碑），仅 --penetrate 有效——CLI 名存实虚 | 缺口级 | P2：删两步或改造为 edge_holding 自比对；墓碑不复活 |
| D4 | 牛散/实控人无任何枚举实体（无词典/无标注） | 缺口级 | 冷启动=免费先行：edge_holding 高频自然人挖掘（待裁 C2） |
| D5 | 策略面零消费：strategy_mounts=[]（yaml:5844）、src/zephyr 信号/因子侧零引用——模块挂了，策略没挂 | 缺口级 | P2：三信号族装配后挂 selection/卖出域 |
| D6 | 质押双载体未统一消费口（CH equity_pledge_detail schemas:38-52 vs PG metaq_pledge 112,822 行双时态） | 缺口级 | P2：统一质押信号视图（待裁 C4 定主载体） |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| C1 | 天眼查/启信宝实控人穿透 API 采购（0.15 元起按量） | 只调研报价呈批 | 不采（花钱门=Owner；Q10 精神先吃仓内） |
| C2 | 牛散词典冷启动路径 | A=edge_holding 高频自然人挖掘（免费先行）；B=外部牛散名录采购 | A；B 只报价并入 C1 采购面 |
| C3 | 同实控人信号底座补源方式 | A=top10_shareholders 文本实控链推断；B=外部穿透 API | A（仓内先行）；B 留 C1 |
| C4 | 质押信号主载体 | A=PG metaq_pledge（112,822 行双时态已回填）；B=CH equity_pledge_detail | A（数据更全）；CH 作对账面 |

## §8 车道回报存档

- 仓内四层＋外部对标：战役协调车道下发（2026-10-13，全带 :行号 锚点）；本起草车道抽验
  apply_entity_graph_ddl.py:54/equity_penetration.py:20、:51 实核一致。

## §9 自审闸三态裁定（初判）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 病灶 6 条全部定级＋处置走向
- [x] 待裁 4 项进 P1 总表候选（C1 花钱门只报价）
- [x] 与传导链域 10_chain_workbook 互引（判据面事件研究同批预注册，§1/§5.5）
- 状态：**初判过闸·封矿候选**（终判留战役总闸；CAR 窗宽等判据数值留 P2 看数前冻结呈批）
