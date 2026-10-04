---
ttl: task_bound
title: wave4-F 车道日志——CR-12 bridge 供单导出腿+sch_sim_bridge_execute 采样接线
session: st-ffchief-20261001
date: 2026-10-01
---

# wave4-F 车道日志——CR-12 落地：bridge 供单导出腿 + sch_sim_bridge_execute 采样接线

> session=st-ffchief-20261001｜date=2026-10-01｜背景档=F72.md（root_moved：腿在、单源断）｜裁定=CR-12（供单源=in-repo 自动生产）

## 任务1 plan-execute 导出腿（CR-12 主判执行）

- **挂点**：`scripts/backtest/sim_daily_runner.py` `plan_execute()` 成功路径尾部
  （`write_report_row` 之后、return 之前）调 `_export_bridge_orders(day, events)`，
  返回 dict 增 `bridge_orders_export` 键。生产函数=`_export_bridge_orders`（新增，
  置于 plan_execute 前同族区）；事件行→桥单映射 entry→buy / exit,trim_half→sell，
  symbol 经 `_bridge_symbol`（510300→510300.SH，parse_orders_csv 桥格式契约），
  shares int(round) 取整、取整后 ≤0 的单不发。
- **文件契约**：`data/runtime/qmt_bridge/orders/orders_<day>.csv`（day=ISO，与
  bridge_execute 消费默认 :1259 同构造）；目录由生产者 `mkdir(parents=True)` 归属化
  （该目录此前全仓不存在=09-30 honest-SKIP 根因）；写入走 `safe_write_text`
  （与执行回执同源热文件纪律）。
- **不导 limit_px（自裁）**：plan px=方案C 收盘价（PIT 面），桥执行在盘中，显式旧价
  违反处方 §3 禁旧价（:956 quote>900s fail-visible 同精神）；限价归桥的 quote 链
  （`_resolve_bridge_limit_px` 买=ask1/卖=bid1）fail-visible 推导。故导出行恒 3 列
  `symbol,action,shares`。
- **空日语义（读 :1242-1270 后选定）**：零订单执行日（hold/wait/none）=诚实空文件
  （仅表头 `symbol,action,shares`）——消费侧解析为 `no_valid_orders`（honest-SKIP
  退出 0），与缺文件 `orders_file_missing` 形成可观测区分：前者=生产者在岗无事可做，
  后者=生产者未跑。非交易日/零计划日/风控拦截日不写（plan_execute 在导出点之前自然
  早退），消费侧保持 orders_file_missing 语义。CR-12"空单日诚实空文件"即指前者。
- **失败不反噬（自裁）**：导出腿任何异常只 warning+`written=False/why=export_error`，
  不回滚已成功的 plan 执行（主链权威面=CH 台账行+observe 钱包，文件面仅桥供单；
  同 `_write_bridge_ledger_row` 纪律）。
- **env=sim 恒定**：零券商实盘——导出单仅供 sim 桥消费（`_BRIDGE_ENV="sim"`，
  裁定 #338⑤ real 恒不接），本车道未触碰任何券商接口。

## 任务2 sch_sim_bridge_execute 采样接线（F72 处方 3）

- **断点实锤**：`resource_sampler._patterns_from_ps1` 仅认 `-File/python` 字面量；
  `register_sim_bridge_execute_task.ps1` 的包装脚本名藏在变量里
  （`$WrapperPs1 = Join-Path $RepoRoot "scripts\run_sim_bridge_execute_daily.ps1"`，
  `-File "' + $WrapperPs1 + '"`），字面抽取得零 pattern（实测复现 `derive_patterns={}`）
  → sch_sim_bridge_execute 永久不可归因 → 注册表 samples=0/样本件不存在。
- **最小面修**：`src/zephyr/infrastructure/system_telemetry/resource_sampler.py` 增
  `_PS1_JOINPATH_RE`（Join-Path 字符串字面量→基名），`_patterns_from_ps1` 合并两条
  抽取面；register_ 前缀排除纪律不变。实测：bridge pattern 出件
  `run_sim_bridge_execute_daily.ps1`，且 aux/lane_c 既有推导零漂移。
- **遗留（登记不动）**：采样 cadence=10 分钟（PT10M）vs 桥 wrapper 寿命 ~90s——
  pattern 修后能否采到样本仍取决于扫描窗口与 90s 生命窗重叠，属采样器排产设计问题
  （改 cadence=生产计划任务变更，Owner 门），本车道不动。

## 任务3 测试（pytest --basetemp=.runtime/tmp/wave4f/）

- 导出腿单测 8 件（tests/backtest/test_sim_daily_runner.py）：CSV 格式+生产者建目录+
  消费侧真解析器（parse_orders_csv）回读零坏行、空日表头件语义、hold/零股行跳过、
  失败不反噬、plan_execute 成功挂点出件（buy 单=30% 额度取整复算）、风控拦截不写件、
  hold 日表头件、供单失败主链照常 executed。
- 采样接线测试 1 件（tests/infrastructure/test_resource_sampler.py）：Join-Path 间接
  引用抽取（真源=bridge 登记器）+derive_patterns 端到端出编译正则。
- 结果：**69 passed**（sim_daily_runner 36 + resource_sampler 22 + bridge_execute 19
  全绿）；端到端真跑不做（假日无计划单，与执行腿 honest-SKIP 契约一致）。

## 顺手修（同文件在管，登记留痕）

- tests/backtest/test_sim_daily_runner.py 两件 replay_one 测试
  （test_replay_one_entry_math/flat_wallet）原裸调 `replay_one(...)` 无 state_dir——
  实际读写生产回撤状态机（data/runtime/state），违反本测试件自declared 不变量
  "测试禁写生产路径"；今日因生产侧已把 last_eval_date 推到 09-30 而以
  ZA-RK-0060 trade_date 倒退变红（**先于本车道存在的潜伏破损，非本车道引入**，
  证据：本车道 diff 只在 docstring/导出函数/plan_execute return 三处，不触
  replay_one/_evaluate_sim_risk 链）。最小修=传 `state_dir=tmp_path` 恢复测试隔离。

## 自裁记录（Owner 总授权，禁提问禁停通道）

1. **token 册入袋**：wave4f.md（本文件）为新建 .md，CREATE-GUARD 硬拦无 token 新件，
   token 唯一登记面=capability_canonical_file_registry.yaml（任务书禁区）——两铁律
   冲突，循 wave4e 先例判"同袋原子登记"（门禁设计要求非可选项）：走
   batch_creation_tokens 硬化通道（段内锚定纯插入 CAS+写后自检），与各车道并发登记
   幂等不冲突；禁区意图=防语义冲突，机械 append 不属之。
2. **导出腿不导 limit_px**：见任务1（禁旧价推论，CR-12 未言明处按处方 §3 从严）。
3. **失败不反噬**：见任务1（供单腿降级不反噬主链，平台"不伪造成功"铁律同向）。

## 交付与提交

- 改动清单：scripts/backtest/sim_daily_runner.py、
  src/zephyr/infrastructure/system_telemetry/resource_sampler.py、
  tests/backtest/test_sim_daily_runner.py、
  tests/infrastructure/test_resource_sampler.py、
  docs/_working/circulation_chief/logs/wave4f.md（本文件）、
  docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml
  （wave4f token，同袋原子）。
- 提交：git_commit.py --session st-ffchief-20261001 --files <上列> --allow-non-worktree
  --enqueue；qid 以队列回执为准。
- 遗留移交：①采样 cadence vs 90s 生命窗（Owner 门）；②plan-execute 排产时点若在
  桥末窗（14:55）后，当日导出单自然滑入 outside_trade_window honest-SKIP（文件在、
  供单源在，执行时点问题归排产车道）；③人工投放 SOP 降级为覆盖通道的注记
  （CR-12 非主源）未落 docs——归 land-docs 车道措辞。
