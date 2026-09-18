---
ttl: task_bound
completes_when: CI 从 collect-only 切到真跑（含并行）的前置条件全部满足或被显式豁免
---

# 测试仪器完整性车道 · CI 真跑前置条件单（T5）

> 车道 = `st-ff-testint-20260918` · 消费方 = 分包12 T4（`st-ff-instL-20260918`，`.github/workflows/governance.yml` owner）
> 目的：把 CI 从 `pytest tests/ --collect-only` 切到**真跑 + 并行**之前，先清掉会让 CI 变成"满屏假红"的地雷。
> 判据来源 = `lanes/testint_census.md`（生成器产出，勿手抄数字）。

## 0. 现状（实测锚点）

| 事实 | 锚点 |
|---|---|
| CI 只做收集不执行测试 | `.github/workflows/governance.yml:265` = `python -m pytest tests/ --collect-only -q --tb=line` |
| 尽调结论 E3（P0）：3,586 个测试从未真正执行 | `docs/_working/2026-09-18-issue-inventory-full.md:78` |
| 全仓测试文件（本车道口径 `tests/**/test_*.py`） | 3,509 件（`find tests -name 'test_*.py'`，排除 `__pycache__`） |
| 跨目录同名 test 文件 | **12 个 basename 各 2 份**（实测 `collections.Counter` 口径） |

## 1. 硬约束（未满足前**不要**切真跑，更不要 `-n`）

- **H1 · 并行禁令**：`确证不自包含 = 0` 且本单 P1/P2 关闭之前，CI 只准**按目录串行**
  （`for d in tests/*/; do python -m pytest "$d" ...; done`），**禁 `-n 4`/`--dist`**。
  理由：顺序依赖测试在 xdist 分片下必然大面积爆红，届时"真实基线"拿不到，反把 CI 可信度打掉。
- **H2 · 收绿≠收绿**：`--collect-only` 退出码 0 **不证明收集成功**——`-p no:cacheprovider` 未与
  `-W "ignore::pytest.PytestConfigWarning"` 成对时是 `INTERNALERROR`（rc≠0，尚算响亮）；
  但 `pytest tests/` 单进程因 12 处跨目录同名 test（多数目录无 `__init__.py`）产生的
  **import mismatch 只报 error 行**，切真跑后极易被读成"测试挂了"。
  → CI 每档必须断言**收集条数**（`--collect-only -q | tail -1` 落盘为基线数字），条数掉了就是收集坏了。
- **H3 · 单条用例的全局超时是 120s**（`pyproject.toml` `[tool.pytest.ini_options] timeout = 120`）。
  实测已有一件**红蓝仪器**单跑需 122s（`tests/rule/test_rule_red_blue.py`，其 TRAE-005 探针跑
  `scripts/governance/d5_architecture/diagnose_depgraph.py` 单进程实测 108s）→ 本车道已按仓库既有约定
  加 `@pytest.mark.timeout(300/600)`。**其余目录里同类"分钟级 subprocess 探针"未穷举**，
  切真跑前须先量出各目录最慢用例（命令见 §3 的 M1），否则 CI 会把这些用例判成超时红。
- **H4 · 测试写生产路径的欠账未清**：`tests/**` 里 244 件提及 `data/`（粗口径 grep），
  宪法 §9.6/手册 §6 要求测试输出一律 `tmp_path`。真跑会把这些写盘行为放大成
  "CI 改坏生产数据 / 因数据在而时好时坏"。→ 先做 §3 的 M2 巡检，命中件进"测试隔离欠账"清单。
- **H5 · xdist 老雷**：`--max-worker-restart=5` 与 PID-unique basetemp 已在库
  （`#ARCH-XDIST-WORKER-CRASH-001` 四层治本，见 `pyproject.toml` 注释），
  但**Windows runner 上的 worker 崩溃史**说明并行本身仍需一档"崩溃率=0"的验收。

## 2. 分档建议（给接手者的落地形状）

| 档 | 范围 | 前置 | 超时策略 |
|---|---|---|---|
| Tier-A 快档 | `tests/governance/**`、`tests/rule/**`、纯静态判据件 | 本单 P1 清零 | `timeout=120` 默认可用 |
| Tier-B 慢档 | 含 subprocess/DB 探针的目录（`tests/autonomy`、`tests/trading/pipeline`、`tests/ex_core`…） | 先出"最慢用例表"（M1） | 显式 `@pytest.mark.timeout(N)` 或整档 `-m "not slow"` |
| Tier-C 并行 | 只在 Tier-A 上开 `-n 2`（不是 4） | Tier-A 连续两轮串行=并行结果逐条一致 | 并行/串行**差值=0** 才算可并行 |

> 本车道**不建议**本轮就开 `-n 4`：收益是墙钟时间，代价是"满屏假红"时无法归因。
> 先按目录串行拿到真实基线（这正是分包12 T4 想要的东西），并行留到差值证据齐了再谈。

## 3. 验收命令（可直接抄）

```bash
# M0 收集条数基线（CI 每次真跑都断言这条数不掉）
python -m pytest tests --collect-only -q -p no:cacheprovider \
  -W "ignore::pytest.PytestConfigWarning" | tail -1

# M1 各目录最慢用例（切真跑前先量，防止全局 120s 兜底把慢探针判成红）
python -m pytest tests/<目录> -q --durations=10 -p no:cacheprovider \
  -W "ignore::pytest.PytestConfigWarning" | tail -15

# M2 测试写生产路径巡检（命中件进"测试隔离欠账"清单）
python - <<'PY'
from pathlib import Path
import re
pat=re.compile(r'(REPO_ROOT\s*/\s*["\']data|open\(\s*["\']data/|write_text\([^)]*data/|"data/[^"]*"\s*/\s*)')
for p in sorted(Path("tests").rglob("test_*.py")):
    t=p.read_text(encoding="utf-8",errors="replace")
    if pat.search(t) and "tmp_path" not in t:
        print(p)
PY

# M3 顺序依赖回归哨（CI 真跑落地后长期挂：倒序跑必须与正序同结果）
PYTHONPATH=.runtime/tmp/ff-testint python -m pytest tests/rule -q -p revorder_plugin \
  -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning"
```

## 4. 本车道已清 / 未清（截止提交时点）

| 项 | 状态 | 证据 |
|---|---|---|
| P1 确证不自包含件 | 已清 1 件（`tests/rule/test_rule_red_blue.py`）；实证批次内**再确证 0 件** | `lanes/testint_census.md` §3、§6 |
| P2 可疑登记（模式命中未确证） | 只登记未修（形3/形4/形5 命中量大，单跑逐条实证仍在跑，数字以 census 为准） | 同上 §2、§5 |
| P3 外来 WIP 挡道件 | `tests/plan_engine/test_judgment_ledger.py`（unstaged 为他人车道）、`tests/ex_core/**`（z-land3 在跑幂等面，其中 4 红它已在归因）→ 本车道未动 | `git status --porcelain` |
| P4 测试隔离欠账（依赖生产库/文件、无法夹具化） | 未穷举，按 H4 的 M2 巡检交接手 | — |
| P5 红蓝仪器检出率门下界 | `tests/rule/test_rule_red_blue.py` 的 `detection_rate >= 0.95` 在 9 条规则口径下**要求 9/9 全 GREEN**（任一条 YELLOW=0.888<0.95 即红）。TRAE-001/002/005 三条的状态由**当轮 subprocess 结果**决定 → 机器负载高时会翻黄。本车道**未降门**（禁为过而改弱断言），只如实登记为 CI 真跑的 flake 源 | 该文件 `:394`（`assert total >= 9`）与 `:397-401`（检出率门） |

> P5 是"尺子会假报"的另一种形态：不是 bug，而是**门下界与并行负载耦合**。
> 若 CI 真跑后该件反复黄，正确解是把九项探针的**状态口径**（GREEN 需要哪些前置）与
> **检出率门**（0.95）分别重设——那是判据设计变更，须总包/Owner 定，不由测试车道擅动。
