---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C02
name_zh: 失败指引锚点递送
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C02
---

# D11-C02 失败指引锚点递送

## 1. 定义
提交车道第二环节（全图 4 个 structure 节点之一，骨架 🔨）：失败时的处方递送面。决策问题=「失败时把 playbook/digest 指引锚点递送到修改者眼前了吗？」机制=git_commit.py 失败路径打印 GUIDE 锚点行（锚=commit_navigation_playbook.md+gate_digest_registry.yaml 双件）；失败退出码矩阵每行带 prescription_zh 处方列。

## 2. 六向台账

### 2.1 输入面
- CommitStatus 失败态（exit 1-10 各分支）
- 锚点命中：失败 message 与 gate_digest_registry 台账词条匹配

### 2.2 输出面
- stderr GUIDE 行：`GUIDE: 指路锚点 -> docs/.../commit_navigation_playbook.md 检索 "..."`（git_commit.py:128 实读格式串）
- 递送审计 sink：**不存在**（:116-133 函数体只含 print/logger.debug，零写盘）

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C02`（build_status=partial、verified_scope=structure、wiring_status=partial、red_reason=unwired——「递送面无审计 sink」如实登记；作业簿 04 已实弹核验并建议转 ✅，转性留总包）
- 锚双件：`docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md`+`commit_guide_sources/gate_digest_registry.yaml`（实存在盘）

### 2.4 代码模块
- `scripts/git_commit.py:216` `def _format_commit_result(result)`（图记 :109，行锚漂移 +107）
- 同文件 `:112` `_GUIDE_REL`、`:128` GUIDE 打印行

### 2.5 门禁约束
- 图面 gate_refs=[]；无门禁直接挂本环节；间接=exit 码矩阵处方列（图 exit_codes.matrix prescription_zh 11 行）即递送内容契约

### 2.6 自动化触发
- 失败即触发（同步 stderr）；无自动化观测回路（是否被读不可证）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 失败态+锚双件实存 |
| 输出面 | warn | stderr 递送在（实弹核验在案）；但零审计 sink=递送无回执 |
| SSOT真源 | warn | 图如实记 structure/🔨；作业簿建议转 ✅ 未落 |
| 代码模块 | pass | 三锚点实存（行锚漂移 +107） |
| 门禁约束 | pass | 处方列契约在图 |
| 自动化触发 | fail | 递送效果零观测（无 sink 无台账），自动化回路断 |

## 4. 缺口与建议
- 【收口最小件】给递送加一行审计 sink（append jsonl 到 .runtime/audit/guide_delivery.jsonl：时间戳×exit 码×命中词条）即可把 structure 转 production——建议与 C13 观测面同批。
- 【转性流程】骨架 🔨→✅ 转性两次被留总包未落，建议本批挖矿后随总包一次清（S05/S07/C02 三处同类）。
