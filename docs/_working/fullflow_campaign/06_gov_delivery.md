---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# S6 治理与交付环节簿

> 本段=数据→治理→交付链。**全套说明书已机生在案**：`docs/01_policies_and_standards/sop/governance_sop/commit_navigation_playbook.md`
> - `L0-JOURNEY` — 施工全程九站地图（J1 开工反查/J2 领锁/J3 隔离/J4 token 意图 API/J5 翻译先行/J6 投影册纪律/J7 提交面选择/J8 死账三步拳/J9 落地核验，每站一行处方+门卡全展开）
> - `序页` — 全文件锚点目录
> - `FT-*` — 按文件类型的逐类清单 ｜ `DEATH-CASES` — 死因处方速查 ｜ `APPENDIX-A/B/C` — 全台速查/待蒸馏/新鲜度
> 进场检票钩子（MOD-GOV-115）拒绝话术已内嵌 L0-JOURNEY 锚点：被拦即读。

## 一、输入面
施工产物（代码/文档/登记册变更）+ 宪法/规则 YAML 约束面。

## 二、输出面
dev 主线提交（GitCommitGateway/队列正门）+ 登记册同步（PG 账本投影）+ 审计留痕（lookup_audit/entrance_audit/gate_audit）。

## 三、入口面
| 入口 | 验证 | 状态 |
|---|---|---|
| `python scripts/git_commit.py --session <sid> --files <清单>` | 实测（本战役多批） | 绿 |
| `python scripts/commit_queue.py enqueue/status/health` | 实测（0013/0015/0020/0021 袋） | 绿 |
| `python scripts/governance/generators/generate_commit_guide.py --check` | 实测（L0 卡后 74296 字符渲染 OK） | 绿 |
| `python scripts/registry_projection/registry_projection_generator.py --render` | 实测（v90 归一化治愈 sharpe2 陈旧插写事故） | 绿 |

## 四、模块面
- `src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py`（唯一合法 commit 入口）
- `scripts/commit_queue.py` + `scripts/governance/commit_queue_landing.py`（队列串行落地面）
- `src/zephyr/governance/registry_ledger/api.py`（登记意图 API）+ `registry_projection/`（投影生成器）
- `src/zephyr/gov_enforcement/commit_gates/*`（门禁族，速查=playbook APPENDIX-A）

## 五、自动化面
- 队列 daemon 自动排干（lease 持有者轮转）；投影 belt daemon 探针在岗；心跳 daemon 随会话生灭。
- 手动面：意图 API register/publish（半自动，工具齐备）；死车道 archive（人工触发、工具化）。

## 六、缺口面
- [黄] 生成器测试源文件缺失（10-04/05 重排误删，仅存 pyc）——L11 测试重收编车道在册事项
- [黄] .gitignore `!.zcode/` 行 + `.zcode/config.json` 入库待 Owner ARCH-APPROVAL（钩子本机已生效，随仓分发待批）
- [绿] 其余通道全通（本战役全链实测）

## 七、自审闸
**绿**——治理与交付链全通（本战役九门实证 + 说明书闭环）。
