---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 包5——ETF 分钟族 trade_time 时区劈叉工单（三步验证完毕，--execute 等 Owner 门位）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
session: st-flashbiz-20260918
---

# 包5 · kline_etf_15min 时区劈叉 → 全 ETF 分钟族工单（破坏性操作前停下，等 Owner）

T lane 发现移交件（Owner 快签总表行 29）。本班完成三步验证+修复件就绪+影响扫描，**在破坏性操作前按指令停下登记**。

## 1. 缺陷真相（较 T lane 报告扩面：15min 一表 → 全 ETF 分钟族五表）

| 表 | 总行数 | UTC 误标（hour∈[1,7]） | 占比 | 北京墙钟（hour∈[9,15]） |
|---|---|---|---|---|
| kline_etf_1min | 326,301,055 | **303,422,787** | 93.0% | 22,878,268 |
| kline_etf_5min | 71,856,186 | **68,163,011** | 94.9% | 3,693,175 |
| kline_etf_15min | 24,331,141 | **23,168,185** | 95.2% | 1,162,956 |
| kline_etf_30min | 11,939,337 | **11,360,495** | 95.1% | 578,842 |
| kline_etf_60min | 5,962,194 | **5,680,248** | 95.3% | 281,946 |

- 纪元边界：**≤2026-06-30 全部 UTC 墙钟误标、≥2026-07-01 全部北京墙钟，五表边界违例均为 0**（比 T lane 的"hour≤7"逐行规则更强：日期规则零歧义）。T lane 报的"07-20 起"系其 510300 窗口视角；全表过渡窗 07-01..07-19 已是北京钟（S-OWNER 考试子集 31 只）。
- trade_date 列**零错日**（UTC 段 trade_date≠toDate(trade_time+8h) 的行数=0）——只需平移 trade_time 一列。
- +8h 落点与现存北京段**零碰撞**（五表逐一 SEMI JOIN 实证）。
- **个股分钟族零受累**（kline_1min/15min/30min/60min hour≤7=0）；kline_5min 有 8,195 行 2026-09-08 单日 hour≤7 零星行=另一独立写入瞬断，不在本工单（登记备考）。
- 510300 全史口径：55,725 行中 55,072 误标（T lane 的 15,405/14,752 是其分析窗子集）。

## 2. data_ops_sop 三步验证（§1 硬闸）

1. **必要性**：有消费方且语义要紧——T lane 极值分析已自带归一消费；后续任何分钟级策略/研究读 ≤06-30 数据必须归一，修复后才能裸读。api_server 数据总览仅计数不敏感（见 §4）。
2. **真实性**：五表行数/小时分布/边界/碰撞/trade_date 全部 CH 实证（上表），样本可复核（本文档所有数字可用同 SQL 复算）。
3. **可逆性**：修复走**影子表重建+RENAME 换名**，旧表整体保留 `*_tz_bak_20260918`——回退=反向换名，零数据丢失；重建前行数/sum(volume) 对账不平即 ABORT（影子表保留待查）。trade_time 在 ORDER BY 键内 ALTER UPDATE 被禁，故必须重建路径（apply_timezone_migration 同款约束）。

## 3. 修复件（已就绪，默认 dry-run，--execute 才动真格）

`scripts/ch/repair_etf_minute_tz_split.py`（已过 dry-run：五表前置核验全 ok=true，零写入）：

```bash
python scripts/ch/repair_etf_minute_tz_split.py             # dry-run（已跑，全绿）
python scripts/ch/repair_etf_minute_tz_split.py --execute   # Owner 批准后真修（约 4.12 亿行重写，建议非交易时段）
python scripts/ch/repair_etf_minute_tz_split.py --verify    # 修后核验（hour<=7 应清零，非零退出码 4）
```

- 变换：`trade_time + 8h WHERE trade_date <= '2026-06-30'`，`INSERT SELECT * REPLACE (...)` 进影子表（DDL 引擎子句原样克隆：ReplacingMergeTree/PARTITION toYYYYMM(trade_date)/ORDER BY (symbol,trade_time)）。
- 合规：scaffold 正门创建+force-override（路径词 'data' alias 撞 integrator=同族巧合，先例 repair_kline_degraded_pull 同域同蓝图）+大白话翻译登记+路径树已刷新。

## 4. 全下游影响扫描（谁读过这张表谁要复核）

| 消费方 | 用法 | 影响判定 |
|---|---|---|
| kimi-audit T lane（510300/510500 极值分析） | ad-hoc 读+自带 hour≤7→+8h 归一 | **结论不受累**（已正确处置；其去重 336 行为窗内自处理） |
| src/zephyr/frontend/dashboard/api_server.py:1447 | 数据总览标签+行数计数 | 不受累（无时间语义） |
| src/zephyr/data/speed_tester.py:275 | 510050 速度测试 | 不受累（测时延不读时间语义） |
| src/zephyr/data/implementations/miniqmt_provider.py + tasks.yaml:372 | 写入侧（07-01 起北京钟 ✓，max(trade_time)=2026-09-16 14:00 实证） | 无需改动 |
| scripts/ch/archiver.py:89 | 按 toYYYYMM(trade_date) 分区归档 | 不受累（trade_date 零错日） |
| scripts/data/repair_kline_degraded_pull.py:67 | 表清单（写入侧） | 不受累 |
| S-OWNER 考试（st-sowner001/002，2026-07 窗 31 只子集） | 消费 07 月分钟数据 | 07 月数据本就是北京钟→大概率不受累；若其读 ≤06-30 段需复核（挂认领，无实证受害） |
| 未来任何 ≤2026-06-30 ETF 分钟消费 | 裸读即错 8h | **修复前须自带归一**（known_data_gaps 条目已写明） |

## 5. 登记与停点

- known_data_gaps.yaml 新条目：`etf_minute_tz_split_pre_202607`（status=monitoring，resolution_plan 挂本件 --execute 等批）。
- **停点声明**：按 Owner 指令"破坏性操作前停下来登记等 Owner"——4.12 亿行重写属 RULE-DATA-OPS 破坏性 DB 操作，三步验证虽全过，放行权在 Owner 门位。Owner 批准=直接跑 `--execute`（建议非交易时段，逐表顺序执行，1min 表最重）。
