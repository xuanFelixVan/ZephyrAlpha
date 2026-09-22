---
ttl: task_bound
completes_when: 随定桩战役归档
title: 图谱谱系注册表——L2 传导图谱层候选盘点与原料评估（W5）
owner: ZephyrAlpha-Owner
session: st-chainpile-20260922
date: 2026-09-22
---

# 图谱谱系注册表（L2 传导图谱层）

> **真源回溯**：[纪要§4] L2=传导图谱（产业链/股权穿透，图谱可被任意源线复用）；[纪要§5] 外部锚点 ChainKnowledgeGraph 开源 10 万节点 17 万边；[纪要§9] 验收硬数字"图谱 ≥3 张带原料评估"；[总包令 W5] 本件=03_graph_registry.md，目标 ≥3 张。
> **[判读]** 内部规模数字取自库内实查留痕（`docs/_working/altdata_line/05_industry_chain_assets_plan.md` 2026-09-17 实查、`scripts/entity_graph/equity_penetration.py` 2026-09-19 首跑 TESTS 头注），非本会话重查；外部数字取自公开渠道，链接经 WebSearch 核实（检索日=2026-09-22）。本表只登记不施工：不建表/不写库/不接线/不采购（[纪要§10] 禁业务施工边界）。

## 0. 登记口径

- 每张图谱七字段：图谱名 / 类型 / 节点边规模 / 真源渠道 / 原料评估（License·新鲜度·接入成本）/ 源线复用接口 / 消费层（统一 L2）。
- 每张图谱末尾挂 W6 展开锚 3-5 槽（§6 统一编号 GRF1-GRF18，槽位占位；W6 按 [纪要§7] 字段清单展开，`graph_ref` 字段回填本表图名）。
- 规模口径注：ig_chunk 存在两波口径（DDL 头注"E 盘语料 76,112 块"vs 09-17 实查 5,200 行），本表采 09-17 实查值并登记差异——机械可证，自裁级留痕。

## G1 产业链图谱（必选）

| 字段 | 登记 |
|---|---|
| 图谱名 | Zephyr 产业链图谱（industry_graph，PG depgraph 图谱域 ig_* 14 表） |
| 类型 | 产业链（环节结构边 + 部门级 IO 供需边 + 公司级供应链边三层） |
| 节点边规模 | 实测（2026-09-17 实查）：ig_chain 873 链（avg 6.4 节点）/ ig_node 5,560 / ig_edge 1,726 / ig_company_edge 58,207 / ig_node_company 18,819 / ig_product_revenue 52,404 / ig_fact 264,072 / ig_unlisted_entity 14,070；CH 侧 industry_class 31,414 + suppl 10,141 |
| 真源渠道 | 内部主源：`scripts/industry_graph/apply_industry_graph_ddl.py`（DDL-as-Code 唯一真源）+ 同花顺终端导出（ths_export，confidence=0.6，仅限本机内部研究消费）；字段真源=`docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml`；审计政策=`docs/01_policies_and_standards/sop/data_audit_sop/industry_chain_data_audit_policy.md` |
| 源线复用接口 | 任意源线可挂（[纪要§4]）：公告/研报文本线抽实体边经 ig_document→ig_chunk→ig_fact 溯源链挂图；行情线按 ig_node_company 成分聚合出板块传导 |
| 消费层 | L2 传导图谱层（上游=L1 全部源线；下游=L3 板块状态变量、L4 决策） |

原料评估（三维度 × 分渠道）：

| 渠道 | License | 新鲜度 | 接入成本 |
|---|---|---|---|
| 自建 industry_graph | 自建+官方统计口径，内部消费无限制 | THS 导出 as_of 2026-09-08；ig_fact 混合 as_of，PIT 靠 source+as_of 双标记 | 已建零成本；缺口=ig_entity_code_map 仅 2 行（消歧桥空置=假边风险，altdata_line WP-0 在案） |
| 同花顺 iFinD（外部候选增强） | 机构商用授权，数据仅限授权范围、禁转售/二次分发，须签数据使用协议（https://quantapi.10jqka.com.cn ） | 机构级日更（收盘后 1-2 小时入库） | 机构采购制，第三方选型文口径年投入 10 万+量级；现有终端导出通道已够用，暂无采购必要 |

W6 展开锚：见 §6 GRF1-GRF4。

## G2 产业链外部开源源——ChainKnowledgeGraph（必选，已导入）

| 字段 | 登记 |
|---|---|
| 图谱名 | ChainKnowledgeGraph（刘焕勇/liuhuanyong 开源，[纪要§5] 锚点） |
| 类型 | 产业链（上市公司-行业-产品三类实体） |
| 节点边规模 | 纪要锚点：10 万节点 17 万边；分项实测（导入脚本头注）：4,654 上市公司 / 511 申万行业 / 95,559 产品 / 110,153 产品-产品边 + 53,785 公司-主营边 + 4,430 公司-行业 + 480 行业树（分项合计与纪要锚点吻合，机械可证） |
| 真源渠道 | 外部：https://github.com/liuhuanyong/ChainKnowledgeGraph ；内部已导入 ig_fact 事实层（source='ckg_2021'，as_of='2021-10-26'，PIT 诚实；不碰 ig_node/ig_edge 防污染链结构），导入件=`scripts/industry_graph/import_ckg_dataset.py` |
| 源线复用接口 | 行业级上游聚合（supplies_to 带 ups JSON）供宏观线做行业传导先验；产品-产品边供研报线抽取结果的交叉验证底图 |
| 消费层 | L2 传导图谱层（G1 的事实层增强） |

原料评估（三行）：
- License：开源仓库未见 LICENSE 文件=默认版权保留（"保留所有权利"）；内部研究消费低风险，禁对外二次分发。
- 新鲜度：差（2021-10-26 最后数据 commit，静态快照）；仅作结构先验，不作现势事实。
- 接入成本：零（已导入，幂等可复跑）；残余成本=产品名与 ig_node 消歧对齐。

W6 展开锚：见 §6 GRF5-GRF7。

## G3 股权穿透图谱（必选）

| 字段 | 登记 |
|---|---|
| 图谱名 | Zephyr 实体股权图谱（entity_graph 六表 + ig_equity_edge + CH 股东三表） |
| 类型 | 股权穿透（股权边/任职边/隐形边三类；N 度向上穿透） |
| 节点边规模 | 实测（2026-09-19 首跑）：ig_equity_edge 804 条并入 edge_holding（THS 被投，as_of=2025-12-31）；A 层 akshare 十大股东现行版本对 274,865（比对：重叠 129 / ig 独有 675 / A 层独有 274,736）；CH 在产续采表：fund_top10_shareholders / fund_top10_circulating_shareholders / fund_shareholder_count |
| 真源渠道 | 内部主源：`scripts/entity_graph/apply_entity_graph_ddl.py`（六表 DDL）+ `scripts/entity_graph/equity_penetration.py`（N 度穿透函数，三家样本 600566/600927/601963 实测通过）；设计真源=`docs/_working/altdata_line/02_entity_graph_equity_person.md`（四决策：uscc 主键 / PIT 双轴 / 持股≠控制 / 境外断线不编造）。外部候选：天眼查开放平台 https://open.tianyancha.com （参考价约 1500 元/万次，股权穿透约 5 层，无免费额度，需商务洽谈）；企查查开放平台 https://openapi.qcc.com （按次/充值/企业套餐三模式，QPS 按套餐，第三方横评称穿透约 3 层）；启信宝（第三方横评：最深约 12 层、约 0.015 元/次起） |
| 源线复用接口 | 公告线（质押/冻结/举牌挂股权域事件）、行情线（同实控人联动/牛散跨票聚合）、龙虎榜线（席位↔实体归并）均可挂本图 |
| 消费层 | L2 传导图谱层（穿透链输出供 L3 情绪/板块与 L4 风控消费） |

原料评估（三维度 × 分渠道）：

| 渠道 | License | 新鲜度 | 接入成本 |
|---|---|---|---|
| 自建 entity_graph + CH 三表 | 自建合规（akshare 开源库 + THS 终端导出仅限本机内部研究消费） | 报告期口径季更，公告日 PIT 锚；akshare 东财 datacenter 公告日窗口续采 | 已建零成本（含穿透函数）；缺口=低比例如<前十门槛关系不入十大口径 |
| 天眼查/企查查/启信宝（外部候选） | 商用授权，数据禁转售/二次分发，条款以官方协议为准；采购=资金门位→Owner（宪法§5 high 域） | 准实时（工商变更日更） | 按次计费（上述公开报价口径）；深层穿透（实控人/代持识别）为内部图不可见项（设计决策③），是外部源唯一不可替代价值 |

W6 展开锚：见 §6 GRF8-GRF11。

## G4 概念/题材图谱（必选）

| 字段 | 登记 |
|---|---|
| 图谱名 | Zephyr 概念标签图谱（stock_concept 表）+ 外部概念源候选 |
| 类型 | 概念/题材（公司属性标签，与产业链结构正交） |
| 节点边规模 | 内部：stock_concept 公司×概念标签（as_of 2026-09-14，THS 公司档案导出，市场分类标签装载前过滤；行数无实查留痕，W6 展开前须先补实测——已登记为 W6 前置动作）；THS 板块行业导出 816 板块。外部参照：OpenConcepts 浙大中文概念图谱 440 万概念 |
| 真源渠道 | 内部：`scripts/industry_graph/concept_ingest.py`（装载器；"概念≠产业链"硬边界——概念型链名禁入 ig_chain）。外部：akshare 东财概念板块接口（stock_board_concept_name_em / _cons_em / _hist_em，文档 https://akshare.akfamily.xyz ）；OpenKG http://openkg.cn （FR2KG 金融研报知识图谱 CCKS2020/达观数据等数据集集散地）；OpenConcepts https://openconcepts.zjukg.cn ；同花顺 iFinD 板块/产业链 https://quantapi.10jqka.com.cn （机构级授权，见 G1 渠道行） |
| 源线复用接口 | 情绪线（概念热度聚合）、行情线（概念成分行情）、资讯/研报线（题材-公司归属判定）挂本图 |
| 消费层 | L2 传导图谱层（供 L3 情绪与板块状态变量的题材维度） |

原料评估（三维度 × 分渠道）：

| 渠道 | License | 新鲜度 | 接入成本 |
|---|---|---|---|
| 自建 stock_concept | 自建（THS 终端导出口径） | 静态快照 as_of 2026-09-14 | 已落零成本 |
| akshare 东财概念板块 | akshare/MIT 开源（底层数据为东财公开页，仅限研究用途） | 日更；限流严格（第三方 issue 实测 10 秒/次仍可能被限流，须限速队列） | 小改：concept_ingest 头注已预留"接 akshare 概念接口做定期增量" |
| OpenKG / OpenConcepts | 逐数据集看授权（FR2KG 为 CCKS2020 评测公开数据；OpenConcepts 开源） | 静态学术数据集，非现势 | 中（需筛选-清洗-对齐三步，题材时效性差，仅作概念词表扩充原料） |

W6 展开锚：见 §6 GRF12-GRF15。

## G5 投入产出/供应链传导图（余力加登）

| 字段 | 登记 |
|---|---|
| 图谱名 | IO 投入产出结构锚（ig_io_edge）+ 公司级供应链边（ig_company_edge） |
| 类型 | 产业链-部门级量化传导（上下游强度的机械判定依据） |
| 节点边规模 | 实测：ig_io_edge 16,859 条（国家统计局 2020 年 153 部门直接消耗系数，2026-09-13 io-structure-anchor-plan 落库）；ig_company_edge 58,207 条（PIT 三时间戳+边元数据五列） |
| 真源渠道 | 内部：`scripts/industry_graph/apply_industry_graph_ddl.py` v7（ig_io_edge DDL）+ 落库计划=`docs/_working/archive/2026-09/c_class_scattered/2026-09-13-io-structure-anchor-plan.md`；外部原始源：国家统计局投入产出表 https://www.stats.gov.cn （域名级链接，未深链核实） |
| 源线复用接口 | 宏观线（大宗/商品价格冲击的行业弹性传导）、量价线（上游涨价→下游毛利传导测算）挂本图 |
| 消费层 | L2 传导图谱层（tier 退役裁定遗留缺口的量化补位件） |

原料评估（三行）：
- License：国家统计局公开统计口径，内部消费无限制。
- 新鲜度：差（投入产出表三年/五年一编，2020 为现版口径）；公司级边随公告/研报更新补时效。
- 接入成本：已落库零成本；头号缺口=io_edge 部门码与 ig_node 是两套 id 体系，16,859 条边现 100% 挂不上节点（altdata_line 已升 WP-0.5）。

W6 展开锚：见 §6 GRF16-GRF18。

## 6. W6 展开锚（GRF 槽位占位，W6 填充）

> 展开规则：每槽产出 q_id（PQ-NNNN，墓碑不复用）+ graph_ref=本表图名 + layer=L2，逐条过五要素机检（[纪要§2]）；每图谱 3-5 问（[总包令 W6]）。以下为候选问题一句话占位，非正式问题。

| 槽 | 所属图 | 候选问题方向（占位） |
|---|---|---|
| GRF1 | G1 | 沿 IO 系数的大宗涨价→下游行业毛利量化传导问（需边挂时滞/弹性——05 计划缺口③在案） |
| GRF2 | G1 | 873 链"节点→公司映射完整度≥阈值"的可考性分级问 |
| GRF3 | G1 | CKG 产品-产品边与研报线抽取边的交叉验证一致率问 |
| GRF4 | G1 | ig_entity_code_map 消歧桥覆盖率对假边率的敏感性问 |
| GRF5 | G2 | CKG 2021 行业上游聚合对当期行业传导判定的仍有效比例问（陈旧度界） |
| GRF6 | G2 | 产品名消歧对齐后 ig_fact 可升级为链结构边的比例问 |
| GRF7 | G2 | CKG 行业树与申万词表映射的覆盖率与冲突率问 |
| GRF8 | G3 | 同实控人上市公司组合收益联动性问（穿透函数现行版本对口径） |
| GRF9 | G3 | 十大股东口径（274,865 对）×ig_equity_edge 互补边的增量信息问 |
| GRF10 | G3 | 股权质押/冻结公告事件与 edge_holding 现行版本的时序一致性（PIT）问 |
| GRF11 | G3 | 境外断线（BVI/开曼止步）导致的穿透覆盖率缺口量化问 |
| GRF12 | G4 | 概念成分股与产业链链名公司的重合/分歧度问（"概念≠产业链"边界实证） |
| GRF13 | G4 | 东财概念 vs THS 概念标签覆盖差异与新鲜度差问 |
| GRF14 | G4 | 概念热度聚合对 L3 情绪变量的先行/同步性问 |
| GRF15 | G4 | 市场分类标签过滤规则的误杀率问 |
| GRF16 | G5 | 部门码↔ig_node 映射补齐后 io_edge 可挂边比例问（现 16,859 条挂零） |
| GRF17 | G5 | ig_company_edge 58,207 条供应链边置信度分层问 |
| GRF18 | G5 | IO 表 2020 口径滞后对当期传导判定误差的界问 |

## 7. 净零声明

- 本表替代物=无（新增登记件，纯文档，零代码零表零配置）；写域=本战役目录内（[纪要§10] 合规）。
- 与既有图谱资产分工：图谱本体元数据真源不变——DDL 真源=`scripts/industry_graph/apply_industry_graph_ddl.py` 与 `scripts/entity_graph/apply_entity_graph_ddl.py`，字段真源=`industry_graph_field_dictionary.yaml`，审计政策=`industry_chain_data_audit_policy.md`，行数实查=`05_industry_chain_assets_plan.md`。本表只新增"问题视角谱系 + 原料评估 + 源线复用接口"三项，不复制上述真源的表结构/字段细目；行数仅作规模登记并注实查留痕出处。
- 外部商用源（天眼查/企查查/启信宝/iFinD）仅登记候选与公开报价口径，未采购未接入；采购涉资金门位=Owner（宪法§5）。
- GRF1-GRF18 为空槽占位，未占用问题登记表 q_id 段位（墓碑不复用规则不受影响）；W6 展开后本表不维护问题全文，全文以 W6 入表件为真源。
