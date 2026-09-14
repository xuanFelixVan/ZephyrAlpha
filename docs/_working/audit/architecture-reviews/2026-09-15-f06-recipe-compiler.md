---
ttl: task_bound
---

# 架构评审：F-06 仓位配方编译器雏形（MOD-POS-029）

- 日期：2026-09-15 ｜ 会话：st-f06combo-20260915 ｜ 变更分级：**L2 局部变更**（新增单模块，D_POSITION 域内）
- 方案真源：`docs/_working/2026-09-14-full-chain-factory-blueprint.md` §十（活性谓词机制）+ `2026-09-14-combination-layer-exhaustive-charter.md`（立项稿 v2，已裁定批准）
- 挖矿背书：蓝图附录 A（C1 条件配置空间=SMAC/TPE/Add-Tree 成熟做法；R1 内部查无）
- 能力反查：`capability_lookup.find(position/组合/仓位/grid)` 2026-09-15 实查——组合域 30+ 件全求解器，零编译器/工厂，REUSE 决策=完全不覆盖→新建

## 六项清单

| # | 项 | 结论 |
|---|---|---|
| 1 | KB 冲突 | 无。新模块是求解器群的上游工厂（产 recipe 候选），不改变任何既有求解器接口；E4/E5 判定权不移动（运动员不兼裁判） |
| 2 | 循环依赖 | 无。仅依赖 `zephyr.shared.foundation.errors` + stdlib + pyyaml；position/core 既有件不反向依赖它 |
| 3 | 可观测性 | 每 recipe 带内容寻址出生证（全维取值+折叠记录+prefix_key）；GridExpansion 报 N_raw 与折叠清单——直接服务立项稿"N 只数真正发生过的尝试" |
| 4 | 数据一致性 | schema（dict/YAML）为唯一输入真源；同 schema+context 编译结果确定性（测试断言）；谓词求值受控命名空间，异常 fail-closed |
| 5 | 回滚方案 | 纯新增文件（模块+蓝图+测试+schema YAML），revert 单 commit 即完全回滚，无存量数据迁移 |
| 6 | 性能 | 折叠先于展开（失活维贡献=1）；雏形返回全量列表，批次 A 规模（~2 万）可承受；36 万+全展开内存问题属批次 A 执行器职责，编译器接口已预留惰性化空间（folded 先记录不展开） |

## 性质声明

雏形阶段（design 态）：编译器三能力（schema 声明/活性折叠/前缀共享分组）正交实现；真回测执行、signal 前缀缓存引擎、出生证落库均属批次 A 执行器，不在本模块。接口按通用件设计（蓝图裁定 §十一-8：第二个消费者出现才提炼通用件）。

**评审结论：PASS**（Owner 授权模式下夜班自裁，依据 memory:owner-delegates-rulings-plain-language 八次实证协议）。
