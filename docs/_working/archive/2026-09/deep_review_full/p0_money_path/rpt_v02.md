---
oid: V02
对象: 四闸证据认证器（pattern_evidence_certifier，WilsonLB+二项+n_eff 收缩+BH FDR）
入口: src/zephyr/signal_ashare/strategy_signal/pattern_evidence_certifier.py:186（certify_family）
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（至 HEAD=6b1f22e148 本对象零漂移）
材料包: 源码+测试全读；churn；消费方 grep（含 pattern_signal_runtime/api_server/pattern_event_job/pattern_lifecycle）；运行时证据=logs 抽查；数据画像=缺项
工作簿说明: 原模板消失（并发会话清理），按 SOP §5 全量重建
ttl: task_bound
---

# 深度审查报告：V02 四闸证据认证器（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：统计核四纯函数（binomial_ge_pvalue L79/effective_n L112/shrunk_rate L120/within_regime_edge L133）+ 状态机 certify_family L186 + CH 读写 load_family_rows L267/persist L299 + run_certify L335（含生命周期覆盖层）。
- 排除项：market_pattern_certification DDL/物化 job 本体；pattern_lifecycle 状态机内部（另对象，只审接缝）。
- 测试：tests/signal_ashare/strategy_signal/test_pattern_evidence_certifier.py 13 用例，实测全绿。
- 变更热力：6 commits，最近 33b9593ad9（p0∈{0,1} 精确分支，GW5 mutation 试点治本）+ c2f258209c（BH 单源收敛）——方向都是堵洞，健康。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | 二项单侧检验 lgamma 实现正确，含 p0∈{0,1}/hits≤0/hits>n 全部精确短路；远尾下溢=0 语义可接受 | pattern_evidence_certifier.py:79-109 | 已查无 | tests:54-77 教科书向量 + P(X≥70\|100,0.5)≈2.84e-5 复算 |
| A | n_eff 折扣把**非整数 n_eff 当二项 n 用**（lgamma 广义二项系数）——非严格概率分布，属预注册的保守近似；同一近似也喂 Wilson（certify_family L234 wilson_fn(hit_rate, n_eff)） | :221-223,233-234 | 已查无（设计选择，建议文档显式声明近似性） | 读 ALGO_FLOW S3 注释 |
| A | **闸C 基线回退不一致（机验实证）**：pooled 基线=0.64 时 `load_family_rows` 不注册 `__pooled__` 键（仅当缺 pooled 基线时才补 0.5），而 `within_regime_edge` 对缺基线的 regime 回退 `get("__pooled__", 0.5)`——同族内混用 0.64 与 0.5 两个基线。实测：slice hit=0.60/n=1000 在正确 0.64 基线下 edge=−0.04（probation 向），错回退下 edge=+0.10（certified 向），**闸C 判决翻转** | pattern_evidence_certifier.py:150-152 vs 294-295 | **P2** | 机验已复现（within_regime_edge 两调用对拍）；修法=回退统一取 baseline_pooled 或恒注册 __pooled__=baseline_pooled |
| A | shrunk_rate 边界校验完整（率越界/n_eff 负/k≤0→ValueError），certify 链上 rate>1 会先经 shrunk_rate 崩出（响亮 fail-closed） | :120-130 | 已查无 | tests:106-113 |
| A | within_regime_edge 全负 edge 时 share=1.0>0.9——但此时 w_edge≤0 同判 probation，两支路一致无漏洞 | :153-161 | 已查无 | 构造全负切片推演 |
| A.3 | 测试无"缺 regime 基线回退"用例（P2 即从该盲区漏过）、无 persist/load_certification 往返、无生命周期 ImportError 降级用例 | tests 全文 | P3 | 读测试目录清单 |
| B | load_family_rows：low_sample 不进认定（fail-closed）✓；**缺 __baseline__ 行时 baseline_pooled 静默落 0.5**（magic constant，对正向族偏保守、对基线<0.5 的族偏松） | :278-279 | P3 | 删基线行看基线取值 |
| C | 消费方：pattern_event_job.run_evidence_certify（任务块）、PatternWeightSync（pattern_signal_runtime.py:472-477）、api_server.py:4249（认证列）。**消费端词汇表漂移（见缺陷#2）** | 各锚点 | 见下 | grep |
| D | 闸A 用纯 BH（c=1，q=0.05）而策略闸 bh_filter 已裁 BHY（c(m)>1，q=0.10）——同是 FDR 钱闸两套口径。判：非缺陷（图形切片族正依赖 PRDS 下 BH 合法 + 阈值各自预注册），但口径分裂应留一张对齐卡 | :228-230 vs strategy_pipeline/bh_fdr.py:71 | P3（登记） | 读两文件头预注册注记 |
| D | persist 写出六态词汇（certified/probation/failed + 生命周期 retired/resurrected/frozen 覆盖，run_certify L373-381 用 lifecycle state 替换后落表）——而主消费方只认三态（见缺陷#2），writer/consumer 词汇漂移=checklist#4/#14 族 | :373-385 + pattern_signal_runtime.py:474-477 | 见下 | grep runtime 全文件零 retired/frozen 字样（已核） |
| E | **生命周期层 ImportError 被静默吞**：`except ImportError: pass` 无任何日志——pattern_lifecycle 模块损坏/改名时认证静默降级三态，无人知晓（E 轴"断了没人知道"） | pattern_evidence_certifier.py:382-383 | **P2** | 临时改 import 名触发（或读码确认无 _logger 调用） |
| E | persist ReplacingMergeTree 幂等重放 ✓；certified_at 显式 UTC ✓；重复 run_certify 无双写风险 | :299-318 | 已查无 | 读 DDL 契约注释 |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| 闸A BH-FDR step-up | 对等已有 | Benjamini & Yekutieli (2001) Annals of Statistics（任意依赖扩展原文）：https://www.researchgate.net/publication/38348313 ；正依赖下纯 BH 合法性同 Benjamini-Hochberg (1995) |
| 闸B n_eff=重窗折扣 | 对等已有（保守近似，业界常用重叠加窗折减） | 本轮检索限流，未取到专门 URL——记"受阻"，公式本身与预注册一致 |
| 闸D 贝叶斯收缩 | 对等已有（Efron-Morris/empirical-Bayes 谱系教科书式实现） | 检索限流记"受阻"；公式为标准 shrinkage-to-prior |
| 闸A 二项精确检验 | 对等已有（教科书单侧精确检验） | 检索限流记"受阻" |

## 4 缺陷清单（按严重级）

1. **P2｜闸C 基线回退不一致可翻转认证态**：现状=缺 regime 基线行时回退 0.5 而 pooled 基线可能是 0.64；证据=pattern_evidence_certifier.py:152 vs 294-295 + 机验（edge −0.04↔+0.10 翻转）；爆炸半径=该形态 certified/probation 误判→runtime 调权口径失真（单形态级）；建议=`load_family_rows` 恒注册 `__pooled__=baseline_pooled`，`within_regime_edge` 缺键回退读该键；验证法=报告 §2 机验两行复现。
2. **P2｜生命周期六态词汇与主消费方三态契约漂移**：现状=run_certify 把 retired/resurrected/frozen 覆盖写进认证表（:373-385），而 PatternWeightSync 只跳过 `state=="failed"`（pattern_signal_runtime.py:474-477，全文件零 retired/frozen 处理）——**已退役/冻结形态照常参与调权**（shrunk_rate 录样本+adjust）；爆炸半径=图形信号族权重（决策偏移非直接资金）；建议=消费端把非 certified/probation 全部 continue（fail-closed 白名单），或落表前把生命周期终态映射回 failed 旁路；验证法=grep pattern_signal_runtime.py "retired\|frozen"=0 命中 + 读 :474-477。
3. **P2｜生命周期层 ImportError 静默降级**：现状=except ImportError: pass 无日志；证据=:382-383；影响=复活/退役治理整层失踪且无痕（该层本应拦退役形态复活）；建议=至少 _logger.warning；验证法=读码确认零日志调用。
4. **P3｜缺基线静默 0.5 / 测试盲区 / BH-BHY 口径分裂**：见 §2 B/D 行。

## 5 挂起疑问

- retired 形态"照常调权"是否 Owner 有意（复活观察期内维持权重）？若是，需在 runtime 消费端显式注释契约；若非，按缺陷#2 收口。
- 认证表内 shrunk_rate 对 failed 行仍写值，前端展示是否区分"failed 的收缩读数不可用"——未审前端语义。

## 6 完备性自评

六轴全查。长尾：①真实统计表画像（低样本率/基线行覆盖 regime 完备性——缺陷#1 触发前提）缺项；②pattern_lifecycle 状态机本体只审接缝；③轴 F 二项/收缩两项受 429 限流记"受阻"。运行时证据：近 3 日 logs 无本对象 error 痕迹。

## 7 收口裁定（收口方 st-deeprev-20260918 填）
- P2-1 闸C基线回退: 确认→治本(load_family_rows 恒同步 __pooled__ 键)+回归(0.64 基线下缺 regime 切片 edge=-0.04 恢复 probation 向)。复检 14/14。
- P2-2 六态词汇漂移/ImportError 静默: 挂起登记(与 V08 接线合并裁定)。
- 修复提交: 队列 q-20260918-st-deeprev-20260918-0007。
