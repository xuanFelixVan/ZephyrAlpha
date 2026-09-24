---
ttl: task_bound
title: QCure作业簿·approval_language
session: st-qcure-20260925
---
# approval_language 作业簿

## 1 环节定义与边界
审批/授权语言 = 本项目一切"这事被批准了"的机器可读表达及其真源/消费链。边界：8 形语言盘点、
交叉点、M4 适配器挂点精评、#410 字段级修补建议。不含：队列信封 M3（producer/landing 簿）、
gate 全景（gate_chain 簿）。

## 2 六向台账

### ①上游输入（8 形批准语言，真源+锚）
| # | 形态 | 真源锚 |
|---|------|--------|
| 1 | `[ARCH-APPROVAL:ARCH-*]` message 标记 | 正则唯一真源 scripts/governance/d6_security/check_protected_paths.py:69（只认 `ARCH-` 前缀，裁定号 #NNN 机械上不匹配） |
| 2 | 裁定#NNN 册 | docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml（entries 232；schema L45-55 无 scope/approved_paths/expires_at；status 四值枚举铁律 L28+L50） |
| 3 | #ARCH-XXX 议题册 | docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml（arch_reference_gate.py:133 _REGISTRY_REL） |
| 4 | `ZEPHYR_PROTECTED_PATHS_BYPASS=1` env | 双处声明：check_protected_paths.py:64 与 protected_paths_gate.py:76（注释声明对齐，弱双真源） |
| 5 | `[no-lookup:<reason>]` 白名单标记 | capability_lookup_bypass_policy.py:160 BYPASS_MARKER_PREFIX（gate 与 reconciler 双真源已收敛，:97 自证） |
| 6 | `--allow-*` 旗 | scripts/git_commit.py:1047 --allow-multi-domain（消费 :639，处方 :199）、:1084 --adopt-prior-work；gateway 字段 allow_overlap/allow_non_worktree/allow_multi_domain/allow_tracked_drift（git_commit_gateway.py:28-29） |
| 7 | creation_token | 检测 create_guard.py:703 `_check_creation_token`（registry_data 注入点 :708/:856）；批量登记 scripts/governance/d3_metadata/batch_creation_tokens.py |
| 8 | human_gate / risk_tier | risk_tier_registry.yaml:37 human_gate 字段；:31 门位变更须 Owner 签字（流程位，无 gate 机械执行者——查无，归因：宪法 §5 门禁强度由 gate 体系独立保证） |

### ②下游消费
- 形1 marker：Layer1 protected_paths_gate.py:247-256（message 逃生+审计 :132-159，priority=28）；Layer2 pre-commit merge 转置 check_protected_paths.py:288-309（**但网关通道已整体 skip 该 hook**，见④）；Layer3 手动 `--staged`。
- 形2 裁定册机械消费方（grep 全谱 30 文件，机械类 8+）：ruling_reference_gate.py:86（staged 内容新增裁定#NNN 引用硬拦，阶段2 hard block）、_reference_helpers.py:28、commit_preflight.py:336-337（RULING-REFERENCE 处方）、registry_alignment.py:495、ai_layer/redline/no_delete_manifest.py:79,88（**禁删清单条目**，禁删不禁改）、ai_layer redline annual_review/order_daemon/scheduling/switch_engine/rollout_tiers、frontend/dashboard/api_server.py、registry_ledger/baseline.py。**无一读 approved_paths（字段尚不存在）**。
- 形3 议题册：arch_reference_gate.py 只校验 **staged 文件内容中新增** #ARCH-NNN 是否登记——与 message 标记通道互不相通。
- 形4 env：Layer1 :239-244（审计 jsonl）+Layer2 :271-276（stderr）。
- **查无**：`.runtime/gate_audit/protected_paths_bypass.jsonl` 全仓仅 gate 本体+test 引用——逃生审计无任何下游读者/reconciler。
- 形6 allow_overlap：gateway :705-738 审计 + :741-787 #ARCH-264 热文件 24h 滚动窗升级阻断（语言自带超时进化，8 形中唯一）。

### ③机制现状（+业界参照）
现状=8 形各自为政：PROTECTED-PATHS 只认 message 标记（ARCH-*）；裁定册只有**登记语义**
（RULING-REFERENCE 查"引用须登记"）无**授权语义**（无路径集/有效期，无任何 gate 查它放行）；
两册编号空间互不相通（ARCH-* vs 裁定#NNN）——这就是 #410"批准对人类有效、对机械无效"的病根。
业界参照（凭知识引，未在线复核）：
- CODEOWNERS（路径→审批人数据化映射）：https://docs.github.com/en/repositories/managing-a-repositorys-settings-and-features/customizing-your-repository/about-code-owners
- GitHub 分支保护 required approvals：https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitLab approval rules（按路径/规则的 MR 审批）：https://docs.gitlab.com/ee/user/project/merge_requests/approvals/rules.html
- Kubernetes Prow approve 插件（message/命令审批语言+回执机器人）：https://github.com/kubernetes/test-infra/tree/master/prow/plugins/approve
- Google 代码评审标准（LGTM 语义最小化）：https://google.github.io/eng-practices/review/reviewer/standard.html
对照结论：业界把"路径→批准"做成**数据**（owners 文件/规则对象），M4.1 approved_paths 同构，方向正确。

### ④代码面
- 双层防线：Layer1 in-process protected_paths_gate.py:209-304（fail-open：清单加载失败降级 4 条内置最小清单 :120-128）；Layer2 pre-commit hook（.pre-commit-config.yaml gate-protected-paths）——**关键新发现：网关通道已整体跳过该 hook**（git_commit_gateway.py:401-407 `_PRECOMMIT_CHANNEL_SKIP_HOOKS` 含 gate-protected-paths，2026-09-24 四死信 0041/0050/0052/0053 实证后加入：hook 消息盲、豁免语义恰在 message 上，会无差别再杀已审批写入）→ 队列落地链实际只剩 Layer1 一道消息感知防线。
- **假号洞**：gate :249-252 对 marker 只 regex 命中即放行+审计，issue_id 不回查任何册；docstring :41 称"可被 post-commit reconciler 校验"——**查无此 reconciler**（全仓 grep approval_marker 零读者）。
- message 通道：`kwargs.get("commit_message") or kwargs.get("message")`（:247）——队列重建 message 丢标记（方案 1.3-7 已立案）。
- preflight：commit_preflight.py:115 PROTECTED-PATHS 在 18 道白名单；:313 处方写死"无 CLI 逃生旗"。

### ⑤运维/呈现面
- 审计落盘两条：protected_paths_bypass.jsonl（gate :155）与 allow_overlap_usage.jsonl（gateway :735）——均无自动读者/周报/看板（查无，归因：审计先于消费设计）。
- 手动审计模式 `--full-tree`（裁定#354）由 GateFullTreeAudit 计划任务每日 3:30 承载（schtasks 实证"就绪"）。
- 裁定册无呈现面：dashboard api_server.py:4326 仅注释提及，无裁定查询视图。

### ⑥失败态与数据面
- 死信：PROTECTED-PATHS 族 26 笔（直拦 9+hook 17，方案 §1.2 表）；其中 hook 17 笔与"09-24 起 Layer2 被跳过"互证（死于跳过之前）。
- #410 三失真（ruling_registry.yaml:5642-5660）：`status: decided` 越四值枚举（:5646）；`related_files` 非 schema 字段（:5655，schema 要求 affected_files）；summary 自称"补全 PROTECTED-PATHS 所需批文"（:5650）但 gate 机械不消费裁定号（check_protected_paths.py:69 正则）——授权链只对人类有效。
- fail-open 面：Layer1 清单加载失败静默降级 4 条（保护缩水无告警）；issue 册读取异常放行（gate 蓝图头 INVARIANTS :8）。

## 3 缺陷与矿脉清单
- **N1【改 M4 施工面】** Layer2 hook 已被网关通道跳过（git_commit_gateway.py:401-407）→ M4 只需改 Layer1 gate + preflight 同源，施工面缩小，Layer2 不动。
- **N2【假号洞】** marker issue_id 零校验 → M4.2 引入查册时顺带把 marker 也回查真源（议题册或裁定册），堵伪造审批。
- **N3【同源铁律】** preflight :313 与 M4.2 放行逻辑必须复用同一 resolver——否则"预检拒/锁内放"新造一类 A 因死信（本役病灶自体繁殖）。
- **N4【挂点精评】** 方案 A（改 gate 内部）：快，但 gate/preflight/(已废 Layer2) 各写查询=漂移；方案 B（抽 approval_resolver 共享模块）：裁定"status active+未过期+approved_paths 覆盖"收敛一处，天然服务 8+ 机械消费方（ruling_reference_gate/commit_preflight/registry_alignment/no_delete_manifest/redline×3/dashboard/baseline）。**建议 A→B 两步走**：resolver 函数从第一天独立成件（先住 gate 文件），M4.2 落地后平移 `zephyr/governance/`——净零、不阻塞第一夜。
- **N5【#410 字段级 diff】** `status: decided`→`active`（扩枚举要改 schema+校验器+册头铁律#4，成本高不值）；`related_files:`→`affected_files:`（保值换键）；新增 `approved_paths: ['docs/01_policies_and_standards/rules/*.yaml']` + `expires_at: '2026-09-30'`（接住清道三袋；rules/ 在保护清单 check_protected_paths.py:74）。三行 diff，与注册表变更同 commit。
- **N6【audit 无读者】** 两条逃生审计 jsonl 零消费——低成本顺带件：挂 GateFullTreeAudit 任务或周审计读 jsonl 出计数。

## 4 自审闸三态裁定
施工——M4 按 N1 收窄（Layer1+resolver 同源+N2 假号洞顺堵），#410 按 N5 三行 diff，方案成立无需封矿。

## 5 长尾清单
- scripts/governance/d3_metadata/batch_creation_tokens.py.tmp.21732.1992a99bc44d——safe_write 中断残留临时文件（违反根目录零临时文件精神，清理件）。
- `_BYPASS_ENV` 双处声明（check_protected_paths.py:64 / protected_paths_gate.py:76）：有对齐注释仍属弱双真源，resolver 化时可一并收敛。
- status 枚举是否扩 `decided`：业界无 decided 态先例，维持四值+#410 归 active 更净零。
- 形8 human_gate 无机械执行者——登记为已知设计（宪法 §5），不施工。
