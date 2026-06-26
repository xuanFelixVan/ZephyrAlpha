---
module_id: KE-018----------two-level-alignm-006
status: active
title: 6.10 双层对齐闸门原则（Two-Level Alignment Gate Mandate）
category: agent_instruction
ttl: permanent
---

# 6.10 双层对齐闸门原则（Two-Level Alignment Gate Mandate）

6.10 双层对齐闸门原则（Two-Level Alignment Gate Mandate）

> **v1.0.0（2026-05-02）**：架构文档存在三层实体——实际代码 + YAML SSoT + Markdown 视图。三层之间若靠"人记住更新"来对齐，漂移不可避免。对标 K8s Admission Controller（硬阻断） + Terraform `terraform-docs`（自动生成），需要两道 CI 闸门来保证三层永远对齐。

**核心原则**：**"冲突不该有"是对的——冲突是流程没有自动化的结果。** 把"人工记得更新"替换为"CI 闸门自动检查"，漂移在发生的那一刻就被拦截，不会累积。

- **三层实体与两次对齐**：

  ```
  [实际代码]  ←→  [YAML SSoT]  ←→  [Markdown 视图]
   src/zephyr/     architecture-     target_architecture/
   scripts/        model/            00-10*.md
       ↑              ↑                   ↑
       └── GATE-A ────┘                   │
       (代码↔YAML)                        │
                      └───── GATE-B ──────┘
                      (YAML↔MD)
  ```

- **GATE-A：实际代码 ↔ YAML SSoT（对齐1）**：
  - **触发**：`src/zephyr/` 或 `scripts/` 下创建新目录/新 `.py` 模块时
  - **检查**：扫描实际目录结构 → 交叉对比 `architecture_model/index.yaml` 中的模块登记
    - 🔴 实际存在但 YAML 未登记 → **CI 失败（硬阻断）**——必须先 `python scripts/governance/.../register_module.py` 登记
    - 🟡 实际不存在但 YAML 标为 `implemented` → **CI 警告**——更新 YAML 状态为 `planned` 或 `removed`
  - **对标**：K8s Admission Controller → 集群中不允许存在未经 Controller 批准的 Pod
  - **通俗解释**：代码里多了新文件夹但 YAML 里没登记？门禁直接挡住，不让合。就像物业——小区里多了个新建筑没在物业登记？先登记再施工。

- **GATE-B：YAML SSoT ↔ Markdown 视图（对齐2）**：
  - **触发**：YAML 文件的 `schema_version` 或内容变更时
  - **检查**：每个 YAML 分区文件记录其版本号 + 最后更新时间戳 → 对应 MD 视图文件记录其引用的 YAML 版本
    - 🔴 YAML 版本 > MD 引用版本 + YAML 新增了 MD 完全未覆盖的模块 → **CI 失败（硬阻断）**——必须先补 MD
    - 🟡 YAML 版本 > MD 引用版本但仅字段微调 → **CI 警告**——提示 MD 需同步哪些节
  - **对标**：Terraform `terraform-docs` → YAML 变了就能自动知道哪些 MD 节需要刷新
  - **通俗解释**：YAML 房产证改了，但 MD 售楼宣传册还是老版本？CI 直接报出来"宣传册落后了，更新这几页"。目标是不需要"人工翻译"——以后最好 YAML 一改，MD 自动生成对应段落。

- **CI 实施路径（分阶段）**：

  | 阶段 | 内容 | 状态 |
  |------|------|:---:|
  | **experimental（当前）** | AGENTS.md + index.md 写入原则——让 AI 每次施工前就知道双对齐是强制要求 | ✅ 本 session |
  | **beta** | 在 `check_architecture_gates.py` 中新增 GATE-A 骨架（`src/` 目录扫描 + 交叉比对） | 📋 Backlog |
  | **beta** | 在 `check_architecture_gates.py` 中新增 GATE-B（YAML 版本号 vs MD 引用版本比对） | 📋 Backlog |
  | **stable** | GATE-B 升级为自动生成：YAML 变更 → 触发 `generate_md_from_yaml.py` → MD 自动更新 | 📋 远期目标 |

- **AI 施工即时约束（experimental 生效，无需等 CI 脚本）**：
  1. **创建新 `src/zephyr/lXX/` 目录时** → AI MUST 同时更新对应 `architecture_model/layers/lXX.yaml` + `_index.yaml`（如该层是新层）
  2. **修改 YAML 中模块状态/属性时** → AI MUST 同时检查对应 MD 视图是否需同步更新
  3. **发现 YAML 与 MD 不一致时** → AI MUST 按 §6.9 冲突裁决流程处理，以 YAML 为准
  4. **每次 session 结束时** → 在 Session Log 中注明"本次是否产出了代码↔YAML↔MD 任一层面的变更"，若有 → 注明已完成了对应层的对齐

- **专业参考**：K8s Admission Controller → 硬阻断不合规的 Pod 创建 / Terraform `terraform plan` → 展示 drift before apply / GitLab CI `rules:changes` → 仅变更触发相关 job / ISO 42010 → Architecture Description 必须保持与系统实现的一致性
