---
module_id: MOD-GOV-debt-rulings
title: 架构债务 DEFERRED-PERMANENT 裁定记录（第103轮架构师裁定）——#ARCH-WORKTREE-002 session_worktree 四重缺陷治本
version: 0.1.0
layer: L2_domain
depends_on: [architecture_debt_registry, architecture_issue_registry]
tags: [ruling, architecture-debt, permanent, worktree, session-isolation]
ttl: permanent
doc_type: audit_report
completes_when: '#ARCH-WORKTREE-002 五阶段治本全部完成并验证（status=resolved）'
---

# 第103轮 DEFERRED-PERMANENT 架构裁定（裁定人：客观专业架构师，受 Owner 委托）

> 裁定原则（第一性原理 + 100% AI 开发 + 长远战略）：
> - P1 防复发 > 存量修复；P2 无回归测试不做高风险重构；P3 实际风险=0 的"违规"非债务；
> - P4 净收益必须为正；P5 可机械验证/执行的优先；P6 SSoT 唯一真源最高原则。
> - 裁定结论两类：EXECUTE（立即治本施工）/ RATIFY（确认前裁定，关闭为 wontfix-permanent 并验证防复发门禁在册）。

## 议题背景

**议题编号**：#ARCH-WORKTREE-002
**议题标题**：session_worktree 四重缺陷治本——REPO_ROOT 解析不一致 / _pre_merge_auto_clean 无回滚 / reconciler 不识别 merge / stash 堆积无自动清理
**登记日期**：2026-07-19
**裁定日期**：2026-07-19
**状态**：resolved（五阶段治本全部完成）

### 病根分析（第一性原理）

session_worktree 君子协定（FP-ISO.4C，2026-07-02）在 worktree 模式下存在 4 个独立缺陷，导致 AI 在 worktree 模式下提交时遭遇 gate 阻断、merge 状态被清理、修改丢失、stash 堆积：

1. **缺陷1（REPO_ROOT 路径解析不一致）**：blueprint_format_gate.py 用 `REPO_ROOT + sys.path` bootstrap 定位 validate_module_id_naming 模块，但在 worktree 模式下 REPO_ROOT 指向主仓库而非 worktree，导致模块加载失败 → gate 报错 → commit 阻断。

2. **缺陷2（_pre_merge_auto_clean 无回滚）**：session_worktree._execute_cleanups 在 merge 前用 `git checkout --` 清理主工作区修改，但 `git checkout --` 会永久丢弃修改（不可恢复）。实测三个文件的修改全部丢失（Select-String 验证 #ARCH-WORKTREE-002 标记消失）。

3. **缺陷3（reconciler 不识别 merge 状态）**：git_commit_gateway._commit_auto 在 merge 进行中（.git/MERGE_HEAD 存在）时仍然尝试 auto-commit，导致 "cannot do a partial commit during a merge" 错误。

4. **缺陷4（stash 堆积无自动清理）**：session_worktree 在多处 stash 临时修改（pre_merge/abort/auto-recover），但从不清理。实测 34 个 stash 堆积，部分 30+ 小时。auto-recover 机制修复了 stash 丢失 bug，但未清理过期 stash。

## 裁定结论

| 缺陷 | 裁定 | 证据与理由 |
|---|---|---|
| 缺陷1 REPO_ROOT 解析不一致 | **EXECUTE** | 100% AI 开发下 gate 阻断=AI 无法提交=开发停滞。治本：动态加载从 gateway.project_root 定位模块，消除 REPO_ROOT 硬依赖。 |
| 缺陷2 _pre_merge_auto_clean 无回滚 | **EXECUTE** | 修改永久丢失=AI 工作成果毁损，违反"备份先行"铁律（trae_054 STEP0）。治本：git stash push 替代 git checkout --（可恢复 via git stash pop）。 |
| 缺陷3 reconciler 不识别 merge | **EXECUTE** | merge 中 auto-commit=git 拒绝=merge 卡住。治本：_commit_auto 检测 MERGE_HEAD 跳过 auto-commit。 |
| 缺陷4 stash 堆积无清理 | **EXECUTE** | 34 个 stash 堆积=stash 栈污染=pop 风险。治本：post-commit reconciler 事件驱动 TTL 清理（24h 过期）。 |

## 五阶段治本方案与执行结果

### Phase 5：存量 stash 清理（已完成 2026-07-19）

- **执行内容**：34 个 stash 全部分析（blob hash 比较 + reverse-apply check），全部 drop，备份 patch 到 .runtime/reconcile_reports/stash_backup/（123MB）
- **分析报告**：stash_deep_analysis.json + stash_reverse_apply_check.json
- **验证**：stash list 清空，无数据丢失（全部备份）

### Phase 1：gate 模块 import 路径统一化（已完成 2026-07-19，commit cd53506d52）

- **执行内容**：blueprint_format_gate.py 用 importlib.util.spec_from_file_location 动态加载 validate_module_id_naming.is_valid_module_id，替换 REPO_ROOT + sys.path bootstrap
- **关键函数**：_load_is_valid_module_id(project_root) 从 gateway.project_root 定位模块；_validate_module_id_cache 按 project_root key 缓存
- **验证**：语法验证通过 + gate 构造测试通过

### Phase 3：reconciler 识别 merge 状态（已完成 2026-07-19，commit 399ab7de）

- **执行内容**：git_commit_gateway.py _commit_auto 入口检测 .git/MERGE_HEAD 存在时返回 NOTHING_TO_COMMIT，跳过 auto-commit
- **效果**：merge 状态保留供手动完成，不再被 auto-commit 干扰
- **验证**：语法验证通过 + e2e 测试通过

### Phase 2：_pre_merge_auto_clean 回滚机制（已完成 2026-07-19，代码 cb2cf154f2 + 状态登记 8770a1fa12）

- **执行内容**：session_worktree._execute_cleanups 用 `git stash push -m "session_worktree_pre_merge: <sid>"` 替代 `git checkout --`
- **效果**：tracked 文件修改保存到 stash 栈（可恢复 via git stash pop），不再永久丢弃
- **一致性**：与 session_worktree_abort 的 S3-B 治本（2026-07-17）一致；session_worktree_abort 已在 S3-B 治本中用 git stash push（无需重复修改）

### Phase 4：stash 过期清理 reconciler（已完成 2026-07-19）

- **执行内容**：新增 make_stash_lifecycle_reconciler()，post-commit 事件触发（priority=801）
- **技术实现**：
  - `git stash list --format=%gd|%ct|%s` 获取 stash ref/timestamp/message
  - 清理 > 24h 的 session_worktree 临时 stash（按 msg 前缀 `session_worktree_pre_merge` / `session_worktree_abort` 识别）
  - 保留 < 24h 的 stash（AI 可能还需要 pop 恢复）
  - 按索引降序 drop（避免 renumbering 问题——drop stash@{3} 后 stash@{4} 变 stash@{3}）
  - 不影响用户手动 stash（无 session_worktree 前缀）
- **注册位置**：GitCommitGateway._register_default_reconcilers（紧跟 worktree_lifecycle=800，在 gate_registry_sync=830 之前）
- **自维护/自关闭**：每次 commit 后自动清理，无需 AI 干预
- **验证**：33 reconcilers 注册，GATE-STASH-LIFECYCLE priority=801，trigger/reconcile 功能正确

## 防复发机制

| 防复发点 | 机制 | 状态 |
|---|---|---|
| gate 模块加载路径 | importlib 动态加载从 gateway.project_root 定位，消除 REPO_ROOT 硬依赖 | ✅ Phase 1 |
| merge 状态检测 | _commit_auto 检测 MERGE_HEAD 跳过 auto-commit | ✅ Phase 3 |
| 修改丢失防护 | _execute_cleanups 用 git stash push 替代 git checkout -- | ✅ Phase 2 |
| stash 堆积防护 | post-commit reconciler 事件驱动 TTL 清理（24h） | ✅ Phase 4 |
| 存量 stash 清理 | Phase 5 一次性清理 + 备份 | ✅ Phase 5 |

## 向内收原则验证

- **扩展 ReconciliationRegistry 框架**（第30个 reconciler），不新建独立清理系统
- **复用 _run_subprocess** 统一 subprocess 解码策略（errors='replace'）
- **复用 session_worktree 前缀约定**（session_worktree_pre_merge / session_worktree_abort），不引入新标记
- **事件驱动**（post-commit trigger），不引入时间触发或手动触发

## 相关裁定与规则

- **FP-ISO.4C**：worktree 君子协定（2026-07-02 正式版）
- **TRAE-062**：SSoT 分类铁律
- **#ARCH-DEPGRAPH-RECONCILER-FAILSILENT**：reconciler 失败静默治本
- **#ARCH-WORKTREE-001**：worktree 隔离机制基础
- **trae_054_depgraph_backup**：备份先行铁律
- **session_worktree 君子协定**：AI session 启动第一件事 MUST 执行 session_worktree_start

## 执行验证

```
RECONCILERS: 33
STASH_LIFECYCLE: True
UNDEFINED_BASELINE: True
```

- make_stash_lifecycle_reconciler 已注册（priority=801）
- make_undefined_name_baseline_reconciler 已注册（priority=211）
- import 链完整：undefined_name_gate.py + reconciliation_registry.py + git_commit_gateway.py
- architecture_issue_registry.yaml status: resolved

## 结论

#ARCH-WORKTREE-002 五阶段治本全部完成，session_worktree 四重缺陷已根除。防复发机制覆盖所有 4 个缺陷点，事件驱动 TTL 清理确保 stash 不会再次堆积。议题 status: resolved。
