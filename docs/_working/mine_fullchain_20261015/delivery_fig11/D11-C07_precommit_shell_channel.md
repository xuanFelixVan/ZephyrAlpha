---
ttl: task_bound
doc_type: fig11_step_ledger
map_node: D11-C07
name_zh: pre-commit shell 门禁通道
mined: 2026-10-15
ssot: config/dev_delivery_map.yaml#D11-C07
---

# D11-C07 pre-commit shell 门禁通道

## 1. 定义
提交车道第七环节：shell 侧门禁的网关内重放通道。决策问题=「shell 侧门禁在网关临时索引通道里拿到执行权了吗？（数量以册 total_gates 字段为准）」要点（图按实查加注）：git hooks 对经网关的提交恒不触发（--no-verify），故本环不是 hook 通道而是**重放通道**——_run_precommit_channel 在 staged 校验后、git commit --no-verify 前补执 pre-commit run；own-scope=GIT_INDEX_FILE 临时索引（read-tree HEAD+仅本提交文件）；失败裁决四态（infra→warn 放行/mutation 重跑仍变异→阻断/own_failed→阻断/foreign_failed→warn 放行）。

## 2. 六向台账

### 2.1 输入面
- 本提交文件集（existing/deleted 双列）
- shell 门禁册：`docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（total_gates=191，实查条目=191；by_channel：commit-gate 100/commit-gateway 2/manual 40/pre-commit 49）
- flag：`config/flags.yaml:127` gate_precommit_run（enabled=true production，裁定#341 方案② Owner 批）

### 2.2 输出面
- None=放行 / str=阻断原因（GATE-PRECOMMIT-RUN 前缀→exit 1）
- 审计面：`.runtime/gate_audit/precommit_incremental_baseline.json`（实查在盘）+.runtime/audit/commit_block_events.jsonl event=precommit_channel_*

### 2.3 SSOT 真源
- `config/dev_delivery_map.yaml#D11-C07`（wired/production，gate_cluster=pre_commit；note 仍述「gate_precommit_run 幽灵键」=G02 旧况，见缺口）
- 骨架：05_门禁链与precommit通道.md

### 2.4 代码模块
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py:386` `_PRECOMMIT_RUN_FLAG = "gate_precommit_run"`（**已对齐在册键**，图记的 :358 旧键 gate_precommit_run_enabled 全仓已无引用）；`:553` `_precommit_run_enabled()`（flag 读取异常回退 OFF=#341 前现状，fail-safe）
- 同文件 `:3853` `def _run_precommit_channel(`（图记 :3189，行锚漂移 +664；docstring 载明裁定#341/own-scope/四态裁决/SKIP 清单/merge 跳过/D2 出锁手术）
- 同文件 `:3641` `_precommit_build_temp_index`（图记 :3091）；`:390-429` 两段式 Phase-A/B（快败子集 env ZEPHYR_PRECOMMIT_FAST_SUBSET=0 手柄；Phase-B 慢尾清单 _PRECOMMIT_SLOW_TAIL_HOOKS；CR-16 超时 900→2400s fail-closed）

### 2.5 门禁约束
- SKIP 名单（_PRECOMMIT_CHANNEL_SKIP_HOOKS）：gate-commit-gw（通道内恒真冲突）+gate-worktree-required（双重计数冲突）+gate-protected-paths（2026-09-24 四死信实证后加第三门）——flags.yaml 描述仍写两门=文档矛盾待收口（图在案）
- own-scope 铁律：外来/存量违规 warn 不阻断无辜提交人（宪法 §3.1）

### 2.6 自动化触发
- 每次经网关提交自动重放；30d 触发 2162 次（53 台挂账）；fail_fast 4 台确定性快检先行（Rx-3）

## 3. 自审闸三态

| 向 | 三态 | 依据 |
|---|---|---|
| 输入面 | pass | 文件集+册+flag 三输入实存 |
| 输出面 | pass | 放行/阻断+双审计面在盘 |
| SSOT真源 | warn | 图 note 仍述 G02 幽灵键旧况（代码已修，见 G02 件）；flags.yaml SKIP 描述两门 vs 实际三门文档矛盾未收口 |
| 代码模块 | pass | 全锚点实存且 flag 键已对齐（行锚漂移 +664） |
| 门禁约束 | pass | own-scope 四态裁决+SKIP 理由齐 |
| 自动化触发 | pass | 重放自动+超时 fail-closed+信号码瞬态拒袋 |

## 4. 缺口与建议
- 【文档收口】flags.yaml gate_precommit_run 描述的 SKIP 清单补第三门 gate-protected-paths（一处描述改版，随下批 commit）。
- 【性能观测】CR-16 实测合法门禁链 1571s 被 900s 误判——建议 health 面输出 precommit 通道耗时 p90，防再触阈值误判。
