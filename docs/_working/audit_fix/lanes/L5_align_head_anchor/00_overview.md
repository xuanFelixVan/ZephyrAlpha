---
ttl: task_bound
---
# L5 registry_alignment 读数 HEAD 锚定（F-AUDIT-BLIND-02 治本）· 挖矿簿

> 环节=E09 ｜ 子环节=5（分母重算 / 锚点选型 / 消费方分派 / 实现 / 红绿双证）｜ 状态=封矿·已施工·已双证

## 子环节 1｜面积分母重算（案卷两次改口，本包给第三个口径并说明为何）

`src/zephyr/gov_enforcement/registry_alignment.py`（632 行）内**取字节**共 9 处 `read_text`、0 处 `open(`：

| 位置 | 内容 | 分类 |
|---|---|---|
| :121 `validate_registry_file` | 传入的册路径 | catalogs（每 spec 读一次） |
| :286 `run_all_registry_validations` | 同一 spec 再读一次 | catalogs（**与 :121 重复读**，22 spec ⇒ 44 次） |
| :344 `_fd_scan_consumer` | 变量 `fname` 循环 | catalogs |
| :370 / :420 / :481 / :482 | field_dictionary / candidate_module_registry / architecture_issue_registry / ruling_registry | catalogs（硬编码名） |
| :607 | industry_graph_field_dictionary | catalogs |
| :263 `in_flight_module_ids` | 变更 **python 源文件** 头 3000 字 | 非 catalog（天然属工作树，不改） |

⇒ 案卷第 7 轮写"6 处"、第 9 轮 R56 自否为"5 处"，两个数都指 `CATALOGS_DIR /` 的**路径构造**（实测该 grep==6；
去重后**硬编码文件名**==5）。本包口径＝**8 处 catalog 字节读 / 6 处 `CATALOGS_DIR` 路径构造 / 7 个锚点决策位**，
三个数各自成立只是量的不是同一件事——记此以避免下一次"分母之争"（文档矛盾=事故，宪法第 4 章第 3 条）。

## 子环节 2｜锚点选型：不翻转默认值，而是加"锚点参数 + 双锚并报"

模块自述只说"三方同源、纯读零写入"（:19-44 与头部 `[INVARIANTS]`），**从未声明锚点**——
所以本件不是改判据方向，是给一个缺失的维度补口径。据此否掉两个更激进的形态：
① 直接把默认翻成 HEAD ⇒ 会打掉 `business_registry_gate`（它校验"即将提交的字节"，必须暂存/工作树锚）
与 5 个基线测试；② 只加一条独立 HEAD 尺 ⇒ 生产链无人调用＝又一个零消费件（违 §4.2 内收判据）。

## 子环节 3｜消费方分派（谁必须留在盘锚，谁该看 HEAD）

| 消费方 | 应然锚点 | 依据 |
|---|---|---|
| `align_all.py [5/9]`（报表/总闸） | **双锚并报** | 它要回答"已入库真源是否自洽" |
| `commit_gates/business_registry_gate.py:138,152,171` | 工作树/暂存（不变） | 门禁语义=拦下即将入库的坏字节；改 HEAD 会**放行坏字节** |
| `commit_gates/industry_chain_map_gate.py:134` | 工作树（不变） | 同上 |
| `tests/governance/test_registry_alignment_layer2.py` | 工作树（不变） | 盘锚基线绿；HEAD 锚今天必红（HEAD 带 3 硬） |
| `scripts/battle_map_coverage_audit.py:38` | 不受影响 | 只用 `REGISTRY_SPECS` 路径不用字节 |

## 子环节 4｜实现（读口收敛为一个，禁止再散 read_text）

新增单一读口 `_load_catalog_yaml(path, *, source=SOURCE_WORKTREE)`：
- `head` 侧一次 `GitCommandBatcher.git_show_batch("HEAD", rels)` 批量取全册并进程内缓存——
  **刻意不用逐文件 `git show`**：本模块全量校验要读 23 册（`_all_catalog_rels()` 实测=23），
  逐册起子进程既撞 `GIT-BUDGET-INV-002 批量化强制` 又被本仓自己定价为 ~50-100ms/次；
  复用现成件（`src/zephyr/infrastructure/git_batcher.py:108`，已被 GIT-BUDGET gate 与 session_worktree 消费）＝零新真源。
- 路径全集从 `REGISTRY_SPECS` + `_FD_CONSUMERS` + 5 个硬编码名**派生**，不手写清单（§9.5 静态清单禁手工维护）。
- 仓外路径（测试用 tmp_path 自造册）→ 自动回落盘读，`_catalog_rel()` 返回 None 即识别；
- HEAD 批量取失败 → **抛错，不静默降回盘读**（降回盘读=把失明面重新藏起来，正是本案的病形）。
- 公开函数全部加 `*, source="worktree"` 关键字（默认不变 ⇒ 门禁与既有测试逐字节零影响）：
  `validate_registry_file / run_all_registry_validations / check_field_dictionary_fk /
   check_candidate_promotion_chain / check_governance_bidirectional / check_industry_graph_field_dictionary`。
- `align_all` 第 5 步改双锚：`layer2_hard = 盘侧硬 + 仅 HEAD 侧有的硬`（同一问题不在两锚重复计数），
  并新增一行 `HEAD 锚点: 硬=N，其中盘侧失明=M` + `HEAD-ONLY FAIL:` 明细。

## 子环节 5｜红绿双证（worktree 实测）

同一生产函数只换锚点：`check_governance_bidirectional()` → **0 硬**（盘侧：本包已把工作树 RR 修成 `[]`）；
`check_governance_bidirectional(source="head")` → **3 硬**（HEAD 侧：`#383/#387` 三值仍悬空）。
⇒ 尺既能红（HEAD 有违规必报）又能绿（对齐即不报），且这 3 硬恰是 L2 的落地对象——
**L5 落地的同时把 L2 的验收从"人工看一眼"升级成"每轮 align 自动看"**。
L2 落地后 HEAD 侧应回到 0，`align_all` 总硬随之归零（E11 复跑口径）。

## 本包自纠与接续（如实记）

施工首版误按主区**未提交**的 `spec_path()/RegistrySpec.base_dir` 形态写（那是 `st-cleanup-final-0009` 在途件），
在 worktree（HEAD 形态）里会 NameError/AttributeError ⇒ 已改回 HEAD 口径并在 `_all_catalog_rels()` 注释里
写明"该会话在途口落地后本函数须随其改走统一解析口"。
另记：**L5 与 `st-cleanup-final-…-0009` 同文件不同面**（那袋改 `spec_path` 与数据源入校验面，实测 `CATALOGS_DIR` 盘读点一行未动），
两袋都带 GW 标记 ⇒ L1 修好后任一后落地者会因基底漂移被判冲突，属主 requeue 即可，**不会互吃**——这正是本案修好的自动化后果。

## 追注（16:0x 实测）：属主口落地后的接续已完成

`f53316c6f9`（15:57）已把 `spec_path`/`RegistrySpec.base_dir`/`data_sources_registry` 送进 HEAD ⇒
本包 worktree 复位到新 dev、逐件重贴自家补丁，并把 `_all_catalog_rels()` 改为**经 `spec_path(spec)` 解析**
（不再自拼 `CATALOGS_DIR`）——于是 `base_dir` 出 catalogs 的数据源册**一并纳入 HEAD 锚点覆盖**，
恰补掉审计班第 9 轮 ⑦ 指出的"探针只重定向 `CATALOGS_DIR`、漏掉 `base_dir` 册"盲区。
复位后复验：本模块 `read_text` 只剩 2 处（读口自身 + `in_flight_module_ids` 读 py 源，天然属工作树）；
新基座上 `test_commit_queue_base_head.py` 7 例 + `test_audit_fix_lanes_rulers.py` 5 例 = **12 passed**【亲验】。
陈旧袋 0005（pre-f53316c6f9 字节）由收官批 0007 的同路径 compaction 自动清除（`supersedes=[0005,0006]`）——
若它先落地就会覆盖属主刚来的重构，这一步是修好之后才有的自动防护。
