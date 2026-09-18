---
ttl: task_bound
completes_when: Max/Owner 对 standards_governance/__init__.py  basename 碰撞三方案择一
---

# req_aibase_01 · standards_governance/__init__.py basename 碰撞（三方案代价对比，含治本项）

## 背景
`src/zephyr/governance/standards_governance/__init__.py` 提交被 basename 碰撞拦（与 `src/zephyr/governance/__init__.py` 同名，ARCH-031 盲区）。
实测（2026-09-18）：该文件 untracked 在盘（`git status` = `??`），本地 import 不受影响；总包已裁"保持现状不硬闯"。

## 三方案代价
| 方案 | 动作 | 代价 | 风险 |
|---|---|---|---|
| ①echo-guard 豁免 basename 碰撞 | 给门禁加白名单 | 表面零代价 | **违 R-002/R-006"豁免类问题一律 merge 治本不许 ack 消警"，且触裁定#273 禁白名单消警 → 不推荐** |
| ②改 PEP420 命名空间包（删 `__init__.py`） | 子包不留 `__init__.py` | 丢掉包级 docstring/re-export；同父包下其它子包仍有 `__init__.py` → 布局不一致，`standards_governance` 与 `governance` 混用两种导入语义 | 部分工具（pkgutil/pytest 收集、depgraph 静态扫描）对命名空间包识别不一，需回归；**本质是"绕过碰撞"而非消除碰撞** |
| ③治本：改包结构使 basename 唯一（**推荐**） | `governance/standards_governance/` → 顶层 `src/zephyr/standards/`（或 `governance/standards/`），basename 变 `standards` 与 `governance` 不再同名 | 需改所有 `from zephyr.governance.standards_governance import` 的 import 点 + `git mv` + `generate_project_depgraph.py --force`（RENAME-DEPGRAPH-SYNC 硬拦要求）+ module_translation_registry 路径键重登记 | 改名面可控（本子包当前引用点少），但**属跨车道文件移动**，需 Max 指定车道并避让 vocabM 在途的 `_shared/module_translation_loader.py` |

## 可行性实测（③）
`standards_governance/` 现有文件：本会话未逐一枚举（**推断级**，Max 验真命令见下）。
若子包内文件数 ≤ 小几十且外部 import 点集中，③成本主要落在"重跑 depgraph + 重登记翻译"两件既有机械流程上，
且这两件正是本车道已跑通的登记器（apply_depgraph / add_module_translation）→ **③技术可行，缺的是授权与车道指派，不是能力**。

## 建议
按 R-002/R-006 同原则选 **③**；①为禁选（消警）；②仅当 Max 判定"包级 docstring 与 re-export 可弃"时作退路。

## Max 验真命令
`ls src/zephyr/governance/standards_governance/ && git grep -n "governance.standards_governance" -- src scripts tests | head -20`
