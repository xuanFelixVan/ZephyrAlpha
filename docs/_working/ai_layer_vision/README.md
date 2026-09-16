---
ttl: task_bound
title: AI 层进化引擎——骨架总览与挖矿导航
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: active
---

# AI 层进化引擎——骨架总览与挖矿导航

> **一句话**：本目录是第三层（AI 层）的骨架工地。验证挖矿（V0/V1/V2 三份报告）与七段逐段
> 深挖全部完成：L1-L7 段卡+OBJ_M/T/S/R 四条对象线均 **design_done**（各 DESIGN.md 为真源）。
> 主文档=[ai_layer_vision_and_roadmap_v1.md](ai_layer_vision_and_roadmap_v1.md)
> （v2.0 active，定调十三条，Owner 2026-09-17 夜全批；文件名沿用 v1 防断链）。

## 0. 验证结论速览（详见三份 V 报告）

| 验证项 | 结论 | 一句话依据 |
|--------|------|-----------|
| V0 大层定义（不犯错/赚钱/进化） | ✅ 站得住，两条精化 | 治理/业务=IIA 三线模型的一线与二三线合并；AI 层=进化=业界前沿同名能力（AlphaEvolve/DGM） |
| V1 三层划分 | ✅ 站得住，一条定位精化 | AI 层=平台型横切引擎（组织独立、运行时咬合）=把 MLOps Level 2 的自动化对象从模型扩到整个系统 |
| V2 六段完备性 | ✅ 已升级**六段→七段一常数**（Owner 夜批采纳） | 搜索→感知（外扫+内监）、新增传承段（回流闭环）、新增目标常数（"更好"的真源不参与自迭代） |

## 1. 进化循环骨架（七段一常数，Owner 2026-09-17 夜批定稿）

```
                    ┌─────────────────────────────────────────────┐
                    │  目标（常数段）："更好"的真源——预注册判据/Owner 口味   │
                    │  不参与自迭代（根约束，防 objective hacking）          │
                    └───────────────────┬─────────────────────────┘
                                        ↓ 定调
  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
  │ L1 感知  │ → │ L2 收集  │ → │ L3 清洗  │ → │ L4 对比  │ → │ L5 排产  │ → │ L6 切换  │
  │ 外扫+内监 │   │ 原材料库 │   │ 强模型洗 │   │ 定优劣   │   │ 门闸开施工│   │ A/B 蓝绿 │
  └────┬────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘   └────┬────┘
       ↑                                                                      │
       │              ┌────────────────────────────────────────┐              │
       └────────────── │ L7 传承（回流）：坑集/模式库/精英档案/判据档案 │ ←────────────┘
                       │ 喂回感知与收集——闭环的关键边                  │
                       └────────────────────────────────────────┘
```

- **L1 感知**（原"搜索"扩为双向）：外部扫描（论文/开源/机制，从大到小先骨架后模块）+ 内部监测
  （性能衰减/regime 变化/成本异常，触发再搜索）。证据：MAPE-K Monitor 循环起点 + MLOps CT drift 触发器。
- **L2 收集**：原材料库分库分表，生熟分离；多样性保底=MAP-Elites 分格保优蓝本。
- **L3 清洗**：强模型（API）执行，本地优先-API 分界；外部代码零执行。
- **L4 对比**：与现状基准实打实比，产出"好在哪"证据；评估者独立于施工者。
- **L5 排产**：门闸条件触发进施工排班表（区域成熟度/配额/算力窗口）。
- **L6 切换**：A/B 蓝绿=champion/challenger（业界标准名）；A 退役不删观察期。
- **L7 传承**（增补提案）：切完不断环——经验回写喂下一代，防每代重踩。

## 1.5 三轴定位：引擎 × 对象 × 运营（2026-09-17 三轮增补，回答"AI 管AI/AI 升级AI 放哪"）

七段循环只是骨架的一条轴。全骨架=三轴一具：

- **引擎轴（怎么进化）**：七段一常数循环——骨架主体（§1），全项目唯一，不另起炉灶。
- **对象轴（进化什么）**：四个对象家族走**同一条**七段循环，各有各的考尺：

| 对象家族 | 例 | 考尺（怎么证明 B>A） | 卡 |
|---------|-----|---------------------|-----|
| 代码/模块 | 模块/算法/门禁参数 | tests+gates+回归+双窗实测（C4 已有） | V0-V2 主对象 |
| **模型** | API 模型/本地模型（全网搜最便宜渠道+活动/免费窗） | 能力考试+同任务双跑+成本审计 | OBJ_M |
| **工具** | AI 的手（执行/修改/删除）/眼（搜索/观测）/脚（浏览器/MCP） | 基准任务成功率实测 | OBJ_T |
| 规则/判据 | 规则 YAML/阈值/rubric/考纲 | 触发率/误报率/重考历史/退役审计 | **OBJ_R**（2026-09-17 四轮新增） |

- **运营轴（谁来跑）**："AI 管 AI"=引擎的运营编制——总包/分包/纠察/维护班+配额池
  （主文档 §二/§三），是轴不是段，不另设骨架文件夹。

一句话：**AI 升级 AI=对象轴的模型家族+工具家族（OBJ_M/OBJ_T）；AI 管 AI=运营轴；两者都进
骨架，但都不是第八段**。配套红线与自由域=OBJ_S（最大自由原则/删除分级/付费独占）；
AI 层自己的尺子升级=OBJ_R（标准与规则线）。

## 1.6 与业务层骨架并轨（2026-09-17 四轮对齐，Owner 转达业务层讨论+双向裁定）

业务层骨架（docs/_working/automation/，commit 2a11b881）定案"四轴+底板"并已封顶。
与本骨架对齐结论：

- **框架互认**：业务层四轴（决策权/时间节拍/产线工段/生命周期）+治理底板；AI 层三轴
  （引擎/对象/运营）+**同一块**治理底板（标准库+红线库版本化，两层共用一块，不是两块）。
  两边同步封顶，不再加轴。
- **骨锁肉动双向适用**：业务层骨=TDM 五层+四节拍锁死；AI 层骨=七段循环+三轴结构+根约束
  清单锁死（定调 #8/#9）；两层的"肉"各自走流水线自动养。结构上同构，互为印证。
- **标准库归属（客观裁定）**：AI 层的尺子（考纲/阈值/rubric/红线）=**治理层资产**，AI 层
  只有使用权+提案权——运动员不持尺。升级流水线四步=AI 提案→治理立案→Owner 修标→
  **重考历史**（新尺对历史提交集重放，排序不变才准换）→ OBJ_R 卡。
- **排班表归属裁定（2026-09-17 夜 Owner 确认）**：**全项目一张真源**（资源画像注册表+周历+
  冲突闸）不变，**禁止各建各表**；三段归属=①**规则与裁决**（schema/闸规则/策略批准）→
  治理层资产+Owner 门；②**自动化运营**（登记服务运行/生成器/采样器/告警值守/健康维护/
  策略建议器 v2）→ **AI 层运营轴**（与 belt_daemon 同类：AI 层养机器；闸机检裁决+策略归
  治理=AI 层无自我插队空间）；③**使用**=两层客户自助登记（业务层③上架流水线的"自动排班"
  =调 AI 层运营的登记接口，不自建排班逻辑）。过渡零搬家：现有件原地保留，仅值守责任归口
  AI 层运营轴。
- **迁移清单（业务层→AI 层，客观筛过）**：①标准库四步流水线→OBJ_R；②事故案例库→L7
  传承（业务层事故与 AI 层缺陷模式互喂，首案=2026-09-17 pathspec bug）；③too-good-to-be-true
  三查→L4 对比段（进化候选好得反常=查泄漏/查钻营/查运气）；④生命周期轴→AI 层资产同走
  （gate/SOP/模型路由/工具条目都有生老死复活，gate 退役审计已有）；⑤月度体检→L1 内监
  慢周期（AI 层骨架月度建议书，血肉级自动/骨架级 Owner）；⑥灰度="warn 先行→阻断"成文
  （EXEMPT-ZONE-FM 从 post-commit warn 升 pre-commit 阻断即现成先例）。
- **不迁移项（客观）**：⑨骨架体检的执行归业务层（AI 层只认领排班策略建议器 v2）；
  整装 A/B/C 联赛+模拟盘分仓=业务层资产（本骨架 L6 只管 AI 层自己的对象）；
  实盘红线分级=业务层执行+治理层资产，AI 层不碰。

## 2. 目录结构与状态

| 路径 | 内容 | 状态 |
|------|------|------|
| `ai_layer_vision_and_roadmap_v1.md` | 主文档（v2.0：定调十三条+七段一常数+三轴一具+排班归属；文件名沿用 v1 防断链） | v2.0 active（Owner 2026-09-17 夜全批） |
| `V0_layer_definition/` | 挖矿① 大层定义验证报告 | ✅ done |
| `V1_three_layer_split/` | 挖矿② 三层划分验证报告 | ✅ done |
| `V2_evolution_loop/` | 挖矿③ 六段完备性→七段一常数提案 | ✅ done |
| `L1_perceive/` | 感知段骨架卡 | design_done（DESIGN.md 真源） |
| `L2_intake_library/` | 收集段骨架卡 | design_done（DESIGN.md 真源） |
| `L3_cleaning/` | 清洗段骨架卡 | design_done（DESIGN.md 真源） |
| `L4_compare/` | 对比段骨架卡 | design_done（DESIGN.md 真源） |
| `L5_schedule_gate/` | 排产段骨架卡 | design_done（DESIGN.md 真源） |
| `L6_ab_switch/` | 切换段骨架卡 | design_done（DESIGN.md 真源） |
| `L7_heredity/` | 传承段骨架卡（增补段） | design_done（DESIGN.md 真源） |
| `OBJ_M_models/` | 模型对象线（API+本地模型升级/考试/切换/预算分析） | design_done（DESIGN.md 真源） |
| `OBJ_T_tools/` | 工具对象线（AI 的手眼脚升级） | design_done（DESIGN.md 真源） |
| `OBJ_S_perimeter/` | 红线与自由域（最大自由原则/删除分级/付费独占） | design_done（DESIGN.md 真源） |
| `OBJ_R_rules_standards/` | 标准与规则线（AI 层尺子升级流水线：提案→立案→修标→重考历史） | design_done（DESIGN.md 真源） |

## 3. 真源登记与净零批次（红蓝 R1-F1/F2/F5 收敛，2026-09-17）

红队 R1 指认：各 DESIGN 新提议的 YAML 真源未挂 ROOR、未声明净零。统一裁定：**施工开单前
必须完成 ROOR 挂接登记+净零声明**（宪法 §4 净零纪律）。批次清单：

| 新真源 | ROOR 挂接 | 净零声明（替代/吸收什么） |
|--------|-----------|-------------------------|
| config/ai_source_registry.yaml（L1） | 数据源族 | 吸收各班散落搜索源笔记+2026-09-13 甄别轮清单 |
| L4 comparison_policy.yaml | 治理族 | 吸收各稿分散显著性判据口述 |
| L5 evolution_schedule_seeds.yaml | 排班族（resource_profile_registry 生成器新源 I7） | 吸收进化任务散落排班需求（不建第二张排班表） |
| L6 switch_criteria.yaml | 治理族 | 主文档 §五 判据的工程化（同一真源非新增） |
| L7 heritage_policy.yaml | 治理族 | 吸收记忆目录坑集的机读化（人读副本保留不删） |
| OBJ_M model_intel_sources / model_scoring_policy / dual_run_criteria / model_routing_policy | 模型族 | 吸收挖矿 SOP 模型分派二维法（升级为数据驱动）+计费线口头约定成文 |
| OBJ_T tool_inventory / tool_exam_policy / tool_model_pairing_policy | 工具族 | 吸收 capability_cards 静态盘点（生成器替代手维护） |
| OBJ_S obj_s_degradation.yaml | 治理族 | 吸收 resource_optimization.yaml 阈值先例的降档语义（不重复建阈值） |
| config/cleaning_policy.yaml（L3 C1） | 治理族 | 吸收各稿分散的清洗策略常数（R8-B 补登） |
| config/schedule_gate_policy.yaml（L5 C1） | 排班族 | 吸收成熟度门闸与配额四读数阈值（R8-B 补登；唯一 OBJ_R 管辖常量件） |

**裁定登记前置（T3 双前置，红蓝 R2 改判）**：L1 施工项 7（外扫节拍宿主）开工前，"外扫=日历
节拍+E0 实闸"属放宽宪法 §9.3 射程的 T3 语义级解释，按 OBJ_R"放松永不自动"自律须 **Owner 追认+
裁定登记双前置**（追认后按 RULE-RULING 原子补进 ruling_registry，详见 L1 DESIGN 修复注记）；
双前置齐前施工项 7 禁开工，其余施工项不受阻。
**宪法挂接批次**：.runtime/ai_layer/perceive/search_orders/ 与 .runtime/ai_intake/ 两新路径
按 .runtime/strategy_pipeline 先例镜像，列入下次宪法等长替换批次（§9.4 落点枚举增补）。
**数值类待 Owner 项追认**：OBJ_R #1/#3/#4、L4 #1、L5 #1、OBJ_S #1 等数值初值按 Owner 夜批
授权追认提案原值生效（红蓝 R2 复核）；治理立案类（OBJ_R #2/#5/#6、L4 gate 立案、L5 白名单
等）保留待治理流程，不越权。逐条全量对账见 §3.5 处置总表。

## 3.5 待 Owner 项处置总表（红蓝 R1 修复新增，2026-09-17）

> 全目录 10 份稿件 DESIGN.md"待 Owner"节汇总对账：**31 项**（红队 B 计数核验一致）。
> 三态处置：**已销**=Owner 2026-09-17 夜批授权下自裁追认（红蓝 R2 复核，§3 既有记录的全量
> 展开）；**治理立案保留**=真需 OBJ_R 四步流水线/治理流程，不越权；**真待 Owner**=唯 Owner
> 可解（资金/门位/跨稿契约/主文档附录级变更）。

### 已销项（16 项，夜批自裁追认）

| 编号 | 稿件 | 事项 | 处置 |
|------|------|------|------|
| OBJ_R-#1 | OBJ_R_rules_standards | 重放通过判据数值预注册（P1 放走=0/P2 ≤2%/P3 Jaccard 0.98·0.95） | 按提案原值追认生效；首轮数据后走 OBJ_R 提案修订 |
| OBJ_R-#3 | OBJ_R_rules_standards | 重放 summary promote 落点目录 | 自裁 `docs/_working/ai_layer_vision/OBJ_R_rules_standards/replays/`（ttl task_bound） |
| OBJ_R-#4 | OBJ_R_rules_standards | 首案 CASE-2026-0917-001 死因细节补登 | 按本卡记录登记销项 |
| OBJ_R-#7 | OBJ_R_rules_standards | creation_token 补登 | 主会话 wave1 ceremony 已登记（capability ai_layer_vision） |
| L2-#1 | L2_intake_library | 机制族 8 族词表+48 格初始网格（6 域×8 族） | 自裁生效追认；Owner 口味修正走字典数据（数据操作非结构变更） |
| L3-#1 | L3_cleaning | 清洗考尺初值（cleaning_policy.yaml 全部常数） | 按提案原值追认生效 |
| L3-#2 | L3_cleaning | creation_token 补登 | 夜批追认补登（token ×5 之一） |
| L4-#1 | L4_compare | 判据常量初值（触发线 G1-G5/α/效应量门槛/锦标赛 K） | 按提案原值追认生效 |
| L4-#4 | L4_compare | creation_token 补登 | 同上（token ×5 之二） |
| L5-#1 | L5_schedule_gate | policy 常量初值（M1-M4/分桶线/降级线/配额上限） | 按提案原值追认生效 |
| L5-#4 | L5_schedule_gate | creation_token 补登 | 同上（token ×5 之三） |
| L6-#1 | L6_ab_switch | 观察期数值门槛（min_months/T2 分歧率 5%/T3 +20%/T4 +15%） | 按提案原值追认生效；首轮数据后 OBJ_R 修订 |
| L6-#3 | L6_ab_switch | CREATE-GUARD creation_token 补登 | 同上（token ×5 之四） |
| L7-#1 | L7_heredity | heritage_policy 数值初值（遗忘/防近亲繁殖参数） | 按提案原值追认生效 |
| L7-#3 | L7_heredity | creation_token 补登 | 同上（token ×5 之五） |
| OBJ_S-#1 | OBJ_S_perimeter | 双指标软/硬线数值（金额+回撤百分比） | 按提案原值追认生效；OBJ_M 首月数据后 OBJ_R 定标 |

### 治理立案保留（9 项，真需流程）

| 编号 | 稿件 | 事项 | 去向 |
|------|------|------|------|
| OBJ_R-#2 | OBJ_R_rules_standards | 评分裁定追认（Jaccard 主判据/Kendall tau 否决理由） | 治理立案 |
| OBJ_R-#5 | OBJ_R_rules_standards | S3 阈值外置化是否立案（触及 gate 源码=治理层资产） | 治理立案 |
| OBJ_R-#6 | OBJ_R_rules_standards | 案例库升格 catalogs 正式注册表时机 | 治理立案（攒案门槛） |
| L4-#2 | L4_compare | 独立性 gate 立案准许（判据保护 gate+criteria_ref 机检） | OBJ_R 四步立案（C7） |
| L5-#2 | L5_schedule_gate | 首批区域白名单点头 | policy 文件 Owner 区登记（治理流程；自治满一季可提案退役） |
| L7-#2 | L7_heredity | defect_pattern_checklist 增量登记纪律增补 | 治理域 policy 修订流程 |
| OBJ_M-#2 | OBJ_M_models | M3 考纲正式化（尺子归治理层） | OBJ_R 四步流水线 |
| OBJ_T-#1 | OBJ_T_tools | 考纲正式化（tool_exam_policy+基准任务集） | OBJ_R 四步流水线 |
| OBJ_T-#2 | OBJ_T_tools | 沙箱边界细则+删除双闸 gate 立案准许 | Owner 对方案点头后治理立案 |

### 真待 Owner（6 项）

| 编号 | 稿件 | 事项 | 为何唯 Owner |
|------|------|------|-------------|
| OBJ_M-#1 | OBJ_M_models | M4 路由表 api_providers 增删+免费窗合规终批（8 条 AI 层轨映射，C6 施工前置） | 计费线/订阅=Owner 独占四类事③② |
| OBJ_S-#2 | OBJ_S_perimeter | secret_registry.yaml 是否增设 `ai_exposure: forbidden` 字段 | registry 修改=Owner 门位（不增设则 S1 deny-list 为唯一机检面，功能等价） |
| L4-#3 | L4_compare | 派考边 `intake_exam_due` 契约对齐（R2 后仅余此边；evidence_ref 增补已随 R2 销账，回执件已改名 intake_exam_receipt） | 跨稿契约变更，需 Owner 确认或 L2 侧修订 |
| L5-#3 | L5_schedule_gate | 任务书 schema v0 增补 provenance 字段（附录 A 版本化变更） | 主文档附录级变更，设计两可 Owner 定向 |
| L6-#2 | L6_ab_switch | 墓碑 TTL 清理判据+注册表净删门确认 | 净删=high human_gate（宪法 §5），AI 永远只提案 |
| OBJ_T-#3 | OBJ_T_tools | creation_token 补登（OBJ_T/DESIGN.md，×5 批次外） | 主会话/Owner 补登动作，登记留痕待办 |

**对账**：已销 16+治理立案保留 9+真待 Owner 6=**31**，与红队 B 计数一致。分稿核验：
L2 共 1（销 1）｜L3 共 2（销 2）｜L4 共 4（销 2/立案 1/待 1）｜L5 共 4（销 2/立案 1/待 1）｜
L6 共 3（销 2/待 1）｜L7 共 3（销 2/立案 1）｜OBJ_M 共 2（立案 1/待 1）｜OBJ_T 共 3（立案 2/待 1）｜
OBJ_R 共 7（销 4/立案 3）｜OBJ_S 共 2（销 1/待 1）。

## 4. 后续挖矿序列（每段深挖走挖矿 SOP 六向寻路）

1. **已完**：V0 大层定义 → V1 三层划分 → V2 循环段位（从大到小三步验证，Owner 要求的顺序）。
2. **已完**：七段逐段深挖+四条对象线（建议顺序=L2 收集库（其他段的枢纽）→ L1 感知（源头）
   → L4 对比（咽喉）→ L6 切换（安全带）→ L3 清洗 → L5 排产 → L7 传承，OBJ_M/T/S/R 同批），
   各段 DESIGN.md=工程真源。
3. **当前**：主文档已升 v2.0 active（Owner 2026-09-17 夜全批）；下一步=各稿施工项按
   construction_workflow 15 步闭环开单施工（L1 施工项 7 受 T3 双前置约束，见 §3）。

## 5. 挖矿日志汇总（本班验证轮次明细，V 报告+各 DESIGN 挖矿日志为全量真源）

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| V0-R1 | 治理/业务分层业界对标 | signal | IIA Three Lines Model (2020) |
| V0-R2 | "AI 改进 AI"前沿 | signal | AlphaEvolve (DeepMind 2025, arXiv 2506.13131) |
| V0-R3 | 自我改进代理 | signal | Darwin Gödel Machine (Sakana AI 2025, arXiv 2505.22954)；首次搜索超时=受阻一次，重试成功 |
| V0-R4 | 自管理系统经典循环 | signal | MAPE-K (Kephart & Chess 2003, IEEE Computer) |
| V1-R1 | 量化机构组织分层 | signal | 功能分离（research/tech/risk）+平台型集中模式 |
| V1-R2 | MLOps 成熟度坐标 | signal | Google Cloud MLOps CI/CD/CT Level 0-2 |
| V2-R1 | A/B 切换业界名 | signal | Champion/Challenger + Shadow Deployment（FICO/DataRobot/银行模型验证） |
| V2-R2 | 多样性档案算法 | signal | MAP-Elites (Mouret & Clune 2015, arXiv 1504.04909) |
| V2-R3 | 全管线同构参照 | signal | RD-Agent（arXiv 2505.15155，2026-09-13 甄别轮在档复用） |
| OBJ-R1 | 模型情报/免费窗口 | signal（在档复用） | 夜间 Flash 免费实战（Owner 自搜福利实例）+GLM 双计费线 |
| OBJ-R2 | 模型考试 | signal（在档复用） | model_capability_exam 模块在档+挖矿 SOP 模型分派二维法 |
| OBJ-R3 | 模型/工具自我升级 | signal（在档复用） | AlphaEvolve/DGM（V0-R2/R3 同源两处消费，交叉验证闸满足） |
| BIZ-R1 | 业务层骨架并轨 | signal（跨会话同步） | automation 目录 2a11b881：四轴+底板/标准库四步/生命周期轴/骨锁肉动 |
| BIZ-R2 | 排班表归属 | signal（内部推理） | 共享资源全机单点（GPU/CH 锁/并发槽/API 配额）→一张真源治理层资产，两层为客户 |
| 多轮 | 搜索服务 429 风暴 | 受阻 | 按挖矿 SOP 60-130s 单发间隔重试，全部轮次最终成功；记档不判查无 |

---

## 红蓝 R1 修复记录（红队 B 发现，修复组 3，2026-09-17）

1. **B①（L1+README）**：L1 §2.4"外扫=日历节拍"升格 T3 处置——开工前置由"自裁补进
   ruling_registry"改为 **Owner 追认+裁定登记双前置**（按 OBJ_R"放松永不自动"自律）；
   §3 裁定登记前置行同步改写，追认前施工项 7 禁开工、其余施工项不受阻。
2. **B②**：§2 目录结构表全量刷新（L1-L7/OBJ_M-T-S-R 统一 design_done（DESIGN.md 真源），
   V0-V2=done，主文档行=v2.0 active）；头部一句话、§0 速览"建议升级"、§4"待 Owner 点头"
   等框架类陈旧措辞清除（Owner 已夜批）；真实治理立案类措辞保留。
3. **B③**：新增 §3.5 待 Owner 项处置总表（全目录 31 项对账：已销 16/治理立案保留 9/真待
   Owner 6，含 token 补登×5 与数值初值追认逐条编号）。

**红蓝 R3 修复记录**：R3：L4-#3 行同步 R2 后实际余量。
