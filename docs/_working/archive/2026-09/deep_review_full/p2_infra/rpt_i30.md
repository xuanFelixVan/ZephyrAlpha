---
ttl: task_bound
title: 深度审查作业簿——提交门禁链own-scope机制
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：提交门禁链own-scope机制（I30）

- 状态: **已审**
- 级别: P2｜类型: 门禁
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/gov_enforcement/commit_gates/_diff_helpers.py:475`（_build_own_scope）/:517（_audit_foreign_staged）+ `docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml`（total_gates=169，own_scope:true=26，机生由 scripts/governance/generators/generate_gate_registry.py）
- 生产调用方: 27 个 gate 文件 import _build_own_scope；全部 gate 经 GitCommitGateway CommitGateRegistry 装配（git_commit_gateway.py:8 头注）
- 测试文件: 分散于 tests/governance/（own-scope 语义未集中测试，长尾）
- 备注: 宪法 §3 作用域与连坐机制的承载件；审计 .runtime/gate_audit/*.jsonl

## 1 对象快照

- 审查范围：own-scope 核心三件（_build_own_scope/_attribute_foreign/_audit_foreign_staged）+ _diff_helpers 的 AST 豁免层（docstring 行/SQL 常量行/diff 行号解析，R95/R96 治本件）+ gate_registry.yaml own_scope 字段生态 + CAP-CONSISTENCY 代表性 gate 的 own-scope 接线。
- 排除项：118 个 gate 文件逐个内容审（I18 已覆盖 capability 系，I29 已覆盖 gateway 装配层）；protected_paths_gate 全文。
- 测试覆盖概况：R95/R96 治本有案例锚测试；own-scope 的 scope 构建/归因/审计三函数未见的集中单测。
- 材料包缺项：无近 N 天 foreign_staged 审计 jsonl 实况（.runtime/gate_audit/ 未取样——运行时证据包缺）。
- 变更热力：commit_gates 目录为全仓最高频改动区之一（每新增 gate 必触）；_diff_helpers 本体 2026-08 有 EOL 幻影行治本（:203-207）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗 | **scope=None 回退全量扫描**：files 与 session 归属均空时退回旧行为（扫全量 staged）——对未注册会话/历史直调是保守正确方向；但意味着「不注册 session 的提交路径」反而吃最严扫描，与"隔离施工=默认"的激励方向相反（注册了反而只扫自己的文件）；恶意会话可用注册+空 claim 收窄被扫面 | _diff_helpers.py:475-501（"返回 None…调用方退化为旧行为"） | P2 | 构造 files=[]+session_id=None 调 own-scope gate 对比扫描面 |
| E 对抗 | **外来 staged 违规=warn+审计不阻断**（宪法 §3.1 设计）：连坐防护的代价=外来文件的真实违规只留 jsonl——若审计文件无人消费（grep 未见 aggregator/告警读取 .runtime/gate_audit/），外来违规=静默沉淀（"warn+审计"退化为"只审计"） | _diff_helpers.py:517-547 + grep 全仓无 gate_audit 消费方 | P2 | `grep -rn "gate_audit" src/ scripts/` 排除写入点即证 |
| A 深度 | 归因窗口竞态（良性）：_attribute_foreign 用 list_active 快照对 foreign_norm——他会话 claim 变更中的归因可能 unknown；仅影响审计质量不影响阻断语义 | _diff_helpers.py:503-515 | P3 | code review |
| D 旁系 | **own_scope 覆盖率 26/169（15%）且无「全仓扫描理由」字段**：宪法 §3.3 要求新 gate 必须 own-scope 或登记全仓扫描理由——注册表只有 own_scope 布尔（机生 ✓）没有理由字段，143 个 false 条目无法区分"遗留豁免"与"违规未登记"；§3.3 合规不可机械核验 | gate_registry.yaml（own_scope 字段无伴随 reason 字段）+ 宪法 §3.3 | P3 | 抽 5 个 own_scope:false 新近 gate 查其 commit 是否附理由 |
| A 深度 | R95/R96/diff 行号三层 AST 豁免全部 fail-open 方向=「宁误报不漏检」（ast.parse 失败返回空豁免集）——与门禁语义正确对齐（正面确认）；EOL 幻影行治本（:203-207）有实证叙事 | _diff_helpers.py:110-126, 163-179, 194-228 | — | 复跑相关案例测试 |
| E 对抗 | worktree 内 commit 跳过搭便车三 gate（_WORKTREE_SKIP_GATES 单一真源，:2191-2196）：物理隔离下无检测对象——但内容型 gate 在 worktree 路径如何取 staged 内容（worktree 的 index ≠ 主区 index）未在本次抽样内核验；若内容 gate 在 worktree 路径静默空转=门禁旁路面 | git_commit_gateway.py:2191-2196（skip 真源）+ 抽样 gate 未做 worktree 分支核对 | P2 | 在 worktree 中 stage 一个违规内容文件跑 commit，观察内容 gate 是否触发 |
| C 下游 | F1 衍生并入与 own-scope 交互：折叠的 rules_integrity_db.json 进 reconciler 批——own-scope 按 held_files 归属扫描，衍生文件归属台账（R-04 派生写入归属）已铺；未发现新增旁路（任务问句的 I30 侧答案=未引入新洞，正向） | fe47296db5 + _build_own_scope held_files 并集语义 | — | — |
| B 上游 | lease 续租修复（I29）降低双 drain 竞态→门禁看到"半撕裂 staging 区"的窗口收窄——own-scope/连坐体系的上游稳定性改善（正向联动） | commit_queue.py:1124-1133 | — | — |
| A 深度(测试) | own-scope 三函数无集中单测（27 个消费 gate 各自隐式覆盖）；_attribute_foreign/_audit_foreign_staged 的 jsonl 内容契约无 schema 校验 | tests/governance/ | P3 | grep tests 无 _build_own_scope 直测 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| own-diff 作用域审查（只扫作者改动，外来违规降级审计） | **对等已有（方向正确）**：与 code review 平台（GitHub required checks 只对 PR diff）/lint 工具（only-changed 模式）同构；业界配套=审计需有消费闭环（dashboard/告警），本项目审计 jsonl 缺消费方=D-2 | GitHub branch protection/required status checks 文档, docs.github.com, 2025（检索受限流批次影响，URL=官方文档域）；ruff/pre-commit only-changed 惯例 |
| 门禁注册表机生（generator 产出+计数字段） | **对等已有偏强**：total_gates=169 与条目数一致（本报告实测），own_scope 字段机生——符合宪法 §4.3 文档纪律（计数用字段） | 本报告实测 + generate_gate_registry.py 在册 |
| 多租户 staged 区隔离（index 归属标记） | 立卡候选：git index 原生无 per-session 归属，业界多用 CI 隔离（每会话独立 runner）而非共享 staging 区+事后归因——本项目路线在单机多会话约束下是务实变通，长尾风险=审计归因永远尽力而为 | 受限流批次口径（Git 内部模型参照，git-scm.com/book, 存档） |

## 4 缺陷清单

1. **D-1（P2）gate_audit 审计无消费闭环**
   - 现状→证据：_audit_foreign_staged 落 jsonl（:517-547），全仓 grep 无读取方；宪法 §3.1 的"warn+审计"实际=违规留档但零触达。
   - 影响：外来 staged 违规（真问题信号：他会话在途违规/毒内容）沉淀无感知——与 884 死信积压 8 天/5510 冻结 19h 同构的"指标无人看"洞。
   - 建议修法：①最小：ops_alert_feed 或 I23 D-1 同款阈值告警（单 gate foreign_count 周增量>N→notify）；②顺手：weekly 审计汇总进 dashboard sources-status。
   - 验证法：手工追加一条高 foreign_count 记录，断言告警触发。
2. **D-2（P2）无 session 注册路径反而吃全量扫描的激励倒挂**（轴 E 行 1）：语义上保守正确，但与 RULE-WORKTREE"隔离施工=默认"叠加后，未注册路径成为全量扫描唯一入口=其提交更易被他人 staged 违规连坐出假红。建议：无注册路径的 own-scope 缺省改为「files 清单即 scope」（本次 commit 明确文件必扫），全量扫描仅保留给显式 opt-in——收口方裁定语义走向。
3. **D-3（P2）worktree 路径内容 gate 旁路面待证**（轴 E 行 5）：需一次 worktree 内违规内容提交实验定性；若坐实，内容 gate 需补 worktree staged 读取分支（`git show :path` 在 worktree 内同样可用，成本极低）。
4. **D-4（P3）§3.3 合规字段缺位**：registry 增 `scope_reason` 字段（生成器同批），143 个 false 条目分类登记。
5. **D-5（P3）own-scope 三函数集中单测缺位**。

## 5 挂起疑问

- 宪法 §3.3「新 gate 必须 own-scope 或登记全仓扫描理由」的执行台账在哪（若有审计批已核 169 条则 D-4 降级）——建议收口方查 2026-09-12 宪法切换批的验收记录。
- worktree 路径内容 gate 行为（D-3）需实验定性，本报告未能实证（环境限制：不做写操作）。
- .runtime/gate_audit/*.jsonl 的现存数据量与是否有历史真实违规（运行时证据）。

## 6 完备性自评

- 六轴全查：A（scope 构建语义/AST 豁免 fail-open 方向/diff 行号治本三案）、B（gateway/queue 上游联动）、C（审计消费方=无）、D（registry 机生生态+宪法 §3.3 合规面）、E（五问：静默失败=D-1、假阳性=激励倒挂、断了没人知道=D-1 同体、重放=own-scope 与重跑无冲突、时序=归因竞态良性）、F（受限流批次影响，来源口径如实记）。
- 长尾：118 gate 文件逐一未审（按抽样+I18/I29 交叉）；protected_paths_gate 未审；generate_gate_registry.py 自身未审（机生件真源）。
