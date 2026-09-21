---
ttl: task_bound
title: 交接令——deep_review_full 战役收尾+挂起处置（st-deeprev-20260918 → 下一班）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 交接令：deep_review_full 战役收尾 + 挂起处置（本文件=新会话开工第一读件）

## 执行模型分派（Owner 指定）

- **执行模型 = 千问 3.8 Flash（快速档）**：只做简单/机械任务（盘点、复跑测试、按既定修法改码、跑批、落文件）。
- **Max 模型 = 全部复杂裁定的唯一裁定者**：接线/退役/语义/归属/豁免类判断一律报 Max 裁定；Max 裁定后，简单执行回派 Flash，高难执行由 Max 亲自做。
- **Flash 禁止**：自行做深度审查结论、自行裁定门禁豁免、自行处置 N-5 待裁件、修改他会话在途 WIP。

## 必读真源（按序）

1. `docs/_working/deep_review_full/morning_report_20260918.md` —— 晨报终版 v1.0 + §6 收尾后记（一页读全场）
2. `docs/_working/deep_review_full/01_master_ledger.csv` —— 235 对象审查台账（唯一进度真源）
3. `docs/_working/deep_review_full/00_panorama.md` —— 全景清单与排除项
4. `docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml` —— **#ARCH-338..#ARCH-356 挂起批 19 条裁定项**（每条含裁定选项+报告锚点）
5. 235 份审查报告：`docs/_working/deep_review_full/p0_money_path/`（38）、`p1_decision_chain/`（76+tdm_supplement 76）、`p2_infra/`（45）

## 冷启动（缺一不可）

1. PATH 修 Python312：`export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"`，`python --version` 必须 3.12.x
2. `python scripts/lock_files.py cleanup && python -m zephyr.trading.process_reaper --status`（reaper 存活才准写操作）
3. `git status --porcelain` 全量盘点，核对 N-5 现状（见任务 2）
4. 新会话自取新 sid（建议 `st-deeprev-handoff-20260918`），提交时用之

## 任务清单（移交）

### 任务 1：crisis_drill_monthly.py 修头版落地（移交待办）
- 现状：`scripts/backtest/crisis_drill_monthly.py` 头已修为 **MOD-BT-219**（编号纪律：仓内最大 MOD-BT-218 后取号），在工作区未落地；落地撞 **NO-HIGH-COMPLEXITY** 门禁——该件 750 行 WIP 自身复杂度债，非头注释问题
- Flash 动作：跑 `tests/backtest/test_crisis_drill_monthly.py` 确认基线 → 报 Max 裁定（重构降复杂度 / 合规豁免 / 退回原车道）→ 按裁定执行 → git_commit.py 落地

### 任务 2：N-5 共享区脏树定夺（Owner 级，Flash 禁擅动）
- 内容：22 个 schema 删除 + 46 个 src 核心改 + stash（WIP on aa43e3b530）+ altdata-night token 注册表纠缠（另一 AI 登记 N-5）
- Flash 动作：仅盘点与报告——`git status --porcelain` 全量 + 逐文件"staged==worktree 无损判定表"，产出裁定建议书落 `docs/_working/deep_review_full/n5_adjudication_brief.md`，报 Max/Owner；**未裁定前禁 restore --staged / stash pop / 任何删除**
- 注：本战役已按 Owner 授权无损撤下 2 件（cohort_daily_ledger.py、crisis_drill_monthly.py，index==worktree 判定），已记晨报 §6

### 任务 3：红蓝检出率门收尾（rule 车道归属）
- 现状：`tests/rule/test_rule_red_blue.py::test_generate_report` 失败（报告生成 0 结果 vs ≥9）；本战役未触 rule 域
- Flash 动作：复跑确认 + 归因（数据/日期/路径三查）→ 归因结论报 Max 裁定修法

### 任务 4：#ARCH-338..356 处置流水线（19 条挂起裁定项）
- 条目清单+裁定选项+锚点全在 issue_registry 与晨报 §1/§3；优先序按晨报 §1：
  ① TF07 daban 名义 DAG 边（日消费←周生产，周二至五读上周事件）② miniQMT 退役 24 任务退路 ③ K08 监管闸武装前置 ④ I26/T06 面板 API 鉴权 ⑤ K02 资金事故假处置 ⑥ pf_alloc 整域 ⑦ Regime 断供三腿 ⑧ Wyckoff 旁路 ⑨ 对账链 ⑩ 告警推送通道 …（全 19 条见 registry）
- 流程：Max 逐条裁定（接线/退役/语义三选一）→ 登记 ruling → Flash 按 construction SOP 执行（claim→修→测→git_commit.py）→ 回写 registry status

## 提交配方（铁律，违者返工）

- 唯一入口：`python scripts/git_commit.py --session <sid> --files <逗号清单> --allow-non-worktree --allow-overlap [--allow-multi-domain] --enqueue`
- 新建文件先补 token：`python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix <目录> --created-by <sid> --capability <cap>`；**token 载体 capability_canonical_file_registry.yaml 必须随批同落**（否则 CREATE-GUARD 死）
- 改 TDM 节点实现码必须同批改 `config/trading_decision_map.yaml` 该节点 algo_note_zh 或加 `note_confirmed: <日期>`（ALGO-NOTE-SYNC）
- 共享热注册表（architecture_issue_registry 等）**禁 yaml.safe_dump 整写**（MASS-DELETION 死+重排版吞他改）——只做文本式追加
- 直连被外来 staged 脏件连坐时：仅对 "index==worktree" 件 `git restore --staged`（无损），不碰 N-5 待裁件
- 每笔 commit 后 `git log -1 --name-only` 核实归属；队列死信读 dead_reason 修正后 requeue 或按新快照重入队

## 战役背景速记

235 对象六轴全审完（12 审查波+1 反驳者波）；25 项治本全部带回归落地；两轮全域回归（R1 6971 过/R2 7055 过）本线零新增红；红蓝 metamorphic 73/73、检出率门 9/10（失败项=任务 3）；N-5 主体非本战役产物。
