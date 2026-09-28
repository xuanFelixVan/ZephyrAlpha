---
ttl: task_bound
volume: 03_tdm_null_node_attribution
session: st-ailayer-final-20260924
creation_token: fullflow-p0-tdm-null-attribution-20260926
---

# 03 · TDM 38 个 `module_ref: null` 节点归属册（P0④ 二验＝**证伪，不成立**）

> 本册是**判定册**不是环节册（对账表 N-1 行判"不成立"）：上棒 P0 第四项"38 个 `module_ref:null` 节点无环节归属"经二验被推翻——**38 个节点的环节归属在 F 册 F30–F36 行原文里已逐段点名**。
> 真缺的是**节点级 `module_ref` 代码锚**（TDM 内部的"节点→模块"指针），属地图册内部登记面欠账，**不是 122 环节集合的漏项**。

## 一、定义与边界（本册判定的对象）

- **判什么**：①38 个 null 节点是否"无环节归属"（上棒命题）；②若是登记面欠账，缺的具体是哪一层（节点→代码模块 vs 节点→环节）。
- **不判什么**：不判 null 节点该不该建码（那是 F30/F31 标 `missing（登记态）` 的施工问题，本册不重挖）。

## 二、六向台账（取证面）

| 向 | 实测证据 |
|---|---|
| 上游输入 | `config/trading_decision_map.yaml` 顶层 `nodes:` @`:26`（区间 26–5271）；`grep -c "^- node_id:"`＝**182**、`module_ref:`＝**182**、`module_ref: null`＝**38**（上棒三数全部复现 ✅） |
| 下游消费 | `module_ref` 字段的读取方实测 8 件：`src/zephyr/autonomy_core/self_evolution_fidelity_gate.py`、`frontend/dashboard/api_server.py`、`frontend/dashboard/web/features/tdm.js`、`features/factory/factory.js`、`pages/factory.html`、`gov_enforcement/commit_gates/algo_note_sync_gate.py`、`infrastructure/rollback/submodule_sync.py`、`intelligence/chain_impact_resolver.py` ＝ null 会让前端 TDM 视图与 fidelity gate 读到空指针（这是"为什么要修"的真实消费端） |
| 自动化触发 | 被动（读图即触发）；`algo_note_sync_gate.py` 在提交链上消费 `module_ref` |
| 真源与注册表 | 节点真源＝TDM yaml；环节真源＝`00_全环节总册.md:65-71`（F30–F36 行，**原文逐段列出 null 节点的 id 区间**，见 §三） |
| 门禁与质量尺 | 实测缺口：**无任何门校验 `module_ref` 非空或指向存在的模块**（`gate_registry.yaml` 对 node/depgraph 只有 `check_doc_node_id_hardcode.py`（:93，反硬编码方向）与 `DEPGRAPH-FRESHNESS`（:941））＝登记态节点长期无对账压力，正是上棒"四次漂移"的同族病灶 |
| 当前运行状态 | **黄**：38 节点全部 `TDM-E-L9-*`（C 段源线/图谱/知识汇聚族），F 册对这些环节的 build_status 自标 `missing（登记态为主）`（F30）、`missing（登记态）`（F31）、`partial（G3 有码，余登记态）`（F32）、`partial`（F33/F35/F36）、`missing`（F34）＝**F 册作者对 null 是知情的**，非"无归属" |

## 三、38 节点逐条归属表（**本册主产物**，全量，非抽样）

null 节点实测 id 清单（38，`awk '/^- node_id:/{id=$3} /module_ref: null/{print id}'` 导出）：
`A01–A16`（16）、`B01–B10`（10）、`C01–C03`（3）、`G1/G2/G4/G5`（4）、`V2`（1）、`AGG`（1）、`D2`（1）、`E2`（1）、`Z1`（1）＝16+10+3+4+1+1+1+1+1＝**38 ✅**（自校闭合）

| 节点 id | 节点名（`name_zh` 实测导出） | 归属环节（F 册原文区间） | F 册行锚 | 判定 |
|---|---|---|---|---|
| TDM-E-L9-A01 | 源线·日线/分钟行情 | **F30** L9 源线·行情基本面族（原文 `TDM-E-L9-A01..A16`） | `:65` | 有归属 |
| A02 | 源线·Tick分笔 | F30 | `:65` | 有归属 |
| A03 | 源线·板块/概念指数 | F30 | `:65` | 有归属 |
| A04 | 源线·估值 | F30 | `:65` | 有归属 |
| A05 | 源线·财务 | F30 | `:65` | 有归属 |
| A06 | 源线·资金流 | F30 | `:65` | 有归属 |
| A07 | 源线·千股千评 | F30 | `:65` | 有归属 |
| A08 | 源线·航运运价BDI | F30（区间内）；语义更近 F31 另类族 | `:65/:66` | 有归属（建议 F 册校准区间边界） |
| A09 | 源线·财经快讯情绪 | F30（区间内）；语义近 F31/D-8 文本线 | `:65` | 有归属（同上） |
| A10 | 源线·国际宏观 | F30（区间内）；语义近 B-6 宏观数据线 | `:65` | 有归属 |
| A11 | 源线·能源库存 | F30（区间内） | `:65` | 有归属 |
| A12 | 源线·天气 | F30 区间内，与 F31「卫星/天气…」重复点名 | `:65/:66` | 有归属（**F 册两处重复，须裁一处**） |
| A13 | 源线·股东户数 | F30 | `:65` | 有归属 |
| A14 | 源线·互动易问答 | F30 | `:65` | 有归属 |
| A15 | 源线·加密永续/费率 | F30 区间内；加密另有 F51（TDM-C-* 实例） | `:65/:91` | 有归属（跨实例口径须注明） |
| A16 | 源线·投入产出 | F30 区间内；与 F32「投入产出传导 G5」交叉 | `:65/:67` | 有归属 |
| B01 | 源线·卫星影像 | **F31** L9 源线·另类数据族（原文 `TDM-E-L9-B01..B10、C01..C03`） | `:66` | 有归属 |
| B02 | 源线·美国官方天气/海洋 | F31 | `:66` | 有归属 |
| B03 | 源线·招聘JD | F31 | `:66` | 有归属 |
| B04 | 源线·电商价格 | F31 | `:66` | 有归属 |
| B05 | 源线·招投标 | F31 | `:66` | 有归属 |
| B06 | 源线·社媒舆情X/Reddit | F31；与 D-8 `nlp` 文本线（`sentiment_pipeline.py`）交叠 | `:66` | 有归属（下游加工线＝新增环节候选，见对账表 D-8） |
| B07 | 源线·雪球/股吧散户情绪 | F31 | `:66` | 有归属 |
| B08 | 源线·APP榜单 | F31 | `:66` | 有归属 |
| B09 | 源线·进出口贸易 | F31 | `:66` | 有归属 |
| B10 | 源线·信用卡/支付消费 | F31 | `:66` | 有归属 |
| C01 | 源线·实时门店客流 | F31（原文含 C01..C03） | `:66` | 有归属 |
| C02 | 源线·银行网点/信贷活跃 | F31 | `:66` | 有归属 |
| C03 | 源线·直播电商实时成交 | F31 | `:66` | 有归属 |
| G1 | 图谱·Zephyr产业链 | **F32** L9 图谱谱系（原文 `TDM-E-L9-G1..G5`） | `:67` | 有归属 |
| G2 | 图谱·ChainKnowledgeGraph事实层 | F32 | `:67` | 有归属 |
| G4 | 图谱·概念/题材 | F32 | `:67` | 有归属 |
| G5 | 图谱·投入产出传导 | F32 | `:67` | 有归属 |
| V2 | 状态变量快照·情绪 | **F33** L9 状态变量快照（原文 `TDM-E-L9-V1..V3`）；情绪快照同时是 L02 情绪链路上棒所称"环节内缺口" | `:68` | 有归属（情绪独立状态变量的**升级**另属待追认，见 §四 堵点 3） |
| AGG | 知识供给汇聚 | **F34** L9 知识供给汇聚（原文 `TDM-E-L9-AGG（module_ref=null）`——**F 册自己就把 null 写在真源字段里**） | `:69` | 有归属 |
| D2 | 决策假设·登记与考试方案 | **F35** L9 决策假设与一问一考（原文 `TDM-E-L9-D1/D2/E1/E2`） | `:70` | 有归属 |
| E2 | 验证·结论回传与修正 | F35 | `:70` | 有归属 |
| Z1 | 治理·问题治理与状态机 | **F36** L9 治理横切（原文 `TDM-E-L9-Z1/Z2`） | `:71` | 有归属（F36 与 `REG-ARCH-ISSUE-001` 的对象关系仍未判＝对账表 B-10 证据不足） |

**结论**：38/38 均可落到 F30–F36，**0 个环节级漏项**；上棒"剩 31 处未判"的说法源于只查 F 册是否出现该节点**全名 id 字符串**（实测 F 册只字面出现 8 个 L9 id），未读 F30–F36 的**区间式**写法（`A01..A16`、`B01..B10、C01..C03`、`G1..G5`、`V1..V3`、`D1/D2/E1/E2`、`Z1/Z2`、`AGG`）——**机械字符串匹配遇上区间写法＝假漏项**，这是本车道新发现的方法论病灶（V-10）。

## 四、堵点与病灶

| # | 现象 | 根因 | 修法草案 | 工作量 | 本车道可修 |
|---|---|---|---|---|---|
| 1 | 38 节点 `module_ref` 为空 → 前端 TDM 视图/`self_evolution_fidelity_gate`/`algo_note_sync_gate` 读到空指针 | F30/F31 标 `missing（登记态）`＝节点先登记、代码后建；无门校验非空 | 分两类处置：已建模块的节点→回填 module_ref（可由生成器从 depgraph 反查）；真未建→保留 null 但需在 F 册行有"待建"标注 | 1 施工袋（生成器，下一波） | 否 |
| 2 | **F 册区间写法与机检不兼容**（上棒因此造假漏项） | 环节真源册为散文表格，无"节点→环节"机生映射 | 出一张机生 `node_id ↔ F号` 映射 yaml（对账表 §五-1 生成器四表之一），F 册改为引用 | 1 施工袋 | 否 |
| 3 | V2 情绪快照同时背负"L02 大盘情绪已定桩独立状态变量"的上棒在途定桩 | 双编号体系未收敛 | 已在 `pending_rulings.md` P-6 登记（不在此裁） | — | 否 |
| 4 | F30 与 F31 对"天气"重复点名（A12 与 F31 描述），A08/A09/A10/A15 按区间落 F30 但语义落 F31 | 区间式归属与语义式归属边界未定义 | F 册 owner 校准区间边界 | 小 | 否 |

## 五、内收与合并机会

- 本册**不新增环节**，因此对终数贡献 0；上棒若按"38 个 null 节点＝漏项面"扩表，会造出最多 38 条假环节（若按其"~151"方案还额外推高 1）。
- "节点→环节映射表"与对账表 §五-1 提议的生成器四张对账表（F↔TDM／F↔ROOR／F↔src 域／F↔能力卡）**同施工袋**（同真源可派生→必并），勿另开工单。

## 六、自审闸三态

**挖干可施工**（六向全有实测锚点；38 行归属表为全量非抽样，并给行数自校 16+10+3+4+1+1+1+1+1＝38）。
派单方向＝§四 堵点 1/2 的施工袋（生成器＋回填），**本车道零施工**。
**待裁**：P-6（V2 情绪快照与 L02 情绪状态变量的层级关系）。

## 七、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python --version
T=config/trading_decision_map.yaml; S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
# 1 基数复现（预期 182 / 182 / 38）
grep -c "^- node_id:" $T; grep -c "module_ref:" $T; grep -c "module_ref: null" $T
# 2 38 节点全量 id＋名（预期与 §三 表逐条一致）
awk '/^- node_id:/{id=$3} /^  name_zh:/{n=$0} /module_ref: null/{if(id!=""&&s[id]==0){gsub(/^  name_zh: */,"",n);print id"="n;s[id]=1}}' $T
# 3 分组自校（预期 16/10/3/4/1/1/1/1/1）
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' $T | grep -c "TDM-E-L9-A"
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' $T | grep -c "TDM-E-L9-B"
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' $T | grep -c "TDM-E-L9-C"
awk '/^- node_id:/{id=$3} /module_ref: null/{print id}' $T | grep -c "TDM-E-L9-G"
# 4 F 册区间写法（证伪关键：F30–F36 行原文含节点区间）
sed -n '65,71p' $S | cut -c1-200
# 5 字面匹配为何会假报（预期只 8 个 L9 id 命中，说明上棒用的就是字符串全名匹配）
grep -o "TDM-E-L9-[A-Z0-9]*" $S | sort -u | tr '\n' ' '; echo
# 6 module_ref 消费方（预期 8 件）
grep -rln "module_ref" src/zephyr scripts | grep -v __pycache__ | head -8
# 7 无门校验 null（预期：只有 node_id 硬编码门与 DEPGRAPH-FRESHNESS）
grep -n -i "module_ref" docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | head -3   # 预期 0 命中
```
