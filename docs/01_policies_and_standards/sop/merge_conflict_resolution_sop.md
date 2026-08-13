---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: Merge 冲突处理 SOP——冲突三分法 + 标准 7 步流程（不盲选边，逐个读内容，结果留痕）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.1"
date: 2026-08-13
topic: merge_conflict_resolution
scope: global
related_issues:
  - "#ARCH-AICOLLAB-001（Git Worktree + File Lock + Task Board 三件套）"
  - "#ARCH-GIT-CLEAN-GUARD-FIX（2026-08-11 git clean 灾难——多会话环境下一切清场式操作的前车之鉴）"
depends_on:
  - 65_git_safety_governance
  - 66_commit_queue_serialization
  - construction_workflow_sop
related_modules:
  - src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py
  - src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
  - scripts/git_commit.py
---

# Merge 冲突处理 SOP——冲突三分法 + 标准 7 步流程

> 本备忘是全项目**冲突处理的唯一真源**，从 2026-08-13 "17 个 worktree 大 merge" 实战提炼：当日 4 处冲突全部按本文方法解决，零业务逻辑误判、零内容丢失。
> 性质：**操作规范（SOP）**，任何 AI 遇到 git 冲突时必须遵循。
> 关联：[65_git_safety_governance](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/65_git_safety_governance.md)（git 安全总案）｜[66_commit_queue_serialization](../../02_enterprise_architecture/07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md)（提交队列）｜[construction_workflow_sop](construction_workflow_sop.md) Step 12（施工流程 merge 环节）

## 1. 适用范围与触发场景

任何产生 git 冲突的操作都适用，包括但不限于：

| 场景 | 典型命令 |
|---|---|
| worktree 分支 merge 回主线 | `git merge ai/<sid>/<task>` / `session_worktree.py merge` |
| 主线 rebase / 分支同步 | `git rebase` / `git pull --rebase` |
| cherry-pick 移植 | `git cherry-pick <sha>` |
| stash 恢复 | `git stash pop` / `git stash apply` |
| 并行会话同改一文件 | merge 时 both modified |

**多会话环境前提**：本项目同时可能有多个 AI 会话施工。冲突现场可能混有**其他会话的 WIP**——处理冲突时的一切操作只许触碰冲突文件本身，禁止任何全区命令（见 §5 红线）。

## 2. 三铁律

1. **不盲选边**：禁止不读内容就 `git checkout --ours/--theirs` 或整文件采用某一边。盲选边 = 赌另一边的内容没价值，在多会话项目里赌注是别人的工作成果。
2. **逐个读内容**：每个冲突文件必须打开，读冲突块（`<<<<<<<` / `=======` / `>>>>>>>`）**及其上下文**，判断两边各自改了什么、为什么。
3. **结果留痕**：每处冲突怎么处理的（合并/取新/升级裁定），必须写进 commit message，供事后审计。

## 3. 冲突三分法（核心判别）

读完双方内容后，每个冲突文件必然落入三类之一：

### A 类 · 叠加型冲突（皆大欢喜）→ **合并，双方新增都保留**

**特征**：两边在同一文件的**相邻区域各加了自己的新内容**，谁也不否定谁。
**典型**：注册表 YAML 两边各加了不同条目；文档目录两边各加了不同行；import 块两边各加了不同模块。
**实战案例**（2026-08-13）：`capability_canonical_file_registry.yaml`——dev 加了 ALGO_FLOW 工具链条目，worktree 加了 SOP 文档 creation_token。处理：两组条目都进最终版。
**动作**：手工编辑，把两边的新增块都保留，删冲突标记，保持文件格式合法。

### B 类 · 迭代型冲突（一边严格更新）→ **取新版，commit message 说明理由**

**特征**：同一处内容被两边修改，但一边是**严格意义上的更新版**——版本号/时间戳/状态字段/统计数字/自动生成产物。
**判别要点**：能明确回答"哪边新、凭什么新"（如生成时间更晚、状态机流转方向正确、行数是超集）。
**实战案例**（2026-08-13）：`registry_master_index.yaml` 自动生成索引，worktree 版时间戳更新且含新注册表条目 → 取 worktree 版；`AGENTS.md` + ROOR 的注册表完工状态，worktree 版是已完成态 → 取 worktree 版。
**动作**：采用新版后，**自动生成物必须重跑生成器验证**（能重新生成即证明取舍正确）；非生成物在 commit message 写明"取 worktree/dev 版，因 XX"。

### C 类 · 互斥型冲突（真逻辑冲突）→ **AI 不自行裁决，整理差异表升级用户拍板**

**特征**：两边**修改了同一处业务逻辑且语义互斥**——同一个算法的两种实现、同一个阈值取不同值、同一段流程的两种设计。选哪边都意味着废弃另一边的意图。
**动作**：
1. 立即停止该文件的解决，继续处理其余 A/B 类文件；
2. 整理 C 类差异对照表：两边各自意图、影响面、倾向建议（可给建议但**不擅自定**）；
3. 提交用户裁定，裁定结论记录进 commit message + 相关 ARCH 议题。

**实战数据**：2026-08-13 十七个 worktree 大 merge，4 处冲突 = A 类 2 + B 类 2，**C 类 0**——session_worktree 隔离施工使各队改不同文件，天然规避了 C 类。C 类罕见不等于没有，遇到必须升级。

### 快速判别表

```
读冲突块 → 两边是"各加新内容"？        ──是──→ A 类：合并
              │否
              ▼
         一边是"严格更新版"？
         （时间戳/版本/状态/生成物）     ──是──→ B 类：取新版 + 说明
              │否
              ▼
                                    C 类：升级用户裁定
```

## 4. 标准处理流程（7 步）

```powershell
# Step 1 · 盘点冲突现场
git status                          # 列出全部 both modified 文件
git diff --name-only --diff-filter=U
```

**Step 2 · 逐个读双方内容**：打开冲突文件，读冲突块 + 上下文。不只看 `<<<<<<<` 标记之间——要看这个文件两边**各自的整体改动意图**（必要时 `git log` 查两边分支的 commit message）。

**Step 3 · 按 §3 判别分类**（A/B/C）。

**Step 4 · 分类处置**：
- A 类 → 手工合并，双方新增都保留
- B 类 → 取新版，生成物重跑生成器验证
- C 类 → 跳过该文件，整理差异表升级用户

**Step 5 · 逐文件验证**：
- YAML/注册表 → 跑对应 audit/校验脚本（如 E1-E20 审计、`check_yaml_frontmatter`）
- 代码 → 跑相关测试
- 文档 → 检查链接、编号连续性、frontmatter 完整

**Step 6 · 留痕 commit**：message 逐文件说明处理方式，示例：

```
merge: <任务名> 完工 merge 回 dev

冲突处理（4 处，A 类 2 / B 类 2 / C 类 0）：
- strategy_book.py（A）：保留 dev ALGO_FLOW 标记块 + worktree 仓位算法改动
- capability_canonical_file_registry.yaml（A）：dev ALGO_FLOW 条目 + worktree SOP token 都保留
- registry_master_index.yaml（B）：取 worktree 版（时间戳更新、含新注册表索引，自动生成物）
- AGENTS.md（B）：取 worktree 版（注册表完工状态为最新事实）
```

**Step 7 · 网关落地**：merge commit 同样走 GitCommitGateway（`scripts/git_commit.py`），禁止裸 `git commit`。

## 5. 红线（禁止事项）

1. **禁止盲选边**：`git checkout --ours/--theirs <file>` 整文件采用，唯一例外是已确认的 B 类自动生成物。
2. **禁止静默丢弃**：为解决冲突删掉任一边的新增内容，必须在 commit message 说明删了什么、为什么。
3. **禁止清场式操作**：冲突未解决完时 `git reset --hard` / `git checkout -- .` / `git clean`——多会话环境下会连带毁掉其他会话的 WIP（#ARCH-GIT-CLEAN-GUARD-FIX 教训）。想放弃整个 merge 用 `git merge --abort`，它是唯一安全的整局回退。
4. **禁止 C 类自行拍板**：业务逻辑互斥冲突升级用户，AI 可给建议不可下结论。
5. **禁止裸 commit**：merge commit 也是 commit，一律走网关。

## 6. 多会话环境特别条款

- 处理冲突前 `git status` + 看 held_files/staged 清单，确认哪些 WIP 是别人的——**别人的 WIP 一个字节都不碰**。
- 冲突文件里发现其他会话的内容（如 ALGO_FLOW 标记、别的施工队条目）：一律按 A 类保留，那是别人的成果，不是冲突噪音。
- merge 期间被 HELD-OVERLAP / WORKTREE-REQUIRED 等门禁阻断：不是冲突问题，是并发防护在正常工作——等对方释放或按 SOP Step 12 保留 worktree 作逃生通道，**不强行绕门禁**。

## 7. 实战案例存档（2026-08-13 十七 worktree 大 merge）

| 冲突文件 | 分类 | dev 侧内容 | worktree 侧内容 | 处理 |
|---|---|---|---|---|
| strategy_book.py | A | runner 的 ALGO_FLOW 标记块 | AI-POS-001 仓位算法施工改动 | 合并，两者都保留 |
| capability_canonical_file_registry.yaml | A | ALGO_FLOW 工具链条目 | AI-SOP-001 的 SOP creation_token | 合并，条目并集 |
| registry_master_index.yaml | B | 旧时间戳索引 | 新时间戳 + chart_pattern 注册表索引 | 取 worktree 版（自动生成物，取新即可再生验证） |
| AGENTS.md + ROOR | B | 注册表旧状态 | IND/EXE/FLD 三表完工状态 | 取 worktree 版（完工状态是最新事实） |

结果：17 个 worktree 全部 merge 成功，零内容丢失，零业务误判。C 类 0 次——session_worktree 物理隔离让各施工队改不同文件，从源头压平了真冲突。

## 8. 修订记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0.0 | 2026-08-13 | 初版：冲突三分法 + 标准 7 步流程 + 5 红线，源自当日 17 worktree 大 merge 实战（用户裁定立项："教科书级别处理方式写成标准 SOP"） |
| v1.0.1 | 2026-08-13 | **搬迁**：从 design_memos/67_merge_conflict_resolution_sop.md 迁至 docs/01_policies_and_standards/sop/merge_conflict_resolution_sop.md（SOP 属永久规则，与施工图纸临时区生命周期分离）；doc_type→policy（rule_form: procedural）；去编号改名 |
