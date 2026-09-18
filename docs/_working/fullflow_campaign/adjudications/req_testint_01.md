---
ttl: task_bound
completes_when: 总包对红蓝仪器三项判据设计变更定案（或显式维持现状）
---

# 裁定申请书 req_testint_01 · 红蓝仪器的三处判据设计（测试车道无权自改）

车道 = `st-ff-testint-20260918` · 提交对象 = 总包 `st-fullflow-20260918`
（⚠️ 按任务书 `COORDINATION_LEDGER.md` 为总包自持件，本车道**未回写 §6 待裁表**，以本文件为准。）

## 背景（一句话）

本车道 T1 治的是"报告测试不自包含"（已落地并给能红证据）。治的过程中发现
`tests/rule/test_rule_red_blue.py` 这套**红蓝验收仪**还有三处"判据设计"问题：
它们不是 bug，改法属于**判据重设**（会让仪器变严或改变它究竟在测什么），
按宪法 §5 与手册"门禁只许加严 #321 / 禁白名单消警 #273"，测试车道不得擅动。

## 议题① 红蓝注入面不闭合（仪器在测「仓库脏不脏」而不是「注入能否被检出」）

- 现状（亲验）：`TRAE-001/002` 把违规文件写进 pytest `tmp_path`，
  而被检脚本 `scripts/governance/d11_compliance/audit_registration.py` 以
  `cwd=REPO_ROOT`（`tests/rule/test_rule_red_blue.py:44-59` `_run_audit_registration`）扫**真仓**。
  实测本仓该脚本 `rc=1`、输出含 `ORPHAN MODULES (25)` → 判定分支走 GREEN。
- 后果：**注入的违规从未进入被检面**，"检出率 100%"是仓库体检结果冒充红蓝对抗结果。
  这是六向验收第⑥向（失败会响）意义上的**恒真返回**（账本 R-021 同族新形态）。
- 选项：
  - A 让 `_run_audit_registration` 接收 `cwd`/`--root` 参数，探针在 scratch 副本里注入违规后扫副本
    （最治本；成本=需要脚本支持只读指定根，**属 scripts/** 侧改动 → 须派工，非本车道写域）。
  - B 保留现扫真仓，但把 TRAE-001/002 的规则语义**改名并降标**为"仓库注册体检"，
    另建真正能注入的红蓝件（诚实但工作量最大）。
  - C 维持现状 + 在本车道 census 永久登记（**本车道已做**，即"只登记不擅改"）。
- 建议：A（并派 `scripts/governance/d11_compliance/` owner）。

## 议题② 检出率门 0.95 与机器负载耦合

- 现状（亲验）：`detection_rate >= 0.95` 且 `total==9` → **必须 9/9 全 GREEN**
  （任一条 YELLOW → 8/9 = 0.888 < 0.95 即红）。
  而 TRAE-005 的探针 `scripts/governance/d5_architecture/diagnose_depgraph.py` 实测单进程 **108s**
  （内部 `subprocess.run(timeout=120)`），仓库 `pyproject.toml` 全局 `timeout = 120`。
  → 并发/CI `-n` 下一句"探针超时"就把整件判红，且与代码好坏无关。
- 本车道已做的（不涉判据）：按仓库既有约定加 `@pytest.mark.timeout(300/600)`，
  **未改 `>= 9` / `>= 0.95` 任何一处**。
- 需裁定：是否把"检出率门"的分母口径改为**可判定规则数**（把环境性 YELLOW 单列，
  不计入分母），或把九项扩到 ≥20 项使 0.95 有工程余量。两者都是判据变更，本车道不提具体数值。

## 议题③ CI 真跑前的并行禁令需接手车道确认

- 本车道产物 `lanes/testint_ci_prereq.md` H1：**确证不自包含未清零前，CI 只准按目录串行、禁 `-n`**。
  分包12 T4（`st-ff-instL-20260918`）的 `governance.yml` 改动若已按下 `-n 4`，
  请以其实测差值（串行 vs 并行逐条对比）决定解除还是维持。
- 需裁定：H1 是否升为战役级约束（写进验收规范 §5），还是仅作为 CI 车道的本地约束。

## 影响面 / 回滚

- 三项均**零代码行为变化**（本件只是申请书）。
- 证据位置：`docs/_working/fullflow_campaign/lanes/testint_census.md` §7（另案 A1/A2）、
  `lanes/testint_ci_prereq.md` §1 H1-H3、§4 P5。
- 复验命令：
  `python -m pytest tests/rule/test_rule_red_blue.py -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning"`
  （当前 10 passed，约 115s）
