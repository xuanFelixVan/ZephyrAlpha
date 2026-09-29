---
ttl: task_bound
title: 骨架定版卷（L00）——F01-F122 完备性复核+候选漏项甄别定版+四方映射缺口+段目录校准+口径漂移钉死
session: zc-l00-20260927
---

# 骨架定版卷（L00·全流通打通战役矿道）

> 真源：环节清单=`docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`（F01-F122/13 段）；
> 候选漏项=`docs/_working/fullflow_mining/00_skeleton/90_crosscheck_link_census.md` §三·E；
> 矿道分工=`docs/_working/fullconnect_campaign/00_orchestration.md` §二。只读复核，零改既有件。

## 一、环节完备性复核（F01-F122 无空洞无重号）

实测命令与读数（`S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md`）：

| 检查 | 命令 | 读数 | 判定 |
|---|---|---|---|
| 总行数 | `grep -c "^| F[0-9]" $S` | **122** | 与册题一致 ✅ |
| 2 位去重 | `grep -o "^| F[0-9]\{2\} " $S \| sort -u \| wc -l` | **99** | F01-F99 全在 ✅ |
| 3 位去重 | `grep -o "^| F[0-9]\{3\} " $S \| sort -u \| wc -l` | **23** | F100-F122 全在 ✅ |
| 空洞扫描 | id 序 `awk` 逐差 | **0 处 GAP**（末=F122） | 无断号 ✅ |
| 重号扫描 | `sort \| uniq -d` | **空** | 无重号 ✅ |

**状态分布（awk 按第 8 列截`（`前基态，41 行带括号注记全部归入基态，无一行落四态之外）**：

| 状态 | 计数 | 成员 |
|---|---|---|
| built | **81** | 其中 12 行带注记：F08（待深挖确认）/F09（M5 补挖）/F11（16 表 vs 13 轴漂移）/F56（SimBridge 取证）/F61（持久化待裁）/F62（零注入 P0 前置）/F68（GPU T1 禁中动）/F88（拦截仅 4 库）/F105（信任绑定待裁）/F106（UNKNOWN 26.9%）/F111（app_panel 退役待裁）/F112（红） |
| partial | **30** | 含 F02/F04（接线空地）、F72（SimBridge 断链嫌疑）、F84/F85/F115（补挖项）、F122（M4/M5 边界）等 |
| design | **5** | F73、F94、F95、F120、F121 |
| missing | **6** | F26（E7 前哨 null）、F30/F31（L9 源线登记态）、F34（汇聚 null）、F51（币圈空壳）、F74（转正汇总器缺位=全链最大单点） |
| 合计 | **122** | 81+30+5+6=122 ✅ |

## 二、候选漏项甄别定版（普查称 29，实数 **30 行**——2+15+13=30，普查 §三·E"29 项"为加总笔误，本卷按 30 行甄别）

三态判据：**并入**=既有 F 环节声明语义已含该对象，落位=册行补真源/锚点（不新增号）；**新增**=无宿主环境，须新号；**Owner 门**=架构取舍未经裁定（裁-6 边界/同物性），且任何定版落笔都打包在**裁-5 改写授权**内。

| # | 对象 | 三态 | 落位/建议 |
|---|---|---|---|
| A-1 | state_matrix（yaml:5556，24 cell=L1×六态挂载，含 pending-owner-adoption 格） | 并入 | **F38**（L1 总闸判定输出之资金姿态细则载体，册行补锚点） |
| A-2 | portfolio_plan（yaml:5639，PP-001 整装组合 11 sleeve，自述"C1/C2 可执行实例"） | 并入 | **F48**（C1 预算切分，册行补锚点） |
| B-1 | REG-TECHNICAL-INDICATOR-001 技术指标册 | 并入 | **F52**（与 REG-DAL-001 同决策算法资产族） |
| B-2 | REG-PAT-001 图表形态册 | 并入 | **F52** |
| B-3 | REG-EXA-001 执行算法册 | 并入 | **F55**（有码无册=出口真源补注） |
| B-4 | REG-SEAT-001 席位册（559 行） | 并入 | **F30**（行情基本面源线族扩员；普查"新增（C 段源线）"收窄为族内成员登记） |
| B-5 | REG-EVT-001 事件日历册（498 行） | 并入 | **F30**（同上） |
| B-6 | REG-MAC-001 宏观指标册 | 并入 | **F38**（宏观传感器补数据线真源） |
| B-7 | REG-FLD-001 字段字典（8280 行，schema v2.0） | **新增** | **F126**（P1，A/K 交界，schema 治理面） |
| B-8 | REG-DATAFLOW-001 数据资产册（15517 行） | 并入 | **F11**（挂轴对象清单，台账与挂轴同面） |
| B-9 | REG-MIGRATION-001 迁移册（276 行） | **新增**（勘误注 2026-09-29：册本体已在 HEAD=`docs/01_policies_and_standards/_registry/catalogs/migration_registry.yaml`，含 13 条 pending 退役议题（F123 卷 §四缺口3，净删=Owner 门）；"新增"指骨架 B 系行项登记+F123 立卡，非新建册文件） | **F123**（**P0**，A 段 F07 邻位，DB schema 迁移通道——F07 只写 depgraph 不含迁移纪律） |
| B-10 | REG-ARCH-ISSUE-001 架构议题册（276 行） | 并入 | **F101**（议题→裁定同链入口补真源；裁定机制 F101 已在） |
| B-11 | REG-INTF-001 接口契约册（physical_path 在 `_archive/`） | 并入 | **F110**（补真源+archive 态注记） |
| B-12 | REG-STATE-VOCAB-001 状态词表册（GATE-VOCAB 实拦无主） | **新增** | **F124**（**P0**，K 段，词表生命周期） |
| B-13 | REG-TASK-META-001 任务卡元数据册（95 行，human_gated） | 并入 | **F83**（自动化班底工作单元 SSoT 补注） |
| B-14 | REG-TEMPLATE/FRONTMATTER/SCRIPT-001·002/CAP 共 5 册 | 并入 | **F117**（文档/脚本/技术栈资产族细化，5 册归并登记） |
| B-15 | REG-CROSS-002／REG-CATALOG-001／REG-SM-001 | 并入 | 拆三：CROSS-002→**F07**（depgraph 即跨模块依赖真源）；CATALOG-001→**F109**（册行已点名 master_index）；SM-001→**F110**（shared/ SSoT 面） |
| D-01 | `alt_data`（28 py） | 并入 | **F31**（另类源线族补代码域锚点，F31 missing 态获实件升级） |
| D-02 | `data_eng`（16 py：data_lake_manager/cold_data_archive_manager 等） | **新增** | **F127**（P1，A 段；与 F08 冷库归档存在冷储交叠=勘误点） |
| D-03 | `data_governance`（21 py） | **新增** | **F125**（**P0**，A/K 交界，数据治理本体） |
| D-04 | `data_security`（10 py：masking/access_auditor） | **新增** | **F128**（P1，K 段；与 F88/F105 异域） |
| D-05 | `market_data`（20 py） | 并入 | **F03/F10**（双真源嫌疑消解+勘误） |
| D-06 | `ml_train`（43 py） | **新增** | **F129**（P1，B/J 交界，训练线；F19 仅基线对台） |
| D-07 | `ml_serve`（11 py：model adapter/compression） | **新增** | **F130**（P1，J 段；与 F89 分界=数值 ML 族 vs LLM 族） |
| D-08 | `nlp`（7 py：news/sentiment） | **新增** | **F131**（P2，C 段，文本情报处理线） |
| D-09 | `intelligence`（89 py） | 并入 | **F96**（胃产物 inbox 域归属勘误） |
| D-10 | `knowledge`（15 py：kb_engine/factor_knowledge_base） | **Owner 门** | 裁-6 边界未定（vs F93 图书馆）；建议候选=F93 扩展，不定号（裁-5 授权下处置） |
| D-11 | `infra_ops`（6 py：loki/storage_cost/wal_monitor） | **新增** | **F132**（P1，I 段，运维工程域） |
| D-12 | `infra_runtime`（9 py：ha_sla/runtime_admission/latency_budget） | **Owner 门** | 裁-6 与 F71 同物性未证；建议候选=F71 子目，不定号 |
| D-13 | `gov_rule`（4 py：constitutional_update/standards_manager） | 并入 | **F101**（规则域代码锚点勘误） |

**定版环节总数 Z = 122 ＋ 新增 10（F123-F132）＝ `132`**（并入 18 行零新号；Owner 门 2 行暂不计号）。
新增序：F123 B-9 迁移(P0/A)｜F124 B-12 状态词表(P0/K)｜F125 data_governance(P0/A·K)｜F126 B-7 字段字典(P1/A·K)｜F127 data_eng(P1/A)｜F128 data_security(P1/K)｜F129 ml_train(P1/B·J)｜F130 ml_serve(P1/J)｜F131 nlp(P2/C)｜F132 infra_ops(P1/I)。编号一律尾插 F123+，保 F01-F122 无空洞不变式。较普查"~151/~140"更紧=18 处机械并入净零收效。**裁-5 提示**：18 处并入+10 新号落笔总册=一次改写授权打包，建议总筹先批本表再动册。

## 三、四方映射缺口表（F 骨架 ↔ TDM 182 ↔ ROOR 77 ↔ src 域 57）

| 方 | 总数 | 骨架无位计数 | 成员与处置 |
|---|---|---|---|
| TDM 节点 | 182（E128/P18/X19/F13/C4） | **0 个节点无 F**（F30-F52 全收）；但 **38 个 module_ref:null 无逐一归属判**（全在 L9，实测名单：A01-A16/B01-B10/C01-C03/G1·G2·G4·G5/V2/AGG/D2/E2/Z1；G3 有码不 null） | P0 待挖面：须生成器出"null 节点→F"映射表逐条判（普查 §六 待挖①），非本轮新号 |
| TDM 结构 | 2（state_matrix:5556、portfolio_plan:5639；edges 254 条已入 §二 DAG） | **2** → 已判 A-1 并入 F38、A-2 并入 F48（见 §二） | 裁-5 打包 |
| ROOR | 77（summary=76，§五-3） | 候选 **15 行/21 册**（12 行并入 18 册+3 册转新环 F123/F124/F126）＋**40 册登记面欠账**（环节在、册内未点 REG 名，如 F64 合写未给 REG 号=机检不可达） | 40 册补注=REG 号批注工单（普查待挖④），不新增环节 |
| src 顶层域 | 57（F 册:12 称 56，§五-4） | 名称未匹配 **17** → 语义已覆盖 4（experiment_tracking→F67、red_blue_validator→F100、signal_quality→F40、strategy_factory→F17/F23）＋真候选 **13**：4 并入（alt_data/market_data/intelligence/gov_rule）＋7 新环（D-02..04·06..08·11）＋2 Owner 门（knowledge/infra_runtime） | 见 §二 |
| 反向（骨架→三方） | 122 | **0**：122 环各有代码/注册表/图锚（K/L/M 段治理横切本就无 TDM 节点对应，属设计内） | — |

## 四、矿道段目录校准表（00_orchestration §二 十二带 ↔ 总册十三段）

带号连续性：12 带区间首尾相接覆盖 F01-F122（12+10+7+7+9+12+12+12+12+12+10+7=122），**无 F 丢失、无跨带重号** ✅。偏差在"带≠段"：

| 矿道 | 段目录 | F 带 | 总册段归属 | 判定 |
|---|---|---|---|---|
| L01 | a_data_foundation | F01-F12 | A 段·数据供给链 F01-F12 | **全等** ✅ |
| L02 | b_factory_inbound | F13-F22 | B 段·策略工厂 F13-F29 前半 | 段内切分 ✅ |
| L03 | c_exam_pipeline | F23-F29 | B 段后半（E4-E9+台账） | 段内切分 ✅；名义"exam"窄于 F24-F29 实体，挖时按总册职责 |
| L04 | d_l9_knowledge | F30-F36 | C 段·知识供给线 F30-F36 | **全等** ✅ |
| L05 | e_decision_chain | F37-F45 | D 段前半（L0-L4+P1-P3+S1） | 段内切分 ✅ |
| L06 | f_exec_risk | F46-F57 | D 段 F46-F52（S2/R1/C1-C3/F51/F52）＋E 段 F53-F57（执行基建） | **跨段**（D+E）⚠️ |
| L07 | g_backtest_gpu | F58-F69 | E 段 F58＋**F 段·风控合规 F59-F63**＋G 段·回测 F64-F69 | **跨段**（E+F+G）⚠️ **最大偏差**：带内 6 环（F58-F63）非回测而是执行成本+风控合规 |
| L08 | h_sched_recovery | F70-F81 | G 段 F70-F71＋**H 段·转正链 F72-F75**＋I 段·调度 F76-F81 | **跨段**（G+H+I）⚠️ 带内 6 环（F70-F75）非调度恢复 |
| L09 | i_ai_ops_gov | F82-F93 | I 段 F82-F85＋J 段·AI 层 F86-F93 | 跨段（I+J），名义兼容 ✅ |
| L10 | j_ai_design_gates | F94-F105 | J 段设计面 F94-F96＋K 段·治理门禁 F97-F105 | 跨段（J+K），名义兼容 ✅ |
| L11 | k_frontend_docs | F106-F115 | **K 段 F106-F110（术语/回滚/门位/注册表族/契约）**＋L 段·前端 F111-F115 | **跨段**（K+L）⚠️ 带内 5 环治理件与"frontend_docs"名义错位 |
| L12 | l_methodology_routing | F116-F122 | M 段·全局横切 F116-F122 | **全等** ✅ |

**校准结论**：全等 3（L01/L04/L12）｜段内切分 3（L02/L03/L05）｜跨段 6（L06-L11）。段目录=并发切工批次，**非语义段真源**；三处名义-内容错位（L07 含风控合规、L08 含转正链、L11 含治理件）派单时各车道主必须按总册段落职责挖，禁按段目录名望文生义。§二新增 10 环落段标注已按总册段体系给出（F127/F129 为跨段交界，归 A/B 主段）。

## 五、四处口径漂移钉死（正数=本次实跑，均复现成立）

| # | 漂移 | 正数（复跑命令） | 过期数位置 |
|---|---|---|---|
| 1 | TDM 节点 138 vs 182 | **182**＝`grep -c "^- node_id:" config/trading_decision_map.yaml` | 138 在 `00_skeleton_fullflow.md:33`、`:146` 与 `09_link_skeletons.md:26`、`:748` 共 4 处 |
| 2 | entry 132 vs 128 | **128**＝`grep -c "^- node_id: TDM-E-" config/trading_decision_map.yaml`（P18/X19/F13/C4 与册吻合；132=128+4 crypto 混计） | 总册 `00_全环节总册.md:73`（实测原文"entry 132/position 18/exit 19/portfolio 13"） |
| 3 | ROOR 76 vs 77 | **77**＝`grep -c "registry_id:" docs/registry_of_registries.yaml`；summary=**76** 在 `registry_of_registries.yaml:881` | 总册 §五.3 自述+普查裁-1（建议 a 刷 summary=77，涉注册表面 Owner 门） |
| 4 | 顶层包 56 vs 57 | **57**＝`find src/zephyr -maxdepth 1 -type d \| grep -v __pycache__ \| tail -n +2 \| wc -l` | 总册 `00_全环节总册.md:12`（"56 包实扫"） |

附带钉死⑤：普查"29 候选"实数 **30 行**（2+15+13），本卷已按 30 行甄别并回写 §二；state_matrix 实为 **24 cell**（普查"82 行"=行距口径 5556→5638），portfolio_plan=PP-001 **11 sleeve**。

## 六、自审闸三态与复跑命令

**自审＝挖干可施工**：§一全数命令实跑（122/99/23/0GAP/0 重号/81-30-5-6）；§二 30 行逐条给证据锚点（21 册 physical_path 逐一验存在；13 域逐一验 py 数）；§三四方计数全实测（38 null 名单机读）；§四逐带比对总册段题；§五四正数复跑。无凭记忆数字。

- **挖干可施工（交总筹）**：§二定版表（Z=132）整体供裁-5 一次授权；40 册 REG 号补注工单；38 null 节点映射表生成器工单。
- **待挖**：38 null 逐条归属判（缺机生映射）；F123-F132 十新环的六向台账卷（本卷只定号定位）。
- **待裁（Owner 门）**：裁-5 改写授权（18 并入+10 新号落册）；裁-6 `knowledge`↔F93、`infra_runtime`↔F71 边界；ROOR summary 76→77 刷新（裁-1 同族）。

复跑（Git Bash，`export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"`）：

```bash
S=docs/_working/fullflow_mining/00_skeleton/00_全环节总册.md
grep -c "^| F[0-9]" $S   # 122
grep -o "^| F[0-9]\{2,3\} " $S | sed 's/[| ]//g' | sort | uniq -d   # 空
grep -o "^| F[0-9]\{2,3\} " $S | sed 's/[| ]//g' | sed 's/F//' | sort -n | awk 'NR==1{p=$1;next}$1!=p+1{print "GAP"p"->"$1}{p=$1}END{print "last="p}'   # last=122 无 GAP
grep "^| F[0-9]" $S | awk -F'|' '{gsub(/ /,"",$8); split($8,a,"（"); print a[1]}' | sort | uniq -c   # built81/partial30/design5/missing6
grep -c "^- node_id:" config/trading_decision_map.yaml   # 182；TDM-E- 128；module_ref: null 38（全 TDM-E-L9）
grep -c "registry_id:" docs/registry_of_registries.yaml  # 77；:881 summary 76
find src/zephyr -maxdepth 1 -type d | grep -v __pycache__ | tail -n +2 | wc -l   # 57
for d in alt_data data_eng data_governance data_security market_data ml_train ml_serve nlp intelligence knowledge infra_ops infra_runtime gov_rule; do [ -d src/zephyr/$d ] && echo "$d OK"; done   # 13 OK
```
