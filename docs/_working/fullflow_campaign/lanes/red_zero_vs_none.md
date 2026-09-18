---
ttl: task_bound
completes_when: 全仓 0-vs-None 同型点逐条判档完毕且高置信项派工落地
---

# 红队 R2② —— "0 / None 语义混用"同型点普查（安静型缺陷族）

> 病形定义（本轮 R-014 抓到的那一类）：**"没有观测" 被写成 "观测到 0"**，
> 于是指标持续产出、永不报错、永不告警，只是**方向永远偏乐观**。
> 判档三问：①0 会不会被下游当**有效观测值**参与聚合/排序/回流？②0 是不是"无基准"的唯一出口？
> ③把 None 折成 0 的那一步是否**跨模块边界**（跨边界即失去"这里曾是 None"的语境）。

## 一、命中（同一族，建议同批处置）

| # | file:line | 形态 | 会造成什么假数 | 置信 |
|---|---|---|---|---|
| 1 | `src/zephyr/ex_core/execution_report.py:52-60` `_signed_slippage_bps` | 函数有两条出口：`(avg-intended)/intended*10000` 与 `if intended_price <= 0: return 0.0`。**没有第三条"无样本⇒None"** | ①**零成交被算成 -10000bps（满分执行）**（本文件主案，实测复现）；②**第二条出口自身就是同型第二例**——无决策基准时返回 `0.0`，而 0.0 在"正=不利"口径里=**零滑点=完美执行**，与"真测得 0 bps"**完全不可分**。即：数据缺失被记成一条满分证据 | **高（亲验，探针跑出 -10000.0 / +10000.0）** |
| 2 | `src/zephyr/ex_core/execution_report_producer.py:344` `avg_price=… or _ZERO`（`:333-335` 先判 None/≤0 再兜底） | None→0 折叠，**恰在跨入 `build_execution_report` 之前一步** | 把"无成交均价"伪装成"均价 0 元"，是 #1 的**燃料**；`avg=0 且 intended=4.07` ⇒ -10000.0 | 高（亲验源码链路） |
| 3 | 同上 `:345` `target_price=order.limit_price or _ZERO` | None→0 折叠 | intended=0 ⇒ 走 #1 第二条出口 ⇒ 该单被记为 **0 bps 完美执行**（而不是"基准价未知、不可判定"）。市价单/无限价单全落此支 | 高（代码直读；未独立造数） |
| 4 | 同上 `:414` `cells.append(f"{float(value):.6f}")` | NULL 在**序列化层**再次不可达 | 即使 #1~#3 改好，只要这里没有 None 分支，落库仍是数字。**8b12ffa789 把列改成 `Nullable(Float64)` 的能力被这一行永久闲置** | 高（亲验） |
| 5 | `src/zephyr/ex_core/execution_report.py:98` `if intended_price < 0 or avg_fill_price < 0: raise` | 用 `<0` 而非 `<=0`/`not in (None,)` 做入参闸 | `0` 被明确判为**合法**并继续参与除法与聚合——闸设在了错误的一侧（挡住负数，放进 0） | 高（亲验：0 通过校验并产出 -10000） |

## 二、待查（形状相同，我未独立造数，**不判为缺陷**）

| file:line | 为什么可疑 | 我缺的那一步 |
|---|---|---|
| `src/zephyr/ex_core/order_execution_saga.py:531` `float(qty * (limit_price or Decimal("0"))) / total_nav` | 双病灶：分子 `or 0` ⇒ 无限价时**仓位权重静默为 0**；分母 `total_nav` 未见零守卫 | 未确认上游是否有 `total_nav>0` 断言；未跑 |
| `src/zephyr/ex_core/trading_session.py:841/845/863-865/879-881/902-904` `qty * (limit_price or 0) * (1±cost_rate)` | 资金预占/释放额度：`or 0` ⇒ 无限价时**预占 0 元**（欠预占=可超买）。这不是"假指标"而是"假风控额" | 未确认市价单是否在此路径上游被强制带限价 |
| `src/zephyr/compliance/manipulation_realtime_monitor.py:350` `price=float(order.limit_price or 0)` | 合规监测的成交价取 0 ⇒ 该笔在操纵识别里可能整体失真（价格 0 通常被过滤，等于**漏计一笔申报**） | 未追该值下游是否被 filter |
| `src/zephyr/ex_core/order_manager.py:557-560` 运行 VWAP 累加 `or Decimal("0")` | 首笔 fill 时 `avg=None→0` 且 `filled_new=0` ⇒ 乘积 0，**当前看是对的**；但依赖"首笔前 filled 必为 0"这一隐式不变量 | 未写钉固化该不变量 |

## 三、排除（**扫过并判定不是病，如实留名以防后人无差别改造**）

这些是"分母为零⇒返回 0"的形状，但 **0 在此处是保守值而非乐观值**，改掉反而制造假信号：
- `src/zephyr/autonomy_core/agentic_drift_guard.py:135-138`（`_entropy`）、`:157-160`（偏离率）：`total = sum(counts)`，`total<=0` ⇔ **没有任何观测**。此时"偏离率 0"= 不指控漂移 → **不会误拉闸**，是 fail-safe 侧。
- `src/zephyr/autonomy_core/drift_semantic_reviewer.py:134-137`：零向量 ⇒ 相似度 0 ⇒ "判定不相似" ⇒ 触发人审 = fail-safe。
⇒ 与 `red_prescriptions.md` P-R2-1 的**判别线**：`0 被读作"没事"还是"好事"`。**滑点/收益/覆盖率型指标里 0=好事（必须改 NULL）；偏离/告警计数型里 0=不报警（不该改）。**
（此即战役"1405 处不得无差别改造"裁定的一个具体落点，机械印证见 R-023。）

## 四、可复现命令

```bash
# 命中 #1/#5（端到端产错数）+ 契约双向探针
python .runtime/tmp/ff-red/r2_slippage_null_probe.py
# 同型点复扫（三条轴）
git grep -nE "(avg_fill_price|target_price|price|value|total|count)[a-z_]*\s+or\s+(_ZERO|Decimal\(\"0\"\)|0(\.0)?)" -- "src/zephyr/*.py"
git grep -nE "if\s+\w*(price|qty|quantity|amount|total|count|avg|nav|equity)\w*\s*:" -- "src/zephyr/*.py"
git grep -nE "return\s+0(\.0)?\s*$" -- "src/zephyr/*.py"
```

## 五、诚实条款

- 第一节 #1/#4/#5 = **亲验**（探针实跑 + 源码链路）；#2/#3 = **亲验源码、未独立造数**。
- 第二节四条 = **我没打完**，不是"攻不动"。要判它们是不是真病，需各自造一条数据看下游消费面。
- 普查**不完备**：我的三条轴只覆盖"列名/属性名里带 price|qty|total|count 等"的显式形状；
  通过 `float()`/`pandas.fillna(0)`/SQL `COALESCE(x,0)` 发生的同类折叠**不在扫面内**
  （已见 `akshare_provider.py:6359` 有 `fillna(0).sum()` 但未追其语义）。⇒ 本节是**下界**，不是全量。
