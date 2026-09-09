---
ttl: permanent
doc_type: policy
rule_form: standard
verifiability: machine
title: 产业链图谱质量标准——二十项合格线与循环修复
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.2.0"
date: 2026-09-09
topic: industry_graph_quality
scope: global
depends_on:
  - industry_chain_data_audit_sop
related_issues: []
related_modules:
  - scripts/industry_graph/graph_quality_check.py
  - scripts/industry_graph/websearch_ingest.py
---

# 产业链图谱质量标准（Graph Quality Standard）

> **用途**：产业链图谱（PG depgraph 库 ig_* 十表）的**质量验收真源**。定义"什么样子算合格"的十九项合格线（§2~§6）。
> **机判引擎**：本标准的每条合格线由 [graph_quality_check.py](../../../../../scripts/industry_graph/graph_quality_check.py) 固化为 SQL 一键体检——**审查判定权归脚本，AI 只负责修复不负责判定**（治 AI 审查口径漂移）。
> **配套编排**：修复循环、退出条件、时间盒见 [industry_chain_data_audit_sop](../sop/industry_chain_data_audit_sop.md) §11（v1.5.0 起）。
> **四大裁定（Owner 2026-09-09 确认）**：① role 词表五值 ② 垃圾修复一律 PIT 关闭零物理 DELETE ③ 单公司挂链阈值 20 ④ 本文件为验收真源、SOP 引用不重复。

## 1. 术语与豁免机制

| 术语 | 含义 |
|---|---|
| 违规 | 引擎 SQL 命中的行/组，出现在违规报告（JSON+MD）中待修 |
| PIT 关闭 | 不删行，将 `valid_to` 置为修复日（查询侧默认过滤 `valid_to IS NULL`）——本标准下垃圾数据的**唯一**处置方式 |
| 豁免清单 | 人工裁定"此违规合法保留"的登记表（`scripts/industry_graph/quality_exemptions.yaml`），引擎读取后从违规中扣除；**豁免必须登记原因+裁定日期**，未登记豁免的违规不许留存 |

## 2. 链层合格线（S-CHAIN，5 条）

| # | 标准 | 判定规则（大白话） | 修复方案 |
|---|---|---|---|
| S1 | 链名零文档标题腔 | 正则命中"一张图看懂/重磅/最新/预测/深度/全景图/解读/盘点/风向标/启幕/ppt"即违规 | 改规范名（"XX产业链"句式）；与既有同义链重者并入（deprecated+merged_into） |
| S2 | 链名唯一且规范 | 同名链>1 违规；含"·数字"尾巴违规 | 保留信息最新者，其余并入 |
| S3 | category 全在申万 38 词表 | 值不在词表=违规 | 就近修正；判不准进开放问题禁塞"综合" |
| S4 | 废弃链闭环 | deprecated 缺 merged_into 违规；废弃链上落位残留违规 | 补指向；残留落位 PIT 关闭后并入目标链 |
| S5 | version_year 覆盖 | 活跃链 version_year IS NULL 违规（豁免：行业锚点链） | 按源文档年份补；无据可查进开放问题 |

## 3. 节点层合格线（S-NODE，4 条）

| # | 标准 | 判定规则 | 修复方案 |
|---|---|---|---|
| S6 | tier 全在 9 值词表且零 unspecified | tier 不在 {上游,中游,下游,设备,材料,零部件,原材料,辅材}（unspecified 另计）违规；tier='unspecified' 违规（豁免：登记待 Owner 处置的 306 条） | 机械判定（环节词/描述推断）落地 380 条；306 待处置留 Owner。**2026-09-09 裁定（Owner 委托夜班 AI）**：废弃链上节点=历史快照不审（引擎已加活跃链过滤，与 S8 同口径）；活跃链上 150 条维持豁免、随链重建时以规范节点替代 |
| S7 | 节点名零 "-tier" 后缀 | name 以 -(上游|中游|下游|设备|材料|零部件|原材料|辅材|unspecified) 结尾违规 | **双轨**：前端/查询侧显示剥离（立刻生效）；数据层改名随迁移脚本慢做（改名牵 node_id，需专项） |
| S8 | 零孤岛节点 | 无边且无落位的节点违规（豁免：行业聚合节点） | 有据补边/补落位；无据 PIT 关闭所在链（链级）或登记 |
| S9 | 同链同名节点零重复 | 同 chain_id 下 name 相同（不同 tier 视为不同节点）>1 违规 | 合并到 tier 正确者 |

## 4. 落位层合格线（S-MAP，5 条）

| # | 标准 | 判定规则 | 修复方案 |
|---|---|---|---|
| S10 | role 全在五值词表 | role 不在 {龙头,核心,主要,参与,提及} 违规 | 语义归一：mentioned/参与/主要→"提及/参与/主要"直译；长尾杂值（如"后段（化成分容）设备龙头"）按含"龙头"归龙头，映射表 `role_migration.yaml` 留痕 |
| S11 | 死映射零存量 | cn symbol 不在 stock_basic 在市集=违规 | 退市/更名所致→PIT 关闭该落位 |
| S12 | market 一致 | node_company.market ≠ node.market 违规 | 机械修正 |
| S13 | 新落位 PIT 覆盖 | 2026-09-08 后新增落位 valid_from IS NULL 违规（存量另立计划：行业锚点回填上市日/环节填盘点日） | 补 valid_from；历史回填走专项脚本 |
| S14 | 挂链数阈值 | 单 symbol 挂活跃链 >20 =违规候选，必须甄别 | 事故性污染（如 000591.SZ 挂 269 链）→保留真实业务链，其余 PIT 关闭；真多元化公司（比亚迪类）→豁免登记 |

## 5. 边层合格线（S-EDGE，5 条）

| # | 标准 | 判定规则 | 修复方案 |
|---|---|---|---|
| S15 | 零自环边 | from_symbol=to_symbol 违规 | PIT 关闭（valid_to 关死） |
| S16 | 零事故性双向边 | 同年同类型存在 A→B 与 B→A=违规；**成对冗余豁免**：supplies_to A→B + customer_of B→A 是设计内反向边，合法 | 同类型重复对：保留证据强者，弱者 PIT 关闭 |
| S17 | websearch 边完整 | websearch 边缺 valid_from/as_of/evidence_type 任一违规 | 补齐；evidence 无据可补→登记 |
| S18 | UNLISTED 格式统一 | symbol 匹配 ^UNLISTED: 但非 UNLISTED:UE-{12hex}=违规 | 登记编码表后换码（migrate 脚本） |
| S19 | 编码表零上市撞名 | unlisted 实体 name 精确等于在市 A 股简称=违规 | 核对→标 listed+listed_symbol→跑 promote 换码 |
| S20 | PIT 反造假（2026-09-09 红蓝对抗增补） | websearch 边 valid_from 早于证据年份前一年（year=2025 而 valid_from<2024-01-01）=违规——防"拍脑袋编历史"式前视造假 | 有据修正（上市日/协议签署日）；无据→清空 valid_from 重填盘点日+登记。**2026-09-09 裁定（Owner 委托夜班 AI）**：判定保留不改——year=新闻年/vf=签约日的"追述型长协边"是本条主要误报源（实测 22 条：15 条签约日即披露日+7 条新闻追述），处置=豁免制度化（登记+抽检原文），不改判定放行以保住反造假哨 |

**豁免滥用法防线（红蓝对抗 2026-09-09 增补）**：任一类豁免数 > 该类违规总数 5% 须 Owner 签名（裁定人=Owner 手写），否则视为无效豁免。

## 6. 深度体系（层级下钻模型，2026-09-09 Owner 定稿——"你中有我我中有你"树状全景）

> **模型**：全景图=可无限下钻的树。L1 主链（如半导体产业链：上游材料/设备/EDA→中游设计/制造/封测→下游应用）→ 每个环节节点可挂 **子链**（child\_chain）继续展开（封测环节→L2 封测产业链→其划片机环节→L3 划片机产业链→……）→ 直到**砖**（叶子）。链的层级递归可查：不被任何节点 child\_chain\_id 指向的链=根链（L1）。

**子链挂接契约（ig\_node 新列，DDL v4）**：
- `child_chain_id TEXT`：该环节的下钻子链（指向 ig\_chain.chain\_id，应用层校验非 FK——与 symbol 软引用同风格）。
- `drill_status TEXT` 封闭枚举：`'child'`（已下钻，child\_chain\_id 必非空）｜`'brick_mass'`（砖·判据A）｜`'brick_noalpha'`（砖·判据B）｜`NULL`（待判定）。
- **砖双判据（下钻终止，Owner 2026-09-09）**：A `brick_mass`=子流程输入是通用大宗（金属/塑料/基础化工原料/标准件等任何行业通用物）→ 停；B `brick_noalpha`=再下钻一层**不新增 A 股标的**→ 停（建图谱为交易服务，无 A 股参与的深层不拆）。判据须在环节 description 附一句依据。
- 挂接纪律：子链必须是已存在的链（先建链再挂接，ingest node 记录带 child\_chain\_id）；同一环节只挂一条子链（多主题拆多环节）。

## 7. 公司详情卡字段标准（2026-09-09 Owner 定稿——"每个节点上下左右都得有"）

> 公司节点（symbol）的完整画像。字段分四级：MUST（缺=残缺，引擎可审）/ SHOULD（缺=登记）/ DERIVED（查询侧实时计算不落库）/ 渐进（样板链验收后转 MUST）。

| 组 | 字段 | 来源 | 级别 | 审查规则 |
|---|---|---|---|---|
| 身份 | symbol 代码 / name 名称 / market 市场 | 落位表+stock\_basic | MUST | S11/S18 已覆盖 |
| 坐标 | chains 所属链（多条合法）/ node 环节 / tier 层位 / role 角色 | 落位→节点→链 | MUST≥1 条坐标 | 链-环节-角色三元组完整 |
| 坐标 | chain\_path 层级路径（L1→L2→…→当前链） | child\_chain\_id 递归 | **渐进** | 样板链（半导体）验收后转 MUST |
| 上游 | suppliers 供应商边（对手方+product+year+PIT+evidence） | 边表 to\_symbol=我 | SHOULD≥1 | 源头类公司（矿业/材料源头）豁免须登记 |
| 下游 | customers 客户边（同构） | 边表 from\_symbol=我 | SHOULD≥1 | 终端类公司（整机/应用）豁免须登记 |
| 网络 | 上二层/下二层（传递上下游） | 图遍历 | DERIVED | 不落库，查询侧实时算（二层闭包 v1.2 已定） |
| 标签 | ths\_industry THS 行业（二级）/ sw\_category 申万一级 | 行业聚合链落位+链 category | MUST（A 股） | 分层标签架构（开放问题 8 裁定） |
| 内容 | profile 公司简介 | ig\_chunk ths\_profile | SHOULD | 无简介登记（THS 铺面已 5200 块） |
| 质量 | confidence / source\_doc / evidence\_text | 各表自带 | MUST | 写入契约（§4）已保证 |

**完备度分档（引擎 S23 口径）**：`完备`=MUST 全有+SHOULD 全有；`基本完备`=MUST 全有；`残缺`=缺任一 MUST。报告出三档占比+残缺清单。

## 8. 深度审查三查（S21~S23，**先进度指标后硬闸**：样板链验收前=报告项不计违规，验收后转硬闸）

| # | 标准 | 判定规则（大白话） |
|---|---|---|
| S21 | 流程主干连通 | 活跃链内节点≥2 却零 structure 边=散点链（当前 289/789）——主链必须从上游头到下游尾连通成线 |
| S22 | 层级下钻到位 | P1 主链每个环节节点：drill\_status='child'（挂了子链）或砖（mass/noalpha）——NULL=待下钻；非 P1 链暂缓 |
| S23 | 公司详情完备 | 按 §7 分档统计完备率+残缺清单（身份/坐标/标签 MUST 项） |

## 9. 进度指标（非违规，报告附栏）

行业宽度（THS 90 行业锚点覆盖）、全球主干链 X/25、事件传导闸通/不通、环节级落位覆盖率、深度三查（S21~S23）。这些是**进度条不是合格线**——只报告不阻断（S21~S23 样板验收后升格）。

## 10. 修复纪律（逐字适用）

1. **修复唯一通道**：存量治理走专项治理脚本（幂等）或 websearch_ingest 通道（新写），**禁手写 SQL 写库**；SELECT 类诊断不受限。
2. **PIT 关闭三字段**：valid_to=修复日 + 修复批次 source_doc 留痕（"quality_fix|批次号|日期"）+ 违规报告归档对账。
3. **豁免即登记**：任何"判断合法保留"的违规必须在 quality_exemptions.yaml 登记（编号/原因/裁定日期/裁定人=Owner 或登记 AI+开放问题编号），未登记豁免留存=下次循环仍违规。
4. **防新增**：写入工具校验与引擎同一套词表/正则——引擎查存量（治标）、工具拒新增（治本），两边规则漂移=事故。

## 11. 版本

- 1.0.0（2026-09-09）：初版十九项合格线（Owner 四裁定确认同日）。
- 1.1.0（2026-09-09）：红蓝对抗增补——S20 PIT 反造假（防编历史式前视造假）+豁免滥用法防线（>5% 须 Owner 签名）。
- 1.2.0（2026-09-09）：**深度体系定稿**（Owner 三层图例定标）——§6 层级下钻模型（子链挂接 child\_chain\_id/drill\_status+砖双判据 mass/noalpha）；§7 公司详情卡字段标准（四级 MUST/SHOULD/DERIVED/渐进+完备度三档）；§8 深度审查三查 S21~S23（样板链验收前为进度指标、验收后升硬闸）。
- 1.2.1（2026-09-09）：**Owner 委托夜班 AI 裁定落地**——S20 判定保留不改、追述型长协误报走豁免制度化（22 条已签豁免）；S6 引擎加活跃链过滤（废弃链节点=历史快照不审，豁免 306→150）；S8 墓碑豁免约定（"（已并入"标记）。
