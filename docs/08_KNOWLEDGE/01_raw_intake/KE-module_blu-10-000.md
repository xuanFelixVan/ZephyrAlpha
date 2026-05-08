---
module_id: KE-module_blu-10-000
title: 10. 禁止行为
category: module_blueprint
---

# 10. 禁止行为

10. 禁止行为

| 禁止行为 | 原因 | 替代方案 |
|------|------|------|
| 创建蓝图时不声明 `belongs_to` 字段 | AI 无法判断蓝图在金字塔中的位置 | 按 §6.1 声明 `belongs_to` |
| 将 Level 2 模块蓝图混放在 Level 0/1 的 `_` 前缀目录下 | ID 命名空间混乱，层次关系不可恢复 | Level 2 放入 `l{NN}_{name}/{module}/` |
| Level 2 模块蓝图文件名用 `{module}-blueprint.md` | 目录名已经承载模块名，重复 | 统一用 `blueprint.md` |
| 在 Level 2 模块蓝图中定义跨系统的 CT-* 合同 | 合同应该在上级（域蓝图/总蓝图）——跨系统合同如果写在具体蓝图里，改一个模块会漏更新合同影响所有系统 | CT-* 合同的定义放 Level 1 域蓝图或 Level 0 总蓝图。Level 2 只引用 CT-* 编号 |
| AI 新 session 跳过 Level 0 直接读 Level 2 | 缺跨系统上下文——"这个模块的上游是谁"不知道 | 按 §7.1 逐级下钻 |
| 在既存蓝图 frontmatter 中加入 `belongs_to` 时，改 module_id 或 status | 仅新增 frontmatter 字段即可 | 不改其他 frontmatter 字段 |
| 为已被覆盖的功能域创建平行蓝图——需要新范围时应升级原蓝图（版本号 + changelog），而非创建同级新蓝图 | MOD-INF-003/004→006 的反模式：创建"任务卡KMS"和"双管线"两个子域蓝图，后发现它们都属于"任务系统"更大的功能域，又创建 006 来合并——根源是跳过功能域重叠检查（GOV-MOD-001 §7 #5） | 升级优先级：① 升级原蓝图（version bump + changelog 在既存蓝图中新增节）→ ② 拆分原蓝图为父蓝图 + 子蓝图（须声明 `responsibility_domain` + `covers[]`）→ ❌ 禁止创建平行蓝图后"合并" |

---
