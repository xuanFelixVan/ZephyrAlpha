---
doc_type: index
ttl: permanent
title: 规则地图战役裁定登记（R1-R6）
adjudicator: knowledge-organizer-survey 会话（Owner 2026-10-14 授权代裁）
owner: ZephyrAlpha-Owner
status: active
version: "1.0.0"
date: 2026-10-14
topic: rule_map_campaign
---

# 规则地图战役裁定登记（R1-R6）

> **性质**：Owner 2026-10-14 授权代裁（"你根据裁定 sop，自己裁定一个答案告诉我"）。走五门流水线（G0-G4），判据编号引自 `sop/governance_sop/adjudication_routing_policy.md` v2.2.1。
> **正式入册**：本页为战役裁定留痕；逐条 `ruling_registry.yaml` 取号登记随施工批次原子落地（RULE-RULING）。
> **保留面声明**：R1 触碰 Owner 保留面⑥「宪法本身」，为授权代裁草案，Owner 可推翻（推翻后按回滚命令恢复）。

## R1 宪法真源唯一化

- **类型**：D1 生死处置（治理资产）｜**判据**：G1-1 同真源可派生→必并 + 可逆性不对称（停用优先于判死）
- **证据（E1 实测）**：根 `AGENTS.md` 15186B／2026-10-13 更新，IDE 注入链与冷启动第一读均指向它；`sop/governance_sop/agent_constitution_l0.md` 11388B／2026-09-12 后未动，两份差 139 行——sop/README.md 指其为真源系过期引用。
- **裁定**：①根 `AGENTS.md` = 宪法唯一真源；②`agent_constitution_l0.md` 原位降级为**指针桩**（保留路径保存量引用，内容改指向 AGENTS.md 的一行+切换说明，走墓碑制 deprecated）；③sop/README.md 与 governance_sop/index.md 引用改指根 AGENTS.md；④机生件随重扫自动跟随。
- **回滚命令**：`git revert <本批 commit>` 后 `git checkout HEAD~1 -- docs/01_policies_and_standards/sop/governance_sop/agent_constitution_l0.md`
- **执行状态**：待施工（本批未动该文件，因同夜他队在途，按"他队编辑中→登记后延"纪律顺延）

## R2 施工范围：P0+P1+P2 全做，并入规则地图施工序列

- **类型**：D5 资源优先级｜**判据**：G0-3 三轴有可测 Δ + G3-6 反拖延（P2 无硬阻塞门）
- **裁定**：全做。地图为总纲，P0=挂载前机械清理、P1=纵轴环节化、P2=facts 四字段落地（trigger_facts/consumers）。分开做=索引建两遍。
- **主轴**：治理质量轴（检索命中+执行面可见+重复显形）；辅轴不劣化：不动物理路径。

## R3 分域维度：按流程环节分，不按主题分

- **类型**：D3 标准｜**判据**：挂图 SOP §1「纵轴=环节」+ E2 先例（图11/12/14 全部按流程切）
- **裁定**：8 环节 + 1 横切轴；`scope` 字段降级为环节内检索键；原 9 主题域提案作废。物理目录不动（见 R4）。

## R4 物理路径一律不动

- **判据**：G1-4 派生成本（87 路径 × 引用面：rule_catalog／perception index／doc.md／门禁锚点）> 索引层分域收益
- **裁定**：`trae_NNN` 文件名与目录维持原状，索引层分域拿 80% 收益、0 路径风险。

## R5 新建规则地图页，制度馆不扩权

- **判据**：G1-1（制度馆为 lib_assets 机生视图且语义=注册表，塞规则需改账本+语义冲突）；地图页走挂图 SOP 家族既有形态（图9/11/12/13/14/15 先例）
- **裁定**：人读总图落 `docs/library/rule_map.md`，由 FRONT_DOOR 指入；制度馆继续管注册表。

## R6 图号改判：规则地图 = 图17（非图16）

- **来源**：四车道挖矿独立双向印证——`fig16_legislation/` 与 `fig16_ruling/` 已双占图16，且 `gate_registry.yaml` 存在 active 门 `GOVERNANCE-LEGISLATION-MAP: 图16（治理立法流图）`，机械锚点全域冲突。
- **裁定**：规则地图顺延为**图17**；原裁定书/调查报告中"图16"表述一律按图17 读。撞号修复入册，MAP-ALIGNMENT 类门若拦则按本裁定放行。

---

## 附：架构裁定摘要（规则地图 × 流程地图 × 门禁）

| 层 | 答什么问句 | 形态 | 与规则地图关系 |
|---|---|---|---|
| 规则地图（图17） | 每个环节守什么规矩／规矩怎么并怎么清 | 治理域总图（本批新建） | — |
| 图11 提交链 | 提交链哪里卡／死信怎么归因 | 流程图（已有） | 指针互链，不合并 |
| 图14 施工流 | 怎么建 | 流程图（已有） | 指针互链 |
| 图12 数据链 | 数据怎么供 | 流程图（已有） | 指针互链 |
| TDM 地图 | 买什么／何时出手 | 业务域地图（已有） | 指针互链（不同域） |
| gate_registry（191 台） | 每台门禁的登记 | 机生总册 | 规则地图只存指针，禁复制（INV-1） |

**不合并三判据**：①不同问句（治理视角 vs 流程优化视角）；②粒度差两个量级（图11 环节为 claim/暂存/merge/入队/死信子环节）；③合并=全量重挂，违 G1-4 派生成本与机生层禁手改。
