---
title: "W-M1 车道A·波0 施工战报——账本底座（DDL 部署器+意图 API+红蓝）"
ttl: task_bound
date: '2026-09-23'
session: st-wm1-buildA-20260923
status: delivered
---

# W-M1 车道A·波0 施工战报（账本底座）

> 施工令：Owner 全批 D1-D6/A1-A3（09_wm1_master_plan.md §四）。真源=02_ledger_design.md（乙号文）。
> 会话=st-wm1-buildA-20260923，worktree 隔离施工（ai/st-wm1-buildA-20260923/wm1-registry-ledger）。

## 一、交付清单

### ① 幂等 DDL 部署器（真源=schemas/categories/registry_ledger/，DDL-as-Code）

| 文件 | 内容 |
|---|---|
| schemas/categories/registry_ledger/registry_catalog.py | 册级登记表（ROOR 派生种子位；extra_families 承接 §2.1 多族两案中的并案） |
| schemas/categories/registry_ledger/registry_entry.py | 条目状态表（UNIQUE(registry_id,family_key,entry_key)+version CAS+tombstone 永不物理删） |
| schemas/categories/registry_ledger/registry_event.py | 事件表（只增不改；before 走 before_sha256 指纹链式引用） |
| schemas/categories/registry_ledger/registry_snapshot.py | 快照表（发布=不可变全量+每册单调版本+git_commit_ref） |
| src/zephyr/governance/registry_ledger/schema.py | DDL 聚合+`_schema_version` 版本表（depgraph 同款 ON CONFLICT DO NOTHING） |
| src/zephyr/governance/registry_ledger/deploy.py | `deploy_registry_ledger()`：CREATE SCHEMA/TABLE IF NOT EXISTS+不可变双保险（REVOKE UPDATE/DELETE FROM PUBLIC+BEFORE UPDATE OR DELETE 触发器 RAISE）+reader/writer 角色按需 GRANT+`schema_fingerprint()` 全对象规范哈希 |

**实弹部署记录**（PG 实例=postgresql://localhost:5432/depgraph，meta_question 同库先例连接）：
- 首跑 16 语句 18 对象；重跑 15 语句对象数不变；`schema_fingerprint` 前后相等=**零漂移实证**；指纹=`738fd904ceff9d97…`。
- schema `registry_ledger` 已落真实实例（空表无数据；Phase 0 基线导入归波1）。

### ② 意图 API（src/zephyr/governance/registry_ledger/api.py）

- `register / update / retire / takeover / fetch_entry`——全部按条目声明；**无任何整文件读写接口**（§3.1 负面清单落实）。
- update 带 expected_version CAS：基线不匹配=`CONFLICT_VERSION`(409) 且**拒绝本身记事件行**（detail.conflict=true，base_version/after_version 留证）。
- retire 强制 authority_ref（缺失=AUTHORITY_REQUIRED 机械拒绝）；tombstone 行保留占坑，同键重登=CONFLICT_DUPLICATE。
- takeover force=True 需 `owner_approval_ref` Owner 批文标记（D-5 high 域门位），否则 FORBIDDEN_FORCE；接管必记 action=takeover 事件（含被顶会话）。
- reason ≥10 字纪律机械强制（INVALID_ARGUMENT/ValueError）。
- identity.py：首标量键真源=门禁 `entry_identity_key`（registry_family 重组位落地后自动切换 import；HEAD 未含时本地同规则+等值测试锚定）；复合键=`首标量|token=值` 与合并器 `_merge_entry_identity` 同规则。

### ③ 红蓝测试（tests/governance/test_registry_ledger.py，19 例）

| 判据 | 用例 | 结果 |
|---|---|---|
| 同条目双写必 409 | 串行陈旧 CAS + 双线程真并发竞跑（恰好一胜一败+败者事件行） | 绿 |
| 事件表物理不可改 | UPDATE/DELETE 触发器 RAISE（owner 也删不动）+ reader 角色权限拒绝 | 绿 |
| 幂等部署器重复跑零漂移 | 临时 schema 双部署 fingerprint 相等+_schema_version 恰 1 行 | 绿 |
| 复合键身份 B22 同构 | 复合键 ↔ (file,token) 二元组无损互映射+对 `_merge_entry_identity` 等值断言 | 绿 |
| 附带 | retire 无批文拒绝/tombstone 保留/404/身份不匹配/短 reason/force 门位/指纹稳定性/事件回放等 11 例 | 绿 |

**两轮回归**：新套件连续两轮 18 passed 1 skipped（全绿稳定）。
**基线既有红披露**（非本批引入，证据=主区同套件全绿）：worktree 纯 HEAD 下 tests/governance/test_commit_queue_landing_nightfix.py 等 3 套件 23 红——夜班手术一（st-nightfix-20260923）`registry_family/` 重组位文件未提交（主区 untracked+modified），已提交的测试依赖未提交代码所致；他会话在飞件按宪法 §3.4 不代修。其中 identity 等值断言 1 例已做自适应 skip，重组位落地后自动恢复硬断言。

## 二、净零声明

新增=4 表 DDL 真源+1 部署器+1 API+1 身份模块（对 02 号文 §5 收编表：不替代任何既有件，W2 合并器/门禁/claim/队列各司其职）。修改=2（schemas/categories/__init__.py 目录地图加 1 行注记；tests 豁免）。注册表/规则/gate 净增=0。

## 三、移交项（波1 输入）

1. registry_catalog 种子=Phase 0 机械扫描（波1 基线导入车道），本批零人工填写。
2. publish/import_baseline/render_yaml 接口按 03 号文投影设计与总图波次施工（本波0 施工令只含三件套，不越界）。
3. registry_family 重组位落地后：identity.py import 自动切换（try 分支已铺），merger 等值 skip 用例恢复硬断言。
4. 写路径 v2 收口（PG EXECUTE-only 函数）按 D-2 档位随波次推进。
