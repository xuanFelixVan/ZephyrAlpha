---
title: "终极图书馆 · 馆员系统蓝图 v0.1（唯一入口/出口的执行层）"
ttl: task_bound
completes_when: 馆员骨架挖干呈批→骨架施工令出单→流程文件落 constitution/SOP
date: "2026-09-21"
owner: "ZephyrAlpha-Owner"
session: "st-ulib-20260921"
---

# 馆员系统蓝图 v0.1 —— 唯一入口/唯一出口的执行层

> **一句话**：图（05）回答"有什么"；馆（总账/总闸/总口）回答"放哪/怎么查"；**馆员回答"凭什么、走哪道门、谁记账"**。没有馆员，馆是死目录；有了馆员，馆才是活系统。

## §1 馆员定义（非人格化角色）

馆员≠某个 AI，=**一组机制+流程+闸门的总称**，持六权：
1. **登记权**：一切新资产出生必须先在馆员处领 asset_id（无籍不生）；
2. **借阅权**：一切查询必经 library_lookup 并留审计（谁/何时/查了什么）；
3. **变更记账权**：一切修改落地即刷指纹（改了什么/何时/基线）；
4. **迁移权**：改名/搬家籍随家动（home 字段同步）；
5. **注销权**：删除必先销户（无销不删）；
6. **盘点权**：定期+事件驱动双向对齐（盘↔馆），blind/ghost 即红。

## §2 六流程（生命周期动线）

| 流程 | 触发 | 动线 | 闸 | 账 |
|---|---|---|---|---|
| 入馆 | 新建任何资产 | 预登记(asset_id+token)→施工→提交 | CREATE-GUARD 扩面 | 总账+指纹 |
| 借阅 | 会话/IDE 要定位任何东西 | library_lookup→返回资产+新鲜度 | 引用必经（软闸+审计） | lookup_audit |
| 变更 | 修改已籍资产 | claim→施工→git_commit.py 网关 | own-scope 门禁族 | 指纹刷新 |
| 迁移 | 改名/搬家 | git mv→登记同步 | RENAME-DEPGRAPH-SYNC 扩面 | home 更新 |
| 注销 | 删除 | 销户申请→删除 | GATE-DELETE-AUDIT 扩面 | status=archived |
| 盘点 | 周窗+提交事件 | 五采集器重扫→双向对齐 | LIBRARY-COVERAGE | blind/ghost 报告 |

## §3 四层强制（"如何确保只有一个入口"）

| 层 | 机制 | 现状 | 缺口 |
|---|---|---|---|
| L1 硬闸（程序不可绕） | CREATE-GUARD/网关/POST-COMMIT-GUARD 回滚/plumbing 禁用/emergency 仅锁灾 | **全在**（实证：本班三次被自家门禁拦截） | 与总账接线（今夜总攻） |
| L2 工具钩（IDE/代理环境） | ZCode PreToolUse/PostToolUse hook：Write/Edit 受管路径先查馆 | 无 | W+1 接线，方案今夜定 |
| L3 制度（宪法条款） | 宪法 L0 一行："一切资产生命周期操作必经馆员" | 无 | 须 Owner 批，W+1 修宪 |
| L4 审计（事后可追） | 借阅审计+周对账报告呈 Owner | capability_lookup 审计模式在 | 总攻后统一入 governance.db |

## §4 IDE 施工动线（Owner 场景："我在编译器里写方案也要过馆员吗？"——要，且现制已基本覆盖）

编辑器新建方案文档 → 保存 → ①新文件：CREATE-GUARD 要求 creation_token+claim（本班实证：漏 token 被 TTL-METADATA/N-03/CREATE-GUARD 三连拦）→ ②git add → ③git_commit.py 网关（馆员柜台：串行锁/门禁/GW 标记）→ ④落 HEAD 即刷总账。**绕过路径=无**：裸 commit 被 POST-COMMIT-GUARD reset 回滚；plumbing（read-tree/update-index/write-tree）宪法禁用；emergency_commit 仅注册表/锁灾可用且手写标记判伪造。缺的只是"落 HEAD 即刷总账"最后半步=今夜总攻接线。

## §5 馆员系统自身的骨架（挖矿对象，与图书馆骨架同理）

六支柱 × 四外部维度，先挖矿后施工：
- **登记协议**：register→validate→resolve 怎么设计（npm/pypi/容器 registry/MCP Registry/Backstage/HuggingFace 模型卡强制制/SLSA 出处签名）
- **借阅协议**：查询口怎么定契约（MCP 工具/RAG 强制引用/新鲜度返回）
- **角色制度**：馆员对应业界什么角色（Records Manager ISO 15489/Data Steward/Release Manager）
- **强制面**：AI 代理环境里怎么逼一切写入过闸（hooks/CODEOWNERS/presubmit/CI 所有权）
- **注销与退役制**：retention/disposition schedule（对应我们的退役/归档流程）
- **对账制**：盘点周期与差异处置（ISO 14721 OAIS 的 SIP/AIP/DIP 三态）

## §6 与今夜总攻的关系

今夜总攻建馆（总账/总闸/总口）=馆员的**手和脚**；馆员流程文件+SOP 增补=今夜新增 **I 包**（纯文档，写流程不写码）；L2 hook 接线+L3 修宪=W+1（修宪须 Owner 批）。馆员系统自身的骨架挖矿（三路子代并行）今夜完成，挖干后骨架施工令 W+1 出单。

## §7 挖矿计划

三路并行子代：①登记制生态（npm/pypi/MCP Registry/Backstage/HF/SLSA 的 register→validate→resolve 协议学）②记录管理与图书馆学（ISO 15489 生命周期/OAIS 三态/编目与元数据/联合目录"一馆一目录"纪律）③AI 原生强制面（hooks 拦截/CODEOWNERS/presubmit/agent 护栏的 2025-2026 实践）→ 产出=07 骨架挖矿台账 → 挖干判定 → W+1 骨架施工令。
