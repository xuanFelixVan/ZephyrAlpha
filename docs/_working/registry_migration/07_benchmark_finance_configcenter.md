---
ttl: task_bound
title: "对标调研·银行/配置中心共享资产并发治理（CAB/Schema工具/Apollo/Nacos/etcd/ZK/K8s SSA/PG审计账本，45 源）"
session: st-regfix-lane0b-20260923
---

# 银行/配置中心共享资产并发治理调研（2026-09-23）

> 调研方法：网络检索+一手文档阅读（K8s/etcd/ZooKeeper/Liquibase/Apollo/FINRA/SEC/PostgreSQL 官方文档为主）。所有事实标注出处；未能打开一手原文、仅经二手摘要确认的标注「二手来源」或「未能证实」。

## 1. 银行/监管变更管理：CAB（ITIL）及其在大规模下的失效

- **并发模型**：任何团队改生产共享资产须先提交变更请求（RFC），由 CAB 集中审批，通过后由实施团队（银行中通常是 DBA/平台组）执行——**人工串行化写入**。Bytebase/NineData 等数据库变更审批产品的存在佐证"开发提交 SQL→审批→DBA 通道执行"模式；具体某大银行 DBA 单写一手资料**未能证实**。
- **风险分级**（ITIL 4 核心）：Standard Change（预授权低风险免 CAB）/Normal Change（风险评估）/Emergency Change（ECAB 紧急通道）。
- **关键实证——FCA（英国金融行为监管局）2021-02-05《Implementing Technology Change》多机构审查**：
  - 抽样银行约 **98.4% 技术变更成功无事故**，约 **1.6% 导致事故**；
  - **major change 事故概率约为 standard change 的两倍**——走了完整 CAB 审批的重大变更反而更危险；
  - **CAB 对 major change 批准率超过 90%**——沦为橡皮图章（原文页 403，数字经多家律所/咨询摘要交叉确认）。
- **DORA 官方结论**："change approvals are best implemented through peer review during the development process, supplemented by automation"；未发现更正式的外部评审流程与更低变更失败率相关；重型审批导致大批量低频发布——更高风险更高失败率。
- KeyPup.io 基准（二手单一来源）：基础设施类 CAB 平均前置 34.5 天，超出 20 天 SLA；只有预授权 standard change 能达 SLA。
- **小结**：大规模下业界结论高度一致——**集中人审既拖慢吞吐又不降事故率；有效做法=预授权标准变更+风险分级自动路由+peer review+强可回滚性**。安全性来源从"人审吞吐"转移到"并发控制+快速回滚+审计"。

## 2. 数据库 Schema 变更治理

- **写入侧单通道**：开发者不直连生产库；变更以 migration/PR 形式提交，经审批后由部署通道执行。Liquibase 用 `DATABASECHANGELOGLOCK` 表保证同一时刻单执行实例——执行期全局互斥锁（整库级）。
- **顺序 migration 模型（Liquibase/Flyway）**：changelog 有序 append-only 账目；执行记录入 `DATABASECHANGELOG` 表——单调递增版本号+执行账本的 exactly-once 收敛。
- **声明式 desired-state 模型（Skeema/Atlas）**：CREATE 语句集表示期望态，`skeema diff/push` 计算活库与目标态差异生成 DDL 收敛；"schema change by pull request"。
- **在线 DDL（gh-ost，GitHub 出品）**：binlog 流异步应用到 ghost 表；真暂停/限流/推迟 cut-over/副本演练（`--test-on-replica`）——把最危险一步变成显式可控的独立动作。
- **审批流产品化（Bytebase）**：CEL 表达式按环境/引擎/SQL 类型/影响行数/**风险等级**匹配审批链（Project Owner→DBA）；GitOps 模式下审批转入 VCS PR。
- **关键洞察**：顺序账本模型胜在审计与 exactly-once；声明式模型胜在可 diff 可评审、天然适合 git/PR。业界新工具都在向"**声明式意图+审批通道+执行账本**"融合——与"YAML 降级为生成器输出、真源进 DB 账本"同构。

## 3. 配置中心：Apollo / Nacos / etcd / ZooKeeper

### 3.1 Apollo（携程）
- **编辑与发布分离**："the management of configurations is divided into two operations: editing and publishing, therefore greatly reducing human errors"；发布需有发布权限的人执行。
- 权限粒度到 namespace（配置文件级）；数据模型：**Release（每次发布=该 namespace 全量配置的不可变快照）/ Commit（未发布修改）/ ReleaseHistory / Audit（记录用户何时以何种方式操作了哪个实体）/ ConsumerAudit** 分表。
- **回滚**："Every configuration releases are versioned, which is friendly to support configuration rollback"——回滚=将历史 Release 重新生效。
- 发布推送：HTTP Long Polling ~1 秒实时+5 分钟兜底轮询+**本地文件缓存容灾**；支持灰度发布（部分实例先生效）。

### 3.2 Nacos（阿里）
- 权限粒度：Namespace/Group/Service/DataId；客户端**长轮询携带配置 MD5** 比对，不一致才返回变更。
- **容灾快照**：客户端本地保存配置快照（"类似 Git 中的本地 commit"），Server 不可用从本地恢复。
- 灰度：Beta/基于 IP 或自定义标签；Nacos 3.x/MSE 全量操作审计（发布/删除/修改/注册/注销自动捕获，可追溯操作人/时间/IP）；历史版本页签可回滚任意版本。

### 3.3 etcd
- 写经 Raft 共识**单 leader 串行提交**（全局全序）；读可走 leader（linearizable）或本地。
- **MVCC 核心**："A persistent, multi-version, concurrency-control data model"；每次原子修改产生新全局 revision（单调递增）；旧版本不覆盖（append-only），所有历史版本可查可 watch；物理 boltDB b+tree 存 (major,sub,type) delta。
- **冲突控制**：v3 txn 支持 compare-and-swap（比较 key 的 value/mod_revision/version 再写）——乐观锁以 mod_revision 为凭据。
- **compaction**：可压缩掉最旧版本，compact 后旧 revision 不可 watch 但**每个 key 最新版本永远保留**——历史保留与物理体积分层权衡。

### 3.4 ZooKeeper
- 写全部转发 leader，ZAB 全序提交；zxid=全部变更全序戳。
- **znode 级乐观锁**：Stat 维护 version/cversion/aversion；更新须"supply the version…if it doesn't match, the update will fail"（BadVersionException）。
- **不保留历史多版本**（仅计数器），无内建回滚审计——与 etcd 最大分野：**ZK 给 CAS 凭据，etcd 给完整多版本历史**。

### 3.5 横截面对比

| 系统 | 写并发控制粒度 | 冲突机制 | 历史版本 | 回滚 | 审计 |
|---|---|---|---|---|---|
| Apollo | namespace 级权限；编辑/发布分离 | 发布=新版本快照 | Release 全保留 | 一键回滚历史 Release | Audit 表 |
| Nacos | namespace/group/DataId 级 | MD5 比对 | 历史版本页签 | 回滚任意版本 | 全量操作审计(3.x) |
| etcd | key 级；txn CAS(mod_revision) | compare 失败即事务失败 | 全部历史 revision（compact 前） | 重放/读旧 revision | 修订号即审计 |
| ZooKeeper | znode 级 version CAS | BadVersionException | 无 | 无内建 | zxid 全序无内容史 |

## 4. Kubernetes：声明式 Desired State + Server-Side Apply 字段所有权

- 所有组件以客户端身份向 API server 提交期望状态，API server 唯一仲裁合并；**协议层面禁止"读全量-改内存-写全量"的裸覆盖模式**。
- **resourceVersion 乐观并发**：更新失配即 409 StatusConflict；正确重试=重新 GET 再改再交。
- **客户端三方合并（kubectl apply）**：`last-applied-configuration` 注解三方计算 patch——他人改过、不在你配置里的字段被保留；教训：所有权信息存客户端注解，粒度粗且易脆。
- **Server-Side Apply（重点）**：
  - 每次 Apply 带 fieldManager 身份；所有权记录在 `metadata.managedFields`，**按字段路径精确到叶子**；
  - 不同控制器写同一对象不同字段不冲突（"multiple actors can update the same object without causing unexpected interference"）；listType set/map 下支持条目级所有权；
  - **冲突=同字段、不同值、他人持有→Apply 无条件失败**，错误列出冲突字段与持有者；
  - **force 语义**：强制覆盖值并"removes the field from all other managers' entries"（所有权强制转移），CI/CD 用需谨慎；
  - 共享所有权：两 manager 同值共享（正规交接手法：先共值再一方删除）；
  - 控制器无需读-改-写："the object doesn't have to be read beforehand; resourceVersion doesn't have to be specified"——**幂等意图收敛**；本地状态过期则下次 apply 必得冲突（新鲜度由冲突检测保证）。
- 回滚=重放旧 spec；SSA 保证回滚只影响原 manager 拥有的字段。
- K8s 是唯一在生产验证"海量异构控制器并发写同一批共享对象"的系统。

## 5. 审计账本模式：PostgreSQL MVCC + 金融监管要求

- **PG MVCC**：每条语句看到一致性快照；"reading never blocks writing and writing never blocks reading"；SSI 最高隔离。**行级账本+MVCC 天然支持多会话并发写各自条目、读端永远一致快照**。
- **触发器+历史表是主流生产实践**：AFTER INSERT/UPDATE/DELETE 行级触发器把旧/新行连同事务号/时间戳/当前用户追加到独立历史表；`REVOKE UPDATE, DELETE`（必要时 BEFORE 触发器抛异常）强制 append-only。
- PG 19 落地 SQL:2011 application-time 时态特性；完整 system-versioning 原生仍未支持，触发器方案继续有效。
- **金融监管留存要求**：
  - SEC Rule 17a-4（2022-10 修订）：电子记录系统须保持"**a complete time-stamped audit trail that includes all modifications and deletions**"（完整、带时间戳、涵盖一切修改与删除）或仍用 WORM；WORM 须配套可问责审计系统，留存与被审计记录同期；
  - 留存年限：业务通讯类≥3 年（首 2 年易取）、核心账簿类 6 年（**FINRA 4511**：无特定期限者≥6 年）；
  - **SOX §802/SEC Rule 2-06**：审计相关工作底稿**七年**不得销毁；配套刑事责任 18 U.S.C. §1519（最高 20 年监禁）。
- 不可抵赖：17a-4 audit-trail 替代的核心即"每次修改都留痕、可归责到人"——与 PG 触发器账本（who/when/what）直接对应。

## 关键设计原则提炼（对"YAML 注册表→PG 行级账本+生成器输出"）

1. **编辑与发布分离，写入单通道化**（Apollo 编辑/发布分离+DBA 单通道）→ AI 会话只向 PG 账本追加变更意图，YAML 生成与分发由独立发布通道完成。
2. **CAS 凭据做进每一行**（ZK version/K8s 409/etcd mod_revision）→ 账本条目带 version 列，`UPDATE…WHERE entry_id=? AND version=?`，失配即拒——**存储层面消灭整文件覆盖写**。
3. **条目级所有权，冲突默认拒绝，抢占显式**（K8s SSA managedFields）→ 行上记 owning_session；同条目双写默认 409，force=显式参数+审计。
4. **写入单位是意图声明（apply）而非读-改-写全量**（SSA 幂等收敛）→ 会话 API=提交名下条目期望态 upsert；禁 dump-全量-回写接口。
5. **每次发布=不可变全量快照，回滚=重发历史版本**（Apollo Release/etcd revision）→ 生成器输出登记单调 snapshot_id；发布原子可审计。
6. **YAML 降级为只读投影+本地快照容灾**（Nacos 快照/Apollo 缓存/Skeema diff）→ 读端脱离 PG 工作；漂移=重生成+diff 检测。
7. **审计表是一等公民**（Apollo Audit 表/Nacos 全量审计/Liquibase DATABASECHANGELOG）→ 账本自带 who/when/what，供 gate 与复盘直接 SQL。
8. **监管级不可抵赖：append-only+全修改留痕**（SEC 17a-4 标准）→ 事件表禁 UPDATE/DELETE；留存基准 FINRA 6 年/SOX 7 年按需裁剪。
9. **风险分级路由审批，低风险直通**（ITIL standard change/Bytebase risk_level/DORA peer review）→ low 全自动、high Owner 门位。
10. **安全来源=并发控制+可回滚+审计，不是审批吞吐**（DORA/FCA 实证）→ 治理目标是每条变更小、可并发、秒级回滚；"Owner 集中审所有 YAML diff"有业界反证。
11. **历史全保留与 compaction 分层**（etcd）→ 事件表长期保留（审计），物化快照/派生索引周期 compaction 控体积；两者分离。
12. **警惕全局锁：锁粒度必须等于冲突粒度**（Liquibase 整库锁 vs etcd key 级/ZK znode 级/K8s 字段级）→ 迁移后锁粒度=条目行。

## 参考资料清单

1. https://dora.dev/capabilities/streamlining-change-approval/ （DORA 变更审批，一手引文）
2. https://www.fca.org.uk/publications/corporate-documents/implementing-technology-change （FCA 2021 报告）
3. https://www.simmons-simmons.com 、https://www.hsfkramer.com 、https://www.rbcompliance.co.uk （FCA 数据二手摘要交叉）
4. https://www.atlassian.com/itsm/change-management/change-advisory-board
5. https://itsm.tools 、https://wiki.en.it-processmaps.com （ITIL 4）
6. https://octopus.com （Change Advisory Boards Don't Work）
7. https://docs.liquibase.com/concepts/introduction-to-liquibase.html
8. https://github.com/github/gh-ost
9. https://www.skeema.io 、https://docs.bytebase.com/change-database/approval/
10. https://planetscale.com 、https://www.red-gate.com 、https://www.bytebase.com
11. https://github.com/apolloconfig/apollo/blob/master/README.md （Apollo 一手）
12. https://github.com/apolloconfig/apollo/blob/master/docs/zh/design/apollo-design.md （Apollo 设计文档）
13. https://nacos.io/en/blog/nacos-gvr7dx_awbbpb_dgbnz71ppmyl7mhz （Nacos 安全实践）
14. https://help.aliyun.com （MSE Nacos 灰度）
15. https://etcd.io/docs/v3.5/learning/data_model/ （etcd MVCC，一手）
16. https://etcd.io/docs/v3.5/maintenance/ （compaction）
17. https://zookeeper.apache.org/doc/current/zookeeperProgrammers.html （ZK version CAS，一手）
18. https://kubernetes.io/docs/reference/using-api/server-side-apply/ （SSA，本报告主源）
19. https://kubernetes.io/docs/tasks/manage-kubernetes-objects/declarative-config/ （三方合并）
20. https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md （resourceVersion）
21. https://www.postgresql.org/docs/current/mvcc-intro.html （PG MVCC，一手）
22. https://hypirion.com （System-Versioned Tables in Postgres）
23. https://www.finra.org/rules-guidance/key-topics/books-records （17a-4 audit-trail 原文）
24. https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511 （六年留存）
25. https://www.sec.gov/rules-regulations/2003/01/retention-records-relevant-audits-reviews （SOX 802 七年）

**未证实项汇总**：具名大银行废除 CAB 案例数字；银行 schema 冻结期一手规范；Nacos 审计留存时长；Google SSA 博客原文（超时）；FCA 数字经二手交叉；PG 审计账本银行生产规模数字。

**核心结论一句话**：五方向共同指向"**意图声明+行级 CAS+条目所有权+不可变快照发布+append-only 审计**"五件套；监管级标准（SEC 17a-4/FINRA/SOX）可直接作为 W-M1 事件账本的设计基线；K8s SSA 是"多写者共享对象"最成熟的所有权仲裁参考实现。
