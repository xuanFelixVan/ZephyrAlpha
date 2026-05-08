---
module_id: KE-governance-6_1_script-005
title: 6.1 SCRIPT 域（脚本治理规则）
category: governance_rule
---

# 6.1 SCRIPT 域（脚本治理规则）

6.1 SCRIPT 域（脚本治理规则）

> 来源：`scripts/governance/quality-standard.md`（SCRIPT-QUALITY-001）

| 登记号 | 规则内容 | 对应 ABS/COND | 强制方式 | 来源路径 |
|--------|---------|:-----------:|---------|---------|
| SCRIPT-001 | 审计脚本 MUST 包含 UTF-8 stdout 强制重声明（D-A-01） | — | manual | `scripts/governance/quality-standard.md` §3 D-A-01 |
| SCRIPT-002 | 审计脚本 MUST 精确捕获具体异常类型，禁止裸 except（D-A-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-A-02 |
| SCRIPT-003 | 审计脚本 MUST NOT 使用 shell=True（D-A-03） | ABS-43 | manual | `scripts/governance/quality-standard.md` §3 D-A-03 |
| SCRIPT-004 | 所有公共函数 MUST 包含完整类型注解（D-B-01） | — | manual | `scripts/governance/quality-standard.md` §3 D-B-01 |
| SCRIPT-005 | main() MUST 声明返回类型 -> None（D-B-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-B-02 |
| SCRIPT-006 | 每个 .py 文件 MUST 包含模块级 docstring（D-C-01） | — | manual | `scripts/governance/quality-standard.md` §3 D-C-01 |
| SCRIPT-007 | 所有公共函数 MUST 包含 Google Style docstring（D-C-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-C-02 |
| SCRIPT-008 | 模块级初始化 MUST 使用惰性加载，禁止 import 时有副作用（D-D-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-D-02 |
| SCRIPT-009 | 所有魔法数字 MUST 提取为命名常量（D-D-03） | — | manual | `scripts/governance/quality-standard.md` §3 D-D-03 |
| SCRIPT-010 | 异常 MUST 分级处理，禁止吞异常（D-E-01/D-E-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-E-01/D-E-02 |
| SCRIPT-011 | 脚本 MUST 支持 --warn-only 参数（D-F-01） | — | manual | `scripts/governance/quality-standard.md` §3 D-F-01 |
| SCRIPT-012 | 脚本 MUST 使用 POSIX exit codes 0/1/2（D-F-02） | — | manual | `scripts/governance/quality-standard.md` §3 D-F-02 |
| SCRIPT-013 | 脚本 MUST 注册在 script_manifest.yaml（D-F-04） | — | manual | `scripts/governance/quality-standard.md` §3 D-F-04 |

---
