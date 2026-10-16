---
doc_type: mine_subdoc
chain: governance
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
step_id: NAV-6
excavated: 2026-10-15
ttl: task_bound
---

# NAV-6 验收（nav 七段导航之六：零失败+四级准入）

## 1. 定义

施工产出物验收+Owner 审批卡；新增模块须通过 GOV-MOD-001 四级准入门控（MAD-001~005）。
SSOT：`config/nav_table_mapping.yaml#seven_stages⑥`。

## 2. 六向台账

### 2.1 输入面
- NAV-5 过双面门禁的施工产出。
- check_items 四问：run_all.py --warn-only 零失败？CI governance.yml 全量回归全绿？validate_manifest_admission.py 新增脚本过准入？新增模块过 MAD-001~005 四级筛选？

### 2.2 输出面
- 验收合格产出（Owner 审批卡固化）→ NAV-7 持续审计。

### 2.3 SSOT 真源
- `config/nav_table_mapping.yaml` seven_stages[5]。
- GOV-MOD-001 模块准入门控→`docs/01_policies_and_standards/governance/module/module_admission_policy.md` **status: planned 未创建**（文件内自declared）——本段唯一判据真源缺位。

### 2.4 代码模块
- `scripts/governance/run_all.py`（实存，审计总入口/调度器）。
- `scripts/governance/d11_compliance/validate_manifest_admission.py`（实存）。
- `.github/workflows/governance.yml`（实存，push 触发全量回归）。

### 2.5 门禁约束
- 验收硬标准：run_all --warn-only 零失败+CI 全绿——即全量审计脚本族（80+，scripts/governance/index.md 总入口实存）零红。
- 四级准入（MAD-001~005）判据文档 planned：准入语义由 validate_manifest_admission.py 机检代偿，政策文档缺位=人工裁量无对照。

### 2.6 自动化触发
- run_all.py 人工/CI 双触发；CI push 自动全量回归。

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | NAV-5 交接清晰 |
| 输出面 | pass | 验收→NAV-7 |
| SSOT 真源 | warn | GOV-MOD-001 政策文档 planned——四级准入判据真源缺位（机检代偿在） |
| 代码模块 | pass | run_all/validate_manifest_admission/CI 三件全实存 |
| 门禁约束 | warn | 准入门控的政策面 planned，仅机检面在岗 |
| 自动化触发 | pass | 双触发通道实证 |

## 4. 缺口与建议

- module_admission_policy.md 建议优先建档或正式除名（9 件 planned 打包裁定时，本件为验收段唯一判据，优先级最高）。
- MAD-001~005 若已由机检实现（validate_manifest_admission.py 内），建议把判据回写为文档或在 nav 表注明"判据在代码"，消除"政策-代码"两真源疑云。
