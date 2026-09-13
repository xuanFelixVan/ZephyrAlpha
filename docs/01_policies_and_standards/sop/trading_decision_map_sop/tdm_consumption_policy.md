---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 交易决策全景图·消费场景规程（TDM Consumption Policy）——什么场合必须打开地图、读什么、验证什么
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-09-14
topic: tdm_consumption_policy
---

# 交易决策全景图·消费场景规程（TDM Consumption Policy）

> **一句话**：凡"建蓝图锚、新模块施工、新策略挂图、回测开跑、改节点判据、信号引擎变更、策略退役、事后复盘、转级检查"九类场合（S1-S9），MUST 按本卷场景表打开 TDM 地图做规定动作——**地图不许只被引用不被阅读**。
> **诞生**：2026-09-14 班起草（起因=Owner 体检发现 TDM"被引用、不被阅读"）；经两轮寻路挖矿（附录 A/B：arXiv 学术支撑+SR 11-7 银行模型治理金标准对齐）后同日升格 permanent。实质条款（S7-S9 场景、知识生效日哨兵）已随 TDM v1.3 施工立项获批（0e94229a1b 验收五条），本卷是其真源落位。
> **亲缘与分工**：增长=../mining_sop/trading_decision_map_pathfinding_policy.md（六向寻路）；层位讨论=同目录 trading_decision_map_layering_policy.md（四道前置检查）；策略挂图操作=../backtest_system_sop/sop_c_strategy_library_intake.md §6。本卷只管"消费"这一缂，与上述真源不重复；冲突时各缂以各自真源为准。

## §1 地图的目的与功能（依据=地图自身 INV-1 声明 + D1-D6/D108 裁定）

**一句话**：TDMAP-001 是我们"怎么交易"的**决策链骨架真源**——全量节点（计数以地图自身实时为准，本卷不写死）把从数据到信号的整条决策链钉死，每个节点带验收判据与置信度标签。

**五大功能**（每条都有文件内证据）：
1. **决策链骨架**：建仓/持仓/离场/组合四条流，L0-Ln 分层（INV-1：只定义骨架，四层资产按标识符引用）；
2. **验收判据载体**：每节点带判据+置信度三态（D5：verified=回测归因支撑/proposed=主观假设待验证/untested）——防止"主观假设冒充已验证"（血肉填充约定）；
3. **回测治理母体**：回测对象预注册表（BT-P0）从地图解析导出，禁手工挑；effective_from（2026-09-08）=知识层 PIT 生效日——**回测区间早于此=知识漂移，必须声明**（D120）；
4. **缺口发现器**：module_ref=null=缺口节点（warning）——地图直接显示"哪个决策环节还没有代码"；
5. **策略挂载点**：策略入库最后一步"挂图"（SOP-C §6）=把策略钉到它服务的节点上。

## §2 消费场景规程（S1-S9：什么场合必须打开地图做什么）——本卷核心

| # | 触发场合 | 必须动作 | 不做的后果 |
|---|---|---|---|
| S1 | **新模块施工前** | 打开地图找到模块服务的节点：若节点 module_ref=null（缺口）→ 本施工是在填缺口，写明；若有主 → 本模块是重复实现，须说明差异 | 重复造轮子/地图与代码脱节 |
| S2 | **新策略挂图时**（SOP-C §6） | 读目标流的节点链，回答"本策略挂在哪个节点的判据下"；该节点置信度若是 proposed → 本策略回测就是它的验证证据，回填 evidence（机构对应物=因子生命周期 research→verified→production；活例=RSRS 三窗→STR-VREV-025 evidence 回填） | 判据永远停在 proposed，地图失去信用 |
| S3 | **回测开跑前**（预检） | 检查①回测区间是否早于 effective_from（知识漂移声明；AI 产物判据携带"知识生效日"=源发布日+模型日期，供本预检消费）②被验证的判据节点是哪几个（写进 run 档案 verdict_ref） | 回测结果无法归因到判据，白测 |
| S4 | **修改任何节点判据时** | 必须 D 裁定+台账留痕+刷新 effective_from（已有流程，重申） | 挪门柱/知识漂移 |
| S5 | **寻路增长时** | 已有寻路 SOP（T1-T4 六向协议），不重复 | — |
| S6 | **信号引擎变更时**（如总闸状态机） | 读对应节点组（如 L0-01/02/03 预案引擎挂载），确认变更范围与节点判据一致（先查 TDM-E-L1 判据再动手） | 引擎改了、判据没跟上 |
| S7 | **策略退役/衰减时** | 追溯哪个节点失去证据 → 更新该节点置信度 → 标记下游受影响策略（D108 三条件 ✓） | 墓碑策略拖累下游判读 |
| S8 | **事后复盘时** | 按决策日期回放地图状态（git 历史=地图时间轴），回答"当时判据说什么"（零新机器，实践约定） | 复盘拿今天的判据苛责当时的决策 |
| S9 | **转级检查点**（candidate→sim→paper→live） | 每次转级核对本节点置信度与衰减状态 | 带病转级 |

## §3 后续机制（已立项，本卷不重复立项）

S1/S3 的门禁化（蓝图锚↔地图节点引用一致性校验、run 档案知识漂移声明校验）与节点验证元数据（last_validated_at/validated_by）、节点级衰减联动（materiality 档位）——**均已并入 TDM v1.3 施工批**（0e94229a1b，Owner 批准，验收五条含 S7-S9 条款与知识生效日哨兵），按施工 SOP 走，落地后回填本卷引用。

---

## 附录 A：寻路批次 #1（2026-09-14，按 TDM 寻路 SOP 对 S1-S6 挖矿）

### S3 知识漂移预检——挖到学术硬支撑

- 机构共识：PiT（时点数据）是量化机构的付费标配——回测在 T 日只能用 T 日前可得的信息
  （[Quant Builder](https://www.quant-builder.ai/articles/point-in-time-data)、
  [Hedge Fund Alpha](https://hedgefundalpha.com/education/why-quants-pay-more-for-point-in-time-data/)、
  [CFA L2 教材](https://analystprep.com/study-notes/cfa-level-2/problems-in-backtesting/)）；
- **学术前沿（直击本图）**：[arXiv:2601.13770 Look-Ahead-Bench](https://arxiv.org/pdf/2601.13770)
  （Benhenda 2026）把 **LLM 的知识截止日**当作时点约束标准化测量——本项目 AI 生成的翻译件/
  判据/SOP 全部适用：**每个 AI 产物应携带"知识生效日"（源发布日+模型日期），供 S3 预检消费**。
  地图现有 effective_from 轴从"规则层"扩展到"AI 产物层"= 状态机升级依据。

**拆分三条件过滤**：独立数据输入（生效日语轴）✓ / 行为差异可回测区分（漂移报告前后对比）✓ /
非纯参数变化（新增哨兵机制）✓ → **立得住，升格为正式场景条款**。

### 其余场景挖掘状态（SOP 纪律：搜不到不硬编）

- S2 evidence 回填：机构对应物=因子生命周期管理（research→verified→production）；
  本班已有活例（RSRS 三窗→STR-VREV-025 evidence 回填），已并入 §2 S2 行；
- S1/S6 挖矿下批（批次边界，寻路 SOP §4）。

## 附录 B：寻路批次 #2——地图方法论本体挖矿（2026-09-14，Owner 澄清后重挖）

> 挖的对象=「这张图该怎么做/还有什么功能/场景集饱和了吗」，非场景内部细节。

### 机构金标准对齐：SR 11-7 模型清单治理（银行界的"模型地图"）

我们的地图本质=**模型清单**（每个节点=一个决策模型：判据+验证状态+实现血统）。
对照 SR 11-7/SR 26-2（[MathWorks](https://www.mathworks.com/discovery/sr11-7.html)、
[ModelOp](https://www.modelop.com/ai-governance/ai-regulations-standards/sr-11-7)、
[SR 26-2 演进](https://www.linkedin.com/pulse/sr-11-7-vs-26-2-evolution-model-risk-management-from-arnab-pandey-qj8ge)）：

| SR 11-7 要求 | 我们已有 | 缺口 |
|---|---|---|
| 全量清单+血统 | ✅ 全量节点+module_ref（null=缺口） | — |
| 验证状态分级 | ✅ 置信度三态（verified/proposed/untested） | ❌ 缺每节点最近验证日期+验证人 |
| 持续监控联动 | ⚠️ decay_watch 存在但未按节点挂钩 | 节点级衰减监控接线 |
| 开发≠验证（独立性） | ⚠️ 红蓝对抗文化存在 | 判据验证须非提出方确认（未成文） |
| 重要性分级（SR 26-2） | ❌ 节点无 materiality 档 | 总闸 L1=高影响应年审；骨架节点按比例 |
| 生命周期文档 | ✅ git 全史+裁定台账 | — |

（缺口三项均已并入 TDM v1.3 施工批，见 §3。）

### 消费场景饱和度检查（新增 S7-S9，合计 9 场景）

S7 退役/衰减、S8 决策回放、S9 转级检查点三条按 D108 三条件过滤全过，已并入 §2 场景表。

### 诚实边界

搜索自证：公开实践里**没有**找到"验证状态直接驱动交易 go/no-go"的成文做法——
我们的"判据即开关"设计（状态矩阵）在公开文献里是超前的；反过来说，无现成模板可抄，
升级只能自研+小步验证。
