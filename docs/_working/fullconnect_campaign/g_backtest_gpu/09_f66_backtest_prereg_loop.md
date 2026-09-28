---
ttl: task_bound
title: "F66 回测预注册与七步循环——REG-BTB-001 跑前写死阈值；无注册不归档"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F66 · 回测预注册与七步循环（总册状态 built/P1；本卷复核=built 维持，**对象数勘误：总册 137→实测 142**）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | config/trading_decision_map.yaml（source_map 实锚，map_schema_version 1.2，effective_from 2026-09-08）；F64 三件套 |
| 下游消费 | 码面消费实测 8：backtest/run_archive.py、core/n_trial_ledger.py、generate_backtest_backlog.py 自身、validate_p0_cost/validate_p0_discrimination、translated/_c4_engine.py、governance/upgrade_tdm_v13_metadata、governance/d3_metadata/check_registry_consistency；流程消费=SOP-B 七步循环+批次决策点+（F25 入库/F50 归因回灌） |
| 自动化触发 | 生成器 CLI（--check smoke 自证）；批次决策点=Owner 三问（SOP-A §5）；无计划任务 |
| 真源与注册表 | REG-BTB-001=docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml；**objects=142（本日 yaml 解析实测；总册"137 对象"与实测差 5）**；generated_at 2026-09-12T06:56；confidence 分布=untested 123/valid 16/pending 2/verified 1（本日 Counter 实测）；对象 schema=object_id/node_ids/node_type/layer/map_layer/flow/market/module_ref/testable/confidence/plan/plan_note（首对象 keys 实测） |
| 门禁与质量尺 | 生成器 INVARIANTS（generate_backtest_backlog.py:8 实锚）："注册先行(SOP-A §1: 无注册条目的回测结果不予归档)；再生成保留既有条目 plan/threshold_status(禁事后挪门柱——冻结阈值只许批次决策点公开修订)；对象从地图解析导出禁手工挑；结构容器/流根标 testable=false(D108)" |
| 当前运行状态 | **绿（机制）/黄（消化）**：预注册-防挪门柱-归档链全在码且被 8 处消费；142 对象中 verified 仅 1+valid 16=消化率低是阶段事实非缺陷（B 批次推进未完） |

## 二、子模块三级枚举（真源三级：SOP 册→生成器→登记表；本日实扫）

- **SOP 面**（docs/01_policies_and_standards/sop/backtest_system_sop/，6 件实测 ls）：sop_a_full_map_orchestration.md（**Step A0 注册→A1 分类合并→A2 优先级→A3 批次≤5 对象走 SOP-B 七步→批次决策点→A4 E2E 冒烟强制插入→A5 归档与地图升级**，:24-83 节题实测；A5=evidence_hash 唯一键写 decisiongraph L5+confidence proposed→verified）；sop_b_node_loop.md（七步循环本体）；exam_policy.md/exam_policy 与 sop_c/sop_d（run_archive_naming）；README+index
- **生成器**：scripts/backtest/generate_backtest_backlog.py（15,204 字节，CONSUMERS=SOP-A A0/A1/A2+verify_run_archive 间接+批次决策点 :5）
- **登记表**：backtest_backlog.yaml（REG-BTB-001，142 对象实测）；归档校验=scripts/backtest/verify_run_archive.py+src/zephyr/backtest/run_archive.py（366 行）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 预注册机制 | built wired（8 码面消费方） | INVARIANTS :8+消费 grep 本日实测 |
| 无注册不归档 | built（纪律+verify 件在） | SOP-A §1 引文+verify_run_archive/run_archive 链；**对"绕过注册直接跑"无硬 gate 拦截**（归档时拦截非跑前拦截） |
| 七步循环执行 | 黄（手动批次制） | SOP-A §5 批次决策点=Owner 三问；automation 缺口=考试编排从未自动运行（IBT-E07，M2-04 §五同判） |
| 地图升级回写（A5） | built 机制/消化黄 | verified 1/142 实测 |

### 骨架勘误
- **对象计数：总册 F66/分工册 TD 组均写"backtest_backlog 137 对象"，本日 yaml 解析实测 142**（generated_at 2026-09-12 早于总册 09-25，非窗口差；疑 137 为更早 map 版本口径沿写）。接线清单 §1.4 未涉此数，请骨架班核正。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | 137→142 计数勘误 | 总册/分工册回写核正（本卷已留证） | P2（文档） |
| 2 | 考试编排从未自动运行（IBT-E07） | GPU 完赛事件触发"考后一链"（M2-05 §五方案，提交队列入 M5） | P1 |
| 3 | valid 与 plan=None 并存（BT-P2-047~053"阈值未预注册"标记-判据不对齐，f41 册实证） | 批次决策点补 plan 或降 confidence（纪律修订） | P2 |
| 4 | 跑前拦截缺（绕注册跑批只能归档时拒） | 跑批入口查 backlog object_id 存在性（XS） | P2 |
| 5 | threshold_status 字段落点（对象级无该键，生成器 INVARIANTS 声称保留——字段在 plan 子结构） | 生成器 schema 注释对齐（XS） | P2 |

## 五、自审闸三态
**挖干可施工**（SOP 七步+生成器 INVARIANTS+142 对象实测三源交叉；勘误 1 条计数）。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "
import yaml,io,collections
d=yaml.safe_load(io.open('docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml',encoding='utf-8'))
print(len(d['objects']), collections.Counter(o['confidence'] for o in d['objects']))"   # 142 Counter(...)
sed -n '8p' scripts/backtest/generate_backtest_backlog.py      # INVARIANTS 全文
grep -n "^## " docs/01_policies_and_standards/sop/backtest_system_sop/sop_a_full_map_orchestration.md   # A0-A5 节
grep -c "" docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml   # 体量对照
```
