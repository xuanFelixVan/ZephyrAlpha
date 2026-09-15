---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓批3 报告（regime 域 42 文件）

> 会话 st-btfix-p15-20260915 | 2026-09-15 | 承接批1（回测 43）+批2（合规 29），commit 64961e2b

## 成果

| 项 | 数 | 说明 |
|---|---|---|
| 源码出仓 | 42 | src/zephyr/regime 全域，内联块换 external 锚，round-trip 逐项一致 |
| 外部 yaml | 42 | docs/03_modules/_domain_regime/algo_flow/（doc_type: architecture_view） |
| creation_token | 42 | batch_creation_tokens.py 批量通道（锚点 btfix_p1p2） |
| TDM 补注 | 5 节点 | TDM-E-L1 / TDM-E-L1-S4 / TDM-E-L1-AGG / TDM-E-L2-01-5 / TDM-E-L3-12-3 |
| 域测试 | 786 passed | tests/regime 全绿（pyproject 配置） |

## 过程发现（后续班注意）

1. **pytest_min.ini markers 失效**：markers 单行分号写法实际只注册了第一个（pytest ini 语义），叠加 --strict-markers 后凡用 @pytest.mark.financial 的文件收集即炸。精简跑法暂用 pyproject 配置（勿加 -p no:cacheprovider，cache_dir 组合 INTERNALERROR）。建议后续班修 ini + compare_pytest_configs.py 看守器同步放宽。
2. **pytest cache 并发锁**：多会话并发跑 pytest 时 .runtime/tmp/pytest_cache/lastfailed PermissionError 致收集中断；用 -o cache_dir=<独立目录> 绕开。
3. **存量 import 坏点**：tests/regime/test_overlay_signals_builder_valuation.py 跨包 import tests.regime（tests/ 无 __init__.py），2026-08-29 7ee214ad55 落库起即阻断 tests/regime 收集；本批一行修复（平 import）。
4. **CloneGuard 暴露存量克隆**：overlay/risk 两 builder 的 _fb_call 同型防御包装 100% 相似，触碰双文件后首次暴露；echo-guard.yml acknowledged 登记（cg-regime-fb-call-fallback-20260915）。
5. **ALGO-NOTE-SYNC 归因窗口实测**：quoted 风格 algo_note_zh 行内追加出仓注记不被归因到节点（hunk 距离>3 行），note_confirmed 必须物理紧贴 node_id 行。

## 普查进度

全仓 3302 内联模块，已出仓 72+42=114（3.5%）。下一批建议：ex_core(61) / ml_train(43)。
