---
ttl: task_bound
completes_when: Max/Owner 裁定 k 值或特征口径，并同步 DESIGN §2.3 与 test_dedup 撤钉
---

# req_aibase_02 · SimHash k≤3 对短卡文本失效（换皮防护弱于 DESIGN 施工项 3 预期）

## 背景（全部本会话亲测，非转报）
DESIGN §2.3/施工项3 定 64-bit + 汉明距离 k≤3（Manku WWW 2007 参数，其原始语境是**数千 shingle 的长文档**）。
L2 卡文本 = title+novelty+mechanism 拼接，实测 token 数仅 74–127。实测距离分布（2026-09-18）：

| 文本对 | 汉明距离 | k≤3 判定 | 期望 |
|---|---|---|---|
| 同文自比 | **0** | 命中 | 命中 ✅ |
| 同 url+title（精确层 sha256） | — | 命中（`duplicate_sha`） | 命中 ✅ |
| **轻改一分句**（`T_BASE + "（原文照抄后补一句）"`） | **6** | **漏检** | 应命中 ❌ |
| 全段改写（>50% 词替换） | 14 | 放行 | 放行 ✅ |
| 无关文本 | >6 | 放行 | 放行 ✅ |
| 指标库原文照抄进 mechanism 字段 | 4 | 漏检 | 期望命中 ❌ |

即：**判据两侧陡度不足**——近重复与远重复挤在 6~14 区间，k=3 卡在两者之下，
`防换皮` 这一 L2 头号使命当前只对"同文重复提交"（精确层）成立，对"改写式换皮"不成立。
实测已落库证据：灌水 9 件中 `CC-reskin-20260918-006`（MAP-Elites 全段改写）与
`CC-indclone-20260918-008`（mechanism 字段照抄指标库 IND-COMP-001 一目均衡表）**均被放行入库**。

## 三选项
| 选项 | 动作 | 代价/风险 |
|---|---|---|
| A 提 k 到 8 | 改 `dedup.HAMMING_K` + DESIGN §2.3 同步 | 短卡误杀风险上升（无关文本经验值 >6，区间余量薄）；需重跑分布校准 |
| B 换特征口径 | CJK 改**字符 5-gram shingle**（Manku 原法）替代相邻 bigram，配 k=3 | 需重建 T4 全部 3595 条快照（幂等生成器可一键刷）；对长文档恢复设计精度，**最贴业界原参** |
| C 分层判据 | 短文本（<N token）走"字段级"分别比对（mechanism 单字段指纹 + title 单字段），任一字段 k≤3 即拒 | 不改全局参数、纯加严（合裁定#321"门禁只许加严"）；实现量最小，但 DESIGN §2.3"拼接后取指纹"口径需增补 |

## 建议
**C（字段级加严）为短期正解 + B（字符 shingle）为中期治本**；A 单独做风险最高。
本车道未擅改参数（MODIFY-GUARD：改判据先改设计稿），改用 `test_known_gap_single_edit_escapes_k3`
把缺陷**钉成红灯前置**：一旦有人收紧判据使距离落入 k 内，该测试即红并提示撤钉，杜绝"悄悄放宽再无人查"。

## Max 验真命令
`python -c "import sys;sys.path.insert(0,'src');from zephyr.ai_layer.intake.dedup import *
a='MAP-Elites 质量多样性：以行为描述子网格取代单目标最优，逐格保留最高适应度个体，变异体入格竞争胜出者留下，规避局部最优陷阱'
print('light-edit distance =', hamming_distance(simhash64(a), simhash64(a+'（原文照抄后补一句）')), 'K =', HAMMING_K)"`
