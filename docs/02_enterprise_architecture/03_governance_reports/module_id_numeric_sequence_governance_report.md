---
title: module_id 数字序号制双轨治理——病根调研与裁定报告
doc_type: audit_report
status: active
ttl: permanent
created_by: agent
created: '2026-06-26'
approved_by: owner
approved_date: '2026-06-26'
module_id: REG-GOV-MODID-RCA-001
related_adjudication: '#208 (承接 #206 B-4 阶段 E)'
related_validator: 'check_naming_convention.py (N-06/N-17) + apply_depgraph.py (--mark-invalid)'
---

# module_id 数字序号制双轨治理——病根调研与裁定报告

> **文档定位**：承接裁定#206 B-4 阶段 E 遗留议题（"立议题不本次施工"），现正式立项 #ARCH-019 + 独立裁定#208 + 治本施工方案。本报告作为客观架构师调研，从第一性原理出发，对标专业机构与 AI 编程社区，查清病根、给出裁定与治本方案。
>
> **调研方法**：内部规则真源审计（trae_028 / derived_identifier_registry / architecture_issue_registry）+ 执行层脚本源码核对 + depgraph.db ro 模式 SQL 实测探针 + #206/#207 既有裁定核对。所有结论附证据（文件:行号 / 量化数据）。
>
> **调研日期**：2026-06-26
> **调研者角色**：客观专业架构师（独立裁定，不回避决策）

---

## 1. 问题陈述

### 1.1 病根全貌（四层）

module_id 数字序号制治理议题（#ARCH-019）暴露四层叠加病根：

| 层 | 病根 | 证据 | 严重度 |
|---|---|---|---|
| 层 1 | **SSoT 自相矛盾**：trae_028 同一文件两条规则对"派生 module_id 是否需要数字序号"判定相反 | L1038（序号必填 fail 其他）vs L1083（派生序号可选 pass） | P0 致命 |
| 层 2 | **历史违规堆积**：5630 行 MOD-* 前缀 blueprint_id 中 627 行格式不合规 | ro SQL 实测（见 §1.3） | P1 高 |
| 层 3 | **议题登记缺失**：#ARCH-XXX 无中央注册表，靠 grep-and-claim 占位 | registry_of_registries.yaml L515-516 仅 ISS-003 | P1 高 |
| 层 4 | **enforcement gap**：N-06 主动放弃强制数字序号制，N-17 warning 不阻断 | check_naming_convention.py L249/L1025-1036（阶段 B 前） | P1 高 |

### 1.2 三个核心问题

> **Q1**：SSoT 内部自相矛盾（L1038 vs L1083）如何调和？二选一还是分层适用？
> **Q2**：268 行（立项时估算）/ 198 行（实测）派生无序号 module_id 是合规（保留）还是违规（需加序号）？
> **Q3**：历史违规 module_id 如何处理？批量重编号还是豁免？门禁如何升级？

### 1.3 量化证据（depgraph.db ro SQL 实测 2026-06-26）

> DB 路径：`D:\ZephyrAlpha\data\databases\depgraph.db`（nodes 表 6501 行，846 个 distinct blueprint_id）
> 探针脚本：`scripts/_tmp_bp_dist.py`（ro 模式，实测后已清理）

MOD-* 前缀 blueprint_id 格式分布（5630 行）：

| 格式分类 | 行数 | 占比 | 合规性 | 处置 |
|---|---|---|---|---|
| layer-master `MOD-XX-NNN` | 4805 | 85.3% | ✅ 合规 | 保留 |
| derived 派生无序号 `MOD-XX_YYY` | 198 | 3.5% | ✅ 合规（R2） | 保留 |
| 单字/层代码无序号 `MOD-XXXX` | 601 | 10.7% | ⚠ 待语义判定 | 阶段 D 分类 |
| 纯数字 `MOD-NNN` | 5 | 0.09% | ❌ 技术违规 | 阶段 C 重编号 |
| 下划线错误 `MOD_XX_NNN` | 21 | 0.37% | ❌ 技术违规 | 阶段 C 重编号 |
| **合计 MOD-* 前缀** | **5630** | 100% | | |
| D- 前缀 | 0 | — | — | — |
| blueprint_id_invalid=1 | 0 | — | — | 阶段 C/D 写入 |

---

## 2. 命名规则真源审计

### 2.1 真源定位

项目命名规则唯一真源为 [trae_028_doc_structure_naming.yaml gov_doc_003_naming_ssot](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml#L1022-L1074)。

### 2.2 矛盾点（阶段 A 修订前）

**L1036-1039（模块ID格式 condition）**——要求数字序号制，"fail: 其他格式"：
- `pass: MOD-{LAYER_CODE}-{SEQ}`（序号必填）
- `fail: 其他格式` → `MOD-ASHARE_SIGNAL`（无 SEQ）应判 fail

**L1083（派生标识符规则，#207 R3-4 新增）**——允许派生无序号：
- `pass: blueprint_id=MOD-ASHARE_SIGNAL[-NNN] 或 MOD-ASHARE_SIGNAL（无 NNN）` → `MOD-ASHARE_SIGNAL` 判 pass

→ 同一文件两条规则对同一 ID 判定相反，SSoT 不自洽使任何自动化 enforcement 都会误判。

### 2.3 阶段 A 修订后（裁定#208 R1 落地）

**L1037-1040（模块ID格式 condition，双轨制）**：
```
check: 模块ID格式（双轨制，裁定#208 R1）
pass: 双轨制 scoped 适用—layer-master轨=MOD-{LAYER_CODE}-{SEQ}(如MOD-L00-001/MOD-INF-005,序号必填);
      domain-functional派生轨=MOD-{DOMAIN_FRAGMENT}[-NNN]或D-XXX-{SEQ}(如MOD-ASHARE_SIGNAL/MOD-ASHARE_SIGNAL-001/D-MKT_DATA-001,
      域片段派生自domain_id去D-前缀,序号可选);Shared为SH-{ABBR}-{NNN};Frontend为FE-L{N}-{ABBR}-{NNN};
      双轨判定=token共享测试(blueprint_id去MOD-/D-前缀与domain_id去D-前缀分词有交集则属派生轨)
fail: 其他格式(既非layer-master轨也非domain-functional派生轨)
rationale: 双轨制对标K8s name/UID分离(layer-master≈UID稳定不透明+派生轨≈name语义可读);
           调和L1038(序号必填)与派生规则(派生序号可选)的历史矛盾
```

**L1082-1085（派生标识符规则，引用双轨主格式）**：
```
check: blueprint_id 派生关系
pass: blueprint_id 的域片段派生自 domain_id(如domain_id=D-ASHARE_SIGNAL则
      blueprint_id=MOD-ASHARE_SIGNAL[-NNN],序号可选,见模块ID格式condition双轨制domain-functional轨);
      派生关系记录在derived_identifier_registry.yaml(sequence_required字段控制序号是否必填,派生轨=false)
fail: blueprint_id 域片段与所属 domain_id 不一致
```

→ 两处规则现在一致使用 `[-NNN]` 表示法，自指循环已消除，SSoT 自洽性恢复。

### 2.4 配套注册表结构化（裁定#208 R5/R6/R7）

- [derived_identifier_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/derived_identifier_registry.yaml)：entry_schema 新增 `sequence_required`/`format_pattern`/`scope` 三字段，4 entries 全部填充。派生轨 `sequence_required=false`（序号可选），layer-master 轨 `sequence_required=true`（序号必填）。
- [architecture_issue_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)（新建）：#ARCH-XXX 唯一真源。登记 #ARCH-019（本议题, status=decided）+ 回溯 #ARCH-008~018（11 条 schema 健康类）+ 编号铁律 6 条（连续分配/不回收/superseded_by 链/status 四值/编号预留 #001-007/登记强制）。

---

## 3. 第一性原理：标识符的两种本质需求

标识符（identifier）在系统中承担两种正交需求：

### 3.1 稳定引用（machine-stable reference）

程序/脚本/配置通过 ID 引用实体，要求 ID **不随语义变化而改变**（实体改名不影响引用链）。

- 需求特征：不透明、稳定、永不改变
- 满足方式：**序号**（纯数字，无业务语义，实体改名时序号不变）
- 典型场景：脚本 `import` / 配置 `depends_on` / 数据库外键引用

### 3.2 语义可读（human-readable semantics）

人类阅读 ID 时能快速推断实体归属（哪个域、什么功能）。

- 需求特征：可读、有意义、可能随业务演化
- 满足方式：**语义片段**（域缩写、功能描述，实体改名时 ID 跟变）
- 典型场景：代码审查 / 架构图阅读 / 日志诊断

### 3.3 单一格式无法同时满足两者

- **纯序号（MOD-ALPHA_SIGNAL_DOMAIN）**：稳定但不可读——人类看到 MOD-ALPHA_SIGNAL_DOMAIN 无法推断归属
- **纯语义（MOD-ASHARE_SIGNAL）**：可读但不稳定——域改名（D-SIGNAL_ASHARE→D-ASHARE_SIGNAL）则 ID 必须跟变，破坏引用链

**这是 L1038（序号必填）与 L1083（序号可选）矛盾的根源**——两条规则各自只看到一个需求：
- L1038 站在"稳定引用"角度，要求序号必填（fail 其他）
- L1083 站在"语义可读"角度，允许派生无序号（pass 无 NNN）

强行统一为任一单轨都会破坏另一需求。正确解法是**双轨制**——按标识符的"出生场景"分轨。

---

## 4. 社区对标

### 4.1 Kubernetes name/UID 分离范式

Kubernetes 是处理"稳定引用 vs 语义可读"矛盾最成熟的工业实践。每个 K8s 资源有三类标识：

| 标识 | 生成方 | 特征 | 角色 | ZephyrAlpha 对标 |
|---|---|---|---|---|
| **UID**（`metadata.uid`） | 系统生成 | 不透明、UUID 格式、永不改变、纯稳定引用 | machine-stable | layer-master 轨 `MOD-{LAYER}-{SEQ}` |
| **name**（`metadata.name`） | 人类指定 | 语义可读、可被引用但非稳定锚点、同 namespace 内唯一 | human-readable | domain-functional 派生轨 `MOD-{DOMAIN_FRAGMENT}[-NNN]` |
| **label**（`metadata.labels`） | 人类指定 | 辅助语义索引、与 name 正交、可多值 | auxiliary index | （ZephyrAlpha 暂无对标，预留） |

> **K8s 设计哲学**（Kubernetes API Conventions）："UID is unique in time and space. name is unique in space at a given time, but may be reused." —— UID 追求永恒稳定，name 追求空间唯一+语义可读，两者职责分离。

**对标结论**：ZephyrAlpha 的 module_id 应分轨——layer-master 轨承担 UID 角色（`MOD-{LAYER}-{SEQ}` 稳定序号），domain-functional 派生轨承担 name 角色（`MOD-{DOMAIN_FRAGMENT}[-NNN]` 语义可读，序号可选因 name 本身已含语义区分度）。

### 4.2 Surrogate Key vs Natural Key（数据库理论）

数据库理论对"稳定引用 vs 语义可读"有经典框架：

| 键类型 | 定义 | 特征 | 适用场景 | ZephyrAlpha 对标 |
|---|---|---|---|---|
| **Surrogate Key**（代理键） | 系统生成、无业务含义、稳定不变（如自增 ID / UUID） | 稳定、不透明、不随业务变 | 外键引用、程序逻辑 | layer-master 轨 |
| **Natural Key**（自然键） | 源自业务属性、有含义、可能变化（如域名 / 身份证号） | 可读、有意义、可能变 | 人类查询、业务展示 | domain-functional 派生轨 |

> **数据库理论共识**（Codd/Date 关系模型）：两种键各有适用场景，强行统一为一种会导致要么丢失语义（纯代理键不可读）要么丢失稳定性（纯自然键随业务变）。实践中常采用"代理键做主键 + 自然键做唯一约束"的双键模式。

**对标结论**：ZephyrAlpha 双轨制 = 代理键（layer-master 轨）+ 自然键（派生轨）的双键模式，是数据库理论的正统实践。

### 4.3 ALCOA+ 数据治理框架

ALCOA+（Attributable / Legible / Contemporaneous / Original / Accurate + Complete / Consistent / Enduring / Traceable）是 FDA/EMA/GxP 监管的数据完整性框架，其中与本议题相关的维度：

| 维度 | 定义 | 本议题病根 | 治本措施 |
|---|---|---|---|
| **Complete（完整）** | 数据无遗漏，所有应有记录均存在 | #ARCH-XXX 无中央注册表，议题编号靠 grep-and-claim 占位 → 不完整 | R6 建立 architecture_issue_registry.yaml |
| **Consistent（一致）** | 数据在所有位置一致，无矛盾 | trae_028 L1038 vs L1083 同文件矛盾 → 不一致 | R1 双轨制调和 |
| **Traceable（可追溯）** | 数据可追溯到来源，有审计链 | 派生 ID 无注册，无法追溯派生关系 → 不可追溯 | R5 derived_identifier_registry 结构化 |

> **ALCOA+ 来源**：FDA Guidance for Industry — Data Integrity and Compliance with CGMP；EMA Guideline on computerised systems. ALCOA+ 是受监管行业（制药/金融）的数据完整性强制标准。

**对标结论**：本议题三维度（Complete/Consistent/Traceable）均不达标，治本措施直接对标 ALCOA+ 框架。

### 4.4 AI 编程社区对标：命名约定的 enforcement gap

| AI 编程工具 | 约定文件 | enforcement 机制 | gap 现状 |
|---|---|---|---|
| **Cursor** | `.cursorrules` | 无强制 enforcement，依赖 AI 自觉遵循 | 约定写了 AI 可能不跟 |
| **Cline** | `.clinerules` | 无强制 enforcement | 同上 |
| **Continue** | `.continuerc` | 无强制 enforcement | 同上 |
| **Claude Code** | `CLAUDE.md` | 无强制 enforcement | 同上 |

> **通病**：AI 编程工具普遍存在"约定写了但无 enforcement"问题——约定文件是人类给 AI 的"建议"，AI 可遵守也可忽略，无机械门禁强制。这是 AI 辅助开发的系统性风险。

ZephyrAlpha 的 N-06（主动放弃强制数字序号制，只校验 scope 前缀）+ N-17（warning 不阻断）是同一病态的本地表现——SSoT 规则写了，但执行层主动放弃 enforcement。

**治本**：SSoT 规则必须与 enforcement 脚本**机械联动**（R4），否则 SSoT 修订无法落地。本报告 §8 记录的阶段 B 施工即解决此 gap——`_validate_ssot_linkage()` 函数在脚本启动时校验 SSoT 与脚本正则一致性，SSoT 改了脚本没跟则报错阻断。

---

## 5. 病根分析（四层）

### 5.1 层 1：SSoT 自洽性

**病根**：trae_028 同一文件内两条规则对"派生 module_id 是否需要数字序号"判定相反。

**证据**：
- L1038（修订前）：`pass: MOD-{LAYER_CODE}-{SEQ}` + `fail: 其他格式` → `MOD-ASHARE_SIGNAL`（无 SEQ）判 fail
- L1083（修订前）：`pass: MOD-ASHARE_SIGNAL 或 MOD-ASHARE_SIGNAL-NNN`（无 NNN 允许）→ `MOD-ASHARE_SIGNAL` 判 pass

**影响**：198 行派生无序号 ID 同时被判 fail 和 pass，任何自动化 enforcement 都会误判。N-06 选择"放弃强制数字序号制"是对此矛盾的逃避式妥协。

**根因**：L1038 与 L1083 由不同裁定（#206 vs #207 R3-4）在不同时间引入，各自只看到标识符的一个需求（稳定 vs 可读），未做跨规则一致性校验。

### 5.2 层 2：历史违规堆积

**病根**：5630 行 MOD-* 前缀 blueprint_id 中 627 行格式不合规（技术违规 26 + 待语义判定 601）。

**证据**：ro SQL 实测（见 §1.3 表）。

**影响**：
- 26 行技术违规（纯数字 5 + 下划线错误 21）：格式明确错误，无语义争议，阶段 C 批量重编号
- 601 行待语义判定（MOD-XXXX 单字/层代码无序号）：需逐类判定归属双轨哪一轨，阶段 D 处理

**根因**：历史无 enforcement（层 4），违规 ID 在缺乏门禁的环境下持续累积。

### 5.3 层 3：议题登记缺失

**病根**：#ARCH-XXX 架构议题编号无中央注册表，靠 grep-and-claim 占位。

**证据**：[registry_of_registries.yaml](file:///d:/ZephyrAlpha/docs/registry_of_registries.yaml) L515-516 仅 ISS-003，无架构议题注册表；[schema_health_root_cure_plan.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/schema_health_root_cure_plan.md) 附录B 用 #ARCH-008~017 占位但从未正式登记。

**影响**：#ARCH-XXX 编号可能冲突/重复/无法追溯，议题状态（open/decided/deprecated）无统一管理。

**根因**：架构治理早期未建立议题登记机制，依赖文档内联引用，缺乏中央真源。

### 5.4 层 4：enforcement gap

**病根**：N-06 主动放弃强制数字序号制，N-17 warning 不阻断。

**证据**（阶段 B 修订前）：
- [check_naming_convention.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py) L249（修订前）：`# N-06: ... 数字序号制 MOD-{LAYER}-{SEQ} 检测为阶段 E 议题，裁定#206 B-4 立议题不施工，当前仅校验 scope 前缀`
- L1025-1036（修订前）：N-17 作为 warning 不阻断，理由"阶段 E 议题"

**影响**：SSoT 规则写了但执行层不 enforcement，违规 ID 持续累积（层 2 的直接原因）。

**根因**：AI 编程社区通病（§4.4）——约定与 enforcement 脱钩，SSoT 修订无法机械落地。

---

## 6. 双轨制方案论证

### 6.1 为什么不选 A/B/C 单选

| 方案 | 描述 | 破坏的需求 | 违背的对标 |
|---|---|---|---|
| **A 强制数字序号制** | 所有 module_id 必须 `MOD-{LAYER}-{SEQ}` | 198 行派生 ID 的语义可读性 | K8s name 范式 / Natural Key |
| **B 全派生语义制** | 所有 module_id 必须 `MOD-{DOMAIN_FRAGMENT}` | 4805 行 layer-master ID 的稳定引用 | K8s UID 范式 / Surrogate Key |
| **C 保留现状不治理** | SSoT 矛盾未除，enforcement gap 持续 | automation 永远误判，技术债累积 | ALCOA+ Consistent |

三方案均只满足标识符的一个需求而破坏另一个，非治本之策。

### 6.2 双轨制 = layer-master 轨 + domain-functional 派生轨

**layer-master 轨**（layer-master 出生）：
- 格式：`MOD-{LAYER_CODE}-{SEQ}`（序号必填）
- 角色：UID（稳定不透明）
- 对标：K8s UID / Surrogate Key
- 适用：模块直接归属某层（无域语义），如 `MOD-L00-001`、`MOD-INF-005`
- 序号：3 位（上限 999/层），与 trae_028 L448 容量评估一致

**domain-functional 派生轨**（domain 出生）：
- 格式：`MOD-{DOMAIN_FRAGMENT}[-NNN]` 或 `D-XXX-{SEQ}`（序号可选）
- 角色：name（语义可读）
- 对标：K8s name / Natural Key
- 适用：模块归属某功能域，如 `MOD-ASHARE_SIGNAL`、`MOD-ASHARE_SIGNAL-001`、`D-MKT_DATA-001`
- 序号：可选，因 name 本身已含语义区分度；同域多模块时加序号区分

### 6.3 双轨判定：token 共享测试

机械化判定一个 module_id 属于哪一轨：

```
1. blueprint_id 去前缀：MOD-ASHARE_SIGNAL → ASHARE_SIGNAL；D-MKT_DATA-001 → MKT_DATA
2. domain_id 去前缀：D-ASHARE_SIGNAL → ASHARE_SIGNAL
3. 分词：按 _ 拆分 → {ASHARE, SIGNAL} / {MKT, DATA}
4. 交集测试：两词集有交集 → 属派生轨；无交集 → 属 layer-master 轨
```

**示例**：
- `MOD-ASHARE_SIGNAL` vs domain `D-ASHARE_SIGNAL`：词集 {ASHARE, SIGNAL} ∩ {ASHARE, SIGNAL} = {ASHARE, SIGNAL} 非空 → 派生轨 ✅
- `MOD-L00-001` vs domain `D-GOVERNANCE`：词集 {L00, 001} ∩ {GOVERNANCE} = ∅ → layer-master 轨 ✅
- `MOD-INF` vs domain `D-GOVERNANCE`：词集 {INF} ∩ {GOVERNANCE} = ∅ → layer-master 轨，但缺序号 → 技术违规（阶段 C 补序号）

此测试已实现为 check_naming_convention.py 的 helper 函数（阶段 B B2 落地）。

---

## 7. 裁定#208 R1-R8 摘要

| 裁定项 | 判定 | 理由 | 状态 |
|---|---|---|---|
| **R1** SSoT 双轨制调和 | trae_028 L1037-1040 改 scoped 双轨制；L1082-1085 删自指循环 | 第一性原理双需求 + K8s name/UID 对标（§3/§4.1） | ✅ 阶段 A 完成 |
| **R2** 派生 ID 合规性 | 198 行派生无序号 ID 属派生轨合规，保留 | 派生 ID 含 domain 语义片段已有区分度，序号可选符合 K8s name 范式 | ✅ 阶段 A 蕴含 |
| **R3** 历史违规分类治理 | 26 行技术违规（阶段 C 批量重编号）+ 601 行待语义判定（阶段 D 逐类判定） | 技术违规无争议可批量；语义违规需人工/AI 判定 | ⏳ 阶段 C/D 待施工 |
| **R4** 门禁执行升级 | N-06 双轨正则 + N-17 升阻断（过渡期 --warn-only） | SSoT 必须与 enforcement 脚本机械联动（§4.4 enforcement gap） | ✅ 阶段 B 完成 |
| **R5** 派生标识符注册表结构化 | derived_identifier_registry 新增 sequence_required/format_pattern/scope | 派生 ID 序号要求从"内联文字"升级为"结构化字段" | ✅ 阶段 A 完成 |
| **R6** 议题登记机制建立 | 新建 architecture_issue_registry.yaml 作 #ARCH-XXX 真源 | ALCOA+ Complete 维度（§4.3） | ✅ 阶段 A 完成 |
| **R7** #ARCH 编号铁律 | 6 条铁律写入 registry 头部 | 编号管理必须有规则，否则分配混乱重现 | ✅ 阶段 A 完成 |
| **R8** 循环验证 3 轮 | 阶段 E 循环审查至 0 残留，轮数 3（高于项目标准 2） | 自指悖论（AI 写规则+AI 写测试同源盲区），机械变异正交 | ⏳ 阶段 E 待施工 |

> R1-R8 完整论证见 [主 plan §五](file:///d:/ZephyrAlpha/.trae/documents/module_id_dual_track_governance_plan.md)。

---

## 8. 阶段 A/B 施工实测

### 8.1 阶段 A 落地证据（commit `2fb6b993d`）

| 文件 | 修改 | 验证 |
|---|---|---|
| trae_028_doc_structure_naming.yaml | v1.2.0→1.3.0；L1037-1040 双轨制 condition + L1082-1085 派生规则引用双轨主格式 | Read 核实 L1037-1040 / L1082-1085 内容（§2.3） |
| derived_identifier_registry.yaml | entry_schema + 4 entries 增 sequence_required/format_pattern/scope | 阶段 A 验证 |
| architecture_issue_registry.yaml（新建） | #ARCH-019 + #ARCH-008~018 + 编号铁律 6 条 | Read 核实全文（§2.4） |
| registry_of_registries.yaml | REG-ARCH-ISSUE-001 条目 + 统计 49/14 | 阶段 A 验证 |

**SSoT 矛盾消除验证**：trae_028 两处规则现在一致使用 `[-NNN]` 表示法，L1038 与 L1084 无矛盾（§2.3）。

### 8.2 阶段 B 落地证据（commit `5dfa2c650`）

**N-06 双轨正则 + helper**：
- [check_naming_convention.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py) L258-263：三个双轨正则常量 `_MODULE_ID_LAYER_MASTER_RE` / `_MODULE_ID_DOMAIN_DERIVED_RE` / `_MODULE_ID_D_PREFIX_RE`
- L270-316：`_check_n06_dual_track_format()` helper（scope 前缀通过后校验双轨格式）

**N-17 升阻断逻辑**（[L1136-1157](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py#L1136-L1157)）：
```python
# 裁定#208 R4: N-17 升为阻断（过渡期 --warn-only 时仍 warning 不阻断，阶段 E 激活后默认阻断）
n17_violations = [v for v in all_violations if v.rule == "N-17"]
other_violations = [v for v in all_violations if v.rule != "N-17"]
...
blocking_count = len(other_violations) + (len(n17_violations) if not args.warn_only else 0)
```
过渡期 `--warn-only` 时 N-17 warning 不阻断；阶段 E 移除 `--warn-only` 后 N-17 正式阻断。

**SSoT 机械联动校验**（[L1019-1062](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py#L1019-L1062)）：
`_validate_ssot_linkage()` 函数校验 SSoT(trae_028)与脚本双轨正则一致性：version≥1.3.0 + 双轨制关键词存在 + 脚本双轨正则已定义。

**apply_depgraph.py --mark-invalid**（[L1048-1084](file:///d:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1048-L1084)）：
`mark_blueprint_invalid()` 函数将 blueprint_id 标记为 invalid（软标记，不删除节点，保留可追溯链），供阶段 C/D 重编号专用。

**.pre-commit-config.yaml 过渡期配置**（[L180-188](file:///d:/ZephyrAlpha/.pre-commit-config.yaml#L180-L188)）：
GATE-11 hook 添加 `args: ["--warn-only"]`，过渡期 N-17/N-06 历史违规不阻断，阶段 E 激活后移除转硬阻断。

### 8.3 阶段 B 实测验证（2026-06-26）

**SSoT 联动校验实测**：
```
$ python scripts/governance/d3_metadata/check_naming_convention.py --validate-ssot
✅ SSoT(trae_028 v1.3.0) 与脚本双轨正则机械联动一致（裁定#208 R4）
EXIT=0
```

**双轨制单测实测**：
```
$ python -m pytest tests/unit/test_check_naming_convention_dual_track.py -q
collected 22 items
tests\unit\test_check_naming_convention_dual_track.py .................. [ 81%]
....                                                                     [100%]
============================= 22 passed in 0.30s ==============================
```

22 tests 覆盖：layer-master pass/fail、domain-derived pass、D-prefix pass/fail、下划线错误 fail、纯数字 fail、MOD-INF 格式层 pass、多值混合、代码块跳过、去重、SSoT 联动返回 True。与 62 现有测试合计 84 pass 无回归。

---

## 9. 数据偏差说明

### 9.1 立项估算 vs 实测偏差

| 指标 | 主 plan §2.4 估算 | ro SQL 实测 | 偏差 |
|---|---|---|---|
| 技术违规（阶段 C） | ~125 行（层代码无序号 105 + 纯数字 5 + 下划线错误 15） | 26 行（纯数字 5 + 下划线错误 21） | -99 行 |
| 待语义判定（阶段 D） | 895 行（单字描述名） | 601 行（单字/层代码无序号） | -294 行 |
| 派生无序号（R2 保留） | 268 行 | 198 行 | -70 行 |

### 9.2 偏差根因

1. **#206-阶段D 已 renumber 75 nodes**：#206 阶段 D（节点路径改名传播）已对 75 个 nodes.path + 1 个 blueprint_links.blueprint_path 重新编号，部分违规 ID 已在此过程中修正。
2. **数据演化**：立项时（主 plan §2.4）与实测时（本报告）之间有数据变动（新增/删除节点）。
3. **分类方法差异**：主 plan §2.4 区分"层代码无序号 MOD-XX 105"与"单字描述名 MOD-XXXX 895"两类；实测探针按 fragment 长度拆分（≤2=layer_code / 3+=description），但实际 layer code 如 `INF` 长度 3，故 layer_code_no_seq=0，全部并入 single_word=601。

### 9.3 对施工的影响

- **阶段 C 工作量减少**：技术违规从 ~125 行降至 26 行，重编号映射表更小，风险更低。
- **阶段 D 工作量基本持平**：601 行待语义判定（含原"层代码无序号"+ "单字描述名"两类），需在 D1 决策树中统一分类（layer_code 缩写匹配 → 归 layer-master 轨补序号；domain_fragment 匹配 → 归派生轨保留；无匹配 → 损坏清理）。
- **数据以实测为准**：阶段 C/D 施工时用 ro SQL 复测确认最新清单，不依赖主 plan §2.4 旧估算。

---

## 10. 治本施工路线图

### 10.1 阶段 A-E 摘要与当前进度

| 阶段 | 内容 | 风险 | 状态 | commit |
|---|---|---|---|---|
| A | SSoT 规则治本 + 注册表结构化（R1/R5/R6/R7） | 低 | ✅ 完成 | `2fb6b993d` |
| B | 执行层门禁升级（R4：N-06 双轨 + N-17 阻断 + SSoT 联动） | 中 | ✅ 完成 | `5dfa2c650` |
| C | 技术违规重编号（26 行：纯数字 5 + 下划线错误 21） | 高（首次改 DB） | ⏳ 待施工 | — |
| D | 语义判定 + 损坏清理（601 行 MOD-XXXX 分类） | 中高 | ⏳ 待施工 | — |
| E | 循环验证 3 轮 + 门禁激活阻断（R8） | 中 | ⏳ 待施工 | — |

### 10.2 阶段 C/D/E 待施工项

**阶段 C**（高风险，首次改 DB）：
- C1：ro SQL 实测确认 26 行技术违规全量清单
- C2：重编号映射表（⚠️ 暂停确认点）
- C3：apply_depgraph.py 执行重编号（改前 git commit 备份；⚠️ `generate_project_depgraph_artifact.py` 已删除，depgraph.db 是唯一真源，见 AGENTS.md §11）
- C4：audit_rename_completeness.py 验证改名传播完整

**阶段 D**（中高风险）：
- D1：601 行 MOD-XXXX 语义分类（layer_code vs domain_fragment vs 损坏）
- D2：语义分类映射表（⚠️ 暂停确认点）
- D3：执行语义重编号
- D4：损坏 ID 清理（--mark-invalid）
- D5：模板/蓝图一致性验证（⚠️ 暂停确认残留违规数）

**阶段 E**（中风险）：
- E1：移除 --warn-only，激活 N-06/N-17 阻断
- E2：循环验证 3 轮至 0 残留（R8，高于项目标准 2 轮）
- E3：commit + #ARCH-019 状态更新

> 阶段 C/D/E 详细步骤见 [主 plan §七](file:///d:/ZephyrAlpha/.trae/documents/module_id_dual_track_governance_plan.md)。

---

## 11. 风险与缓解（Top 5）

| # | 风险 | 严重度 | 缓解 |
|---|---|---|---|
| 1 | 改 depgraph.db 数据损坏/丢失 | P0 | 改前 git commit 备份；用 apply_depgraph.py 不直接改 .db；制品用只读 artifact 生成器（onboarding STEP 4.15） |
| 2 | commit 误扫入无关修改（工作树有其他 session 文件） | P1 | --files 精确指定；commit 后 git show --stat 核验 |
| 3 | 语义判定（601 行 MOD-XXXX）误分类 | P1 | D1 决策树 + D2 暂停确认；token 共享测试机械化判定减少主观性 |
| 4 | N-17 升阻断后阻塞开发（历史违规未清零时） | P1 | 过渡期 --warn-only（B7）；阶段 E 激活前确保 C/D 违规清零 |
| 5 | SSoT 与脚本联动断裂（trae_028 改了脚本没跟） | P2 | B4 SSoT 机械联动校验（`_validate_ssot_linkage`）；阶段 E 循环验证 3 轮 |

---

## 12. 附录

### 12.1 Fresh SQL 探针脚本（实测后已清理）

探针路径：`scripts/_tmp_bp_dist.py`（ro 模式，数据采集完成后按零残留铁律删除）

核心逻辑：
```python
import sqlite3, re
c = sqlite3.connect("file:data/databases/depgraph.db?mode=ro", uri=True)
# 按 layer_master / derived_no_seq / single_word / pure_number / underscore_error 分类
# 输出 total_nodes / distinct_blueprint_id / MOD_prefix_rows / 各分类计数 / D_prefix / invalid
```

### 12.2 量化数据原始输出（2026-06-26 实测）

```
total_nodes=6501
distinct_blueprint_id=846
MOD_prefix_rows=5630
  layer_master_MOD-XX-NNN: 4805
  derived_no_seq_MOD-XX_YYY: 198
  layer_code_no_seq_MOD-XX_2letter: 0
  single_word_MOD-XXXX_3plus: 601
  pure_number_MOD-NNN: 5
  underscore_error_MOD_XX: 21
D_prefix_rows=0
blueprint_id_invalid=1 rows: 0
```

### 12.3 关键文件绝对路径清单

**裁定与调研文档**：
- `D:\ZephyrAlpha\docs\_working\blueprint_id_naming_root_cause_report.md` — 裁定#206 主文档
- `D:\ZephyrAlpha\docs\_working\ssot_completeness_root_cause_report.md` — 裁定#207
- `D:\ZephyrAlpha\.trae\documents\module_id_dual_track_governance_plan.md` — 裁定#208 主 plan
- `D:\ZephyrAlpha\.trae\documents\adjudication_208_module_id_dual_track.md` — 裁定#208 裁定文档

**规则真源（SSoT）**：
- `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` — 命名规则 SSoT（v1.3.0 双轨制）
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\derived_identifier_registry.yaml` — 派生标识符注册表
- `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\architecture_issue_registry.yaml` — 架构议题注册表

**执行层（门禁脚本）**：
- `D:\ZephyrAlpha\scripts\governance\d3_metadata\check_naming_convention.py` — N-06/N-17 实现
- `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` — 全景图操作主工具
- `D:\ZephyrAlpha\scripts\governance\audit_rename_completeness.py` — 改名完整性审计（裁定#207 R1）
- ~~`D:\ZephyrAlpha\scripts\governance\generate_project_depgraph_artifact.py`~~ ⚠️ 已删除（2026-06-26）— depgraph.db 是唯一真源，见 AGENTS.md §11

**数据现状**：
- `D:\ZephyrAlpha\data\databases\depgraph.db` — 量化数据真源
- `D:\ZephyrAlpha\docs\03_modules\module_registry.yaml` — module_id 登记
- `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` — 蓝图登记

---

> **报告版本**：v1.0（2026-06-26 首次产出）
> **关联裁定**：#208（承接 #206 B-4 阶段 E）
> **关联议题**：#ARCH-019（status=decided）
> **下一步**：阶段 C 技术违规重编号（待用户确认后施工）
