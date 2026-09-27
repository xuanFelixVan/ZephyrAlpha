---
ttl: task_bound
title: FMS 战役·读侧门挂接处方（实测数据定档，禁凭印象接线）
created: 2026-09-27
sid: st-fms-tc-20260927
---

# X2 门挂接处方：FMS-REGEN-CLEAN 该不该进 .pre-commit

## 一、现状实测（[亲验] 2026-09-27 10:5x-11:0x）

1. 注册态：`FMS-HYGIENE` 已在 `in_process_gate_registry.yaml:734`（priority=138，enabled=true，warn 起步）；
   **`FMS-REGEN-CLEAN` 在三处登记面零命中**——`.pre-commit-config.yaml` 无 entry、
   `in_process_gate_registry.yaml` 无条目、`gate_registry.yaml`（机生）自然也没有。
   即：检查器本体已落 HEAD（`3f9b600d21`+`q-0009`），但**执法面=0，属"装饰件待接线"形态**。
2. 单对成本实测（上一轮全量 `--check` 的 jsonl 逐对 elapsed）：

| 受检对 | 单次重生成耗时 | 该轮判读 |
|---|---:|---|
| `rule_catalog_registry` | **27.2 s** | clean |
| `registry_master_index` | 15.1 s | drift（硬拦） |
| `script_manifest` | 6.6 s | drift（硬拦） |
| `script_manifest_fulltree` | 0.7 s | drift（硬拦） |
| `gate_registry` | 0.5 s | drift（基线内 warn） |
| `commit_navigation_playbook` | 0.2 s | error（死门护栏，非本缺陷） |
| `docs_index_structural` | 0.0 s | drift（基线内 warn） |

   最坏单对 27.2 s；全量 36 对一轮 ≈50 s（跳过红级/未触发对时）。

## 二、裁定（总筹自裁，附代价标价）

**本战役不把 FMS-REGEN-CLEAN 挂进 `.pre-commit-config.yaml`，改挂事件触发核对器链。** 三条理由：

1. **提交速度代价**：Owner 把"提交链速度"定为全项目开发速度的度量口径；本仓 `rule_catalog_registry`
   一类改动一旦 staged 即触发 27 s 重生成，最坏单对就把一次提交拖过 P50 一个量级——
   用"生成闭环"名义换回提交链退化，代价与收益倒挂。
2. **连坐代价**：当前脏面（主区多车道混合暂存）下该尺报 3 对"基线外硬拦"
   （`script_manifest`/`script_manifest_fulltree`/`registry_master_index`），
   成因=生成器读工作区而他在途件未落地。按提交门挂=无辜提交人被别人的工作树卡死，
   违宪法 §3.1 own-scope 默认。
3. **合规代价**：宪法 §9.3 永久系统禁 cron/Timer；而"备份成功事件链 + 生成链尾步"是已有合法先例
   （`rolling_archive_reconciler` 挂 STAGE 4b 先例），事件面比每次提交面更贴合"生成闭环"语义。

## 三、接线路径（后波照执，勿另起）

1. 挂接位=`scripts/governance/`既有 reconciler 事件链（与 `regen_clean_check.py --check` 同入参），
   **禁新增计划任务**；
2. 提交面只保留**触发过滤的轻量白名单对**（elapsed < 1 s 的对，如 `gate_registry`/`docs_index_structural`），
   重对（>5 s）一律走事件面——阈值写常量，禁散文档；
3. 三对在途假红**不入棘轮基线**（基线是"存量豁免只减不增"，把测量口径缺陷写进基线=永久豁免假问题）；
   待多车道落地、工作树收敛后复测，若仍红=真漂移，走 `--auto-fix` 由属主批清偿；
4. 判据防回潮红样：本处方落册后，若有人在 `.pre-commit-config.yaml` 加回重对 entry，
   `tests/governance/generators/test_regen_clean_check.py` 需有一条断言拒收（后波补）。

## 四、同型提醒（别把 FMS-HYGIENE 急着翻 block）

`FMS_HYGIENE_GATE_MODE` 翻 block 的前置=3,702 条存量基线清偿过半，现远未到；
本班按 §五.3 保持 warn，翻档时机与判据锚在基线条数（机读），不锚日历。
