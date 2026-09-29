---
ttl: task_bound
title: F21 E2 假说预审逻辑门（防噪音总闸）——L02 接线矿道案卷
session: zc-l02-20260927
updated: 2026-09-29
---

# F21 · E2 假说预审逻辑门（hypothesis_precheck）

> 挖矿基册=01_strategy_factory/09_f21_e2_hypothesis_precheck.md（SF-A）。本卷=独立复核+09-26/27 CH 增量（58→63 行）。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | 六源进货台账 D/B/C/C2/G/I（load_candidates 校验 birth 四列 :170-180）；09-27 CH 渠道存量：D 60 行/唯一 29（台账）、B 4、C 16、C2 8、G 0、I 10 |
| 下游 | **c1_backtest.hypothesis_precheck 09-27 实测 63 行**（15 批 09-14~09-26）：13 passed/26 rejected/24 deferred（全 defer_llm_unreachable）；E3 消费面见 10_f22 卷；FL1 法定回灌终点 |
| 自动触发 | 无常驻；编排 run 自动接续=唯一自动面；deferred 重审通道仍缺 |
| 真源注册表 | MOD-BT-091=path_ownership_map.yaml:15963,16222（grep 实证）；图 9 FAC-E2 partial（store_refs=c1_backtest.hypothesis_precheck 永久）；DDL-as-Code=schemas/categories/backtest/backtest_hypothesis_precheck.py；tests/backtest/test_hypothesis_precheck.py 在盘 |
| 门禁质量尺 | verdict/理由码封闭枚举禁手填；reject 不可映射转 defer 不落脏码（:121-123）；LLM 异常→defer_llm_unreachable；低置信阈 0.6；台账只追加；判定权留 E4 |
| 运行状态 | 绿（判定通路）/**红（滞留面扩大）**。最近运行=**2026-09-26 10:28**（E2-20260926-102842：C 渠道 5 条新审全 defer——Ollama 断供期；prechecked_at max=09-26 10:29:03 CH 实证）；基册"09-19 后零新判定"已被 09-26 班推翻 **〔过时标记 2026-09-29：滞留"无重审通道"定性已翻——SQL_ALREADY 幂等治本已落（S4 包 f28ce0d0f0），见卷末刷新批注〕** |

## 二、子模块三级枚举
1. **代码面**：build_prompt :80-95（六问确定性）｜parse_reply :98-145｜precheck_one :156-167｜**fetch_prechecked_ids :183-191（缺陷维持：SQL_ALREADY="SELECT DISTINCT candidate_id FROM {table}" :70 全表 DISTINCT 含 deferred→滞留）**｜insert_verdicts :194-211｜run :214-254｜cmd_status :257-269。**〔过时标记 2026-09-29：SQL_ALREADY 已改 :82 `WHERE verdict != 'precheck_deferred'`，缺陷销案，见卷末刷新批注〕**
2. **注册表/文档面**：path_ownership_map:15963,16222；FAC-E2（design_refs=FaVOR/Harvey-Liu-Zhu/Owner 先验笔记）；CH 表 DDL 归 schemas/categories/backtest。
3. **数据面**：63 行批次分布（09-27 CH execute 实证）：09-14 三批（D 2p+1r/6p+1r/C 1p+7r/B 1p+3r）→09-15（C2 3r+3r+2d/D 5d/C 2d）→09-16（B 3p+8r）→09-19（I 10d）→**09-26（C 5d）**。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**。
- **骨架勘误/增量**：①基册 P0"deferred 19 条永久滞留"数字**已过期：现 24 条**（+5=09-26 C 渠道新审 defer）；且 09-26 班实证"新 id 照常入审、旧 defer 永不再审"的双轨行为——缺陷语义获得正向对照证据。②基册"09-19 后零新判定"失效（09-26 有班）；总册 F21 无此表述，无需改总册。③漏斗更新：D 8p/15 审、B 4p/15 审、C 1p/15 审、C2 0p/8 审、I 0p/10 审（合计 63 行）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | 【P0 维持+扩大】deferred 24 条滞留无重审通道 **〔09-29 SQL 腿已闭合，见刷新批注〕** | SQL_ALREADY :70 全表 DISTINCT；09-26 新增 5 条 defer；:190 注释自认 deferred 可重跑语义 | 施工：SQL 改 `WHERE verdict != 'precheck_deferred'`（1 行+测试 0.5 天）+Ollama 恢复后重审 24 条 | P0 |
| 2 | head(limit) 截取文件头非新增 | load_candidates df.head(limit)（:181 前后）；D 60 行唯一 29 挤占名额 | 施工：幂等过滤后再截断（顺序对调）+去重；0.5 天 | P1 |
| 3 | LLM 不可达窗口无告警 | 09-15/19/26 三波 defer 共 24 条；Ollama 不进 M5 巡检 | 施工：defer 率阈值夜批告警（跨 M5）0.5 天 | P1 |
| 4 | 判定权单点（qwen3:8b 一票制） | 单模型单温 0.0；FaVOR 未落地 | 待裁：低置信双模型复核（判定权设计=Owner 域） | P2 |
| 5 | 26 reject 无抽检标定 | 无复核记录 | 施工：抽 10% 复核一轮留档 0.5 天/轮 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核有增量：P0 滞留 19→24 条且获正向对照证据；运行时间线更新至 09-26；其余三伤维持。**〔过时标记 2026-09-29：P0 已由 S4 包翻面，三态刷新见卷末批注〕**

## 刷新批注（2026-09-29 st-finaldel-freshb）

> 刷新基线：HEAD dev @ 0cacd4a64d（09-29）；对卷内真源跑 `git log --since=2026-09-28` 复核＋码面现读。

- **翻面 commit**：`f28ce0d0f0`（09-28 15:11，S4 工厂修复包·一、F21 deferred 幂等治本）。
- **影响（缺口1 P0 的 SQL 腿闭合）**：
  - `scripts/backtest/hypothesis_precheck.py` **SQL_ALREADY 现锚 :82**：`SELECT DISTINCT candidate_id FROM {table} WHERE verdict != 'precheck_deferred'`——幂等集只认终局结论（passed/rejected），deferred 留重审通道；卷内处方原样兑现（"1 行+测试"）。随批 INVARIANTS 头注同步（:13-14）+ 治本注记（:78-80）+ `tests/backtest/test_hypothesis_precheck.py` +167 行。
  - **销案口径**：卷 §二"SQL_ALREADY :70 全表 DISTINCT 含 deferred→滞留"缺陷现场过时（行号亦漂移 :70→:82）；"24 条 defer 被永久锁死"的死锁定性解除——deferred 现可随下一班自动重入（**重审实际发生仍待 Ollama 11434 恢复**，Owner 门不变）；CH 表内 24 条历史 defer 行数据未动。
- **缺口状态修订**：缺口1 P0→SQL 腿已闭合（重审动作待 Ollama）｜缺口2（head(limit) 截取）维持（本批未触及）｜缺口3（LLM 不可达无告警）维持｜缺口4/5 维持。
- **自审闸三态（刷新后）**：**partial（维持，P0 销案后余量为 P1×2+P2×2）**——卷作"滞留坑"历史定性+治本验收锚使用；缺口1 处方对施工面失效，复跑命令 :70 锚点改 :82。
- **复跑**：`git show f28ce0d0f0 --stat`｜`sed -n '78,82p' scripts/backtest/hypothesis_precheck.py`（治本注记+新 SQL）｜`python -m pytest tests/backtest/test_hypothesis_precheck.py -q`。

## 六、复跑命令
```bash
python scripts/backtest/hypothesis_precheck.py status     # total=63
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"; python -c "
from zephyr.data.ch_writer import get_client_strict
c=get_client_strict()
for r in c.execute('SELECT precheck_batch,birth_channel,verdict,count() FROM c1_backtest.hypothesis_precheck GROUP BY 1,2,3 ORDER BY 1'): print(r)"
sed -n '70p;183,191p' scripts/backtest/hypothesis_precheck.py   # 缺陷现场
python -m pytest tests/backtest/test_hypothesis_precheck.py -q
```
