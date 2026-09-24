---
ttl: task_bound
title: 红证矩阵 · 本包测试承重性变异探针（六项全红）
sid: st-t0-matrix-20260924
created: "2026-09-24"
lane: t0_matrix
evidence_level: A（可复算：脚本内嵌于本包交付，变异-还原带 sha256 双核）
---

# 为什么需要这份文件

本项目 100% AI 开发的硬风险是"自写判据脚本自我证明为真"。测试全绿不等于测试承重——
只有**把产品件改坏而测试转红**，才证明那条断言在守着一个真约束。本包对四条新逻辑
（六段映射引用性 / auto_mount 去重修复 / M-2 往返同体 / 新轴闭卷定档）逐一施加最小变异，
观察 pytest 是否转红。

## 探针结果（2026-09-24 02:2x，Python 3.12.8 / pytest 8.4.2）

| # | 变异（把产品件改坏） | 目标测试文件 | 结果 | pytest 尾行 |
|---|---------------------|-------------|------|------------|
| 1 | 灰度五档边界改成自定值 `(0.25,0.45,0.65,0.85)` | test_t0_gpu_condition_pack.py | **RED ✔ 承重** | 1 failed |
| 2 | 板别判定恒返回主板（废掉创业板/科创板识别） | test_t0_conditional_e4_v3_exam.py | **RED ✔ 承重** | 1 failed, 4 passed |
| 3 | M-2 退化回"先合并所有 run 再配对"（即 V2 的缺陷做法） | test_t0_conditional_e4_v3_exam.py | **RED ✔ 承重** | 1 failed |
| 4 | 撤掉 auto_mount 的去重（`if snap.index.has_duplicates`→`if False`） | test_t0_six_phase_materialize.py | **RED ✔ 承重** | 1 failed, 11 passed |
| 5 | 六段映射改为本地自定字典（脱离 auto_mount.R2SIX） | test_t0_six_phase_materialize.py | **RED ✔ 承重** | 1 failed |
| 6 | 新轴定档窗越过闭卷切点（`2025-09-09`→`2026-12-31`） | test_t0_gpu_condition_pack.py | **RED ✔ 承重** | 1 failed, 23 passed |

**6/6 全部转红**；每轮变异后按字节还原并核 sha256 全等（`all hashes restored OK`）。

## 复算命令

```bash
cd D:/ZephyrAlpha/.worktrees/st-t0-matrix-20260924   # 落地后改主区路径
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
# 正向：全绿
python -m pytest tests/audit/test_t0_conditional_e4_v3_exam.py \
  tests/audit/test_t0_gpu_condition_pack.py \
  tests/audit/test_t0_six_phase_materialize.py \
  tests/backtest/test_auto_mount.py tests/backtest/test_auto_mount_sle3.py -q
# 期望：179 passed（其中 76 项是 auto_mount 既有回归，证明本包修复零破坏）
```

变异探针本身是**临时件**（字节级写回 + 还原 + 哈希断言），不在仓内留脚本，
避免"测试用的测试"成为第二套真源；上表即其运行记录。

## 同轮另外两条"能红"证据（非本包测试，是判据件自证）

1. **v1 考件守卫触发**：情绪门接成可评后，`t0_conditional_e4_exam.py` 按其自身 `:147` 条款
   精准 `SystemExit`，未产出任何 verdict 文件，09-22 基线 yaml 字节未变 ⇒
   证明该 fail-closed 闸是真的会拦，不是文档装饰。
2. **frozen 判据逐位复现**：`cost_trio_exam.py` 原样重跑得 24 对/0 净正/0≥30bp/毛 −9.2bp/
   毛 p50 −5.13bp，与 09-22 提交信息所载五值**逐位一致**（其 `[TESTS]` 注释里的"净 −45.0"
   与自身产物 −40.40 不符=文档漂移，已登记，不据以改判据）。
