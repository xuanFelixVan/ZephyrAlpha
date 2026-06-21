---
module_id: KE-022-------------blueprint-cod-006
status: active
title: 6.14 蓝图-代码同步强制约定（Blueprint-Code Synchronization Mandate）
category: agent_instruction
---

# 6.14 蓝图-代码同步强制约定（Blueprint-Code Synchronization Mandate）

6.14 蓝图-代码同步强制约定（Blueprint-Code Synchronization Mandate）

> **v1.0.0（2026-05-03）**：触发条件——任何对蓝图覆盖范围内的源码文件进行创建/修改/删除/移动操作。对标 ITIL SACM → CI Registration（配置项创建后必须立即注册到 CMDB）/ Kubernetes Admission Controller（未注册资源拒绝进入集群）/ AWS Kiro Hooks（代码变更后自动更新 spec 文档）/ SDD Design-Sync Policy（实现偏差必须回写设计文档）。本节是 §6.10 双层对齐闸门在蓝图层面的具体执行层——§6.10 管代码↔YAML↔MD 的架构层对齐，本节管蓝图↔代码的施工层对齐。

**核心原则**：**蓝图是代码的"地址簿"——代码变了，地址簿必须同步更新。** 蓝图 §16 路径索引声称的文件列表必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。

**为什么这个问题会反复出现**：Vibe Coding AI 的上下文记忆极短（§5.1），每次 session 结束后对"上次做了什么"毫无记忆。如果蓝图路径索引不更新，下一个 AI session 读到蓝图 §16 里写的"未实现"，但磁盘上已经有了代码——AI 会认为该模块不存在，可能重复实现或忽略已有能力。反过来，蓝图写了"已实现"但磁盘上没有文件——AI 会引用不存在的代码。

- **三层防线**（从轻到重，对标 K8s Admission Controller 三阶段）：

  | 层级 | 位置 | 机制 | 对标 | 状态 |
  |------|------|------|------|:---:|
  | **第 1 层：规则写入** | AGENTS.md §6.14（本节） | AI 施工纪律——每次创建/修改/删除代码后 MUST 更新蓝图 §16 路径索引 | ITIL SACM CI Registration | ✅ 本 session |
  | **第 2 层：蓝图标准写入** | PS-STD-002 蓝图模板 | 蓝图模板必须包含「已实现代码路径索引」章节 | SDD Design-Sync Policy | ✅ 本 session |
  | **第 3 层：CI 门禁脚本** | `validate_blueprint_code_sync.py` | 自动扫描蓝图 §16 声称的路径 vs 磁盘实际文件，不一致 → CI 失败 | K8s Admission Controller | ✅ 本 session |

- **强制同步清单**（创建/修改/删除蓝图覆盖范围内的源码文件时，以下蓝图内容 MUST 同步更新）：
  1. **蓝图 §16.1 模块路径表**——更新对应模块的"实现状态"列 + "源码路径/测试路径/配置路径"列
  2. **蓝图 §6 模块分解表**——更新对应模块的"实现状态"列
  3. **蓝图 §7.4 AI 自治权限表**——新增模块的 AI 自治权限声明
  4. **蓝图 frontmatter version**——版本号 +1（遵循 semver，新增模块 minor +1，路径修正 patch +1）

- **操作后自检**（创建/修改/删除代码后，AI MUST 立即执行）：
  1. 蓝图 §16 声称的"已实现"文件是否在磁盘上存在？（幽灵检查）
  2. 磁盘上新增的蓝图覆盖范围内的文件是否已在蓝图 §16 登记？（遗漏检查）
  3. 蓝图 §16 声称的路径是否与实际文件路径一致？（路径漂移检查）

- **禁止行为**：
  - ❌ 创建代码后不更新蓝图 §16——不存在"以后再说"
  - ❌ 修改代码路径后不更新蓝图 §16——路径漂移 = 下一个 AI session 被误导
  - ❌ 删除代码后不更新蓝图 §16——幽灵路径 = 下一个 AI session 引用不存在的文件
  - ❌ 蓝图 §16 的"实现状态"与实际不一致——状态漂移 = 下一个 AI session 误判进度

- **CI 门禁脚本 `validate_blueprint_code_sync.py`**（第 3 层）：
  - 扫描所有 `docs/03_modules/*/blueprint.md` + `docs/03_modules/*/*/blueprint.md`
  - 提取蓝图 §16 中声称"已实现"或"部分实现"的文件路径
  - 逐条验证路径是否在磁盘上存在
  - 扫描蓝图覆盖范围内的 `src/zephyr/` + `scripts/governance/` + `config/` + `tests/` 目录
  - 检测磁盘上存在但蓝图 §16 未登记的文件
  - 不一致 → CI 失败（硬阻断）
  - 注册位置：`scripts/governance/d5_architecture/validate_blueprint_code_sync.py`
  - Manifest 条目：dimensions [D5, D8], priority P0

- **专业参考**：ITIL SACM → CI Registration（配置项创建后必须立即注册到 CMDB）/ Kubernetes Admission Controller（未注册资源拒绝进入集群）/ AWS Kiro Hooks（onFileSave/onCommit 事件触发 spec 文档更新）/ SDD Design-Sync Policy（实现偏差必须回写设计文档）/ GitHub compose-workflow Design-Sync（偏差三档：minor 标注 PR / major 更新设计文档 / architectural 必须更新设计文档）

