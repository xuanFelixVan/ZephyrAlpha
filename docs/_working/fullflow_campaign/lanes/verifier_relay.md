---
ttl: task_bound
completes_when: 验收仪交工批经队列落地且总包完成首轮三态裁定
---

# 验收仪车道接力（st-ff-verifier-20260918 → 总包）

## 状态
- 代码 `scripts/automation/flowthrough_verifier.py` + 测试 `tests/automation/test_flowthrough_verifier.py`
  + 产物 `skeleton/03_omission_crosscheck.md` / `04_sixway_ledger.md` / `04_sixway_machine_ledger.yaml`
  + token/翻译载体 = **7 文件已入队** q-20260918-st-ff-verifier-20260918-0001（state=pending，serializer 自落）
- 三件套已做：depgraph design node MOD-AUTO-L3-002（D_GOVERNANCE）/ creation_token ×4 / module_translation ×2

## 逐子命令
| 子命令 | 状态 | 断点 / 下一步 |
|---|---|---|
| `--crosscheck` | 已完成并落盘 | 异名归一"多义不猜"：D_EXECUTION_CORE→{D_EX_CORE,D_EXEC_SIM} 双命中故仍列未归属；若总包要 0，须补 domain 别名册（真源缺，非工具缺陷） |
| `--stage/--all` | 17 环节全跑通（实测：红=13 黄=5 绿=0） | ②真跑入口的 rc 含"缺必填参数"（rc=2 已单列黄），逐环节补调用口径归车道 |
| `--verdict` | 可用（读台账出分布+逐环节红向） | 裁定权在总包 |
| `--prove-red` | PASS（对照=绿；注入链跳→红且指名 `表名__ff_probe_missing__`；注入 tasks.yaml 按字节临时件→红且指名；生产 sha 不变） | 若要断"0 行空表"型红，需 Owner 门位建影子表 |
| `--e2e` | 可用（逐跳四数字 + break 判定） | 落 `.runtime/tmp/ff-verifier/e2e_result.json`，未产 Markdown（预算耗尽） |

## 未达成（诚实条款）
1. **⑥失败会响对各环节是 STATIC 推演**（AST 扫静默 except + 告警接线计数），**未做逐环节动态断供注入**；
   动态注入只做了验收仪自身（`--prove-red` 两条）。
2. `depgraph.dataflow_runs` 仍 0 行（BRK-059）：验收仪把"无运行时观测"实测出来了，但**未回填观测**——
   那需要施工侧在链路上打点（另车道）。
3. `--e2e` 的"下游读取行数"用"下游声明读取表数"近似，非真实读取量。
4. 测试 11 条中真仓那条依赖 ClickHouse 通道，通道故障时 skip（不假绿）。

## 复跑命令
`PYTHONPATH=src python scripts/automation/flowthrough_verifier.py --all --limit-tables 3 --limit-runs 1 --timeout 45`
