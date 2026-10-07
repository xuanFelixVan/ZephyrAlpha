---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# C156 登记册数据卫生 — 纯改名映射表 + 合法化批处方（st-mastertc-l5，2026-10-07）

> 卡面：字段改名 486 条 + ruling decided/void 枚举立法。本档=改名映射唯一执行面；批量改名**本夜不执行**（另批，理由见 §4）。
> 校验器：`scripts/governance/check_registry_field_legality.py`（只读；改名批执行前出清单、执行后验零残留，exit 0=clean）。

## 1. D6 枚举立法（本夜已落）

ruling_registry 册头铁律#4 四值 → **六值**：`active / superseded / deprecated / draft / decided / void`。

- `decided`（13 条）：裁定已成立——含代裁批注类登记，效力等同 active 的时点性变体；新登记仍推荐 active。
- `void`（2 条）：编号墓碑——撞号/让位留痕（裁定#265/#408，标题自注"tombstone，非裁定"），承载铁律#2"编号不回收"。
- 存量越界值逐一列出（2026-10-07 普查，本立法批不改数据）：
  - decided=13：裁定#403 #404 #405 #406 #407 #409 #411 #412 #413 #444 #445 #481 #482
  - void=2：裁定#265 #408
- 立法后 `check_registry_field_legality.py` 实测越界=0（六值全合法），数据零改动。

## 2. D11 纯改名映射表（486 条，方向=归一到各册 entry_schema 立法名）

| # | 册 | 漂移字段(旧) | 立法名(新) | 条数 | 条目样本 | 机制注记 |
|---|---|---|---|---|---|---|
| 1 | candidate_module_registry.yaml | `created` | `created_at` | 457 | CAND-AISA-002..011 等 | schema L80=created_at；漂移为历史登记习惯 |
| 2 | module_translation_registry.yaml | `domain` | `domain_id` | 7 | schemas/categories/market/market_alt_* 6+typhoon 2 | schema L30=domain_id；全部集中 market 域 schema 条目 |
| 3 | risk_limit_registry.yaml | `limit_id` | `risk_limit_id` | 3 | RLM-FIRM-RISK-006/007/008 | schema L37=risk_limit_id；嵌套组内条目，行级 grep 不可见（须 YAML 解析） |
| 4 | architecture_issue_registry.yaml | `final_adjudication` | `adjudication` | 19 | #ARCH-338..#ARCH-356（连续段） | schema L42=adjudication；连续段=同批登记习惯漂移 |

合计 **486**（457+7+3+19），与 qmine 2026-09-25 基线一致。普查工具=本档校验器 `--json`（YAML 解析条目级，行级 grep 会漏嵌套 limit_id 且会误计 schema 段）。

## 3. 消费方审计（改前必读面）

- `created→created_at`：candidate 册条目被 `zephyr.governance` 候选模块消费面（capability_canonical_file_registry 描述、AGENTS 速查计数器）按 `unique_key=id` 取行，日期字段无代码级硬消费（速查区只数条目数）。改名后跑 `agents_cheatsheet_drift_reconciler` 复核 warn=0。
- `domain→domain_id`：module_translation 消费经 `module_translation_registry` loader（三层翻译），loader 读 `domain_id`；7 条漂移行 loader 视为缺 domain_id（现即降级行为），改名=修复非破坏。
- `limit_id→risk_limit_id`：risk_limit 册消费面=风险限额 gate；3 条漂移行同样属"缺立法名"降级行。
- `final_adjudication→adjudication`：architecture_issue 册无代码消费者（人读+引用 gate 只查 issue_id 存在性）；纯文档字段归一。
- 结论：四族均为**纯改名零语义差**（旧字段在 schema 外=本就未被机械读取），D 类批量改名安全前提成立。

## 4. 为何本夜不批量改（卡面要求 workbook 说明）

1. **批面纪律**：486 条横跨 4 册热文件（其中 ruling_registry/module_translation_registry 等处于他会话高频写入窗——本夜 git status 实测多册 MM 在途），同名共册同夜撞写=连坐高危；总纲 §三.5 禁碰他会话在途文件。
2. **改动面性质**：486 条分布 4 册 ≈ 数千行 diff，与立法批（本夜 2 处锚点小改）性质不同；纯机械但体量大，须按 RULE-DATA-OPS 三步验证+逐条 diff 预览+改后进程外复核独立成批，不与立法混袋。
3. **校验器先行**：合法化批的验收工具（本校验器）本夜落地并实测可跑（exit 1=漂移 486 在账，改名批后应 exit 0）——工具链就绪，执行批零准备成本。
4. **净零**：立法批已让 15 条 decided/void 从"越界"变"合法"，枚举面已收口；486 条改名不阻塞任何下游（§3 证实零硬消费），无抢跑收益。

## 5. 另批执行处方（交接）

1. 取四册锁（lock_files acquire 逐册）；他册在途=分册拆袋不硬闯。
2. 每册：safe_write_text CAS + 仅改漂移字段名（值零动）；每册改完跑本校验器单册核对。
3. 全量复核：`python scripts/governance/check_registry_field_legality.py` exit 0（clean=True）。
4. 提交：git_commit.py 单袋四册（或分四袋）；commit 后 `git log -1 --name-only` 核实无连坐。
5. 伴生（另行立项，非本批）：RULING-REFERENCE gate 增强 status 枚举校验（qmine 矿簿 §2 gate 缺口建议）。
