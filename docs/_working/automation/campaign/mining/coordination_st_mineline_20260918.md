---
ttl: task_bound
completes_when: 挖矿 11 簿入袋且各车道施工分工被认领
---

# 挖矿战役车道协调字条（st-mineline-20260918，2026-09-18 04:1x）

## 1. 横扫事故实录（两次，已抢救）

- 03:47-03:54 tdchain 车道连续 pre-merge sweep（stash@{4}-@{7} 四代快照）+ `reset: moving to HEAD`（reflog 实证）抹除全仓未提交件，mining 全树两度消失。
- 抢救：`git checkout stash@{3} -- docs/_working/automation/campaign/mining/`（最新快照=我方还原版）全量还原；clean_exam_e2e 第三车道件自 stash@{6}（原 @{3}，nightcoord-preserve）还原至工作区，归其属主车道入袋。
- 教训重申：**验收即提交入袋=唯一可靠防御**（本夜第二次实证）；写完即 git add 不够，必须落 HEAD。

## 2. 版本与认领裁定

- ③④⑤ 作业簿=st-mineline-20260918 重写版（supersede st-mine-0456 旧边界稿；旧稿漏挖项已并入新簿并在簿内存档裁定）。
- ⑥⑦⑧⑨⑩+①②+00 总谱=收养 st-mine-0456/st-autolnk 原版（其会话心跳消失=死会话，stale claim 按 第2.7节 配方精准释放后由本车道认领）。
- 11 簿已全部入袋（HEAD）。

## 3. WO-③-00 自愈记录

- 03:03 发现工作区裸删 ECB 四登记+WORK-ORDER-3 接线（-49 行，stash_notice 无记载），03:17 调度器重启曾加载删除态。
- 同一横扫将删除回退，工作区==HEAD（4058b7b1e0）全量齐全。残余动作=调度器重启窗（04:00-05:00）重载使 daily_alt_fx 正门班生效（autolnk 台账 R1 项，运维级）。

## 4. 施工分工（线间并行流水，谁挖干谁先开工）

- 挖矿已全线封矿，各车道按各簿 第10节 工单自行认领施工；本车道（st-mineline）认领：
  - WO-④-01 数据质量常驻哨兵（1970/tz 变异检测）
  - WO-①-01+①-03 intel_harvester 源注册表化+词表外置
  - WO-①-05 源发现→源卡片草案转化器（①→③产线打通）
  - R-H5F-1 合理性收益带单一真源（Owner 已给修法：死信快照取差落地）
- 其余工单开放给任何车道认领，认领后在本文件 第5节 登记防撞。

## 5. 认领登记（追加式）

| 工单 | 认领车道 | 状态 |
|---|---|---|
| WO-④-01 / WO-①-01+03 / WO-①-05 / R-H5F-1 | st-mineline-20260918 | 施工中 |
| WO-①-01（源注册表化） | st-mineline-w101 | 已交付（config/intel_sources.yaml+intel_harvester.py 消费改造+validate_intel_registry.py，行为等价 305 passed） |
| WO-①-03（词表外置） | st-mineline-w101 | 已交付（config/intel_keywords.yaml 28 词干外置+加载器降级，随上同批） |
| WO-①-05（源卡片草案转化器） | st-mineline-w105 | 已交付（scripts/automation/source_card_drafter.py+tests 13 件零网零 LLM，24 passed 合批回归；草案仅落 config/source_cards/drafts/、CLI 无生效路径、Owner 门保留；depgraph 14799410/14799411；commit=1f3f9de02b 经队列 q-20260918-st-mineline-w105-0009 落地） |
| WO-③-03+WO-③-04（批量上架 --cards-dir+四登记 checklist+源健康度巡检器 source_health_patrol.py）| st-mineline-w304 | 已交付（onboard_source 批量模式+onboarding_checklist.md+巡检器+测试 20 件零网零 CH，31 passed 合批回归；.gitignore 收编+CREATE-GUARD/翻译/depgraph 14815765/14815766 同批；commit 待填） |
