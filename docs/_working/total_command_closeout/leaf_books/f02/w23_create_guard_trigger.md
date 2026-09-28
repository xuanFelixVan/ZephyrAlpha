---
ttl: task_bound
---

# 叶簿 W-23 · CREATE-GUARD 触发面登记 files_trigger（成本源=类级全树 git grep）

> 族 2（提交链解锁与治本）· 骨架行锚=`00_master_skeleton.md` L67（态 ⬜，出处「全流通§5④/§6-T3（数字经 A 册复算）」，案卷 A）
> 编译：2026-09-28，会话 st-zcloseout-20260928（Agent-H），lane HEAD=`325b69a193`。
> 状态标记：⬜ 未开工（触发面登记未见落地；本会话复读 `files_trigger: ''` 仍在 HEAD）。
> 素材真源：`dossier_A_commit_chain.md` §1 条 7a/7c/7d/6f、§4 附读、§6 第 4 条；`wave1b/chain_detox_report.md` assumed 段。
> 禁碰声明：`create_guard.py` 在兄弟 agent 热路径清单内——本叶簿只挖矿登记，施工须另行 claim。

## 1. 六向台账（对象=CREATE-GUARD 的触发面与成本）

| 向 | 内容 | 锚 |
|---|---|---|
| 上游供数 | 名册条目 `files_trigger: ''`（空串）+ `always_run: false` + `own_scope: false`——**空串≠模式**，触发面裁剪对它无效 | dossier_A §4 附读（在册条目全文）；本会话 HEAD 复读同值 |
| 下游消费 | 每条提交链全量跑（无触发过滤）；账本排名：CREATE-GUARD 1519 次/19186.1s/均 12.63s，全账第 1（第 2 CAPABILITY-OVERLAP 7619.3s） | dossier_A §1-7c（账本 `.runtime/audit/gate_execution_stats.jsonl`，1964 行，09-15→09-25） |
| 名册声明 | gate_registry 有键但空值；in_process 册条目**无 files_trigger 键**（键仅 enabled/factory_function/gate_id/module_path/register_line/source） | dossier_A §1-7a |
| 读声明的代码 | 成本四源：①L350 全暂存新增枚举 `git diff --cached --diff-filter=A`；②L373/L468 两次 rename 枚举；③L432-446 按扩展名分流；④L504-542 `_check_class_uniqueness` 对每个新增 .py 的每个 ClassDef 起一次全树 `git grep -l "^class <name>\b" -- src/zephyr/`（L527），grep 故障 fail-closed 直接阻断（L536-542） | dossier_A §1-7d；本会话复读 HEAD `create_guard.py` L525-529 见类名分块实现（「各批名字互斥…判据与逐名版全等」docstring） |
| 覆盖测试 | 无「空 files_trigger 应算病理」的用例证据在锚面出现 | dossier_A §6 第 4 条（28 条装载告警不含 CREATE-GUARD，见执法向） |
| 执法门禁 | 装载期 files_trigger 体检两道（超宽≥1000 文件/死触发零命中）都**判不到它**：空串既不超宽也非死模式 ⇒ 体检盲区 | dossier_A §1-5e（28 条告警清单）+ §6 第 4 条 |

## 2. 现状实测（基线 → 本会话）

| # | 断言 | 读数 | 锚 |
|---|---|---|---|
| M1 | `files_trigger: ''` 仍在 HEAD | 本会话 `git show HEAD:…/gate_registry.yaml \| grep -A11 "gate_id: CREATE-GUARD"` 实读：`files_trigger: ''`、`always_run: false`、`own_scope: false`、`status: active` | 本会话直读；与 dossier_A §4 附读一致 |
| M2 | 成本账 | 1519 次 / 19186.1s / 均 12.63s，占全账（141565s）≈13.6%；09-25 后窗口 105 次/2529.8s/均 24.09s | dossier_A §1-7c |
| M3 | 交接书口径「4488 次×23.4s≈105154s，最大单项」 | **不可复现**：账本最大单 gate 调用数=1519；105154s 超 74% 全门累计——次数与总量均对不上；「最大单项耗时」这半句成立 | dossier_A §1-7c（证据冲突，两数并列上报，不采 4488/105154） |
| M4 | 病理定性 | 「无登记」的说法不准：**有键但空值=无触发面过滤**；且不进任何既有告警名单 | dossier_A §1-7a + §6 第 4 条 |
| M5 | 与 own-scope 的关系 | CREATE-GUARD 读 index（L350），`own_scope: false`——即它本来就全量扫，触发面登记是唯一裁剪通道 | dossier_A §1-6f/§4 附读 |

## 3. 缺口与根因（转述）

- 根因链：空 `files_trigger` → 无裁剪 → 每链全跑 → 成本第 1；成本大头=④类级全树 grep（每新增 .py 每类一次）与①②全暂存枚举（dossier_A §1-7d）。
- 体检盲区：装载器只检「超宽/死触发」两态，空串第三态漏检（dossier_A §6 第 4 条）——修触发面时须同时补体检第三态，否则下次同类病仍静默。
- 病史：`CREATE-GUARD 阻断: 无 creation_token` 死信 48 封（dead 签名第 3 名，dossier_A §2 附表）+「字段头部不完整（ARCH-031）」10 封（第 13 名）——触发面不加裁剪，这些拦截成本照付。

## 4. 施工项（带锚）

1. 登记触发面：给 CREATE-GUARD 定 `files_trigger`（候选口径=新增 .py/.yaml/.md 等 7 扩展名，即其 L432-446 分流面，dossier_A §1-7d③），经名册再生器落册（禁手改，宪法 §9 第 5 条）。
2. 同批补装载体检第三态「空串 files_trigger 且 always_run=false」告警（dossier_A §6 第 4 条的盲区闭合）。
3. 净零声明：触发面裁剪**替代**的是现状「每链全量跑」的成本路径，不新增台（骨架册 §4 第 1 条）。
4. 施工前置：本文件在兄弟 agent 热路径清单（create_guard.py）——开工须向总筹 claim 排他窗口。

## 5. 复验命令（可重跑）

```bash
cd /d/ZephyrAlpha/.worktrees/st-zcloseout-leaves
git show HEAD:docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml | grep -A11 "gate_id: CREATE-GUARD" | grep -E "files_trigger|always_run|own_scope"
# 期望：files_trigger: '' / always_run: false / own_scope: false —— 即「无触发面过滤」三连；若 files_trigger 已非空，本叶簿 M1 失效须重挖
```

## 6. 自审闸三态

- **挖干**：已干——名册态（M1）、成本账（M2）、成本源码位（§1 读声明的代码）、体检盲区（§1 执法门禁）、死信病史（§3）五面齐锚；「4488 次」口径冲突已并列上报（M3），无未读矿脉。
- **施工中**：无——触发面登记无在途载体证据（本会话 M1 复读空值未变）。
- **未开工**：§4 四项全 ⬜；证据=M1 空值在 HEAD + 热路径禁碰声明。
