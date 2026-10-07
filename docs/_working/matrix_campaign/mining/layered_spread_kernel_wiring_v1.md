---
ttl: task_bound
title: layered_spread_kernel_wiring_v1 —— compute_layer_spread 委托 xp 核接线基准册
session: st-mx07-L4
---

# layered_spread_kernel_wiring_v1 —— compute_layer_spread 委托 xp 核接线基准册

- 车道: st-mx07-L4（matrix 战役 2026-10-07 夜战）
- 真源代码: `src/zephyr/factor/analysis/layered_backtest.py`（MOD-L02-007，D-FACTOR-ANA-06）
- 变更: `compute_layer_spread` 接线委托 `compute_layer_spread_kernel`（新增 `use_kernel: bool = True`
  参数；False 保留原纯 pandas 逐日 `layered_returns` 路径作为后备）。签名向后兼容（原三位调用方不受影响；
  全仓 grep 证实无外部消费方，唯一内部消费方 `parity_end_to_end` 参照侧已显式 `use_kernel=False`，
  防接线后 kernel-vs-kernel 自比失效）。
- depgraph: 存量 file 粒度节点已在册（node_id=16391335，module_id=MOD-L02-007，production），
  本变更属同模块内行为保持型接线，无新模块——按净零内收不重复登记设计节点。

## 1. 对拍实测（2026-10-07 夜，本机实测读数）

`parity_end_to_end()`（参照侧=纯 pandas 后备 vs kernel，quantile_replica 模式，5 组随机面板）:

| 面板 shape | NaN% | 天数(参照) | 天数(kernel) | 逐位相等 | max_abs_diff | >0.5 ULP 天数 |
|---|---|---|---|---|---|---|
| 300x50 | 0.10 | 300 | 300 | true | 0.0 | 0 |
| 500x200 | 0.05 | 500 | 500 | true | 0.0 | 0 |
| 200x80 | 0.25 | 200 | 200 | true | 0.0 | 0 |
| 1622x564 | 0.08 | 1622 | 1622 | true | 0.0 | 0 |
| 100x40 | 0.00 | 100 | 100 | true | 0.0 | 0 |

`all_bitwise = true`（5/5 零差，0 ULP 超限）。层号映射网格实证（`parity_grid`，n=2..400 全量+高段抽样，
k∈{2,3,5,7,10}）quantile_replica 模式零错位（kernel docstring 留档，本次未重跑）。

## 2. 耗时对比（接线后默认路径 vs 纯 pandas 后备，best of 3，本机同进程）

| 面板 shape | kernel(s) | pandas(s) | 提速 | 逐位一致 | 日期索引一致 |
|---|---|---|---|---|---|
| 300x50 | 0.0084 | 0.7278 | 87.1x | true | true |
| 500x200 | 0.0176 | 1.2775 | 72.6x | true | true |
| 1622x564 | 0.1168 | 4.5835 | 39.3x | true | true |

- 实测提速 39-87x，高于历史口径 6.6x（历史读数含不同测量面/负载背景；本机今晚 CPU 占用 ~85%、
  另有 5+ 并行施工会话，读数为同进程同面板对照值，横向可比、纵向仅供量级参考）。
- pandas 侧耗时随天数×逐日 `layered_returns`（qcut+groupby）线性放大；kernel 侧为向量化排序+查找表映射。

## 3. 验收记录

- 既有 layered 测试: `tests/research/factor/test_layered_backtest.py` **10/10 passed**（1.87s），
  其中 TestComputeLayerSpread 4 例已走 kernel 默认路径（含空面板/数据不足截面跳过契约）。
- 对拍+耗时: 见上两表（本机实测）。
- 遗留: `tests/research/factor/__pycache__/test_layered_spread_kernel_parity.*` 为陈旧 pyc
  （独立对拍测试文件已并入主模块后删除），未清理（不属本车道范围）。
