---
module_id: KE-module_blu-16-006
title: 16. 变更记录
category: module_blueprint
---

# 16. 变更记录

16. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|------|
| 1.1.0 | 2026-05-06 | **SSoT 操作化——§10 新增禁止行为 #7 + §3.3 升级为创建条件+前置闸门双列表**。根源：MOD-INF-003/004→006 的"平行蓝图后合并"反模式——003 和 004 分别覆盖了 006 功能域的子范围，而现有规则只禁止结构性违规（缺 belongs_to、错目录、错命名），不禁止功能性重叠。修复：(1) §10 #7 明确禁止为已被覆盖的功能域创建平行蓝图，需要新范围时必须升级原蓝图；(2) §3.3 表新增"前置闸门"列——Level 2 创建前 MUST 通过 GOV-MOD-001 §7 #5 功能域重叠检查；(3) 定义替代方案优先级：① 升级原蓝图 → ② 拆分 + responsibility_domain → ❌ 禁止平行蓝图。对标：唯一真源原则的操作化落地。版本号 minor +1。 |
| 1.0.0 | 2026-05-04 | 初始版本。建立蓝图三级金字塔体系：(1) Level 0 ⇒ 全系统总蓝图 `_system-master/`，(2) Level 1 ⇒ 域集成蓝图 `_domain-{layers}/`，(3) Level 2 ⇒ 模块蓝图 `l{NN}_{name}/{module}/blueprint.md`。定义 `belongs_to` frontmatter 字段、14 层 ID 前缀表、既有 19 份蓝图归属清单。AI 冷启动 6 步定位路径。对标 Codified Context 三层内存模型。禁止行为 6 条。1 瞬态豁免——既存蓝图不强制立即声明 `belongs_to`，experimental 结束时触发。关联决策线：`R85`（本决策在 architecture-rationale-log.md 中的记录）|
