---
oid: V01
对象: Wilson 下界单源（PatternWinRateProvider / _wilson_lower_bound）
入口: src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py:42
状态: 已审
审查者: GLM-5.3-Flash/st-deeprev-20260918
审查基线: 2fa92002c3（实测至 HEAD=6b1f22e148 本对象及测试零漂移，证据不过期）
材料包: 源码+测试全读；churn=git log --follow；消费方=全仓 grep；运行时证据=logs 抽查（见 §6）；数据画像=缺项（审查者无 CH 访问）
工作簿说明: 原作业簿模板文件在开工窗口（2026-09-18 04:40-04:42）已从磁盘消失（疑似并发会话 worktree pre-merge 清理，见 .runtime/workspace_alerts/stash_notice.json 惯例），本簿按 deep_review_policy §5 模板全量重建
ttl: task_bound
---

# 深度审查报告：V01 Wilson 下界单源（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 范围：`pattern_win_rate_provider.py` 全文件——`_wilson_lower_bound` 纯函数（L42-55）、`PatternWinRateProvider`（get/get_baseline/get_detail/get_conservative/list_pattern_ids）、`engine_win_rate_callable` 方向封闭集 wrapper。
- 排除项：ClickHouse 真库数据画像（审查者不触生产库，材料包缺项）；`c1_market.market_pattern_win_rate` 物化侧（属 W3 job，另对象）。
- 测试：`tests/signal_ashare/test_pattern_win_rate_provider.py`（13 用例），实测 13/13 绿（39 绿含 V02/V03 批；`-p no:cacheprovider` 因 pyproject `cache_dir` 严格配置报 INTERNALERROR，去该 flag 复跑通过）。
- 变更热力：7 commits（59544e35cb W3→ad35935728），W-C2 Wilson 化是最近语义变更（a425d565ae），无反复返工型高危。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 级 | 验证法 |
|---|---|---|---|---|
| A | Wilson 公式逐项正确：centre=p+z²/2n，margin=z√((p(1−p)+z²/4n)/n)，denom=1+z²/n，与 Wilson(1927) 标准式一致；z=1.959963984540054 精确 95% 分位；LB 恒≤raw、max(0,·) 截负 | pattern_win_rate_provider.py:52-55 | 已查无 | python 复算 n=100,p=0.62→0.5227；对照 tests:94-101 |
| A | 边界 n≤0→0.0 零信任 ✓；但 rate∉[0,1] 无入参校验：p>1 或 p<0 时 sqrt 项取负→`max(0.0, complex)` 抛 TypeError（`'>' not supported between complex and float`）——崩得响但不干净，且 `get_conservative` 直接喂 DB 裸值 | pattern_win_rate_provider.py:49-55,162-163 | P3 | `_wilson_lower_bound(1.2, 100)` 复现 TypeError（已机验） |
| A | `get_conservative` 对 hit_rate 非空但 n_events 为 NULL/0 的行返回 0.0 而非 None——"零信任"被伪装成"实测零胜率"，与 None 契约（无统计=NULL）语义打架 | pattern_win_rate_provider.py:162-163 | P3 | 造 row=(0, 0.6, 0) 喂 fake client 看 get_conservative==0.0 |
| A.3 | 测试 spy 死断言（checklist#3 邻类）：`_Spy.get` 内 `captured = (...)` 遮蔽外层 dict，方向映射（双顶→向下 等）实际未被断言，wrapper 只验证了返回值透传 | tests/signal_ashare/test_pattern_win_rate_provider.py:74-82 | P3 | 读测试：断言只查 `rates("双底")==0.75` 与未知名 None；把 Spy 的 direction 断言补上即见其缺失 |
| A.3 | 无 rate 越界/负值用例（对应上 P3），n=0 路径有覆盖 ✓ | tests:105-112 | P3 | 同上 |
| B | 上游=market_pattern_win_rate（W3 物化）：low_sample/NULL/查无三途→None 契约有测试且实现一致 ✓；SQL 全参数化、FINAL 去重 ✓ | pattern_win_rate_provider.py:198-207,209-218 | 已查无 | 读 load/test_none_semantics |
| B | 表名经 f-string 拼接（`FROM {self._table}`）——构造参数可注入；默认常量、生产不外传，记 P3 硬化项 | pattern_win_rate_provider.py:179,199 | P3 | 传恶意 table 参复现 |
| C | 消费方：pattern_to_signal_mapper（MOD-SIG-115，加权=置信度×胜率）、unified_pattern_engine W4 注入、pattern_signal_runtime.py:490-496（Wilson 回落路径）、api_server /api/pattern-winrate、internal_compute_provider:403（调权委托）。LB 错值→形态权重静默偏移；None 契约被消费方遵守（runtime:497 无统计跳过） | 各 file:line | 爆炸半径=图形信号族权重 | grep 调用方全列已核 |
| D | 单源核实：全仓唯一 Wilson 数学实现（certifier 经 import 复用，c2f258209c；他处均为注释/展示引用） | grep -rni wilson src | 已查无 | grep 输出仅本文件含公式 |
| E | 静默失败：`_ensure_client` RuntimeError 出声 ✓；只读无幂等问题；时序=FINAL+参数化无攻击面 | pattern_win_rate_provider.py:65-72 | 已查无 | 读码 |

## 3 SOTA 对照

| 算法 | 结论 | 来源 |
|---|---|---|
| Wilson 得分区间下界 | 对等已有（公式逐项一致） | Wilson, E.B. (1927) JASA 22(158):209-212——检索遇 429 限流，出处为工具侧教科书引文，**URL 未实证，记"受阻"级**；docstring 内 "TradingView winrate 脚本实照同法" 主张未核（外部断言挂 §5） |

## 4 缺陷清单（按严重级）

1. **P3｜rate∉[0,1] 无校验致 TypeError**：现状=裸公式直接算；证据=pattern_win_rate_provider.py:49-55 + 机验复现；影响=DB 脏数据（hit_rate>1）时 weight sync 任务崩（响亮失败，无静默放水）；建议=入口 `if not 0<=p<=1: raise ValueError`；验证法=同上机验一行。
2. **P3｜n_events NULL→LB=0.0 冒充实测零**：现状=`int(row.get("n_events") or 0)`→n=0→0.0；证据=L162-163；影响=审计读数误导（非钱闸直伤）；建议=rate 有值而 n 缺失时返回 None；验证法=造 (None, 0.6, 0) 行。
3. **P3｜引擎 wrapper 方向映射零断言**：见 §2 A.3 行；建议=补 direction 捕获断言；验证法=审 tests:74-82。
4. **P3｜f-string 表名拼接**：见 §2 B 行；建议=白名单常量表名。

## 5 挂起疑问

- "TradingView winrate 脚本同法"外部主张无 URL 实证（限流），待主力会话补一条链接或降级措辞。
- 真实表 n_events/hit_rate 分布（low_sample 率、NULL 率）未查=数据画像缺项，本报告 A 轴边界结论基于代码而非数据。

## 6 完备性自评

六轴全查（A/B/C/D/E/F 均有结论）。长尾：①数据画像缺项（无 CH 访问）；②运行时证据包：logs 近 3 日无本对象 error 痕迹（c4_exam.log OOS 批 exit 0）；③Wilson SOTA 对照受 429 限流只达教科书级。
