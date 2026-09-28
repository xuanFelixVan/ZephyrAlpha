---
ttl: task_bound
title: "F64 回测三件套——universe 7/benchmark 9/cost_model 6 每测 MUST 指定"
session: zc-l07-20260927
create_guard: creation_token 由落地车道随批补办（M2 车道先例）
---

# F64 · 回测三件套（总册状态 built/P1；本卷复核=三册全 built，条数逐一实测核真，生存偏差缺口在案）

## 一、六向台账（实证锚点）

| 向 | 实证（本日实勘） |
|---|---|
| 上游输入 | 成分/指数/成本三源数据（data 域供）；instrument_master/universe 选择器 |
| 下游消费 | F65 引擎族（每测 MUST 三指定）；F66 预注册循环（SOP-A A0 对象含 universe/benchmark/cost 维度）；GPU 矩阵（_c4_engine 成本口径=MatchingConfig #233，M2-02 实锚） |
| 自动化触发 | imported 库件（无自有触发）；随回测批次消费 |
| 真源与注册表 | 三册（docs/01_policies_and_standards/_registry/catalogs/）：universe_registry.yaml（**universes=7 实测**）、benchmark_registry.yaml（**benchmarks=9 实测**）、cost_model_registry.yaml（**cost_models=6 实测**）；MUST 条款三册各 :21 实锚（"每次回测 MUST 指定 universe_id/benchmark_id/cost_model_id…否则结果严重失真"） |
| 门禁与质量尺 | 生存偏差显式字段 survivorship_free：CSI300/CSI800 两条目 **false 自注"无 PIT 成分文件…MUST 补历史成分"**（universe_registry :180/:214 实测）；delisted_handling include/exclude 语义字段 |
| 当前运行状态 | **built（登记+消费链在）**：成本口径 CST-ASTOCK-001（回测实盘档）/CST-T0-001（做T 31.2bp 往返）双口径（M2-05 §5.7）；三册为回测 MUST 输入被 SOP/prereg 引用 |

## 二、子模块三级枚举（三册三级：册→条目族→关键字段）

- **universe_registry.yaml（7 条）**：每条=universe_id+成分定义+delisted_handling+survivorship_free；CSI300/CSI800 现役无 PIT 成分（生存偏差暴露位）
- **benchmark_registry.yaml（9 条）**：benchmark_id→超额/相对收益基准；000300 为 IBT 基准（M2-06 实锚）
- **cost_model_registry.yaml（6 条）**：cost_model_id→佣金/印花/滑点参数；CST-ASTOCK-001 冻结土规=佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp（prereg objective.cost_caliber 实锚）；市场差异化（转债/跨境 ETF 无印花 1-8bp）
- **消费代码面**：src/zephyr/data/instrument_master.py、crypto_universe_selector.py、signal_ashare/market_cap_tier.py、trading/decision_map.py（registry 映射）、gov_enforcement 双 checker（registry_code_anchor/fingerprint gate）

## 三、接线四态独立复核

| 面 | 四态判定 | 复核证据 |
|---|---|---|
| 三册登记 | built（条数核真 7/9/6） | 本日 yaml 解析三册计数与总册逐一相符 |
| MUST 纪律 | built（语义在）/机检弱 | 三册 :21 MUST 条款实测；**"每测未指定则拒跑"无机械闸**（靠 SOP 纪律+prereg 面约束） |
| 成本口径消费 | built | _c4_engine MatchingConfig #233 零硬编码（M2-02 2.4）+exam_cost_gate 五档 |
| PIT 成分 | **缺位** | CSI300/CSI800 survivorship_free=false 自认（:180/:214） |

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | CSI300/CSI800 无 PIT 历史成分=生存偏差 | 补历史成分文件（册内 MUST 自认；施工级 S） | P1 |
| 2 | 成本两真相分裂（考尺平面 5bp vs IBT ADV 分层，IBT-D01） | Owner 待裁 R-M2-2（建议毕业生复考强制双口径出证） | P1（Owner） |
| 3 | MUST 指定无机械闸（跑批脚本漏指定靠自律） | 跑批入口加三 id 必填断言（XS） | P2 |
| 4 | 登记面欠账口径：环节在册未点 REG 号（wiring 清单 §1.3 通用病） | 机检可达性回填 | P2 |

## 五、自审闸三态
**挖干可施工**（三册计数实测+MUST/生存偏差字段行级实锚；缺口 2 Owner 挂 R-M2-2 不代裁）。

## 六、复跑命令
```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$PATH"
python -c "
import yaml,io
for f,k in [('universe_registry','universes'),('benchmark_registry','benchmarks'),('cost_model_registry','cost_models')]:
    d=yaml.safe_load(io.open(f'docs/01_policies_and_standards/_registry/catalogs/{f}.yaml',encoding='utf-8'));print(f,len(d[k]))"
sed -n '21p;180p;214p' docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml   # MUST+生存偏差
```
