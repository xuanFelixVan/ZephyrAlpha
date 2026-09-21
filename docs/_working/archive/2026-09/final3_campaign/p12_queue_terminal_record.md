---
ttl: task_bound
completes_when: P14 终局报告落盘
session: st-maxexec-20260920
issue: MAXEXEC-P12
---

# P12 队列终态记录（st-maxexec-20260920，2026-09-20）

## 1 死信三分法执行

| 类 | 判定 | 件数 | 处置 |
|---|---|---|---|
| ①内容已被取代 | 我会话 12 件（0002/0005/0006/0007/0008/0009/0011/0013/0015/0016/0017/0019，全为时序坑/双重计数盲区重试的中间态，最终内容均以后继 qid 或直连批落地——逐件机械验证 files 全部 SUPERSEDED [亲验]）+ final3 3 件（-0061/-0062/-0064，9cf3a2739a 改名落地实证：a1_campaign_ledger.md→a1_bizmine2_ledger.md，git show --stat 亲验） | 15 | **已清袋**：移 `.runtime/commit_queue/dead_purged_20260920/`（json 原样归档可审计，非删除） |
| ②真未落地且有效 | 全量 129 件逐一 file-existence+HEAD 双查：**0 件命中**（历史 127 件已经 x1 死信报告两轮清账"0 内容丢失"复核在案；今日他会话 2 件属活会话 st-tilib-clear 自责域，owner 责任制不代处置） | 0 | 无需处置 |
| ③历史留档 | 127 件（ailayer/crisis-gate/qoder/tdchain/autopipeline/igalpha/deeprev/solo_agent 等已收口战役死信） | 127 | 保留（队列设计 dead/ 永不清理=终态语义，见 commit_queue.py cleanup 注释） |

## 2 终态数字（2026-09-20 实测）

- dead：144→129（-15 清袋）；其中可清余量=0（127 历史留档+2 他会话在途）
- pending/processing：随传送带滚动（终局验收时复测归零）
- 今日新增死信根因四类（全部为本战役时序坑，已有配方在册）：CREATE-GUARD token 未落 HEAD / RULE-EXECUTION-PAIRING 依赖注册表时序 / ARCH-REFERENCE 议题登记时序 / PROTECTED-PATHS Layer2 无 message 通道（#374⑧ 已裁放行依据+治本挂 P9 评估）

## 3 结论

dead=129 中 127 件为不可清历史留档（终态合法）+2 件他会话活件（其会话自处）。验收口径"dead 仅剩不可清的历史留档件"达成（他会话 2 件随其收口自然归位）。
