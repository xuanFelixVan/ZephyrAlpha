---
ttl: task_bound
title: ADJ 案卷·清道三袋 ARCH 议题注册必要性与 [ARCH-APPROVAL] 触发机制
---

# ADJ · 清道三袋 ARCH 议题注册

## ① 一句话问的是什么

86 份 `rules/trae_*.yaml` 的"tags 批注摘除"三袋在队列里死了两天——问的是：**要不要先注册一个 ARCH-RULES-CLEAN-410 议题、再带 `[ARCH-APPROVAL:…]` 标记重投，还是可以直接重投**。

## ② 现状实测

### 2.1 三袋是什么

真源=裁定#410 summary（`docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml` 内，实测原文）指认三袋 qid：

| qid | 件数 | created | dead_at | 实测死因 |
|---|---|---|---|---|
| `q-20260923-st-ulib3c-20260923-0012` | 39 | 09-23 19:16:28 | 09-23 22:19:02 | PROTECTED-PATHS 阻断（39 hit） |
| `q-…-0013` | 25 | 09-23 19:16:29 | 09-23 22:19:20 | PROTECTED-PATHS 阻断（25 hit） |
| `q-…-0014` | 22 | 09-23 19:16:30 | 09-23 22:19:54 | PROTECTED-PATHS 阻断（22 hit） |

- 合计 **86 件 = 39+25+22**（实测，与裁定#410 所述 86 一致；本次为复测非引用）。
- 拆袋理由在册：单批 40 文件硬顶→按 rule 号段拆三袋、失败面互不连坐（袋内 message 原文，实测）。
- 内容物实测：三袋 86 路径全部落在 `docs/01_policies_and_standards/rules/trae_0XX_*.yaml`，且**逐件比 HEAD 只少 7 字节**——统一是删掉 `tags:` 段里的 `- TRAE` 一行。抽样 `trae_001_file_operation_security.yaml` 的 unified diff 实测：`-tags:\n- TRAE\n file_operation`。

### 2.2 落地进度与漂移实测（决定"能不能直接重投"）

- 主区盘 `git status --porcelain docs/01_policies_and_standards/rules/` = **0 行**（实测，工作区对该目录 clean）。
- 86 件在册 blob **全部与 HEAD 不一致**（实测 same_as_HEAD=0 / drift=86）→ 清道改动**至今未落地**，HEAD 仍是带 `- TRAE` 的旧态。
- 86 件在册 blob 与主区盘上文件归一后**零差异**（实测 differs_from_bag=0）→ 即"盘上零漂移"仍成立，**内容面不存在 stale-base 冲突**，缺的只是审批通道。

### 2.3 [ARCH-APPROVAL] 机制怎么触发、注册在哪（代码级实测）

现役正门 = in-process gate `PROTECTED-PATHS`：

- 注册：`docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml:527-532`，`module_path: zephyr.gov_enforcement.commit_gates.protected_paths_gate`，`enabled: true`（实测）。
- 判定收敛器：`src/zephyr/gov_enforcement/commit_gates/approval_resolver.py:8`（模块头 [INVARIANTS] 全文自述三通道）。三通道按序：
  - **a) marker 通道**：正则 `\[ARCH-APPROVAL:(#?ARCH-[A-Z0-9_-]+)\]`（`approval_resolver.py:70`，SSoT 回退自 `scripts/governance/d6_security/check_protected_paths.py:69`）——**且 id 必须实存于** `architecture_issue_registry.yaml` 的 `issue_id` **或** `ruling_registry.yaml` 的 `ruling_id`，查即不放行（`approval_resolver.py:140-149` `_id_in_entries`；`approval_resolver.py:275` 伪造拒绝 detail）。这是堵"假号洞"的治本（旧实现只 regex 命中即放行）。
  - **b) 裁定通道**：`ruling_registry.yaml` 中 `status=active` 且未过 `expires_at` 且 `approved_paths`（fnmatch + 目录前缀双语义，`_path_covered` at `approval_resolver.py:165-180`）覆盖任一命中路径 → 放行。
  - **c)** 都不命中 → 阻断。注册表读失败 → `source="unknown"`，gate 侧沿袭 fail-open。
- 另一逃生：env `ZEPHYR_PROTECTED_PATHS_BYPASS=1`（`protected_paths_gate.py:84`，落审计）。
- 议题册现状实测：`architecture_issue_registry.yaml` 共 **804 条 entries**，**不存在 `ARCH-RULES-CLEAN-410`**（按 `issue_id` 归一化查无）→ 19 号文 B5 的"议题注册"是**待办**，不是已办。
- 裁定#410 在册态实测：`status=active`、`approved_paths=['docs/01_policies_and_standards/rules/']`、`expires_at=2026-10-08`。

### 2.4 决定性实测：不注册议题，通道 b 已经放行

以只读方式在进程内直调现役判定器（不改任何东西）：

```
from zephyr.gov_enforcement.commit_gates.approval_resolver import resolve_approval
resolve_approval(<三袋全部 86 路径>, "不带任何 marker 的普通 message", ".")
→ ApprovalVerdict(approved=True, source='ruling',
  detail="裁定#410: active ruling approved_paths cover [...](expires_at=2026-10-08)")
```

逐件抽样实测亦 True（`trae_001` / `trae_002` / `trae_085` / `trae_086` 均 approved）。
→ **"必须先注册 ARCH 议题带 marker 重投"这句话，在 2026-10-08 之前不成立**：裁定#410 的 `approved_paths` 目录前缀语义已整体覆盖这 86 件。
→ 全册扫描实测：仅 #410 一条裁定的 `approved_paths` 覆盖 `rules/`，无第二条兜底。

## ③ 可选路径

**路径 A：直接重投（不注册新议题），message 内引"裁定#410 通道 b"**
- 动作：三袋全新 enqueue（禁 `--from-bag`），或合成一袋（86 件超单批 40 硬顶→**必须仍按三袋投**）。
- 代价：零新增资产。审批留痕=gate 审计 detail 里的裁定号（机生，可事后核）。
- 不可逆点：无。**但有效期只到 2026-10-08**（过期日判定用 UTC 当日仍有效、次日过期，`approval_resolver.py:8`）。

**路径 B：按 19 号文 B5 注册 `ARCH-RULES-CLEAN-410` 议题 + 带 marker 重投**
- 动作：`architecture_issue_registry.yaml` 加 1 条（`issue_id/title/severity/adjudication/status/created/last_updated`，schema 实测 7 字段），重投 message 挂 `[ARCH-APPROVAL:ARCH-RULES-CLEAN-410]`。
- 代价：**议题册是受保护热文件**——注册动作本身就要过一次 PROTECTED-PATHS（先例=#ARCH-359、#ARCH-C4CACHE-001 都是"登记载体被拿来当自己那次登记的通行证"，实测这两条 title 原文即写着"PROTECTED-PATHS [ARCH-APPROVAL] 正门标记载体"）；且新增一条议题与裁定#410 **同域同对象**，触宪法 §4 全资产净零（新增须声明替代/合并旧条目）。
- 不可逆点：议题册 804→805 净增，事后退役要走净删门位（high 域，Owner 门）。

**路径 C：A 打底 + B 的议题只作"过期后兜底"延后注册**
- 若 10-08 前三袋落齐 → 议题永不需注册（B 自然作废）；若未落齐 → 到点再注册，理由与证据链都是现成的。
- 代价：需在 10-08 前设一个复核点（可由死信循环顺带）。

## ④ 专业对照（外部论据，URL+发布方+年份）

1. **"授权一次、复用多次"是变更控制的正规形态，而非漏洞**：NIST SP 800-53 Rev.5 控制项 **CM-3（Configuration Change Control）** 要求变更由"predefined organization-established conditions"授权，授权与具体变更可分离登记；CM-3(5) 更把"automated enforcement of security checks"作为增强项——即机器消费在册授权、而不是每次新增登记。
   - https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final （NIST，2020-11，CM-3）
2. **"已有覆盖性批准即不需逐次新批"是代码所有权评审的通行实现**：GitHub 受保护分支的 CODEOWNERS 机制中，一次 owner 审批即覆盖其规则命中的全部文件变更，无需为每批变更另开评审单；GitHub 官方文档明确 required review 的匹配是"per-file ownership rule"粒度而非"per-pull-request 新议题"粒度。
   - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners （GitHub，2024 更新）
3. **反面对照（"breaking glass" 应留痕且不常规化）**：Google SRE Workbook "Managing Deployments"（O'Reilly，2018）主张紧急绕行通道必须产生可审后记录、且不能成为常态路径——与宪法 §9.8"`emergency_commit` 仅注册表/锁不可用时可用、手写标记判 forged"同构。
   - https://sre.google/workbook/managing-deployments/ （O'Reilly / Google，2018）

三条独立来源（NIST / GitHub / Google-O'Reilly），检索日期 2026-09-25，均支持"通道 b 已覆盖时不必另建议题"的判断。

## ⑤ 风险（做错的最坏情形）

- **资金安全：无暴露**。86 件改的是规则 YAML 的 `tags` 元数据段，不触阈值、不触判据、不触执行面（实测 diff 仅删 `- TRAE` 一行 7 字节）。
- 路径 B 的真实风险=**双真源**：同一批清道动作同时被"裁定#410"和"ARCH-RULES-CLEAN-410"授权，将来裁定过期而议题长存，等于给一个已结束的工程留下永久通行证——本仓有过热授权被后续会话滥用的先例记录（`fail_open_register.yaml` 与 `#ARCH-QCURE-APPROVAL-CHAIN-001` in_progress 条即在收这条缝，实测该议题 title 原文）。
- 路径 A 的真实风险=**窗口硬边界**：2026-10-08 之后重投必再死（且会再死一次没人认领），需要排一个到期复核点，否则三袋变"永久死信"。
- 共同风险：三袋若被合并成一袋 86 件 → 直接撞单批文件数硬顶，白死一轮。

## ⑥ 解锁依赖

1. 无缺件——**内容与通道两侧都已就绪**（实测：盘 clean、blob 与盘零漂移、resolve_approval 直调 approved=True）。
2. 唯一外部依赖=落地出口（LANE-LAND 死信循环）愿意按"三袋各自 enqueue"投。
3. 若要路径 B：还需一份"本议题替代/合并了哪条旧条目"的净零声明（宪法 §4.1），否则议题册净增无据。

## ⑦ 一句话推荐（推荐待总筹拍）

推荐 **C（直接重投，不注册议题；把议题注册降级为"2026-10-08 未落齐才触发"的条件项）**——理由是实测 `resolve_approval` 通道 b 已对全部 86 件放行，注册只会净增一条与裁定#410 同对象的授权、并制造双真源。
