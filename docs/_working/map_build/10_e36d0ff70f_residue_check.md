---
ttl: task_bound
completes_when: 结论三行并入转正批收尾报告后归档
title: e36d0ff70f 残留核查（转正批前置件，任务3）
owner: st-mapreg-20261003
---

# e36d0ff70f 残留核查报告（只读挖矿，零写入）

> 核查对象：commit `e36d0ff70f`（2026-09-28，st-zchief8，「终验处置·孤儿对抗测试退役」）。
> 方法：`git show e36d0ff70f` 全文 + `git log --follow` 三张图 YAML/生成器/校验器路径 + 盘面实测。

## 结论三行

**a) 三张图本体当前状态=在册在产，非半退役。**
三张 YAML 均在 HEAD 且活跃演进：`config/dev_delivery_map.yaml`（531ac17ef7 建 → b192fa39126 2026-09-30 重生成复活「D11-G02 对账尺翻绿」→ 10-03 仍在更新）；`config/trading_day_cycle_map.yaml`（531ac17ef7 建 → a4b503a163 10-02 触达 → fig13 车道在飞）；`config/data_supply_chain_map.yaml`（531ac17ef7 建 → st-vm12surg-20261003 schema 0.3 升版在途）。工件族在盘实测：`generate_dev_delivery_map.py`+`validate_dev_delivery_map.py`（10-03 23:45 仍在被更新）、`generate_trading_day_cycle_map.py`（10-02）、`generate_data_supply_chain_map.py`+`validate_data_supply_chain_map.py`（10-03）；唯 `validate_trading_day_cycle_map.py` 尚不存在（图13 现为生成器单件，校验器/gate 随转正批，属待建非退役）。

**b) 「对抗测试随被测对象退役」的语境=测试模块级 skip，而非图本体退役。**
e36d0ff70f 的处置动作只有两件：给 `test_dev_delivery_map_adversarial.py`（493 行）与 `test_trading_day_cycle_map_adversarial.py`（985 行）加 `pytest.skip(allow_module_level)` + SUBJECT-RETIRED 注记，commit 未触任何图 YAML（stat 仅 2 测试文件纯插入）。其 skip 理由「被测图已于 531ac17ef7 退役」事后被推翻——531ac17ef7（2026-09-26 st-final-build 尾批）实为三图的**诞生 commit**（`git show --stat`：三 YAML +9443 行纯插入，零删除）。

**c) 残留：图13 测试一处活性残留，其余零命中。**
`tests/governance/d5_architecture/test_trading_day_cycle_map_adversarial.py:57-58` 仍带 `pytest.skip("SUBJECT-RETIRED: config/trading_day_cycle_map.yaml retired in 531ac17ef7; ...")` ——指向活图（fig13 车道今夜在飞），属陈旧 skip，处置归 fig13 车道（非本批写域）。图11 侧已自愈：`test_dev_delivery_map_adversarial.py:47` 有「2026-10-03 解封（st-chief-mount-20261003）：skip 所述退役已被推翻」注记。此外全仓 grep `SUBJECT-RETIRED`/退役/降级字样指向这三张图者，再无命中。

## 证据明细

| 件 | 证据 |
|---|---|
| e36d0ff70f 动作面 | `git show e36d0ff70f --stat`：仅 `test_dev_delivery_map_adversarial.py` +493 / `test_trading_day_cycle_map_adversarial.py` +985，两文件为该 commit 新建（携 skip 出生） |
| 531ac17ef7 实质 | `git show 531ac17ef7 --stat -- config/三YAML`：data_supply_chain_map +3562 / dev_delivery_map +1547 / trading_day_cycle_map +4334，全插入 |
| 图11 复活链 | `git log --follow config/dev_delivery_map.yaml`：531ac17ef7 → b192fa39126（09-30 重生成，commit 正文「同批重生成图11 dev_delivery_map」） |
| 图13 活性 | `git log --follow config/trading_day_cycle_map.yaml`：a4b503a163（10-02）后 fig13 车道多袋在飞（q-st-fig13-chief-20261003 队列在案）；盘面 HEAD 与工作树均 48 节点 |
| 图12 活性 | `git status`：config/data_supply_chain_map.yaml staged（st-vm12surg-20261003 三袋 processing 在飞） |
| 校验器账实 | validators/ 目录实测：validate_dev_delivery_map.py（35,982B）与 validate_data_supply_chain_map.py（58,346B）在盘；validate_trading_day_cycle_map.py 无（生成器 generate_trading_day_cycle_map.py 155,229B 在盘） |
| 解封注记 | test_dev_delivery_map_adversarial.py:47（st-chief-mount-20261003）；test_trading_day_cycle_map_adversarial.py:57-58（仍封） |
