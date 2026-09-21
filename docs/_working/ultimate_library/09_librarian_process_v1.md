---
title: "馆员流程 v1（六权六流程 SOP 条款，I 包交付）"
ttl: task_bound
completes_when: 总攻验收通过后随九件套转正；L2 hook/L3 修宪 W+1
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 馆员流程 v1（I 包：六权六流程 SOP 条款）

> 定位：馆员=机制+流程+闸门（非人格化）。本件=可执行的流程条款；强制=四层漏斗（L1 git 硬闸唯一收口/L2 工具钩前置滤网 W+1/L3 宪法降险 W+1 修宪/L4 审计追责）。

## 六权六流程条款

1. **登记权（无籍不生）**：新建任何资产，第一步=馆员处领 asset_id（`act('register')` 或 CREATE-GUARD token 流程）；文件带索书号表头（08 §7，一行）。
2. **借阅权（查询必经）**：定位任何资产走 `python -m zephyr.library.lookup <关键词>`；AI 会话重要引用写 read 事件留审计。
3. **变更记账权**：修改已籍资产，落地即 `act('update')` 刷指纹；提交走 git_commit.py 网关（馆员柜台）。
4. **迁移权（籍随家动）**：改名/搬家后 `act('move')` 更新 home；asset_id 永不变。
5. **注销权（无销不删）**：删除前 `act('delete', authority=<批件号>)` 签发死亡证明（08 §3.1）；无授权机械拒绝。
6. **盘点权（双向差集清零）**：`check_library_coverage.py` 产盲册（blind/ghost）；三处置=收编/归档/注销；连续两轮差集清零才算盘平。

## 并发条款（08 §3.3）

- 施工并发无上限；落盘走队列（慢资源串行）；登记走 PG 并行（MVCC）。
- 同条目并发=行级串行+指纹基线乐观锁（冲突=重读重放，同 git rebase）。
- 账本写权限收口（W+1）：app 角色仅 EXECUTE `librarian.act()`，直写表权限收回。

## 增枝条款

字段/类目新增=增枝制：停止判据三问+本账补行+Owner 批；schema 演进只增不改语义。
