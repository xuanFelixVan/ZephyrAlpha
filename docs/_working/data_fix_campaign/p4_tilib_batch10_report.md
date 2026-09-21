---
ttl: task_bound
campaign: 总包甲·数据正确性线
work_order: WO-4（分包4·tilib 延续批·批10 筹码族）
session: st-data-fix-20260921
date: 2026-09-21
status: done_code_trial_accepted_backfill_blocked
---

# WO-4 批10 筹码族三件套 施工报告（代码层+试跑+210 列验收准备）

> 前置裁定执行情况：时序板 `docs/_working/unified_campaign/t_timing_window_board.md` 截至 2026-09-21 10:50 **无乙 W1 done 行**（仅分包1 CH 重启、分包5 F→G 镜像两行 done）→ 按总包前置：代码/注册表/测试/单票试跑全做，**全市场回填未做**，恢复命令见 §5。

## 1. 交付物①：三件套实现+单测全绿+CYQ 复算对表

### 1.1 实现（src/zephyr/factor/technical_indicators/chips.py，MOD-L02-031，第 9 类 chips）

| indicator_id | 输出列 | 算法口径 |
|---|---|---|
| cyq | chips_winner / chips_avg_cost / chips_cost_5 / chips_cost_95 | 迭代衰减筹码分布（400 bins，PIT 只用过去+当日；一字板全质量落位；tr>100% 截断；NaN 不衰减；网格越界 CDF 质量守恒重铺） |
| scr | scr | 100×(cost95−cost5)/(cost95+cost5)，与 CYQ 分位同源 |
| cyc | cyc_5 / cyc_13 / cyc_34 / cyc_inf | cyc_N=Σamount/(Σvolume×100)（通达信原式）；cyc_inf=DMA(close,tr/100) 递推，种子=首收盘 |

- **契约扩张落地**（16 号 memo §2/§6.10）：指标输入首次引入换手率。provider 仅 daily 并入 stock_daily_basic.turnover_rate（`_merge_turnover_rate`）；`_filter_symbol` 白名单放行该列；chips 指标缺列软降级空输出（禁抛——provider 逐标的异常会跳过整标的）。
- **量纲实证修正**：kline_daily 存量 volume=手（000852 2026-09-01：124016 手×100=1.24 亿股 ↔ turnover_rate=1.3051% 交叉吻合；首跑 CYC=558.6 恰大 100 倍实证）→ CYC 按通达信原式 ÷100。表 DDL 注释"成交量(股)"与存量不符=既有漂移，留痕 memo §6.10 不代改。

### 1.2 单测（tests/zephyr/factor/technical_indicators/test_chips.py，30 用例）

- 手工精确场景：单日均匀 winner=0.5、两日手算 winner=140/190、avg=2190/190、q05/q95 解析解；
- 边界：停牌（volume=0 分布冻结）、新股（单日/价格破网格）、一字涨跌停（低换手旧筹码留存拉低均价=手算 10.753 精确复核）、换手 100%/250% 截断等价、NaN 换手=0 衰减等价、全零成交量 NaN 不前填；
- **PIT 无前视不变量**：前缀序列输出==全序列前缀（rtol=1e-12）；
- 软降级：缺换手率 CYQ/SCR 空输出不抛、CYC cyc_inf=NaN 余列照算、缺 amount 硬列仍 ValueError。
- 全套件：**1109 passed, 5 skipped**（含 DDL↔Registry 210 列双向交叉校验）。

### 1.3 CYQ 抽样复算硬验收（000852 近 20 交易日，PASS）

- 方法：独立实现（另编码：clip 索引法铺量/不同分位实现路径，同 400 bins 口径）复算 2021-01-04→2026-09-18 全 1386 根，取近 20 交易日逐日对表 vs 引擎；
- **结果：winner 逐日偏差 0.0（20/20）、avg_cost 最大偏差 1.78e-15、分位 0.0**；
- 对表留痕：`.runtime/tmp/st-data-fix-20260921/cyq_recalc_000852.tsv`（日期/收盘/双实现 winner/avg/q5/q95/偏差全列）；
- 样例（2026-09-18）：close=5.46，winner=0.3211304203（双实现逐位一致），avg_cost=5.961198，q5=5.026115，q95=8.052431。

## 2. 交付物②：注册表 138→141 + memo 更新（红证双向）

| 方向 | 证据 |
|---|---|
| 注册表字段 | `technical_indicator_registry.yaml`：version **1.5.0→1.6.0**，entry_count **138→141**，last_updated 2026-09-21，description 9 大类/140 在产/210 输出列；safe_write_text CAS 写入（before/after sha256 留审计），yaml.safe_load 复核 entries=141==entry_count，IND-CHIPS-001/002/003 在册 |
| 测试反向锁 | test_indicator_base.py `_EXPECTED_TOTAL=140`/`_EXPECTED_COLUMN_TOTAL=210` 契约钉死，Registry↔DDL 集合相等测试过 |
| DDL 落地 | market_technical_indicator.py +9 列（INSERT_COLUMNS 同步）；CH 逐列 ALTER 干净进程执行，system.columns 探针 **9/9 Nullable(Float64) 全绿**（`.runtime/tmp/st-data-fix-20260921/alter_chips_columns.py`） |
| memo 活真源 | 16 号 v1.11.0：§2 契约扩张条、§6 头计数 140/210、新 §6.10 筹码族（含量纲实证）、修订记录行；frontmatter version 1.0.1(滞留)→1.11.0 消矛盾 |

## 3. 交付物③：单票试跑绿证（两票近 33 交易日，实测数字）

- 链路：InternalComputeProvider.fetch（含换手率并入）→ BufferedWriter → CH；66 行写入，盘中轻写合规；
- **000852**（2026-08-05..09-18，n=33）：chips_winner/avg_cost/cost_5/cost_95/scr/cyc_inf 全部 **33/33 非空**；cyc_5=29/33、cyc_13=21/33、cyc_34=0/33（=33 日窗口预热期精确计数，非缺口）；最新日 winner=0.2691、avg_cost=5.662、scr=7.429、cyc_5=5.586、cyc_inf=5.542；
- **000001**（同窗 n=33）：chips 五列+cyc_inf **33/33 非空**；最新日 winner=0.6353、avg_cost=11.542、scr=3.516、cyc_5=11.732、cyc_inf=11.295；
- 口径备注：窗口化试跑=路径依赖指标冷启动，winner 与全历史值（0.3211）不同属预期；正式数值以 §5 全历史回填为准。

## 4. 交付物④：210 列验收台账（全量扫描今晚低峰执行）

- 台账脚本：`scripts/audit_technical_indicator_columns.py`（列清单动态取自 INSERT_COLUMNS 真源，禁手抄静态清单）；
- **盘中已验证**：sample 模式轻查询抽验 000852 chips 三列输出正常；
- **全量命令（禁盘中跑，153GiB 重读+内存总闸）**：

```bash
# 前置：长任务登记防误杀
echo "audit_technical_indicator_columns" >> data/runtime/process_reaper_keep.txt
# 低峰窗执行（22:00 后或 05:00 夜跑结束后，避开 02:30 tilib_indicator_backfill_nightly 带）
python scripts/audit_technical_indicator_columns.py --mode summary --period daily \
    --out .runtime/tmp/st-data-fix-20260921/audit_ledger_daily.tsv
```

- 判据：total>0 且 **0 非空列=0**（210 列含批10 9 列；cyc_34 等预热期除外口径=列级非空计数>0 即达标）；exit 1=存在全空列（缺口清单在台账）。

## 5. 全市场回填恢复命令（被时序板乙 W1 前置挡，交总包）

解禁条件：`t_timing_window_board.md` 出现乙 W1 done 行且无其他 active 窗冲突 → 经时序板自查后择低峰执行。

```bash
# 单进程串行（血泪铁律：并发=互相撞死），dry-run 预检先行
python scripts/data/backfill_technical_indicator_dwm.py --periods daily --end 2026-09-21 --dry-run
# 实跑（默认起点 2021-01-01 全历史重算，chips 9 列随批补齐；盘中禁跑）
python scripts/data/backfill_technical_indicator_dwm.py --periods daily --end 2026-09-21
# 替代路径：代码入库后，02:30 夜跑 tilib_indicator_backfill_nightly 同口径自动补齐（该任务默认起点即 2021-01-01）
# 回填后必跑：§4 台账 summary 判 0 空列 + 本报告 §1.3 复算脚本抽查三票
```

## 6. 合规链与遗留

- capability_lookup.find('technical indicator chips', session) 已留审计（0 命中=新族无既有能力卡）；
- creation_token：chips.py/audit 脚本/p4 报告三件已登记 creation_tokens 节（两段式：token 先批入 HEAD，正文随后批）；
- add_module_translation.py 已登记（7160/7161 条）；depgraph 生成器跑通 2×（chips.py 节点未见于 nodes 表——cycle.py 同样缺，模块节点登记口径与文件扫描分离=既有现象，留痕待治）；
- ROOR（registry_of_registries.yaml）REG-IND-001 描述停于"41 条/58 列"=既有漂移，该文件由 st-code-doc-20260921 持有，按作用域纪律不代修；
- 全部写入 CH 走 DatabaseService/ch_writer/ch_reader；无 OPTIMIZE/TRUNCATE/DROP；测试只写 tmp_path。
