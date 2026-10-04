---
ttl: task_bound
completes_when: branch_zero 接管战役文档随 F8 家族处置批B 归档
---
# 混沌演训方案（Owner 令：10+ 并发车道+中途死亡模拟）

## 目的
验证三夜基建在真实并发+真实死亡场景下：老问题是否复发、死亡是否自动显化、接管是否闭环、零堆积是否成立。

## 编制
- 10 条 chaos 车道（chaos-st-01..10），各自注册独立 sid（pid=0），做最小真实工作：tests/governance/chaos_drill/test_chaos_NN.py（tests 豁免 token/词条，全链=注册→claim→写→add→gateway enqueue）
- 其中 01-05 正常跑完生命周期；06-10 在袋入带后被总包外部处死（registry 删号+无清理）=模拟"对话被关闭"

## 红蓝判据
| # | 向量 | 预期防御 |
|---|---|---|
| R1 | 10 车道并发 commit | 全局锁串行零丢失；index.lock 竞态自愈 |
| R2 | 5 车道中途死亡（袋在带/claim 在手） | ghost 闸拒自动重投→死信带处方；接管 --scan 生成 5 条 open 条目 |
| R3 | 死者资源面被触碰 | TAKEOVER-PENDING 门阻断+出处方 |
| R4 | 接管闭环 | --resolve 后门放行；袋改挂活 sid 落地 |
| R5 | 死信堆积 | --sweep-absorbed 三分流（吸收销账/超龄升级/新鲜保留） |
| R6 | 基线还原 | 全部 resolve+落地后：三桶/队列/锁回到基线，零无主资源 |

## 判定
全部向量过=三夜基建"彻底治本"成立；任一失败=修复后重跑，两轮全过才算根治。
