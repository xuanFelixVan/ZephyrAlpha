---
ttl: task_bound
---

# 红蓝 v3 P0-1 语法门禁修复工作日志（批 2）

> 2026-09-14。执行会话 solo_agent（GLM-5.3 Flash）。规格来源=`2026-09-13-xtreme-redblue-v3-report.md`
> §1 P0-1 + §5 修复建议第 2 条 + Owner 批 2 任务书。两段式施工（写码备弹 + 接线上线）同批完成，全闭环。

## 任务与提交对账

| 任务 | 内容 | 提交 | 文件 |
|------|------|------|------|
| P0-1 | SYNTAX-VALIDATION gate 本体 + 单测 + 接线登记 | `e9e3dd6f`（7 文件原子） | gate/test/__init__/in_process_registry + 3 项配套登记 |
| 配套登记吸收 | capability 三 token + 翻译条目 | `631450cb92`（他会话提交吸收落库，git log 溯源透明） | capability/translation 两注册表 |
| 事故清库 | revert 坏文件探针提交 cf565a8a | （见文末事故节） | tests/governance/rule_bridge/xt_p01_syntaxerr.py |

## 1. 治本设计要点

- **扫描源语义（本批最重要的实战发现）**：网关 gate 链跑在 `git add` 之前
  （`_check_gates_with_drift_watch` → `_commit_locked/add`），扫描暂存区会漏拦未暂存坏文件。
  初版扫暂存区，probe 2i 实弹复验时坏文件**直接入库**（cf565a8a）——当场改为扫描
  `commit()` 的 files 参数（本 commit 真实提交清单），复验拦截成功（10:30:55 落账）。
- 检测范围含 tests/（红蓝实证坏文件恰从 tests/ 进来）；豁免只认
  `# noqa: syntax-fixture  <理由≥10字符>` 登记标记（noqa_exempt_registry.yaml 同批登记，m11 同构）。
- fail-closed：SyntaxError 阻断含文件名+行号+错误信息；非 SyntaxError 解析异常（ValueError 等）
  fail-open（环境异常非违规）；null bytes 在 Py3.12 报 SyntaxError 属真实坏源码 → 阻断。
- own-scope（#ARCH-310 R2，对标 NOQA-VALIDATION）。
- priority=49：初选 48 与 COMMIT-SCOPE 撞号，auto_registrar GateRegistrationError 实测抓出，
  按后到者让位先例（DATA-TASK 78→41 等在案）改 49。静态探针漏检原因：文件头注释抢先命中
  `priority=(\d+)` 首个匹配——教训：**priority 占位核查以 auto_registrar 实测为准**。
- worktree 通道自动生效（不进 `_WORKTREE_SKIP_GATES`，与六类跳过集合正交）。

## 2. 登记配套全记录

- in_process_gate_registry.yaml：条目追加 + total_gates 110→111 同批同步（历史漏同步教训在案）。
- commit_gates/__init__.py：`_ORPHAN_MODULE_STATIC_IMPORTS` 区块静态 import 锚定
  （ORPHAN-MODULE gate 只认静态引用，YAML 动态加载的 gate 必须前置锚定——probe 2d 撞出）。
- capability_canonical_file_registry.yaml：creation_tokens 三条（syntax-gate-20260914 /
  syntax-gate-test-20260914 / p0-syntax-gate-log-20260914）。
- module_translation_registry.yaml：大白话条目（add_module_translation.py 写入）。
- depgraph：文件节点 13260227（add-design-node 创建 → 按状态机流转
  planned→generated→testing→stable + design→production；planned→production 直达非法，
  apply_depgraph 报合法转换表）。**注意**：transition 后台自动触发 depgraph 全量重建
  （[REGENERATE] 后台进程），blueprint.md design_maturity 曾被同步为 design，节点流转
  production 后 sync 归位（工作区已核与 HEAD 一致）。
- 净零声明：本 gate 替代"语法错误由其他 gate 检测"的隐性口头约定（六处 fail-open 注释在案），
  规范总量不新增。

## 3. 验证证据

- 单测 14 passed：好文件放行 / 坏文件阻断含文件名行号 / 绝对路径入扫 / tests/ 检测 /
  noqa 放行与拒绝（短 reason）/ null-byte / fail-open（rev-parse 失败）/ GateSpec 字段。
- 实弹拦截两轮堵点本精确归因：
  - `2026-09-14T06:40:53 | commit_blocked | SYNTAX-VALIDATION | solo_agent`（首拦，探针 staged 态）
  - `2026-09-14T10:30:55 | commit_blocked | SYNTAX-VALIDATION | solo_agent`（files 语义复拦，
    探针未暂存直提——首拦盲区修复的实证）
- 全量回归：tests/governance/commit_gates/ + tests/git/test_git_commit_gateway.py = **2480 passed**。
- auto_registrar 冒烟：111/111 注册 0 failures + 守卫测试 34 passed（total_gates↔条目数一致）。
- 门禁链实弹穿行（真实提交撞墙全记录）：CAPABILITY-LOOKUP → OK / ORPHAN-MODULE（补 __init__ 锚定后过）/
  MUTABLE-CONST-WITHOUT-FINAL（`__all__` 与常量补 Final 后过）/ NO-HIGH-COMPLEXITY（_check 复杂度 18→
  拆出 _scan_py_file_syntax 后过）/ ARCH-REFERENCE（瞬态解析失败：后台 depgraph 重建进程写文件窗口期
  读取撞上，重试即过——**瞬态竞态特征**，记录不修）。

## 4. 过程事故记录（probe 2i 坏文件意外入库）

- 时序：复验 round2 时，前次失败提交的 finally 清理把探针文件撤出暂存区（`??` 未跟踪态），
  随后 probe 2i 提交经网关——gate 链扫暂存区无 .py → 放行 → `_commit_locked` 内 add → 入库 cf565a8a。
- 定性：**gate 链与 add 的时序盲区**（gate 看不到本 commit 即将 add 的内容），非门禁逻辑失效——
  正是该盲区的实弹代价证明，直接推动扫描源改为 files 参数。
- 清库方案：坏文件的删除提交必须先让文件从磁盘消失（网关 `_add_and_remove_normal_files`
  对盘上存在的文件走 git add，会把坏文件重新吸入 index）。
  磁盘删除被 AI 安全审批拦截，已移交 Owner 手动执行：删除磁盘文件后跑
  `python scripts/git_commit.py --session solo_agent --files "tests/governance/rule_bridge/xt_p01_syntaxerr.py" --message "chore(gov): 清库 cf565a8a"`。
  本 gate 同批补齐 staged-delete 跳过逻辑（index=D 且盘上无文件 → 删除提交不再被坏内容拦），
  保证上述清库命令可一次通过。

## 5. 遗留与移交

- **磁盘残留（待 Owner 手动删除，AI 删除通道被安全审批拦截）**：
  - `tests/governance/rule_bridge/xt_p01_syntaxerr.py`（探针坏文件，仍在 HEAD/磁盘；删除后按 §4 命令清库）
  - `.runtime/tmp/probe_*.py` 8 件 + `commit_msg_p01.txt`（gitignored 临时区，可留待 TTL 清扫）
- 他会话陈旧 hunk 未搭便车：module_translation_registry.yaml 工作区仍含 c4_valuation_pe_low
  陈旧改动（classify=stale_rollback，st-c4tail 会话遗留），未随本批提交，留他会话/Owner 处置。
- ARCH-REFERENCE 瞬态解析失败一例（后台重建写窗口期竞态）——记录不修，建议 Owner 关注
  depgraph 重建与提交窗口的互斥（fail-closed 语义正确，重试即可恢复）。
- 红蓝 v4 复测就绪：kickoff 在 Owner 任务书（语法坏文件双通道验收已预演通过）。
