---
ttl: task_bound
session: st-infoaxis-20261013
date: 2026-10-13
title: 信息供给轴 P0 作业簿·传导链域（首件校准）
status: mining_sealed_pending_gate
goal_block:
  goal_statement: 事件发生后算出"谁受益、多强、多久"——产出可被事件研究验证的受益标的集＋方向＋强度＋时滞四元组
  output_contract: chain_event_impact 事件流：每事件→[(标的, direction∈{+1,-1,0}, strength∈[0,1], lag_days 预估窗)]＋ PIT 滞后面登记
  exam_ref: 事件研究协议（信号后 N 日超额＋方向命中＋无链对照组差分＋多重比较校正；与 condaxis P2 口径同批对齐）
  campaign_ref: st-infoaxis-20261013（裁定#516 Q3；condaxis S4/S5 双锚）
---

# 传导链域作业簿（10_chain_workbook.md）

## §1 问题定义（它出什么）

事件（涨价/断供/扩产/制裁/技术突破…）沿产业链上下游传导，输出**受益标的集＋方向＋强度＋
时滞四元组**，供：①板块催化定位（L2-09 催化剂识别消费）；②条件轴拐点确认器（信息事件
标注不占 18 格，X2-B 先例）；③负面否决器（受损方向）。

## §2 输出契约 v0

```
chain_event_impact 事件流（表名走 TableRegistry 派生，P2 定形）：
  event_id, event_ts, event_type, subject_node(ig_node), direction_signed,
  targets[(code, direction, strength, lag_days_band, path_hops, evidence_edge_ids)],
  pit_lag 注册（源可见时点→落库时点），freeze_batch_id
方向语义：direction = polarity × chain_role_sign(event_type, 上下游角色)
  ——涨价:上游供方+1/下游需方-1；断供:替代品供方+1/原需方-1；扩产:设备/原料需方+1…
强度先验：IO 直接消耗系数（G5 治本后）× hop 衰减；时滞：先验带（1-5 日上游/5-20 日下游），
  后由事件研究标定（禁止看数前定数值）
```

## §3 外部对标（2026-10-13 全网搜，详见班账 §8 车道回报）

| 来源 | 可借鉴点 |
|---|---|
| Cohen-Frazzini 2008 (JF) | 客户-供应商映射＋CAR 事件研究＋无链对照组差分——本役验收协议直接沿用 |
| Cen et al. (Mgmt Sci) | 价格延迟度量化链上信息扩散速度——时滞标定的现成度量 |
| Inoue 2024 (arXiv 2409.06255) | 公司新闻→供应商/客户 CAR 直接范本 |
| ChainKnowledgeGraph (GitHub 10万节点) | 图谱冷启动底座/六类关系 schema 对照 |
| FinDKG＋KGTransformer | 新闻流→动态图谱→事件推理的管线形态 |
| DuEE-fin/熵简 FinBERT | 中文金融事件抽取（13 类事件+论元角色）——两段式：事件抽取→按角色推方向 |
| 张龑 2021/石泽龙 2022（IO 网络研究） | IO 表 42/153 部门作行业级传导先验，边权=直接消耗系数 |
| iFinD/野尘/Choice | 无公开"事件→受益集"API；字段对齐 iFinD 事件库 schema 留采购替换接口（采购=Owner 花钱门，只报价） |

**方向语义裁定（S5 对齐）**：不用规则词表硬写链向反号——采用"事件类型×主体角色→方向
符号"两段式：事件类型/论元角色用 DuEE-fin 式抽取（规则冷启动词表先行＋LLM 按(事件类型×
角色)生成方向标签蒸馏，LLM 走 LSG 网关）。与 condaxis S5 建议默认 A（规则词表先行+LLM
蒸馏后置）一致。

## §4 仓内四层盘点（六向台账·前四向）

### 4.1 数据面
- PG ig_* 13 表 live 实查（2026-10-13）：ig_chain 873/ig_node 5,560(活 4,742)/ig_edge
  1,726/ig_node_company 25,559/ig_company_edge 58,207/ig_fact 264,072/ig_io_edge 16,859/
  ig_product_revenue 165,255/ig_chunk 5,200/ig_document 3,050/ig_company_metric 235,392。
  字段真源=industry_graph_field_dictionary.yaml。
- **G5 挂零病灶（精确）**：ig_io_edge.from/to_sector_code=统计局 153 部门三位码 vs
  ig_node.node_id=ND-xxx 两套 id。旁挂桥 ig_sector_bridge 88/153 部门但**生产只读角色
  PermissionDenied 不可读**（io_edge_binding_register.yaml:168-169）——治本第一步是修权限
  而非建桥。WO-007 旁挂册 T1_node_identity 仅 193 边（1.14%），hard_judge 禁令 79-83。
- SQLite 小图（MOD-SIG-125）：ic_nodes/ic_edges 两表连接全注入，src 内零生产实例化仅
  tests :memory:——纯库无落盘，与 PG 完全两套（condaxis S4 挖矿新证复核一致）。
- W1-W6：W2 新闻落 CH c3_fundamental.news_data（延迟 p50≈6min/p90≈13min）；W3/W4 只读
  不落库；W5 快照内存对象。

### 4.2 模块面
- news_chain_node_linker（ZA-IT-0029，testing）：link(text)→ChainNodeHit，规则法最长词优先。
- chain_impact_resolver（ZA-IT-0030，testing）：resolve(hits,polarity)→ImpactTarget，
  ig_edge 无向 BFS 2 跳，conf=hit×0.6^hop×company_conf；polarity±0.15 死区；**成本反号
  传导明确不做（:30,:56 known simplification）→方向×事件类型缺失＝本域 P2 主施工面**。
- chain_impact_stream（ZA-IT-0031，testing）：run(now)→ChainImpactSnapshot，单拍 fail-open，
  图缓存 600s。
- MOD-SIG-125 blueprint ai_autonomy=human_gated（S4 退役审批位）。

### 4.3 接线面
- TDM G1(:5767)/G2(:5797)/G4(:5852)/G5(:5879) module_ref 全 null；G5 red_reason:not_built、
  无 module_mounts 键（真空确认）；G3 已挂 equity_penetration.py＋MOD-ENTITY-GRAPH。
- 下游 L2-09-1/L2-09-2 已挂 W3/W4 模块（yaml:1575/1607，module_mounts 含 MOD-SIG-125）。
- ig_io_edge 生产消费方唯一=l9_readiness_aggregator（G5 红读数）；chain_impact_* 消费方
  唯一=api_server /api/chain-impact-stream 只读端点＋TDM 边。偏离监控/盘中扫描/负面否决
  仅为 CONSUMERS 声明未真实接线。

### 4.4 词表面
- 方向语义仅有情绪极性雏形：resolver 利好/利空中性标签；event_score surprise_direction
  ±1/0；news_sentiment_analyzer 静态正负词表（无链向语义）。
- 全仓 grep 涨价|断供|受益|受损：仅 GRF1 登记位（chain_piling 03_graph_registry.md:124，
  大宗涨价→下游毛利需边挂时滞/弹性缺口在案）＋TDM yaml:1551 催化剂词。
- 时滞仅 TDM 边 payload 静态登记（yaml:6427-6433），无计算件。

## §5 六向台账（后两向）

### 5.5 判据面（与 condaxis 口径同批对齐）
- 事件研究协议：事件日 t0，CAR 窗 (-1,+5)~(-1,+20)（具体窗宽=看数前冻结呈批），市场模型
  超额收益，无链对照组差分；方向命中=direction 与 CAR 符号一致率；多重比较校正随批。
- PIT：news_data 落库延迟 p50 6min/p90 13min 登记为滞后面；ig_* 图谱快照 PIT 口径=
  valid_from/valid_to 双时间轴（字段真源 :289）。
- 强度校验：strength 分桶后 CAR 单调性（分层单调性方向与预注册一致——condaxis 02:34 同款）。

### 5.6 消费面
- 挂条件轴：condition_package 信息事件=行级标注不占格（X2-B 先例）。
- 挂 L2-09 催化剂识别：四元组 targets 直接进冲击标的生成。
- 挂负面否决器 L3-04：direction=-1 的标的进否决候选。
- 做T域联动：盘中事件→涨速异动扫描（L3-11-2）交叉验证（后置）。

## §6 病灶诊断（自审闸输入）

| # | 病灶 | 定级 | 处置走向 |
|---|---|---|---|
| D1 | G5 双 id 挂零（153 部门码↔ND-xxx），桥表 88/153 且生产角色无权读 | 阻断级 | P2 治本：先修权限→桥表补齐→ig_io_edge 挂 ig_node（联动 WP-0.5/f32） |
| D2 | 方向=极性死区，无链向反号（涨价上游+1/下游-1 未建模） | 阻断级 | P2 主施工：事件类型×角色→方向符号两段式（S5 对齐） |
| D3 | 时滞无计算件 | 缺口级 | P2：先验带＋事件研究标定 |
| D4 | SQLite 小图零实例化（双真源） | 保留面 | S4 走 A（语义并入 PG，壳退役走轨 B 呈批——出方案不动手） |
| D5 | W1-W6 未结案（2026-09-09 directive） | 收口级 | 本役 P2 一并结案：W4 方向语义落地即结案主件 |
| D6 | resolver BFS 无向、全跳同向 | 缺口级 | P2 重写为带角色有向传导 |

## §7 待裁项（进 P1 总表）

| # | 项 | 选项 | 建议默认 |
|---|---|---|---|
| C1 | ig_sector_bridge 生产只读角色权限修复 | A 授读（治理面动作）；B 复制到公共 schema | A（最小权限面） |
| C2 | CAR 窗宽/方向命中率门槛等判据数值 | 看数前冻结呈批 | (-1,+5)/(-1,+20) 双窗起步 |
| C3 | SQLite 小图退役（轨 B 保留面） | 退役/保留 | 退役走墓碑（S4 建议默认 A，MOD-SIG-125 human_gated 审批） |
| C4 | 研报级"受益标的"数据源采购（iFinD 事件库等） | 只调研报价呈批 | 不采（Q10 精神：先吃仓内） |

## §8 车道回报存档

- 仓内四层盘点：agent_cf82248e（2026-10-13 23:5x 回报，全带 :行号 锚点）
- 外部对标：agent_b0590707（Cohen-Frazzini/Cen/Inoue/ChainKnowledgeGraph/FinDKG/DuEE-fin/
  张龑/石泽龙/iFinD/野尘，URL 在案）

## §9 自审闸三态裁定（封矿）

- [x] 六向台账齐（数据/模块/接线/词表/判据/消费）
- [x] 病灶全部定级＋处置走向
- [x] 待裁项进 P1 总表
- [x] 与 condaxis S4/S5 双锚互引（§3 §6-D4）
- 状态：**过闸·封矿**（判据数值留 P2 看数前冻结呈批＝纪律不违封矿）
