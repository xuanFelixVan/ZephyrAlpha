---
ttl: task_bound
title: 全项目六轴深度审查战役 deep_review_full
owner: st-deeprev-20260918
created: 2026-09-18
---

# 全项目六轴深度审查+施工战役（2026-09-18 通宵班）

- 真源: `docs/01_policies_and_standards/sop/review_sop/deep_review_policy.md` v1.2.0（六轴审查法）+ `defect_pattern_checklist.md` v1.1.0（15条缺陷模式）
- 基线 commit: 2fa92002c3（施工会使兄弟对象基线漂移，收口方按新基线重验）
- 角色分离: 审查者只出报告（数据）；收口/施工=主力会话（st-deeprev-20260918）。审查→收口复核→施工修复→复检，缺一环不算完成。
- 优先级 Best-first: P0钱路径 → P1决策链 → P2基础设施；只定先后不定深浅，全部审到底。
- P0 加试双角色单轮: 审查者+复算反驳者隔离复算，数值对拍实证门裁决。

## 目录
- `00_panorama.md` 审查对象全景清单（159 对象，封矿真源）
- `01_master_ledger.csv` 审查总台账（唯一进度真源）
- `p0_money_path/` 钱路径 38 对象
- `p1_decision_chain/` 决策链 76 对象
- `p2_infra/` 基础设施+自动化任务族 45 对象

## 状态机
review_status: 待审→在审→已审；closeout_status: 待收口→收口中→施工中→已收口/挂起

## 关键裁定约束
- 裁定#304 做T v2现形态已砍（窄考试RED）；#305 切换判据定稿+CRISIS禁当日回切；#306 组合门尺子v2提案draft；#309 卖出族12件整族挂起；#317 盘中对账Timer→事件触发+30min兜底改造中；#322 S6死刑名单剔除两件。
