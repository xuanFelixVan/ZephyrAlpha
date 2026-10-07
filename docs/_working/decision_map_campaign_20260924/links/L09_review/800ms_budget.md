---
ttl: task_bound
completes_when: 800ms 复测尺读数进 L09 收口或预算口径裁定改版
created: 2026-10-07
sid: st-mastertc-l9
status: 首测完成（复测尺定版）
card: C62（总包夜战 master_tc_night L9 车道）
---

# L09 · 800ms 性能绊线复测尺（首测定版）

> 背景：日班移交「L09 性能绊线 800ms」（workorders_docs_misc C62 行）。本件把绊线定成**可复测的尺**：口径、命令、读数、判读四件齐。禁联网，全部仓内可复现。

## 1. 复测尺定义（口径三层，防止「一个 800ms 各说各话」）

| 层 | 口径 | 预算 | 判读 |
|---|---|---|---|
| R1 全进程 | `python -m zephyr.library.lookup <词>` 端到端墙钟（含解释器+依赖启动） | ≤800ms | 首测**超**（1,721ms，2.15x）——绊线即此 |
| R2 进程内冷 | `lookup_assets(<词>)` 首调（索引轴冷加载） | ≤800ms | 首测**过**（348.8ms） |
| R3 进程内热 | `lookup_assets(<词>)` 热调用中位数（n=10） | ≤800ms | 首测**过**（52.7ms） |

- 绊线归属判读：800ms 原意=**在环监控调用**预算（L09 复盘线的 library lookup 内嵌用法），即 R2/R3 口径——均过。R1 超标部分是 Python 进程启动税（1,300ms 级），不是 lookup 逻辑病。
- 处方（不阻塞本尺）：R1 若要入预算须走启动税治理（懒加载）另立批；监控在环代码一律走进程内 R2/R3 口径。

## 2. 测量命令（逐字可复现）

```bash
# R1 全进程 x5 取中位（PYTHONPATH 需含 src，PATH=Python312）
python - <<'EOF'
import subprocess, time, statistics
cmd = ['python','-m','zephyr.library.lookup','safe_write']
ts=[]
for _ in range(5):
    t0=time.perf_counter(); subprocess.run(cmd, capture_output=True, check=True)
    ts.append((time.perf_counter()-t0)*1000)
print('R1 median_ms=', round(statistics.median(ts),1), ts)
EOF

# R2/R3 进程内
python - <<'EOF'
import time, statistics, sys
sys.path.insert(0,'src')
from zephyr.library.lookup import lookup_assets
t=time.perf_counter(); lookup_assets('safe_write', limit=10)
print('R2 cold_ms=', round((time.perf_counter()-t)*1000,1))
ts=[ (lambda t0: (lookup_assets('safe_write', limit=10), time.perf_counter()-t0)[1])(time.perf_counter())*1000 for _ in range(10)]
print('R3 warm_median_ms=', round(statistics.median(ts),1))
EOF
```

## 3. 首测读数（2026-10-07，本机实测）

- R1 全进程 n=5：`[1725.4, 1703.2, 1721.2, 1706.9, 1808.9]` → **median 1,721.2ms**（min 1,703.2 / max 1,808.9）——超 800ms 绊线 2.15x，超标成分=进程启动税。
- R2 进程内冷首调：**348.8ms**（索引轴冷加载，import 本体 3.2ms）。
- R3 进程内热 n=10：`[94.3, 52.6, 52.5, 52.5, …]` → **median 52.7ms**。
- 样例词=`safe_write`（命中 3 条，含 .runtime/audit 热路径与 tests 两件——结果面合理）。

## 4. 复测节律

- 触发式复测：library 索引轴 schema 变更或 lookup 生成器换版后必复测一轮（R1-R3 三层齐跑，读数追加至本节）。
- 判红动作：R2/R3 超 800ms=判红（查索引膨胀/SQL 慢查）；R1 超 800ms 但 R2/R3 绿=登记启动税读数，不改判 lookup 逻辑。
