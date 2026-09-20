---
ttl: task_bound
completes_when: Owner 对三选项点单后转 archived
---

# TC-06 R2 裁定卡——E1C-09 存疑件后续（三选项呈报，禁自裁）

> 这是什么：E1C-09（P3-E1C-09 唯一 PASS 候选）E4 完整考试判**存疑**（fail-closed），
> can_deploy=false。考试档案：data/backtest_artifacts/runs/E4-E1C09-P3-E1C-09/verdict.md
> （本班实读复核）。为何要 Owner 点单：放行/补考/放弃三选一是策略生死权，AI 只呈选项。

## 考试硬数字（verdict.md 原文，本班复核一致）

- 候选：`ts_corr_20(ts_delta_5(mul(-0.614, close_ma20)), min(close_ma20, sqrt(div(vol_20d, ret_20d))))`
- IS sharpe=1.469（mining 段）；OOS sharpe=2.027（298td）；OOS/IS=1.3797
- DSR=0.732（N_eff=13，落 review 带 0.50-0.95）
- WFA 2/3 折通过：折2（mining_overlap，63 天）sharpe=**-1.953** / maxDD=**-40.44%** 灾难折
- 过拟合检出：WFA Sharpe 变异系数 1.83（阈值 1.50）+灾难折
- E2 幂等预审/E3 构造环**未跑**（预注册卡注明 E4 不替代）

## 三选项

| 选项 | 内容 | 依据 | 代价/风险 |
|---|---|---|---|
| A（挂起） | 等新数据积累后补样本重考（灾难折仅 63 天，样本薄是 DSR 与稳定性双疑的共同根源） | DSR 0.732 落 review 带=「补样本或人工复核」的官方语义；折2 灾难发生在最小折 | 候选冻结期机会成本；重考需预注册新卡 |
| B（立项） | 走 E2 幂等预审+E3 构造环完整通道再回来重考 E4 | 预注册卡明写 E4 不替代 E2/E3；完整通道是制度正路 | 工量最大；若 E2/E3 再曝缺陷，沉没成本 |
| C（放弃） | 候选归档留案底，不再投入 | 灾难折 -40.44% 的尾部形态+CV 1.83 超阈，实盘解释成本高 | 放弃一个 OOS 2.027 的候选（虽 select-bias 偏内） |

## 与他卡口径互锁

- 本卡引用裁定编号一律用新号（#331=做T砍、#386=S-OWNER-001 禁复试图救，renumber_note
  在 ruling_registry 3766/4256 行，本班复核）；S18 族编号（#333 签署）与本题无关勿混。
- tc_10 卡 P2 小活若吃 E1C 域，以本卡三选项定性为准。
