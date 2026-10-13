---
ttl: task_bound
title: D 族资格冻结稿（状态识别/环境族）——段数/边界/特征集/重建规则逐项钉死呈批版
created: '2026-10-12'
session: st-minedig-20261012
family_id: MINEDIG-CAMPAIGN
status: draft_for_ruling
---
> ## 结案报告（2026-10-14 由 st-wkcure-chief-20261013 核验）
> **总结论：未结案（验收四件全绿、§3.1 裁 A 已实测入册，但末改 10-13 01:33 距今不足 7 天稳定窗，且呈批转正/run_id 钉版/安置问题三桩未落——接近结案待成熟）。**
> **✅ 已完成（逐条，每条带可回溯证据）**
> - §5 四件资格判据验收已跑一轮且全绿：证据=本稿 §8 验收回执（挖矿二班 10-13 追加，含重放 1,824 日逐日零不一致/三截断窗逐日全等等具体读数），回执指针件 docs/_working/minedig2_campaign/10_dfamily_qualification_acceptance.md 实测存在（git ls 命中）
> - §3.1"r1/r2 不路由"裁 A 已入册：证据=docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4557-4564 实测命中（裁 A 保持不路由/unrouted 合法态；evidence 与 related_files 双指本稿 §3 及验收件；署名=总统统筹对话面补签 2026-10-13 01:2x，登记执行=st-minedig2-20261012——本班仅核实在册，不复核署名真伪）
> - 后续裁定登记动作在册：证据=commit 7f4a10af2f（挖矿二班裁定入册袋，提交信息自述按硬规则第 8 条走正门补录 2026-10-13 15:4x 统筹三裁）
> - 全稿合规面（零 CH/零卡/零考试/纯追加）：证据=本稿 §7+§8 追加节声明
> **⚠️ 未完成（逐条）**
> - §3.2-3.5 其余四未冻点的逐项裁定入册：现状=本班仅在册面核到 3.1 裁文，其余四条未逐条验证在册命中｜缺口=逐条对 ruling_registry 补核（7f4a10af2f 的"三裁"是否全覆盖未证）
> - 呈批菜单 §6.2"§5 四件判据追认为 D 族通用门槛、本稿转正式"：现状=frontmatter 仍 status: draft_for_ruling（实测未改）｜缺口=Owner 追认+状态转正式
> - ⚑本稿 §8 自记三桩未落件之两项：load_phase_panel 的 run_id 钉版（归统筹/册主）、落台件 ttl 与 5 条 production 考卷消费的 §9.4 安置问题——现状=均未见落地痕迹留本稿｜缺口=他役承接或本稿销账
> - CLOSED 条件③：git log -1 实测末次提交 10-13 01:33，距今不足 7 天零变动
> **对旧章/落码宣称的复核**：无旧结案章；本稿 §8 自记"令卡称 A×5 已入册、本班实测 ruling_registry 零命中"——2026-10-13/14 盘面复核：3.1 裁 A 现已在册（:4557，10-13 补录晚于该实测），该自述缺口的方向已推进，A×5 全量仍待逐条核
> **核验方式**：全文读（含 §8 追加节）；ruling_registry.yaml grep 六段/2026-10-12/minedig 命中行位；minedig2_campaign 目录与 99_delivery 实测；git log/worktree list 查活跃车道（未见 minedig 在途车道，役活跃性不足以判"役内在用"）；HEAD=b05345f8e6
> **证据等级**：A=在册条目与文件状态实测；验收读数本身为 B（回执件未逐字节复跑）
> **处置建议**：留根面（待稳定窗+转正式；残余三桩均具名归属，不催办）

# D 族资格冻结稿（状态识别/环境族）——只起草呈批，不开考

> **令据**：令 A 附录批 3 同包之「D 族资格冻结稿（普查 D 族"先补资格"）」：起草状态识别族的冻结稿——段数/边界/特征集/重建规则（含情绪六段）逐项钉死成可考面；**只起草呈批，不自行开考（判据面等裁）**。
> **普查锚**：[2026-10-12-exam-card-mining-meta-method-research.md](2026-10-12-exam-card-mining-meta-method-research.md) §9 :174（"六段规则未冻结＝无考试资格"）/:185（"适用，先补冻结资格"）。
> **纪律**：本稿为资格面冻结草案（呈批件），非开考令；引用式冻结优先（能指真源就不抄数值，防第二真源，27_five_card_freeze_protocol 精神）；全稿零 CH、零卡、零考试。

## 1. 对象与成员清单（普查 D 族＝状态识别/环境）

| # | 成员 | 段数/边界现状 | 真源锚 | 资格面现状 |
|---|---|---|---|---|
| D1 | **情绪六段**（本稿主对象） | 6 段词表已定稿，判定规则两腿合成，**重建规则半冻结** | `src/zephyr/shared/vocab/market_state.py:66-78`；`config/trading_decision_map.yaml:4474,6454`（v1.2 定稿） | 未冻（§2/§3） |
| D2 | 宏观 regime（HMM 4+3 overlay） | 7 态：r1/r2/r3/r4＋r10 危机/r11 修复/r12 突破 | `src/zephyr/regime/core/regime_detector.py:47-49` | 半冻（HMM 拟合随机性，§3.4） |
| D3 | 锚定风险四档 | r3≤0.30/r2 0.30-0.60/r1 0.60-0.80/r4>0.80（vol_pct 250 日分位，零拟合纯阈值） | `anchored_state_machine.py:36-56`（裁定#229 禁调） | **资格已齐** |
| D4 | 盘中五态→六段映射 | 五态已定，降采样映射一条 proposed | `market_state.py:81-104` | 未冻（§3.2） |
| D5 | 地量档位开关 | 20 日分位十分位＋8000 亿绝对线二值 | `exam_cards/entry_flow/L3/TDM-E-L3-06__calibration__02`（status: examined） | 已考在册 |
| D6 | 流动性五层（成本模型） | ADV 五分位边界已标定冻结 | `cost_model_calibration.py:174-200` | 资格已齐 |
| D7 | 波动率档 | 未立独立档（t0 用三桶 vol 代理） | `archive/2026-10/t0_matrix/LEDGER.md:61` | 缺位（普查已记） |
| D8 | 拥挤度档 | 未见 | 普查 :114 | 缺位（普查已记） |

## 2. 情绪六段逐项钉死（D1 可考面）

### 2.1 段数与段名（冻结，已定稿勿动）

6 段：`投降(冰点) / 蓄势 / 点火 / 主升 / 亢奋 / 退潮(派发)`——真源=`market_state.py:66-78` `EmotionCycleSixVocab`，出处=`trading_decision_map.yaml` state_matrix.states（v1.2 定稿，Owner 裁定"机构命名+修复期独立成段"）。**段名段数本稿零改动**。

### 2.2 边界（两腿合成规则，全部可符号引用）

- **宏观腿映射 R2SIX**（`scripts/backtest/auto_mount.py:135`）：`r10→投降 / r4→蓄势 / r11→蓄势 / r3→主升 / r12→点火`；r1/r2（低/中波震荡）**无六段对应＝不路由**。
- **优先级 PREEMPT**（`auto_mount.py:270-281`）：`宏观极端态(r10/r11) > 退潮 > 亢奋 > 基础映射`——宏观极端不被微观读数覆盖。
- **微观腿阈值**（`auto_mount.py:95-102, 246-268`，纯 trailing 无前视）：
  - 亢奋 = 乖离度(close/MA20−1) 250 日分位 ≥ 0.90 ∧ 20 日上涨家数占比 250 日分位 ≥ 0.85 ∧ 60 日收益 > 0；
  - 退潮 = 亢奋后 60 日记忆窗内破 MA20 ∧ br20 < 0.50。
- **特征集**：宏观腿=HMM 七态 dominant（特征列序真源=MOD-REGIME-002 FEATURE_NAMES）；微观腿=广度帧（399106 广度指数主源＋EQW_ALLA 补位，`auto_mount._breadth_frame`）。

### 2.3 重建规则（幂等性是资格核心）

- **物化通道**：`scripts/audit/t0_six_phase_materialize.py`（1,816 日物化全史在册）——`PHASE_VERSION="sixphase-v1"`（映射变更须升版禁原地改）、`CLOSED_BOOK_CUTOFF="2025-09-09"`、`PHASE_WARMUP_DAYS=700`、`PIT_TAIL_LAG=1`、双写日 fail-closed（`load_phase_panel` 对重不 Duplicate 拒收）。
- **宏观腿 HMM 侧**（有拟合随机性，冻结稿必须钉）：组件数=4；槽位确定性=`anchored_component_order`（主锚 vol 列 0 升序、次锚 slope 列 2，裁定#304 抗 label switching）；训练/重拟合节奏=季度 walk-forward；**run_id 钉法先例**=`regime_recal_protocol_2026_09_17.md` §2（`run_id='VAL-P0-20260916-230726'`）。
- **幂等验收标准（引先例）**：同一码本两次重放 dominant 序列**逐日一致**（`regime_recal_protocol_2026_09_17.md` §5"重放幂等"）——本稿建议将其立为 D 族重建资格的机械判据。
- 六段实测分布（在册 meta）：expansion 388 / distribution 221 / capitulation 202 / accumulation 201 / euphoria 40 / ignition 2 / **unrouted 762 日（41.9%）**。

## 3. 未冻点清单（呈批裁决项，逐项编号）

| # | 未冻点 | 事实 | 裁决选项（建议默认加粗） |
|---|---|---|---|
| 3.1 | **r1/r2 不路由** | 六段不闭仓：1,816 日中 762 日无段（41.9%），fail-closed"宁漏勿误" | **A 保持不路由（unrouted 合法态，卡面 bucket 单列）**；B 补映射（r1→?/r2→? 须 Owner 定名）；C 按六段占比降权 |
| 3.2 | 盘中 EUPHORIC→IGNITION 映射 proposed | `market_state.py:98-104` 自标"待 Owner 校准" | **A 维持 proposed 挂起（本稿不代钉）**；B 批准转正式 |
| 3.3 | **两源分歧 21.09%** | 六段宏观腿 vs 包体宏观腿 dominant 逐日一致率仅 383/1816（`t0_matrix/reconcile_pack_v1_summary.csv`；同名 rN 语义不同） | **A 钉 t0 物化件（sixphase-v1）为六段唯一重建真源，包体口径另轴并存禁混用**；B 先做语义对账再定 |
| 3.4 | HMM label switching 残余 | anchored 重排已落地（裁定#304），但跨 run 漂移无逐日验收在册 | **A 按 recal 协议补"重放幂等"验收入资格面**；B 维持现状 |
| 3.5 | 微观腿广度源断供 | 399106 有断更死日成例（补洞=dd04d9d20c） | **A 维持 EQW_ALLA 补位规则并在卡面披露**；B 另选主源 |

## 4. 其余成员资格判定一句话

D3 锚定四档（阈值裁定#229 在册，零拟合）＝**资格已齐，可直接作考试条件轴**；D5 地量卡已考在册；D6 流动性五层成本标定冻结在册；D7 波动率档、D8 拥挤度档＝缺位，按普查记录留待后续矿脉（本稿不代建）。

## 5. "补齐资格"的机械定义（何谓冻结完成）

D1 情绪六段获得考试资格 ⇔ 以下四件全绿：
1. **段定义冻结**：词表+R2SIX+PREEMPT+微观阈值以 `sixphase-v1` 版本号整体引用（升版=新资格，禁原地改）；
2. **重建幂等**：同一码本两次重放 dominant 序列逐日一致（§2.3 判据）；
3. **PIT 无前视**：trailing 窗+CLOSED_BOOK_CUTOFF+PIT_TAIL_LAG 三件在册且被物化件执行；
4. **逐日落台可读**：六段序列以逐日快照表可查（解锁 `TDM-E-L1__ablation__02` 的 blocked_reason(1) 与 TDM:5939 红节点的前提）。

## 6. 呈批菜单（Owner 门位，建议默认已标注）

1. §3.1-3.3 三大未冻点逐项裁决（建议默认 A/A/A）；
2. §5 四件资格判据是否追认为 D 族通用门槛（建议：追认，写回本稿转正式）；
3. 冻结稿批准后：六段重建资格验收跑一轮（重放幂等+落台核查，跑数前本稿经网关 commit，跑数后只允许执行判据不允许改判据——regime_recal 协议 §0 纪律）；
4. D7/D8 缺位档是否立项（普查矿脉清单已有位，本稿不催）。

## 7. compliance

零 CH ｜ 零新卡 ｜ 零考试 ｜ 零注册表改动 ｜ 本稿 files_created=1 ｜ 判据面等裁（G4-5：批准前无人可挪门柱）

## 8. 验收回执（2026-10-13 挖矿二班追加，§1–§7 原文字节零改动）

按收尾令 §二.2，本班以本稿 **§5 四件判据原文**跑了一轮资格验收，四件全绿；逐件读数、正对照（能红证明）、
码本面普查与两条结构性风险登记在
**[10_dfamily_qualification_acceptance.md](10_dfamily_qualification_acceptance.md)**，本处只落三条结论性指针：

1. **§5.2 重建幂等＝绿**：官方物化通道两次独立进程重放，1,824 日 `dominant` 与 `six_phase` **逐日零不一致**
   （产物逐字节相同）；与 dev 已落地那份 1,816 日重叠段亦零不一致，差 8 个尾日＝只追加不改史；
   正对照＝改 `--start` 出行数变化（1,395），排除"读缓存冒充重放"。
2. **§5.3 PIT 无前视＝绿**（新增机械证据，非注释背书）：把装载窗口截到 2023-12-31／2024-12-31／2025-09-09 三点，
   历史标签与全窗口**逐日全等（差异 0）**；PIT_TAIL_LAG=1 实测切掉表内尾日 2026-10-12 ⇒ 面板止 2026-10-09。
3. **§5.4 落台可读＝绿，但只解他人卡的三面之一**：`TDM-E-L1__ablation__02` 的 `blocked_reason` 有 (1)(2)(3) 三面，
   本轮只测清 (1)（且为 CSV 面非该卡原指 CH 表面），(2) 逐 sleeve 日频权重帧、(3) 消融侧 activation 注入器
   本班零触碰 ⇒ **该卡保持 `blocked_on_data`，本班不转不改**。

⚑ 本班**未做**且归统筹/册主的三件：五未冻点的裁定入册（令卡称 A×5 已入册，本班实测 ruling_registry 内
`2026-10-12` 零命中，正对照为裁定#229/#304/#325/#501/#502 五条各命中 1——尺在岗；本班按 §3 建议默认 A×5 执行，
因该组默认下 §5 判据文字与本班动作一字不改，本班不自代 Owner 署名）；
`load_phase_panel` 的 run_id 钉版（今日幂等靠"全表同日 dominant 零分歧＋分歧即 RuntimeError fail-closed"两防线）；
落台件住在 `docs/_working/`（ttl task_bound）而被 5 条 production 考卷消费的 §9.4 安置问题。

本追加节合规：纯追加零删除（本稿 `## ` 节数 7→8）｜零判据改动零阈值改动｜跑数后只执行不改｜
CH 腿全在 01:00–04:00 让路窗外（首跑 00:05，末腿 00:14 前）｜N 账本零写（资格验收非考试）。

