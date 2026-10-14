---
ttl: task_bound
completes_when: 清单内问题全部施工完成、或 Owner 叫停、或清单整体被替代时
title: "10 · GPU 与算力"
---

# 10 · GPU 与算力

> 取数时间：2026-10-14 21:0x（CST）　HEAD：`f300c3d02f`　分支：dev
> 原样底稿：`_raw/10_GPU_与算力.md`（106KB + 第二遍补抽 25 段）
> 本域来源文档：22 个（第一查）+ 13 个（第二查）

---

## §0 一句话结论

**GPU 侧最大的变化是 `_GPU_AUTO_MIN_CELLS` 已从 8,000,000 下调到 500,000**（`_c4_engine.py:622`）——
09-30 记忆里"小尺寸别上 GPU（8e6 格守卫）"这条**已过时，需更正**：现在 50 万格就自动上 GPU。
`gpu_core.py` **已真合入主树**（1,346 行），消费方 3 处（含 `backtest/__init__.py:60` 顶层导入）。
**依赖口径矛盾仍在**：实测 `torch 2.13.0+cu126` 且 `cuda.is_available()=True`，而裁定 `#ARCH-TORCH-CPU-ONLY` 钉的是 CPU 版。

---

## §1 现状实测

| 指标 | 读数 |
|---|---|
| `src/zephyr/backtest/gpu_core.py` | **1,346 行**，已在 HEAD（09-30 时还在 worktree 未合入） |
| gpu_core 消费方 | **3 处**：`src/zephyr/backtest/__init__.py:60` `from zephyr.backtest.gpu_core import (`（顶层导入）；`scripts/backtest/factory_grid_executor.py:3071` `from zephyr.backtest import gpu_core as _gc_sum`；`tests/research/backtest/test_gpu_core_parity.py:46` |
| `_GPU_AUTO_MIN_CELLS` | **`500_000`**（`scripts/backtest/translated/_c4_engine.py:622`）；使用点 `:845` `if backend == "gpu" or weights.size >= _GPU_AUTO_MIN_CELLS:` |
| torch 实测 | **`2.13.0+cu126`**，`torch.cuda.is_available()` = **True** |
| requirements 中 torch | 本轮 grep 未命中（requirements*.txt 清单未取到，需复核文件是否存在） |
| E0 算力闸 | `compute_window_gate.py:55-56,64-65,93-94,104`：`OPEN_BUFFER=09:00` / `CLOSE_BUFFER=15:30` / `light_only` / `heavy_ok`，**按交易时窗分级（与 GPU 可用性无关）**，正常 |
| gpu 相关测试 | `tests/research/backtest/test_gpu_core_parity.py`、`test_l2_gpu_landing.py`（见 gpu_core.py:6 [TESTS] 锚）；`docs/03_modules/_domain_backtest/algo_flow/gpu_core.yaml`（ALGO_FLOW 锚在位） |
| `docs/_working/gpu_rewrite/` | 12 文件（新基准文档所在） |

---

## §2 确认仍成立（A 类）

| ID | 问题 | 现状证据 | 建议处置 | 优先级 |
|---|---|---|---|---|
| ~~GPU-1~~ | ~~依赖口径矛盾~~ | **✅ 已消化**（见 §3） | 销案 | — |
| **GPU-2** | **`_GPU_AUTO_MIN_CELLS` 已下调到 500,000，旧基准结论（hs300/zz500 上 GPU 反而慢 0.25-0.53x）可能已不适用** | `_c4_engine.py:622` 值 = `500_000`（记忆里是 `8_000_000`）；:845 触发条件 | **必须重跑基准**：50 万格阈值下小尺寸也会上 GPU，若旧结论成立则**大量小任务被拖慢** | **P1** |
| **GPU-3** | **L2 RawKernel 是否投产未核** | `gpu_core.py:6` [TESTS] 锚指向 `test_l2_gpu_landing.py`；该文件是否在 HEAD 需确认 | 核测试与实现 | P1 |
| **GPU-4** | **`gpu_core` 是包 `__init__` 顶层导入** | `src/zephyr/backtest/__init__.py:60` — 与 `bootstrap_kernel.py:38/120` 注释警示的「包 __init__ 传递加载 gpu_core 会把 cupy 塞进…」**存在设计张力** | 核 `bootstrap_kernel.py` 是否已规避 | P2 |
| **GPU-5** | **GPU-01 夜窗首夜 / GPU-02 四夜分片首轮 / GPU-03B 训练线** 三条在等前置 | 见 18 卷 §2.2 解锁 5/6/7 | 见 17 卷 E-9 | P2 |
| **GPU-6** | **旧基准是否被新架构推翻未核** | 新基准文档在 `docs/_working/gpu_rewrite/`（12 文件），本轮未逐条读 | 读后给结论 | P2 |

---

## §3 已过时 / 已消化（B 类）

| 原条目 | 判定 | 依据 |
|---|---|---|
| **依赖口径矛盾：实测 cu126 vs 裁定 `#ARCH-TORCH-CPU-ONLY` 钉 CPU 版**〔原 GPU-1，已推翻〕 | **✅ 已消化，销案** | **三重证据闭合**：①**全量 4 份依赖声明面全部指向 cu126、无一残留 CPU 钉版**——`requirements.txt:23 torch==2.13.0+cu126`（#ARCH-TORCH-CUDA-PIN）、`pyproject.toml:58 "torch==2.13.0+cu126"`（收编为显式核心依赖）、`requirements-dev.txt` 无 torch、`requirements-demo.txt` 无 torch；两处 `#ARCH-TORCH-CPU-ONLY` 字面**仅存在于注释正文**（`:6` supersession 注记 / `:32` 病根描述），不起锁定作用；②注册表 `architecture_issue_registry.yaml:9858-9866` `#ARCH-TORCH-CPU-ONLY` 已 `superseded_by: #ARCH-TORCH-CUDA-PIN`（**2026-10-12 Owner 裁定③**）；③本机实测 `torch.__version__=2.13.0+cu126` / `torch.version.cuda=12.6` / `cuda.is_available()=True` / `device=NVIDIA GeForce RTX 3090` / `cupy 14.2.0` |
| **`gpu_core.py` 未合入主树**（09-30 结论） | **已合入** | 1,346 行在 HEAD，且有 ALGO_FLOW 锚 + [TESTS] 锚 |
| **主树接线缺失（ImportError 静默回退）** | **已接线** | `backtest/__init__.py:60` 顶层导入；`_c4_engine.py:622/845` 有阈值与触发点 |
| **E0 算力闸异常** | 正常 | 时窗分级正确 |

---

## §4 🔴 本域新发现

1. **`_GPU_AUTO_MIN_CELLS` 8e6 → 5e5（降了 16 倍）**——这是**记忆与现状的硬漂移**，任何按旧阈值写的调度/预期都失效。
2. **`gpu_core` 被包 `__init__` 顶层导入**，而 `bootstrap_kernel.py` 的注释明确警告过这种模式会"把 cupy 塞进宿主不知情的上 GPU"——**两条设计意图冲突**，需裁定。

---

## §5 Owner 门位

| # | 事项 |
|---|---|
| **O-GPU-1** | torch CPU vs cu126 依赖口径裁定（改依赖=生产环境变更） |
| **O-GPU-2** | GPU-03B 训练线（金标集 v1 冻结后开跑，及格线 0.767） |
| **O-GPU-3** | F5（GPU ③ 立项）追认——L2 已在施工是否"先斩后奏"（17 卷 A-12） |

## §6 无法判断（C 类）

| 事项 | 阻塞点 |
|---|---|
| requirements 是否真钉 CPU 版 | 本轮 grep 未取到 requirements 文件清单，需复核 |
| L2 RawKernel 投产状态 | 未读 `gpu_core.py` 实现段 |
| 新基准数字（吞吐/利用率） | `docs/_working/gpu_rewrite/` 12 文件未逐条读 |

## §7 可复现取证命令

```bash
"C:/Users/fanzi/AppData/Local/Programs/Python/Python312/python.exe" -c "import torch;print(torch.__version__, torch.cuda.is_available())"
grep -rn "_GPU_AUTO_MIN_CELLS" --include=*.py src/ scripts/
grep -rn "from zephyr.backtest.gpu_core\|import gpu_core" --include=*.py src/ scripts/ tests/
git show HEAD:src/zephyr/backtest/gpu_core.py | wc -l
```
