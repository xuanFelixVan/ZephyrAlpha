---
ttl: task_bound
completes_when: 全流通战役收口报告归档
---

# 处方 · daily_valuation 行情三列恒 0（N-1 型错数）——交派生/接入车道

**本车道只点亮，不动手**（`src/zephyr/data/implementations/*provider*.py` 禁写）。

## 症状（2026-09-18 亲验，只读）
- `c1_market.daily_valuation` FINAL **259,238** 行；`countIf(close<>0)=0`、`amount`=0、`turnover`=0；`countIf(isNull(close))=0`（列非 Nullable → 无值被写成 0）。
- 近月窗（>=2026-09-01）**87,377** 行同样三列全 0，而 `pe_ttm` 非零 **87,111/87,377（99.7%）** → 派生链的"估值比"腿是活的。
- `data_source=local_valuation`、`max(trade_date)=2026-09-17`（新鲜）。
- 同日同标的与 `c1_market.kline_daily.close` 逐行对照抽 20：**20/20 不一致**（dv=0 vs kd=6.41/8.08/4.94…）。

## 判读
不是"缺数"，是**错数进闭环**：任何读 `daily_valuation.close/amount/turnover` 的下游（换手率、成交额类因子、流动性闸）拿到的是 0，且不会被任何行数/新鲜度检测发现。

## 建议处置（按优先级）
1. 写侧：`local_valuation` 派生在行情三列取不到值时**禁写 0**——要么写 NULL（列需改 Nullable，走 DDL 评审 + RULE-SCHEMA-TZ），要么整行不写并计 degraded；
2. 若列不宜改 Nullable：把"是否有价"上移为质量标志位，由下游按标志过滤；
3. 消费面排查：`git grep -n "daily_valuation" src/**` 找出读 close/amount/turnover 的因子，在其上挂非零率断言；
4. 哨兵侧防线本车道已落：`data_supply_sentinel.yaml` 的 `column_fill_ratio{cols:[close,amount,turnover], min_ratio:0.95, window_days:10}`——修复落地后该腿自行转绿，**禁为过检把 min_ratio 调低**。
