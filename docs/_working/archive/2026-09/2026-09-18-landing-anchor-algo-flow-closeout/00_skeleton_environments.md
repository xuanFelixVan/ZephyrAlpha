---
ttl: task_bound
completes_when: W1 锚定态假红治本代码已落地(2ac7d910ed)+5 双向钉经变异证红+commit_gates 套件连续两轮 0 自有问题，本文档族归档即完成
title: 落地面锚定态假红治本战役——W1~W5 环节全景封矿 / 依赖并发编排 / DoD
owner: ZephyrAlpha-Owner
session: st-anchorfix-20260918
date: 2026-09-18
---

# 落地面锚定态战役 · 骨架挖矿总谱

> **总令**：Owner 通宵交接令 2026-09-18。核心命题 = #ARCH-324 落地面（队列落地
> worktree / 会话 worktree）读自带 `.runtime` 锚定态 → 停更/空 → 永久假红（或假绿
> /保护失明）。挖矿纪律：先把五环节挖穿（本文档）再逐项封矿留痕。

## 环节全景封矿表

| 环节 | 命题 | 真源/入口 | 状态 | 门位 |
|------|------|-----------|------|------|
| W1 | worktree→主仓判定收敛唯一真源，修三消费方假红/失明 | `shared/io/paths.main_worktree_root` | 已落地 2ac7d910ed | 全自动 |
| W2 | 落地索引滞留 + qid 幂等（先查在途） | `scripts/commit_queue.py` | 登记不硬闯 | 全自动 |
| W3 | 孤儿 `model_capability_exam__init__.yaml` 退役 | `capability_canonical_file_registry.yaml` | 登记待 Owner | Owner 永久门 |
| W4 | 24 自指 fixture 判据式豁免 | `externalize_algo_flow.py`/`report_algo_flow_author_debt.py` | 判据设计在册 | 全自动 |
| W5 | 69 作者语义欠账身份核验（不代填） | 台账 47+17+5=69 | 身份核验完成 | 裁定#292 |

## 依赖与并发编排

- W1 是根因修复，W2~W5 不阻塞 W1；W1 落地后 W2 提交链才可安全评估。
- 落地走队列正门（`--no-bootstrap`），串行器隔离 worktree，结构性免疫混抢连坐。
- 热文件（注册表/宪法）写必经 CAS；洁净窗前禁写 tokens（#ARCH-329 整文件吸收风险）。

## DoD（万无一失判据）

1. W1 三消费方改锚 + helper 单源 + 5 双向钉（每钉含"打回旧行为必红"变异子测）；
2. commit_gates 套件连续两轮 0 自有问题（foreign 在途违规按 §3.4 不计）；
3. 落地经 GitCommitGateway，`git log -1 --name-only` 核归属，MM 滞留 index 已 add 刷新；
4. 临时件清零（`.runtime/tmp`），claim 全 release。

分项细节见 W1~W5 各子文档。
