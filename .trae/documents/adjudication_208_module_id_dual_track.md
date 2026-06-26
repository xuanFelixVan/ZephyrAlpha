---
ttl: task_bound
---

# 裁定#208：module_id 数字序号制双轨治理

> **裁定编号**：#208
> **关联议题**：#ARCH-019（status=decided, severity=P1高）
> **立项背景**：承接裁定#206 B-4 阶段 E 遗留议题（"立议题不本次施工"）。裁定#206 已完成阶段 A-D（规则治本 + 改名传播 + 制品分离 + 节点路径重编号），B-4 明确"module_id 数字序号制"为独立议题剥离至阶段 E 立项。本裁定正式立项 + 独立裁定 + 治本方案。
> **裁定日期**：2026-06-26
> **裁定者角色**：客观专业架构师（独立裁定，不回避决策）
> **关联文档**：
> - 主 plan：[module_id_dual_track_governance_plan.md](module_id_dual_track_governance_plan.md)
> - 深度调研报告：`docs/02_enterprise_architecture/03_governance_reports/module_id_numeric_sequence_governance_report.md`
> - 恢复执行 plan：[module_id_dual_track_resume_execution_plan.md](module_id_dual_track_resume_execution_plan.md)

---

## 一、裁定核心立场

**双轨制 scoped 适用**：不强制统一为单一格式，而是按标识符的"出生场景"分轨：

| 轨 | 格式 | 角色 | 对标 | 序号 |
|---|---|---|---|---|
| **layer-master 轨** | `MOD-{LAYER_CODE}-{SEQ}` | UID（稳定不透明） | K8s UID / Surrogate Key | 必填 |
| **domain-functional 派生轨** | `MOD-{DOMAIN_FRAGMENT}[-NNN]` 或 `D-XXX-{SEQ}` | name（语义可读） | K8s name / Natural Key | 可选 |

**双轨判定**：token 共享测试——blueprint_id 去 `MOD-`/`D-` 前缀与 domain_id 去 `D-` 前缀分词有交集 → 属派生轨；无交集 → 属 layer-master 轨。

**为什么不选 A/B/C 单选**：
- A（强制数字序号制）：破坏 198 行派生 ID 的语义可读性，违背 K8s name 范式。
- B（全派生语义制）：破坏 4805 行 layer-master ID 的稳定引用，违背 UID 范式。
- C（保留现状不治理）：SSoT 矛盾未除，automation 永远误判，技术债持续累积。
- **双轨制**：调和两者，理论正解（第一性原理标识符双需求），工业有先例（K8s name/UID + DB Surrogate/Natural Key）。

> 完整论证见深度调研报告 §3（第一性原理）+ §4（社区对标）+ §6（双轨制方案论证）。

---

## 二、裁定项 R1-R8

### R1：SSoT 双轨制调和（layer-master + domain-functional scoped）

- **判定**：trae_028 L1037-1040 模块ID格式 condition 改为 scoped 双轨制；L1082-1085 派生规则删除自指循环，引用双轨主格式。
- **理由**：第一性原理双需求（稳定引用 vs 语义可读）+ K8s name/UID 对标 + Surrogate/Natural Key 对标。
- **状态**：✅ 阶段 A 完成（commit `2fb6b993d`）。trae_028 v1.2.0→1.3.0，两处规则一致使用 `[-NNN]` 表示法，SSoT 自洽性恢复。

### R2：派生 ID 合规性（198 行派生无序号 ID 保留）

- **判定**：`MOD-ASHARE_SIGNAL` 等 198 行派生无序号 ID 属 domain-functional 派生轨合规（序号可选），保留不强制加序号。
- **理由**：派生 ID 本身含 domain 语义片段已有区分度，序号可选符合 K8s name 范式（name 本身已含语义，UID 才需不透明序号）。
- **状态**：✅ 阶段 A R1 双轨制已蕴含此判定。
- **数据更新**：立项时估算 268 行，ro SQL 实测 198 行（偏差 -70 行，根因见报告 §9.2）。

### R3：历史违规分类治理

- **判定**：按违规性质分两类——
  - **技术违规（26 行：纯数字 5 + 下划线错误 21）**：阶段 C 批量重编号，无语义争议。
  - **语义判定（601 行 MOD-XXXX 单字/层代码无序号）**：阶段 D 逐类语义判定（layer_code 缩写 → 归 layer-master 轨补序号；domain_fragment → 归派生轨保留；无匹配 → 损坏清理）。
- **理由**：技术违规无争议可批量处理；语义违规需人工/AI 判定归属，不可一刀切。
- **状态**：⏳ 阶段 C/D 待施工。
- **数据更新**：立项时估算技术违规 ~125 行 / 语义判定 895 行；ro SQL 实测技术违规 26 行 / 语义判定 601 行（偏差根因见报告 §9.2，主因 #206-阶段D 已 renumber 75 nodes + 分类阈值差异）。

### R4：门禁执行升级（N-06 双轨正则 + N-17 升阻断）

- **判定**：N-06 升级为双轨正则校验（`_MODULE_ID_LAYER_MASTER_RE` + `_MODULE_ID_DOMAIN_DERIVED_RE` + `_MODULE_ID_D_PREFIX_RE`），删除"阶段 E 议题"注释；N-17 从 warning 升为阻断（过渡期 `--warn-only`）；新增 `_validate_ssot_linkage()` SSoT 机械联动校验。
- **理由**：SSoT 修订必须与 enforcement 脚本机械联动，否则修订无法落地（AI 编程社区 enforcement gap 通病，见报告 §4.4）。
- **状态**：✅ 阶段 B 完成（commit `5dfa2c650`）。
- **实测验证**：`--validate-ssot` 输出 `✅ SSoT(trae_028 v1.3.0) 与脚本双轨正则机械联动一致` EXIT=0；22 单测全绿。

### R5：派生标识符注册表结构化

- **判定**：derived_identifier_registry.yaml entry_schema 新增 `sequence_required`/`format_pattern`/`scope` 三字段，4 entries 全部填充。派生轨 `sequence_required=false`，layer-master 轨 `sequence_required=true`。
- **理由**：派生 ID 的序号要求从"内联文字描述"升级为"结构化字段"，供 N-06 机械读取。
- **状态**：✅ 阶段 A 完成（commit `2fb6b993d`）。

### R6：议题登记机制建立（architecture_issue_registry.yaml）

- **判定**：新建架构议题注册表，作为 #ARCH-XXX 唯一真源，治本"grep-and-claim 占位"病根。登记 #ARCH-019（本议题）+ 回溯 #ARCH-008~018（11 条 schema 健康类）。
- **理由**：ALCOA+ Complete 维度——无中央注册表则议题编号不可追溯（见报告 §4.3）。
- **状态**：✅ 阶段 A 完成（commit `2fb6b993d`）。

### R7：#ARCH 编号分配铁律

- **判定**：6 条铁律写入 architecture_issue_registry.yaml 头部：①连续分配（禁止跳号）②不回收（废弃编号仍保留）③superseded_by 链（取代关系可追溯）④status 四值（open/decided/deprecated/superseded）⑤编号预留 #001-007 ⑥登记强制（禁止 grep-and-claim）。
- **理由**：编号管理必须有规则，否则未来 #ARCH-XXX 分配混乱重现。
- **状态**：✅ 阶段 A 完成（commit `2fb6b993d`）。

### R8：循环验证 3 轮（高于项目标准 2 轮）

- **判定**：阶段 E 循环审查至 0 残留，轮数设为 3（高于项目标准 2 轮）。
- **理由**：本议题涉及 SSoT 自洽性 + DB 数据 + 脚本 enforcement 三层联动，盲区风险高于常规。自指悖论（AI 写规则 + AI 写测试共享同源盲区），机械注入变异与 AI 认知盲区正交（项目 memory：mutation testing 经验）。
- **状态**：⏳ 阶段 E 待施工。

---

## 三、关联议题 #ARCH-019

| 字段 | 值 |
|---|---|
| issue_id | #ARCH-019 |
| title | module_id 数字序号制双轨治理（SSoT 自相矛盾 + 历史违规 + 议题登记机制） |
| severity | P1高 |
| adjudication | 裁定#208 双轨制（layer-master 数字序号制 + domain-functional 派生语义制 scoped 适用）；R1-R8 详见本文件 §二 |
| fix_phase | 裁定#208 阶段 A-E（A+B 已完成，C/D/E 待施工） |
| status | decided |
| related_adjudication | #208 |
| created | 2026-06-26 |
| last_updated | 2026-06-26 |
| 登记位置 | [architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) L132-140 |

---

## 四、阶段 A-E 施工进度

| 阶段 | 内容 | 风险 | 状态 | commit |
|---|---|---|---|---|
| A | SSoT 规则治本 + 注册表结构化（R1/R5/R6/R7） | 低 | ✅ 完成 | `2fb6b993d` |
| B | 执行层门禁升级（R4：N-06 双轨 + N-17 阻断 + SSoT 联动 + --mark-invalid + 过渡期 warn-only + 单测） | 中 | ✅ 完成 | `5dfa2c650` |
| C | 技术违规重编号（26 行：纯数字 5 + 下划线错误 21） | 高（首次改 DB） | ⏳ 待施工 | — |
| D | 语义判定 + 损坏清理（601 行 MOD-XXXX 分类） | 中高 | ⏳ 待施工 | — |
| E | 循环验证 3 轮 + 门禁激活阻断（R8） | 中 | ⏳ 待施工 | — |

### Fresh 数据偏差说明

ro SQL 实测（2026-06-26）与主 plan §2.4 立项估算的偏差：
- 技术违规：实测 26 行 vs 估算 ~125 行（-99 行，主因 #206-阶段D 已 renumber 75 nodes + 分类阈值差异）
- 待语义判定：实测 601 行 vs 估算 895 行（-294 行，同上根因）
- 派生无序号：实测 198 行 vs 估算 268 行（-70 行，同上根因）

> 偏差根因详见深度调研报告 §9。阶段 C/D 施工以 ro SQL 复测为准，不依赖旧估算。

---

## 五、衍生决策 F1-F6

| # | 决策 | 内容 |
|---|---|---|
| F1 | 双轨判定 token 共享测试实现 | blueprint_id 去 `MOD-`/`D-` 前缀后按 `_` 分词，domain_id 去 `D-` 前缀后按 `_` 分词，两词集有交集则属派生轨。已实现为 check_naming_convention.py 的 helper 函数（阶段 B B2） |
| F2 | layer-master 轨序号宽度 | 维持 3 位（MOD-XX-NNN，上限 999/层），与 trae_028 L448 容量评估一致；4 位扩展（MOD-XX-NNNN）作为预留不立即启用 |
| F3 | 派生轨序号宽度 | 可选序号同样 3 位，`MOD-{DOMAIN_FRAGMENT}-NNN` |
| F4 | 过渡期时长 | 阶段 B 至阶段 E 激活前均为过渡期（`--warn-only`），预计 1-2 个工作 session |
| F5 | architecture_issue_registry 维护责任 | owner=MOD-INF-037，与 REG-ARCH-PANORAMA-001/REG-DEPGRAPH-001 同 owner |
| F6 | #ARCH-001~007 预留段 | 永久保留为预留，不强制回溯补录，避免编号膨胀 |

---

## 六、验收标准进度（主 plan §十二 10 项）

| # | 验收项 | 状态 | 证据 |
|---|---|---|---|
| 1 | trae_028 v1.3.0 双轨制 condition + 无自指循环 | ✅ | commit `2fb6b993d`；Read 核实 L1037-1040 / L1082-1085 |
| 2 | derived_identifier_registry 4 entries 全部有结构化字段 | ✅ | commit `2fb6b993d` |
| 3 | architecture_issue_registry 含 12 entries + 编号铁律 6 条 | ✅ | commit `2fb6b993d`；Read 核实全文 |
| 4 | registry_of_registries 含 REG-ARCH-ISSUE-001 + 统计 49/14 | ✅ | commit `2fb6b993d` |
| 5 | SSoT 矛盾消除（L1038 与 L1084 一致 `[-NNN]`） | ✅ | commit `2fb6b993d` |
| 6 | check_naming_convention.py N-06 双轨正则 + N-17 可阻断 | ✅ | commit `5dfa2c650`；`--validate-ssot` EXIT=0 |
| 7 | B9 单测全绿 | ✅ | commit `5dfa2c650`；22 tests passed in 0.30s |
| 8 | 技术违规（26 行）清零 | ⏳ | 阶段 C 验证（ro SQL 实测） |
| 9 | 语义判定（601 行）分类完成 + 损坏清理 | ⏳ | 阶段 D 验证 |
| 10 | 循环验证 3 轮 0 残留 + N-06/N-17 正式阻断激活 | ⏳ | 阶段 E 验证 |

---

## 七、与裁定#206/#207 的衔接

- **裁定#206**（blueprint_id 命名病根）：阶段 A-D 已完成规则治本 + 改名传播 + 制品分离 + 节点路径重编号。B-4（阶段 E module_id 数字序号制）明确"立议题不本次施工"→ 本裁定（#208/#ARCH-019）承接。
- **裁定#207**（SSoT 完整性）：阶段 A 已完成 NR-001/NR-003 补收录 + 派生标识符规则 + 改名传播规则。R2 制品生成器职责分离 → 本裁定 C/D 遵循（只用只读 artifact 生成器）。R1 改名完整性审计工具 → 本裁定 C4/D5 消费。
- **阶段 E 对齐**：本裁定阶段 A 在 #207 已建立的 SSoT 框架上施工，不重复 #207 已做的工作，仅补 module_id 双轨制调和。

---

> **裁定状态**：R1/R2/R4/R5/R6/R7 已完成（阶段 A+B）；R3/R8 待施工（阶段 C/D/E）。
> **下一步**：阶段 C 技术违规重编号（26 行，首次改 DB，待用户确认后施工）。
